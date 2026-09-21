# -*- coding: utf-8 -*-
# 修复：歌手不显示歌手图片
# by：垃圾星河
# 代码指导：嗷呜呜呜呜
# 增加：自动人机验证绕过

import re
import sys
import time
from base64 import b64encode, b64decode
from urllib.parse import quote, unquote
from pyquery import PyQuery as pq
from requests import Session, adapters
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append('..')
from base.spider import Spider


class Spider(Spider):
    def init(self, extend=""):
        self.host = "https://www.22a5.com"
        self.session = Session()
        adapter = adapters.HTTPAdapter(
            max_retries=Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504]),
            pool_connections=20,
            pool_maxsize=50
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        }
        self.session.headers.update(self.headers)

    def getName(self):
        return "爱听音乐"

    def isVideoFormat(self, url):
        return bool(re.search(r'\.(m3u8|mp4|mp3|m4a|flv)(\?|$)', url or "", re.I))

    def manualVideoCheck(self):
        return False

    def destroy(self):
        self.session.close()

    # ==================== 新增人机验证绕过 ====================

    def _bypass_verification(self, url, response_text):
        """若当前页面是人机验证，自动提交勾选"""
        if '安全人机验证' not in response_text and 'human_check' not in response_text:
            return None

        # 提取 csrf_token（支持多种格式）
        token_match = re.search(r'name="csrf_token"\s+value="([^"]+)"', response_text)
        if not token_match:
            print("[爱听音乐] 未找到 csrf_token，跳过绕过")
            return None
        token = token_match.group(1)

        # 构造提交数据
        data = {
            'csrf_token': token,
            'human_check': 'on'
        }

        try:
            # 发送 POST 请求，自动跟随重定向
            post_resp = self.session.post(url, data=data, allow_redirects=True, timeout=10)
            print("[爱听音乐] 人机验证已绕过")
            return post_resp
        except Exception as e:
            print(f"[爱听音乐] 人机验证提交失败: {e}")
            return None

    def getpq(self, url):
        """获取页面并自动处理人机验证（重试3次）"""
        full_url = self._abs(url)

        for attempt in range(3):
            try:
                resp = self.session.get(full_url, timeout=5)

                # 若遇到验证页，尝试绕过
                if '安全人机验证' in resp.text or 'human_check' in resp.text:
                    print("[爱听音乐] 检测到人机验证，尝试自动绕过...")
                    bypass_resp = self._bypass_verification(full_url, resp.text)
                    if bypass_resp:
                        # 验证成功后，返回最终页面（可能是重定向后的目标）
                        return pq(bypass_resp.text)
                    else:
                        # 绕过失败，等待后重试
                        time.sleep(1)
                        continue
                else:
                    # 正常页面直接返回
                    return pq(resp.text)

            except Exception as e:
                print(f"[爱听音乐] 请求失败 (尝试 {attempt+1}/3): {e}")
                time.sleep(0.5 * (attempt + 1))

        # 全部失败，返回空文档
        return pq("<html></html>")

    # ==================== 原有功能（保持不变） ====================

    def homeContent(self, filter):
        classes = [
            {"type_name": n, "type_id": i}
            for n, i in [
                ("歌手", "/singerlist/index/index/index/index.html"),
                ("TOP榜单", "/list/top.html"),
                ("新歌榜", "/list/new.html"),
                ("电台", "/radiolist/index.html"),
                ("高清MV", "/mvlist/oumei.html"),
                ("专辑", "/albumlist/index.html"),
                ("歌单", "/playtype/index.html")
            ]
        ]
        filters = {}
        for p in [c["type_id"] for c in classes if "singer" not in c["type_id"]]:
            d = self._fetch_filters(p)
            if d:
                filters[p] = d

        if "/radiolist/index.html" not in filters:
            filters["/radiolist/index.html"] = [{
                "key": "id",
                "name": "分类",
                "value": [
                    {"n": n, "v": v}
                    for n, v in zip(
                        ["最新", "最热", "有声小说", "相声", "音乐", "情感", "国漫", "影视", "脱口秀", "历史", "儿童", "教育", "八卦", "推理", "头条"],
                        ["index", "hot", "novel", "xiangyi", "music", "emotion", "game", "yingshi", "talkshow", "history",
                         "children", "education", "gossip", "tuili", "headline"]
                    )
                ]
            }]

        filters["/singerlist/index/index/index/index.html"] = [
            {
                "key": "area",
                "name": "地区",
                "value": [
                    {"n": "全部", "v": "index"},
                    {"n": "华语", "v": "huayu"},
                    {"n": "欧美", "v": "oumei"},
                    {"n": "韩国", "v": "hanguo"},
                    {"n": "日本", "v": "ribrn"}
                ]
            },
            {
                "key": "sex",
                "name": "性别",
                "value": [
                    {"n": "全部", "v": "index"},
                    {"n": "男", "v": "male"},
                    {"n": "女", "v": "girl"},
                    {"n": "组合", "v": "band"}
                ]
            },
            {
                "key": "genre",
                "name": "流派",
                "value": [
                    {"n": "全部", "v": "index"},
                    {"n": "流行", "v": "liuxing"},
                    {"n": "电子", "v": "dianzi"},
                    {"n": "摇滚", "v": "yaogun"},
                    {"n": "嘻哈", "v": "xiha"},
                    {"n": "R&B", "v": "rb"},
                    {"n": "民谣", "v": "minyao"},
                    {"n": "爵士", "v": "jueshi"},
                    {"n": "古典", "v": "gudian"}
                ]
            }
        ]
        return {"class": classes, "filters": filters, "list": []}

    def homeVideoContent(self):
        return {"list": []}

    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg or 1)
        url = tid
        if "/singerlist/" in tid:
            parts = tid.split('/')
            if len(parts) >= 6:
                url = "/".join(parts[:2] + [extend.get(k, parts[i]) for i, k in enumerate(["area", "sex", "genre"], 2)] +
                              [f"{extend.get('char', 'index')}.html"])
        elif "id" in extend and extend["id"] not in ["index", "top"]:
            url = tid.replace("index.html", f"{extend['id']}.html").replace("top.html", f"{extend['id']}.html")
            if url == tid:
                url = f"{tid.rsplit('/', 1)[0]}/{extend['id']}.html"

        if pg > 1:
            sep = "/" if any(x in url for x in ["/singerlist/", "/radiolist/", "/mvlist/", "/playtype/", "/list/"]) else "_"
            url = re.sub(r'(_\d+|/\d+)?\.html$', f'{sep}{pg}.html', url)

        doc = self.getpq(url)
        items = doc(".play_list li, .video_list li, .pic_list li, .singer_list li, .ali li, .layui-row li, .base_l li")
        return {
            "list": self._parse_list(items, tid),
            "page": pg,
            "pagecount": 9999,
            "limit": 90,
            "total": 999999
        }

    def searchContent(self, key, quick, pg="1"):
        doc = self.getpq(f"/so/{quote(key)}/{pg}.html")
        items = doc(".base_l li, .play_list li")
        return {
            "list": self._parse_list(items, "search"),
            "page": int(pg)
        }

    def detailContent(self, ids):
        url = self._abs(ids[0])
        doc = self.getpq(url)
        vod = {
            "vod_id": url,
            "vod_name": self._clean(doc("h1").text() or doc("title").text()),
            "vod_pic": self._abs(doc(".djpg img, .pic img, .djpic img").attr("src")),
            "vod_play_from": "爱听音乐",
            "vod_content": ""
        }

        if any(x in url for x in ["/playlist/", "/album/", "/list/", "/singer/", "/special/", "/radio/", "/radiolist/"]):
            eps = self._get_eps(doc)
            page_urls = {
                self._abs(a.attr("href"))
                for a in doc(".page a, .dede_pages a, .pagelist a").items()
                if a.attr("href") and "javascript" not in a.attr("href")
            } - {url}
            if page_urls:
                with ThreadPoolExecutor(max_workers=5) as ex:
                    futures = []
                    for u in sorted(page_urls, key=lambda x: int(re.search(r'[_/](\d+)\.html', x).group(1)) if re.search(
                            r'[_/](\d+)\.html', x) else 0):
                        futures.append(ex.submit(lambda uu: self._get_eps(self.getpq(uu)), u))
                    for f in as_completed(futures):
                        eps.extend(f.result() or [])
            if eps:
                vod.update({
                    "vod_play_from": "播放列表",
                    "vod_play_url": "#".join(eps)
                })
                return {"list": [vod]}

        play_list = []
        if mid := re.search(r'/(song|mp3|radio|radiolist|radioplay)/([^/]+)\.html', url):
            lrc_url = f"{self.host}/plug/down.php?ac=music&lk=lrc&id={mid.group(2)}"
            play_list = [f"播放${self.e64('0@@@@' + url + '|||' + lrc_url)}"]

        elif vid := re.search(r'/(video|mp4)/([^/]+)\.html', url):
            with ThreadPoolExecutor(max_workers=3) as ex:
                fs = {
                    ex.submit(self._api, "/plug/down.php", {"ac": "vplay", "id": vid.group(2), "q": q}): n
                    for n, q in [("蓝光", 1080), ("超清", 720), ("高清", 480)]
                }
                play_list = [f"{fs[f]}${self.e64('0@@@@'+u)}" for f in as_completed(fs) if (u := f.result())]
            play_list.sort(key=lambda x: {"蓝": 0, "超": 1, "高": 2}.get(x[0], 3))

        vod["vod_play_url"] = "#".join(play_list) if play_list else f"解析失败${self.e64('1@@@@'+url)}"
        return {"list": [vod]}

    def playerContent(self, flag, id, vipFlags):
        raw = self.d64(id).split("@@@@")[-1]
        url, subt = raw.split("|||") if "|||" in raw else (raw, "")
        url = url.replace(r"\/", "/")

        if ".html" in url and not self.isVideoFormat(url):
            if mid := re.search(r'/(song|mp3|radio|radiolist|radioplay)/([^/]+)\.html', url):
                if r_url := self._api("/js/play.php", method="POST", data={"id": mid.group(2), "type": "music"},
                                      headers={"Referer": url.replace("http://", "https://"),
                                               "X-Requested-With": "XMLHttpRequest"}):
                    url = r_url if ".php" not in r_url else url
            elif vid := re.search(r'/(video|mp4)/([^/]+)\.html', url):
                with ThreadPoolExecutor(max_workers=3) as ex:
                    for f in as_completed(
                            [ex.submit(self._api, "/plug/down.php", {"ac": "vplay", "id": vid.group(2), "q": q}) for q in
                             [1080, 720, 480]]):
                        if v_url := f.result():
                            url = v_url
                            break

        result = {"parse": 0, "url": url, "header": {"User-Agent": self.headers["User-Agent"]}}
        if "22a5.com" in url:
            result["header"]["Referer"] = self.host + "/"

        # OK影视3.6.5+支持LRC格式滚动歌词
        if subt:
            try:
                r = self.session.get(subt, headers={"Referer": self.host + "/"}, timeout=5)
                lrc_content = r.text
                if lrc_content:
                    lrc_content = self._filter_lrc_ads(lrc_content)
                    result["lrc"] = lrc_content
            except:
                pass

        return result

    def _filter_lrc_ads(self, lrc_text):
        """过滤LRC歌词中的广告内容"""
        lines = lrc_text.splitlines()
        filtered_lines = []

        # 广告关键词模式
        ad_patterns = [
            r'欢迎来访.*',
            r'本站.*',
            r'.*广告.*',
            r'QQ群.*',
            r'.*www\..*',
            r'.*http.*',
            r'.*\.com.*',
            r'.*\.cn.*',
            r'.*\.net.*',
            r'.*音乐网.*',
            r'.*提供.*',
            r'.*下载.*',
        ]

        for line in lines:
            if re.match(r'\[\d{2}:\d{2}', line):
                is_ad = False
                for pattern in ad_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        is_ad = True
                        break
                if not is_ad:
                    filtered_lines.append(line)
            else:
                filtered_lines.append(line)

        return '\n'.join(filtered_lines)

    def localProxy(self, param):
        url = unquote(param.get("url", ""))
        type_ = param.get("type")

        if type_ == "img":
            try:
                headers = {
                    "Referer": "https://www.baidu.com/",
                    "User-Agent": self.headers["User-Agent"],
                    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9"
                }
                resp = self.session.get(url, headers=headers, timeout=10)
                return [200, "image/jpeg", resp.content, {}]
            except Exception as e:
                print(f"图片代理失败: {e}")
                return [404, "text/plain", b"", {}]

        elif type_ == "lrc":
            try:
                r = self.session.get(url, headers={"Referer": self.host + "/"}, timeout=5)
                lrc_content = r.text
                lrc_content = self._filter_lrc_ads(lrc_content)
                return [200, "application/octet-stream", lrc_content.encode('utf-8'), {}]
            except:
                return [404, "text/plain", "Error", {}]

        return None

    # ==================== 辅助方法 ====================

    def _parse_list(self, items, tid=""):
        """解析列表项，修复歌手头像 - 直接返回原始图片URL"""
        res = []
        for li in items.items():
            a = li("a").eq(0)
            if not (href := a.attr("href")) or href == "/" or any(x in href for x in ["/user/", "/login/", "javascript"]):
                continue
            if not (name := self._clean(li(".name").text() or a.attr("title") or a.text())):
                continue

            is_singer = "/singer/" in href or "/singerlist" in tid

            pic = ""
            src = ""

            if is_singer:
                img = li(".pic img").eq(0)
                src = img.attr("src") or ""
                if not src:
                    img = li("img").eq(0)
                    src = img.attr("src") or ""
            else:
                img = li("img").eq(0)
                src = img.attr("src") or ""
                if not src:
                    img = li(".pic img").eq(0)
                    src = img.attr("src") or ""

            if src:
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = self.host + src
                pic = src

            res.append({
                "vod_id": self._abs(href),
                "vod_name": name,
                "vod_pic": pic,
                "style": {
                    "type": "oval" if is_singer else ("list" if any(
                        x in tid for x in ["/list/", "/playtype/", "/albumlist/"]) else "rect"),
                    "ratio": 1 if is_singer else 1.33
                }
            })
        return res

    def _get_eps(self, doc):
        eps = []
        for li in doc(".play_list li, .song_list li, .music_list li").items():
            a = li("a").eq(0)
            href = a.attr("href")
            if not href or not re.search(r'/(song|mp3|radio|radiolist|radioplay)/([^/]+)\.html', href):
                continue
            full_url = self._abs(href)

            lrc_part = ""
            mid = re.search(r'/(song|mp3|radio|radiolist|radioplay)/([^/]+)\.html', full_url)
            if mid:
                lrc_url = f"{self.host}/plug/down.php?ac=music&lk=lrc&id={mid.group(2)}"
                lrc_part = f"|||{lrc_url}"

            eps.append(f"{self._clean(a.text() or li('.name').text())}${self.e64('0@@@@' + full_url + lrc_part)}")
        return eps

    def _clean(self, text):
        return re.sub(
            r'(爱玩音乐网|视频下载说明|视频下载地址|www\.2t58\.com|MP3免费下载|LRC歌词下载|全部歌曲|\[第\d+页\]|刷新|每日推荐|最新|热门|推荐|MV|高清|无损)',
            '',
            text or '',
            flags=re.I
        ).strip()

    def _fetch_filters(self, url):
        doc = self.getpq(url)
        filters = []
        for i, group in enumerate([
            doc(".ilingku_fl"),
            doc(".class_list"),
            doc(".screen_list"),
            doc(".box_list"),
            doc(".nav_list")
        ]):
            if group:
                opts = [{"n": "全部", "v": "top" if "top" in url else "index"}]
                seen = set()
                for a in group("a").items():
                    v = (a.attr("href") or "").split("?")[0].rstrip('/').split('/')[-1].replace('.html', '')
                    if v and v not in seen:
                        opts.append({"n": a.text().strip(), "v": v})
                        seen.add(v)
                if len(opts) > 1:
                    filters.append({"key": f"id{i}" if i else "id", "name": "分类", "value": opts})
        return filters

    def _api(self, path, params=None, method="GET", headers=None, data=None):
        try:
            h = self.headers.copy()
            if headers:
                h.update(headers)
            r = (self.session.post if method == "POST" else self.session.get)(
                f"{self.host}{path}",
                params=params,
                data=data,
                headers=h,
                timeout=10,
                allow_redirects=False
            )
            if loc := r.headers.get("Location"):
                return self._abs(loc.strip())
            return self._abs(r.json().get("url", "").replace(r"\/", "/")) or (r.text.strip() if r.text.strip().startswith(
                "http") else "")
        except:
            return ""

    def _abs(self, url):
        if not url:
            return ""
        if url.startswith("http"):
            return url
        if url.startswith("//"):
            return "https:" + url
        return f"{self.host}{'/' if not url.startswith('/') else ''}{url}"

    def e64(self, text):
        return b64encode(text.encode("utf-8")).decode("utf-8")

    def d64(self, text):
        return b64decode(text.encode("utf-8")).decode("utf-8")