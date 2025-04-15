# -*- coding: utf-8 -*-
# by @嗷呜
import sys
sys.path.append('..')
from base.spider import Spider

class Spider(Spider):

    def init(self, extend=""):
        '''
        example:
        {
            "key": "py_appV2",
            "name": "xxx",
            "type": 3,
            "searchable": 1,
            "quickSearch": 1,
            "filterable": 1,
            "api": "./py/APPV2.py",
            "ext": "http://cmsyt.lyyytv.cn"
        }
        
        '''
        self.host=extend
        pass

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    headers = {
        'User-Agent': 'okhttp/4.12.0',
    }

    def homeContent(self, filter):
        data = self.fetch(f"{self.host}//api.php/app/nav?token=",headers=self.headers).json()
        keys = ["class", "area", "lang", "year", "letter", "by", "sort"]
        filters = {}
        classes = []
        for item in data['list']:
            has_non_empty_field = False
            jsontype_extend = item["type_extend"]
            classes.append({"type_name": item["type_name"], "type_id": item["type_id"]})
            for key in keys:
                if key in jsontype_extend and jsontype_extend[key].strip() != "":
                    has_non_empty_field = True
                    break
            if has_non_empty_field:
                filters[str(item["type_id"])] = []
            for dkey in jsontype_extend:
                if dkey in keys and jsontype_extend[dkey].strip() != "":
                    values = jsontype_extend[dkey].split(",")
                    value_array = [{"n": value.strip(), "v": value.strip()} for value in values if
                                   value.strip() != ""]
                    filters[str(item["type_id"])].append({"key": dkey, "name": dkey, "value": value_array})
        result = {}
        result["class"] = classes
        result["filters"] = filters
        return result

    def homeVideoContent(self):
        data=self.fetch(f"{self.host}/api.php/app/index_video?token=",headers=self.headers).json()
        videos=[]
        for item in data['list']:videos.extend(item['vlist'])
        return {'list':videos}

    def categoryContent(self, tid, pg, filter, extend):
        params = {'tid':tid,'class':extend.get('class',''),'area':extend.get('area',''),'lang':extend.get('lang',''),'year':extend.get('year',''),'limit':'18','pg':pg}
        data=self.fetch(f"{self.host}/api.php/app/video",params=params,headers=self.headers).json()
        return data

    def detailContent(self, ids):
        data=self.fetch(f"{self.host}/api.php/app/video_detail?id={ids[0]}",headers=self.headers).json()
        return  {'list':[data['data']]}

    def searchContent(self, key, quick, pg="1"):
        data=self.fetch(f"{self.host}/api.php/app/search?text={key}&pg={pg}",headers=self.headers).json()
        videos=data['list']
        for item in data['list']:
            item.pop('type', None)
        return {'list':videos,'page':pg}

    def playerContent(self, flag, id, vipFlags):
        return  {'jx':1,'playUrl':'','parse': 1, 'url': id, 'header': self.headers}

    def localProxy(self, param):
        pass


