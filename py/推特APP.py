# -*- coding: utf-8 -*-
# by @嗷呜
import json
import random
import string
import sys
import time
from base64 import b64decode
from urllib.parse import quote
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from Crypto.Util.Padding import unpad
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):

    def init(self, extend=""):
        self.did = self.getdid()
        self.token,self.phost,self.host = self.gettoken()
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def action(self, action):
        pass

    def destroy(self):
        pass

    hs=['wcyfhknomg','pdcqllfomw','alxhzjvean','bqeaaxzplt','hfbtpixjso']

    ua='Mozilla/5.0 (Linux; Android 11; M2012K10C Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36;SuiRui/twitter/ver=1.4.4'

    def homeContent(self, filter):
        data = self.fetch(f'{self.host}/api/video/classifyList', headers=self.headers()).json()['encData']
        data1 = self.aes(data)
        result = {'filters': {"1": [{"key": "fl", "name": "分类",
                                     "value": [{"n": "最近更新", "v": "1"}, {"n": "最多播放", "v": "2"},
                                               {"n": "好评榜", "v": "3"}]}], "2": [{"key": "fl", "name": "分类",
                                                                                    "value": [
                                                                                        {"n": "最近更新", "v": "1"},
                                                                                        {"n": "最多播放", "v": "2"},
                                                                                        {"n": "好评榜", "v": "3"}]}],
                              "3": [{"key": "fl", "name": "分类",
                                     "value": [{"n": "最近更新", "v": "1"}, {"n": "最多播放", "v": "2"},
                                               {"n": "好评榜", "v": "3"}]}], "4": [{"key": "fl", "name": "分类",
                                                                                    "value": [
                                                                                        {"n": "最近更新", "v": "1"},
                                                                                        {"n": "最多播放", "v": "2"},
                                                                                        {"n": "好评榜", "v": "3"}]}],
                              "5": [{"key": "fl", "name": "分类",
                                     "value": [{"n": "最近更新", "v": "1"}, {"n": "最多播放", "v": "2"},
                                               {"n": "好评榜", "v": "3"}]}], "6": [{"key": "fl", "name": "分类",
                                                                                    "value": [
                                                                                        {"n": "最近更新", "v": "1"},
                                                                                        {"n": "最多播放", "v": "2"},
                                                                                        {"n": "好评榜", "v": "3"}]}],
                              "7": [{"key": "fl", "name": "分类",
                                     "value": [{"n": "最近更新", "v": "1"}, {"n": "最多播放", "v": "2"},
                                               {"n": "好评榜", "v": "3"}]}], "jx": [{"key": "type", "name": "精选",
                                                                                     "value": [{"n": "日榜", "v": "1"},
                                                                                               {"n": "周榜", "v": "2"},
                                                                                               {"n": "月榜", "v": "3"},
                                                                                               {"n": "总榜",
                                                                                                "v": "4"}]}]}}
        classes = [{'type_name': "精选", 'type_id': "jx"}]
        for k in data1['data']:
            classes.append({'type_name': k['classifyTitle'], 'type_id': k['classifyId']})
        result['class'] = classes
        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        path = f'/api/video/queryVideoByClassifyId?pageSize=20&page={pg}&classifyId={tid}&sortType={extend.get("fl", "1")}'
        if 'click' in tid:
            path = f'/api/video/queryPersonVideoByType?pageSize=20&page={pg}&userId={tid.replace("click", "")}'
        if tid == 'jx':
            path = f'/api/video/getRankVideos?pageSize=20&page={pg}&type={extend.get("type", "1")}'
        data = self.fetch(f'{self.host}{path}', headers=self.headers()).json()['encData']
        data1 = self.aes(data)['data']
        result = {}
        videos = []
        for k in data1:
            id = f'{k.get("videoId")}?{k.get("userId")}?{k.get("nickName")}'
            if 'click' in tid:
                id = id + 'click'
            videos.append({"vod_id": id, 'vod_name': k.get('title'), 'vod_pic': self.getProxyUrl() + f"&url={k.get('coverImg')[0]}",
                           'vod_remarks': self.dtim(k.get('playTime')),'style': {"type": "rect", "ratio": 1.33}})
        result["list"] = videos
        result["page"] = pg
        result["pagecount"] = 9999
        result["limit"] = 90
        result["total"] = 999999
        return result

    def detailContent(self, ids):
        vid = ids[0].replace('click', '').split('?')
        path = f'/api/video/can/watch?videoId={vid[0]}'
        data = self.fetch(f'{self.host}{path}', headers=self.headers()).json()['encData']
        data1 = self.aes(data)['playPath']
        clj = '[a=cr:' + json.dumps({'id': vid[1] + 'click', 'name': vid[2]}) + '/]' + vid[2] + '[/a]'
        if 'click' in ids[0]:
            clj = vid[2]
        vod = {'vod_director': clj, 'vod_play_from': "推特", 'vod_play_url': vid[2] + "$" + data1}
        result = {"list": [vod]}
        return result

    def searchContent(self, key, quick, pg='1'):
        path = f'/api/search/keyWord?pageSize=20&page={pg}&searchWord={quote(key)}&searchType=1'
        data = self.fetch(f'{self.host}{path}', headers=self.headers()).json()['encData']
        data1 = self.aes(data)['videoList']
        result = {}
        videos = []
        for k in data1:
            id = f'{k.get("videoId")}?{k.get("userId")}?{k.get("nickName")}'
            videos.append({"vod_id": id, 'vod_name': k.get('title'), 'vod_pic': self.getProxyUrl() + f"&url={k.get('coverImg')[0]}",
                           'vod_remarks': self.dtim(k.get('playTime')), 'style': {"type": "rect", "ratio": 1.33}})
        result["list"] = videos
        result["page"] = pg
        result["pagecount"] = 9999
        result["limit"] = 90
        result["total"] = 999999
        return result

    def playerContent(self, flag, id, vipFlags):
        return {"parse": 0, "url": id, "header": self.headers()}

    def localProxy(self, param):
        return self.imgs(param)

    def getsign(self):
        t = str(int(time.time() * 1000))
        sign = self.md5(t)
        return sign, t

    def headers(self):
        sign, t = self.getsign()
        return {'User-Agent': self.ua,'deviceid': self.did, 't': t, 's': sign, 'aut': self.token}

    def aes(self, word):
        key = b64decode("SmhiR2NpT2lKSVV6STFOaQ==")
        iv = key
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(b64decode(word)), AES.block_size)
        return json.loads(decrypted.decode('utf-8'))

    def dtim(self, seconds):
        try:
            seconds = int(seconds)
            hours = seconds // 3600
            remaining_seconds = seconds % 3600
            minutes = remaining_seconds // 60
            remaining_seconds = remaining_seconds % 60

            formatted_minutes = str(minutes).zfill(2)
            formatted_seconds = str(remaining_seconds).zfill(2)

            if hours > 0:
                formatted_hours = str(hours).zfill(2)
                return f"{formatted_hours}:{formatted_minutes}:{formatted_seconds}"
            else:
                return f"{formatted_minutes}:{formatted_seconds}"
        except:
            return "666"

    def gettoken(self, i=0, max_attempts=10):
        if i >= len(self.hs) or i >= max_attempts:
            return ''
        current_domain = f"https://{''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 10)))}.{self.hs[i]}.work"
        try:
            url = f'{current_domain}/api/user/traveler'
            sign, t = self.getsign()
            headers = {
                'User-Agent': self.ua,
                'Accept': 'application/json',
                'deviceid': self.did,
                't': t,
                's': sign,
            }
            data = {
                'deviceId': self.did,
                'tt': 'U',
                'code': '##X-4m6Goo4zzPi1hF##',
                'chCode': 'tt09'
            }
            response = self.post(url, json=data, headers=headers)
            response.raise_for_status()
            data1 = response.json()['data']
            return data1['token'], data1['imgDomain'], current_domain
        except Exception as e:
            return self.gettoken(i + 1, max_attempts)

    def getdid(self):
        did = self.getCache('did')
        if not did:
            t = str(int(time.time()))
            did = self.md5(t)
            self.setCache('did', did)
        return did

    def md5(self, text):
        h = MD5.new()
        h.update(text.encode('utf-8'))
        return h.hexdigest()

    def imgs(self, param):
        headers = {'User-Agent': self.ua}
        url = param['url']
        data = self.fetch(f"{self.phost}{url}",headers=headers)
        bdata = self.img(data.content, 100, '2020-zq3-888')
        return [200, data.headers.get('Content-Type'), bdata]

    def img(self, data: bytes, length: int, key: str):
        GIF = b'\x47\x49\x46'
        JPG = b'\xFF\xD8\xFF'
        PNG = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'

        def is_dont_need_decode_for_gif(data):
            return len(data) > 2 and data[:3] == GIF

        def is_dont_need_decode_for_jpg(data):
            return len(data) > 7 and data[:3] == JPG

        def is_dont_need_decode_for_png(data):
            return len(data) > 7 and data[1:8] == PNG[1:8]

        if is_dont_need_decode_for_png(data):
            return data
        elif is_dont_need_decode_for_gif(data):
            return data
        elif is_dont_need_decode_for_jpg(data):
            return data
        else:
            key_bytes = key.encode('utf-8')
            result = bytearray(data)
            for i in range(length):
                result[i] ^= key_bytes[i % len(key_bytes)]
            return bytes(result)
