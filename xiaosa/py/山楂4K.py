# coding: utf-8
# 山楂4K（43.248.128.122:578）· TVBox / FongMi Python 站源
# 协议：设备登录拿 JWT → /api/v1/security/challenge → init 换 session_id，
#       之后带 Bearer + X-Session-Id 调业务接口；播放走 ticket → parse_api。
import json
import os
import time
import urllib.parse
import urllib.request

try:
    from base.spider import Spider as BaseSpider
except Exception:
    class BaseSpider(object):
        pass

BASE = "http://43.248.128.122:578"
UA = "Mozilla/5.0 (Linux/Android 12) okhttp/3.12.1"
USER, PASS = "sukeke", "sukeke.1"
DID = "de94cd65-a825-4972-adf9-7dbece13e9f1"
TYPES = [("1", "电影"), ("2", "连续剧"), ("3", "综艺"), ("4", "动漫"),
         ("20", "短剧"), ("21", "少儿"), ("22", "漫剧"), ("23", "纪录片")]
PAGE_SIZE = 20


def _s(v):
    return "" if v is None else str(v).strip()


class Spider(BaseSpider):
    _sess = {"jwt": "", "sid": "", "at": 0.0}

    def getName(self):
        return "山楂4K"

    def getDependence(self):
        return []

    def setExtendInfo(self, extend):
        pass

    def init(self, extend=""):
        self.host = BASE
        try:
            if isinstance(extend, str) and extend.strip().startswith("{"):
                cfg = json.loads(str(extend))
                if cfg.get("host"):
                    self.host = str(cfg["host"]).rstrip("/")
        except Exception:
            pass

    # ---------------------------------------------------------------- HTTP
    def _req(self, method, path, body=None, hdr=None, timeout=20):
        h = {"User-Agent": UA, "Referer": "https://www.google.com/", "Accept-Encoding": "identity"}
        if hdr:
            h.update(hdr)
        data = None
        if body is not None:
            data = body.encode("utf-8")
            h["Content-Type"] = "application/json"
        req = urllib.request.Request(self.host + path, data=data, headers=h, method=method)
        for _ in range(2):
            try:
                return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")
            except Exception:
                time.sleep(0.5)
        return ""

    def _json(self, method, path, body=None, hdr=None):
        txt = self._req(method, path, body, hdr)
        try:
            return json.loads(txt)
        except Exception:
            return {}

    # ---------------------------------------------------------------- 会话
    def _login(self):
        st = Spider._sess
        if st["sid"] and time.time() - st["at"] < 480:
            return True
        r = self._json("POST", "/api/v1/user/login",
                       json.dumps({"Username": USER, "Password": PASS, "device_id": DID}))
        tok = (r.get("data") or {}).get("token") or ""
        if not tok:
            return False
        ch = self._json("GET", "/api/v1/security/challenge", None, {"Authorization": "Bearer " + tok})
        d = ch.get("data") or {}
        if not d.get("challenge"):
            return False
        body = {
            "challenge": d.get("challenge", ""), "challenge_id": d.get("challenge_id", ""),
            "device_id": DID, "token": tok, "client_token": "", "timestamp": int(time.time()),
            "nonce": os.urandom(16).hex(), "username": USER, "password": PASS,
            "sign": "s", "signature": "s", "app_id": "1", "app_key": "1", "app_version": "1.0",
            "version": "1", "platform": "android", "device": "android", "version_code": 1,
            "uid": "1", "source_id": "1", "site_id": "1", "type": "1",
        }
        init = self._json("POST", "/api/v1/security/init", json.dumps(body))
        sid = (init.get("data") or {}).get("session_id") or ""
        if not sid:
            return False
        st["jwt"], st["sid"], st["at"] = tok, sid, time.time()
        return True

    def _api(self, path, query=""):
        for attempt in range(2):
            if not self._login():
                return {}
            h = {"Authorization": "Bearer " + Spider._sess["jwt"],
                 "X-Session-Id": Spider._sess["sid"]}
            j = self._json("GET", path + (("?" + query) if query else ""), None, h)
            if j.get("code") == 1:
                return j
            Spider._sess["sid"] = ""
        return {}

    # ---------------------------------------------------------------- 数据映射
    def _vod(self, v):
        vid = _s(v.get("vod_id"))
        name = _s(v.get("vod_name"))
        if not vid or not name:
            return None
        pic = _s(v.get("vod_pic")) or _s(v.get("vod_pic_slide"))
        if pic.startswith("//"):
            pic = "https:" + pic
        remarks = _s(v.get("vod_remarks")) or _s(v.get("vod_year"))
        return {"vod_id": vid, "vod_name": name, "vod_pic": pic, "vod_remarks": remarks}

    def _list(self, arr):
        out = []
        for v in arr or []:
            it = self._vod(v)
            if it:
                out.append(it)
        return out

    # ---------------------------------------------------------------- 六方法
    def homeContent(self, filter):
        classes = [{"type_id": t, "type_name": n} for t, n in TYPES]
        return {"class": classes, "filters": {t: [] for t, _ in TYPES}}

    def homeVideoContent(self):
        j = self._api("/api/v1/search", "wd=*&page=1")
        hits = ((j.get("data") or {}).get("hits")) or []
        return {"list": self._list(hits)}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            page = max(1, int(str(pg).strip() or 1))
        except Exception:
            page = 1
        q = "wd=%s&page=%d" % (urllib.parse.quote("*"), page)
        if tid and str(tid) in dict(TYPES):
            q += "&type=" + urllib.parse.quote(str(tid))
        j = self._api("/api/v1/search", q)
        data = j.get("data") or {}
        hits = data.get("hits") or []
        pages = int(data.get("total_pages") or page + 1)
        return {"page": page, "pagecount": pages, "limit": PAGE_SIZE,
                "total": pages * PAGE_SIZE, "list": self._list(hits)}

    def detailContent(self, ids):
        vid = _s(ids[0] if ids else "")
        if not vid:
            return {"list": []}
        try:
            j = self._api("/api/v1/video/detail", "id=" + urllib.parse.quote(vid))
            info = ((j.get("data") or {}).get("vod_info")) or {}
            if not info:
                return {"list": []}
            froms, urls = [], []
            for line in (info.get("vod_url_with_player") or []):
                name = _s(line.get("name")) or "线路"
                eps = []
                for part in _s(line.get("url")).split("#"):
                    if not part:
                        continue
                    if "$" in part:
                        t, u = part.split("$", 1)
                    else:
                        t, u = "正片", part
                    t = t.replace("$", " ").replace("#", " ")
                    if u:
                        eps.append("%s$%s" % (t, u))
                if eps:
                    froms.append(name)
                    urls.append("#".join(eps))
            pic = _s(info.get("vod_pic"))
            if pic.startswith("//"):
                pic = "https:" + pic
            vod = {
                "vod_id": vid,
                "vod_name": _s(info.get("vod_name")),
                "vod_pic": pic,
                "type_name": _s(info.get("vod_class")),
                "vod_year": _s(info.get("vod_year")),
                "vod_area": _s(info.get("vod_area")),
                "vod_remarks": _s(info.get("vod_remarks")),
                "vod_actor": _s(info.get("vod_actor")),
                "vod_director": _s(info.get("vod_director")),
                "vod_content": _s(info.get("vod_blurb")) or _s(info.get("vod_content")),
                "vod_play_from": "$$$".join(froms),
                "vod_play_url": "$$$".join(urls),
            }
            if not urls:
                vod["vod_play_from"] = "网页"
                vod["vod_play_url"] = "正片$%s/api/v1/video/detail?id=%s" % (self.host, vid)
            return {"list": [vod]}
        except Exception:
            return {"list": []}

    def searchContent(self, key, quick, pg="1"):
        try:
            page = max(1, int(str(pg).strip() or 1))
        except Exception:
            page = 1
        j = self._api("/api/v1/search", "wd=%s&page=%d" % (urllib.parse.quote(_s(key)), page))
        data = j.get("data") or {}
        return {"list": self._list(data.get("hits")), "page": page}

    # ---------------------------------------------------------------- 播放
    def playerContent(self, flag, id, vipFlags):
        tok = _s(id)
        try:
            if not self._login():
                return {"parse": 1, "playUrl": "", "url": "", "header": ""}
            h = {"Authorization": "Bearer " + Spider._sess["jwt"], "X-Session-Id": Spider._sess["sid"]}
            if not tok.startswith("tk:"):
                tok = "tk:" + tok
            t = self._json("POST", "/api/v1/vod/ticket", json.dumps({"token": tok}), h)
            ticket = (t.get("data") or {}).get("ticket") or ""
            if not ticket:
                return {"parse": 1, "playUrl": "", "url": "", "header": ""}
            head = ticket.split(".")[0]
            head += "=" * (-len(head) % 4)
            import base64
            info = json.loads(base64.urlsafe_b64decode(head).decode("utf-8", "ignore")).get("data") or {}
            api = _s(info.get("parse_api"))
            target = _s(info.get("url"))
            if not api or not target:
                return {"parse": 1, "playUrl": "", "url": "", "header": ""}
            if api.startswith("/"):
                api = self.host + api
            full = api + urllib.parse.quote(target, safe="")
            txt = self._req("GET", full[len(self.host):] if full.startswith(self.host) else full, None, h)
            j = json.loads(txt) if txt.strip().startswith("{") else {}
            url = _s(j.get("url"))
            if url.startswith("http"):
                return {"parse": 0, "playUrl": "", "url": url,
                        "header": '{"User-Agent":"%s"}' % UA}
        except Exception:
            pass
        return {"parse": 1, "playUrl": "", "url": "", "header": ""}
