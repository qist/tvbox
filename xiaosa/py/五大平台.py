# -*- coding: utf-8 -*-
"""
五平台聚合爬虫（TVBox Python 格式）
====================================
平台：腾讯视频 / 爱奇艺 / 优酷 / 芒果TV / 哔哩哔哩

接口约定（TVBox py 爬虫）：
  - 类名必须为 Spider，继承 base.spider.Spider
  - 各方法返回 dict，由 TVBox 引擎序列化
  - playerContent 返回 parse=1 + jx=1 表示交由外部解析播放

播放策略：
  - 哔哩哔哩：优先调用官方 playurl 接口返回直链（parse=0），失败回退播放页外挂解析
  - 腾讯/爱奇艺/优酷/芒果：输出官方播放页地址，parse=1 交由外部解析
"""

import re
import json
import time
import hashlib
import threading

# ---------- 壳子兼容层 ----------
# TVBox / OK影视(影视仓) 的 Python 引擎为 Jython 2.7，没有 urllib.parse/urllib.request/urllib.error，
# 且 urllib2 不支持 method= / context= 参数。这里做 Py3/Py2 双兼容，_quote 统一处理中文编码。
try:  # Python 3
    from urllib.parse import quote as _quote
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError

    def _q(s):
        return _quote(str(s), safe="/")

    _PY2 = False
except Exception:  # Jython 2.7 / Python 2 (TVBox/OK影视)
    from urllib import quote as _quote
    from urllib2 import Request, urlopen, URLError, HTTPError

    def _q(s):
        if isinstance(s, unicode):
            s = s.encode("utf-8")
        return _quote(str(s), safe="/")

    _PY2 = True

try:
    import requests as _rq
except Exception:
    _rq = None

try:
    from base.spider import Spider
except Exception:
    class Spider(object):
        pass

UA_PC = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
UA_MB = "Mozilla/5.0 (Linux; Android 12; Pixel 6 Build/SQ3A.220705.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/106.0.5249.126 Mobile Safari/537.36"

# 各平台播放页 Referer
HDR_REF = {
    "tx": "https://v.qq.com/",
    "iq": "https://www.iqiyi.com/",
    "yk": "https://www.youku.com/",
    "mg": "https://www.mgtv.com/",
    "bl": "https://www.bilibili.com/",
}

# 腾讯频道映射（getMVLPage channel_id）
TX_CHANNEL = {
    "movie": "100173", "tv": "100113", "mini_series": "120188",
    "variety": "100109", "cartoon": "100119", "child": "100150", "doco": "100105",
}

# B站 PGC 分类（season_type）
BL_CATE = {"1": "番剧", "4": "国创", "2": "电影", "5": "电视剧", "3": "纪录片", "7": "综艺"}


def _http(method, url, headers=None, body=None, timeout=15):
    """统一 HTTP 请求：优先 requests，缺失时兜底 urllib（兼容 Jython2/Py2）。
    返回 (status, text)，text 强制 UTF-8 解码，避免壳子编码推断不一致乱码。"""
    hdrs = {"User-Agent": UA_PC, "Accept": "*/*"}
    if headers:
        hdrs.update(headers)
    data = body.encode("utf-8") if isinstance(body, str) else body
    try:
        if _rq is not None:
            r = _rq.request(method.upper(), url, headers=hdrs, data=data,
                            timeout=timeout, verify=False)
            return r.status_code, r.content.decode("utf-8", "ignore")
        req = Request(url, data=data, headers=hdrs)
        try:
            import ssl
            ctx = ssl.create_unverified_context()
        except Exception:
            ctx = None
        if ctx is not None:
            try:
                with urlopen(req, timeout=timeout, context=ctx) as resp:
                    return resp.getcode(), resp.read().decode("utf-8", "ignore")
            except TypeError:  # Py2/Jython 的 urlopen 不支持 context 参数
                pass
        with urlopen(req, timeout=timeout) as resp:
            return resp.getcode(), resp.read().decode("utf-8", "ignore")
    except Exception:
        return 0, ""


def _jload(txt):
    """容错 JSON 解析（兼容 QZOutputJson= 前缀）"""
    if not txt:
        return {}
    txt = txt.strip()
    i = txt.find("{")
    if i < 0:
        return {}
    try:
        return json.loads(txt[i:])
    except Exception:
        try:
            return json.loads(txt[i:].rstrip(";"))
        except Exception:
            return {}


