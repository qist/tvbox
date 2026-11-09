# coding: utf-8
# 多多影视 极速（duoduo_tv）· TVBox / FongMi Python 站源
# 站点：https://dduotv01.top  接口：/api.php/web/*
# 播放：站内线路是加密串，官方用 wasm+protobuf 向 /api.php/web/decode/url 换直链，
#       这里用纯 Python 复刻 protobuf 编解码与 SHA-256 签名。
import hashlib
import json
import os
import re
import time
import urllib.parse

from base.spider import Spider as BaseSpider

HOST = "https://dduotv01.top"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
HEADERS = {
    "User-Agent": UA,
    "X-Client": "8f3d2a1c7b6e5d4c9a0b1f2e3d4c5b6a",
    "web-sign": "ddtvf65f3a83d6d9ad6f",
}
SIGN_FINGER = "WF-2c064bc5b3400788f31b848849bc3a60f835423ba2dfe69d7ea93974c216e4f2"
SIGN_SK = "WEB-50a8e9c84a1dc05669a692ded99a2dac46527229e607a7be15db88dbc59059d1"

CLASSES = [{"type_id": "1", "type_name": "电影"}, {"type_id": "2", "type_name": "剧集"},
           {"type_id": "3", "type_name": "动漫"}, {"type_id": "4", "type_name": "综艺"}]
TYPE_NAME = {"1": "电影", "2": "剧集", "3": "动漫", "4": "综艺"}
LINE_NAME = {
    "BBA": "BB蓝光", "qsvip": "青山蓝光", "NBY": "NB蓝光", "co": "CO蓝光", "CO4K": "CO4K",
    "zijianm3u8": "ZJ4K", "PAN1": "PO蓝光", "qq": "腾讯", "bilibili": "bilibili",
    "qiyi": "奇艺", "youku": "优酷", "mgtv": "芒果", "jsm3u8": "站外-极速",
    "rym3u8": "站外-如意", "lzm3u8": "站外-量子", "bfzym3u8": "站外-暴风",
    "ikm3u8": "站外-ikun", "modum3u8": "站外-魔都", "subm3u8": "站外-速播",
    "gsm3u8": "站外-光速", "hnm3u8": "站外-红牛",
}
YEAR = ["", "2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018",
        "2017", "2016", "2015-2011", "2010-2000", "90年代", "80年代"]
SORTS = [{"n": "默认", "v": ""}, {"n": "人气", "v": "hits"}, {"n": "最新", "v": "time"},
         {"n": "评分", "v": "score"}, {"n": "年份", "v": "year"}]
MEDIA_RE = re.compile(r"\.(?:m3u8|mp4|flv|mkv|ts|m4a|mp3)(?:[?#]|$)", re.I)
PAGE_RE = re.compile(r"\.(?:html?|shtml)(?:[?#]|$)", re.I)
OFFICIAL_RE = re.compile(r"^https?://(?:www\.)?(?:mgtv\.com|v\.qq\.com|www\.iqiyi\.com|"
                         r"v\.youku\.com|www\.bilibili\.com|b23\.tv)/", re.I)


def _varint(n):
    out = bytearray()
    n = int(n)
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | 0x80 if n else b)
        if not n:
            return bytes(out)


def _pb_str(field, value):
    b = value.encode("utf-8") if isinstance(value, str) else (value or b"")
    return _varint((field << 3) | 2) + _varint(len(b)) + b


def _pb_num(field, value):
    return _varint(field << 3) + _varint(value)


def _pb_decode(buf):
    out = {}
    pos = 0
    n = len(buf)
    while pos < n:
        tag, pos = _read_varint(buf, pos)
        field, wire = tag >> 3, tag & 7
        if wire == 0:
            val, pos = _read_varint(buf, pos)
        elif wire == 2:
            ln, pos = _read_varint(buf, pos)
            val = buf[pos:pos + ln]
            pos += ln
        elif wire == 1:
            val = buf[pos:pos + 8]
            pos += 8
        elif wire == 5:
            val = buf[pos:pos + 4]
            pos += 4
        else:
            break
        out.setdefault(field, []).append(val)
    return out


def _read_varint(buf, pos):
    v = 0
    shift = 0
    while pos < len(buf):
        b = buf[pos]
        pos += 1
        v |= (b & 0x7F) << shift
        if not b & 0x80:
            return v, pos
        shift += 7
    raise ValueError("bad varint")


def _clean(s):
    s = str(s or "")
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = (s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&quot;", '"')
          .replace("&#39;", "'").replace("&lt;", "<").replace("&gt;", ">"))
    return re.sub(r"[ \t]+", " ", s).strip()


