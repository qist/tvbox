# -*- coding: utf-8 -*-
# by @嗷呜
import time
import uuid
from base64 import b64decode, b64encode
import json
import sys
from urllib.parse import urlparse, urlunparse
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from Crypto.Util.Padding import unpad, pad
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

    host = "https://api.230110.xyz"

    phost = "https://cdn.230110.xyz"

    headers = {
        'origin': host,
        'referer': f'{host}/',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.8 Mobile/15E148 Safari/604.1',
    }

    def homeContent(self, filter):
        data='9XSPkyFMrOOG34JSg//ZosMof45cyBo9hwZMZ5rvI6Yz/ZZlXWIf8/644OzwW+FNIOdJ61R/Lxjy1tqN+ZzokxtiVzb8LjYAkh6GFudwAUXFt9yS1ZjAxC3tDKrQsJQLk3nym0s00DBBzLBntRBDFz7nbba+OOBuQOZpL3CESGL42l4opdoViQLhO/dIizY1kIOk2NxxpDC9Z751gPl1ctHWuLWhuLG/QWgNWi/iHScjKrMHJKcC9GQHst/4Q3dgZ03eQIIVB6jvoV1XXoBCz6fjM/jM3BXpzSttT4Stglwy93gWuNWuZiKypHK2Q0lO10oM0ceRW2a0fPGId+rNYMRO3cR/C0ZueD4cmTAVOuxVr9ZZSP8/nhD0bHyAPONXtchIDJb0O/kdFHk2KTJfQ5q4fHOyzezczc4iQDV/R0S8cGZKM14MF+wytA/iljfj43H0UYqq5pM+MCUGRTdYEtuxCp0+A+DiOhNZwY/Km/TgBoGZQWGbpljJ2LAVnWhxX+ickLH7zuR/FeIwP/R8zOuR+8C8UlT9eHTqtvfNzaGdFxt316atHy8TNjRO7J5a177mqsHs3ziG0toDDzLDCbhRUjFgVA3ktahhXiWaaCo/ZGSJAA8TDO5DYqnJ0JDaX0ILPj8QB5zxrHYmRE8PboIr3RBAjz1sREbaHfjrUjoh29ePhlolLV00EvgoxP5knaqt5Ws/sq5IG57qKCAPgqXzblPLHToJGBtukKhLp8jbGJrkb6PVn4/jysks0NGE'
        return {'class':self.aes(data,False)}

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        data = {"q": "", "filter": [f"type_id = {tid}"], "offset": (int(pg)-1) * 24, "limit": 24, "sort": ["video_time:desc"],"lang": "zh-cn", "route": "/videos/search"}
        result = {}
        if 'skey_' in tid:return self.searchContent(tid.split('_')[-1], True, pg)
        result['list'] = self.getl(self.getdata(data))
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        data={"limit":1,"filter":[f"video_id = {ids[0]}"],"lang":"zh-cn","route":"/videos/search"}
        res = self.getdata(data)[0]
        purl=urlunparse(urlparse(self.phost)._replace(path=urlparse(res.get('video_url')).path))
        vod = {
            'vod_play_from': 'dsysav',
            'vod_play_url': f"{res.get('video_duration')}${purl}"
        }
        if res.get('video_tag'):
            clist = []
            tags=res['video_tag'].split(',')
            for k in tags:
                clist.append('[a=cr:' + json.dumps({'id': f'skey_{k}', 'name': k}) + '/]' + k + '[/a]')
            vod['vod_content'] = ' '.join(clist)
        return {'list':[vod]}

    def searchContent(self, key, quick, pg="1"):
        data={"q":key,"filter":[],"offset":(int(pg)-1) * 24,"limit":24,"sort":["video_time:desc"],"lang":"zh-cn","route":"/videos/search"}
        return {'list':self.getl(self.getdata(data)),'page':pg}

    def playerContent(self, flag, id, vipFlags):
        if id.endswith('.mpd'):
            id=f"{self.getProxyUrl()}&url={self.e64(id)}&type=mpd"
        return  {'parse': 0, 'url': id, 'header':self.headers}

    def localProxy(self, param):
        if param.get('type') and param['type']=='mpd':
            url = self.d64(param.get('url'))
            ids=url.split('/')
            id=f"{ids[-3]}/{ids[-2]}/"
            xpu = f"{self.getProxyUrl()}&path=".replace('&', '&amp;')
            data = self.fetch(url, headers=self.headers).text
            data = data.replace('initialization="', f'initialization="{xpu}{id}').replace('media="',f'media="{xpu}{id}')
            return [200,'application/octet-stream',data]
        else:
            hsign=self.md5(f"AjPuom638LmWfWyeM5YueKuJ9PuWLdRn/mpd/{param.get('path')}1767196800")
            bytes_data = bytes.fromhex(hsign)
            sign = b64encode(bytes_data).decode('utf-8').replace('=','').replace('+','-').replace('/','_')
            url=f"{self.phost}/mpd/{param.get('path')}?sign={sign}&expire=1767196800"
            return [302,'text/plain',None,{'Location':url}]

    def liveContent(self, url):
        pass

    def aes(self, text, operation=True):
        key = b'OPQT123412FRANME'
        iv = b'MRDCQP12QPM13412'
        cipher = AES.new(key, AES.MODE_CBC, iv)
        if operation:
            ct_bytes = cipher.encrypt(pad(json.dumps(text).encode("utf-8"), AES.block_size))
            ct = b64encode(ct_bytes).decode("utf-8")
            return ct
        else:
            pt = unpad(cipher.decrypt(b64decode(text)), AES.block_size)
            return json.loads(pt.decode("utf-8"))

    def e64(self, text):
        try:
            text_bytes = text.encode('utf-8')
            encoded_bytes = b64encode(text_bytes)
            return encoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Base64编码错误: {str(e)}")
            return ""

    def d64(self,encoded_text):
        try:
            encoded_bytes = encoded_text.encode('utf-8')
            decoded_bytes = b64decode(encoded_bytes)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Base64解码错误: {str(e)}")
            return ""

    def md5(self, text):
        h = MD5.new()
        h.update(text.encode('utf-8'))
        return h.hexdigest()

    def getl(self,data):
        videos = []
        for i in data:
            img = i.get('video_cover')
            if img and 'http' in img:img = urlunparse(urlparse(self.phost)._replace(path=urlparse(img).path))
            videos.append({
                'vod_id': i.get('video_id'),
                'vod_name': i.get('video_title'),
                'vod_pic': img,
                'vod_remarks': i.get('video_duration'),
                'style': {"type": "rect", "ratio": 1.33}
            })
        return videos

    def getdata(self,data):
        uid = str(uuid.uuid4())
        t = int(time.time())
        json_data = {
            'sign': self.md5(f"{self.e64(json.dumps(data))}{uid}{t}AjPuom638LmWfWyeM5YueKuJ9PuWLdRn"),
            'nonce': uid,
            'timestamp': t,
            'data': self.aes(data),
        }
        res = self.post(f"{self.host}/v1", json=json_data, headers=self.headers).json()
        res = self.aes(res['data'], False)
        return res
