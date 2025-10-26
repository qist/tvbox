# -*- coding: utf-8 -*-
# by @嗷呜
import json
import random
import sys
from base64 import b64encode, b64decode
from concurrent.futures import ThreadPoolExecutor
sys.path.append('..')
from base.spider import Spider

class Spider(Spider):

    def init(self, extend=""):
        did=self.getdid()
        self.headers.update({'deviceId': did})
        token=self.gettk()
        self.headers.update({'token': token})
        pass

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    host='http://ldys.sq1005.top'

    headers = {
        'User-Agent': 'okhttp/4.12.0',
        'client': 'app',
        'deviceType': 'Android'
    }

    def homeContent(self, filter):
        data=self.post(f"{self.host}/api/v1/app/screen/screenType", headers=self.headers).json()
        result = {}
        cate = {
            "类型": "classify",
            "地区": "region",
            "年份": "year"
        }
        sort={
            'key':'sreecnTypeEnum',
            'name': '排序',
            'value':[{'n':'最新','v':'NEWEST'},{'n':'人气','v':'POPULARITY'},{'n':'评分','v':'COLLECT'},{'n':'热搜','v':'HOT'}]
        }
        classes = []
        filters = {}
        for k in data['data']:
            classes.append({
                'type_name': k['name'],
                'type_id': k['id']
            })
            filters[k['id']] = []
            for v in k['children']:
                filters[k['id']].append({
                    'name': v['name'],
                    'key': cate[v['name']],
                    'value':[{'n':i['name'],'v':i['name']} for i in v['children']]
                })
            filters[k['id']].append(sort)
        result['class'] = classes
        result['filters'] = filters
        return result

    def homeVideoContent(self):
        jdata={"condition":64,"pageNum":1,"pageSize":40}
        data=self.post(f"{self.host}/api/v1/app/recommend/recommendSubList", headers=self.headers, json=jdata).json()
        return {'list':self.getlist(data['data']['records'])}

    def categoryContent(self, tid, pg, filter, extend):
        jdata = {
            'condition': {
                'sreecnTypeEnum': 'NEWEST',
                'typeId': tid,
            },
            'pageNum': int(pg),
            'pageSize': 40,
        }
        jdata['condition'].update(extend)
        data = self.post(f"{self.host}/api/v1/app/screen/screenMovie", headers=self.headers, json=jdata).json()
        result = {}
        result['list'] = self.getlist(data['data']['records'])
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        ids = ids[0].split('@@')
        jdata = {"id": int(ids[0]), "typeId": ids[-1]}
        v = self.post(f"{self.host}/api/v1/app/play/movieDesc", headers=self.headers, json=jdata).json()
        v = v['data']
        vod = {
            'type_name': v.get('classify'),
            'vod_year': v.get('year'),
            'vod_area': v.get('area'),
            'vod_actor': v.get('star'),
            'vod_director': v.get('director'),
            'vod_content': v.get('introduce'),
            'vod_play_from': '',
            'vod_play_url': ''
        }
        c = self.post(f"{self.host}/api/v1/app/play/movieDetails", headers=self.headers, json=jdata).json()
        l = c['data']['moviePlayerList']
        n = {str(i['id']): i['moviePlayerName'] for i in l}
        m = jdata.copy()
        m.update({'playerId': str(l[0]['id'])})
        pd = self.getv(m, c['data']['episodeList'])
        if len(l)-1:
            with ThreadPoolExecutor(max_workers=len(l)-1) as executor:
                future_to_player = {executor.submit(self.getd, jdata, player): player for player in l[1:]}
                for future in future_to_player:
                    try:
                        o,p = future.result()
                        pd.update(self.getv(o,p))
                    except Exception as e:
                        print(f"请求失败: {e}")
        w, e = [],[]
        for i, x in pd.items():
            if x:
                w.append(n[i])
                e.append(x)
        vod['vod_play_from'] = '$$$'.join(w)
        vod['vod_play_url'] = '$$$'.join(e)
        return {'list': [vod]}

    def searchContent(self, key, quick, pg="1"):
        jdata={
          "condition": {
            "value": key
          },
          "pageNum": int(pg),
          "pageSize": 40
        }
        data=self.post(f"{self.host}/api/v1/app/search/searchMovie", headers=self.headers, json=jdata).json()
        return {'list':self.getlist(data['data']['records']),'page':pg}

    def playerContent(self, flag, id, vipFlags):
        jdata=json.loads(self.d64(id))
        data = self.post(f"{self.host}/api/v1/app/play/movieDetails", headers=self.headers, json=jdata).json()
        try:
            params={'playerUrl':data['data']['url'],'playerId':jdata['playerId']}
            pd=self.fetch(f"{self.host}/api/v1/app/play/analysisMovieUrl", headers=self.headers, params=params).json()
            url,p=pd['data'],0
        except Exception as e:
            print(f"请求失败: {e}")
            url,p=data['data']['url'],0
        return  {'parse': p, 'url': url, 'header': {'User-Agent': 'okhttp/4.12.0'}}

    def localProxy(self, param):
        pass

    def liveContent(self, url):
        pass

    def gettk(self):
        data=self.fetch(f"{self.host}/api/v1/app/user/visitorInfo", headers=self.headers).json()
        return data['data']['token']

    def getdid(self):
        did=self.getCache('ldid')
        if not did:
            hex_chars = '0123456789abcdef'
            did =''.join(random.choice(hex_chars) for _ in range(16))
            self.setCache('ldid',did)
        return did

    def getd(self,jdata,player):
        x = jdata.copy()
        x.update({'playerId': str(player['id'])})
        response = self.post(f"{self.host}/api/v1/app/play/movieDetails", headers=self.headers, json=x).json()
        return x, response['data']['episodeList']

    def getv(self,d,c):
        f={d['playerId']:''}
        g=[]
        for i in c:
            j=d.copy()
            j.update({'episodeId':str(i['id'])})
            g.append(f"{i['episode']}${self.e64(json.dumps(j))}")
        f[d['playerId']]='#'.join(g)
        return f

    def getlist(self,data):
        videos = []
        for i in data:
            videos.append({
                'vod_id': f"{i['id']}@@{i['typeId']}",
                'vod_name': i.get('name'),
                'vod_pic': i.get('cover'),
                'vod_year': i.get('year'),
                'vod_remarks': i.get('totalEpisode')
            })
        return videos

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
