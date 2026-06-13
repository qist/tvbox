# -*- coding: utf-8 -*-
# by @星河
# 修复版本 - 参考最新三合一.js重构虎牙、斗鱼、B站直播逻辑
# 修复：虎牙清晰度选择，确保ratio参数正确传递码率值
# 修复：斗鱼切换分辨率只能播放1秒的问题（每次重新获取安全密钥和签名）
# 修复：B站使用特殊UA和WBI签名绕过-352风控 [^90^][^30^]
import json
import re
import sys
import time
import hashlib
import random
import urllib.parse
from base64 import b64decode, b64encode
from urllib.parse import parse_qs
import requests
from pyquery import PyQuery as pq
sys.path.append('..')
from base.spider import Spider
from concurrent.futures import ThreadPoolExecutor


class Spider(Spider):

    def init(self, extend=""):
        # 初始化B站WBI密钥
        self.bili_wbi_keys = None
        self.bili_wbi_expire = 0
        pass

    def getName(self):
        return "直播"

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    headers = [
        {
            # 特殊UA绕过B站风控 [^90^]
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
        },
        {
            "User-Agent": "Dart/3.4 (dart:io)"
        }
    ]

    excepturl = 'https://www.baidu.com'

    hosts = {
        "huya": ["https://www.huya.com", "https://mp.huya.com"],
        "douyu": "https://www.douyu.com",
        "wangyi": "https://cc.163.com",
        "bili": ["https://api.live.bilibili.com", "https://api.bilibili.com"]
    }

    referers = {
        "huya": "https://live.cdn.huya.com",
        "douyu": "https://m.douyu.com",
        "bili": "https://live.bilibili.com"
    }

    playheaders = {
        "wangyi": {
            "User-Agent": "ExoPlayer",
            "Connection": "Keep-Alive",
            "Icy-MetaData": "1"
        },
        "bili": {
            'Accept': '*/*',
            'Icy-MetaData': '1',
            'referer': 'https://live.bilibili.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        },
        'huya': {
            'User-Agent': 'ExoPlayer',
            'Connection': 'Keep-Alive',
            'Icy-MetaData': '1'
        },
        'douyu': {
            'User-Agent': 'libmpv',
            'Icy-MetaData': '1'
        }
    }

    # WBI签名相关常量 [^30^]
    MIXIN_KEY_ENC_TAB = [
        46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
        33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
        61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
        36, 20, 34, 44, 52
    ]

    def _get_bili_wbi_keys(self):
        """获取B站WBI密钥 [^30^]"""
        try:
            # 检查缓存
            if self.bili_wbi_keys and time.time() < self.bili_wbi_expire:
                return self.bili_wbi_keys
            
            # 从导航接口获取 - 使用特殊UA [^90^]
            resp = self.fetch(
                'https://api.bilibili.com/x/web-interface/nav',
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
                    'Referer': 'https://www.bilibili.com/'
                }
            ).json()
            
            if resp.get('code') != 0:
                return None
            
            img_url = resp['data']['wbi_img']['img_url']
            sub_url = resp['data']['wbi_img']['sub_url']
            
            # 提取文件名作为key
            img_key = img_url.rsplit('/', 1)[1].split('.')[0]
            sub_key = sub_url.rsplit('/', 1)[1].split('.')[0]
            
            self.bili_wbi_keys = (img_key, sub_key)
            self.bili_wbi_expire = time.time() + 86400  # 24小时过期
            
            return self.bili_wbi_keys
        except Exception as e:
            print(f"获取B站WBI密钥失败: {e}")
            return None

    def _get_mixin_key(self, orig: str):
        """生成mixin_key [^30^]"""
        return ''.join([orig[i] for i in self.MIXIN_KEY_ENC_TAB])[:32]

    def _enc_wbi(self, params: dict):
        """WBI签名 [^30^]"""
        keys = self._get_bili_wbi_keys()
        if not keys:
            return params
        
        img_key, sub_key = keys
        mixin_key = self._get_mixin_key(img_key + sub_key)
        
        # 添加时间戳
        params['wts'] = round(time.time())
        
        # 排序参数
        params = dict(sorted(params.items()))
        
        # 过滤特殊字符
        params = {
            k: ''.join(filter(lambda c: c not in "!'()*", str(v)))
            for k, v in params.items()
        }
        
        # 计算签名
        query = urllib.parse.urlencode(params)
        w_rid = hashlib.md5((query + mixin_key).encode()).hexdigest()
        
        params['w_rid'] = w_rid
        return params

    def process_bili(self):
        """获取B站分类列表 - 使用WBI签名 [^30^]"""
        try:
            # 尝试获取分类列表 - 使用特殊UA和WBI签名
            params = {'need_entrance': 1, 'parent_id': 0}
            signed_params = self._enc_wbi(params)
            
            data = self.fetch(
                f'{self.hosts["bili"][0]}/room/v1/Area/getList',
                params=signed_params,
                headers=self.headers[0]
            ).json()
            
            if data.get('code') == 0 and data.get('data'):
                # 保存分类数据供后续使用
                self.bili_areas = data['data']
                return ('bili', [{'key': 'cate', 'name': '分类',
                                  'value': [{'n': i['name'], 'v': str(i['id'])}
                                            for i in data['data']]}])
            return 'bili', None
        except Exception as e:
            print(f"bili处理错误: {e}")
            # 使用默认分类
            return 'bili', [{'key': 'cate', 'name': '分类',
                            'value': [{'n': '网游', 'v': '2'}, {'n': '手游', 'v': '3'},
                                      {'n': '单机', 'v': '6'}, {'n': '娱乐', 'v': '1'},
                                      {'n': '电台', 'v': '5'}, {'n': '虚拟主播', 'v': '9'},
                                      {'n': '生活', 'v': '10'}, {'n': '知识', 'v': '11'},
                                      {'n': '赛事', 'v': '13'}]}]

    def process_douyu(self):
        try:
            self.dyufdata = self.fetch(
                f'{self.referers["douyu"]}/api/cate/list',
                headers=self.headers[1]
            ).json()
            return ('douyu', [{'key': 'cate', 'name': '分类',
                               'value': [{'n': i['cate1Name'], 'v': str(i['cate1Id'])}
                                         for i in self.dyufdata['data']['cate1Info']]}])
        except Exception as e:
            print(f"douyu错误: {e}")
            return 'douyu', None

    def homeContent(self, filter):
        result = {}
        cateManual = {
            "虎牙": "huya",
            "斗鱼": "douyu",
            "网易": "wangyi",
            "B站": "bili"
        }
        classes = []
        filters = {
            'huya': [{'key': 'cate', 'name': '分类',
                      'value': [{'n': '网游', 'v': '1'}, {'n': '单机', 'v': '2'},
                                {'n': '娱乐', 'v': '8'}, {'n': '手游', 'v': '3'}]}]
        }

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(self.process_bili): 'bili',
                executor.submit(self.process_douyu): 'douyu'
            }

            for future in futures:
                platform, filter_data = future.result()
                if filter_data:
                    filters[platform] = filter_data

        for k in cateManual:
            classes.append({
                'type_name': k,
                'type_id': cateManual[k]
            })

        result['class'] = classes
        result['filters'] = filters
        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        vdata = []
        result = {}
        pagecount = 9999
        result['page'] = pg
        result['limit'] = 90
        result['total'] = 999999
        if tid == 'wangyi':
            vdata, pagecount = self.wyccContent(tid, pg, filter, extend, vdata)
        elif 'bili' in tid:
            vdata, pagecount = self.biliContent(tid, pg, filter, extend, vdata)
        elif 'huya' in tid:
            vdata, pagecount = self.huyaContent(tid, pg, filter, extend, vdata)
        elif 'douyu' in tid:
            vdata, pagecount = self.douyuContent(tid, pg, filter, extend, vdata)
        result['list'] = vdata
        result['pagecount'] = pagecount
        return result

    def wyccContent(self, tid, pg, filter, extend, vdata):
        params = {
            'format': 'json',
            'start': (int(pg) - 1) * 20,
            'size': '20',
        }
        response = self.fetch(f'{self.hosts[tid]}/api/category/live/', params=params, headers=self.headers[0]).json()
        for i in response['lives']:
            if i.get('cuteid'):
                bvdata = self.buildvod(
                    vod_id=f"{tid}@@{i['cuteid']}",
                    vod_name=i.get('title'),
                    vod_pic=i.get('cover'),
                    vod_remarks=i.get('nickname'),
                    style={"type": "rect", "ratio": 1.33}
                )
                vdata.append(bvdata)
        return vdata, 9999

    def biliContent(self, tid, pg, filter, extend, vdata):
        """B站分类内容 - 使用WBI签名绕过风控 [^30^][^90^]"""
        try:
            # 分类列表 - 显示子分类
            if extend.get('cate') and pg == '1' and 'click' not in tid:
                # 从已保存的分类数据中找到对应分类的子分类
                if hasattr(self, 'bili_areas'):
                    for area in self.bili_areas:
                        if str(area['id']) == extend['cate']:
                            for sub_area in area.get('list', []):
                                v = self.buildvod(
                                    vod_id=f"click_{tid}@@{extend['cate']}@@{sub_area['id']}",
                                    vod_name=sub_area.get('name'),
                                    vod_pic=sub_area.get('pic'),
                                    vod_tag=1,
                                    style={"type": "oval", "ratio": 1}
                                )
                                vdata.append(v)
                            return vdata, 1
                # 如果没有找到子分类，直接返回空，让用户进入房间列表
                return vdata, 1
            
            # 房间列表 - 使用getList接口并添加WBI签名 [^30^]
            if 'click' in tid:
                # 子分类房间
                ids = tid.split('_')[1].split('@@')
                tid = ids[0]
                parent_area_id = ids[1]
                area_id = ids[2]
            else:
                # 默认使用分类ID作为parent_area_id，area_id为0表示该分类下所有
                parent_area_id = extend.get('cate', '2')  # 默认网游
                area_id = 0
            
            # 构建请求参数并添加WBI签名 [^30^]
            params = {
                'parent_area_id': parent_area_id,
                'area_id': area_id,
                'page': pg,
                'platform': 'web',
                'sort_type': 'online'  # 按热度排序
            }
            signed_params = self._enc_wbi(params)
            
            # 调用getList接口
            api_url = f'{self.hosts[tid][0]}/xlive/web-interface/v1/second/getList'
            data = self.fetch(api_url, params=signed_params, headers=self.headers[0]).json()
            
            # 如果WBI签名失败，尝试不带签名
            if data.get('code') == -352:
                print("WBI签名失败，尝试无签名请求...")
                params = {
                    'parent_area_id': parent_area_id,
                    'area_id': area_id,
                    'page': pg,
                    'platform': 'web',
                    'sort_type': 'online'
                }
                data = self.fetch(api_url, params=params, headers=self.headers[0]).json()
            
            if data.get('code') == 0:
                room_list = data.get('data', {}).get('list', [])
                for room in room_list:
                    if room.get('roomid'):
                        # 处理在线人数显示
                        online = room.get('online', 0)
                        if online > 10000:
                            online_str = f"{online / 10000:.1f}万"
                        else:
                            online_str = str(online)
                        
                        v = self.buildvod(
                            f"{tid}@@{room['roomid']}",
                            room.get('title', '未知标题'),
                            room.get('cover') or room.get('system_cover'),
                            f"{online_str}人",
                            0,
                            room.get('uname', ''),
                            style={"type": "rect", "ratio": 1.33}
                        )
                        vdata.append(v)
                
                # 检查是否有更多数据
                has_more = data.get('data', {}).get('has_more', 0)
                if not has_more:
                    pagecount = int(pg)
                else:
                    pagecount = 9999
            else:
                print(f"B站API返回错误: {data.get('message', '未知错误')} (code: {data.get('code')})")
                pagecount = 1
            
            return vdata, pagecount
            
        except Exception as e:
            print(f"B站内容获取错误: {e}")
            return vdata, 1

    def huyaContent(self, tid, pg, filter, extend, vdata):
        if extend.get('cate') and pg == '1' and 'click' not in tid:
            id = extend.get('cate')
            data = self.fetch(f'{self.referers[tid]}/liveconfig/game/bussLive?bussType={id}',
                              headers=self.headers[1]).json()
            for i in data['data']:
                v = self.buildvod(
                    vod_id=f"click_{tid}@@{int(i['gid'])}",
                    vod_name=i.get('gameFullName'),
                    vod_pic=f'https://huyaimg.msstatic.com/cdnimage/game/{int(i["gid"])}-MS.jpg',
                    vod_tag=1,
                    style={"type": "oval", "ratio": 1}
                )
                vdata.append(v)
            return vdata, 1
        else:
            gid = ''
            if 'click' in tid:
                ids = tid.split('_')[1].split('@@')
                tid = ids[0]
                gid = f'&gameId={ids[1]}'
            data = self.fetch(f'{self.hosts[tid][0]}/cache.php?m=LiveList&do=getLiveListByPage&tagAll=0{gid}&page={pg}',
                              headers=self.headers[1]).json()
            for i in data['data']['datas']:
                if i.get('profileRoom'):
                    v = self.buildvod(
                        f"{tid}@@{i['profileRoom']}",
                        i.get('introduction'),
                        i.get('screenshot'),
                        str(int(i.get('totalCount', '1')) / 10000) + '万',
                        0,
                        i.get('nick'),
                        style={"type": "rect", "ratio": 1.33}

                    )
                    vdata.append(v)
            return vdata, 9999

    def douyuContent(self, tid, pg, filter, extend, vdata):
        if extend.get('cate') and pg == '1' and 'click' not in tid:
            for i in self.dyufdata['data']['cate2Info']:
                if str(i['cate1Id']) == extend['cate']:
                    v = self.buildvod(
                        vod_id=f"click_{tid}@@{i['cate2Id']}",
                        vod_name=i.get('cate2Name'),
                        vod_pic=i.get('icon'),
                        vod_remarks=i.get('count'),
                        vod_tag=1,
                        style={"type": "oval", "ratio": 1}
                    )
                    vdata.append(v)
            return vdata, 1
        else:
            path = f'/japi/weblist/apinc/allpage/6/{pg}'
            if 'click' in tid:
                ids = tid.split('_')[1].split('@@')
                tid = ids[0]
                path = f'/gapi/rkc/directory/mixList/2_{ids[1]}/{pg}'
            url = f'{self.hosts[tid]}{path}'
            data = self.fetch(url, headers=self.headers[1]).json()
            for i in data['data']['rl']:
                v = self.buildvod(
                    vod_id=f"{tid}@@{i['rid']}",
                    vod_name=i.get('rn'),
                    vod_pic=i.get('rs16'),
                    vod_year=str(int(i.get('ol', 1)) / 10000) + '万',
                    vod_remarks=i.get('nn'),
                    style={"type": "rect", "ratio": 1.33}
                )
                vdata.append(v)
            return vdata, 9999

    def detailContent(self, ids):
        ids = ids[0].split('@@')
        if ids[0] == 'wangyi':
            vod = self.wyccDetail(ids)
        elif ids[0] == 'bili':
            vod = self.biliDetail(ids)
        elif ids[0] == 'huya':
            vod = self.huyaDetail(ids)
        elif ids[0] == 'douyu':
            vod = self.douyuDetail(ids)
        return {'list': [vod]}

    def wyccDetail(self, ids):
        try:
            vdata = self.getpq(f'{self.hosts[ids[0]]}/{ids[1]}', self.headers[0])('script').eq(-1).text()

            def get_quality_name(vbr):
                if vbr <= 600:
                    return "标清"
                elif vbr <= 1000:
                    return "高清"
                elif vbr <= 2000:
                    return "超清"
                else:
                    return "蓝光"

            data = json.loads(vdata)['props']['pageProps']['roomInfoInitData']
            name = data['live'].get('title', ids[0])
            vod = self.buildvod(vod_name=data.get('keywords_suffix'), vod_remarks=data['live'].get('title'),
                                vod_content=data.get('description_suffix'))
            resolution_data = data['live']['quickplay']['resolution']
            all_streams = {}
            sorted_qualities = sorted(resolution_data.items(),
                                      key=lambda x: x[1]['vbr'],
                                      reverse=True)
            for quality, data in sorted_qualities:
                vbr = data['vbr']
                quality_name = get_quality_name(vbr)
                for cdn_name, url in data['cdn'].items():
                    if cdn_name not in all_streams and type(url) == str and url.startswith('http'):
                        all_streams[cdn_name] = []
                    if isinstance(url, str) and url.startswith('http'):
                        all_streams[cdn_name].extend([quality_name, url])
            plists = []
            names = []
            for i, (cdn_name, stream_list) in enumerate(all_streams.items(), 1):
                names.append(f'线路{i}')
                pstr = f"{name}${ids[0]}@@{self.e64(json.dumps(stream_list))}"
                plists.append(pstr)
            vod['vod_play_from'] = "$$$".join(names)
            vod['vod_play_url'] = "$$$".join(plists)
            return vod
        except Exception as e:
            return self.handle_exception(e)

    def biliDetail(self, ids):
        """
        B站直播详情 - 使用playUrl接口获取多清晰度
        """
        try:
            room_id = ids[1]
            
            # 获取房间信息
            info_res = self.fetch(
                f'{self.hosts["bili"][0]}/room/v1/Room/get_info?room_id={room_id}',
                headers=self.headers[0]
            ).json()
            
            if info_res.get('code') != 0:
                return self.handle_exception(Exception("获取房间信息失败"))
            
            room_info = info_res['data']
            title = room_info.get('title', 'B站直播')
            
            vod = self.buildvod(
                vod_name=title,
                type_name=f"{room_info.get('parent_area_name', '')}/{room_info.get('area_name', '')}",
                vod_director=room_info.get('uname', ''),
                vod_remarks=f"在线{room_info.get('online', 0)}人"
            )
            
            # 获取播放地址信息
            play_res = self.fetch(
                f'{self.hosts["bili"][0]}/room/v1/Room/playUrl?cid={room_id}&qn=10000&platform=web',
                headers={
                    **self.headers[0],
                    'Referer': 'https://live.bilibili.com/',
                    'Origin': 'https://live.bilibili.com'
                }
            ).json()
            
            if play_res.get('code') != 0:
                return self.handle_exception(Exception("获取播放地址失败"))
            
            play_data = play_res['data']
            accept_quality = play_data.get('accept_quality', ['10000', '400', '250', '150'])
            quality_desc = {item['qn']: item['desc'] for item in play_data.get('quality_description', [])}
            
            # 构建清晰度列表
            qualities = []
            for qn in sorted([int(q) for q in accept_quality], reverse=True):
                desc = quality_desc.get(qn, f'清晰度{qn}')
                qualities.append(f"{desc}$bili@@{room_id}@@{qn}")
            
            vod['vod_play_from'] = 'B站直播'
            vod['vod_play_url'] = '#'.join(qualities)
            return vod
            
        except Exception as e:
            print(f"B站详情错误: {e}")
            return self.handle_exception(e)

    def huyaDetail(self, ids):
        """
        虎牙播放详情 - 参考最新三合一.js重构
        支持多线路多清晰度选择
        核心算法：通过房间信息API获取uid、streamName和rateArray，为每个清晰度生成签名URL
        清晰度说明：
        - 蓝光8M/6M/4M/10M = 8000/6000/4000/10000 kbps = 1080P+
        - 蓝光 = 3000 kbps = 1080P
        - 超清 = 2000 kbps = 1080P (官方标准)
        - 高清 = 1200 kbps = 720P
        - 标清/流畅 = 500-800 kbps = 480P/540P
        """
        try:
            room_id = ids[1]
            
            # 1. 获取房间信息
            api_url = f'{self.hosts[ids[0]][1]}/cache.php?m=Live&do=profileRoom&roomid={room_id}'
            res = self.fetch(api_url, headers=self.headers[0])
            
            if res.status_code != 200:
                return self.handle_exception(Exception(f"API请求失败: {res.status_code}"))
            
            data = res.json()
            if not data or not data.get('data'):
                return self.handle_exception(Exception("房间数据为空"))
            
            room_data = data['data']
            
            # 2. 提取关键信息
            uid = room_data.get('profileInfo', {}).get('uid')
            stream_info = room_data.get('stream', {})
            live_data = room_data.get('liveData', {})
            
            if not uid:
                return self.handle_exception(Exception("缺少uid"))
            
            # 3. 获取streamName和码率信息
            base_stream_list = stream_info.get('baseSteamInfoList', [])
            if not base_stream_list:
                return self.handle_exception(Exception("无直播流信息"))
            
            # 获取第一个CDN的streamName作为基准
            base_stream = base_stream_list[0]
            stream_name = base_stream.get('sStreamName')
            if not stream_name:
                return self.handle_exception(Exception("无法获取streamName"))
            
            # 4. 构建VOD对象
            vod = self.buildvod(
                vod_name=live_data.get('introduction', '虎牙直播'),
                type_name=live_data.get('gameFullName', ''),
                vod_director=live_data.get('nick', ''),
                vod_remarks=live_data.get('contentIntro', ''),
            )
            
            # 5. 获取所有CDN线路
            cdn_list = []
            for stream in base_stream_list:
                cdn_type = stream.get('sCdnType', 'AL')
                flv_url = stream.get('sFlvUrl', '')
                hls_url = stream.get('sHlsUrl', '')
                stream_name_cdn = stream.get('sStreamName', stream_name)
                
                if flv_url:
                    cdn_list.append({
                        'cdn': cdn_type,
                        'flv_base': flv_url,
                        'hls_base': hls_url,
                        'stream_name': stream_name_cdn,
                        'priority': stream.get('iWebPriorityRate', 0)
                    })
            
            # 按优先级排序
            cdn_list.sort(key=lambda x: x['priority'], reverse=True)
            
            # 6. 获取清晰度列表 (rateArray)
            rate_array = stream_info.get('rateArray', [])
            
            # 如果没有rateArray，尝试从vMultiStreamInfo获取
            if not rate_array and 'vMultiStreamInfo' in room_data:
                rate_array = room_data['vMultiStreamInfo']
            
            # 如果仍然没有，使用默认清晰度（按虎牙官方标准）
            if not rate_array:
                rate_array = [
                    {'sDisplayName': '蓝光4M', 'iBitRate': 4000},
                    {'sDisplayName': '蓝光', 'iBitRate': 3000},
                    {'sDisplayName': '超清', 'iBitRate': 2000},  # 2000kbps = 1080P
                    {'sDisplayName': '高清', 'iBitRate': 1200},   # 1200kbps = 720P
                    {'sDisplayName': '流畅', 'iBitRate': 500}
                ]
            
            # 过滤和排序清晰度
            # 虎牙的rateArray中，iBitRate就是码率值，sDisplayName是显示名称
            # 需要确保：超清=2000kbps(1080P)，高清=1200kbps(720P)
            filtered_rates = []
            seen_bitrates = set()
            
            for rate in rate_array:
                bit_rate = rate.get('iBitRate', 0)
                name = rate.get('sDisplayName', '')
                
                # 跳过重复的码率
                if bit_rate in seen_bitrates:
                    continue
                
                # 修正清晰度名称，确保符合虎牙标准
                # 2000kbps应该是超清(1080P)，不是高清
                if bit_rate == 2000 and ('高清' in name or '720' in name):
                    name = '超清'  # 强制修正为超清
                elif bit_rate == 1200 and ('标清' in name or '480' in name):
                    name = '高清'  # 1200kbps对应高清
                elif bit_rate == 2000 and name == '原画':
                    name = '超清'  # 修正原画为超清
                
                seen_bitrates.add(bit_rate)
                filtered_rates.append({
                    'sDisplayName': name,
                    'iBitRate': bit_rate
                })
            
            # 按码率从高到低排序
            sorted_rates = sorted(filtered_rates, key=lambda x: x['iBitRate'], reverse=True)
            
            # 7. 为每个CDN生成各清晰度的播放URL
            play_lines = []
            line_names = []
            
            for cdn_idx, cdn in enumerate(cdn_list[:3]):  # 最多取3个CDN
                cdn_name = cdn['cdn']
                line_names.append(f"线路{cdn_idx + 1}({cdn_name})")
                
                qualities = []
                for rate in sorted_rates:
                    quality_name = rate['sDisplayName']
                    bit_rate = rate['iBitRate']
                    
                    # 生成该清晰度的URL
                    quality_url = self._generate_huya_play_url(
                        cdn, uid, stream_name, bit_rate
                    )
                    
                    qualities.extend([quality_name, quality_url])
                
                # 编码该线路的所有清晰度
                encoded_qualities = self.e64(json.dumps(qualities))
                play_lines.append(f"{live_data.get('introduction', '直播')}${ids[0]}@@{encoded_qualities}")
            
            # 8. 构建播放数据
            vod['vod_play_from'] = "$$$".join(line_names)
            vod['vod_play_url'] = "$$$".join(play_lines)
            
            return vod
            
        except Exception as e:
            return self.handle_exception(e)
    
    def _generate_huya_play_url(self, cdn, uid, stream_name, bit_rate):
        """
        生成虎牙播放URL，参考最新三合一.js算法
        关键：ratio参数必须正确设置为iBitRate值（如2000、4000等）
        """
        # 基础URL构建
        flv_base = cdn['flv_base']
        stream = cdn['stream_name']
        
        # 生成时间戳和签名参数
        timestamp = int(time.time())
        seqid = f"{uid}{timestamp}"
        ss = hashlib.md5(f"{seqid}|huya_adr|102".encode()).hexdigest()
        ws_time = hex(timestamp + 21600)[2:]  # 16进制，有效期6小时
        
        # 计算wsSecret
        ws_secret = hashlib.md5(
            f"DWq8BcJ3h6DJt6TY_{uid}_{stream_name}_{ss}_{ws_time}".encode()
        ).hexdigest()
        
        # 构建基础URL
        base_url = f"{flv_base}/{stream}.flv"
        
        # 关键修复：ratio参数直接使用iBitRate值
        # 超清=2000，高清=1200，蓝光=3000/4000/6000/8000
        if bit_rate > 0:
            ratio_param = f"ratio={bit_rate}"
        else:
            # 原画/0码率时，使用默认2000或从URL推断
            ratio_param = "ratio=2000"
        
        # 构建完整URL
        play_url = (
            f"{base_url}?{ratio_param}&wsSecret={ws_secret}&wsTime={ws_time}"
            f"&ctype=huya_adr&seqid={seqid}&uid={uid}"
            f"&fs=bgct&ver=1&t=102"
        )
        
        return play_url

    def douyuDetail(self, ids):
        """
        斗鱼播放详情 - 参考最新三合一.js重构
        核心算法：设备ID生成 -> 获取加密密钥 -> 计算签名 -> 获取播放地址
        修复：切换分辨率只能播放1秒的问题
        方案：存储房间号和码率信息，在playerContent中实时获取对应码率的URL
        """
        try:
            channel = ids[1]
            headers = self.gethr(0, zr=f'{self.hosts[ids[0]]}/{channel}')
            
            # 1. 初始化会话和设备ID (参考JS中的initialize和setupDeviceId)
            session = {}
            
            # 请求首页获取Cookie
            try:
                home_res = self.fetch(f'{self.hosts[ids[0]]}/{channel}', headers=headers)
                if home_res.headers.get('Set-Cookie'):
                    cookie_str = home_res.headers.get('Set-Cookie')
                    # 解析dy_did
                    did_match = re.search(r'dy_did=([a-f0-9]{32})', cookie_str)
                    if did_match:
                        device_id = did_match.group(1)
                    else:
                        device_id = self._generate_random_hex(32)
                else:
                    device_id = self._generate_random_hex(32)
            except:
                device_id = self._generate_random_hex(32)
            
            session['dy_did'] = device_id
            session['mantine-color-scheme-value'] = 'light'
            
            # 2. 获取房间基本信息
            betard_res = self.fetch(f'{self.hosts[ids[0]]}/betard/{channel}', headers=headers).json()
            if not betard_res or not betard_res.get('room'):
                return self.handle_exception(Exception("获取房间信息失败"))
            
            room_info = betard_res['room']
            vname = room_info.get('room_name', '斗鱼直播')
            
            vod = self.buildvod(
                vod_name=vname,
                vod_remarks=room_info.get('second_lvl_name', ''),
                vod_director=room_info.get('nickname', ''),
            )
            
            # 3. 获取安全密钥 (参考JS中的getSecurityKey)
            sec_url = f"{self.hosts[ids[0]]}/wgapi/livenc/liveweb/websec/getEncryption?did={device_id}"
            sec_res = self.fetch(sec_url, headers=headers).json()
            
            if not sec_res or sec_res.get('error') != 0:
                return self.handle_exception(Exception("获取加密密钥失败"))
            
            security_data = sec_res['data']
            secret_key = security_data.get('key')
            random_str = security_data.get('rand_str')
            enc_time = security_data.get('enc_time', 1)
            enc_data = security_data.get('enc_data')
            
            # 4. 计算签名 (参考JS中的computeSignature)
            current_time = int(time.time())
            
            # 迭代计算MD5
            current = random_str
            for _ in range(enc_time):
                current = hashlib.md5(f"{current}{secret_key}".encode()).hexdigest()
            
            signature = hashlib.md5(f"{current}{secret_key}{channel}{current_time}".encode()).hexdigest()
            
            # 5. 请求播放地址 (参考JS中的requestStreamData)
            play_payload = {
                'enc_data': enc_data,
                'tt': str(current_time),
                'did': device_id,
                'auth': signature,
                'cdn': '',
                'rate': '',
                'hevc': '0',
                'fa': '0',
                'ive': '0'
            }
            
            play_api = f"{self.hosts[ids[0]]}/lapi/live/getH5PlayV1/{channel}"
            
            # 构建请求头带Cookie
            play_headers = headers.copy()
            cookie_str = '; '.join([f"{k}={v}" for k, v in session.items()])
            play_headers['Cookie'] = cookie_str
            play_headers['Content-Type'] = 'application/x-www-form-urlencoded'
            
            play_res = requests.post(play_api, data=play_payload, headers=play_headers, timeout=10).json()
            
            if not play_res or play_res.get('error') != 0:
                # 尝试旧版API
                play_res = self._try_legacy_douyu_api(channel, device_id, signature, current_time, play_headers)
                if not play_res:
                    return self.handle_exception(Exception("获取播放地址失败"))
            
            stream_info = play_res.get('data', {})
            
            # 6. 检查并更新设备ID (参考JS中的checkAndUpdateDeviceId)
            rtmp_live = stream_info.get('rtmp_live', '')
            if rtmp_live:
                did_match = re.search(r'did=([a-f0-9]{32})', rtmp_live)
                if did_match and did_match.group(1) != device_id:
                    device_id = did_match.group(1)
                    session['dy_did'] = device_id
                    # 重新请求
                    play_payload['did'] = device_id
                    play_res = requests.post(play_api, data=play_payload, headers=play_headers, timeout=10).json()
                    if play_res and play_res.get('error') == 0:
                        stream_info = play_res.get('data', {})
            
            # 7. 提取播放URL和多码率信息
            stream_url = None
            if stream_info.get('rtmp_url') and stream_info.get('rtmp_live'):
                stream_url = f"{stream_info['rtmp_url']}/{stream_info['rtmp_live']}"
            elif stream_info.get('hls_url'):
                stream_url = stream_info['hls_url']
            
            if not stream_url:
                return self.handle_exception(Exception("无法获取播放地址"))
            
            # 8. 构建多码率选项
            multirates = stream_info.get('multirates', [])
            
            # 关键修复：存储房间号和码率信息，而不是直接存储URL
            # 这样在切换清晰度时可以重新获取对应码率的签名URL
            qualities = []
            
            if multirates:
                # 按码率排序
                sorted_rates = sorted(multirates, key=lambda x: x.get('bit', 0), reverse=True)
                for rate in sorted_rates:
                    bit_rate = rate.get('rate', -1)
                    name = rate.get('name', f"{bit_rate}P")
                    
                    # 存储格式：码率值，用于playerContent中重新获取URL
                    # 使用特殊标记#来区分这是码率值而不是URL
                    qualities.extend([name, f"#{bit_rate}"])
            else:
                # 只有原画
                qualities = ['原画', '#-1']
            
            # 同时存储房间号和设备信息，用于重新获取URL
            # 格式：房间号|设备ID|签名信息（base64编码）
            session_info = {
                'channel': channel,
                'device_id': device_id,
                'secret_key': secret_key,
                'random_str': random_str,
                'enc_time': enc_time,
                'enc_data': enc_data
            }
            encoded_session = self.e64(json.dumps(session_info))
            
            # 9. 构建播放数据
            # vod_play_url格式：房间名$平台@@base64(清晰度列表)@@base64(会话信息)
            encoded_qualities = self.e64(json.dumps(qualities))
            vod['vod_play_from'] = '斗鱼直播'
            vod['vod_play_url'] = f"{vname}${ids[0]}@@{encoded_qualities}@@{encoded_session}"
            
            return vod
            
        except Exception as e:
            return self.handle_exception(e)
    
    def _generate_random_hex(self, length):
        """生成随机十六进制字符串"""
        hex_chars = '0123456789abcdef'
        return ''.join(random.choice(hex_chars) for _ in range(length))

    def _try_legacy_douyu_api(self, channel, device_id, signature, timestamp, headers):
        """尝试使用旧版API获取播放地址"""
        try:
            legacy_payload = {
                'did': device_id,
                'tt': str(timestamp),
                'sign': signature,
                'cdn': '',
                'rate': '-1',
                'ver': 'Douyu_223061205',
                'iar': '1',
                'ive': '1',
                'hevc': '0',
                'fa': '0'
            }
            legacy_api = f"https://www.douyu.com/lapi/live/getH5Play/{channel}"
            res = requests.post(legacy_api, data=legacy_payload, headers=headers, timeout=10)
            return res.json() if res.status_code == 200 else None
        except:
            return None
    
    def _get_douyu_play_url(self, channel, device_id, secret_key, random_str, enc_time, enc_data, rate):
        """
        获取斗鱼指定码率的播放URL（带签名）
        用于切换清晰度时重新获取URL
        """
        try:
            current_time = int(time.time())
            
            # 重新计算签名
            current = random_str
            for _ in range(enc_time):
                current = hashlib.md5(f"{current}{secret_key}".encode()).hexdigest()
            
            signature = hashlib.md5(f"{current}{secret_key}{channel}{current_time}".encode()).hexdigest()
            
            # 构建请求
            play_payload = {
                'enc_data': enc_data,
                'tt': str(current_time),
                'did': device_id,
                'auth': signature,
                'cdn': '',
                'rate': str(rate) if rate > 0 else '',
                'hevc': '0',
                'fa': '0',
                'ive': '0'
            }
            
            play_api = f"https://www.douyu.com/lapi/live/getH5PlayV1/{channel}"
            
            headers = {
                'User-Agent': self.headers[0]['User-Agent'],
                'Referer': f'https://www.douyu.com/{channel}',
                'Origin': 'https://www.douyu.com',
                'Cookie': f'dy_did={device_id}; mantine-color-scheme-value=light',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            play_res = requests.post(play_api, data=play_payload, headers=headers, timeout=10).json()
            
            if not play_res or play_res.get('error') != 0:
                # 尝试旧版API
                return self._get_douyu_play_url_legacy(channel, device_id, signature, current_time, rate)
            
            stream_info = play_res.get('data', {})
            
            # 检查设备ID是否匹配
            if stream_info.get('rtmp_live'):
                did_match = re.search(r'did=([a-f0-9]{32})', stream_info['rtmp_live'])
                if did_match and did_match.group(1) != device_id:
                    # 设备ID不匹配，使用新设备ID重新获取
                    return self._get_douyu_play_url(channel, did_match.group(1), secret_key, random_str, enc_time, enc_data, rate)
            
            if stream_info.get('rtmp_url') and stream_info.get('rtmp_live'):
                return f"{stream_info['rtmp_url']}/{stream_info['rtmp_live']}"
            elif stream_info.get('hls_url'):
                return stream_info['hls_url']
            
            return None
        except Exception as e:
            print(f"获取斗鱼播放URL失败: {e}")
            return None
    
    def _get_douyu_play_url_legacy(self, channel, device_id, signature, timestamp, rate):
        """使用旧版API获取斗鱼播放URL"""
        try:
            legacy_payload = {
                'did': device_id,
                'tt': str(timestamp),
                'sign': signature,
                'cdn': '',
                'rate': str(rate) if rate > 0 else '-1',
                'ver': 'Douyu_223061205',
                'iar': '1',
                'ive': '1',
                'hevc': '0',
                'fa': '0'
            }
            legacy_api = f"https://www.douyu.com/lapi/live/getH5Play/{channel}"
            
            headers = {
                'User-Agent': self.headers[0]['User-Agent'],
                'Referer': f'https://www.douyu.com/{channel}',
                'Cookie': f'dy_did={device_id}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            res = requests.post(legacy_api, data=legacy_payload, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if data.get('error') == 0:
                    stream_info = data.get('data', {})
                    if stream_info.get('rtmp_url') and stream_info.get('rtmp_live'):
                        return f"{stream_info['rtmp_url']}/{stream_info['rtmp_live']}"
            return None
        except:
            return None

    def searchContent(self, key, quick, pg="1"):
        pass

    def playerContent(self, flag, id, vipFlags):
        try:
            ids = id.split('@@')
            p = 1
            if ids[0] in ['wangyi']:
                p, url = 0, json.loads(self.d64(ids[1]))
            elif ids[0] == 'bili':
                p, url = self.biliplay(ids)
            elif ids[0] == 'huya':
                p, url = self.huyaplay(ids)
            elif ids[0] == 'douyu':
                p, url = self.douyuplay(ids)
            return {'parse': p, 'url': url, 'header': self.playheaders[ids[0]]}
        except Exception as e:
            return {'parse': 1, 'url': self.excepturl, 'header': self.headers[0]}

    def biliplay(self, ids):
        """
        B站播放解析 - 使用playUrl接口获取指定清晰度直播流
        ids: [平台, 房间号, 清晰度qn]
        支持多线路返回
        """
        try:
            room_id = ids[1]
            qn = ids[2] if len(ids) > 2 else '10000'
            
            # 使用playUrl接口获取直播流
            play_url = f'{self.hosts["bili"][0]}/room/v1/Room/playUrl?cid={room_id}&qn={qn}&platform=web'
            data = self.fetch(play_url, headers={
                **self.headers[0],
                'Referer': 'https://live.bilibili.com/',
                'Origin': 'https://live.bilibili.com'
            }).json()
            
            if data.get('code') != 0:
                return 1, self.excepturl
            
            play_data = data['data']
            durl_list = play_data.get('durl', [])
            
            if not durl_list:
                return 1, self.excepturl
            
            # 构建多线路结果 [线路1, URL1, 线路2, URL2, ...]
            urls = []
            for idx, item in enumerate(durl_list, 1):
                url = item.get('url')
                if url:
                    urls.extend([f'线路{idx}', url])
            
            # 如果只有一条线路，直接返回URL
            if len(urls) == 2:
                return 0, urls[1]  # 直接返回URL字符串
            
            return 0, urls
            
        except Exception as e:
            print(f"B站播放错误: {e}")
            return 1, self.excepturl

    def huyaplay(self, ids):
        """
        虎牙播放解析 - 返回所有清晰度选项供用户选择
        ids[1] 格式: base64编码的 [清晰度名称1, URL1, 清晰度名称2, URL2, ...]
        """
        try:
            # ids[1] 是编码后的播放地址列表 [名称1, URL1, 名称2, URL2, ...]
            decoded = json.loads(self.d64(ids[1]))
            # decoded 是一个列表，奇数索引是名称，偶数索引是URL
            return 0, decoded
        except Exception as e:
            print(f"虎牙播放解析错误: {e}")
            return 1, self.excepturl

    def douyuplay(self, ids):
        """
        斗鱼播放解析 - 实时获取对应码率的播放URL
        ids格式: [平台, base64(清晰度列表), base64(会话信息)]
        清晰度列表: [名称1, #码率1, 名称2, #码率2, ...]
        #表示这是码率值，需要重新获取URL
        """
        try:
            if len(ids) < 3:
                # 兼容旧格式
                decoded = json.loads(self.d64(ids[1]))
                return 0, decoded
            
            # 解析清晰度列表和会话信息
            qualities = json.loads(self.d64(ids[1]))
            session_info = json.loads(self.d64(ids[2]))
            
            channel = session_info['channel']
            device_id = session_info['device_id']
            secret_key = session_info['secret_key']
            random_str = session_info['random_str']
            enc_time = session_info['enc_time']
            enc_data = session_info['enc_data']
            
            # 为每个清晰度实时获取播放URL
            result = []
            for i in range(0, len(qualities), 2):
                name = qualities[i]
                rate_marker = qualities[i + 1]
                
                # 解析码率值（去掉#前缀）
                if rate_marker.startswith('#'):
                    rate = int(rate_marker[1:])
                else:
                    rate = -1
                
                # 实时获取对应码率的URL
                play_url = self._get_douyu_play_url(
                    channel, device_id, secret_key, random_str, 
                    enc_time, enc_data, rate
                )
                
                if play_url:
                    result.extend([name, play_url])
            
            if not result:
                return 1, self.excepturl
            
            return 0, result
        except Exception as e:
            print(f"斗鱼播放解析错误: {e}")
            return 1, self.excepturl

    def localProxy(self, param):
        pass

    def e64(self, text):
        try:
            text_bytes = text.encode('utf-8')
            encoded_bytes = b64encode(text_bytes)
            return encoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Base64编码错误: {str(e)}")
            return ""

    def d64(self, encoded_text):
        try:
            encoded_bytes = encoded_text.encode('utf-8')
            decoded_bytes = b64decode(encoded_bytes)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Base64解码错误: {str(e)}")
            return ""

    def josn_to_params(self, params, skip_empty=False):
        query = []
        for k, v in params.items():
            if skip_empty and not v:
                continue
            query.append(f"{k}={v}")
        return "&".join(query)

    def params_to_json(self, query_string):
        parsed_data = parse_qs(query_string)
        result = {key: value[0] for key, value in parsed_data.items()}
        return result

    def buildvod(self, vod_id='', vod_name='', vod_pic='', vod_year='', vod_tag='', vod_remarks='', style='',
                 type_name='', vod_area='', vod_actor='', vod_director='',
                 vod_content='', vod_play_from='', vod_play_url=''):
        vod = {
            'vod_id': vod_id,
            'vod_name': vod_name,
            'vod_pic': vod_pic,
            'vod_year': vod_year,
            'vod_tag': 'folder' if vod_tag else '',
            'vod_remarks': vod_remarks,
            'style': style,
            'type_name': type_name,
            'vod_area': vod_area,
            'vod_actor': vod_actor,
            'vod_director': vod_director,
            'vod_content': vod_content,
            'vod_play_from': vod_play_from,
            'vod_play_url': vod_play_url
        }
        vod = {key: value for key, value in vod.items() if value}
        return vod

    def getpq(self, url, headers=None, cookies=None):
        data = self.fetch(url, headers=headers, cookies=cookies).text
        try:
            return pq(data)
        except Exception as e:
            print(f"解析页面错误: {str(e)}")
            return pq(data.encode('utf-8'))

    def gethr(self, index, rf='', zr=''):
        headers = self.headers[index]
        if zr:
            headers['referer'] = zr
        else:
            headers['referer'] = f"{self.referers[rf]}/"
        return headers

    def handle_exception(self, e):
        print(f"报错: {str(e)}")
        return {'vod_play_from': '哎呀翻车啦', 'vod_play_url': f'翻车啦${self.excepturl}'}