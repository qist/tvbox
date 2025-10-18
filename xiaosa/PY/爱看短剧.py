# -*- coding: utf-8 -*-
# by @嗷呜
import base64
import binascii
import json
import random
import sys
import time
import uuid
from base64 import b64decode, b64encode
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from Crypto.Util.Padding import unpad, pad
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):

    def init(self, extend=""):
        self.ut = False
        # self.did, self.ntid =self.getdid()
        self.did, self.ntid = 'e59eb2465f61b9ca','65a0de19b3a2ec93fa479ad6'
        self.token, self.uid = self.gettoken()
        self.phost, self.phz,self.mphost=self.getpic()
        # self.phost, self.phz,self.mphost = ('https://dbtp.tgydy.com','.log','https://dplay.nbzsmc.com')
        pass

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    host='http://192.151.245.34:8089'

    def md5(self, text):
        h = MD5.new()
        h.update(text.encode('utf-8'))
        return h.hexdigest()

    def uuid(self):
        return str(uuid.uuid4())

    def getdid(self):
        did = self.random_str(16)
        ntid = self.random_str(24)
        return did, ntid
        # try:
        #     if self.getCache('did'):
        #         return self.getCache('did'), self.getCache('ntid')
        #     else:
        #         self.setCache('did', did)
        #         self.setCache('ntid', ntid)
        #         return did, ntid
        # except Exception as e:
        #     self.setCache('did', did)
        #     self.setCache('ntid', ntid)
        #     return did, ntid

    def aes(self, text, bool=True):
        key = b64decode('c0k4N1RfKTY1U1cjJERFRA==')
        iv = b64decode('VzIjQWRDVkdZSGFzSEdEVA==')
        if bool:
            cipher = AES.new(key, AES.MODE_CBC, iv)
            ct_bytes = cipher.encrypt(pad(text.encode("utf-8"), AES.block_size))
            ct = b64encode(ct_bytes).decode("utf-8")
            return ct
        else:
            cipher = AES.new(key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(b64decode(text)), AES.block_size)
            ptt=json.loads(pt.decode("utf-8"))
            return ptt

    def random_str(self,length=24):
        hex_chars = '0123456789abcdef'
        return ''.join(random.choice(hex_chars) for _ in range(length))

    def gettoken(self):
        params={"deviceId":self.did,"deviceModel":"8848钛晶手机","devicePlatform":"1","tenantId":self.ntid}
        data=self.getdata('/supports/anonyLogin',params)
        self.ut=True
        return data['data']['token'], data['data']['userId']

    def getdata(self,path,params=None):
        t = int(time.time()*1000)
        n=self.md5(f'{self.uuid()}{t}')
        if params:
            ct=self.aes(json.dumps(params))
        else:
            ct=f'{t}{n}'
        s=self.md5(f'{ct}8j@78m.367HGDF')
        headers = {
            'User-Agent': 'okhttp-okgo/jeasonlzy',
            'Connection': 'Keep-Alive',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'tenantId': self.ntid,
            'n': n,
            't': str(int(t/1000)),
            's': s,
        }
        if self.ut:
            headers['ta-token'] = self.token
            headers['userId'] = self.uid
        if params:
            params={'ct':ct}
            response = self.post(f'{self.host}{path}', headers=headers, json=params).text
        else:
            response = self.fetch(f'{self.host}{path}', headers=headers).text
        data=self.aes(response[1:-1],False)
        return data

    def getpic(self):
        try:
            at = int(time.time() * 1000)
            t=str(int(at/ 1000))
            n = self.md5(f'{self.uuid()}{at}')
            headers = {
                'Host': '192.151.245.34:8089',
                'User-Agent': 'okhttp-okgo/jeasonlzy',
                'Connection': 'Keep-Alive',
                'Accept-Language': 'zh-CN,zh;q=0.8',
                'tenantId': self.ntid,
                'userId': self.uid,
                'ta-token': self.token,
                'n': n,
                't': t,
                's': self.md5(f'{t}{n}8j@78m.367HGDF')
            }
            params = {
                'tenantId': self.ntid,
            }
            response = self.fetch(f'{self.host}/supports/configs', params=params, headers=headers).text
            data=self.aes(response[1:-1],False)
            config = {
                'image_cdn': '',
                'image_cdn_path': '',
                'cdn-domain': ''
            }
            for item in data.get('data', []):
                name = item.get('name')
                records = item.get('records', [])

                if name in config and records:
                    value = records[0].get('value', '')
                    if name == 'cdn-domain':
                        value = value.split('#')[0]
                    config[name] = value

            return config['image_cdn'], config['image_cdn_path'], config['cdn-domain']

        except Exception as e:
            print(f"Error in getpic: {e}")
            return 'https://dbtp.tgydy.com', '.log', 'https://dplay.nbzsmc.com'

    def getlist(self,data):
        vod=[]
        for i in data:
            vod.append({
                'vod_id': f'{i.get("movieId")}@{i.get("entryNum")}',
                'vod_name': i.get('title'),
                'vod_pic': f'{self.getProxyUrl()}&path={i.get("thumbnail")}',
                'vod_year': i.get('score'),
                'vod_remarks': f'{i.get("entryNum")}集'
            })
        return vod

    def homeContent(self, filter):
        data=self.getdata('/movies/classifies')
        result = {}
        cateManual = {
            "榜单": "ranking/getTodayHotRank",
            "专辑": "getTMovieFolderPage",
            "剧场": "getClassMoviePage2",
            "演员": "follow/getRecommendActorPage",
        }
        classes = []
        for k in cateManual:
            classes.append({
                'type_name': k,
                'type_id': cateManual[k]
            })
        filters = {}
        if data.get('data'):
            filters["getClassMoviePage2"] = [
                {
                    "key": "type",
                    "name": "分类",
                    "value": [
                        {"n": item["name"], "v": item["classifyId"]}
                        for item in data["data"]
                    ]
                }
            ]
        filters["ranking/getTodayHotRank"] = [
            {
                "key": "type",
                "name": "榜单",
                "value": [
                    {"n": "播放榜", "v": "getWeekHotPlayRank"},
                    {"n": "高赞榜", "v": "getWeekStarRank"},
                    {"n": "追剧榜", "v": "getSubTMoviePage"},
                    {"n": "高分榜", "v": "ranking/getScoreRank"}
                ]
            }
        ]
        filters["follow/getRecommendActorPage"] = [
            {
                "key": "type",
                "name": "性别",
                "value": [
                    {"n": "男", "v": "0"},
                    {"n": "女", "v": "1"}
                ]
            }
        ]
        result['class'] = classes
        result['filters'] = filters
        return result

    def homeVideoContent(self):
        params = {"pageNo":"1","pageSize":"30","platform":"1","deviceId":self.did,"tenantId":self.ntid}
        data=self.getdata('/news/getRecommendTMoviePage',params)
        vod=self.getlist(data['data']['records'])
        return {'list':vod}

    def categoryContent(self, tid, pg, filter, extend):
        params={}
        path = f'/news/{tid}'
        if tid=='getClassMoviePage2':
            parama={"pageNo":pg,"pageSize":"30","orderFlag":"0","haveActor":"-1","classifyId":extend.get('type','-1'),"tagId":""}
        elif 'rank' in tid:
            path=f'/news/{extend.get("type") or tid}'
            parama={"pageNo":pg,"pageSize":"30"}
        elif 'follow' in tid:
            parama={"pageNo":pg,"pageSize":"20"}
            if extend.get('type'):
                path=f'/news/getActorPage'
                parama={"pageNo":pg,"pageSize":"50","sex":extend.get('type')}
        elif tid=='getTMovieFolderPage':
            parama={"pageNo":pg,"pageSize":"20"}
        elif '@' in tid:
            path='/news/getActorTMoviePage'
            parama={"id":tid.split('@')[0],"pageNo":pg,"pageSize":"30"}
        params['platform'] = '1'
        params['deviceId'] = self.did
        params['tenantId'] = self.ntid
        data=self.getdata(path,parama)
        vods=[]
        if 'follow' in tid:
            for i in data['data']['records']:
                vods.append({
                    'vod_id': f'{i.get("id")}@',
                    'vod_name': i.get('name'),
                    'vod_pic': i.get('avatar'),
                    'vod_tag': 'folder',
                    'vod_remarks': f'作品{i.get("movieNum")}',
                    'style': {"type": "oval"}
                })
        else:
            vdata=data['data']['records']
            if tid=='getTMovieFolderPage':
                vdata=[j for i in data['data']['records'] for j in i['movieList']]
            vods=self.getlist(vdata)
        result = {}
        result['list'] = vods
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        ids=ids[0].split('@')
        params = {"pageNo": "1", "pageSize": ids[1], "movieId": ids[0], "platform": "1", "deviceId": self.did, "tenantId": self.ntid}
        data = self.getdata('/news/getEntryPage', params)
        print(data)
        plist=[f'第{i.get("entryNum")}集${i.get("mp4PlayAddress") or i.get("playAddress")}' for i in data['data']['records']]
        vod = {
            'vod_play_from': '爱看短剧',
            'vod_play_url': '#'.join(plist),
        }
        return {'list':[vod]}

    def searchContent(self, key, quick, pg="1"):
        params = {"pageNo": pg, "pageSize": "20", "keyWord": key, "orderFlag": "0", "platform": "1", "deviceId": self.did, "tenantId": self.ntid}
        data = self.getdata('/news/searchTMoviePage', params)
        vod = self.getlist(data['data']['records'])
        return {'list':vod,'page':pg}

    def playerContent(self, flag, id, vipFlags):
        return  {'parse': 0, 'url': f'{self.mphost}{id}', 'header': {'User-Agent':'Dalvik/2.1.0 (Linux; U; Android 11; M2012K10C Build/RP1A.200720.011)'}}

    def localProxy(self, param):
        type=param.get('path').split('.')[-1]
        data=self.fetch(f'{self.phost}{param.get("path")}{self.phz}',headers={'User-Agent':'Dalvik/2.1.0 (Linux; U; Android 11; M2012K10C Build/RP1A.200720.011)'})
        def decrypt(encrypted_text):
            try:
                key = base64.urlsafe_b64decode("iM41VipvCFtToAFFRExEXw==")
                iv = base64.urlsafe_b64decode("0AXRTXzmMSrlRSemWb4sVQ==")
                cipher = AES.new(key, AES.MODE_CBC, iv)
                decrypted_padded = cipher.decrypt(encrypted_text)
                decrypted_data = unpad(decrypted_padded, AES.block_size)
                return decrypted_data
            except (binascii.Error, ValueError):
                return None
        return [200, f'image/{type}', decrypt(data.content)]

