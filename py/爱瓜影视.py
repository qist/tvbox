# -*- coding: utf-8 -*-
# by @嗷呜
# 温馨提示：搜索只能搜拼音联想
# 播放需要挂代理
import sys
import time
import uuid
from Crypto.Hash import MD5
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):

    def init(self, extend=""):
        self.uid = self.getuid()
        self.token, self.code = self.getuserinfo()
        pass

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    host = 'https://tvapi211.magicetech.com'

    headers = {'User-Agent': 'okhttp/3.11.0'}

    def homeContent(self, filter):
        body = {'token': self.token, 'authcode': self.code}
        data = self.post(f'{self.host}/hr_1_1_0/apptvapi/web/index.php/video/filter-header', json=self.getbody(body),
                         headers=self.headers).json()
        result = {}
        classes = []
        filters = {}
        for k in data['data']:
            classes.append({
                'type_name': k['channel_name'],
                'type_id': str(k['channel_id']),
            })
            filters[str(k['channel_id'])] = []
            for i in k['search_box']:
                if len(i['list']):
                    filters[str(k['channel_id'])].append({
                        'key': i['field'],
                        'name': i['label'],
                        'value': [{'n': j['display'], 'v': str(j['value'])} for j in i['list'] if j['value']]
                    })
        result['class'] = classes
        result['filters'] = filters
        return result

    def homeVideoContent(self):
        body = {'token': self.token, 'authcode': self.code}
        data = self.post(f'{self.host}/hr_1_1_0/apptvapi/web/index.php/video/index-tv', json=self.getbody(body),
                         headers=self.headers).json()
        return {'list': self.getlist(data['data'][0]['banner'])}

    def categoryContent(self, tid, pg, filter, extend):
        body = {'token': self.token, 'authcode': self.code, 'channel_id': tid, 'area': extend.get('area', '0'),
                'year': extend.get('year', '0'), 'sort': extend.get('sort', '0'), 'tag': extend.get('tag', 'hot'),
                'status': extend.get('status', '0'), 'page_num': pg, 'page_size': '24'}
        data = self.post(f'{self.host}/hr_1_1_0/apptvapi/web/index.php/video/filter-video', json=self.getbody(body),
                         headers=self.headers).json()
        result = {}
        result['list'] = self.getlist(data['data']['list'])
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        ids = ids[0].split('@')
        body = {'token': self.token, 'authcode': self.code, 'channel_id': ids[0], 'video_id': ids[1]}
        data = self.post(f'{self.host}/hr_1_1_0/apptvapi/web/index.php/video/detail', json=self.getbody(body),
                         headers=self.headers).json()
        vdata = {}
        for k in data['data']['chapters']:
            i = k['sourcelist']
            for j in i:
                if j['source_name'] not in vdata: vdata[j['source_name']] = []
                vdata[j['source_name']].append(f"{k['title']}${j['source_url']}")
        plist, names = [], []
        for key, value in vdata.items():
            names.append(key)
            plist.append('#'.join(value))
        vod = {
            'vod_play_from': '$$$'.join(names),
            'vod_play_url': '$$$'.join(plist),
        }
        return {'list': [vod]}

    def searchContent(self, key, quick, pg="1"):
        body = {'token': self.token, 'authcode': self.code, 'keyword': key, 'page_num': pg}
        data = self.post(f'{self.host}/hr_1_1_0/apptvapi/web/index.php/search/letter-result', json=self.getbody(body),
                         headers=self.headers).json()
        return {'list': self.getlist(data['data']['list'])}

    def playerContent(self, flag, id, vipFlags):
        # https://rysp.tv
        # https://aigua.tv
        result = {
            "parse": 0,
            "url": id,
            "header": {
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; M2012K10C Build/RP1A.200720.011)",
                "Origin": "https://aigua.tv",
                "Referer": "https://aigua.tv/"
            }
        }
        return result

    def localProxy(self, param):
        pass

    def getuserinfo(self):
        data = self.post(f'{self.host}/hr_1_1_0/apptvapi/web/index.php/user/auth-login', json=self.getbody(),
                         headers=self.headers).json()
        v = data['data']
        return v['user_token'], v['authcode']

    def getuid(self):
        uid = self.getCache('uid')
        if not uid:
            uid = str(uuid.uuid4())
            self.setCache('uid', uid)
        return uid

    def getbody(self, json_data=None):
        if json_data is None: json_data = {}
        params = {"product": "4", "ver": "1.1.0", "debug": "1", "appId": "1", "osType": "3", "marketChannel": "tv",
                  "sysVer": "11", "time": str(int(time.time())), "packageName": "com.gzsptv.gztvvideo",
                  "udid": self.uid, }
        json_data.update(params)
        sorted_json = dict(sorted(json_data.items(), key=lambda item: item[0]))
        text = '&'.join(f"{k}={v}" for k, v in sorted_json.items() if v != '')
        md5_hash = self.md5(f"jI7POOBbmiUZ0lmi{text}D9ShYdN51ksWptpkTu11yenAJu7Zu3cR").upper()
        json_data.update({'sign': md5_hash})
        return json_data

    def md5(self, text):
        h = MD5.new()
        h.update(text.encode('utf-8'))
        return h.hexdigest()

    def getlist(self, data):
        videos = []
        for i in data:
            if type(i.get('video')) == dict: i = i['video']
            videos.append({
                'vod_id': f"{i.get('channel_id')}@{i.get('video_id')}",
                'vod_name': i.get('video_name'),
                'vod_pic': i.get('cover'),
                'vod_year': i.get('score'),
                'vod_remarks': i.get('flag'),
            })
        return videos

