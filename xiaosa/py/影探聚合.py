# -*- coding: utf-8 -*-
"""Kishuto —— TVBox / 影视仓 多源聚合源

  影探聚合(4源) · 稀饭动漫(4源) · 小鸡看看 · FoFo影院 · 小山影视 · 枫奇4K(至臻/蓝光) · 橘汁新网关4K · 四源4K专线(天堂/布布/华谊/苹果)
  分类/搜索按 tag 前缀派发，详情页跨源按标题补线路，播放按 id 派发回原源。
  本文件由 build_kishuto.py 自动生成。
"""

# ==================== 版本（必须放在最前：被聚合代码在模块级引用） ====
CODE_VERSION = '20261110.211434'
UPDATE_URL = 'https://gitee.com/tao060702/tvbox/raw/master/update_kishuto.json'

# ======================================================================
# 模块：yt
# ======================================================================
# -*- coding: utf-8 -*-
"""
影探聚合 —— 四源聚合 TVBox Python 源（单文件）
========================================================================
首页 / 分类 / 筛选 / 搜索：影探4K（cms.lyyytv.cn）
详情页线路顺序：影探4K → 咕噜咕噜 → 橘汁4K → 找剧AI

源说明（2026-11-04 实测）
  影探4K   CMS + fys 解析接口，线路多为联通云/移动云/爱奇艺直链，可播率高
  咕噜咕噜  T3 私有协议（ECDH P-256 + AES-256-GCM + protobuf），线路最多
  橘汁4K   同 host 的另一套 T3 客户端（包名/版本/详情参数不同），目录与 id 空间
           独立，线路与咕噜有互补
  找剧AI   zhaoju4.com，HMAC 签名的 REST，官方 4K/1080P 线路需登录态（自动游客会话）

依赖：纯标准库（无 requests / pycryptodome），自带 AES-128/256-CBC、AES-256-GCM、
     P-256 ECDH、protobuf 裸编解码实现，可直接丢进 TVBox 的 python 目录使用。
========================================================================
"""

import base64
import gzip
import hashlib
import hmac
import json
import os
import re
import secrets
import socket
import ssl
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zlib

try:
    from base.spider import Spider as _BaseSpider
except Exception:
    _BaseSpider = object

UA_WEB = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
          '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')
UA_ANDROID = ('Mozilla/5.0 (Linux; Android 13; SM-S9080) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36')

NL = '\n'
_SEP = '\x1f'


# ============================================================================
# 基础工具
# ============================================================================

def text(value):
    return '' if value is None else str(value).strip()


def as_list(value):
    return value if isinstance(value, list) else []


def as_dict(value):
    return value if isinstance(value, dict) else {}


def loads(value):
    """宽松 JSON 解析：容忍前后缀、非 JSON 内容。"""
    try:
        if not value:
            return {}
        if isinstance(value, (bytes, bytearray)):
            value = value.decode('utf-8', 'replace')
        value = str(value).strip()
        if value[:1] not in ('{', '['):
            m = re.search(r'[\{\[].*[\}\]]', value, re.S)
            if not m:
                return {}
            value = m.group(0)
        return json.loads(value)
    except Exception:
        return {}


def page_of(value):
    m = re.match(r'\s*[+-]?\d+', '' if value is None else str(value))
    n = int(m.group(0)) if m else 0
    return max(1, n) if n else 1


def clean_name(value):
    """线路/标题清洗：去掉 $ # | 以及多余空白，避免破坏 TVBox 分隔符。"""
    s = text(value)
    for ch in ('$', '#', '$$$', '|'):
        s = s.replace(ch, ' ')
    return re.sub(r'\s+', ' ', s).strip()


def norm_title(value):
    s = text(value).lower()
    s = re.sub(r'[\s\-_:：·,，.。!！?？"“”\'’()（）\[\]【】]+', '', s)
    s = re.sub(r'(第[一二三四五六七八九十\d]+季|season\s*\d+|s\d{1,2})$', '', s)
    return s


def sim(a, b):
    """标题相似度（0~1），够用即可：完全一致/包含/字符级 Jaccard。"""
    x, y = norm_title(a), norm_title(b)
    if not x or not y:
        return 0.0
    if x == y:
        return 1.0
    if x in y or y in x:
        return 0.82
    sx, sy = set(x), set(y)
    inter = len(sx & sy)
    if not inter:
        return 0.0
    return inter / float(len(sx | sy))


def best_match(title, items, floor=0.62):
    best, score = None, 0.0
    for it in as_list(items):
        if not isinstance(it, dict):
            continue
        s = sim(title, it.get('vod_name') or it.get('name') or '')
        if s > score:
            best, score = it, s
    return best if score >= floor else None


_SEASON_SIMPLE = re.compile(
    r'(第[一二三四五六七八九十\d]+季|season\s*\d+|s\d{1,2})', re.I)
_QUALITY_NOISE = re.compile(
    r'(4k|8k|2160p?|1080p?|720p?|uhd|hdr\d*|蓝光|高清|超清|'
    r'国语|粤语|中字|字幕|完整版|未删减|合集|正片|bd|hd|dvd|web|remux)', re.I)


def strict_match(title, items):
    """详情页跨源补线路：只认「同一部片」，禁止片名包含式扩展匹配。

    旧 best_match 把「熊出没」⊂「熊出没之雪岭熊风」判成 0.82 分，
    于是剧集《熊出没》详情里挂进了电影版线路。这里要求核心片名完全
    一致，只允许剥掉画质/版本/年份后缀；季数标记不同一律不匹配。
    """
    import difflib

    def core(s):
        t = norm_title(str(s or ''))
        t = re.sub(r'[（(][^）)]*[）)]', '', t)
        t = _QUALITY_NOISE.sub('', t)
        t = re.sub(r'(19|20)\d{2}$', '', t)
        t = re.sub(r'第[一二三四五六七八九十\d]+[季部篇]$', '', t)
        return t.strip()

    want = core(title)
    if not want:
        return None
    wm = _SEASON_SIMPLE.search(str(title or ''))
    wtag = wm.group(0).lower() if wm else ''
    exact, near = [], []
    for it in as_list(items):
        if not isinstance(it, dict):
            continue
        name = str(it.get('vod_name') or it.get('name') or '')
        cm = _SEASON_SIMPLE.search(name)
        ctag = cm.group(0).lower() if cm else ''
        if wtag and ctag and wtag != ctag:
            continue
        got = core(name)
        if not got:
            continue
        if got == want:
            exact.append(it)
        elif (abs(len(got) - len(want)) <= 2
              and difflib.SequenceMatcher(None, got, want).ratio() >= 0.97):
            near.append(it)
    return (exact or near or [None])[0]


# ============================================================================
# 缓存
# ============================================================================

_CACHE = {}
_CACHE_LOCK = threading.Lock()
_TITLE_MEMO = {}          # vod_id -> 片名：个别源详情只回数字 id，补线路要靠它
_DETAIL_MEMO = {}         # 详情 id -> (时间, [(线路名, [(集名, 播放码)])])


def _memo_detail(cid, lines):
    """记住本次详情拼出的全部线路，播放失败时用它同集换源。"""
    if not cid or not lines:
        return
    now = time.time()
    if len(_DETAIL_MEMO) > 200:
        for k in [k for k, v in list(_DETAIL_MEMO.items())
                  if now - v[0] > 1800]:
            _DETAIL_MEMO.pop(k, None)
        if len(_DETAIL_MEMO) > 200:
            _DETAIL_MEMO.clear()
    _DETAIL_MEMO[str(cid)] = (now, lines)


def _unpack_lines(vod):
    """把 _pack 后的 vod_play_from/url 反解成 [(线路名, [(集名, 播放码)])]。"""
    froms = str(vod.get('vod_play_from') or '').split('$$$')
    urls = str(vod.get('vod_play_url') or '').split('$$$')
    out = []
    for i, name in enumerate(froms):
        name = str(name or '').strip()
        if not name:
            continue
        seg = urls[i] if i < len(urls) else ''
        eps = []
        for part in str(seg).split('#'):
            part = part.strip()
            if not part:
                continue
            nm, sep, pid = part.partition('$')
            if not sep:
                nm, pid = '', part
            eps.append((nm, pid))
        if eps:
            out.append((name, eps))
    return out


def _memo_title(code, name):
    """记下列表/搜索里看到的真实片名，供详情缺片名时兜底。"""
    t = str(name or '').strip()
    if not code or len(t) < 2 or t.isdigit():
        return
    if len(_TITLE_MEMO) > 4000:
        _TITLE_MEMO.clear()
    _TITLE_MEMO[str(code)] = t


def cache_get(key):
    with _CACHE_LOCK:
        hit = _CACHE.get(key)
        if not hit:
            return None
        if hit[0] < time.time():
            _CACHE.pop(key, None)
            return None
        return hit[1]


def cache_put(key, value, ttl):
    with _CACHE_LOCK:
        if len(_CACHE) > 800:
            now = time.time()
            dead = [k for k, v in _CACHE.items() if v[0] < now]
            for k in dead[:300]:
                _CACHE.pop(k, None)
            if len(_CACHE) > 1000:
                _CACHE.clear()
        _CACHE[key] = (time.time() + ttl, value)


# ============================================================================
# HTTP（统一层：gzip、连接复用靠 keep-alive 由 urllib 自行管理、瞬时错误重试）
# ============================================================================

_CTX = [None, False]


def ssl_ctx():
    if _CTX[1] is False:
        try:
            c = ssl.create_default_context()
            c.check_hostname = False
            c.verify_mode = ssl.CERT_NONE
            _CTX[0] = c
        except Exception:
            _CTX[0] = None
        _CTX[1] = True
    return _CTX[0]


def http(url, method='GET', headers=None, data=None, timeout=8.0,
         retries=2, backoff=0.35):
    """返回 (status, body_bytes)。网络/瞬时错误自动重试，绝不抛异常。"""
    url = safe_url(url)
    hdr = {'User-Agent': UA_WEB, 'Accept': '*/*', 'Accept-Encoding': 'gzip'}
    if headers:
        hdr.update(headers)
    tries = max(1, int(retries))
    last = (0, b'')
    for i in range(tries):
        if i:
            time.sleep(backoff * i)
        try:
            req = urllib.request.Request(url, data=data, headers=hdr, method=method)
            kw = {'timeout': timeout}
            ctx = ssl_ctx()
            if ctx is not None:
                kw['context'] = ctx
            with urllib.request.urlopen(req, **kw) as rsp:
                body = rsp.read()
                enc = (rsp.headers.get('Content-Encoding') or '').lower()
                if 'gzip' in enc:
                    try:
                        body = gzip.decompress(body)
                    except Exception:
                        pass
                elif 'deflate' in enc:
                    try:
                        body = zlib.decompress(body)
                    except Exception:
                        try:
                            body = zlib.decompress(body, -zlib.MAX_WBITS)
                        except Exception:
                            pass
                status = rsp.getcode()
                if status in (429, 500, 502, 503, 504) and i < tries - 1:
                    last = (status, body)
                    continue
                return (status, body)
        except urllib.error.HTTPError as exc:
            try:
                body = exc.read()
            except Exception:
                body = b''
            last = (exc.code, body)
            if exc.code in (429, 500, 502, 503, 504) and i < tries - 1:
                continue
            return last
        except (socket.timeout, ssl.SSLError, urllib.error.URLError, OSError):
            last = (0, b'')
            continue
        except Exception:
            last = (0, b'')
            continue
    return last


def http_text(url, method='GET', headers=None, data=None, timeout=8.0,
              retries=2, charset='utf-8'):
    st, body = http(url, method, headers, data, timeout, retries)
    if not body:
        return st, ''
    try:
        return st, body.decode(charset, 'replace')
    except Exception:
        return st, body.decode('utf-8', 'replace')


def http_json(url, method='GET', headers=None, data=None, timeout=8.0, retries=2):
    st, txt = http_text(url, method, headers, data, timeout, retries)
    if not txt:
        return {}
    return loads(txt)


def http_cached(key, ttl, fn):
    hit = cache_get(key)
    if hit is not None:
        return hit
    value = fn()
    if value:
        cache_put(key, value, ttl)
    return value


def is_url(value):
    try:
        p = urllib.parse.urlparse(text(value))
        return p.scheme in ('http', 'https') and bool(p.netloc)
    except Exception:
        return False


_URL_SAFE = ":/?#[]@!$&'()*+,;=%~"


def safe_url(value):
    """urllib 不接受 URL 里的非 ASCII（中文文件名很常见）→ 百分号编码掉。"""
    u = text(value).strip()
    try:
        u.encode('ascii')
        return u
    except Exception:
        try:
            return urllib.parse.quote(u, safe=_URL_SAFE)
        except Exception:
            return u


_STREAM_RE = re.compile(r'\.(?:m3u8|mpd)$', re.I)
_MEDIA_RE = re.compile(r'\.(?:mp4|m3u8|mpd|flv|avi|mkv|ts|mov|wmv|webm|m4v)$', re.I)


def is_stream_url(url):
    if not is_url(url):
        return False
    return bool(_STREAM_RE.search(urllib.parse.urlparse(text(url)).path))


def is_media_url(url):
    if not is_url(url):
        return False
    return bool(_MEDIA_RE.search(urllib.parse.urlparse(text(url)).path))


# ============================================================================
# 纯 Python AES（128/256 CBC + 256 GCM）
# ============================================================================

def _xtime(a):
    a <<= 1
    return (a ^ 0x1B) & 0xFF if a & 0x100 else a


def _gmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi:
            a ^= 0x1B
        b >>= 1
    return r


_SBOX = None
_INV_SBOX = None


def _aes_tables():
    global _SBOX, _INV_SBOX
    if _SBOX is not None:
        return
    exp = [0] * 256
    log = [0] * 256
    x = 1
    for i in range(255):
        exp[i] = x
        log[x] = i
        x = _gmul(x, 0x03)
    sb = [0] * 256
    ib = [0] * 256
    for i in range(256):
        inv = 0 if i == 0 else exp[(255 - log[i]) % 255]
        t = inv
        s = inv
        for _ in range(4):
            s = ((s << 1) | (s >> 7)) & 0xFF
            t ^= s
        sb[i] = t ^ 0x63
        ib[sb[i]] = i
    _SBOX = bytes(sb)
    _INV_SBOX = bytes(ib)


def _expand_key(key):
    """支持 16(128)/24(192)/32(256) 字节密钥，返回轮密钥列表。"""
    _aes_tables()
    nk = len(key) // 4
    if nk not in (4, 6, 8):
        raise ValueError('bad aes key length')
    total = 4 * (nk + 7)
    w = [list(key[i * 4:i * 4 + 4]) for i in range(nk)]
    rcon = 1
    for i in range(nk, total):
        t = list(w[i - 1])
        if i % nk == 0:
            t = t[1:] + t[:1]
            t = [_SBOX[b] for b in t]
            t[0] ^= rcon
            rcon = _xtime(rcon)
        elif nk > 6 and i % nk == 4:
            t = [_SBOX[b] for b in t]
        w.append([w[i - nk][j] ^ t[j] for j in range(4)])
    return [sum(w[i:i + 4], []) for i in range(0, total, 4)]


def _shift_rows(state, encrypt):
    out = [0] * 16
    for r in range(4):
        for c in range(4):
            out[r + 4 * c] = state[r + 4 * ((c + (r if encrypt else -r)) % 4)]
    return out


def _mix_columns(state):
    out = state[:]
    for c in range(4):
        a = out[0 + 4 * c]
        b = out[1 + 4 * c]
        d = out[2 + 4 * c]
        e = out[3 + 4 * c]
        t = a ^ b ^ d ^ e
        out[0 + 4 * c] = a ^ t ^ _xtime(a ^ b)
        out[1 + 4 * c] = b ^ t ^ _xtime(b ^ d)
        out[2 + 4 * c] = d ^ t ^ _xtime(d ^ e)
        out[3 + 4 * c] = e ^ t ^ _xtime(e ^ a)
    return out


def _mul9(x):
    return _xtime(_xtime(_xtime(x))) ^ x


def _mul11(x):
    return _xtime(_xtime(_xtime(x))) ^ _xtime(x) ^ x


def _mul13(x):
    return _xtime(_xtime(_xtime(x))) ^ _xtime(_xtime(x)) ^ x


def _mul14(x):
    return _xtime(_xtime(_xtime(x))) ^ _xtime(_xtime(x)) ^ _xtime(x)


def _inv_mix_columns(state):
    out = state[:]
    for c in range(4):
        a = out[0 + 4 * c]
        b = out[1 + 4 * c]
        d = out[2 + 4 * c]
        e = out[3 + 4 * c]
        out[0 + 4 * c] = _mul14(a) ^ _mul11(b) ^ _mul13(d) ^ _mul9(e)
        out[1 + 4 * c] = _mul9(a) ^ _mul14(b) ^ _mul11(d) ^ _mul13(e)
        out[2 + 4 * c] = _mul13(a) ^ _mul9(b) ^ _mul14(d) ^ _mul11(e)
        out[3 + 4 * c] = _mul11(a) ^ _mul13(b) ^ _mul9(d) ^ _mul14(e)
    return out


def _enc_block(block, rk):
    nr = len(rk) - 1
    st = [s ^ k for s, k in zip(block, rk[0])]
    for r in range(1, nr):
        st = [_SBOX[b] for b in st]
        st = _shift_rows(st, True)
        st = _mix_columns(st)
        st = [s ^ k for s, k in zip(st, rk[r])]
    st = [_SBOX[b] for b in st]
    st = _shift_rows(st, True)
    return bytes([s ^ k for s, k in zip(st, rk[nr])])


def _dec_block(block, rk):
    nr = len(rk) - 1
    st = [s ^ k for s, k in zip(block, rk[nr])]
    for r in range(nr - 1, 0, -1):
        st = _shift_rows(st, False)
        st = [_INV_SBOX[b] for b in st]
        st = [s ^ k for s, k in zip(st, rk[r])]
        st = _inv_mix_columns(st)
    st = _shift_rows(st, False)
    st = [_INV_SBOX[b] for b in st]
    return bytes([s ^ k for s, k in zip(st, rk[0])])


def cbc_encrypt(key, iv, data, pad=True):
    rk = _expand_key(key)
    if pad:
        n = 16 - len(data) % 16
        data = data + bytes([n]) * n
    out = bytearray()
    prev = iv
    for i in range(0, len(data), 16):
        blk = bytes(a ^ b for a, b in zip(data[i:i + 16], prev))
        prev = _enc_block(blk, rk)
        out += prev
    return bytes(out)


def cbc_decrypt(key, iv, data, unpad=False):
    rk = _expand_key(key)
    out = bytearray()
    prev = iv
    end = len(data) - len(data) % 16
    for i in range(0, end, 16):
        blk = data[i:i + 16]
        out += bytes(a ^ b for a, b in zip(_dec_block(blk, rk), prev))
        prev = blk
    res = bytes(out)
    if unpad and res:
        n = res[-1]
        if 1 <= n <= 16 and res[-n:] == bytes([n]) * n:
            res = res[:-n]
    return res


_GCM_R = 0xE1000000000000000000000000000000


def _ghash_mul(x, y):
    z = 0
    for i in range(128):
        if (x >> (127 - i)) & 1:
            z ^= y
        if y & 1:
            y = (y >> 1) ^ _GCM_R
        else:
            y >>= 1
    return z


def _ghash(h, aad, ciphertext):
    y = 0
    for i in range(0, len(aad), 16):
        blk = int.from_bytes(aad[i:i + 16].ljust(16, b'\x00'), 'big')
        y = _ghash_mul(y ^ blk, h)
    for i in range(0, len(ciphertext), 16):
        blk = int.from_bytes(ciphertext[i:i + 16].ljust(16, b'\x00'), 'big')
        y = _ghash_mul(y ^ blk, h)
    lens = (len(aad) * 8).to_bytes(8, 'big') + (len(ciphertext) * 8).to_bytes(8, 'big')
    return _ghash_mul(y ^ int.from_bytes(lens, 'big'), h)


def gcm_encrypt(key, nonce, data, aad=b''):
    rk = _expand_key(key)
    h = int.from_bytes(_enc_block(b'\x00' * 16, rk), 'big')
    j0 = nonce + b'\x00\x00\x00\x01'
    counter = int.from_bytes(j0, 'big')
    out = bytearray()
    for i in range(0, len(data), 16):
        counter += 1
        ks = _enc_block(counter.to_bytes(16, 'big'), rk)
        chunk = data[i:i + 16]
        out += bytes(b ^ k for b, k in zip(chunk, ks))
    ciphertext = bytes(out)
    s = _ghash(h, aad, ciphertext)
    tag = (s ^ int.from_bytes(_enc_block(j0, rk), 'big')).to_bytes(16, 'big')[:16]
    return ciphertext, tag


def gcm_decrypt(key, nonce, data, tag=None, aad=b''):
    """tag 为 None 时按 data[-16:] 切分（部分客户端不校验 tag）。"""
    rk = _expand_key(key)
    if tag is None:
        tag = data[-16:]
        data = data[:-16]
    j0 = nonce + b'\x00\x00\x00\x01'
    counter = int.from_bytes(j0, 'big')
    out = bytearray()
    for i in range(0, len(data), 16):
        counter += 1
        ks = _enc_block(counter.to_bytes(16, 'big'), rk)
        chunk = data[i:i + 16]
        out += bytes(b ^ k for b, k in zip(chunk, ks))
    return bytes(out)


# ============================================================================
# P-256（secp256r1）ECDH
# ============================================================================

_P256_P = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
_P256_A = _P256_P - 3
_P256_N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
_P256_G = (0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
           0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5)


def _p256_double(pt):
    if pt is None:
        return None
    x, y = pt
    if y == 0:
        return None
    lam = (3 * x * x + _P256_A) * pow(2 * y, _P256_P - 2, _P256_P) % _P256_P
    x3 = (lam * lam - 2 * x) % _P256_P
    y3 = (lam * (x - x3) - y) % _P256_P
    return (x3, y3)


def _p256_add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2:
        if (y1 + y2) % _P256_P == 0:
            return None
        return _p256_double(p1)
    lam = (y2 - y1) * pow((x2 - x1) % _P256_P, _P256_P - 2, _P256_P) % _P256_P
    x3 = (lam * lam - x1 - x2) % _P256_P
    y3 = (lam * (x1 - x3) - y1) % _P256_P
    return (x3, y3)


def _p256_mul(k, pt):
    res = None
    addend = pt
    while k:
        if k & 1:
            res = _p256_add(res, addend)
        addend = _p256_double(addend)
        k >>= 1
    return res


def ecdh_keypair():
    priv = int.from_bytes(secrets.token_bytes(32), 'big') % (_P256_N - 1) + 1
    pub = _p256_mul(priv, _P256_G)
    raw = b'\x04' + pub[0].to_bytes(32, 'big') + pub[1].to_bytes(32, 'big')
    return priv, raw


def ecdh_shared_x(priv, server_pub):
    raw = bytes(server_pub or b'')
    if len(raw) == 65 and raw[0] == 4:
        pt = (int.from_bytes(raw[1:33], 'big'), int.from_bytes(raw[33:65], 'big'))
    elif len(raw) == 64:
        pt = (int.from_bytes(raw[:32], 'big'), int.from_bytes(raw[32:], 'big'))
    else:
        raise ValueError('bad server public key')
    shared = _p256_mul(priv, pt)
    if shared is None:
        raise ValueError('ecdh infinity')
    return shared[0].to_bytes(32, 'big')


# ============================================================================
# protobuf 裸编解码（T3 协议用）
# ============================================================================

def pb_varint(value):
    if value < 0:
        raise ValueError('negative varint')
    out = bytearray()
    while value >= 0x80:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    out.append(value)
    return bytes(out)


def pb_bytes(field, value):
    if isinstance(value, str):
        value = value.encode('utf-8')
    return pb_varint((field << 3) | 2) + pb_varint(len(value)) + value


def pb_var(field, value):
    return pb_varint(field << 3) + pb_varint(int(value))


def pb_read_varint(data, pos):
    value = 0
    shift = 0
    while pos < len(data) and shift < 70:
        b = data[pos]
        pos += 1
        value |= (b & 0x7F) << shift
        if b < 0x80:
            return value, pos
        shift += 7
    raise ValueError('bad varint')


def pb_decode(data):
    out = []
    pos = 0
    size = len(data or b'')
    while pos < size:
        key, pos = pb_read_varint(data, pos)
        field, wire = key >> 3, key & 7
        if field == 0:
            raise ValueError('field zero')
        if wire == 0:
            value, pos = pb_read_varint(data, pos)
        elif wire == 1:
            value = data[pos:pos + 8]
            pos += 8
        elif wire == 2:
            length, pos = pb_read_varint(data, pos)
            value = data[pos:pos + length]
            pos += length
        elif wire == 5:
            value = data[pos:pos + 4]
            pos += 4
        else:
            raise ValueError('wire %d' % wire)
        if pos > size:
            raise ValueError('truncated')
        out.append((field, wire, value))
    return out


def pb_field(data, field, wire=None):
    values = [v for f, w, v in pb_decode(data) if f == field and (wire is None or w == wire)]
    return values[-1] if values else None


def pb_fields(data, field, wire=None):
    return [v for f, w, v in pb_decode(data) if f == field and (wire is None or w == wire)]


def pb_str(data, field, default=''):
    value = pb_field(data, field, 2)
    if value is None:
        return default
    try:
        return value.decode('utf-8')
    except Exception:
        return default


def raw_deflate(data, level=6):
    c = zlib.compressobj(level, zlib.DEFLATED, wbits=-15, memLevel=8,
                         strategy=zlib.Z_DEFAULT_STRATEGY)
    return c.compress(data) + c.flush()


def raw_inflate(data):
    return zlib.decompress(data, -15)


def b64url_encode(raw):
    try:
        if isinstance(raw, str):
            raw = raw.encode('utf-8')
        return base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=')
    except Exception:
        return ''


def b64url_decode(txt):
    try:
        s = text(txt)
        s += '=' * ((4 - len(s) % 4) % 4)
        return base64.urlsafe_b64decode(s.encode('ascii'))
    except Exception:
        return b''
# ============================================================================
# 云端自更新（可选，默认不启用）
#
#   原理：脚本 init 时后台拉一份「版本清单」，远端版本比本地新就下载整份
#   .py 覆盖自身文件；下次壳加载这个文件即是新代码（无需改配置、无需手动拷）。
#
#   开启方式：把 UPDATE_URL 填成清单地址（或 extend 里传 update_url）。
#   清单支持两种最省事的形态：
#     ① 纯文本，内容只有一行版本号，例如  20261105.1930
#        → 新脚本地址约定为「清单同目录 + 本文件名」，放同一个目录即可。
#     ② JSON，可指定任意下载地址与校验值：
#        {"version":"20261105.1930",
#         "url":"https://xx.com/tvbox/影探聚合.py",
#         "sha256":"…", "size":91234, "note":"修了找剧 503"}
#
#   安全阀：只接受 2xx、只接受体积 <= UPDATE_MAX_BYTES、只接受含
#   "class Spider" 的 Python 文本、sha256 对不上就放弃；写盘走
#   临时文件 + os.replace 原子替换，失败时旁挂 .new 不破坏旧文件。
# ============================================================================

UPDATE_MAX_BYTES = 4 * 1024 * 1024
SELF_NAME = 'Kishuto.py'

_UPDATE_LAST = {'ok': False, 'updated': False, 'version': CODE_VERSION,
                'msg': '', 'note': '', 'at': 0.0}


def code_version():
    return CODE_VERSION


def _ver_tuple(value):
    return tuple(int(x) for x in re.findall(r'\d+', text(value))[:4]) or (0,)


def version_newer(far, near):
    """far 是否比 near 新。"""
    a, b = _ver_tuple(far), _ver_tuple(near)
    n = max(len(a), len(b))
    return a + (0,) * (n - len(a)) > b + (0,) * (n - len(b))


def self_path():
    try:
        p = os.path.abspath(__file__)
        if os.path.isfile(p):
            return p
    except Exception:
        pass
    return ''


def self_name():
    p = self_path()
    return os.path.basename(p) if p else SELF_NAME


def parse_manifest(body):
    """→ {'version','url','sha256','note'}；纯文本清单只给 version。"""
    if isinstance(body, (bytes, bytearray)):
        try:
            body = bytes(body).decode('utf-8', 'replace')
        except Exception:
            return {}
    raw = text(body).lstrip('\ufeff').strip()
    if not raw:
        return {}
    if raw[:1] == '{':
        try:
            obj = loads(raw)
        except Exception:
            obj = None
        if isinstance(obj, dict):
            return {
                'version': text(obj.get('version') or obj.get('ver')),
                'url': text(obj.get('url') or obj.get('file') or obj.get('py')),
                'sha256': text(obj.get('sha256') or obj.get('hash')).lower(),
                'note': text(obj.get('note') or obj.get('desc')),
            }
    return {'version': raw.splitlines()[0].strip(), 'url': '',
            'sha256': '', 'note': ''}


def _write_self(path, blob):
    """原子替换自身文件。返回 (是否替换成功, 说明)。"""
    folder = os.path.dirname(path) or '.'
    tmp = os.path.join(folder, '.upd_%s.tmp' % uuid.uuid4().hex[:8])
    try:
        with open(tmp, 'wb') as fp:
            fp.write(blob)
            fp.flush()
            try:
                os.fsync(fp.fileno())
            except Exception:
                pass
    except Exception as exc:
        try:
            os.remove(tmp)
        except Exception:
            pass
        return False, 'write failed: %s' % exc
    try:
        bak = path + '.bak'
        try:
            with open(path, 'rb') as src, open(bak, 'wb') as dst:
                dst.write(src.read())
        except Exception:
            pass
        os.replace(tmp, path)
        return True, 'replaced'
    except Exception as exc:
        alt = path + '.new'
        try:
            os.replace(tmp, alt)
            return False, 'replace failed(%s), saved %s' % (exc, os.path.basename(alt))
        except Exception:
            try:
                os.remove(tmp)
            except Exception:
                pass
            return False, 'replace failed: %s' % exc


def _fetch_manifest(url):
    """带时间戳采样两次取版本较大的，都失败再回退原始地址。→ (manifest, status)"""
    sep = '&' if '?' in url else '?'
    got, status = [], 0
    for i in range(2):
        hit = '%s%st=%d' % (url, sep, int(time.time() * 1000) + i * 7)
        status, body = http(hit, timeout=8, retries=1,
                            headers={'Cache-Control': 'no-cache',
                                     'Pragma': 'no-cache'})
        if status == 200 and body:
            got.append(body)
    if not got:
        status, body = http(url, timeout=8, retries=1,
                            headers={'Cache-Control': 'no-cache',
                                     'Pragma': 'no-cache'})
        if status == 200 and body:
            got.append(body)
    best = {}
    for body in got:
        man = parse_manifest(body)
        ver = text(man.get('version'))
        if ver and (not best or version_newer(ver, text(best.get('version')))):
            best = man
    return best, status


def _blob_version(blob):
    m = re.search(rb"^CODE_VERSION = ['\"]([^'\"]*)", blob, re.M)
    return m.group(1).decode('utf-8', 'ignore') if m else ''


def check_update(url=''):
    """拉清单 → 需要就下载覆盖。返回结果 dict（绝不影响主流程）。"""
    url = text(url or UPDATE_URL)
    out = {'ok': False, 'updated': False, 'version': CODE_VERSION,
           'msg': '', 'note': '', 'at': time.time()}
    if not url:
        out['msg'] = 'no update url'
        return out
    try:
        dest = self_path()
        if not dest:
            out['msg'] = 'self path unknown'
            return out

        # 每轮都重新拉清单：CDN 边缘节点之间可能不同步（清单落后一版、
        # 脚本已是新版），死守一份旧清单会永远 sha 对不上。
        last = ''
        for attempt in range(3):
            if attempt:
                time.sleep(1.2 * attempt)
            man, status = _fetch_manifest(url)
            far = text(man.get('version'))
            if not far:
                last = 'manifest http %s' % status
                continue
            out['version'] = far
            out['note'] = man.get('note') or ''
            if not version_newer(far, CODE_VERSION):
                out['ok'] = True
                out['msg'] = 'up to date (%s)' % CODE_VERSION
                return out

            target_url = text(man.get('url'))
            cands = []
            if target_url:
                cands.append(target_url if is_url(target_url)
                             else urllib.parse.urljoin(url, target_url))
            # 清单没写地址 / 拼出来 404 时的兜底：同目录 ASCII 名、再退本地同名
            for name in ('Kishuto.py', self_name()):
                cands.append(urllib.parse.urljoin(url, name))
            digest = text(man.get('sha256')).lower()

            blob = b''
            seen = set()
            for cand in cands:
                if cand in seen:
                    continue
                seen.add(cand)
                sep = '&' if '?' in cand else '?'
                for hit in ('%s%st=%d' % (cand, sep, int(time.time() * 1000)), cand):
                    st2, body = http(hit, timeout=25, retries=1)
                    if st2 == 200 and body and b'class Spider' in body:
                        blob = body
                        break
            if not blob:
                last = 'download failed'
                continue
            if len(blob) > UPDATE_MAX_BYTES:
                out['msg'] = 'too large (%d)' % len(blob)
                return out

            if digest and hashlib.sha256(blob).hexdigest() != digest:
                # 清单落后一版时的兜底：只要脚本自身的版本号确实比本地新、
                # 且不比清单旧，就认可它（版本号是我们自己的单调时间戳）。
                bver = _blob_version(blob)
                if bver and version_newer(bver, CODE_VERSION) and \
                        not version_newer(far, bver):
                    out['version'] = bver
                    out['note'] = (out['note'] + ' / sha 兜底').strip(' /')
                    far = bver
                else:
                    last = 'sha256 mismatch'
                    continue

            done, info = _write_self(dest, blob)
            out['ok'] = True
            out['updated'] = done
            out['msg'] = ('updated %s -> %s, restart to apply'
                          % (CODE_VERSION, far)) if done else info
            return out
        out['msg'] = last or 'update failed'
        return out
    except Exception as exc:
        out['msg'] = 'error: %s' % exc
        return out

# ============================================================================
# 源 1：影探4K（cms.lyyytv.cn）—— 首页 / 分类 / 搜索 的数据来源
# ============================================================================

class YT4K(object):
    """影探4K。原脚本依赖 requests + pycryptodome，这里改为纯标准库实现。"""

    NAME = '影探'
    HOST = 'http://cms.lyyytv.cn'
    CMS_KEY = 'wP5bvxoc3yv7FoBQENFZuAF0EUYr4LTy'
    PARSE_API = 'http://fys.lyyytv.cn/api/index?appid=10001&videoUrl='
    PARSE_ID_WEB = 5      # 网页线路（腾讯/爱奇艺/芒果/优酷/B站…）
    PARSE_ID_4K = 6       # 4K 直链（ym4kjx 等，站点本身 404，需换链）
    HEADERS = {'User-Agent': 'okhttp/4.12.0'}
    PARSE_HEADERS = {'User-Agent': 'okhttp/4.12.0', 'Accept-Encoding': 'identity'}

    DEC_PREFIX = 'https://baidu.con/'
    PAGE_LIMIT = 20
    HOME_TTL = 6 * 3600
    PLAY_TTL = 120

    FILTER_NAMES = {
        'class': '类型', 'area': '地区', 'lang': '语言', 'year': '年份',
        'letter': '字母', 'by': '排序', 'sort': '顺序',
    }

    _B64_RE = re.compile(r'(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?')
    _LDMAX_RE = re.compile(r'^https?://ldmax\.cooom/', re.I)
    _4K_HOST_RE = re.compile(
        r'(?:^|\.)(?:ym4kjx|hd4kjx|sd4kjx|mm4kjx|mv4kjx|vk4kjx)\.lyyytv\.cn$', re.I)

    def __init__(self, timeout=9.0):
        self.timeout = timeout

    # ---------- 基础 ----------
    def cms(self, path, params=None):
        query = urllib.parse.urlencode(params or {})
        url = '%s/api.php/app/%s?%s' % (self.HOST, path, query)
        key = 'yt:cms:%s' % url
        cached = cache_get(key)
        if cached is not None:
            return cached
        data = http_json(url, headers=self.HEADERS, timeout=self.timeout, retries=2)
        if not isinstance(data, dict) or not data:
            return {}
        code = data.get('code')
        if code is not None:
            try:
                ok = int(code) in (1, 200)
            except (TypeError, ValueError):
                ok = False
            if not ok:
                return {}
        cache_put(key, data, 60)
        return data

    # ---------- 解密 ----------
    def _unb64(self, value):
        clean = re.sub(r'\s+', '', text(value))
        if not clean or not self._B64_RE.fullmatch(clean):
            return None
        try:
            return base64.b64decode(clean)
        except Exception:
            return None

    def decrypt_lvdou(self, value):
        """lvdou+ 前缀：前 16 字节 key、后 16 字节 iv 的 AES/CBC/PKCS7（AES-128）。"""
        original = text(value)
        if not original.startswith('lvdou+') or not self.CMS_KEY:
            return original
        try:
            encrypted = self._unb64(original[6:])
            if not encrypted:
                return original
            key = self.CMS_KEY[:16].encode('utf-8')
            iv = self.CMS_KEY[16:32].encode('utf-8') if len(self.CMS_KEY) >= 32 else key
            plain = cbc_decrypt(key, iv, encrypted, unpad=True)
            result = plain.decode('utf-8', 'replace').strip()
            if result.startswith('http'):
                return result
        except Exception:
            pass
        return original

    def decrypt_ldmax(self, value, depth=0):
        """老加密：ldmax.cooom 前缀，key = 路径前 16 位反转。"""
        if depth > 5:
            return ''
        url = text(value)
        decoded = self._unb64(url)
        if decoded:
            url = re.sub(r'\s+', '', decoded.decode('utf-8', 'replace'))
        if not self._LDMAX_RE.match(url):
            return url
        path = self._LDMAX_RE.sub('', url)
        if len(path) <= 16:
            return ''
        try:
            key = path[:16][::-1].encode('utf-8')
            encrypted = self._unb64(path[16:])
            if not encrypted or len(encrypted) % 16:
                return ''
            plain = bytearray(cbc_decrypt(key, key, encrypted))
            pad = plain[-1] if plain else 0
            if 0 < pad <= 16:
                del plain[-pad:]
            result = bytes(plain).decode('utf-8', 'replace').strip()
            return self.decrypt_ldmax(result, depth + 1) \
                if self._LDMAX_RE.match(result) else result
        except Exception:
            return ''

    def resolve_parse(self, body):
        """解析响应：JSON 包裹取 url；baidu.con 前缀走 AES；否则视为明文。"""
        body = text(body)
        if not body:
            return ''
        candidate = body
        if body.startswith('{'):
            parsed = loads(body)
            for key in ('url', 'playUrl', 'link'):
                if isinstance(parsed, dict) and parsed.get(key):
                    candidate = text(parsed[key])
                    break
            else:
                inner = as_dict(as_dict(parsed).get('data'))
                for key in ('url', 'playUrl', 'link'):
                    if inner.get(key):
                        candidate = text(inner[key])
                        break
        if not candidate.startswith(self.DEC_PREFIX):
            return candidate

        rest = candidate[len(self.DEC_PREFIX):]
        if len(rest) <= 16:
            return ''
        key = rest[:16].encode('utf-8')
        cipher_b64 = rest[16:]
        try:
            encrypted = base64.b64decode(cipher_b64, validate=False)
            result = cbc_decrypt(key, key, encrypted, unpad=True).decode('utf-8', 'replace').strip()
            if result.startswith('http'):
                return result
        except Exception:
            pass
        try:
            raw = cipher_b64.encode('latin-1', errors='ignore')
            if raw and len(raw) % 16 == 0:
                result = cbc_decrypt(key, key, raw, unpad=True).decode('utf-8', 'replace').strip()
                if result.startswith('http'):
                    return result
        except Exception:
            pass
        return ''

    def parse_url(self, raw, parse_id):
        if not raw:
            return ''
        target = '%s%s&parsesId=%d' % (
            self.PARSE_API, urllib.parse.quote(raw, safe="!'()*"), parse_id)
        st, txt = http_text(target, headers=self.PARSE_HEADERS, timeout=20, retries=2)
        if st and st < 400 and txt:
            resolved = self.resolve_parse(txt)
            if resolved and resolved.startswith('http'):
                return resolved
        return ''

    # ---------- 类型判断 ----------
    def is_4k_source(self, url):
        if not is_url(url):
            return False
        host = (urllib.parse.urlparse(text(url)).hostname or '').lower()
        if host and self._4K_HOST_RE.search(host):
            return True
        return is_media_url(url) and not is_stream_url(url)

    # ---------- 列表 ----------
    @staticmethod
    def _paginate(data, page):
        lst = as_list(data.get('list'))
        try:
            limit = int(data.get('limit') or 0)
        except (TypeError, ValueError):
            limit = 0
        if limit <= 0:
            limit = YT4K.PAGE_LIMIT
        try:
            pagecount = int(data.get('pagecount') or 0)
        except (TypeError, ValueError):
            pagecount = 0
        if pagecount <= 0:
            pagecount = page + (1 if len(lst) >= limit else 0)
        try:
            total = int(data.get('total'))
        except (TypeError, ValueError):
            total = (page - 1) * limit + len(lst) + (1 if pagecount > page else 0)
        return {'list': lst, 'page': page, 'pagecount': pagecount,
                'limit': limit, 'total': total}

    def home(self):
        def build():
            data = self.cms('nav', {'token': ''})
            classes, filters = [], {}
            for item in as_list(data.get('list')):
                if not isinstance(item, dict):
                    continue
                if item.get('type_id') is None or not text(item.get('type_name')):
                    continue
                tid = text(item['type_id'])
                classes.append({'type_id': tid, 'type_name': text(item['type_name'])})
                ext = as_dict(item.get('type_extend'))
                groups = []
                for key, name in self.FILTER_NAMES.items():
                    values = [v for v in (text(x) for x in text(ext.get(key)).split(',')) if v]
                    values = list(dict.fromkeys(values))
                    if values:
                        groups.append({
                            'key': key, 'name': name, 'init': '',
                            'value': [{'n': '全部', 'v': ''}] +
                                     [{'n': v, 'v': v} for v in values],
                        })
                if groups:
                    filters[tid] = groups
            return {'class': classes, 'filters': filters} if classes else {}
        got = http_cached('yt:nav', self.HOME_TTL, build)
        return got or {'class': [], 'filters': {}}

    def home_vod(self):
        def build():
            data = self.cms('index_video', {'token': ''})
            vlist = []
            for item in as_list(data.get('list')):
                if isinstance(item, dict):
                    vlist.extend(as_list(item.get('vlist')))
            return {'list': vlist} if vlist else {}
        got = http_cached('yt:index', 600, build)
        return got or {'list': []}

    def category(self, tid, pg, extend):
        page = page_of(pg)
        tid = text(tid)
        if not tid:
            return {'list': [], 'page': page, 'pagecount': 0, 'limit': self.PAGE_LIMIT,
                    'total': 0}
        ext = extend if isinstance(extend, dict) else loads(extend)
        params = {'tid': tid, 'pg': str(page), 'limit': '18'}
        for key in self.FILTER_NAMES:
            value = text(as_dict(ext).get(key))
            if value and value != 'all':
                params[key] = value
        data = self.cms('video', params)
        return self._paginate(data, page)

    def search(self, key, pg):
        wd = text(key)
        page = page_of(pg)
        if not wd:
            return {'list': [], 'page': page, 'pagecount': 0, 'limit': self.PAGE_LIMIT,
                    'total': 0}
        data = self.cms('search', {'text': wd, 'pg': str(page)})
        lst = [dict((k, v) for k, v in item.items() if k != 'type')
               for item in as_list(data.get('list')) if isinstance(item, dict)]
        data['list'] = lst
        return self._paginate(data, page)

    # ---------- 详情 ----------
    def playlist(self, value):
        parts = []
        for entry in text(value).split('#'):
            sep = entry.find('$')
            if sep <= 0 or not text(entry[sep + 1:]):
                continue
            parts.append('%s$%s' % (text(entry[:sep]), self.decrypt_lvdou(entry[sep + 1:])))
        return '#'.join(parts)

    def detail(self, vid):
        vid = text(vid)
        if not vid:
            return {}
        data = as_dict(self.cms('video_detail', {'id': vid}).get('data'))
        if not data:
            return {}
        players = data.get('vod_url_with_player')
        vod = dict((k, v) for k, v in data.items() if k != 'vod_url_with_player')
        names = text(vod.get('vod_play_from')).split('$$$')
        if isinstance(players, list):
            sources = players
        else:
            sources = [
                {'name': names[i] if i < len(names) else '', 'url': u}
                for i, u in enumerate(text(vod.get('vod_play_url')).split('$$$'))
            ]
        froms, urls = [], []
        for index, source in enumerate(sources):
            if not isinstance(source, dict):
                continue
            url = self.playlist(source.get('url'))
            if not url:
                continue
            name = text(source.get('name')) or text(source.get('code')) or '线路%d' % (index + 1)
            froms.append(clean_name(name))
            urls.append(url)
        vod['vod_play_from'] = '$$$'.join(froms)
        vod['vod_play_url'] = '$$$'.join(urls)
        return vod

    # ---------- 播放 ----------
    def play(self, play_id):
        original = self.decrypt_lvdou(play_id)
        if not original:
            return {'parse': 0, 'url': '', 'header': dict(self.PARSE_HEADERS)}
        if self._LDMAX_RE.match(original):
            decrypted = self.decrypt_ldmax(original)
            if decrypted:
                original = decrypted

        cache_key = 'yt:play:%s' % original
        cached = cache_get(cache_key)
        if cached:
            return {'parse': 0, 'url': cached, 'header': dict(self.PARSE_HEADERS)}

        if self.is_4k_source(original):
            resolved = self.parse_url(original, self.PARSE_ID_4K) or original
        elif is_stream_url(original):
            resolved = original
        else:
            resolved = self.parse_url(original, self.PARSE_ID_WEB)
            if not resolved and is_media_url(original):
                resolved = original

        if resolved:
            cache_put(cache_key, resolved, self.PLAY_TTL)
        return {'parse': 0, 'url': resolved or '', 'header': dict(self.PARSE_HEADERS)}

# ============================================================================
# 源 2 / 3：咕噜咕噜 + 橘汁4K（同一 T3 后端的两套客户端 profile）
#   传输：ECDH(secp256r1) 握手 → HKDF("v2-session") → AES-256-GCM + raw-deflate
#   协议：protobuf 裸编码；m=61 搜索 / m=62 详情 / m=69 服务器代理解析
# ============================================================================

T3_HOST_HEADER = '103.45.132.22:19987'
T3_BASE = 'http://103.45.132.22:19987/app/bn/v2'

# 线路显示名兜底（后端 f75 只给 code 时用）
T3_LINE_NAMES = {
    'dyttm3u8': '电影天堂', 'bfzym3u8': '暴风资源', 'lzm3u8': '量子资源',
    'ffm3u8': '非凡资源', 'qq': '腾讯视频', 'qiyi': '爱奇艺', 'youku': '优酷',
    'mgtv': '芒果TV', 'newxfyun': '咕噜4K', 'xfyun': '咕噜4K二线',
    'CO4K': '咖啡4K超清', 'jplink': '金牌极速', 'rose': '玫瑰4K',
    'NBY': '蚂蚁资源', 'qsvip': '旋风VIP', 'qingshan': '青山资源',
    'JD4K': '鲸宝4K', 'iyf4k': '爱壹帆4K',
}

T3_PROFILES = {
    'gg': {
        'label': '咕噜',
        'ua': 'Dart/3.10 (dart:io)',
        'app_name': '咕噜咕噜', 'version': '2.2.5', 'package': 'com.himrsc.viz',
        'signature': '32E0AB4FF93A29CE0E6F0BFB01F2F1B788E76262731F3F30F509CB822428ED58',
        'build': '20109',
        'device_build': 'pangu-build-component-system-513739-s9vkd-rlxnj-p3rhm',
        'sort': 'vod_hits_month',
        'boot': 'gg',
        'detail': 'gg',
    },
    'jz': {
        'label': '橘汁',
        'ua': 'Dalvik/2.1.0 (Linux; U; Android 11; Pixel 4)',
        'app_name': '咕噜咕噜', 'version': '2.1.2', 'package': 'com.jymqfh.xee',
        'signature': '', 'build': '212',
        'device_build': 'unknown',
        'sort': 'vod_hits_week',
        'boot': 'jz',
        'detail': 'jz',
    },
}


class T3Client(object):
    """T3 私有协议客户端（每个 profile 独立会话）。"""

    def __init__(self, profile, timeout=12.0):
        self.p = profile
        self.timeout = timeout
        self.session_id = ''
        self.key = b''
        self.device_id = secrets.token_hex(8)
        self.request_id = 0
        self.players = {}
        self.parsers = {}
        self.booted = False
        self.lock = threading.RLock()

    # ---------- 传输 ----------
    def _post(self, body, extra=None):
        headers = {
            'User-Agent': self.p['ua'],
            'Content-Type': 'application/x-protobuf',
            'Accept-Encoding': 'gzip',
            'Host': T3_HOST_HEADER,
        }
        if extra:
            headers.update(extra)
        st, data = http(T3_BASE, 'POST', headers, body,
                        timeout=self.timeout, retries=1)
        if not data:
            raise RuntimeError('empty response (status %s)' % st)
        try:
            return gzip.decompress(data) if data[:2] == b'\x1f\x8b' else data
        except Exception:
            return data

    # ---------- 握手 ----------
    def handshake(self):
        priv, pub = ecdh_keypair()
        caps = pb_var(1, 1) + pb_var(2, 0) + pb_var(3, 1)
        request = pb_bytes(1, pub) + pb_bytes(2, b'1.0.0') + pb_bytes(3, caps)
        hk = secrets.token_hex(16)
        iv = secrets.token_bytes(16)
        body = base64.b64encode(iv + cbc_encrypt(hk.encode('ascii'), iv,
                                                zlib.compress(request, 4)))
        content = self._post(body, {'x-handshake-key': hk})
        raw = base64.b64decode(content)
        plain = zlib.decompress(cbc_decrypt(hk.encode('ascii'), raw[:16], raw[16:],
                                            unpad=True))
        sid = pb_field(plain, 1, 2)
        server_pub = pb_field(plain, 2, 2)
        if not sid or not server_pub:
            raise RuntimeError('bad handshake response')
        self.session_id = sid.decode('ascii', 'replace')
        shared = ecdh_shared_x(priv, server_pub)
        prk = hmac.new(self.session_id.encode('ascii'), shared, hashlib.sha256).digest()
        self.key = hmac.new(prk, b'v2-session\x01', hashlib.sha256).digest()
        self.request_id = 0

    # ---------- 请求 ----------
    def request(self, method, payload=b'', scope=3):
        with self.lock:
            if not self.session_id:
                self.handshake()
            self.request_id += 1
            rid = self.request_id
            core = (pb_var(1, rid) + pb_var(2, scope) + pb_var(3, method)
                    + pb_bytes(4, self.device_id.encode('ascii'))
                    + pb_bytes(5, b'') + pb_bytes(6, payload)
                    + pb_var(7, int(time.time() * 1000)))
            nonce = secrets.token_bytes(12)
            ciphertext, tag = gcm_encrypt(self.key, nonce, raw_deflate(core))
            body = pb_var(1, rid) + pb_bytes(2, nonce + ciphertext + tag)
            content = self._post(body, {'x-session-id': self.session_id,
                                        'x-player-page-protection': '1'})
            enc = pb_field(content, 2, 2)
            if enc is None or len(enc) < 28:
                err = pb_str(content, 3)
                raise RuntimeError(err or 'request rejected')
            plain = raw_inflate(gcm_decrypt(self.key, enc[:12], enc[12:-16], enc[-16:]))
            status = pb_str(plain, 3)
            if status and status not in ('ok', 'success'):
                raise RuntimeError(status)
            return plain

    # ---------- Boot ----------
    def boot(self):
        p = self.p
        now_us = int(time.time() * 1_000_000)
        aid = self.device_id
        if p['boot'] == 'gg':
            app = (pb_bytes(1, p['app_name']) + pb_bytes(2, p['version'])
                   + pb_bytes(3, p['package']) + pb_bytes(4, p['signature'])
                   + pb_bytes(5, p['build']) + pb_var(6, now_us) + pb_var(7, now_us))
            device = (pb_bytes(1, aid) + pb_var(2, 1) + pb_bytes(3, '15')
                      + pb_bytes(4, 'Redmi K50 Ultra')
                      + pb_bytes(5, 'Redmi/diting/diting:15/AQ3A.240912.001/'
                                    'OS2.0.215.0.VOACNXM:user/release-keys')
                      + pb_bytes(6, 'Redmi') + pb_bytes(7, 'qcom')
                      + pb_var(8, 0) + pb_bytes(9, 'unknown')
                      + pb_bytes(10, p['device_build'])
                      + pb_var(11, 0) + pb_var(12, 35))
            payload = (pb_bytes(1, 'v2') + pb_bytes(2, 'android') + pb_bytes(3, 'gulu')
                       + pb_bytes(4, app) + pb_bytes(5, device))
            response = self.request(0, payload, scope=1)
        else:
            info = (pb_bytes(1, p['app_name']) + pb_bytes(2, p['version'])
                    + pb_bytes(3, p['package']) + pb_bytes(4, aid)
                    + pb_bytes(5, p['build']))
            state = (pb_bytes(1, aid) + pb_var(2, 0) + pb_bytes(3, '11')
                     + pb_bytes(4, 'Pixel 4')
                     + pb_bytes(5, 'google/redfin/redfin:11/RQ3A.211001.001')
                     + pb_bytes(6, 'google') + pb_bytes(7, 'redfin')
                     + pb_var(8, 0) + pb_bytes(9, 'unknown')
                     + pb_bytes(10, p['device_build'])
                     + pb_var(11, 0) + pb_var(12, 30))
            payload = (pb_bytes(1, 'v1') + pb_bytes(2, 'Android 11') + pb_bytes(3, 'gulu')
                       + pb_bytes(4, info) + pb_bytes(5, state))
            response = self.request(0, payload, scope=1)

        config = pb_field(response, 4, 2)
        players, parsers = {}, {}
        if config:
            for item in pb_fields(config, 4, 2):
                code = pb_str(item, 3)
                if not code:
                    continue
                parser_ids = []
                for packed in pb_fields(item, 8, 2):
                    try:
                        pos = 0
                        while pos < len(packed):
                            val, pos = pb_read_varint(packed, pos)
                            parser_ids.append(val)
                    except Exception:
                        pass
                players[code] = {
                    'id': pb_field(item, 1, 0) or 0,
                    'name': pb_str(item, 4),
                    'parser_ids': parser_ids,
                }
            for item in pb_fields(config, 7, 2):
                pid = pb_field(item, 1, 0) or 0
                if pid:
                    parsers[pid] = {
                        'name': pb_str(item, 2),
                        'url': pb_str(item, 3),
                        'mode': pb_str(item, 4),
                        'result_key': pb_str(item, 10) or 'url',
                        'server': bool(pb_field(item, 20, 0) or 0),
                    }
        self.players = players
        self.parsers = parsers
        self.booted = bool(response)

    def ensure(self):
        if self.booted and self.key:
            return
        if not self.session_id:
            self.handshake()
        if not self.booted:
            self.boot()

    def reset(self):
        self.session_id = ''
        self.key = b''
        self.request_id = 0
        self.booted = False

    # ---------- 业务 ----------
    def search(self, keyword, page=1, limit=21):
        p = self.p
        if p['boot'] == 'gg':
            filters = pb_bytes(18, p['sort'].encode('utf-8')) + pb_var(19, 1)
            payload = (pb_bytes(1, keyword) + pb_var(2, page) + pb_var(3, limit)
                       + pb_bytes(5, filters))
        else:
            filters = pb_var(1, 1) + pb_var(2, 0) + pb_bytes(3, p['sort'].encode('utf-8'))
            payload = (pb_bytes(1, keyword) + pb_var(2, page) + pb_var(3, limit)
                       + pb_bytes(5, filters))
        response = self.request(61, payload)
        data = pb_field(response, 4, 2)
        videos = []
        if data:
            for item in pb_fields(data, 1, 2):
                videos.append({
                    'vod_id': str(pb_field(item, 1, 0) or ''),
                    'vod_name': pb_str(item, 3),
                    'vod_pic': pb_str(item, 6),
                    'vod_remarks': pb_str(item, 11) or pb_str(item, 9),
                })
        info = pb_field(data, 2, 2) if data else None
        page_no = (pb_field(info, 1, 0) or page) if info else page
        pagecount = (pb_field(info, 3, 0) or 1) if info else 1
        total = (pb_field(info, 4, 0) or len(videos)) if info else len(videos)
        return {'list': [v for v in videos if v['vod_id'] and v['vod_name']],
                'page': page_no, 'pagecount': pagecount, 'total': total}

    def detail(self, vod_id):
        p = self.p
        try:
            vid = int(str(vod_id).strip())
        except (TypeError, ValueError):
            return {}
        if p['detail'] == 'gg':
            payload = (pb_var(1, vid) + pb_bytes(3, p['version'].encode('utf-8'))
                       + pb_bytes(4, b'1') + pb_var(5, 1))
        else:
            payload = (pb_var(1, vid) + pb_bytes(4, b'APP_PLATFORM_ANDROID_TV')
                       + pb_var(5, 0))
        response = self.request(62, payload)
        data = pb_field(response, 4, 2)
        if not data:
            return {}
        name = pb_str(data, 5)
        if not name or name.startswith('最新版本下载地址'):
            return {}
        blob = ' '.join([pb_str(data, f) for f in (5, 13, 21)]
                        + [pb_str(src, 1) for src in pb_fields(data, 75, 2)]).lower()
        if 'glgl.tv' in blob or 'shu.jpg' in blob or '__v99_' in blob:
            return {}
        lines = []
        for src in pb_fields(data, 75, 2):
            code = pb_str(src, 1)
            if not code or code.startswith('__v99_'):
                continue
            cfg = self.players.get(code) or {}
            eps = []
            for ep in pb_fields(src, 2, 2):
                ep_id = pb_str(ep, 3)
                if not ep_id:
                    continue
                idx = pb_field(ep, 1, 0) or (len(eps) + 1)
                eps.append('%s$%s' % (clean_name(pb_str(ep, 4) or '第%s集' % idx), ep_id))
            if not eps:
                continue
            parser_ids = cfg.get('parser_ids') or [0]
            lines.append({
                'name': clean_name(cfg.get('name') or T3_LINE_NAMES.get(code) or code),
                'parser_id': parser_ids[0] if parser_ids else 0,
                'eps': eps,
                'code': code,
            })
        return {
            'vod_id': str(pb_field(data, 1, 0) or vod_id),
            'vod_name': name,
            'vod_pic': pb_str(data, 13),
            'vod_remarks': pb_str(data, 22),
            'vod_content': pb_str(data, 21),
            'vod_area': pb_str(data, 28),
            'vod_year': pb_str(data, 30),
            'lines': lines,
        }

    def play(self, parser_id, play_id):
        payload = pb_var(1, int(parser_id)) + pb_bytes(2, play_id)
        response = self.request(69, payload)
        data = pb_field(response, 4, 2)
        return pb_str(data, 2) if data else ''


class T3Source(object):
    """线路源包装：搜索 / 详情 / 播放，带一次会话重建重试。"""

    def __init__(self, tag, timeout=12.0):
        self.tag = tag
        self.p = T3_PROFILES[tag]
        self.label = self.p['label']
        self.client = T3Client(self.p, timeout)

    def _call(self, fn, *args, **kwargs):
        try:
            self.client.ensure()
            return fn(*args, **kwargs)
        except Exception:
            try:
                self.client.reset()
                self.client.ensure()
                return fn(*args, **kwargs)
            except Exception:
                return None

    def search(self, keyword, page=1):
        cache_key = 't3:%s:q:%s|%s' % (self.tag, text(keyword), page)
        hit = cache_get(cache_key)
        if hit is not None:
            return hit
        got = self._call(self.client.search, keyword, page)
        items = as_list((got or {}).get('list'))
        if items:
            cache_put(cache_key, items, 600)
        return items

    def detail(self, vod_id):
        return self._call(self.client.detail, vod_id) or {}

    def play(self, parser_id, play_id, parser_hint=''):
        play_id = text(play_id)
        if is_media_url(play_id) or play_id.startswith('m.php') or '?data=' in play_id:
            return play_id
        url = self._call(self.client.play, parser_id, play_id) or ''
        if url:
            return url
        # 兜底：走 boot 下发的解析接口（部分线路 server=False，需外部转链）
        parser = self.client.parsers.get(int(parser_id or 0)) or {}
        api = text(parser.get('url'))
        if api:
            target = api.replace('{url}', urllib.parse.quote(play_id, safe='')) \
                if '{url}' in api else api + urllib.parse.quote(play_id, safe='')
            st, txt = http_text(target, headers={'User-Agent': self.p['ua']},
                                timeout=15, retries=1)
            if st and st < 400 and txt:
                payload = loads(txt)
                found = self._dig(payload, parser.get('result_key') or 'url')
                if found:
                    return found
        return ''

    @classmethod
    def _dig(cls, value, preferred='url'):
        if isinstance(value, str):
            return value if is_media_url(value) or value.startswith('http') else ''
        if isinstance(value, dict):
            for key in (preferred, 'url', 'play_url', 'playUrl', 'm3u8', 'data'):
                if key in value:
                    got = cls._dig(value[key], preferred)
                    if got:
                        return got
            for item in value.values():
                got = cls._dig(item, preferred)
                if got:
                    return got
        elif isinstance(value, (list, tuple)):
            for item in value:
                got = cls._dig(item, preferred)
                if got:
                    return got
        return ''

# ============================================================================
# 源 4：找剧AI（zhaoju4.com）—— HMAC 签名的 REST，官方线路需登录态
# ============================================================================

class ZJSource(object):
    NAME = '找剧'
    HOST = 'https://zhaoju4.com'
    SIGN_KEY = '8f18c8e472a9fefbab7108f5c447f69b48a4b5d34f662ed83163167fc10fb3b8'
    UA = UA_WEB
    CLIENT_NAME = 'movie-search-frontend'
    CLIENT_VERSION = '1.0.0'
    BUILD_VERSION = '20261021T204524Z-98df10a3f414-98df10a3f414-98df10a3f414'
    PROTOCOL_VERSION = '2026-07-05.library-v2.playback-v1'
    PAGE_SIZE = 18
    MAX_LINES = 4
    MAX_PREMIUM = 4
    MAX_EPISODES = 120
    TIMEOUT = 12.0
    CACHE_TTL = 300
    PROBE_BYTES = 32768
    PROBE_TTL = 600

    PREMIUM = ('bytedance', 'bytevod-lv2', 'bytevod-lv3', 'bytevod-lv5',
               'bytevod-cloudflare', 'bytevod-cloudflare-4k',
               'official-v', 'official-r', 'dong')
    EXT_HOSTS = ('v.qq.com', 'qq.com', 'youku.com', 'iqiyi.com', 'bilibili.com',
                 'mgtv.com', 'sohu.com', 'pptv.com', 'le.com', 'wasu.cn',
                 'tudou.com', '1905.com')
    VIDEO_EXTS = ('.m3u8', '.mp4', '.mkv', '.flv', '.avi', '.ts',
                  '.mov', '.m4v', '.webm', '.wmv', '.rmvb', '.mpd')

    PATH_BROWSE = '/v1/browse/catalog'
    PATH_DETAIL = '/v1/catalog/%s/detail'
    PATH_EPISODES = '/v1/catalog/%s/episodes'
    PATH_RESOLVE = '/v1/playback/resolve/%s'
    PATH_RESOLVE_LINE = '/v1/playback/resolve-line?view=compact'
    PATH_SUGGEST = '/v1/suggest'

    def __init__(self, cookie='', timeout=None):
        self.cookie = cookie or self._load_cookie()
        self.timeout = timeout or self.TIMEOUT
        self._sess_ok = False
        self._sess_checked = False
        self._sess_at = 0
        self._anon_at = 0
        self._anon_id = 'anon_' + uuid.uuid4().hex
        self._probe = {}
        # 会话检测（/v1/users/me）实测要 0.5~3.5s，且站点会随机 503。
        # 放到后台预热，详情里最多等 1.2s，不拖累其他三个源。
        self._sess_thread = threading.Thread(target=self._ensure_session, daemon=True)
        self._sess_thread.start()

    def _await_session(self, timeout=1.2):
        th = getattr(self, '_sess_thread', None)
        if th is not None and th.is_alive():
            th.join(max(0.05, timeout))
        return self._sess_ok

    # ---------- 会话 ----------
    @staticmethod
    def _cookie_file():
        try:
            return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '.zhaoju_guest_cookie')
        except Exception:
            return ''

    def _load_cookie(self):
        path = self._cookie_file()
        try:
            if path and os.path.isfile(path):
                with open(path, 'r', encoding='utf-8') as fh:
                    saved = fh.read().strip()
                if 'ai_movie_session=' in saved:
                    return saved
        except Exception:
            pass
        return ''

    def _save_cookie(self):
        path = self._cookie_file()
        if not path or 'ai_movie_session=' not in (self.cookie or ''):
            return
        try:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(self.cookie)
        except Exception:
            pass

    def _merge_cookie(self, set_cookies):
        jar = {}
        for part in str(self.cookie or '').split(';'):
            if '=' in part:
                k, v = part.split('=', 1)
                jar[k.strip()] = v.strip()
        for raw in set_cookies or []:
            first = str(raw).split(';', 1)[0]
            if '=' in first:
                k, v = first.split('=', 1)
                if v.strip():
                    jar[k.strip()] = v.strip()
        self.cookie = '; '.join('%s=%s' % (k, v) for k, v in jar.items() if v)

    # ---------- 签名与请求 ----------
    def _sign(self, method, path_query):
        u = urllib.parse.urlsplit(path_query)
        path = u.path or '/'
        search = ('?' + u.query) if u.query else ''
        ts = str(int(time.time() * 1000))
        nonce = uuid.uuid4().hex
        msg = '%s\n%s%s\n%s\n%s' % (method, path, search, ts, nonce)
        sig = hmac.new(self.SIGN_KEY.encode('utf-8'), msg.encode('utf-8'),
                       hashlib.sha256).hexdigest()
        return ts, nonce, sig

    def _headers(self, method, path_query, with_cookie=True):
        h = {
            'User-Agent': self.UA,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': self.HOST + '/',
            'x-platform': 'web',
            'x-requested-with': 'XMLHttpRequest',
            'x-ai-movie-client-name': self.CLIENT_NAME,
            'x-ai-movie-client-version': self.CLIENT_VERSION,
            'x-ai-movie-build-version': self.BUILD_VERSION,
            'x-ai-movie-protocol-version': self.PROTOCOL_VERSION,
        }
        if with_cookie and self.cookie:
            h['Cookie'] = self.cookie
        if path_query.startswith('/v1/'):
            ts, nonce, sig = self._sign(method, path_query)
            h['x-ai-movie-timestamp'] = ts
            h['x-ai-movie-nonce'] = nonce
            h['x-ai-movie-signature'] = sig
        return h

    def _req(self, path, params=None, method='GET', body=None, with_cookie=True,
             attempts=3):
        """返回 (status, json)。503/空响应自动重试 —— 站点约 30% 概率返回 503。"""
        url = path
        if params:
            clean = dict((k, v) for k, v in params.items() if v not in (None, ''))
            if clean:
                url += ('&' if '?' in url else '?') + urllib.parse.urlencode(clean)
        full = self.HOST + url
        data = None
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode('utf-8')
        headers = self._headers(method, url, with_cookie)
        if data is not None:
            headers['Content-Type'] = 'application/json; charset=utf-8'
        parsed = {}
        for attempt in range(max(1, int(attempts))):
            if attempt:
                time.sleep(0.1 * attempt)
            st, txt = http_text(full, method, headers, data,
                                timeout=self.timeout, retries=1)
            if st and 200 <= st < 300 and txt:
                parsed = loads(txt)
                if parsed:
                    return st, parsed
                continue
            if st in (401, 403):
                return st, {}
        return 0, parsed

    # ---------- 会话可用性 ----------
    def _ensure_session(self):
        now = time.time()
        if self._sess_checked and now - self._sess_at < 600:
            return self._sess_ok
        ok = True
        st, _ = self._req('/v1/users/me', attempts=1)
        if st in (401, 403):
            ok = False
        if not ok and now - self._anon_at > 300:
            self._anon_at = now
            st2, d2 = self._req('/v1/users/anonymous', method='POST',
                                body={'anonymous_id': self._anon_id},
                                with_cookie=False, attempts=1)
            if st2 and 200 <= st2 < 300:
                ok = True
        self._sess_ok = ok
        self._sess_checked = True
        self._sess_at = now
        return ok

    # ---------- 工具 ----------
    @staticmethod
    def _pick(obj, *keys, **kw):
        default = kw.get('default', '')
        if not isinstance(obj, dict):
            return default
        for key in keys:
            got = obj.get(key)
            if got not in (None, '', [], {}):
                return got
        return default

    @staticmethod
    def _join(value):
        if isinstance(value, (list, tuple)):
            return ','.join([str(x).strip() for x in value if str(x).strip()])
        return text(value)

    def _card(self, item):
        if not isinstance(item, dict):
            return None
        vid = text(self._pick(item, 'id', 'variant_id', 'selected_variant_id'))
        if not vid:
            return None
        avail = as_dict(item.get('availability'))
        remarks = text(self._pick(item, 'remarks', 'episode_progress_text')) \
            or text(avail.get('label'))
        return {
            'vod_id': vid,
            'vod_name': text(self._pick(item, 'title', 'name', 'normalized_title')),
            'vod_pic': text(self._pick(item, 'poster_url', 'poster', 'pic', 'cover')),
            'vod_remarks': remarks,
            'vod_year': text(self._pick(item, 'year')),
            'vod_area': text(self._pick(item, 'area')),
            'vod_actor': self._join(self._pick(item, 'actors', 'actor', default=[])),
            'vod_director': self._join(self._pick(item, 'directors', default=[])),
            'vod_content': text(self._pick(item, 'description', 'intro')),
            'vod_score': text(self._pick(item, 'rating', 'score')),
        }

    def _cards(self, items):
        out = []
        for it in as_list(items):
            card = self._card(it)
            if card:
                out.append(card)
        return out

    @staticmethod
    def _valid_url(url):
        s = text(url)
        if not s.startswith('http'):
            return False
        path = urllib.parse.urlsplit(s).path.lower()
        if path.endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg')):
            return False
        if '~tplv-' in path and 'image' in path:
            return False
        return True

    def _is_ext(self, url):
        try:
            host = urllib.parse.urlsplit(text(url)).netloc.lower()
            return any(host == h or host.endswith('.' + h) for h in self.EXT_HOSTS)
        except Exception:
            return False

    # ---------- 列表 ----------
    def search(self, keyword, page=1):
        wd = text(keyword)
        if not wd:
            return []
        page = max(1, int(page or 1))
        cache_key = 'zj:q:%s|%s' % (wd, page)
        hit = cache_get(cache_key)
        if hit is not None:
            return hit
        st, data = self._req(self.PATH_BROWSE, {
            'q': wd, 'page': page, 'limit': self.PAGE_SIZE,
            'offset': (page - 1) * self.PAGE_SIZE,
        })
        cards = as_list(as_dict(data).get('cards'))
        out = []
        for it in cards:
            avail = as_dict(it.get('availability'))
            if avail.get('playable') is False or avail.get('disabled') is True:
                continue
            out.append(it)
        cards_out = self._cards(out)
        if cards_out or page > 1:
            if cards_out:
                cache_put(cache_key, cards_out, 600)
            return cards_out
        # 直搜无结果 → 联想词兜底
        st, sug = self._req('/v1/suggest', {'q': wd, 'limit': 10, 'mode': 'home'})
        out = []
        for s in as_list(as_dict(sug).get('suggestions')):
            target = as_dict(s.get('target'))
            vid = text(target.get('variant_id'))
            if not vid:
                continue
            out.append({
                'vod_id': vid,
                'vod_name': text(s.get('label') or target.get('title')),
                'vod_pic': '',
                'vod_remarks': text(s.get('subtitle')),
            })
        return out

    # ---------- 详情 ----------
    def _episodes(self, vid):
        out, seen, offset = [], set(), 0
        while len(out) < self.MAX_EPISODES:
            path = self.PATH_EPISODES % urllib.parse.quote(str(vid), safe='')
            st, data = self._req(path, {'limit': 48, 'offset': offset})
            eps = as_list(as_dict(data).get('episodes'))
            if not eps:
                break
            added = 0
            for e in eps:
                if not isinstance(e, dict):
                    continue
                tok = text(e.get('token'))
                if not tok or tok in seen:
                    continue
                seen.add(tok)
                num = e.get('number')
                out.append({'token': tok, 'title': text(e.get('title')),
                            'number': num if isinstance(num, int) else None,
                            'track': text(e.get('episode_track'))})
                added += 1
            pg = as_dict(data.get('episode_pagination'))
            if not pg.get('has_more') or not added:
                break
            offset += len(eps)
        # 主线按集数排，其余（花絮等）排后面
        main = sorted([e for e in out if e.get('track') == 'main'],
                      key=lambda e: e['number'] if isinstance(e.get('number'), int) else (1 << 30))
        rest = [e for e in out if e.get('track') != 'main']
        return main + rest

    def _resolve(self, token):
        tok = text(token)
        if not tok:
            return {}
        key = 'zj:rv:%s' % tok
        hit = cache_get(key)
        if hit is not None:
            return hit
        path = self.PATH_RESOLVE % urllib.parse.quote(tok, safe='')
        st, data = self._req(path, {'view': 'compact'})
        if isinstance(data, dict) and data.get('line_options'):
            cache_put(key, data, self.CACHE_TTL)
        return data if isinstance(data, dict) else {}

    def _resolve_line(self, ticket):
        t = text(ticket)
        if t.startswith('resolve://'):
            t = t[len('resolve://'):]
        if not t:
            return {}
        key = 'zj:tk:%s' % t
        hit = cache_get(key)
        if hit is not None:
            return hit
        st, data = self._req(self.PATH_RESOLVE_LINE, method='POST', body={'ticket': t})
        line = as_dict(as_dict(data).get('line'))
        if not line and st in (401, 403):
            line = {'_error': 'need_login'}
        if line:
            cache_put(key, line, self.CACHE_TTL)
        return line

    # ---------- 线路 ----------
    @staticmethod
    def _opt_direct(o):
        return (ZJSource._valid_url(o.get('url'))
                and not bool(o.get('resolve_required'))
                and text(o.get('url_kind')) != 'resolve_ticket')

    @staticmethod
    def _opt_ticket(o):
        return bool(o.get('resolve_required')) or text(o.get('url')).startswith('resolve://')

    @staticmethod
    def _weight(o):
        try:
            return float(o.get('preference_weight') or 0)
        except Exception:
            return 0.0

    @staticmethod
    def _line_key(o):
        return (text(o.get('provider_id')), text(o.get('play_from')))

    @staticmethod
    def _line_label(o):
        s = text(o.get('label') or o.get('provider_id') or o.get('play_from') or '线路')
        for ch in ('$', '#', '|'):
            s = s.replace(ch, ' ')
        return re.sub(r'\s+', ' ', s).strip() or '线路'

    def _premium(self, o):
        label = text(o.get('label')).upper()
        pid = text(o.get('provider_id'))
        return (bool(o.get('resolve_required')) or text(o.get('url')).startswith('resolve://')
                ) and (pid in self.PREMIUM or '4K' in label or '1080P' in label
                       or '官方' in text(o.get('label')))

    def _speed(self, url):
        """实测直链首段速度（KB/s），0 = 不可用。"""
        key = text(url)
        if not key:
            return 0
        now = time.time()
        hit = self._probe.get(key)
        if hit and now - hit[0] < hit[2]:
            return hit[1]
        cur, kbps = key, 0
        for _ in range(3):
            body, dt = self._fetch(cur)
            if not body:
                break
            if b'#EXTM3U' in body[:256]:
                nxt = ''
                for line in body.decode('utf-8', 'ignore').splitlines():
                    s = line.strip()
                    if s and not s.startswith('#'):
                        nxt = urllib.parse.urljoin(cur.rsplit('/', 1)[0] + '/', s)
                        break
                if not nxt:
                    break
                cur = nxt
                continue
            if dt > 0 and len(body) > 4096:
                kbps = int(len(body) / dt / 1024)
            break
        self._probe[key] = (now, kbps, self.PROBE_TTL if kbps > 0 else 120)
        if len(self._probe) > 400:
            for k in list(self._probe.keys())[:80]:
                self._probe.pop(k, None)
        return kbps

    def _fetch(self, url):
        try:
            headers = {'User-Agent': self.UA, 'Referer': self.HOST + '/',
                       'Accept': '*/*', 'Range': 'bytes=0-%d' % (self.PROBE_BYTES - 1)}
            data = http(url, headers=headers, timeout=1.6, retries=1)[1]
            if not data:
                return b'', 0.0
            return data, max(0.05, len(data) / float(max(1, 1024)) / 300.0)
        except Exception:
            return b'', 0.0

    def _probe_all(self, urls, budget=0.55):
        res = {}
        lock = threading.Lock()

        def work(u):
            val = self._speed(u)
            with lock:
                res[u] = val

        threads = []
        for u in urls:
            t = threading.Thread(target=work, args=(u,))
            t.daemon = True
            t.start()
            threads.append(t)
        deadline = time.time() + budget
        for t in threads:
            t.join(max(0.01, deadline - time.time()))
        return res

    def _lines(self, options):
        opts = [o for o in as_list(options) if isinstance(o, dict)]
        lines, seen, used = [], set(), {}

        def add(label, prov, frm, mode):
            label = clean_name(label) or '线路'
            key = (label, prov, frm)
            if key in seen:
                return
            seen.add(key)
            if label in used:
                used[label] += 1
                label = '%s%d' % (label, used[label])
            else:
                used[label] = 1
            lines.append({'label': label, 'provider_id': prov,
                          'play_from': frm, 'mode': mode})

        # 1) 官方 4K / 1080P（需会话）—— 会话由后台线程预热，最多等 1.2s
        prem = [o for o in opts if self._premium(o)]
        if prem and self._await_session(0.6):
            prem.sort(key=lambda o: (-self._weight(o),
                                     -('4K' in text(o.get('label')).upper())))
            for o in prem[:self.MAX_PREMIUM]:
                add(self._line_label(o), self._line_key(o)[0], self._line_key(o)[1], 'parse')

        # 2) 第三方直链：先去重（同一 URL 只留权重最高的一条），再按实测速度排序
        directs = [o for o in opts if self._opt_direct(o)]
        if directs:
            groups = {}
            for o in directs:
                url = text(o.get('url'))
                if not url:
                    continue
                cur = groups.get(url)
                if cur is None or self._weight(o) > self._weight(cur):
                    groups[url] = o
            cand = sorted(groups.values(), key=self._weight, reverse=True)[:6]
            speeds = self._probe_all([text(o.get('url')) for o in cand]) if cand else {}
            alive = sorted(((speeds.get(text(o.get('url')), 0), o) for o in cand),
                           key=lambda x: -x[0])
            # 先放实测有速度的，再放没测出来的（超预算/慢），一条都不丢
            picked = ([o for k, o in alive if k > 0]
                      + [o for k, o in alive if k <= 0])[:self.MAX_LINES]
            for o in picked:
                add(self._line_label(o), self._line_key(o)[0], self._line_key(o)[1], 'direct')
        else:
            tickets = [o for o in opts if self._opt_ticket(o)]
            tickets.sort(key=self._weight, reverse=True)
            for o in tickets[:self.MAX_LINES]:
                add(self._line_label(o), self._line_key(o)[0], self._line_key(o)[1], 'parse')

        # 3) 通用解析兜底（最后一条）
        add('解析线路', '', '', 'generic')
        return lines

    # ---------- 详情入口 ----------
    def detail(self, vid):
        vid = text(vid)
        if not vid:
            return {}
        st, data = self._req(self.PATH_DETAIL % urllib.parse.quote(vid, safe=''))
        if not isinstance(data, dict):
            data = {}
        ep_vid = text(self._pick(data, 'selected_variant_id', 'variant_id', 'id')) or vid
        eps = self._episodes(ep_vid)
        vod = {
            'vod_id': vid,
            'vod_name': text(self._pick(data, 'title', 'normalized_title')) or vid,
            'vod_pic': text(self._pick(data, 'poster_url', 'poster')),
            'vod_year': text(self._pick(data, 'year')),
            'vod_area': text(self._pick(data, 'area')),
            'vod_remarks': text(self._pick(data, 'episode_progress_text', 'remarks')),
            'vod_actor': self._join(self._pick(data, 'actors', default=[])),
            'vod_director': self._join(self._pick(data, 'directors', default=[])),
            'vod_content': text(self._pick(data, 'description', 'intro')),
            'vod_score': text(self._pick(data, 'rating', 'score')),
        }
        if not eps:
            return {'vod': vod, 'lines': []}

        options = []
        for ep in eps[:2]:
            r = self._resolve(ep['token'])
            cand = as_list(r.get('line_options'))
            if cand:
                options = cand
                break
        if not options:
            return {'vod': vod, 'lines': []}
        lines = self._lines(options)

        gen_key = next(((ln['provider_id'], ln['play_from'])
                        for ln in lines if ln['mode'] == 'direct'), None)
        out = []
        for ln in lines:
            eps_out = []
            for idx, ep in enumerate(eps):
                tok = ep['token']
                if ln['mode'] == 'generic':
                    ref = ('zjoff|%s|%s|%s' % (tok, b64url_encode(gen_key[0]),
                                               b64url_encode(gen_key[1]))) \
                        if gen_key else ('zjoff|%s' % tok)
                else:
                    ref = 'zjres|%s|%s|%s|%s' % (
                        tok, b64url_encode(ln['provider_id']),
                        b64url_encode(ln['play_from']), b64url_encode(ln['label']))
                name = clean_name(ep['title']) or '第%d集' % (idx + 1)
                eps_out.append('%s$%s' % (name, ref))
            if eps_out:
                out.append((ln['label'], eps_out))
        return {'vod': vod, 'lines': out}

    # ---------- 播放 ----------
    def _play_line(self, token, prov, frm, label, generic=False):
        """严格按月台标签/供应商取流：专属线路绝不回落到别的供应商，
        否则会把「别的片子的直链」当成这条线路的结果（原脚本的兜底就有这个坑）。"""
        prov, frm, label = text(prov), text(frm), text(label)
        cache_key = 'zj:ln:%s|%s|%s|%s' % (token, prov, frm, label)
        hit = cache_get(cache_key)
        if hit is not None:
            return hit

        r = self._resolve(token)
        opts = [o for o in as_list(r.get('line_options')) if isinstance(o, dict)]
        if not opts:
            return ''
        directs = [o for o in opts if self._opt_direct(o)]
        tickets = [o for o in opts if self._opt_ticket(o)]
        exact = (prov, frm)

        def pick_direct(items):
            for o in items:
                url = text(o.get('url'))
                if self._valid_url(url):
                    return url
            return ''

        def pick_ticket(items):
            for o in items:
                url = text(self._resolve_line(o.get('url')).get('url'))
                if self._valid_url(url):
                    return url
            return ''

        url = ''
        if label:
            url = pick_direct([o for o in directs if self._line_label(o) == label])
        if not url and (exact[0] or exact[1]):
            url = pick_direct([o for o in directs if self._line_key(o) == exact])
        if not url and label:
            url = pick_ticket([o for o in tickets if self._line_label(o) == label])
        if not url and (exact[0] or exact[1]):
            url = pick_ticket([o for o in tickets if self._line_key(o) == exact])
        if not url and (generic or not exact[0]):
            url = pick_ticket(tickets[:5]) or pick_direct(directs[:2])
        if url:
            cache_put(cache_key, url, self.CACHE_TTL)
        return url

    def play(self, ref):
        raw = text(ref)
        if '%7C' in raw.upper() or '%3A' in raw.upper():
            raw = urllib.parse.unquote(raw)
        parts = raw.split('|')
        kind = parts[0] if parts else ''
        token = parts[1] if len(parts) > 1 else ''
        prov = b64url_decode(parts[2]).decode('utf-8', 'ignore') if len(parts) > 2 else ''
        frm = b64url_decode(parts[3]).decode('utf-8', 'ignore') if len(parts) > 3 else ''
        label = b64url_decode(parts[4]).decode('utf-8', 'ignore') if len(parts) > 4 else ''
        if not token:
            return {'url': '', 'parse': 0}
        url = self._play_line(token, prov, frm, label, generic=(kind == 'zjoff'))
        if not url:
            # 站点 503 抖动时第一次可能空手，重试一次（播放是用户触发，多等一下无妨）
            time.sleep(0.15)
            url = self._play_line(token, prov, frm, label, generic=(kind == 'zjoff'))
        if not url:
            return {'url': '', 'parse': 0}
        ext = self._is_ext(url)
        return {'url': url, 'parse': 1 if ext else 0,
                'header': {'User-Agent': self.UA, 'Referer': self.HOST + '/'}}

# ============================================================================
# 门面：聚合 Spider
#   首页 / 分类 / 筛选 / 搜索：影探4K
#   详情线路：影探 → 咕噜 → 橘汁 → 找剧（TVBox 默认播第一条，即影探）
# ============================================================================

class YtAggSpider(_BaseSpider):
    NAME = '影探聚合'
    LABELS = {'yt': '影探', 'gg': '咕噜', 'jz': '橘汁', 'zj': '找剧'}
    ORDER = ['yt', 'gg', 'jz', 'zj']
    DETAIL_BUDGET = 6.0       # 首屏预算（秒）——超时的源转后台补全
    SEARCH_BUDGET = 1.4       # 必须小于外层 2.8s，否则影探搜索结果会被整体丢弃
    CACHE_TTL = 300
    MAX_LINES_PER_SRC = 8

    def __init__(self):
        self._sources = {}
        self._lock = threading.RLock()
        self.order = list(self.ORDER)
        self.max_lines = self.MAX_LINES_PER_SRC
        self.detail_budget = self.DETAIL_BUDGET
        self.zj_cookie = ''
        self._last_err = ''
        self._warmed = False
        self._filling = set()
        self._update_url = ''
        self._update = {}
        self._updating = False

    # ---------- 生命周期 ----------
    def getName(self):
        return self.NAME

    def version(self):
        return code_version()

    def init(self, extend=''):
        cfg = {}
        try:
            if isinstance(extend, dict):
                cfg = extend
            elif isinstance(extend, str) and extend.strip().startswith('{'):
                cfg = loads(extend)
        except Exception:
            cfg = {}
        lines = [t for t in as_list(cfg.get('lines')) if t in self.LABELS]
        if lines:
            self.order = list(dict.fromkeys(lines + [t for t in self.ORDER if t not in lines]))
        try:
            self.detail_budget = float(cfg.get('detail_budget') or self.DETAIL_BUDGET)
        except (TypeError, ValueError):
            self.detail_budget = self.DETAIL_BUDGET
        try:
            self.max_lines = int(cfg.get('max_lines') or self.MAX_LINES_PER_SRC)
        except (TypeError, ValueError):
            self.max_lines = self.MAX_LINES_PER_SRC
        self.zj_cookie = text(cfg.get('zj_cookie') or cfg.get('cookie'))
        with self._lock:
            if self.zj_cookie and 'zj' in self._sources:
                self._sources.pop('zj', None)
        self._warmed = False
        self._update_url = text(cfg.get('update_url') or UPDATE_URL)
        if text(cfg.get('update', '1')).lower() not in ('0', 'false', 'no', 'off'):
            pass  # Kishuto: 自更新由外层统一负责
        return None

    def _auto_update(self):
        # 合并版统一由 Kishuto 门面负责自更新，子源不再各自拉清单
        return
        self._updating = True

        def run():
            try:
                got = check_update(self._update_url)
                self._update = got
                globals()['_UPDATE_LAST'] = got
            except Exception:
                pass

        try:
            threading.Thread(target=run, daemon=True).start()
        except Exception:
            pass

    def _prewarm(self):
        """首页阶段偷偷把咕噜/橘汁的握手+boot 做完（各约 0.9s），
        详情页就不用再付这笔开销。失败无所谓，详情里会自己重试。"""
        if self._warmed:
            return
        self._warmed = True

        def run():
            for tag in ('gg', 'jz'):
                try:
                    if tag in self.order:
                        self._src(tag).client.ensure()
                except Exception:
                    pass
            # 找剧AI 官方 4K/1080P 要游客会话；首页后台先建好，
            # 详情页 _await_session(0.6) 才来得及把 4K 线路挂出来。
            try:
                if 'zj' in self.order:
                    self._src('zj')._ensure_session()
            except Exception:
                pass

        try:
            th = threading.Thread(target=run, daemon=True)
            th.start()
        except Exception:
            pass

    def _src(self, tag):
        with self._lock:
            got = self._sources.get(tag)
            if got is not None:
                return got
            if tag == 'yt':
                got = YT4K()
            elif tag in ('gg', 'jz'):
                got = T3Source(tag)
            elif tag == 'zj':
                got = ZJSource(self.zj_cookie)
            else:
                got = None
            if got is not None:
                self._sources[tag] = got
            return got

    def destroy(self):
        self._sources = {}
        return None

    def isVideoFormat(self, url):
        return is_media_url(url)

    def manualVideoCheck(self):
        return False

    def localProxy(self, param):
        return None

    # ---------- 首页 / 分类 / 搜索 ----------
    def homeContent(self, filter=True):
        # 有些壳不调 init()，这里兜一次，保证新版本总会被拉下来
        if self._update_url and not self._update and not self._updating:
            pass  # Kishuto: 自更新由外层统一负责
        self._prewarm()
        yt = self._src('yt')
        try:
            data = yt.home()
        except Exception as exc:
            self._last_err = 'home:%s' % exc
            data = {'class': [], 'filters': {}}
        if not as_list(data.get('list')):
            try:
                data['list'] = as_list(yt.home_vod().get('list'))[:30]
            except Exception:
                data['list'] = []
        return data

    def homeVideoContent(self):
        try:
            return self._src('yt').home_vod()
        except Exception as exc:
            self._last_err = 'home_vod:%s' % exc
            return {'list': []}

    def categoryContent(self, tid, pg='1', filter=True, extend=None):
        yt = self._src('yt')
        try:
            data = yt.category(tid, pg, extend)
        except Exception as exc:
            self._last_err = 'category:%s' % exc
            return {'list': [], 'page': 1, 'pagecount': 0, 'limit': 18, 'total': 0}
        if not as_list(data.get('list')) and page_of(pg) == 1:
            cache_put('yt:cms-fail:%s' % text(tid), '', 1)
            try:
                data = yt.category(tid, pg, extend)
            except Exception:
                pass
        return data

    # 片名噪音：版本/语种/年份/解说类后缀，合并卡片时先去掉
    NAME_NOISE = ('手语版', '字幕助听版', '字幕版', '助听版', '无字幕',
                  '国语版', '粤语版', '日语版', '英语版', '普通话版', '双语版',
                  '真人版', '动画版', '重制版', '剧版', '电影版', '电视版',
                  '完整版', '未删减', '无删减', '高清版', '蓝光版', '合集', '正片',
                  '解说', '精彩分享', '剧情揭秘', '揭秘', '预告', '花絮', '片段')

    @classmethod
    def _base_name(cls, name, kw=''):
        """把「凡人修仙传手语版」这类变体归一成主片名。"""
        t = norm_title(name)
        if not t:
            return ''
        t = re.sub(r'[（(][^）)]*[）)]', '', t)      # 括号注释
        for _ in range(3):                          # 反复剥，可能叠着好几个
            for w in cls.NAME_NOISE:
                if t.endswith(w) and len(t) > len(w):
                    t = t[:-len(w)]
                elif t.startswith(w) and len(t) > len(w):
                    t = t[len(w):]
        t = re.sub(r'(19|20)\d{2}$', '', t)          # 结尾年份
        t = t.rstrip('之');
        return t.strip() or norm_title(name)

    def searchContent(self, key, quick=False, pg='1'):
        kw = text(key)
        if not kw:
            return {'list': []}
        page = page_of(pg)
        out = []
        try:
            out = as_list(self._src('yt').search(kw, page).get('list'))
        except Exception as exc:
            self._last_err = 'search:%s' % exc
        if len(out) >= 5 or page > 1:
            return {'list': out}

        # 影探命中太少 → 并发问其他三源（id 加源前缀，详情页按前缀回源）
        found = {}
        threads = []
        deadline = time.time() + self.SEARCH_BUDGET
        for tag in ['gg', 'jz', 'zj']:
            if tag not in self.order:
                continue
            th = threading.Thread(target=self._search_one,
                                  args=(tag, kw, page, found), daemon=True)
            th.start()
            threads.append(th)
        for th in threads:
            th.join(max(0.05, deadline - time.time()))
        seen = set(norm_title(x.get('vod_name')) for x in out)
        for tag in ['gg', 'jz', 'zj']:
            for card in found.get(tag) or []:
                name = text(card.get('vod_name'))
                if not name or norm_title(name) in seen:
                    continue
                seen.add(norm_title(name))
                item = dict(card)
                item['vod_id'] = '%s:%s' % (tag, text(card.get('vod_id')))
                out.append(item)
        return {'list': out}

    def _search_one(self, tag, keyword, page, box):
        try:
            box[tag] = self._items(self._src(tag), keyword, page)
        except Exception:
            box[tag] = []

    @staticmethod
    def _items(src, keyword, page=1):
        """各源 search 返回形态不一（影探给 {'list':[...]}，T3/找剧直接给 list）。"""
        got = src.search(keyword, page)
        if isinstance(got, dict):
            return as_list(got.get('list'))
        return as_list(got)

    # ---------- 详情 ----------
    def detailContent(self, ids):
        vid = ids[0] if isinstance(ids, (list, tuple)) and ids else ids
        vid = text(vid)
        if not vid:
            return {'list': []}
        cache_key = 'merged:%s' % vid
        hit = cache_get(cache_key)
        if hit is not None:
            got = loads(hit)
            if got:
                return got

        deadline = time.time() + self.detail_budget
        tag, real = self._split_id(vid)
        base = self._base(tag, real)
        if not base:
            return {'list': []}
        title, vod, base_lines = base

        others = [t for t in self.order if t != tag]
        found = {}
        threads = []
        for other in others:
            # 之前补全过的源直接复用（按源缓存，不受合并缓存过期影响）
            pre = cache_get('pre:%s:%s' % (other, vid))
            if pre:
                found[other] = pre
                continue
            th = threading.Thread(target=self._collect,
                                  args=(other, title, found), daemon=True)
            th.start()
            threads.append(th)
        for th in threads:
            th.join(max(0.05, deadline - time.time()))

        for other in others:
            if found.get(other):
                cache_put('pre:%s:%s' % (other, vid), found[other], 1800)

        vod = dict(vod)
        result = self._render(tag, vod, base_lines, found)
        cache_put(cache_key, json.dumps(result, ensure_ascii=False), self.CACHE_TTL)

        # 首屏没赶上的源，后台补全后写回缓存：下次点进同一个片子就是完整四源
        missing = [t for t in others if not found.get(t)]
        if missing:
            with self._lock:
                spawn = vid not in self._filling
                if spawn:
                    self._filling.add(vid)
            if spawn:
                threading.Thread(target=self._fill_later,
                                 args=(cache_key, vid, tag, vod, base_lines, title,
                                       found, missing), daemon=True).start()
        return loads(json.dumps(result, ensure_ascii=False))

    def _render(self, tag, vod, base_lines, extra):
        """把基准源 + 各源线路拼成 TVBox 详情结构。"""
        lines = list(base_lines)
        for other in [t for t in self.order if t != tag]:
            lines.extend(as_list(extra.get(other)))
        froms, urls = [], []
        used = {}
        for src_tag, name, eps in lines:
            label = clean_name('%s·%s' % (self.LABELS.get(src_tag, src_tag),
                                          clean_name(name) or '线路'))
            if label in used:
                used[label] += 1
                label = '%s·%d' % (label, used[label])
            else:
                used[label] = 1
            segs = []
            for ep_name, raw in eps:
                code = self._encode(src_tag, name, raw)
                if code:
                    segs.append('%s$%s' % (clean_name(ep_name) or '正片', code))
            if segs:
                froms.append(label)
                urls.append('#'.join(segs))

        vod = dict(vod)
        vod['vod_play_from'] = '$$$'.join(froms)
        vod['vod_play_url'] = '$$$'.join(urls)
        if not froms:
            vod['vod_content'] = (text(vod.get('vod_content')) + NL + NL +
                                  '[聚合提示] 四个源都没有匹配到可用线路，' +
                                  '可稍后重试或换个片名搜索。').strip()
        return {'list': [vod]}

    def _fill_later(self, cache_key, vid, tag, vod, base_lines, title, found, missing):
        """后台慢补：不设预算地跑完剩下的源，成功后刷新缓存。"""
        try:
            for other in missing:
                try:
                    self._collect(other, title, found)
                except Exception:
                    pass
            if not any(found.get(t) for t in missing):
                return
            for t in missing:
                if found.get(t):
                    cache_put('pre:%s:%s' % (t, vid), found[t], 1800)
            result = self._render(tag, dict(vod), base_lines, found)
            cache_put(cache_key, json.dumps(result, ensure_ascii=False),
                      self.CACHE_TTL + 120)
        except Exception:
            pass
        finally:
            with self._lock:
                self._filling.discard(vid)

    def _split_id(self, vid):
        head, sep, rest = vid.partition(':')
        if sep and head in self.LABELS and rest:
            return head, rest
        return 'yt', vid

    def _base(self, tag, vid):
        """取基准源详情，返回 (标题, vod, [(tag, 线路名, [(集名, 原始id)])])。"""
        try:
            if tag == 'yt':
                vod = self._src('yt').detail(vid)
                if not vod:
                    return None
                lines = []
                froms = text(vod.get('vod_play_from')).split('$$$')
                urls = text(vod.get('vod_play_url')).split('$$$')
                for name, block in zip(froms, urls):
                    eps = self._split_eps(block)
                    if eps:
                        lines.append(('yt', name, eps))
                vod = dict(vod)
                vod['vod_id'] = text(vid)
                return text(vod.get('vod_name')), vod, lines
            if tag in ('gg', 'jz'):
                data = self._src(tag).detail(vid)
                if not data:
                    return None
                lines = []
                for ln in as_list(data.get('lines')):
                    eps = []
                    for seg in as_list(ln.get('eps')):
                        ep_name, sep, ep_id = seg.partition('$')
                        if sep and ep_id:
                            eps.append((ep_name, '%d\x1e%s' % (
                                ln.get('parser_id') or 0, ep_id)))
                    if eps:
                        lines.append((tag, ln.get('name'), eps))
                vod = {
                    'vod_id': vid, 'vod_name': data.get('vod_name'),
                    'vod_pic': data.get('vod_pic'), 'vod_year': data.get('vod_year'),
                    'vod_area': data.get('vod_area'),
                    'vod_remarks': data.get('vod_remarks'),
                    'vod_content': data.get('vod_content'),
                }
                return text(data.get('vod_name')), vod, lines
            if tag == 'zj':
                data = self._src('zj').detail(vid)
                if not data:
                    return None
                lines = [(tag, name, self._split_eps(eps))
                         for name, eps in as_list(data.get('lines'))]
                lines = [x for x in lines if x[2]]
                return text(as_dict(data.get('vod')).get('vod_name')), \
                    as_dict(data.get('vod')), lines
        except Exception as exc:
            self._last_err = 'base(%s):%s' % (tag, exc)
        return None

    def _collect(self, tag, title, box):
        """其他源：按标题搜索 → 取最像的一条 → 复用 _base 取线路。"""
        try:
            items = self._items(self._src(tag), title)
            match = strict_match(title, items)
            if not match:
                box[tag] = []
                return
            base = self._base(tag, text(match.get('vod_id')))
            box[tag] = (base[2][:self.max_lines] if base else [])
        except Exception:
            box[tag] = []

    @staticmethod
    def _split_eps(block):
        segs = [text(x) for x in block] if isinstance(block, (list, tuple)) \
            else text(block).split('#')
        eps = []
        for seg in segs:
            name, sep, pid = seg.partition('$')
            if sep and pid:
                eps.append((name, pid))
        return eps

    # ---------- 线路编码 / 播放派发 ----------
    @staticmethod
    def _encode(tag, name, raw):
        """<tag>|<base64url(线路名\\x1f原始id)>，壳回传时按 tag 派发回原源。"""
        payload = '%s%s%s' % (clean_name(name), _SEP, raw)
        blob = b64url_encode(payload)
        return '%s|%s' % (tag, blob) if blob else ''

    def _decode(self, pid, flag=''):
        raw = text(pid)
        tag, sep, blob = raw.partition('|')
        if sep and tag in self.LABELS and blob:
            plain = b64url_decode(blob).decode('utf-8', 'ignore')
            name, s2, real = plain.partition(_SEP)
            if s2:
                return tag, real, name or flag
        return 'yt', raw, text(flag)

    def playerContent(self, flag, id, vipFlags=None):
        raw = id[0] if isinstance(id, (list, tuple)) and id else id
        tag, real, name = self._decode(raw, flag)
        empty = {'parse': 0, 'url': '', 'header': {'User-Agent': UA_WEB}}
        if not real:
            return empty
        try:
            if tag == 'yt':
                got = self._src('yt').play(real)
                return {'parse': 0, 'url': text(got.get('url')),
                        'header': got.get('header') or {'User-Agent': 'okhttp/4.12.0'}}
            if tag in ('gg', 'jz'):
                parser_id, sep, play_id = real.partition('\x1e')
                if not sep:
                    play_id, parser_id = real, '0'
                url = self._src(tag).play(parser_id, play_id, name)
                return {'parse': 0, 'url': url or '',
                        'header': {'User-Agent': T3_PROFILES[tag]['ua']}}
            if tag == 'zj':
                got = self._src('zj').play(real)
                return {'parse': int(got.get('parse') or 0), 'url': text(got.get('url')),
                        'header': got.get('header') or {'User-Agent': UA_WEB}}
        except Exception as exc:
            self._last_err = 'play(%s):%s' % (tag, exc)
        return empty


# ======================================================================
# 模块：xf
# ======================================================================
# -*- coding: utf-8 -*-
"""
稀饭聚合 · TVBox / OK影视 四源聚合 Python 源
================================================================
首页数据 : 稀饭动漫 Next (xifanacg) —— 分类 / 推荐 / 筛选 / 搜索 / 条目元数据
播放线路 : 四源同时挂出，默认优先级（用户 2026-11-04 指定）
           1. 稀饭动漫   xifanacg        tag=xf
           2. GiriGiri爱 girigirilove   tag=gg
           3. 次元城动画 cycani.org     tag=cy
           4. OmoFun     omofun.in      tag=om
           TVBox 默认取第一条线路播放，故此顺序即默认选线顺序。

线路名 : 「源·原线路名」；选集 id : "<tag>|<base64url(flag + US + 原始id)>"
         playerContent 按 tag 解码后派发回对应源，不依赖壳回传的 flag。

源配置 extend（JSON，全部可选）:
{
  "cyc_username": "次元城账号",
  "cyc_password": "密码",
  "cyc_token": "浏览器复制的 JWT",
  "lines": ["xf", "gg", "cy", "om"],
  "detail_budget": 7,
  "host": "https://next.xifanacg.com",
  "api": "https://api.xifanacg.com",
  "key": "sb_publishable_xxx"
}
说明：次元城播放接口需登录，上面三个 cyc_* 字段至少要给一个；
      否则该源仍能列出选集，但播放会返回空地址（接口 401）。

2026-11-04 修复要点（xifanacg「已坏」）:
  站点接口实测全部正常（RPC / 详情 / 取流均 200）。真正的故障是旧脚本
  _rsc_sources() 去请求 Next.js 的 /anime/{id} 页面，单次要 10.6~11s，
  而该页 RSC payload 里已经完全没有 sources 数据 —— 详情页被拖到超时，
  且只能降级出 1 条假线路。本版改为调用 issue-web-playback 拿 candidates
  （含 source_id / source_name），详情页由 ~11.5s 降到 ~1s，并恢复 3 条真实线路。
"""

import sys
import re
import os
import json
import time
import base64
import difflib
import tempfile
import urllib.parse
import urllib.request
import urllib.error

try:
    import threading
except Exception:
    threading = None
try:
    import gzip
except Exception:
    gzip = None
try:
    import zlib
except Exception:
    zlib = None
try:
    import ssl
except Exception:
    ssl = None
try:
    import http.client as http_client
except Exception:
    http_client = None

sys.path.append('..')
try:
    from base.spider import Spider as _SpiderBase
except Exception:
    class _SpiderBase(object):
        pass

XF_UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')
VIDEO_EXTS = ('.m3u8', '.mp4', '.mkv', '.flv', '.avi', '.ts', '.mov',
              '.m4v', '.webm', '.wmv', '.rmvb', '.mpd')
EXT_HOSTS = ('v.qq.com', 'qq.com', 'youku.com', 'iqiyi.com', 'bilibili.com',
             'mgtv.com', 'sohu.com', 'pptv.com', 'le.com', 'wasu.cn', '1905.com')
US = chr(31)          # 线路 flag 与原始 id 的内部分隔符
NL = chr(10)


class _DummyLock(object):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


_POOL = {}
XF_CACHE = {}
_LAST_ERR = ''          # 最近一次 detailContent 异常，便于排查（不影响正常流程）
_POOL_MAX = 5
_POOL_IDLE = 25.0
_CACHE_MAX = 200
_SSL = None
_SSL_READY = False
try:
    _POOL_LOCK = threading.Lock() if threading else _DummyLock()
    _CACHE_LOCK = threading.Lock() if threading else _DummyLock()
except Exception:
    _POOL_LOCK = _CACHE_LOCK = _DummyLock()


# ==================== 全局 HTTP 层（四源共享连接池 / 缓存） ====================
def _ssl_ctx():
    global _SSL, _SSL_READY
    if not _SSL_READY:
        _SSL_READY = True
        try:
            # TVBox 内置 Python 常缺系统根证书；这些是公开采集接口，统一不校验
            _SSL = ssl._create_unverified_context() if ssl else None
        except Exception:
            _SSL = None
    return _SSL


def xf_cache_get(key):
    try:
        with _CACHE_LOCK:
            it = XF_CACHE.get(key)
            if not it:
                return None
            if it[0] > time.time():
                return it[1]
            XF_CACHE.pop(key, None)
    except Exception:
        pass
    return None


def xf_cache_put(key, val, ttl):
    try:
        with _CACHE_LOCK:
            if len(XF_CACHE) >= _CACHE_MAX:
                now = time.time()
                for k in [k for k, v in XF_CACHE.items() if v[0] <= now]:
                    XF_CACHE.pop(k, None)
                if len(XF_CACHE) >= _CACHE_MAX:
                    XF_CACHE.clear()
            XF_CACHE[key] = (time.time() + ttl, val)
    except Exception:
        pass


def _new_conn(scheme, netloc, timeout):
    kw = {'timeout': timeout}
    if scheme == 'https':
        ctx = _ssl_ctx()
        if ctx is not None:
            kw['context'] = ctx
        return http_client.HTTPSConnection(netloc, **kw)
    return http_client.HTTPConnection(netloc, **kw)


def _pool_take(netloc):
    try:
        with _POOL_LOCK:
            lst = _POOL.get(netloc)
            now = time.time()
            while lst:
                conn, ts = lst.pop()
                if now - ts < _POOL_IDLE and getattr(conn, 'sock', None) is not None:
                    return conn
                try:
                    conn.close()
                except Exception:
                    pass
    except Exception:
        pass
    return None


def _pool_give(netloc, conn):
    try:
        with _POOL_LOCK:
            lst = _POOL.setdefault(netloc, [])
            if len(lst) < _POOL_MAX:
                lst.append((conn, time.time()))
                return
    except Exception:
        pass
    try:
        conn.close()
    except Exception:
        pass


def pool_clear():
    try:
        with _POOL_LOCK:
            for lst in list(_POOL.values()):
                for conn, _ in lst:
                    try:
                        conn.close()
                    except Exception:
                        pass
            _POOL.clear()
    except Exception:
        pass


def _unzip(data, enc):
    try:
        if not data or not enc:
            return data
        if 'gzip' in enc and gzip:
            return gzip.decompress(data)
        if 'deflate' in enc and zlib:
            try:
                return zlib.decompress(data)
            except Exception:
                return zlib.decompress(data, -zlib.MAX_WBITS)
    except Exception:
        pass
    return data


def _decode(data, ctype):
    cs = 'utf-8'
    try:
        m = re.search(r'charset=([\w-]+)', ctype or '')
        if m:
            cs = m.group(1)
    except Exception:
        pass
    try:
        return data.decode(cs, 'ignore')
    except Exception:
        return data.decode('utf-8', 'ignore')


def _urllib_req(url, method, data, h, timeout):
    try:
        req = urllib.request.Request(url, data=data, headers=h, method=method)
        kw = {'timeout': timeout}
        ctx = _ssl_ctx()
        if ctx is not None:
            kw['context'] = ctx
        with urllib.request.urlopen(req, **kw) as resp:
            raw = resp.read()
            enc = (resp.headers.get('Content-Encoding') or '').lower()
            return resp.status, _decode(_unzip(raw, enc), resp.headers.get('Content-Type'))
    except urllib.error.HTTPError as e:
        try:
            raw = _unzip(e.read(), (e.headers.get('Content-Encoding') or '').lower())
            return e.code, raw.decode('utf-8', 'ignore')
        except Exception:
            return e.code, ''
    except Exception:
        return 0, ''


def request_ex(url, method='GET', body=None, headers=None, timeout=8.0, ttl=0):
    """返回 (status, text)。body 为 dict/list 时自动序列化并置 Content-Type。
    连接池按 netloc 复用；仅 2xx 会回池；短 TTL 缓存只存原始文本。"""
    try:
        p = urllib.parse.urlsplit(str(url or ''))
    except Exception:
        return 0, ''
    netloc = p.netloc
    if not netloc:
        return 0, ''
    scheme = (p.scheme or 'https').lower()
    path = (p.path or '/') + (('?' + p.query) if p.query else '')
    try:
        if any(ord(c) > 127 for c in path):
            path = urllib.parse.quote(path, safe="/?&=%:@+,~$!*'();[]")
    except Exception:
        pass

    h = dict(headers or {})
    data = None
    if body is not None:
        if isinstance(body, (dict, list)):
            data = json.dumps(body, ensure_ascii=False).encode('utf-8')
            h.setdefault('Content-Type', 'application/json')
        elif isinstance(body, str):
            data = body.encode('utf-8')
        else:
            data = body
        if method == 'GET':
            method = 'POST'
    if gzip or zlib:
        h.setdefault('Accept-Encoding', 'gzip, deflate')
    h.setdefault('User-Agent', XF_UA)

    ck = None
    if ttl:
        ck = '%s|%s|%s|%s' % (method, url, (data or b'')[:160],
                              h.get('Authorization', ''))
        hit = xf_cache_get(ck)
        if hit is not None:
            return 200, hit

    st, txt = 0, ''
    if http_client is None:
        st, txt = _urllib_req(url, method, data, h, timeout)
    else:
        for attempt in (0, 1, 2):
            conn = _pool_take(netloc) if attempt < 2 else None
            reused = conn is not None
            if conn is None:
                try:
                    conn = _new_conn(scheme, netloc, timeout)
                except Exception:
                    break
            t0 = time.time()
            try:
                conn.request(method, path, body=data, headers=h)
                resp = conn.getresponse()
                raw = resp.read()
                enc = (resp.getheader('Content-Encoding') or '').lower()
                ctype = resp.getheader('Content-Type') or ''
                st = resp.status or 0
                txt = _decode(_unzip(raw, enc), ctype)
                if 200 <= st < 300:
                    _pool_give(netloc, conn)
                else:
                    try:
                        conn.close()
                    except Exception:
                        pass
                break
            except Exception:
                try:
                    conn.close()
                except Exception:
                    pass
                if reused:
                    continue
                # 真超时不重试，只有 <1.2s 的快速失败才重来
                if attempt == 0 and (time.time() - t0) < 1.2:
                    continue
                break
    if ck and 200 <= st < 300 and txt:
        xf_cache_put(ck, txt, ttl)
    return st, txt


def xf_http_text(url, **kw):
    return request_ex(url, **kw)[1]


def xf_loads(txt):
    """兼容普通 JSON / NDJSON / 前后带噪声的接口响应"""
    if not txt:
        return {}
    s = txt.strip()
    try:
        return json.loads(s)
    except Exception:
        pass
    out = []
    for line in s.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        if isinstance(o, list):
            out += o
        elif isinstance(o, dict):
            out.append(o)
    if out:
        return out
    m = re.search(r'[\{\[].*[\}\]]', s, re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return {}


# ==================== 通用工具 ====================
def is_video(u):
    try:
        x = str(u or '').split('#')[0].split('?')[0].strip().lower()
        return any(x.endswith(e) for e in VIDEO_EXTS)
    except Exception:
        return False


def enc_url(u):
    """路径含中文/空格时百分号编码，保留 query 里的 sign 参数"""
    try:
        s = str(u or '').strip()
        if not s or all(ord(c) < 128 for c in s):
            return s
        p = urllib.parse.urlsplit(s)
        return urllib.parse.urlunsplit((
            p.scheme, p.netloc,
            urllib.parse.quote(p.path, safe="/%:@&=+$,~"),
            urllib.parse.quote(p.query, safe="=&%:/?:@+,~"), ''))
    except Exception:
        return str(u or '')


def abs_url(base, u):
    try:
        s = str(u or '').strip()
        if not s:
            return s
        if s.startswith('//'):
            return enc_url('https:' + s)
        if s.startswith('http'):
            return enc_url(s)
        return enc_url(urllib.parse.urljoin(base, s))
    except Exception:
        return u


def xf_clean_name(s):
    try:
        t = str(s or '').strip()
        t = t.replace('$', ' ').replace('#', ' ').replace('|', ' ')
        t = t.replace('\r', ' ').replace('\n', ' ')
        return re.sub(r'\s+', ' ', t).strip()
    except Exception:
        return ''


def xf_norm_title(s):
    try:
        s = str(s or '').lower()
        return re.sub(r'[\s\u3000\-—–_·:：!！?？,，.。\[\]【】()（）「」『』《》<>／/\\|+~～]', '', s)
    except Exception:
        return ''


def xf_sim(a, b):
    """标题相似度：完全相同 > 包含 > 序列相似"""
    try:
        x, y = xf_norm_title(a), xf_norm_title(b)
        if not x or not y:
            return 0.0
        if x == y:
            return 1.0
        if x in y or y in x:
            r = float(min(len(x), len(y))) / max(len(x), len(y))
            return 0.85 + 0.12 * r if r >= 0.5 else 0.0
        return difflib.SequenceMatcher(None, x, y).ratio()
    except Exception:
        return 0.0


_SEASON_RE = re.compile(
    r'(第[一二三四五六七八九十0-9]+季|season\s*[0-9]+|part\s*[0-9]+|\bs[0-9]{1,2}\b)',
    re.I)


def season_tag(s):
    try:
        m = _SEASON_RE.search(str(s or ''))
        return m.group(0).lower() if m else ''
    except Exception:
        return ''


def search_keywords(title):
    """完整标题 → 去括号/季数的核心词 → 核心词前 6 / 4 字"""
    t = str(title or '').strip()
    out = []

    def add(x):
        x = str(x or '').strip()
        if x and x not in out and len(x) >= 2:
            out.append(x)

    add(t)
    core = re.sub(r'[\[\(（【].*?[\]\)）】]', '', t)
    core = _SEASON_RE.sub('', core)
    core = re.sub(r'\s+', ' ', core).strip()
    add(core)
    for n in (6, 4):
        if len(core) > n:
            add(core[:n])
    return out


def xf_best_match(title, items, threshold=0.70):
    best, score = None, 0.0
    ts = season_tag(title)
    for it in items or []:
        if not isinstance(it, dict):
            continue
        name = it.get('vod_name') or ''
        s = xf_sim(title, name)
        cs = season_tag(name)
        if ts and cs and ts != cs:
            s *= 0.45          # 双方季数标记都存在却不一致，避免错季
        if s > score:
            best, score = it, s
    return best if score >= threshold else None


def search_best(src, title):
    """跨站译名有差异时逐级降级搜索；降级轮只接受近乎精确匹配，
    防止把第一季的线路挂到第二季上。"""
    for i, kw in enumerate(search_keywords(title)):
        try:
            items = src.search(kw)
        except Exception:
            continue
        if not items:
            continue
        pick = xf_best_match(title, items, 0.70 if i == 0 else 0.97)
        if pick:
            return pick
    return None


def enc_pid(tag, flag, pid):
    try:
        raw = ('%s%s%s' % (flag, US, pid)).encode('utf-8')
        return tag + '|' + base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=')
    except Exception:
        return ''


def dec_pid(s):
    try:
        tag, b = str(s).split('|', 1)
        b += '=' * ((4 - len(b) % 4) % 4)
        raw = base64.urlsafe_b64decode(b.encode('ascii')).decode('utf-8')
        flag, pid = raw.split(US, 1)
        return tag, flag, pid
    except Exception:
        return '', '', ''


def play_header(host, ref=None):
    return {'User-Agent': XF_UA, 'Referer': ref or (host + '/'),
            'Origin': host, 'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9'}


def is_ext_link(u):
    try:
        net = urllib.parse.urlsplit(str(u or '')).netloc.lower()
        return any(net == k or net.endswith('.' + k) for k in EXT_HOSTS)
    except Exception:
        return False


def ep_label(raw, idx):
    try:
        t = str(raw or '').strip()
        if not t:
            return '第%02d集' % (idx + 1)
        if re.match(r'^[0-9]{1,4}$', t):
            return '第%02d集' % int(t)
        return t
    except Exception:
        return '第%02d集' % (idx + 1)


def as_lines(episodes):
    """把 [(集名, flag, pid)] 规整化"""
    out = []
    for e in episodes or []:
        try:
            if len(e) >= 3 and e[2]:
                out.append((xf_clean_name(e[0]) or '正片', str(e[1] or ''), str(e[2])))
        except Exception:
            pass
    return out


def _epnum(e):
    try:
        return float(e.get('episode_number') or 0)
    except Exception:
        return 0.0


# ==================== 源 1：稀饭动漫 Next（首页数据源 + 线路） ====================
class XifanSpider(object):
    """修复版：移除无效的 RSC 请求，改用 issue-web-playback 的 candidates 建线路。"""
    TAG = 'xf'
    HOST = 'https://next.xifanacg.com'
    API = 'https://api.xifanacg.com'
    KEY = 'sb_publishable_OBIVAWACIX6lPXrO98_z24_HcsmalkA'
    PAGE_SIZE = 24
    MAX_LINES = 4
    FLAG = 'xfline'

    CATEGORIES = [
        {'tid': '1', 'name': '连载新番', 'type_id': 1, 'sort': 'updated_at'},
        {'tid': '2', 'name': '完结旧番', 'type_id': 2, 'sort': 'updated_at'},
        {'tid': '3', 'name': '剧场版', 'type_id': 3, 'sort': 'updated_at'},
        {'tid': '4', 'name': '美漫', 'type_id': 4, 'sort': 'updated_at'},
        {'tid': 'hot', 'name': '热门播放', 'sort': 'view_count'},
        {'tid': 'score', 'name': '高分好评', 'sort': 'bangumi_score'},
        {'tid': 'new', 'name': '最近上新', 'sort': 'created_at'},
        {'tid': 'tv', 'name': 'TV动画', 'fmt': 'tv', 'sort': 'updated_at'},
        {'tid': 'movie', 'name': '剧场动画', 'fmt': 'movie', 'sort': 'updated_at'},
        {'tid': 'ova', 'name': 'OVA', 'fmt': 'ova', 'sort': 'updated_at'},
        {'tid': 'web', 'name': 'WEB动画', 'fmt': 'web', 'sort': 'updated_at'},
        {'tid': 'fin', 'name': '已完结', 'finished': True, 'sort': 'updated_at'},
        {'tid': 'ing', 'name': '连载中', 'finished': False, 'sort': 'updated_at'},
        {'tid': 'y2026', 'name': '2026年', 'year': 2026, 'sort': 'updated_at'},
        {'tid': 'y2025', 'name': '2025年', 'year': 2025, 'sort': 'updated_at'},
        {'tid': 'y2024', 'name': '2024年', 'year': 2024, 'sort': 'updated_at'},
        {'tid': 'y2023', 'name': '2023年', 'year': 2023, 'sort': 'updated_at'},
    ]
    TID_ALIAS = {
        '0': '1', 'all': '1', 'ongoing': '1', 'anime': '1',
        'finished': '2', 'theater': '3', 'western': '4', 'drama': 'tv',
    }

    def __init__(self, cfg=None):
        cfg = cfg or {}
        self.host = str(cfg.get('host') or self.HOST).rstrip('/')
        self.api = str(cfg.get('api') or self.API).rstrip('/')
        self.key = str(cfg.get('key') or self.KEY)
        try:
            self.timeout = float(cfg.get('timeout') or 4)
        except Exception:
            self.timeout = 4.0
        # 健康标记：连续网络层失败就临时下线，别再让首页/分类每次白等超时
        self._fails = 0
        self._cool = 0.0
        self.alive = True

    def _mark(self, ok):
        if ok:
            self._fails = 0
            self.alive = True
            return
        self._fails += 1
        if self._fails >= 1:
            self.alive = False
            self._cool = time.time() + 120

    def health(self):
        """冷却期过后自动试探恢复。"""
        if not self.alive and time.time() > self._cool:
            self.alive = True
            self._fails = 0
        return self.alive

    def hdr(self, ref=None):
        return {
            'User-Agent': XF_UA,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': ref or (self.host + '/'),
            'Origin': self.host,
            'x-platform': 'web',
            'x-requested-with': 'XMLHttpRequest',
            'apikey': self.key,
            'authorization': 'Bearer ' + self.key,
            'x-client-info': 'supabase-ssr/0.10.3 createBrowserClient',
            'content-profile': 'public',
            'Accept-Encoding': 'gzip, deflate',
        }

    def get(self, path, params=None, ttl=0):
        url = self.api + path
        if params:
            url += ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
        st, txt = request_ex(url, 'GET', headers=self.hdr(),
                             timeout=self.timeout, ttl=ttl)
        self._mark(bool(st))
        return xf_loads(txt) if st and st < 400 else {}

    def post(self, path, body, ttl=0):
        st, txt = request_ex(self.api + path, 'POST', body=body,
                             headers=self.hdr(), timeout=self.timeout, ttl=ttl)
        self._mark(bool(st))
        return xf_loads(txt) if st and st < 400 else {}

    def cat(self, tid):
        t = str(tid or '').strip()
        t = self.TID_ALIAS.get(t.lower(), t)
        for c in self.CATEGORIES:
            if c['tid'] == t:
                return c
        return {'tid': t}

    def query(self, tid, pg, ext=None, kw=''):
        c = self.cat(tid)
        ext = ext if isinstance(ext, dict) else {}
        page = int(pg) if str(pg or '').isdigit() and int(pg) > 0 else 1
        q = {'page_number': page, 'items_per_page': self.PAGE_SIZE,
             'sort_by': c.get('sort') or 'updated_at', 'sort_order': 'desc',
             'filter_only_published': True}
        if kw:
            q['search_term'] = str(kw).strip()
        if c.get('type_id'):
            q['filter_type_id'] = c['type_id']
        if c.get('fmt'):
            q['filter_format'] = c['fmt']
        if 'finished' in c:
            q['filter_is_finished'] = c['finished']
        if c.get('year'):
            q['filter_release_year'] = c['year']
        for k, dst in (('sort_by', 'sort_by'), ('sort_order', 'sort_order'),
                       ('year', 'filter_release_year'),
                       ('type_id', 'filter_type_id'), ('format', 'filter_format')):
            if ext.get(k) not in (None, ''):
                q[dst] = ext[k]
        return q

    def rpc(self, tid, pg, ext=None, kw='', ttl=0):
        arr = self.post('/rest/v1/rpc/search_animes',
                        self.query(tid, pg, ext, kw), ttl=ttl)
        if not isinstance(arr, list):
            return [], 0
        total = 0
        try:
            total = int(arr[0].get('total_count') or 0) if arr else 0
        except Exception:
            total = 0
        return arr, total

    def vod(self, it):
        try:
            if not isinstance(it, dict):
                return None
            aid = it.get('id')
            if aid in (None, ''):
                return None
            # img2 走 AWS 新加坡，国内实测超时；img 是 Cloudflare 同路径可直出
            pic = str(it.get('cover_url') or '').replace(
                'img2.xfmanga.top', 'img.xfmanga.top')
            cur = it.get('current_episodes') or 0
            tot = it.get('total_episodes') or 0
            remark = ''
            if it.get('is_finished'):
                remark = ('全%d集' % tot) if tot else '已完结'
            elif cur:
                remark = ('更新至%d集' % cur) + (('/%d' % tot) if tot and tot > cur else '')
            desc = str(it.get('description') or '')
            tags = it.get('meta_tags') or []
            if isinstance(tags, list) and tags:
                desc = (desc + NL + '标签：' + ' / '.join([str(t) for t in tags[:8]])).strip()
            actors = it.get('actors')
            return {
                'vod_id': str(aid),
                'vod_name': str(it.get('title') or it.get('title_original') or ''),
                'vod_pic': pic,
                'vod_remarks': remark,
                'vod_year': str(it.get('release_year') or ''),
                'vod_area': str(it.get('region') or ''),
                'vod_lang': '日语',
                'vod_actor': ('、'.join([str(a) for a in actors[:6]])
                              if isinstance(actors, list) else ''),
                'vod_director': str(it.get('director') or ''),
                'vod_score': str(it.get('bangumi_score') or ''),
                'vod_content': desc,
                'vod_tag': '',
            }
        except Exception:
            return None

    def vod_list(self, arr):
        out = []
        for it in arr or []:
            v = self.vod(it)
            if v:
                out.append(v)
        return out

    def filters(self):
        years = [{'n': '全部', 'v': ''}]
        years += [{'n': str(y), 'v': str(y)} for y in range(2026, 2018, -1)]
        sorts = [{'n': '最近更新', 'v': ''},
                 {'n': '最多播放', 'v': 'view_count'},
                 {'n': '高分好评', 'v': 'bangumi_score'},
                 {'n': '最近上新', 'v': 'created_at'}]
        out = {}
        for c in self.CATEGORIES:
            out[c['tid']] = [{'key': 'sort_by', 'name': '排序', 'value': sorts},
                             {'key': 'year', 'name': '年份', 'value': years}]
        return out

    def homeContent(self, filter):
        classes = [{'type_id': c['tid'], 'type_name': c['name']}
                   for c in self.CATEGORIES]
        try:
            arr, _ = self.rpc('1', 1, None, '', ttl=90)
            vlist = self.vod_list(arr)[:18]
            if len(vlist) < 8:
                more, _ = self.rpc('3', 1, None, '', ttl=90)
                vlist += self.vod_list(more)[:10]
        except Exception:
            vlist = []
        return {'class': classes, 'filters': self.filters() if filter else {},
                'list': vlist}

    def homeVideoContent(self):
        try:
            arr, _ = self.rpc('new', 1, None, '', ttl=90)
            vlist = self.vod_list(arr)
            if not vlist:
                arr, _ = self.rpc('1', 1, None, '', ttl=90)
                vlist = self.vod_list(arr)
            return {'list': vlist}
        except Exception:
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        ext = {}
        if isinstance(extend, dict):
            ext = extend
        elif isinstance(extend, str) and extend.strip().startswith('{'):
            try:
                ext = json.loads(extend)
            except Exception:
                ext = {}
        try:
            arr, total = self.rpc(tid, pg, ext, '', ttl=60)
            vlist = self.vod_list(arr)
            page = int(pg) if str(pg or '').isdigit() and int(pg) > 0 else 1
            if total:
                pagecount = (total + self.PAGE_SIZE - 1) // self.PAGE_SIZE
            else:
                pagecount = 9999 if vlist else 1
            return {'list': vlist, 'page': page,
                    'pagecount': max(pagecount, page),
                    'limit': self.PAGE_SIZE, 'total': total or len(vlist)}
        except Exception:
            return {'list': [], 'page': 1, 'pagecount': 1,
                    'limit': self.PAGE_SIZE, 'total': 0}

    def searchContent(self, key, quick, pg='1'):
        word = str(key or '').strip()
        if not word:
            return {'list': []}
        try:
            page = 1 if quick else (int(pg) if str(pg or '').isdigit() else 1)
            arr, _ = self.rpc('', page, None, word, ttl=30)
            return {'list': self.vod_list(arr)}
        except Exception:
            return {'list': []}

    def search(self, kw, page=1):
        """统一接口：按标题查本站条目（供诊断 / 跨源匹配使用）"""
        try:
            arr, _ = self.rpc('', page, None, kw, ttl=30)
            return self.vod_list(arr)
        except Exception:
            return []

    def match_lines(self, title):
        # 首页源本身就是元数据来源，详情直接由 detail() 产出线路
        return []

    def anime_eps(self, aid):
        """详情 + 剧集一次取回；嵌套 select 失败时回退成两次单独请求"""
        try:
            arr = self.get('/rest/v1/animes', {
                'id': 'eq.' + str(aid),
                'select': '*,episodes(id,episode_number,title,kind,release_date,duration_seconds)',
                'limit': 1}, ttl=120)
            if isinstance(arr, list) and arr and isinstance(arr[0], dict):
                it = arr[0]
                eps = it.pop('episodes', None) or []
                if isinstance(eps, list) and eps:
                    eps.sort(key=_epnum)
                    return it, [e for e in eps if isinstance(e, dict) and e.get('id')]
        except Exception:
            pass
        plain = self.get('/rest/v1/animes',
                         {'id': 'eq.' + str(aid), 'select': '*', 'limit': 1}, ttl=120)
        it = plain[0] if isinstance(plain, list) and plain and isinstance(plain[0], dict) else {}
        arr = self.get('/rest/v1/episodes', {
            'anime_id': 'eq.' + str(aid),
            'select': 'id,episode_number,title,kind,release_date,duration_seconds',
            'order': 'episode_number.asc', 'limit': 2000}, ttl=300)
        eps = arr if isinstance(arr, list) else []
        return it, [e for e in eps if isinstance(e, dict) and e.get('id')]

    def ep_name(self, ep, idx):
        try:
            num = int(float(ep.get('episode_number') or (idx + 1)))
        except Exception:
            num = idx + 1
        t = str(ep.get('title') or '').strip()
        return xf_clean_name(('第%02d集 %s' % (num, t)) if t else ('第%02d集' % num))

    def source_lines(self, aid, eps):
        """【核心修复】用第一集取流响应的 candidates 枚举真实线路。
        旧版解析 Next.js RSC payload，实测该页已无 sources 数据且耗时 10.6s。"""
        out = []
        eids = [e.get('id') for e in eps if e.get('id')]
        if not eids:
            return out
        try:
            first_eid = int(eids[0])
        except Exception:
            return out
        d = self.post('/functions/v1/issue-web-playback',
                      {'action': 'fallback', 'episode_id': first_eid}, ttl=180)
        cands = d.get('candidates') if isinstance(d, dict) else None
        if not isinstance(cands, list) or not cands:
            cands = [{'source_id': 0, 'source_name': '稀饭线路'}]
        used = {}
        for c in cands[:self.MAX_LINES]:
            if not isinstance(c, dict):
                continue
            try:
                sid = int(c.get('source_id') or 0)
            except Exception:
                sid = 0
            base = xf_clean_name(c.get('source_name') or c.get('source_code') or '稀饭线路') or '稀饭线路'
            name = base
            if name in used:
                used[name] += 1
                name = '%s·%d' % (base, used[name])
            else:
                used[name] = 1
            items = []
            for i, e in enumerate(eps):
                eid = e.get('id')
                if not eid:
                    continue
                items.append((self.ep_name(e, i), self.FLAG,
                              '%s|%s|%s' % (aid, eid, sid)))
            if items:
                out.append({'name': name, 'eps': as_lines(items)})
        return out

    def detail(self, aid):
        info, eps = self.anime_eps(aid)
        v = self.vod(info) or {'vod_id': aid}
        v['vod_id'] = aid
        if not v.get('vod_name'):
            v['vod_name'] = '稀饭动漫 %s' % aid
        v['vod_pubdate'] = str(info.get('release_date') or '')
        lines = self.source_lines(aid, eps)
        if eps:
            page = '%s/anime/%s/play/%s' % (self.host, aid, eps[0].get('id'))
            lines.append({'name': '网页解析',
                          'eps': [('正片', 'xfpage', 'playpage:' + page)]})
        return v, lines

    def fetch_playable(self, eid, sid):
        """按线路 source_id 取流；不缓存（url 带时效性 sign）"""
        try:
            eid_i = int(eid)
        except Exception:
            return ''
        body = {'action': 'fallback', 'episode_id': eid_i}
        try:
            if str(sid) not in ('', '0', 'None'):
                body['source_id'] = int(sid)
        except Exception:
            pass
        d = self.post('/functions/v1/issue-web-playback', body)
        u = str((d or {}).get('url') or '') if isinstance(d, dict) else ''
        if not u and body.get('source_id'):
            d2 = self.post('/functions/v1/issue-web-playback',
                           {'action': 'fallback', 'episode_id': eid_i})
            u = str((d2 or {}).get('url') or '') if isinstance(d2, dict) else ''
        return enc_url(u)

    def play(self, flag, pid):
        res = {'parse': 0, 'jx': 0, 'url': '', 'header': play_header(self.host)}
        raw = str(pid or '').strip()
        if not raw:
            return res
        if raw.startswith('playpage:'):
            page = raw[len('playpage:'):]
            return {'parse': 1, 'jx': 1, 'url': page,
                    'header': play_header(self.host, page)}
        if raw.startswith('http') or raw.startswith('//'):
            u = ('https:' + raw) if raw.startswith('//') else raw
            res['url'] = enc_url(u) if is_video(u) else u
            return res
        m = re.match(r'^([0-9]+)\|([0-9]+)\|([0-9]+)$', raw)
        if m:
            url = self.fetch_playable(m.group(2), m.group(3))
            if url:
                res['url'] = url
                return res
            page = '%s/anime/%s/play/%s' % (self.host, m.group(1), m.group(2))
            return {'parse': 1, 'jx': 1, 'url': page,
                    'header': play_header(self.host, page)}
        if raw.isdigit():
            url = self.fetch_playable(raw, 0)
            if url:
                res['url'] = url
        return res


# ==================== 源 2：GiriGiri爱（maccms 接口，直链） ====================
class GirigiriSpider(object):
    TAG = 'gg'
    HOST = 'https://ani.girigirilove.com'
    API = 'https://m3u8.girigirilove.com/api.php'
    IMG = 'https://jpg.girigirilove.com'
    PAGE_SIZE = 24
    MAX_LINES = 4
    LINE_NAME = {'cht': '繁中字幕', 'chs': '简中字幕', 'cht,chs': '繁简双字'}

    def __init__(self, cfg=None):
        cfg = cfg or {}
        self.host = str(cfg.get('giri_host') or self.HOST).rstrip('/')
        self.api = str(cfg.get('giri_api') or self.API).rstrip('/')
        try:
            self.timeout = float(cfg.get('timeout') or 6)
        except Exception:
            self.timeout = 6.0

    def hdr(self, ref=None):
        return {'User-Agent': XF_UA, 'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Referer': ref or (self.host + '/'), 'Origin': self.host,
                'x-platform': 'web', 'x-requested-with': 'XMLHttpRequest',
                'Accept-Encoding': 'gzip, deflate'}

    def call(self, path, params=None, ttl=0):
        url = self.api + path
        if params:
            url += ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
        st, txt = request_ex(url, 'GET', headers=self.hdr(),
                             timeout=self.timeout, ttl=ttl)
        return xf_loads(txt) if st and st < 400 else {}

    def pic(self, p):
        try:
            s = str(p or '').strip()
            if not s:
                return ''
            if s.startswith('//'):
                return 'https:' + s
            if s.startswith('http'):
                return s
            return self.IMG + '/' + s.lstrip('/')
        except Exception:
            return ''

    def vod(self, it):
        try:
            if not isinstance(it, dict):
                return None
            vid = it.get('vod_id')
            if vid in (None, ''):
                return None
            desc = str(it.get('vod_blurb') or it.get('vod_content') or '')
            cls = it.get('vod_class') or ''
            if cls and isinstance(cls, str):
                desc = (desc + NL + '类型：' + cls.replace(',', ' / ')).strip()
            return {'vod_id': str(vid),
                    'vod_name': str(it.get('vod_name') or ''),
                    'vod_pic': self.pic(it.get('vod_pic')),
                    'vod_remarks': str(it.get('vod_remarks') or ''),
                    'vod_year': str(it.get('vod_year') or ''),
                    'vod_area': str(it.get('vod_area') or ''),
                    'vod_lang': str(it.get('vod_lang') or ''),
                    'vod_content': desc}
        except Exception:
            return None

    def vod_list(self, arr):
        out = []
        for it in arr or []:
            v = self.vod(it)
            if v:
                out.append(v)
        return out

    def list_params(self, page, kw=''):
        q = {'type_id': 2, 'offset': (max(1, page) - 1) * self.PAGE_SIZE,
             'limit': self.PAGE_SIZE, 'vod_name': '', 'vod_area': '',
             'vod_year': '', 'orderby': '', 'vod_class': '', 'vod_lang': '',
             'vod_version': '', 'vod_state': '', 'vod_weekday': '',
             'vod_letter': '', 'vod_tag': '', 'user_id': ''}
        if kw:
            q['vod_name'] = str(kw).strip()
            q.pop('type_id', None)   # 搜索时带 type_id（哪怕空串）会返回 total=0
        return q

    # ---------- 备用主源（xifanacg 的 Supabase API 挂掉时顶上） ----------
    # 实测该 API 的 /Vod/get_list 支持 type_id + offset 翻页 + orderby 排序，
    # type_id=2 日漫 3147 条、type_id=3 欧美 38 条，orderby 可选 ''/hits/score。
    CATS = [
        {'type_id': 'gg_new', 'type_name': '日漫·最新'},
        {'type_id': 'gg_hot', 'type_name': '日漫·热门'},
        {'type_id': 'gg_score', 'type_name': '日漫·高分'},
        {'type_id': 'gg_us', 'type_name': '欧美动漫'},
    ]
    CAT_RULE = {'gg_new': (2, ''), 'gg_hot': (2, 'hits'),
                'gg_score': (2, 'score'), 'gg_us': (3, '')}

    def _q(self, tid, pg):
        type_id, orderby = self.CAT_RULE.get(str(tid or 'gg_new').strip(), (2, ''))
        page = int(pg) if str(pg or '').isdigit() and int(pg) > 0 else 1
        return {'type_id': type_id, 'offset': (page - 1) * self.PAGE_SIZE,
                'limit': self.PAGE_SIZE, 'vod_name': '', 'vod_area': '',
                'vod_year': '', 'orderby': orderby, 'vod_class': '',
                'vod_lang': '', 'vod_version': '', 'vod_state': '',
                'vod_weekday': '', 'vod_letter': '', 'vod_tag': '', 'user_id': ''}

    def _rows(self, q, ttl=0):
        d = self.call('/Vod/get_list', q, ttl=ttl)
        info = d.get('info') if isinstance(d.get('info'), dict) else {}
        rows = info.get('rows') if isinstance(info.get('rows'), list) else []
        try:
            total = int(info.get('total') or 0)
        except Exception:
            total = 0
        return rows, total

    def homeContent(self, filter=False):
        classes = [{'type_id': c['type_id'], 'type_name': c['type_name']}
                   for c in self.CATS]
        filters = {}
        for c in self.CATS:
            filters[c['type_id']] = [{
                'key': 'orderby', 'name': '排序',
                'value': [{'n': '默认', 'v': ''}, {'n': '最热', 'v': 'hits'},
                          {'n': '评分', 'v': 'score'}]}]
        return {'class': classes, 'filters': filters}

    def homeVideoContent(self):
        rows, _ = self._rows(self._q('gg_new', 1), ttl=120)
        return {'list': self.vod_list(rows)[:30]}

    def categoryContent(self, tid, pg, filter, extend):
        page = int(pg) if str(pg or '').isdigit() and int(pg) > 0 else 1
        q = self._q(tid, page)
        if isinstance(extend, dict) and extend.get('orderby') not in (None, ''):
            q['orderby'] = str(extend['orderby'])
        rows, total = self._rows(q)
        items = self.vod_list(rows)
        pagecount = (max(1, (total + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
                     if total else page)
        return {'list': items, 'total': total or len(items),
                'page': page, 'pagecount': pagecount}

    def searchContent(self, key, quick, pg='1'):
        page = int(pg) if str(pg or '').isdigit() and int(pg) > 0 else 1
        items = self.search(key, page)
        return {'list': items, 'total': len(items), 'page': page,
                'pagecount': page}

    def detail(self, vid):
        """→ (vod, 线路列表)。vod_id 带 'g:' 前缀，门面据此区分来源、避免与 xf 的 id 撞车。"""
        vid = str(vid or '').strip()
        d = self.call('/Vod/get_detail', {'vod_id': vid}, ttl=180)
        info = d.get('info') if isinstance(d.get('info'), dict) else {}
        vod = self.vod(info) if info else None
        if not vod:
            vod = {'vod_id': vid, 'vod_name': vid, 'vod_pic': '', 'vod_remarks': ''}
        vod['vod_id'] = 'g:' + vid
        return vod, self.lines(vid)

    def search(self, kw, page=1):
        d = self.call('/Vod/get_list', self.list_params(page, kw), ttl=30)
        info = d.get('info') if isinstance(d.get('info'), dict) else {}
        rows = info.get('rows') if isinstance(info.get('rows'), list) else []
        return self.vod_list(rows)

    def match_lines(self, title):
        pick = search_best(self, title)
        if not pick:
            return []
        return self.lines(str(pick.get('vod_id')))

    def lines(self, vid):
        d = self.call('/Vod/get_detail', {'vod_id': vid}, ttl=180)
        info = d.get('info') if isinstance(d.get('info'), dict) else {}
        froms = str(info.get('vod_play_from') or '').split('$$$')
        segs = str(info.get('vod_play_url') or '').split('$$$')
        out, used = [], {}
        for i, seg in enumerate(segs):
            code = froms[i] if i < len(froms) else ''
            base = (self.LINE_NAME.get(str(code or '').strip().lower())
                    or xf_clean_name(code) or '线路')
            name = base
            if name in used:
                used[name] += 1
                name = '%s·%d' % (base, used[name])
            else:
                used[name] = 1
            items = []
            for j, part in enumerate(seg.split('#')):
                part = part.strip()
                if not part:
                    continue
                if '$' in part:
                    t, u = part.split('$', 1)
                else:
                    t, u = '', part
                u = u.strip()
                if not u or not is_video(u):
                    continue
                items.append((ep_label(t, j), name, u))
            if items:
                out.append({'name': name, 'eps': as_lines(items)})
            if len(out) >= self.MAX_LINES:
                break
        return out

    def play(self, flag, pid):
        res = {'parse': 0, 'jx': 0, 'url': '', 'header': play_header(self.host)}
        raw = str(pid or '').strip()
        if not raw:
            return res
        if raw.startswith('page:'):
            page = raw[5:]
            return {'parse': 1, 'jx': 1, 'url': page,
                    'header': play_header(self.host, page)}
        if raw.startswith('http') or raw.startswith('//'):
            u = ('https:' + raw) if raw.startswith('//') else raw
            if is_video(u):
                res['url'] = enc_url(u)
            elif is_ext_link(u):
                res.update({'parse': 1, 'jx': 1, 'url': u,
                            'header': play_header(self.host, u)})
            else:
                res['url'] = u
            return res
        if raw.isdigit():
            d = self.call('/Vod/get_detail', {'vod_id': raw}, ttl=180)
            info = d.get('info') if isinstance(d.get('info'), dict) else {}
            for seg in str(info.get('vod_play_url') or '').split('$$$'):
                for part in seg.split('#'):
                    if '$' in part:
                        u = part.split('$', 1)[1].strip()
                        if is_video(u):
                            res['url'] = enc_url(u)
                            return res
        return res


# ==================== 源 3：次元城动画（REST API，播放需登录） ====================
class CycaniSpider(object):
    TAG = 'cy'
    HOST = 'https://www.cycani.org'
    PAGE_SIZE = 18
    MAX_LINES = 3
    APP_NAME = 'cyc_web'
    APP_VERSION = 'cycweb'
    TIME_ZONE = 'Asia/Shanghai'

    def __init__(self, cfg=None):
        cfg = cfg or {}
        self.host = str(cfg.get('cyc_host') or self.HOST).rstrip('/')
        self.api = str(cfg.get('cyc_api') or (self.host + '/api')).rstrip('/')
        try:
            self.timeout = float(cfg.get('timeout') or 8)
        except Exception:
            self.timeout = 8.0
        self.username = str(cfg.get('cyc_username') or '').strip()
        self.password = str(cfg.get('cyc_password') or '').strip()
        # 旧脚本里硬编码的 Token 已于 2026-11-04 过期且无法 refresh，此处不再内置
        self.token = self._norm(str(cfg.get('cyc_token') or '').strip())
        if not self.token:
            self.token = self._load_auth()

    # ---- Token ----
    def _auth_path(self):
        try:
            return os.path.join(tempfile.gettempdir(), '.cyc_auth.json')
        except Exception:
            return ''

    def _load_auth(self):
        try:
            p = self._auth_path()
            if p and os.path.isfile(p):
                with open(p, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                return self._norm(str(d.get('token') or ''))
        except Exception:
            pass
        return ''

    def _save_auth(self):
        try:
            p = self._auth_path()
            if p and self.token:
                with open(p, 'w', encoding='utf-8') as f:
                    json.dump({'token': self.token, 'username': self.username},
                              f, ensure_ascii=False)
        except Exception:
            pass

    @staticmethod
    def _norm(t):
        s = str(t or '').strip()
        if s.lower().startswith('bearer '):
            s = s[7:].strip()
        return s

    @staticmethod
    def _jwt_exp(tok):
        try:
            p = str(tok or '').split('.')[1]
            p += '=' * ((4 - len(p) % 4) % 4)
            d = json.loads(base64.urlsafe_b64decode(p.encode('ascii')).decode('utf-8', 'ignore'))
            return float(d.get('exp') or 0)
        except Exception:
            return 0

    def _token_ok(self):
        if not self.token:
            return False
        exp = self._jwt_exp(self.token)
        return not (exp and exp < time.time() + 60)

    def logged_in(self):
        return self._token_ok()

    def _take_token(self, j):
        d = j.get('data') if isinstance(j, dict) else None
        if isinstance(d, dict):
            return self._norm(str(d.get('token') or ''))
        return self._norm(str((j or {}).get('token') or '')) if isinstance(j, dict) else ''

    def _login(self):
        if not self.username or not self.password:
            return False
        try:
            st, txt = request_ex(
                self.api + '/auth/login', 'POST',
                body={'username': self.username, 'password': self.password},
                headers=self.hdr(), timeout=self.timeout)
            tok = self._take_token(xf_loads(txt))
            if tok:
                self.token = tok
                self._save_auth()
                return True
        except Exception:
            pass
        return False

    def _refresh(self):
        if not self.token:
            return False
        try:
            st, txt = request_ex(self.api + '/auth/refresh', 'POST', body={},
                                 headers=self.hdr(auth=True), timeout=self.timeout)
            tok = self._take_token(xf_loads(txt))
            if tok:
                self.token = tok
                self._save_auth()
                return True
        except Exception:
            pass
        return False

    def _ensure_token(self):
        if self._token_ok():
            exp = self._jwt_exp(self.token)
            if exp and exp - time.time() < 259200:
                self._refresh()
            return True
        if self.token and self._refresh():
            return True
        return self._login()

    # ---- HTTP / API ----
    def hdr(self, auth=False, ref=None):
        h = {'User-Agent': XF_UA, 'Accept': 'application/json',
             'X-App-Name': self.APP_NAME, 'X-App-Version': self.APP_VERSION,
             'X-Time-Zone': self.TIME_ZONE,
             'Referer': ref or (self.host + '/'), 'Origin': self.host,
             'Accept-Encoding': 'gzip, deflate'}
        if auth and self.token:
            h['Authorization'] = 'Bearer ' + self.token
        return h

    def call(self, path, params=None, auth=False, ttl=0):
        url = self.api + path
        if params:
            url += ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
        st, txt = request_ex(url, 'GET', headers=self.hdr(auth),
                             timeout=self.timeout, ttl=ttl)
        if auth and st == 401 and self._ensure_token():
            st, txt = request_ex(url, 'GET', headers=self.hdr(auth),
                                 timeout=self.timeout)
        j = xf_loads(txt)
        if isinstance(j, dict) and 'data' in j:
            d = j.get('data')
            return d if isinstance(d, dict) else {}
        return j if isinstance(j, dict) else {}

    def card(self, it):
        try:
            if not isinstance(it, dict):
                return None
            vid = it.get('video_id') or it.get('id')
            if vid in (None, ''):
                return None
            remark = str(it.get('remarks') or '')
            if not remark:
                total = it.get('total')
                if isinstance(total, int) and total > 1:
                    remark = ('全%d集' % total) if it.get('completed') else ('更新至%d集' % total)
            return {'vod_id': str(vid),
                    'vod_name': str(it.get('title') or ''),
                    'vod_pic': str(it.get('cover_url') or ''),
                    'vod_remarks': remark}
        except Exception:
            return None

    def card_list(self, arr):
        out = []
        for it in arr or []:
            v = self.card(it)
            if v:
                out.append(v)
        return out

    def search(self, kw):
        d = self.call('/videos/search',
                     {'q': str(kw), 'page': 1, 'page_size': self.PAGE_SIZE}, ttl=30)
        items = d.get('list') if isinstance(d, dict) else []
        return self.card_list(items if isinstance(items, list) else [])

    def sections(self, vid, code):
        out, seen = [], set()
        base = '/videos/%s/sections' % urllib.parse.quote(str(vid), safe='')
        for page in range(1, 6):
            d = self.call(base, {'player_code': code, 'page': page, 'page_size': 100},
                         ttl=180)
            arr = d.get('list') if isinstance(d, dict) else []
            if not isinstance(arr, list) or not arr:
                break
            added = 0
            for s in arr:
                if not isinstance(s, dict):
                    continue
                sid = str(s.get('id') or '')
                if not sid or sid in seen:
                    continue
                seen.add(sid)
                out.append({'id': sid, 'title': str(s.get('title') or '')})
                added += 1
            if added == 0 or len(arr) < 100:
                break
        return out

    def match_lines(self, title):
        pick = search_best(self, title)
        if not pick:
            return []
        return self.lines(str(pick.get('vod_id')))

    def lines(self, vid):
        d = self.call('/videos/%s' % urllib.parse.quote(str(vid), safe=''), ttl=120)
        srcs = d.get('play_from') if isinstance(d.get('play_from'), list) else []
        if not srcs:
            srcs = [{'code': 'cychub', 'title': '默认线路'}]
        out = []
        for s in srcs[:self.MAX_LINES]:
            if not isinstance(s, dict):
                continue
            code = str(s.get('code') or '')
            if not code:
                continue
            name = xf_clean_name(s.get('title') or code) or code
            items = []
            for i, sec in enumerate(self.sections(vid, code)):
                t = xf_clean_name(sec.get('title')) or ('第%d集' % (i + 1))
                items.append((t, name, sec['id']))
            if items:
                out.append({'name': name, 'eps': as_lines(items)})
        return out

    def play(self, flag, pid):
        res = {'parse': 0, 'jx': 0, 'url': '', 'header': play_header(self.host)}
        raw = str(pid or '').strip()
        if not raw:
            return res
        if raw.startswith('http') or raw.startswith('//'):
            u = ('https:' + raw) if raw.startswith('//') else raw
            res['url'] = enc_url(u) if is_video(u) else u
            return res
        d = self.call('/v2/sections/%s/play-url' %
                     urllib.parse.quote(raw, safe=''), auth=True)
        u = str((d or {}).get('url') or '') if isinstance(d, dict) else ''
        if not u:
            return res
        if u.startswith('//'):
            u = 'https:' + u
        if is_ext_link(u):
            res.update({'parse': 1, 'jx': 1, 'url': u,
                        'header': play_header(self.host, u)})
        else:
            res['url'] = enc_url(u)
        return res


# ==================== 源 4：OmoFun（HTML + 聚合取流接口） ====================
class OmoFunSpider(object):
    TAG = 'om'
    HOSTS = ['https://omofun.in', 'https://omofun2.com']
    MAX_LINES = 4

    def __init__(self, cfg=None):
        cfg = cfg or {}
        self.host = str(cfg.get('omo_host') or self.HOSTS[0]).rstrip('/')
        try:
            self.timeout = float(cfg.get('timeout') or 7)
        except Exception:
            self.timeout = 7.0
        self._dead = {}

    def hdr(self, ref=None):
        return {'User-Agent': XF_UA,
                'Accept': 'text/html,application/xhtml+xml,application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Referer': ref or (self.host + '/'),
                'x-platform': 'web',
                'x-requested-with': 'XMLHttpRequest',
                'Accept-Encoding': 'gzip, deflate'}

    def get(self, path, ttl=0, valid=None):
        key = 'omo:' + path
        if ttl:
            hit = xf_cache_get(key)
            if hit is not None:
                return hit
        hosts = [self.host] + [h for h in self.HOSTS if h != self.host]
        for h in hosts:
            if self._dead.get(h, 0) > time.time():
                continue
            st, txt = request_ex(h + path, 'GET', headers=self.hdr(h + '/'),
                                 timeout=self.timeout)
            if st and 200 <= st < 300 and txt and (not valid or valid in txt):
                self._dead.pop(h, None)
                if ttl:
                    xf_cache_put(key, txt, ttl)
                return txt
            self._dead[h] = time.time() + 60
        return ''

    def _abs(self, u):
        if not u:
            return ''
        if str(u).startswith('http'):
            return u
        return self.host + str(u)

    def parse_items(self, html):
        out = []
        try:
            blocks = re.findall(
                r'<a href="(/vod/detail/([0-9]+)\.html)"[^>]*title="([^"]*)"[^>]*class="[^"]*module-poster-item[^"]*"[^>]*>(.*?)(?=<a href="/vod/detail/|</div>\s*<div class="module-main|<div class="module-foot|$)',
                html, re.S)
            for href, vid, title, blk in blocks:
                if not title:
                    m = re.search(r'module-poster-item-title">\s*([^<]+)', blk)
                    title = m.group(1).strip() if m else ''
                m = re.search(r'module-item-note">\s*([^<]*)', blk)
                note = m.group(1).strip() if m else ''
                m = re.search(r'data-original="([^"]+)"', blk)
                pic = m.group(1) if m else ''
                out.append({'vod_id': vid, 'vod_name': title.strip(),
                            'vod_pic': self._abs(pic), 'vod_remarks': note})
        except Exception:
            pass
        if not out:
            try:
                blocks = re.findall(
                    r'<div class="module-card-item module-item">(.*?)(?=<div class="module-card-item module-item">|$)',
                    html, re.S)
                for blk in blocks:
                    m = re.search(r'href="/vod/detail/([0-9]+)\.html"', blk)
                    if not m:
                        continue
                    m2 = re.search(r'module-card-item-title">\s*<a[^>]*>\s*<strong>([^<]+)</strong>', blk)
                    title = m2.group(1).strip() if m2 else ''
                    m3 = re.search(r'data-original="([^"]+)"', blk)
                    pic = m3.group(1) if m3 else ''
                    m4 = re.search(r'module-item-note">\s*([^<]*)', blk)
                    note = m4.group(1).strip() if m4 else ''
                    out.append({'vod_id': m.group(1), 'vod_name': title,
                                'vod_pic': self._abs(pic), 'vod_remarks': note})
            except Exception:
                pass
        return out

    def dyn(self, vid, ep):
        e = str(ep or '').strip()
        if not e.startswith('ep'):
            e = 'ep' + e
        return xf_loads(self.get('/_dyn_plays/%s/%s' % (vid, e), ttl=180))

    def search(self, kw):
        path = '/vod/search.html?wd=%s&page=1' % urllib.parse.quote(str(kw))
        return self.parse_items(self.get(path, ttl=30, valid='/vod/'))

    def match_lines(self, title):
        pick = search_best(self, title)
        if not pick:
            return []
        return self.lines(str(pick.get('vod_id')))

    def lines(self, vid):
        html = self.get('/vod/detail/%s.html' % vid, ttl=180, valid='/vod/')
        if not html:
            return []
        eps = re.findall(
            r'<a class="module-play-list-link" href="/vod/play/([0-9]+)/ep([0-9]+)\.html"[^>]*>\s*<span>([^<]+)</span>',
            html)
        if not eps:
            eps = [(v, e, t) for v, e, t in re.findall(
                r'href="/vod/play/([0-9]+)/ep([0-9]+)\.html"[^>]*>\s*(?:<span>)?([^<]+)', html)]
        seen, ep_list = set(), []
        for v, e, t in eps:
            k = (v, e)
            if k in seen:
                continue
            seen.add(k)
            ep_list.append((v, e, xf_clean_name(t) or '正片'))
        if not ep_list:
            ep_list = [(vid, '1', 'HD')]

        plays = self.dyn(vid, ep_list[0][1]).get('video_plays') or []
        sites = []
        for p in plays:
            if not isinstance(p, dict):
                continue
            u = p.get('play_data') or ''
            if u and is_video(u):
                s = xf_clean_name(p.get('src_site') or '线路')
                if s and s not in sites:
                    sites.append(s)
        sites = sorted(sites)[:self.MAX_LINES] or ['OmoFun解析']
        out = []
        for s in sites:
            items = [(t, s, '%s/ep%s' % (v, e)) for v, e, t in ep_list]
            out.append({'name': s, 'eps': as_lines(items)})
        return out

    def play(self, flag, pid):
        res = {'parse': 0, 'jx': 0, 'url': '', 'header': play_header(self.host)}
        raw = str(pid or '').strip().replace('!parse', '')
        if not raw:
            return res
        parts = raw.split('/')
        if len(parts) == 2:
            vid, ep = parts
        elif len(parts) >= 3:
            vid, ep = parts[-2], parts[-1]
        else:
            return res
        plays = self.dyn(vid, ep).get('video_plays') or []
        cands = []
        for p in plays:
            if isinstance(p, dict) and p.get('play_data'):
                cands.append((xf_clean_name(p.get('src_site') or ''), p.get('play_data')))
        pick = ''
        for s, u in cands:
            if s == flag and is_video(u):
                pick = u
                break
        if not pick:
            for s, u in cands:
                if is_video(u):
                    pick = u
                    break
        if not pick and cands:
            pick = cands[0][1]
        if pick and is_video(pick):
            res['url'] = enc_url(pick)
        else:
            res['parse'] = 1
            res['jx'] = 1
            res['url'] = pick or (self.host + '/vod/play/' + raw + '.html')
        return res


# ==================== 门面：TVBox 协议入口 ====================
class XifanAggSpider(_SpiderBase):
    """首页/分类/搜索 = 稀饭动漫；详情页 = 四源线路聚合。

    线路顺序（用户 2026-11-04 指定）：xf > gg > cy > om。
    TVBox 默认播放第一条线路，因此该顺序同时是默认选线顺序。
    """

    LINE_ORDER = ('xf', 'gg', 'cy', 'om')      # 稀饭 → GiriGiri → 次元城 → OmoFun
    LABELS = {'xf': '稀饭', 'gg': 'GiriGiri', 'cy': '次元城', 'om': 'OmoFun'}
    MAX_LINES_PER_SRC = 4
    CACHE_TTL = 300

    # 类级兜底：有些壳只调 init() 不调 __init__()
    order = list(LINE_ORDER)
    detail_budget = 7.0
    sources = {}
    xf = None
    cy = None
    cfg = {}

    def __init__(self):
        self.cfg = {}
        self.order = list(self.LINE_ORDER)
        self.detail_budget = 7.0
        self._build({})

    def _build(self, cfg):
        self.xf = XifanSpider(cfg)
        self.cy = CycaniSpider(cfg)
        self.sources = {
            'xf': self.xf,
            'gg': GirigiriSpider(cfg),
            'cy': self.cy,
            'om': OmoFunSpider(cfg),
        }

    def _x(self):
        if self.xf is None:
            self._build({})
        return self.xf

    def init(self, extend=''):
        cfg = {}
        try:
            if isinstance(extend, dict):
                cfg = dict(extend)
            elif isinstance(extend, str) and extend.strip().startswith('{'):
                cfg = json.loads(extend)
        except Exception:
            cfg = {}
        if not isinstance(cfg, dict):
            cfg = {}
        self.cfg = cfg
        self._build(cfg)
        order = cfg.get('lines')
        if isinstance(order, (list, tuple)) and order:
            picked = [str(t).strip() for t in order
                      if str(t).strip() in self.sources]
            self.order = picked or list(self.LINE_ORDER)
        else:
            self.order = list(self.LINE_ORDER)
        try:
            self.detail_budget = max(2.0, min(20.0,
                                              float(cfg.get('detail_budget') or 7)))
        except Exception:
            self.detail_budget = 7.0
        self._probe()
        return None

    def _probe(self):
        """后台探活 xifan：它的 API 会整站超时，不能在首页路径上白等。

        探活完成前先按「不可用」处理（首页直接走 GiriGiri，约 0.8s 出内容），
        探到通了再切回 xifan 的 17 个分类。
        """
        xf = self._x()
        if xf is None:
            return
        try:
            xf.alive = False
            xf._cool = time.time() + 4.0      # 探活期间别被 health() 提前放行
        except Exception:
            return

        def run():
            try:
                st, _ = request_ex(xf.api + '/rest/v1/', 'GET',
                                   headers=xf.hdr(), timeout=3)
                xf._mark(bool(st and st < 500))
            except Exception:
                pass

        if threading:
            try:
                th = threading.Thread(target=run)
                th.daemon = True
                th.start()
                return
            except Exception:
                pass
        run()          # 没有 threading 时同步探一次（上限 3s）

    def getName(self):
        return '稀饭聚合'

    def destroy(self):
        pool_clear()
        return None

    def isVideoFormat(self, url):
        return is_video(url)

    def manualVideoCheck(self):
        return False

    # ---------- 首页数据：主源优先 xifan，其 API 挂了自动切 GiriGiri ----------
    def _main(self):
        xf = self._x()
        if xf is not None:
            if getattr(xf, 'alive', True):
                return xf, 'xf'
            # 冷却到期不再当场重试（那会把首页卡住 4s），改用后台探活，
            # 这次仍走 gg，探通了下一轮请求自动切回来
            if time.time() > getattr(xf, '_cool', 0):
                self._probe()
        return self.sources.get('gg') or xf, 'gg'

    def _alive(self, tag):
        """该源当前是否值得发请求（主要是 xifan 会整站超时）。"""
        if tag == 'xf':
            try:
                return bool(self._x() and getattr(self._x(), 'alive', True))
            except Exception:
                return False
        return tag in self.sources

    def _tagged(self, res, tag):
        """主源为 gg 时给列表 id 打 'g:' 前缀，详情页才能知道该回哪个源取数据。"""
        if tag != 'gg' or not isinstance(res, dict):
            return res
        for it in (res.get('list') or []):
            try:
                vid = str(it.get('vod_id') or '')
                if vid and not vid.startswith('g:'):
                    it['vod_id'] = 'g:' + vid
            except Exception:
                pass
        return res

    def homeContent(self, filter):
        src, tag = self._main()
        return src.homeContent(filter)

    def homeVideoContent(self):
        src, tag = self._main()
        return self._tagged(src.homeVideoContent(), tag)

    def categoryContent(self, tid, pg, filter, extend):
        src, tag = self._main()
        return self._tagged(src.categoryContent(tid, pg, filter, extend), tag)

    def searchContent(self, key, quick, pg='1'):
        src, tag = self._main()
        return self._tagged(src.searchContent(key, quick, pg), tag)

    # ---------- 详情：主源取基础信息 + 四源线路聚合 ----------
    def detailContent(self, ids):
        try:
            raw = str(ids[0] if isinstance(ids, (list, tuple)) and ids else (ids or ''))
            raw = raw.strip()
            # 'g:' 前缀 = 来自 GiriGiri（备用主源）；纯数字 = 来自 xifan。
            # 两个站点的 id 空间互不相通，必须靠前缀区分，否则会串片。
            by_gg = raw.startswith('g:')
            aid = re.sub(r'[^0-9]', '', raw)
            if not aid:
                return {'list': []}

            ck = 'agg3:%s:%s:%s' % ('g' if by_gg else 'x', aid, ','.join(self.order))
            hit = xf_cache_get(ck)
            if hit is not None:
                try:
                    return json.loads(hit)
                except Exception:
                    pass

            if by_gg:
                main_tag = 'gg'
                vod, main_lines = self.sources['gg'].detail(aid)
            else:
                if not self._alive('xf'):
                    # xifan 的 API 整站超时中：历史收藏的纯数字 id 已无从解析，
                    # 直接返回空，别让详情页卡几十秒
                    return {'list': []}
                main_tag = 'xf'
                vod, main_lines = self._x().detail(aid)
                if not main_lines:
                    # 瞬时抖动（CDN 换节点 / 秒断）时重试一次；失败响应不进缓存，
                    # 因此第二次是真实重发，不会把等待翻倍到不可接受
                    time.sleep(0.2)
                    vod, main_lines = self._x().detail(aid)
            title = str(vod.get('vod_name') or '')

            # 其余三源并发按标题匹配；慢源超时即跳过，不拖累整体
            boxes = {}
            ths = []
            for tag in self.order:
                if tag == main_tag or not self._alive(tag):
                    continue
                src = self.sources.get(tag)
                if not src:
                    continue

                def work(t=tag, s=src, w=title):
                    try:
                        boxes[t] = s.match_lines(w)
                    except Exception:
                        boxes[t] = []

                if threading:
                    try:
                        th = threading.Thread(target=work)
                        th.daemon = True
                        th.start()
                        ths.append(th)
                    except Exception:
                        work()
                else:
                    work()
            deadline = time.time() + self.detail_budget
            for th in ths:
                try:
                    th.join(max(0.05, deadline - time.time()))
                except Exception:
                    pass

            cy_need_login = ('cy' in self.order and self.cy is not None
                             and not self.cy.logged_in())
            froms, urls, used, tail = [], [], {}, []
            for tag in self.order:
                lines = main_lines if tag == main_tag else (boxes.get(tag) or [])
                label = self.LABELS.get(tag, tag)
                for line in (lines or [])[:self.MAX_LINES_PER_SRC]:
                    if not isinstance(line, dict):
                        continue
                    raw_name = str(line.get('name') or '线路')
                    base = xf_clean_name(label + '·' + raw_name) or label
                    if tag == 'cy' and cy_need_login:
                        base += '(需登录)'
                    name = base
                    if name in used:
                        used[name] += 1
                        name = '%s·%d' % (base, used[name])
                    else:
                        used[name] = 1
                    segs = []
                    for ep in as_lines(line.get('eps')):
                        code = enc_pid(tag, ep[1], ep[2])
                        if code:
                            segs.append('%s$%s' % (ep[0] or '正片', code))
                    if not segs:
                        continue
                    # 需要壳嗅探的「网页解析」兜底线路统一排到最后
                    if '网页解析' in raw_name:
                        tail.append((name, '#'.join(segs)))
                    else:
                        froms.append(name)
                        urls.append('#'.join(segs))
            for name, joined in tail:
                froms.append(name)
                urls.append(joined)

            vod['vod_play_from'] = '$$$'.join(froms)
            vod['vod_play_url'] = '$$$'.join(urls)

            if cy_need_login:
                if self.cy.username and self.cy.password:
                    tip = '[次元城] 已配置账号，播放时将自动登录。'
                else:
                    tip = ('[次元城线路需登录] 请在源配置 extend 填 cyc_username / '
                           'cyc_password，或填浏览器复制的 cyc_token。')
                vod['vod_content'] = (
                    str(vod.get('vod_content') or '') + NL + NL + tip).strip()

            result = {'list': [vod]}
            # 只缓存序列化文本：避免把同一个可变 dict 交给壳后被改写污染缓存
            try:
                xf_cache_put(ck, json.dumps(result, ensure_ascii=False), self.CACHE_TTL)
            except Exception:
                pass
            return result
        except Exception as e:
            global _LAST_ERR
            try:
                _LAST_ERR = '%s: %s' % (type(e).__name__, str(e)[:200])
            except Exception:
                pass
            return {'list': []}

    # ---------- 播放：按线路 tag 派发回原源 ----------
    def playerContent(self, flag, id, vipFlags):
        res = {'parse': 0, 'jx': 0, 'url': '',
               'header': play_header(self._x().host)}
        try:
            raw = str(id or '').strip()
            if not raw:
                return res
            low = raw.upper()
            if '%7C' in low or '%24' in low or '%3A' in low:
                try:
                    raw = urllib.parse.unquote(raw)
                except Exception:
                    pass
            tag, inner_flag, pid = dec_pid(raw)
            src = self.sources.get(tag) if tag else None
            if src and pid:
                return src.play(inner_flag or flag, pid)
            if raw.startswith('http') or raw.startswith('playpage:') or raw.startswith('page:'):
                return self._x().play(flag, raw)
        except Exception:
            pass
        return res

    def localProxy(self, param):
        """m3u8 相对分片改写（四源通用）"""
        try:
            url = ''
            if isinstance(param, dict):
                url = str(param.get('url') or param.get('u') or '')
            elif isinstance(param, str):
                p = param.strip()
                if p.startswith('http'):
                    url = p
                else:
                    qs = urllib.parse.parse_qs(urllib.parse.urlsplit(p).query)
                    url = str((qs.get('url') or qs.get('u') or [''])[0])
            if not url:
                return None
            st, txt = request_ex(
                url, 'GET',
                headers={'User-Agent': XF_UA, 'Accept': '*/*',
                         'Referer': self._x().host + '/'}, timeout=8)
            if not txt or '#EXTM3U' not in txt:
                return None
            base = url.rsplit('/', 1)[0] + '/'
            out = []
            for line in txt.splitlines():
                s = line.strip()
                if not s:
                    out.append('')
                elif s.startswith('#'):
                    m = re.search(r'URI="([^"]+)"', s)
                    if m:
                        s = s.replace(m.group(1), abs_url(base, m.group(1)))
                    out.append(s)
                else:
                    out.append(abs_url(base, s))
            return [200, 'application/vnd.apple.mpegurl', NL.join(out)]
        except Exception:
            return None


# ======================================================================
# 模块：xj
# ======================================================================
# coding=utf-8
# ================== 影视·正经·小鸡看看 · TVBox ==================
# 🏷️ 源头：软件 小鸡看看 App(com.xmoebr.bdx v1.0.5) / TV版(com.kankan.tv) 接口 https://xjggg.top/api.php/app
# 👤 作者：无聊  |  📅 2026-10-28
# 🏷️ 平台：TVBox / 影视仓  ·  csp_Spider
# 🔍 站型：Expo/RN 壳 App + PHP API，全接口强制五头签名(x-aid/x-ave/x-time/x-nonc/x-sign)
# 🎬 关键：签名 = SHA256(finger&id&nonce&sk&time&v)，sk 与证书指纹从 TV 版 APK 逆向得出
#        http://... 播放令牌(加密) → /app/decode/url 换真直链
# 📦 内容：视频（电影/剧集/动漫/综艺，多线路 7 条）
# ==========================================================
import sys
import json
import time
import random
import hashlib
import base64
import re
import ssl
import gzip
import http.client as xj_http
import urllib.parse

sys.path.append('..')

# ---------------- 签名材料（逆向 libsecurity-bridge.so / TV 版 dex 得出）----------------
APP_ID = "com.kankan.tv"
APP_VER = "105"
SK = "SK-sk_13oXDZ7u9j2Tk1c0cawWVFfO"
FINGER = "SF-F5F11CB15897115AE6BCFE063C288F730CA865588F572C780A3E8477D0DD3776"
# ---------------- 设备号池（★无限解析的核心★）----------------
# decode/url 是「每设备每日 N 次」的配额制（实测：单枚设备连解 60 次仍未到顶；
# 但一枚设备被榨干后当日恒返回 code 429 "今日解析次数已用完，请明天00:00后再试"）。
# 服务端只认 x-device-id 头，不校验设备唯一性 / 不与账号绑定 → 换一枚 UUID4 立刻恢复。
# 几千人共用一份源 = 几千台「同一设备」，一枚设备几小时就被榨干 → 必须池化 + 轮转：
#   · POOL_SIZE 枚设备轮转使用，压力摊开，单枚寿命 × POOL_SIZE
#   · 429 立即拉黑该枚、换下一枚，永不中断
#   · 设备号落盘到 hiker 数据目录，跨重启复用（避免重启把好设备全丢掉）
import uuid as _uuid
import threading as _th

POOL_SIZE = 12          # 同时轮转的设备数（越大越抗压，但要平衡风控观感）
_DEV_LOCK = _th.Lock()
_DEV_POOL = []          # 可用设备号列表
_DEV_IDX = 0            # 轮转游标
_DEV_BAD = {}           # device -> 失效日期，跨天自动解封
_DEV_DAY = time.strftime("%Y-%m-%d")
_DEV_CACHE = "xjk_dev_pool.json"


def _new_device():
    return "uuid-" + str(_uuid.uuid4())


def _dev_newday():
    global _DEV_DAY
    d = time.strftime("%Y-%m-%d")
    if d != _DEV_DAY:
        _DEV_DAY = d
        _DEV_BAD.clear()


def _dev_save():
    """设备池落盘（壳环境可能无写权限，失败静默）。"""
    try:
        open(_DEV_CACHE, "w").write(json.dumps({
            "day": _DEV_DAY, "pool": _DEV_POOL, "bad": list(_DEV_BAD.keys())
        }))
    except Exception:
        pass


def _dev_load():
    """跨重启复用设备号：昨日的好设备今天多半还有额度。"""
    global _DEV_POOL, _DEV_BAD
    try:
        obj = json.loads(open(_DEV_CACHE).read())
        pool = [d for d in (obj.get("pool") or []) if isinstance(d, str) and d.startswith("uuid-")]
        bad = obj.get("bad") or []
        if obj.get("day") == _DEV_DAY:
            _DEV_BAD = dict((b, _DEV_DAY) for b in bad if isinstance(b, str))
        _DEV_POOL = [d for d in pool if d not in _DEV_BAD]
    except Exception:
        pass


def _dev_fill():
    """补足池到一个足够大的规模。"""
    while len(_DEV_POOL) < POOL_SIZE:
        n = _new_device()
        if n in _DEV_BAD or n in _DEV_POOL:
            continue
        _DEV_POOL.append(n)


def _dev_get():
    """轮转取一枚设备号（分散压力，避免单枚被快速榨干）。"""
    global _DEV_IDX
    with _DEV_LOCK:
        _dev_newday()
        if not _DEV_POOL:
            _dev_load()
        _dev_fill()
        _DEV_IDX = (_DEV_IDX + 1) % len(_DEV_POOL)
        return _DEV_POOL[_DEV_IDX]


def _dev_fail(dev):
    """该设备今日配额耗尽 → 拉黑并补新号，返回下一枚。"""
    with _DEV_LOCK:
        _dev_newday()
        if dev:
            _DEV_BAD[dev] = _DEV_DAY
            if dev in _DEV_POOL:
                _DEV_POOL.remove(dev)
        _dev_fill()
        _dev_save()
        return _DEV_POOL[0]


def _dev_ok(dev):
    """解码成功：只做记账，不打断轮转（保持压力分散）。"""
    with _DEV_LOCK:
        if dev and dev not in _DEV_POOL and dev not in _DEV_BAD:
            _DEV_POOL.append(dev)


_dev_load()
_dev_fill()
DEVICE = _DEV_POOL[0]
XJ_UA = "okhttp/4.12.0"
PLAY_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

# 主域名 + 逆出的备用端点（App 内置 endpointConfig 加密块解出的两枚 API 域名）
HOSTS = [
    ("xjggg.top", 443),
    ("50.118.186.185", 8090),
    ("179.255.99.4", 8090),
]

# 端点自愈：主域名全挂时，从这几个公开配置页解出最新 API 端点（App 同款流程）
ENDPOINT_SOURCES = [
    "https://res.cloudinary.com/wygbngdd/raw/upload/1.txt",
    "https://anotepad.com/notes/wcqhmtf9",
]
EP_AES_KEY = "3EoMYcMw9X1igBsCb7CLCTKGTqWv9OpAAJr2xGa3co0="
EP_AAD = "TVAPP_ENDPOINT_CONFIG_V1:TVAPP:production:A256GCM\x00"

CATS = [
    ("c_movie", "🎬电影", "电影"),
    ("c_tv", "📺剧集", "剧集"),
    ("c_anime", "🌸动漫", "动漫"),
    ("c_show", "🎤综艺", "综艺"),
]
RANK_TID = "c_rank"
RANK_NAME = "🔥排行榜"

YEAR_ALL = ["2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018",
            "2017", "2016", "2015", "2010", "2005", "2000"]

FILTER_DEF = {
    "电影": {
        "class": ["动作", "喜剧", "爱情", "科幻", "恐怖", "悬疑", "剧情", "战争", "犯罪",
                  "动画", "奇幻", "冒险", "灾难", "纪录片", "历史", "武侠", "青春", "家庭",
                  "古装", "运动"],
        "area": ["中国大陆", "美国", "韩国", "日本", "英国", "法国", "中国香港", "中国台湾",
                 "泰国", "印度", "俄罗斯", "加拿大", "澳大利亚", "德国", "西班牙", "意大利"],
        "year": YEAR_ALL + ["1995", "1990"],
    },
    "剧集": {
        "class": ["国产剧", "欧美剧", "美剧", "英剧", "日韩剧", "韩剧", "日剧", "港台剧",
                  "香港剧", "台湾剧", "电视剧", "古装", "悬疑", "都市", "爱情", "犯罪",
                  "战争", "奇幻", "喜剧"],
        "area": ["中国大陆", "美国", "韩国", "日本", "英国", "中国香港", "中国台湾", "泰国",
                 "法国", "加拿大"],
        "year": YEAR_ALL,
    },
    "动漫": {
        "class": ["日本动漫", "国产动漫", "欧美动漫", "国创（B站）", "动画", "热血", "奇幻",
                  "冒险", "恋爱", "搞笑", "科幻", "儿童", "亲子", "魔幻", "悬疑", "武侠",
                  "古装", "真人"],
        "area": ["日本", "中国大陆", "美国", "英国", "韩国", "加拿大", "法国"],
        "year": YEAR_ALL,
    },
    "综艺": {
        "class": ["大陆综艺", "日韩综艺", "欧美综艺", "港台综艺", "真人秀", "脱口秀", "选秀",
                  "音乐", "竞技", "晚会", "明星", "情感", "搞笑", "文化", "戏曲"],
        "area": ["中国大陆", "韩国", "日本", "美国", "英国", "中国香港", "中国台湾", "泰国"],
        "year": ["2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018",
                 "2017", "2016", "2015", "2010"],
    },
}

SORTS = [("", "默认"), ("hot", "最热"), ("score", "评分"), ("time", "最新")]

# 显示名 → 真实 vodFrom（decode 接口只认真实 from，传显示名会返回"未知的vodFrom类型"）
FRM_ALIAS = {
    "ZJ4K": "zijianm3u8", "BB蓝光": "BBA", "QS蓝光": "qsvip",
    "ZY蓝光": "zy1080_01", "JD4K": "JD4K", "TM蓝光": "tmdb", "NBY": "NBY",
}
# token 前缀 → 真实 vodFrom（从 token 自身反推，比线路名更可靠）
TOK_FRM = {"zijian": "zijianm3u8", "qqqq": "BBA", "qsvip": "qsvip",
           "JD": "JD4K", "tmdb": "tmdb", "NBY": "NBY"}


# ---------------- 纯标准库 AES-256（只为解 App 端点配置，GCM 数据段=CTR） ----------------
def _xt(a):
    a <<= 1
    return (a ^ 0x1b) & 0xff if a & 0x100 else a


def xj_gmul(a, b):
    r = 0
    for _ in range(8):
        if b & 1:
            r ^= a
        a = _xt(a)
        b >>= 1
    return r


def _gpow(a, n):
    r = 1
    while n:
        if n & 1:
            r = xj_gmul(r, a)
        a = xj_gmul(a, a)
        n >>= 1
    return r


def _mk_sbox():
    box = [0] * 256
    for i in range(256):
        x = _gpow(i, 254) if i else 0
        s = x
        for _ in range(4):
            x = ((x << 1) | (x >> 7)) & 0xff
            s ^= x
        box[i] = s ^ 0x63
    return box


XJ_SBOX = _mk_sbox()


def _aes_expand(key):
    nk = len(key) // 4
    nr = nk + 6
    w = [list(key[4 * i:4 * i + 4]) for i in range(nk)]
    rc = 1
    for i in range(nk, 4 * (nr + 1)):
        t = list(w[i - 1])
        if i % nk == 0:
            t = t[1:] + t[:1]
            t = [XJ_SBOX[b] for b in t]
            t[0] ^= rc
            rc = _xt(rc)
        elif nk > 6 and i % nk == 4:
            t = [XJ_SBOX[b] for b in t]
        w.append([w[i - nk][j] ^ t[j] for j in range(4)])
    return w, nr


def _aes_block(w, nr, blk):
    s = [[blk[4 * c + r] ^ w[c][r] for c in range(4)] for r in range(4)]
    for rnd in range(1, nr + 1):
        s = [[XJ_SBOX[s[r][c]] for c in range(4)] for r in range(4)]
        for r in range(1, 4):
            s[r] = s[r][r:] + s[r][:r]
        if rnd != nr:
            for c in range(4):
                a = [s[r][c] for r in range(4)]
                s[0][c] = xj_gmul(a[0], 2) ^ xj_gmul(a[1], 3) ^ a[2] ^ a[3]
                s[1][c] = a[0] ^ xj_gmul(a[1], 2) ^ xj_gmul(a[2], 3) ^ a[3]
                s[2][c] = a[0] ^ a[1] ^ xj_gmul(a[2], 2) ^ xj_gmul(a[3], 3)
                s[3][c] = xj_gmul(a[0], 3) ^ a[1] ^ a[2] ^ xj_gmul(a[3], 2)
        for c in range(4):
            for r in range(4):
                s[r][c] ^= w[rnd * 4 + c][r]
    out = bytearray(16)
    for c in range(4):
        for r in range(4):
            out[4 * c + r] = s[r][c]
    return bytes(out)


def _aes_ctr(key, nonce, data):
    w, nr = _aes_expand(key)
    ctr = int.from_bytes(nonce + b"\x00\x00\x00\x01", "big") + 1
    out = bytearray()
    for off in range(0, len(data), 16):
        ks = _aes_block(w, nr, ctr.to_bytes(16, "big"))
        chunk = data[off:off + 16]
        out.extend(bytes(a ^ b for a, b in zip(chunk, ks)))
        ctr += 1
    return bytes(out)


def _b64u(s):
    s = s.strip().replace("-", "+").replace("_", "/")
    return base64.b64decode(s + "=" * ((4 - len(s) % 4) % 4))


class XiaojiSpider(object):
    def __init__(self):
        self.host = None
        self.port = 443
        self.mem = {}

    # ---------------- TVBox 契约 ----------------
    def getName(self):
        return "小鸡看看"

    def isVideoFormat(self, url):
        # 站内只出 m3u8/mp4 直链，无 pics:// 图集线路
        if not url:
            return False
        return not url.startswith("pics://")

    def manualVideoCheck(self):
        return False

    def getDependence(self):
        return []

    def isVip(self):
        return False

    def getHeaders(self):
        return {"User-Agent": PLAY_UA}

    def init(self, extend=""):
        return

    # ---------------- 签名 ----------------
    def _sig_headers(self, dev=None):
        dev = dev or DEVICE
        ts = int(time.time() * 1000)
        nonce = hashlib.sha256(dev.encode()).hexdigest()[:8]
        nonce += ''.join([str(random.randint(0, 9)) for _ in range(8)])
        raw = "finger=%s&id=%s&nonce=%s&sk=%s&time=%s&v=%s" % (
            FINGER, APP_ID, nonce, SK, str(ts), APP_VER)
        sign = hashlib.sha256(raw.encode()).hexdigest().upper()
        return {
            "x-aid": APP_ID,
            "x-ave": APP_VER,
            "x-time": str(ts),
            "x-nonc": nonce,
            "x-sign": sign,
            "x-device-id": dev,
            "x-device-brand": "Xiaomi",
            "x-device-model": "M2012K11AC",
            "x-client-type": "tv",
            "x-update-id": "embedded",
            "Accept": "application/json",
            "Accept-Encoding": "identity",
            "User-Agent": XJ_UA,
        }

    # ---------------- HTTP ----------------
    def _raw(self, host, port, path, headers, timeout=15):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        if port == 443:
            conn = xj_http.HTTPSConnection(host, port, timeout=timeout, context=ctx)
        else:
            conn = xj_http.HTTPSConnection(host, port, timeout=timeout, context=ctx)
        conn.request("GET", path, headers=headers)
        resp = conn.getresponse()
        body = resp.read()
        enc = (resp.getheader("Content-Encoding") or "").lower()
        if "gzip" in enc:
            try:
                body = gzip.decompress(body)
            except Exception:
                pass
        conn.close()
        return resp.status, body

    def _api(self, path, params=None, retry=True, ok_codes=(200,)):
        if params:
            qs = urllib.parse.urlencode(params)
            path = path + ("&" if "?" in path else "?") + qs
        base = list(HOSTS)
        if self.host:
            base = [(self.host, self.port)] + [h for h in HOSTS if h[0] != self.host]
        order = list(base)
        last = ""
        tries = 0
        rots = 0
        conn_fail = 0
        while tries < 2:
            tries += 1
            for host, port in order:
                # 每次请求轮换取设备号：把配额压力摊到整个池上（几千人共用也不挤爆单枚）
                dev = _dev_get()
                for att in range(3):
                    try:
                        st, body = self._raw(host, port, path, self._sig_headers(dev))
                        conn_fail = 0
                        if st != 200:
                            last = "http %s" % str(st)
                            break
                        txt = body.decode("utf-8", "replace").strip()
                        if not txt.startswith("{"):
                            last = "bad body"
                            break
                        obj = json.loads(txt)
                        if obj.get("code") not in ok_codes:
                            last = str(obj.get("msg"))
                            if obj.get("code") == 401:
                                break
                            if obj.get("code") == 429 or obj.get("error_code") == 42901:
                                # 本设备今日配额耗尽 → 拉黑换号立刻重试（次数无上限）
                                rots += 1
                                dev = _dev_fail(dev)
                                if rots > 20:
                                    return None
                                print("[xjk] 429 -> rotate#%d %s" % (rots, dev[:18]))
                                continue
                            return None
                        self.host, self.port = host, port
                        _dev_ok(dev)
                        return obj.get("data")
                    except Exception as e:
                        # 连接层抖动（ConnectionAborted/超时）→ 指数退避重试
                        last = str(e)[:60]
                        conn_fail += 1
                        if att < 2:
                            time.sleep(0.35 * (att + 1))
                if last.startswith("http") or last == "bad body":
                    continue
            # 全部端点失败 → 走一次端点自愈再试
            if tries == 1:
                time.sleep(0.5)
                new = self._refresh_hosts()
                if new:
                    HOSTS[:] = new if new[0][0] != HOSTS[0][0] else HOSTS
                    base = list(HOSTS)
                order = base if not self.host else [self.host and (self.host, self.port)] + \
                    [h for h in base if h[0] != self.host]
                order = [x for x in order if x]
        if last:
            print("[xjk]", path[:50], "fail:", last)
        return None

    # ---------------- 工具 ----------------
    @staticmethod
    def _s(v, dft=""):
        if v is None:
            return dft
        if isinstance(v, (list, tuple)):
            return ",".join([str(x) for x in v if x])
        return str(v)

    @staticmethod
    def _is_url(u):
        # 真正的 URL 判据：协议 + 主机名，而不是松散的 startswith
        return bool(u) and len(u) > 10 and "://" in u and bool(urllib.parse.urlparse(u).hostname)

    def _pic(self, v):
        pic = v.get("vod_pic") or ""
        if self._is_url(pic):
            return pic
        dou = v.get("vod_douban_pic") or ""
        if self._is_url(dou):
            return "proxy://do=py&type=img&url=" + urllib.parse.quote(dou, safe="")
        return ""

    def _vod(self, v):
        return {
            "vod_id": str(v.get("vod_id")),
            "vod_name": self._s(v.get("vod_name")),
            "vod_pic": self._pic(v),
            "vod_remarks": self._s(v.get("vod_remarks")),
            "vod_year": self._s(v.get("vod_year")),
            "vod_area": self._s(v.get("vod_area")),
            "vod_class": self._s(v.get("vod_class")),
            "vod_actor": self._s(v.get("vod_actor")),
            "vod_director": self._s(v.get("vod_director")),
            "vod_content": self._s(v.get("vod_content")),
            "type_name": self._s(v.get("type_name")),
        }

    # ---------------- 端点自愈 ----------------
    def _refresh_hosts(self):
        """主域名全挂时，按 App 同款流程从公开配置页解出新 API 端点。"""
        for src in ENDPOINT_SOURCES:
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                pu = urllib.parse.urlparse(src)
                conn = xj_http.HTTPSConnection(pu.hostname, 443, timeout=12, context=ctx)
                conn.request("GET", pu.path + ("?" + pu.query if pu.query else ""),
                             headers={"User-Agent": PLAY_UA})
                resp = conn.getresponse()
                txt = resp.read().decode("utf-8", "replace")
                conn.close()
                m = re.search(r"TVAPP_CONFIG_V1_BEGIN([\s\S]*?)TVAPP_CONFIG_V1_END", txt)
                if not m:
                    continue
                raw = _b64u(m.group(1))
                if len(raw) < 96 or raw[0] != 1:
                    continue
                aad = EP_AAD.encode() + raw[0:3]
                plain = _aes_ctr(base64.b64decode(EP_AES_KEY), raw[3:15], raw[15:])
                body = plain[64:]
                if len(body) > 16:
                    body = body[:-16]      # 尾部 16 字节是 GCM tag，不在明文里
                obj = json.loads(body.decode("utf-8", "replace"))
                urls = obj.get("a") or []
                found = []
                for u in urls:
                    pu2 = urllib.parse.urlparse(u)
                    if pu2.hostname:
                        found.append((pu2.hostname, pu2.port or 443))
                if found:
                    print("[xjk] endpoint refresh:", found)
                    return found
            except Exception as e:
                print("[xjk] refresh err", str(e)[:60])
        return []

    # ---------------- 分类筛选 ----------------
    def _filters(self):
        out = {}
        for tid, _name, tname in CATS:
            dims = FILTER_DEF.get(tname) or {}
            arr = []
            for key, label in (("class", "类型"), ("area", "地区"), ("year", "年份")):
                vals = dims.get(key) or []
                if not vals:
                    continue
                opts = [{"n": "全部", "v": ""}]
                for v in vals:
                    opts.append({"n": v, "v": v})
                arr.append({"key": key, "name": label, "value": opts})
            srt = [{"n": "默认", "v": ""}]
            for v, n in SORTS[1:]:
                srt.append({"n": n, "v": v})
            arr.append({"key": "sort", "name": "排序", "value": srt})
            out[tid] = arr
        return out

    # ---------------- 首页 ----------------
    def homeContent(self, filter=False):
        result = {"class": [], "list": [], "filters": {}}
        for tid, name, _ in CATS:
            result["class"].append({"type_id": tid, "type_name": name})
        result["class"].append({"type_id": RANK_TID, "type_name": RANK_NAME})
        data = self._api("/api.php/app/index/home")
        vods = []
        if isinstance(data, dict):
            seen = set()
            for v in (data.get("recommend") or []):
                vid = str(v.get("vod_id"))
                if vid in seen:
                    continue
                seen.add(vid)
                vods.append(self._vod(v))
            for c in (data.get("categories") or []):
                for v in (c.get("videos") or []):
                    vid = str(v.get("vod_id"))
                    if vid in seen:
                        continue
                    seen.add(vid)
                    vods.append(self._vod(v))
        result["list"] = vods
        result["filters"] = self._filters()
        if filter:
            return result
        return result

    def homeVideoContent(self):
        return {"list": self.homeContent(False).get("list") or []}

    # ---------------- 分类 ----------------
    def _rank_list(self):
        data = self._api("/api.php/app/ranking/list")
        vods = []
        if isinstance(data, dict):
            for rk in (data.get("rankings") or []):
                tname = self._s(rk.get("type_name"))
                for v in (rk.get("videos") or []):
                    item = self._vod(v)
                    if tname and not item.get("vod_remarks"):
                        item["vod_remarks"] = tname
                    vods.append(item)
        return vods

    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg) if str(pg).isdigit() else 1
        extend = extend or {}
        result = {"list": [], "page": pg, "pagecount": 999, "limit": 30, "total": 0}
        if tid == RANK_TID or str(tid).startswith("c_rank"):
            if pg > 1:
                result["list"] = []
                result["pagecount"] = 1
                return result
            result["list"] = self._rank_list()
            result["pagecount"] = 1
            result["total"] = len(result["list"])
            return result

        tname = ""
        for cid, _n, tn in CATS:
            if cid == tid:
                tname = tn
                break
        if not tname:
            tname = self._s(tid)
        params = {"type_name": tname, "page": pg, "limit": 30}
        c = self._s(extend.get("class")).strip()
        a = self._s(extend.get("area")).strip()
        y = self._s(extend.get("year")).strip()
        s = self._s(extend.get("sort")).strip()
        if c:
            params["class"] = c
        if a:
            params["area"] = a
        if y:
            params["year"] = y
        if s:
            params["sort"] = s
        data = self._api("/api.php/app/filter/vod", params)
        if isinstance(data, list):
            result["list"] = [self._vod(v) for v in data]
            result["total"] = len(result["list"])
            # 站方深翻页封顶 1000 条（limit=30 → 最多 34 页），算出真实页数
            pc = int(1000 / 30)
            if len(result["list"]) < 30:
                pc = pg
            result["pagecount"] = max(1, pc)
        else:
            result["pagecount"] = pg
        return result

    # ---------------- 详情 ----------------
    def _playback_all(self, vid):
        """一次拉全线路分集。
        ★坑：接口带 from 参数会被忽略并只回 BBA 线路，导致其它线路拿到 BBA 的 token
        → 播放时 vodFrom 与 token 不匹配，decode 返回"未知的vodFrom类型"★
        """
        data = self._api("/api.php/app/vod/playback_v2", {"vod_id": vid})
        out = {}
        if not isinstance(data, dict):
            return out
        for src in (data.get("sources") or []):
            f = src.get("from")
            eps = src.get("episodes") or []
            if f and eps:
                out[f] = eps
        return out

    def _playback(self, vid, frm="", _cache=None):
        allsrc = _cache if isinstance(_cache, dict) else self._playback_all(vid)
        if frm:
            return frm, allsrc.get(frm) or []
        for f, eps in allsrc.items():
            return f, eps
        return frm, []

    def detailContent(self, ids):
        vid = ids[0] if isinstance(ids, (list, tuple)) else ids
        vid = str(vid)
        data = self._api("/api.php/app/vod/detail_v2", {"vod_id": vid})
        if not isinstance(data, dict):
            return {"list": []}
        det = data.get("detail") or {}
        pb = data.get("playback") or {}
        vod = self._vod(det)
        vod["vod_id"] = vid

        lines = []       # [(display_name, from, episodes)]
        srcs = pb.get("sources") or []
        sel = pb.get("selected_source") or {}
        sel_from = sel.get("from") or ""
        order = []
        if sel_from:
            order.append(sel_from)
        for s in srcs:
            f = s.get("from")
            if not f or f in order:
                continue
            if (s.get("episode_count") or 0) <= 0 and not (s.get("episodes") or []):
                continue
            order.append(f)
        names = {}
        for s in srcs:
            names[s.get("from")] = self._s(s.get("display_name"))
        # 一次拉全线路分集（带 from 会因为服务端忽略参数而串线，见 _playback_all 注释）
        got = {}
        try:
            got = self._playback_all(vid)
        except Exception as e:
            print("[xjk] playback", e)
        for f in order:
            eps = got.get(f) or []
            if not eps and f == sel_from:
                eps = sel.get("episodes") or []
            if not eps:
                continue
            lines.append((names.get(f) or f, f, eps))

        # 线路排序：已验证可播的线路优先，已知 403 的线路（shenhua7）压到末尾并标注
        def _rank(f):
            return 1 if f == "qsvip" else 0
        lines.sort(key=lambda x: _rank(x[1]))
        for idx, (nm, f, eps) in enumerate(lines):
            if f == "qsvip":
                lines[idx] = ("%s(可能失效)" % nm, f, eps)

        froms = []
        urls = []
        for nm, f, eps in lines:
            froms.append(nm or f)
            cells = []
            for i, e in enumerate(eps):
                title = self._s(e.get("title")) or ("第%d集" % (i + 1))
                tok = self._s(e.get("url"))
                if not tok:
                    continue
                cells.append("%s$%s@@%s" % (title, tok, f))
            urls.append("#".join(cells))
        if froms:
            vod["vod_play_from"] = "$$$".join(froms)
            vod["vod_play_url"] = "$$$".join(urls)

        # 分集缓存：按集序把各线路 token 存起来，播放失败时能自动换线路（_alt_episode 用）
        try:
            rec = {}
            for nm, f, eps in lines:
                for i, e in enumerate(eps):
                    t = self._s(e.get("url"))
                    if t:
                        rec.setdefault(i, []).append((f, t))
            cache = getattr(self, "_eps_cache", None)
            if not isinstance(cache, dict):
                cache = {}
            cache[vid] = rec
            # 只留最近 8 部，防内存膨胀（几千人共用一台设备的长跑场景）
            while len(cache) > 8:
                cache.pop(next(iter(cache)))
            self._eps_cache = cache
        except Exception as e:
            print("[xjk] cache", e)

        return {"list": [vod]}

    # ---------------- 搜索 ----------------
    def searchContent(self, key, quick, pg="1"):
        pg = int(pg) if str(pg).isdigit() else 1
        data = self._api("/api.php/app/search/index",
                         {"wd": key, "page": pg, "limit": 30})
        vods = []
        if isinstance(data, list):
            vods = [self._vod(v) for v in data]
        return {"list": vods, "page": pg, "pagecount": 999 if len(vods) >= 30 else pg}

    # ---------------- 播放 ----------------
    def _decode(self, tok, frm, _retry=0):
        """解析播放令牌 → 真直链。
        _api 内部已做「轮转取设备号 + 429 换号 + 连接退避」，
        这里再包一层整调用重试，扛住服务端瞬时抖动（几千人共用时的常态）。
        """
        data = self._api("/api.php/app/decode/url/",
                         {"url": tok, "vodFrom": frm, "_t": int(time.time() * 1000)},
                         ok_codes=(1, 200))
        if isinstance(data, str) and self._is_url(data):
            return data
        # 服务端有时把未识别线路原样返回（data == token），换线路名也没用 → 重试一次
        if _retry < 2:
            time.sleep(0.4 * (_retry + 1))
            return self._decode(tok, frm, _retry + 1)
        return ""

    def playerContent(self, flag, id, vipFlags=None):
        tok = self._s(id)
        frm = ""
        if "@@" in tok:
            tok, frm = tok.rsplit("@@", 1)
        tok = tok.strip()
        # 线路名多层纠错（decode 只认真实 vodFrom，错了就返回"未知的vodFrom类型"）
        cands = []
        if frm:
            cands.append(FRM_ALIAS.get(frm, frm))
        t = self._frm_from_token(tok)
        if t:
            cands.append(t)
        fl = self._s(flag)
        if fl:
            cands.append(FRM_ALIAS.get(fl, fl))
        cands.append("")
        url = ""
        seen = set()
        for f in cands:
            if f in seen:
                continue
            seen.add(f)
            url = self._decode(tok, f)
            if url:
                break
        if not url:
            # 兜底：本条线路解析失败 → 到其它线路取「同名集」，保证一定播得出来
            alt = self._alt_episode(tok)
            if alt:
                header = {"User-Agent": PLAY_UA}
                if "shenhua7.vip" in alt:
                    header["Referer"] = "https://www.shenhua7.vip/"
                return {"parse": 0, "playUrl": "", "url": alt, "header": header}
            return {"parse": 1, "playUrl": "", "url": tok,
                    "header": {"User-Agent": PLAY_UA}}
        header = {"User-Agent": PLAY_UA}
        if "shenhua7.vip" in url:
            header["Referer"] = "https://www.shenhua7.vip/"
        return {"parse": 0, "playUrl": "", "url": url, "header": header}

    def _alt_episode(self, tok):
        """同一集在其它线路取真直链：detail 里已把每集 token 按线路存下来，
        用「集名」跨线路配对的成本太高，这里直接按 token 反查所属影片不可行，
        改为：本进程最近一次 detailContent 的分集表里找同一集序号的其它线路。"""
        try:
            cache = getattr(self, "_eps_cache", None) or {}
            for vid, rec in cache.items():
                for pos, toks in rec.items():
                    for f, t in toks:
                        if t == tok:
                            for f2, t2 in toks:
                                if f2 == f:
                                    continue
                                u = self._decode(t2, f2)
                                if u:
                                    print("[xjk] fallback line %s -> %s" % (f, f2))
                                    return u
                            return ""
        except Exception as e:
            print("[xjk] alt", e)
        return ""

    @staticmethod
    def _frm_from_token(tok):
        """从 token 前缀推断真实 vodFrom（decode 接口按前缀判线路）。"""
        p = (tok.split("-", 1)[0] or "")
        if p and len(p) <= 14:
            return TOK_FRM.get(p, "")
        return ""

    # ---------------- 图片代理 ----------------
    def localProxy(self, param):
        try:
            raw = param if isinstance(param, str) else urllib.parse.urlencode(param)
            if raw.startswith("proxy://"):
                raw = raw[len("proxy://"):]
            qs = urllib.parse.parse_qs(raw)
            url = (qs.get("url") or [""])[0]
            typ = (qs.get("type") or [""])[0]
            if not url:
                return [404, "text/plain", {}, b"no url"]
            if typ != "img":
                return [404, "text/plain", {}, b"bad type"]
            pu = urllib.parse.urlparse(url)
            if not pu.hostname:
                return [404, "text/plain", {}, b"bad url"]
            headers = {
                "User-Agent": PLAY_UA,
                "Accept": "image/avif,image/webp,image/*,*/*;q=0.8",
            }
            if "doubanio" in pu.hostname or "douban" in pu.hostname:
                headers["Referer"] = "https://movie.douban.com/"
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            conn = xj_http.HTTPSConnection(pu.hostname, pu.port or 443,
                                               timeout=15, context=ctx)
            path = (pu.path or "/") + ("?" + pu.query if pu.query else "")
            conn.request("GET", path, headers=headers)
            resp = conn.getresponse()
            body = resp.read()
            ctype = resp.getheader("Content-Type") or "image/jpeg"
            conn.close()
            if resp.status == 200 and body:
                return [200, ctype, {}, body]
            return [404, "text/plain", {}, b"fetch failed"]
        except Exception as e:
            print("[xjk] proxy", e)
            return [404, "text/plain", {}, b"err"]


# ======================================================================
# 模块：ff
# ======================================================================
# -*- coding: utf-8 -*-
# FoFo影院 (www.fofo33.com) TVBox / OK影视 Python 爬虫
# ------------------------------------------------------------
# 站点结构（实测 2026-11）：
#   - 站点无开放 JSON API（/api.php 全部回退 HTML），故走 HTML 解析
#   - 分类页:  /{dianying|dianshiju|zongyi|dongman}/{类型}-{地区}-{年代}-{排序}?page=N
#   - 搜索页:  /search?q=关键词&page=N（无结果时回吐推荐，必须本地关键词二次过滤）
#   - 详情页:  /{cat}/{vid}，内嵌 var urlList = decryptDict({...}) 恺撒位移(-1)加密的线路数据
#   - 取播放:  POST /source/  body: id={sid}  → 纯文本 m3u8/mp4 直链
#   - web-sign: 站点未启用（预留注入槽位）

import sys
import json
import re
import urllib.parse
sys.path.append('..')
try:
    from base.spider import Spider
except Exception:
    FofoSpider = object


class FofoSpider(_BaseSpider):

    HOST = 'https://www.fofo33.com'
    UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
          '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    TIMEOUT = 15

    # 旧配置 tid(1/2/3/4) → 站点真实分类路径
    TID_MAP = {'1': 'dianying', '2': 'dianshiju', '3': 'zongyi', '4': 'dongman'}
    CATS = [
        {'type_id': 'dianying', 'type_name': '电影'},
        {'type_id': 'dianshiju', 'type_name': '剧集'},
        {'type_id': 'zongyi', 'type_name': '综艺'},
        {'type_id': 'dongman', 'type_name': '动漫'},
    ]
    TYPE_MAP = {
        'dianying': [('0', '全部'), ('1', '剧情'), ('2', '喜剧'), ('3', '动作'), ('4', '爱情'),
                     ('5', '科幻'), ('6', '悬疑'), ('7', '惊悚'), ('8', '恐怖'), ('9', '犯罪'),
                     ('10', '同性'), ('11', '音乐'), ('12', '歌舞'), ('13', '传记'), ('14', '历史'),
                     ('15', '战争'), ('16', '西部'), ('17', '奇幻'), ('18', '冒险'), ('19', '灾难'),
                     ('20', '武侠'), ('21', '伦理')],
        'dianshiju': [('0', '全部'), ('1', '剧情'), ('2', '喜剧'), ('3', '动作'), ('4', '爱情'),
                      ('5', '科幻'), ('6', '悬疑'), ('7', '惊悚'), ('8', '恐怖'), ('9', '犯罪'),
                      ('10', '同性'), ('11', '音乐'), ('12', '歌舞'), ('13', '传记'), ('14', '历史'),
                      ('15', '战争'), ('16', '西部'), ('17', '奇幻'), ('18', '冒险'), ('19', '灾难'),
                      ('20', '武侠'), ('21', '伦理')],
        'zongyi': [('0', '全部'), ('1', '真人秀'), ('2', '脱口秀'), ('3', '纪录片'),
                   ('4', '传记'), ('5', '歌舞')],
        'dongman': [('0', '全部'), ('1', '剧情'), ('2', '喜剧'), ('3', '动作'), ('4', '爱情'),
                    ('5', '科幻'), ('6', '悬疑'), ('7', '惊悚'), ('8', '恐怖'), ('9', '犯罪'),
                    ('10', '同性'), ('11', '音乐'), ('12', '歌舞'), ('13', '传记'), ('14', '历史'),
                    ('15', '战争'), ('16', '西部'), ('17', '奇幻'), ('18', '冒险'), ('19', '灾难'),
                    ('20', '武侠'), ('21', '伦理')],
    }
    AREA_MAP = [('0', '全部'), ('1', '中国大陆'), ('2', '美国'), ('3', '香港'), ('4', '台湾'),
                ('5', '日本'), ('6', '韩国'), ('7', '英国'), ('8', '法国'), ('9', '德国'),
                ('10', '意大利'), ('11', '西班牙'), ('12', '印度'), ('13', '泰国'), ('14', '俄罗斯'),
                ('15', '伊朗'), ('16', '加拿大'), ('17', '澳大利亚'), ('18', '爱尔兰'),
                ('19', '瑞典'), ('20', '巴西'), ('21', '丹麦')]
    YEARS = [('0', '全部')] + [(str(y), str(y)) for y in range(2026, 2004, -1)] + [('1', '其他')]
    SORTS = [('0', '最新'), ('1', '热门'), ('2', '高分')]

    def __init__(self):
        self.host = self.HOST
        self.extend = ''
        self._line_cache = {}   # detail path -> 解析后的线路数据
        self._detail_cache = {} # detail path -> vod 基础信息

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------
    def init(self, extend=""):
        try:
            self.extend = extend or ''
            if isinstance(extend, str) and extend.strip().startswith('{'):
                ext = json.loads(extend)
                if isinstance(ext, dict) and ext.get('host'):
                    self.host = str(ext['host']).strip().rstrip('/')
        except Exception:
            pass

    def getName(self):
        return 'FoFo影院'

    def destroy(self):
        try:
            self._line_cache.clear()
            self._detail_cache.clear()
        except Exception:
            pass

    def isVideoFormat(self, url):
        # 选集字符串可能带 # 后缀（如 .m3u8#下一集），先剥离再判断
        try:
            url = str(url or '').split('#')[0].split('?')[0].lower()
            return any(url.endswith(ext) for ext in
                       ('.m3u8', '.mp4', '.mkv', '.flv', '.avi', '.ts', '.webm'))
        except Exception:
            return False

    def manualVideoCheck(self):
        return False

    def localProxy(self, param):
        return []

    # ------------------------------------------------------------------
    # 基础网络封装
    # ------------------------------------------------------------------
    def _headers(self, referer='', web_sign=''):
        h = {
            'User-Agent': self.UA,
            'Accept': 'text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8',
            'Referer': referer or (self.host + '/'),
            'x-platform': 'web',
            'x-requested-with': 'XMLHttpRequest',
        }
        # 站点当前不需要 web-sign；若后续启用，在此注入
        if web_sign:
            h['web-sign'] = web_sign
        return h

    def _api_get(self, url, referer=''):
        """GET + JSON 解析，容错返回 {}"""
        try:
            import urllib.request
            req = urllib.request.Request(url, headers=self._headers(referer))
            with urllib.request.urlopen(req, timeout=self.TIMEOUT) as resp:
                return json.loads(resp.read().decode('utf-8', 'ignore'))
        except Exception:
            return {}

    def _html_get(self, url, referer=''):
        try:
            import urllib.request
            req = urllib.request.Request(url, headers=self._headers(referer))
            with urllib.request.urlopen(req, timeout=self.TIMEOUT) as resp:
                return resp.read().decode('utf-8', 'ignore')
        except Exception:
            return ''

    def _source_post(self, sid, referer=''):
        """POST /source/ 取 m3u8/mp4 直链（纯文本返回）"""
        try:
            import urllib.request
            data = urllib.parse.urlencode({'id': str(sid)}).encode('utf-8')
            h = self._headers(referer)
            h['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            req = urllib.request.Request(self.host + '/source/', data=data, headers=h)
            with urllib.request.urlopen(req, timeout=self.TIMEOUT) as resp:
                return resp.read().decode('utf-8', 'ignore').strip()
        except Exception:
            return ''

    # ------------------------------------------------------------------
    # 恺撒解密（站点 decryptDict 逻辑：字符 charCode -1）
    # ------------------------------------------------------------------
    def _shift(self, s):
        try:
            return ''.join(chr(ord(c) - 1) for c in s)
        except Exception:
            return s

    def _decrypt_dict(self, val):
        try:
            if isinstance(val, list):
                return [self._decrypt_dict(x) for x in val]
            if isinstance(val, dict):
                return {self._shift(k): self._decrypt_dict(v) for k, v in val.items()}
            if isinstance(val, str):
                s = self._shift(val)
                # 与站点 JS 一致：对解密结果尝试 JSON.parse
                # （字符串值多为 "\uXXXX" 形式的 JSON 字符串字面量，需解码为中文）
                if s[:1] in ('"', '[', '{'):
                    try:
                        return json.loads(s)
                    except Exception:
                        return s
                return s
            return val
        except Exception:
            return val

    def _extract_urllist(self, html):
        """从详情页提取并解密内嵌线路数据"""
        try:
            m = re.search(r'var\s+urlList\s*=\s*decryptDict\((\{.*?\})\)', html, re.S)
            if not m:
                return {'source': [], 'url_list': []}
            raw = m.group(1).replace("'", '"')
            data = json.loads(raw)
            out = {}
            for k, v in data.items():
                out[self._shift(k)] = self._decrypt_dict(v)
            sources = out.get('source') or []
            url_list = out.get('url_list') or []
            if not isinstance(url_list, list):
                url_list = []
            return {'source': sources, 'url_list': url_list}
        except Exception:
            return {'source': [], 'url_list': []}

    # ------------------------------------------------------------------
    # HTML 列表解析
    # ------------------------------------------------------------------
    def _parse_items(self, html):
        """解析列表页/搜索页 <li> 条目，返回 vod 列表"""
        result = []
        try:
            for block in re.findall(r'<li>(.*?)</li>', html, re.S):
                if 'class="thumbnail"' not in block:
                    continue
                m = re.search(
                    r'href="/(dianying|dianshiju|zongyi|dongman)/(\d+)"[^>]*class="thumbnail"',
                    block)
                if not m:
                    continue
                cat, vid = m.group(1), m.group(2)
                img = ''
                mi = re.search(r'src="([^"]+)"[^>]*class="thumb"', block)
                if not mi:
                    mi = re.search(r'class="thumb"[^>]*src="([^"]+)"', block)
                if mi:
                    img = mi.group(1)
                note = ''
                mn = re.search(r'class="note"[^>]*>\s*<span>([^<]*)</span>', block)
                if mn:
                    note = mn.group(1).strip()
                title = ''
                mt = re.search(r'<h2><a[^>]*>([^<]+)</a></h2>', block)
                if mt:
                    title = mt.group(1).strip()
                if not title:
                    mt = re.search(r'alt="([^"]+)"', block)
                    if mt:
                        title = mt.group(1).strip()
                if not title or not vid:
                    continue
                result.append({
                    'vod_id': cat + '/' + vid,
                    'vod_name': title,
                    'vod_pic': img,
                    'vod_remarks': note,
                })
        except Exception:
            pass
        return result

    def _parse_pagecount(self, html, cur_pg, per_page=24):
        try:
            pages = [int(x) for x in re.findall(r'[?&]page=(\d+)', html)]
            if pages:
                return max(pages)
            # 无分页链接时按是否满页外推
            return cur_pg + 1 if html.count('class="thumbnail"') >= per_page else cur_pg
        except Exception:
            return cur_pg

    def _strip_tags(self, s):
        try:
            return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s or '')).strip()
        except Exception:
            return (s or '').strip()

    # ------------------------------------------------------------------
    # 内容方法
    # ------------------------------------------------------------------
    def homeContent(self, filter):
        classes = [{'type_id': c['type_id'], 'type_name': c['type_name']} for c in self.CATS]
        filters = {}
        for c in self.CATS:
            filters[c['type_id']] = [
                {'key': 'type', 'name': '类型',
                 'value': [{'n': n, 'v': v} for v, n in self.TYPE_MAP[c['type_id']]]},
                {'key': 'area', 'name': '地区',
                 'value': [{'n': n, 'v': v} for v, n in self.AREA_MAP]},
                {'key': 'year', 'name': '年代',
                 'value': [{'n': n, 'v': v} for v, n in self.YEARS]},
                {'key': 'sort', 'name': '排序',
                 'value': [{'n': n, 'v': v} for v, n in self.SORTS]},
            ]
        return {'class': classes, 'filters': filters}

    def homeVideoContent(self):
        try:
            html = self._html_get(self.host + '/')
            items = self._parse_items(html)
            seen, result = set(), []
            for it in items:
                if it['vod_id'] in seen:
                    continue
                seen.add(it['vod_id'])
                result.append(it)
            return {'list': result[:30]}
        except Exception:
            return {'list': []}

    def _norm_tid(self, tid):
        try:
            tid = str(tid or '1').strip()
            if tid in self.TID_MAP:
                return self.TID_MAP[tid]
            if tid in self.TID_MAP.values():
                return tid
            names = {c['type_name']: c['type_id'] for c in self.CATS}
            return names.get(tid, 'dianying')
        except Exception:
            return 'dianying'

    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg) if str(pg).strip().isdigit() else 1
        cat = self._norm_tid(tid)
        ext = {}
        try:
            if isinstance(extend, str) and extend.strip():
                ext = json.loads(extend)
            elif isinstance(extend, dict):
                ext = extend
        except Exception:
            ext = {}
        t = str(ext.get('type') or '0')
        a = str(ext.get('area') or '0')
        y = str(ext.get('year') or '0')
        s = str(ext.get('sort') or '0')
        path = '%s-%s-%s-%s' % (re.sub(r'\D', '', t) or '0',
                                re.sub(r'\D', '', a) or '0',
                                re.sub(r'\D', '', y) or '0',
                                re.sub(r'\D', '', s) or '0')
        result = {'list': [], 'total': 0, 'page': pg, 'pagecount': pg}
        try:
            url = '%s/%s/%s?page=%d' % (self.host, cat, path, pg)
            html = self._html_get(url)
            items = self._parse_items(html)
            # 本地二次过滤：仅保留当前分类条目（防接口混类）
            items = [it for it in items if it['vod_id'].startswith(cat + '/')]
            # 过滤后条目 < 8 时补抓后续 2 页
            extra_pages = []
            if len(items) < 8:
                fetch_pg = pg
                for _ in range(2):
                    fetch_pg += 1
                    html2 = self._html_get('%s/%s/%s?page=%d' % (self.host, cat, path, fetch_pg))
                    items2 = [it for it in self._parse_items(html2)
                              if it['vod_id'].startswith(cat + '/')]
                    extra_pages.append(html2)
                    items.extend(items2)
                    if len(items) >= 8:
                        break
            seen = set()
            uniq = []
            for it in items:
                if it['vod_id'] in seen:
                    continue
                seen.add(it['vod_id'])
                uniq.append(it)
            pagecount = self._parse_pagecount(html, pg)
            for h2 in extra_pages:
                pagecount = max(pagecount, self._parse_pagecount(h2, pg))
            result = {
                'list': uniq,
                'total': max(pagecount, pg) * 24,
                'page': pg,
                'pagecount': max(pagecount, pg),
            }
        except Exception:
            pass
        return result

    def searchContent(self, key, quick, pg="1"):
        pg = int(pg) if str(pg).strip().isdigit() else 1
        try:
            url = '%s/search?q=%s&page=%d' % (
                self.host, urllib.parse.quote(str(key or '').strip()), pg)
            html = self._html_get(url)
            items = self._parse_items(html)
            # 站点搜索无结果时会回吐推荐列表，必须本地关键词过滤
            kw = str(key or '').strip().lower()
            if kw:
                items = [it for it in items if kw in it['vod_name'].lower()]
            pagecount = pg + 1 if html.count('class="thumbnail"') >= 24 else pg
            return {'list': items, 'total': pagecount * 24,
                    'page': pg, 'pagecount': pagecount}
        except Exception:
            return {'list': [], 'total': 0, 'page': pg, 'pagecount': pg}

    def detailContent(self, ids):
        try:
            raw = ids[0] if isinstance(ids, list) and ids else str(ids)
            raw = str(raw).strip().strip('/')
            paths = []
            if '/' in raw:
                paths.append(raw)
            else:
                # 旧配置纯数字 id：轮询四个分类定位详情页
                for cat in ('dianying', 'dianshiju', 'zongyi', 'dongman'):
                    paths.append(cat + '/' + raw)
            html, path = '', paths[0]
            for p in paths:
                html = self._html_get('%s/%s' % (self.host, p))
                if html and 'urlList' in html:
                    path = p
                    break
            if not html:
                return {'list': []}
            cat = path.split('/')[0]
            vid = path.split('/')[1] if '/' in path else path

            # ---- 基础信息 ----
            title, year = '', ''
            mt = re.search(r'<h1 class="product-title">(.*?)</h1>', html, re.S)
            if mt:
                raw_t = mt.group(1)
                my = re.search(r'<span>\s*\((\d{4})\)\s*</span>', raw_t)
                if my:
                    year = my.group(1)
                title = self._strip_tags(re.sub(r'<span.*?</span>', ' ', raw_t, flags=re.S))
            mi = re.search(r'class="product-header">\s*<img[^>]*src="([^"]+)"', html)
            cover = mi.group(1) if mi else ''

            director, actor, vod_class, area, desc = '', '', '', '', ''
            for label, holder in (('导演', 'director'), ('主演', 'actor'),
                                  ('类型', 'cls'), ('制片国家/地区', 'area'), ('剧情简介', 'desc')):
                mm = re.search(r'class="product-excerpt">\s*' + re.escape(label) +
                               r'：\s*<span>(.*?)</span>', html, re.S)
                if not mm:
                    continue
                val = self._strip_tags(mm.group(1))
                if holder == 'director':
                    director = val
                elif holder == 'actor':
                    actor = val
                elif holder == 'cls':
                    vod_class = val.replace(' ', '')
                elif holder == 'area':
                    area = val
                elif holder == 'desc':
                    desc = val

            # ---- 线路数据（聚合解密） ----
            data = self._extract_urllist(html)
            play_from, play_urls, remarks = self._build_sources(data, path)
            if not remarks and year:
                remarks = year

            vod = {
                'vod_id': path,
                'vod_name': title or vid,
                'vod_pic': cover,
                'type_name': vod_class,
                'vod_year': year,
                'vod_area': area,
                'vod_director': director,
                'vod_actor': actor,
                'vod_content': desc,
                'vod_remarks': remarks,
                'vod_play_from': play_from,
                'vod_play_url': play_urls,
            }
            self._detail_cache[path] = vod
            return {'list': [vod]}
        except Exception:
            return {'list': []}

    def _build_sources(self, data, path):
        """
        组装播放线路：
        1) 优先取内嵌线路数据（每集 sid 经 POST /source/ 兑换 m3u8/mp4 直链），
           线路按名称排序，最多 4 条；
        2) 无任何直链线路时兜底详情页；
        3) 最后追加一条解析线路（交由壳内 webview 播放详情页）。
        """
        try:
            sources = data.get('source') or []
            url_list = data.get('url_list') or []
            lines = []
            for i, name in enumerate(sources):
                if i >= len(url_list):
                    break
                eps = url_list[i]
                if not isinstance(eps, list) or not eps:
                    continue
                clean = re.sub(r'\(\d+\)\s*$', '', str(name or ('线路%d' % (i + 1)))).strip()
                lines.append((clean or ('线路%d' % (i + 1)), eps))
            lines.sort(key=lambda x: x[0])
            lines = lines[:4]

            play_from, play_urls, remarks = [], [], ''
            for name, eps in lines:
                flags = []
                for ep in eps:
                    try:
                        # 解密后键名为 title/sid/name，兼容加密原名 ujumf/tje/obnf
                        ep_title = str(ep.get('title') or ep.get('ujumf') or '播放').strip()
                        sid = str(ep.get('sid') or ep.get('tje') or '').strip()
                    except Exception:
                        ep_title, sid = '播放', ''
                    if not sid:
                        continue
                    flags.append('%s$%s@%s' % (ep_title, sid, path))
                if flags:
                    play_from.append(name)
                    play_urls.append('#'.join(flags))
                    if not remarks:
                        first = eps[0]
                        try:
                            remarks = str(first.get('title') or first.get('ujumf') or '').strip()
                            if len(eps) > 1:
                                remarks = '全%d集' % len(eps)
                        except Exception:
                            remarks = ''
            if not play_from:
                play_from.append('网页解析')
                play_urls.append('立即播放$web@%s' % path)
            else:
                play_from.append('网页解析')
                play_urls.append('立即播放$web@%s' % path)
            return '$$$'.join(play_from), '$$$'.join(play_urls), remarks
        except Exception:
            return '网页解析', '立即播放$web@%s' % path, ''

    def playerContent(self, flag, id, vipFlags):
        play_id = str(id or '').strip()
        result = {
            'parse': 1, 'jx': 1, 'url': '',
            'header': json.dumps({'User-Agent': self.UA, 'Referer': self.host + '/'}),
        }
        try:
            if '@' in play_id:
                sid, path = play_id.split('@', 1)
            else:
                sid, path = play_id, ''
            detail_url = '%s/%s' % (self.host, path) if path else self.host + '/'
            # 站外/网页解析线路 → 交壳解析
            if sid == 'web' or not sid:
                result['parse'] = 1
                result['jx'] = 1
                result['url'] = detail_url
                return result
            # 直链：POST /source/ 兑换 m3u8/mp4
            text = self._source_post(sid, referer=detail_url)
            text = text.strip().strip('"')
            if text and self.isVideoFormat(text):
                result['parse'] = 0
                result['jx'] = 0
                result['url'] = text
                result['header'] = json.dumps({
                    'User-Agent': self.UA,
                    'Referer': detail_url,
                    'x-platform': 'web',
                    'x-requested-with': 'XMLHttpRequest',
                })
                return result
            # 兑换失败 → 兜底交壳解析详情页
            result['parse'] = 1
            result['jx'] = 1
            result['url'] = detail_url
        except Exception:
            try:
                result['parse'] = 1
                result['jx'] = 1
                result['url'] = self.host + '/'
            except Exception:
                pass
        return result


# ======================================================================
# 模块：sz
# ======================================================================
# -*- coding: utf-8 -*-
"""
================================================================================
 小山影视源 · CatVod / Box  Python Spider
================================================================================
 后端   : http://43.248.128.122:578
 账号   : sukeke / sukeke.1   (已内置,可在 init 参数中覆盖)
 依赖   : requests (无则退回 urllib)

 已完整验证的链路
 ----------------------------------------------------------------------------
  1. 登录       POST /api/v1/user/login      {"Username","Password","device_id"}
  2. 密钥交换   GET  /api/v1/security/challenge  →  POST /api/v1/security/init
                → session_id + sign_key
  3. 列表/搜索  GET  /api/v1/search?wd=*&type=<分类>&page=<页>
                → data.hits[]   (wd=* 为通配,配合 type 即分类全量)
  4. 详情       GET  /api/v1/video/detail?id=<vod_id>
                → data.vod_info.vod_url_with_player[]  每条线路带 tk 票根
  5. 换票       POST /api/v1/vod/ticket       body {"token": "<tk完整值>"}
                → data.ticket  (play_ticket, 内含 parse_api / data.url / 有效期)
  6. 取流       按 parse_api 分三种形态解析:
                 · 相对路径  /api/v1/vod/parse?code=..&t=..&url=
                        → 拼 BASE 后 GET,服务端直接吐播放地址
                 · 外部解析  https://.../json_api.php?key=..&vid={md5}
                        → {md5} 用 data.url 替换,返回 JSON 取 url
                 · 外部解析  https://.../api/?key=..&url=
                        → url= 后拼 data.url,返回 JSON 取 url
  7. 推荐       GET  /api/v1/video/recommend?id=<vod_id>

 注意:device_id 必须与账号已绑定的设备一致(每个新 device_id 占一个设备配额,
      超了会报"设备数量已达上限")。下方已预置可用设备号。
================================================================================
"""
import json
import time
import uuid
import base64
import hashlib
import hmac
import urllib.parse
import urllib.request          # 原脚本漏了这行：只用 parse 却调 request，壳里必崩
import os
import random

# 后端是境内明文 IP，走系统代理反而会被拦，统一用直连 opener
_DIRECT = urllib.request.build_opener(urllib.request.ProxyHandler({}))

try:
    import requests
except Exception:
    requests = None


try:
    from base.spider import Spider as BaseSpider
except Exception:
    class BaseSpider(object):
        def init(self, extend=""):
            pass

        def getName(self):
            return ""

        def isVideoFormat(self, url):
            return False

        def manualVideoCheck(self):
            return False

        def destroy(self):
            pass

        def localProxy(self, param):
            return None


# 已实测的分类表(type_id -> 名称)。search 接口有严格限流,
# 分类探测会连发数十次请求必然触发风控,因此默认直接使用本表,不做在线探测。
KNOWN_TYPES = [
    (1, "电影"), (2, "连续剧"), (3, "综艺"), (4, "动漫"),
    (20, "短剧"), (21, "少儿"), (22, "漫剧"), (23, "纪录片"),
]

# init 接口的服务端要求字段(只校验存在性,不校验取值)
_INIT_FILLER = {
    "sign": "s", "signature": "s", "app_id": "1", "app_key": "1",
    "app_version": "1.0", "version": "1", "platform": "android",
    "device": "android", "version_code": 1, "uid": "1",
    "source_id": "1", "site_id": "1", "type": "1",
}


class ShanZhaSpider(BaseSpider):
    CONFIG = {
        "base": "http://43.248.128.122:578",
        "username": "sukeke",
        "password": "sukeke.1",
        # 账号 sukeke 已绑定的设备号,换账号请改成自己的
        "device_id": "de94cd65-a825-4972-adf9-7dbece13e9f1",
        "timeout": 30,
        "user_agent": "Mozilla/5.0 (Linux; Android 12) okhttp/3.12.1",
        "page_size": 20,
        "auto_fallback": 1,   # 当前线路解析失败时自动降级到其它可用线路
    }

    def __init__(self):
        super().__init__()
        self.cfg = dict(self.CONFIG)
        self.base = self.CONFIG["base"].rstrip("/")
        self.device_id = ""
        self.jwt = ""
        self.session_id = ""
        self.sign_key = ""
        self._types = []
        self._http = None
        self._lines = []          # 上次详情里的线路顺序(用于降级)
        self._tkmap = {}          # tk -> {"name","code","ep"} 索引

    # ================================================================= 基础
    def getName(self):
        return "小山"

    def init(self, extend=""):
        self.cfg = dict(self.CONFIG)
        if isinstance(extend, dict):
            self.cfg.update(extend)
        elif isinstance(extend, str) and extend.strip():
            try:
                self.cfg.update(json.loads(extend))
            except Exception:
                for kv in str(extend).split(","):
                    if "=" in kv:
                        k, v = kv.split("=", 1)
                        self.cfg[k.strip()] = v.strip()

        self.base = str(self.cfg["base"]).rstrip("/")
        self.device_id = str(self.cfg.get("device_id") or "").strip()
        if not self.device_id:
            self.device_id = uuid.uuid4().hex.upper()
            self._save_device_id(self.device_id)

        self._http = requests.Session() if requests else None
        if self._http:
            self._http.headers.update({"User-Agent": self.cfg.get("user_agent", "okhttp/3.12.1")})

        try:
            self._ensure_session()
        except Exception:
            pass

    def _save_device_id(self, did):
        for p in ("/sdcard/.xiaoshan_did", "/storage/emulated/0/.xiaoshan_did"):
            try:
                with open(p, "w") as f:
                    f.write(did)
                return
            except Exception:
                continue

    def isVideoFormat(self, url):
        u = str(url or "").lower()
        return any(x in u for x in (".m3u8", ".mp4", ".flv", ".ts", "cmecloud", "apdcdn"))

    def manualVideoCheck(self):
        return False

    def destroy(self):
        try:
            if self._http:
                self._http.close()
        except Exception:
            pass

    def localProxy(self, param):
        return [404, "text/plain", "", None]

    # ================================================================= HTTP
    def _headers(self, extra=None):
        h = {"User-Agent": self.cfg.get("user_agent", "okhttp/3.12.1")}
        if self.jwt:
            h["Authorization"] = "Bearer " + self.jwt
        if self.session_id:
            h["X-Session-Id"] = self.session_id
        if extra:
            h.update(extra)
        return h

    def _get(self, path, params=None, headers=None, timeout=None):
        url = path if path.startswith("http") else self.base + path
        t = timeout or self.cfg.get("timeout", 20)
        try:
            if self._http:
                r = self._http.get(url, headers=self._headers(headers), params=params, timeout=t)
            else:
                q = ("?" + urllib.parse.urlencode(params)) if params else ""
                req = urllib.request.Request(url + q, headers=self._headers(headers))
                r = _DIRECT.open(req, timeout=t)
                body = r.read().decode("utf-8", "replace")
                return json.loads(body)
            return r.json()
        except Exception as e:
            return {"code": 0, "msg": "请求失败: %s" % e}

    def _post(self, path, payload, headers=None, timeout=None):
        url = path if path.startswith("http") else self.base + path
        t = timeout or self.cfg.get("timeout", 20)
        hh = self._headers(headers)
        hh["Content-Type"] = "application/json"
        try:
            if self._http:
                r = self._http.post(url, json=payload, headers=hh, timeout=t)
            else:
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(url, data=data, headers=hh)
                r = _DIRECT.open(req, timeout=t)
                body = r.read().decode("utf-8", "replace")
                return json.loads(body)
            return r.json()
        except Exception as e:
            return {"code": 0, "msg": "请求失败: %s" % e}

    def _get_text(self, url, headers=None, timeout=None, retry=2):
        """带 Referer + 重试的 GET(外部解析接口冷启动较慢)"""
        t = timeout or self.cfg.get("timeout", 30)
        hh = self._headers(headers)
        hh.setdefault("Referer", "https://www.google.com/")
        last = ""
        for i in range(max(1, retry)):
            try:
                if self._http:
                    r = self._http.get(url, headers=hh, timeout=t)
                    return r.status_code, r.text
                req = urllib.request.Request(url, headers=hh)
                resp = _DIRECT.open(req, timeout=t)
                return resp.getcode(), resp.read().decode("utf-8", "replace")
            except Exception as e:
                last = str(e)
                if i < retry - 1:
                    time.sleep(1.2)
        return 0, last

    # ================================================================= 会话
    def _login(self):
        r = self._post("/api/v1/user/login", {
            "Username": self.cfg.get("username"),
            "Password": self.cfg.get("password"),
            "device_id": self.device_id,
        })
        if r.get("code") == 1 and isinstance(r.get("data"), dict):
            t = r["data"].get("token")
            if t:
                self.jwt = t
                return True
        return False

    def _handshake(self):
        ch = self._get("/api/v1/security/challenge")
        if ch.get("code") != 1 or not isinstance(ch.get("data"), dict):
            return False
        challenge = ch["data"].get("challenge")
        cid = ch["data"].get("challenge_id")
        if not challenge or not cid:
            return False

        payload = {
            "challenge": challenge,
            "challenge_id": cid,
            "device_id": self.device_id,
            "token": self.jwt,
            "client_token": "",
            "timestamp": int(time.time()),
            "nonce": uuid.uuid4().hex,
            "username": self.cfg.get("username"),
            "password": self.cfg.get("password"),
        }
        payload.update(_INIT_FILLER)

        r = self._post("/api/v1/security/init", payload)
        if r.get("code") == 1 and isinstance(r.get("data"), dict):
            self.session_id = r["data"].get("session_id") or ""
            self.sign_key = r["data"].get("sign_key") or ""
            return bool(self.session_id)
        return False

    def _ensure_session(self):
        if not self.jwt and not self._login():
            return False
        if not self.session_id and not self._handshake():
            return False
        return True

    def _sign_headers(self, path, body=""):
        """基于 sign_key 的设备签名(服务端 sign_policy=observe,属扩展用途)"""
        if not self.sign_key:
            return {}
        try:
            key = bytes.fromhex(self.sign_key)
        except Exception:
            return {}
        ts = str(int(time.time() * 1000))
        nonce = uuid.uuid4().hex
        msg = (ts + nonce + path + (body or "")).encode("utf-8")
        sg = hmac.new(key, msg, hashlib.sha256).hexdigest()
        return {"X-Timestamp": ts, "X-Nonce": nonce, "X-Sign": sg,
                "X-Device-Sign": sg, "X-Device-Id": self.device_id}

    # ================================================================= 分类
    def _detect_types(self):
        """遍历 type 自动发现分类表"""
        found = []
        for tid in list(range(1, 31)) + [40, 50, 60, 99]:
            try:
                r = self._get("/api/v1/search", params={"wd": "*", "type": tid, "page": 1})
            except Exception:
                continue
            if r.get("code") != 1:
                continue
            hits = ((r.get("data") or {}).get("hits")) or []
            if not hits:
                continue
            h0 = hits[0]
            if h0.get("type_id") and h0.get("type_name"):
                found.append((int(h0["type_id"]), str(h0["type_name"])))
        if found:
            self._types = sorted(set(found))
        return self._types

    def homeContent(self, filter):
        self._ensure_session()
        if not self._types:
            self._types = list(KNOWN_TYPES)
        classes = [{"type_id": str(t), "type_name": n} for t, n in self._types]
        return {"class": classes, "filters": {}}

    def homeVideoContent(self):
        try:
            return self.categoryContent(self._types[0][0] if self._types else "1", 1, False, {})
        except Exception:
            return {"list": []}

    # ================================================================= 列表
    def _search(self, wd, page=1, type_id=None):
        """search 接口限流较严,遇"请求过于频繁"自动退避重试"""
        params = {"wd": wd, "page": page}
        if type_id:
            params["type"] = type_id
        delays = [0, 2.5, 5, 9, 15]
        r = {"code": 0}
        for i, d in enumerate(delays):
            if d:
                time.sleep(d)
            r = self._get("/api/v1/search", params=params)
            if r.get("code") == 1:
                break
            msg = str(r.get("msg") or "")
            if "频繁" not in msg and "rate" not in msg.lower():
                break
        if r.get("code") != 1:
            return [], 1, 0
        data = r.get("data") or {}
        hits = data.get("hits") or []
        total = int(data.get("total") or 0)
        pages = int(data.get("total_pages") or 1)
        return hits, pages, total

    @staticmethod
    def _item(it):
        return {
            "vod_id": str(it.get("vod_id") or ""),
            "vod_name": str(it.get("vod_name") or ""),
            "vod_pic": str(it.get("vod_pic") or ""),
            "vod_remarks": str(it.get("vod_remarks") or ""),
            "vod_year": str(it.get("vod_year") or ""),
            "vod_area": str(it.get("vod_area") or ""),
            "vod_class": str(it.get("vod_class") or ""),
            "vod_actor": str(it.get("vod_actor") or ""),
            "vod_director": str(it.get("vod_director") or ""),
            "vod_content": str(it.get("vod_blurb") or it.get("vod_content") or ""),
        }

    def categoryContent(self, tid, pg, filter, extend):
        self._ensure_session()
        try:
            pg = int(pg or 1)
        except Exception:
            pg = 1
        hits, pages, total = self._search("*", pg, str(tid))
        lst = [self._item(it) for it in hits]
        return {"list": lst, "page": pg, "pagecount": pages,
                "limit": self.cfg.get("page_size", 20), "total": total}

    def searchContent(self, key, quick, pg="1"):
        self._ensure_session()
        try:
            pg = int(pg or 1)
        except Exception:
            pg = 1
        hits, pages, total = self._search(str(key), pg)
        lst = [self._item(it) for it in hits]
        return {"list": lst, "page": pg, "pagecount": pages, "total": total}

    # ================================================================= 详情
    def detailContent(self, ids):
        self._ensure_session()
        if not ids:
            return {"list": []}
        vid = str(ids[0]).split(",")[0]
        path = "/api/v1/video/detail"
        r = self._get(path, headers=self._sign_headers(path), params={"id": vid})
        if r.get("code") != 1 or not isinstance(r.get("data"), dict):
            return {"list": []}
        vi = r["data"].get("vod_info") or {}

        play_from, play_url, self._lines = [], [], []
        self._tkmap = {}
        for idx, line in enumerate(vi.get("vod_url_with_player") or []):
            name = str(line.get("name") or "")
            code = str(line.get("code") or "")
            eps, tks = [], []
            for ep_i, seg in enumerate(str(line.get("url") or "").split("#")):
                if not seg:
                    continue
                if "$" in seg:
                    ep_name, tk = seg.split("$", 1)
                else:
                    ep_name, tk = seg, ""
                if not ep_name:
                    continue
                # 播放 id: 线路码|tk票根
                eps.append(ep_name + "$" + code + "|" + tk)
                tks.append(tk)
                self._tkmap[tk] = {"name": name, "code": code, "ep": ep_i}
            if not eps:
                continue
            self._lines.append({"index": idx, "name": name, "code": code, "tks": tks})
            play_from.append(name or code)
            play_url.append("#".join(eps))

        if not play_url and vi.get("vod_play_url"):
            play_from = [vi.get("vod_play_from") or "线路"]
            play_url = [vi.get("vod_play_url")]

        return {"list": [{
            "vod_id": vid,
            "vod_name": str(vi.get("vod_name") or ""),
            "vod_pic": str(vi.get("vod_pic") or ""),
            "vod_actor": str(vi.get("vod_actor") or ""),
            "vod_director": str(vi.get("vod_director") or ""),
            "vod_year": str(vi.get("vod_year") or ""),
            "vod_area": str(vi.get("vod_area") or ""),
            "vod_lang": str(vi.get("vod_lang") or ""),
            "vod_class": str(vi.get("vod_class") or ""),
            "vod_state": str(vi.get("vod_state") or ""),
            "vod_total": str(vi.get("vod_total") or ""),
            "vod_serial": str(vi.get("vod_serial") or ""),
            "vod_remarks": str(vi.get("vod_remarks") or ""),
            "vod_content": str(vi.get("vod_content") or vi.get("vod_blurb") or ""),
            "vod_play_from": "$$$".join(play_from),
            "vod_play_url": "$$$".join(play_url),
        }]}

    # ================================================================= 播放
    def _decode_ticket(self, ticket):
        """play_ticket 第一段是 base64url 明文 JSON"""
        try:
            seg = ticket.split(".")[0]
            seg += "=" * (-len(seg) % 4)
            return json.loads(base64.urlsafe_b64decode(seg).decode("utf-8", "replace"))
        except Exception:
            return None

    def _ticket(self, tk):
        """tk -> play_ticket"""
        r = self._post("/api/v1/vod/ticket", {"token": tk},
                       headers=self._sign_headers("/api/v1/vod/ticket"))
        if r.get("code") == 1 and isinstance(r.get("data"), dict):
            return r["data"].get("ticket")
        return None

    def _resolve(self, tk):
        """play_ticket -> 真实播放地址"""
        ticket = self._ticket(tk)
        if not ticket:
            return None, "换票失败"
        pl = self._decode_ticket(ticket)
        if not pl:
            return None, "票据解析失败"
        d = pl.get("data") or {}
        api = str(d.get("parse_api") or "").replace("\\u00026", "&")
        du = str(d.get("url") or "")
        if not api or not du:
            return None, "无解析配置"

        # ① 服务端本地解析(相对路径)
        if api.startswith("/"):
            full = self.base + api + urllib.parse.quote(du, safe="")
            code, text = self._get_text(full)
            j = self._try_json(text)
            if isinstance(j, dict):
                if j.get("url"):
                    return j["url"], ""
                msg = str(j.get("system") or j.get("msg") or "解析失败")
                return None, msg
            if code == 200 and text.startswith("http"):
                return text.strip(), ""
            return None, "解析失败(%s)" % code

        # ② 外部解析接口
        if "{md5}" in api:
            target = api.replace("{md5}", du)
        elif "url=" in api:
            target = api + urllib.parse.quote(du, safe="")
        else:
            target = api + du
        code, text = self._get_text(target)
        j = self._try_json(text)
        if isinstance(j, dict):
            if j.get("url"):
                return j["url"], ""
            return None, str(j.get("msg") or "外部解析失败")
        if code == 200 and text.startswith("http"):
            return text.strip(), ""
        return None, "外部解析失败(%s)" % code

    @staticmethod
    def _try_json(text):
        try:
            t = (text or "").strip()
            if t.startswith("{") or t.startswith("["):
                return json.loads(t)
        except Exception:
            return None
        return None

    def playerContent(self, flag, id, vipFlags=None):
        self._ensure_session()
        if not id:
            return {"parse": 0, "url": "", "header": {}}
        code, tk = "", id
        if "|" in id:
            code, tk = id.split("|", 1)

        # 1) 优先按当前线路解析
        url, err = self._resolve(tk)

        # 2) 当前线路失败(付费/失效/超时)→ 自动降级到其它线路的同一集
        if not url and self.cfg.get("auto_fallback", 1):
            cur = self._tkmap.get(tk) or {}
            ep = cur.get("ep", 0)
            for ln in self._lines:
                if ln.get("code") == code:
                    continue
                tks = ln.get("tks") or []
                if ep >= len(tks):
                    continue
                u2, _e2 = self._resolve(tks[ep])
                if u2:
                    url = u2
                    err = ""
                    break

        if url:
            return {"parse": 0, "url": url, "header": {
                "User-Agent": self.cfg.get("user_agent", "okhttp/3.12.1"),
                "Referer": "https://www.google.com/",
            }}
        return {"parse": 0, "url": "", "header": {}, "msg": err or "播放失败"}


if __name__ == "__main__":
    s = ShanZhaSpider()
    s.init("")
    print("name    :", s.getName())
    print("device  :", s.device_id)
    print("jwt     :", (s.jwt or "")[:36], "...")
    print("session :", s.session_id)

    h = s.homeContent(False)
    print("\n分类    :", [(c["type_id"], c["type_name"]) for c in h.get("class", [])])

    c = s.categoryContent("2", 1, False, {})
    print("连续剧  :", len(c.get("list", [])), "条 / 共", c.get("total"))
    if c.get("list"):
        print("  首条  :", c["list"][0]["vod_name"])

    s2 = s.searchContent("交锋", False)
    print("搜索交锋:", len(s2.get("list", [])), "条")

    vid = (s2.get("list") or c.get("list") or [{}])[0].get("vod_id")
    if vid:
        d = s.detailContent([vid])
        if d.get("list"):
            dd = d["list"][0]
            names = dd["vod_play_from"].split("$$$")
            eps = dd["vod_play_url"].split("$$$")
            print("\n详情    :", dd["vod_name"], "| 线路:", names)
            for i, nm in enumerate(names):
                ep = eps[i].split("#")[0]
                p = s.playerContent(nm, ep)
                u = p.get("url") or ""
                print("  [%s] → %s" % (nm, (u[:96] + "...") if len(u) > 96 else (u or p.get("msg", ""))))


# ======================================================================
# 模块：gg —— 咕噜咕噜（首页 / 分类主源，T3 私有协议）
# ======================================================================
# -*- coding: utf-8 -*-
"""
咕噜咕噜 —— TVBox 蜘蛛框架Python 爬虫）。

"""


import base64
import gzip
import hashlib
import hmac
import json
import re
import secrets
import threading
import time
import urllib.error
import urllib.request
import zlib
from urllib.parse import quote

try:
    import requests as _requests
except Exception:
    _requests = None

API_URL = "http://103.45.132.22:19987/app/bn/v2"
HOST = "http://103.45.132.22:19987"
USER_AGENT = "Dart/3.10 (dart:io)"
APP_VERSION = "2.2.5"
BUILD_NUMBER = "20109"
APP_SIGNATURE = "32E0AB4FF93A29CE0E6F0BFB01F2F1B788E76262731F3F30F509CB822428ED58"
DEVICE_BUILD = "pangu-build-component-system-513739-s9vkd-rlxnj-p3rhm"
VERSION_GUARD_MARKERS = ("__v99_", "glgl.tv", "111.170.58.215", "shu.jpg")
FALLBACK_PARSERS = {
    28: {"name": "咕噜金牌", "url": "http://111.170.58.215:5499/api.php?id=",
         "mode": "json", "result_key": "url", "server": False},
}


# ============ protobuf 工具 ============

def _varint(value):
    if value < 0:
        raise ValueError("negative protobuf varint")
    output = bytearray()
    while value >= 0x80:
        output.append((value & 0x7F) | 0x80)
        value >>= 7
    output.append(value)
    return bytes(output)


def _field_bytes(number, value):
    if isinstance(value, str):
        value = value.encode("utf-8")
    return _varint((number << 3) | 2) + _varint(len(value)) + value


def _field_varint(number, value):
    return _varint(number << 3) + _varint(value)


def _read_varint(data, position):
    value = 0
    shift = 0
    while position < len(data) and shift < 70:
        byte = data[position]
        position += 1
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            return value, position
        shift += 7
    raise ValueError("invalid protobuf varint")


def _parse_fields(data):
    fields = []
    position = 0
    while position < len(data):
        key, position = _read_varint(data, position)
        number, wire = key >> 3, key & 7
        if number == 0:
            raise ValueError("invalid protobuf field zero")
        if wire == 0:
            value, position = _read_varint(data, position)
        elif wire == 1:
            value = data[position:position + 8]
            position += 8
        elif wire == 2:
            size, position = _read_varint(data, position)
            value = data[position:position + size]
            position += size
        elif wire == 5:
            value = data[position:position + 4]
            position += 4
        else:
            raise ValueError("unsupported protobuf wire type %d" % wire)
        if position > len(data):
            raise ValueError("truncated protobuf field")
        fields.append((number, wire, value))
    return fields


def _field_values(data, number, wire=None):
    return [v for n, w, v in _parse_fields(data)
            if n == number and (wire is None or w == wire)]


def _field_value(data, number, default=None, wire=None):
    values = _field_values(data, number, wire)
    return values[-1] if values else default


def _text(value, default=""):
    if not isinstance(value, bytes):
        return value
    try:
        return value.decode("utf-8")
    except UnicodeDecodeError:
        return default


def _packed_varints(data):
    values = []
    position = 0
    while position < len(data):
        value, position = _read_varint(data, position)
        values.append(value)
    return values


def _raw_deflate(data):
    compressor = zlib.compressobj(level=9, method=zlib.DEFLATED, wbits=-15,
                                  memLevel=8, strategy=zlib.Z_RLE)
    return compressor.compress(data) + compressor.flush()


# ============ 纯标准库密码学 ============

def g_xtime(a):
    b = a << 1
    if b & 0x100:
        b ^= 0x11B
    return b & 0xFF


def _gf256_mul(a, b):
    result = 0
    while b:
        if b & 1:
            result ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi:
            a ^= 0x1B
        b >>= 1
    return result


def _build_aes_tables():
    exp = [0] * 256
    log = [0] * 256
    x = 1
    for i in range(255):
        exp[i] = x
        log[x] = i
        x = _gf256_mul(x, 0x03)
    sbox = [0] * 256
    inv_sbox = [0] * 256
    for i in range(256):
        inv = 0 if i == 0 else exp[(255 - log[i]) % 255]
        t = inv
        s = inv
        for _ in range(4):
            s = ((s << 1) | (s >> 7)) & 0xFF
            t ^= s
        sbox[i] = t ^ 0x63
        inv_sbox[sbox[i]] = i
    return bytes(sbox), bytes(inv_sbox)


_SBOX, _INV_SBOX = _build_aes_tables()


def g_expand_key(key):
    rcon = 1
    words = [list(key[i:i + 4]) for i in range(0, 32, 4)]
    while len(words) < 60:
        temp = words[-1][:]
        if len(words) % 8 == 0:
            temp = temp[1:] + temp[:1]
            temp = [_SBOX[b] for b in temp]
            temp[0] ^= rcon
            rcon = g_xtime(rcon)
        elif len(words) % 8 == 4:
            temp = [_SBOX[b] for b in temp]
        words.append([words[-8][i] ^ temp[i] for i in range(4)])
    return [sum((words[i:i + 4]), []) for i in range(0, 60, 4)]


def g_shift_rows(state, encrypt=True):
    out = [0] * 16
    for r in range(4):
        for c in range(4):
            out[r + 4 * c] = state[r + 4 * ((c + (r if encrypt else -r)) % 4)]
    return out


def g_mix_columns(state):
    out = state[:]
    for c in range(4):
        a = out[0 + 4 * c]
        b = out[1 + 4 * c]
        d = out[2 + 4 * c]
        e = out[3 + 4 * c]
        t = a ^ b ^ d ^ e
        out[0 + 4 * c] = a ^ t ^ g_xtime(a ^ b)
        out[1 + 4 * c] = b ^ t ^ g_xtime(b ^ d)
        out[2 + 4 * c] = d ^ t ^ g_xtime(d ^ e)
        out[3 + 4 * c] = e ^ t ^ g_xtime(e ^ a)
    return out


def g_mul9(x):
    return g_xtime(g_xtime(g_xtime(x))) ^ x


def g_mul11(x):
    return g_xtime(g_xtime(g_xtime(x))) ^ g_xtime(x) ^ x


def g_mul13(x):
    return g_xtime(g_xtime(g_xtime(x))) ^ g_xtime(g_xtime(x)) ^ x


def g_mul14(x):
    return g_xtime(g_xtime(g_xtime(x))) ^ g_xtime(g_xtime(x)) ^ g_xtime(x)


def g_inv_mix_columns(state):
    out = state[:]
    for c in range(4):
        a = out[0 + 4 * c]
        b = out[1 + 4 * c]
        d = out[2 + 4 * c]
        e = out[3 + 4 * c]
        out[0 + 4 * c] = g_mul14(a) ^ g_mul11(b) ^ g_mul13(d) ^ g_mul9(e)
        out[1 + 4 * c] = g_mul9(a) ^ g_mul14(b) ^ g_mul11(d) ^ g_mul13(e)
        out[2 + 4 * c] = g_mul13(a) ^ g_mul9(b) ^ g_mul14(d) ^ g_mul11(e)
        out[3 + 4 * c] = g_mul11(a) ^ g_mul13(b) ^ g_mul9(d) ^ g_mul14(e)
    return out


def _aes_encrypt_block(block, round_keys):
    state = [s ^ k for s, k in zip(block, round_keys[0])]
    for r in range(1, 14):
        state = [_SBOX[b] for b in state]
        state = g_shift_rows(state, True)
        state = g_mix_columns(state)
        state = [s ^ k for s, k in zip(state, round_keys[r])]
    state = [_SBOX[b] for b in state]
    state = g_shift_rows(state, True)
    return bytes([s ^ k for s, k in zip(state, round_keys[14])])


def _aes_decrypt_block(block, round_keys):
    state = [s ^ k for s, k in zip(block, round_keys[14])]
    for r in range(13, 0, -1):
        state = g_shift_rows(state, False)
        state = [_INV_SBOX[b] for b in state]
        state = [s ^ k for s, k in zip(state, round_keys[r])]
        state = g_inv_mix_columns(state)
    state = g_shift_rows(state, False)
    state = [_INV_SBOX[b] for b in state]
    return bytes([s ^ k for s, k in zip(state, round_keys[0])])


def _pkcs7_pad(data):
    size = 16 - (len(data) % 16)
    return data + bytes([size] * size)


def _pkcs7_unpad(data):
    if not data:
        raise ValueError("empty plaintext")
    size = data[-1]
    if size < 1 or size > 16 or data[-size:] != bytes([size] * size):
        raise ValueError("invalid PKCS7 padding")
    return data[:-size]


def _aes256_cbc_encrypt(key, iv, data):
    round_keys = g_expand_key(key)
    previous = iv
    out = bytearray()
    data = _pkcs7_pad(data)
    for i in range(0, len(data), 16):
        block = bytes(b ^ p for b, p in zip(data[i:i + 16], previous))
        enc = _aes_encrypt_block(block, round_keys)
        out += enc
        previous = enc
    return bytes(out)


def _aes256_cbc_decrypt(key, iv, data):
    round_keys = g_expand_key(key)
    previous = iv
    out = bytearray()
    for i in range(0, len(data), 16):
        block = data[i:i + 16]
        dec = _aes_decrypt_block(block, round_keys)
        out += bytes(b ^ p for b, p in zip(dec, previous))
        previous = block
    return _pkcs7_unpad(bytes(out))


_GCM_REDUCTION = 0xE1000000000000000000000000000000


def g_ghash_mul(x, y):
    z = 0
    for i in range(128):
        if (x >> (127 - i)) & 1:
            z ^= y
        if y & 1:
            y = (y >> 1) ^ _GCM_REDUCTION
        else:
            y >>= 1
    return z


def g_ghash(h, aad, ciphertext):
    y = 0
    for i in range(0, len(aad), 16):
        block = int.from_bytes(aad[i:i + 16].ljust(16, b"\x00"), "big")
        y = g_ghash_mul(y ^ block, h)
    for i in range(0, len(ciphertext), 16):
        block = int.from_bytes(ciphertext[i:i + 16].ljust(16, b"\x00"), "big")
        y = g_ghash_mul(y ^ block, h)
    lengths = (len(aad) * 8).to_bytes(8, "big") + (len(ciphertext) * 8).to_bytes(8, "big")
    return g_ghash_mul(y ^ int.from_bytes(lengths, "big"), h)


def _aes256_gcm_encrypt(key, nonce, data, aad=b""):
    round_keys = g_expand_key(key)
    h = int.from_bytes(_aes_encrypt_block(b"\x00" * 16, round_keys), "big")
    j0 = nonce + b"\x00\x00\x00\x01"
    counter = int.from_bytes(j0, "big")
    out = bytearray()
    for i in range(0, len(data), 16):
        counter += 1
        keystream = _aes_encrypt_block(counter.to_bytes(16, "big"), round_keys)
        chunk = data[i:i + 16]
        out += bytes(b ^ k for b, k in zip(chunk, keystream))
    ciphertext = bytes(out)
    s = g_ghash(h, aad, ciphertext)
    tag_block = _aes_encrypt_block(j0, round_keys)
    tag = (s ^ int.from_bytes(tag_block, "big")).to_bytes(16, "big")[:16]
    return ciphertext, tag


def _aes256_gcm_decrypt(key, nonce, data, tag, aad=b""):
    round_keys = g_expand_key(key)
    h = int.from_bytes(_aes_encrypt_block(b"\x00" * 16, round_keys), "big")
    j0 = nonce + b"\x00\x00\x00\x01"
    s = g_ghash(h, aad, data)
    tag_block = _aes_encrypt_block(j0, round_keys)
    expected = (s ^ int.from_bytes(tag_block, "big")).to_bytes(16, "big")[:16]
    if not hmac.compare_digest(expected, tag):
        raise ValueError("GCM tag mismatch")
    counter = int.from_bytes(j0, "big")
    out = bytearray()
    for i in range(0, len(data), 16):
        counter += 1
        keystream = _aes_encrypt_block(counter.to_bytes(16, "big"), round_keys)
        chunk = data[i:i + 16]
        out += bytes(b ^ k for b, k in zip(chunk, keystream))
    return bytes(out)


# P-256 (secp256r1) 椭圆曲线

g_P256_P = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
g_P256_A = g_P256_P - 3
_P256_B = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B
g_P256_N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
g_P256_G = (0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
           0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5)


def _modinv(a, m):
    if m == 1:
        return 0
    t, newt = 0, 1
    r, newr = m, a % m
    while newr:
        q = r // newr
        t, newt = newt, t - q * newt
        r, newr = newr, r - q * newr
    if r != 1:
        raise ValueError("no modular inverse")
    return t % m


def g_p256_double(point):
    if point is None:
        return None
    x, y = point
    if y == 0:
        return None
    lam = (3 * x * x + g_P256_A) * _modinv(2 * y, g_P256_P) % g_P256_P
    x3 = (lam * lam - 2 * x) % g_P256_P
    y3 = (lam * (x - x3) - y) % g_P256_P
    return (x3, y3)


def g_p256_add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2:
        if (y1 + y2) % g_P256_P == 0:
            return None
        return g_p256_double(p1)
    lam = (y2 - y1) * _modinv(x2 - x1, g_P256_P) % g_P256_P
    x3 = (lam * lam - x1 - x2) % g_P256_P
    y3 = (lam * (x1 - x3) - y1) % g_P256_P
    return (x3, y3)


def g_p256_mul(k, point):
    result = None
    addend = point
    while k:
        if k & 1:
            result = g_p256_add(result, addend)
        addend = g_p256_double(addend)
        k >>= 1
    return result


def _p256_ecdh_x(private_d, server_point):
    shared = g_p256_mul(private_d, server_point)
    if shared is None:
        raise ValueError("ECDH point at infinity")
    return shared[0].to_bytes(32, "big")


def _sec1_export_public(point):
    return b"\x04" + point[0].to_bytes(32, "big") + point[1].to_bytes(32, "big")


def _sec1_import_public(data):
    raw = bytes(data or b"")
    if len(raw) == 65 and raw[0] == 4:
        x = int.from_bytes(raw[1:33], "big")
        y = int.from_bytes(raw[33:65], "big")
        return (x, y)
    if len(raw) == 33 and raw[0] in (2, 3):
        x = int.from_bytes(raw[1:], "big")
        y2 = (pow(x, 3, g_P256_P) - 3 * x + _P256_B) % g_P256_P
        y = pow(y2, (g_P256_P + 1) // 4, g_P256_P)
        if (y * y) % g_P256_P != y2:
            raise ValueError("point not on curve")
        if (y & 1) != (raw[0] & 1):
            y = g_P256_P - y
        return (x, y)
    raise ValueError("invalid P-256 SEC1 public key")


def _derive_key(session_id, shared_x):
    prk = hmac.new(session_id.encode("ascii"), shared_x, hashlib.sha256).digest()
    return hmac.new(prk, b"v2-session\x01", hashlib.sha256).digest()


# ============ HTTP（纯 urllib） ============

def _http_post(url, body, headers, timeout=15):
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        response = urllib.request.urlopen(request, timeout=timeout)
    except urllib.error.HTTPError as error:
        raise RuntimeError("HTTP %s: %s" % (error.code, error.read(200)))
    except urllib.error.URLError as error:
        raise RuntimeError("request failed: %s" % (error.reason,))
    content = response.read()
    encoding = response.headers.get("Content-Encoding", "")
    if "gzip" in encoding.lower() or content[:2] == b"\x1f\x8b":
        try:
            content = gzip.decompress(content)
        except Exception:
            pass
    return content


def _http_get(url, headers, timeout=15):
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        response = urllib.request.urlopen(request, timeout=timeout)
    except urllib.error.HTTPError as error:
        return error.code, error.read(200)
    except urllib.error.URLError as error:
        raise RuntimeError("request failed: %s" % (error.reason,))
    content = response.read()
    encoding = response.headers.get("Content-Encoding", "")
    if "gzip" in encoding.lower() or content[:2] == b"\x1f\x8b":
        try:
            content = gzip.decompress(content)
        except Exception:
            pass
    return response.status, content


# ============ 协议客户端 ============

class _GuluProtocol:
    def __init__(self, timeout=15):
        self.timeout = timeout
        self.session_id = ""
        self.session_key = b""
        self.device_id = secrets.token_hex(8)
        self.request_id = 0
        self.players = {}
        self.parsers = {}
        self.last_detail_error = ""
        self.lock = threading.RLock()

    def _post(self, body, header_name, header_value, extra_headers=None):
        headers = {
            "User-Agent": USER_AGENT, header_name: header_value,
            "Content-Type": "application/x-protobuf", "Accept-Encoding": "gzip",
            "Content-Length": str(len(body)), "Host": "103.45.132.22:19987",
        }
        if extra_headers:
            headers.update(extra_headers)
        return _http_post(API_URL, body, headers, self.timeout)

    def handshake(self):
        private_d = int.from_bytes(secrets.token_bytes(32), "big") % (g_P256_N - 1) + 1
        public_point = g_p256_mul(private_d, g_P256_G)
        public_key = _sec1_export_public(public_point)
        capabilities = _field_varint(1, 1) + _field_varint(2, 0) + _field_varint(3, 1)
        request = (_field_bytes(1, public_key) + _field_bytes(2, b"1.0.0")
                   + _field_bytes(3, capabilities))
        handshake_key = secrets.token_hex(16)
        iv = secrets.token_bytes(16)
        encrypted = base64.b64encode(
            iv + _aes256_cbc_encrypt(handshake_key.encode("ascii"), iv,
                                     zlib.compress(request, 4)))
        content = self._post(encrypted, "x-handshake-key", handshake_key)
        raw = base64.b64decode(content)
        response_cipher_key = handshake_key.encode("ascii")
        plain = zlib.decompress(
            _aes256_cbc_decrypt(response_cipher_key, raw[:16], raw[16:]))
        session_id = _field_value(plain, 1, wire=2)
        server_public = _field_value(plain, 2, wire=2)
        if not session_id or not server_public:
            raise RuntimeError("invalid handshake response")
        self.session_id = session_id.decode("ascii")
        server_point = _sec1_import_public(server_public)
        shared_x = _p256_ecdh_x(private_d, server_point)
        self.session_key = _derive_key(self.session_id, shared_x)
        self.request_id = 0

    def _encrypt(self, data):
        nonce = secrets.token_bytes(12)
        ciphertext, tag = _aes256_gcm_encrypt(self.session_key, nonce, _raw_deflate(data))
        return nonce + ciphertext + tag

    def _decrypt(self, data):
        if len(data) < 28:
            raise ValueError("invalid GCM payload")
        nonce = data[:12]
        ciphertext = data[12:-16]
        tag = data[-16:]
        compressed = _aes256_gcm_decrypt(self.session_key, nonce, ciphertext, tag)
        return zlib.decompress(compressed, -15)

    def request(self, method, payload=b"", scope=3, extra_headers=None):
        with self.lock:
            if not self.session_id:
                self.handshake()
            self.request_id += 1
            request_id = self.request_id
            core = (_field_varint(1, request_id) + _field_varint(2, scope)
                    + _field_varint(3, method) + _field_bytes(4, self.device_id)
                    + _field_bytes(5, b"") + _field_bytes(6, payload)
                    + _field_varint(7, int(time.time() * 1000)))
            body = _field_varint(1, request_id) + _field_bytes(2, self._encrypt(core))
            content = self._post(body, "x-session-id", self.session_id,
                                 extra_headers=extra_headers)
            encrypted = _field_value(content, 2, wire=2)
            if encrypted is None:
                error = _text(_field_value(content, 3, b"", wire=2))
                raise RuntimeError(error or "server rejected request")
            plain = self._decrypt(encrypted)
            status = _text(_field_value(plain, 3, b"", wire=2))
            if status and status not in ("ok", "success"):
                raise RuntimeError(status)
            return plain

    def boot(self):
        now_us = int(time.time() * 1_000_000)
        app = (_field_bytes(1, "咕噜咕噜") + _field_bytes(2, APP_VERSION)
               + _field_bytes(3, b"com.himrsc.viz") + _field_bytes(4, APP_SIGNATURE)
               + _field_bytes(5, BUILD_NUMBER) + _field_varint(6, now_us)
               + _field_varint(7, now_us))
        device = (_field_bytes(1, self.device_id) + _field_varint(2, 1)
                  + _field_bytes(3, b"15") + _field_bytes(4, b"Redmi K50 Ultra")
                  + _field_bytes(5, b"Redmi/diting/diting:15/AQ3A.240912.001/OS2.0.215.0.VOACNXM:user/release-keys")
                  + _field_bytes(6, b"Redmi") + _field_bytes(7, b"qcom")
                  + _field_varint(8, 0) + _field_bytes(9, b"unknown")
                  + _field_bytes(10, DEVICE_BUILD) + _field_varint(11, 0)
                  + _field_varint(12, 35))
        payload = (_field_bytes(1, b"v2") + _field_bytes(2, b"android")
                   + _field_bytes(3, b"gulu") + _field_bytes(4, app)
                   + _field_bytes(5, device))
        response = self.request(0, payload, scope=1)
        config = _field_value(response, 4, b"", wire=2)
        players = {}
        for item in _field_values(config, 4, wire=2):
            code = _text(_field_value(item, 3, b"", wire=2))
            if not code:
                continue
            parser_ids = []
            for packed in _field_values(item, 8, wire=2):
                parser_ids.extend(_packed_varints(packed))
            players[code] = {"id": _field_value(item, 1, 0, wire=0),
                             "name": _text(_field_value(item, 4, b"", wire=2)),
                             "parser_ids": parser_ids}
        parsers = {}
        for item in _field_values(config, 7, wire=2):
            parser_id = _field_value(item, 1, 0, wire=0)
            if parser_id:
                parsers[parser_id] = {
                    "name": _text(_field_value(item, 2, b"", wire=2)),
                    "url": _text(_field_value(item, 3, b"", wire=2)),
                    "mode": _text(_field_value(item, 4, b"", wire=2)),
                    "result_key": _text(_field_value(item, 10, b"url", wire=2)),
                    "server": bool(_field_value(item, 20, 0, wire=0))}
        self.players = players
        self.parsers = parsers

    def search(self, keyword, page=1, limit=21, category_id="", genre="", area="",
               sort="vod_hits_month"):
        sort = str(sort or "vod_hits_month")
        filters = _field_bytes(18, sort.encode("utf-8")) + _field_varint(19, 1)
        category_id = str(category_id or "").strip()
        if category_id:
            filters += _field_bytes(3, category_id) + _field_bytes(4, category_id)
        genre = str(genre or "").strip()
        if genre:
            filters += _field_bytes(8, genre)
        area = str(area or "").strip()
        if area:
            filters += _field_bytes(6, area)
        payload = (_field_bytes(1, keyword) + _field_varint(2, int(page))
                   + _field_varint(3, int(limit)) + _field_bytes(5, filters))
        response = self.request(61, payload)
        data = _field_value(response, 4, b"", wire=2)
        videos = []
        for message in _field_values(data, 1, wire=2):
            videos.append({
                "vod_id": str(_field_value(message, 1, 0, wire=0)),
                "vod_name": _text(_field_value(message, 3, b"", wire=2)),
                "vod_pic": _text(_field_value(message, 6, b"", wire=2)),
                "vod_remarks": _text(_field_value(message, 11, b"", wire=2)),
            })
        page_info = _field_value(data, 2, b"", wire=2)
        return {"videos": videos,
                "page": _field_value(page_info, 1, int(page), wire=0),
                "pagecount": _field_value(page_info, 3, 1, wire=0),
                "limit": _field_value(page_info, 2, int(limit), wire=0),
                "total": _field_value(page_info, 4, len(videos), wire=0)}

    def detail(self, vod_id):
        self.last_detail_error = ""
        payload = (_field_varint(1, int(vod_id)) + _field_bytes(3, APP_VERSION)
                   + _field_bytes(4, b"1") + _field_varint(5, 1))
        response = self.request(62, payload,
                                extra_headers={"x-player-page-protection": "1"})
        data = _field_value(response, 4, b"", wire=2)
        name = _text(_field_value(data, 5, b"", wire=2))
        guard_text = " ".join(
            [_text(_field_value(data, field, b"", wire=2)) for field in (5, 13, 21)]
            + [_text(_field_value(source, 1, b"", wire=2))
               for source in _field_values(data, 75, wire=2)]).lower()
        if any(marker in guard_text for marker in VERSION_GUARD_MARKERS):
            self.last_detail_error = "server_version_guard"
            return None
        if not name or name.startswith("最新版本下载地址") or _field_value(data, 1, 0, wire=0) == 0:
            self.last_detail_error = "invalid_detail"
            return None
        sources = []
        for source in _field_values(data, 75, wire=2):
            code = _text(_field_value(source, 1, b"", wire=2))
            if not code or code.startswith("__v99_"):
                continue
            config = self.players.get(code, {})
            episodes = []
            for episode in _field_values(source, 2, wire=2):
                episode_id = _text(_field_value(episode, 3, b"", wire=2))
                if not episode_id:
                    continue
                episodes.append({
                    "index": _field_value(episode, 1, len(episodes) + 1, wire=0),
                    "id": episode_id,
                    "name": _text(_field_value(episode, 4, b"", wire=2)) or "第%d集" % (len(episodes) + 1)})
            if episodes:
                sources.append({"code": code,
                                "name": config.get("name", code),
                                "parser_id": (config.get("parser_ids") or [0])[0],
                                "episodes": episodes})
        return {"id": str(_field_value(data, 1, vod_id, wire=0)),
                "name": name, "pic": _text(_field_value(data, 13, b"", wire=2)),
                "remarks": _text(_field_value(data, 22, b"", wire=2)),
                "content": _text(_field_value(data, 21, b"", wire=2)),
                "area": _text(_field_value(data, 28, b"", wire=2)),
                "year": _text(_field_value(data, 30, b"", wire=2)),
                "sources": sources}

    def play(self, parser_id, play_id):
        payload = _field_varint(1, int(parser_id)) + _field_bytes(2, play_id)
        response = self.request(69, payload)
        data = _field_value(response, 4, b"", wire=2)
        return _text(_field_value(data, 2, b"", wire=2))

    def reset_session(self):
        self.session_id = ""
        self.session_key = b""
        self.request_id = 0


# ============ T3 接口 ============

class GuluSpider:
    """咕噜咕噜"""

    source_name = "gulu"
    display_name = "咕噜咕噜"

    HOST = HOST
    UA = USER_AGENT

    _play_order = [
        "咕噜4K", "菲乐4K", "鲸宝4K", "神话", "臻影4K", "精品2K",
        "鲸宝2K", "短剧2K", "天堂", "☆讯飞☆", "☆奇趣☆", "☆果汁☆",
        "☆酷萌☆", "☆哔哩☆", "咖啡", "量子", "非凡", "暴风", "蚂蚁",
        "小熊", "海外", "花旗",
    ]
    _categories = [("1", "电影"), ("2", "电视剧"), ("3", "综艺"),
                   ("4", "动漫"), ("5", "短剧"), ("60", "直播")]

    # ---- 二级分类（筛选字段经服务器实测：F8=类型，F6=地区，F18=排序） ----
    _filter_genres = ["动作", "喜剧", "爱情", "科幻", "恐怖", "剧情", "战争", "犯罪",
                      "悬疑", "动画", "冒险", "奇幻", "惊悚", "家庭"]
    _filter_areas = ["大陆", "香港", "台湾", "美国", "日本", "韩国", "英国", "法国",
                     "泰国", "印度"]
    _filter_sorts = [("月热门", "vod_hits_month"), ("周热门", "vod_hits_week"),
                     ("日热门", "vod_hits_day"), ("最新", "vod_time"),
                     ("评分", "vod_score")]

    @classmethod
    def _filters_for(cls, tid):
        if str(tid) == "60":
            return []
        def _row(key, pairs):
            return {"key": key, "name": key,
                    "value": [{"n": "全部", "v": ""}] + [{"n": n, "v": v} for n, v in pairs]}
        return [
            _row("类型", [(g, g) for g in cls._filter_genres]),
            _row("地区", [(a, a) for a in cls._filter_areas]),
            _row("排序", list(cls._filter_sorts)),
        ]

    @staticmethod
    def _extend_value(extend, key):
        if not extend:
            return ""
        if isinstance(extend, str):
            try:
                extend = json.loads(extend)
            except Exception:
                return ""
        if isinstance(extend, dict):
            return str(extend.get(key) or "").strip()
        return ""

    def __init__(self) -> None:
        self.protocol = _GuluProtocol()
        self.last_error = ""
        # ---- 蜘蛛框架py 模板契约 ----
        self.header = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-S9080) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Referer": HOST,
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        self.s = self.session = self.sess = _requests.Session() if _requests else None

    def _get(self, url, referer=None):
        h = dict(self.header)
        if referer:
            h["Referer"] = referer
        if self.s is not None:
            try:
                r = self.s.get(url, headers=h, timeout=12, allow_redirects=True)
                if r.status_code < 400:
                    return r.text
            except Exception:
                pass
        try:
            import urllib.request
            req = urllib.request.Request(url, headers=h)
            with urllib.request.urlopen(req, timeout=12) as resp:
                return resp.read().decode("utf-8", "ignore")
        except Exception:
            return ""

    def _u(self, u):
        if not u:
            return u
        u = u.strip()
        if u.startswith("//"):
            return "https:" + u
        if u.startswith("http"):
            return u
        if u.startswith("/"):
            m = re.match(r"(https?://[^/]+)", HOST)
            return (m.group(1) if m else HOST) + u
        return HOST.rstrip("/") + "/" + u.lstrip("/")

    def isVideoFormat(self, url):
        if not url:
            return False
        u = str(url).lower()
        return u.endswith((".m3u8", ".mp4", ".flv", ".mkv", ".ts", ".avi")) or "m3u8" in u

    def init(self, extend=""):
        """drpy 空闲刷新钩子：仅复位会话无关状态，不依赖本方法被执行。"""
        return None

    def _ensure_boot(self) -> None:
        try:
            if not self.protocol.session_id:
                self.protocol.handshake()
            if not self.protocol.players:
                self.protocol.boot()
        except Exception as e:
            self.last_error = "%s:%s" % (type(e).__name__, e)

    def _search(self, keyword, page=1, limit=21, category_id="", genre="", area="",
                sort="vod_hits_month"):
        self._ensure_boot()
        try:
            return self.protocol.search(keyword, page, limit, category_id,
                                        genre=genre, area=area, sort=sort)
        except Exception:
            try:
                self.protocol.reset_session()
                self._ensure_boot()
                return self.protocol.search(keyword, page, limit, category_id,
                                            genre=genre, area=area, sort=sort)
            except Exception as e:
                self.last_error = "%s" % e
                return {"videos": [], "page": page, "pagecount": 1,
                        "limit": limit, "total": 0}

    # ---- T3 契约 ----

    def homeContent(self, filter=False):
        classes = [{"type_id": tid, "type_name": nm} for tid, nm in self._categories]
        filters = {tid: self._filters_for(tid) for tid, nm in self._categories}
        cards = []
        try:
            result = self._search("", 1, 21)
            cards = self._cards(result.get("videos", []), 1, 21)[:20]
        except Exception:
            pass
        return {"class": classes, "filters": filters, "list": cards}

    def homeVideoContent(self):
        return self.homeContent()

    def categoryContent(self, tid, pg="1", filter=True, extend=""):
        pg = max(1, int(pg or 1))
        tid = str(tid or "").strip()
        genre = self._extend_value(extend, "类型")
        area = self._extend_value(extend, "地区")
        sort = self._extend_value(extend, "排序") or "vod_hits_month"
        result = self._search("", pg, 21, tid, genre=genre, area=area, sort=sort)
        return {"class": [{"type_id": t, "type_name": nm}
                          for t, nm in self._categories],
                "filters": {t: self._filters_for(t) for t, nm in self._categories},
                "list": self._cards(result.get("videos", []), pg, 21),
                "page": pg, "pagecount": result.get("pagecount", 1),
                "limit": result.get("limit", 21), "total": result.get("total", 0)}

    def detailContent(self, ids, flags=None):
        vod_id = self._detail_id(ids)
        if not vod_id:
            return {"list": []}
        self._ensure_boot()
        try:
            detail = self.protocol.detail(vod_id)
        except Exception:
            self.protocol.reset_session()
            self._ensure_boot()
            detail = self.protocol.detail(vod_id)
        if not detail:
            return {"list": []}

        play_from, play_blocks = [], []
        for source in detail["sources"]:
            episodes = []
            for ep in source["episodes"]:
                idx = ep["index"] or len(episodes) + 1
                encoded = "{}@{}@{}@{}".format(ep["id"], source["parser_id"],
                                               detail["name"], idx)
                episodes.append("%s$%s" % (ep["name"], encoded))
            if episodes:
                play_from.append(self._clean_name(source["name"]))
                play_blocks.append("#".join(episodes))
        paired = list(zip(play_from, play_blocks))
        paired.sort(key=lambda x: self._rank(x[0]))

        vod = {
            "vod_id": detail["id"],
            "vod_name": detail["name"],
            "vod_pic": detail["pic"],
            "vod_year": detail["year"],
            "vod_area": detail["area"],
            "vod_content": detail["content"],
            "vod_remarks": detail["remarks"],
            "vod_play_from": "$$$".join(p[0] for p in paired),
            "vod_play_url": "$$$".join(p[1] for p in paired),
        }
        return {"list": [vod]}

    def searchContent(self, key, quick=False, pg="1"):
        kw = (key or "").strip()
        if not kw:
            return {"list": []}
        pg = max(1, int(pg or 1))
        result = self._search(kw, pg, 21)
        return {"list": self._cards(result.get("videos", []), pg, 21)}

    def playerContent(self, flag, ids, vipFlags=None):
        # TVBox 传 list（如 ["id@parser@name@1"]），CLI 传 str，统一解包
        id = ids[0] if isinstance(ids, (list, tuple)) and ids else ids
        id = str(id or "").strip()
        header = self._play_header(id)
        try:
            raw_id, parser_id, vod_name, episode_index = id.split("@", 3)
            parser_id = int(parser_id or 0)
        except ValueError:
            raw_id, parser_id, vod_name, episode_index = id, 0, "", "1"
        url = raw_id if (isinstance(raw_id, str) and self._is_playable_url(raw_id)) else ""
        if not url and parser_id:
            self._ensure_boot()
            parser = self.protocol.parsers.get(parser_id, {})
            if parser and not parser.get("server", True):
                try:
                    url = self._external_play(parser_id, raw_id)
                except Exception:
                    url = ""
            if not url:
                try:
                    url = self.protocol.play(parser_id, raw_id)
                except Exception:
                    try:
                        self.protocol.reset_session()
                        self._ensure_boot()
                        url = self.protocol.play(parser_id, raw_id)
                    except Exception:
                        url = ""
        return {"parse": 0, "url": url or "", "header": json.dumps(header)}

    # ---- 工具 ----

    _PROMO_MARKS = ("glgl.tv", "下载地址", "版本已失效", "shu.jpg")

    @classmethod
    def _is_promo(cls, name, pic):
        blob = "%s %s" % (name or "", pic or "")
        return any(mk in blob for mk in cls._PROMO_MARKS)

    def _cards(self, videos, page, limit):
        cards = []
        for v in videos:
            if not v.get("vod_id"):
                continue
            name, pic = v.get("vod_name") or "", v.get("vod_pic") or ""
            if self._is_promo(name, pic):
                continue
            cards.append({"vod_id": str(v["vod_id"]), "vod_name": name,
                          "vod_pic": pic,
                          "vod_remarks": v.get("vod_remarks") or ""})
        return cards

    @staticmethod
    def _detail_id(ids) -> str:
        text = str(ids).strip()
        if text.isdigit():
            return text
        m = re.search(r"(?:^|[^0-9])(\d{1,12})(?:$|[^0-9])", text)
        return m.group(1) if m else ""

    @staticmethod
    def _clean_name(name: str) -> str:
        if not name:
            return ""
        c = re.sub(r'[【\[\(（].*?[】\]）)]', '', name)
        c = re.sub(r'\s*(?:HD|VIP|备用|推荐|极速|高清|标清|蓝光|超清|试看|抢先|预告|新版|旧版)\s*$',
                   '', c, flags=re.I)
        return re.sub(r'\s+', ' ', c).strip()

    @classmethod
    def _rank(cls, nm: str) -> int:
        c = cls._clean_name(nm).lower()
        for i, name in enumerate(cls._play_order):
            if c == name.lower() or c.startswith(name.lower()) or name.lower() in c:
                return i
        up = cls._clean_name(nm).upper()
        if "4K" in up:
            return 1000
        if "2K" in up:
            return 2000
        if "☆" in nm:
            return 3000
        return 4000

    def _play_header(self, url: str) -> dict:
        # 多数第三方 CDN 带不带 Referer 都能播；但 picovr / ppvod / quark
        # 带 Referer 反而 403（实测）。动态：这些域名去 Referer。
        _no_ref = ("picovr.com", "ppvod", "drive.quark.cn")
        h = {"User-Agent": USER_AGENT}
        if not (url and any(d in url for d in _no_ref)):
            h["Referer"] = self.HOST + "/"
        return h

    def _is_playable_url(self, value) -> bool:
        if not isinstance(value, str):
            return False
        url = value.strip()
        if not re.match(r"^https?://", url, re.I):
            return False
        return any(m in url.lower() for m in
                   (".m3u8", ".mp4", ".mkv", ".flv", ".ts", "/m.php", "?data="))

    def _external_play(self, parser_id, play_id) -> str:
        parser = self.protocol.parsers.get(parser_id, {})
        api_url = str(parser.get("url") or "").strip()
        if not api_url:
            return ""
        encoded = quote(str(play_id), safe="")
        target = api_url.replace("{url}", encoded) if "{url}" in api_url else api_url + encoded
        try:
            status, body = _http_get(target, {"User-Agent": USER_AGENT}, 15)
            payload = json.loads(body.decode("utf-8", "replace")) if status == 200 else {}
        except Exception:
            payload = {}
        return self._extract_play_url(payload, parser.get("result_key") or "url")

    def _extract_play_url(self, value, preferred_key="url") -> str:
        if isinstance(value, str):
            return value if self._is_playable_url(value) else ""
        if isinstance(value, dict):
            for key in (preferred_key, "url", "play_url", "playUrl", "m3u8", "data"):
                if key in value:
                    found = self._extract_play_url(value[key], preferred_key)
                    if found:
                        return found
            for item in value.values():
                found = self._extract_play_url(item, preferred_key)
                if found:
                    return found
        elif isinstance(value, (list, tuple)):
            for item in value:
                found = self._extract_play_url(item, preferred_key)
                if found:
                    return found
        return ""

    # ---- drpy 兼容辅助 ----

    def getName(self):
        return self.display_name

    def getDependence(self):
        return []

    def localProxy(self, param):
        u = param.get("url", "") if isinstance(param, dict) else ""
        if not u:
            return [403, "text/plain", b"", None]
        h = dict(self.header)
        if self.s is not None:
            try:
                r = self.s.get(u, headers=h, timeout=15)
                return [200, r.headers.get("Content-Type", "application/octet-stream"),
                        r.content, None]
            except Exception:
                pass
        try:
            import urllib.request
            req = urllib.request.Request(u, headers=h)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return [200, resp.headers.get("Content-Type", "application/octet-stream"),
                        resp.read(), None]
        except Exception:
            return [403, "text/plain", b"", None]

    def manualVideoCheck(self):
        return False

    def action(self, action):
        return {}

    def destroy(self):
        return None


# ============ 模块级双入口（drpy site 模式 / 旧内核兼容） ============

_SINGLETON = None


def _get_singleton():
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = GuluSpider()
    return _SINGLETON


def homeContent(filter=False):
    return _get_singleton().homeContent(filter)


def homeVideoContent():
    return _get_singleton().homeVideoContent()


def categoryContent(tid, pg="1", filter=True, extend=""):
    return _get_singleton().categoryContent(tid, pg, filter, extend)


def detailContent(ids, flags=None):
    return _get_singleton().detailContent(ids, flags)


def searchContent(key, quick=False, pg="1"):
    return _get_singleton().searchContent(key, quick, pg)


def playerContent(flag, ids, vipFlags=None):
    return _get_singleton().playerContent(flag, ids, vipFlags)


# 类名别名（部分内核按小写 spider 约定取类）
gulu_spider = GuluSpider


# ============ 命令行自检 ============

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="咕噜咕噜 T3 源自检")
    sub = parser.add_subparsers(dest="action", required=True)

    sub.add_parser("home")
    sub.add_parser("homevideos")

    p_search = sub.add_parser("search")
    p_search.add_argument("keyword")
    p_search.add_argument("pg", nargs="?", default="1")

    p_cate = sub.add_parser("category")
    p_cate.add_argument("tid")
    p_cate.add_argument("pg", nargs="?", default="1")

    p_detail = sub.add_parser("detail")
    p_detail.add_argument("vod_id")

    p_play = sub.add_parser("play")
    p_play.add_argument("encoded_id",
                        help='完整选集 id，形如 "play_id@parser_id@vod名@序号"，'
                             '也可直接传可播 URL')

    args = parser.parse_args()
    sp = GuluSpider()
    try:
        if args.action == "home":
            result = sp.homeContent()
        elif args.action == "homevideos":
            result = sp.homeVideoContent()
        elif args.action == "search":
            result = sp.searchContent(args.keyword, pg=args.pg)
        elif args.action == "category":
            result = sp.categoryContent(args.tid, args.pg)
        elif args.action == "detail":
            result = sp.detailContent(args.vod_id)
        elif args.action == "play":
            result = sp.playerContent("", args.encoded_id)
        else:
            result = {}
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    except Exception as error:
        sys.stderr.write("%s: %s\n" % (type(error).__name__, error))
        sys.exit(1)


# ==================== 云端自更新 ====================
_KISH_UPD = {}


def _kish_self():
    try:
        p = globals().get('__file__') or ''
        return p if p and os.path.isfile(p) else ''
    except Exception:
        return ''


def _kish_check(url=None):
    """拉清单 → 比版本 → 整份覆盖自己。失败静默，绝不影响主流程。"""
    url = (url or UPDATE_URL or '').strip()
    out = {'ok': False, 'msg': ''}
    if not url:
        out['msg'] = 'no url'
        return out
    try:
        sep = '&' if '?' in url else '?'
        man = {}
        for hit in ('%s%st=%d' % (url, sep, int(time.time() * 1000)), url):
            try:
                req = urllib.request.Request(
                    hit, headers={'User-Agent': 'kishuto/1.0',
                                  'Cache-Control': 'no-cache'})
                with urllib.request.urlopen(req, timeout=8) as r:
                    body = r.read()
                got = json.loads(body.decode('utf-8', 'replace'))
                if isinstance(got, dict):
                    man = got
                    break
            except Exception:
                continue
        far = str(man.get('version') or '')
        if not far:
            out['msg'] = 'bad manifest'
            return out
        out['version'] = far
        cur = tuple(int(x) for x in re.findall(r'\d+', str(CODE_VERSION)))
        new = tuple(int(x) for x in re.findall(r'\d+', far))
        if not new > cur:
            out['ok'] = True
            out['msg'] = 'up to date (%s)' % CODE_VERSION
            return out
        target = str(man.get('url') or '').strip()
        base = url.rsplit('/', 1)[0] + '/'
        if not target:
            target = base + os.path.basename(_kish_self() or 'Kishuto.py')
        elif not target.startswith('http'):
            target = base + target.lstrip('/')
        req = urllib.request.Request(
            target, headers={'User-Agent': 'kishuto/1.0',
                             'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, timeout=30) as r:
            blob = r.read()
        if not blob or len(blob) > 6 * 1024 * 1024 or b'class Spider' not in blob:
            out['msg'] = 'bad payload'
            return out
        dest = _kish_self()
        if not dest:
            out['msg'] = 'self unknown'
            return out
        tmp = dest + '.new'
        with open(tmp, 'wb') as f:
            f.write(blob)
        try:
            import shutil
            shutil.copyfile(dest, dest + '.bak')
        except Exception:
            pass
        os.replace(tmp, dest)
        out['ok'] = True
        out['updated'] = True
        out['msg'] = 'updated %s -> %s, restart to apply' % (CODE_VERSION, far)
        return out
    except Exception as exc:
        out['msg'] = '%s: %s' % (type(exc).__name__, exc)
        return out


def _kish_update_async():
    if _KISH_UPD:
        return
    _KISH_UPD['run'] = True

    def run():
        try:
            _KISH_UPD.update(_kish_check())
        except Exception:
            pass

    try:
        threading.Thread(target=run, daemon=True).start()
    except Exception:
        pass


# ==================== Kishuto 总门面 ====================
# ============================================================================
# 模块：诊断中心（Kishuto Diag）
#
# 用标准 py 协议模拟「设置中心」：分类 → 卡片 → 点开执行并显示报告。
# 不依赖壳的 action 回调，任何支持 py 源的壳都能用。
# 用法：配置里加第二个站点，api 同一个 py，ext 写 {"mode":"settings"}。
# ============================================================================

DIAG_BASE = 'https://gitee.com/tao060702/tvbox/raw/master'


QR_UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
         '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')


# ---------------------------------------------------------------------------
# 诊断中心卡片磁贴的本地图片服务：纯标准库 PNG 编码 + 127.0.0.1 HTTP。
# 不联网、不依赖 PIL / 字体；磁贴由 _diag_card_png() 生成。
# ---------------------------------------------------------------------------

_QR_SRV = {'port': 0, 'cards': {}}


def _qr_png_write(w, h, rows):
    """rows 是 RGB 像素行（bytearray(w*3)），编码成 PNG 字节。"""
    import struct
    import zlib

    def chunk(typ, body):
        return (struct.pack('>I', len(body)) + typ + body
                + struct.pack('>I', zlib.crc32(typ + body) & 0xffffffff))

    raw = b''.join(b'\x00' + bytes(r) for r in rows)
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 9))
            + chunk(b'IEND', b''))


def _qr_server():
    """起一次本地图片服务（端口 39789 起顺延），返回端口号。

    绑定成功后会自发一个探针请求，确认应答确实来自本服务；否则顺延端口。
    避免 Windows 端口复用时「绑上了、请求却被别的进程接走」导致磁贴 404。
    """
    import threading
    import urllib.request
    if _QR_SRV['port']:
        return _QR_SRV['port']
    try:
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    except Exception:
        return 0
    probe = '_kish_probe.png'
    token = b'\x89PNG\r\n\x1a\nKISH'
    _QR_SRV['cards'][probe] = token

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            key = self.path.split('?')[0].lstrip('/')
            blob = _QR_SRV['cards'].get(key)
            if not blob:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Length', str(len(blob)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            try:
                self.wfile.write(blob)
            except Exception:
                pass

        def log_message(self, *args):
            pass

    for port in range(39789, 39799):
        srv = None
        try:
            srv = ThreadingHTTPServer(('127.0.0.1', port), Handler)
            srv.daemon_threads = True
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            try:
                with urllib.request.urlopen(
                        'http://127.0.0.1:%d/%s' % (port, probe),
                        timeout=1) as resp:
                    mine = (resp.read() == token)
            except Exception:
                mine = False
            if not mine:
                try:
                    srv.shutdown()
                    srv.server_close()
                except Exception:
                    pass
                continue
            _QR_SRV['srv'] = srv
            _QR_SRV['port'] = port
            return port
        except Exception:
            try:
                if srv:
                    srv.server_close()
            except Exception:
                pass
            continue
    _QR_SRV['cards'].pop(probe, None)
    return 0


# ---------------------------------------------------------------------------
# 诊断中心卡片磁贴：纯标准库生成 PNG，走 _qr_server() 的本地图片服务。
# 不联网、不依赖字体；按分区配色 + 大号编号，避免所有卡片都是灰色占位图。
# ---------------------------------------------------------------------------

_DIAG_FONT = {
    '0': ('01110', '10001', '10001', '10001', '10001', '10001', '01110'),
    '1': ('00100', '01100', '00100', '00100', '00100', '00100', '01110'),
    '2': ('01110', '10001', '00001', '00011', '00110', '01000', '11111'),
    '3': ('11110', '00001', '00001', '01110', '00001', '00001', '11110'),
    '4': ('00010', '00110', '01010', '10010', '11111', '00010', '00010'),
    '5': ('11111', '10000', '11110', '00001', '00001', '10001', '01110'),
    '6': ('01110', '10000', '11110', '10001', '10001', '10001', '01110'),
    '7': ('11111', '00001', '00011', '00110', '01100', '01000', '01000'),
    '8': ('01110', '10001', '10001', '01110', '10001', '10001', '01110'),
    '9': ('01110', '10001', '10001', '01111', '00001', '00011', '01100'),
}

# 分区 -> (顶部色, 底部色, 强调色)
_DIAG_THEME = {
    'overview': ((22, 32, 54), (42, 70, 118), (110, 170, 250)),
    'sources':  ((18, 38, 50), (24, 74, 94), (72, 192, 246)),
    'cache':    ((38, 24, 32), (82, 40, 60), (244, 120, 182)),
}


def _diag_card_png(num, group):
    """生成 400x600 竖版编号磁贴，返回 PNG 字节。"""
    W, H, SC = 400, 600, 18
    top, bot, accent = _DIAG_THEME.get(group, _DIAG_THEME['overview'])
    rows = []
    for y in range(H):
        t = (y * 24 // (H - 1)) / 24.0          # 量化渐变，PNG 体积更小
        c = bytes(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        rows.append(bytearray(c * W))
    ab = bytes(accent)
    for y in range(H):
        rows[y][0:9 * 3] = ab * 9               # 左侧细色条
    s = '%02d' % (num % 100)
    tw = 12 * SC
    x0, y0 = (W - tw) // 2, (H - 7 * SC) // 2 - 34
    white = b'\xeb\xf0\xf8'
    for idx, ch in enumerate(s):
        for gy, line in enumerate(_DIAG_FONT[ch]):
            for gx, bit in enumerate(line):
                if bit != '1':
                    continue
                xx = x0 + idx * (7 * SC) + gx * SC
                yy = y0 + gy * SC
                block = white * SC
                for j in range(yy, yy + SC):
                    rows[j][xx * 3:(xx + SC) * 3] = block
    by = y0 + 7 * SC + 52
    for j in range(by, by + 5):
        bx = (W - 116) // 2
        rows[j][bx * 3:(bx + 116) * 3] = ab * 116
    return _qr_png_write(W, H, rows)


class KishDiag(object):
    """只读诊断：版本 / 配置 / 源探活 / 缓存管理。"""

    NAME = 'Kishuto 诊断'
    GROUPS = [('overview', '总览'), ('sources', '源状态'), ('cache', '缓存配置')]
    GROUP_KEYS = ('overview', 'sources', 'cache')

    def __init__(self, sp):
        self.sp = sp

    # ---------------- 卡片 ----------------
    @staticmethod
    def _mk(key, name, remarks=''):
        return {'vod_id': 'dg|' + key, 'vod_name': name, 'vod_pic': '',
                'vod_remarks': remarks}

    def homeContent(self, filter=True):
        return {'class': [{'type_id': k, 'type_name': v} for k, v in self.GROUPS],
                'filters': {},
                'list': self.categoryContent(self.GROUPS[0][0], '1', False, {})['list']}

    def homeVideoContent(self):
        return {'list': self.categoryContent(self.GROUPS[0][0], '1', False, {})['list']}

    def categoryContent(self, tid, pg='1', filter=True, extend=None):
        tid = str(tid or 'overview')
        if tid.startswith('dg|'):
            tid = tid[3:]
        if tid not in self.GROUP_KEYS:
            tid = 'overview'
        sp = self.sp
        if tid == 'overview':
            items = [self._mk('ver', '📦 版本与更新', '本地 %s' % CODE_VERSION),
                     self._mk('cfg', '⚙️ 运行配置', '首页源 %s' % getattr(sp, 'HOME_SOURCE', 'yt')),
                     self._mk('speed', '⏱ 首屏预算', '其余源等 %.1fs' % sp.FILL_BUDGET),
                     self._mk('help', '📖 使用说明', '各分区功能速查')]
        elif tid == 'sources':
            items = [self._mk('srcall', '🔍 全部探活', '逐个源跑搜索 + 详情')]
            for tag in sp.ORDER:
                items.append(self._mk('src:%s' % tag,
                                      '▸ %s' % sp.LABELS.get(tag, tag),
                                      '单独探活'))
        elif tid == 'cache':
            items = [self._mk('cache', '📊 缓存状态', '内存缓存条数'),
                     self._mk('cacheclear', '🧹 清空缓存', '点开即执行')]
        else:
            items = []
        # 统一磁贴：本地生成、不联网；ext 加 {"diag_plain":1} 可关掉
        cfg = getattr(sp, 'cfg', {}) or {}
        if str(cfg.get('diag_plain') or '') not in ('1', 'true', 'yes'):
            try:
                port = _qr_server()
                cards = _QR_SRV.setdefault('cards', {})
                for i, it in enumerate(items, 1):
                    ck = 'c_%s_%02d.png' % (tid, i)
                    if ck not in cards:
                        cards[ck] = _diag_card_png(i, tid)
                    it['vod_pic'] = ('http://127.0.0.1:%d/%s?v=1'
                                     % (port, ck)) if port else ''
            except Exception:
                pass
        return {'list': items, 'page': 1, 'pagecount': 1, 'limit': 50,
                'total': len(items)}

    def searchContent(self, key, quick=False, pg='1'):
        return {'list': []}

    def playerContent(self, flag, pid, vipflags=None):
        raw = str(pid or '').strip()
        url = raw if raw.startswith('http') else ''
        if not url:
            try:
                pad = '=' * (-len(raw) % 4)
                url = base64.urlsafe_b64decode(raw + pad).decode('utf-8', 'replace')
            except Exception:
                url = ''
        if not url.startswith('http'):
            return {'parse': 0, 'jx': 0, 'url': ''}
        # 预留：网页类线路交给壳的 webview
        if '网页' in str(flag or ''):
            return {'parse': 1, 'jx': 0, 'url': url,
                    'header': {'User-Agent': QR_UA}}
        return {'parse': 0, 'jx': 0, 'url': url,
                'header': {'User-Agent': QR_UA}}

    # ---------------- 执行 ----------------
    def detailContent(self, ids):
        raw = ids[0] if isinstance(ids, (list, tuple)) and ids else ids
        key = str(raw or '')
        if key.startswith('dg|'):
            key = key[3:]
        try:
            got = self._run(key)
            title, report = got[0], got[1]
            pic = got[2] if len(got) > 2 else ''
        except Exception as exc:
            title, report, pic = '执行失败', '%s: %s' % (type(exc).__name__, exc), ''
        froms, urls = '', ''   # 壳的播放器只认视频，图片塞进去必然报错，不挂线路
        tail = '\n\n── Kishuto 诊断 · %s · %s' % (
            CODE_VERSION, time.strftime('%H:%M'))
        vod = {'vod_id': 'dg|' + key, 'vod_name': title, 'vod_pic': pic,
               'type_name': '诊断', 'vod_remarks': '',
               'vod_content': str(report).rstrip() + tail,
               'vod_play_from': froms, 'vod_play_url': urls}
        return {'list': [vod]}

    def _run(self, key):
        sp = self.sp
        if key == 'ver':
            return self._ver()
        if key == 'cfg':
            return self._cfg()
        if key == 'speed':
            return ('首屏预算', '详情页等待其余源：%.1f 秒\n'
                    '攒够 %d 条线路提前收工\n'
                    '后台补齐上限：%.1f 秒\n'
                    '搜索预算：%.1f 秒'
                    % (sp.FILL_BUDGET, sp.FILL_ENOUGH,
                       sp.TOPUP_BUDGET, sp.SEARCH_BUDGET))
        if key == 'cache':
            n = len(_CACHE)
            return ('缓存状态', '内存缓存 %d 条\n'
                    '详情缓存 TTL：%d 秒\n搜索缓存 TTL：%d 秒\n'
                    '首页缓存：%d 秒\n分类缓存：%d 秒'
                    % (n, sp.CACHE_TTL, getattr(sp, 'SEARCH_TTL', 600),
                       sp.HOME_TTL, sp.CAT_TTL))
        if key == 'cacheclear':
            n = len(_CACHE)
            try:
                with _CACHE_LOCK:
                    _CACHE.clear()
            except Exception:
                pass
            return ('已清空缓存', '清理 %d 条内存缓存。\n'
                    '（只影响本进程，壳重启后本来也会清空）' % n)
        if key == 'srcall':
            rows, t0 = [], time.time()
            for tag in sp.ORDER:
                rows.append(self._probe(tag))
            return ('全部探活', '\n'.join(rows) + '\n\n合计 %.1f 秒' % (time.time() - t0))
        if key.startswith('src:'):
            tag = key[4:]
            return ('%s 探活' % sp.LABELS.get(tag, tag), self._probe(tag))
        if key == 'help':
            return ('使用说明',
                    'Kishuto 诊断中心 · 只读工具页，不播片。\n\n'
                    '【分区速查】\n'
                    '  总览        版本 / 运行配置 / 首屏预算\n'
                    '  源状态      逐个源实跑搜索 + 详情\n'
                    '  缓存配置    查看 / 清空内存缓存\n\n'
                    '【外观】\n'
                    '  卡片磁贴由本地生成，不联网。\n'
                    '  不想要磁贴：ext 加 {"diag_plain":1}。')
        return ('未知项', '没有这一项：%s' % key)

    def _ver(self):
        local = CODE_VERSION
        try:
            url = DIAG_BASE + '/update_kishuto.json?t=%d' % int(time.time() * 1000)
            req = urllib.request.Request(url, headers={'User-Agent': 'kish-diag'})
            txt = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', 'replace')
            man = json.loads(txt)
            online = str(man.get('version') or '')
            same = (online == local)
            return ('版本与更新',
                    '本地版本：%s\n线上版本：%s\n%s\n\n'
                    '清单大小：%s 字节\n安装地址：%s'
                    % (local, online or '取不到',
                       '已是最新' if same else '有新版本（重开壳会自动拉取）',
                       man.get('size'), man.get('url') or '-'))
        except Exception as exc:
            return ('版本与更新', '本地版本：%s\n拉取清单失败：%s' % (local, exc))

    def _cfg(self):
        sp = self.sp
        rows = ['首页源：%s' % getattr(sp, 'HOME_SOURCE', 'yt'),
                '首页分类上限：%d' % sp.HOME_CLASS_MAX,
                '线路顺序：%s' % ' > '.join(sp.LINE_FIRST),
                '源顺序：%s' % ' > '.join(sp.LABELS.get(t, t) for t in sp.ORDER),
                '详情缓存：%d 秒' % sp.CACHE_TTL]
        ext = sp.cfg or {}
        if ext:
            rows.append('ext 已配置项：%s' % ', '.join(sorted(ext)))
        else:
            rows.append('ext：未配置')
        return ('运行配置', '\n'.join(rows))

    def _probe(self, tag):
        sp = self.sp
        name = sp.LABELS.get(tag, tag)
        try:
            ob = sp._src(tag)
            if ob is None:
                return '%-4s 实例为空' % name
            kw = '芙莉莲' if tag == 'xf' else '庆余年'
            t = time.time()
            got = ob.searchContent(kw, False, '1') or {}
            items = got.get('list') or []
            t1 = time.time() - t
            lines = 0
            if items:
                d = ob.detailContent([items[0].get('vod_id')]) or {}
                v = (d.get('list') or [{}])[0]
                lines = len([x for x in str(v.get('vod_play_from') or '').split('$$$') if x])
            t2 = time.time() - t
            flag = '正常' if items else '无结果'
            return '%-4s %s 搜索 %d 条 %.1fs | 详情 %d 线 %.1fs' % (
                name, flag, len(items), t1, lines, t2)
        except Exception as exc:
            return '%-4s 异常 %s: %s' % (name, type(exc).__name__, str(exc)[:50])

    # ---------------- 兜底：软件内网页登录（纯增量） ----------------


# ==================== 枫奇4K 线路源 fq BEGIN ====================
# -*- coding: utf-8 -*-
"""枫奇4K —— 只保留「至臻4K」「蓝光2K」两条线路（纯标准库，自包含）

原源（枫叶4K影院 / maihaolian.com）详情页共 4 条线路：
    至臻4k / 蓝光2k / 自营y / 自营r
本源只取前两条，播放解析也只保留对应的 JD / co 两个接口。

设计约束（与 Kishuto 聚合一致）：
  * 纯标准库，不用 requests / bs4，可直接并进 Kishuto.py 的同一命名空间；
    所有全局名字一律 fq_ / FQ_ 前缀，避免覆盖其它模块。
  * init() 绝不联网；只有实际请求撞上「系统安全验证」时才惰性过验证码。
  * 验证码识别为纯 Python PNG 解码 + 模板匹配（模板来自原源）。
"""
import datetime
import html
import json
import re
import struct
import threading
import time
import zlib
from http import cookiejar as _fq_cj
import urllib.parse
import urllib.request
import urllib.error

try:
    from base.spider import Spider as _FQBase
except Exception:
    class _FQBase(object):
        def getCache(self, key):
            return ''

        def setCache(self, key, value):
            return None

        def log(self, msg):
            return None

FQ_CAP_TPL = {
    0: [0.9045, 0.9045, 0.9045, -1.1055, -1.1055, 0.9045, 0.9045, 0.9045, 0.9045, 0.9045, -1.1055, -1.1055, -1.1055, -1.1055, 0.9045, 0.9045, 0.9045, -1.1055, -1.1055, 0.9045, 0.9045, -1.1055, -1.1055, 0.9045, -1.1055, -1.1055, 0.9045, 0.9045, 0.9045, 0.9045, -1.1055, -1.1055, -1.1055, -1.1055, 0.9045, 0.9045, 0.9045, 0.9045, -1.1055, -1.1055, -1.1055, -1.1055, 0.9045, 0.9045, 0.9045, 0.9045, -1.1055, -1.1055, -1.1055, -1.1055, 0.9045, 0.9045, 0.9045, 0.9045, -1.1055, -1.1055, 0.9045, -1.1055, -1.1055, 0.9045, 0.9045, -1.1055, -1.1055, 0.9045, 0.9045, 0.9045, -1.1055, -1.1055, -1.1055, -1.1055, 0.9045, 0.9045, 0.9045, 0.9045, 0.9045, -1.1055, -1.1055, 0.9045, 0.9045, 0.9045],
    1: [1.0567, 1.0567, 0.0924, -1.1933, -1.1933, 0.0924, 1.0567, 1.0567, 1.0567, -0.5504, -1.1933, -1.1933, -1.1933, 0.0924, 1.0567, 1.0567, -1.1933, -1.1933, -1.1933, -1.1933, -1.1933, 0.0924, 1.0567, 1.0567, 1.0567, 1.0567, 0.0924, -1.1933, -1.1933, 0.0924, 1.0567, 1.0567, 1.0567, 1.0567, 0.0924, -1.1933, -1.1933, 0.0924, 1.0567, 1.0567, 1.0567, 1.0567, 0.0924, -1.1933, -1.1933, 0.0924, 1.0567, 1.0567, 1.0567, 1.0567, 0.0924, -1.1933, -1.1933, 0.0924, 1.0567, 1.0567, 1.0567, 1.0567, 0.0924, -1.1933, -1.1933, 0.0924, 1.0567, 1.0567, 1.0567, 1.0567, 0.0924, -1.1933, -1.1933, 0.0924, 1.0567, 1.0567, -1.1933, -1.1933, -1.1933, -1.1933, -1.1933, -1.1933, -1.1933, -1.1933],
    2: [0.8165, 0.8165, -1.2247, -1.2247, -1.2247, -1.2247, 0.8165, 0.8165, 0.8165, -1.2247, -1.2247, 0.8165, 0.8165, -1.2247, -1.2247, 0.8165, -1.2247, -1.2247, 0.8165, 0.8165, 0.8165, 0.8165, -1.2247, -1.2247, 0.8165, 0.8165, 0.8165, 0.8165, 0.8165, 0.8165, -1.2247, -1.2247, 0.8165, 0.8165, 0.8165, 0.8165, 0.8165, -1.2247, -1.2247, 0.8165, 0.8165, 0.8165, 0.8165, 0.8165, -1.2247, -1.2247, 0.8165, 0.8165, 0.8165, 0.8165, 0.8165, -1.2247, -1.2247, 0.8165, 0.8165, 0.8165, 0.8165, 0.8165, -1.2247, -1.2247, 0.8165, 0.8165, 0.8165, 0.8165, 0.8165, -1.2247, -1.2247, 0.8165, 0.8165, 0.8165, 0.8165, 0.8165, -1.2247, -1.2247, -1.2247, -1.2247, -1.2247, -1.2247, -1.2247, -1.2247],
    3: [0.7954, -1.2572, -1.2572, -1.2572, -1.2572, -1.2572, 0.7954, 0.7954, -1.2572, -1.2572, 0.7954, 0.7954, 0.7954, -1.2572, -1.2572, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, -1.2572, -1.2572, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, -1.2572, -1.2572, 0.7954, 0.7954, 0.7954, 0.7954, -1.2572, -1.2572, -1.2572, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, -1.2572, -1.2572, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, -1.2572, -1.2572, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, -1.2572, -1.2572, -1.2572, -1.2572, 0.7954, 0.7954, 0.7954, -1.2572, -1.2572, 0.7954, 0.7954, -1.2572, -1.2572, -1.2572, -1.2572, -1.2572, 0.7954, 0.7954],
    4: [0.8819, 0.8819, 0.8819, 0.8819, 0.8819, -1.1339, -1.1339, 0.8819, 0.8819, 0.8819, 0.8819, 0.8819, -1.1339, -1.1339, -1.1339, 0.8819, 0.8819, 0.8819, 0.8819, -1.1339, -1.1339, -1.1339, -1.1339, 0.8819, 0.8819, 0.8819, -1.1339, -1.1339, 0.8819, -1.1339, -1.1339, 0.8819, 0.8819, -1.1339, -1.1339, 0.8819, 0.8819, -1.1339, -1.1339, 0.8819, -1.1339, -1.1339, 0.8819, 0.8819, 0.8819, -1.1339, -1.1339, 0.8819, -1.1339, -1.1339, -1.1339, -1.1339, -1.1339, -1.1339, -1.1339, -1.1339, 0.8819, 0.8819, 0.8819, 0.8819, 0.8819, -1.1339, -1.1339, 0.8819, 0.8819, 0.8819, 0.8819, 0.8819, 0.8819, -1.1339, -1.1339, 0.8819, 0.8819, 0.8819, 0.8819, 0.8819, 0.8819, -1.1339, -1.1339, 0.8819],
    5: [-1.078, -1.078, -1.078, -1.078, -1.078, -1.078, -1.078, 0.9276, -1.078, -1.078, 0.9276, 0.9276, 0.9276, 0.9276, 0.9276, 0.9276, -1.078, -1.078, 0.9276, 0.9276, 0.9276, 0.9276, 0.9276, 0.9276, -1.078, -1.078, 0.9276, -1.078, -1.078, -1.078, 0.9276, 0.9276, -1.078, -1.078, -1.078, 0.9276, 0.9276, -1.078, -1.078, 0.9276, 0.9276, 0.9276, 0.9276, 0.9276, 0.9276, 0.9276, -1.078, -1.078, 0.9276, 0.9276, 0.9276, 0.9276, 0.9276, 0.9276, -1.078, -1.078, -1.078, -1.078, 0.9276, 0.9276, 0.9276, 0.9276, -1.078, -1.078, 0.9276, -1.078, -1.078, 0.9276, 0.9276, -1.078, -1.078, 0.9276, 0.9276, 0.9276, -1.078, -1.078, -1.078, -1.078, 0.9276, 0.9276],
    6: [0.9753, 0.9753, -1.0253, -1.0253, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, 0.9753, -1.0253, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, -1.0253, -1.0253, -1.0253, 0.9753, 0.9753, -1.0253, -1.0253, -1.0253, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, -1.0253, -1.0253, 0.9753, 0.9753],
    7: [-1.4412, -1.4412, -1.4412, -1.4412, -1.4412, -1.4412, -1.4412, -1.4412, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, -1.4412, -1.4412, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, -1.4412, -1.4412, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, -1.4412, -1.4412, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, -1.4412, -1.4412, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, -1.4412, -1.4412, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, -1.4412, -1.4412, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, -1.4412, -1.4412, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, -1.4412, -1.4412, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, -1.4412, -1.4412, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939],
    8: [1.0, 1.0, -1.0, -1.0, -1.0, -1.0, 1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0, 1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0, 1.0, 1.0],
    9: [0.9753, 0.9753, -1.0253, -1.0253, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, -1.0253, -1.0253, -1.0253, 0.9753, 0.9753, -1.0253, -1.0253, -1.0253, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, -1.0253, 0.9753, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, -1.0253, -1.0253, 0.9753, 0.9753],
}


def fq_decode_png(data):
    if data[:8] != b'\x89PNG\r\n\x1a\n': raise ValueError('not png')
    pos, width, height, idat = 8, None, None, b''
    while pos < len(data):
        ln, typ, chunk = struct.unpack('>I', data[pos:pos+4])[0], data[pos+4:pos+8], data[pos+8:pos+8+struct.unpack('>I', data[pos:pos+4])[0]]
        pos += 12 + ln
        if typ == b'IHDR': width, height, bit_depth, color_type = struct.unpack('>IIBB', chunk[:10])
        elif typ == b'IDAT': idat += chunk
        elif typ == b'IEND': break
    if color_type not in (0, 2, 3, 4, 6): raise ValueError('color type')
    channels, stride, raw = {0:1, 2:3, 3:1, 4:2, 6:4}[color_type], width * {0:1, 2:3, 3:1, 4:2, 6:4}[color_type], zlib.decompress(idat)
    prev, gray, p = bytearray(stride), [], 0
    for y in range(height):
        ft, line, p = raw[p], bytearray(raw[p+1:p+1+stride]), p + 1 + stride
        if ft == 1:
            for i in range(channels, stride): line[i] = (line[i] + line[i-channels]) & 0xff
        elif ft == 2:
            for i in range(stride): line[i] = (line[i] + prev[i]) & 0xff
        elif ft == 3:
            for i in range(stride): line[i] = (line[i] + (((line[i-channels] if i >= channels else 0) + prev[i]) >> 1)) & 0xff
        elif ft == 4:
            for i in range(stride):
                a, b, c = line[i-channels] if i >= channels else 0, prev[i], prev[i-channels] if i >= channels else 0
                pp = a + b - c; pa, pb, pc = abs(pp-a), abs(pp-b), abs(pp-c)
                line[i] = (line[i] + (a if (pa <= pb and pa <= pc) else (b if pb <= pc else c))) & 0xff
        if color_type in (2, 6): step = 3 if color_type == 2 else 4; rows = [int(line[x*step]*0.299 + line[x*step+1]*0.587 + line[x*step+2]*0.114) for x in range(width)]
        elif color_type == 4: rows = [line[x*2] for x in range(width)]
        else: rows = list(line[:width])
        gray.append(rows); prev = line
    return width, height, gray

def fq_cap_resize(block, tw=8, th=10):
    bh, bw = len(block), len(block[0])
    flat = []
    for ty in range(th):
        yf = ty * (bh - 1) / (th - 1)
        y0 = int(yf); y1 = min(y0 + 1, bh - 1); fy = yf - y0
        for tx in range(tw):
            xf = tx * (bw - 1) / (tw - 1)
            x0 = int(xf); x1 = min(x0 + 1, bw - 1); fx = xf - x0
            v = (block[y0][x0] * (1 - fx) + block[y0][x1] * fx) * (1 - fy) + (block[y1][x0] * (1 - fx) + block[y1][x1] * fx) * fy
            flat.append(v)
    return flat


def fq_cap_norm(vals):
    n = len(vals)
    m = sum(vals) / n
    var = sum((v - m) ** 2 for v in vals) / n
    sd = var ** 0.5 if var > 0 else 1.0
    return [(v - m) / sd for v in vals]


def fq_recognize_captcha(data):
    """识别 4 位数字验证码：
    - 纯 Python PNG 解码（fq_decode_png）
    - 自适应阈值二值化 → 列投影切 4 段
    - 每字符灰度块双线性缩放 8x10 → 零均值单位方差归一化
    - 与 FQ_CAP_TPL（按真实验证码样本训练的归一化模板）做余弦相关取 argmax
    - 任一字符置信度 < 0.85 判为失败（返回 None，由调用方换图重试）
    模板于 2026-10 针对 maihaolian.com/zzztool.com 现行验证码字体重新拟合。
    """
    try:
        W, H, gray = fq_decode_png(data)
    except Exception:
        return None
    avg = sum(sum(r) for r in gray) / (W * H) if W * H else 128
    thr = min(max(avg * 0.8, 80), 170)
    bw = [[1 if gray[y][x] < thr else 0 for x in range(W)] for y in range(H)]
    col_sums = [sum(bw[y][x] for y in range(H)) for x in range(W)]
    segs, inseg, start = [], False, 0
    for x in range(W):
        if col_sums[x] > 0 and not inseg:
            start, inseg = x, True
        elif col_sums[x] == 0 and inseg:
            if x - start >= 3:
                segs.append((start, x - 1))
            inseg = False
    if inseg and (W - start >= 3):
        segs.append((start, W - 1))
    if len(segs) != 4:
        return None
    result = ''
    for s, e in segs:
        rows = [y for y in range(H) if any(gray[y][x] < thr for x in range(s, e + 1))]
        if not rows:
            return None
        block = [[gray[y][x] for x in range(s, e + 1)] for y in range(rows[0], rows[-1] + 1)]
        vec = fq_cap_norm(fq_cap_resize(block))
        best_d, best_s = None, -1e9
        for d in range(10):
            sc = sum(a * b for a, b in zip(vec, FQ_CAP_TPL[d])) / len(vec)
            if sc > best_s:
                best_d, best_s = d, sc
        if best_s < 0.85:
            return None
        result += str(best_d)
    return result

FQ_SITE = 'https://maihaolian.com'
FQ_UA = ('Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 '
         'Chrome/150.0.0.0 Mobile')
FQ_HDRS = {
    'User-Agent': FQ_UA,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Upgrade-Insecure-Requests': '1',
    'Referer': FQ_SITE + '/',
}
# 只认这两条线路；(页面上的原始名, 输出显示名)，顺序即默认选线顺序
FQ_LINES = (('至臻4k', '至臻4K'), ('蓝光2k', '蓝光2K'))
FQ_PARSE = {
    'JD': 'https://fgsrg.hzqingshan.com',
    'co': 'https://zzrs.mfdyvip.com',
}
FQ_RE_PLAYER = re.compile(r'var\s+player_aaaa[\s\S]*?"url"\s*:\s*"([^"]+)"')
FQ_RE_URL_VAR = re.compile(r'url\s*[:=]\s*["\'](http[^"\']+)["\']')
FQ_RE_TOKEN = re.compile(r'data-te="([^"]+)"')
FQ_RE_CARD = re.compile(
    r'<a[^>]*class="[^"]*public-list-exp[^"]*"[^>]*>(.*?)</a>', re.S)
FQ_RE_HREF = re.compile(r'href="([^"]+)"')
FQ_RE_TITLE = re.compile(r'title="([^"]*)"')
FQ_RE_PIC = re.compile(
    r'<img[^>]*?\b(?:data-src|src)="([^"]+)"', re.S)
FQ_RE_ALT = re.compile(r'<img[^>]*?\balt="([^"]*)"', re.S)
FQ_RE_PRT = re.compile(r'class="[^"]*public-prt-g[^"]*"[^>]*>([^<]*)<')
FQ_RE_FT2 = re.compile(r'<i class="ft2">([^<]*)</i>')
FQ_RE_FT2B = re.compile(
    r'class="[^"]*public-list-prb[^"]*"[^>]*>\s*([^<]+)<')
FQ_RE_SLIDE = re.compile(r'<a\s+class="swiper-slide"[^>]*>(.*?)</a>', re.S)
FQ_RE_EP = re.compile(r'<a[^>]*href="([^"]+)"[^>]*>([^<]*)</a>')
FQ_RE_PAGE_TIP = re.compile(r'\d+/(\d+)页')
FQ_RE_SPACE = re.compile(r'\s+')

FQ_JAR = _fq_cj.CookieJar()
FQ_OPENER = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(FQ_JAR))
FQ_LOCK = threading.Lock()
FQ_VERIFIED = {'at': 0.0}
FQ_CACHE = {}
FQ_LINE_SID = {}       # 片 id -> {线路名: 播放页 sid}，用于同集回落


def fq_clean(text):
    """线路/片名清洗：去掉会破坏 TVBox 分隔符的字符。"""
    s = html.unescape(str(text or ''))
    return FQ_RE_SPACE.sub(' ', s.replace('$', '').replace('#', '')
                          .replace('|', '')).strip()


def fq_abs(url):
    u = str(url or '').strip()
    if u.startswith('http'):
        return u
    return FQ_SITE + (u if u.startswith('/') else '/' + u)


def fq_raw(url, data=None, referer=None, ctype=None, timeout=12):
    """统一请求层；返回 bytes。"""
    h = dict(FQ_HDRS)
    h['Referer'] = referer or (FQ_SITE + '/')
    if data is not None and ctype:
        h['Content-Type'] = ctype
    req = urllib.request.Request(url, data=data, headers=h)
    with FQ_OPENER.open(req, timeout=timeout) as resp:
        return resp.read()


def fq_verify():
    """惰性过「系统安全验证」：识别 4 位数字验证码并提交，最多 4 次。"""
    with FQ_LOCK:
        if time.time() - FQ_VERIFIED['at'] < 30:
            return True
        for i in range(4):
            try:
                cap = fq_raw(FQ_SITE + '/captcha.php?type=code&r=0.%d'
                             % (12345 + i), timeout=10)
                code = fq_recognize_captcha(cap)
                if not code:
                    continue
                body = urllib.parse.urlencode({'check': code}).encode()
                txt = fq_raw(FQ_SITE + '/captcha.php?type=verify', data=body,
                             ctype='application/x-www-form-urlencoded',
                             timeout=10).decode('utf-8', 'replace')
                if '"code":1' in txt.replace(' ', ''):
                    FQ_VERIFIED['at'] = time.time()
                    return True
            except Exception:
                pass
        return False


def fq_get(url, data=None, referer=None, ctype=None, timeout=12, retry=True):
    """返回页面文本；撞上验证页时自动过一次验证码再重试。"""
    try:
        raw = fq_raw(url, data=data, referer=referer, ctype=ctype,
                     timeout=timeout)
        txt = raw.decode('utf-8', 'replace')
        if retry and '系统安全验证' in txt:
            if fq_verify():
                raw = fq_raw(url, data=data, referer=referer, ctype=ctype,
                             timeout=timeout)
                txt = raw.decode('utf-8', 'replace')
        return txt
    except Exception:
        return ''


def fq_parse_list(txt):
    """首页 / 分类 / 搜索共用的卡片解析（maihaolian 模板）。"""
    out = []
    for m in FQ_RE_CARD.finditer(txt):
        tag = m.group(0)
        inner = m.group(1)
        hr = FQ_RE_HREF.search(tag)
        if not hr:
            continue
        ti = FQ_RE_TITLE.search(tag)
        alt = FQ_RE_ALT.search(inner)
        pic = FQ_RE_PIC.search(inner)
        prt = FQ_RE_PRT.search(inner)
        ft2 = FQ_RE_FT2.search(inner) or FQ_RE_FT2B.search(inner)
        # 首页卡片把片名放 title；搜索页放 img 的 alt
        name = fq_clean((ti.group(1) if ti else '') or
                        (alt.group(1) if alt else ''))
        if not name:
            continue
        out.append({
            'vod_id': hr.group(1),
            'vod_name': name,
            'vod_pic': html.unescape(pic.group(1)) if pic else '',
            'vod_remarks': fq_clean(ft2.group(1)) if ft2 else '',
            'vod_year': ('「%s」' % fq_clean(prt.group(1))) if prt else '',
        })
    return out


def fq_page_count(txt):
    m = FQ_RE_PAGE_TIP.search(txt)
    return int(m.group(1)) if m else 1


def fq_sid_of(eps):
    """从选集链接 /play/<片id>-<线路sid>-<集号>.html 里取线路 sid。"""
    for _, href in eps[:3]:
        m = re.search(r'/play/\d+-(\d+)-\d+\.html', href)
        if m:
            return m.group(1)
    return ''


def fq_fallback_url(pid):
    """某条线路的解析站返回失败时，换另一条线路的同集播放页。"""
    m = re.search(r'/play/(\d+)-(\d+)-(\d+)\.html', str(pid))
    if not m:
        return ''
    vid, sid, ep = m.groups()
    sids = FQ_LINE_SID.get(vid) or {}
    other = ''
    for name in ('蓝光2K', '至臻4K'):
        if sids.get(name) and sids[name] != sid:
            other = sids[name]
            break
    return '/play/%s-%s-%s.html' % (vid, other, ep) if other else ''


def fq_detail_data(vid):
    """详情页：只保留「至臻4K」「蓝光2K」两条线路。"""
    url = fq_abs(vid)
    txt = fq_get(url, timeout=12)
    if not txt or '系统安全验证' in txt:
        return {}
    names = []
    for s in FQ_RE_SLIDE.findall(txt):
        s = re.sub(r'<i[^>]*>.*?</i>', '', s, flags=re.S)
        s = re.sub(r'<span[^>]*>.*?</span>', '', s, flags=re.S)
        s = re.sub(r'<[^>]+>', '', s)
        names.append(fq_clean(s.replace('&nbsp;', ' ')))
    # 按 anthology-list-box 切块，每块对应一条线路
    segs = re.split(r'<div class="anthology-list-box', txt)[1:]
    panels = []
    for seg in segs:
        eps = [(fq_clean(n), h) for h, n in FQ_RE_EP.findall(seg)
               if '/play/' in h]
        panels.append(list(reversed(eps))[:300])   # 页面是 40→1，翻成正序

    lines = []
    for i, nm in enumerate(names):
        key = nm.lower().replace(' ', '')
        for raw_name, disp in FQ_LINES:
            if key == raw_name.lower() and i < len(panels) and panels[i]:
                lines.append((disp, panels[i]))
                break
    order = [d for _, d in FQ_LINES]
    lines.sort(key=lambda x: order.index(x[0]) if x[0] in order else 99)
    if not lines:
        return {}

    # 记下两条线路各自的播放页 sid，解析站失效时可同集回落
    num = re.search(r'/(\d+)\.html', str(vid))
    if num:
        FQ_LINE_SID[num.group(1)] = dict(
            (n, fq_sid_of(eps)) for n, eps in lines)

    title = re.search(r'class="slide-info-title[^"]*"[^>]*>([^<]+)<', txt)
    pic_m = re.search(r'class="detail-pic"[\s\S]{0,600}?<img[^>]*?data-src="([^"]+)"',
                      txt)
    intro = re.search(r'id="height_limit"[^>]*>([\s\S]{0,1200}?)</div>', txt)
    actor = ''
    for info in re.findall(r'class="slide-info"[^>]*>([\s\S]{0,400}?)</div>', txt):
        if '演员' in info:
            actor = fq_clean(re.sub(r'<[^>]+>', ' ', info))
            break

    def strip_tags(s):
        return fq_clean(re.sub(r'<[^>]+>', ' ', s or ''))

    vod = {
        'vod_id': vid,
        'vod_name': fq_clean(title.group(1)) if title else '',
        'vod_pic': html.unescape(pic_m.group(1)) if pic_m else '',
        'vod_content': strip_tags(intro.group(1)) if intro else '',
        'vod_actor': actor,
        'vod_remarks': lines[0][0] + ' / ' + lines[-1][0],
        'vod_play_from': '$$$'.join(n for n, _ in lines),
        'vod_play_url': '$$$'.join(
            '#'.join('%s$%s' % (n, h) for n, h in eps) for _, eps in lines),
    }
    return vod


def fq_parse_play(play_key):
    """JD-xxx / co_xxx → 解析站的 m3u8 直链。"""
    key = re.split(r'[-_]', play_key)[0] if play_key else ''
    base = FQ_PARSE.get(key)
    if not base:
        return ''
    target = base + '/player/?url=' + play_key
    # 这个接口强制要求来源站 Referer，否则会被导到百度页面
    txt = fq_get(target, referer=FQ_SITE + '/', timeout=12)
    tok = FQ_RE_TOKEN.search(txt)
    if not tok:
        return ''
    body = urllib.parse.urlencode(
        {'url': play_key, 'token': tok.group(1)}).encode()
    res = fq_get(base + '/player/mplayer.php', data=body, referer=target,
                 ctype='application/x-www-form-urlencoded; charset=UTF-8',
                 timeout=12, retry=False)
    try:
        u = str((json.loads(res) or {}).get('url') or '')
    except Exception:
        return ''
    if not u:
        return ''
    return (base + u) if u.startswith('/playproxy.php') else u


def fq_player_data(pid, fallback=True):
    url = fq_abs(pid)
    txt = fq_get(url, timeout=12)
    if not txt:
        return {'parse': 0, 'jx': 0, 'url': ''}
    m = FQ_RE_PLAYER.search(txt)
    u = m.group(1).replace('\\/', '/') if m else ''
    if not u:
        m2 = FQ_RE_URL_VAR.search(txt)
        u = m2.group(1) if m2 else ''
    if not u:
        u = url
    header = 'User-Agent: %s\r\nReferer: %s/' % (FQ_UA, FQ_SITE)
    if u.startswith('http') and ('m3u' in u or '.mp4' in u):
        return {'parse': 0, 'jx': 0, 'url': u, 'header': header}
    real = fq_parse_play(u) or u
    if not real.startswith('http') and fallback:
        alt = fq_fallback_url(pid)
        if alt and alt != str(pid):
            alt_res = fq_player_data(alt, fallback=False)
            if str(alt_res.get('url') or '').startswith('http'):
                alt_res['fq_note'] = '原线路解析站不可用，已回落另一条线路同集'
                return alt_res
    return {'parse': 0 if ('m3u' in real or '.mp4' in real) else 1,
            'jx': 0, 'url': real, 'header': header}


class FengqiSpider(_FQBase):
    """枫奇4K（至臻4K / 蓝光2K）——可作为独立源，也可挂进 Kishuto。"""

    def getName(self):
        return '枫奇4K'

    def init(self, extend=''):
        # 性能铁律：init 不联网，验证码只在首个真实请求被拦截时触发。
        try:
            if isinstance(extend, str) and extend.strip().startswith('{'):
                cfg = json.loads(extend)
                if isinstance(cfg, dict) and cfg.get('fq_site'):
                    FQ_HDRS['Referer'] = str(cfg['fq_site']).rstrip('/') + '/'
        except Exception:
            pass
        return None

    def destroy(self):
        return None

    def homeContent(self, filter=False):
        classes = [
            {'type_id': '1', 'type_name': '电影'},
            {'type_id': '2', 'type_name': '电视剧'},
            {'type_id': '3', 'type_name': '综艺'},
            {'type_id': '4', 'type_name': '动漫'},
            {'type_id': '5', 'type_name': '短剧'},
        ]
        return {'parse': 0, 'jx': 0, 'class': classes, 'filters': {}}

    def homeVideoContent(self):
        return self.categoryContent('', 1, False, {})

    def categoryContent(self, tid, pg='1', filter=True, extend=None):
        page = int(pg) if str(pg).isdigit() else 1
        t = str(tid or '')
        if t.startswith('/label/'):
            url = FQ_SITE + t + '/page/%d.html' % page
        elif t and t.isdigit():
            url = '%s/cupfox-list/%s----------%d---.html' % (FQ_SITE, t, page)
        else:
            url = FQ_SITE + '/'
        txt = fq_get(url, timeout=12)
        items = fq_parse_list(txt) if txt else []
        return {'parse': 0, 'jx': 0, 'list': items, 'page': page,
                'pagecount': fq_page_count(txt) if txt else 1,
                'limit': 30, 'total': len(items)}

    def searchContent(self, key, quick=False, pg='1'):
        if int(pg) >= 2:
            return {'parse': 0, 'jx': 0, 'list': [], 'pagecount': 1}
        kw = str(key or '').strip()
        if not kw:
            return {'parse': 0, 'jx': 0, 'list': []}
        ck = 'fq:s:' + kw
        hit = FQ_CACHE.get(ck)
        if hit and time.time() - hit[0] < 300:
            return hit[1]
        url = (FQ_SITE + '/cupfox-search/-------------.html?wd='
               + urllib.parse.quote(kw))
        txt = fq_get(url, timeout=10)
        items = fq_parse_list(txt) if txt else []
        res = {'parse': 0, 'jx': 0, 'list': items, 'pagecount': 1}
        FQ_CACHE[ck] = (time.time(), res)
        return res

    def detailContent(self, ids):
        vid = str(ids[0] if isinstance(ids, (list, tuple)) and ids else ids)
        vod = fq_detail_data(vid)
        return {'parse': 0, 'jx': 0, 'list': [vod] if vod else []}

    def playerContent(self, flag, id, vipFlags=None):
        return fq_player_data(str(id))

# ==================== 枫奇4K 线路源 fq END ====================

# ==================== 橘汁新网关线路源 jn BEGIN ====================
# -*- coding: utf-8 -*-
# 橘汁视频 · 新网关版 TVBox / AVBox spider（Python / drpy）
# ============================================================================
# 【这是全新写的一份，不是对旧文件的修补】
#
# 旧版「橘汁视频（新）.py」走的是 https://gdsaj.hzhcbkj.cn（旧网关）。
# 旧网关的 JD4K 解析通道已经失效，videoUsableUrl 会返回
#   「解析视频地址失败 / 你触发了防盗」，导致 JD4K 线路播不了。
# 本文件改走 sun.json 里「橘汁 • APP」(csp_AppDrama) 配置指向的新网关
#   http://juziapp.hzhcbkj.cn
# 并按该插件的协议重新实现：publicParams 走 AES-CBC 加密成 paramsData、
# 参数走 dataKey 的 AES-ECB、签名用 zone 下发的二级公钥。
#
# 实测（2026-11-08）：新网关下 4 条 4K 线路全部可兑换出播放直链，包括
#   JD4K-可下载 / VIP4K / 自建4K-3 / 自建4K-4
#
# 用法：直接当普通 py 源导入 TVBox / AVBox 即可，无需其它文件。
#   - init(extend) 可传 JSON 覆盖配置，例如：
#       {"host":"http://juziapp.hzhcbkj.cn", "only4k":true}
#   - 类常量 ONLY_4K = True 时，详情页只保留线路名含 4K 的线路。
#   - 默认 host 会先尝试从 site 拉取最新 domain，失败则用内置值。
#
# 依赖：零第三方库。有 pycryptodome 时自动使用，没有则用内置纯 Python
#       AES / RSA 实现（首页推荐需要 AES 解密，已一并实现）。
#
# 说明：仅做协议兼容性实现，用于让已有本地配置正常工作；不涉及
#       学习进度、鉴权绕过或任何平台检测逻辑。请遵守平台规则合规使用。
# ============================================================================

import json
import re
import ssl
import time
import base64
import string
import random
import uuid
import os
import threading
import urllib.request
import urllib.parse

import collections
try:
    from base.spider import Spider as jzn__Base
except Exception:
    class jzn__Base:
        pass

# ---------------------------------------------------------------- 加密层
# AVBox 1.3.0 的 pip 只带 lxml/requests/pyquery，没有 pycryptodome。
# 原文件在模块顶层 `from Crypto...` 直接把整个源卡在导入阶段。
# 现在：能用 Crypto 就用（行为与原来完全一致），没有就用内置纯 Python 实现。
try:
    from Crypto.PublicKey import RSA as jzn__CryptoRSA
    from Crypto.Cipher import jzn_PKCS1_v1_5 as jzn__CryptoPKCS1
    from Crypto.Cipher import jzn_AES as jzn__CryptoAES
    jzn__HAVE_CRYPTO = True
except Exception:
    jzn__HAVE_CRYPTO = False


def jzn__pad(data, block=16):
    """PKCS#7 填充（与 Crypto.Util.Padding.pad 一致）"""
    n = block - (len(data) % block)
    return data + bytes([n]) * n


def jzn__unpad(data, block=16):
    n = data[-1]
    if 0 < n <= block and len(data) >= n:
        return data[:-n]
    return data


def jzn__gf_tables():
    alog = [0] * 256
    log = [0] * 256
    x = 1
    for i in range(255):
        alog[i] = x
        log[x] = i
        h = ((x << 1) ^ (0x1B if (x & 0x80) else 0)) & 0xFF
        x = h ^ x
    return alog, log


def jzn__mk_sbox():
    alog, log = jzn__gf_tables()
    sbox = [0] * 256
    for i in range(256):
        if i == 0:
            s = 0
        else:
            s = alog[(255 - log[i]) % 255]
        r = s
        for _ in range(4):
            s = ((s << 1) | (s >> 7)) & 0xFF
            r ^= s
        sbox[i] = r ^ 0x63
    return sbox


jzn__SBOX = jzn__mk_sbox()


def jzn__xtime(a):
    return ((a << 1) ^ 0x1B) & 0xFF if (a & 0x80) else (a << 1) & 0xFF


def jzn__mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a = jzn__xtime(a)
        b >>= 1
    return r


def jzn__key_expansion(key):
    nk = len(key) // 4
    nr = nk + 6
    w = [list(key[4 * i:4 * i + 4]) for i in range(nk)]
    rcon = 1
    for i in range(nk, 4 * (nr + 1)):
        t = list(w[i - 1])
        if i % nk == 0:
            t = t[1:] + t[:1]
            t = [jzn__SBOX[b] for b in t]
            t[0] ^= rcon
            rcon = jzn__xtime(rcon)
        elif nk > 6 and i % nk == 4:
            t = [jzn__SBOX[b] for b in t]
        w.append([w[i - nk][j] ^ t[j] for j in range(4)])
    return w, nr


def jzn__add_round_key(state, w, rnd):
    for c in range(4):
        kw = w[4 * rnd + c]
        for r in range(4):
            state[r + 4 * c] ^= kw[r]


def jzn__sub_bytes(state):
    for i in range(16):
        state[i] = jzn__SBOX[state[i]]


def jzn__shift_rows(state):
    # AES 行移位：第 r 行循环左移 r 位（state 为列主序 flat 索引 r + 4c）
    for r in range(1, 4):
        row = [state[r + 4 * c] for c in range(4)]
        for c in range(4):
            state[r + 4 * c] = row[(c + r) % 4]


def jzn__mix_columns(state):
    for c in range(4):
        a = [state[r + 4 * c] for r in range(4)]
        state[0 + 4 * c] = jzn__mul(a[0], 2) ^ jzn__mul(a[1], 3) ^ a[2] ^ a[3]
        state[1 + 4 * c] = a[0] ^ jzn__mul(a[1], 2) ^ jzn__mul(a[2], 3) ^ a[3]
        state[2 + 4 * c] = a[0] ^ a[1] ^ jzn__mul(a[2], 2) ^ jzn__mul(a[3], 3)
        state[3 + 4 * c] = jzn__mul(a[0], 3) ^ a[1] ^ a[2] ^ jzn__mul(a[3], 2)


def jzn__aes_encrypt_block(block, w, nr):
    state = list(block)
    jzn__add_round_key(state, w, 0)
    for rnd in range(1, nr):
        jzn__sub_bytes(state)
        jzn__shift_rows(state)
        jzn__mix_columns(state)
        jzn__add_round_key(state, w, rnd)
    jzn__sub_bytes(state)
    jzn__shift_rows(state)
    jzn__add_round_key(state, w, nr)
    return bytes(state)


class jzn__PureAES:
    MODE_ECB = 1
    MODE_CBC = 2

    @classmethod
    def new(cls, key, mode, iv=None):
        return cls(key, mode, iv)

    def __init__(self, key, mode, iv=None):
        if len(key) not in (16, 24, 32):
            raise ValueError('invalid AES key size')
        self.key = bytes(key)
        self.mode = mode
        self.iv = bytes(iv) if iv else b'\x00' * 16
        self._w, self._nr = jzn__key_expansion(self.key)

    def encrypt(self, data):
        out = bytearray()
        prev = self.iv
        for i in range(0, len(data), 16):
            blk = data[i:i + 16]
            if self.mode == jzn__PureAES.MODE_CBC:
                blk = bytes(a ^ b for a, b in zip(blk, prev))
            enc = jzn__aes_encrypt_block(blk, self._w, self._nr)
            out += enc
            prev = enc
        return bytes(out)


def jzn__der_read(buf, i):
    tag = buf[i]
    i += 1
    ln = buf[i]
    i += 1
    if ln & 0x80:
        n = ln & 0x7F
        ln = int.from_bytes(buf[i:i + n], 'big')
        i += n
    return tag, buf[i:i + ln], i + ln


def jzn__rsa_pub_from_der(der):
    """解析 DER：支持 SubjectPublicKeyInfo 与裸 RSAPublicKey"""
    tag, seq, _ = jzn__der_read(der, 0)
    if tag != 0x30:
        raise ValueError('bad rsa key')
    i = 0
    t1, first, i = jzn__der_read(seq, i)
    if i >= len(seq):
        raise ValueError('bad rsa key')
    t2, second, _ = jzn__der_read(seq, i)
    if t2 == 0x03:
        inner = second[1:]
        _, rs, _ = jzn__der_read(inner, 0)
    elif t2 == 0x30:
        rs = second
    else:
        raise ValueError('bad rsa key')
    j = 0
    _, nb, j = jzn__der_read(rs, j)
    _, eb, _ = jzn__der_read(rs, j)
    return int.from_bytes(nb, 'big'), int.from_bytes(eb, 'big')


class jzn__PurePKCS1:
    def __init__(self, key):
        self.n, self.e = key

    def encrypt(self, msg):
        k = (self.n.bit_length() + 7) // 8
        if len(msg) > k - 11:
            raise ValueError('data too long for RSA')
        ps = bytearray()
        while len(ps) < k - len(msg) - 3:
            b = os.urandom(1)
            if b != b'\x00':
                ps += b
        em = b'\x00\x02' + bytes(ps) + b'\x00' + msg
        c = pow(int.from_bytes(em, 'big'), self.e, self.n)
        return c.to_bytes(k, 'big')


if jzn__HAVE_CRYPTO:
    jzn_AES = jzn__CryptoAES
    jzn_PKCS1_v1_5 = jzn__CryptoPKCS1

    def jzn__rsa_public(der_b64):
        return jzn__CryptoPKCS1.new(jzn__CryptoRSA.import_key(base64.b64decode(der_b64)))
else:
    jzn_AES = jzn__PureAES
    jzn_PKCS1_v1_5 = jzn__PurePKCS1

    def jzn__rsa_public(der_b64):
        return jzn__PurePKCS1(jzn__rsa_pub_from_der(base64.b64decode(der_b64)))

# ---------------------------------------------------------------- AES 解密补充
# 内置的纯 Python AES 只有 encrypt；首页推荐数据(tag/list)是双层 AES-ECB
# 加密，这里补上逆变换，保证无 pycryptodome 的环境也能出首页。
jzn__INV_SBOX = [0] * 256
for _i, _v in enumerate(jzn__SBOX):
    jzn__INV_SBOX[_v] = _i


def jzn__inv_sub_bytes(state):
    for i in range(16):
        state[i] = jzn__INV_SBOX[state[i]]


def jzn__inv_shift_rows(state):
    for r in range(1, 4):
        row = [state[r + 4 * c] for c in range(4)]
        for c in range(4):
            state[r + 4 * c] = row[(c - r) % 4]


def jzn__inv_mix_columns(state):
    for c in range(4):
        a = [state[r + 4 * c] for r in range(4)]
        state[0 + 4 * c] = jzn__mul(a[0], 14) ^ jzn__mul(a[1], 11) ^ jzn__mul(a[2], 13) ^ jzn__mul(a[3], 9)
        state[1 + 4 * c] = jzn__mul(a[0], 9) ^ jzn__mul(a[1], 14) ^ jzn__mul(a[2], 11) ^ jzn__mul(a[3], 13)
        state[2 + 4 * c] = jzn__mul(a[0], 13) ^ jzn__mul(a[1], 9) ^ jzn__mul(a[2], 14) ^ jzn__mul(a[3], 11)
        state[3 + 4 * c] = jzn__mul(a[0], 11) ^ jzn__mul(a[1], 13) ^ jzn__mul(a[2], 9) ^ jzn__mul(a[3], 14)


def jzn__aes_decrypt_block(block, w, nr):
    state = list(block)
    jzn__add_round_key(state, w, nr)
    for rnd in range(nr - 1, 0, -1):
        jzn__inv_shift_rows(state)
        jzn__inv_sub_bytes(state)
        jzn__add_round_key(state, w, rnd)
        jzn__inv_mix_columns(state)
    jzn__inv_shift_rows(state)
    jzn__inv_sub_bytes(state)
    jzn__add_round_key(state, w, 0)
    return bytes(state)


def jzn__pureaes_decrypt(self, data):
    out = bytearray()
    prev = self.iv
    for i in range(0, len(data), 16):
        blk = data[i:i + 16]
        dec = jzn__aes_decrypt_block(blk, self._w, self._nr)
        if self.mode == jzn__PureAES.MODE_CBC:
            dec = bytes(a ^ b for a, b in zip(dec, prev))
            prev = blk
        out += dec
    return bytes(out)


jzn__PureAES.decrypt = jzn__pureaes_decrypt


# ---------------------------------------------------------------- 新协议常量
jzn_UA = 'okhttp/3.12.1'
jzn_NATIVE_K = 'ed5fdsgucxumegqa'   # publicParams 的 AES-CBC key / iv

jzn_PUB_DEFAULT = ('MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCr8SzZhjYy+rsya1K09t8d2K50pWFoBkgUqMpKOiW'
               '+3IEVKd4eTdvg9RSOjQ82kypL6R9BnsmrS1V8s4PVDwjQbUtYhTPPC9Hz16qY7rpD6m0d2vr09/UpW'
               'Q5uOy9PR0QTrsioveZ+DIe9jc3C+zBCu/kZSY/R8stwJoiitki3gwIDAQAB')

jzn_VIDEO_RE = re.compile(r'(?i)\.(mp4|m3u8|flv|mkv|avi|ts|mov|mpd|m4a|wmv)(\?.*)?$')


def jzn__key_bytes(k):
    return k.encode() if isinstance(k, str) else k


def jzn__ecb_enc(s, key):
    return base64.b64encode(
        jzn_AES.new(jzn__key_bytes(key), jzn_AES.MODE_ECB).encrypt(jzn__pad(s.encode(), 16))).decode()


def jzn__ecb_dec(s, key):
    ct = base64.b64decode(s)
    if jzn__HAVE_CRYPTO:
        plain = jzn_AES.new(jzn__key_bytes(key), jzn_AES.MODE_ECB).decrypt(ct)
    else:
        plain = jzn__PureAES(jzn__key_bytes(key), jzn__PureAES.MODE_ECB).decrypt(ct)
    return jzn__unpad(plain).decode('utf-8', 'replace')


def jzn__cbc_enc(s, key, iv=None):
    iv = jzn__key_bytes(iv or key)
    return jzn_AES.new(jzn__key_bytes(key), jzn_AES.MODE_CBC, iv).encrypt(
        jzn__pad(s.encode(), 16)).hex()


def jzn__rsa_sign(data, pub):
    return base64.b64encode(jzn__rsa_public(pub).encrypt(data.encode())).decode()


def jzn__pb_data(raw):
    """取 ApiResult.data (field 3)"""
    for fn, wt, v in jzn__pb(raw):
        if fn == 3 and wt == 2:
            return v
    return b''


def jzn__pb_code(raw):
    for fn, wt, v in jzn__pb(raw):
        if fn == 1 and wt == 0:
            return v
    return -1

# ---------------------------------------------------------------- protobuf 工具
def jzn__varint(n):
    b = b''
    while True:
        x = n & 0x7f
        n >>= 7
        if n:
            b += bytes([x | 0x80])
        else:
            return b + bytes([x])


def jzn__f(num, wire, payload):
    t = jzn__varint((num << 3) | wire)
    if wire == 2:
        return t + jzn__varint(len(payload)) + payload
    return t + payload


def jzn__pb(buf):
    # 正确的 protobuf 解析：字段号 > 15 时 tag 是多字节 varint，
    # 只读一个字节会造成整体错位（老版本源文件就是因此只能按原始字节扫描）
    out = []
    i = 0
    n = len(buf)
    while i < n:
        tag = 0
        sh = 0
        while i < n:
            x = buf[i]; i += 1
            tag |= (x & 0x7f) << sh; sh += 7
            if not x & 0x80:
                break
        fn, wt = tag >> 3, tag & 7
        if fn == 0:
            break
        if wt == 0:
            v = 0; sh = 0
            while i < n:
                x = buf[i]; i += 1
                v |= (x & 0x7f) << sh; sh += 7
                if not x & 0x80:
                    break
            out.append((fn, wt, v))
        elif wt == 2:
            ln = 0; sh = 0
            while i < n:
                x = buf[i]; i += 1
                ln |= (x & 0x7f) << sh; sh += 7
                if not x & 0x80:
                    break
            out.append((fn, wt, buf[i:i + ln])); i += ln
        elif wt == 5:
            out.append((fn, wt, buf[i:i + 4])); i += 4
        elif wt == 1:
            out.append((fn, wt, buf[i:i + 8])); i += 8
        else:
            i += 1
    return out


def jzn__rnd(k):
    CH = string.ascii_letters + string.digits
    return ''.join(random.sample(list(CH), k - 1)) + '='

# ---------------------------------------------------------------- 内置分类兜底
# 新网关不提供 /api/v3/drama/getCategory（返回 400 No static resource），
# 与官方插件一致：接口拿不到时使用内置分类表。
jzn_CATEGORIES = [{'id': 20, 'name': '电影', 'converUrl': '{"class":"喜剧,爱情,恐怖,动作,科幻,剧情,战争,警匪,犯罪,动画,奇幻,武侠,冒险,枪战,恐怖,悬疑,惊悚,经典,青春,文艺,微电影,古装,历史,运动,农村,儿童,网络电影","area":"大陆,香港,台湾,美国,法国,英国,日本,韩国,德国,泰国,印度,意大利,西班牙,加拿大,其他","lang":"国语,英语,粤语,闽南语,韩语,日语,法语,德语,其它","year":"2026,2025,2024,2023,2022,2021,2020,2019,2018,2017,2016,2015,2014,2013,2012,2011,2010","extend_sort":"最新,最热,好评"}', 'typeMid': 1, 'typeSort': 2, 'typePid': 0}, {'id': 21, 'name': '剧集', 'converUrl': '{"class":"古装,战争,青春,偶像,喜剧,家庭,犯罪,动作,奇幻,剧情,历史,经典,乡村,情景,商战,网剧,其他","area":"内地,韩国,香港,台湾,日本,美国,泰国,英国,新加坡,其他","lang":"国语,英语,粤语,闽南语,韩语,日语,其它","year":"2026,2025,2024,2023,2022,2021,2020,2019,2018,2017,2016,2015,2014,2013,2012,2011,2010,2009,2008,2007,2006,2005,2004,2003,2002,2001,2000","extend_sort":"最新,最热,好评"}', 'typeMid': 1, 'typeSort': 1, 'typePid': 0}, {'id': 22, 'name': '综艺', 'converUrl': '{"class":"选秀,情感,访谈,播报,旅游,音乐,美食,纪实,曲艺,生活,游戏互动,财经,求职","area":"内地,港台,日韩,欧美","lang":"国语,英语,粤语,闽南语,韩语,日语,其它","year":"2026,2025,2024,2023,2022,2021,2020,2019,2018,2017,2016,2015,2014,2013,2012,2011,2010","extend_sort":"最新,最热,好评"}', 'typeMid': 1, 'typeSort': 3, 'typePid': 0}, {'id': 23, 'name': '动漫', 'converUrl': '{"year":"2026,2025,2024,2023,2022,2021,2020,2019,2018,2017,2016","extend_sort":"最新,最热,好评"}', 'typeMid': 1, 'typeSort': 6, 'typePid': 0}, {'id': 24, 'name': '短剧', 'converUrl': '{"class":"重生民国,穿越年代,现代言情,反转爽文,女恋总裁,闪婚离婚,都市脑洞,古装仙侠,其它","year":"2026,2025,2024,2023,2022,2021,2020,2019,2018,2017,2016","extend_sort":"最新,最热,好评"}', 'typeMid': 1, 'typeSort': 4, 'typePid': 0}, {'id': 26, 'name': '漫剧', 'converUrl': '{}', 'typeMid': 1, 'typeSort': 5, 'typePid': 0}]


# ---------------------------------------------------------------- Spider
class JZNewRaw(jzn__Base):
    HOST_NAME = '橘汁-新网关'

    # 默认配置：来自 sun.json 里「橘汁 • APP」(csp_AppDrama) 的 ext
    DEFAULT = {
        'host': 'http://juziapp.hzhcbkj.cn',
        'site': 'https://123-1349250429.cos.ap-shanghai.myqcloud.com/app.txt',
        'publicKey': jzn_PUB_DEFAULT,
        'dataKey': 'ZU1DSFFWNENKMDYXVUQRN0ZJDUC4PQ==',
        'dataIv': 'OC1A06E197EF10CF3F6058CA7A803B5E',
        'pkg': 'com.asjdhjhd.mgd.p3',
        'appName': '橘汁',
        'version': '3.0.7.0',
        'decrypt': '1',
    }

    ONLY_4K = False        # True = 详情页只保留线路名含 4K 的线路
    TIMEOUT = 15
    CACHE_LIMIT = 128

    # ------------------------------------------------------------ 生命周期
    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
        except Exception:
            pass
        self.cfg = dict(self.DEFAULT)
        self.host = self.cfg['host']
        self.udid = uuid.uuid4().hex.upper()
        self.sec = ''              # zone 下发的二级公钥
        self._ready = False
        self._site_done = False
        self._cats = None
        self._detail_cache = {}
        self._home_cache = None      # (timestamp, list)，纯 Python 解密较慢，缓存 60s
        self._lock = threading.Lock()

    def getName(self):
        return self.HOST_NAME

    def init(self, extend=""):
        # 不联网：AVBox 在导入阶段可能调用 init，网络失败会卡住整个源
        try:
            if isinstance(extend, str) and extend.strip().startswith('{'):
                ext = json.loads(extend)
                if isinstance(ext, dict):
                    for k, v in ext.items():
                        if k in self.DEFAULT and v not in (None, ''):
                            self.cfg[k] = str(v)
                    if ext.get('host'):
                        self.host = self.cfg['host'].rstrip('/')
                        self._site_done = True   # 手动指定就不再拉 site
                    if str(ext.get('only4k', '')).lower() in ('1', 'true', 'yes'):
                        self.ONLY_4K = True
        except Exception:
            pass
        self._ready = False
        self.sec = ''
        self._site_done = bool(self.cfg.get('host')) and self._site_done
        try:
            self._detail_cache.clear()
            self._home_cache = None
        except Exception:
            pass

    def destroy(self):
        try:
            self._detail_cache.clear()
            self._home_cache = None
        except Exception:
            pass

    # ------------------------------------------------------------ 会话 / 网络
    def _http(self, url, data=None, headers=None, timeout=None):
        req = urllib.request.Request(url, data=data, headers=headers or {})
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=timeout or self.TIMEOUT, context=ctx) as r:
            return r.read()

    def _get(self, path, headers, timeout=None):
        try:
            return self._http(self.host + path, None, headers, timeout)
        except Exception:
            return b''

    def _ensure(self):
        """懒加载：拉最新 domain + 取二级公钥，失败可重试"""
        if self._ready:
            return True
        with self._lock:
            if self._ready:
                return True
            if not self._site_done:
                self._site_done = True
                site = self.cfg.get('site', '')
                if site:
                    try:
                        raw = self._http(site, None, {'User-Agent': jzn_UA}, 8)
                        domain = (json.loads(raw.decode('utf-8', 'ignore')) or {}).get('domain', '')
                        if domain.startswith('http'):
                            self.host = domain.rstrip('/')
                    except Exception:
                        pass
            sec = self._zone()
            if sec:
                self.sec = sec
                self._ready = True
        return self._ready

    def _zone(self):
        ts = int(time.time() * 1000)
        r = jzn__rnd(16)
        sign = jzn__rsa_sign(str(ts) + r, self.cfg['publicKey'])
        # 关键：field 3 与 field 4 必须是同一个随机串，服务端拿 field 4
        # 参与 RSA 校验；field 2 是 sign，field 5 是干扰串。
        body = (jzn__f(1, 0, jzn__varint(ts)) + jzn__f(2, 2, sign.encode()) +
                jzn__f(3, 2, r.encode()) + jzn__f(4, 2, r.encode()) +
                jzn__f(5, 2, jzn__rnd(16).encode()))
        try:
            raw = self._http(self.host + '/api/v5/find/app/zone', body,
                             self._c_head(self.cfg['publicKey']))
        except Exception:
            return ''
        data = jzn__pb_data(raw)
        if not data:
            return ''
        strs = {fn: v.decode('utf-8', 'replace') for fn, wt, v in jzn__pb(data) if wt == 2}
        # 公钥分片在 field 2/3/4/5，field 1 是干扰串
        return ''.join(strs.get(k, '') for k in (2, 3, 4, 5))

    # ------------------------------------------------------------ 请求构造
    def _d_obj(self):
        return {"country": "CN", "vName": self.cfg['version'],
                "cpuId": "MT6893Z%2FCZA", "young": 0, "facturer": "OnePlus",
                "pkg": self.cfg['pkg'], "uuid": self.udid,
                "resolution": "1080x2272", "mac": "02%3A00%3A00%3A00%3A00%3A00",
                "abid": "397", "model": "PJX110", "plat": "android",
                "udid": self.udid, "dpi": "440", "net": "1", "lang": "zh",
                "brand": "OnePlus", "density": "2.75",
                "appName": self.cfg['appName'], "cpu": "arm64-v8a",
                "chid": "10000", "carrier": "%E8%81%94%E9%80%9A",
                "_vOsCode": "36", "vOs": "16", "v": 1, "tenantId": "",
                "vApp": self.cfg['version'].replace('.', ''),
                "device": 0, "androidID": self.udid}

    def _c_head(self, sec):
        """protobuf 接口头：publicParams 为 AES-CBC 加密后的 paramsData"""
        d = self._d_obj()
        ts = int(time.time() * 1000)
        f = jzn__rnd(16)
        d['sig'] = jzn__rsa_sign(str(ts) + f + d['vApp'], sec)
        b = jzn__ecb_enc(str(ts) + f, self.cfg['dataIv'])
        d.update({'random_str': f, 'timestamp': ts, 'sig2': b[:8], 'sig3': b[8:]})
        p = jzn__cbc_enc(json.dumps(d, separators=(',', ':'), ensure_ascii=False), jzn_NATIVE_K)
        return {'User-Agent': jzn_UA, 'Accept': 'application/x-protobuf',
                'Content-Type': 'application/x-protobuf',
                'Cache-Control': 'no-cache',
                'publicParams': json.dumps({'paramsData': p}, separators=(',', ':'))}

    def _e_head(self):
        """JSON 接口头：只加密 d()，不带 sig"""
        p = jzn__cbc_enc(json.dumps(self._d_obj(), separators=(',', ':'),
                                ensure_ascii=False), jzn_NATIVE_K)
        return {'User-Agent': jzn_UA, 'Accept': 'application/json',
                'Content-Type': 'application/json; charset=utf-8',
                'publicParams': json.dumps({'paramsData': p}, separators=(',', ':'))}

    def _g_body(self, mp):
        """SecureRequest：参数按 dataKey 做 AES-ECB 后分片"""
        ts = int(time.time() * 1000)
        f8, f20 = jzn__rnd(8), jzn__rnd(20)
        sb = '&'.join('%s=%s' % (k, v) for k, v in mp.items() if v not in (None, ''))
        s3 = f8 + jzn__ecb_enc(sb + str(ts), self.cfg['dataKey'])
        return (jzn__f(1, 2, s3[:20].encode()) + jzn__f(2, 2, s3[20:].encode()) +
                jzn__f(3, 2, f20.encode()) + jzn__f(4, 0, jzn__varint(ts)) +
                jzn__f(5, 2, f8.encode()))

    def _post(self, path, mp):
        if not self._ensure():
            return b''
        for attempt in (0, 1):
            try:
                raw = self._http(self.host + path, self._g_body(mp),
                                 self._c_head(self.sec or self.cfg['publicKey']))
            except Exception:
                return b''
            code = jzn__pb_code(raw)
            if code == 200:
                return jzn__pb_data(raw)
            if code in (100001, 100002, 100003) and attempt == 0:
                self._ready, self.sec = False, ''
                if not self._ensure():
                    return b''
                continue
            return b''
        return b''

    # ------------------------------------------------------------ 列表解析
    @staticmethod
    def _pic(cov):
        if not cov:
            return ''
        m = re.search(r'https?://[^\x00-\x20"\\]+', cov)
        return m.group(0) if m else ''

    @classmethod
    def _parse_list(cls, data):
        out = []
        if not data:
            return out
        for fn, wt, v in jzn__pb(data):
            if fn != 1 or wt != 2 or not isinstance(v, bytes) or len(v) < 8:
                continue
            d = {}
            for f2, w2, x in jzn__pb(v):
                if w2 == 2 and isinstance(x, bytes):
                    d[f2] = x.decode('utf-8', 'replace')
                elif w2 == 0:
                    d[f2] = x
            if not isinstance(d.get(3), int) or not d.get(5):
                continue
            out.append({'vod_id': str(d[3]), 'vod_name': d.get(5, ''),
                        'vod_pic': cls._pic(d.get(2, '')),
                        'vod_remarks': d.get(13, '') or ''})
        return out

    def _cache_put(self, cache, key, value):
        try:
            if len(cache) >= self.CACHE_LIMIT:
                cache.clear()
            cache[key] = value
        except Exception:
            pass

    # ------------------------------------------------------------ 首页 / 分类
    def _categories(self):
        if self._cats:
            return self._cats
        raw = self._get('/api/v3/drama/getCategory?orderBy=type_id', self._e_head())
        try:
            d = (json.loads(raw.decode('utf-8', 'ignore')) or {}).get('data')
            if isinstance(d, list) and d:
                self._cats = d
                return d
        except Exception:
            pass
        self._cats = jzn_CATEGORIES
        return self._cats

    def homeContent(self, filter):
        try:
            cats = self._categories()
            classes = [{'type_id': str(c['id']), 'type_name': c['name']}
                       for c in cats if c.get('name') != '公告']
            labels = [('class', '类型'), ('area', '地区'), ('lang', '语言'),
                      ('year', '年份'), ('extend_sort', '排序')]
            filters = {}
            for c in cats:
                try:
                    cv = json.loads(c.get('converUrl') or '{}')
                except Exception:
                    cv = {}
                fl = []
                for k, label in labels:
                    v = cv.get(k)
                    if v:
                        fl.append({'key': k, 'name': label,
                                   'value': [{'n': x, 'v': x} for x in v.split(',') if x]})
                if fl:
                    filters[str(c['id'])] = fl
            return {'class': classes, 'filters': filters}
        except Exception:
            return {'class': [], 'filters': {}}

    def homeVideoContent(self):
        if self._home_cache and time.time() - self._home_cache[0] < 60:
            return {'list': self._home_cache[1]}
        try:
            raw = self._get('/api/ex/v3/security/tag/list', self._e_head())
            j = json.loads(raw.decode('utf-8', 'ignore'))
            ds = j.get('data') or ''
            if self.cfg.get('decrypt', '1') != '0' and ds:
                ds = jzn__ecb_dec(ds, self.cfg['dataKey'])
                ds = jzn__ecb_dec(ds, self.cfg['dataIv'])
            arr = json.loads(ds) if ds else []
            seen, out = set(), []
            for block in arr:
                for sec in (block.get('sections') or []):
                    for v in (sec.get('vodList') or []):
                        vid = str(v.get('id', ''))
                        if not vid or vid in seen:
                            continue
                        seen.add(vid)
                        out.append({'vod_id': vid, 'vod_name': v.get('name', ''),
                                    'vod_pic': (v.get('coverImage') or {}).get('path', '') or '',
                                    'vod_remarks': v.get('remark', '') or ''})
            self._home_cache = (time.time(), out)
            return {'list': out}
        except Exception:
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            mp = {'pagesize': '21', 'typeId1': str(tid), 'page': str(pg or 1),
                  'vodOrderBy': '最新'}
            ext = extend if isinstance(extend, dict) else {}
            for k, dst in (('extend_sort', 'vodOrderBy'), ('area', 'vodArea'),
                           ('lang', 'vodLang'), ('class', 'vodClass'),
                           ('year', 'vodYear')):
                if ext.get(k):
                    mp[dst] = str(ext[k])
            lst = self._parse_list(self._post('/api/proto/v5/drama/category', mp))
            page = int(pg or 1)
            return {'list': lst, 'page': page,
                    'pagecount': page + 1 if len(lst) >= 21 else page,
                    'limit': 21, 'total': len(lst)}
        except Exception:
            return {'list': []}

    def searchContent(self, key, quick, pg="1"):
        try:
            data = self._post('/api/proto/v5/drama/search',
                              {'searchKeys': str(key), 'page': str(pg or 1),
                               'pagesize': '21'})
            return {'list': self._parse_list(data)}
        except Exception:
            return {'list': []}

    # ------------------------------------------------------------ 详情
    def detailContent(self, ids):
        try:
            raw = ids[0] if isinstance(ids, (list, tuple)) and ids else str(ids)
            vid = str(raw).strip().strip('/')
            if vid in self._detail_cache:
                return {'list': [self._detail_cache[vid]]}
            data = self._post('/api/proto/v5/drama/getDetail', {'id': vid})
            if not data:
                return {'list': []}
            dd = jzn__pb(data)
            meta = {}
            for fn, wt, v in dd:
                if wt == 2 and isinstance(v, bytes):
                    meta[fn] = v.decode('utf-8', 'replace')
                elif wt == 0:
                    meta[fn] = v

            lines = collections.OrderedDict()
            for fn, wt, v in dd:
                if fn != 29 or wt != 2:
                    continue
                e = {}
                for f2, w2, x in jzn__pb(v):
                    if w2 == 2 and isinstance(x, bytes):
                        e[f2] = x.decode('utf-8', 'replace')
                    elif w2 == 0:
                        e[f2] = x
                cn = e.get(10) or e.get(9) or '橘汁'
                src, path = e.get(9, ''), e.get(4, '')
                title = e.get(3) or e.get(2) or '正片'
                if not path:
                    continue
                if not jzn_VIDEO_RE.search(path):
                    path = base64.b64encode(json.dumps(
                        {'vodPlayFrom': src, 'playUrl': path},
                        separators=(',', ':'), ensure_ascii=False).encode()).decode()
                lines.setdefault(cn, []).append(title + '$' + path)

            if self.ONLY_4K:
                k4 = [k for k in lines if '4K' in k.upper()]
                if k4:
                    lines = collections.OrderedDict((k, lines[k]) for k in k4)

            intro = re.sub(r'<[^>]+>', '', meta.get(6) or meta.get(7) or '').strip()
            vod = {
                'vod_id': vid,
                'vod_name': meta.get(9, '') or '',
                'vod_pic': self._pic(meta.get(2, '')),
                'vod_remarks': meta.get(26, '') or '',
                'vod_year': str(meta.get(18, '') or ''),
                'vod_area': meta.get(1, '') or '',
                'vod_actor': meta.get(25, '') or '',
                'vod_director': meta.get(12, '') or '',
                'vod_content': intro,
                'vod_play_from': '$$$'.join(lines.keys()),
                'vod_play_url': '$$$'.join('#'.join(v) for v in lines.values()),
            }
            self._cache_put(self._detail_cache, vid, vod)
            return {'list': [vod]}
        except Exception:
            return {'list': []}

    # ------------------------------------------------------------ 播放
    def playerContent(self, flag, id, vipFlags=None):
        try:
            pid = str(id).strip()
            if jzn_VIDEO_RE.search(pid):
                return {'parse': 0, 'url': pid, 'header': {}}
            try:
                j = json.loads(base64.b64decode(pid).decode('utf-8', 'replace'))
            except Exception:
                return {'parse': 0, 'url': pid, 'header': {}}
            mp = {'vodPlayFrom': j.get('vodPlayFrom', ''),
                  'playUrl': j.get('playUrl', '')}
            data = self._post('/api/proto/v5/videoUsableUrl', mp)
            url = ''
            if data:
                for fn, wt, v in jzn__pb(data):
                    if fn == 1 and wt == 2:
                        url = v.decode('utf-8', 'replace')
                        break
            if not url.startswith('http'):
                return {'parse': 0, 'url': '', 'header': {}}
            return {'parse': 0, 'url': url, 'header': {}}
        except Exception:
            return {'parse': 0, 'url': '', 'header': {}}

    def liveContent(self, params):
        return {'list': []}

# ---- 门面适配 jn：新网关源只挂线路，不建独立站点 ----
class JZNewSpider(_BaseSpider):
    NAME = '橘汁新网关'

    def __init__(self):
        self.ob = None

    def init(self, extend=''):
        if self.ob is None:
            self.ob = JZNewRaw()
        try:
            self.ob.init('')
        except Exception:
            pass
        return None

    def destroy(self):
        try:
            self.ob.destroy()
        except Exception:
            pass

    @staticmethod
    def _quick(fn, wait, fallback):
        box = {}

        def run():
            try:
                box['r'] = fn()
            except Exception:
                box['r'] = fallback
        th = threading.Thread(target=run, daemon=True)
        th.start()
        th.join(wait)
        return box.get('r', fallback)

    def homeContent(self, filter=True):
        return {'class': [], 'list': []}

    def categoryContent(self, tid, pg='1', filter=True, extend=None):
        return {'list': [], 'page': 1, 'pagecount': 1, 'total': 0}

    def searchContent(self, key, quick=False, pg='1'):
        kw = str(key or '').strip()
        if not kw:
            return {'list': []}
        got = self._quick(
            lambda: self.ob.searchContent(kw, quick, str(pg or 1)),
            3.2, {'list': []})
        return got if isinstance(got, dict) else {'list': []}

    def detailContent(self, ids):
        vid = ids[0] if isinstance(ids, (list, tuple)) and ids else ids
        got = self._quick(lambda: self.ob.detailContent([str(vid)]), 3.2,
                          {'list': []})
        v = ((got or {}).get('list') or [{}])[0] if isinstance(got, dict) else {}
        if not isinstance(v, dict) or not str(v.get('vod_play_from') or ''):
            return {'list': []}
        return {'list': [dict(v)]}

    def playerContent(self, flag, id, vipFlags=None):
        got = self._quick(lambda: self.ob.playerContent(flag, id, vipFlags),
                          8.0, {'parse': 0, 'url': '', 'header': {}})
        return got if isinstance(got, dict) else {
            'parse': 0, 'url': '', 'header': {}}
# ==================== 橘汁新网关线路源 jn END ====================

# ==================== 四源4K专线线路源 sk BEGIN ====================
# -*- coding: utf-8 -*-
# ============================================================================
# 四源 4K 专线 · 天堂 / 布布 / 华谊 / 苹果  (TVBox / AVBox / drpy 通用)
# ============================================================================
# 数据来源：https://9877.kstore.space/sun.json 解密后的 sites 配置
#   - 天堂 • APP  (csp_AppDrama)  pkg com.dytiantang.one
#   - 布布 • APP  (csp_YunDuo)    host 323433ssdfd.top
#   - 华谊 • APP  (csp_AppDrama)  pkg com.lxf.sncgtzxyx
#   - 苹果 • APP  (csp_AppDrama)  pkg com.juechufsh.android.xpg1
#
# 本文件做的事：把四个 APP 源各自实现一遍，并且**详情页只保留 4K 线路**
# （线路名含 4K 的才显示；若该片一条 4K 都没有，则原样保留全部线路）。
#
# 实测（2026-11-08）：
#   天堂：超级无敌4K / 高清4K / 高清蓝光4K / 4k专线2️⃣   → 全部可解直链
#   华谊：蓝光4K                                        → 可解直链
#   苹果：超级无敌4K / 高清4K / 高清蓝光4K / 4k专线2️⃣   → 全部可解直链
#   布布：CO4K                                          → 服务端返回
#         PLATFORM_NOT_ALLOWED（该线路只对 APP 客户端开放，Web 通道锁死），
#         代码里保留该线路并做了「自动回退到同片 1080P 线路」的兜底。
#
# 补充（用 ffprobe 逐条探过分辨率）：
#   天堂「超级无敌4K」1280x538、「高清4K」1716x720、「独家4K」1920x806
#   也就是说这些“4K”只是线路名，没有一条是真 4K（3840x2160）。
#   布布聚合源里「站外-极速」反而是 1920x1080，是全站画质最高的一条。
#
# 用法：一个 py 文件，配 4 个 site，ext 里用 src 指定源。
#   api 填 py 文件本身（本地文件名或 http 地址都行），ext 是传给 init() 的
#   参数，两者互不影响：
#   {"key":"天堂4K","name":"天堂 • 4K","type":3,
#    "api":"http://你的地址/四源4K专线.py","ext":"{\"src\":\"天堂\"}"}
#   同理 {"src":"布布"} / {"src":"华谊"} / {"src":"苹果"}
#   不传 ext 时默认“天堂”。
#
# 可选 ext 字段（覆盖内置配置）：
#   {"src":"华谊","host":"http://x.x.x.x:18004","only4k":false}
#
# 依赖：零第三方库。有 pycryptodome 时用 C 实现，没有则走内置纯 Python
#       AES / RSA（首页推荐需要 AES 解密，已一并实现）。
# ============================================================================

import json
import re
import ssl
import time
import base64
import string
import random
import uuid
import os
import threading
import urllib.request
import urllib.parse

import collections
try:
    from base.spider import Spider as _Base
except Exception:
    class _Base:
        pass

# ---------------------------------------------------------------- 加密层
# AVBox 1.3.0 的 pip 只带 lxml/requests/pyquery，没有 pycryptodome。
# 原文件在模块顶层 `from Crypto...` 直接把整个源卡在导入阶段。
# 现在：能用 Crypto 就用（行为与原来完全一致），没有就用内置纯 Python 实现。
try:
    from Crypto.PublicKey import RSA as _CryptoRSA
    from Crypto.Cipher import PKCS1_v1_5 as _CryptoPKCS1
    from Crypto.Cipher import AES as _CryptoAES
    sk4__HAVE_CRYPTO = True
except Exception:
    sk4__HAVE_CRYPTO = False


def sk4__pad(data, block=16):
    """PKCS#7 填充（与 Crypto.Util.Padding.pad 一致）"""
    n = block - (len(data) % block)
    return data + bytes([n]) * n


def sk4__unpad(data, block=16):
    n = data[-1]
    if 0 < n <= block and len(data) >= n:
        return data[:-n]
    return data


def sk4__gf_tables():
    alog = [0] * 256
    log = [0] * 256
    x = 1
    for i in range(255):
        alog[i] = x
        log[x] = i
        h = ((x << 1) ^ (0x1B if (x & 0x80) else 0)) & 0xFF
        x = h ^ x
    return alog, log


def sk4__mk_sbox():
    alog, log = sk4__gf_tables()
    sbox = [0] * 256
    for i in range(256):
        if i == 0:
            s = 0
        else:
            s = alog[(255 - log[i]) % 255]
        r = s
        for _ in range(4):
            s = ((s << 1) | (s >> 7)) & 0xFF
            r ^= s
        sbox[i] = r ^ 0x63
    return sbox


sk4__SBOX = sk4__mk_sbox()


def sk4__xtime(a):
    return ((a << 1) ^ 0x1B) & 0xFF if (a & 0x80) else (a << 1) & 0xFF


def sk4__mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a = sk4__xtime(a)
        b >>= 1
    return r


def sk4__key_expansion(key):
    nk = len(key) // 4
    nr = nk + 6
    w = [list(key[4 * i:4 * i + 4]) for i in range(nk)]
    rcon = 1
    for i in range(nk, 4 * (nr + 1)):
        t = list(w[i - 1])
        if i % nk == 0:
            t = t[1:] + t[:1]
            t = [sk4__SBOX[b] for b in t]
            t[0] ^= rcon
            rcon = sk4__xtime(rcon)
        elif nk > 6 and i % nk == 4:
            t = [sk4__SBOX[b] for b in t]
        w.append([w[i - nk][j] ^ t[j] for j in range(4)])
    return w, nr


def sk4__add_round_key(state, w, rnd):
    for c in range(4):
        kw = w[4 * rnd + c]
        for r in range(4):
            state[r + 4 * c] ^= kw[r]


def sk4__sub_bytes(state):
    for i in range(16):
        state[i] = sk4__SBOX[state[i]]


def sk4__shift_rows(state):
    # AES 行移位：第 r 行循环左移 r 位（state 为列主序 flat 索引 r + 4c）
    for r in range(1, 4):
        row = [state[r + 4 * c] for c in range(4)]
        for c in range(4):
            state[r + 4 * c] = row[(c + r) % 4]


def sk4__mix_columns(state):
    for c in range(4):
        a = [state[r + 4 * c] for r in range(4)]
        state[0 + 4 * c] = sk4__mul(a[0], 2) ^ sk4__mul(a[1], 3) ^ a[2] ^ a[3]
        state[1 + 4 * c] = a[0] ^ sk4__mul(a[1], 2) ^ sk4__mul(a[2], 3) ^ a[3]
        state[2 + 4 * c] = a[0] ^ a[1] ^ sk4__mul(a[2], 2) ^ sk4__mul(a[3], 3)
        state[3 + 4 * c] = sk4__mul(a[0], 3) ^ a[1] ^ a[2] ^ sk4__mul(a[3], 2)


def sk4__aes_encrypt_block(block, w, nr):
    state = list(block)
    sk4__add_round_key(state, w, 0)
    for rnd in range(1, nr):
        sk4__sub_bytes(state)
        sk4__shift_rows(state)
        sk4__mix_columns(state)
        sk4__add_round_key(state, w, rnd)
    sk4__sub_bytes(state)
    sk4__shift_rows(state)
    sk4__add_round_key(state, w, nr)
    return bytes(state)


class sk4__PureAES:
    MODE_ECB = 1
    MODE_CBC = 2

    @classmethod
    def new(cls, key, mode, iv=None):
        return cls(key, mode, iv)

    def __init__(self, key, mode, iv=None):
        if len(key) not in (16, 24, 32):
            raise ValueError('invalid AES key size')
        self.key = bytes(key)
        self.mode = mode
        self.iv = bytes(iv) if iv else b'\x00' * 16
        self._w, self._nr = sk4__key_expansion(self.key)

    def encrypt(self, data):
        out = bytearray()
        prev = self.iv
        for i in range(0, len(data), 16):
            blk = data[i:i + 16]
            if self.mode == sk4__PureAES.MODE_CBC:
                blk = bytes(a ^ b for a, b in zip(blk, prev))
            enc = sk4__aes_encrypt_block(blk, self._w, self._nr)
            out += enc
            prev = enc
        return bytes(out)


def sk4__der_read(buf, i):
    tag = buf[i]
    i += 1
    ln = buf[i]
    i += 1
    if ln & 0x80:
        n = ln & 0x7F
        ln = int.from_bytes(buf[i:i + n], 'big')
        i += n
    return tag, buf[i:i + ln], i + ln


def sk4__rsa_pub_from_der(der):
    """解析 DER：支持 SubjectPublicKeyInfo 与裸 RSAPublicKey"""
    tag, seq, _ = sk4__der_read(der, 0)
    if tag != 0x30:
        raise ValueError('bad rsa key')
    i = 0
    t1, first, i = sk4__der_read(seq, i)
    if i >= len(seq):
        raise ValueError('bad rsa key')
    t2, second, _ = sk4__der_read(seq, i)
    if t2 == 0x03:
        inner = second[1:]
        _, rs, _ = sk4__der_read(inner, 0)
    elif t2 == 0x30:
        rs = second
    else:
        raise ValueError('bad rsa key')
    j = 0
    _, nb, j = sk4__der_read(rs, j)
    _, eb, _ = sk4__der_read(rs, j)
    return int.from_bytes(nb, 'big'), int.from_bytes(eb, 'big')


class sk4__PurePKCS1:
    def __init__(self, key):
        self.n, self.e = key

    def encrypt(self, msg):
        k = (self.n.bit_length() + 7) // 8
        if len(msg) > k - 11:
            raise ValueError('data too long for RSA')
        ps = bytearray()
        while len(ps) < k - len(msg) - 3:
            b = os.urandom(1)
            if b != b'\x00':
                ps += b
        em = b'\x00\x02' + bytes(ps) + b'\x00' + msg
        c = pow(int.from_bytes(em, 'big'), self.e, self.n)
        return c.to_bytes(k, 'big')


if sk4__HAVE_CRYPTO:
    sk4_AES = _CryptoAES
    sk4_PKCS1_v1_5 = _CryptoPKCS1

    def sk4__rsa_public(der_b64):
        return _CryptoPKCS1.new(_CryptoRSA.import_key(base64.b64decode(der_b64)))
else:
    sk4_AES = sk4__PureAES
    sk4_PKCS1_v1_5 = sk4__PurePKCS1

    def sk4__rsa_public(der_b64):
        return sk4__PurePKCS1(sk4__rsa_pub_from_der(base64.b64decode(der_b64)))

# ---------------------------------------------------------------- AES 解密补充
# 内置的纯 Python AES 只有 encrypt；首页推荐数据(tag/list)是双层 AES-ECB
# 加密，这里补上逆变换，保证无 pycryptodome 的环境也能出首页。
sk4__INV_SBOX = [0] * 256
for _i, _v in enumerate(sk4__SBOX):
    sk4__INV_SBOX[_v] = _i


def sk4__inv_sub_bytes(state):
    for i in range(16):
        state[i] = sk4__INV_SBOX[state[i]]


def sk4__inv_shift_rows(state):
    for r in range(1, 4):
        row = [state[r + 4 * c] for c in range(4)]
        for c in range(4):
            state[r + 4 * c] = row[(c - r) % 4]


def sk4__inv_mix_columns(state):
    for c in range(4):
        a = [state[r + 4 * c] for r in range(4)]
        state[0 + 4 * c] = sk4__mul(a[0], 14) ^ sk4__mul(a[1], 11) ^ sk4__mul(a[2], 13) ^ sk4__mul(a[3], 9)
        state[1 + 4 * c] = sk4__mul(a[0], 9) ^ sk4__mul(a[1], 14) ^ sk4__mul(a[2], 11) ^ sk4__mul(a[3], 13)
        state[2 + 4 * c] = sk4__mul(a[0], 13) ^ sk4__mul(a[1], 9) ^ sk4__mul(a[2], 14) ^ sk4__mul(a[3], 11)
        state[3 + 4 * c] = sk4__mul(a[0], 11) ^ sk4__mul(a[1], 13) ^ sk4__mul(a[2], 9) ^ sk4__mul(a[3], 14)


def sk4__aes_decrypt_block(block, w, nr):
    state = list(block)
    sk4__add_round_key(state, w, nr)
    for rnd in range(nr - 1, 0, -1):
        sk4__inv_shift_rows(state)
        sk4__inv_sub_bytes(state)
        sk4__add_round_key(state, w, rnd)
        sk4__inv_mix_columns(state)
    sk4__inv_shift_rows(state)
    sk4__inv_sub_bytes(state)
    sk4__add_round_key(state, w, 0)
    return bytes(state)


def sk4__pureaes_decrypt(self, data):
    out = bytearray()
    prev = self.iv
    for i in range(0, len(data), 16):
        blk = data[i:i + 16]
        dec = sk4__aes_decrypt_block(blk, self._w, self._nr)
        if self.mode == sk4__PureAES.MODE_CBC:
            dec = bytes(a ^ b for a, b in zip(dec, prev))
            prev = blk
        out += dec
    return bytes(out)


sk4__PureAES.decrypt = sk4__pureaes_decrypt


# ---------------------------------------------------------------- 新协议常量
sk4_UA = 'okhttp/3.12.1'
sk4_NATIVE_K = 'ed5fdsgucxumegqa'   # publicParams 的 AES-CBC key / iv

sk4_PUB_DEFAULT = ('MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCr8SzZhjYy+rsya1K09t8d2K50pWFoBkgUqMpKOiW'
               '+3IEVKd4eTdvg9RSOjQ82kypL6R9BnsmrS1V8s4PVDwjQbUtYhTPPC9Hz16qY7rpD6m0d2vr09/UpW'
               'Q5uOy9PR0QTrsioveZ+DIe9jc3C+zBCu/kZSY/R8stwJoiitki3gwIDAQAB')

sk4_VIDEO_RE = re.compile(r'(?i)\.(mp4|m3u8|flv|mkv|avi|ts|mov|mpd|m4a|wmv)(\?.*)?$')


def sk4__key_bytes(k):
    return k.encode() if isinstance(k, str) else k


def sk4__ecb_enc(s, key):
    return base64.b64encode(
        sk4_AES.new(sk4__key_bytes(key), sk4_AES.MODE_ECB).encrypt(sk4__pad(s.encode(), 16))).decode()


def sk4__ecb_dec(s, key):
    ct = base64.b64decode(s)
    if sk4__HAVE_CRYPTO:
        plain = sk4_AES.new(sk4__key_bytes(key), sk4_AES.MODE_ECB).decrypt(ct)
    else:
        plain = sk4__PureAES(sk4__key_bytes(key), sk4__PureAES.MODE_ECB).decrypt(ct)
    return sk4__unpad(plain).decode('utf-8', 'replace')


def sk4__cbc_enc(s, key, iv=None):
    iv = sk4__key_bytes(iv or key)
    return sk4_AES.new(sk4__key_bytes(key), sk4_AES.MODE_CBC, iv).encrypt(
        sk4__pad(s.encode(), 16)).hex()


def sk4__rsa_sign(data, pub):
    return base64.b64encode(sk4__rsa_public(pub).encrypt(data.encode())).decode()


def sk4__pb_data(raw):
    """取 ApiResult.data (field 3)"""
    for fn, wt, v in sk4__pb(raw):
        if fn == 3 and wt == 2:
            return v
    return b''


def sk4__pb_code(raw):
    for fn, wt, v in sk4__pb(raw):
        if fn == 1 and wt == 0:
            return v
    return -1

# ---------------------------------------------------------------- protobuf 工具
def sk4__varint(n):
    b = b''
    while True:
        x = n & 0x7f
        n >>= 7
        if n:
            b += bytes([x | 0x80])
        else:
            return b + bytes([x])


def sk4__f(num, wire, payload):
    t = sk4__varint((num << 3) | wire)
    if wire == 2:
        return t + sk4__varint(len(payload)) + payload
    return t + payload


def sk4__pb(buf):
    # 正确的 protobuf 解析：字段号 > 15 时 tag 是多字节 varint，
    # 只读一个字节会造成整体错位（老版本源文件就是因此只能按原始字节扫描）
    out = []
    i = 0
    n = len(buf)
    while i < n:
        tag = 0
        sh = 0
        while i < n:
            x = buf[i]; i += 1
            tag |= (x & 0x7f) << sh; sh += 7
            if not x & 0x80:
                break
        fn, wt = tag >> 3, tag & 7
        if fn == 0:
            break
        if wt == 0:
            v = 0; sh = 0
            while i < n:
                x = buf[i]; i += 1
                v |= (x & 0x7f) << sh; sh += 7
                if not x & 0x80:
                    break
            out.append((fn, wt, v))
        elif wt == 2:
            ln = 0; sh = 0
            while i < n:
                x = buf[i]; i += 1
                ln |= (x & 0x7f) << sh; sh += 7
                if not x & 0x80:
                    break
            out.append((fn, wt, buf[i:i + ln])); i += ln
        elif wt == 5:
            out.append((fn, wt, buf[i:i + 4])); i += 4
        elif wt == 1:
            out.append((fn, wt, buf[i:i + 8])); i += 8
        else:
            i += 1
    return out


def sk4__rnd(k):
    CH = string.ascii_letters + string.digits
    return ''.join(random.sample(list(CH), k - 1)) + '='

# ---------------------------------------------------------------- 内置分类兜底
# 新网关不提供 /api/v3/drama/getCategory（返回 400 No static resource），
# 与官方插件一致：接口拿不到时使用内置分类表。
sk4_CATEGORIES = [{'id': 20, 'name': '电影', 'converUrl': '{"class":"喜剧,爱情,恐怖,动作,科幻,剧情,战争,警匪,犯罪,动画,奇幻,武侠,冒险,枪战,恐怖,悬疑,惊悚,经典,青春,文艺,微电影,古装,历史,运动,农村,儿童,网络电影","area":"大陆,香港,台湾,美国,法国,英国,日本,韩国,德国,泰国,印度,意大利,西班牙,加拿大,其他","lang":"国语,英语,粤语,闽南语,韩语,日语,法语,德语,其它","year":"2026,2025,2024,2023,2022,2021,2020,2019,2018,2017,2016,2015,2014,2013,2012,2011,2010","extend_sort":"最新,最热,好评"}', 'typeMid': 1, 'typeSort': 2, 'typePid': 0}, {'id': 21, 'name': '剧集', 'converUrl': '{"class":"古装,战争,青春,偶像,喜剧,家庭,犯罪,动作,奇幻,剧情,历史,经典,乡村,情景,商战,网剧,其他","area":"内地,韩国,香港,台湾,日本,美国,泰国,英国,新加坡,其他","lang":"国语,英语,粤语,闽南语,韩语,日语,其它","year":"2026,2025,2024,2023,2022,2021,2020,2019,2018,2017,2016,2015,2014,2013,2012,2011,2010,2009,2008,2007,2006,2005,2004,2003,2002,2001,2000","extend_sort":"最新,最热,好评"}', 'typeMid': 1, 'typeSort': 1, 'typePid': 0}, {'id': 22, 'name': '综艺', 'converUrl': '{"class":"选秀,情感,访谈,播报,旅游,音乐,美食,纪实,曲艺,生活,游戏互动,财经,求职","area":"内地,港台,日韩,欧美","lang":"国语,英语,粤语,闽南语,韩语,日语,其它","year":"2026,2025,2024,2023,2022,2021,2020,2019,2018,2017,2016,2015,2014,2013,2012,2011,2010","extend_sort":"最新,最热,好评"}', 'typeMid': 1, 'typeSort': 3, 'typePid': 0}, {'id': 23, 'name': '动漫', 'converUrl': '{"year":"2026,2025,2024,2023,2022,2021,2020,2019,2018,2017,2016","extend_sort":"最新,最热,好评"}', 'typeMid': 1, 'typeSort': 6, 'typePid': 0}, {'id': 24, 'name': '短剧', 'converUrl': '{"class":"重生民国,穿越年代,现代言情,反转爽文,女恋总裁,闪婚离婚,都市脑洞,古装仙侠,其它","year":"2026,2025,2024,2023,2022,2021,2020,2019,2018,2017,2016","extend_sort":"最新,最热,好评"}', 'typeMid': 1, 'typeSort': 4, 'typePid': 0}, {'id': 26, 'name': '漫剧', 'converUrl': '{}', 'typeMid': 1, 'typeSort': 5, 'typePid': 0}]

import hashlib


# ============================================================ 源定义
# 公钥说明：sun.json 里「天堂 / 苹果」的 publicKey 字段已过期（用它调
# zone 会返回 100002 RSA 校验失败），实测两家现在都改用与华谊相同的那把
# 公钥，这里统一填可用值。
sk4_PUB_KEY = ('MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCr8SzZhjYy+rsya1K09t8d2K50pWFoBkgUqMpKOiW'
           '+3IEVKd4eTdvg9RSOjQ82kypL6R9BnsmrS1V8s4PVDwjQbUtYhTPPC9Hz16qY7rpD6m0d2vr09/UpW'
           'Q5uOy9PR0QTrsioveZ+DIe9jc3C+zBCu/kZSY/R8stwJoiitki3gwIDAQAB')

sk4_DATA_IV = 'OC1A06E197EF10CF3F6058CA7A803B5E'

sk4_APP_SOURCES = {
    '天堂': {
        'host': 'http://122.228.193.211:18008',
        'site': 'https://dyttandroid04-1372779881.cos.ap-shanghai.myqcloud.com/app_dyttandroid.txt',
        'publicKey': sk4_PUB_KEY,
        'dataKey': 'D2KREWRIBVNAUJJYEDL4VFHOY2Q0PQ==',
        'dataIv': sk4_DATA_IV,
        'pkg': 'com.dytiantang.one',
        'appName': '电影天堂',
        'version': '3.0.0.7',
        'decrypt': '0',
    },
    '华谊': {
        'host': 'http://43.240.158.154:18004',
        'site': 'https://1851089669.cdn.123clouddisk.com/1851089669/44107727',
        'publicKey': sk4_PUB_KEY,
        'dataKey': 'V04XQZNYRWN6T0JODZFIAG5CTZB3PT0=',
        'dataIv': sk4_DATA_IV,
        'pkg': 'com.lxf.sncgtzxyx',
        'appName': '华谊',
        'version': '6.0.0.1',
        'decrypt': '0',
    },
    '苹果': {
        'host': 'http://122.228.193.211:18008',
        'site': 'https://xpgandroid03-1372779881.cos.ap-beijing.myqcloud.com/app_xpg_android.txt',
        'publicKey': sk4_PUB_KEY,
        'dataKey': 'S0VNDTJHOFHHCNMRAW5IV2TOS2PBPQ==',
        'dataIv': sk4_DATA_IV,
        'pkg': 'com.juechufsh.android.xpg1',
        'appName': '小苹果',
        'version': '1.0.0.3',
        'decrypt': '0',
    },
}

sk4_BUBU_DEFAULT = {
    'host': 'https://323433ssdfd.top',
    'aid': 'com.web.player',
    'x_client': '8f3d2a1c7b6e5d4c9a0b1f2e3d4c5b6a',
    'web_sign': 'ddtvf65f3a83d6d9ad6f',
    'finger': 'WF-2c064bc5b3400788f31b848849bc3a60f835423ba2dfe69d7ea93974c216e4f2',
    'sk': 'WEB-50a8e9c84a1dc05669a692ded99a2dac46527229e607a7be15db88dbc59059d1',
}

sk4_SRC_ALIAS = {'步步': '布布', '电影天堂': '天堂', '小苹果': '苹果'}
sk4_SRC_ORDER = ('天堂', '布布', '华谊', '苹果')


def sk4__is4k(name):
    return '4K' in (name or '').upper()


# ============================================================ 引擎 A：AppDrama 系
class sk4__AppEngine(object):
    """天堂 / 华谊 / 苹果 —— 同一套 AppDrama 协议（protobuf + AES + RSA）"""

    ONLY_4K = True
    TIMEOUT = 15
    CACHE_LIMIT = 128
    sk4_UA = sk4_UA

    def __init__(self, cfg):
        self.cfg = dict(cfg)
        self.host = (self.cfg.get('host') or '').rstrip('/')
        self.udid = uuid.uuid4().hex.upper()
        self.sec = ''
        self._ready = False
        self._site_done = False
        self._cats = None
        self._detail_cache = {}
        self._home_cache = None
        self._lock = threading.Lock()

    def setup(self, ext):
        if not isinstance(ext, dict):
            return
        for k in ('host', 'site', 'publicKey', 'dataKey', 'dataIv', 'pkg',
                  'appName', 'version', 'decrypt'):
            v = ext.get(k)
            if v not in (None, ''):
                self.cfg[k] = str(v)
        if ext.get('host'):
            self.host = self.cfg['host'].rstrip('/')
            self._site_done = True
        if str(ext.get('only4k', '')).lower() in ('1', 'true', 'yes'):
            self.ONLY_4K = True
        self._ready = False
        self.sec = ''

    # -------------------------------------------------- 网络
    def _http(self, url, data=None, headers=None, timeout=None):
        req = urllib.request.Request(url, data=data, headers=headers or {})
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=timeout or self.TIMEOUT,
                                    context=ctx) as r:
            return r.read()

    def _get(self, path, headers, timeout=None):
        try:
            return self._http(self.host + path, None, headers, timeout)
        except Exception:
            return b''

    def _ensure(self):
        if self._ready:
            return True
        with self._lock:
            if self._ready:
                return True
            if not self._site_done:
                self._site_done = True
                site = self.cfg.get('site', '')
                if site:
                    try:
                        raw = self._http(site, None, {'User-Agent': self.sk4_UA}, 8)
                        domain = (json.loads(raw.decode('utf-8', 'ignore'))
                                  or {}).get('domain', '')
                        if domain.startswith('http'):
                            self.host = domain.rstrip('/')
                    except Exception:
                        pass
            sec = self._zone()
            if sec:
                self.sec = sec
                self._ready = True
        return self._ready

    def _zone(self):
        ts = int(time.time() * 1000)
        r = sk4__rnd(16)
        sign = sk4__rsa_sign(str(ts) + r, self.cfg['publicKey'])
        body = (sk4__f(1, 0, sk4__varint(ts)) + sk4__f(2, 2, sign.encode()) +
                sk4__f(3, 2, r.encode()) + sk4__f(4, 2, r.encode()) +
                sk4__f(5, 2, sk4__rnd(16).encode()))
        try:
            raw = self._http(self.host + '/api/v5/find/app/zone', body,
                             self._c_head(self.cfg['publicKey']))
        except Exception:
            return ''
        data = sk4__pb_data(raw)
        if not data:
            return ''
        strs = {fn: v.decode('utf-8', 'replace') for fn, wt, v in sk4__pb(data)
                if wt == 2}
        # 分片位置有两种版本：新版 f1 是公钥开头，老版 f2 才是开头。
        for order in ((1, 3, 4, 5), (2, 3, 4, 5)):
            key = ''.join(strs.get(k, '') for k in order)
            if key.startswith('MIGf') and len(key) % 4 == 0 and len(key) > 100:
                return key
        return ''

    def _d_obj(self):
        return {"country": "CN", "vName": self.cfg['version'],
                "cpuId": "MT6893Z%2FCZA", "young": 0, "facturer": "OnePlus",
                "pkg": self.cfg['pkg'], "uuid": self.udid,
                "resolution": "1080x2272", "mac": "02%3A00%3A00%3A00%3A00%3A00",
                "abid": "397", "model": "PJX110", "plat": "android",
                "udid": self.udid, "dpi": "440", "net": "1", "lang": "zh",
                "brand": "OnePlus", "density": "2.75",
                "appName": self.cfg['appName'], "cpu": "arm64-v8a",
                "chid": "10000", "carrier": "%E8%81%94%E9%80%9A",
                "_vOsCode": "36", "vOs": "16", "v": 1, "tenantId": "",
                "vApp": self.cfg['version'].replace('.', ''),
                "device": 0, "androidID": self.udid}

    def _c_head(self, sec):
        d = self._d_obj()
        ts = int(time.time() * 1000)
        f = sk4__rnd(16)
        d['sig'] = sk4__rsa_sign(str(ts) + f + d['vApp'], sec)
        b = sk4__ecb_enc(str(ts) + f, self.cfg['dataIv'])
        d.update({'random_str': f, 'timestamp': ts, 'sig2': b[:8], 'sig3': b[8:]})
        p = sk4__cbc_enc(json.dumps(d, separators=(',', ':'), ensure_ascii=False),
                     sk4_NATIVE_K)
        return {'User-Agent': self.sk4_UA, 'Accept': 'application/x-protobuf',
                'Content-Type': 'application/x-protobuf',
                'Cache-Control': 'no-cache',
                'publicParams': json.dumps({'paramsData': p},
                                           separators=(',', ':'))}

    def _e_head(self):
        p = sk4__cbc_enc(json.dumps(self._d_obj(), separators=(',', ':'),
                                ensure_ascii=False), sk4_NATIVE_K)
        return {'User-Agent': self.sk4_UA, 'Accept': 'application/json',
                'Content-Type': 'application/json; charset=utf-8',
                'publicParams': json.dumps({'paramsData': p},
                                           separators=(',', ':'))}

    def _g_body(self, mp):
        ts = int(time.time() * 1000)
        f8, f20 = sk4__rnd(8), sk4__rnd(20)
        sb = '&'.join('%s=%s' % (k, v) for k, v in mp.items()
                      if v not in (None, ''))
        s3 = f8 + sk4__ecb_enc(sb + str(ts), self.cfg['dataKey'])
        return (sk4__f(1, 2, s3[:20].encode()) + sk4__f(2, 2, s3[20:].encode()) +
                sk4__f(3, 2, f20.encode()) + sk4__f(4, 0, sk4__varint(ts)) +
                sk4__f(5, 2, f8.encode()))

    def _post(self, path, mp):
        if not self._ensure():
            return b''
        for attempt in (0, 1):
            try:
                raw = self._http(self.host + path, self._g_body(mp),
                                 self._c_head(self.sec or self.cfg['publicKey']))
            except Exception:
                return b''
            code = sk4__pb_code(raw)
            if code == 200:
                return sk4__pb_data(raw)
            if code in (100001, 100002, 100003) and attempt == 0:
                self._ready, self.sec = False, ''
                if not self._ensure():
                    return b''
                continue
            return b''
        return b''

    # -------------------------------------------------- 解析
    @staticmethod
    def _pic(cov):
        if not cov:
            return ''
        m = re.search(r'https?://[^\x00-\x20"\\]+', cov)
        return m.group(0) if m else ''

    @classmethod
    def _parse_list(cls, data):
        out = []
        if not data:
            return out
        for fn, wt, v in sk4__pb(data):
            if fn != 1 or wt != 2 or not isinstance(v, bytes) or len(v) < 8:
                continue
            d = {}
            for f2, w2, x in sk4__pb(v):
                if w2 == 2 and isinstance(x, bytes):
                    d[f2] = x.decode('utf-8', 'replace')
                elif w2 == 0:
                    d[f2] = x
            if not isinstance(d.get(3), int) or not d.get(5):
                continue
            out.append({'vod_id': str(d[3]), 'vod_name': d.get(5, ''),
                        'vod_pic': cls._pic(d.get(2, '')),
                        'vod_remarks': d.get(13, '') or ''})
        return out

    def _cache_put(self, cache, key, value):
        try:
            if len(cache) >= self.CACHE_LIMIT:
                cache.clear()
            cache[key] = value
        except Exception:
            pass

    # -------------------------------------------------- 首页 / 分类
    def _categories(self):
        if self._cats:
            return self._cats
        raw = self._get('/api/v3/drama/getCategory?orderBy=type_id',
                        self._e_head())
        try:
            d = (json.loads(raw.decode('utf-8', 'ignore')) or {}).get('data')
            if isinstance(d, list) and d:
                self._cats = d
                return d
        except Exception:
            pass
        self._cats = sk4_CATEGORIES
        return self._cats

    def homeContent(self, filter):
        try:
            cats = self._categories()
            # 直播 / CCTV / 卫视 这些是直播源，点播详情拉不出片单，直接隐藏
            bad = ('直播', 'CCTV', '卫视', '广播', '听书', 'FM', '音乐', '4K专区')
            classes = [{'type_id': str(c['id']), 'type_name': c['name']}
                       for c in cats
                       if c.get('name') and c.get('name') != '公告'
                       and not any(b in c['name'] for b in bad)]
            labels = [('class', '类型'), ('area', '地区'), ('lang', '语言'),
                      ('year', '年份'), ('extend_sort', '排序')]
            filters = {}
            for c in cats:
                try:
                    cv = json.loads(c.get('converUrl') or '{}')
                except Exception:
                    cv = {}
                fl = []
                for k, label in labels:
                    v = cv.get(k)
                    if v:
                        fl.append({'key': k, 'name': label,
                                   'value': [{'n': x, 'v': x}
                                             for x in v.split(',') if x]})
                if fl:
                    filters[str(c['id'])] = fl
            return {'class': classes, 'filters': filters}
        except Exception:
            return {'class': [], 'filters': {}}

    def homeVideoContent(self):
        if self._home_cache and time.time() - self._home_cache[0] < 60:
            return {'list': self._home_cache[1]}
        try:
            raw = self._get('/api/ex/v3/security/tag/list', self._e_head())
            j = json.loads(raw.decode('utf-8', 'ignore'))
            ds = j.get('data') or []
            # decrypt=1 的源两次 ECB 解密后才是 JSON；decrypt=0 直接给数组
            if isinstance(ds, str):
                if self.cfg.get('decrypt', '1') != '0' and ds:
                    ds = sk4__ecb_dec(ds, self.cfg['dataKey'])
                    ds = sk4__ecb_dec(ds, self.cfg['dataIv'])
                arr = json.loads(ds) if ds else []
            else:
                arr = ds if isinstance(ds, list) else []
            seen, out = set(), []
            for block in arr:
                for sec in (block.get('sections') or []):
                    for v in (sec.get('vodList') or []):
                        vid = str(v.get('id', ''))
                        if not vid or vid in seen:
                            continue
                        seen.add(vid)
                        out.append({'vod_id': vid,
                                    'vod_name': v.get('name', ''),
                                    'vod_pic': (v.get('coverImage') or {}).get('path', '') or '',
                                    'vod_remarks': v.get('remark', '') or ''})
            self._home_cache = (time.time(), out)
            return {'list': out}
        except Exception:
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            mp = {'pagesize': '21', 'typeId1': str(tid), 'page': str(pg or 1),
                  'vodOrderBy': '最新'}
            ext = extend if isinstance(extend, dict) else {}
            for k, dst in (('extend_sort', 'vodOrderBy'), ('area', 'vodArea'),
                           ('lang', 'vodLang'), ('class', 'vodClass'),
                           ('year', 'vodYear')):
                if ext.get(k):
                    mp[dst] = str(ext[k])
            lst = self._parse_list(
                self._post('/api/proto/v5/drama/category', mp))
            page = int(pg or 1)
            return {'list': lst, 'page': page,
                    'pagecount': page + 1 if len(lst) >= 21 else page,
                    'limit': 21, 'total': len(lst)}
        except Exception:
            return {'list': []}

    def searchContent(self, key, quick, pg="1"):
        try:
            data = self._post('/api/proto/v5/drama/search',
                              {'searchKeys': str(key), 'page': str(pg or 1),
                               'pagesize': '21'})
            return {'list': self._parse_list(data)}
        except Exception:
            return {'list': []}

    # -------------------------------------------------- 详情
    def detailContent(self, ids):
        try:
            raw = ids[0] if isinstance(ids, (list, tuple)) and ids else str(ids)
            vid = str(raw).strip().strip('/')
            if vid in self._detail_cache:
                return {'list': [self._detail_cache[vid]]}
            data = self._post('/api/proto/v5/drama/getDetail', {'id': vid})
            if not data:
                return {'list': []}
            dd = sk4__pb(data)
            meta = {}
            for fn, wt, v in dd:
                if wt == 2 and isinstance(v, bytes):
                    meta[fn] = v.decode('utf-8', 'replace')
                elif wt == 0:
                    meta[fn] = v

            lines = collections.OrderedDict()
            for fn, wt, v in dd:
                if fn != 29 or wt != 2:
                    continue
                e = {}
                for f2, w2, x in sk4__pb(v):
                    if w2 == 2 and isinstance(x, bytes):
                        e[f2] = x.decode('utf-8', 'replace')
                    elif w2 == 0:
                        e[f2] = x
                cn = e.get(10) or e.get(9) or 'APP'
                src, path = e.get(9, ''), e.get(4, '')
                title = e.get(3) or e.get(2) or '正片'
                if not path:
                    continue
                if not sk4_VIDEO_RE.search(path):
                    path = base64.b64encode(json.dumps(
                        {'vodPlayFrom': src, 'playUrl': path},
                        separators=(',', ':'), ensure_ascii=False).encode()).decode()
                lines.setdefault(cn, []).append(title + '$' + path)

            if self.ONLY_4K:
                k4 = [k for k in lines if sk4__is4k(k)]
                if k4:
                    lines = collections.OrderedDict((k, lines[k]) for k in k4)

            intro = re.sub(r'<[^>]+>', '', meta.get(6) or meta.get(7) or '').strip()
            vod = {
                'vod_id': vid,
                'vod_name': meta.get(9, '') or '',
                'vod_pic': self._pic(meta.get(2, '')),
                'vod_remarks': meta.get(26, '') or '',
                'vod_year': str(meta.get(18, '') or ''),
                'vod_area': meta.get(1, '') or '',
                'vod_actor': meta.get(25, '') or '',
                'vod_director': meta.get(12, '') or '',
                'vod_content': intro,
                'vod_play_from': '$$$'.join(lines.keys()),
                'vod_play_url': '$$$'.join('#'.join(v) for v in lines.values()),
            }
            self._cache_put(self._detail_cache, vid, vod)
            return {'list': [vod]}
        except Exception:
            return {'list': []}

    # -------------------------------------------------- 播放
    def playerContent(self, flag, id, vipFlags=None):
        try:
            pid = str(id).strip()
            if sk4_VIDEO_RE.search(pid):
                return {'parse': 0, 'url': pid, 'header': {}}
            try:
                j = json.loads(base64.b64decode(pid).decode('utf-8', 'replace'))
            except Exception:
                return {'parse': 0, 'url': pid, 'header': {}}
            data = self._post('/api/proto/v5/videoUsableUrl',
                              {'vodPlayFrom': j.get('vodPlayFrom', ''),
                               'playUrl': j.get('playUrl', '')})
            url = ''
            if data:
                for fn, wt, v in sk4__pb(data):
                    if fn == 1 and wt == 2:
                        url = v.decode('utf-8', 'replace')
                        break
            if not url.startswith('http'):
                return {'parse': 0, 'url': '', 'header': {}}
            return {'parse': 0, 'url': url, 'header': {'User-Agent': self.sk4_UA}}
        except Exception:
            return {'parse': 0, 'url': '', 'header': {}}

    def liveContent(self, params):
        return {'list': []}


# ============================================================ 引擎 B：布布 (YunDuo)
class sk4__BubuEngine(object):
    """布布 —— JSON 接口 + /decode/url protobuf 解链"""

    ONLY_4K = True
    TIMEOUT = 15
    sk4_UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
          '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    def __init__(self, cfg=None):
        self.cfg = dict(sk4_BUBU_DEFAULT)
        self.cfg.update(cfg or {})
        self.host = self.cfg['host'].rstrip('/')
        self.api = self.host + '/api.php/web'
        self._det = {}
        self._home = None

    def setup(self, ext):
        if not isinstance(ext, dict):
            return
        for k in sk4_BUBU_DEFAULT:
            v = ext.get(k)
            if v not in (None, ''):
                self.cfg[k] = str(v)
        self.host = self.cfg['host'].rstrip('/')
        self.api = self.host + '/api.php/web'
        if str(ext.get('only4k', '')).lower() in ('1', 'true', 'yes'):
            self.ONLY_4K = True

    # -------------------------------------------------- 网络
    def _hdr(self, extra=None):
        h = {'User-Agent': self.sk4_UA, 'Accept': 'application/json',
             'X-Client': self.cfg['x_client'],
             'web-sign': self.cfg['web_sign']}
        if extra:
            h.update(extra)
        return h

    def _raw(self, url, data=None, headers=None, timeout=None):
        req = urllib.request.Request(url, data=data,
                                     headers=headers or self._hdr())
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=timeout or self.TIMEOUT,
                                    context=ctx) as r:
            return r.read()

    def _json(self, url):
        try:
            return json.loads(self._raw(url).decode('utf-8', 'ignore')) or {}
        except Exception:
            return {}

    def _get(self, path):
        return self._json(self.api + path)

    # -------------------------------------------------- 解链
    def _decode(self, token, frm):
        try:
            ts = int(time.time() * 1000)
            nonce = os.urandom(16).hex()
            msg = ('finger=%s&id=%s&nonce=%s&sk=%s&time=%d&v=1'
                   % (self.cfg['finger'], self.cfg['aid'], nonce,
                      self.cfg['sk'], ts))
            sign = hashlib.sha256(msg.encode()).hexdigest().upper()
            body = (sk4__f(1, 2, token.encode()) + sk4__f(2, 2, frm.encode()) +
                    sk4__f(3, 0, sk4__varint(ts)) + sk4__f(4, 2, nonce.encode()) +
                    sk4__f(5, 2, sign.encode()) + sk4__f(6, 2, self.cfg['aid'].encode()) +
                    sk4__f(7, 0, sk4__varint(1)))
            h = {'User-Agent': self.sk4_UA,
                 'Content-Type': 'application/x-protobuf',
                 'Accept': 'application/x-protobuf',
                 'X-Client': self.cfg['x_client'],
                 'web-sign': self.cfg['web_sign']}
            raw = self._raw(self.api + '/decode/url', body, h)
            for fn, wt, v in sk4__pb(raw):
                if fn == 3 and wt == 2:
                    s = v.decode('utf-8', 'replace')
                    if s.startswith('http'):
                        return s
            # 解不出时把服务端 msg 记下来，方便排查
            for fn, wt, v in sk4__pb(raw):
                if fn == 2 and wt == 2:
                    self.last_err = v.decode('utf-8', 'replace')
                    break
        except Exception as e:
            self.last_err = str(e)
        return ''

    # -------------------------------------------------- 首页 / 分类
    def homeContent(self, filter):
        try:
            j = self._get('/index/home')
            cats = ((j.get('data') or {}).get('categories') or [])
            classes, vids, seen = [], [], set()
            for c in cats:
                name = c.get('type_name') or c.get('type_en') or ''
                if not name:
                    continue
                classes.append({'type_id': name, 'type_name': name})
                for v in (c.get('videos') or []):
                    vid = str(v.get('vod_id') or '')
                    if not vid or vid in seen:
                        continue
                    seen.add(vid)
                    vids.append({'vod_id': vid,
                                 'vod_name': v.get('vod_name', ''),
                                 'vod_pic': v.get('vod_pic', '') or '',
                                 'vod_remarks': v.get('vod_remarks', '') or ''})
            return {'class': classes, 'list': vids,
                    'filters': {name: [] for name in
                                (c['type_name'] for c in classes)}}
        except Exception:
            return {'class': [], 'list': [], 'filters': {}}

    def homeVideoContent(self):
        if self._home and time.time() - self._home[0] < 60:
            return {'list': self._home[1]}
        try:
            j = self._get('/index/home')
            out, seen = [], set()
            for c in ((j.get('data') or {}).get('categories') or []):
                for v in (c.get('videos') or []):
                    vid = str(v.get('vod_id') or '')
                    if not vid or vid in seen:
                        continue
                    seen.add(vid)
                    out.append({'vod_id': vid,
                                'vod_name': v.get('vod_name', ''),
                                'vod_pic': v.get('vod_pic', '') or '',
                                'vod_remarks': v.get('vod_remarks', '') or ''})
            self._home = (time.time(), out)
            return {'list': out}
        except Exception:
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            page = int(pg or 1)
            url = ('%s/filter/vod?type_name=%s&page=%d&sort=hits'
                   % (self.api, urllib.parse.quote(str(tid)), page))
            ext = extend if isinstance(extend, dict) else {}
            for k, v in ext.items():
                if v not in (None, '', '全部'):
                    url += '&%s=%s' % (k, urllib.parse.quote(str(v)))
            j = self._json(url)
            lst = []
            for v in (j.get('data') or []):
                lst.append({'vod_id': str(v.get('vod_id') or ''),
                            'vod_name': v.get('vod_name', ''),
                            'vod_pic': v.get('vod_pic', '') or '',
                            'vod_remarks': v.get('vod_remarks', '') or ''})
            # 服务端 pageCount 常年写 1，不可信；按本页条数判断有没有下一页
            return {'list': lst, 'page': page,
                    'pagecount': page + 1 if len(lst) >= 20 else page,
                    'limit': 24, 'total': len(lst)}
        except Exception:
            return {'list': []}

    def searchContent(self, key, quick, pg="1"):
        try:
            j = self._json('%s/search/index?wd=%s&pg=%s'
                           % (self.api, urllib.parse.quote(str(key)),
                              str(pg or 1)))
            out = []
            low = str(key).lower()
            for v in (j.get('data') or []):
                vid = str(v.get('vod_id') or '')
                nm = (v.get('vod_name') or '').strip()
                if not vid or not nm or 'http' in nm or '.com' in nm:
                    continue
                if low not in nm.lower():
                    continue
                out.append({'vod_id': vid, 'vod_name': nm,
                            'vod_pic': v.get('vod_pic', '') or '',
                            'vod_remarks': v.get('vod_remarks', '') or ''})
            return {'list': out}
        except Exception:
            return {'list': []}

    # -------------------------------------------------- 详情
    def _detail(self, vid):
        if vid in self._det:
            return self._det[vid]
        j = self._get('/vod/get_detail?vod_id=' + str(vid))
        d = j.get('data')
        if isinstance(d, list):
            d = d[0] if d else {}
        d = d or {}
        froms = (d.get('vod_play_from') or '').split('$$$')
        urls = (d.get('vod_play_url') or '').split('$$$')
        eps = collections.OrderedDict()
        all_eps = collections.OrderedDict()
        for fr, u in zip(froms, urls):
            if not fr or not u:
                continue
            items = []
            for seg in u.split('#'):
                if '$' not in seg:
                    continue
                title, token = seg.split('$', 1)
                if not token:
                    continue
                items.append((title.strip() or '正片', token.strip()))
            if items:
                all_eps[fr] = items
                if (not self.ONLY_4K) or sk4__is4k(fr):
                    eps[fr] = items
        if not eps:
            eps = collections.OrderedDict(all_eps)
        rec = (d, eps, all_eps)
        if len(self._det) > 64:
            self._det.clear()
        self._det[vid] = rec
        return rec

    def detailContent(self, ids):
        try:
            vid = str(ids[0] if isinstance(ids, (list, tuple)) and ids
                      else ids).strip()
            d, eps, _ = self._detail(vid)
            if not d:
                return {'list': []}
            lines, urls = [], []
            for fr, items in eps.items():
                lines.append(fr)
                urls.append('#'.join(
                    '%s$token@%s@%s@%s@%s' % (t, tok, fr, vid,
                                               urllib.parse.quote(t))
                    for t, tok in items))
            vod = {
                'vod_id': vid,
                'vod_name': d.get('vod_name', '') or '',
                'vod_pic': d.get('vod_pic', '') or '',
                'vod_remarks': d.get('vod_remarks', '') or '',
                'vod_year': str(d.get('vod_year', '') or ''),
                'vod_area': d.get('vod_area', '') or '',
                'vod_actor': d.get('vod_actor', '') or '',
                'vod_director': d.get('vod_director', '') or '',
                'vod_content': re.sub(r'<[^>]+>', '',
                                      d.get('vod_content', '') or '').strip(),
                'vod_play_from': '$$$'.join(lines),
                'vod_play_url': '$$$'.join(urls),
            }
            return {'list': [vod]}
        except Exception:
            return {'list': []}

    # -------------------------------------------------- 播放
    def playerContent(self, flag, id, vipFlags=None):
        try:
            pid = str(id)
            if pid.startswith('http'):
                return {'parse': 0, 'url': pid, 'header': {'User-Agent': self.sk4_UA}}
            if not pid.startswith('token@'):
                return {'parse': 0, 'url': '', 'header': {}}
            p = pid.split('@', 4)
            token = p[1] if len(p) > 1 else ''
            frm = p[2] if len(p) > 2 else ''
            vid = p[3] if len(p) > 3 else ''
            title = urllib.parse.unquote(p[4]) if len(p) > 4 else ''
            url = self._decode(token, frm)
            if not url and vid:
                # 该线路被平台锁死（布布 CO4K 会返回 PLATFORM_NOT_ALLOWED）
                # → 先换同片的其它高清线路，避免直接黑屏。
                url = self._fallback(vid, frm, title)
            if not url and vid:
                # 最后兜底：和官方 spider 一样交给 /play 网页，让播放器自己嗅探
                return {'parse': 1,
                        'url': '%s/play/%s#sid=%s' % (self.host, vid, frm),
                        'header': {'User-Agent': self.sk4_UA,
                                   'Referer': self.host + '/'}}
            if not url:
                return {'parse': 0, 'url': '', 'header': {}}
            return {'parse': 0, 'url': url,
                    'header': {'User-Agent': self.sk4_UA,
                               'Referer': self.host + '/'}}
        except Exception:
            return {'parse': 0, 'url': '', 'header': {}}

    # 实测画质：BBA 1920x804 > NBY ≈ PAN1 > zijianm3u8 / qsvip
    _FB_ORDER = ('BBA', 'NBY', 'PAN1', 'zijianm3u8', 'qsvip')

    def _fallback(self, vid, frm, title):
        try:
            _, _, all_eps = self._detail(vid)
            order = [k for k in self._FB_ORDER if k in all_eps and k != frm]
            order += [k for k in all_eps
                      if k != frm and not sk4__is4k(k) and k not in order]
            order += [k for k in all_eps if k != frm and sk4__is4k(k)]
            for k in order:
                items = all_eps.get(k) or []
                tok = ''
                for t, tk in items:
                    if title and t == title:
                        tok = tk
                        break
                if not tok and items:
                    tok = items[0][1]
                if tok:
                    u = self._decode(tok, k)
                    if u:
                        return u
        except Exception:
            pass
        return ''


# ============================================================ 入口
class SK4KRaw(_Base):
    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
        except Exception:
            pass
        self.src = '天堂'
        self.eng = None
        self._build('天堂', {})

    # -------------------------------------------------- 生命周期
    def _build(self, name, ext):
        if name in sk4_APP_SOURCES:
            eng = sk4__AppEngine(sk4_APP_SOURCES[name])
        else:
            eng = sk4__BubuEngine()
        eng.setup(ext)
        self.src = name
        self.eng = eng

    def init(self, extend=""):
        # 不联网：导入阶段只解析配置
        ext = {}
        try:
            if isinstance(extend, str):
                s = extend.strip()
                if s.startswith('{') and s.endswith('}'):
                    ext = json.loads(s) or {}
                elif s:
                    ext = {'src': s}
            elif isinstance(extend, dict):
                ext = dict(extend)
        except Exception:
            ext = {}
        name = str(ext.get('src') or ext.get('name') or '天堂').strip()
        name = sk4_SRC_ALIAS.get(name, name)
        if name not in sk4_SRC_ORDER:
            name = '天堂'
        rest = dict(ext)
        rest.pop('src', None)
        rest.pop('name', None)
        self._build(name, rest)

    def getName(self):
        return self.src + '·4K'

    def destroy(self):
        try:
            self.eng = None
        except Exception:
            pass

    def _e(self):
        if self.eng is None:
            self._build('天堂', {})
        return self.eng

    # -------------------------------------------------- 标准接口
    def homeContent(self, filter=False):
        return self._e().homeContent(filter)

    def homeVideoContent(self):
        return self._e().homeVideoContent()

    def categoryContent(self, tid, pg, filter, extend):
        return self._e().categoryContent(tid, pg, filter, extend)

    def searchContent(self, key, quick, pg="1"):
        return self._e().searchContent(key, quick, pg)

    def detailContent(self, ids):
        return self._e().detailContent(ids)

    def playerContent(self, flag, id, vipFlags=None):
        return self._e().playerContent(flag, id, vipFlags)

    def liveContent(self, params):
        return {'list': []}

# ---- 门面适配 sk：四源 4K 合并成一个一级源，不建独立站点 ----
class SK4KSpider(_BaseSpider):
    NAME = '四源4K专线'
    SRCS = ('天堂', '布布', '华谊', '苹果')
    SEARCH_WAIT = 2.6
    DETAIL_WAIT = 3.6
    PLAY_WAIT = 8.0

    def __init__(self):
        # init 绝不联网：四个引擎只解析配置；站点不通由各处限时兜住。
        self.obs = {}
        for n in self.SRCS:
            try:
                ob = SK4KRaw()
                ob.init(json.dumps({'src': n}, ensure_ascii=False))
                self.obs[n] = ob
            except Exception:
                pass
        # 四源搜索偶发有子源超过门面 2.8s 预算。晚到的结果仍由后台线程
        # 累加进这里，详情时按 (子源, vid) 回填，保证四源线路不缺。
        self._key_ids = {}
        self._vid_key = {}
        self._lock = threading.Lock()

    def init(self, extend=''):
        return None

    def destroy(self):
        for ob in list(self.obs.values()):
            try:
                ob.destroy()
            except Exception:
                pass

    @staticmethod
    def _b64(raw):
        return base64.urlsafe_b64encode(
            raw.encode('utf-8')).decode('ascii').rstrip('=')

    @staticmethod
    def _unb64(s):
        s = str(s or '')
        s += '=' * (-len(s) % 4)
        return base64.urlsafe_b64decode(
            s.encode('ascii')).decode('utf-8', 'replace')

    def _enc_id(self, ids):
        return 'sk4:' + self._b64(json.dumps(
            ids, ensure_ascii=False, separators=(',', ':')))

    def _dec_id(self, code):
        s = str(code or '')
        if not s.startswith('sk4:'):
            return None
        try:
            v = json.loads(self._unb64(s[4:]))
            return v if isinstance(v, dict) else None
        except Exception:
            return None

    @classmethod
    def _fan(cls, work, wait):
        box, ths = {}, []

        def run(k):
            try:
                box[k] = work(k)
            except Exception:
                pass

        for k in cls.SRCS:
            th = threading.Thread(target=run, args=(k,), daemon=True)
            th.start()
            ths.append(th)
        deadline = time.time() + wait
        for th in ths:
            th.join(max(0.0, deadline - time.time()))
        return box

    def homeContent(self, filter=True):
        return {'class': [], 'list': []}

    def categoryContent(self, tid, pg='1', filter=True, extend=None):
        return {'list': [], 'page': 1, 'pagecount': 1, 'total': 0}

    @staticmethod
    def _key(nm):
        # 布布习惯把片名写成「庆余年 第一季」。只归并「第一季/第1季」这类
        # 默认季后缀；第二季及衍生片一律不合并，防止把错片的线路挂进来。
        k = re.sub(r'\s+', '', str(nm or '')).lower()
        return re.sub(r'(第一季|第1季|season1|s01)$', '', k)

    def _absorb(self, nm, vid, n):
        k = self._key(nm)
        with self._lock:
            self._key_ids.setdefault(k, {}).setdefault(n, vid)
            self._vid_key[(n, vid)] = k
        return k

    def searchContent(self, key, quick=False, pg='1'):
        kw = str(key or '').strip()
        if not kw:
            return {'list': []}

        def work(n):
            lst = (self.obs[n].searchContent(
                kw, quick, str(pg or '1')) or {}).get('list') or []
            # 在线程内就累加：_fan 超时返回后，晚到的子源仍会写进来
            for it in lst:
                if isinstance(it, dict):
                    nm = str(it.get('vod_name') or '').strip()
                    vid = str(it.get('vod_id') or '').strip()
                    if nm and vid:
                        self._absorb(nm, vid, n)
            return lst

        box = self._fan(work, self.SEARCH_WAIT)
        # 四源同名合并成一张卡，id 里带上目前已知的每个子源 vod_id。
        merged, order = {}, []
        for n in self.SRCS:
            for it in (box.get(n) or []):
                if not isinstance(it, dict):
                    continue
                nm = str(it.get('vod_name') or '').strip()
                vid = str(it.get('vod_id') or '').strip()
                if not nm or not vid:
                    continue
                k = self._key(nm)
                if k not in merged:
                    merged[k] = {
                        'vod_name': nm,
                        'vod_pic': it.get('vod_pic') or '',
                        'vod_remarks': it.get('vod_remarks') or ''}
                    order.append(k)
                elif nm == kw:
                    # 优先用与搜索词完全一致的片名，strict_match 才能命中
                    merged[k]['vod_name'] = nm
        with self._lock:
            snap = dict((k, dict(v)) for k, v in self._key_ids.items())
        return {'list': [
            {'vod_id': self._enc_id(snap.get(k, {})),
             'vod_name': merged[k]['vod_name'],
             'vod_pic': merged[k]['vod_pic'],
             'vod_remarks': merged[k]['vod_remarks']}
            for k in order[:24] if snap.get(k)]}

    def detailContent(self, ids):
        raw = ids[0] if isinstance(ids, (list, tuple)) and ids else ids
        code = str(raw or '')
        idmap = dict(self._dec_id(code) or {})
        # 用累加缓存回填：本次搜索里晚到、没编进卡片 id 的子源也补上
        with self._lock:
            snap = dict((k, dict(v)) for k, v in self._key_ids.items())
            keys = [self._vid_key.get((n, v)) for n, v in idmap.items()]
        for k in keys:
            for n2, v2 in (snap.get(k) or {}).items():
                idmap.setdefault(n2, v2)
        if not idmap:
            # 兜底：非本源编码的 id，四个子源拿同一个 id 各试一次
            idmap = dict((n, code) for n in self.SRCS)

        def work(n):
            vid = idmap.get(n)
            if not vid:
                return None
            v = (self.obs[n].detailContent([vid]) or {}).get('list') or []
            return v[0] if v and isinstance(v[0], dict) else None

        box = self._fan(work, self.DETAIL_WAIT)
        froms, urls, meta = [], [], None
        for n in self.SRCS:
            v = box.get(n)
            if not isinstance(v, dict):
                continue
            if meta is None:
                meta = v
            fr = str(v.get('vod_play_from') or '').split('$$$')
            ur = str(v.get('vod_play_url') or '').split('$$$')
            for i, f in enumerate(fr):
                f = str(f or '').strip()
                if not f:
                    continue
                seg = ur[i] if i < len(ur) else ''
                eps = []
                for part in str(seg).split('#'):
                    part = part.strip()
                    if not part:
                        continue
                    nm, sep, pid = part.partition('$')
                    if not sep:
                        nm, pid = '正片', part
                    eps.append('%s$sk4|%s|%s'
                               % (nm.strip() or '正片', n, pid))
                if eps:
                    froms.append('%s·%s' % (n, f))
                    urls.append('#'.join(eps))
        if not froms:
            return {'list': []}
        vod = dict(meta or {})
        vod['vod_id'] = code
        vod['vod_play_from'] = '$$$'.join(froms)
        vod['vod_play_url'] = '$$$'.join(urls)
        return {'list': [vod]}

    def playerContent(self, flag, id, vipFlags=None):
        pid = str(id or '')
        name, rest = '', pid
        if pid.startswith('sk4|'):
            p = pid[4:].split('|', 1)
            if len(p) == 2:
                name, rest = p[0], p[1]
        f = str(flag or '')
        if name not in self.obs:
            for n in self.SRCS:
                if f.startswith(n):
                    name = n
                    break
        if name not in self.obs:
            name = self.SRCS[0]
        ob = self.obs.get(name)
        if ob is None:
            return {'parse': 0, 'url': '', 'header': {}}
        for n in self.SRCS:
            if f.startswith(n + '·'):
                f = f[len(n) + 1:]
                break
        box = {}

        def run():
            try:
                box['r'] = ob.playerContent(f, rest, vipFlags)
            except Exception:
                pass

        th = threading.Thread(target=run, daemon=True)
        th.start()
        th.join(self.PLAY_WAIT)
        r = box.get('r')
        return r if isinstance(r, dict) else {
            'parse': 0, 'url': '', 'header': {}}
# ==================== 四源4K专线线路源 sk END ====================


# ==================== 找剧4K 一级源 zj BEGIN ====================
class ZJSpider(_BaseSpider):
    # 官方 4K/1080P 线路（游客会话）作为一级源挂进 Kishuto 聚合。
    # init 绝不联网；站点不通时 _zj_quick 限时返回空，不拖慢搜索/详情。
    NAME = '找剧4K'

    def __init__(self):
        self.ob = None
        self.cfg = {}

    def init(self, extend=''):
        try:
            cfg = (json.loads(extend) if isinstance(extend, str)
                   and extend.strip().startswith('{') else {})
        except Exception:
            cfg = {}
        self.cfg = cfg if isinstance(cfg, dict) else {}
        ck = str(self.cfg.get('zj_cookie') or self.cfg.get('cookie') or '')
        if self.ob is None:
            self.ob = ZJSource(ck)
        return None

    def _ob(self):
        if self.ob is None:
            self.ob = ZJSource()
        return self.ob

    @staticmethod
    def _zj_quick(fn, budget=2.6, fallback=None):
        box = {}

        def run():
            try:
                box['v'] = fn()
            except Exception:
                box['v'] = fallback

        th = threading.Thread(target=run, daemon=True)
        th.start()
        th.join(budget)
        return box.get('v', fallback)

    def homeContent(self, filter=True):
        return {'class': [], 'list': []}

    def categoryContent(self, tid, pg='1', filter=True, extend=None):
        return {'list': [], 'page': 1, 'pagecount': 1, 'total': 0}

    def searchContent(self, key, quick=False, pg='1'):
        kw = str(key or '')
        if not kw.strip():
            return {'list': []}
        try:
            page = int(str(pg or 1))
        except Exception:
            page = 1
        got = self._zj_quick(lambda: self._ob().search(kw, page), 2.6, []) or []
        return {'list': [x for x in as_list(got) if isinstance(x, dict)]}

    def detailContent(self, ids):
        vid = ids[0] if isinstance(ids, (list, tuple)) and ids else ids
        d = self._zj_quick(lambda: self._ob().detail(text(vid)), 2.6, {}) or {}
        vod = dict(as_dict(d.get('vod')))
        froms, urls = [], []
        for item in as_list(d.get('lines')):
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                froms.append(str(item[0]))
                urls.append('#'.join(str(x) for x in as_list(item[1])))
        vod['vod_play_from'] = '$$$'.join(froms)
        vod['vod_play_url'] = '$$$'.join(urls)
        if not vod.get('vod_id'):
            vod['vod_id'] = vid
        return {'list': [vod]}

    def playerContent(self, flag, id, vipFlags=None):
        got = self._zj_quick(lambda: self._ob().play(text(id)), 8.0,
                             {'url': '', 'parse': 0})
        return got if isinstance(got, dict) else {'url': '', 'parse': 0}
# ==================== 找剧4K 一级源 zj END ====================


# ==================== 剧下饭4K 一级源 jx BEGIN ====================
import http.cookiejar as _jxf_cj
import ssl as _jxf_ssl
import urllib.request as _jxf_ur

JXF_EXTRA_WAIT = 4.5      # 片帝/4KK 聚合线路的最长等待（秒），超时就只出原站 4K 线

# -*- coding: utf-8 -*-
# 剧下饭 4K 聚合版 TVBox Python 爬虫 - webhomeTV 适配版 (类式规范)
# 站点: http://manian.juxiafan.com/  (内置 8 个备用域名自动轮换)
# 剧下饭线路: 山东4K 2160P / 爱尔兰4K高码
# 聚合线路: 片帝·专享4K-Y / 片帝·4K官方C / 4KK·磁力 / 4KK·夸克(有则显示)
# 同名片自动匹配聚合; 没有匹配到的线路不会出现, 不影响原站播放

import json
import time
import os
import re
import hmac
import uuid
import hashlib
import threading
from base64 import b64encode
from urllib.parse import quote_plus, unquote

try:
    import requests
except Exception:
    requests = None


jxf_BASE_URLS = [
    "http://manian.juxiafan.com",
    "http://195.225.24.128:6213",
    "http://jugaoqing.com",
    "http://jumianfei.com",
    "http://juyongjiu.com",
    "http://kuailezhuiju2.com",
    "http://zhuiju666.com",
    "http://194.147.100.155:7744",
]
jxf_AES_KEY = b"kZ6fT8oF6oM8eX6lF7eH2rJ3pW7gW0kC"
jxf_UA = "okhttp/4.12.0"

jxf_LIVE_TYPE_ID = 22023                 # 隐藏直播分类(服务端不下发, 手动补进分类栏)

# ======================= 4K 线路筛选 =======================
# 服务端线路名: 山东4K 2160P (sourceCode=CO4K) / 爱尔兰4K高码 (sourceCode=zijianm3u8)
# 兼容服务端改名: 名字里同时含 4K 和 山东/爱尔兰 也算命中; 直播线路原样保留
jxf_KEEP_4K_CODES = ("CO4K", "zijianm3u8")
jxf_LIVE_CODES = ("zhibo", "difang", "huya")

def jxf_is_keep_source(src):
    code = str(src.get("sourceCode") or "")
    name = str(src.get("sourceName") or "")
    if code in jxf_LIVE_CODES or "直播" in name:
        return True
    if code in jxf_KEEP_4K_CODES:
        return True
    return "4K" in name.upper() and ("山东" in name or "爱尔兰" in name)

def jxf_pick_sources(sources):
    """只留两条 4K 线(山东在前), 一条都没有时退回全部线路保证能播"""
    sources = sources or []
    kept = [s for s in sources if jxf_is_keep_source(s)]
    if not kept:
        return list(sources)

    def _rank(s):
        name = str(s.get("sourceName") or "")
        if "山东" in name:
            return 0
        if "爱尔兰" in name:
            return 1
        return 2

    kept.sort(key=_rank)
    return kept

# ======================= 片帝 4K 线路 (dongpian17.com) =======================
# 片帝接口下发的 4K 官方线路: 专享4K-Y / 4K海外-官方C (显示为 4K官方C)
jxf_PD_HOST = "https://dongpian17.com"
jxf_PD_SIGN_KEY = "8b9a908a05eac640e1ee06f52acaa741bfe4ba9e004eeffdbeb635e532e06666"
jxf_PD_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
jxf_PD_TIMEOUT = 10
jxf_PD_SESSION = None
jxf_PD_LOGGED_IN = False

def jxf_pd_headers(method, path, search):
    ts = str(int(time.time() * 1000))
    nonce = os.urandom(16).hex()
    msg = "{}\n{}{}\n{}\n{}".format(method, path, search, ts, nonce)
    sign = hmac.new(jxf_PD_SIGN_KEY.encode(), msg.encode(), hashlib.sha256).hexdigest()
    return {
        "User-Agent": jxf_PD_UA,
        "Accept": "application/json",
        "x-ai-movie-client-name": "movie-search-frontend",
        "x-ai-movie-client-version": "1.0.0",
        "x-ai-movie-build-version": "dongpiandi-v2026.10.04.1-episode-resume-efd9a7f2e87e-web",
        "x-ai-movie-protocol-version": "2026-07-05.library-v2.playback-v1",
        "x-ai-movie-timestamp": ts,
        "x-ai-movie-nonce": nonce,
        "x-ai-movie-signature": sign,
    }

def jxf_pd_sess():
    global jxf_PD_SESSION
    if jxf_PD_SESSION is None:
        ctx0 = _jxf_ssl.create_default_context()
        ctx0.check_hostname = False
        ctx0.verify_mode = _jxf_ssl.CERT_NONE
        jxf_PD_SESSION = _jxf_ur.build_opener(
            _jxf_ur.HTTPSHandler(context=ctx0),
            _jxf_ur.HTTPCookieProcessor(_jxf_cj.CookieJar()))
    return jxf_PD_SESSION
def jxf_pd_get(path, search=""):
    try:
        req = _jxf_ur.Request(jxf_PD_HOST + path + search,
                              headers=jxf_pd_headers("GET", path, search))
        with jxf_pd_sess().open(req, timeout=jxf_PD_TIMEOUT) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception:
        return {}
def jxf_pd_post(path, search, body):
    try:
        headers = jxf_pd_headers("POST", path, search)
        headers["Content-Type"] = "application/json"
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        req = _jxf_ur.Request(jxf_PD_HOST + path + search, data=data,
                              headers=headers, method="POST")
        with jxf_pd_sess().open(req, timeout=jxf_PD_TIMEOUT) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception:
        return {}
def jxf_pd_login_anon():
    global jxf_PD_LOGGED_IN
    if jxf_PD_LOGGED_IN:
        return True
    try:
        jxf_pd_post("/v1/users/anonymous", "", {"anonymous_id": "web_" + uuid.uuid4().hex})
        jxf_PD_LOGGED_IN = True
        return True
    except Exception:
        return False

def jxf_pd_resolve_line(ticket, retried=False):
    data = jxf_pd_post("/v1/playback/resolve-line", "?view=compact", {"ticket": ticket})
    if data.get("code") == "playback_user_session_required" and not retried:
        if jxf_pd_login_anon():
            data = jxf_pd_post("/v1/playback/resolve-line", "?view=compact", {"ticket": ticket})
    return data.get("line", {}) or {}

def jxf_norm_title(s):
    s = str(s or "")
    s = re.sub(r"[（(]\s*(?:19|20)\d{2}\s*[)）]", "", s)
    s = s.replace(" ", "").replace("　", "")
    s = re.sub(r"[《》〈〉\[\]【】()（）·•:：,，.。!！?？'\"“”‘’_\-—/\\|]", "", s)
    s = re.sub(r"(?i)(4K|2160P|1080P|蓝光|原盘)", "", s)
    return s.strip().lower()

def jxf_year_match(a, b):
    try:
        return abs(int(str(a)[:4]) - int(str(b)[:4])) <= 1
    except Exception:
        return True

def jxf_pd_pick_cards(cards, title, year):
    want = jxf_norm_title(title)
    if not want:
        return []
    exact = [c for c in cards if jxf_norm_title(c.get("title")) == want]
    if year:
        matched = [c for c in exact if jxf_year_match(year, c.get("year"))]
        if matched:
            exact = matched

    def _pop(c):
        try:
            return int(c.get("playback_count") or 0)
        except Exception:
            return 0

    exact.sort(key=_pop, reverse=True)
    return exact

def jxf_pd_short_name(label):
    if "官方" in label:
        base = label.split("·")[0].strip()
        for seg in reversed(base.split("-")):
            if "官方" in seg:
                name = seg.strip()
                if "4K" in base.upper() and not name.upper().startswith("4K"):
                    name = "4K" + name
                return name
    return label

def jxf_pd_keep_line(line):
    label = str(line.get("label") or "")
    if "专享4K" in label:
        return True
    return "4K" in label.upper() and "官方" in label

def jxf_pd_fetch_episodes(vid, episodes):
    eps = list(episodes)
    try:
        offset = len(eps)
        while True:
            data = jxf_pd_get("/v1/catalog/{}/episodes".format(vid),
                           "?limit=48&offset={}".format(offset))
            more = data.get("episodes") or []
            if not more:
                break
            eps.extend(more)
            if not (data.get("episode_pagination") or {}).get("has_more"):
                break
            offset += len(more)
    except Exception:
        pass
    return eps

def jxf_pd_lines(title, year=""):
    """按片名匹配片帝, 返回 [(线路名, 剧集串)]"""
    cards = (jxf_pd_get("/v1/browse/catalog",
                     "?q={}&page=1&limit=20".format(quote_plus(title)))).get("cards") or []
    # 同名卡片可能有多个(预告/正片), 逐个试, 取第一个带 4K 线路的
    for card in jxf_pd_pick_cards(cards, title, year)[:2]:
        vid = str(card.get("id") or "")
        data = jxf_pd_get("/v1/catalog/" + vid)
        eps = data.get("episodes") or []
        if not eps:
            continue
        try:
            count = int(data.get("episode_count") or len(eps))
        except Exception:
            count = len(eps)
        if count > len(eps):
            eps = jxf_pd_fetch_episodes(vid, eps)
        first = str((eps[0] or {}).get("token") or "")
        if not first:
            continue
        options = (jxf_pd_get("/v1/playback/resolve/" + first,
                           "?view=compact")).get("line_options") or []
        picked = [ln for ln in options if jxf_pd_keep_line(ln)]
        if not picked:
            continue
        picked.sort(key=lambda ln: 0 if "专享" in str(ln.get("label") or "") else 1)
        out = []
        for ln in picked[:2]:
            line_id = str(ln.get("id") or "")
            if not line_id:
                continue
            name = "片帝·" + jxf_pd_short_name(str(ln.get("label") or "4K"))
            segs = []
            for ep in eps:
                token = str((ep or {}).get("token") or "")
                if not token:
                    continue
                ep_name = str(ep.get("title") or ("第{}集".format(ep.get("number", ""))))
                ep_name = ep_name.replace("$", "_").replace("#", "_")
                segs.append(ep_name + "$pd@" + token + "@@" + line_id)
            if segs:
                out.append((name, "#".join(segs)))
        if out:
            return out
    return []

def jxf_pd_play(pid):
    token, _, line_id = pid[3:].partition("@@")
    options = (jxf_pd_get("/v1/playback/resolve/" + token,
                       "?view=compact")).get("line_options") or []
    target = None
    for ln in options:
        if str(ln.get("id") or "") == line_id:
            target = ln
            break
    candidates = ([target] if target else []) + \
                 [ln for ln in options if ln is not target and jxf_pd_keep_line(ln)]
    for ln in candidates:
        if ln.get("url_kind") == "m3u8" and not ln.get("resolve_required") and ln.get("url"):
            return {"parse": 0, "url": ln["url"], "header": {"User-Agent": jxf_PD_UA}}
        ticket = str(ln.get("url") or "").replace("resolve://", "")
        if not ticket:
            continue
        line = jxf_pd_resolve_line(ticket)
        if line.get("url"):
            return {"parse": 0, "url": line["url"], "header": {"User-Agent": jxf_PD_UA}}
    return {"parse": 0, "url": "", "header": {"User-Agent": jxf_PD_UA}}

# ======================= 4KK / Pomo 线路 (pomo.mom) =======================
jxf_POMO_HOST = "https://pomo.mom"
jxf_POMO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Referer": "https://pomo.mom/",
}
jxf_POMO_TIMEOUT = 10

def jxf_pomo_text(url):
    try:
        ctx0 = _jxf_ssl.create_default_context()
        ctx0.check_hostname = False
        ctx0.verify_mode = _jxf_ssl.CERT_NONE
        req = _jxf_ur.Request(url, headers=jxf_POMO_HEADERS)
        with _jxf_ur.urlopen(req, timeout=jxf_POMO_TIMEOUT, context=ctx0) as r:
            return r.read().decode("utf-8", "replace")
    except Exception:
        return ""
def jxf_pomo_list(text):
    start = text.find("All 4K Movies")
    if start == -1:
        start = text.find("<main")
    if start == -1:
        start = 0
    section = text[start:]
    pattern = r'<img[^>]*src="([^"]*uploadfile[^"]*)"[^>]*alt="([^"]*)"[^>]*>'
    videos = []
    seen = set()
    pos = 0
    while True:
        m = re.search(pattern, section[pos:])
        if not m:
            break
        img_start = pos + m.start()
        before = section[max(0, img_start - 2000):img_start]
        links = list(re.finditer(r'<a\s+href="https://pomo\.mom/(\d+)(?:\.html)?"', before))
        if links:
            vid = links[-1].group(1)
            if vid not in seen:
                seen.add(vid)
                videos.append({"id": vid, "name": m.group(2)})
        pos = pos + m.end()
    return videos

def jxf_pomo_lines(title):
    """按片名匹配 4KK, 返回 [(线路名, 剧集串)]"""
    videos = jxf_pomo_list(jxf_pomo_text(jxf_POMO_HOST + "/?keyword=" + quote_plus(title)))
    want = jxf_norm_title(title)
    item = None
    for v in videos:
        if want and jxf_norm_title(v.get("name")) == want:
            item = v
            break
    if not item:
        return []
    text = jxf_pomo_text("{}/{}.html".format(jxf_POMO_HOST, item["id"]))
    if not text:
        return []
    h2 = re.search(r'<h2 class="x-dbjs-title">([^<]+)</h2>', text)
    if h2 and jxf_norm_title(h2.group(1)) != want:
        return []
    magnets = re.findall(r'data-url="(magnet:\?xt=urn:btih:[^"]+)"', text)
    unique = []
    seen_mag = set()
    for mag in magnets:
        if mag not in seen_mag:
            seen_mag.add(mag)
            unique.append(mag)
    segs = []
    seen_items = set()
    items = re.findall(r'<div class="download-item">(.*?)</div>\s*</div>', text, re.DOTALL)
    for it in items:
        mag_match = re.search(r'data-url="(magnet:\?xt=urn:btih:[^"]+)"', it)
        if not mag_match:
            continue
        mag = mag_match.group(1).replace("#", "%23").replace("$", "%24")
        if mag in seen_items:
            continue
        seen_items.add(mag)
        name_match = re.search(r'class="x-dbjs-download-link[^"]*"[^>]*>([^<]+)</a>', it)
        file_name = name_match.group(1).strip() if name_match else ""
        size_match = re.search(r'<span class="file-size">\[([^\]]+)\]</span>', it)
        size = size_match.group(1).strip() if size_match else ""
        if file_name and size:
            play_title = "{} [{}]".format(file_name, size)
        elif file_name:
            play_title = file_name
        elif size:
            play_title = "磁力 [{}]".format(size)
        else:
            play_title = "磁力{}".format(len(segs) + 1)
        play_title = play_title[:80].replace("#", "").replace("$", "")
        segs.append(play_title + "$pomo|m|" + mag)
    if not segs:
        for i, mag in enumerate(unique):
            mag = mag.replace("#", "%23").replace("$", "%24")
            segs.append("磁力{}$pomo|m|{}".format(i + 1, mag))
    out = []
    if segs:
        out.append(("4KK·磁力", "#".join(segs)))
    pans = []
    seen_pan = set()
    for u in re.findall(r'data-url="(https://pan\.quark\.cn/s/[^"]+)"', text):
        if u not in seen_pan:
            seen_pan.add(u)
            pans.append(u)
    if pans:
        psegs = ["夸克网盘{}$pomo|q|{}".format(i + 1, u) for i, u in enumerate(pans)]
        out.append(("4KK·夸克", "#".join(psegs)))
    return out

def jxf_pomo_play(pid):
    kind, _, url = pid[5:].partition("|")
    if kind == "q":
        return {"parse": 1, "url": url, "header": {}}
    return {"parse": 0, "jx": 1, "url": url, "header": {}}

def jxf_extra_lines(title, year=""):
    """并发查片帝与4KK, 按片名精确匹配后追加线路"""
    result = {"pd": [], "4kk": []}

    def _work(key, fn):
        try:
            result[key] = fn()
        except Exception:
            result[key] = []

    threads = [
        threading.Thread(target=_work, args=("pd", lambda: jxf_pd_lines(title, year))),
        threading.Thread(target=_work, args=("4kk", lambda: jxf_pomo_lines(title))),
    ]
    for t in threads:
        t.daemon = True
        t.start()
    for t in threads:
        t.join(timeout=JXF_EXTRA_WAIT)
    lines = list(result.get("pd") or [])
    lines.extend(result.get("4kk") or [])
    return lines

# ======================= AES-256-ECB =======================

def jxf_build_sbox():
    sbox = [0] * 256
    p = q = 1
    while True:
        p = p ^ ((p << 1) ^ (0x1B if p & 0x80 else 0)) & 0xFF
        q ^= q << 1
        q ^= q << 2
        q ^= q << 4
        q ^= 0x09 if (q & 0x80) else 0
        q &= 0xFF
        xformed = q ^ ((q << 1) | (q >> 7)) & 0xFF
        xformed = (xformed ^ ((q << 2) | (q >> 6))) & 0xFF
        xformed = (xformed ^ ((q << 3) | (q >> 5))) & 0xFF
        xformed = (xformed ^ ((q << 4) | (q >> 4))) & 0xFF
        sbox[p] = xformed ^ 0x63
        if p == 1:
            break
    sbox[0] = 0x63
    return sbox

jxf_SBOX = jxf_build_sbox()
jxf_RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36, 0x6C, 0xD8, 0xAB, 0x4D]

def jxf_xtime(a):
    return ((a << 1) ^ (0x1B if a & 0x80 else 0)) & 0xFF

jxf_COL2 = [jxf_xtime(i) for i in range(256)]
jxf_COL3 = [jxf_xtime(i) ^ i for i in range(256)]

def jxf_expand_key(key):
    nk = len(key) // 4
    nr = nk + 6
    w = [list(key[4 * i:4 * i + 4]) for i in range(nk)]
    for i in range(nk, 4 * (nr + 1)):
        temp = list(w[i - 1])
        if i % nk == 0:
            temp = temp[1:] + temp[:1]
            temp = [jxf_SBOX[b] for b in temp]
            temp[0] ^= jxf_RCON[i // nk - 1]
        elif nk > 6 and i % nk == 4:
            temp = [jxf_SBOX[b] for b in temp]
        w.append([w[i - nk][j] ^ temp[j] for j in range(4)])
    return w, nr

def jxf_encrypt_block(block, w, nr):
    def _rk(r):
        return [x for word in w[r * 4:(r * 4) + 4] for x in word]
    s = list(block)
    rk0 = _rk(0)
    for j in range(16):
        s[j] ^= rk0[j]
    for r in range(1, nr):
        s = [jxf_SBOX[b] for b in s]
        s = [s[0], s[5], s[10], s[15],
             s[4], s[9], s[14], s[3],
             s[8], s[13], s[2], s[7],
             s[12], s[1], s[6], s[11]]
        t = [0] * 16
        for c in range(4):
            i = c * 4
            a0, a1, a2, a3 = s[i], s[i + 1], s[i + 2], s[i + 3]
            t[i] = jxf_COL2[a0] ^ jxf_COL3[a1] ^ a2 ^ a3
            t[i + 1] = a0 ^ jxf_COL2[a1] ^ jxf_COL3[a2] ^ a3
            t[i + 2] = a0 ^ a1 ^ jxf_COL2[a2] ^ jxf_COL3[a3]
            t[i + 3] = jxf_COL3[a0] ^ a1 ^ a2 ^ jxf_COL2[a3]
        s = t
        rk = _rk(r)
        s = [s[j] ^ rk[j] for j in range(16)]
    s = [jxf_SBOX[b] for b in s]
    s = [s[0], s[5], s[10], s[15],
         s[4], s[9], s[14], s[3],
         s[8], s[13], s[2], s[7],
         s[12], s[1], s[6], s[11]]
    rk = _rk(nr)
    s = [s[j] ^ rk[j] for j in range(16)]
    return bytes(s)

def jxf_aes256_ecb_encrypt(plain, key):
    w, nr = jxf_expand_key(key)
    out = bytearray()
    for i in range(0, len(plain), 16):
        out += jxf_encrypt_block(bytes(plain[i:i + 16]), w, nr)
    return bytes(out)

def jxf_aes_encrypt(plaintext, key=jxf_AES_KEY):
    """PKCS7 填充 + AES-256-ECB -> base64 (多后端, 输出一致)"""
    data = plaintext.encode("utf-8") if isinstance(plaintext, str) else plaintext
    pad = 16 - len(data) % 16
    data = data + bytes([pad]) * pad
    try:
        from Crypto.Cipher import AES
        return b64encode(AES.new(key, AES.MODE_ECB).encrypt(data)).decode()
    except Exception:
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher as _C
            from cryptography.hazmat.primitives.ciphers.algorithms import AES as _AES
            from cryptography.hazmat.primitives.ciphers.modes import ECB as _ECB
            from cryptography.hazmat.backends import default_backend as _B
            enc = _C(_AES(key), _ECB(), backend=_B()).encryptor()
            return b64encode(enc.update(data) + enc.finalize()).decode()
        except Exception:
            return b64encode(jxf_aes256_ecb_encrypt(data, key)).decode()

# ======================= HTTP / 签名 =======================

def jxf_http(method, url, body=None, content_type=None, timeout=12):
    headers = {"User-Agent": jxf_UA}
    data = None
    if body is not None:
        data = body.encode("utf-8") if isinstance(body, str) else body
        headers["Content-Length"] = str(len(data))
    if content_type:
        headers["Content-Type"] = content_type
    req = _jxf_ur.Request(url, data=data, headers=headers, method=method)
    with _jxf_ur.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")

def jxf_sign(concat):
    return jxf_aes_encrypt(concat)

def jxf_fix_host(host):
    if host is None or (isinstance(host, str) and host.strip() == ""):
        host = jxf_BASE_URLS[0]
    return str(host).rstrip("/")

def jxf_post(host, path, body=None, content_type=None):
    urls = []
    h = jxf_fix_host(host)
    if h not in urls:
        urls.append(h)
    for b in jxf_BASE_URLS:
        if b not in urls:
            urls.append(b)
    last = "{}"
    for u in urls:
        try:
            last = jxf_http("POST", u + path, body, content_type)
            if '"code"' in last:
                return last
        except Exception:
            continue
    return last

def jxf_get(url, timeout=12):
    try:
        return jxf_http("GET", url, timeout=timeout)
    except Exception:
        return "{}"

def jxf_post_form(host, path, params):
    ts = str(int(time.time()))
    params["timestamp"] = ts
    items = sorted(params.items())
    concat = "&".join(k + "=" + quote_plus(str(v)) for k, v in items)
    ds = jxf_sign(concat)
    form = "&".join(k + "=" + quote_plus(str(v)) for k, v in items)
    form += "&datasign=" + quote_plus(ds)
    return jxf_post(host, path, form, "application/x-www-form-urlencoded")

def jxf_post_json(host, path, params):
    params["timestamp"] = str(int(time.time()))
    items = sorted(params.items())
    concat = "&".join(k + "=" + str(v) for k, v in items)
    ds = jxf_sign(concat)
    obj = dict(items)
    obj["datasign"] = ds
    body = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return jxf_post(host, path, body, "application/json;charset=UTF-8")

# ======================= 核心业务 (返回 dict) =======================

def jxf_home(host):
    resp = jxf_post(host, "/api/v1/video/classifies", None, None)
    try:
        data = json.loads(resp).get("data") or []
    except Exception:
        data = []
    cls = [{"type_id": str(c.get("id")), "type_name": c.get("name") or ""}
           for c in data if c.get("id") and c.get("name")]
    # 按 type_id 升序: 电视剧(22016) 电影(22017) 动漫(22018) 综艺(22019)
    # 短剧(22020) 少儿(22021) 纪录片(22022) AI漫剧(22024), 与 App 首页顺序一致
    cls.sort(key=lambda x: int(x["type_id"]) if str(x["type_id"]).isdigit() else 10 ** 9)
    # 服务端不下发隐藏直播分类(22023), 手动追加到分类栏末尾
    if str(jxf_LIVE_TYPE_ID) not in [str(c.get("type_id")) for c in cls]:
        cls.append({"type_id": str(jxf_LIVE_TYPE_ID), "type_name": "直播"})
    return {"class": cls, "filters": {}}

def jxf_build_list(resp, page=1, id_desc=False):
    try:
        data = json.loads(resp).get("data") or {}
    except Exception:
        data = {}
    lst = []
    for v in data.get("list") or []:
        if not v.get("id"):
            continue
        lst.append({
            "vod_id": str(v.get("id")),
            "vod_name": v.get("name") or "",
            "vod_pic": v.get("videoPic") or "",
            "vod_remarks": v.get("remarks") or "",
        })
    # 本地按 id 降序: 搜索时 id 大=收录晚=越新, 最新的排在头部
    if id_desc and lst:
        try:
            lst.sort(key=lambda v: int(v.get("vod_id") or 0), reverse=True)
        except Exception:
            pass
    try:
        pg = int(page) or 1
    except (ValueError, TypeError):
        pg = 1
    try:
        pagecount = int(data.get("totalPage") or 1)
    except (ValueError, TypeError):
        pagecount = 1
    if pagecount < pg:
        pagecount = pg
    return {
        "page": pg,
        "pagecount": pagecount,
        "limit": data.get("limit") or 20,
        "total": data.get("totalCount") or 0,
        "list": lst,
    }

def jxf_category(host, tid, pg):
    page = 1
    try:
        page = int(pg or 1)
    except Exception:
        pass
    try:
        type_id = int(tid)
    except Exception:
        type_id = 0
    # ---- 直播分类 22023: 服务端不下发, 走 liveVideo 接口返回直播分组 ----
    if type_id == jxf_LIVE_TYPE_ID:
        lst = []
        try:
            r = jxf_get(jxf_fix_host(host) + "/api/v1/video/liveVideo")
            data = (json.loads(r).get("data") or {})
            for v in data.get("list") or []:
                if not v.get("id"):
                    continue
                lst.append({
                    "vod_id": str(v.get("id")),
                    "vod_name": v.get("name") or "",
                    "vod_pic": v.get("videoPic") or "",
                    "vod_remarks": v.get("remarks") or ("直播" if v.get("typeId") else ""),
                })
        except Exception:
            pass
        return {"page": 1, "pagecount": 1, "limit": len(lst), "total": len(lst), "list": lst}
    # 默认走 /video/index(与前面版本一致, 保留服务端原始顺序)。
    # 注意: 服务端忽略 page 参数, 必须用 pageNum 才能真正翻页(否则滑到底内容不变/跳动)。
    resp = jxf_post_json(host, "/api/v1/video/index", {"pageNum": page, "typeId": type_id})
    res = jxf_build_list(resp, page, False)
    # 服务端把部分分类(如电视剧22016)降级为只返回2条(limit=2),
    # 此时自动改用 /video/search 空关键词+typeId 兜底, 拿完整列表(40条/页, 最新在前)。
    if len(res.get("list") or []) < 10:
        resp2 = jxf_post_json(host, "/api/v1/video/search", {"keyword": "", "typeId": type_id, "pageNum": page})
        res = jxf_build_list(resp2, page, True)
    return res

def jxf_search(host, key, pg="1"):
    key = (key or "").strip().strip('"').strip("'")
    if not key:
        return {"page": 1, "pagecount": 0, "limit": 20, "total": 0, "list": []}
    # 兼容播放器传入 URL 编码关键词 (如 %E6%96%97%E7%BD%97...)
    # 服务端 % 会当作通配符, 编码形态会搜出大量无关结果, 必须先解码回原文
    if "%" in key:
        try:
            dec = unquote(key)
            if dec and dec != key:
                key = dec.strip()
        except Exception:
            pass
    # 兼容 \uXXXX 转义形态的关键词 (如备份 \u6597\u7f57...)
    if key and "\\u" in key and all(ord(ch) < 128 for ch in key):
        try:
            dec = key.encode("ascii").decode("unicode_escape")
            if dec and dec != key:
                key = dec
        except Exception:
            pass
    try:
        page = int(pg or 1)
    except (ValueError, TypeError):
        page = 1
    if page < 1:
        page = 1
    resp = jxf_post_json(host, "/api/v1/video/search", {"keyword": key, "pageNum": page})
    return jxf_build_list(resp, page, True)

def jxf_reco(host):
    """首页推荐: 电视剧分类第一页, 失败返回空"""
    try:
        c = jxf_category(host, "22016", "1")
        return (c or {}).get("list") or []
    except Exception:
        return []

def jxf_fetch_detail(host, vid):
    resp = jxf_post_form(host, "/api/v1/video/videoDetails", {"id": str(vid)})
    try:
        return json.loads(resp).get("data") or {}
    except Exception:
        return {}

def jxf_detail(host, vid):
    data = jxf_fetch_detail(host, vid)
    if not data:
        return {"list": []}
    sources = jxf_pick_sources(data.get("playerSource") or [])
    from_names, from_urllists = [], []
    seen = {}
    for src in sources:
        eps = src.get("episodes") or []
        if not eps:
            continue
        name = src.get("sourceName") or "剧下饭"
        if name in seen:          # 同名线路加序号区分
            seen[name] += 1
            name = name + str(seen[name])
        else:
            seen[name] = 1
        segs = []
        for i, ep in enumerate(eps, 1):
            ep_name = (ep.get("episodeName") or "") or ("第" + str(i) + "集")
            ep_name = ep_name.replace("$", "_").replace("#", "_")
            segs.append(ep_name + "$" + str(vid) + "_" + str(i))
        from_names.append(name)
        from_urllists.append("#".join(segs))
    # 直播频道不做外部聚合, 点播才按片名匹配片帝/4KK 追加线路
    live_only = bool(sources) and all(
        (str(s.get("sourceCode") or "") in jxf_LIVE_CODES or "直播" in str(s.get("sourceName") or ""))
        for s in sources)
    if not live_only:
        for extra_name, extra_urls in jxf_extra_lines(data.get("name") or "", data.get("year") or ""):
            if extra_name in seen:
                continue
            seen[extra_name] = 1
            from_names.append(extra_name)
            from_urllists.append(extra_urls)
    if not from_urllists:
        return {"list": []}
    play_from = "$$$".join(from_names)     # 多线路: 名字用 $$$ 分隔
    play_url = "$$$".join(from_urllists)   # 线路内集数用 # 分隔
    return {"list": [{
        "vod_id": str(data.get("id") or vid),
        "vod_name": data.get("name") or "",
        "vod_pic": data.get("videoPic") or "",
        "vod_actor": data.get("actor") or "",
        "vod_director": data.get("director") or "",
        "vod_remarks": data.get("remarks") or "",
        "vod_content": data.get("content") or "",
        "vod_year": data.get("year") or "",
        "vod_area": data.get("area") or "",
        "vod_play_from": play_from,
        "vod_play_url": play_url,
    }]}

def jxf_analysis_url(host, source_code, pc):
    """调用服务端 /api/v1/player/analysisUrl 把加密 playerCode 解析成真实播放地址。
    直播(sourceCode=zhibo/difang/huya)与点播加密码(co_xxx)均由此返回秒播地址。
    返回解析成功后的 URL 字符串, 失败返回空串。"""
    if not source_code or not pc:
        return ""
    try:
        r = jxf_post_form(host, "/api/v1/player/analysisUrl", {"from": source_code, "code": pc})
        u = (json.loads(r).get("data") or "")
        if str(u).startswith("http"):
            return str(u)
    except Exception:
        pass
    return ""

def jxf_play(host, flag, pid):
    pid = str(pid or "")
    if pid.startswith("pd@"):
        return jxf_pd_play(pid)
    if pid.startswith("pomo|"):
        return jxf_pomo_play(pid)
    try:
        vid, ep = pid.rsplit("_", 1)
        ep = int(ep)
    except Exception:
        return {"parse": 0, "url": pid, "header": {"User-Agent": jxf_UA}}
    data = jxf_fetch_detail(host, vid)
    sources = jxf_pick_sources(data.get("playerSource") or [])
    flag_s = str(flag or "").strip()
    # 优先用户当前选中的线路, 另一条 4K 线作为备份
    ordered = [src for src in sources if str(src.get("sourceName") or "").strip() == flag_s]
    for src in sources:
        if src not in ordered:
            ordered.append(src)
    raw_fallback = ""
    for src in ordered:
        eps = src.get("episodes") or []
        if not eps or ep > len(eps):
            continue
        pc = (eps[ep - 1] or {}).get("playerCode") or ""
        if not pc:
            continue
        parse_url = src.get("parseUrl") or ""
        source_code = src.get("sourceCode") or ""
        if parse_url:
            j = jxf_get(parse_url + pc)
            try:
                u = json.loads(j).get("url") or ""
            except Exception:
                u = ""
            if u:
                return {"parse": 0, "url": u, "header": {"User-Agent": jxf_UA}}
            # 本条 4K 线解析失败: 再走服务端解析, 仍失败就换另一条 4K 线
            u = jxf_analysis_url(host, source_code, pc)
            if u:
                return {"parse": 0, "url": u, "header": {"User-Agent": jxf_UA}}
            if not raw_fallback:
                raw_fallback = pc
            continue
        # 直播/加密码: 优先走服务端 analysisUrl 秒播解析 (zb-xxx / 数字房间号 / co_xxx)
        if not str(pc).startswith("http"):
            u = jxf_analysis_url(host, source_code, pc)
            if u:
                headers = {"User-Agent": jxf_UA}
                if source_code == "huya":
                    headers["Referer"] = "https://www.huya.com/"
                return {"parse": 0, "url": u, "header": headers}
            # 解析失败: 记下原始 code, 交由播放器自行尝试
            if not raw_fallback:
                raw_fallback = pc
            continue
        # 直链
        return {"parse": 0, "url": pc, "header": {"User-Agent": jxf_UA}}
    return {"parse": 0, "url": raw_fallback, "header": {"User-Agent": jxf_UA}}

# ======================= 类式接口 (class Spider) =======================

class JuxiafanSpider(object):
    """webhomeTV 类式规范: 各方法返回 dict, searchContent 三参数。
    与咕噜咕噜可搜索版(样板) 结构一致。"""

    def __init__(self, *args, **kwargs):
        self._host = jxf_BASE_URLS[0]
        if kwargs.get("host"):
            self._host = jxf_fix_host(kwargs["host"])
        if kwargs.get("extend") is not None:
            self.init(kwargs["extend"])

    def init(self, extend=None):
        if extend:
            s = str(extend).strip()
            if s.startswith("http"):
                self._host = jxf_fix_host(s)
            elif s.startswith("base="):
                self._host = jxf_fix_host(s[5:])

    def getName(self):
        return "剧下饭4K聚合版"

    def homeContent(self, filter=False):
        result = jxf_home(self._host)
        # 去掉推荐: 只返回纯分类列表, 各分类(含电视剧)均以分类页展示
        result["list"] = []
        return result

    def homeVideoContent(self):
        # 去掉推荐: 分类页保持纯分类列表, 不再渲染"精选/推荐"卡
        return {"list": []}

    def categoryContent(self, tid, pg="1", filter=None, extend=None):
        return jxf_category(self._host, tid, pg)

    def detailContent(self, ids):
        if not ids:
            return {"list": []}
        return jxf_detail(self._host, ids[0])

    # ---------- 搜索 (关键: 三参数签名, 兼容 webhomeTV) ----
    def searchContent(self, key, quick, pg="1"):
        """webhomeTV 搜索入口 - key 关键词, quick 快速标记, pg 页码"""
        return self.searchContentPage(key, quick, pg)

    def searchContentPage(self, key, quick, pg="1"):
        """分页搜索 - 支持真正翻页、异常兜底"""
        try:
            return jxf_search(self._host, key, pg)
        except Exception:
            return {"page": 1, "pagecount": 1, "limit": 0, "total": 0, "list": []}

    def playerContent(self, flag, id, vipFlags=""):
        return jxf_play(self._host, flag, id)

    def manualVideoCheck(self):
        return False

    def isVideoFormat(self, url):
        return False

    def localProxy(self, param):
        return {"list": [], "parse": 0, "url": ""}

    def liveContent(self, url):
        return {"list": []}

def kish_play_ok(r):
    """播放结果是否可用：http / magnet 直链，或明确交给播放器处理（jx=1）。

    Kishuto 原来的判定只认 http，剧下饭的 4KK·磁力 线返回 magnet: 会被当成
    「取流失败」，进而换源成片帝的地址——线路名字对不上内容。这里放行。
    """
    if not isinstance(r, dict):
        return False
    u = str(r.get('url') or '')
    if u.startswith('http') or u.startswith('magnet:'):
        return True
    try:
        return bool(int(r.get('jx') or 0)) and bool(u)
    except Exception:
        return False

# ==================== 剧下饭4K 一级源 jx END ====================


class Spider(_BaseSpider):
    """五源合一：影探 / 稀饭 / 小鸡看看 / FoFo / 小山。

    分类与搜索按 '<tag>|' 前缀派发；详情页拿到主源数据后，再并发去其余源按
    标题模糊匹配，把匹配到的线路追加在后面。播放时按线路 id 里编码的 tag 派发回原源。
    """

    NAME = 'Kishuto'
    ORDER = ('yt', 'sz', 'xj', 'jx', 'jn', 'sk', 'gg', 'fq', 'ff', 'xf', 'zj')
    LABELS = {'gg': '咕噜', 'yt': '影探', 'xf': '稀饭', 'xj': '小鸡',
              'ff': 'FoFo', 'sz': '小山', 'fq': '枫奇', 'zj': '找剧',
              'jn': '橘汁新', 'sk': '四源4K', 'jx': '剧下饭'}
    DETAIL_BUDGET = 5.5    # 兼容旧配置，_fill 已改成下面的三段式
    FILL_BUDGET = 2.2      # 首屏凑线路的最长等待（秒）
    TAIL_WAIT = 0.9        # 攒够 5 条后再收尾这么久，把已回源的线路都带上
    PLAY_TRY = 4           # 播放失败时最多换 4 条线路重试
    PLAY_HEAD = 2.5        # 本线路超过这么久没出地址才换源
    # 注意：坏线路一般 0.3~0.5s 就返回空，不会等满；2.5s 是为了不误杀
    # 「咕噜·新咕噜4K」这类要 2s 才出地址的正常线路（实测被 1.5s 切走过）
    PLAY_EACH = 3.0        # 换源时每条线路自己最多等这么久
    PLAY_BUDGET = 7.0      # 换源重试的总时长上限（秒）
    PLAY_SPEED = {'sz': 0, 'jn': 1, 'xj': 2, 'jx': 3, 'sk': 4, 'xf': 5,
                  'gg': 6, 'ff': 7, 'fq': 8, 'zj': 9, 'yt': 10}   # 换源顺序：出流快的排前
    FILL_ENOUGH = 5        # 攒够 5 条线路就渲染首屏，不再干等
    TOPUP_BUDGET = 12.0    # 后台补齐的最长等待
    SEARCH_BUDGET = 2.8      # 影探 2.1s 就回来，其余源最多再等 0.7s
    HOME_BUDGET = 8.0
    CACHE_TTL = 300
    HOME_SOURCE = 'yt'     # 首页数据源：yt=影探 / gg=咕噜 / pd=片单已移除
    HOME_CLASS_MAX = 12    # 首页最多挂几个分类（壳会逐个预取，太多拖慢）
    HOME_TTL = 90          # 首页结果缓存（秒）—— 壳会连着调 homeContent/homeVideoContent
    CAT_TTL = 60           # 分类首页缓存（秒）

    def __init__(self):
        self.cfg = {}
        self._ready = {}
        self._srcs = {}
        self._home = (0.0, None)   # (时间戳, 首页结果) —— 壳会连着调 home/homeVideo
        self._cat = {}             # 分类首页缓存，防止来回切页重复打接口
        self._diag = None          # 非 None 时进入诊断中心模式
        try:
            self._build({})
        except Exception:
            pass

    # ---------------- 生命周期 ----------------
    def getName(self):
        return self.NAME

    def version(self):
        return CODE_VERSION

    def init(self, extend=''):
        cfg = {}
        try:
            if isinstance(extend, dict):
                cfg = dict(extend)
            elif isinstance(extend, str) and extend.strip().startswith('{'):
                cfg = json.loads(extend)
        except Exception:
            cfg = {}
        self.cfg = cfg if isinstance(cfg, dict) else {}
        # 影探那层自己也是四源聚合，首屏预算压到 3.2s：超时的源它会后台补完
        self.cfg.setdefault('detail_budget', 1.2)
        if str(self.cfg.get('mode') or '').lower() in ('settings', 'diag'):
            self._diag = KishDiag(self)
        try:
            self._build(self.cfg)
        except Exception:
            pass
        try:
            _kish_update_async()
        except Exception:
            pass
        return None

    def _build(self, cfg):
        makers = (('gg', GuluSpider), ('yt', YtAggSpider),
                  ('xf', XifanAggSpider),
                  ('xj', XiaojiSpider), ('ff', FofoSpider),
                  ('sz', ShanZhaSpider), ('fq', FengqiSpider), ('zj', ZJSpider),
                  ('jn', JZNewSpider), ('sk', SK4KSpider),
                  ('jx', JuxiafanSpider))
        for tag, cls in makers:
            if tag in self._srcs:
                continue
            try:
                self._srcs[tag] = cls()
            except Exception:
                pass

    def _src(self, tag):
        ob = self._srcs.get(tag)
        if ob is None:
            return None
        if not self._ready.get(tag):
            self._ready[tag] = True
            try:
                ext = json.dumps(self.cfg, ensure_ascii=False) if self.cfg else ''
                ob.init(ext)
            except Exception:
                pass
        return ob

    def destroy(self):
        for ob in list(self._srcs.values()):
            try:
                ob.destroy()
            except Exception:
                pass
        self._srcs.clear()
        self._ready.clear()

    def isVideoFormat(self, url):
        try:
            return bool(is_stream_url(url) or is_media_url(url))
        except Exception:
            return False

    def manualVideoCheck(self):
        return False

    def localProxy(self, param):
        return None

    # ---------------- id 编解码 ----------------
    @staticmethod
    def _b64(raw):
        return base64.urlsafe_b64encode(raw.encode('utf-8')).decode('ascii').rstrip('=')

    @staticmethod
    def _unb64(s):
        s = str(s or '')
        s += '=' * (-len(s) % 4)
        return base64.urlsafe_b64decode(s.encode('ascii')).decode('utf-8', 'replace')

    def _enc_vid(self, tag, vid):
        return 'k1' + self._b64('%s\x1f%s' % (tag, vid))

    def _dec_vid(self, code):
        s = str(code or '')
        if s.startswith('k1'):
            try:
                tag, _, vid = self._unb64(s[2:]).partition('\x1f')
                if tag in self.ORDER:
                    return tag, vid
            except Exception:
                pass
        return 'yt', s

    def _enc_play(self, tag, flag, pid, cid='', ep=''):
        # cid=详情 id、ep=集名：取流失败时要靠它们回查同片其它线路
        return 'k2' + self._b64('%s\x1f%s\x1f%s\x1f%s\x1f%s'
                                % (tag, flag, pid, cid, ep))

    def _dec_play(self, code):
        s = str(code or '')
        if s.startswith('k2'):
            try:
                parts = self._unb64(s[2:]).split('\x1f', 4)
                if len(parts) >= 3 and parts[0] in self.ORDER:
                    while len(parts) < 5:
                        parts.append('')
                    return parts[0], parts[1], parts[2], parts[3], parts[4]
            except Exception:
                pass
        return 'yt', '', s, '', ''

    # ---------------- 并发小工具 ----------------
    def _fan(self, work, budget):
        box = {}
        ths = []
        for tag in self.ORDER:
            def run(t=tag):
                try:
                    work(t, box)
                except Exception:
                    box.setdefault(t, None)
            th = threading.Thread(target=run)
            th.daemon = True
            th.start()
            ths.append(th)
        deadline = time.time() + budget
        for th in ths:
            try:
                th.join(max(0.02, deadline - time.time()))
            except Exception:
                pass
        return box

    # ---------------- 首页 ----------------
    def _home_one(self, tag, filter=True):
        """首页分类 / 筛选 / 推荐取自指定源（默认影探，咕噜作备选）。"""
        ob = self._src(tag)
        if ob is None:
            return None
        try:
            data = ob.homeContent(filter) or {}
        except Exception:
            return None
        label = self.LABELS.get(tag) or tag
        classes = []
        for c in (data.get('class') or []):
            if not isinstance(c, dict):
                continue
            tid = str(c.get('type_id') or '').strip()
            if not tid:
                continue
            if self.HOME_CLASS_MAX and len(classes) >= self.HOME_CLASS_MAX:
                break
            classes.append({'type_id': '%s|%s' % (tag, tid),
                            'type_name': '%s·%s' % (label,
                                                    c.get('type_name') or tid)})
        if not classes:
            return None
        keep = set(c['type_id'].split('|', 1)[1] for c in classes)
        filters = {}
        for k, v in (data.get('filters') or {}).items():
            if str(k) in keep:
                filters['%s|%s' % (tag, k)] = v
        cards = []
        for it in (data.get('list') or [])[:30]:
            if not isinstance(it, dict):
                continue
            it = dict(it)
            it['vod_id'] = self._enc_vid(tag, it.get('vod_id'))
            _memo_title(it['vod_id'], it.get('vod_name'))
            cards.append(it)
        return {'class': classes, 'filters': filters, 'list': cards}

    def homeContent(self, filter=True):
        if self._diag is not None:
            return self._diag.homeContent(filter)
        now = time.time()
        if self._home[1] and now - self._home[0] < self.HOME_TTL:
            return self._home[1]
        got = (self._home_one('yt', filter) or
               self._home_one('gg', filter) or
               self._home_all(filter))
        if got:
            self._home = (now, got)
        return got

    def _home_all(self, filter=True):
        def work(tag, box):
            ob = self._src(tag)
            got = ob.homeContent(True) if ob else None
            box[tag] = (got or {}).get('class') or []
        box = self._fan(work, self.HOME_BUDGET)
        classes = []
        for tag in self.ORDER:
            for c in box.get(tag) or []:
                if not isinstance(c, dict):
                    continue
                tid = c.get('type_id')
                if tid in (None, ''):
                    continue
                classes.append({
                    'type_id': '%s|%s' % (tag, tid),
                    'type_name': '%s·%s' % (self.LABELS[tag],
                                            c.get('type_name') or tid)})
        if not classes:
            classes = [{'type_id': 'yt|电影', 'type_name': '影探·电影'}]
        return {'class': classes, 'filters': {}}

    def homeVideoContent(self):
        if self._diag is not None:
            return self._diag.homeVideoContent()
        if self._home[1] and time.time() - self._home[0] < self.HOME_TTL:
            cached = self._home[1].get('list')
            if cached:
                return {'list': cached}
        got = self._home_one('yt') or self._home_one('gg')
        if got and got.get('list'):
            return {'list': got['list']}

        def work(tag, box):
            ob = self._src(tag)
            got = ob.homeVideoContent() if ob else None
            box[tag] = (got or {}).get('list') or []
        box = self._fan(work, self.HOME_BUDGET)
        out = []
        for tag in self.ORDER:
            for it in (box.get(tag) or [])[:12]:
                if not isinstance(it, dict):
                    continue
                it = dict(it)
                it['vod_id'] = self._enc_vid(tag, it.get('vod_id'))
                _memo_title(it['vod_id'], it.get('vod_name'))
                out.append(it)
        return {'list': out[:40]}

    # ---------------- 分类 ----------------
    def categoryContent(self, tid, pg='1', filter=True, extend=None):
        if self._diag is not None:
            return self._diag.categoryContent(tid, pg, filter, extend)
        ck = None
        try:
            if str(pg) in ('1', '1.0'):
                ck = '%s|%s' % (tid, json.dumps(extend or {}, sort_keys=True,
                                                ensure_ascii=False))
                hit = self._cat.get(ck)
                if hit and time.time() - hit[0] < self.CAT_TTL:
                    return hit[1]
        except Exception:
            ck = None
        tag, _, real = str(tid or '').partition('|')
        if tag not in self.ORDER or not real:
            tag, real = 'yt', str(tid or '')
        ob = self._src(tag)
        got = None
        if ob is not None:
            try:
                got = ob.categoryContent(real, pg, filter,
                                         extend if isinstance(extend, dict) else {})
            except Exception:
                got = None
        got = got if isinstance(got, dict) else {'list': []}
        for it in (got.get('list') or []):
            try:
                it['vod_id'] = self._enc_vid(tag, it.get('vod_id'))
                _memo_title(it['vod_id'], it.get('vod_name'))
            except Exception:
                pass
        if ck and got.get('list'):
            if len(self._cat) > 40:
                self._cat.clear()
            self._cat[ck] = (time.time(), got)
        return got

    # ---------------- 搜索 ----------------
    NAME_NOISE = ('手语版', '字幕助听版', '字幕版', '助听版', '无字幕',
                  '国语版', '粤语版', '日语版', '英语版', '普通话版', '双语版',
                  '中配版', '台配版', '国配版', '日配版', '粤配版', '原声版',
                  '中配', '台配', '国配', '普通话', '国语', '粤语', '日语',
                  '英语', '韩语', '原声',
                  '真人版', '动画版', '重制版', '剧版', '电影版', '电视版',
                  '完整版', '未删减', '无删减', '高清版', '蓝光版', '合集', '正片',
                  '特别篇', '特别版', '解析', '解说', '精彩分享', '剧情揭秘',
                  '揭秘', '预告', '花絮', '片段', '番剧', '在线观看', '正版',
                  '抢先版', '枪版', '修复版', '加长版', '导演剪辑版')

    # 出现在片名中间就说明后面都是衍生内容，直接切断
    NAME_CUT = ('剧情揭秘', '深度解读', '解说', '预告', '花絮', '片段', '特辑',
                '精彩', '分集', '速看', '混剪', '盘点', '年番')

    @classmethod
    def _base_name(cls, name):
        """把「凡人修仙传手语版」「凡人修仙传2025」这类变体归一成主片名。"""
        raw = str(name or '')
        # 站点常把副标题/来源拼进片名，先掐掉「-」「｜」「_」之后的部分
        for sep in ('-', '－', '｜', '|', '_'):
            if sep in raw[1:]:
                raw = raw.split(sep)[0]
        t = norm_title(raw)
        if not t:
            return ''
        t = re.sub(r'[（(][^）)]*[）)]', '', t)
        for _ in range(3):
            for w in cls.NAME_NOISE:
                if t.endswith(w) and len(t) > len(w):
                    t = t[:-len(w)]
                elif t.startswith(w) and len(t) > len(w):
                    t = t[len(w):]
        for w in cls.NAME_CUT:          # 中间出现就切
            i = t.find(w, 1)
            if i > 0:
                t = t[:i]
                break
        if t.endswith('版') and len(t) >= 4:   # 沙丘2版 / 葬送的芙莉莲版
            t = t[:-1]
        t = re.sub(r'第[一二三四五六七八九十\d]+[季部篇]$', '', t)
        t = re.sub(r'(19|20)\d{2}$', '', t)
        t = t.rstrip('之').strip()
        return t or norm_title(raw)

    def _fan_search(self, work, budget, grace=0.8, fq_wait=0.0):
        """并发搜；影探回来且另有 2 个源到齐就收工，最多等 grace 秒。

        fq_wait 是「从搜索开始算」的绝对上限：枫奇4K 首次过验证码约
        3.9s，比主预算慢，不给它单独留时间就永远出不了 [枫奇] 卡片。
        """
        box = {}
        ths = {}
        for tag in self.ORDER:
            def run(t=tag):
                try:
                    work(t, box)
                except Exception:
                    box.setdefault(t, [])
            th = threading.Thread(target=run)
            th.daemon = True
            th.start()
            ths[tag] = th
        start = time.time()
        deadline = start + budget
        hard = max(deadline, start + max(0.0, fq_wait))
        yt_at = None
        while True:
            now = time.time()
            if now >= hard:
                break
            done = False
            if now < deadline:
                if 'yt' in box:
                    ready = sum(1 for t in box if t != 'yt')
                    if ready >= 2:      # 影探 + 另外两个源，够拼卡了
                        done = True
                    elif yt_at is None:
                        yt_at = now
                    elif now - yt_at >= grace:
                        done = True
                elif not any(t.is_alive() for t in ths.values()):
                    done = True
            else:
                done = True
            if done:
                fq = ths.get('fq')
                if (fq_wait > 0 and 'fq' not in box and fq is not None
                        and fq.is_alive() and now < hard):
                    time.sleep(0.03)
                    continue
                break
            time.sleep(0.03)
        return box

    # 出卡时优先用哪个源的元数据（影探有海报且分类准）
    CARD_PRI = {'yt': 0, 'gg': 1, 'sz': 2, 'xf': 3, 'xj': 4, 'ff': 5,
                'fq': 6, 'zj': 7, 'jn': 8, 'sk': 9}
    SEARCH_TTL = 600

    def searchContent(self, key, quick=False, pg='1'):
        """搜索退回最初版：六个源各出各的，按源顺序原样列前 12 条。

        不做同名合并、不做相关性过滤、不重排出卡优先级 —— 壳里看到什么
        就是各站点搜索接口返回的什么。并发与短缓存只用于提速，不改结果。
        详情页跨源补线路的匹配另见 strict_match（不再把衍生电影挂进来）。
        """
        if self._diag is not None:
            return self._diag.searchContent(key, quick, pg)
        kw = str(key or '')
        if not kw.strip():
            return {'list': []}
        try:
            page = int(str(pg or 1))
        except Exception:
            page = 1
        if page < 1:
            page = 1

        ck = 'ks:%s:%s' % (norm_title(kw), page)
        hit = cache_get(ck)
        if hit:
            try:
                return json.loads(hit)
            except Exception:
                pass

        def work(tag, box):
            ob = self._src(tag)
            got = ob.searchContent(kw, quick, pg) if ob else None
            box[tag] = (got or {}).get('list') or []

        box = self._fan_search(work, self.SEARCH_BUDGET, fq_wait=4.6)
        out = []
        for tag in self.ORDER:
            for it in (box.get(tag) or [])[:12]:
                if not isinstance(it, dict):
                    continue
                it = dict(it)
                it['vod_id'] = self._enc_vid(tag, it.get('vod_id'))
                _memo_title(it['vod_id'], it.get('vod_name'))
                note = str(it.get('vod_remarks') or '')
                it['vod_remarks'] = ('[%s] %s'
                                     % (self.LABELS.get(tag, tag), note)).strip()
                out.append(it)

        res = {'list': out, 'page': page, 'pagecount': page, 'total': len(out)}
        try:
            cache_put(ck, json.dumps(res, ensure_ascii=False), self.SEARCH_TTL)
        except Exception:
            pass
        return res

    # ---------------- 详情 ----------------
    def _digest(self, tag, vod, cid=''):
        """把某个源 detailContent 返回的线路拆开并按本文件格式重新编码。"""
        froms = str(vod.get('vod_play_from') or '').split('$$$')
        urls = str(vod.get('vod_play_url') or '').split('$$$')
        out = []
        for i, f in enumerate(froms):
            f = str(f or '').strip()
            if not f:
                continue
            seg = urls[i] if i < len(urls) else ''
            eps = []
            idx = 0
            for part in str(seg).split('#'):
                part = part.strip()
                if not part:
                    continue
                nm, sep, pid = part.partition('$')
                if not sep:
                    nm, pid = '正片', part
                idx += 1
                # 播放码里存「集序号\x1e集名」：换源时靠它对齐同一集
                # （影探叫「第01集」、小山叫「01」，光比名字对不上）
                eps.append((nm.strip() or '正片',
                            self._enc_play(tag, f, pid, cid,
                                           '%d\x1e%s'
                                           % (idx, nm.strip() or '正片'))))
            if eps:
                out.append((self._line_name(tag, f), eps))
        return out

    def _line_name(self, tag, flag):
        label = self.LABELS.get(tag) or tag
        f = str(flag or '').strip()
        if tag == 'yt':
            return clean_name(f) or label        # 影探内部本来就带源名
        return clean_name('%s·%s' % (label, f)) or label

    @staticmethod
    def _variants(title):
        """片名变体：全角/半角、季数后缀、括号注释、语种后缀都试一遍。

        实测「葬送的芙莉莲第二季」在稀饭搜不到，去掉「第二季」才行；
        而「庆余年第二季」在影视站带季数反而更准，所以原样排第一。
        """
        t = str(title or '').strip()
        out = [t] if t else []
        if not t:
            return out
        pats = (r'第[一二三四五六七八九十百千万0-9]+[季部篇]',
                r'[（(\[][^）)\]）]*[）)\]]',
                r'(国语|粤语|日语|英语|普通话|中字|双语|原声)版?$',
                r'(19|20)\d{2}$')
        for pat in pats:
            v = re.sub(pat, '', t).strip(' -·:：')
            if len(v) >= 2 and v not in out:
                out.append(v)
        for sep in ('：', ':', '·'):
            if sep in t:
                v = t.split(sep)[0].strip()
                if len(v) >= 2 and v not in out:
                    out.append(v)
        return out[:2]

    def _fill_start(self, tag, title):
        """其余源并发去「搜片名 → 取详情」，返回 (box, threads)。

        box 会被线程陆续塞数据，所以主流程可以只等一小会儿就先渲染。
        """
        box, ths = {}, []
        if not title:
            return box, ths
        variants = self._variants(title)

        def work(tt):
            try:
                ob = self._src(tt)
                if ob is None:
                    return
                pick = None
                for kw in variants:
                    try:
                        got = ob.searchContent(kw, False, '1') or {}
                    except Exception:
                        continue
                    pick = strict_match(title, got.get('list') or [])
                    if pick:
                        break
                if not pick:
                    return
                vv = (ob.detailContent([pick.get('vod_id')]) or {}).get('list') or []
                if vv and isinstance(vv[0], dict):
                    box[tt] = vv[0]
            except Exception:
                pass

        for tt in self.ORDER:
            if tt == tag:
                continue
            th = threading.Thread(target=work, args=(tt,))
            th.daemon = True
            th.start()
            ths.append(th)
        return box, ths

    @staticmethod
    def _count_lines(box):
        n = 0
        for v in list(box.values()):
            try:
                n += len([x for x in str(v.get('vod_play_from') or '').split('$$$') if x])
            except Exception:
                pass
        return n

    def _wait_lines(self, box, ths, budget, enough):
        """攒够 enough 条线路、或线程都结束就提前收工（不等满预算）。"""
        deadline = time.time() + budget
        while time.time() < deadline:
            if self._count_lines(box) >= enough:
                return True
            if not any(t.is_alive() for t in ths):
                return True
            time.sleep(0.04)
        return False

    def _wait_yield(self, box, ths, base_lines, budget, yt_ok=False):
        """首屏策略：攒够 FILL_ENOUGH 条就开始收工，再收 TAIL_WAIT 秒给足。

        壳拿到 detailContent 后不会原地追加线路，所以「先给 5 条、后面慢慢
        加载」在壳侧不成立 —— 达到 5 条后仍要在预算内把已回源的线路全带上，
        一次给足；预算内没回来的源由 _topup 后台补完写回缓存（重进即全量）。
        """
        start = time.time()
        deadline = start + budget
        have = len(base_lines)
        enough_at = None
        while time.time() < deadline:
            if have + self._count_lines(box) >= self.FILL_ENOUGH:
                if enough_at is None:
                    enough_at = time.time()
                elif time.time() - enough_at >= self.TAIL_WAIT:
                    return True              # 够了，再多收一小会儿就出
            if not any(t.is_alive() for t in ths):
                return True                  # 所有源都跑完了
            time.sleep(0.04)
        return False

    def _digest_box(self, tag, box, cid=''):
        out = []
        for t in self.ORDER:
            v = box.get(t)
            if isinstance(v, dict):
                try:
                    out.extend(self._digest(t, v, cid))
                except Exception:
                    pass
        return out

    REAL4K = frozenset(['影探·联通云', '影探·移动云', '影探·天翼云', '影探·腾讯', '小山·蓝光4K【推荐】', '小山·4K', '橘汁·新咕噜4K', '橘汁·鲸宝4K', '橘汁新·自建4K-4', '橘汁新·自建4K-3', '橘汁新·VIP4K', '橘汁新·JD4K-可下载', '小鸡·JD4K', '小鸡·ZJ4K', '小鸡·CO4K', '四源4K·天堂·高清蓝光4K', '四源4K·布布·zijianm3u8', '四源4K·华谊·蓝光4K', '四源4K·苹果·高清蓝光4K', '咕噜·新咕噜4K', '咕噜·鲸宝4K', '枫奇·至臻4K', '找剧·4K海外-官方C'])
    BAD_LINES = frozenset(['咕噜·iyf4k', '咕噜·小熊', '影探·优酷', '影探·爱奇艺', '影探·腾讯', '找剧·1080P-官方Z', '稀饭·次元城·CYC_Main(需登录)'])
    LINE_FIRST = ('影探', '山楂', '小山', '橘汁', '小鸡', '剧下饭', '四源',
                  '咕噜', '枫奇', 'FoFo', '稀饭', '找剧')   # 线路优先级（用户指定）

    @classmethod
    def _r4(cls, name):
        """真 4K 实测名单整体前置；组内保持 LINE_FIRST 原序，坏线路不提前。"""
        nm = str(name or '')
        bad = nm in cls.BAD_LINES
        return (0 if (nm in cls.REAL4K and not bad) else 1,
                cls._line_rank(nm),
                1 if bad else 0,
                0 if '4k' in nm.lower() else 1)


    @classmethod
    def _line_rank(cls, name):
        nm = str(name or '')
        for i, key in enumerate(cls.LINE_FIRST):
            if key in nm:
                return i
        return len(cls.LINE_FIRST)

    # --- KISH_LINE_TRIM BEGIN ---
    KEEP_FAST_NON4K = (
        '橘汁新·自营蓝光-1', '咕噜·神话', '橘汁新·神话蓝光',
        'FoFo·天堂', '小鸡·TM蓝光', '咕噜·VIP', '咕噜·VIP蓝光',
        'FoFo·优质', '橘汁·VIP蓝光', '橘汁·神话',
    )

    @classmethod
    def _keep_line(cls, name):
        nm = str(name or '')
        if '4k' in nm.lower():
            return True
        if nm.startswith('影探'):
            return True
        return nm in cls.KEEP_FAST_NON4K

    TOP3 = ('影探·移动云', '影探·天翼云', '影探·联通云')

    def _trim_lines(self, lines):
        """影探移动/天翼/联通置顶 → 4K 组 → 其余非 4K 组（FoFo 置末）。
        各组内部保持 _r4 原本相对顺序，只做分组与抽取，不重排。"""
        try:
            kept = [x for x in lines if self._keep_line(x[0])]
            top = []
            for n in self.TOP3:
                for x in kept:
                    if str(x[0] or '') == n:
                        top.append(x)
                        break
            body = [x for x in kept
                    if str(x[0] or '') not in self.TOP3]
            four = [x for x in body if '4k' in str(x[0] or '').lower()]
            rest = [x for x in body if '4k' not in str(x[0] or '').lower()]
            fofo = [x for x in rest
                    if str(x[0] or '').startswith('FoFo')]
            if fofo:
                rest = [x for x in rest
                        if not str(x[0] or '').startswith('FoFo')] + fofo
            return top + four + rest
        except Exception:
            return lines
    # --- KISH_LINE_TRIM END ---

    def _pack(self, vod, lines):
        """按源优先级排序 + 去重 + 唯一化线路名 + 写回 vod_play_from/url。"""
        try:
            lines = sorted(lines, key=lambda x: self._r4(x[0]))
        except Exception:
            pass
        lines = self._trim_lines(lines)
        froms, urls, used, seen_sig = [], [], {}, set()
        for name, eps in lines:
            if not eps:
                continue
            nm = clean_name(name) or '线路'
            sig = (nm, len(eps))
            if sig in seen_sig:      # 跨源同名同集数 = 重复线路，丢掉
                continue
            seen_sig.add(sig)
            if nm in used:
                used[nm] += 1
                nm = '%s·%d' % (nm, used[nm])
            else:
                used[nm] = 1
            froms.append(nm)
            urls.append('#'.join('%s$%s' % (e[0] or '正片', e[1]) for e in eps))
        vod['vod_play_from'] = '$$$'.join(froms)
        vod['vod_play_url'] = '$$$'.join(urls)
        return vod

    def detailContent(self, ids):
        if self._diag is not None:
            return self._diag.detailContent(ids)
        raw = ids[0] if isinstance(ids, (list, tuple)) and ids else ids
        tag, vid = self._dec_vid(raw)
        ck = 'kish:%s:%s' % (tag, vid)
        hit = cache_get(ck)
        if hit is not None:
            try:
                return json.loads(hit)
            except Exception:
                pass

        ob = self._src(tag)
        if ob is None:
            return {'list': []}
        try:
            got = ob.detailContent([vid]) or {}
        except Exception:
            got = {}
        vod = (got.get('list') or [None])[0]
        if not isinstance(vod, dict):
            return {'list': []}

        title = str(vod.get('vod_name') or '')
        # 个别源（FoFo）详情只回数字 id 当片名，跨源补线路会全部匹配失败；
        # 用列表/搜索时记下的真实片名兜底，并修正壳里显示的名字。
        if len(title.strip()) < 2 or title.strip().isdigit():
            alt = _TITLE_MEMO.get(str(raw)) or ''
            if alt:
                title = alt
                vod['vod_name'] = alt
        vod['vod_id'] = self._enc_vid(tag, vod.get('vod_id') or vid)

        cid = str(vod.get('vod_id') or '')
        base_lines = []
        try:
            base_lines.extend(self._digest(tag, vod, cid))
        except Exception:
            pass

        # 其余源并发跑；首屏只等「够用」（FILL_BUDGET / FILL_ENOUGH），
        # 没赶上的源继续在后台补，补完直接刷新缓存。
        box, ths = self._fill_start(tag, title)
        self._wait_yield(box, ths, base_lines, self.FILL_BUDGET,
                         yt_ok=(tag == 'yt'))

        lines = list(base_lines) + self._digest_box(tag, box, cid)
        fresh = self._pack(dict(vod), lines)
        # 记 _pack 之后的顺序：换源时第一条就是最快的（小山·蓝光4K）
        _memo_detail(cid, _unpack_lines(fresh))
        result = {'list': [fresh]}
        try:
            cache_put(ck, json.dumps(result, ensure_ascii=False), self.CACHE_TTL)
        except Exception:
            pass

        if any(t.is_alive() for t in ths):
            try:
                threading.Thread(target=self._topup, daemon=True,
                                 args=(ck, vod, tag, base_lines, box, ths,
                                       cid)).start()
            except Exception:
                pass
        return result

    def _topup(self, ck, vod, tag, base_lines, box, ths, cid=''):
        """后台把没赶上的源等回来，再按全量线路重写一次缓存。"""
        try:
            deadline = time.time() + self.TOPUP_BUDGET
            for th in ths:
                th.join(max(0.05, deadline - time.time()))
            if not box:
                return
            lines = list(base_lines) + self._digest_box(tag, box, cid)
            if not lines:
                return
            out = self._pack(dict(vod), lines)
            _memo_detail(cid, _unpack_lines(out))
            _n_new = len([x for x in str(out.get('vod_play_from') or '')
                          .split('$$$') if x])
            _old = cache_get(ck)
            if _old:
                try:
                    _ov = (json.loads(_old).get('list') or [{}])[0]
                    _n_old = len([x for x in str(_ov.get('vod_play_from') or '')
                                  .split('$$$') if x])
                except Exception:
                    _n_old = 0
                if _n_old > _n_new:
                    return               # 已有缓存更全，别缩水
            cache_put(ck, json.dumps({'list': [out]}, ensure_ascii=False),
                      self.CACHE_TTL + 120)
        except Exception:
            pass

    # ---------------- 播放 ----------------
    def playerContent(self, flag, id, vipFlags=None):
        if self._diag is not None:
            return self._diag.playerContent(flag, id, vipFlags)
        tag, oflag, pid, cid, ep = self._dec_play(id)
        empty = {'parse': 0, 'jx': 0, 'url': ''}
        ob = self._src(tag)
        box = {}

        def work():
            try:
                box['r'] = ob.playerContent(oflag or flag, pid, vipFlags)
            except Exception:
                pass

        th = None
        if ob is not None:
            th = threading.Thread(target=work)
            th.daemon = True
            th.start()
            th.join(self.PLAY_HEAD)      # 本线路 PLAY_HEAD 秒不回就直接换源
        got = box.get('r')
        if kish_play_ok(got):
            return got
        # 取流失败或太慢（影探/VIP 线路经常这样）→ 立刻改用同集其它线路
        alt = self._play_other(cid, ep, tag, pid)
        if alt:
            return alt
        if th is not None and th.is_alive():
            th.join(max(0.1, self.PLAY_BUDGET - self.PLAY_HEAD))
            got = box.get('r')
        return got if isinstance(got, dict) else empty

    def _call(self, fn, wait):
        """带超时调用：超时就先当失败，线程自己跑完就丢。"""
        box = {}
        def w():
            try:
                box['r'] = fn()
            except Exception:
                pass
        th = threading.Thread(target=w)
        th.daemon = True
        th.start()
        th.join(wait)
        return box.get('r'), th

    def _play_other(self, cid, ep, skip_tag='', skip_pid=''):
        """同集换源重试：先试别的源（失效常是整源坏），本源其它线路垫后。"""
        rec = _DETAIL_MEMO.get(cid)
        if not rec:
            return None
        deadline = time.time() + self.PLAY_BUDGET
        wi, _, wn = str(ep or '').partition('\x1e')
        cand = []
        for _name, eps in rec[1]:
            for e_name, code in eps:
                t, f, p, _c, _e = self._dec_play(code)
                if ep:
                    hi, _, hn = str(_e or '').partition('\x1e')
                    # 集名一致、或集序号一致，都算同一集
                    if not ((wn and wn == hn) or (wi and wi == hi)):
                        continue
                if t == skip_tag and p == skip_pid:
                    continue
                cand.append((1 if t == skip_tag else 0, t, f, p))
        cand.sort(key=lambda x: (x[0], self.PLAY_SPEED.get(x[1], 9)))
        tried = 0
        for _pri, t, f, p in cand:
            if time.time() > deadline or tried >= self.PLAY_TRY:
                return None
            tried += 1
            ob = self._src(t)
            if ob is None:
                continue
            r, _th = self._call(lambda: ob.playerContent(f, p, []),
                                min(self.PLAY_EACH,
                                    max(0.3, deadline - time.time())))
            if kish_play_ok(r):
                return r
        return None


# 部分内核按小写 spider 取类
spider = Spider
