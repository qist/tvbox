# -*- coding: utf-8 -*-
# by @嗷呜
import json
import re
import sys
import time
from base64 import b64decode, b64encode
from urllib.parse import parse_qs
import requests
from pyquery import PyQuery as pq
sys.path.append('..')
from base.spider import Spider
from concurrent.futures import ThreadPoolExecutor


class Spider(Spider):

    def init(self, extend=""):
        tid = 'douyin'
        headers = self.gethr(0, tid)
        response = requests.head(self.hosts[tid], headers=headers)
        ttwid = response.cookies.get('ttwid')
        headers.update({
            'authority': self.hosts[tid].split('//')[-1],
            'cookie': f'ttwid={ttwid}' if ttwid else ''
        })
        self.dyheaders = headers
        pass

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    headers = [
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
        },
        {
            "User-Agent": "Dart/3.4 (dart:io)"
        }
    ]

    excepturl = 'https://www.baidu.com'

    hosts = {
        "huya": ["https://www.huya.com","https://mp.huya.com"],
        "douyin": "https://live.douyin.com",
        "douyu": "https://www.douyu.com",
        "wangyi": "https://cc.163.com",
        "bili": ["https://api.live.bilibili.com", "https://api.bilibili.com"]
    }

    referers = {
        "huya": "https://live.cdn.huya.com",
        "douyin": "https://live.douyin.com",
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
            'referer': referers['bili'],
            'user-agent': headers[0]['User-Agent']
        },
        'douyin': {
            'User-Agent': 'libmpv',
            'Icy-MetaData': '1'
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

    def process_bili(self):
        try:
            self.blfdata = self.fetch(
                f'{self.hosts["bili"][0]}/room/v1/Area/getList?need_entrance=1&parent_id=0',
                headers=self.gethr(0, 'bili')
            ).json()
            return ('bili', [{'key': 'cate', 'name': '分类',
                              'value': [{'n': i['name'], 'v': str(i['id'])}
                                        for i in self.blfdata['data']]}])
        except Exception as e:
            print(f"bili处理错误: {e}")
            return 'bili', None

    def process_douyin(self):
        try:
            data = self.getpq(self.hosts['douyin'], headers=self.dyheaders)('script')
            for i in data.items():
                if 'categoryData' in i.text():
                    content = i.text()
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    if start != -1 and end != -1:
                        json_str = content[start:end]
                        json_str = json_str.replace('\\"', '"')
                        try:
                            self.dyifdata = json.loads(json_str)
                            return ('douyin', [{'key': 'cate', 'name': '分类',
                                                'value': [{'n': i['partition']['title'],
                                                           'v': f"{i['partition']['id_str']}@@{i['partition']['title']}"}
                                                          for i in self.dyifdata['categoryData']]}])
                        except json.JSONDecodeError as e:
                            print(f"douyin解析错误: {e}")
            return 'douyin', None
        except Exception as e:
            print(f"douyin请求或处理错误: {e}")
            return 'douyin', None

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
            "哔哩": "bili",
            "抖音": "douyin",
            "斗鱼": "douyu",
            "网易": "wangyi"
        }
        classes = []
        filters = {
            'huya': [{'key': 'cate', 'name': '分类',
                      'value': [{'n': '网游', 'v': '1'}, {'n': '单机', 'v': '2'},
                                {'n': '娱乐', 'v': '8'}, {'n': '手游', 'v': '3'}]}]
        }

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self.process_bili): 'bili',
                executor.submit(self.process_douyin): 'douyin',
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
        elif 'douyin' in tid:
            vdata, pagecount = self.douyinContent(tid, pg, filter, extend, vdata)
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
        if extend.get('cate') and pg == '1' and 'click' not in tid:
            for i in self.blfdata['data']:
                if str(i['id']) == extend['cate']:
                    for j in i['list']:
                        v = self.buildvod(
                            vod_id=f"click_{tid}@@{i['id']}@@{j['id']}",
                            vod_name=j.get('name'),
                            vod_pic=j.get('pic'),
                            vod_tag=1,
                            style={"type": "oval", "ratio": 1}
                        )
                        vdata.append(v)
            return vdata, 1
        else:
            path = f'/xlive/web-interface/v1/second/getListByArea?platform=web&sort=online&page_size=30&page={pg}'
            if 'click' in tid:
                ids = tid.split('_')[1].split('@@')
                tid = ids[0]
                path = f'/xlive/web-interface/v1/second/getList?platform=web&parent_area_id={ids[1]}&area_id={ids[-1]}&sort_type=&page={pg}'
            data = self.fetch(f'{self.hosts[tid][0]}{path}', headers=self.gethr(0, tid)).json()
            for i in data['data']['list']:
                if i.get('roomid'):
                    data = self.buildvod(
                        f"{tid}@@{i['roomid']}",
                        i.get('title'),
                        i.get('cover'),
                        i.get('watched_show', {}).get('text_large'),
                        0,
                        i.get('uname'),
                        style={"type": "rect", "ratio": 1.33}
                    )
                vdata.append(data)
            return vdata, 9999

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

    def douyinContent(self, tid, pg, filter, extend, vdata):
        if extend.get('cate') and pg == '1' and 'click' not in tid:
            ids = extend.get('cate').split('@@')
            for i in self.dyifdata['categoryData']:
                c = i['partition']
                if c['id_str'] == ids[0] and c['title'] == ids[1]:
                    vlist = i['sub_partition'].copy()
                    vlist.insert(0, {'partition': c})
                    for j in vlist:
                        j = j['partition']
                        v = self.buildvod(
                            vod_id=f"click_{tid}@@{j['id_str']}@@{j['type']}",
                            vod_name=j.get('title'),
                            vod_pic='https://p3-pc-weboff.byteimg.com/tos-cn-i-9r5gewecjs/pwa_v3/512x512-1.png',
                            vod_tag=1,
                            style={"type": "oval", "ratio": 1}
                        )
                        vdata.append(v)
            return vdata, 1
        else:
            path = f'/webcast/web/partition/detail/room/?aid=6383&app_name=douyin_web&live_id=1&device_platform=web&count=15&offset={(int(pg) - 1) * 15}&partition=720&partition_type=1'
            if 'click' in tid:
                ids = tid.split('_')[1].split('@@')
                tid = ids[0]
                path = f'/webcast/web/partition/detail/room/?aid=6383&app_name=douyin_web&live_id=1&device_platform=web&count=15&offset={(int(pg) - 1) * 15}&partition={ids[1]}&partition_type={ids[-1]}&req_from=2'
            data = self.fetch(f'{self.hosts[tid]}{path}', headers=self.dyheaders).json()
            for i in data['data']['data']:
                v = self.buildvod(
                    vod_id=f"{tid}@@{i['web_rid']}",
                    vod_name=i['room'].get('title'),
                    vod_pic=i['room']['cover'].get('url_list')[0],
                    vod_year=i.get('user_count_str'),
                    vod_remarks=i['room']['owner'].get('nickname'),
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
        elif ids[0] == 'douyin':
            vod = self.douyinDetail(ids)
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
        try:
            vdata = self.fetch(
                f'{self.hosts[ids[0]][0]}/xlive/web-room/v1/index/getInfoByRoom?room_id={ids[1]}&wts={int(time.time())}',
                headers=self.gethr(0, ids[0])).json()
            v = vdata['data']['room_info']
            vod = self.buildvod(
                vod_name=v.get('title'),
                type_name=v.get('parent_area_name') + '/' + v.get('area_name'),
                vod_remarks=v.get('tags'),
                vod_play_from=v.get('title'),
            )
            data = self.fetch(
                f'{self.hosts[ids[0]][0]}/xlive/web-room/v2/index/getRoomPlayInfo?room_id={ids[1]}&protocol=0%2C1&format=0%2C1%2C2&codec=0%2C1&platform=web',
                headers=self.gethr(0, ids[0])).json()
            vdnams = data['data']['playurl_info']['playurl']['g_qn_desc']
            all_accept_qns = []
            streams = data['data']['playurl_info']['playurl']['stream']
            for stream in streams:
                for format_item in stream['format']:
                    for codec in format_item['codec']:
                        if 'accept_qn' in codec:
                            all_accept_qns.append(codec['accept_qn'])
            max_accept_qn = max(all_accept_qns, key=len) if all_accept_qns else []
            quality_map = {
                item['qn']: item['desc']
                for item in vdnams
            }
            quality_names = [f"{quality_map.get(qn)}${ids[0]}@@{ids[1]}@@{qn}" for qn in max_accept_qn]
            vod['vod_play_url'] = "#".join(quality_names)
            return vod
        except Exception as e:
            return self.handle_exception(e)

    def huyaDetail(self, ids):
        try:
            vdata = self.fetch(f'{self.hosts[ids[0]][1]}/cache.php?m=Live&do=profileRoom&roomid={ids[1]}',
                               headers=self.headers[0]).json()
            v = vdata['data']['liveData']
            vod = self.buildvod(
                vod_name=v.get('introduction'),
                type_name=v.get('gameFullName'),
                vod_director=v.get('nick'),
                vod_remarks=v.get('contentIntro'),
            )
            data = dict(reversed(list(vdata['data']['stream'].items())))
            names = []
            plist = []

            for stream_type, stream_data in data.items():
                if isinstance(stream_data, dict) and 'multiLine' in stream_data and 'rateArray' in stream_data:
                    names.append(f"线路{len(names) + 1}")
                    qualities = sorted(
                        stream_data['rateArray'],
                        key=lambda x: (x['iBitRate'], x['sDisplayName']),
                        reverse=True
                    )
                    cdn_urls = []
                    for cdn in stream_data['multiLine']:
                        quality_urls = []
                        for quality in qualities:
                            quality_name = quality['sDisplayName']
                            bit_rate = quality['iBitRate']
                            base_url = cdn['url']
                            if bit_rate > 0:
                                if '.m3u8' in base_url:
                                    new_url = base_url.replace(
                                        'ratio=2000',
                                        f'ratio={bit_rate}'
                                    )
                                else:
                                    new_url = base_url.replace(
                                        'imgplus.flv',
                                        f'imgplus_{bit_rate}.flv'
                                    )
                            else:
                                new_url = base_url
                            quality_urls.extend([quality_name, new_url])
                        encoded_urls = self.e64(json.dumps(quality_urls))
                        cdn_urls.append(f"{cdn['cdnType']}${ids[0]}@@{encoded_urls}")

                    if cdn_urls:
                        plist.append('#'.join(cdn_urls))
            vod['vod_play_from'] = "$$$".join(names)
            vod['vod_play_url'] = "$$$".join(plist)
            return vod
        except Exception as e:
            return self.handle_exception(e)

    def douyinDetail(self, ids):
        url = f'{self.hosts[ids[0]]}/webcast/room/web/enter/?aid=6383&app_name=douyin_web&live_id=1&device_platform=web&enter_from=web_live&web_rid={ids[1]}&room_id_str=&enter_source=&Room-Enter-User-Login-Ab=0&is_need_double_stream=false&cookie_enabled=true&screen_width=1980&screen_height=1080&browser_language=zh-CN&browser_platform=Win32&browser_name=Edge&browser_version=125.0.0.0'
        data = self.fetch(url, headers=self.dyheaders).json()
        try:
            vdata = data['data']['data'][0]
            vod = self.buildvod(
                vod_name=vdata['title'],
                vod_remarks=vdata['user_count_str'],
            )
            resolution_data = vdata['stream_url']['live_core_sdk_data']['pull_data']['options']['qualities']
            stream_json = vdata['stream_url']['live_core_sdk_data']['pull_data']['stream_data']
            stream_json = json.loads(stream_json)
            available_types = []
            if any(sdk_key in stream_json['data'] and 'main' in stream_json['data'][sdk_key] for sdk_key in
                   stream_json['data']):
                available_types.append('main')
            if any(sdk_key in stream_json['data'] and 'backup' in stream_json['data'][sdk_key] for sdk_key in
                   stream_json['data']):
                available_types.append('backup')
            plist = []
            for line_type in available_types:
                format_arrays = {'flv': [], 'hls': [], 'lls': []}
                qualities = sorted(resolution_data, key=lambda x: x['level'], reverse=True)
                for quality in qualities:
                    sdk_key = quality['sdk_key']
                    if sdk_key in stream_json['data'] and line_type in stream_json['data'][sdk_key]:
                        stream_info = stream_json['data'][sdk_key][line_type]
                        if stream_info.get('flv'):
                            format_arrays['flv'].extend([quality['name'], stream_info['flv']])
                        if stream_info.get('hls'):
                            format_arrays['hls'].extend([quality['name'], stream_info['hls']])
                        if stream_info.get('lls'):
                            format_arrays['lls'].extend([quality['name'], stream_info['lls']])
                format_urls = []
                for format_name, url_array in format_arrays.items():
                    if url_array:
                        encoded_urls = self.e64(json.dumps(url_array))
                        format_urls.append(f"{format_name}${ids[0]}@@{encoded_urls}")

                if format_urls:
                    plist.append('#'.join(format_urls))

            names = ['线路1', '线路2'][:len(plist)]
            vod['vod_play_from'] = "$$$".join(names)
            vod['vod_play_url'] = "$$$".join(plist)
            return vod

        except Exception as e:
            return self.handle_exception(e)

    def douyuDetail(self, ids):
        headers = self.gethr(0, zr=f'{self.hosts[ids[0]]}/{ids[1]}')
        try:
            data = self.fetch(f'{self.hosts[ids[0]]}/betard/{ids[1]}', headers=headers).json()
            vname = data['room']['room_name']
            vod = self.buildvod(
                vod_name=vname,
                vod_remarks=data['room'].get('second_lvl_name'),
                vod_director=data['room'].get('nickname'),
            )
            vdata = self.fetch(f'{self.hosts[ids[0]]}/swf_api/homeH5Enc?rids={ids[1]}', headers=headers).json()
            json_body = vdata['data']
            json_body = {"html": self.douyu_text(json_body[f'room{ids[1]}']), "rid": ids[1]}
            sign = self.post('http://alive.nsapps.cn/api/AllLive/DouyuSign', json=json_body, headers=self.headers[1]).json()['data']
            body = f'{sign}&cdn=&rate=-1&ver=Douyu_223061205&iar=1&ive=1&hevc=0&fa=0'
            body=self.params_to_json(body)
            nubdata = self.post(f'{self.hosts[ids[0]]}/lapi/live/getH5Play/{ids[1]}', data=body, headers=headers).json()
            plist = []
            names = []
            for i,x in enumerate(nubdata['data']['cdnsWithName']):
                names.append(f'线路{i+1}')
                d = {'sign': sign, 'cdn': x['cdn'], 'id': ids[1]}
                plist.append(
                    f'{vname}${ids[0]}@@{self.e64(json.dumps(d))}@@{self.e64(json.dumps(nubdata["data"]["multirates"]))}')
            vod['vod_play_from'] = "$$$".join(names)
            vod['vod_play_url'] = "$$$".join(plist)
            return vod
        except Exception as e:
            return self.handle_exception(e)

    def douyu_text(self, text):
        function_positions = [m.start() for m in re.finditer('function', text)]
        total_functions = len(function_positions)
        if total_functions % 2 == 0:
            target_index = total_functions // 2 + 1
        else:
            target_index = (total_functions - 1) // 2 + 1
        if total_functions >= target_index:
            cut_position = function_positions[target_index - 1]
            ctext = text[4:cut_position]
            return re.sub(r'eval\(strc\)\([\w\d,]+\)', 'strc', ctext)
        return text

    def searchContent(self, key, quick, pg="1"):
        pass

    def playerContent(self, flag, id, vipFlags):
        try:
            ids = id.split('@@')
            p = 1
            if ids[0] in ['wangyi', 'douyin','huya']:
                p, url = 0, json.loads(self.d64(ids[1]))
            elif ids[0] == 'bili':
                p, url = self.biliplay(ids)
            elif ids[0] == 'huya':
                p, url = 0, json.loads(self.d64(ids[1]))
            elif ids[0] == 'douyu':
                p, url = self.douyuplay(ids)
            return {'parse': p, 'url': url, 'header': self.playheaders[ids[0]]}
        except Exception as e:
            return {'parse': 1, 'url': self.excepturl, 'header': self.headers[0]}

    def biliplay(self, ids):
        try:
            data = self.fetch(
                f'{self.hosts[ids[0]][0]}/xlive/web-room/v2/index/getRoomPlayInfo?room_id={ids[1]}&protocol=0,1&format=0,2&codec=0&platform=web&qn={ids[2]}',
                headers=self.gethr(0, ids[0])).json()
            urls = []
            line_index = 1
            for stream in data['data']['playurl_info']['playurl']['stream']:
                for format_item in stream['format']:
                    for codec in format_item['codec']:
                        for url_info in codec['url_info']:
                            full_url = f"{url_info['host']}/{codec['base_url'].lstrip('/')}{url_info['extra']}"
                            urls.extend([f"线路{line_index}", full_url])
                            line_index += 1
            return 0, urls
        except Exception as e:
            return 1, self.excepturl

    def douyuplay(self, ids):
        try:
            sdata = json.loads(self.d64(ids[1]))
            headers = self.gethr(0, zr=f'{self.hosts[ids[0]]}/{sdata["id"]}')
            ldata = json.loads(self.d64(ids[2]))
            result_obj = {}
            with ThreadPoolExecutor(max_workers=len(ldata)) as executor:
                futures = [
                    executor.submit(
                        self.douyufp,
                        sdata,
                        quality,
                        headers,
                        self.hosts[ids[0]],
                        result_obj
                    ) for quality in ldata
                ]
                for future in futures:
                    future.result()

            result = []
            for bit in sorted(result_obj.keys(), reverse=True):
                result.extend(result_obj[bit])

            if result:
                return 0, result
            return 1, self.excepturl

        except Exception as e:
            return 1, self.excepturl

    def douyufp(self, sdata, quality, headers, host, result_obj):
        try:
            body = f'{sdata["sign"]}&cdn={sdata["cdn"]}&rate={quality["rate"]}'
            body=self.params_to_json(body)
            data = self.post(f'{host}/lapi/live/getH5Play/{sdata["id"]}',
                             data=body, headers=headers).json()
            if data.get('data'):
                play_url = data['data']['rtmp_url'] + '/' + data['data']['rtmp_live']
                bit = quality.get('bit', 0)
                if bit not in result_obj:
                    result_obj[bit] = []
                result_obj[bit].extend([quality['name'], play_url])
        except Exception as e:
            print(f"Error fetching {quality['name']}: {str(e)}")

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

