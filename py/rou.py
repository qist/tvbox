# -*- coding: utf-8 -*-
# @Author  : Doubebly
# @Time    : 2025/1/20 14:55

import sys
import requests
from lxml import etree

sys.path.append('..')
from base.spider import Spider


class Spider(Spider):
    def getName(self):
        return "Rou"

    def init(self, extend):
        self.home_url = 'https://rou.video'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

    def getDependence(self):
        return []

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        url = self.home_url + '/cat'
        try:
            res = requests.get(url, headers=self.headers)
            if res.status_code != 200:
                return {'class': [], 'msg': f'status_code: {res.status_code}'}
            root = etree.HTML(res.text.encode('utf-8'))
            name_list = root.xpath('//div[@class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3"]/a/text()')
            url_list = root.xpath('//div[@class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3"]/a/@href')
            if len(name_list) < 1 or len(url_list) < 1:
                return {'class': [], 'msg': '获取的数据为空'}
            a = []
            for name, url in zip(name_list, url_list):
                a.append({'type_name': name, 'type_id': url})
            return {'class': a}
        except requests.exceptions.RequestException as e:
            return {'class': [], 'msg': str(e)}

    def homeVideoContent(self):
        url = self.home_url + '/home'
        try:
            res = requests.get(url, headers=self.headers)
            if res.status_code != 200:
                return {'list': [], 'parse': 0, 'jx': 0, 'msg': f'status_code: {res.status_code}'}
            root = etree.HTML(res.text.encode('utf-8'))
            data_list = root.xpath('//div[@class="aspect-video relative"]/a')
            if len(data_list) < 1:
                return {'list': [], 'parse': 0, 'jx': 0, 'msg': '获取的数据为空'}
            a = []
            for i in data_list:
                vod_remarks = i.xpath('./div[2]/text()')
                vod_year = i.xpath('./div[3]/text()')
                vod_name = i.xpath('./img/@alt')

                a.append(
                    {
                        'vod_id': i.xpath('./@href')[0],
                        'vod_name': vod_name[0] if len(vod_name[0]) > 0 else vod_name[1],
                        'vod_pic': i.xpath('./img/@src')[0],
                        'vod_remarks': vod_remarks[0] if vod_remarks else '',
                        'vod_year': vod_year[0] if vod_year else '',
                        'style': {"type": "rect", "ratio": 1.5}
                    }
                )
            return {'list': a, 'parse': 0, 'jx': 0}
        except requests.exceptions.RequestException as e:
            return {'list': [], 'parse': 0, 'jx': 0, 'msg': str(e)}

    def categoryContent(self, cid, page, filter, ext):
        url = f'{self.home_url}{cid}?order=createdAt&page={page}'
        try:
            res = requests.get(url, headers=self.headers)
            if res.status_code != 200:
                return {'list': [], 'parse': 0, 'jx': 0, 'msg': f'status_code: {res.status_code}'}
            root = etree.HTML(res.text.encode('utf-8'))
            data_list = root.xpath('//div[@class="aspect-video relative"]/a')
            if len(data_list) < 1:
                return {'list': [], 'parse': 0, 'jx': 0, 'msg': '获取的数据为空'}
            a = []
            for i in data_list:
                vod_remarks = i.xpath('./div[2]/text()')
                vod_year = i.xpath('./div[3]/text()')
                vod_name = i.xpath('./img/@alt')
                a.append(
                    {
                        'vod_id': i.xpath('./@href')[0],
                        'vod_name': vod_name[0] if len(vod_name[0]) > 0 else vod_name[1],
                        'vod_pic': i.xpath('./img/@src')[0],
                        'vod_remarks': vod_remarks[0] if vod_remarks else '',
                        'vod_year': vod_year[0] if vod_year else '',
                        'style': {"type": "rect", "ratio": 1.5}
                    }
                )
            return {'list': a, 'parse': 0, 'jx': 0}
        except requests.exceptions.RequestException as e:
            return {'list': [], 'parse': 0, 'jx': 0, 'msg': str(e)}

    def detailContent(self, did):
        ids = did[0]
        video_list = []
        url = self.home_url + f'/api{ids}'
        h = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'referer': 'https://rou.video',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
        try:
            res = requests.get(url, headers=h)
            if res.status_code != 200:
                return {'list': [], 'parse': 0, 'jx': 0, 'msg': f'status_code: {res.status_code}'}
            play_url = res.json()['video']['videoUrl']
            video_list.append(
                {
                    'type_name': '',
                    'vod_id': ids,
                    'vod_name': '',
                    'vod_remarks': '',
                    'vod_year': '',
                    'vod_area': '',
                    'vod_actor': '',
                    'vod_director': '书生玩剑',
                    'vod_content': '',
                    'vod_play_from': '老僧酿酒',
                    'vod_play_url': f'名妓读经${play_url}',

                }
            )
            return {"list": video_list, 'parse': 0, 'jx': 0}
        except requests.RequestException as e:
            return {'list': [], 'msg': e}

    def searchContent(self, key, quick, page='1'):
        url = f'{self.home_url}/search?q={key}&page={page}'
        try:
            res = requests.get(url, headers=self.headers)
            if res.status_code != 200:
                return {'list': [], 'parse': 0, 'jx': 0, 'msg': f'status_code: {res.status_code}'}
            root = etree.HTML(res.text.encode('utf-8'))
            data_list = root.xpath('//div[@class="aspect-video relative"]/a')
            if len(data_list) < 1:
                return {'list': [], 'parse': 0, 'jx': 0, 'msg': '获取的数据为空'}
            a = []
            for i in data_list:
                vod_remarks = i.xpath('./div[2]/text()')
                vod_year = i.xpath('./div[3]/text()')
                vod_name = i.xpath('./img/@alt')
                a.append(
                    {
                        'vod_id': i.xpath('./@href')[0],
                        'vod_name': vod_name[0] if len(vod_name[0]) > 0 else vod_name[1],
                        'vod_pic': i.xpath('./img/@src')[0],
                        'vod_remarks': vod_remarks[0] if vod_remarks else '',
                        'vod_year': vod_year[0] if vod_year else '',
                        'style': {"type": "rect", "ratio": 1.5}
                    }
                )
            return {'list': a, 'parse': 0, 'jx': 0}
        except requests.exceptions.RequestException as e:
            return {'list': [], 'parse': 0, 'jx': 0, 'msg': str(e)}

    def playerContent(self, flag, pid, vipFlags):
        return {'url': pid, "header": self.headers, 'parse': 0, 'jx': 0}

    def localProxy(self, params):
        pass

    def destroy(self):
        return '正在Destroy'


if __name__ == '__main__':
    pass