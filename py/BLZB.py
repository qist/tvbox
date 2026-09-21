<<<<<<< HEAD
# coding=utf-8
# !/usr/bin/python

"""

作者 丢丢喵 🚓 内容均从互联网收集而来 仅供交流学习使用 版权归原创者所有 如侵犯了您的权益 请通知作者 将及时删除侵权内容
                    ====================Diudiumiao====================

"""

from Crypto.Util.Padding import unpad
from Crypto.Util.Padding import pad
from urllib.parse import unquote
from Crypto.Cipher import ARC4
from urllib.parse import quote
from base.spider import Spider
from Crypto.Cipher import AES
from datetime import datetime
from bs4 import BeautifulSoup
from base64 import b64decode
import urllib.request
import urllib.parse
import datetime
import binascii
import requests
import base64
import json
import time
import sys
import re
import os

sys.path.append('..')

xurl = "https://search.bilibili.com"

xurl1 = "https://api.live.bilibili.com"

headerx = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
          }

class Spider(Spider):
    global xurl
    global xurl1
    global headerx

    def getName(self):
        return "首页"

    def init(self, extend):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def extract_middle_text(self, text, start_str, end_str, pl, start_index1: str = '', end_index2: str = ''):
        if pl == 3:
            plx = []
            while True:
                start_index = text.find(start_str)
                if start_index == -1:
                    break
                end_index = text.find(end_str, start_index + len(start_str))
                if end_index == -1:
                    break
                middle_text = text[start_index + len(start_str):end_index]
                plx.append(middle_text)
                text = text.replace(start_str + middle_text + end_str, '')
            if len(plx) > 0:
                purl = ''
                for i in range(len(plx)):
                    matches = re.findall(start_index1, plx[i])
                    output = ""
                    for match in matches:
                        match3 = re.search(r'(?:^|[^0-9])(\d+)(?:[^0-9]|$)', match[1])
                        if match3:
                            number = match3.group(1)
                        else:
                            number = 0
                        if 'http' not in match[0]:
                            output += f"#{match[1]}${number}{xurl}{match[0]}"
                        else:
                            output += f"#{match[1]}${number}{match[0]}"
                    output = output[1:]
                    purl = purl + output + "$$$"
                purl = purl[:-3]
                return purl
            else:
                return ""
        else:
            start_index = text.find(start_str)
            if start_index == -1:
                return ""
            end_index = text.find(end_str, start_index + len(start_str))
            if end_index == -1:
                return ""

        if pl == 0:
            middle_text = text[start_index + len(start_str):end_index]
            return middle_text.replace("\\", "")

        if pl == 1:
            middle_text = text[start_index + len(start_str):end_index]
            matches = re.findall(start_index1, middle_text)
            if matches:
                jg = ' '.join(matches)
                return jg

        if pl == 2:
            middle_text = text[start_index + len(start_str):end_index]
            matches = re.findall(start_index1, middle_text)
            if matches:
                new_list = [f'{item}' for item in matches]
                jg = '$$$'.join(new_list)
                return jg

    def homeContent(self, filter):
        result = {}
        result = {"class": [{"type_id": "舞", "type_name": "舞蹈"},
                            {"type_id": "音乐", "type_name": "音乐"},
                            {"type_id": "手游", "type_name": "手游"},
                            {"type_id": "网游", "type_name": "网游"},
                            {"type_id": "单机游戏", "type_name": "单机游戏"},
                            {"type_id": "虚拟主播", "type_name": "虚拟主播"},
                            {"type_id": "电台", "type_name": "电台"},
                            {"type_id": "体育", "type_name": "体育"},
                            {"type_id": "聊天", "type_name": "聊天"},
                            {"type_id": "娱乐", "type_name": "娱乐"},
                            {"type_id": "电影", "type_name": "影视"},
                            {"type_id": "新闻", "type_name": "新闻"}]
                 }

        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, cid, pg, filter, ext):
        result = {}
        videos = []

        if pg:
            page = int(pg)
        else:
            page = 1

        url = f'{xurl}/live?keyword={cid}&page={str(page)}'
        detail = requests.get(url=url, headers=headerx)
        detail.encoding = "utf-8"
        res = detail.text
        doc = BeautifulSoup(res, "lxml")

        soups = doc.find_all('div', class_="video-list-item")

        for vod in soups:

            names = vod.find('h3', class_="bili-live-card__info--tit")
            name = names.text.strip().replace('直播中', '')

            id = names.find('a')['href']
            id = self.extract_middle_text(id, 'bilibili.com/', '?', 0)

            pic = vod.find('img')['src']
            if 'http' not in pic:
                pic = "https:" + pic

            remarks = vod.find('a', class_="bili-live-card__info--uname")
            remark = remarks.text.strip()

            video = {
                "vod_id": id,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remark
                    }
            videos.append(video)

        result = {'list': videos}
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        did = ids[0]
        result = {}
        videos = []
        xianlu = ''
        bofang = ''

        url = f'{xurl1}/xlive/web-room/v2/index/getRoomPlayInfo?room_id={did}&platform=web&protocol=0,1&format=0,1,2&codec=0,1'
        detail = requests.get(url=url, headers=headerx)
        detail.encoding = "utf-8"
        data = detail.json()

        content = '欢迎观看哔哩直播'

        setup = data['data']['playurl_info']['playurl']['stream']

        nam = 0

        for vod in setup:

            try:
                host = vod['format'][nam]['codec'][0]['url_info'][1]['host']
            except (KeyError, IndexError):
                continue

            base = vod['format'][nam]['codec'][0]['base_url']

            extra = vod['format'][nam]['codec'][0]['url_info'][1]['extra']

            id = host + base + extra

            nam = nam + 1

            namc = f"{nam}号线路"

            bofang = bofang + namc + '$' + id + '#'

        bofang = bofang[:-1]

        xianlu = '哔哩专线'

        videos.append({
            "vod_id": did,
            "vod_content": content,
            "vod_play_from": xianlu,
            "vod_play_url": bofang
                     })

        result['list'] = videos
        return result

    def playerContent(self, flag, id, vipFlags):

        result = {}
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = id
        result["header"] = headerx
        return result

    def searchContentPage(self, key, quick, pg):
        result = {}
        videos = []

        if pg:
            page = int(pg)
        else:
            page = 1

        url = f'{xurl}/live?keyword={key}&page={str(page)}'
        detail = requests.get(url=url, headers=headerx)
        detail.encoding = "utf-8"
        res = detail.text
        doc = BeautifulSoup(res, "lxml")

        soups = doc.find_all('div', class_="video-list-item")

        for vod in soups:

            names = vod.find('h3', class_="bili-live-card__info--tit")
            name = names.text.strip().replace('直播中', '')

            id = names.find('a')['href']
            id = self.extract_middle_text(id, 'bilibili.com/', '?', 0)

            pic = vod.find('img')['src']
            if 'http' not in pic:
                pic = "https:" + pic

            remarks = vod.find('a', class_="bili-live-card__info--uname")
            remark = remarks.text.strip()

            video = {
                "vod_id": id,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remark
                    }
            videos.append(video)

        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def searchContent(self, key, quick, pg="1"):
        return self.searchContentPage(key, quick, '1')

    def localProxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        elif params['type'] == "media":
            return self.proxyMedia(params)
        elif params['type'] == "ts":
            return self.proxyTs(params)
        return None








