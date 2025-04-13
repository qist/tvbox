# -*- coding: utf-8 -*-
# by @嗷呜
import random
import sys
from base64 import b64encode, b64decode
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlencode
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):

    def init(self, extend=""):
        self.did = self.random_str(32)
        pass

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    rhost = 'https://www.iqiyi.com'

    hhost='https://mesh.if.iqiyi.com'

    dhost='https://miniapp.iqiyi.com'

    headers = {
        'Origin': rhost,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        'Referer': f'{rhost}/',
    }

    def homeContent(self, filter):
        result = {}
        cateManual = {
            "全部": "1009",
            "电影": "1",
            "剧集": "2",
            "综艺": "6",
            "动漫": "4",
            "儿童": "15",
            "微剧": "35",
            "纪录片": "3"
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
        data=self.fetch(f'{self.hhost}/portal/lw/v5/channel/recommend?v=13.014.21150', headers=self.headers).json()
        vlist = []
        for i in data['items'][1:]:
            for j in i['video'][0]['data']:
                id = j.get('firstId')
                pic=j.get('prevue',{}).get('image_url') or j.get('album_image_url_hover')
                if id and pic:
                    pu=j.get('prevue',{}).get('page_url') or j.get('page_url').split('?')[0]
                    id = f'{id}@{self.e64(pu)}'
                    vlist.append({
                        'vod_id': id,
                        'vod_name': j.get('display_name'),
                        'vod_pic': pic,
                        'vod_year': j.get('sns_score'),
                        'vod_remarks': j.get('dq_updatestatus') or j.get('rank_prefix')
                    })
        return {'list':vlist}

    def categoryContent(self, tid, pg, filter, extend):
        if pg == "1":
            self.sid = ''
        new_data = {'mode':'24'}
        for key, value in extend.items():
            if value:
                key_value_pairs = self.d64(value).split(',')
                for pair in key_value_pairs:
                    k, v = pair.split('=')
                    if k in new_data:
                        new_data[k] += "," + v
                    else:
                        new_data[k] = v
        path=f'/portal/lw/videolib/data?uid=&passport_id=&ret_num=60&version=13.014.21150&device_id={self.did}&channel_id={tid}&page_id={pg}&session={self.sid}&os=&conduit_id=&vip=0&auth&recent_selected_tag=&ad=%5B%7B%22lm%22:%225%22,%22ai%22:%225%22,%22fp%22:%226%22,%22sei%22:%22Sa867aa9d326e2bd8654d8c2a8636055e%22,%22position%22:%22library%22%7D%5D&adExt=%7B%22r%22:%221.2.1-ares6-pure%22%7D&dfp=a12f96215b2f7842a98c082799ca0c3d9236be00946701b106829754d8ece3aaf8&filter={urlencode(new_data)}'
        data=self.fetch(f'{self.hhost}{path}', headers=self.headers).json()
        self.sid = data['session']
        videos = []
        for i in data['data']:
            id = i.get('firstId') or i.get('tv_id')
            if not id:
                id=i.get('play_url').split(';')[0].split('=')[-1]
            if id and not i.get('h'):
                id=f'{id}@{self.e64(i.get("page_url"))}'
                videos.append({
                    'vod_id': id,
                    'vod_name': i.get('display_name'),
                    'vod_pic': i.get('album_image_url_hover'),
                    'vod_year': i.get('sns_score'),
                    'vod_remarks': i.get('dq_updatestatus') or i.get('pay_mark')
                })
        result = {}
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        ids = ids[0].split('@')
        ids[-1] = self.d64(ids[-1])
        data = self.fetch(f'{self.dhost}/h5/mina/baidu/play/body/v1/{ids[0]}/', headers=self.headers).json()
        v=data['data']['playInfo']
        vod = {
            'vod_name': v.get('albumName'),
            'type_name': v.get('tags'),
            'vod_year': v.get('albumYear'),
            'vod_remarks': v.get('updateStrategy'),
            'vod_actor': v.get('mainActors'),
            'vod_director': v.get('directors'),
            'vod_content': v.get('albumDesc'),
            'vod_play_from': '爱奇艺',
            'vod_play_url': ''
        }
        if data.get('data') and data['data'].get('videoList') and data['data']['videoList'].get('videos'):
            purl=[f'{i["shortTitle"]}${i["pageUrl"]}' for i in data['data']['videoList']['videos']]
            pg=data['data']['videoList'].get('totalPages')
            if pg and pg > 1:
                id = v['albumId']
                pages = list(range(2, pg + 1))
                page_results = {}
                with ThreadPoolExecutor(max_workers=10) as executor:
                    future_to_page = {
                        executor.submit(self.fetch_page_data, page, id): page
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
                    purl.extend(page_results[page])
            vod['vod_play_url'] = '#'.join(purl)
        else:
            vdata=self.fetch(f'{self.dhost}/h5/mina/baidu/play/head/v1/{ids[0]}/', headers=self.headers).json()
            v=vdata['data']['playInfo']
            vod = {
                'vod_name': v.get('shortTitle'),
                'type_name': v.get('channelName'),
                'vod_year': v.get('year'),
                'vod_remarks': v.get('focus'),
                'vod_actor': v.get('mainActors'),
                'vod_director': v.get('directors'),
                'vod_content': v.get('desc'),
                'vod_play_from': '爱奇艺',
                'vod_play_url': f'{v.get("shortTitle")}${ids[-1]}'
            }
        return {'list':[vod]}

    def searchContent(self, key, quick, pg="1"):
        data=self.fetch(f'{self.hhost}/portal/lw/search/homePageV3?key={key}&current_page={pg}&mode=1&source=input&suggest=&version=13.014.21150&pageNum={pg}&pageSize=25&pu=&u={self.did}&scale=150&token=&userVip=0&conduit=&vipType=-1&os=&osShortName=win10&dataType=&appMode=', headers=self.headers).json()
        videos = []
        vdata=data['data']['templates']
        for i in data['data']['templates']:
            if i.get('intentAlbumInfos'):
                vdata=[{'albumInfo': c} for c in i['intentAlbumInfos']]+vdata

        for i in vdata:
            if i.get('albumInfo') and (i['albumInfo'].get('playQipuId','') or i['albumInfo'].get('qipuId')) and i['albumInfo'].get('pageUrl'):
                b=i['albumInfo']
                id=f"{(b.get('playQipuId','') or b.get('qipuId'))}@{self.e64(b.get('pageUrl'))}"
                videos.append({
                    'vod_id': id,
                    'vod_name': b.get('title'),
                    'vod_pic': b.get('img'),
                    'vod_year': (b.get('year',{}) or {}).get('value'),
                    'vod_remarks': b.get('subscriptContent') or b.get('channel') or b.get('vipTips')
                })
        return {'list':videos,'page':pg}

    def playerContent(self, flag, id, vipFlags):
        return  {'jx':1,'parse': 1, 'url': id, 'header': ''}

    def localProxy(self, param):
        pass

    def fetch_page_data(self, page, id):
        try:
            url = f'{self.dhost}/h5/mina/avlist/{page}/{id}/'
            data = self.fetch(url, headers=self.headers).json()
            return [f'{i["shortTitle"]}${i["pageUrl"]}' for i in data['data']['videoList']['videos']]
        except:
            return []

    def getf(self,body):
        data=self.fetch(f'{self.hhost}/portal/lw/videolib/tag?channel_id={body["type_id"]}&tagAdd=&selected_tag_name=&version=13.014.21150&device={self.did}&uid=', headers=self.headers).json()
        ft = []
        # for i in data[:-1]:
        for i in data:
            try:
                value_array = [{"n": value['text'], "v": self.e64(value['tag_param'])} for value in i['tags'] if
                               value.get('tag_param')]
                ft.append({"key": i['group'], "name": i['group'], "value": value_array})
            except:
                print(i)
        return (body['type_id'], ft)

    def e64(self, text):
        try:
            text_bytes = text.encode('utf-8')
            encoded_bytes = b64encode(text_bytes)
            return encoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Base64编码错误: {str(e)}")
            return ""

    def d64(self,encoded_text: str):
        try:
            encoded_bytes = encoded_text.encode('utf-8')
            decoded_bytes = b64decode(encoded_bytes)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Base64解码错误: {str(e)}")
            return ""

    def random_str(self,length=16):
        hex_chars = '0123456789abcdef'
        return ''.join(random.choice(hex_chars) for _ in range(length))
