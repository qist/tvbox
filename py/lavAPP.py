# -*- coding: utf-8 -*-
# by @嗷呜
import sys
from base64 import b64encode, b64decode
from Crypto.Hash import MD5, SHA256
sys.path.append('..')
from base.spider import Spider
from Crypto.Cipher import AES
import json
import time


class Spider(Spider):

    def getName(self):
        return "lav"

    def init(self, extend=""):
        self.id = self.ms(str(int(time.time() * 1000)))[:16]
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def action(self, action):
        pass

    def destroy(self):
        pass

    host = "http://sir_new.tiansexyl.tv"
    t = str(int(time.time() * 1000))
    headers = {'User-Agent': 'okhttp-okgo/jeasonlzy', 'Connection': 'Keep-Alive',
               'Content-Type': 'application/x-www-form-urlencoded'}

    def homeContent(self, filter):
        cateManual = {"演员": "actor", "分类": "avsearch", }
        classes = []
        for k in cateManual:
            classes.append({'type_name': k, 'type_id': cateManual[k]})
        j = {'code': 'homePage', 'mod': 'down', 'channel': 'self', 'via': 'agent', 'bundleId': 'com.tvlutv',
             'app_type': 'rn', 'os_version': '12.0.5', 'version': '3.2.3', 'oauth_type': 'android_rn',
             'oauth_id': self.id}

        body = self.aes(j)
        data = self.post(f'{self.host}/api.php?t={str(int(time.time() * 1000))}', data=body, headers=self.headers).json()['data']
        data1 = self.aes(data, False)['data']
        self.r = data1['r']
        for i, d in enumerate(data1['avTag']):
            # if i == 4:
                # break
            classes.append({'type_name': d['name'], 'type_id': d['tag']})
        resutl = {}
        resutl["class"] = classes
        return resutl

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        id = tid.split("@@")
        result = {}
        result["page"] = pg
        result["pagecount"] = 9999
        result["limit"] = 90
        result["total"] = 999999
        if id[0] == 'avsearch':
            if pg == '1':
                j = {'code': 'avsearch', 'mod': 'search', 'channel': 'self', 'via': 'agent', 'bundleId': 'com.tvlutv',
                     'app_type': 'rn', 'os_version': '12.0.5', 'version': '3.2.3', 'oauth_type': 'android_rn',
                     'oauth_id': self.id}
            if len(id) > 1:
                j = {'code': 'find', 'mod': 'tag', 'channel': 'self', 'via': 'agent', 'bundleId': 'com.tvlutv',
                     'app_type': 'rn', 'os_version': '12.0.5', 'version': '3.2.3', 'oauth_type': 'android_rn',
                     'oauth_id': self.id, 'type': 'av', 'dis': 'new', 'page': str(pg), 'tag': id[1]}
        elif id[0] == 'actor':
            j = {'mod': 'actor', 'channel': 'self', 'via': 'agent', 'bundleId': 'com.tvlutv', 'app_type': 'rn',
                 'os_version': '12.0.5', 'version': '3.2.3', 'oauth_type': 'android_rn', 'oauth_id': self.id,
                 'page': str(pg), 'filter': ''}
            if len(id) > 1:
                j = {'code': 'eq', 'mod': 'actor', 'channel': 'self', 'via': 'agent', 'bundleId': 'com.tvlutv',
                     'app_type': 'rn', 'os_version': '12.0.5', 'version': '3.2.3', 'oauth_type': 'android_rn',
                     'oauth_id': self.id, 'page': str(pg), 'id': id[1], 'actor': id[2]}
        else:
            j = {'code': 'search', 'mod': 'av', 'channel': 'self', 'via': 'agent', 'bundleId': 'com.tvlutv',
                 'app_type': 'rn', 'os_version': '12.0.5', 'version': '3.2.3', 'oauth_type': 'android_rn',
                 'oauth_id': self.id, 'page': str(pg), 'tag': id[0]}

        body = self.aes(j)
        data = self.post(f'{self.host}/api.php?t={str(int(time.time() * 1000))}', data=body, headers=self.headers).json()['data']
        data1 = self.aes(data, False)['data']
        videos = []
        if tid == 'avsearch' and len(id) == 1:
            for item in data1:
                videos.append({"vod_id": id[0] + "@@" + str(item.get('tags')), 'vod_name': item.get('name'),
                               'vod_pic': self.imgs(item.get('ico')), 'vod_tag': 'folder',
                               'style': {"type": "rect", "ratio": 1.33}})
        elif tid == 'actor' and len(id) == 1:
            for item in data1:
                videos.append({"vod_id": id[0] + "@@" + str(item.get('id')) + "@@" + item.get('name'),
                               'vod_name': item.get('name'), 'vod_pic': self.imgs(item.get('cover')),
                               'vod_tag': 'folder', 'style': {"type": "oval"}})
        else:
            for item in data1:
                if item.get('_id'):
                    videos.append({"vod_id": str(item.get('id')), 'vod_name': item.get('title'),
                                   'vod_pic': self.imgs(item.get('cover_thumb') or item.get('cover_full')),
                                   'vod_remarks': item.get('good'), 'style': {"type": "rect", "ratio": 1.33}})
        result["list"] = videos
        return result

    def detailContent(self, ids):
        id = ids[0]
        j = {'code': 'detail', 'mod': 'av', 'channel': 'self', 'via': 'agent', 'bundleId': 'com.tvlutv',
             'app_type': 'rn', 'os_version': '12.0.5', 'version': '3.2.3', 'oauth_type': 'android_rn',
             'oauth_id': self.id, 'id': id}
        body = self.aes(j)
        data = self.post(f'{self.host}/api.php?t={str(int(time.time() * 1000))}', data=body, headers=self.headers).json()['data']
        data1 = self.aes(data, False)['line']
        vod = {}
        play = []
        for itt in data1:
            a = itt['line'].get('s720')
            if a:
                b = a.split('.')
                b[0] = 'https://m3u8'
                a = '.'.join(b)
                play.append(itt['info']['tips'] + "$" + a)
                break
        vod["vod_play_from"] = 'LAV'
        vod["vod_play_url"] = "#".join(play)
        result = {"list": [vod]}
        return result

    def searchContent(self, key, quick, pg="1"):
        pass

    def playerContent(self, flag, id, vipFlags):
        url = self.getProxyUrl() + "&url=" + b64encode(id.encode('utf-8')).decode('utf-8') + "&type=m3u8"
        self.hh = {'User-Agent': 'dd', 'Connection': 'Keep-Alive', 'Referer': self.r}
        result = {}
        result["parse"] = 0
        result["url"] = url
        result["header"] = self.hh
        return result

    def localProxy(self, param):
        url = param["url"]
        if param.get('type') == "m3u8":
            return self.vod(b64decode(url).decode('utf-8'))
        else:
            return self.img(url)

    def vod(self, url):
        data = self.fetch(url, headers=self.hh).text
        key = bytes.fromhex("13d47399bda541b85e55830528d4e66f1791585b2d2216f23215c4c63ebace31")
        iv = bytes.fromhex(data[:32])
        data = data[32:]
        cipher = AES.new(key, AES.MODE_CFB, iv, segment_size=128)
        data_bytes = bytes.fromhex(data)
        decrypted = cipher.decrypt(data_bytes)
        encoded = decrypted.decode("utf-8").replace("\x08", "")
        return [200, "application/vnd.apple.mpegur", encoded]

    def imgs(self, url):
        return self.getProxyUrl() + '&url=' + url

    def img(self, url):
        type = url.split('.')[-1]
        data = self.fetch(url).text
        key = bytes.fromhex("ba78f184208d775e1553550f2037f4af22cdcf1d263a65b4d5c74536f084a4b2")
        iv = bytes.fromhex(data[:32])
        data = data[32:]
        cipher = AES.new(key, AES.MODE_CFB, iv, segment_size=128)
        data_bytes = bytes.fromhex(data)
        decrypted = cipher.decrypt(data_bytes)
        return [200, f"image/{type}", decrypted]

    def ms(self, data, m=False):
        h = MD5.new()
        if m:
            h = SHA256.new()
        h.update(data.encode('utf-8'))
        return h.hexdigest()

    def aes(self, data, operation=True):
        key = bytes.fromhex("620f15cfdb5c79c34b3940537b21eda072e22f5d7151456dec3932d7a2b22c53")
        t = str(int(time.time()))
        ivt = self.ms(t)
        if operation:
            data = json.dumps(data, separators=(',', ':'))
            iv = bytes.fromhex(ivt)
        else:
            iv = bytes.fromhex(data[:32])
            data = data[32:]
        cipher = AES.new(key, AES.MODE_CFB, iv, segment_size=128)
        if operation:
            data_bytes = data.encode('utf-8')
            encrypted = cipher.encrypt(data_bytes)
            ep = f'{ivt}{encrypted.hex()}'
            edata = f"data={ep}&timestamp={t}0d27dfacef1338483561a46b246bf36d"
            sign = self.ms(self.ms(edata, True))
            edata = f"timestamp={t}&data={ep}&sign={sign}"
            return edata
        else:
            data_bytes = bytes.fromhex(data)
            decrypted = cipher.decrypt(data_bytes)
            return json.loads(decrypted.decode('utf-8'))

