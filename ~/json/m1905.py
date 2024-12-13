#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import re
import math
import json
import time
import hashlib
import uuid

class Spider(Spider):  # 元类 默认的元类 type
    def getName(self):
        return "1905电影网"
    def init(self,extend=""):
        pass
    def isVideoFormat(self,url):
        pass
    def manualVideoCheck(self):
        pass
    def homeContent(self,filter):
        result = {}
        cateManual = {
            "电影": "n_1/o3p",
            "微电影":"n_1_c_922/o3p",
            "系列电影":"n_2/o3p",
            "记录片":"c_927/o3p",
            "晚会":"n_1_c_586/o3p",
            "独家":"n_1_c_178/o3p",
            "综艺":"n_1_c_1024/o3p",
            "体育":"n_1_c_1053/o3p"
        }
        classes = []
        for k in cateManual:
            classes.append({
                'type_name':k,
                'type_id':cateManual[k]
            })
        result['class'] = classes
        return result
    def homeVideoContent(self):
        result = {}
        url = 'https://www.1905.com/vod/cctv6/lst/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43',
            'Referer': 'https://www.1905.com/vod/list/n_1/o3p1.html',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
        }
        rsp = self.fetch(url, headers=headers)
        html = self.html(rsp.text)
        aList = html.xpath("//div[@class='grid-2x']/a")
        videos = []
        for a in aList:
            aid = a.xpath("./@href")[0] #https://www.1905.com/vod/play/85646.shtml
            if '//vip.1905.com' in str(aid):
                continue #跳过VIP视频
            aid = self.regStr(reg=r'play/(.*?).sh', src=aid) # 85646
            img = a.xpath('./img/@src')[0]
            title = a.xpath('./img/@alt')[0]
            videos.append({
            "vod_id": aid,
            "vod_name": title,
            "vod_pic": img,
            "vod_remarks": ''
            })
        result['list'] = videos
        return result
    def categoryContent(self,tid,pg,filter,extend):
        result = {}
        url = 'https://www.1905.com/vod/list/{}{}.html'.format(tid, pg)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43',
            'Referer': 'https://www.1905.com/vod/list/n_1/o3p1.html',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
        }
        rsp = self.fetch(url, headers=headers)
        html = self.html(rsp.text)
        aList = html.xpath("//section[contains(@class,'search-list')]/div/a" if tid != u'n_2/o3p' else "//div[@class='mod']/div[1]/a")
        videos = []
        limit = len(aList)
        for a in aList:
            aid = a.xpath("./@href")[0]  # https://www.1905.com/vod/play/85646.shtml
            aid = self.regStr(reg=r'play/(.*?).sh', src=aid)  # 85646
            img = a.xpath('./img/@src')[0]
            title = a.xpath('./@title')[0]
            videos.append({
                "vod_id": aid,
                "vod_name": title,
                "vod_pic": img,
                "vod_remarks": ''
        })
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 100
        result['limit'] = limit
        result['total'] = 100 * limit
        return result
    def detailContent(self,array):
        aid = array[0]
        url = "https://www.1905.com/api/content/?callback=&m=Vod&a=getVodSidebar&id={0}&fomat=json".format(aid)
        rsp = self.fetch(url)
        root = json.loads(rsp.text)
        title = root['title']
        pic = root['thumb']
        remark = root['commendreason']
        content = root['description']
        actor = root['starring']
        direct = root['direct']
        vod = {
            "vod_id": aid,
            "vod_name": title,
            "vod_pic": pic,
            "type_name": "",
            "vod_year": "",
            "vod_area": "",
            "vod_remarks": remark,
            "vod_actor": actor,
            "vod_director":direct,
            "vod_content": content
                }
        vodItems = []
        vodItems.append(title + "$" + aid)
        #处理多集的电影
        series = root['info']['series_data']
        for ser in series:
            vodItems.append(ser['title'] + "$" + ser['contentid'])
        playList = []
        joinStr = '#'.join(vodItems)
        playList.append(joinStr)
        vod['vod_play_from'] = '默认最高画质'
        vod['vod_play_url'] = '$$$'.join(playList)
        result = {
            'list': [
                vod
            ]
        }
        return result
    def searchContent(self,key,quick):
        result = {}
        url = 'https://www.1905.com/search/index-p-type-all-q-{}.html'.format(key)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43',
            'Referer': 'https://www.1905.com/vod/list/n_1/o3p1.html',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
        }
        rsp = self.fetch(url, headers=headers)
        html = self.html(rsp.text)
        aList = html.xpath("//div[contains(@class,'movie_box')]/div/div")
        videos = []
        for a in aList:
            aid = a.xpath("./div/ul/li[contains(@class,'paly-tab-icon')]/a/@href")[0] #https://www.1905.com/vod/play/85646.shtml
            if len(aid) == 0:
                continue
            aid = self.regStr(reg=r'play/(.*?).sh', src=aid) # 85646
            img = a.xpath('./div/div/a/img/@src')[0]
            title = a.xpath('./div/a/img/@alt')[0]
            videos.append({
                "vod_id": aid,
                "vod_name": title,
                "vod_pic": img,
                "vod_remarks": ''
            })
        result['list'] = videos
        return result
    def playerContent(self,flag,id,vipFlags):
        result = {}
        nonce = int(round(time.time() * 1000))
        expiretime = nonce + 600
        uid = str(uuid.uuid4())
        playerid = uid.replace("-", "")[5:20]
        signature = 'cid={0}&expiretime={1}&nonce={2}&page=https%3A%2F%2Fwww.1905.com%2Fvod%2Fplay%2F{3}.shtml&playerid={4}&type=hls&uuid={5}.dde3d61a0411511d'.format(id,expiretime,nonce,id,playerid,uid)
        signature = hashlib.sha1(signature.encode()).hexdigest()
        url = 'https://profile.m1905.com/mvod/getVideoinfo.php?nonce={0}&expiretime={1}&cid={2}&uuid={3}&playerid={4}&page=https%3A%2F%2Fwww.1905.com%2Fvod%2Fplay%2F{5}.shtml&type=hls&signature={6}&callback='.format(nonce,expiretime,id,uid,playerid,id,signature)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43',
            'Referer': 'https://www.1905.com/vod/list/n_1/o3p1.html',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
        }
        rsp = self.fetch(url,headers=headers)
        jo = json.loads(rsp.text.replace("(", "").replace(")", ""))
        data = jo['data']['sign']
        sign = ''
        qualityStr = ''
        if 'uhd' in data.keys():
            sign = data['uhd']['sign']
            qualityStr = 'uhd'
        elif 'hd' in data.keys():
            sign = data['hd']['sign']
            qualityStr = 'hd'
        elif 'sd' in data.keys():
            sign = data['sd']['sign']
            qualityStr = 'sd'
        host = jo['data']['quality'][qualityStr]['host']
        path = jo['data']['path'][qualityStr]['path']
        playUrl = host + sign + path
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = playUrl
        result["header"] = ''
        return result

    config = {
        "player": {},
        "filter": {}
    }
    header = {}

    def localProxy(self,param):
        return [200, "video/MP2T", action, ""]
