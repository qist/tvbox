# coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import json
import time
import urllib.parse
import re
import requests
from lxml import etree

class Spider(Spider):
    def getName(self):
        return "四虎视频"

    def init(self, extend=""):
        self.baseUrl = "https://www.sihuhu.xyz"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Referer": self.baseUrl
        }

    def homeContent(self, filter):
        result = {}
        # 从HTML中提取分类信息
        cateManual = {
            "传媒厂商": "20",
            "麻豆传媒": "21",
            "91制片": "22",
            "蜜桃传媒": "23",
            "天美传媒": "24",
            "精东影片": "25",
            "星空传媒": "26",
            "葫芦影业": "27",
            "糖心VLOG": "28",
            "精品推荐": "29",
            "日本无码": "30",
            "日本有码": "31",
            "AV解说": "32",
            "中文有码": "33",
            "中文无码": "34",
            "日韩极品": "35",
            "日韩无码": "36",
            "少女萝莉": "37",
            "水嫩萝莉": "38",
            "极品主播": "40",
            "卡通动漫": "43",
            "SM调教": "44",
            "探花合集": "50",
            "91大神": "51",
            "台湾萝莉": "54",
            "萝莉传媒": "55",
            "白虎口爆": "57",
            "嫩女网爆": "47",
            "嫩逼乌鸡": "42",
            "少女伦理": "45",
            "萝莉互口": "46",
            "黑料网爆": "48",
            "野战车震": "52",
            "萝莉黑瓜": "53",
            "萝莉巨乳": "58",
            "明星换脸": "73",
            "萝莉抠逼": "56",
            "国产大作": "39",
            "欧美萝莉": "41",
            "热门事件": "49",
            "少女3P": "59",
            "偷拍萝莉": "60",
            "强奸少女": "61",
            "重口猎奇": "62",
            "制服萝控": "63",
            "极品少女": "64",
            "明星爆料": "65",
            "X短视频": "66",
            "AV明星": "67",
            "极品萝莉": "68",
            "人妻艹妈": "69",
            "VR视角": "70",
            "角色扮演": "71",
            "男同男娘": "72"
        }
        classes = []
        for k in cateManual:
            classes.append({
                'type_name': k,
                'type_id': cateManual[k]
            })
        result['class'] = classes
        return result

    def homeVideoContent(self):
        result = {}
        # 尝试获取首页推荐视频
        try:
            rsp = self.fetch(self.baseUrl, headers=self.headers)
            html = etree.HTML(rsp.text)
            
            videos = []
            # 尝试解析首页视频列表
            video_elements = html.xpath('//ul[@class="thumbnail-group clearfix"]/li')
            for element in video_elements:
                try:
                    name = element.xpath('.//h5/a/text()')[0].strip()
                    pic = element.xpath('.//img/@data-original')[0]
                    if not pic.startswith('http'):
                        pic = self.baseUrl + pic
                    href = element.xpath('.//a[@class="thumbnail"]/@href')[0]
                    vid = href.split('/')[-1].replace('.html', '')
                    remark = element.xpath('.//span[@class="title"]/text()')
                    remark = remark[0] if remark else ""
                    
                    videos.append({
                        "vod_id": vid,
                        "vod_name": name,
                        "vod_pic": pic,
                        "vod_remarks": remark
                    })
                except:
                    continue
            
            result['list'] = videos
        except:
            result['list'] = []
        
        return result

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        url = f'{self.baseUrl}/vod/type/id/{tid}/page/{pg}.html'
        rsp = self.fetch(url, headers=self.headers)
        html = etree.HTML(rsp.text)
        
        vodList = []
        video_elements = html.xpath('//ul[@class="thumbnail-group clearfix"]/li')
        for element in video_elements:
            try:
                name = element.xpath('.//h5/a/text()')[0].strip()
                pic = element.xpath('.//img/@data-original')[0]
                if not pic.startswith('http'):
                    pic = self.baseUrl + pic
                href = element.xpath('.//a[@class="thumbnail"]/@href')[0]
                vid = href.split('/')[-1].replace('.html', '')
                remark = element.xpath('.//span[@class="title"]/text()')
                remark = remark[0] if remark else ""
                
                vodList.append({
                    "vod_id": vid,
                    "vod_name": name,
                    "vod_pic": pic,
                    "vod_remarks": remark
                })
            except:
                continue
                
        result['list'] = vodList
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 20
        result['total'] = 999999
        return result

    def detailContent(self, array):
        tid = array[0]
        url = f'{self.baseUrl}/vod/detail/id/{tid}.html'
        rsp = self.fetch(url, headers=self.headers)
        html = etree.HTML(rsp.text)
        
        # 获取视频详情
        title = html.xpath('//title/text()')[0].replace(' - 四虎视频', '')
        pic = html.xpath('//meta[@property="og:image"]/@content')
        pic = pic[0] if pic else ""
        desc = html.xpath('//meta[@name="description"]/@content')
        desc = desc[0] if desc else ""
        
        # 获取播放列表 - 修复播放地址获取
        play_from = []
        play_url = []
        
        # 尝试获取所有播放源
        play_sources = html.xpath('//div[@class="module-play-list"]/div')
        for source in play_sources:
            source_name = source.xpath('.//span/text()')
            if source_name:
                source_name = source_name[0].strip()
                play_from.append(source_name)
                
                # 获取该源下的所有剧集
                episodes = source.xpath('.//a')
                episode_urls = []
                for episode in episodes:
                    ep_name = episode.xpath('./text()')[0].strip()
                    ep_href = episode.xpath('./@href')[0]
                    episode_urls.append(f"{ep_name}${self.baseUrl}{ep_href}")
                
                play_url.append("#".join(episode_urls))
        
        # 如果没有找到播放源，使用默认方式
        if not play_from:
            play_from = ["默认"]
            play_page_url = f"{self.baseUrl}/vod/play/id/{tid}/sid/1/nid/1.html"
            play_url.append(f"第1集${play_page_url}")
        
        vod = {
            "vod_id": tid,
            "vod_name": title,
            "vod_pic": pic,
            "vod_content": desc,
            "vod_play_from": "$$$".join(play_from),
            "vod_play_url": "$$$".join(play_url)
        }
        
        return {'list': [vod]}

    def searchContent(self, key, quick):
        result = {}
        url = f'{self.baseUrl}/vod/search/page/1/wd/{urllib.parse.quote(key)}.html'
        rsp = self.fetch(url, headers=self.headers)
        html = etree.HTML(rsp.text)
        
        vodList = []
        video_elements = html.xpath('//ul[@class="thumbnail-group clearfix"]/li')
        for element in video_elements:
            try:
                name = element.xpath('.//h5/a/text()')[0].strip()
                pic = element.xpath('.//img/@data-original')[0]
                if not pic.startswith('http'):
                    pic = self.baseUrl + pic
                href = element.xpath('.//a[@class="thumbnail"]/@href')[0]
                vid = href.split('/')[-1].replace('.html', '')
                remark = element.xpath('.//span[@class="title"]/text()')
                remark = remark[0] if remark else ""
                
                vodList.append({
                    "vod_id": vid,
                    "vod_name": name,
                    "vod_pic": pic,
                    "vod_remarks": remark
                })
            except:
                continue
                
        result['list'] = vodList
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {}
        # 解析播放地址
        url = f'{self.baseUrl}{id}' if id.startswith('/') else id
        
        # 检查是否已经是m3u8链接
        if id.endswith('.m3u8'):
            result["parse"] = 0
            result["playUrl"] = ""
            result["url"] = id
            result["header"] = json.dumps(self.headers)
            return result
            
        rsp = self.fetch(url, headers=self.headers)
        
        # 方法1: 尝试从JavaScript变量中提取播放信息
        pattern = r'var player_aaaa\s*=\s*({.*?});'
        match = re.search(pattern, rsp.text, re.DOTALL)
        
        if match:
            try:
                player_info = json.loads(match.group(1))
                video_url = player_info.get('url', '')
                
                if video_url:
                    # 处理转义字符
                    video_url = video_url.replace('\\/', '/')
                    result["parse"] = 0
                    result["playUrl"] = ""
                    result["url"] = video_url
                    result["header"] = json.dumps(self.headers)
                    return result
            except:
                pass
        
        # 方法2: 尝试从JavaScript中找到url字段
        url_patterns = [
            r'"url"\s*:\s*"([^"]+)"',
            r"url\s*:\s*'([^']+)'",
            r'video_url\s*:\s*"([^"]+)"',
            r"video_url\s*:\s*'([^']+)'"
        ]
        
        for pattern in url_patterns:
            match = re.search(pattern, rsp.text)
            if match:
                video_url = match.group(1).replace('\\/', '/')
                if video_url and ('m3u8' in video_url or 'mp4' in video_url):
                    result["parse"] = 0
                    result["playUrl"] = ""
                    result["url"] = video_url
                    result["header"] = json.dumps(self.headers)
                    return result
        
        # 方法3: 尝试从iframe中提取视频地址
        iframe_pattern = r'<iframe[^>]+src="([^"]+)"'
        iframe_match = re.search(iframe_pattern, rsp.text)
        if iframe_match:
            iframe_src = iframe_match.group(1)
            if iframe_src.startswith('//'):
                iframe_src = 'https:' + iframe_src
            elif iframe_src.startswith('/'):
                iframe_src = self.baseUrl + iframe_src
                
            # 递归获取iframe内容
            return self.playerContent(flag, iframe_src, vipFlags)
        
        # 如果以上方法都失败，返回原始页面供进一步解析
        result["parse"] = 1
        result["playUrl"] = ""
        result["url"] = url
        result["header"] = json.dumps(self.headers)
        
        return result

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def localProxy(self, param):
        return []