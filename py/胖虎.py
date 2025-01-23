# coding=utf-8
# !/usr/bin/python
import re
import sys

sys.path.append("..")
from base.spider import Spider
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode
import os
from lxml import etree
import json
import time
import base64


class Spider(Spider):

    def init(self, extend=""):
        pass

    def destroy(self):
        pass

    def aes(self, operation, text):
        key = "ihIwTbt2YAe9TGea".encode("utf-8")
        iv = key

        if operation == "encrypt":
            cipher = AES.new(key, AES.MODE_CBC, iv)
            ct_bytes = cipher.encrypt(pad(text.encode("utf-8"), AES.block_size))
            ct = b64encode(ct_bytes).decode("utf-8")
            return ct
        elif operation == "decrypt":
            cipher = AES.new(key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(b64decode(text)), AES.block_size)
            return pt.decode("utf-8")

    host = "http://sm.physkan.top:3389"
    t = str(int(time.time()))

    def homeContent(self, filter):
        self.header = {
            "User-Agent": "okhttp/3.14.9",
            "app-version-code": "402",
            "app-ui-mode": "light",
            "app-user-device-id": "25f869d32598d3d3089a929453dff0bb7",
            "app-api-verify-time": self.t,
            "app-api-verify-sign": self.aes("encrypt", self.t),
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        }
        data = self.fetch(
            "{0}/api.php/getappapi.index/initV119".format(self.host),
            headers=self.header,
        ).content.decode("utf-8")
        data1 = json.loads(data)["data"]

        data2 = self.aes("decrypt", data1)
        dy = {
            "class": "类型",
            "area": "地区",
            "lang": "语言",
            "year": "年份",
            "letter": "字母",
            "by": "排序",
            "sort": "排序",
        }

        filter = {}
        classes = []
        json_data = json.loads(data2)["type_list"]
        self.homedata = json.loads(data2)["banner_list"]

        for item in json_data:
            if item["type_name"] == "全部":
                continue

            has_non_empty_field = False
            jsontype_extend = json.loads(item["type_extend"])
            jsontype_extend["sort"] = "最新,最热,最赞"

            classes.append({"type_name": item["type_name"], "type_id": item["type_id"]})

            for key in dy:
                if key in jsontype_extend and jsontype_extend[key].strip() != "":
                    has_non_empty_field = True
                    break

            if has_non_empty_field:
                filter[str(item["type_id"])] = []

                for dkey in jsontype_extend:
                    if dkey in dy and jsontype_extend[dkey].strip() != "":
                        values = jsontype_extend[dkey].split(",")
                        value_array = [
                            {"n": value.strip(), "v": value.strip()}
                            for value in values
                            if value.strip() != ""
                        ]

                        filter[str(item["type_id"])].append(
                            {"key": dkey, "name": dy[dkey], "value": value_array}
                        )
        result = {}
        result["class"] = classes
        result["filter"] = filter
        return result

    def homeVideoContent(self):
        result = {"list": self.homedata}
        return result

    def categoryContent(self, tid, pg, filter, extend):
        body = f"area={extend.get('area', '全部')}&year={extend.get('year', '全部')}&type_id={tid}&page={pg}&sort={extend.get('sort', '最新')}&lang={extend.get('lang', '全部')}&class={extend.get('class', '全部')}"
        result = {}
        url = "{0}/api.php/getappapi.index/typeFilterVodList".format(self.host)
        data = self.post(url, headers=self.header, data=body).content.decode("utf-8")
        data1 = json.loads(data)["data"]
        data2 = self.aes("decrypt", data1)
        result["list"] = json.loads(data2)["recommend_list"]
        result["page"] = pg
        result["pagecount"] = 9999
        result["limit"] = 90
        result["total"] = 999999
        return result

    def detailContent(self, ids):
        body = f"vod_id={ids[0]}"
        url = "{0}/api.php/getappapi.index/vodDetail".format(self.host)
        data = self.post(url, headers=self.header, data=body).content.decode("utf-8")
        data1 = json.loads(data)["data"]
        data2 = json.loads(self.aes("decrypt", data1))
        vod = data2["vod"]
        play = []
        names = []
        for itt in data2["vod_play_list"]:
            a = []
            names.append(itt["player_info"]["show"])
            parse = itt["player_info"]["parse"]
            for it in itt["urls"]:
                if re.search(r"mp4|m3u8", it["url"]):
                    a.append(f"{it['name']}${it['url']}")
                elif re.search(r"www.yemu.xyz", it["parse_api_url"]):
                    a.append(f"{it['name']}${it['parse_api_url']}")
                else:
                    a.append(
                        f"{it['name']}${'parse_api=' + parse + '&url=' + self.aes('encrypt', it['url']) + '&token=' + it['token']}"
                    )
            play.append("#".join(a))
        vod["vod_play_from"] = "$$$".join(names)
        vod["vod_play_url"] = "$$$".join(play)
        result = {"list": [vod]}
        return result

    def searchContent(self, key, quick, pg="1"):
        body = f"keywords={key}&type_id=0&page={pg}"
        url = "{0}/api.php/getappapi.index/searchList".format(self.host)
        data = self.post(url, headers=self.header, data=body).content.decode("utf-8")
        data1 = json.loads(data)["data"]
        data2 = self.aes("decrypt", data1)
        result = {"list": json.loads(data2)["search_list"]}
        return result

    def playerContent(self, flag, id, vipFlags):
        def edu(str):
            def replacer(match):
                from urllib.parse import quote_plus
                return match.group(1) + quote_plus(match.group(2)) + match.group(3)
            return re.sub(r"(url=)(.*?)(&token)", replacer, str)

        url = id
        parse = 0
        if "m3u8" not in url and "mp4" not in url:
            try:
                body = edu(url)
                data = self.post(
                    "{0}/api.php/getappapi.index/vodParse".format(self.host),
                    headers=self.header,
                    data=body
                ).content.decode("utf-8")
                data1 = json.loads(data)["data"]
                data2 = json.loads(self.aes("decrypt", data1))["json"]
                url = json.loads(data2)["url"]
            except:
                parse = 1
                if not url.startswith("https://www.yemu.xyz"):
                    url = "https://www.yemu.xyz/?url={0}".format(id)
        result = {}
        headers = self.header.copy()
        del headers["Content-type"]
        result["parse"] = parse
        result["url"] = url
        result["header"] = headers
        return result

    def localProxy(self, param):
        pass
