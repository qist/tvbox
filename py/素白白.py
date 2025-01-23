# -*- coding: utf-8 -*-
# @Author  : kaiyuebinguan
# @Time    : 2025/01/02


from Crypto.Util.Padding import unpad
from urllib.parse import unquote
from Crypto.Cipher import ARC4
from base.spider import Spider
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import binascii
import requests
import base64
import json
import time
import sys
import re
import os

sys.path.append('..')

xurl = "https://www.subaibai.com"

headerx = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    'authority': 'www.subaibai.com',
    'Referer': 'https://www.subaibai.com/',
    'Origin': 'https://www.subaibai.com/'
          }

pm = ''

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
                            output += f"#{ match[1]}${number}{xurl}{match[0]}"
                        else:
                            output += f"#{ match[1]}${number}{match[0]}"
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
                new_list = [f for item in matches]
                jg = '$$$'.join(new_list)
                return jg

    def homeContent(self, filter):
        result = {}
        result = {"class": [{"type_id": "new-movie", "type_name": "电影"},
                            {"type_id": "tv-drama", "type_name": "剧集"},
                            {"type_id": "hot-month", "type_name": "热门电影"},
                            {"type_id": "high-movie", "type_name": "高分电影"},
                            {"type_id": "cartoon-movie", "type_name": "动漫电影"},
                            {"type_id": "hongkong-movie", "type_name": "香港经典"},
                            {"type_id": "domestic-drama", "type_name": "国产剧"},
                            {"type_id": "american-drama", "type_name": "欧美剧"},
                            {"type_id": "korean-drama", "type_name": "韩剧"},
                            {"type_id": "anime-drama", "type_name": "动漫剧"}]
                  }

        return result

    def homeVideoContent(self):
        videos = []

        try:

            detail = requests.get(url=xurl, headers=headerx)
            detail.encoding = "utf-8"
            res = detail.text

            doc = BeautifulSoup(res, "lxml")

            soups = doc.find_all('div', class_="bt_img")

            for soup in soups:
                vods = soup.find_all('li')

                for vod in vods:

                    name = vod.find('img')['alt']

                    ids = vod.find('h3', class_="dytit")
                    id = ids.find('a')['href']
                    id = id.replace('www.subaibaiys.com', 'www.subaibai.com')

                    pic = vod.find('img')['data-original']

                    if 'http' not in pic:
                        pic = xurl + pic

                    remark = self.extract_middle_text(str(vod), 'class="rating">', '</div>', 0)

                    video = {
                        "vod_id": id,
                        "vod_name": name,
                        "vod_pic": pic,
                        "vod_remarks": remark
                             }
                    videos.append(video)

            result = {'list': videos}
            return result
        except:
            pass

    def categoryContent(self, cid, pg, filter, ext):
        result = {}
        videos = []

        if pg:
            page = int(pg)
        else:
            page = 1

        if page == '1':
            url = f'{xurl}/{cid}'

        else:
            url = f'{xurl}/{cid}/page/{str(page)}'

        try:
            detail = requests.get(url=url, headers=headerx)
            detail.encoding = "utf-8"
            res = detail.text
            doc = BeautifulSoup(res, "lxml")

            soups = doc.find_all('div', class_="bt_img")

            for soup in soups:
                vods = soup.find_all('li')

                for vod in vods:

                    name = vod.find('img')['alt']

                    ids = vod.find('h3', class_="dytit")
                    id = ids.find('a')['href']
                    id = id.replace('www.subaibaiys.com', 'www.subaibai.com')

                    pic = vod.find('img')['data-original']

                    if 'http' not in pic:
                        pic = xurl + pic

                    remark = self.extract_middle_text(str(vod), 'class="rating">', '</div>', 0)

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
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        global pm
        did = ids[0]
        result = {}
        videos = []

        if 'http' not in did:
            did = xurl + did

        res1 = requests.get(url=did, headers=headerx)
        res1.encoding = "utf-8"
        res = res1.text

        url = 'https://www.subaibai.com'
        response = requests.get(url)
        response.encoding = 'utf-8'
        code = response.text
        name = self.extract_middle_text(code, "s1='", "'", 0)
        Jumps = self.extract_middle_text(code, "s2='", "'", 0)

        content = self.extract_middle_text(res,'<div class="yp_context">','</p>', 0)
        content = content.replace('\t', '').replace('<p>', '').replace(' ', '').replace('\n', '')

        if name not in content:
            bofang = Jumps
        else:
            bofang = self.extract_middle_text(res, '<div class="paly_list_btn">', '</div>', 3, 'href="(.*?)">(.*?)</a>')
            bofang = bofang.replace('www.subaibaiys.com', 'www.subaibai.com').replace('立即播放&nbsp;&nbsp;', '')

        videos.append({
            "vod_id": did,
            "vod_actor": '',
            "vod_director": '',
            "vod_content": content,
            "vod_play_from": '专线',
            "vod_play_url": bofang
                     })

        result['list'] = videos
        return result

    def playerContent(self, flag, id, vipFlags):
        parts = id.split("http")

        xiutan = 1

        if xiutan == 0:
            if len(parts) > 1:
                before_https, after_https = parts[0], 'http' + parts[1]

            if '' in after_https:
                url = after_https
            else:
                res = requests.get(url=after_https, headers=headerx)
                res = res.text

                url = self.extract_middle_text(res, '},"url":"', '"', 0).replace('\\', '')

                #  =======================================

                # url = base64.b64decode(url).decode('utf-8')

                # url = unquote(url)

                # import base64
                # base64_decoded_bytes = base64.b64decode(url)
                # base64_decoded_string = base64_decoded_bytes.decode('utf-8')
                # url = unquote(base64_decoded_string)
                # url="https://"+self.extract_middle_text(url,'https://','.m3u8',0)+'.m3u8'

                #  =======================================

            result = {}
            result["parse"] = xiutan
            result["playUrl"] = ''
            result["url"] = url
            result["header"] = headerx
            return result

                #  =======================================

        if xiutan == 1:
            if len(parts) > 1:
                before_https, after_https = parts[0], 'http' + parts[1]
            result = {}
            result["parse"] = xiutan
            result["playUrl"] = ''
            result["url"] = after_https
            result["header"] = headerx
            return result

    def searchContentPage(self, key, quick, page):
        result = {}
        videos = []

        if not page:
            page = '1'
        if page == '1':
            url = f'{xurl}/?s={key}'

        else:
            url = f'{xurl}//page/{str(page)}?s={key}'

        detail = requests.get(url=url, headers=headerx)
        detail.encoding = "utf-8"
        res = detail.text
        doc = BeautifulSoup(res, "lxml")

        soups = doc.find_all('div', class_="bt_img")

        for soup in soups:
            vods = soup.find_all('li')

            for vod in vods:

                name = vod.find('img')['alt']

                ids = vod.find('h3', class_="dytit")
                id = ids.find('a')['href']
                id = id.replace('www.subaibaiys.com', 'www.subaibai.com')

                pic = vod.find('img')['data-original']

                if 'http' not in pic:
                    pic = xurl + pic

                remark = self.extract_middle_text(str(vod), 'class="rating">', '</div>', 0)

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

    def searchContent(self, key, quick):
        return self.searchContentPage(key, quick, '1')

    def localProxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        elif params['type'] == "media":
            return self.proxyMedia(params)
        elif params['type'] == "ts":
            return self.proxyTs(params)
        return None


