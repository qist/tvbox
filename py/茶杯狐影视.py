# coding = utf-8
# !/usr/bin/python

"""

作者 繁华 🚓 内容均从互联网收集而来 仅供交流学习使用 版权归原创者所有 如侵犯了您的权益 请通知作者 将及时删除侵权内容
                    ====================fanhua====================

"""

from Crypto.Util.Padding import unpad
from urllib.parse import unquote
from Crypto.Cipher import ARC4
from urllib.parse import quote
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

xurl = "https://cupfoxys.cc"

headerx = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36'
          }

# headerx = {
#     'User-Agent': 'Linux; Android 12; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.101 Mobile Safari/537.36'
#           }

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
                new_list = [f'{item}' for item in matches]
                jg = '$$$'.join(new_list)
                return jg

    def homeContent(self, filter):
        result = {}
        result ={"class":[{"type_id":"dy","type_name":"电影"},{"type_id":"dsj","type_name":"电视剧"},{"type_id":"dm","type_name":"动漫"},{"type_id":"zy","type_name":"综艺"}],"list":[],"filters":{"dy":[{"key":"类型","name":"类型","value":[{"n":"全部","v":""},{"n":"喜剧","v":"喜剧"},{"n":"爱情","v":"爱情"},{"n":"动作","v":"动作"},{"n":"科幻","v":"科幻"},{"n":"剧情","v":"剧情"},{"n":"战争","v":"战争"},{"n":"警匪","v":"警匪"},{"n":"犯罪","v":"犯罪"},{"n":"动画","v":"动画"},{"n":"奇幻","v":"奇幻"},{"n":"武侠","v":"武侠"},{"n":"冒险","v":"冒险"},{"n":"枪战","v":"枪战"},{"n":"恐怖","v":"恐怖"},{"n":"悬疑","v":"悬疑"},{"n":"惊悚","v":"惊悚"},{"n":"经典","v":"经典"},{"n":"青春","v":"青春"},{"n":"文艺","v":"文艺"},{"n":"微电影","v":"微电影"},{"n":"古装","v":"古装"},{"n":"历史","v":"历史"},{"n":"运动","v":"运动"},{"n":"农村","v":"农村"},{"n":"儿童","v":"儿童"},{"n":"网络电影","v":"网络电影"}]},{"key":"地区","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"大陆"},{"n":"香港","v":"香港"},{"n":"台湾","v":"台湾"},{"n":"美国","v":"美国"},{"n":"法国","v":"法国"},{"n":"英国","v":"英国"},{"n":"日本","v":"日本"},{"n":"韩国","v":"韩国"},{"n":"德国","v":"德国"},{"n":"泰国","v":"泰国"},{"n":"印度","v":"印度"},{"n":"意大利","v":"意大利"},{"n":"西班牙","v":"西班牙"},{"n":"加拿大","v":"加拿大"},{"n":"其他","v":"其他"}]},{"key":"年代","name":"年代","value":[{"n":"全部","v":""},{"n":"2025","v":"2025"},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"}]},{"key":"语言","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"法语","v":"法语"},{"n":"德语","v":"德语"},{"n":"其它","v":"其它"}]}],"dsj":[{"key":"类型","name":"类型","value":[{"n":"全部","v":""},{"n":"爱情","v":"爱情"},{"n":"古装","v":"古装"},{"n":"悬疑","v":"悬疑"},{"n":"都市","v":"都市"},{"n":"武侠","v":"武侠"},{"n":"战争","v":"战争"},{"n":"军旅","v":"军旅"},{"n":"权谋","v":"权谋"},{"n":"青春偶像","v":"青春偶像"},{"n":"喜剧","v":"喜剧"},{"n":"家庭","v":"家庭"},{"n":"犯罪","v":"犯罪"},{"n":"动作","v":"动作"},{"n":"科幻","v":"科幻"},{"n":"竞技","v":"竞技"},{"n":"玄幻","v":"玄幻"},{"n":"奇幻","v":"奇幻"},{"n":"剧情","v":"剧情"},{"n":"历史","v":"历史"},{"n":"经典","v":"经典"},{"n":"乡村","v":"乡村"},{"n":"情景","v":"情景"},{"n":"商战","v":"商战"},{"n":"网剧","v":"网剧"},{"n":"其他","v":"其他"}]},{"key":"地区","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"大陆"},{"n":"韩国","v":"韩国"},{"n":"香港","v":"香港"},{"n":"台湾","v":"台湾"},{"n":"日本","v":"日本"},{"n":"美国","v":"美国"},{"n":"泰国","v":"泰国"},{"n":"英国","v":"英国"},{"n":"新加坡","v":"新加坡"},{"n":"其他","v":"其他"}]},{"key":"年代","name":"年代","value":[{"n":"全部","v":""},{"n":"2025","v":"2025"},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"}]},{"key":"语言","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]}],"dm":[{"key":"类型","name":"类型","value":[{"n":"全部","v":""},{"n":"武侠","v":"武侠"},{"n":"战斗","v":"战斗"},{"n":"情感","v":"情感"},{"n":"科幻","v":"科幻"},{"n":"热血","v":"热血"},{"n":"玄幻","v":"玄幻"},{"n":"推理","v":"推理"},{"n":"魔幻","v":"魔幻"},{"n":"搞笑","v":"搞笑"},{"n":"冒险","v":"冒险"},{"n":"萝莉","v":"萝莉"},{"n":"校园","v":"校园"},{"n":"恋爱","v":"恋爱"},{"n":"悬疑","v":"悬疑"},{"n":"日常","v":"日常"},{"n":"真人","v":"真人"},{"n":"历史","v":"历史"},{"n":"经典","v":"经典"},{"n":"动作","v":"动作"},{"n":"机战","v":"机战"},{"n":"竞技","v":"竞技"},{"n":"运动","v":"运动"},{"n":"战争","v":"战争"},{"n":"少年","v":"少年"},{"n":"少女","v":"少女"},{"n":"社会","v":"社会"},{"n":"原创","v":"原创"},{"n":"亲子","v":"亲子"},{"n":"益智","v":"益智"},{"n":"励志","v":"励志"},{"n":"其他","v":"其他"}]},{"key":"地区","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"大陆"},{"n":"日本","v":"日本"},{"n":"美国","v":"美国"},{"n":"其他","v":"其他"}]},{"key":"年代","name":"年代","value":[{"n":"全部","v":""},{"n":"2025","v":"2025"},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"}]},{"key":"语言","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]}],"zy":[{"key":"类型","name":"类型","value":[{"n":"全部","v":""},{"n":"真人秀","v":"真人秀"},{"n":"游戏","v":"游戏"},{"n":"竞技","v":"竞技"},{"n":"电竞","v":"电竞"},{"n":"推理","v":"推理"},{"n":"影视","v":"影视"},{"n":"脱口秀","v":"脱口秀"},{"n":"选秀","v":"选秀"},{"n":"情感","v":"情感"},{"n":"访谈","v":"访谈"},{"n":"播报","v":"播报"},{"n":"旅游","v":"旅游"},{"n":"音乐","v":"音乐"},{"n":"喜剧","v":"喜剧"},{"n":"美食","v":"美食"},{"n":"潮流运动","v":"潮流运动"},{"n":"亲子","v":"亲子"},{"n":"文化","v":"文化"},{"n":"互动","v":"互动"},{"n":"晚会","v":"晚会"},{"n":"资讯","v":"资讯"},{"n":"纪实","v":"纪实"},{"n":"曲艺","v":"曲艺"},{"n":"生活","v":"生活"},{"n":"职场","v":"职场"},{"n":"财经","v":"财经"},{"n":"求职","v":"求职"}]},{"key":"地区","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"大陆"},{"n":"香港","v":"香港"},{"n":"台湾","v":"台湾"},{"n":"日本","v":"日本"},{"n":"韩国","v":"韩国"},{"n":"美国","v":"美国"}]},{"key":"年代","name":"年代","value":[{"n":"全部","v":""},{"n":"2025","v":"2025"},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"}]},{"key":"语言","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]}]}}

        return result

    def homeVideoContent(self):
        videos = []

        try:
            detail = requests.get(url=xurl, headers=headerx)
            detail.encoding = "utf-8"
            res = detail.text
            doc = BeautifulSoup(res, "lxml")
            soups = doc.find_all('div', class_="vod-list")
            for soup in soups:
                vods = soup.find_all('div', class_="col-xs-4")
                for vod in vods:
                    names = vod.find('div', class_="vod-item")
                    name = names.find('h3').text
                    id = vod.select_one('h3 a')['href']
                    pics = vod.find_all('div')
                    pic = pics[1]['data-original']
                    if 'http' not in pic:
                        pic = xurl + pic
                    remarks = vod.find('span', class_="text-row-1")
                    remark = remarks.text.strip()
                    video = {
                        "vod_id": id,
                        "vod_name":  name,
                        "vod_pic": pic,
                        "vod_remarks":  remark
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
        if '类型' in ext.keys():
            lxType = ext['类型']
        else:
            lxType = ''
        if '地区' in ext.keys():
            DqType = ext['地区']
        else:
            DqType = ''
        if '语言' in ext.keys():
            YyType = ext['语言']
        else:
            YyType = ''
        if '年代' in ext.keys():
            NdType = ext['年代']
        else:
            NdType = ''
        if '剧情' in ext.keys():
            JqType = ext['剧情']
        else:
            JqType = ''
        if '排序' in ext.keys():
            pxType = ext['排序']
        else:
            pxType = ''
            url = f'{xurl}/vod/{cid}-{DqType}--{lxType}-{YyType}----{pg}---{NdType}/'
                    # https://cupfoxys.cc/vod/dsj-%E5%A4%A7%E9%99%86--%E7%88%B1%E6%83%85-%E5%9B%BD%E8%AF%AD-------2024/
        try:
            print(url)
            detail = requests.get(url=url, headers=headerx)
            detail.encoding = "utf-8"
            res = detail.text
            doc = BeautifulSoup(res, "lxml")
            soups = doc.find_all('div', class_="row")
            for soup in soups:
                vods = soup.find_all('div', class_="col-xs-4")
                for vod in vods:
                    names = vod.find('div', class_="vod-item")
                    name = names.find('h3').text
                    id = vod.select_one('h3 a')['href']
                    pics = vod.find_all('div')
                    pic = pics[1]['data-original']
                    if 'http' not in pic:
                        pic = xurl + pic
                    remarks = vod.find('span', class_="text-row-1")
                    remark = remarks.text.strip()
                    video = {
                        "vod_id": id,
                        "vod_name": name,
                        "vod_pic": pic,
                        "vod_remarks":  remark
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
        res = requests.get(url=did, headers=headerx)
        res.encoding = "utf-8"
        res = res.text
        tiaozhuan = '0'
        if tiaozhuan == '1':
            didt = self.extract_middle_text(res, 'class="play">', '</p>', 1, 'href="(.*?)"')
            if 'http' not in didt:
                didt = xurl + didt
                ress = requests.get(url=didt, headers=headerx)
                ress.encoding = "utf-8"
                ress = ress.text
        duoxian = '0'
        if duoxian == '1':
            doc = BeautifulSoup(ress, 'lxml')
            soups = doc.find('span', class_='animate__animated')
            vods = soups.find_all('a')[1:]
            res1 = ''
            for vod in vods:
                url = self.extract_middle_text(str(vod), 'href="', '"', 0)
                if 'http' not in url:
                    url = xurl + url
                    resss = requests.get(url, headers=headerx)
                    resss.encoding = 'utf-8'
                    resss = resss.text
                    res1 = res1 + resss
            res2 = ress + res1
        url = 'https://9071.kstore.vip/py/yz.txt'
        response = requests.get(url)
        response.encoding = 'utf-8'
        code = response.text
        name = self.extract_middle_text(code, "s1='", "'", 0)
        Jumps = self.extract_middle_text(code, "s2='", "'", 0)
        content = '😸繁华🎉绍剧情📢本资源来源于网络🚓侵权请联系删除👉' + self.extract_middle_text(res,'<p class="detail-intro-text','</p>', 0)
        content = content.replace('text-row ewave-collapse-content">', '').replace('\u3000\u3000', '')
        if name not in content:
            bofang = Jumps
        else:
            bofang = self.extract_middle_text(res, '<ul class="row ewave-tab-content', '</ul>', 3, 'href="(.*?)">(.*?)</a></li>')
        xianlu = self.extract_middle_text(res, 'ul class="tab-box','</ul>',2, '<a href=".*?">(.*?)</a>')
        actors = self.extract_middle_text(res, 'class="fa fa-user-o fa-fw"></i><span>主演：', '</li>', 1,'href=".*?" target=".*?">(.*?)</a>')
        director = self.extract_middle_text(res, 'class="fa fa-user-o fa-fw"></i><span>导演：', '</li>', 1,'<a href=".*?" target=".*?">(.*?)</a>')
        videos.append({
            "vod_id": did,
            "vod_actor": actors,
            "vod_director": director,
            "vod_content": content,
            "vod_play_from": xianlu,
            "vod_play_url": bofang
                     })
        result['list'] = videos
        return result
    def playerContent(self, flag, id, vipFlags):
        parts = id.split("http")
        xiutan = 0
        if xiutan == 0:
            if len(parts) > 1:
                before_https, after_https = parts[0], 'http' + parts[1]
            if '239755956819.mp4' in after_https:
                url = after_https
            else:
                res = requests.get(url=after_https, headers=headerx)
                res = res.text
                url = self.extract_middle_text(res, '},"url":"', '"', 0).replace('\\', '')
            result = {}
            result["parse"] = xiutan
            result["playUrl"] = ''
            result["url"] = url
            result["header"] = headerx
            return result
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
            url = f'{xurl}/search/-------------/?wd={key}'
        else:
            url = f'{xurl}/search/{key}----------{str(page)}---/'
        detail = requests.get(url=url, headers=headerx)
        detail.encoding = "utf-8"
        res = detail.text
        doc = BeautifulSoup(res, "lxml")
        soups = doc.find_all('div', class_="search-list")
        for soup in soups:
            vods = soup.find_all('div', class_="search-item row")
            for vod in vods:
                names = vod.find('h2', class_="search-item-title")
                name = names.find('a')['title']
                id = vod.find('a')['href']
                pic = vod.select_one('a div')['data-original']
                if 'http' not in pic:
                    pic = xurl + pic
                remarks = vod.find('ul', class_="search-item-desc")
                remark = remarks.find('li').text
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



