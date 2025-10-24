# -*- coding: utf-8 -*-
# by @嗷呜
import copy
import gzip
import json
import re
import sys
import time
import uuid
import requests
from base64 import b64decode
from Crypto.Hash import SHA1, HMAC
from pyquery import PyQuery as pq
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):

    def init(self, extend="{}"):
        config = json.loads(extend)
        self.host = f"{config['site']}"
        self.cfproxy = config.get('cfproxy', '')
        self.plp=config.get('plp', '')
        self.proxy=config.get('proxy', {})
        self.headers = {
            'referer': f'{self.host}',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
        }
        pass

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    xhost='https://client-rapi-missav.recombee.com'

    countr='/dm15/cn'

    ccccc='H4sIAAAAAAAAA4uuViqpLEiNz0vMTVWyUlB6Nqfhxf6Jz2ZveTZtg5IORC4zBSSTkmtqaKKfnKefl1quVKuDrm/ahid75zzZ0fV0RxOGPgsLkL6i1JzUxOJULHqnL3i+oPHZ1san7bvQ9ZoZGYL0luYlp+YV5xelpugCDcnGNOPp0s1P9sx4sqPhxfIOVDOAuhOTS4pSi4tTizH1Pd+4++m8bgwd6al5RdiUP+2f+GJhz9OpbRg6chOzU4uAOmIBkkRrDlIBAAA='

    fts = 'H4sIAAAAAAAAA23P30rDMBQG8FeRXM8X8FVGGZk90rA0HU3SMcZgXjn8V6p2BS2KoOiFAwUn2iK+TBP7GBpYXbG9/c6Pc77TnaABjNHOFtojVIDPUQcx7IJJvl9ydX30GwSYSpN0J4iZgTqJiywrPlN1vm/GJiPMJgGxJaZo2qnc3WXDuZIKMqSwUcX7Ui8O1DJRH3Gldh3CgMM2l31BhNGW8euq3PNFrac+PVNZ2NYzjMrbY53c6/Sm2uwDBczB7mGxqaDTWfkV6atXvXiu4FD2KeHOf3nxViahjv8YxwHYtWfyQ3NvFZYP85oSno3HvYDAiNevPqnosWFHAAPahnU6b2DXY8Jp0bO8QdfEmlo/SBd5PPUBAAA='

    actfts = 'H4sIAAAAAAAAA5WVS2sUQRRG/0rT6xTcqq5Xiwjm/X6sQxZjbBLRBBeOIEGIIEgWrtwI4lJEQsjGhU6Iv2bGcf6FVUUydW/d1SxT55sDfbpmsn9WP+/e1A+q+rh7dnT8qp6rT3snXTz4N7icXH4OB697L/rxZP+sPo1g+Ot8PPg+vvoyOb+IOJ7Vb+fuqGxkJSrZmMOTexiORDjAGxs3GvDGinCANjp5NPbo4NHYo5PHYI8OHoM9JnkM9pjgMdhjksdijwkeiz02eSz22OCx2GOTx2GPDR6HPS55HPa44HHY45LHY48LHo89Pnk89vjg8djjk6fFHh88bfAcxNXduz/sv0Qvfnz74+/X65lf/OMqfzD9ndF8geYzWijQQkaLBVrMaKlASxktF2g5o5UCrWS0WqDVjNYKtJbReoHWM9oo0EZGmwXazGirQFsZbRdoO6OdAu1ktFug3Yz2CrRH70TvqEN3YvT75+TP+5nvxMNKwf0pCIWur4JwM5spVCAaRJtI9ZQ2IPBPg47UTKkGgb/wJlI7pQYE/ho/QsiCaFv61E+7J338Izj6MJi8+xSefnhzO/PTK1CmGt58G118zM+pDBloPtBk0PBBQwaKDxQZSD6QZAB8QN6UbNlAtmTg+cCTgeMDRwaWDywZ8JKSlJS8pCQlJS8pSUnJS0pSUvKSkpSUvKQkJYGXBFISeEkgJYGXBFISeEkgJYGXBFISeEkgJYGXBFISeEkgJYGXBFISeElI/7QO/gOZ7bAksggAAA=='

    def homeContent(self, filter):
        html = pq(requests.get(f"{self.cfproxy}{self.host}{self.countr}",headers=self.headers,proxies=self.proxy).content)
        result = {}
        filters = {}
        classes=self.ungzip(self.ccccc)
        for i in classes:
            id=i['type_id']
            filters[id] = copy.deepcopy(self.ungzip(self.fts))
            if 'cn/actresses' in id:filters[id].extend(self.ungzip(self.actfts))
        result['class'] = classes
        result['filters'] = filters
        result['list'] = self.getlist(html('.grid-cols-2.md\\:grid-cols-3 .thumbnail.group'))
        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        params={
            'page':pg
        }
        ft = {
            'filters': extend.get('filters', ''),
            'sort': extend.get('sort', '')
        }
        if tid in ['cn/genres', 'cn/makers']:
            ft = {}
        elif tid == 'cn/actresses':
            ft = {
                'height': extend.get('height', ''),
                'cup': extend.get('cup', ''),
                'debut': extend.get('debut', ''),
                'age': extend.get('age', ''),
                'sort': extend.get('sort', '')
            }
        params.update(ft)
        params={k: v for k, v in params.items() if v}
        req = requests.Request(
            url=f"{self.host}/{tid}",
            params=params,
        ).prepare()
        data=pq(requests.get(f"{self.cfproxy}{req.url}",headers=self.headers,proxies=self.proxy).content)
        result = {}
        if tid in ['cn/genres', 'cn/makers']:
            videos = self.gmsca(data)
        elif tid == 'cn/actresses':
            videos = self.actca(data)
        else:
            videos = self.getlist(data('.grid-cols-2.md\\:grid-cols-3 .thumbnail.group'))
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        urlllll=f"{self.cfproxy}{self.host}/{ids[0]}"
        v=pq(requests.get(urlllll,headers=self.headers,proxies=self.proxy).content)
        sctx=v('body script').text()
        urls=self.execute_js(sctx)
        if not urls:urls=f"嗅探${urlllll}"
        c=v('.space-y-2 .text-secondary')
        ac,dt,cd,bq=[],[],[],['点击展开↓↓↓\n']
        for i in c.items():
            xxx=i('span').text()
            if re.search(r"导演:|发行商:",xxx):
                dt.extend(['[a=cr:' + json.dumps({'id': j.attr('href').split('/',3)[-1], 'name': j.text()}) + '/]' + j.text() + '[/a]' for j in i('a').items()])
            elif re.search(r"女优:",xxx):
                ac.extend(['[a=cr:' + json.dumps({'id': j.attr('href').split('/',3)[-1], 'name': j.text()}) + '/]' + j.text() + '[/a]' for j in i('a').items()])
            elif re.search(r"类型:|系列:",xxx):
                bq.extend(['[a=cr:' + json.dumps({'id': j.attr('href').split('/',3)[-1], 'name': j.text()}) + '/]' + j.text() + '[/a]' for j in i('a').items()])
            elif re.search(r"标籤:",xxx):
                cd.extend(['[a=cr:' + json.dumps({'id': j.attr('href').split('/',3)[-1], 'name': j.text()}) + '/]' + j.text() + '[/a]' for j in i('a').items()])
        np={'MissAV':urls,'Recommend':self.getfov(ids[0])}
        vod = {
            'type_name': c.eq(-3)('a').text(),
            'vod_year': c.eq(0)('time').text(),
            'vod_remarks': ' '.join(cd),
            'vod_actor': ' '.join(ac),
            'vod_director': ' '.join(dt),
            'vod_content': f"{' '.join(bq)}\n{v('.text-secondary.break-all').text()}"
        }
        names,plist=[],[]
        for i,j in np.items():
            if j:
                names.append(i)
                plist.append(j)
        vod['vod_play_from']='$$$'.join(names)
        vod['vod_play_url']='$$$'.join(plist)
        return {'list': [vod]}

    def searchContent(self, key, quick, pg="1"):
        req = requests.Request(
            url=f"{self.host}/search/{key}",
            params={'page': pg},
        ).prepare()
        data = pq(requests.get(f"{self.cfproxy}{req.url}", headers=self.headers, proxies=self.proxy).content)
        return {'list': self.getlist(data('.grid-cols-2.md\\:grid-cols-3 .thumbnail.group')),'page':pg}

    def playerContent(self, flag, id, vipFlags):
        p=0 if '.m3u8' in id else 1
        if flag == 'Recommend':
            urlllll = f"{self.cfproxy}{self.host}/{id}"
            try:
                v = pq(requests.get(urlllll, headers=self.headers, proxies=self.proxy).content)
                sctx = v('body script').text()
                url = self.execute_js(sctx)
                if not url: raise Exception("没有找到地址")
                p,id=0,url.split('$')[-1]
            except:
                p,id=1,urlllll
        return {'parse': p, 'url': id if p else f"{self.plp}{id}", 'header': self.headers}

    def localProxy(self, param):
        pass

    def getlist(self,data):
        videos = []
        names,ids=[],[]
        for i in data.items():
            k = i('.overflow-hidden.shadow-lg a')
            id=k.eq(0).attr('href')
            name=i('.text-secondary').text()
            if id and id not in ids and name not in names:
                ids.append(id)
                names.append(name)
                videos.append({
                    'vod_id': id.split('/',3)[-1],
                    'vod_name': name,
                    'vod_pic': k.eq(0)('img').attr('data-src'),
                    'vod_year': '' if len(list(k.items())) < 3 else k.eq(1).text(),
                    'vod_remarks': k.eq(-1).text(),
                    'style': {"type": "rect", "ratio": 1.33}
                })
        return videos

    def gmsca(self,data):
        acts=[]
        for i in data('.grid.grid-cols-2.md\\:grid-cols-3 div').items():
            id=i('.text-nord13').attr('href')
            acts.append({
                'vod_id':id.split('/', 3)[-1] if id else id,
                'vod_name': i('.text-nord13').text(),
                'vod_pic': '',
                'vod_remarks': i('.text-nord10').text(),
                'vod_tag': 'folder',
                'style': {"type": "rect", "ratio": 2}
            })
        return acts

    def actca(self,data):
        acts=[]
        for i in data('.max-w-full ul li').items():
            id=i('a').attr('href')
            acts.append({
                'vod_id': id.split('/', 3)[-1] if id else id,
                'vod_name': i('img').attr('alt'),
                'vod_pic': i('img').attr('src'),
                'vod_year': i('.text-nord10').eq(-1).text(),
                'vod_remarks': i('.text-nord10').eq(0).text(),
                'vod_tag': 'folder',
                'style': {"type": "oval"}
            })
        return acts

    def getfov(self, url):
        try:
            h=self.headers.copy()
            ids=url.split('/')
            h.update({'referer':f'{self.host}/{url}/'})
            t=str(int(time.time()))
            params = {
                'frontend_timestamp': t,
                'frontend_sign': self.getsign(f"/missav-default/batch/?frontend_timestamp={t}"),
            }
            uid=str(uuid.uuid4())
            json_data = {
                'requests': [
                    {
                        'method': 'POST',
                        'path': f'/recomms/items/{ids[-1]}/items/',
                        'params': {
                            'targetUserId': uid,
                            'count': 13,
                            'scenario': 'desktop-watch-next-side',
                            'returnProperties': True,
                            'includedProperties': [
                                'title_cn',
                                'duration',
                                'has_chinese_subtitle',
                                'has_english_subtitle',
                                'is_uncensored_leak',
                                'dm',
                            ],
                            'cascadeCreate': True,
                        },
                    },
                    {
                        'method': 'POST',
                        'path': f'/recomms/items/{ids[-1]}/items/',
                        'params': {
                            'targetUserId': uid,
                            'count': 12,
                            'scenario': 'desktop-watch-next-bottom',
                            'returnProperties': True,
                            'includedProperties': [
                                'title_cn',
                                'duration',
                                'has_chinese_subtitle',
                                'has_english_subtitle',
                                'is_uncensored_leak',
                                'dm',
                            ],
                            'cascadeCreate': True,
                        },
                    },
                ],
                'distinctRecomms': True,
            }
            data = requests.post(f'{self.xhost}/missav-default/batch/', params=params,headers=h, json=json_data,proxies=self.proxy).json()
            vdata=[]
            for i in data:
                for j in i['json']['recomms']:
                    if j.get('id'):
                        vdata.append(f"{j['values']['title_cn']}${j['id']}")
            return '#'.join(vdata)
        except Exception as e:
            self.log(f"获取推荐失败: {e}")
            return ''

    def getsign(self, text):
        message_bytes = text.encode('utf-8')
        key_bytes = b'Ikkg568nlM51RHvldlPvc2GzZPE9R4XGzaH9Qj4zK9npbbbTly1gj9K4mgRn0QlV'
        h = HMAC.new(key_bytes, digestmod=SHA1)
        h.update(message_bytes)
        signature = h.hexdigest()
        return signature

    def ungzip(self, data):
        result=gzip.decompress(b64decode(data)).decode('utf-8')
        return json.loads(result)

    def execute_js(self, jstxt):
        js_code = re.search(r"eval\(function\(p,a,c,k,e,d\).*?return p}(.*?)\)\)", jstxt).group(0)
        try:
            from com.whl.quickjs.wrapper import QuickJSContext
            ctx = QuickJSContext.create()
            result=ctx.evaluate(f"{js_code}\nsource")
            ctx.destroy()
            return f"多画质${result}"
        except Exception as e:
            self.log(f"执行失败: {e}")
            return None
