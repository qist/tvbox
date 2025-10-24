# -*- coding: utf-8 -*-
# @Author  : Doubebly
# @Time    : 2025/1/21 23:07

import hashlib
import re
import sys
import time
import requests
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):
    def getName(self):
        return "JieYingShi"

    def init(self, extend):
        self.home_url = 'https://www.hkybqufgh.com'
        self.error_url = 'https://json.doube.eu.org/error/4gtv/index.m3u8'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }

    def getDependence(self):
        return []

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):

        return {'class': [
            {
                'type_id': '1',
                'type_name': '电影'
            },
            {
                'type_id': '2',
                'type_name': '电视剧'
            },
            {
                'type_id': '4',
                'type_name': '动漫'
            },
            {
                'type_id': '3',
                'type_name': '综艺'
            }
        ]}

    def homeVideoContent(self):
        a = self.get_data(self.home_url)
        return {'list': a, 'parse': 0, 'jx': 0}

    def categoryContent(self, cid, page, filter, ext):
        url = self.home_url + f'/vod/show/id/{cid}/page/{page}'
        data = self.get_data(url)
        return {'list': data, 'parse': 0, 'jx': 0}


    def detailContent(self, did):
        ids = did[0]
        data = self.get_detail_data(ids)
        return {"list": data, 'parse': 0, 'jx': 0}

    def searchContent(self, key, quick, page='1'):
        if int(page) > 1:
            return {'list': [], 'parse': 0, 'jx': 0}
        url = self.home_url + f'/vod/search/{key}'
        data = self.get_data(url)
        return {'list': data, 'parse': 0, 'jx': 0}

    def playerContent(self, flag, pid, vipFlags):
        url = self.get_play_data(pid)
        return {"url": url, "header": self.headers, "parse": 1, "jx": 0}

    def localProxy(self, params):
        pass

    def destroy(self):
        return '正在Destroy'


    def get_data(self, url):
        data = []
        try:
            res = requests.get(url, headers=self.headers)
            if res.status_code != 200:
                return data
            vod_id_s = re.findall(r'\\"vodId\\":(.*?),', res.text)
            vod_name_s = re.findall(r'\\"vodName\\":\\"(.*?)\\"', res.text)
            vod_pic_s = re.findall(r'\\"vodPic\\":\\"(.*?)\\"', res.text)
            vod_remarks_s = re.findall(r'\\"vodRemarks\\":\\"(.*?)\\"', res.text)

            for i in range(len(vod_id_s)):
                data.append(
                    {
                        'vod_id': vod_id_s[i],
                        'vod_name': vod_name_s[i],
                        'vod_pic': vod_pic_s[i],
                        'vod_remarks': vod_remarks_s[i],
                    }
                )
        except requests.RequestException as e:
            print(e)
        return data

    def get_detail_data(self, ids):
        url = self.home_url + f'/api/mw-movie/anonymous/video/detail?id={ids}'
        t = str(int(time.time() * 1000))
        headers = self.get_headers(t, f'id={ids}&key=cb808529bae6b6be45ecfab29a4889bc&t={t}')
        try:
            res = requests.get(url, headers=headers)
            if res.status_code != 200:
                return []
            i = res.json()['data']
            urls = []
            for ii in res.json()['data']['episodeList']:
                name = ii['name']
                url = ii['nid']
                urls.append(f'{name}${ids}-{url}')
            data = {
                'type_name': i['vodClass'],
                'vod_id': i['vodId'],
                'vod_name': i['vodName'],
                'vod_remarks': i['vodRemarks'],
                'vod_year': i['vodYear'],
                'vod_area': i['vodArea'],
                'vod_actor': i['vodActor'],
                'vod_director': i['vodDirector'],
                'vod_content': i['vodContent'],
                'vod_play_from': '默认',
                'vod_play_url': '#'.join(urls),

            }
            return [data]

        except requests.RequestException as e:
            print(e)
        return []

    def get_play_data(self, play):
        info = play.split('-')
        _id = info[0]
        _pid = info[1]
        url = self.home_url + f'/api/mw-movie/anonymous/v2/video/episode/url?id={_id}&nid={_pid}'
        t = str(int(time.time() * 1000))
        headers = self.get_headers(t, f'id={_id}&nid={_pid}&key=cb808529bae6b6be45ecfab29a4889bc&t={t}')
        try:
            res = requests.get(url, headers=headers)
            if res.status_code != 200:
                return self.error_url
            return res.json()['data']['list'][0]['url']
        except requests.RequestException as e:
            print(e)
        return self.error_url

    @staticmethod
    def get_headers(t, e):
        sign = hashlib.sha1(hashlib.md5(e.encode()).hexdigest().encode()).hexdigest()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'sign': sign,
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            't': t,
            'referer': 'https://www.hkybqufgh.com/',
        }
        return headers

if __name__ == '__main__':
    pass




