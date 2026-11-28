# -*- coding: utf-8 -*-
# 重写版：采集站直连（弃 TMDB API），requests 实现，兼容 FongMi/TVBox py 源
import sys, os, re, json, time, html as html_lib, urllib.parse, requests

try:
    from base.spider import Spider as BaseSpider
except ImportError:
    BaseSpider = object

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
TIMEOUT = 8

SITES = [
    {"name": "魔都资源", "host": "https://www.mdzyapi.com/api.php/provide/vod/", "backup": []},
    {"name": "丫丫资源", "host": "https://api.yyzy-tv.vip/inc/apijson.php", "backup": []},
    {"name": "量子资源", "host": "https://cj.lziapi.com/api.php/provide/vod/from/lzm3u8/", "backup": ["https://cj.lziapi.com/api.php/provide/vod/"]},
    {"name": "母鸡资源", "host": "https://mujiziyuan00.com/api.php/provide/vod/", "backup": []},
    {"name": "非凡资源", "host": "https://api.ffzyapi.com/api.php/provide/vod/", "backup": ["http://cj.ffzyapi.com/api.php/provide/vod/"]},
    {"name": "360资源", "host": "https://360zy.com/api.php/provide/vod/", "backup": []},
    {"name": "红牛资源", "host": "https://www.hongniuzy3.com/api.php/provide/vod/", "backup": ["https://hongniuzy2.com/api.php/provide/vod/"]},
    {"name": "百度资源", "host": "https://api.apibdzy.com/api.php/provide/vod/", "backup": []},
    {"name": "爱旦资源", "host": "https://lovedan.net/api.php/provide/vod/", "backup": []},
    {"name": "爱奇艺资源", "host": "https://iqiyizyapi.com/api.php/provide/vod/", "backup": []},
    {"name": "最大资源", "host": "http://zuidazy.me/api.php/provide/vod/", "backup": []},
    {"name": "蘑菇资源", "host": "https://www.5o5k.com/api.php/provide/vod/", "backup": []},
    {"name": "星球资源", "host": "http://www.ysxq.cc/api.php/provide/vod/", "backup": []},
    {"name": "极速资源", "host": "https://jszyapi.com/api.php/provide/vod/from/jsm3u8/at/json", "backup": []},
    {"name": "金鹰资源", "host": "https://jinyingzy.com/api.php/provide/vod/", "backup": []},
    {"name": "海豚资源", "host": "https://hhzyapi.com/api.php/provide/vod/", "backup": []},
    {"name": "新浪资源", "host": "https://api.xinlangapi.com/xinlangapi.php/provide/vod/", "backup": []},
    {"name": "暴风资源", "host": "https://bfzyapi.com/api.php/provide/vod/", "backup": []},
    {"name": "猫眼资源", "host": "https://api.maoyanapi.top/api.php/provide/vod/", "backup": []},
    {"name": "U酷资源", "host": "https://api.ukuapi88.com/api.php/provide/vod/", "backup": []},
    {"name": "电影天堂", "host": "http://caiji.dyttzyapi.com/api.php/provide/vod/", "backup": []},
]

