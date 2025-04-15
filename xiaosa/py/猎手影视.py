# coding=utf-8
# !/usr/bin/python
# by嗷呜(finally)
import sys
import os
sys.path.append("..")
import re
import hashlib
import hmac
import random
import string
from Crypto.Util.Padding import unpad
from concurrent.futures import ThreadPoolExecutor
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5, AES
from base64 import b64encode, b64decode
import json
import time
from base.spider import Spider

class Spider(Spider):

    def getName(self):
        return "电影猎手"

    def init(self, extend=""):
        self.device = self.device_id()
        self.host = self.gethost()
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def action(self, action):
        pass

    def destroy(self):
        pass

    t = str(int(time.time()))

    def homeContent(self, filter):
        result = {}
        filters = {}
        classes = []
        bba = self.url()
        data = self.fetch(f"{self.host}/api/v1/app/config?pack={bba[0]}&signature={bba[1]}", headers=self.header()).text
        data1 = self.aes(data)
        dy = {"class":"类型","area":"地区","lang":"语言","year":"年份","letter":"字母","by":"排序","sort":"排序"}
        data1['data']['movie_screen']['sort'].pop(0)
        for item in data1['data']['movie_screen']['sort']:
            item['n'] = item.pop('name')
            item['v'] = item.pop('value')
        for item in data1['data']['movie_screen']['filter']:
            has_non_empty_field = False
            classes.append({"type_name": item["name"], "type_id": str(item["id"])})
            for key in dy:
                if key in item and item[key]:
                    has_non_empty_field = True
                    break
            if has_non_empty_field:
                filters[str(item["id"])] = []
                filters[str(item["id"])].append(
                    {"key": 'sort', "name": '排序', "value": data1['data']['movie_screen']['sort']})
                for dkey in item:
                    if dkey in dy and item[dkey]:
                        item[dkey].pop(0)
                        value_array = [
                            {"n": value.strip(), "v": value.strip()}
                            for value in item[dkey]
                            if value.strip() != ""
                        ]
                        filters[str(item["id"])].append(
                            {"key": dkey, "name": dy[dkey], "value": value_array}
                        )
        result["class"] = classes
        result["filters"] = filters
        return result

    def homeVideoContent(self):
        bba = self.url()
        url = f'{self.host}/api/v1/movie/index_recommend?pack={bba[0]}&signature={bba[1]}'
        data = self.fetch(url, headers=self.header()).json()
        videos = []
        for item in data['data']:
            if len(item['list']) > 0:
                for it in item['list']:
                    try:
                        videos.append(self.voides(it))
                    except Exception as e:
                        continue
        result = {"list": videos}
        return result

    def categoryContent(self, tid, pg, filter, extend):
        body = {"type_id": tid, "sort": extend.get("sort", "by_default"), "class": extend.get("class", "类型"),
                "area": extend.get("area", "地区"), "year": extend.get("year", "年份"), "page": str(pg),
                "pageSize": "21"}
        result = {}
        list = []
        bba = self.url(body)
        url = f"{self.host}/api/v1/movie/screen/list?pack={bba[0]}&signature={bba[1]}"
        data = self.fetch(url, headers=self.header()).json()['data']['list']
        for item in data:
            list.append(self.voides(item))
        result["list"] = list
        result["page"] = pg
        result["pagecount"] = 9999
        result["limit"] = 90
        result["total"] = 999999
        return result

    def detailContent(self, ids):
        body = {"id": ids[0]}
        bba = self.url(body)
        url = f'{self.host}/api/v1/movie/detail?pack={bba[0]}&signature={bba[1]}'
        data = self.fetch(url, headers=self.header()).json()['data']
        video = {'vod_name': data.get('name'),'type_name': data.get('type_name'),'vod_year': data.get('year'),'vod_area': data.get('area'),'vod_remarks': data.get('dynami'),'vod_content': data.get('content')}
        play = []
        names = []
        tasks = []
        for itt in data["play_from"]:
            name = itt["name"]
            a = []
            if len(itt["list"]) > 0:
                names.append(name)
                play.append(self.playeach(itt['list']))
            else:
                tasks.append({"movie_id": ids[0], "from_code": itt["code"]})
                names.append(name)
        if tasks:
            with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
                results = executor.map(self.playlist, tasks)
                for result in results:
                    if result:
                        play.append(result)
                    else:
                        play.append("")
        video["vod_play_from"] = "$$$".join(names)
        video["vod_play_url"] = "$$$".join(play)
        result = {"list": [video]}
        return result

    def searchContent(self, key, quick, pg=1):
        body = {"keyword": key, "sort": "", "type_id": "0", "page": str(pg), "pageSize": "10",
                "res_type": "by_movie_name"}
        bba = self.url(body)
        url = f"{self.host}/api/v1/movie/search?pack={bba[0]}&signature={bba[1]}"
        data = self.fetch(url, headers=self.header()).json()['data'].get('list')
        videos = []
        for it in data:
            try:
                videos.append(self.voides(it))
            except Exception as e:
                continue
        result = {"list": videos, "page": pg}
        return result

    def playerContent(self, flag, id, vipFlags):
        url = id
        if "m3u8" not in url and "mp4" not in url:
            try:
                add = id.split('|||')
                data = {"from_code": add[0], "play_url": add[1], "episode_id": add[2], "type": "play"}
                bba = self.url(data)
                data2 = self.fetch(f"{self.host}/api/v1/movie_addr/parse_url?pack={bba[0]}&signature={bba[1]}",
                                   headers=self.header()).json()['data']
                url = data2.get('play_url') or data2.get('download_url')
                try:
                    url1 = self.fetch(url, headers=self.header(), allow_redirects=False).headers['Location']
                    if url1 and "http" in url1:
                        url = url1
                except:
                    pass
            except Exception as e:
                pass
        if '.jpg' in url or '.jpeg' in url or '.png' in url:
            url = self.getProxyUrl() + "&url=" + b64encode(url.encode('utf-8')).decode('utf-8') + "&type=m3u8"
        result = {}
        result["parse"] = 0
        result["url"] = url
        result["header"] = {'user-agent': 'okhttp/4.9.2'}
        return result

    def localProxy(self, param):
        url = b64decode(param["url"]).decode('utf-8')
        durl = url[:url.rfind('/')]
        data = self.fetch(url, headers=self.header()).content.decode("utf-8")
        lines = data.strip().split('\n')
        for index, string in enumerate(lines):
            # if 'URI="' in string and 'http' not in string:
            #     lines[index] = index
            # 暂时预留，貌似用不到
            if '#EXT' not in string and 'http' not in string:
                lines[index] = durl + ('' if string.startswith('/') else '/') + string
        data = '\n'.join(lines)
        return [200, "application/vnd.apple.mpegur", data]

    def device_id(self):
        characters = string.ascii_lowercase + string.digits
        random_string = ''.join(random.choices(characters, k=32))
        return random_string

    def gethost(self):
        headers = {
            'User-Agent': 'okhttp/4.9.2',
            'Connection': 'Keep-Alive',
        }
        response = self.fetch('https://app-site.ecoliving168.com/domain_v5.json', headers=headers).json()
        url = response['api_service'].replace('/api/', '')
        return url

    def header(self):
        headers = {
            'User-Agent': 'Android',
            'Accept': 'application/prs.55App.v2+json',
            'timestamp': self.t,
            'x-client-setting': '{"pure-mode":1}',
            'x-client-uuid': '{"device_id":' + self.device + '}, "type":1,"brand":"Redmi", "model":"M2012K10C", "system_version":30, "sdk_version":"3.1.0.7"}',
            'x-client-version': '3096 '
        }
        return headers

    def url(self, id=None):
        if not id:
            id = {}
        id["timestamp"] = self.t
        public_key = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA02F/kPg5A2NX4qZ5JSns+bjhVMCC6JbTiTKpbgNgiXU+Kkorg6Dj76gS68gB8llhbUKCXjIdygnHPrxVHWfzmzisq9P9awmXBkCk74Skglx2LKHa/mNz9ivg6YzQ5pQFUEWS0DfomGBXVtqvBlOXMCRxp69oWaMsnfjnBV+0J7vHbXzUIkqBLdXSNfM9Ag5qdRDrJC3CqB65EJ3ARWVzZTTcXSdMW9i3qzEZPawPNPe5yPYbMZIoXLcrqvEZnRK1oak67/ihf7iwPJqdc+68ZYEmmdqwunOvRdjq89fQMVelmqcRD9RYe08v+xDxG9Co9z7hcXGTsUquMxkh29uNawIDAQAB'
        encrypted_text = json.dumps(id)
        public_key = RSA.import_key(b64decode(public_key))
        cipher = PKCS1_v1_5.new(public_key)
        encrypted_message = cipher.encrypt(encrypted_text.encode('utf-8'))
        encrypted_message_base64 = b64encode(encrypted_message).decode('utf-8')
        result = encrypted_message_base64.replace('+', '-').replace('/', '_').replace('=', '')
        key = '635a580fcb5dc6e60caa39c31a7bde48'
        sign = hmac.new(key.encode(), result.encode(), hashlib.md5).hexdigest()
        return result, sign

    def playlist(self, body):
        try:
            bba = self.url(body)
            url = f'{self.host}/api/v1/movie_addr/list?pack={bba[0]}&signature={bba[1]}'
            data = self.fetch(url, headers=self.header()).json()['data']
            return self.playeach(data)
        except Exception:
            return []

    def playeach(self,data):
        play_urls = []
        for it in data:
            if re.search(r"mp4|m3u8", it["play_url"]):
                play_urls.append(f"{it['episode_name']}${it['play_url']}")
            else:
                play_urls.append(
                    f"{it['episode_name']}${it['from_code']}|||{it['play_url']}|||{it['episode_id']}"
                )
        return '#'.join(play_urls)
    
    def voides(self, item):
        if item['name'] or item['title']:
            voide = {
                "vod_id": item.get('id') or item.get('click'),
                'vod_name': item.get('name') or item.get('title'),
                'vod_pic': item.get('cover') or item.get('image'),
                'vod_year': item.get('year') or item.get('label'),
                'vod_remarks': item.get('dynamic') or item.get('sub_title')
            }
            return voide

    def aes(self, text):
        text = text.replace('-', '+').replace('_', '/') + '=='
        key = b"e6d5de5fcc51f53d"
        iv = b"2f13eef7dfc6c613"
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(b64decode(text)), AES.block_size).decode("utf-8")
        return json.loads(pt)
