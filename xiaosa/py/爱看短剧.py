# -*- coding: utf-8 -*-
# by @嗷呜
import json
import sys
from pyquery import PyQuery as pq
sys.path.append('..')
from base.spider import Spider

class Spider(Spider):

    def init(self, extend=""):
        pass

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    host='http://www.toule.top'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Referer':f'{host}/',
        'Origin':host
    }

    def homeContent(self, filter):
        data=self.getpq()
        result = {}
        classes = []
        for k in data('.swiper-wrapper .swiper-slide').items():
            classes.append({
                'type_name': k.text(),
                'type_id': k.text()
            })
        result['class'] = classes
        result['list'] = self.getlist(data('.container.items ul li'))
        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        data=self.getpq(f"/index.php/vod/show/class/{tid}/id/1/page/{pg}.html")
        result = {}
        result['list'] = self.getlist(data('.container.items ul li'))
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        data=self.getpq(ids[0])
        v=data('.container.detail-content')
        vod = {
            'vod_remarks': v('.items-tags a').text(),
            'vod_content': v('.text-content .detail').text(),
            'vod_play_from': '爱看短剧',
            'vod_play_url': '#'.join([f"{i.text()}${i('a').attr('href')}" for i in data('.swiper-wrapper .swiper-slide').items()])
        }
        return {'list':[vod]}

    def searchContent(self, key, quick, pg="1"):
        data=self.getpq(f"/index.php/vod/search/page/{pg}/wd/{key}.html")
        return {'list':self.getlist(data('.container.items ul li')),'page':pg}

    def playerContent(self, flag, id, vipFlags):
        data=self.getpq(id)
        try:
            jstr=data('.player-content script').eq(0).text()
            jt=json.loads(jstr.split('=',1)[-1])
            p,url=0,jt['url']
        except Exception as e:
            print(f"获取播放地址失败: {e}")
            p,url=1,f'{self.host}{id}'
        return  {'parse': p, 'url': url, 'header': self.headers}

    def localProxy(self, param):
        pass

    def liveContent(self, url):
        pass

    def getpq(self, path=''):
        data=self.fetch(f"{self.host}{path}",headers=self.headers).text
        try:
            return pq(data)
        except Exception as e:
            print(f"{str(e)}")
            return pq(data.encode('utf-8'))

    def getlist(self,data):
        videos = []
        for i in data.items():
            videos.append({
                'vod_id': i('.image-line').attr('href'),
                'vod_name': i('img').attr('alt'),
                'vod_pic': i('img').attr('src'),
                'vod_remarks': i('.remarks.light').text()
            })
        return videos