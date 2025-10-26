# -*- coding: utf-8 -*-
# by @嗷呜
import re
import sys
from urllib.parse import quote, urlparse
from Crypto.Hash import SHA256
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

    host='https://www.knvod.com'

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Sec-Fetch-Dest': 'document',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="134", "Google Chrome";v="134"',
        'sec-ch-ua-platform': '"macOS"',
        'Origin': host,
        'Referer': f"{host}/",
        'Cookie':'X-Robots-Tag=CDN-VERIFY'
    }

    def homeContent(self, filter):
        data=self.getpq(self.fetch(self.host,headers=self.headers).text)
        result = {}
        classes = []
        for k in data('.head-more.box a').items():
            i=k.attr('href')
            if i and '/show' in i:
                classes.append({
                    'type_name': k.text(),
                    'type_id': re.findall(r'\d+', i)[0]
                })
        result['class'] = classes
        result['list']=self.getlist(data('.border-box.public-r .public-list-div'))
        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        data=self.getpq(self.fetch(f"{self.host}/show/{tid}--------{pg}---/",headers=self.headers).text)
        result = {}
        result['list'] = self.getlist(data('.border-box.public-r .public-list-div'))
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        data = self.getpq(self.fetch(f"{self.host}/list/{ids[0]}/", headers=self.headers).text)
        v=data('.detail-info.lightSpeedIn .slide-info')
        vod = {
            'vod_year': v.eq(-1).text().split(':',1)[-1],
            'vod_remarks': v.eq(0),
            'vod_actor': v.eq(3).text().split(':',1)[-1],
            'vod_director': v.eq(2).text().split(':',1)[-1],
            'vod_content': data('.switch-box #height_limit').text()
        }
        np=data('.anthology.wow.fadeInUp')
        ndata=np('.anthology-tab .swiper-wrapper .swiper-slide')
        pdata=np('.anthology-list .anthology-list-box ul')
        play,names=[],[]
        for i in range(len(ndata)):
            n=ndata.eq(i)('a')
            n('span').remove()
            names.append(n.text())
            vs=[]
            for v in pdata.eq(i)('li').items():
                vs.append(f"{v.text()}${v('a').attr('href')}")
            play.append('#'.join(vs))
        vod["vod_play_from"] = "$$$".join(names)
        vod["vod_play_url"] = "$$$".join(play)
        result = {"list": [vod]}
        return result

    def searchContent(self, key, quick, pg="1"):
        data = self.fetch(f"{self.host}/index.php/ajax/suggest?mid=1&wd={key}&limit=9999&timestamp={int(time.time()*1000)}", headers=self.headers).json()
        videos=[]
        for i in data['list']:
            videos.append({
                'vod_id': i['id'],
                'vod_name': i['name'],
                'vod_pic': i['pic']
            })
        return {'list':videos,'page':pg}

    def playerContent(self, flag, id, vipFlags):
        h={
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.8 Mobile/15E148 Safari/604.1',
            'Origin': self.host
        }
        data = self.getpq(self.fetch(f"{self.host}{id}", headers=self.headers).text)
        try:
            jstr = data('.player-box .player-left script').eq(1).text()
            jsdata = json.loads(jstr.split('=',1)[-1])
            url = jsdata.get('url')
            if not re.search(r'\.m3u8|\.mp4',jsdata['url']):
                jxd=self.fetch(f"{self.host}/static/player/{jsdata['from']}.js", headers=self.headers).text
                jx=re.search(r'http.*?url=', jxd)
                if not jx:raise Exception('未找到jx')
                parsed_url = urlparse(jx.group())
                jxhost = parsed_url.scheme + "://" + parsed_url.netloc
                title=data('head title').eq(0).text().split('-')[0]
                next=f"{self.host.split('//')[-1]}{jsdata['link_next']}" if jsdata.get('link_next') else ''
                cd=self.fetch(f"{jx.group()}{jsdata['url']}&next=//{next}&title={quote(title)}", headers=self.headers).text
                match = re.search(r'var\s+config\s*=\s*(\{[\s\S]*?\})', cd)
                if not match:raise Exception('未找到config')
                cm=re.sub(r',\s*}(?=\s*$)', '}', match.group(1))
                config=json.loads(cm)
                config.update({'key':self.sha256(f"{self.gettime()}knvod")})
                config.pop('next',None)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.8 Mobile/15E148 Safari/604.1',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Cache-Control': 'no-cache',
                    'DNT': '1',
                    'Origin': jxhost,
                    'Pragma': 'no-cache',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Storage-Access': 'active',
                    'X-Requested-With': 'XMLHttpRequest',
                }
                h['Origin']=jxhost
                jd=self.post(f"{jxhost}/post.php", headers=headers, data=json.dumps(config))
                data=json.loads(jd.content.decode('utf-8-sig'))
                url=data.get('knvod')
            p = 0
            if not url:raise Exception('未找到播放地址')
        except Exception as e:
            print('错误信息：',e)
            p,url=1,f"{self.host}{id}"
        return {"parse": p, "url": url, "header": h}

    def localProxy(self, param):
        pass

    def getlist(self,data):
        videos=[]
        for i in data.items():
            id = i('a').attr('href')
            if id:
                id = re.search(r'\d+', id).group(0)
                img = i('img').attr('data-src')
                if img and 'url=' in img and 'http' not in img: img = f'{self.host}{img}'
                videos.append({
                    'vod_id': id,
                    'vod_name': i('a').attr('title'),
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

    def gettime(self):
        current_time = int(time.time())
        hourly_timestamp = current_time - (current_time % 3600)
        return hourly_timestamp

    def sha256(self, text):
        sha = SHA256.new()
        sha.update(text.encode())
        return sha.hexdigest()
