# -*- coding: utf-8 -*-
# by @嗷呜
import re
import sys
from Crypto.Hash import MD5
sys.path.append("..")
import json
import time
from pyquery import PyQuery as pq
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

    def action(self, action):
        pass

    def destroy(self):
        pass

    host = 'https://www.lreeok.vip'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'sec-ch-ua-platform': '"macOS"',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="134", "Google Chrome";v="134"',
        'Origin': host,
        'Referer': f"{host}/",
    }

    def homeContent(self, filter):
        data = self.getpq(self.fetch(self.host, headers=self.headers).text)
        result = {}
        classes = []
        for k in data('.head-more.box a').items():
            i = k.attr('href')
            if i and '/vod' in i:
                classes.append({
                    'type_name': k.text(),
                    'type_id': re.search(r'\d+', i).group(0)
                })
        result['class'] = classes
        result['list'] = self.getlist(data('.border-box.diy-center .public-list-div'))
        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        body = {'type': tid, 'class': '', 'area': '', 'lang': '', 'version': '', 'state': '', 'letter': '', 'page': pg}
        data = self.post(f"{self.host}/index.php/api/vod", headers=self.headers, data=self.getbody(body)).json()
        result = {}
        result['list'] = data['list']
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        data = self.getpq(self.fetch(f"{self.host}/voddetail/{ids[0]}.html", headers=self.headers).text)
        v = data('.detail-info.lightSpeedIn .slide-info')
        vod = {
            'vod_year': v.eq(-1).text(),
            'vod_remarks': v.eq(0).text(),
            'vod_actor': v.eq(3).text(),
            'vod_director': v.eq(2).text(),
            'vod_content': data('.switch-box #height_limit').text()
        }
        np = data('.anthology.wow.fadeInUp')
        ndata = np('.anthology-tab .swiper-wrapper .swiper-slide')
        pdata = np('.anthology-list .anthology-list-box ul')
        play, names = [], []
        for i in range(len(ndata)):
            n = ndata.eq(i)('a')
            n('span').remove()
            names.append(n.text())
            vs = []
            for v in pdata.eq(i)('li').items():
                vs.append(f"{v.text()}${v('a').attr('href')}")
            play.append('#'.join(vs))
        vod["vod_play_from"] = "$$$".join(names)
        vod["vod_play_url"] = "$$$".join(play)
        result = {"list": [vod]}
        return result

    def searchContent(self, key, quick, pg="1"):
        # data = self.getpq(self.fetch(f"{self.host}/vodsearch/{key}----------{pg}---.html", headers=self.headers).text)
        # return {'list': self.getlist(data('.row-right .search-box .public-list-bj')), 'page': pg}
        data = self.fetch(
            f"{self.host}/index.php/ajax/suggest?mid={pg}&wd={key}&limit=999&timestamp={int(time.time() * 1000)}",
            headers=self.headers).json()
        videos = []
        for i in data['list']:
            videos.append({
                'vod_id': i['id'],
                'vod_name': i['name'],
                'vod_pic': i['pic']
            })
        return {'list': videos, 'page': pg}

    def playerContent(self, flag, id, vipFlags):
        h, p = {"User-Agent": "okhttp/3.14.9"}, 1
        url = f"{self.host}{id}"
        data = self.getpq(self.fetch(url, headers=self.headers).text)
        try:
            jstr = data('.player .player-left script').eq(0).text()
            jsdata = json.loads(jstr.split('aaa=')[-1])
            body = {'url': jsdata['url']}
            if not re.search(r'\.m3u8|\.mp4', body['url']):
                data = self.post(f"{self.host}/okplay/api_config.php", headers=self.headers,
                                 data=self.getbody(body)).json()
                url = data.get('url') or data.get('data', {}).get('url')
            p = 0
        except Exception as e:
            print('错误信息：', e)
            pass
        result = {}
        result["parse"] = p
        result["url"] = url
        result["header"] = h
        return result

    def localProxy(self, param):
        pass

    def getbody(self, params):
        t = int(time.time())
        h = MD5.new()
        h.update(f"DS{t}DCC147D11943AF75".encode('utf-8'))
        key = h.hexdigest()
        params.update({'time': t, 'key': key})
        return params

    def getlist(self, data):
        videos = []
        for i in data.items():
            id = i('a').attr('href')
            if id:
                id = re.search(r'\d+', id).group(0)
                img = i('img').attr('data-src')
                if img and 'url=' in img: img = f'{self.host}{img}'
                videos.append({
                    'vod_id': id,
                    'vod_name': i('img').attr('alt'),
                    'vod_pic': img,
                    'vod_remarks': i('.public-prt').text() or i('.public-list-prb').text()
                })
        return videos

    def getpq(self, data):
        try:
            return pq(data)
        except Exception as e:
            print(f"{str(e)}")
            return pq(data.encode('utf-8'))
