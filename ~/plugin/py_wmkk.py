# coding=utf-8
# !/usr/bin/python
import sys
import re
sys.path.append('..')
from base.spider import Spider



class Spider(Spider):  # 元类 默认的元类 type
    def getName(self):
        return "完美看看"

    def init(self, extend=""):
        print("============{0}============".format(extend))
        pass

    def homeContent(self, filter):
        result = {}
        cateManual = {
            "电影": "1",
            "国产剧": "5",
            "欧美剧": "2",
            "韩剧": "3",
            "泰剧": "9",
            "日剧": "4",
            "动漫": "6",
            "综艺": "7",
            "纪录片": "10"
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
        url = 'https://www.wanmeikk.film/category/{0}-{1}.html'.format(tid, pg)
        rsp = self.fetch(url)
        root = self.html(rsp.text)
        aList = root.xpath("//div[@class='stui-pannel_bd']/ul[1]/li")
        videos = []
        for a in aList:
            name = a.xpath('./div/a/@title')[0]
            pic = a.xpath('./div/a/@data-original')[0]
            mark = a.xpath("./div/a/span[@class='pic-text text-right']/text()")[0]
            sid = a.xpath("./div/a/@href")[0].replace("/", "").replace("project", "").replace(".html", "")
            videos.append({
                "vod_id": sid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": mark
            })
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, array):
        tid = array[0]
        url = 'https://www.wanmeikk.film/project/{0}.html'.format(tid)
        header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"}
        rsp = self.fetch(url, headers=header)
        root = self.html(rsp.content)
        divContent = root.xpath("//div[@class='col-lg-wide-75 col-xs-1']")[0]
        title = divContent.xpath(".//h1[@class='title']/text()")[0]
        pic = divContent.xpath(".//a[@class='stui-vodlist__thumb picture v-thumb']/img/@data-original")[0]
        detail = divContent.xpath(".//p[@class='desc detail hidden-xs']/span[@class='detail-content']/text()")[0]
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
            "vod_content": detail
        }
        infoArray = divContent.xpath(".//div[@class='stui-content__detail']/p[@class='data']")
        for info in infoArray:
            content = info.xpath('string(.)')
            if content.startswith('类型'):
                infon = content.split('\xa0')
                for inf in infon:
                    if inf.startswith('类型'):
                        vod['type_name'] = inf.replace("类型：", "")
                    if inf.startswith('地区'):
                        vod['vod_area'] = inf.replace("地区：", "")
                    if inf.startswith('年份'):
                        vod['vod_year'] = inf.replace("年份：", "")
            if content.startswith('主演'):
                vod['vod_actor'] = content.replace("\xa0", "/").replace("主演：", "")
            if content.startswith('导演'):
                vod['vod_director'] = content.replace("\xa0", "").replace("导演：", "")
        vod_play_url = '$$$'
        vod['vod_play_from'] = '完美看看'
        purl = divContent.xpath(".//div[@class='stui-pannel_bd col-pd clearfix']/ul/li")
        playList = []
        vodItems = []
        for plurl in purl:
            plaurl = plurl.xpath(".//a/@href")[0]
            name = plurl.xpath(".//a/text()")[0]
            tId = self.regStr(plaurl, '/play/(\\S+).html')
            vodItems.append(name + "$" + tId)
        joinStr = '#'
        joinStr = joinStr.join(vodItems)
        playList.append(joinStr)
        vod_play_url = vod_play_url.join(playList)
        vod['vod_play_url'] = vod_play_url
        result = {
            'list': [
                vod
            ]
        }
        return result

    def searchContent(self, key, quick):
        result = {}
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {}
        url = 'https://www.wanmeikk.film/play/{0}.html'.format(id)
        rsp = self.fetch(url)
        root = self.html(rsp.text)
        scripts = root.xpath("//div[@class='stui-player__video embed-responsive embed-responsive-16by9 clearfix']/script/text()")[0]
        key = scripts.split("url")[1].replace('"', "").replace(':', "").replace(',', "").replace("'", "")
        surl = 'https://www.wanmeikk.film/dplayer.php?url={0}'.format(key)
        srsp = self.fetch(surl)
        sroot = self.html(srsp.text)
        murl = sroot.xpath("//script[@type='text/javascript']/text()")[0]
        mp4url = re.findall(r"var urls = '(.*)';", murl)[0]
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = mp4url
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