# coding=utf-8
# !/usr/bin/python
import sys
import re
sys.path.append('..')
from base.spider import Spider
import urllib.parse
import json

class Spider(Spider):  # 元类 默认的元类 type
    def getName(self):
        return "快播影视"

    def init(self, extend=""):
        print("============{0}============".format(extend))
        pass

    def homeContent(self, filter):
        result = {}
        cateManual = {
            "电影": "movie",
            "剧集": "serie",
            "综艺": "variety",
            "动漫": "anime"
        }
        classes = []
        for k in cateManual:
            classes.append({
                'type_name': k,
                'type_id': cateManual[k]
            })

        result['class'] = classes
        if (filter):
            result['filters'] = self.config['filter']
        return result

    def homeVideoContent(self):
        result = {
            'list': []
        }
        return result

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"}
        url = 'https://www.3qu.live/videos/{0}?page={1}'.format(tid, pg)
        rsp = self.fetch(url,headers=header)
        root = self.html(self.cleanText(rsp.text))
        aList = root.xpath("//div[@class='main-content-box']/div/div/div/div/div/div/a")
        videos = []
        for a in aList:
            name = a.xpath('./@title')[0]
            picl = a.xpath('./@style')[0]
            pica = re.findall(r"url\(\'(.*)\'\);", picl)[0]
            pic = 'https://www.3qu.live{0}'.format(pica)
            sidh = a.xpath("./@href")[0]
            sid = self.regStr(sidh,'/videos/(\\S+).html')
            videos.append({
                "vod_id": sid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": ""
            })
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 100
        result['total'] = 99999
        return result

    def detailContent(self, array):
        tid = array[0]
        url = 'https://www.3qu.live/videos/{0}.html'.format(tid)
        header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"}
        rsp = self.fetch(url,headers=header)
        root = self.html(self.cleanText(rsp.text))
        divContent = root.xpath("//div[@class='video-detail row']")[0]
        title = divContent.xpath(".//div[@class='info-box']/a/h1/text()")[0]
        pica = divContent.xpath(".//div[@class='thumb-box']/img/@src")[0]
        pic = 'https://www.3qu.live{0}'.format(pica)
        vod = {
            "vod_id": tid,
            "vod_name": title,
            "vod_pic": pic,
            "type_name": "",
            "vod_year": "",
            "vod_area": "",
            "vod_remarks": "",
            "vod_actor": "",
            "vod_director": "",
            "vod_content": ""
        }
        infoArray = divContent.xpath(".//div[@class='info-box']/ul/li")
        for info in infoArray:
            content = info.xpath('string(.)')
            flag = "类型" in content
            if flag == True:
                infon = content.strip().split(' ')
                for inf in infon:
                    if inf.startswith('类型'):
                        vod['type_name'] = inf.replace("类型:", "")
                    if inf.startswith('地区'):
                        vod['vod_area'] = inf.replace("地区:", "")
                    if inf.startswith('语言'):
                        vod['vod_remarks'] = inf.replace("语言:", "")
            if content.startswith('演员'):
                vod['vod_actor'] = content.replace("演员:", "")
            if content.startswith('年份'):
                yearl = content.split(' ')
                year = yearl[0].replace("年份:", "")
                vod['vod_year'] = year
            if content.startswith('导演'):
                vod['vod_director'] = content.replace("导演:", "")
            if content.startswith('简介'):
                vod['vod_content'] = content.replace("简介:", "")
        vodList = root.xpath(".//div[@class='tab-content']/div[@id='playlist']/a")
        playUrl = ''
        for vl in vodList:
            name = vl.xpath("./text()")[0]
            did = vl.xpath("./@data-id")[0]
            playUrl = playUrl + '{0}${1}_{2}#'.format(name,tid,did)
        vod['vod_play_from'] = '快播影视'
        vod['vod_play_url'] = playUrl
        result = {
            'list': [
                vod
            ]
        }
        return result

    def searchContent(self, key, quick):
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"}
        url = 'https://www.3qu.live/api/v1/search?page=1&q={0}&type=all&period=0'.format(key)
        rsp = self.fetch(url, headers=header)
        jRoot = json.loads(rsp.text)
        videos = []
        vodList = jRoot['data']['videos']
        for vod in vodList:
            id = vod['id']
            title = vod['name']
            img = vod['coverURL']
            pic = 'https://www.3qu.live{0}'.format(img)
            videos.append({
                "vod_id": id,
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": ""
            })
        result = {
            'list': videos
        }
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {}
        ids = id.split("_")
        header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"}
        url = 'https://www.3qu.live/api/v1/videos/{0}/{1}/playUrl'.format(ids[0],ids[1])
        rsp = self.fetch(url,headers=header)
        jRoot = json.loads(rsp.text)
        apiurl = jRoot['data']['url']
        url = 'https://www.3qu.live{0}'.format(apiurl)
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] =url
        result["header"] = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"}
        return result

    config = {
        "player": {},
        "filter": {}
    }
    header = {}

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def localProxy(self, param):
        action = {
            'url': '',
            'header': '',
            'param': '',
            'type': 'string',
            'after': ''
        }
        return [200, "video/MP2T", action, ""]