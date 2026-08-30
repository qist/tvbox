# coding=utf-8
# !/usr/bin/python

"""

内容均从互联网收集而来 仅供交流学习使用 严禁用于商业用途 请于24小时内删除

"""

from Crypto.Util.Padding import unpad
from Crypto.Util.Padding import pad
from urllib.parse import urlparse
from urllib.parse import unquote
from Crypto.Cipher import ARC4
from urllib.parse import quote
from base.spider import Spider
from Crypto.Cipher import AES
from datetime import datetime
from base64 import b64decode
import concurrent.futures
import urllib.request
import urllib.parse
import datetime
import binascii
import requests
import hashlib
import base64
import json
import time
import hmac
import sys
import re
import os

sys.path.append('..')

xurl = "https://www.wasu.cn"

headerx = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36'
          }

headerz = {
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'no-cache',
    'origin': xurl,
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': xurl,
    'sec-ch-ua': '"Microsoft Edge";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0',
           }

class Spider(Spider):

    def getName(self):
        return "精彩"

    def init(self, extend):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeVideoContent(self):
        pass

    def homeContent(self, filter):
        result = {}
        result = {"class": [{"type_id": "961", "type_name": "电影"},
                            {"type_id": "962", "type_name": "剧集"},
                            {"type_id": "963", "type_name": "少儿"},
                            {"type_id": "965", "type_name": "栏目"},
                            {"type_id": "966", "type_name": "新闻"}],
                  "list": [],
                  "filters": {"961": [{"key": "地区",
                                      "name": "地区",
                                      "value": [{"n": "全部", "v": ""},
                                                {"n": "内地", "v": "内地"},
                                                {"n": "港台", "v": "港台"},
                                                {"n": "欧美", "v": "欧美"},
                                                {"n": "日韩", "v": "日韩"},
                                                {"n": "泰国", "v": "泰国"},
                                                {"n": "其他", "v": "其他"}]},
                                      {"key": "类型",
                                      "name": "类型",
                                      "value": [{"n": "全部", "v": ""},
                                                {"n": "动作", "v": "动作"},
                                                {"n": "科幻", "v": "科幻"},
                                                {"n": "惊悚", "v": "惊悚"},
                                                {"n": "冒险", "v": "冒险"},
                                                {"n": "剧情", "v": "剧情"},
                                                {"n": "励志", "v": "励志"},
                                                {"n": "爱情", "v": "爱情"},
                                                {"n": "喜剧", "v": "喜剧"},
                                                {"n": "家庭", "v": "家庭"},
                                                {"n": "历史", "v": "历史"},
                                                {"n": "魔幻", "v": "魔幻"},
                                                {"n": "恐怖", "v": "恐怖"},
                                                {"n": "战争", "v": "战争"},
                                                {"n": "武侠", "v": "武侠"}]},
                                      {"key": "年代",
                                      "name": "年代",
                                      "value": [{"n": "全部", "v": ""},
                                                {"n": "2025", "v": "2025"},
                                                {"n": "2024", "v": "2024"},
                                                {"n": "2023", "v": "2023"},
                                                {"n": "2022", "v": "2022"},
                                                {"n": "2021", "v": "2021"},
                                                {"n": "2020", "v": "2020"},
                                                {"n": "2019", "v": "2019"},
                                                {"n": "2018", "v": "2018"},
                                                {"n": "2017", "v": "2017"},
                                                {"n": "2016", "v": "2016"},
                                                {"n": "2015", "v": "2015"},
                                                {"n": "2014", "v": "2014"},
                                                {"n": "2013", "v": "2013"},
                                                {"n": "2012", "v": "2012"},
                                                {"n": "2011", "v": "2011"},
                                                {"n": "2010", "v": "2010"}]}],
                              "962": [{"key": "地区",
                                      "name": "地区",
                                      "value": [{"n": "全部", "v": ""},
                                                {"n": "内地", "v": "内地"},
                                                {"n": "港台", "v": "港台"},
                                                {"n": "日韩", "v": "日韩"},
                                                {"n": "欧美", "v": "欧美"},
                                                {"n": "泰国", "v": "泰国"},
                                                {"n": "其他", "v": "其他"}]},
                                      {"key": "类型",
                                      "name": "类型",
                                      "value": [{"n": "全部", "v": ""},
                                                {"n": "都市", "v": "都市"},
                                                {"n": "爱情", "v": "爱情"},
                                                {"n": "战争", "v": "战争"},
                                                {"n": "家庭", "v": "家庭"},
                                                {"n": "悬疑", "v": "悬疑"},
                                                {"n": "古装", "v": "古装"},
                                                {"n": "短剧", "v": "短剧"},
                                                {"n": "谍战", "v": "谍战"},
                                                {"n": "喜剧", "v": "喜剧"},
                                                {"n": "农村", "v": "农村"},
                                                {"n": "刑侦", "v": "刑侦"},
                                                {"n": "武侠", "v": "武侠"},
                                                {"n": "历史", "v": "历史"}]},
                                      {"key": "年代",
                                      "name": "年代",
                                      "value": [{"n": "全部", "v": ""},
                                                {"n": "2025", "v": "2025"},
                                                {"n": "2024", "v": "2024"},
                                                {"n": "2023", "v": "2023"},
                                                {"n": "2022", "v": "2022"},
                                                {"n": "2021", "v": "2021"},
                                                {"n": "2020", "v": "2020"},
                                                {"n": "2019", "v": "2019"},
                                                {"n": "2018", "v": "2018"},
                                                {"n": "2017", "v": "2017"},
                                                {"n": "2016", "v": "2016"},
                                                {"n": "2015", "v": "2015"},
                                                {"n": "2014", "v": "2014"},
                                                {"n": "2013", "v": "2013"},
                                                {"n": "2012", "v": "2012"},
                                                {"n": "2011", "v": "2011"},
                                                {"n": "2010", "v": "2010"}]}],
                              "963": [{"key": "地区",
                                      "name": "地区",
                                      "value": [{"n": "全部", "v": ""},
                                                {"n": "内地", "v": "内地"},
                                                {"n": "日韩", "v": "日韩"},
                                                {"n": "欧美", "v": "欧美"},
                                                {"n": "港台", "v": "港台"},
                                                {"n": "其他", "v": "其他"}]},
                                      {"key": "类型",
                                      "name": "类型",
                                      "value": [{"n": "全部", "v": ""},
                                                {"n": "动作", "v": "动作"},
                                                {"n": "冒险", "v": "冒险"},
                                                {"n": "益智", "v": "益智"},
                                                {"n": "亲子", "v": "亲子"},
                                                {"n": "热血", "v": "热血"},
                                                {"n": "剧情", "v": "剧情"},
                                                {"n": "魔幻", "v": "魔幻"},
                                                {"n": "励志", "v": "励志"},
                                                {"n": "机战", "v": "机战"},
                                                {"n": "搞笑", "v": "搞笑"},
                                                {"n": "科幻", "v": "科幻"},
                                                {"n": "治愈", "v": "治愈"},
                                                {"n": "儿歌", "v": "儿歌"},
                                                {"n": "教育", "v": "教育"},
                                                {"n": "校园", "v": "校园"},
                                                {"n": "童话", "v": "童话"},
                                                {"n": "推理", "v": "推理"},
                                                {"n": "怀旧", "v": "怀旧"},
                                                {"n": "宠物", "v": "宠物"},
                                                {"n": "舞蹈", "v": "舞蹈"}]},
                                      {"key": "年代",
                                      "name": "年代",
                                      "value": [{"n": "全部", "v": ""},
                                                {"n": "2025", "v": "2025"},
                                                {"n": "2024", "v": "2024"},
                                                {"n": "2023", "v": "2023"},
                                                {"n": "2022", "v": "2022"},
                                                {"n": "2021", "v": "2021"},
                                                {"n": "2020", "v": "2020"},
                                                {"n": "2019", "v": "2019"},
                                                {"n": "2018", "v": "2018"},
                                                {"n": "2017", "v": "2017"},
                                                {"n": "2016", "v": "2016"},
                                                {"n": "2015", "v": "2015"},
                                                {"n": "2014", "v": "2014"},
                                                {"n": "2013", "v": "2013"},
                                                {"n": "2012", "v": "2012"},
                                                {"n": "2011", "v": "2011"},
                                                {"n": "2010", "v": "2010"}]}],
                              "965": [{"key": "地区",
                                      "name": "地区",
                                      "value": [{"n": "全部", "v": ""},
                                                {"n": "内地", "v": "内地"},
                                                {"n": "欧美", "v": "欧美"}]},
                                      {"key": "类型",
                                      "name": "类型",
                                      "value": [{"n": "全部", "v": ""},
                                                {"n": "文化", "v": "文化"},
                                                {"n": "纪实", "v": "纪实"},
                                                {"n": "访谈", "v": "访谈"},
                                                {"n": "历史", "v": "历史"},
                                                {"n": "美食", "v": "美食"},
                                                {"n": "旅游", "v": "旅游"},
                                                {"n": "时尚", "v": "时尚"},
                                                {"n": "情感", "v": "情感"},
                                                {"n": "生活", "v": "生活"},
                                                {"n": "真人秀", "v": "真人秀"}]},
                                      {"key": "年代",
                                      "name": "年代",
                                      "value": [{"n": "全部", "v": ""},
                                                {"n": "2025", "v": "2025"},
                                                {"n": "2024", "v": "2024"},
                                                {"n": "2023", "v": "2023"},
                                                {"n": "2022", "v": "2022"},
                                                {"n": "2021", "v": "2021"},
                                                {"n": "2020", "v": "2020"},
                                                {"n": "2019", "v": "2019"},
                                                {"n": "2018", "v": "2018"},
                                                {"n": "2017", "v": "2017"},
                                                {"n": "2016", "v": "2016"},
                                                {"n": "2015", "v": "2015"},
                                                {"n": "2014", "v": "2014"},
                                                {"n": "2013", "v": "2013"},
                                                {"n": "2012", "v": "2012"},
                                                {"n": "2011", "v": "2011"},
                                                {"n": "2010", "v": "2010"}]}],
                              "966": [{"key": "类型",
                                      "name": "类型",
                                      "value": [{"n": "全部", "v": ""},
                                                {"n": "国内视野", "v": "国内视野"},
                                                {"n": "国际纵览", "v": "国际纵览"},
                                                {"n": "军事话题", "v": "军事话题"},
                                                {"n": "社会百态", "v": "社会百态"},
                                                {"n": "央视频", "v": "央视频"}]}]}}
        return result

    def generate_x_sign(self, secret_b64):
        secret_key = self.decode_secret_key(secret_b64)
        data = self.get_data_string()
        signature = self.compute_signature(secret_key, data)
        x_sign = self.encode_signature(signature)
        return x_sign

    def decode_secret_key(self, secret_b64):
        return base64.b64decode(secret_b64)

    def get_data_string(self):
        return "{}"

    def compute_signature(self, secret_key, data):
        return hmac.new(secret_key, data.encode('utf-8'), hashlib.sha256).digest()

    def encode_signature(self, signature):
        return base64.b64encode(signature).decode('utf-8')

    def get_current_app_key(self, xurl, headerx):
        resp = self.fetch_index_page(xurl, headerx)
        js_path = self.extract_js_path(resp.text)
        js_url = f"{xurl}{js_path}"
        js_content = self.fetch_js_content(js_url, headerx)
        target_key_b64 = self.extract_target_key(js_content)
        return target_key_b64

    def fetch_index_page(self, xurl, headerx):
        resp = requests.get(xurl, headers=headerx)
        resp.raise_for_status()
        return resp

    def extract_js_path(self, html_content):
        js_path_pattern = r'src="(/[\d\.]+/assets/js/index-[\w\.-]+\.js)"'
        match = re.search(js_path_pattern, html_content)
        return match.group(1)

    def fetch_js_content(self, js_url, headerx):
        js_resp = requests.get(js_url, headers=headerx)
        js_resp.raise_for_status()
        return js_resp.text

    def extract_target_key(self, js_content):
        key_pattern = r'const \w+="([^"]+)",\w+="([^"]+)",\w+="([^"]+)";'
        key_match = re.search(key_pattern, js_content)
        return key_match.group(2)

    def get_headers(self, sign1, xurl):
        return {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'launchchannel': 'web_channel',
            'origin': xurl,
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': xurl,
            'sec-ch-ua': '"Microsoft Edge";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'siteid': '1000101',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0',
            'x-sign': sign1,
                 }

    def categoryContent(self, cid, pg, filter, ext):
        secret_b64 = self.get_current_app_key(xurl, headerx)
        sign1 = self.generate_x_sign(secret_b64)
        page = self.get_page_number(pg)
        NdType, DqType, LxType = self.extract_filter_types(ext)
        headers = self.get_headers(sign1, xurl)
        params = self.build_category_params(cid, page, NdType, DqType, LxType)
        data = self.fetch_category_data(params, headers)
        videos = self.parse_category_videos(data)
        return self.build_category_result(videos, pg)

    def get_page_number(self, pg):
        return int(pg) if pg else 1

    def extract_filter_types(self, ext):
        NdType = ext.get('年代', '全部')
        DqType = ext.get('地区', '全部')
        LxType = ext.get('类型', '全部')
        return NdType, DqType, LxType

    def build_category_params(self, cid, page, NdType, DqType, LxType):
        return {'functionName': 'getNewsSearchedByCondition','nodeId': cid,'nodeTag': LxType,'yearTag': NdType,'countryTag': DqType,'orderType': '0','pageSize': '40','page': page,'keyword': '','siteId': '1000101',}

    def fetch_category_data(self, params, headers):
        detail = requests.get('https://ups.5g.wasu.tv/rmp-user-suggest/1000101/hzhs/searchServlet', params=params,headers=headers)
        detail.encoding = "utf-8"
        return detail.json()

    def parse_category_videos(self, data):
        videos = []
        for vod in data['data']:
            videos.append(self.parse_category_video(vod))
        return videos

    def parse_category_video(self, vod):
        return {"vod_id": f"{vod['nodeId']}@{vod['newsId']}","vod_name": vod['title'],"vod_pic": vod['hPic'],"vod_year": vod.get('pubTime', '暂无日期'),"vod_remarks": vod.get('episodeDesc', '暂无备注')}

    def build_category_result(self, videos, pg):
        result = {'list': videos}
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        did = ids[0]
        secret_b64 = self.get_current_app_key(xurl, headerx)
        sign1 = self.generate_x_sign(secret_b64)
        fenge = did.split("@")
        headers = self.get_headers(sign1, xurl)
        params = self.build_detail_params(fenge)
        data = self.fetch_detail_data(params, headers)
        content = self.build_content(data)
        director = self.extract_detail_field(data, 'director')
        actor = self.extract_detail_field(data, 'actor')
        remarks = self.extract_detail_field(data, 'episodeDesc')
        year = self.extract_detail_field(data, 'pubTime')
        area = self.extract_detail_field(data, 'countryTag')
        title = self.extract_detail_field(data, 'title') or (data.get('data', {}).get('newsTitle') or '')
        bofang = self.build_play_url(data)
        videos = [self.build_video_data(did, title, director, actor, remarks, year, area, content, bofang)]
        return self.build_result(videos)

    def build_detail_params(self, fenge):
        return {'siteId': '1000101', 'functionName': 'getCurrentNews', 'nodeId': fenge[0], 'newsId': fenge[1],'platform': 'web',}

    def fetch_detail_data(self, params, headers):
        detail = requests.get('https://mcspapp.5g.wasu.tv/bvradio_app/hzhs/newsServlet', params=params, headers=headers)
        detail.encoding = "utf-8"
        return detail.json()

    def build_content(self, data):
        return '介绍剧情📢' + data.get('data', {}).get('newsAbstract', '')

    def extract_detail_field(self, data, field_name):
        return data.get('data', {}).get(field_name, '')

    def build_play_url(self, data):
        bofang = ''
        for vod in data['data']['vodList']:
            name = vod['title']
            if len(vod['fileList']) > 1:
                id = vod['fileList'][1]['playUrl']
            else:
                id = vod['fileList'][0]['playUrl']
            bofang += name + '$' + id + '#'
        return bofang[:-1]

    def build_video_data(self, did, title, director, actor, remarks, year, area, content, bofang):
        return {"vod_id": did, "vod_name": title, "vod_director": director, "vod_actor": actor, "vod_remarks": remarks, "vod_year": year, "vod_area": area, "vod_content": content, "vod_play_from": "华数专线", "vod_play_url": bofang}

    def build_result(self, videos):
        result = {}
        result['list'] = videos
        return result

    def get_x_sign_for_post(self, secret_b64, playUrl):
        secret_key = self.decode_secret_key(secret_b64)
        payload_dict = self.build_payload_dict(playUrl)
        data_string = self.serialize_payload(payload_dict)
        signature = self.compute_hmac_signature(secret_key, data_string)
        x_sign = self.encode_signature(signature)
        return x_sign

    def decode_secret_key(self, secret_b64):
        return base64.b64decode(secret_b64)

    def build_payload_dict(self, playUrl):
        return {"playUrl": playUrl, "platform": "web"}

    def serialize_payload(self, payload_dict):
        return json.dumps(payload_dict, separators=(',', ':'), ensure_ascii=False)

    def compute_hmac_signature(self, secret_key, data_string):
        return hmac.new(secret_key, data_string.encode('utf-8'), hashlib.sha256).digest()

    def encode_signature(self, signature):
        return base64.b64encode(signature).decode('utf-8')

    def playerContent(self, flag, id, vipFlags):
        secret_b64 = self.get_current_app_key(xurl, headerx)
        id = self.normalize_play_url(id)
        sign2 = self.get_x_sign_for_post(secret_b64, id)
        headers = self.get_headers(sign2, xurl)
        json_data = self.build_request_json(id)
        result = self.post_play_url_request(headers, json_data)
        play_url = result['data']['playUrl']
        return self.build_player_result(play_url)

    def normalize_play_url(self, id):
        return id.replace('.mp4', '/playlist.m3u8')

    def build_request_json(self, playUrl):
        return {'playUrl': playUrl, 'platform': 'web', }

    def post_play_url_request(self, headers, json_data):
        response = requests.post('https://mcspapp.5g.wasu.tv/thirdApiFile/file/getPlayUrl', headers=headers, json=json_data)
        return response.json()

    def build_player_result(self, play_url):
        result = {}
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = play_url
        result["header"] = headerz
        return result

    def searchContentPage(self, key, quick, pg):
        page = self.get_page_number(pg)
        secret_b64 = self.get_current_app_key(xurl, headerx)
        sign1 = self.generate_x_sign(secret_b64)
        headers = self.get_headers(sign1, xurl)
        params = self.build_search_params(key, page)
        data = self.fetch_search_data(params, headers)
        videos = self.parse_search_videos(data)
        return self.build_search_result(videos, pg)

    def get_page_number(self, pg):
        return int(pg) if pg else 1

    def build_search_params(self, key, page):
        return {'functionName': 'getNewsSearched', 'searchNewsType': '3,4,5', 'keyword': key, 'pageSize': 10, 'page': page, 'siteId': 1000101}

    def fetch_search_data(self, params, headers):
        detail = requests.get("https://ups.5g.wasu.tv/rmp-user-suggest/1000101/hzhs/searchServlet", params=params, headers=headers)
        detail.encoding = "utf-8"
        return detail.json()

    def parse_search_videos(self, data):
        videos = []
        for vod in data['data']:
            videos.append(self.parse_search_video(vod))
        return videos

    def parse_search_video(self, vod):
        return {"vod_id": f"{vod['nodeId']}@{vod['newsId']}", "vod_name": vod['title'], "vod_pic": vod['hPic'], "vod_year": vod.get('pubTime', '暂无日期'), "vod_remarks": vod.get('episodeDesc', '暂无备注')}

    def build_search_result(self, videos, pg):
        result = {'list': videos}
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def searchContent(self, key, quick, pg="1"):
        return self.searchContentPage(key, quick, '1')

    def localProxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        elif params['type'] == "media":
            return self.proxyMedia(params)
        elif params['type'] == "ts":
            return self.proxyTs(params)
        return None










