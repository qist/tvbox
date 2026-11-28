# coding: utf-8
# 片帝4K（dongpian17.com）· TVBox / FongMi Python 站源
# 协议：GET/POST 带 HMAC-SHA256 签名头（method\npath+query\nts\nnonce），
#       详情给每集 token，播放先 /v1/playback/resolve/{token} 拿线路，
#       再 POST /v1/playback/resolve-line {"ticket": ...} 换真实地址。
import hashlib
import hmac
import json
import os
import ssl
import time
import urllib.parse
import urllib.request

try:
    from base.spider import Spider as BaseSpider
except Exception:
    class BaseSpider(object):
        pass

HOST = "https://dongpian17.com"
SIGN_KEY = "8b9a908a05eac640e1ee06f52acaa741bfe4ba9e004eeffdbeb635e532e06666"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36")
CLIENT = {
    "x-ai-movie-client-name": "movie-search-frontend",
    "x-ai-movie-client-version": "1.0.0",
    "x-ai-movie-build-version": "dongpiandi-v2026.10.04.1-episode-resume-efd9a7f2e87e-web",
    "x-ai-movie-protocol-version": "2026-07-05.library-v2.playback-v1",
}
KINDS = [("all", "全部"), ("movie", "电影"), ("series", "剧集"),
         ("short_drama", "短剧"), ("anime", "动漫"), ("variety", "综艺")]
WINDOWS = [("day", "日榜"), ("week", "周榜"), ("month", "月榜"), ("total", "总榜")]

_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE


def _clean(s):
    s = str(s or "").replace("\u00a0", " ")
    return " ".join(s.split()).replace("$", " ").replace("#", " ").strip()


