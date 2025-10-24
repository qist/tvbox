# coding=utf-8
# !/python
import sys
import requests
from bs4 import BeautifulSoup
import re
from base.spider import Spider

sys.path.append('..')
xurl = "https://kb11.adultporna-av1sim111.xyz"
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

    def homeVideoContent(self):
        videos = []
        try:
            res = requests.get(xurl + '/show/30/', headers=headerx)
            res.encoding = "utf-8"
            res = res.text
            doc = BeautifulSoup(res, "html.parser")
            vodss = doc.find('ul', class_='row row-space8 row-m-space8')
            vods = vodss.find_all('li')
            for vod in vods:
                name = vod.select_one('section a')['title']
                id = vod.select_one('section a')['href']
                remarks = vod.select_one('section a span small').text
                pic = vod.select_one('section a img')['src']
                video = {
                    "vod_id": id,
                    "vod_name": name,
                    "vod_pic": pic,
                    "vod_remarks": remarks
                }
                videos.append(video)
        except:
            pass
        result = {'list': videos}
        return result

    def homeContent(self, filter):
        res = requests.get(xurl + '/zzzz', headers=headerx)
        res.encoding = "utf-8"
        res = res.text
        doc = BeautifulSoup(res, "html.parser")
        result = {}
        result['class'] = []
        vodss = doc.find_all('dd')        
        result['class'].append({'type_id': '/t/86', 'type_name': '女优'})
        result['class'].append({'type_id': '/t/141', 'type_name': '日本番號'})
        result['class'].append({'type_id': '/t/1', 'type_name': '日本有码'})
        result['class'].append({'type_id': '/t/5', 'type_name': '日本无码'})
        result['class'].append({'type_id': '/t/32', 'type_name': '日本巨乳无码'})
        result['class'].append({'type_id': '/t/34', 'type_name': '日本人妻无码'})
        result['class'].append({'type_id': '/t/35', 'type_name': '日本制服无码'})        
        result['class'].append({'type_id': '/t/223', 'type_name': '日本乱伦无码'})
        result['class'].append({'type_id': '/t/224', 'type_name': '日本强奸无码'})        
        result['class'].append({'type_id': '/t/36', 'type_name': '日本丝袜美腿'})
        result['class'].append({'type_id': '/t/13', 'type_name': '日本中文字幕'})
        result['class'].append({'type_id': '/t/53', 'type_name': '日本绝美少女'}) 
        result['class'].append({'type_id': '/t/6', 'type_name': '日本强奸乱伦'})
        result['class'].append({'type_id': '/t/7', 'type_name': '日本巨乳'})
        result['class'].append({'type_id': '/t/9', 'type_name': '日本制服诱惑'})
        result['class'].append({'type_id': '/t/11', 'type_name': '日本调教'})
        result['class'].append({'type_id': '/t/58', 'type_name': '日本口爆'})
        result['class'].append({'type_id': '/t/30', 'type_name': '欧美'})
        result['class'].append({'type_id': '/t/164', 'type_name': '成人动漫'})
        result['class'].append({'type_id': '/t/85', 'type_name': '伦理电影'}) 
        result['class'].append({'type_id': '/t/2', 'type_name': '国产传媒'})
        result['class'].append({'type_id': '/t/163', 'type_name': '国产视频'})        
        result['class'].append({'type_id': '/t/67', 'type_name': '国产空姐模特'})
        result['class'].append({'type_id': '/t/69', 'type_name': '国产学生'})
        result['class'].append({'type_id': '/t/70', 'type_name': '国产人妻熟女'})
        result['class'].append({'type_id': '/t/71', 'type_name': '国产乱伦'})
        result['class'].append({'type_id': '/t/72', 'type_name': '国产自慰'})
        result['class'].append({'type_id': '/t/73', 'type_name': '国产野合车震'})
        result['class'].append({'type_id': '/t/75', 'type_name': '国产名人'})
        result['class'].append({'type_id': '/t/74', 'type_name': '国产OL'})
        result['class'].append({'type_id': '/t/18', 'type_name': '国产剧情'})
        result['class'].append({'type_id': '/t/19', 'type_name': '国产偷怕'})
        result['class'].append({'type_id': '/t/76', 'type_name': '国产网曝'})        
        result['class'].append({'type_id': '/t/227', 'type_name': '综合传媒'})
        result['class'].append({'type_id': '/t/38', 'type_name': '麻豆合集'})
        result['class'].append({'type_id': '/t/109', 'type_name': '葫芦影业'})        
        result['class'].append({'type_id': '/t/111', 'type_name': '天美传媒'})
        result['class'].append({'type_id': '/t/112', 'type_name': '果冻传媒'})
        result['class'].append({'type_id': '/t/131', 'type_name': '91制片厂'})
        result['class'].append({'type_id': '/t/113', 'type_name': '蜜桃传媒'})
        result['class'].append({'type_id': '/t/114', 'type_name': '精东影业'})
        result['class'].append({'type_id': '/t/115', 'type_name': '皇家华人'})
        result['class'].append({'type_id': '/t/116', 'type_name': 'SWAG'})       
        result['class'].append({'type_id': '/t/120', 'type_name': '兔子先生'})
        result['class'].append({'type_id': '/t/122', 'type_name': 'PsychoPornTW'})        
        result['class'].append({'type_id': '/t/124', 'type_name': '微啪 & 陌丽影像传媒'})
        result['class'].append({'type_id': '/t/125', 'type_name': '大象传媒'})
        result['class'].append({'type_id': '/t/126', 'type_name': '乌鸦传媒'})
        result['class'].append({'type_id': '/t/141', 'type_name': '日本番号'})
        result['class'].append({'type_id': '/t/225', 'type_name': '综合番号'})
        result['class'].append({'type_id': '/t/142', 'type_name': '200GANA'})
        result['class'].append({'type_id': '/t/146', 'type_name': '259LUXU'})
        result['class'].append({'type_id': '/t/147', 'type_name': '261ARA'})
        result['class'].append({'type_id': '/t/148', 'type_name': '277DCV'})
        result['class'].append({'type_id': '/t/143', 'type_name': '300MIUM'})
        result['class'].append({'type_id': '/t/149', 'type_name': '300MAAN'})
        result['class'].append({'type_id': '/t/150', 'type_name': '300NTK'})
        result['class'].append({'type_id': '/t/152', 'type_name': '328HMDN'})        
        result['class'].append({'type_id': '/t/154', 'type_name': '336KNB'})
        result['class'].append({'type_id': '/t/155', 'type_name': '348NTR'})
        result['class'].append({'type_id': '/t/156', 'type_name': '390JAC'})
        result['class'].append({'type_id': '/t/158', 'type_name': '428SUKE'})
        result['class'].append({'type_id': '/t/181', 'type_name': 'AARM'})
        result['class'].append({'type_id': '/t/180', 'type_name': 'ADN'})
        result['class'].append({'type_id': '/t/185', 'type_name': 'ATID'})        
        result['class'].append({'type_id': '/t/192', 'type_name': 'DFDM'})
        result['class'].append({'type_id': '/t/194', 'type_name': 'DLDSS'})
        
        
        for vod in vodss:
            id = vod.find('a')['href'].rstrip("/")
            name = vod.find('a').text
            if not any(d['type_name'] == name for d in result['class']):
                result['class'].append({'type_id': id, 'type_name': name})
        return result

    def categoryContent(self, cid, pg, filter, ext):
        result = {}
        videos = []
        if pg == "" or pg == 1:
            url = xurl + cid
        else:
            url = xurl + cid + '-' + str(pg)

        
        res = requests.get(url=url, headers=headerx)
        res.encoding = "utf-8"
        res = res.text

        doc = BeautifulSoup(res, "html.parser")
        vodss = doc.find('ul', class_='row row-space8 row-m-space8')
        vods = vodss.find_all('li')
        for vod in vods:
            name = vod.select_one('section a')['title']
            id = vod.select_one('section a')['href']
            remarks = vod.select_one('section a span small').text
            pic = vod.select_one('section a img')['src']
            video = {
                "vod_id": id,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remarks
            }
            videos.append(video)

        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        did = ids[0].replace("voddetail", "v")
        videos = []
        result = {}
        res = requests.get(url=xurl + did, headers=headerx)
        res.encoding = "utf-8"
        res = res.text
        source_match = re.search(r'"","url":"(.*?)"', res)
        if source_match:
            purl = source_match.group(1).replace("\\", "")
            videos.append({
                "vod_id": did,
                "vod_name": '',
                "vod_pic": "",
                "type_name": "",
                "vod_year": "",
                "vod_area": "",
                "vod_remarks": "",
                "vod_actor": "",
                "vod_director": "",
                "vod_content": "",
                "vod_play_from": '直链播放',
                "vod_play_url": purl
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

    def searchContent(self, key, quick):
        return self.searchContentPage(key, quick, '1')

    def searchContentPage(self, key, quick, page):
        result = {}
        

        header2 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'
        }
        
        res = requests.get(xurl + '/s/page/' + str(page) + '/wd/' + key, headers=header2)
        res.encoding = "utf-8"
        res = res.text
        videos = []
        doc = BeautifulSoup(res, "html.parser")
        vodss = doc.find('ul', class_='row row-space8 row-m-space8')
        vods = vodss.find_all('li')
        for vod in vods:
            name = vod.select_one('section a')['title']
            id = vod.select_one('section a')['href']
            remarks = vod.select_one('section a span small').text
            pic = vod.select_one('section a img')['src']
            video = {
                "vod_id": id,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remarks
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
