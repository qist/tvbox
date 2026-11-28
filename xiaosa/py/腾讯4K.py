# coding: utf-8
# 腾讯视频 4K（tencent_video）· TVBox / FongMi Python 站源
# 首页/分类：pbaccess MVLPage；搜索：MbSearch；详情：float_vinfo2 + union 分集；播放：jx4k 解析直链
import json
import re
import time
import urllib.parse

from base.spider import Spider as BaseSpider

PC_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36")
MVL = ("https://pbaccess.video.qq.com/trpc.multi_vector_layout.mvl_controller."
       "MVLPageHTTPService/getMVLPage?&vversion_platform=2")
SEARCH_API = ("https://pbaccess.video.qq.com/trpc.videosearch.mobile_search."
              "MultiTerminalSearch/MbSearch?vplatform=2")
VINFO = "https://node.video.qq.com/x/api/float_vinfo2?cid="
UNION = ("https://union.video.qq.com/fcgi-bin/data?otype=json&tid=1804&appid=20001238"
         "&appkey=6c03bbe9658448a4&union_platform=1&idlist=")
JX4K = "https://jx4k.fuyingapi.top/api/?key=f9ecd007748997c6a81a83c425e9448a&url="
COVER = "https://v.qq.com/x/cover/"

CHANNELS = [
    {"type_id": "movie", "type_name": "电影", "channel": "100173"},
    {"type_id": "tv", "type_name": "电视剧", "channel": "100113"},
    {"type_id": "mini_series", "type_name": "短剧", "channel": "120188"},
    {"type_id": "variety", "type_name": "综艺", "channel": "100109"},
    {"type_id": "cartoon", "type_name": "动漫", "channel": "100119"},
    {"type_id": "child", "type_name": "少儿", "channel": "100150"},
    {"type_id": "doco", "type_name": "纪录片", "channel": "100105"},
]
CHANNEL_BY_ID = {c["type_id"]: c["channel"] for c in CHANNELS}
PAGE_SIZE = 21
MAX_VIDS = 300
MEDIA_RE = re.compile(r"\.(?:m3u8|mp4|flv|mkv|mpd|ts)(?:[?#]|$)", re.I)
TRAILER_KEYS = ["预告", "花絮", "片花", "特辑", "幕后", "采访", "制作", "MV", "主题曲"]


def _clean(s):
    s = str(s or "")
    s = re.sub(r"<[^>]*>", "", s)
    s = (s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
          .replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " "))
    return re.sub(r"\s+", " ", s).strip()


def _safe(s):
    return _clean(s).replace("$", " ").replace("#", " ").strip()


def _fix_pic(pic):
    s = str(pic or "").strip()
    if not s:
        return ""
    if s.startswith("//"):
        s = "https:" + s
    if s.startswith("http://"):
        s = "https://" + s[7:]
    if s.endswith("/"):
        s += "0"
    return s


