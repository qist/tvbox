"""
czzyv.com - 厂长资源
"""

import re
import time
from urllib.parse import urljoin, quote, unquote, urlparse, parse_qs

import requests

from base.spider import Spider


class Spider(Spider):
    def __init__(self):
        self.host = "https://czzyv.com"
        self.timeout = 20
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "Referer": "https://czzyv.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        self.session = None
        self._text_cache = {}
        self._text_cache_ttl = 300
        self._api_base = ""
        self._use_api = False
        self._ua_fallback = "Dalvik/2.1.0 (Linux; U; Android 10)"

        self._class_map = [
            ("最新电影", "/zuixindianying"),
            ("豆瓣Top250", "/dbtop250"),
            ("国产剧", "/gcj"),
            ("美剧", "/meijutt"),
            ("韩剧", "/hanjutv"),
            ("日剧", "/riju"),
            ("番剧", "/fanju"),
            ("剧场版", "/dongmanjuchangban"),
            ("海外剧", "/haiwaijuqita"),
        ]

    def getName(self):
        return "厂长资源"

    def init(self, extend=""):
        if isinstance(extend, dict):
            host = (extend.get("host") or extend.get("site") or "").strip()
            if host:
                self.host = host.rstrip("/")
        elif isinstance(extend, str) and extend.strip():
            self.host = extend.strip().rstrip("/")

        self.headers["Referer"] = self.host + "/"
        self.headers["Origin"] = self.host
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self._detect_api()
        self._warmup()

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    def _detect_api(self):
        candidates = [
            "/api.php/provide/vod?ac=list",
            "/api.php/provide/vod/?ac=list",
            "/index.php/api/vod?ac=list",
        ]
        for p in candidates:
            url = urljoin(self.host + "/", p.lstrip("/"))
            try:
                r = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                ct = (r.headers.get("Content-Type") or "").lower()
                if r.status_code == 200 and (("json" in ct) or ("xml" in ct) or r.text.strip().startswith(("{", "<"))):
                    self._api_base = url.split("?", 1)[0]
                    self._use_api = True
                    return
            except Exception:
                continue
        self._api_base = ""
        self._use_api = False

    def _warmup(self):
        try:
            self.session.get(self.host + "/", timeout=self.timeout, allow_redirects=True)
        except Exception:
            pass

    def _fetch_text(self, url):
        now = time.time()
        cached = self._text_cache.get(url)
        if cached and cached[0] > now:
            return cached[1]

        try:
            r = None
            for _ in range(3):
                try:
                    r = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                    break
                except Exception:
                    time.sleep(1)
            if not r or r.status_code != 200:
                if r and r.status_code in (403, 406, 412):
                    self.session.headers["User-Agent"] = self._ua_fallback
                    try:
                        r = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                    except Exception:
                        r = None
                if not r or r.status_code != 200:
                    return ""
            r.encoding = "utf-8"
            text = r.text or ""
            if "访问已被拦截" in text or "已被拦截" in text:
                self.session.headers["User-Agent"] = self._ua_fallback
                try:
                    r2 = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                    if r2 and r2.status_code == 200:
                        r2.encoding = "utf-8"
                        text = r2.text or ""
                except Exception:
                    pass
            if text:
                self._text_cache[url] = (now + self._text_cache_ttl, text)
            return text
        except Exception:
            return ""

    def _abs(self, href):
        return urljoin(self.host + "/", href or "")

    def _parse_pagecount(self, html, current_pg):
        m = re.findall(r"/page/(\d+)", html or "")
        nums = [int(x) for x in m if x.isdigit()]
        if nums:
            return max(max(nums), current_pg)
        return 999

    def _parse_vod_list(self, html):
        html = html or ""
        vods = []

        blocks = re.findall(r"(?is)<li\b[^>]*>.*?</li>", html)
        for b in blocks:
            if "/movie/" not in b:
                continue
            m_id = re.search(r'(?is)href=["\'](?:https?://[^"\']+)?/movie/(\d+)\.html["\']', b)
            if not m_id:
                continue
            mid = m_id.group(1)

            m_alt = re.search(r'(?is)<img\b[^>]*\balt=["\']([^"\']+)["\']', b)
            name = (m_alt.group(1).strip() if m_alt else "") or mid

            m_pic = re.search(r'(?is)<img\b[^>]*(?:data-original|data-src|data-lazy-src|src)=["\']([^"\']+)["\']', b)
            pic = (m_pic.group(1).strip() if m_pic else "")

            remark = ""
            m_qb = re.search(r'(?is)<div\b[^>]*class=["\'][^"\']*\bhdinfo\b[^"\']*["\'][^>]*>.*?<span\b[^>]*>(.*?)</span>', b)
            if m_qb:
                remark = re.sub(r"(?is)<[^>]+>", "", m_qb.group(1)).strip()
            m_score = re.search(r'(?is)<div\b[^>]*class=["\'][^"\']*\brating\b[^"\']*["\'][^>]*>\s*([^<]+)\s*</div>', b)
            score = (m_score.group(1).strip() if m_score else "")
            if remark and score and score not in remark:
                remark = f"{remark} {score}"
            elif not remark:
                remark = score

            vods.append({"vod_id": mid, "vod_name": name, "vod_pic": pic, "vod_remarks": remark})

        seen = set()
        unique = []
        for v in vods:
            if v["vod_id"] in seen:
                continue
            seen.add(v["vod_id"])
            unique.append(v)
        return unique

    def homeContent(self, filter):
        result = {"class": [], "list": []}
        for name, path in self._class_map:
            result["class"].append({"type_name": name, "type_id": path})

        if self._use_api:
            return result

        html = self._fetch_text(self.host + "/")
        result["list"] = self._parse_vod_list(html)[:24]
        return result

    def homeVideoContent(self):
        return {}

    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg or 1)
        result = {"list": [], "page": pg, "pagecount": 999, "limit": 24, "total": 0}

        if self._use_api:
            return result

        if tid.startswith("http"):
            base = tid
        else:
            base = self._abs(tid)

        if pg > 1:
            if base.endswith("/"):
                url = base + f"page/{pg}"
            else:
                url = base + f"/page/{pg}"
        else:
            url = base

        html = self._fetch_text(url)
        result["list"] = self._parse_vod_list(html)
        result["pagecount"] = self._parse_pagecount(html, pg)
        result["total"] = result["pagecount"] * result["limit"]
        return result

    def detailContent(self, ids):
        if not ids or not ids[0]:
            return {"list": []}
        vid = ids[0]
        if vid.startswith("http"):
            url = vid
        else:
            url = f"{self.host}/movie/{vid}.html"

        html = self._fetch_text(url)
        name = ""
        m_title = re.search(r"(?is)<h1[^>]*>\s*([^<]+)\s*</h1>", html or "")
        if m_title:
            name = m_title.group(1).strip()

        pic = ""
        m_pic = re.search(r'(?is)<div\b[^>]*class=["\'][^"\']*\bdyimg\b[^"\']*["\'][^>]*>[\s\S]*?<img\b[^>]*(?:data-original|data-src|data-lazy-src|src)=["\']([^"\']+)["\']', html or "")
        if not m_pic:
            m_pic = re.search(r'(?is)<img\b[^>]*(?:data-original|data-src|data-lazy-src|src)=["\']([^"\']+)["\']', html or "")
        if m_pic:
            pic = m_pic.group(1).strip()

        desc = ""
        m_desc = re.search(r'(?is)<div\b[^>]*class=["\'][^"\']*\byp_context\b[^"\']*["\'][^>]*>\s*([\s\S]*?)\s*</div>', html or "")
        if m_desc:
            desc = re.sub(r"(?is)<[^>]+>", "", m_desc.group(1)).strip()

        actor = ""
        director = ""
        m_actor = re.search(r"(?is)主演：\s*([^<\n\r]+)", html or "")
        if m_actor:
            actor = m_actor.group(1).strip()
        m_director = re.search(r"(?is)导演：\s*([^<\n\r]+)", html or "")
        if m_director:
            director = m_director.group(1).strip()

        play_items = []
        for m in re.finditer(r'(?is)<a\b[^>]*href=["\']([^"\']*/v_play/[^"\']+)["\'][^>]*>\s*([^<]+)\s*</a>', html or ""):
            href = self._abs(m.group(1).strip())
            t = m.group(2).strip()
            if t and href:
                play_items.append(f"{t}${href}")

        if not play_items:
            play_items.append(f"播放${url}")

        return {
            "list": [
                {
                    "vod_id": vid,
                    "vod_name": name or vid,
                    "vod_pic": pic,
                    "vod_remarks": "",
                    "vod_year": "",
                    "type_name": "",
                    "vod_content": desc,
                    "vod_actor": actor,
                    "vod_director": director,
                    "vod_play_from": "厂长资源",
                    "vod_play_url": "#".join(play_items),
                }
            ]
        }

    def searchContent(self, key, quick, pg="1"):
        if not key:
            return {"list": []}
        if self._use_api:
            return {"list": []}
        pg = str(pg or "1")
        url = f"{self.host}/boss1O1?q={quote(key)}"
        if pg != "1":
            url += f"&page={quote(pg)}"
        html = self._fetch_text(url)
        return {"list": self._parse_vod_list(html)}

    def playerContent(self, flag, id, vipFlags):
        h = {"User-Agent": self.headers.get("User-Agent", ""), "Referer": self.host + "/"}

        if not id:
            return {"parse": 1, "url": "", "header": h, "playUrl": ""}

        if isinstance(id, str) and (".m3u8" in id or ".mp4" in id) and id.startswith("http"):
            return {"parse": 0, "url": id, "header": h, "playUrl": ""}

        play_url = id if id.startswith("http") else self._abs(id)
        if "/v_play/" not in play_url:
            return {"parse": 1, "url": play_url, "header": h, "playUrl": ""}

        html = self._fetch_text(play_url)
        m_iframe = re.search(r'(?is)<iframe\b[^>]*\bsrc=["\']([^"\']+)["\']', html or "")
        if m_iframe:
            src = m_iframe.group(1).strip()
            if src:
                qs = parse_qs(urlparse(src).query)
                raw = (qs.get("url") or [""])[0]
                raw = unquote(raw).strip()
                if raw.startswith("http"):
                    return {"parse": 0, "url": raw, "header": h, "playUrl": ""}
                return {"parse": 1, "url": src, "header": h, "playUrl": ""}

        m = re.findall(r'https?://[^\s"\']+?\.(?:m3u8|mp4)(?:\?[^\s"\']*)?', html or "")
        if m:
            return {"parse": 0, "url": m[0], "header": h, "playUrl": ""}

        return {"parse": 1, "url": play_url, "header": h, "playUrl": ""}

    def localProxy(self, param):
        return None
