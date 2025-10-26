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

xurl = "https://www.yymp3.com"

headerx = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36'
          }

class Spider(Spider):
    global xurl
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
        result = {"class": []}

        detail = requests.get(url=xurl, headers=headerx)
        detail.encoding = "utf-8"
        res = detail.text
        doc = BeautifulSoup(res, "lxml")

        soups = doc.find_all('div', id="nav_box")

        for soup in soups:
            vods = soup.find_all('a')

            for vod in vods:
                name = vod.text.strip()
                skip_keywords = ["首页", "动漫"]
                if any(keyword in name for keyword in skip_keywords):
                    continue

                id = vod['href']
                if 'http' not in id:
                    id = xurl + id

                result["class"].append({"type_id": id, "type_name": name})

        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, cid, pg, filter, ext):
        result = {}
        videos = []

        if '@' in cid:
            fenge = cid.split("@")

            detail = requests.get(url=xurl + fenge[0], headers=headerx)
            detail.encoding = "utf-8"
            res = detail.text
            doc = BeautifulSoup(res, "lxml")

            soups = doc.find_all('dl', class_="albumlist c")

            for vod in soups:
                names = vod.find('a', class_="A_name")
                name = names.text.strip()

                ids = vod.find('dd', class_="A_details")
                id = ids.find('a')['href']

                pic = vod.find('img')['src']

                if 'http' not in pic:
                    pic = "https:" + pic

                remark = "推荐"

                video = {
                    "vod_id": id,
                    "vod_name": name,
                    "vod_pic": pic,
                    "vod_remarks": remark
                        }
                videos.append(video)

        else:
            detail = requests.get(url=cid, headers=headerx)
            detail.encoding = "utf-8"
            res = detail.text
            doc = BeautifulSoup(res, "lxml")
            soups = doc.find_all('ul', class_="Cate_slist c")

            for soup in soups:
                vods = soup.find_all('a')

                for vod in vods:

                    name = vod.text.strip()

                    id = vod['href']

                    pic = "https://fs-im-kefu.7moor-fs1.com/ly/4d2c3f00-7d4c-11e5-af15-41bf63ae4ea0/af3a1f95d591c34d/1755975256375.png"

                    remark = "推荐"

                    video = {
                        "vod_id": id+'@'+name,
                        "vod_name": name,
                        "vod_pic": pic,
                        "vod_tag": "folder",
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

        if 'Play' in did:
            if 'http' not in did:
                bofang = xurl + did

            xianlu = '搜索专线'

            videos.append({
                "vod_id": did,
                "vod_play_from": xianlu,
                "vod_play_url": bofang
                         })

        else:
            if 'http' not in did:
                did = xurl + did

            res = requests.get(url=did, headers=headerx)
            res.encoding = "utf-8"
            res = res.text
            doc = BeautifulSoup(res, "lxml")

            content = self.extract_middle_text(res,'style="height:93px;">','</p>', 0)
            content = content.replace('<br>', '').replace('</br>', '').replace(' ', '')

            director = self.extract_middle_text(res,'公司：','</', 0)

            actor = self.extract_middle_text(res, '歌手：', '</li>',1,'href=.*?>(.*?)</a>')

            year = self.extract_middle_text(res, '时间：', '<', 0)

            area = self.extract_middle_text(res, '语种：', '<', 0)

            soups = doc.find_all('ul', class_="A_list4")

            for item in soups:
                vods = item.find_all('li')

                for sou in vods:

                    ids = sou.find('div', class_="td1_l")
                    id = ids.find('a')['href']

                    if 'http' not in id:
                        id = xurl + id

                    names = sou.find('div', class_="td1_l")
                    name = names.text.strip()

                    bofang = bofang + name + '$' + id + '#'

                bofang = bofang[:-1]

                xianlu = '音乐专线'

            videos.append({
                "vod_id": did,
                "vod_director": director,
                "vod_actor": actor,
                "vod_year": year,
                "vod_area": area,
                "vod_content": content,
                "vod_play_from": xianlu,
                "vod_play_url": bofang
                         })

        result['list'] = videos
        return result

    def playerContent(self, flag, id, vipFlags):

        res = requests.get(url=id, headers=headerx)
        res.encoding = "utf-8"
        res = res.text

        year = self.extract_middle_text(res, '$song_data[0]', ';', 0)
        fenge = year.split('|')

        url = "https://ting8.yymp3.com/" + fenge[4]
        url = url.replace('wma', 'mp3')

        result = {}
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = url
        result["header"] = headerx
        return result

    def searchContentPage(self, key, quick, pg):
        result = {}
        videos = []

        if pg:
            page = int(pg)
        else:
            page = 1

        url = f'{xurl}/search/?page={str(page)}&key={key}&tp=1'
        detail = requests.get(url=url, headers=headerx)
        detail.encoding = "utf-8"
        res = detail.text
        doc = BeautifulSoup(res, "lxml")

        soups = doc.find_all('ul', class_="searchResult c")

        for item in soups:
            vods = item.find_all('li')

            for vod in vods[1:]:

                names = vod.find('div', class_="p3")
                name1 = names.text.strip()

                name2s = vod.find('div', class_="p2")
                name2 = name2s.text.strip()

                name = name1 + ' ' + name2

                id = names.find('a')['href']

                pic = "https://fs-im-kefu.7moor-fs1.com/ly/4d2c3f00-7d4c-11e5-af15-41bf63ae4ea0/af3a1f95d591c34d/1755975256375.png"

                remark = "推荐"

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