class Spider(BaseSpider):
    def __init__(self):
        self.sites = [dict(s) for s in SITES]
        self.session = requests.Session()
        self.session.verify = False
        try:
            requests.packages.urllib3.disable_warnings()
        except Exception:
            pass
        self._cache = {}
        self._cur_site = -1
        self._last_err = ""

    def getName(self):
        return "TMDB多线影视"

    def init(self, extend=""):
        self._cache = {}
        self._last_err = ""
        return True

    def isVideoFormat(self, url):
        u = str(url or "").lower()
        return ".m3u8" in u or ".mp4" in u or ".flv" in u or ".mkv" in u

    def manualVideoCheck(self):
        return False

    def destroy(self):
        self._cache = {}
        return None

    def _fetch_json(self, url, timeout=TIMEOUT):
        try:
            r = self.session.get(url, headers={
                "User-Agent": UA,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }, timeout=timeout)
            if r.status_code != 200:
                return None
            try:
                return r.json()
            except Exception:
                return None
        except Exception as e:
            self._last_err = str(e)
            return None

    def _site_url(self, idx, params):
        base = self.sites[idx]["host"]
        q = urllib.parse.urlencode(params)
        sep = "&" if "?" in base else "?"
        return base + sep + q

    def _site_call(self, idx, params, timeout=TIMEOUT):
        return self._fetch_json(self._site_url(idx, params), timeout)

    def _ensure_site(self):
        if self._cur_site >= 0:
            return self._cur_site
        for i in range(len(self.sites)):
            d = self._site_call(i, {"ac": "list"}, 6)
            if d and d.get("code") == 1 and d.get("class"):
                self._cur_site = i
                return i
        self._cur_site = 0
        return 0

    def _card(self, it):
        return {
            "vod_id": str(it.get("vod_id", "")),
            "vod_name": it.get("vod_name", ""),
            "vod_pic": it.get("vod_pic", ""),
            "vod_remarks": it.get("vod_remarks", ""),
            "vod_year": it.get("vod_year", ""),
            "vod_actor": it.get("vod_actor", ""),
            "vod_director": it.get("vod_director", ""),
            "vod_content": it.get("vod_content", ""),
        }

    def homeContent(self, filter=False):
        idx = self._ensure_site()
        d = self._site_call(idx, {"ac": "list"})
        classes = []
        if d and d.get("class"):
            for c in d["class"]:
                classes.append({"type_name": str(c.get("type_name", "")),
                                "type_id": str(c.get("type_id", ""))})
        result = {"class": classes}
        if filter:
            result["filters"] = {}
        return result

    def homeVideoContent(self):
        d = self._site_call(self._ensure_site(), {"ac": "videolist", "pg": 1})
        lst = []
        if d and d.get("list"):
            for it in d["list"][:12]:
                lst.append(self._card(it))
        return {"list": lst}

    def categoryContent(self, tid, pg=1, filter=False, extend=None):
        try:
            page = int(pg or 1)
        except Exception:
            page = 1
        params = {"ac": "videolist", "pg": page}
        if tid:
            params["t"] = str(tid)
        idx = self._ensure_site()
        d = self._site_call(idx, params)
        lst = []
        if d and d.get("list"):
            for it in d["list"]:
                lst.append(self._card(it))
        pagecount = int(d.get("pagecount", page + 1)) if d else page + 1
        total = int(d.get("total", len(lst))) if d else len(lst)
        return {"page": page, "pagecount": pagecount, "limit": len(lst),
                "total": total, "list": lst}

    def detailContent(self, ids):
        raw = ""
        if isinstance(ids, (list, tuple)) and ids:
            raw = str(ids[0])
        elif ids:
            raw = str(ids)
        raw = raw.strip().split("?")[0]
        idx = self._ensure_site()
        d = self._site_call(idx, {"ac": "detail", "ids": raw})
        raw_list = []
        if d and d.get("list"):
            raw_list = d["list"]
        if not raw_list:
            d2 = self._site_call(idx, {"ac": "videolist", "ids": raw})
            if d2 and d2.get("list"):
                raw_list = d2["list"]
        out = []
        for it in raw_list:
            card = self._card(it)
            card["vod_play_from"] = it.get("vod_play_from", "")
            card["vod_play_url"] = it.get("vod_play_url", "")
            out.append(card)
        return {"list": out}

    def _pick_url(self, play_url, flag):
        if not play_url:
            return ""
        parts = [x for x in str(play_url).split("#") if x]
        # flag 可能是线路名或集名
        for p in parts:
            if "$" in p:
                name, url = p.split("$", 1)
                if flag and (flag in name or name in flag):
                    return url
        if parts:
            p = parts[0]
            return p.split("$", 1)[1] if "$" in p else p
        return play_url

    def playerContent(self, flag, id, vipFlags=None):
        url = str(id or "").strip()
        if not url:
            return {"parse": 0, "playUrl": "", "url": "", "header": {"User-Agent": UA}}
        if url.startswith("http"):
            return {"parse": 0, "playUrl": "", "url": url, "header": {"User-Agent": UA}}
        # pid 是 vod_id，从详情取播放
        d = self.detailContent([url])
        if d.get("list"):
            it = d["list"][0]
            pu = it.get("vod_play_url", "")
            return {"parse": 0, "playUrl": "", "url": self._pick_url(pu, flag),
                    "header": {"User-Agent": UA}}
        return {"parse": 0, "playUrl": "", "url": "", "header": {"User-Agent": UA}}

    def searchContent(self, key, quick, pg="1"):
        p = pg or "1"
        idx = self._ensure_site()
        d = self._site_call(idx, {"ac": "videolist", "wd": str(key), "pg": p})
        lst = []
        if d and d.get("list"):
            for it in d["list"]:
                lst.append(self._card(it))
        return {"list": lst}

    def localProxy(self, params):
        return None


if __name__ == "__main__":
    sp = Spider()
    sp.init({})
    hc = sp.homeContent(False)
    print("分类数:", len(hc["class"]), "| 主站:", sp.sites[sp._cur_site]["name"])
    print("前6分类:", [c["type_name"] for c in hc["class"]][:6])
    if hc["class"]:
        tid = hc["class"][0]["type_id"]
        cc = sp.categoryContent(tid, 1, False, {})
        print("分类[%s] 列表:" % tid, len(cc["list"]))
        if cc["list"]:
            it = cc["list"][0]
            print("  样例:", it["vod_name"], "| play_from:", it["vod_play_from"][:30])
            det = sp.detailContent([it["vod_id"]])
            if det["list"]:
                v = det["list"][0]
                print("  详情:", v["vod_name"], "| play_url 前80:", str(v["vod_play_url"])[:80])
                pc = sp.playerContent("", v["vod_id"])
                print("  player:", pc["url"][:80])