"""

   =======================================

   换行 \n   零个或者多个空格 \s+   数字型 int   文本型 str   分页{} '年代':'2021'       

   性能要求高"lxml"   处理不规范的HTML"html5lib"   简单应用"html.parser"   解析XML"xml"

   =======================================

   /rss/index.xml?wd=爱情&page=1                                搜索有验证

   /index.php/ajax/suggest?mid=1&wd=爱情&page=1&limit=30        搜索有验证

   /index.php/ajax/data?mid=1&tid={cateId}&class={class}&area={area}&page={catePg}&limit=30   分类有验证

   /index.php/vod/type/class/{cid}/id/41/page/{str(page)}/year/{NdType}.html        隐藏分类

   /{cateId}-{area}-{by}-{class}-{lang}-{letter}---{catePg}---{year}.html

   短剧 穿越 古装 仙侠 女频 恋爱 反转 现代 都市 剧情 玄幻 脑洞 悬疑  

   =======================================

   aaa = self.extract_middle_text(res, 'bbb', 'ccc', 0)
   aaa = aaa.replace('aaa', '').replace('bbb', '') 替换多余
   取头 取尾  （不循环)   截取项  （不循环)   长用于直链  二次截取                0号子程序

   aaa =self.extract_middle_text(res, 'bbb', 'ccc',1,'html">(.*?)<')
   aaa = aaa.replace('aaa', '').replace('bbb', '') 替换多余
   取头 取尾  （不循环)   截取项  （循环)     长用于详情  和2号区别没有$$$        1号子程序

   aaa = self.extract_middle_text(res, 'bbb','ccc', 2,'<span class=".*?" id=".*?">(.*?)</span>')
   aaa = aaa.replace('aaa', '').replace('bbb', '') 替换多余
   取头 取尾  （不循环)   截取项  （循环)     只能用于线路数组  里面包含$$$       2号子程序

   aaa = self.extract_middle_text(res, 'bbb', 'ccc', 3,'href="(.*?)" class=".*?">(.*?)</a>')
   aaa = aaa.replace('aaa', '').replace('bbb', '') 替换多余
   取头 取尾  （循环)     截取项  （循环)    长用于播放数组                     3号子程序

   =======================================

"""

if __name__ == '__main__':
    spider_instance = Spider()

    # res=spider_instance.homeContent('filter')  #  分类🚨

    # res = spider_instance.homeVideoContent()  # 首页🚨

    # res=spider_instance.categoryContent('new-movie', 2, 'filter', {})  #  分页🚨

    res = spider_instance.detailContent(['https://www.subaibai.com/movie/56949.html'])  #  详情页🚨

    # res = spider_instance.playerContent('1', '0https://www.mjzj.me/74354-1-1.html', 'vipFlags')  #  播放页🚨

    # res = spider_instance.searchContentPage('爱情', 'quick', '2')  # 搜索页🚨

    print(res)