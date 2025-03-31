# -*- coding: utf-8 -*-
# by @嗷呜
import sys
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):
    def getName(self):
        return "mp"

    def init(self, extend=""):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    host = 'https://g.c494.com'

    header = {
        'User-Agent': 'Dart/2.10 (dart:io)',
        'platform_version': 'RP1A.200720.011',
        'version': '2.2.3',
        'copyright': 'xiaogui',
        'platform': 'android',
        'client_name': '576O5p+P5b2x6KeG',
    }

    def homeContent(self, filter):
        data = self.fetch(f'{self.host}/api.php/app/nav?token=', headers=self.header).json()
        dy = {"class": "类型", "area": "地区", "lang": "语言", "year": "年份", "letter": "字母", "by": "排序",
              "sort": "排序"}
        filters = {}
        classes = []
        json_data = data["list"]
        for item in json_data:
            has_non_empty_field = False
            jsontype_extend = item["type_extend"]
            classes.append({"type_name": item["type_name"], "type_id": str(item["type_id"])})
            for key in dy:
                if key in jsontype_extend and jsontype_extend[key].strip() != "":
                    has_non_empty_field = True
                    break
            if has_non_empty_field:
                filters[str(item["type_id"])] = []
                for dkey in jsontype_extend:
                    if dkey in dy and jsontype_extend[dkey].strip() != "":
                        values = jsontype_extend[dkey].split(",")
                        value_array = [{"n": value.strip(), "v": value.strip()} for value in values if
                                       value.strip() != ""]
                        filters[str(item["type_id"])].append({"key": dkey, "name": dy[dkey], "value": value_array})
        result = {}
        result["class"] = classes
        result["filters"] = filters
        return result

    def homeVideoContent(self):
        rsp = self.fetch(f"{self.host}/api.php/app/index_video?token=", headers=self.header)
        root = rsp.json()['list']
        videos = [item for vodd in root for item in vodd['vlist']]
        return {'list': videos}

    def categoryContent(self, tid, pg, filter, extend):
        parms = {"pg": pg, "tid": tid, "class": extend.get("class", ""), "area": extend.get("area", ""),
                 "lang": extend.get("lang", ""), "year": extend.get("year", ""), "token": ""}
        data = self.fetch(f'{self.host}/api.php/app/video', params=parms, headers=self.header).json()
        return data

    def detailContent(self, ids):
        parms = {"id": ids[0], "token": ""}
        data = self.fetch(f'{self.host}/api.php/app/video_detail', params=parms, headers=self.header).json()
        vod = data['data']
        vod.pop('pause_advert_list', None)
        vod.pop('init_advert_list', None)
        vod.pop('vod_url_with_player', None)
        return {"list": [vod]}

    def searchContent(self, key, quick, pg='1'):
        parms = {'pg': pg, 'text': key, 'token': ''}
        data = self.fetch(f'{self.host}/api.php/app/search', params=parms, headers=self.header).json()
        return data

    def playerContent(self, flag, id, vipFlags):
        return {"parse": 0, "url": id, "header": {'User-Agent': 'User-Agent: Lavf/58.12.100'}}

    def localProxy(self, param):
        pass
