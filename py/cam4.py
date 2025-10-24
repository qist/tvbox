# -*- coding: utf-8 -*-
import json
import time
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        return "Cam4直播"

    def init(self, extend=""):
        self.base = "https://zh.cam4.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        return self

    def homeContent(self, filter):
        classes = [
            {"type_id": "all", "type_name": "全部"},
            {"type_id": "female", "type_name": "女性"},
            {"type_id": "male", "type_name": "男性"},
            {"type_id": "couples", "type_name": "情侣"},
            {"type_id": "shemale", "type_name": "变性"},
        ]
        return {"class": classes}

    def categoryContent(self, tid, pg, filter, extend):
        if not pg:
            pg = 1
        params = f"?directoryJson=true&online=true&url=true&page={pg}"
        if tid == "female":
            params += "&gender=female"
        elif tid == "male":
            params += "&gender=male"
        elif tid == "couples":
            params += "&broadcastType=male_female_group"
        elif tid == "shemale":
            params += "&gender=shemale"

        url = f"{self.base}/directoryCams{params}"
        rsp = self.fetch(url, headers=self.headers)
        data = rsp.text
        try:
            jRoot = json.loads(data)
        except:
            return {"list": []}

        videos = []
        for u in jRoot.get("users", []):
            title = f"{u.get('username')} ({u.get('countryCode', '')})"
            if "age" in u:
                title += f" - {u['age']}岁"
            if "resolution" in u:
                res = u["resolution"].split(":")[-1]
                title += f" [HD:{res}]"
            video = {
                "vod_id": u.get("hlsPreviewUrl"),
                "vod_name": title,
                "vod_pic": u.get("snapshotImageLink", ""),
                "vod_remarks": u.get("statusMessage", ""),
            }
            videos.append(video)

        result = {
            "list": videos,
            "page": int(pg),
            "pagecount": 9999,
            "limit": 90,
            "total": len(videos)
        }
        return result

    def detailContent(self, ids):
        id = ids[0]
        vod = {
            "vod_id": id,
            "vod_name": "Cam4直播",
            "vod_pic": "",
            "vod_play_from": "Cam4",
            "vod_play_url": f"直播源${id}",
        }
        return {"list": [vod]}

    def playerContent(self, flag, id, vipFlags):
        play_url = id
        return {
            "parse": 0,
            "playUrl": "",
            "url": play_url,
            "header": self.headers
        }

    def searchContent(self, key, quick, pg="1"):
        url = f"{self.base}/directoryCams?directoryJson=true&online=true&url=true&showTag={key}&page={pg}"
        rsp = self.fetch(url, headers=self.headers)
        data = rsp.text
        try:
            jRoot = json.loads(data)
        except:
            return {"list": []}

        videos = []
        for u in jRoot.get("users", []):
            title = f"{u.get('username')} ({u.get('countryCode', '')})"
            video = {
                "vod_id": u.get("hlsPreviewUrl"),
                "vod_name": title,
                "vod_pic": u.get("snapshotImageLink", ""),
                "vod_remarks": u.get("statusMessage", ""),
            }
            videos.append(video)
        return {"list": videos}

    def isVideoFormat(self, url):
        return ".m3u8" in url

    def manualVideoCheck(self):
        return True