class Spider(BaseSpider):
    def getName(self):
        return "片帝4K"

    def getDependence(self):
        return []

    def setExtendInfo(self, extend):
        pass

    def init(self, extend=""):
        self.host = HOST
        self.cookies = {}
        try:
            if isinstance(extend, str) and extend.strip().startswith("{"):
                cfg = json.loads(str(extend))
                if cfg.get("host"):
                    self.host = str(cfg["host"]).rstrip("/")
        except Exception:
            pass

    # ---------------------------------------------------------------- 签名请求
    def _call(self, method, path_query, body=None, timeout=20):
        for _ in range(2):
            try:
                ts = str(int(time.time() * 1000))
                nonce = os.urandom(16).hex()
                msg = "%s\n%s\n%s\n%s" % (method, path_query, ts, nonce)
                sig = hmac.new(SIGN_KEY.encode(), msg.encode(), hashlib.sha256).hexdigest()
                h = {"User-Agent": UA, "Accept": "application/json"}
                h.update(CLIENT)
                h["x-ai-movie-timestamp"] = ts
                h["x-ai-movie-nonce"] = nonce
                h["x-ai-movie-signature"] = sig
                if self.cookies:
                    h["Cookie"] = "; ".join("%s=%s" % kv for kv in self.cookies.items())
                data = body.encode("utf-8") if body is not None else None
                if data is not None:
                    h["Content-Type"] = "application/json"
                req = urllib.request.Request(self.host + path_query, data=data, headers=h, method=method)
                r = urllib.request.urlopen(req, timeout=timeout, context=_CTX)
                for c in (r.headers.get_all("Set-Cookie") or []):
                    kv = c.split(";")[0]
                    if "=" in kv:
                        k, v = kv.split("=", 1)
                        self.cookies[k.strip()] = v.strip()
                raw = r.read().decode("utf-8", "ignore")
                try:
                    return json.loads(raw)
                except Exception:
                    return {}
            except Exception:
                time.sleep(0.4)
        return {}

    def _get(self, path_query):
        return self._call("GET", path_query)

    def _post(self, path_query, obj):
        body = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
        return self._call("POST", path_query, body)

    # ---------------------------------------------------------------- 列表转换
    def _card(self, c):
        if not isinstance(c, dict) or not c.get("id"):
            return None
        pic = c.get("poster_url") or c.get("backdrop_url") or ""
        if pic.startswith("//"):
            pic = "https:" + pic
        return {
            "vod_id": str(c.get("id")),
            "vod_name": _clean(c.get("title") or c.get("normalized_title")),
            "vod_pic": pic,
            "vod_remarks": _clean(c.get("remarks") or c.get("badge") or ""),
            "vod_year": str(c.get("year") or ""),
            "vod_area": _clean(c.get("area") or ""),
        }

    def _cards(self, arr):
        out = []
        for c in (arr or []):
            v = self._card(c)
            if v and v["vod_name"]:
                out.append(v)
        return out

    # ---------------------------------------------------------------- 首页
    def homeContent(self, filter):
        classes = [{"type_id": k, "type_name": n} for k, n in KINDS]
        filters = {}
        for k, _ in KINDS:
            filters[k] = [{"key": "window", "name": "榜单",
                           "value": [{"n": n, "v": w} for w, n in WINDOWS]}]
        return {"class": classes, "filters": filters}

    def homeVideoContent(self):
        try:
            j = self._get("/v1/feed/home?scope=public&mode=preview&sections=3&cards=12")
            secs = j.get("sections") or []
            best = []
            for s in secs:
                cards = self._cards(s.get("cards"))
                if s.get("id") == "feed_sec_everyone_watching" or s.get("type") == "trend":
                    if cards:
                        return {"list": cards}
                if not best and cards:
                    best = cards
            if not best:
                for s in secs:
                    c = self._cards(s.get("cards"))
                    if c:
                        best = c
                        break
            return {"list": best}
        except Exception:
            return {"list": []}

    # ---------------------------------------------------------------- 分类
    def categoryContent(self, tid, pg, filter, extend):
        ext = extend if isinstance(extend, dict) else {}
        window = (ext.get("window") or "day")
        try:
            page = max(1, int(str(pg).strip() or 1))
        except Exception:
            page = 1
        q = "?sort=trending&window=%s&page=%d&limit=20" % (urllib.parse.quote(window), page)
        if tid and tid != "all":
            q += "&kind=" + urllib.parse.quote(str(tid))
        try:
            j = self._get("/v1/browse/catalog" + q)
            lst = self._cards(j.get("cards"))
            p = j.get("pagination") or {}
            more = bool(p.get("has_more"))
            total = p.get("total") or (page * 20 + (20 if more else 0))
            pagecount = (int(total) + 19) // 20 if total else (page + 1 if more else page)
            return {"page": page, "pagecount": pagecount, "limit": 20,
                    "total": int(total or 0), "list": lst}
        except Exception:
            return {"page": page, "pagecount": page, "limit": 20, "total": 0, "list": []}

    # ---------------------------------------------------------------- 详情
    def detailContent(self, ids):
        vid = str(ids[0] or "")
        if not vid:
            return {"list": []}
        try:
            j = self._get("/v1/catalog/" + urllib.parse.quote(vid))
            card = j.get("card") or j
            eps = card.get("episodes") or []
            need = int(card.get("episode_count") or 0)
            if need > len(eps):
                eps = self._all_episodes(vid, eps)
            urls = []
            for i, e in enumerate(eps):
                if not isinstance(e, dict):
                    continue
                title = _clean(e.get("title") or e.get("display_name") or "")
                if not title:
                    title = "第%s集" % (e.get("number") or (i + 1))
                tok = str(e.get("token") or "")
                if not tok:
                    continue
                urls.append("%s$%s" % (title, tok))
            pic = card.get("poster_url") or card.get("backdrop_url") or ""
            if pic.startswith("//"):
                pic = "https:" + pic
            vod = {
                "vod_id": vid,
                "vod_name": _clean(card.get("title") or card.get("normalized_title")),
                "vod_pic": pic,
                "type_name": "/".join([str(g) for g in (card.get("genres") or [])][:3]),
                "vod_year": str(card.get("year") or ""),
                "vod_area": _clean(card.get("area") or ""),
                "vod_remarks": _clean(card.get("update_status") or card.get("episode_progress_text") or ""),
                "vod_actor": _clean(", ".join(card.get("actors") or []) if isinstance(card.get("actors"), list) else card.get("actors")),
                "vod_director": _clean(", ".join(card.get("directors") or []) if isinstance(card.get("directors"), list) else card.get("directors")),
                "vod_content": _clean(card.get("description") or card.get("summary") or ""),
                "vod_play_from": "片帝4K",
                "vod_play_url": "#".join(urls),
            }
            if not urls:
                vod["vod_play_from"] = "网页"
                vod["vod_play_url"] = "正片$%s/v1/catalog/%s" % (self.host, vid)
            return {"list": [vod]}
        except Exception:
            return {"list": []}

    def _all_episodes(self, vid, eps):
        out = list(eps or [])
        offset = len(out)
        for _ in range(20):
            j = self._get("/v1/catalog/%s/episodes?limit=48&offset=%d" % (urllib.parse.quote(vid), offset))
            arr = j.get("episodes") or []
            if not arr:
                break
            out.extend(arr)
            p = j.get("episode_pagination") or {}
            if not p.get("has_more"):
                break
            offset += len(arr)
        return out

    # ---------------------------------------------------------------- 搜索
    def searchContent(self, key, quick, pg="1"):
        try:
            page = max(1, int(str(pg).strip() or 1))
        except Exception:
            page = 1
        q = "?q=%s&page=%d&limit=20" % (urllib.parse.quote(str(key or "")), page)
        try:
            j = self._get("/v1/browse/catalog" + q)
            return {"list": self._cards(j.get("cards")), "page": page}
        except Exception:
            return {"list": [], "page": page}

    # ---------------------------------------------------------------- 播放
    def playerContent(self, flag, id, vipFlags):
        tok = str(id or "")
        try:
            j = self._get("/v1/playback/resolve/%s?view=compact" % urllib.parse.quote(tok))
            lines = [x for x in (j.get("line_options") or []) if isinstance(x, dict)]
            if not lines:
                return {"parse": 1, "playUrl": "", "url": "", "header": ""}
            # 官方线路优先，其次 4K
            def rank(o):
                label = str(o.get("label") or "")
                pid = str(o.get("provider_id") or "")
                official = ("官方" in label) or pid.startswith("official") or pid.startswith("bytevod")
                return (0 if official else 1, 0 if "4K" in label.upper() else 1)
            lines.sort(key=rank)
            for o in lines:
                url = str(o.get("url") or "")
                if not url:
                    continue
                if url.startswith("resolve://"):
                    ticket = url[len("resolve://"):]
                    r = self._post("/v1/playback/resolve-line?view=compact", {"ticket": ticket})
                    line = r.get("line") or {}
                    play = str(line.get("url") or "")
                    if play.startswith("http"):
                        return {"parse": 0, "playUrl": "", "url": play,
                                "header": '{"User-Agent":"%s"}' % UA}
                elif url.startswith("http"):
                    return {"parse": 0, "playUrl": "", "url": url,
                            "header": '{"User-Agent":"%s"}' % UA}
            return {"parse": 1, "playUrl": "", "url": "", "header": ""}
        except Exception:
            return {"parse": 1, "playUrl": "", "url": "", "header": ""}
