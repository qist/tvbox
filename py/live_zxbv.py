# -*- coding: utf-8 -*-
# @Author  : Doubebly
# @Time    : 2025/10/9 18:16
import sys
import requests
import json
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):
    def getName(self):
        return self.vod.name

    def init(self, extend):
        self.vod = Vod(extend, self.getProxyUrl())

    def getDependence(self):
        return []

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def liveContent(self, url):
        return self.vod.liveContent(url)

    def homeContent(self, filter):
        return self.vod.homeContent(filter)

    def homeVideoContent(self):
        return self.vod.homeVideoContent()

    def categoryContent(self, cid, page, filter, ext):
        return self.vod.categoryContent(cid, page, filter, ext)

    def detailContent(self, did):
        return self.vod.detailContent(did)

    def searchContent(self, key, quick, page='1'):
        return self.vod.searchContent(key, quick, page)

    def playerContent(self, flag, pid, vipFlags):
        return self.vod.playerContent(flag, pid, vipFlags)

    def localProxy(self, params):
        pass

    def destroy(self):
        return '正在Destroy'


class Vod:
    def __init__(self, extend='{}', proxy_url=""):

        self.debug = False
        self.getProxyUrl = proxy_url

        self.name = '央视直播'
        self.error_play_url = 'https://sf1-cdn-tos.huoshanstatic.com/obj/media-fe/xgplayer_doc_video/mp4/xgplayer-demo-720p.mp4'
        self.home_url = 'https://zxbv5123.xymjzxyey.com/assets/js/tv.js'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
        }

    def homeContent(self, filter):
        return {}

    def homeVideoContent(self):
        return {'list': [], 'parse': 0, 'jx': 0}

    def categoryContent(self, cid, page, filter, ext):
        data_list = []
        data_list.append(
            {
                'vod_id': '',
                'vod_name': '',
                'vod_pic': '',
                'vod_remarks': ''
            }
        )
        return {'list': [], 'parse': 0, 'jx': 0}

    def detailContent(self, did):
        ids = did[0]
        video_list = []
        video_list.append(
            {
                'type_name': '',
                'vod_id': ids,
                'vod_name': '',
                'vod_remarks': '',
                'vod_year': '',
                'vod_area': '',
                'vod_actor': '',
                'vod_director': '',
                'vod_content': '',
                'vod_play_from': '',
                'vod_play_url': ''

            }
        )
        return {"list": video_list, 'parse': 0, 'jx': 0}

    def searchContent(self, key, quick, page='1'):
        return {'list': [], 'parse': 0, 'jx': 0}

    def playerContent(self, flag, pid, vipFlags):
        return {'url': self.error_play_url, 'parse': 0, 'jx': 0}

    def liveContent(self, url):
        data_list = self.get_js_data()
        tv_list = ['#EXTM3U']
        for data in data_list:
            for i in data['tvlist']:
                tvg_id = i['id']
                tvg_name = i['title']
                tvg_logo = i['logo']
                group_name = data['groupname']
                name = i['title']
                url = i['vurl']
                tv_list.append(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{tvg_name}" tvg-logo="{tvg_logo}" group-title="{group_name}",{name}')
                tv_list.append(url)

        return '\n'.join(tv_list)

    def get_js_data(self):
        response = requests.get(self.home_url, headers=self.headers)
        js_code = response.text
        try:
            from com.whl.quickjs.wrapper import QuickJSContext
            ctx = QuickJSContext.create()
            result = ctx.evaluate(f"{js_code}\nJSON.stringify(tvdata);")
            ctx.destroy()
            return json.loads(result)

        except Exception as e:
            self.log(f"执行失败: {e}")
            return []

    def log(self,  msg):
        if self.debug:
            try:
                requests.post('http://192.168.31.12:5000/log', data=msg, timeout=1)
            except Exception as e:
                print(e)

if __name__ == '__main__':
    pass