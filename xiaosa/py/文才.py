# coding: utf-8
# 文才影视（wencaiyingshi）· TVBox / FongMi Python 站源
# 签名：sign = sha1( md5("k=v&...&key=...&t=...") )，随 header 发送
import hashlib
import json
import re
import time
import uuid

from base.spider import Spider as BaseSpider

HOST = "https://www.jiabaide.cn"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.6478.61 Safari/537.36")
SIGN_KEY = "cb808529bae6b6be45ecfab29a4889bc"

API_TYPES = "/api/mw-movie/anonymous/get/filer/type"
API_FILTER = "/api/mw-movie/anonymous/v1/get/filer/list"
API_HOME = "/api/mw-movie/anonymous/v1/home/all/list"
API_HOT = "/api/mw-movie/anonymous/home/hotSearch"
API_LIST = "/api/mw-movie/anonymous/video/list"
API_SEARCH = "/api/mw-movie/anonymous/video/searchByWord"
API_DETAIL = "/api/mw-movie/anonymous/video/detail"
API_PLAY = "/api/mw-movie/anonymous/v2/video/episode/url"

SORTS = [{"n": "最近更新", "v": "2"}, {"n": "人气高低", "v": "3"}, {"n": "评分高低", "v": "4"}]

BASE_CLASSES = [{"type_id": "1", "type_name": "电影"}, {"type_id": "2", "type_name": "电视剧"},
                {"type_id": "3", "type_name": "综艺"}, {"type_id": "4", "type_name": "动漫"},
                {"type_id": "88", "type_name": "短剧"}, {"type_id": "7", "type_name": "体育直播"}]


def _clean(s):
    s = str(s or "")
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", "", s)
    s = re.sub(r"(?i)<br\s*/?>|</p>|</div>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = (s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<")
          .replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'"))
    return re.sub(r"[ \t]+", " ", s).strip()


def _opt(items, name_key="itemText", val_key="itemValue"):
    out = [{"n": "全部", "v": ""}]
    for x in items or []:
        try:
            out.append({"n": str(x.get(name_key) or ""), "v": str(x.get(val_key) or "")})
        except Exception:
            continue
    return out