class Spider(BaseSpider):
    def getName(self):
        return "多多影视"

    def getDependence(self):
        return []

    def setExtendInfo(self, extend):
        return None

    def init(self, extend=""):
        self.host = HOST

    # ---- 网络 ----------------------------------------------------------
    def _get(self, path, timeout=20):
        url = self.host + path
        for _ in range(2):
            try:
                sess = getattr(self, "session", None)
                if sess is not None:
                    r = sess.request("GET", url, headers=dict(HEADERS), timeout=timeout)
                    text = getattr(r, "text", None)
                    if text is None:
                        text = (getattr(r, "content", b"") or b"").decode("utf-8", "ignore")
                else:
                    r = self.fetch(url, headers=dict(HEADERS), timeout=timeout)
                    text = getattr(r, "text", "") or ""
                if text:
                    return json.loads(text)
            except Exception:
                time.sleep(0.5)
        return {}

    def _api(self, path):
        try:
            j = self._get(path)
            if int(j.get("code") or 0) != 200:
                return {}
            return j
        except Exception:
            return {}

    # ---- 列表 ----------------------------------------------------------
    def _vod(self, it):
        vid = str((it or {}).get("vod_id") or (it or {}).get("id") or "")
        name = str((it or {}).get("vod_name") or (it or {}).get("name") or "").strip()
        if not vid or not name:
            return None
        pic = str((it or {}).get("vod_pic") or (it or {}).get("vod_pic_slide") or (it or {}).get("pic") or "")
        pic = pic.replace("&amp;", "&")
        if pic.startswith("//"):
            pic = "https:" + pic
        area = (it or {}).get("vod_area")
        if isinstance(area, list):
            area = ",".join(str(x) for x in area)
        return {
            "vod_id": vid, "vod_name": name, "vod_pic": pic,
            "vod_remarks": str((it or {}).get("vod_remarks") or ""),
            "vod_year": str((it or {}).get("vod_year") or ""),
            "vod_area": str(area or ""),
        }

    def _list(self, arr):
        out = []
        seen = set()
        for it in arr or []:
            try:
                v = self._vod(it)
            except Exception:
                continue
            if v and v["vod_id"] not in seen:
                seen.add(v["vod_id"])
                out.append(v)
        return out

    # ---- 首页 / 分类 ---------------------------------------------------
    def homeContent(self, filter):
        filters = {}
        for c in CLASSES:
            tid = c["type_id"]
            cls = {
                "1": ["动作", "喜剧", "爱情", "科幻", "恐怖", "悬疑", "犯罪", "战争",
                      "动画", "冒险", "历史", "灾难", "纪录", "剧情"],
                "2": ["爱情", "古装", "武侠", "历史", "家庭", "喜剧", "悬疑", "犯罪",
                      "战争", "奇幻", "科幻", "恐怖"],
                "3": ["真人秀", "音乐", "脱口秀", "歌舞", "爱情"],
                "4": ["冒险", "奇幻", "科幻", "武侠", "悬疑"],
            }[tid]
            area = {
                "1": ["大陆", "香港", "台湾", "美国", "日本", "韩国", "泰国", "印度",
                      "英国", "法国", "德国", "加拿大", "西班牙", "意大利", "澳大利亚"],
                "2": ["大陆", "香港", "台湾", "美国", "日本", "韩国", "泰国", "英国"],
                "3": ["大陆", "香港", "台湾", "美国", "日本", "韩国"],
                "4": ["大陆", "日本", "欧美"],
            }[tid]
            filters[tid] = [
                {"key": "sort", "name": "排序", "value": SORTS},
                {"key": "class", "name": "类型",
                 "value": [{"n": "全部", "v": ""}] + [{"n": x, "v": x} for x in cls]},
                {"key": "area", "name": "地区",
                 "value": [{"n": "全部", "v": ""}] + [{"n": x, "v": x} for x in area]},
                {"key": "year", "name": "年份",
                 "value": [{"n": y or "全部", "v": y} for y in YEAR]},
            ]
        return {"class": CLASSES, "filters": filters, "list": self.homeVideoContent().get("list") or []}

    def homeVideoContent(self):
        try:
            data = self._api("/api.php/web/index/home").get("data") or {}
            items = list(data.get("recommend") or [])
            for c in data.get("categories") or []:
                items.extend(c.get("videos") or [])
            return {"list": self._list(items)[:60]}
        except Exception:
            return {"list": []}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            page = max(1, int(str(pg).strip() or 1))
            ext = extend or {}
            params = {"type_id": str(tid), "page": str(page),
                      "sort": str(ext.get("sort") or "hits") or "hits",
                      "type_name": TYPE_NAME.get(str(tid), "电影")}
            for k in ("class", "area", "year"):
                v = str(ext.get(k) or "").strip()
                if v:
                    params[k] = v
            j = self._api("/api.php/web/filter/vod?" + urllib.parse.urlencode(params))
            items = self._list(j.get("data") if isinstance(j.get("data"), list) else [])
            pagecount = int(j.get("pageCount") or j.get("pagecount") or 0)
            if len(items) >= 18:
                pagecount = max(pagecount, page + 1)
            pagecount = max(pagecount, page)
            return {"list": items, "page": page, "pagecount": pagecount,
                    "limit": 24, "total": 9999 if items else 0}
        except Exception:
            return {"list": [], "page": 1, "pagecount": 1, "limit": 24, "total": 0}

    def searchContent(self, key, quick, pg="1"):
        try:
            page = max(1, int(str(pg).strip() or 1))
            wd = str(key).strip()
            if not wd:
                return {"list": [], "page": page, "pagecount": page}
            j = self._api("/api.php/web/search/index?wd=%s&page=%d&limit=15"
                          % (urllib.parse.quote(wd), page))
            items = self._list(j.get("data") if isinstance(j.get("data"), list) else [])
            return {"list": items, "page": page,
                    "pagecount": page + 1 if len(items) >= 15 else page}
        except Exception:
            return {"list": [], "page": 1, "pagecount": 1}

    # ---- 详情 ----------------------------------------------------------
    def _episodes(self, group):
        out = []
        for part in str(group or "").split("#"):
            raw = part.strip()
            if not raw:
                continue
            at = raw.find("$")
            title = (raw[:at] if at >= 0 else raw).strip()
            payload = (raw[at + 1:] if at >= 0 else "").strip()
            if title and payload:
                out.append((title, payload))
        return out

    def _lines(self, vod_id):
        j = self._api("/api.php/web/vod/get_detail?vod_id=" + urllib.parse.quote(vod_id))
        data = j.get("data")
        vod = data[0] if isinstance(data, list) and data else None
        if not vod:
            return None, []
        froms = [x.strip() for x in str(vod.get("vod_play_from") or "").split("$$$") if x.strip()]
        groups = [x.strip() for x in str(vod.get("vod_play_url") or "").split("$$$") if x.strip()]
        players = {}
        for p in (j.get("vodplayer") or []):
            if p and p.get("from"):
                players[p["from"]] = p
        lines = []
        for i in range(min(len(froms), len(groups))):
            key, group = froms[i], groups[i]
            if not key or not group:
                continue
            p = players.get(key) or {}
            name = str(p.get("show") or LINE_NAME.get(key) or key).strip() or key
            try:
                sort = float(p.get("sort"))
            except Exception:
                sort = 9999
            lines.append({"name": name, "key": key, "group": group, "sort": sort})
        try:
            a = self._api("/api.php/web/internal/search_aggregate?vod_id=" + urllib.parse.quote(vod_id))
            for st in (a.get("data") if isinstance(a.get("data"), list) else []):
                if not st or not st.get("vod_play_url"):
                    continue
                key = str(st.get("vod_play_from") or st.get("site_key") or "").strip()
                name = str(st.get("site_name") or LINE_NAME.get(key) or key).strip()
                if not key or not name:
                    continue
                try:
                    sort = float(st.get("sort"))
                except Exception:
                    sort = 9999
                lines.append({"name": name, "key": key,
                              "group": str(st["vod_play_url"]), "sort": sort})
        except Exception:
            pass
        lines.sort(key=lambda x: x["sort"])
        return vod, lines

    def detailContent(self, ids):
        try:
            vid = str(ids[0] if isinstance(ids, (list, tuple)) else ids).strip()
            if not vid:
                return {"list": []}
            vod, lines = self._lines(vid)
            if not vod:
                return {"list": []}
            names, urls, used = [], [], set()
            for line in lines:
                if line["name"] in used:
                    continue
                eps = self._episodes(line["group"])
                if not eps:
                    continue
                used.add(line["name"])
                names.append(line["name"])
                items = []
                for i, (title, payload) in enumerate(eps):
                    t = title.replace("$", "").replace("#", "")
                    pid = "%s|%s|%d|%s" % (line["key"], vid, i, payload)
                    items.append("%s$%s" % (t, pid))
                urls.append("#".join(items))
            v = self._vod(vod) or {"vod_id": vid, "vod_name": vid}
            v["vod_id"] = str(vod.get("vod_id") or vid)
            v["vod_content"] = _clean(vod.get("vod_content"))
            v["vod_actor"] = str(vod.get("vod_actor") or "")
            v["vod_director"] = str(vod.get("vod_director") or "")
            cls = vod.get("vod_class")
            v["type_name"] = ",".join(cls) if isinstance(cls, list) else str(cls or "")
            v["vod_play_from"] = "$$$".join(names)
            v["vod_play_url"] = "$$$".join(urls)
            return {"list": [v]}
        except Exception:
            return {"list": []}

    # ---- 播放 ----------------------------------------------------------
    def _decode(self, payload, key, timeout=15):
        ts = int(time.time() * 1000)
        nonce = os.urandom(16).hex()
        pre = ("finger=%s&id=com.web.player&nonce=%s&sk=%s&time=%d&v=1"
               % (SIGN_FINGER, nonce, SIGN_SK, ts))
        sign = hashlib.sha256(pre.encode("utf-8")).hexdigest().upper()
        body = (_pb_str(1, payload) + _pb_str(2, key or "") + _pb_num(3, ts)
                + _pb_str(4, nonce) + _pb_str(5, sign)
                + _pb_str(6, "com.web.player") + _pb_num(7, 1))
        headers = dict(HEADERS)
        headers["Content-Type"] = "application/x-protobuf"
        headers["Accept"] = "application/x-protobuf"
        url = self.host + "/api.php/web/decode/url"
        try:
            sess = getattr(self, "session", None)
            if sess is not None:
                r = sess.request("POST", url, data=body, headers=headers, timeout=timeout)
                raw = getattr(r, "content", b"") or b""
            else:
                r = self.post(url, data=body, headers=headers, timeout=timeout)
                raw = getattr(r, "content", b"") or b""
        except Exception:
            return {"code": 0, "msg": "http", "data": ""}
        try:
            f = _pb_decode(raw)
        except Exception:
            return {"code": 0, "msg": "pb", "data": ""}

        def s(num):
            v = (f.get(num) or [None])[0]
            return v.decode("utf-8", "ignore") if isinstance(v, bytes) else ("" if v is None else str(v))
        return {"code": int((f.get(1) or [0])[0] or 0), "msg": s(2), "data": s(3)}

    @staticmethod
    def _is_media(url):
        if not re.match(r"^https?://", url or ""):
            return False
        if MEDIA_RE.search(url) or re.search(r"[?&]url=[^&]*\.m3u8", url, re.I):
            return True
        if PAGE_RE.search(url) or OFFICIAL_RE.match(url):
            return False
        return True

    def playerContent(self, flag, pid, vipFlags):
        raw = str(pid or "").strip()
        if not raw:
            return {"parse": 1, "url": ""}
        parts = raw.split("|")
        key = parts[0] or ""
        if "$" in key:
            key = key[key.rfind("$") + 1:]
        if len(parts) >= 4 and parts[1].isdigit() and parts[2].isdigit():
            vod_id, idx, payload = parts[1], int(parts[2]), "|".join(parts[3:])
        elif len(parts) >= 2:
            vod_id, idx, payload = "", -1, "|".join(parts[1:])
        else:
            vod_id, idx, payload = "", -1, raw
        if not key and flag:
            for k, v in LINE_NAME.items():
                if v == flag:
                    key = k
                    break
        # 1) 第一候选
        if re.match(r"^https?://", payload):
            if self._is_media(payload):
                return {"parse": 0, "url": payload, "header": {"User-Agent": UA}}
        else:
            out = self._decode(payload, key)
            if out["code"] == 1 and self._is_media(out["data"]):
                return {"parse": 0, "url": out["data"], "header": {"User-Agent": UA}}
        # 2) 换同集其它线路
        if vod_id and idx >= 0:
            try:
                _, lines = self._lines(vod_id)
                delayed = {"CO4K": 1, "qq": 1, "qiyi": 1, "youku": 1, "mgtv": 1, "bilibili": 1}
                lines = [l for l in lines if l["key"] != key]
                lines.sort(key=lambda l: delayed.get(l["key"], 0))
                for line in lines[:8]:
                    eps = self._episodes(line["group"])
                    if idx >= len(eps):
                        continue
                    pl = eps[idx][1]
                    if re.match(r"^https?://", pl):
                        if self._is_media(pl):
                            return {"parse": 0, "url": pl, "header": {"User-Agent": UA}}
                        continue
                    r2 = self._decode(pl, line["key"])
                    if r2["code"] == 1 and self._is_media(r2["data"]):
                        return {"parse": 0, "url": r2["data"], "header": {"User-Agent": UA}}
            except Exception:
                pass
        return {"parse": 1, "url": raw, "header": {"User-Agent": UA}}
