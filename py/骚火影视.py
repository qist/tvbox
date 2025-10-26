# -*- coding: utf-8 -*-
# by @嗷呜
import re
import sys
from urllib.parse import urlparse
import base64
from pyquery import PyQuery as pq
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):

    def init(self, extend=""):
        self.host=self.gethost()
        self.headers.update({'referer': f'{self.host}/'})
        pass

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="130", "Google Chrome";v="130"',
        'sec-ch-ua-platform': '"Android"',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }

    def homeContent(self, filter):
        data=self.getpq()
        result = {}
        classes = []
        filters = {"1": {"name": "类型","key": "tid","value": [{"n": "喜剧","v": 6},{"n": "爱情","v": 7},{"n": "恐怖","v": 8},{"n": "动作","v": 9},{"n": "科幻","v": 10},{"n": "战争","v": 11},{"n": "犯罪","v": 12},{"n": "动画","v": 13},{"n": "奇幻","v": 14},{"n": "剧情","v": 15},{"n": "冒险","v": 16},{"n": "悬疑","v": 17},{"n": "惊悚","v": 18},{"n": "其它","v": 19}]},"2": {"name": "类型","key": "tid","value": [{"n": "大陆剧","v": 20},{"n": "港剧","v": 21},{"n": "韩剧","v": 22},{"n": "美剧","v": 23},{"n": "日剧","v": 24},{"n": "英剧","v": 25},{"n": "台剧","v": 26},{"n": "其它","v": 27}]}}
        for k in data('.top_bar.clearfix a').items():
            j = k.attr('href')
            if j and 'list' in j:
                id = re.search(r'\d+', j).group(0)
                classes.append({
                    'type_name': k.text(),
                    'type_id': id
                })
        result['class'] = classes
        result['filters'] = filters
        result['list'] = self.getlist(data('.grid_box ul li'))
        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        data=self.getpq(f"/list/{extend.get('tid',tid)}-{pg}.html")
        result = {}
        result['list'] = self.getlist(data('.grid_box ul li'))
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        data=self.getpq(ids[0])
        vod = {
            'vod_remarks': data('.grid_box.v_info_box p').text(),
            'vod_content': data('.p_txt.show_part').text().split('\n')[0],
        }
        n=list(data('.play_from ul li').items())
        p=list(data('ul.play_list li').items())
        ns,ps=[],[]
        for i,j in enumerate(n):
            ns.append(j.text())
            ps.append('#'.join([f"{k.text()}${k.attr('href')}" for k in list(p[i]('a').items())[::-1]]))
        vod['vod_play_from']='$$$'.join(ns)
        vod['vod_play_url']='$$$'.join(ps)
        return {'list':[vod]}

    def searchContent(self, key, quick, pg="1"):
        pass

    def playerContent(self, flag, id, vipFlags):
        data=self.getpq(id)
        try:
            surl=data('section[style*="padding-top"] iframe').eq(0).attr('src')
            sd=pq(self.fetch(surl,headers=self.headers).text)('body script').html()
            jdata=self.extract_values(sd)
            jdata['key']=self.hhh(jdata['key'])
            parsed_url = urlparse(surl)
            durl = parsed_url.scheme + "://" + parsed_url.netloc
            headers = {
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'cache-control': 'no-cache',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'dnt': '1',
                'origin': durl,
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': f'{surl}',
                'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="130", "Google Chrome";v="130"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-storage-access': 'active',
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest',
            }
            jjb=self.post(f"{durl}/api.php",headers=headers,data=jdata).json()
            url,p=jjb['url'],0
        except Exception as e:
            self.log(f"失败: {e}")
            url,p=f'{self.host}{id}',1
        phd={
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="130", "Google Chrome";v="130"',
            'sec-fetch-dest': 'video',
            'referer': f'{self.host}/',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        return  {'parse': p, 'url': url, 'header': phd}

    def localProxy(self, param):
        pass

    def liveContent(self, url):
        pass

    def gethost(self):
        data=pq(self.fetch("http://shapp.us",headers=self.headers).text)
        for i in data('.content-top ul li').items():
            h=i('a').attr('href')
            if h:
                data = self.fetch(h, headers=self.headers, timeout=5)
                if data.status_code == 200:
                    return h

    def extract_values(self, text):
        url_match = re.search(r'var url = "([^"]+)"', text)
        url = url_match.group(1) if url_match else None
        t_match = re.search(r'var t = "([^"]+)"', text)
        t = t_match.group(1) if t_match else None
        key_match = re.search(r'var key = hhh\("([^"]+)"\)', text)
        key_param = key_match.group(1) if key_match else None
        act_match = re.search(r'var act = "([^"]+)"', text)
        act = act_match.group(1) if act_match else None
        play_match = re.search(r'var play = "([^"]+)"', text)
        play = play_match.group(1) if play_match else None
        return {
            "url": url,
            "t": t,
            "key": key_param,
            "act": act,
            "play": play
        }

    def getlist(self,data):
        videos = []
        for i in data.items():
            videos.append({
                'vod_id': i('a').attr('href'),
                'vod_name': i('a').attr('title'),
                'vod_pic': i('a img').attr('data-original'),
                'vod_remarks': i('.v_note').text()
            })
        return videos

    def getpq(self, path=''):
        data=self.fetch(f"{self.host}{path}",headers=self.headers).text
        try:
            return pq(data)
        except Exception as e:
            print(f"{str(e)}")
            return pq(data.encode('utf-8'))

    def hhh(self, t):
        ee = {
            "0Oo0o0O0": "a", "1O0bO001": "b", "2OoCcO2": "c", "3O0dO0O3": "d",
            "4OoEeO4": "e", "5O0fO0O5": "f", "6OoGgO6": "g", "7O0hO0O7": "h",
            "8OoIiO8": "i", "9O0jO0O9": "j", "0OoKkO0": "k", "1O0lO0O1": "l",
            "2OoMmO2": "m", "3O0nO0O3": "n", "4OoOoO4": "o", "5O0pO0O5": "p",
            "6OoQqO6": "q", "7O0rO0O7": "r", "8OoSsO8": "s", "9O0tO0O9": "t",
            "0OoUuO0": "u", "1O0vO0O1": "v", "2OoWwO2": "w", "3O0xO0O3": "x",
            "4OoYyO4": "y", "5O0zO0O5": "z", "0OoAAO0": "A", "1O0BBO1": "B",
            "2OoCCO2": "C", "3O0DDO3": "D", "4OoEEO4": "E", "5O0FFO5": "F",
            "6OoGGO6": "G", "7O0HHO7": "H", "8OoIIO8": "I", "9O0JJO9": "J",
            "0OoKKO0": "K", "1O0LLO1": "L", "2OoMMO2": "M", "3O0NNO3": "N",
            "4OoOOO4": "O", "5O0PPO5": "P", "6OoQQO6": "Q", "7O0RRO7": "R",
            "8OoSSO8": "S", "9O0TTO9": "T", "0OoUO0": "U", "1O0VVO1": "V",
            "2OoWWO2": "W", "3O0XXO3": "X", "4OoYYO4": "Y", "5O0ZZO5": "Z"
        }
        n = ""
        o = base64.b64decode(t).decode('utf-8', errors='replace')
        i = 0
        while i < len(o):
            l = o[i]
            found = False
            for key, value in ee.items():
                if o[i:i + len(key)] == key:
                    l = value
                    i += len(key) - 1
                    found = True
                    break
            if not found:
                pass
            n += l
            i += 1
        return n