class Spider(BaseSpider):
    def getName(self):
        return "文才影视"

    def getDependence(self):
        return []

    def setExtendInfo(self, extend):
        return None

    def init(self, extend=""):
        self.host = HOST

    # ---- 请求 ----------------------------------------------------------
    def _headers(self, params):
        t = str(int(time.time() * 1000))
        signing = dict(params)
        signing["key"] = SIGN_KEY
        signing["t"] = t
        raw = "&".join("%s=%s" % (k, v) for k, v in signing.items())
        md5 = hashlib.md5(raw.encode("utf-8")).hexdigest()
        return {
            "User-Agent": UA,
            "Accept": "application/json, text/plain, */*",
            "sign": hashlib.sha1(md5.encode("utf-8")).hexdigest(),
            "t": t,
            "deviceid": str(uuid.uuid4()),
        }

    def _get(self, path, params=None, timeout=20):
        p = params or {}
        qs = "&".join("%s=%s" % (k, v) for k, v in p.items())
        url = self.host + path + ("?" + qs if qs else "")
        headers = self._headers(p)
        for _ in range(2):
            try:
                sess = getattr(self, "session", None)
                if sess is not None:
                    r = sess.request("GET", url, headers=headers, timeout=timeout)
                    text = getattr(r, "text", None)
                    if text is None:
                        text = (getattr(r, "content", b"") or b"").decode("utf-8", "ignore")
                else:
                    r = self.fetch(url, headers=headers, timeout=timeout)
                    text = getattr(r, "text", "") or ""
                if text:
                    return json.loads(text)
            except Exception:
                time.sleep(0.6)
        return {}

    # ---- 列表 ----------------------------------------------------------
    def _vod(self, it):
        vid = str(it.get("vodId") or "")
        name = _clean(it.get("vodName"))
        if not vid or not name:
            return None
        return {
            "vod_id": vid,
            "vod_name": name,
            "vod_pic": str(it.get("vodPic") or ""),
            "vod_remarks": _clean(it.get("vodRemarks") or it.get("vodBlurb") or ""),
            "vod_year": str(it.get("vodYear") or ""),
            "vod_area": str(it.get("vodArea") or ""),
            "type_name": str(it.get("typeName") or ""),
        }

    def _page(self, data, page, size):
        data = data if isinstance(data, dict) else {}
        items = data.get("list") if isinstance(data.get("list"), list) else []
        out = []
        seen = set()
        for it in items:
            try:
                v = self._vod(it)
            except Exception:
                continue
            if v and v["vod_id"] not in seen:
                seen.add(v["vod_id"])
                out.append(v)
        total = int(data.get("totalCount") or data.get("total") or 0)
        pages = int(data.get("totalPage") or data.get("pages") or 0)
        if not pages:
            pages = page + 1 if len(out) >= size else page
        return {"list": out, "page": page, "pagecount": max(1, pages),
                "limit": size, "total": total}

    # ---- 接口 ----------------------------------------------------------
    def homeContent(self, filter):
        try:
            types = self._get(API_TYPES).get("data") or []
            classes = []
            for x in types:
                tid = str(x.get("typeId") or "")
                if not tid:
                    continue
                classes.append({"type_id": tid, "type_name": str(x.get("typeName") or "")})
            flt = self._get(API_FILTER).get("data") or {}
            filters = {}
            for c in classes:
                d = flt.get(c["type_id"]) or {}
                groups = [{"key": "type", "name": "类型", "value": _opt(d.get("typeList"))}]
                if d.get("plotList"):
                    groups.append({"key": "v_class", "name": "剧情", "value": _opt(d.get("plotList"))})
                groups.append({"key": "area", "name": "地区", "value": _opt(d.get("districtList"))})
                groups.append({"key": "year", "name": "年份", "value": _opt(d.get("yearList"))})
                groups.append({"key": "lang", "name": "语言", "value": _opt(d.get("languageList"))})
                sorts = SORTS[1:] if c["type_id"] == "1" else SORTS
                groups.append({"key": "sort", "name": "排序",
                               "value": [{"n": "默认", "v": "1"}] + sorts})
                filters[c["type_id"]] = groups
            if not classes:
                classes = list(BASE_CLASSES)
                filters = {c["type_id"]: [] for c in classes}
            return {"class": classes, "filters": filters}
        except Exception:
            return {"class": list(BASE_CLASSES),
                    "filters": {c["type_id"]: [] for c in BASE_CLASSES}}

    def homeVideoContent(self):
        try:
            data = self._get(API_HOME).get("data") or {}
            items = []
            seen = set()
            for v in data.values():
                if isinstance(v, dict) and isinstance(v.get("list"), list):
                    for it in v["list"]:
                        vid = str(it.get("vodId") or "")
                        if vid and vid not in seen:
                            seen.add(vid)
                            items.append(it)
            hot = self._get(API_HOT).get("data")
            if isinstance(hot, list):
                for it in hot:
                    vid = str(it.get("vodId") or "")
                    if vid and vid not in seen:
                        seen.add(vid)
                        items.append(it)
            out = []
            for it in items[:60]:
                v = self._vod(it)
                if v:
                    out.append(v)
            return {"list": out}
        except Exception:
            return {"list": []}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            page = max(1, int(str(pg).strip() or 1))
            ext = extend or {}
            params = {
                "area": str(ext.get("area") or ""),
                "filterStatus": "1",
                "lang": str(ext.get("lang") or ""),
                "pageNum": str(page),
                "pageSize": "30",
                "sort": str(ext.get("sort") or "1"),
                "sortBy": "1",
                "type": str(ext.get("type") or ""),
                "type1": str(tid),
                "v_class": str(ext.get("v_class") or ""),
                "year": str(ext.get("year") or ""),
            }
            data = self._get(API_LIST, params).get("data") or {}
            return self._page(data, page, 30)
        except Exception:
            return {"list": [], "page": 1, "pagecount": 1, "limit": 30, "total": 0}

    def searchContent(self, key, quick, pg="1"):
        try:
            page = max(1, int(str(pg).strip() or 1))
            data = self._get(API_SEARCH, {"keyword": str(key), "pageNum": str(page),
                                          "pageSize": "8", "sourceCode": "1"}).get("data") or {}
            result = data.get("result") if isinstance(data, dict) else None
            if isinstance(result, dict):
                return self._page(result, page, 8)
            if isinstance(result, list):
                return self._page({"list": result}, page, 8)
            return {"list": [], "page": page, "pagecount": page}
        except Exception:
            return {"list": [], "page": 1, "pagecount": 1}

    def detailContent(self, ids):
        try:
            vid = str(ids[0] if isinstance(ids, (list, tuple)) else ids).strip()
            if not vid:
                return {"list": []}
            data = self._get(API_DETAIL, {"id": vid}).get("data") or {}
            if not data:
                return {"list": []}
            v = self._vod(data)
            if not v:
                return {"list": []}
            eps = data.get("episodeList") or data.get("episodelist") or []
            items = []
            for i, ep in enumerate(eps):
                nid = ep.get("nid") or ep.get("nId") or ep.get("id")
                if nid in (None, ""):
                    continue
                name = _clean(ep.get("name")) or ("第%d集" % (i + 1))
                name = name.replace("$", "").replace("#", "")
                items.append("%s$%s@@%s" % (name, vid, nid))
            v["vod_content"] = _clean(data.get("vodContent") or data.get("vodBlurb") or "")
            v["vod_actor"] = _clean(data.get("vodActor"))
            v["vod_director"] = _clean(data.get("vodDirector"))
            v["vod_year"] = str(data.get("vodYear") or v.get("vod_year") or "")
            v["vod_area"] = str(data.get("vodArea") or v.get("vod_area") or "")
            v["vod_play_from"] = "文才影视" if items else ""
            v["vod_play_url"] = "#".join(items)
            return {"list": [v]}
        except Exception:
            return {"list": []}

    def playerContent(self, flag, pid, vipFlags):
        try:
            raw = str(pid or "")
            if re.search(r"\.(m3u8|mp4|flv|mkv|ts)(\?|$)", raw, re.I):
                return {"parse": 0, "url": raw, "header": {"User-Agent": UA}}
            if "@@" not in raw:
                return {"parse": 1, "url": raw, "header": {"User-Agent": UA}}
            vid, nid = raw.split("@@", 1)
            data = self._get(API_PLAY, {"clientType": "1", "id": vid,
                                        "nid": nid}).get("data") or {}
            opts = [x for x in (data.get("list") or []) if isinstance(x, dict)
                    and str(x.get("url") or "").startswith("http")]
            if not opts:
                return {"parse": 1, "url": raw, "header": {"User-Agent": UA}}
            best = None
            for x in opts:
                if re.search(r"4k|1080|高清|蓝光", str(x.get("resolutionName") or ""), re.I):
                    best = x
                    break
            best = best or opts[0]
            return {"parse": 0, "url": str(best.get("url")),
                    "header": {"User-Agent": UA, "Referer": HOST + "/"}}
        except Exception:
            return {"parse": 1, "url": str(pid), "header": {"User-Agent": UA}}
