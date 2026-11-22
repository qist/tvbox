# -*- coding: utf-8 -*-
# @name 看看鸭
# @version 1.0.1

"""
看看鸭 (www.kankanya.me) OmniBox 爬虫源
=========================================
实现 home / category / detail / search / play 五个接口。

站点特点：
1. 全站有「宝塔人机验证」：首次请求返回验证页 (robot.php 挑战)，
   需带 PHPSESSID 会话提交 value/token 后重取，本脚本用纯 Python 模拟该流程。
2. 播放地址经两层加密：播放页 player_aaaa.url -> POST /kkyplayer/api.php
   得到二次加密串 -> 用 md5("test") 做异或 + 双字母表替换解密得到直链。
   该解密逻辑已在本地与站点 JS 输出逐字节比对验证，无需 Node / Playwright。
"""

import base64
import hashlib
import json
import random
import re
from urllib.parse import quote, quote_plus, unquote

from spider_runner import OmniBox, run

BASE = "https://www.kankanya.me"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# 人机验证 encrypt() 使用的固定字符表
CHARS = "PXhw7UT1B0a9kQDKZsjIASmOezxYG4CHo5Jyfg2b8FLpEvRr3WtVnlqMidu6cN"

# 默认分类（当首页导航解析失败时使用）
DEFAULT_CATEGORIES = [
    ("dianying", "电影"),
    ("juji", "剧集"),
    ("zongyi", "综艺"),
    ("dongman", "动漫"),
]

# 中文分类名 -> slug
TYPE_SLUG = {
    "电影": "dianying", "剧集": "juji", "电视剧": "juji",
    "综艺": "zongyi", "动漫": "dongman", "动画": "dongman",
}


# ---------------------------------------------------------------------------
# 基础工具
# ---------------------------------------------------------------------------
def _body(resp):
    """从 OmniBox.request 的返回值中取 body。"""
    if not isinstance(resp, dict):
        return ""
    return resp.get("body") or ""


