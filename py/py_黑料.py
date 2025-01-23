# coding=utf-8
# !/usr/bin/python
import sys
import requests
from bs4 import BeautifulSoup
import re
import base64
from base.spider import Spider
import random

sys.path.append('..')
xurl = "https://heiliaowang-44.buzz"
headerx = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36',

}
class Spider(Spider):
    global xurl
    global headerx


    def getName(self):
        return "首页"

    def init(self, extend):
        pass

    def destroy(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        res = requests.get(xurl, headers=headerx)
        res.encoding = "utf-8"
        doc = BeautifulSoup(res.text, "html.parser")
        sourcediv = doc.find('div', class_='nav')
        vod = sourcediv.find_all('dd')
        string_list = ["首页", "激情图漫", "激情小说",
                       "情色小说", "随机推荐", "顶级资源"]

        result = {}
        result['class'] = []
        result['class'].append({'type_id': "/type/328", 'type_name': "国产视频"})
        result['class'].append({'type_id': "/type/329", 'type_name': "中文字幕"})
        result['class'].append({'type_id': "/type/331", 'type_name': "日本有码"})
        result['class'].append({'type_id': "/type/332", 'type_name': "日本无码"})
        result['class'].append({'type_id': "/type/333", 'type_name': "欧美无码"})
        result['class'].append({'type_id': "/type/334", 'type_name': "强奸乱轮"})
        result['class'].append({'type_id': "/type/335", 'type_name': "制服诱惑"})
        result['class'].append({'type_id': "/type/336", 'type_name': "直播主播"})
        result['class'].append({'type_id': "/type/338", 'type_name': "明星换脸"})
        result['class'].append({'type_id': "/type/339", 'type_name': "抖阴视频"})
        result['class'].append({'type_id': "/type/340", 'type_name': "女优明星"})
        result['class'].append({'type_id': "/type/343", 'type_name': "网爆门"})
        result['class'].append({'type_id': "/type/345", 'type_name': "伦理三级"})
        result['class'].append({'type_id': "/type/346", 'type_name': "AV解说"})
        result['class'].append({'type_id': "/type/347", 'type_name': "SM调教"})
        result['class'].append({'type_id': "/type/348", 'type_name': "萝莉少女"})
        result['class'].append({'type_id': "/type/349", 'type_name': "极品媚黑"})
        result['class'].append({'type_id': "/type/350", 'type_name': "女同性恋"})
        result['class'].append({'type_id': "/type/351", 'type_name': "玩偶姐姐"})
        result['class'].append({'type_id': "/type/353", 'type_name': "人妖系列"})
        result['class'].append({'type_id': "/type/373", 'type_name': "韩国主播"})
        result['class'].append({'type_id': "/type/378", 'type_name': "VR视角"})
        for item in vod:
            name = item.find('a').text
            if name in string_list:
                continue

            id = item.find('a')['href']
            id = id.replace(".html", "")
            result['class'].append({'type_id': id, 'type_name': name})

        return result
    def homeVideoContent(self):
        videos = []
        try:
            res = requests.get(xurl, headers=headerx)
            res.encoding = "utf-8"
            doc = BeautifulSoup(res.text, "html.parser")
            sourcediv = doc.find_all('div', class_='pic')
            for vod in sourcediv:
                ul_elements = vod.find_all('ul')
                for item in ul_elements:
                    name = item.select_one("li a")['title']
                    pic = item.select_one("li a img")["data-src"]
                    remark = item.select_one("li a span").text
                    id = item.select_one("li a")['href']
                    video = {
                        "vod_id": id,
                        "vod_name": name,
                        "vod_pic": pic,
                        "vod_remarks": remark
                    }
                    videos.append(video)
        except:
            pass
        result = {'list': videos}
        return result

    def categoryContent(self, cid, pg, filter, ext):
        result = {}
        videos = []
        if not pg:
            pg = 1

        url = xurl +cid + "/" + str(pg) + ".html"
        detail = requests.get(url=url, headers=headerx)
        detail.encoding = "utf-8"
        doc = BeautifulSoup(detail.text, "html.parser")
        sourcediv = doc.find_all('div', class_='pic')
        for vod in sourcediv:
            ul_elements = vod.find_all('ul')
            for item in ul_elements:
                name = item.select_one("li a")['title']
                pic = item.select_one("li a img")["src"]
                remark = item.select_one("li a span").text
                id = item.select_one("li a")['href']
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

    def detailContent(self, ids):
        did = ids[0]
        videos = []
        result = {}
        res = requests.get(url=xurl + did, headers=headerx)
        res.encoding = "utf-8"
        doc = BeautifulSoup(res.text, "html.parser")
        sourcediv = doc.find('div', style='padding-bottom: 10px;')
        vod = sourcediv.find_all('a')
        play_from = ""
        play_url = ""
        for item in vod:
            play_from = play_from + item.text + "$$$"
            play_url = play_url + item['href'] + "$$$"
        while play_url[-1] == "#" or play_url[-1] == "$":
            play_url = play_url[:-1]

        while play_from[-1] == "#" or play_from[-1] == "$":
            play_from = play_from[:-1]

        source_match = re.search(r"<li>播放地址:<strong>(.*?)</strong></li>", res.text)
        if source_match:
            tx = source_match.group(1)

        videos.append({
            "vod_id": did,
            "vod_name": tx,
            "vod_pic": "",
            "type_name": "ぃぅおか🍬 คิดถึง",
            "vod_year": "",
            "vod_area": "",
            "vod_remarks": "",
            "vod_actor": "",
            "vod_director": "",
            "vod_content": "",
            "vod_play_from": play_from,
            "vod_play_url": play_url
        })

        result['list'] = videos
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {}
        res = requests.get(url=xurl + id, headers=headerx)
        res.encoding = "utf-8"
        if '"rid"' in res.text:
            decoded_str = ''
            while not decoded_str:
                source_match3 = re.search(r'"rid" : "(.*?)"', res.text)
                if source_match3:
                    id = source_match3.group(1)

                    data = "rid=" + id
                    header = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36",
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                    }
                    res2 = requests.post(url="https://heiliaowang-44.buzz/fetchPlayUrl3", headers=header, data=data)

                    source_match4 = re.search(r'"returnData"\s*:\s*"([^"]+)"', res2.text)
                    if source_match4:
                        decoded_str = source_match4.group(1)


        else:
            source_match = re.search(r"http:(.*?)\.m3u8", res.text)
            decoded_str = ""
            if source_match:
                str3 = source_match.group(1)
                if "aHR0c" in str3:
                    padding_needed = len(str3) % 4
                    if padding_needed:
                        str3 += '=' * (4 - padding_needed)
                    decoded_str = base64.b64decode(str3).decode("utf-8")
            if not decoded_str:
                source_match2 = re.search(r"'(.*?)\.m3u8';", res.text)
                if source_match2:
                    decoded_str = source_match2.group(1) + ".m3u8"

        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = decoded_str
        result["header"] = headerx
        return result

    def searchContent(self, key, quick):
        return self.searchContentPage(key, quick, '1')

    def searchContentPage(self, key, quick, page):

        result = {}
        videos = []
        if not page:
            page = 1


        url = xurl +"/search/"+ key +"/n/" + str(page)+".html"
        detail = requests.get(url=url, headers=headerx)
        detail.encoding = "utf-8"
        doc = BeautifulSoup(detail.text, "html.parser")
        sourcediv = doc.find_all('div', class_='pic')
        for vod in sourcediv:
            ul_elements = vod.find_all('ul')
            for item in ul_elements:
                name = item.select_one("li a")['title']
                pic = item.select_one("li a img")["src"]
                remark = item.select_one("li a span").text
                id = item.select_one("li a")['href']
                video = {
                    "vod_id": id,
                    "vod_name": name,
                    "vod_pic": pic,
                    "vod_remarks": remark
                }
                videos.append(video)

        result['list'] = videos
        result['page'] = page
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def localProxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        elif params['type'] == "media":
            return self.proxyMedia(params)
        elif params['type'] == "ts":
            return self.proxyTs(params)
        return None
