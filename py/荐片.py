# -*- coding: utf-8 -*-
import json
import sys
sys.path.append('..')
from base.spider import Spider
import requests

class Spider(Spider):
    def init(self, extend=""):
        self.host = 'https://ev5356.970xw.com'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 9; V2196A Build/PQ3A.190705.08211809; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.114 Mobile Safari/537.36;webank/h5face;webank/1.0;netType:NETWORK_WIFI;appVersion:416;packageName:com.jp3.xg3',
            'Referer': self.host
        }
        self.ihost = self.imgsite()
        self.skey = ''
        self.stype = '3'

    def getName(self):
        return "JianPian"

    def imgsite(self):
        data = requests.get(f"{self.host}/api/appAuthConfig", headers=self.headers).json()
        host = data['data']['imgDomain']
        return f"https://{host}" if not host.startswith('http') else host

    def homeContent(self, filter):
        classes = [
            {'type_id': '1', 'type_name': '电影'},
            {'type_id': '2', 'type_name': '电视剧'},
            {'type_id': '3', 'type_name': '动漫'},
            {'type_id': '4', 'type_name': '综艺'}
        ]
        filterObj = {
            "1": [
                {"key": "cateId", "name": "分类", "value": [
                    {"v": "1", "n": "剧情"}, {"v": "2", "n": "爱情"}, {"v": "3", "n": "动画"}, {"v": "4", "n": "喜剧"},
                    {"v": "5", "n": "战争"}, {"v": "6", "n": "歌舞"}, {"v": "7", "n": "古装"}, {"v": "8", "n": "奇幻"},
                    {"v": "9", "n": "冒险"}, {"v": "10", "n": "动作"}, {"v": "11", "n": "科幻"}, {"v": "12", "n": "悬疑"},
                    {"v": "13", "n": "犯罪"}, {"v": "14", "n": "家庭"}, {"v": "15", "n": "传记"}, {"v": "16", "n": "运动"},
                    {"v": "18", "n": "惊悚"}, {"v": "20", "n": "短片"}, {"v": "21", "n": "历史"}, {"v": "22", "n": "音乐"},
                    {"v": "23", "n": "西部"}, {"v": "24", "n": "武侠"}, {"v": "25", "n": "恐怖"}
                ]},
                {"key": "area", "name": "地區", "value": [
                    {"v": "1", "n": "国产"}, {"v": "3", "n": "香港"}, {"v": "6", "n": "台湾"},
                    {"v": "5", "n": "美国"}, {"v": "18", "n": "韩国"}, {"v": "2", "n": "日本"}
                ]},
                {"key": "year", "name": "年代", "value": [
                    {"v": "107", "n": "2025"}, {"v": "119", "n": "2024"}, {"v": "153", "n": "2023"},
                    {"v": "101", "n": "2022"}, {"v": "118", "n": "2021"}, {"v": "16", "n": "2020"},
                    {"v": "7", "n": "2019"}, {"v": "2", "n": "2018"}, {"v": "3", "n": "2017"},
                    {"v": "22", "n": "2016"}, {"v": "2015", "n": "2015以前"}
                ]},
                {"key": "sort", "name": "排序", "value": [
                    {"v": "update", "n": "最新"}, {"v": "hot", "n": "最热"}, {"v": "rating", "n": "评分"}
                ]}
            ],
            "2": [
                {"key": "area", "name": "地區", "value": [
                    {"v": "1", "n": "国产"}, {"v": "3", "n": "香港"}, {"v": "6", "n": "台湾"},
                    {"v": "5", "n": "美国"}, {"v": "18", "n": "韩国"}, {"v": "2", "n": "日本"}
                ]},
                {"key": "year", "name": "年代", "value": [
                    {"v": "107", "n": "2025"}, {"v": "119", "n": "2024"}, {"v": "153", "n": "2023"},
                    {"v": "101", "n": "2022"}, {"v": "118", "n": "2021"}, {"v": "16", "n": "2020"},
                    {"v": "7", "n": "2019"}, {"v": "2", "n": "2018"}, {"v": "3", "n": "2017"},
                    {"v": "22", "n": "2016"}, {"v": "2015", "n": "2015以前"}
                ]},
                {"key": "sort", "name": "排序", "value": [
                    {"v": "update", "n": "最新"}, {"v": "hot", "n": "最热"}, {"v": "rating", "n": "评分"}
                ]}
            ],
            "3": [
                {"key": "area", "name": "地區", "value": [
                    {"v": "1", "n": "国产"}, {"v": "3", "n": "香港"}, {"v": "6", "n": "台湾"},
                    {"v": "5", "n": "美国"}, {"v": "18", "n": "韩国"}, {"v": "2", "n": "日本"}
                ]},
                {"key": "year", "name": "年代", "value": [
                    {"v": "107", "n": "2025"}, {"v": "119", "n": "2024"}, {"v": "153", "n": "2023"},
                    {"v": "101", "n": "2022"}, {"v": "118", "n": "2021"}, {"v": "16", "n": "2020"},
                    {"v": "7", "n": "2019"}, {"v": "2", "n": "2018"}, {"v": "3", "n": "2017"},
                    {"v": "22", "n": "2016"}, {"v": "2015", "n": "2015以前"}
                ]},
                {"key": "sort", "name": "排序", "value": [
                    {"v": "update", "n": "最新"}, {"v": "hot", "n": "最热"}, {"v": "rating", "n": "评分"}
                ]}
            ],
            "4": [
                {"key": "area", "name": "地區", "value": [
                    {"v": "1", "n": "国产"}, {"v": "3", "n": "香港"}, {"v": "6", "n": "台湾"},
                    {"v": "5", "n": "美国"}, {"v": "18", "n": "韩国"}, {"v": "2", "n": "日本"}
                ]},
                {"key": "year", "name": "年代", "value": [
                    {"v": "107", "n": "2025"}, {"v": "119", "n": "2024"}, {"v": "153", "n": "2023"},
                    {"v": "101", "n": "2022"}, {"v": "118", "n": "2021"}, {"v": "16", "n": "2020"},
                    {"v": "7", "n": "2019"}, {"v": "2", "n": "2018"}, {"v": "3", "n": "2017"},
                    {"v": "22", "n": "2016"}, {"v": "2015", "n": "2015以前"}
                ]},
                {"key": "sort", "name": "排序", "value": [
                    {"v": "update", "n": "最新"}, {"v": "hot", "n": "最热"}, {"v": "rating", "n": "评分"}
                ]}
            ]
        }
        return {
            'class': classes,
            'filters': filterObj
        }

    def homeVideoContent(self):
        url = f"{self.host}/api/slide/list?pos_id=88"
        data = requests.get(url, headers=self.headers).json()
        videos = [{
            'vod_id': item['jump_id'],
            'vod_name': item['title'],
            'vod_pic': f"{self.ihost}{item['thumbnail']}",
            'vod_remarks': "",
            'style': json.dumps({"type": "rect", "ratio": 1.33})
        } for item in data['data']]
        return {'list': videos}

    def categoryContent(self, tid, pg, filter, extend):
        params = {
            'fcate_pid': tid,
            'page': pg,
            'category_id': extend.get('cateId', ''),
            'area': extend.get('area', ''),
            'year': extend.get('year', ''),
            'type': extend.get('cateId', ''),
            'sort': extend.get('sort', '')
        }
        url = f"{self.host}/api/crumb/list"
        data = requests.get(url, params=params, headers=self.headers).json()
        videos = [{
            'vod_id': item['id'],
            'vod_name': item['title'],
            'vod_pic': f"{self.ihost}{item['path']}",
            'vod_remarks': item['mask'],
            'vod_year': ""
        } for item in data['data']]
        return {
            'list': videos,
            'page': pg,
            'pagecount': 99999,
            'limit': 15,
            'total': 99999
        }

    def detailContent(self, ids):
        id = ids[0]
        url = f"{self.host}/api/video/detailv2?id={id}"
        data = requests.get(url, headers=self.headers).json()
        res = data['data']
        
        play_from = ['边下边播']
        play_url = []
        
        # 寻找并处理“常规线路”
        for source in res.get('source_list_source', []):
            if source['name'] == '常规线路':
                parts = [f"{part.get('source_name', part.get('weight', ''))}${part['url']}" for part in source.get('source_list', [])]
                play_url.append('#'.join(parts))
                break  # 找到后立即退出循环
        
        vod = {
            'vod_id': id,
            'type_name': '/'.join([t['name'] for t in res.get('types', [])]),
            'vod_year': res.get('year', ''),
            'vod_area': res.get('area', ''),
            'vod_remarks': res.get('mask', ''),
            'vod_content': res.get('description', ''),
            'vod_play_from': '$$$'.join(play_from),
            'vod_play_url': '$$$'.join(play_url)
        }
        return {'list': [vod]}

    def playerContent(self, flag, id, vipFlags):
        if ".m3u8" in id:
            return {'parse': 0, 'url': id}
        else:
            return {'parse': 0, 'url': f"tvbox-xg:{id}"}

    def searchContent(self, key, quick, pg="1"):
        url = f"{self.host}/api/v2/search/videoV2"
        params = {'key': key, 'category_id': 88, 'page': pg, 'pageSize': 20}
        data = requests.get(url, params=params, headers=self.headers).json()
        key_lower = key.lower()
        filtered_items = [item for item in data['data'] if key_lower in item['title'].lower()]

        videos = [{
            'vod_id': item['id'],
            'vod_name': item['title'],
            'vod_pic': f"{self.ihost}{item['thumbnail']}",
            'vod_remarks': item.get('mask', ''),
            'vod_year': ""
        } for item in filtered_items]

        return {
            'list': videos,
            'limit': 20
        }

    def isVideoFormat(self, url): pass
    def manualVideoCheck(self): pass
    def destroy(self): pass
    def localProxy(self, param): pass
    def liveContent(self, url): pass