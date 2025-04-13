# -*- coding: utf-8 -*-
# by @嗷呜
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote
from Crypto.Hash import MD5
import requests
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):

    def init(self, extend=""):
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.cookies.update(self.cookie)
        self.get_ctoken()
        pass

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    host='https://www.youku.com'

    shost='https://search.youku.com'

    h5host='https://acs.youku.com'
    
    ihost='https://v.youku.com'

    headers = {
        'User-Agent': 'Mozilla/5.0 (; Windows 10.0.26100.3194_64 ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Electron/14.2.0 Safari/537.36 Node/14.17.0 YoukuDesktop/9.2.60 UOSYouku (2.0.1)-Electron(UTDID ZYmGMAAAACkDAMU8hbiMmYdd;CHANNEL official;ZREAL 0;BTYPE TM2013;BRAND TIMI;BUILDVER 9.2.60.1001)',
        'Referer': f'{host}/'
    }

    cookie={
      "__ysuid": "17416134165380iB",
      "__aysid": "1741613416541WbD",
      "xlly_s": "1",
      "isI18n": "false",
      "cna": "bNdVIKmmsHgCAXW9W6yrQ1/s",
      "__ayft": "1741672162330",
      "__arpvid": "1741672162331FBKgrn-1741672162342",
      "__ayscnt": "1",
      "__aypstp": "1",
      "__ayspstp": "3",
      "tfstk": "gZbiib4JpG-6DqW-B98_2rwPuFrd1fTXQt3vHEp4YpJIBA3OgrWcwOi90RTOo9XVQ5tAM5NcK_CP6Ep97K2ce1XDc59v3KXAgGFLyzC11ET2n8U8yoyib67M3xL25e8gS8pbyzC1_ET4e8URWTsSnHv2uh8VTeJBgEuN3d-ELQAWuKWV36PHGpJ2uEWVTxvicLX1ewyUXYSekxMf-CxMEqpnoqVvshvP_pABOwvXjL5wKqeulm52np_zpkfCDGW9Ot4uKFIRwZtP7vP9_gfAr3KEpDWXSIfWRay-DHIc_Z-hAzkD1i5Ooi5LZ0O5YO_1mUc476YMI3R6xzucUnRlNe_zemKdm172xMwr2L7CTgIkbvndhFAVh3_YFV9Ng__52U4SQKIdZZjc4diE4EUxlFrfKmiXbBOHeP72v7sAahuTtWm78hRB1yV3tmg9bBOEhWVnq5KwOBL5."
    }

    def homeContent(self, filter):
        result = {}
        categories = ["电视剧", "电影", "综艺", "动漫", "少儿", "纪录片", "文化", "亲子", "教育", "搞笑", "生活",
                      "体育", "音乐", "游戏"]
        classes = [{'type_name': category, 'type_id': category} for category in categories]
        filters = {}
        self.typeid = {}
        with ThreadPoolExecutor(max_workers=len(categories)) as executor:
            tasks = {
                executor.submit(self.cf, {'type': category}, True): category
                for category in categories
            }

            for future in as_completed(tasks):
                try:
                    category = tasks[future]
                    session, ft = future.result()
                    filters[category] = ft
                    self.typeid[category] = session
                except Exception as e:
                    print(f"处理分类 {tasks[future]} 时出错: {str(e)}")

        result['class'] = classes
        result['filters'] = filters
        return result

    def homeVideoContent(self):
        try:
            vlist = []
            params={"ms_codes":"2019061000","params":"{\"debug\":0,\"gray\":0,\"pageNo\":1,\"utdid\":\"ZYmGMAAAACkDAMU8hbiMmYdd\",\"userId\":\"\",\"bizKey\":\"YOUKU_WEB\",\"appPackageKey\":\"com.youku.YouKu\",\"showNodeList\":0,\"reqSubNode\":0,\"nodeKey\":\"WEBHOME\",\"bizContext\":\"{\\\"spmA\\\":\\\"a2hja\\\"}\"}","system_info":"{\"device\":\"pcweb\",\"os\":\"pcweb\",\"ver\":\"1.0.0.0\",\"userAgent\":\"Mozilla/5.0 (; Windows 10.0.26100.3194_64 ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Electron/14.2.0 Safari/537.36 Node/14.17.0 YoukuDesktop/9.2.60 UOSYouku (2.0.1)-Electron(UTDID ZYmGMAAAACkDAMU8hbiMmYdd;CHANNEL official;ZREAL 0;BTYPE TM2013;BRAND TIMI;BUILDVER 9.2.60.1001)\",\"guid\":\"1590141704165YXe\",\"appPackageKey\":\"com.youku.pcweb\",\"young\":0,\"brand\":\"\",\"network\":\"\",\"ouid\":\"\",\"idfa\":\"\",\"scale\":\"\",\"operator\":\"\",\"resolution\":\"\",\"pid\":\"\",\"childGender\":0,\"zx\":0}"}
            data=self.getdata(f'{self.h5host}/h5/mtop.youku.columbus.home.query/1.0/',params)
            okey=list(data['data'].keys())[0]
            for i in data['data'][okey]['data']['nodes'][0]['nodes'][-1]['nodes'][0]['nodes']:
                if i.get('nodes') and i['nodes'][0].get('data'):
                    i=i['nodes'][0]['data']
                    if i.get('assignId'):
                        vlist.append({
                            'vod_id': i['assignId'],
                            'vod_name': i.get('title'),
                            'vod_pic': i.get('vImg') or i.get('img'),
                            'vod_year': i.get('mark',{}).get('data',{}).get('text'),
                            'vod_remarks': i.get('summary')
                        })
            return {'list': vlist}
        except Exception as e:
            print(f"处理主页视频数据时出错: {str(e)}")
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        vlist = []
        result['page'] = pg
        result['limit'] = 90
        result['total'] = 999999
        pagecount = 9999
        params = {'type': tid}
        id = self.typeid[tid]
        params.update(extend)
        if pg == '1':
            id=self.cf(params)
        data=self.session.get(f'{self.host}/category/data?session={id}&params={quote(json.dumps(params))}&pageNo={pg}').json()
        try:
            data=data['data']['filterData']
            for i in data['listData']:
                if i.get('videoLink') and 's=' in i['videoLink']:
                    vlist.append({
                        'vod_id': i.get('videoLink').split('s=')[-1],
                        'vod_name': i.get('title'),
                        'vod_pic': i.get('img'),
                        'vod_year': i.get('rightTagText'),
                        'vod_remarks': i.get('summary')
                    })
            self.typeid[tid]=quote(json.dumps(data['session']))
        except:
            pagecount=pg
        result['list'] = vlist
        result['pagecount'] = pagecount
        return result

    def detailContent(self, ids):
        try:
            data=self.session.get(f'{self.ihost}/v_getvideo_info/?showId={ids[0]}').json()
            v=data['data']
            vod = {
                'type_name': v.get('showVideotype'),
                'vod_year': v.get('lastUpdate'),
                'vod_remarks': v.get('rc_title'),
                'vod_actor': v.get('_personNameStr'),
                'vod_content': v.get('showdesc'),
                'vod_play_from': '优酷',
                'vod_play_url': ''
            }
            params={"biz":"new_detail_web2","videoId":v.get('vid'),"scene":"web_page","componentVersion":"3","ip":data.get('ip'),"debug":0,"utdid":"ZYmGMAAAACkDAMU8hbiMmYdd","userId":0,"platform":"pc","nextSession":"","gray":0,"source":"pcNoPrev","showId":ids[0]}
            sdata,index=self.getinfo(params)
            pdata=sdata['nodes']
            if index > len(pdata):
                batch_size = len(pdata)
                total_batches = ((index + batch_size - 1) // batch_size) - 1
                ssj = json.loads(sdata['data']['session'])
                with ThreadPoolExecutor(max_workers=total_batches) as executor:
                    futures = []
                    for batch in range(total_batches):
                        start = batch_size + 1 + (batch * batch_size)
                        end = start + batch_size - 1
                        next_session = ssj.copy()
                        next_session.update({
                            "itemStartStage": start,
                            "itemEndStage": min(end, index)
                        })
                        current_params = params.copy()
                        current_params['nextSession'] = json.dumps(next_session)
                        futures.append((start, executor.submit(self.getvinfo, current_params)))
                    futures.sort(key=lambda x: x[0])

                    for _, future in futures:
                        try:
                            result = future.result()
                            pdata.extend(result['nodes'])
                        except Exception as e:
                            print(f"Error fetching data: {str(e)}")
            vod['vod_play_url'] = '#'.join([f"{i['data'].get('title')}${i['data']['action'].get('value')}" for i in pdata])
            return {'list': [vod]}
        except Exception as e:
            print(e)
            return {'list': [{'vod_play_from': '哎呀翻车啦', 'vod_play_url': f'呜呜呜${self.host}'}]}

    def searchContent(self, key, quick, pg="1"):
        data=self.session.get(f'{self.shost}/api/search?pg={pg}&keyword={key}').json()
        vlist = []
        for i in data['pageComponentList']:
            if i.get('commonData') and (i['commonData'].get('showId') or i['commonData'].get('realShowId')):
                i=i['commonData']
                vlist.append({
                    'vod_id': i.get('showId') or i.get('realShowId'),
                    'vod_name': i['titleDTO'].get('displayName'),
                    'vod_pic': i['posterDTO'].get('vThumbUrl'),
                    'vod_year': i.get('feature'),
                    'vod_remarks': i.get('updateNotice')
                    })
        return {'list': vlist, 'page': pg}

    def playerContent(self, flag, id, vipFlags):
        return  {'jx':1,'parse': 1, 'url': f"{self.ihost}/video?vid={id}", 'header': ''}

    def localProxy(self, param):
        pass

    def cf(self,params,b=False):
        response = self.session.get(f'{self.host}/category/data?params={quote(json.dumps(params))}&optionRefresh=1&pageNo=1').json()
        data=response['data']['filterData']
        session=quote(json.dumps(data['session']))
        if b:
            return session,self.get_filter_data(data['filter']['filterData'][1:])
        return session

    def process_key(self, key):
        if '_' not in key:
            return key
        parts = key.split('_')
        result = parts[0]
        for part in parts[1:]:
            if part:
                result += part[0].upper() + part[1:]
        return result

    def get_filter_data(self, data):
        result = []
        try:
            for item in data:
                if not item.get('subFilter'):
                    continue
                first_sub = item['subFilter'][0]
                if not first_sub.get('filterType'):
                    continue
                filter_item = {
                    'key': self.process_key(first_sub['filterType']),
                    'name': first_sub['title'],
                    'value': []
                }
                for sub in item['subFilter']:
                    if 'value' in sub:
                        filter_item['value'].append({
                            'n': sub['title'],
                            'v': sub['value']
                        })
                if filter_item['value']:
                    result.append(filter_item)

        except Exception as e:
            print(f"处理筛选数据时出错: {str(e)}")

        return result

    def get_ctoken(self):
        data=self.session.get(f'{self.h5host}/h5/mtop.ykrec.recommendservice.recommend/1.0/?jsv=2.6.1&appKey=24679788')

    def md5(self,t,text):
        h = MD5.new()
        token=self.session.cookies.get('_m_h5_tk').split('_')[0]
        data=f"{token}&{t}&24679788&{text}"
        h.update(data.encode('utf-8'))
        return h.hexdigest()

    def getdata(self, url, params, recursion_count=0, max_recursion=3):
        data = json.dumps(params)
        t = int(time.time() * 1000)
        jsdata = {
            'appKey': '24679788',
            't': t,
            'sign': self.md5(t, data),
            'data': data
        }
        response = self.session.get(url, params=jsdata)
        if '令牌过期' in response.text:
            if recursion_count >= max_recursion:
                raise Exception("达到最大递归次数，无法继续请求")
            self.get_ctoken()
            return self.getdata(url, params, recursion_count + 1, max_recursion)
        else:
            return response.json()

    def getvinfo(self,params):
        body = {
            "ms_codes": "2019030100",
            "params": json.dumps(params),
            "system_info": "{\"os\":\"iku\",\"device\":\"iku\",\"ver\":\"9.2.9\",\"appPackageKey\":\"com.youku.iku\",\"appPackageId\":\"pcweb\"}"
        }
        data = self.getdata(f'{self.h5host}/h5/mtop.youku.columbus.gateway.new.execute/1.0/', body)
        okey = list(data['data'].keys())[0]
        i = data['data'][okey]['data']
        return i

    def getinfo(self,params):
        i = self.getvinfo(params)
        jdata=i['nodes'][0]['nodes'][3]
        info=i['data']['extra']['episodeTotal']
        if i['data']['extra']['showCategory'] in ['电影','游戏']:
            jdata = i['nodes'][0]['nodes'][4]
        return jdata,info

