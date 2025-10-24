# -*- coding: utf-8 -*-
import re, json, requests
from base.spider import Spider
class Spider(Spider):
    def getName(self): return "Chaturbate 直播"
    def init(self, extend=""):
        self.base, self.headers = "https://chaturbate.com", {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        return self
    def homeContent(self, filter):
        return {"class": [{"type_id": "f", "type_name": "女性"}, {"type_id": "m", "type_name": "男性"}, {"type_id": "c", "type_name": "情侣"}]}
    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg) if pg else 0
        gender = {"f": "f", "m": "m", "c": "c"}.get(tid, "")
        url = f"{self.base}/api/ts/roomlist/room-list/?enable_recommendations=false&genders={gender}&limit=90&offset={pg*90}"
        data = self.fetch(url, headers=self.headers).json()
        total = data.get("total_count", 0)
        videos = [
            {"vod_id": r["username"], "vod_pic": r.get("img", ""), "vod_remarks": "",
             "vod_name": f'{r["username"]}{" (" + str(r["display_age"]) + ")" if r.get("display_age") else ""}'}
            for r in data.get("rooms", [])
        ]
        return {"list": videos, "page": pg + 1, "pagecount": (total + 89) // 90, "limit": 90, "total": total}
    def detailContent(self, ids):
        room_slug = ids[0]
        return {"list": [{"vod_id": room_slug, "vod_name": f"Chaturbate - {room_slug}", "vod_pic": "", 
                "vod_play_from": "老僧酿酒、名妓读经", "vod_play_url": f"书生玩剣、将军作文${room_slug}"}]}
    def playerContent(self, flag, id, vipFlags):
        url, data, headers = "https://chaturbate.com/get_edge_hls_url_ajax/", {"room_slug": id}, {"X-Requested-With": "XMLHttpRequest"}
        try:
            play_url = requests.post(url, data=data, headers=headers).json().get("url", id)
        except (requests.RequestException, json.JSONDecodeError):
            play_url = id
        return {"parse": 0, "playUrl": "", "url": play_url, "header": headers}

    def searchContent(self, key, quick, pg="0"):
        pg = int(pg) if pg else 0
        url_api = f"{self.base}/api/ts/roomlist/room-list/?enable_recommendations=false&limit=90&offset={pg*90}&query={key}"
        data = self.fetch(url_api, headers=self.headers).json()
        videos = [
            {"vod_id": r["username"], "vod_pic": r.get("img", ""), "vod_remarks": "",
             "vod_name": f'{r["username"]}{" (" + str(r["display_age"]) + ")" if r.get("display_age") else ""}'}
            for r in data.get("rooms", [])
        ]
        return {"list": videos}

    def isVideoFormat(self, url): return ".m3u8" in url
    def manualVideoCheck(self): return True