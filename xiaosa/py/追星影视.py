# -*- coding: utf-8 -*-
# by @嗷呜
import json
import random
import string
import sys
from base64 import b64decode, b64encode
from urllib.parse import quote, unquote
sys.path.append('..')
import concurrent.futures
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

    host='https://xy.51gy.top'

    headers = {
        'User-Agent': 'okhttp/4.9.1',
        'mark-time': 'null',
        'fn-api-version': '3.1.9',
        'versionCode': '19',
        'product': 'gysg',
        'sg': '22664e555e0015684f988833803b3055',
    }

    def homeContent(self, filter):
        data=self.fetch(f"{self.host}/api.php/vod/type", headers=self.headers).json()
        result,filters,videos = {},{},[]
        classes = [{'type_id': i['type_name'], 'type_name': i['type_name']} for i in data['list'][1:]]
        body={'token':'', 'type_id':data['list'][0]['type_id']}
        ldata=self.post(f"{self.host}/api.php/vod/category", data=body, headers=self.headers).json()
        for i in ldata['data']['banner']:
            videos.append({
                'vod_id':i.get('vod_id'),
                'vod_name':i.get('vod_name'),
                'vod_pic':i.get('vod_pic_thumb')
            })
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(classes)) as executor:
            future_to_aid = {executor.submit(self.fts, aid): aid for aid in classes}
            for future in concurrent.futures.as_completed(future_to_aid):
                aid = future_to_aid[future]
                try:
                    aid_id, fts = future.result()
                    filters[aid_id] = fts
                except Exception as e:
                    print(f"Error processing aid {aid}: {e}")
        result['class'] = classes
        result['filters'] = filters
        result['list'] = videos
        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        params={'state':extend.get('state',tid) or tid,'class':extend.get('classes','全部'),'area':extend.get('area','全部'),'year':extend.get('year','全部'),'lang':extend.get('lang','全部'),'version':extend.get('version','全部'),'pg':pg}
        data=self.fetch(f"{self.host}/api.php/vod/list", params=params, headers=self.headers).json()
        result = {}
        videos = []
        for i in data['data']['list']:
            if str(i.get('vod_id', 0)) != '0':
                videos.append({
                    'vod_id': i.get('vod_id'),
                    'vod_name': i.get('vod_name'),
                    'vod_pic': i.get('vod_pic'),
                    'vod_year': f"{i.get('vod_score')}分",
                    'vod_remarks': i.get('vod_remarks')
                })
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        body={'ids':ids[0],'uni_code':self.getunc(),'ac':'detail','token':''}
        data=self.post(f"{self.host}/api.php/vod/detail2", data=body, headers=self.headers).json()
        v=data['data']
        vod = {
            'type_name': v.get('type_name'),
            'vod_year': v.get('vod_year'),
            'vod_area': v.get('vod_area'),
            'vod_lang': v.get('vod_lang'),
            'vod_remarks': v.get('vod_remarks'),
            'vod_actor': v.get('vod_actor'),
            'vod_director': v.get('vod_director'),
            'vod_content': v.get('vod_content')
        }
        n,p=[],[]
        for i in v['vod_play_list']:
            pp=i['player_info']
            n.append(pp['show'])
            np=[]
            for j in i['urls']:
                cd={'parse':pp.get('parse'),'url':j['url'],'headers':pp.get('headers')}
                np.append(f"{j['name']}${self.e64(json.dumps(cd))}")
            p.append('#'.join(np))
        vod.update({'vod_play_from':'$$$'.join(n),'vod_play_url':'$$$'.join(p)})
        return {'list':[vod]}

    def searchContent(self, key, quick, pg="1"):
        data=self.fetch(f"{self.host}/api.php/vod/search", params={'keywords':key,'type':'1','pg':pg}, headers=self.headers).json()
        return {'list':data['list'],'page':pg}

    def playerContent(self, flag, id, vipFlags):
        ids=json.loads(self.d64(id))
        headers = {}
        urls=ids['url']
        if ids.get('headers'):
            hs=ids['headers'].split('=>',1)
            headers[hs[0].strip()]=hs[-1].strip()
        if isinstance(ids.get('parse'), list) and len(ids['parse']) > 0:
            urls=[]
            for i,x in enumerate(ids['parse']):
                su=f"{self.getProxyUrl()}&url={quote(x+ids['url'])}"
                urls.extend([f'解析{i+1}',su])
        return  {'parse': 0, 'url': urls, 'header': headers}

    def localProxy(self, param):
        try:
            body = {'url':unquote(param['url'])}
            data=self.post(f"{self.host}/api.php/vod/m_jie_xi", data=body, headers=self.headers).json()
            url=data.get('url') or data['data'].get('url')
            return [302,'video/MP2T',None,{'Location':url}]
        except:
            return []

    def liveContent(self, url):
        pass

    def fts(self, tdata):
        params={'state':tdata['type_id'],'pg':'1'}
        data = self.fetch(f"{self.host}/api.php/vod/list", params=params, headers=self.headers).json()
        ftks = ["classes", "area", "lang", "year", "version", "state"]
        filter = [
            {
                'name': k,
                'key': k,
                'value': [{'n': i, 'v': i} for i in v.split(',')]
            }
            for k, v in data['data']['classes']["type_extend"].items()
            if k in ftks and v
        ]
        return tdata['type_id'],filter

    def getunc(self):
        chars = string.ascii_lowercase + string.digits
        data = ''.join(random.choice(chars) for _ in range(16))
        return self.e64(data)

    def e64(self, text):
        try:
            text_bytes = text.encode('utf-8')
            encoded_bytes = b64encode(text_bytes)
            return encoded_bytes.decode('utf-8')
        except Exception as e:
            return ""

    def d64(self,encoded_text):
        try:
            encoded_bytes = encoded_text.encode('utf-8')
            decoded_bytes = b64decode(encoded_bytes)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            return ""