def _clean(html_text):
    """去除 HTML 标签、压缩空白。"""
    if not html_text:
        return ""
    text = re.sub(r"<[^>]+>", "", html_text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", text).strip()


def _is_verify_page(body):
    return ("人机验证" in body) or ("robot.php" in body)


def _encrypt(text):
    """对应站点验证页里的 encrypt()：字符后移3位 + 随机前后填充 + base64。"""
    out = []
    for ch in text:
        idx = CHARS.find(ch)
        code = ch if idx < 0 else CHARS[(idx + 3) % 62]
        out.append(CHARS[random.randint(0, 61)])
        out.append(code)
        out.append(CHARS[random.randint(0, 61)])
    return base64.b64encode("".join(out).encode("latin-1")).decode("ascii")


def _cookie_from(resp, fallback=""):
    """从响应 headers 中提取 Set-Cookie（取 PHPSESSID 所在的第一个键值对）。"""
    headers = resp.get("headers") or {} if isinstance(resp, dict) else {}
    set_cookie = ""
    for key, value in headers.items():
        if str(key).lower() == "set-cookie":
            if isinstance(value, (list, tuple)):
                value = value[0] if value else ""
            set_cookie = str(value)
            break
    if not set_cookie:
        return fallback
    # 只保留 name=value，丢弃 path/expires 等属性
    return set_cookie.split(";")[0].strip()


async def _post(url, data, headers):
    try:
        return await OmniBox.request(url, {
            "method": "POST",
            "headers": headers,
            "body": data,
        })
    except Exception:
        return {}


async def http_get(url, context=None):
    """带「宝塔人机验证」自动处理的 GET。"""
    headers = {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    ctx_headers = (context or {}).get("headers") or {}
    for key in ("Cookie", "cookie"):
        if ctx_headers.get(key):
            headers["Cookie"] = ctx_headers[key]
            break

    body = ""
    try:
        resp = await OmniBox.request(url, {"method": "GET", "headers": dict(headers)})
        body = _body(resp)
    except Exception as exc:
        await OmniBox.log("warn", "请求失败 %s: %s" % (url, exc))
        return ""

    if not _is_verify_page(body):
        return body

    # --- 人机验证 ---
    cookie = _cookie_from(resp, headers.get("Cookie", ""))
    if cookie:
        headers["Cookie"] = cookie
    match = re.search(r'var\s+token\s*=\s*encrypt\("([^"]+)"\)', body)
    if not match:
        # 兜底 token（站点默认固定值）
        token_plain = "MTc5NTMzMzM5Mw=="
    else:
        token_plain = match.group(1)

    post_headers = dict(headers)
    post_headers["Content-Type"] = "application/x-www-form-urlencoded"
    post_headers["Referer"] = url
    payload = "value=%s&token=%s" % (
        quote(_encrypt(url), safe=""),
        quote(_encrypt(token_plain), safe=""),
    )
    await _post(BASE + "/robot.php", payload, post_headers)

    # 验证后重取（最多重试两次）
    for _ in range(2):
        try:
            resp2 = await OmniBox.request(url, {"method": "GET", "headers": dict(headers)})
            body2 = _body(resp2)
        except Exception:
            break
        if not _is_verify_page(body2):
            return body2
        cookie2 = _cookie_from(resp2, headers.get("Cookie", ""))
        if cookie2:
            headers["Cookie"] = cookie2
    return body


# ---------------------------------------------------------------------------
# 页面解析
# ---------------------------------------------------------------------------
def _parse_poster_items(html_text, type_id="", type_name=""):
    """解析首页/分类页的 module-poster-item 卡片。"""
    items = []
    for match in re.finditer(r"<a\b([^>]*)>(.*?)</a>", html_text, re.S):
        attrs, inner = match.group(1), match.group(2)
        if "module-poster-item" not in attrs:
            continue
        href_match = re.search(r'href="/detail/([A-Za-z0-9]+)\.html"', attrs)
        if not href_match:
            continue
        vod_id = href_match.group(1)
        title_match = re.search(r'title="([^"]*)"', attrs)
        name = title_match.group(1) if title_match else ""
        name2 = re.search(r'<div class="module-poster-item-title">(.*?)</div>', inner, re.S)
        if name2:
            name = _clean(name2.group(1)) or name
        note_match = re.search(r'<div class="module-item-note">(.*?)</div>', inner, re.S)
        pic_match = re.search(r'data-original="([^"]+)"', inner)
        items.append({
            "vod_id": vod_id,
            "vod_name": name,
            "vod_pic": pic_match.group(1) if pic_match else "",
            "vod_remarks": _clean(note_match.group(1)) if note_match else "",
            "type_id": type_id,
            "type_name": type_name,
        })
    return items


def _parse_card_items(html_text):
    """解析搜索页的 module-card-item 卡片。"""
    items = []
    for block in re.split(r'<div class="module-card-item module-item">', html_text)[1:]:
        href_match = re.search(r'href="/detail/([A-Za-z0-9]+)\.html"', block)
        if not href_match:
            continue
        vod_id = href_match.group(1)
        class_match = re.search(r'<div class="module-card-item-class">(.*?)</div>', block, re.S)
        type_name = _clean(class_match.group(1)) if class_match else ""
        title_match = re.search(
            r'<div class="module-card-item-title">\s*<a[^>]*>\s*<strong>(.*?)</strong>',
            block, re.S,
        )
        name = _clean(title_match.group(1)) if title_match else ""
        pic_match = re.search(r'data-original="([^"]+)"', block)
        note_match = re.search(r'<div class="module-item-note">(.*?)</div>', block, re.S)
        info_match = re.search(
            r'<div class="module-info-item">\s*<div class="module-info-item-content">(.*?)</div>',
            block, re.S,
        )
        info = _clean(info_match.group(1)) if info_match else ""
        year_match = re.search(r"(?:19|20)\d{2}", info)
        items.append({
            "vod_id": vod_id,
            "vod_name": name,
            "vod_pic": pic_match.group(1) if pic_match else "",
            "vod_remarks": _clean(note_match.group(1)) if note_match else "",
            "vod_year": year_match.group(0) if year_match else "",
            "type_id": TYPE_SLUG.get(type_name, ""),
            "type_name": type_name,
        })
    return items


def _info_value(html_text, label):
    match = re.search(
        r'<span class="module-info-item-title">\s*' + re.escape(label)
        + r'\s*</span>\s*<div class="module-info-item-content">(.*?)</div>',
        html_text, re.S,
    )
    return _clean(match.group(1)) if match else ""


def _normalize_video_id(value):
    """把 detail 收到的 videoId 归一化成站点视频ID。

    客户端可能传入：纯 vod_id、豆瓣/本站完整链接、/detail/xxx.html、
    playId(xxx-1-1) 等格式，统一提取出核心 ID（如 XHmhhk）。
    """
    if not value:
        return ""
    text = str(value).strip()
    # 完整 URL -> 取路径最后一段
    if "://" in text:
        text = text.split("?", 1)[0].split("#", 1)[0].rstrip("/")
        text = text.rsplit("/", 1)[-1]
    # 去掉 .html 后缀
    if text.endswith(".html"):
        text = text[:-5]
    # /detail/xxx 或 /play/xxx-1-1 形式 -> 取最后一段
    if "/" in text:
        text = text.rstrip("/").rsplit("/", 1)[-1]
    # playId 形式 xxx-1-1 -> 取首段（视频ID本身是字母数字，不含连字符）
    if re.fullmatch(r"[A-Za-z0-9]+-\d+-\d+", text):
        text = text.split("-", 1)[0]
    # URL 编码情况
    if "%" in text:
        text = unquote(text)
    return text


def _page_url(category_id, page):
    """分类页 URL。category_id 支持 dianying/juji/... 及 new/hot。"""
    if category_id in ("new", "hot"):
        base = "%s/label/%s.html" % (BASE, category_id)
    else:
        base = "%s/type/%s.html" % (BASE, category_id)
    if page and int(page) > 1:
        return base.replace(".html", "/page/%s.html" % int(page))
    return base


def _search_url(keyword, page):
    base = "%s/search/%s-------------.html" % (BASE, quote_plus(keyword))
    if page and int(page) > 1:
        return base.replace(".html", "/page/%s.html" % int(page))
    return base


# ---------------------------------------------------------------------------
# OmniBox 接口
# ---------------------------------------------------------------------------
async def home(params, context):
    await OmniBox.log("info", "看看鸭：获取首页")
    html_text = await http_get(BASE + "/", context)

    classes = []
    for slug, name in DEFAULT_CATEGORIES:
        classes.append({"type_id": slug, "type_name": name})
    # 动态补充导航里的分类
    for slug, name in re.findall(
        r'<a[^>]*href="/type/([a-z]+)\.html"[^>]*>(.*?)</a>', html_text, re.S
    ):
        clean_name = _clean(name)
        if slug and clean_name and slug not in [c["type_id"] for c in classes]:
            classes.append({"type_id": slug, "type_name": clean_name})

    video_list = _parse_poster_items(html_text)
    return {"class": classes, "list": video_list}


async def category(params, context):
    category_id = params.get("categoryId") or params.get("type_id") or "dianying"
    page = int(params.get("page") or 1)
    html_text = await http_get(_page_url(category_id, page), context)
    type_name = params.get("typeName", "")
    video_list = _parse_poster_items(html_text, category_id, type_name)
    return {
        "page": page,
        "pagecount": 50,
        "total": 0,
        "list": video_list,
    }


async def detail(params, context):
    raw_id = (
        params.get("videoId") or params.get("vod_id")
        or params.get("id") or params.get("keyword") or ""
    )
    video_id = _normalize_video_id(raw_id)
    # 兜底：若传来的不是站内视频ID（例如片名），先在站内搜索拿真实ID
    if video_id and not re.fullmatch(r"[A-Za-z0-9]+", video_id):
        search_html = await http_get(
            "%s/search/%s-------------.html" % (BASE, quote_plus(video_id)), context
        )
        found = re.search(r'href="/detail/([A-Za-z0-9]+)\.html"', search_html)
        video_id = found.group(1) if found else ""
    if not video_id:
        return {"list": []}
    await OmniBox.log("info", "看看鸭详情: %s -> %s" % (raw_id, video_id))
    html_text = await http_get("%s/detail/%s.html" % (BASE, video_id), context)

    # 若详情页本身没取到 h1（ID 无效/被风控），尝试用片名搜索兜底
    if "<h1" not in html_text and raw_id:
        search_html = await http_get(
            "%s/search/%s-------------.html" % (BASE, quote_plus(str(raw_id))), context
        )
        found = re.search(r'href="/detail/([A-Za-z0-9]+)\.html"', search_html)
        if found and found.group(1) != video_id:
            video_id = found.group(1)
            html_text = await http_get(
                "%s/detail/%s.html" % (BASE, video_id), context
            )

    name_match = re.search(r"<h1[^>]*>(.*?)</h1>", html_text, re.S)
    name = _clean(name_match.group(1)) if name_match else ""
    intro_match = re.search(
        r'<div class="module-info-introduction-content">(.*?)</div>', html_text, re.S
    )
    content = _clean(intro_match.group(1)) if intro_match else ""
    pic_match = re.search(r'data-original="([^"]+)"', html_text)

    director = _info_value(html_text, "导演：")
    actor = _info_value(html_text, "主演：")
    release = _info_value(html_text, "上映：")
    remarks = _info_value(html_text, "集数：") or _info_value(html_text, "更新：")
    year_match = re.search(r"(?:19|20)\d{2}", release)

    # 播放源：按线路(sid)分组
    sources = {}
    for match in re.finditer(r"<a\b([^>]*)>(.*?)</a>", html_text, re.S):
        attrs, inner = match.group(1), match.group(2)
        if "module-play-list-link" not in attrs:
            continue
        play_match = re.search(
            r'href="/play/([A-Za-z0-9]+)-(\d+)-(\d+)\.html"', attrs
        )
        if not play_match:
            continue
        vid, sid, nid = play_match.groups()
        ep_name = _clean(inner) or ("第%s集" % nid)
        sources.setdefault(int(sid), []).append({
            "name": ep_name,
            "playId": "%s-%s-%s" % (vid, sid, nid),
        })

    play_sources = [
        {"name": "线路%s" % sid, "episodes": sources[sid]}
        for sid in sorted(sources)
    ]

    return {
        "list": [{
            "vod_id": video_id,
            "vod_name": name,
            "vod_pic": pic_match.group(1) if pic_match else "",
            "vod_content": content,
            "vod_director": director,
            "vod_actor": actor,
            "vod_area": "",
            "vod_year": year_match.group(0) if year_match else "",
            "vod_remarks": remarks,
            "vod_play_sources": play_sources,
        }],
    }


async def search(params, context):
    keyword = (params.get("keyword") or params.get("wd") or "").strip()
    page = int(params.get("page") or 1)
    if not keyword:
        return {"page": page, "pagecount": 0, "total": 0, "list": []}
    html_text = await http_get(_search_url(keyword, page), context)
    video_list = _parse_card_items(html_text)
    return {
        "page": page,
        "pagecount": 50,
        "total": 0,
        "list": video_list,
    }


# ---------------------------------------------------------------------------
# 播放地址解密（纯 Python 复刻站点 player JS 的 Decode1.get）
# ---------------------------------------------------------------------------
def _b64decode(data):
    data = "".join(
        ch for ch in data
        if ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
    )
    return base64.b64decode(data + "=" * (-len(data) % 4)).decode("latin-1")


def _b64encode(text):
    return base64.b64encode(text.encode("latin-1")).decode("ascii").rstrip("=")


def _custom_str_decode(text, key):
    """站点 customStrDecode：base64decode -> 逐字节异或 -> base64decode。"""
    raw = _b64decode(text)
    xor = "".join(
        chr(ord(raw[i]) ^ ord(key[i % len(key)])) for i in range(len(raw))
    )
    return _b64decode(xor)


def decrypt_play_url(encrypted):
    """解密 api.php 返回的 url，得到真实视频直链。"""
    key = hashlib.md5(b"test").hexdigest()
    decoded = _custom_str_decode(encrypted, key)
    parts = decoded.split("/")
    if len(parts) < 3:
        raise ValueError("播放地址解密失败：分段数异常")
    table_a = json.loads(_b64decode(parts[0]))  # 目标字母表
    table_b = json.loads(_b64decode(parts[1]))  # 源字母表
    ciphertext = _b64decode("/".join(parts[2:]))
    return "".join(
        table_a[table_b.index(ch)] if ch in table_b else ch
        for ch in ciphertext
    )


async def play(params, context):
    play_id = params.get("playId") or ""
    flag = params.get("flag") or "play"
    if not play_id:
        raise ValueError("playId 不能为空")

    # playId 形如 XHmhhk-1-1 -> /play/XHmhhk-1-1.html
    if play_id.startswith("http"):
        play_url = play_id
    elif play_id.endswith(".html"):
        play_url = BASE + play_id if play_id.startswith("/") else BASE + "/" + play_id
    else:
        play_url = "%s/play/%s.html" % (BASE, play_id)

    html_text = await http_get(play_url, context)

    # 1) 取播放页里的加密 vid (player_aaaa.url)
    #    player_aaaa 对象内有嵌套 vod_data，且其前面还有 maccms.url，
    #    因此取 player_aaaa 定义之后出现的、长度最长的 "url" 值作为加密 vid。
    start = html_text.find("player_aaaa")
    block = html_text[start:start + 4000] if start >= 0 else html_text
    candidates = re.findall(r'"url"\s*:\s*"([^"]+)"', block)
    candidates = [c for c in candidates if len(c) > 30]  # 排除 maccms 的站点域名 url
    if not candidates:
        raise ValueError("播放页未找到 player_aaaa.url")
    vid = max(candidates, key=len).replace("\\/", "/")

    # 2) 用 vid 请求解析接口
    post_headers = {
        "User-Agent": UA,
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": play_url,
    }
    resp = await _post(
        BASE + "/kkyplayer/api.php",
        "vid=%s" % quote(vid, safe=""),
        post_headers,
    )
    try:
        api_data = json.loads(_body(resp))
        encrypted_url = api_data["data"]["url"]
        real_url = decrypt_play_url(encrypted_url)
    except Exception as exc:
        await OmniBox.log("warn", "直链解析失败，回退嗅探: %s" % exc)
        return {
            "urls": [{"name": "播放", "url": play_url}],
            "flag": flag,
            "header": {"User-Agent": UA, "Referer": BASE + "/"},
            "parse": 1,
        }

    return {
        "urls": [{"name": "播放", "url": real_url}],
        "flag": flag,
        "header": {"User-Agent": UA, "Referer": BASE + "/"},
        "parse": 0,
    }


if __name__ == "__main__":
    run({
        "home": home,
        "category": category,
        "detail": detail,
        "search": search,
        "play": play,
    })
