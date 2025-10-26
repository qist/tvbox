# -*- coding: utf-8 -*-
# by @嗷呜
import json
import random
import string
import sys
import time
from base64 import b64decode
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

    def destroy(self):
        pass

    hs = ['fhoumpjjih', 'dyfcbkggxn', 'rggwiyhqtg', 'bpbbmplfxc']

    def homeContent(self, filter):
        data = self.fetch(f'{self.host}/api/video/queryClassifyList?mark=4', headers=self.headers()).json()['encData']
        data1 = self.aes(data)
        result = {}
        classes = []
        for k in data1['data']:
            classes.append({'type_name': k['classifyTitle'], 'type_id': k['classifyId']})
        result['class'] = classes
        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        path=f'/api/short/video/getShortVideos?classifyId={tid}&videoMark=4&page={pg}&pageSize=20'
        result = {}
        videos = []
        data=self.fetch(f'{self.host}{path}', headers=self.headers()).json()['encData']
        vdata=self.aes(data)
        for k in vdata['data']:
            videos.append({"vod_id": k['videoId'], 'vod_name': k.get('title'), 'vod_pic': self.getProxyUrl() + '&url=' + k['coverImg'],
                           'vod_remarks': self.dtim(k.get('playTime')),'style': {"type": "rect", "ratio": 1.33}})
        result["list"] = videos
        result["page"] = pg
        result["pagecount"] = 9999
        result["limit"] = 90
        result["total"] = 999999
        return result

    def detailContent(self, ids):
        path = f'/api/video/getVideoById?videoId={ids[0]}'
        data = self.fetch(f'{self.host}{path}', headers=self.headers()).json()['encData']
        v = self.aes(data)
        d=f'{v["title"]}$auth_key={v["authKey"]}&path={v["videoUrl"]}'
        vod = {'vod_name': v["title"], 'type_name': ''.join(v.get('tagTitles',[])),'vod_play_from': v.get('nickName') or "小红书官方", 'vod_play_url': d}
        result = {"list": [vod]}
        return result

    def searchContent(self, key, quick, pg='1'):
        pass

    def playerContent(self, flag, id, vipFlags):
        h=self.headers()
        h['Authorization'] = h.pop('aut')
        del h['deviceid']
        result = {"parse": 0, "url": f"{self.host}/api/m3u8/decode/authPath?{id}", "header":  h}
        return result

    def localProxy(self, param):
        return self.action(param)

    def md5(self, text):
        h = MD5.new()
        h.update(text.encode('utf-8'))
        return h.hexdigest()

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
            return ''

    def getdid(self):
        did = self.getCache('did')
        if not did:
            t = str(int(time.time()))
            did = self.md5(t)
            self.setCache('did', did)
        return did

    def getsign(self):
        t=str(int(time.time() * 1000))
        return self.md5(t[3:8]),t
        
    def gettoken(self, i=0, max_attempts=10):
        if i >= len(self.hs) or i >= max_attempts:
            return ''
        current_domain = f"https://{''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 10)))}.{self.hs[i]}.work"
        try:
            sign,t=self.getsign()
            url = f'{current_domain}/api/user/traveler'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 11; M2012K10C Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36;SuiRui/xhs/ver=1.2.6',
                'deviceid': self.did, 't': t, 's': sign, }
            data = {'deviceId': self.did, 'tt': 'U', 'code': '', 'chCode': 'dafe13'}
            data1 = self.post(url, json=data, headers=headers)
            data1.raise_for_status()
            data2 = data1.json()['data']
            return data2['token'], data2['imgDomain'],current_domain
        except:
            return self.gettoken(i+1, max_attempts)

    def headers(self):
        sign,t=self.getsign()
        henda = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 11; M2012K10C Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36;SuiRui/xhs/ver=1.2.6',
            'deviceid': self.did, 't': t, 's': sign, 'aut': self.token}
        return henda

    def action(self, param):
        headers = {
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 11; M2012K10C Build/RP1A.200720.011)'}
        data = self.fetch(f'{self.phost}{param["url"]}', headers=headers)
        type=data.headers.get('Content-Type').split(';')[0]
        base64_data = self.img(data.content, 100, '2020-zq3-888')
        return [200, type, base64_data]

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
