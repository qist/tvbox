# -*- coding: utf-8 -*-
# by @嗷呜
import json
import sys
import threading
import uuid
import requests
sys.path.append('..')
from base.spider import Spider
import time
from Crypto.Hash import MD5, SHA1

class Spider(Spider):
    '''
    配置示例：
    {
        "key": "xxxx",
        "name": "xxxx",
        "type": 3,
        "api": ".所在路径/金牌.py",
        "searchable": 1,
        "quickSearch": 1,
        "filterable": 1,
        "changeable": 1,
        "ext": {
            "site": "https://www.jiabaide.cn,域名2,域名3"
        }
    },
    '''
    def init(self, extend=""):
        if extend:
            hosts=json.loads(extend)['site']
        self.host = self.host_late(hosts)
        pass

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    def homeContent(self, filter):
        cdata = self.fetch(f"{self.host}/api/mw-movie/anonymous/get/filer/type", headers=self.getheaders()).json()
        fdata = self.fetch(f"{self.host}/api/mw-movie/anonymous/v1/get/filer/list", headers=self.getheaders()).json()
        result = {}
        classes = []
        filters={}
        for k in cdata['data']:
            classes.append({
                'type_name': k['typeName'],
                'type_id': str(k['typeId']),
            })
        sort_values = [{"n": "最近更新", "v": "2"},{"n": "人气高低", "v": "3"}, {"n": "评分高低", "v": "4"}]
        for tid, d in fdata['data'].items():
            current_sort_values = sort_values.copy()
            if tid == '1':
                del current_sort_values[0]
            filters[tid] = [
                {"key": "type", "name": "类型",
                 "value": [{"n": i["itemText"], "v": i["itemValue"]} for i in d["typeList"]]},

                *([] if not d["plotList"] else [{"key": "v_class", "name": "剧情",
                                                 "value": [{"n": i["itemText"], "v": i["itemText"]}
                                                           for i in d["plotList"]]}]),

                {"key": "area", "name": "地区",
                 "value": [{"n": i["itemText"], "v": i["itemText"]} for i in d["districtList"]]},

                {"key": "year", "name": "年份",
                 "value": [{"n": i["itemText"], "v": i["itemText"]} for i in d["yearList"]]},

                {"key": "lang", "name": "语言",
                 "value": [{"n": i["itemText"], "v": i["itemText"]} for i in d["languageList"]]},

                {"key": "sort", "name": "排序", "value": current_sort_values}
            ]
        result['class'] = classes
        result['filters'] = filters
        return result

    def homeVideoContent(self):
        data1 = self.fetch(f"{self.host}/api/mw-movie/anonymous/v1/home/all/list", headers=self.getheaders()).json()
        data2=self.fetch(f"{self.host}/api/mw-movie/anonymous/home/hotSearch",headers=self.getheaders()).json()
        data=[]
        for i in data1['data'].values():
            data.extend(i['list'])
        data.extend(data2['data'])
        vods=self.getvod(data)
        return {'list':vods}

    def categoryContent(self, tid, pg, filter, extend):

        params = {
          "area": extend.get('area', ''),
          "filterStatus": "1",
          "lang": extend.get('lang', ''),
          "pageNum": pg,
          "pageSize": "30",
          "sort": extend.get('sort', '1'),
          "sortBy": "1",
          "type": extend.get('type', ''),
          "type1": tid,
          "v_class": extend.get('v_class', ''),
          "year": extend.get('year', '')
        }
        data = self.fetch(f"{self.host}/api/mw-movie/anonymous/video/list?{self.js(params)}", headers=self.getheaders(params)).json()
        result = {}
        result['list'] = self.getvod(data['data']['list'])
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        data=self.fetch(f"{self.host}/api/mw-movie/anonymous/video/detail?id={ids[0]}",headers=self.getheaders({'id':ids[0]})).json()
        vod=self.getvod([data['data']])[0]
        vod['vod_play_from']='金牌'
        vod['vod_play_url'] = '#'.join(
            f"{i['name'] if len(vod['episodelist']) > 1 else vod['vod_name']}${ids[0]}@@{i['nid']}" for i in
            vod['episodelist'])
        vod.pop('episodelist', None)
        return {'list':[vod]}

    def searchContent(self, key, quick, pg="1"):
        params = {
          "keyword": key,
          "pageNum": pg,
          "pageSize": "8",
          "sourceCode": "1"
        }
        data=self.fetch(f"{self.host}/api/mw-movie/anonymous/video/searchByWord?{self.js(params)}",headers=self.getheaders(params)).json()
        vods=self.getvod(data['data']['result']['list'])
        return {'list':vods,'page':pg}

    def playerContent(self, flag, id, vipFlags):
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.61 Chrome/126.0.6478.61 Not/A)Brand/8  Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'DNT': '1',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'Origin': self.host,
            'Referer': f'{self.host}/'
        }
        ids=id.split('@@')
        pdata = self.fetch(f"{self.host}/api/mw-movie/anonymous/v2/video/episode/url?clientType=1&id={ids[0]}&nid={ids[1]}",headers=self.getheaders({'clientType':'1','id': ids[0], 'nid': ids[1]})).json()
        vlist=[]
        for i in pdata['data']['list']:vlist.extend([i['resolutionName'],i['url']])
        return {'parse':0,'url':vlist,'header':self.header}

    def localProxy(self, param):
        pass

    def host_late(self, url_list):
        if isinstance(url_list, str):
            urls = [u.strip() for u in url_list.split(',')]
        else:
            urls = url_list
        if len(urls) <= 1:
            return urls[0] if urls else ''

        results = {}
        threads = []

        def test_host(url):
            try:
                start_time = time.time()
                response = requests.head(url, timeout=1.0, allow_redirects=False)
                delay = (time.time() - start_time) * 1000
                results[url] = delay
            except Exception as e:
                results[url] = float('inf')
        for url in urls:
            t = threading.Thread(target=test_host, args=(url,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        return min(results.items(), key=lambda x: x[1])[0]

    def md5(self, sign_key):
        md5_hash = MD5.new()
        md5_hash.update(sign_key.encode('utf-8'))
        md5_result = md5_hash.hexdigest()
        return md5_result

    def js(self, param):
        return '&'.join(f"{k}={v}" for k, v in param.items())

    def getheaders(self, param=None):
        if param is None:param = {}
        t=str(int(time.time()*1000))
        param['key']='cb808529bae6b6be45ecfab29a4889bc'
        param['t']=t
        sha1_hash = SHA1.new()
        sha1_hash.update(self.md5(self.js(param)).encode('utf-8'))
        sign = sha1_hash.hexdigest()
        deviceid = str(uuid.uuid4())
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.61 Chrome/126.0.6478.61 Not/A)Brand/8  Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'sign': sign,
            't': t,
            'deviceid':deviceid
        }
        return headers

    def convert_field_name(self, field):
        field = field.lower()
        if field.startswith('vod') and len(field) > 3:
            field = field.replace('vod', 'vod_')
        if field.startswith('type') and len(field) > 4:
            field = field.replace('type', 'type_')
        return field

    def getvod(self, array):
        return [{self.convert_field_name(k): v for k, v in item.items()} for item in array]