class Spider(BaseSpider):
    def getName(self):
        return "腾讯视频"

    def getDependence(self):
        return []

    def setExtendInfo(self, extend):
        return None

    def init(self, extend=""):
        self.host = "https://v.qq.com"

    # ---- 网络 ----------------------------------------------------------
    def _headers(self, extra=None):
        h = {
            "User-Agent": PC_UA,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Origin": "https://v.qq.com",
            "Referer": "https://v.qq.com/",
        }
        if extra:
            h.update(extra)
        return h

    def _text(self, url, method="GET", body=None, headers=None, timeout=20):
        for _ in range(2):
            try:
                sess = getattr(self, "session", None)
                if sess is not None:
                    r = sess.request(method, url, data=body,
                                     headers=headers or self._headers(), timeout=timeout)
                else:
                    if method == "GET":
                        r = self.fetch(url, headers=headers or self._headers(), timeout=timeout)
                    else:
                        r = self.post(url, data=body, headers=headers or self._headers(), timeout=timeout)
                text = getattr(r, "text", None)
                if text is None:
                    text = (getattr(r, "content", b"") or b"").decode("utf-8", "ignore")
                if text:
                    return text
            except Exception:
                time.sleep(0.5)
        return ""

    def _post_json(self, url, payload, timeout=20):
        text = self._text(url, "POST", json.dumps(payload),
                          self._headers({"Content-Type": "application/json"}), timeout)
        try:
            return json.loads(text)
        except Exception:
            return {}

    # ---- 首页 / 分类 ---------------------------------------------------
    def homeContent(self, filter):
        try:
            jobs = [{"page_params": {"page_type": "operation", "page_id": "channel_list",
                                     "channel_id": c["channel"], "filter_params": "sort=75"},
                     "page_context": self._ctx(1)} for c in CHANNELS[:3]]
            seen = set()
            items = []
            for j in [self._post_json(MVL, b) for b in jobs]:
                for it in self._cards(j):
                    if it["vod_id"] in seen:
                        continue
                    seen.add(it["vod_id"])
                    items.append(it)
            return {"class": [{"type_id": c["type_id"], "type_name": c["type_name"]} for c in CHANNELS],
                    "filters": {c["type_id"]: [] for c in CHANNELS},
                    "list": items}
        except Exception:
            return {"class": [], "filters": {}, "list": []}

    def homeVideoContent(self):
        try:
            return {"list": self.homeContent(True).get("list") or []}
        except Exception:
            return {"list": []}

    def _ctx(self, page):
        offset = (page - 1) * PAGE_SIZE
        return {
            "page_index": str(page), "_ctrl_page_index": str(page),
            "_ds_cli_6970df954e7a9803_poster_offset": str(offset),
            "_ds_cli_6970df954e7a9803_poster_size": str(PAGE_SIZE),
            "_ctrl_showed_module_num": "1", "_merger_mod_cnt": "1",
            "sdk_page_ctx": '{"page_offset":1,"page_size":5,"used_module_num":1}',
            "video_un_page_index": "1",
        }

    def _cards(self, j):
        out = []
        try:
            cards = j.get("data", {}).get("modules", {}).get("normal", {}).get("cards") or []
            for card in cards:
                for key, val in (card.get("children_list") or {}).items():
                    if key in ("filter_card", "nav_card"):
                        continue
                    lst = (val or {}).get("cards")
                    if not isinstance(lst, list):
                        continue
                    for item in lst:
                        p = item.get("params") or {}
                        title = _safe(p.get("title") or p.get("sub_title") or "")
                        pic = p.get("new_pic_hz") or p.get("new_pic_vt") or p.get("image_url") or ""
                        if not title and p.get("poster"):
                            try:
                                poster = json.loads(p["poster"])
                                title = _safe(poster.get("title"))
                                pic = pic or poster.get("image_url") or ""
                            except Exception:
                                pass
                        cid = str(p.get("cid") or "").strip()
                        if not cid or not title:
                            continue
                        out.append({
                            "vod_id": cid,
                            "vod_name": title,
                            "vod_pic": _fix_pic(pic),
                            "vod_remarks": _safe(p.get("timelong") or p.get("episode_updated")
                                                 or p.get("marklabel_0_prime_text") or ""),
                            "vod_year": str(p.get("year") or ""),
                        })
        except Exception:
            pass
        return out

    def categoryContent(self, tid, pg, filter, extend):
        try:
            page = max(1, int(str(pg).strip() or 1))
            channel = CHANNEL_BY_ID.get(str(tid)) or (str(tid) if str(tid).isdigit() else "100173")
            parts = []
            ext = extend or {}
            for key in ("sort", "itype", "ipay", "iarea", "iyear", "theater", "award",
                        "recommend", "producer", "characteristic", "exclusive", "itrailer",
                        "iregion", "pay", "anime_status", "item", "all", "gender",
                        "language", "child_ip", "prefer", "story", "identity", "attraction"):
                v = str(ext.get(key) or "").strip()
                if v and v not in ("-1", "undefined"):
                    parts.append("%s=%s" % (key, urllib.parse.quote(v)))
            if not any(p.startswith("sort=") for p in parts):
                parts.insert(0, "sort=75")
            body = {"page_params": {"page_type": "operation", "page_id": "channel_list",
                                    "channel_id": channel, "filter_params": "&".join(parts)},
                    "page_context": self._ctx(page)}
            j = self._post_json(MVL, body)
            items = self._cards(j)
            more = bool((j.get("data") or {}).get("has_next_page"))
            return {"list": items, "page": page, "pagecount": page + 1 if more else page,
                    "limit": len(items), "total": len(items) if not more else (page + 1) * PAGE_SIZE}
        except Exception:
            return {"list": [], "page": 1, "pagecount": 1, "limit": 0, "total": 0}

    # ---- 搜索 ----------------------------------------------------------
    def searchContent(self, key, quick, pg="1"):
        try:
            wd = str(key).strip()
            if not wd:
                return {"list": [], "page": 1, "pagecount": 1}
            body = {
                "version": "25042201", "clientType": 1, "filterValue": "",
                "uuid": "B1E50847-D25F-4C4B-BBA0-36F0093487F6", "retry": 0,
                "query": wd, "pagenum": 0, "isPrefetch": True, "pagesize": 30,
                "queryFrom": 0, "searchDatakey": "", "transInfo": "",
                "isneedQc": True, "preQid": "", "adClientInfo": "",
                "extraInfo": {"isNewMarkLabel": "1", "multi_terminal_pc": "1",
                              "themeType": "1", "sugRelatedIds": "{}", "appVersion": ""},
            }
            j = self._post_json(SEARCH_API, body)
            out = []
            seen = set()

            def push(lst):
                for it in lst or []:
                    doc = (it or {}).get("doc") or {}
                    info = (it or {}).get("videoInfo") or {}
                    vid = str(doc.get("id") or "")
                    name = _safe(info.get("title"))
                    if not vid or not name or vid in seen:
                        continue
                    sites = info.get("playSites") or []
                    if sites and not any(str(s.get("enName") or "").lower() == "qq" for s in sites):
                        continue
                    seen.add(vid)
                    out.append({"vod_id": vid, "vod_name": name,
                                "vod_pic": _fix_pic(info.get("imgUrl")),
                                "vod_remarks": _safe(info.get("secondLine")),
                                "_score": self._score(name, wd)})

            push(((j.get("data") or {}).get("normalList") or {}).get("itemList"))
            for box in (j.get("data") or {}).get("areaBoxList") or []:
                push(box.get("itemList"))
            out.sort(key=lambda x: -x["_score"])
            good = [x for x in out if x["_score"] > 0]
            res = (good or out)[:30]
            for x in res:
                x.pop("_score", None)
            return {"list": res, "page": 1, "pagecount": 1, "limit": len(res), "total": len(res)}
        except Exception:
            return {"list": [], "page": 1, "pagecount": 1}

    @staticmethod
    def _score(name, wd):
        s = 1
        if name == wd:
            s = 6
        elif name.startswith(wd):
            s = 5
        elif wd in name:
            s = 4 if len(name) <= 12 else 2
        for k in ("预告", "花絮", "解说", "盘点", "混剪", "彩蛋", "速看", "剪辑", "反应"):
            if k in name:
                s -= 3
                break
        if len(name) > 30:
            s -= 1
        return s

    # ---- 详情 ----------------------------------------------------------
    def detailContent(self, ids):
        try:
            cid = str(ids[0] if isinstance(ids, (list, tuple)) else ids).strip()
            if not cid:
                return {"list": []}
            text = self._text(VINFO + urllib.parse.quote(cid), headers=self._headers({"Referer": "https://v.qq.com/"}))
            try:
                j = json.loads(text)
            except Exception:
                return {"list": []}
            c = (j or {}).get("c") or {}
            if not c:
                return {"list": []}
            typ = j.get("typ") or []
            type_name = ""
            if isinstance(typ, list) and typ:
                main = str(typ[0] or "")
                sub = typ[1] if len(typ) > 1 and isinstance(typ[1], list) else []
                type_name = ",".join([main] + [str(x) for x in sub if x]).strip(",")
            nam = j.get("nam") or []
            flat = []
            for x in nam:
                if isinstance(x, list):
                    flat.extend(x)
                elif x:
                    flat.append(x)
            vod = {
                "vod_id": cid,
                "vod_name": _safe(c.get("title") or c.get("full_title") or cid),
                "vod_pic": _fix_pic(c.get("pic")),
                "vod_content": _clean(c.get("description")),
                "vod_year": str(c.get("year") or ""),
                "vod_area": _clean(c.get("area")),
                "vod_remarks": _safe(j.get("rec") or c.get("rec") or ""),
                "vod_actor": _clean(",".join(str(x) for x in flat)),
                "type_name": type_name,
            }
            vids = [str(v) for v in (c.get("video_ids") or []) if v][:MAX_VIDS]
            eps = []
            seen = set()
            for i in range(0, len(vids), 30):
                batch = vids[i:i + 30]
                txt = self._text(UNION + ",".join(batch))
                k, m2 = txt.find("{"), txt.rfind("}")
                if k < 0 or m2 <= k:
                    continue
                try:
                    o = json.loads(txt[k:m2 + 1])
                except Exception:
                    continue
                for item in o.get("results") or []:
                    f = (item or {}).get("fields") or {}
                    vid = str(f.get("vid") or "")
                    if not vid or vid in seen:
                        continue
                    seen.add(vid)
                    cat = f.get("category_map") or []
                    eps.append({"vid": vid,
                                "title": _safe(f.get("title")) or ("第%d集" % (len(eps) + 1)),
                                "type": str(cat[1]) if len(cat) > 1 else ""})
            if not eps:
                for i, vid in enumerate(vids):
                    eps.append({"vid": vid, "title": ("第%d集" % (i + 1)) if len(vids) > 1 else "正片", "type": ""})
            main, groups = [], {"预告": [], "花絮片花": [], "特辑": []}
            for ep in eps:
                t = ep["type"]
                if t and any(k in t for k in TRAILER_KEYS):
                    if "预告" in t:
                        groups["预告"].append(ep)
                    elif "花絮" in t or "片花" in t:
                        groups["花絮片花"].append(ep)
                    else:
                        groups["特辑"].append(ep)
                else:
                    main.append(ep)
            froms, urls = [], []
            def to_url(lst):
                return "#".join("%s$%s%s/%s.html" % (e["title"], COVER, cid, e["vid"]) for e in lst)
            if main:
                froms.append("正片")
                urls.append(to_url(main))
            for name in ("预告", "花絮片花", "特辑"):
                if groups[name]:
                    froms.append(name)
                    urls.append(to_url(groups[name]))
            vod["vod_play_from"] = "$$$".join(froms)
            vod["vod_play_url"] = "$$$".join(urls)
            return {"list": [vod]}
        except Exception:
            return {"list": []}

    # ---- 播放 ----------------------------------------------------------
    def playerContent(self, flag, pid, vipFlags):
        header = self._headers({"Referer": "https://v.qq.com/"})
        try:
            raw = str(pid or "").strip()
            if raw and not raw.startswith("http") and "$" in raw:
                raw = raw[raw.rfind("$") + 1:].strip()
            if not raw:
                return {"parse": 1, "url": "", "header": header}
            if raw.startswith("http") and MEDIA_RE.search(raw):
                return {"parse": 0, "url": raw, "header": header}
            page = raw
            if not re.match(r"^https?://", page):
                m = re.search(r"/x/cover/([0-9A-Za-z]+)/([0-9A-Za-z]+)\.html", page)
                if m:
                    page = COVER + m.group(1) + "/" + m.group(2) + ".html"
                else:
                    cid_m = re.search(r"[?&]cid=([0-9A-Za-z]+)", page)
                    if cid_m:
                        page = COVER + cid_m.group(1) + ".html"
            api = JX4K + urllib.parse.quote(page, safe="")
            txt = self._text(api, headers={"User-Agent": "okhttp/3.14.9",
                                           "Content-Type": "application/x-www-form-urlencoded"}, timeout=25)
            try:
                j = json.loads(txt)
            except Exception:
                j = {}
            url = str(j.get("url") or "")
            if str(j.get("code")) == "200" and url.startswith("http"):
                return {"parse": 0, "url": url, "header": {"User-Agent": PC_UA}}
            return {"parse": 1, "url": page, "header": header}
        except Exception:
            return {"parse": 1, "url": str(pid), "header": header}
