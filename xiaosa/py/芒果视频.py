# -*- coding: utf-8 -*-
# by @嗷呜
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
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

    rhost='https://www.mgtv.com'

    host='https://pianku.api.mgtv.com'

    vhost='https://pcweb.api.mgtv.com'

    mhost='https://dc.bz.mgtv.com'

    shost='https://mobileso.bz.mgtv.com'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.61 Chrome/126.0.6478.61 Not/A)Brand/8  Safari/537.36',
        'origin': rhost,
        'referer': f'{rhost}/'
    }

    def homeContent(self, filter):
        result = {}
        cateManual = {
            "电影": "3",
            "电视剧": "2",
            "综艺": "1",
            "动画": "50",
            "少儿": "10",
            "纪录片": "51",
            "教育": "115"
        }
        classes = []
        filters = {}
        for k in cateManual:
            classes.append({
                'type_name': k,
                'type_id': cateManual[k]
            })
        with ThreadPoolExecutor(max_workers=len(classes)) as executor:
            results = executor.map(self.getf, classes)
            for id, ft in results:
                if len(ft):filters[id] = ft
        result['class'] = classes
        result['filters'] = filters
        return result

    def homeVideoContent(self):
        data=self.fetch(f'{self.mhost}/dynamic/v1/channel/index/0/0/0/1000000/0/0/17/1354?type=17&version=5.0&t={str(int(time.time()*1000))}&_support=10000000', headers=self.headers).json()
        videoList = []
        for i in data['data']:
            if i.get('DSLList') and len(i['DSLList']):
                for j in i['DSLList']:
                    if j.get('data') and j['data'].get('items') and len(j['data']['items']):
                        for k in j['data']['items']:
                            videoList.append({
                                'vod_id': k["videoId"],
                                'vod_name': k['videoName'],
                                'vod_pic': k['img'],
                                'vod_year': k.get('cornerTitle'),
                                'vod_remarks': k.get('time') or k.get('desc'),
                            })
        return {'list':videoList}

    def categoryContent(self, tid, pg, filter, extend):
        body={
            'allowedRC': '1',
            'platform': 'pcweb',
            'channelId': tid,
            'pn': pg,
            'pc': '80',
            'hudong': '1',
            '_support': '10000000'
        }
        body.update(extend)
        data=self.fetch(f'{self.host}/rider/list/pcweb/v3', params=body, headers=self.headers).json()
        videoList = []
        for i in data['data']['hitDocs']:
            videoList.append({
                'vod_id': i["playPartId"],
                'vod_name': i['title'],
                'vod_pic': i['img'],
                'vod_year': (i.get('rightCorner',{}) or {}).get('text') or i.get('year'),
                'vod_remarks': i['updateInfo']
            })
        result = {}
        result['list'] = videoList
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        vbody={'allowedRC': '1', 'vid': ids[0], 'type': 'b', '_support': '10000000'}
        vdata=self.fetch(f'{self.vhost}/video/info', params=vbody, headers=self.headers).json()
        d=vdata['data']['info']['detail']
        vod = {
            'vod_name': vdata['data']['info']['title'],
            'type_name': d.get('kind'),
            'vod_year': d.get('releaseTime'),
            'vod_area': d.get('area'),
            'vod_lang': d.get('language'),
            'vod_remarks': d.get('updateInfo'),
            'vod_actor': d.get('leader'),
            'vod_director': d.get('director'),
            'vod_content': d.get('story'),
            'vod_play_from': '芒果TV',
            'vod_play_url': ''
        }
        data,pdata=self.fetch_page_data('1', ids[0],True)
        pagecount=data['data'].get('total_page') or 1
        if int(pagecount)>1:
            pages = list(range(2, pagecount+1))
            page_results = {}
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_page = {
                    executor.submit(self.fetch_page_data, page, ids[0]): page
                    for page in pages
                }
                for future in as_completed(future_to_page):
                    page = future_to_page[future]
                    try:
                        result = future.result()
                        page_results[page] = result
                    except Exception as e:
                        print(f"Error fetching page {page}: {e}")
            for page in sorted(page_results.keys()):
                pdata.extend(page_results[page])
        vod['vod_play_url'] = '#'.join(pdata)
        return {'list':[vod]}

    def searchContent(self, key, quick, pg="1"):
        data=self.fetch(f'{self.shost}/applet/search/v1?channelCode=mobile-wxap&q={key}&pn={pg}&pc=10&_support=10000000', headers=self.headers).json()
        videoList = []
        for i in data['data']['contents']:
            if i.get('data') and len(i['data']):
                k = i['data'][0]
                if k.get('vid') and k.get('img'):
                    try:
                        videoList.append({
                            'vod_id': k['vid'],
                            'vod_name': k['title'],
                            'vod_pic': k['img'],
                            'vod_year': (i.get('rightTopCorner',{}) or {}).get('text') or i.get('year'),
                            'vod_remarks': '/'.join(i.get('desc',[])),
                        })
                    except:
                        print(k)
        return {'list':videoList,'page':pg}

    def playerContent(self, flag, id, vipFlags):
        id=f'{self.rhost}{id}'
        return  {'jx':1,'parse': 1, 'url': id, 'header': ''}

    def localProxy(self, param):
        pass

    def getf(self, body):
        params = {
            'allowedRC': '1',
            'channelId': body['type_id'],
            'platform': 'pcweb',
            '_support': '10000000',
        }
        data = self.fetch(f'{self.host}/rider/config/channel/v1', params=params, headers=self.headers).json()
        ft = []
        for i in data['data']['listItems']:
            try:
                value_array = [{"n": value['tagName'], "v": value['tagId']} for value in i['items'] if
                               value.get('tagName')]
                ft.append({"key": i['eName'], "name": i['typeName'], "value": value_array})
            except:
                print(i)
        return body['type_id'], ft

    def fetch_page_data(self, page, id, b=False):
        body = {'version': '5.5.35', 'video_id': id, 'page': page, 'size': '30',
                'platform': '4', 'src': 'mgtv', 'allowedRC': '1', '_support': '10000000'}
        data = self.fetch(f'{self.vhost}/episode/list', params=body, headers=self.headers).json()
        ldata = [f'{i["t3"]}${i["url"]}' for i in data['data']['list']]
        if b:
            return data, ldata
        else:
            return ldata