=======
# coding=utf-8
# !/usr/bin/python

"""

作者 丢丢喵 🚓 内容均从互联网收集而来 仅供交流学习使用 版权归原创者所有 如侵犯了您的权益 请通知作者 将及时删除侵权内容
                    ====================Diudiumiao====================

"""

from Crypto.Util.Padding import unpad
from Crypto.Util.Padding import pad
from urllib.parse import unquote
from Crypto.Cipher import ARC4
from urllib.parse import quote
from base.spider import Spider
from Crypto.Cipher import AES
from datetime import datetime
from bs4 import BeautifulSoup
from base64 import b64decode
import urllib.request
import urllib.parse
import datetime
import binascii
import requests
import base64
import json
import time
import sys
import re
import os

sys.path.append('..')

xurl = "https://search.bilibili.com"

xurl1 = "https://api.live.bilibili.com"

headerx = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
          }

class Spider(Spider):
    global xurl
    global xurl1
    global headerx

    def getName(self):
        return "首页"

    def init(self, extend):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def extract_middle_text(self, text, start_str, end_str, pl, start_index1: str = '', end_index2: str = ''):
        if pl == 3:
            plx = []
            while True:
                start_index = text.find(start_str)
                if start_index == -1:
                    break
                end_index = text.find(end_str, start_index + len(start_str))
                if end_index == -1:
                    break
                middle_text = text[start_index + len(start_str):end_index]
                plx.append(middle_text)
                text = text.replace(start_str + middle_text + end_str, '')
            if len(plx) > 0:
                purl = ''
                for i in range(len(plx)):
                    matches = re.findall(start_index1, plx[i])
                    output = ""
                    for match in matches:
                        match3 = re.search(r'(?:^|[^0-9])(\d+)(?:[^0-9]|$)', match[1])
                        if match3:
                            number = match3.group(1)
                        else:
                            number = 0
                        if 'http' not in match[0]:
                            output += f"#{match[1]}${number}{xurl}{match[0]}"
                        else:
                            output += f"#{match[1]}${number}{match[0]}"
                    output = output[1:]
                    purl = purl + output + "$$$"
                purl = purl[:-3]
                return purl
            else:
                return ""
        else:
            start_index = text.find(start_str)
            if start_index == -1:
                return ""
            end_index = text.find(end_str, start_index + len(start_str))
            if end_index == -1:
                return ""

        if pl == 0:
            middle_text = text[start_index + len(start_str):end_index]
            return middle_text.replace("\\", "")

        if pl == 1:
            middle_text = text[start_index + len(start_str):end_index]
            matches = re.findall(start_index1, middle_text)
            if matches:
                jg = ' '.join(matches)
                return jg

        if pl == 2:
            middle_text = text[start_index + len(start_str):end_index]
            matches = re.findall(start_index1, middle_text)
            if matches:
                new_list = [f'{item}' for item in matches]
                jg = '$$$'.join(new_list)
                return jg

    def homeContent(self, filter):
        result = {}
        result = {"class": [{"type_id": "舞", "type_name": "舞蹈"},
                            {"type_id": "音乐", "type_name": "音乐"},
                            {"type_id": "手游", "type_name": "手游"},
                            {"type_id": "网游", "type_name": "网游"},
                            {"type_id": "单机游戏", "type_name": "单机游戏"},
                            {"type_id": "虚拟主播", "type_name": "虚拟主播"},
                            {"type_id": "电台", "type_name": "电台"},
                            {"type_id": "体育", "type_name": "体育"},
                            {"type_id": "聊天", "type_name": "聊天"},
                            {"type_id": "娱乐", "type_name": "娱乐"},
                            {"type_id": "电影", "type_name": "影视"},
                            {"type_id": "新闻", "type_name": "新闻"}]
                 }

        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, cid, pg, filter, ext):
        result = {}
        videos = []

        if pg:
            page = int(pg)
        else:
            page = 1

        url = f'{xurl}/live?keyword={cid}&page={str(page)}'
        detail = requests.get(url=url, headers=headerx)
        detail.encoding = "utf-8"
        res = detail.text
        doc = BeautifulSoup(res, "lxml")

        soups = doc.find_all('div', class_="video-list-item")

        for vod in soups:

            names = vod.find('h3', class_="bili-live-card__info--tit")
            name = names.text.strip().replace('直播中', '')

            id = names.find('a')['href']
            id = self.extract_middle_text(id, 'bilibili.com/', '?', 0)

            pic = vod.find('img')['src']
            if 'http' not in pic:
                pic = "https:" + pic

            remarks = vod.find('a', class_="bili-live-card__info--uname")
            remark = remarks.text.strip()

            video = {
                "vod_id": id,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remark
                    }
            videos.append(video)

        result = {'list': videos}
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        did = ids[0]
        result = {}
        videos = []
        xianlu = ''
        bofang = ''

        url = f'{xurl1}/xlive/web-room/v2/index/getRoomPlayInfo?room_id={did}&platform=web&protocol=0,1&format=0,1,2&codec=0,1'
        detail = requests.get(url=url, headers=headerx)
        detail.encoding = "utf-8"
        data = detail.json()

        content = '欢迎观看哔哩直播'

        setup = data['data']['playurl_info']['playurl']['stream']

        nam = 0

        for vod in setup:

            try:
                host = vod['format'][nam]['codec'][0]['url_info'][1]['host']
            except (KeyError, IndexError):
                continue

            base = vod['format'][nam]['codec'][0]['base_url']

            extra = vod['format'][nam]['codec'][0]['url_info'][1]['extra']

            id = host + base + extra

            nam = nam + 1

            namc = f"{nam}号线路"

            bofang = bofang + namc + '$' + id + '#'

        bofang = bofang[:-1]

        xianlu = '哔哩专线'

        videos.append({
            "vod_id": did,
            "vod_content": content,
            "vod_play_from": xianlu,
            "vod_play_url": bofang
                     })

        result['list'] = videos
        return result

    def playerContent(self, flag, id, vipFlags):

        result = {}
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = id
        result["header"] = headerx
        return result

    def searchContentPage(self, key, quick, pg):
        result = {}
        videos = []

        if pg:
            page = int(pg)
        else:
            page = 1

        url = f'{xurl}/live?keyword={key}&page={str(page)}'
        detail = requests.get(url=url, headers=headerx)
        detail.encoding = "utf-8"
        res = detail.text
        doc = BeautifulSoup(res, "lxml")

        soups = doc.find_all('div', class_="video-list-item")

        for vod in soups:

            names = vod.find('h3', class_="bili-live-card__info--tit")
            name = names.text.strip().replace('直播中', '')

            id = names.find('a')['href']
            id = self.extract_middle_text(id, 'bilibili.com/', '?', 0)

            pic = vod.find('img')['src']
            if 'http' not in pic:
                pic = "https:" + pic

            remarks = vod.find('a', class_="bili-live-card__info--uname")
            remark = remarks.text.strip()

            video = {
                "vod_id": id,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remark
                    }
            videos.append(video)

        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def searchContent(self, key, quick, pg="1"):
        return self.searchContentPage(key, quick, '1')

    def localProxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        elif params['type'] == "media":
            return self.proxyMedia(params)
        elif params['type'] == "ts":
            return self.proxyTs(params)
        return None








>>>>>>> upstream/master
