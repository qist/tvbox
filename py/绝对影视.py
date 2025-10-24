# -*- coding: utf-8 -*-
# by @嗷呜
import base64
import re
import sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from pyquery import PyQuery as pq
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):

    def init(self, extend=""):
        pass

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    host = 'https://www.jdys.art'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '"macOS"',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="134", "Google Chrome";v="134"',
        'dnt': '1',
        'sec-ch-ua-mobile': '?0',
        'origin': host,
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': f'{host}/',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'priority': 'u=1, i',
    }

    def homeContent(self, filter):
        data = self.getpq(self.fetch(self.host, headers=self.headers).text)
        result = {}
        classes = []
        for k in list(data('.navtop .navlist li').items())[:9]:
            classes.append({
                'type_name': k('a').text(),
                'type_id': k('a').attr('href'),
            })
        result['class'] = classes
        result['list'] = self.getlist(data('.mi_btcon .bt_img ul li'))
        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        data = self.getpq(self.fetch(f"{tid}{'' if pg == '1' else f'page/{pg}/'}", headers=self.headers).text)
        result = {}
        result['list'] = self.getlist(data('.mi_cont .bt_img ul li'))
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        data = self.getpq(self.fetch(ids[0], headers=self.headers).text)
        data2 = data('.moviedteail_list li')
        vod = {
            'vod_name': data('.dytext h1').text(),
            'type_name': data2.eq(0).text(),
            'vod_year': data2.eq(2).text(),
            'vod_area': data2.eq(1).text(),
            'vod_remarks': data2.eq(4).text(),
            'vod_actor': data2.eq(7).text(),
            'vod_director': data2.eq(5).text(),
            'vod_content': data('.yp_context').text().strip()
        }
        vdata = data('.paly_list_btn a')
        play = []
        for i in vdata.items():
            a = i.text() + "$" + i.attr.href
            play.append(a)
        vod["vod_play_from"] = "在线播放"
        vod["vod_play_url"] = "#".join(play)
        result = {"list": [vod]}
        return result

    def searchContent(self, key, quick, pg="1"):
        data = self.getpq(self.fetch(f"{self.host}/page/{pg}/?s={key}", headers=self.headers).text)
        return {'list': self.getlist(data('.mi_cont .bt_img ul li')), 'page': pg}

    def playerContent(self, flag, id, vipFlags):
        data = self.getpq(self.fetch(id, headers=self.headers).text)
        try:
            sc = data('.videoplay script').eq(-1).text()
            strd = re.findall(r'var\s+[^=]*=\s*"([^"]*)";', sc)
            kdata = re.findall(r'parse\((.*?)\);', sc)
            jm = self.aes(strd[0], kdata[0].replace('"', ''), kdata[1].replace('"', ''))
            url = re.search(r'url: "(.*?)"', jm).group(1)
            p = 0
        except:
            p = 1
            url = id
        result = {}
        result["parse"] = p
        result["url"] = url
        result["header"] = self.headers
        return result

    def localProxy(self, param):
        pass

    def getpq(self, text):
        try:
            return pq(text)
        except Exception as e:
            print(f"{str(e)}")
            return pq(text.encode('utf-8'))

    def getlist(self, data):
        videos = []
        for i in data.items():
            videos.append({
                'vod_id': i('a').attr('href'),
                'vod_name': i('a img').attr('alt'),
                'vod_pic': i('a img').attr('src'),
                'vod_remarks': i('.dycategory').text(),
                'vod_year': i('.dyplayinfo').text() or i('.rating').text(),
            })
        return videos

    def aes(self, word, key, iv):
        key = key.encode('utf-8')
        iv = iv.encode('utf-8')
        encrypted_data = base64.b64decode(word)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = cipher.decrypt(encrypted_data)
        decrypted_data = unpad(decrypted_data, AES.block_size)
        return decrypted_data.decode('utf-8')