def _clean(s):
    if not s:
        return ""
    return re.sub(r"</?em[^>]*>", "", str(s)).strip()


class Spider(Spider):

    def getName(self):
        return "五平台聚合"

    def init(self, extend=""):
        self.host = ""
        self.headers = {"User-Agent": UA_PC}
        self.ext = extend or ""

    # ================================================================
    #  工具
    # ================================================================
    def _mk_vod(self, vid, name, pic, remarks="", **kw):
        v = {
            "vod_id": vid, "vod_name": name, "vod_pic": pic or "",
            "vod_year": kw.get("year", ""), "vod_area": kw.get("area", ""),
            "vod_remarks": remarks or "", "vod_actor": kw.get("actor", ""),
            "vod_director": kw.get("director", ""), "vod_content": kw.get("content", ""),
            "type_name": kw.get("type_name", ""),
        }
        return v

    def _page(self, pg, items, total=None):
        return {
            "page": int(pg or 1), "pagecount": 99, "limit": len(items),
            "total": total if total is not None else len(items), "list": items,
        }

    # ================================================================
    #  腾讯视频
    # ================================================================
    def _tx_search(self, key, pg):
        body = json.dumps({
            "version": "25042201", "clientType": 1, "filterValue": "",
            "uuid": "B1E50847-D25F-4C4B-BBA0-36F0093487F6", "retry": 0,
            "query": key, "pagenum": int(pg or 1) - 1, "isPrefetch": True,
            "pagesize": 30, "queryFrom": 0, "searchDatakey": "", "transInfo": "",
            "isneedQc": True, "preQid": "", "adClientInfo": "",
            "extraInfo": {"isNewMarkLabel": "1", "multi_terminal_pc": "1",
                          "themeType": "1", "sugRelatedIds": "{}", "appVersion": ""},
        })
        st, txt = _http("POST", "https://pbaccess.video.qq.com/trpc.videosearch.mobile_search.MultiTerminalSearch/MbSearch?vplatform=2",
                        headers={"Content-Type": "application/json", "Origin": "https://v.qq.com",
                                 "Referer": "https://v.qq.com/"}, body=body)
        j = _jload(txt)
        items = (j.get("data") or {}).get("normalList", {}).get("itemList", []) or []
        bad = ("预告", "花絮", "片花", "特辑", "幕后", "采访", "制作", "MV", "主题曲",
               "插曲", "彩蛋", "精彩", "集锦", "盘点", "回顾", "解说", "评测")
        out, seen = [], set()
        for it in items:
            vi = it.get("videoInfo") or {}
            title = _clean(vi.get("title"))
            if not title or not vi:
                continue
            if any(k in title for k in bad):
                continue
            cid = (it.get("doc") or {}).get("id")
            if not cid or cid in seen:
                continue
            seen.add(cid)
            img = vi.get("imgUrl") or ""
            if img.startswith("//"):
                img = "https:" + img
            out.append(self._mk_vod("tx|" + cid, title, img,
                                    remarks=vi.get("secondLine") or "",
                                    year=vi.get("year") or "", type_name="腾讯视频"))
        return out

    def _tx_cate(self, ch, pg):
        chid = TX_CHANNEL.get(ch, "100173")
        body = json.dumps({"page_params": {"page_type": "operation", "page_id": "channel_list",
                                           "channel_id": chid, "filter_params": "sort=75"}})
        st, txt = _http("POST", "https://pbaccess.video.qq.com/trpc.multi_vector_layout.mvl_controller.MVLPageHTTPService/getMVLPage?&vversion_platform=2",
                        headers={"Content-Type": "application/json", "Origin": "https://v.qq.com",
                                 "Referer": "https://v.qq.com/"}, body=body)
        j = _jload(txt)
        if j.get("ret") != 0:
            return []
        cards = ((j.get("data") or {}).get("modules") or {}).get("normal", {}).get("cards", []) or []
        out = []
        for c in cards:
            cl = (c.get("children_list") or {}).get("poster_card") or {}
            for it in (cl.get("cards") or []):
                p = it.get("params") or {}
                cid, title = p.get("cid") or "", _clean(p.get("title"))
                if not cid or not title:
                    continue
                img = p.get("new_pic_hz") or p.get("new_pic_vt") or ""
                if img.startswith("//"):
                    img = "https:" + img
                if img.endswith("/"):
                    img += "0"
                out.append(self._mk_vod("tx|" + cid, title, img,
                                        remarks=p.get("episode_updated") or p.get("marklabel_0_prime_text") or "",
                                        type_name="腾讯视频"))
        return out

    def _tx_detail(self, cid):
        st, txt = _http("GET", "https://node.video.qq.com/x/api/float_vinfo2?cid=" + cid,
                        headers={"Referer": "https://v.qq.com/"})
        j = _jload(txt)
        c = j.get("c") or {}
        title = _clean(c.get("title")) or cid
        typ = c.get("type") if isinstance(c.get("type"), list) else []
        nam = c.get("nam") if isinstance(c.get("nam"), list) else []
        pic = c.get("pic") or ""
        if pic.startswith("//"):
            pic = "https:" + pic
        vod = self._mk_vod("tx|" + cid, title, pic,
                           remarks=c.get("rec") or "", year=c.get("year") or "",
                           actor=",".join([x for x in nam if x]), content=c.get("description") or "",
                           type_name=",".join([x for x in typ if x]))
        vids = c.get("video_ids") or []
        eps = []
        if vids:
            for i in range(0, len(vids), 30):
                batch = vids[i:i + 30]
                u = ("https://union.video.qq.com/fcgi-bin/data?otype=json&tid=1804&appid=20001238"
                     "&appkey=6c03bbe9658448a4&union_platform=1&idlist=" + ",".join(batch))
                st2, txt2 = _http("GET", u, headers={"Referer": "https://v.qq.com/"})
                j2 = _jload(txt2)
                for r in (j2.get("results") or []):
                    f = r.get("fields") or {}
                    vid = f.get("vid")
                    if not vid:
                        continue
                    eps.append("%s$https://v.qq.com/x/cover/%s/%s.html" % (
                        _clean(f.get("title")) or ("第%s集" % f.get("video_checkup_time", "")), cid, vid))
        if not eps:
            for v in vids:
                eps.append("正片$https://v.qq.com/x/cover/%s/%s.html" % (cid, v))
        vod["vod_play_from"] = "腾讯视频"
        vod["vod_play_url"] = "#".join(eps)
        return vod

    # ================================================================
    #  爱奇艺
    # ================================================================
    def _iq_search(self, key, pg):
        u = ("https://search.video.iqiyi.com/o?if=html5&key=%s&pageNum=%s&pos=1&pageSize=24&site=iqiyi"
             % (_q(key), pg or 1))
        st, txt = _http("GET", u, headers={"Referer": "https://www.iqiyi.com/"})
        j = _jload(txt)
        docs = (j.get("data") or {}).get("docinfos", []) or []
        out = []
        for d in docs:
            a = d.get("albumDocInfo")
            if not a or not a.get("albumId"):
                continue
            img = a.get("albumVImage") or a.get("albumHImage") or ""
            if img.startswith("//"):
                img = "https:" + img
            ch = (a.get("channel") or "").split(",")[0]
            out.append(self._mk_vod("iq|%s" % a.get("albumId"), _clean(a.get("albumTitle")), img,
                                    remarks=ch, type_name=ch))
        return out

    def _iq_cate(self, cid, pg):
        if str(cid) == "16":
            u = ("https://pcw-api.iqiyi.com/search/recommend/list?channel_id=1&data_type=1"
                 "&page_id=%s&ret_num=48&three_category_id=27401" % (pg or 1))
        elif str(cid) == "5":
            u = ("https://pcw-api.iqiyi.com/search/recommend/list?channel_id=5&data_type=2"
                 "&page_id=%s&ret_num=48" % (pg or 1))
        else:
            u = ("https://pcw-api.iqiyi.com/search/recommend/list?channel_id=%s&data_type=1"
                 "&page_id=%s&ret_num=48" % (cid, pg or 1))
        st, txt = _http("GET", u, headers={"Referer": "https://www.iqiyi.com/"})
        j = _jload(txt)
        lst = (j.get("data") or {}).get("list", []) or []
        out = []
        for it in lst:
            aid = it.get("albumId")
            if not aid:
                continue
            lc, vc = it.get("latestOrder"), it.get("videoCount")
            rem = ""
            if it.get("channelId") in (2, 4):
                rem = ("%s集全" % lc) if (lc and vc and str(lc) == str(vc)) else ("更新至 %s集" % lc)
            elif it.get("period"):
                rem = it.get("period")
            elif it.get("focus"):
                rem = it.get("focus")
            sc = it.get("score")
            if sc:
                rem = ("%s分\t" % sc) + rem
            out.append(self._mk_vod("iq|%s" % aid, _clean(it.get("name")), it.get("imageUrl") or "",
                                    remarks=rem, year=(it.get("period") or "")[:4],
                                    content=it.get("description") or "", type_name="爱奇艺"))
        return out

    def _iq_detail(self, aid):
        u = ("https://pcw-api.iqiyi.com/video/video/videoinfowithuser/%s?agent_type=1&authcookie=&subkey=%s&subscribe=1"
             % (aid, aid))
        st, txt = _http("GET", u, headers={"Referer": "https://www.iqiyi.com/"})
        d = (_jload(txt).get("data") or {})
        if not d:
            return None
        cats = d.get("categories") if isinstance(d.get("categories"), list) else []
        ppl = d.get("people") if isinstance(d.get("people"), dict) else {}
        actors = ""
        mc = ppl.get("main_charactor") if isinstance(ppl.get("main_charactor"), list) else []
        if mc:
            actors = ",".join([x.get("name", "") for x in mc if isinstance(x, dict)])
        img = d.get("imageUrl") or ""
        if img.startswith("//"):
            img = "https:" + img
        rem = ""
        if d.get("latestOrder"):
            rem = "更新至 第%s集(期)/共%s集(期)" % (d.get("latestOrder"), d.get("videoCount"))
        elif d.get("period"):
            rem = d.get("period")
        if d.get("score"):
            rem = ("评分：%s " % d.get("score")) + rem
        vod = self._mk_vod("iq|%s" % aid, _clean(d.get("name")), img, remarks=rem,
                           year=(d.get("period") or "")[:4], actor=actors,
                           content=d.get("description") or "",
                           type_name=",".join([c.get("name", "") for c in cats if isinstance(c, dict)]))
        eps = []
        if d.get("channelId") in (1, 5) and d.get("playUrl"):
            eps.append("正片$%s" % d.get("playUrl"))
        else:
            page = 1
            while True:
                u2 = "https://pcw-api.iqiyi.com/albums/album/avlistinfo?aid=%s&size=200&page=%s" % (aid, page)
                st2, txt2 = _http("GET", u2, headers={"Referer": "https://www.iqiyi.com/"})
                d2 = (_jload(txt2).get("data") or {})
                el = d2.get("epsodelist") or []
                for e in el:
                    pu = e.get("playUrl") or ""
                    if pu:
                        eps.append("%s$%s" % (_clean(e.get("name")) or ("第%s集" % e.get("order", "")), pu))
                total = d2.get("total") or 0
                if len(el) < 200 or page * 200 >= int(total):
                    break
                page += 1
                if page > 20:
                    break
        vod["vod_play_from"] = "爱奇艺"
        vod["vod_play_url"] = "#".join(eps)
        return vod

    # ================================================================
    #  优酷
    # ================================================================
    def _yk_search(self, key, pg):
        u = "https://search.youku.com/api/search?pg=%s&keyword=%s" % (pg or 1, _q(key))
        st, txt = _http("GET", u, headers={"Referer": "https://www.youku.com/"})
        j = _jload(txt)
        out = []
        for it in (j.get("pageComponentList") or []):
            cd = it.get("commonData")
            if not cd:
                continue
            sid = cd.get("showId")
            if not sid:
                continue
            td = cd.get("titleDTO") or {}
            pd = cd.get("posterDTO") or {}
            feature = cd.get("feature") or ""
            parts = [x.strip() for x in feature.split("·") if x.strip()]
            year = parts[0] if parts and parts[0].isdigit() else ""
            area = parts[-1] if len(parts) > 1 else ""
            director = re.sub(r"^导演：", "", (cd.get("director") or "").strip())
            actor = re.sub(r"^演员：", "", (cd.get("notice") or "").strip())
            out.append(self._mk_vod("yk|" + sid, _clean(td.get("displayName")), pd.get("vThumbUrl") or "",
                                    remarks=feature, year=year, area=area,
                                    actor=actor, director=director, type_name="优酷"))
        return out

    def _yk_cate(self, name, pg):
        params = _q(json.dumps({"type": name}, ensure_ascii=False))
        u = "https://www.youku.com/category/data?optionRefresh=1&pageNo=%s&params=%s" % (pg or 1, params)
        st, txt = _http("GET", u, headers={"Referer": "https://www.youku.com/",
                                           "Accept": "application/json"})
        j = _jload(txt)
        fd = (j.get("data") or {}).get("filterData") or {}
        lst = fd.get("listData") or []
        out = []
        for it in lst:
            link = it.get("videoLink") or ""
            m = re.search(r"id_([\w=]+)\.html", link)
            vid = m.group(1) if m else ""
            if not vid:
                continue
            out.append(self._mk_vod("yk|" + vid, _clean(it.get("title")), it.get("img") or "",
                                    remarks=it.get("subTitle") or "", content=it.get("summary") or "",
                                    type_name=name))
        return out

    def _yk_detail(self, sid):
        u = "https://search.youku.com/api/search?appScene=show_episode&showIds=" + sid
        st, txt = _http("GET", u, headers={"Referer": "https://www.youku.com/"})
        j = _jload(txt)
        sl = j.get("serisesList") or j.get("seriesList") or []
        src = j.get("sourceName") or "优酷"
        eps = []
        for it in sl:
            vid = it.get("videoId")
            if not vid:
                continue
            title = _clean(it.get("title")) or it.get("displayName") or ""
            eps.append("%s$https://v.youku.com/v_show/id_%s.html" % (title, vid))
        vod = self._mk_vod("yk|" + sid, sid, "", remarks=src, type_name=src)
        if sl:
            vod["vod_name"] = re.sub(r"\d+", "", _clean(sl[0].get("title")) or "") or src
        vod["vod_play_from"] = src
        vod["vod_play_url"] = "#".join(eps)
        return vod

    # ================================================================
    #  芒果TV
    # ================================================================
    def _mg_search(self, key, pg):
        d = {}
        for u in ("https://mobileso.bz.mgtv.com/msite/search/v2?q=%s&pn=%s&pc=10" % (_q(key), pg or 1),
                  "https://mobileso.bz.mgtv.com/pc/search/v1?q=%s&pn=%s&pc=10" % (_q(key), pg or 1)):
            st, txt = _http("GET", u, headers={"Referer": "https://www.mgtv.com/", "User-Agent": UA_MB})
            j = _jload(txt)
            d = j.get("data") or {}
            if d.get("contents") or d.get("listItems"):
                break
        raws = []
        for c in (d.get("contents") or []):
            if c.get("type") == "media" and isinstance(c.get("data"), list):
                raws.extend(c["data"])
        if not raws:
            raws = d.get("listItems") or []
        out = []
        for it in raws:
            if not isinstance(it, dict):
                continue
            vid = it.get("playPartId") or it.get("videoId") or it.get("video_id")
            title = _clean(it.get("title"))
            if not vid or not title:
                continue
            rc = it.get("rightCorner")
            rem = ""
            if isinstance(rc, dict):
                rem = rc.get("text") or ""
            if it.get("updateInfo"):
                rem = (rem + " " + it.get("updateInfo")).strip()
            img = it.get("img") or it.get("imgUrlH") or ""
            out.append(self._mk_vod("mg|" + str(vid), title, img, remarks=rem,
                                    year=it.get("year") or "", actor=it.get("subtitle") or "",
                                    content=it.get("story") or "", type_name="芒果TV"))
        return out

    def _mg_cate(self, ch, pg):
        u = ("https://pianku.api.mgtv.com/rider/list/pcweb/v3?platform=pcweb&channelId=%s&pn=%s&pc=30"
             "&hudong=1&_support=10000000&kind=a1&area=a1" % (ch, pg or 1))
        st, txt = _http("GET", u, headers={"Referer": "https://www.mgtv.com/"})
        j = _jload(txt)
        hd = (j.get("data") or {}).get("hitDocs") or []
        out = []
        for it in hd:
            vid = it.get("playPartId")
            if not vid:
                continue
            rc = it.get("rightCorner")
            rem = it.get("updateInfo") or ""
            if isinstance(rc, dict) and rc.get("text"):
                rem = (rc.get("text") + " " + rem).strip()
            out.append(self._mk_vod("mg|" + str(vid), _clean(it.get("title")), it.get("img") or "",
                                    remarks=rem, year=it.get("year") or "",
                                    actor=it.get("subtitle") or "", content=it.get("story") or "",
                                    type_name="芒果TV"))
        return out

    def _mg_detail(self, vid):
        u = "https://pcweb.api.mgtv.com/episode/list?page=1&size=50&video_id=" + str(vid)
        st, txt = _http("GET", u, headers={"Referer": "https://www.mgtv.com/"})
        d = (_jload(txt).get("data") or {})
        info = d.get("info") if isinstance(d.get("info"), dict) else {}
        lst = d.get("list") or []
        series = d.get("series") or []
        title = _clean(info.get("title")) or _clean(info.get("videoName")) or str(vid)
        eps = []
        for e in lst:
            url = e.get("url") or ""
            if not url:
                continue
            if not url.startswith("http"):
                url = "https://www.mgtv.com" + url
            t = e.get("t4") or e.get("t1") or "正片"
            eps.append("%s$%s" % (t, url))
        if not eps and series:
            url = series[0].get("url") or ""
            if url:
                if not url.startswith("http"):
                    url = "https://www.mgtv.com" + url
                eps.append("正片$" + url)
        vod = self._mk_vod("mg|" + str(vid), title, info.get("img") or "",
                           remarks=info.get("updateInfo") or "", year=info.get("year") or "",
                           actor=info.get("subtitle") or "", content=info.get("story") or "",
                           type_name="芒果TV")
        vod["vod_play_from"] = "芒果TV"
        vod["vod_play_url"] = "#".join(eps)
        return vod

    # ================================================================
    #  哔哩哔哩
    # ================================================================
    _WBI_TAB = [46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49, 33, 9,
                42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1,
                60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52]

    def _bl_mixin(self):
        st, txt = _http("GET", "https://api.bilibili.com/x/web-interface/nav",
                        headers={"Referer": "https://www.bilibili.com/"})
        j = _jload(txt)
        wi = (j.get("data") or {}).get("wbi_img") or {}
        img_key = (wi.get("img_url") or "").rsplit("/", 1)[-1].split(".")[0]
        sub_key = (wi.get("sub_url") or "").rsplit("/", 1)[-1].split(".")[0]
        orig = img_key + sub_key
        if len(orig) < 32:
            return ""
        return "".join(orig[self._WBI_TAB[i]] for i in range(32))

    def _bl_search(self, key, pg):
        mixin = self._bl_mixin()
        if not mixin:
            return []
        params = {"keyword": key, "page": int(pg or 1), "page_size": 20,
                  "platform": "pc", "wts": int(time.time())}
        q = "&".join("%s=%s" % (k, _q(str(params[k]).replace("!", "").replace("'", "").replace("(", "").replace(")", "")))
                     for k in sorted(params))
        w_rid = hashlib.md5((q + mixin).encode("utf-8")).hexdigest()
        u = "https://api.bilibili.com/x/web-interface/wbi/search/all/v2?%s&w_rid=%s" % (q, w_rid)
        st, txt = _http("GET", u, headers={"Referer": "https://www.bilibili.com/"})
        j = _jload(txt)
        if j.get("code") != 0:
            return []
        out = []
        for cat in ((j.get("data") or {}).get("result") or []):
            if cat.get("result_type") not in ("media_bangumi", "media_ft"):
                continue
            for v in (cat.get("data") or []):
                sid = v.get("season_id")
                title = _clean(v.get("title"))
                if not sid or not title or "预告" in title:
                    continue
                out.append(self._mk_vod("bl|%s" % sid, title, v.get("cover") or "",
                                        remarks=_clean(v.get("index_show") or ""),
                                        type_name="哔哩哔哩"))
        return out

    def _bl_cate(self, stype, pg):
        u = ("https://api.bilibili.com/pgc/season/rank/web/list?season_type=%s&pagesize=20&page=%s&day=3"
             % (stype, pg or 1))
        st, txt = _http("GET", u, headers={"Referer": "https://www.bilibili.com/"})
        j = _jload(txt)
        lst = (j.get("result") or {}).get("list") or (j.get("data") or {}).get("list") or []
        out = []
        for v in lst:
            sid = v.get("season_id")
            title = _clean(v.get("title"))
            if not sid or not title or "预告" in title:
                continue
            ne = v.get("new_ep") or {}
            rem = ne.get("index_show") or v.get("index_show") or ""
            if v.get("rating"):
                rem = ("%s分 " % v.get("rating")) + rem
            out.append(self._mk_vod("bl|%s" % sid, title, v.get("cover") or "",
                                    remarks=rem, type_name=BL_CATE.get(str(stype), "哔哩哔哩")))
        return out

    def _bl_detail(self, sid):
        u = "https://api.bilibili.com/pgc/view/web/season?season_id=" + str(sid)
        st, txt = _http("GET", u, headers={"Referer": "https://www.bilibili.com/"})
        r = (_jload(txt).get("result") or {})
        if not r:
            return None
        pub = r.get("publish") or {}
        ne = r.get("new_ep") or {}
        areas = r.get("areas") or []
        rating = r.get("rating") or {}
        stat = r.get("stat") or {}
        status = "弹幕: %s 点赞: %s 追番: %s" % (
            stat.get("danmakus", ""), stat.get("likes", ""), stat.get("favorites", ""))
        score = ("评分: %s %s" % (rating.get("score"), rating.get("subtitle", ""))) if rating else "暂无评分"
        vod = self._mk_vod("bl|%s" % sid, _clean(r.get("title")), r.get("cover") or "",
                           remarks=ne.get("desc") or "", year=(pub.get("pub_time") or "")[:4],
                           area=(areas[0].get("name") if areas and isinstance(areas[0], dict) else ""),
                           actor=status, director=score, content=r.get("evaluate") or "",
                           type_name=r.get("share_sub_title") or "哔哩哔哩")
        direct, pages = [], []
        for ep in (r.get("episodes") or []):
            t = _clean(ep.get("title")) or ""
            badge = ep.get("badge") or ""
            if "预告" in t or "预告" in badge:
                continue
            name = (t + " " + _clean(ep.get("long_title") or "")).strip()
            ep_id, cid, link = ep.get("ep_id"), ep.get("cid"), ep.get("link") or ""
            if ep_id and cid:
                direct.append("%s$blplay|%s|%s|%s" % (name, ep_id, cid, link))
            if link:
                pages.append("%s$%s" % (name, link))
        vod["vod_play_from"] = "$$$".join([x for x in (["B站直链"] if direct else []) + (["B站播放页"] if pages else [])])
        vod["vod_play_url"] = "$$$".join([x for x in (["#".join(direct)] if direct else []) + (["#".join(pages)] if pages else [])])
        return vod

    def _bl_play(self, ep_id, cid):
        u = ("https://api.bilibili.com/pgc/player/web/playurl?ep_id=%s&cid=%s&fnval=16&qn=64"
             "&fnver=0&fourk=0&session=&device=pc&platform=web&otype=json" % (ep_id, cid))
        st, txt = _http("GET", u, headers={"Referer": "https://www.bilibili.com/"})
        res = (_jload(txt).get("result") or {})
        if res.get("durl"):
            return res["durl"][0].get("url") or ""
        dash = res.get("dash") or {}
        if dash.get("video"):
            return dash["video"][0].get("baseUrl") or ""
        return ""

    # ================================================================
    #  TVBox 接口
    # ================================================================
    def homeContent(self, filter):
        classes = []
        for cid, name in [("movie", "腾讯·电影"), ("tv", "腾讯·电视剧"), ("variety", "腾讯·综艺"),
                          ("cartoon", "腾讯·动漫"), ("doco", "腾讯·纪录片"), ("mini_series", "腾讯·短剧")]:
            classes.append({"type_id": "tx|%s" % cid, "type_name": name})
        for cid, name in [("1", "爱奇艺·电影"), ("2", "爱奇艺·电视剧"), ("6", "爱奇艺·综艺"),
                          ("4", "爱奇艺·动漫"), ("3", "爱奇艺·纪录片"), ("16", "爱奇艺·网络电影")]:
            classes.append({"type_id": "iq|%s" % cid, "type_name": name})
        for name in ["电视剧", "电影", "综艺", "动漫", "纪录片"]:
            classes.append({"type_id": "yk|%s" % name, "type_name": "优酷·%s" % name})
        for cid, name in [("2", "芒果·电视剧"), ("3", "芒果·电影"), ("1", "芒果·综艺"),
                          ("50", "芒果·动漫"), ("51", "芒果·纪录片")]:
            classes.append({"type_id": "mg|%s" % cid, "type_name": name})
        for cid, name in [("1", "B站·番剧"), ("4", "B站·国创"), ("2", "B站·电影"),
                          ("5", "B站·电视剧"), ("3", "B站·纪录片"), ("7", "B站·综艺")]:
            classes.append({"type_id": "bl|%s" % cid, "type_name": name})
        return {"class": classes, "filters": {}}

    def homeVideoContent(self):
        # 并行拉取五个平台首页推荐，总限时 8s，避免壳子对首页接口超时
        out = []
        lock = threading.Lock()

        def run(fn):
            try:
                r = fn()
                if r:
                    with lock:
                        out.extend(r[:4])
            except Exception:
                pass

        fns = [lambda: self._tx_cate("movie", 1),
               lambda: self._iq_cate("1", 1),
               lambda: self._yk_cate("电影", 1),
               lambda: self._mg_cate("3", 1),
               lambda: self._bl_cate("1", 1)]
        ts = [threading.Thread(target=run, args=(f,)) for f in fns]
        for t in ts:
            t.start()
        for t in ts:
            t.join(8)
        return {"list": out}

    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg or 1)
        try:
            pf, sub = str(tid).split("|", 1)
        except Exception:
            return {"list": [], "page": pg}
        items = []
        try:
            if pf == "tx":
                items = self._tx_cate(sub, pg)
            elif pf == "iq":
                items = self._iq_cate(sub, pg)
            elif pf == "yk":
                items = self._yk_cate(sub, pg)
            elif pf == "mg":
                items = self._mg_cate(sub, pg)
            elif pf == "bl":
                items = self._bl_cate(sub, pg)
        except Exception:
            items = []
        return self._page(pg, items)

    def detailContent(self, ids):
        vods = []
        for vid in (ids or []):
            try:
                pf, sub = str(vid).split("|", 1)
            except Exception:
                continue
            vod = None
            try:
                if pf == "tx":
                    vod = self._tx_detail(sub)
                elif pf == "iq":
                    vod = self._iq_detail(sub)
                elif pf == "yk":
                    vod = self._yk_detail(sub)
                elif pf == "mg":
                    vod = self._mg_detail(sub)
                elif pf == "bl":
                    vod = self._bl_detail(sub)
            except Exception:
                vod = None
            if vod:
                vods.append(vod)
        return {"list": vods}

    def searchContent(self, key, quick, pg="1"):
        pg = int(pg or 1)
        results, lock = [], threading.Lock()

        def run(fn):
            try:
                r = fn()
                with lock:
                    results.extend(r or [])
            except Exception:
                pass

        fns = [lambda: self._tx_search(key, pg), lambda: self._iq_search(key, pg),
               lambda: self._yk_search(key, pg), lambda: self._mg_search(key, pg),
               lambda: self._bl_search(key, pg)]
        threads = [threading.Thread(target=run, args=(f,)) for f in fns]
        for t in threads:
            t.start()
        for t in threads:
            t.join(18)
        return {"list": results, "page": pg}

    def playerContent(self, flag, id, vipFlags):
        try:
            id = str(id or "")
            if id.startswith("blplay|"):
                parts = id.split("|")
                ep_id, cid = parts[1], parts[2]
                link = parts[3] if len(parts) > 3 else ""
                url = self._bl_play(ep_id, cid)
                if url:
                    return {"parse": 0, "url": url, "jx": 0,
                            "header": {"User-Agent": UA_PC, "Referer": HDR_REF["bl"]}}
                if link:
                    return {"parse": 1, "jx": 1, "url": link,
                            "header": json.dumps({"User-Agent": UA_PC, "Referer": HDR_REF["bl"]})}
                return {"parse": 1, "jx": 1, "url": "", "header": json.dumps({})}
            ref = "https://www.mgtv.com/"
            if "v.qq.com" in id:
                ref = HDR_REF["tx"]
            elif "iqiyi.com" in id:
                ref = HDR_REF["iq"]
            elif "youku.com" in id:
                ref = HDR_REF["yk"]
            elif "bilibili.com" in id:
                ref = HDR_REF["bl"]
            return {"parse": 1, "jx": 1, "url": id,
                    "header": json.dumps({"User-Agent": UA_PC, "Referer": ref})}
        except Exception:
            return {"parse": 1, "jx": 1, "url": str(id or ""),
                    "header": json.dumps({"User-Agent": UA_PC})}

    def isVideoFormat(self, url):
        return bool(re.search(r"\.(m3u8|mp4|flv|mkv|webm)(\?|$)", str(url or "")))

    def manualVideoCheck(self):
        return False

    def localProxy(self, param):
        return None

    def destroy(self):
        return None
