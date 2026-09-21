# -*- coding: utf-8 -*-
# by @Qist
"""
嘀嗒影视 (didahd.xyz) - 海外华人影视
"""
import re
import json
import time
import base64
import hashlib
import requests
from urllib.parse import quote, unquote
from base.spider import Spider

try:
    from Crypto.Cipher import AES
except ImportError:
    AES = None

# smart-play 接口与解密盐（来自播放器混淆脚本）
_API_URL = 'https://hd.ticktockwow.com/smartplay-cache/api/webvideo_ty.php'
_SALT = 'RY7e48naFXPsLJC'


class Spider(Spider):
    def getName(self):
        return '嘀嗒影视'

    def init(self, extend=""):
        self.host = 'https://www.didahd.xyz'
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Referer': self.host + '/',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        self.timeout = 20
        self.session = requests.Session()
        self.session.headers.update(self.header)

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    def _safe_get(self, url, headers=None):
        try:
            resp = self.session.get(url, headers=headers, timeout=self.timeout)
            resp.encoding = 'utf-8'
            if resp.status_code == 200:
                return resp
        except:
            pass
        return None

    def _parse_videos(self, html):
        """解析 myui-vodlist ul li 视频列表"""
        videos = []
        seen = set()
        block = re.search(r'<ul class="myui-vodlist[^"]*"[^>]*>(.*?)</ul>', html, re.S)
        if not block:
            return videos
        for li in re.findall(r'<li[^>]*>(.*?)</li>', block.group(1), re.S):
            m = re.search(r'<a[^>]+href="(/detail/\d+\.html)"[^>]*title="([^"]*)"', li)
            if not m:
                continue
            url, name = m.group(1), m.group(2)
            if not name or url in seen:
                continue
            seen.add(url)
            pic = ''
            pm = re.search(r'data-original="([^"]+)"', li)
            if pm:
                pic = pm.group(1)
            remarks = ''
            rm = re.search(r'class="pic-text[^"]*"[^>]*>([^<]*)', li, re.S)
            if rm:
                remarks = re.sub(r'\s+', ' ', rm.group(1)).strip()
            videos.append({
                'vod_id': m.group(1).rstrip('.html').split('/')[-1],
                'vod_name': name,
                'vod_pic': pic,
                'vod_remarks': remarks,
            })
        return videos

    # ------------------------------------------------------------------ #
    # 首页
    # ------------------------------------------------------------------ #
    def homeContent(self, filter):
        result = {'class': [], 'list': []}
        for tid, name in [('1', '电影'), ('2', '电视剧'), ('3', '纪录片'), ('4', '动漫'), ('5', '综艺')]:
            result['class'].append({'type_name': name, 'type_id': tid})
        resp = self._safe_get(self.host + '/')
        if resp:
            result['list'] = self._parse_videos(resp.text)[:30]
        return result

    def homeVideoContent(self):
        return {}

    # ------------------------------------------------------------------ #
    # 分类
    # ------------------------------------------------------------------ #
    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg)
        result = {'list': [], 'page': pg, 'pagecount': 999, 'limit': 24, 'total': 0}
        # /type/{tid}-{pg}.html 分页（/show/ 筛选被 Cloudflare 拦截，暂不支持）
        resp = self._safe_get(f'{self.host}/type/{tid}-{pg}.html')
        if not resp:
            return result
        videos = self._parse_videos(resp.text)
        result['list'] = videos
        result['limit'] = len(videos)
        pagecount = 999
        nums = [int(n) for n in re.findall(r'/type/' + re.escape(str(tid)) + r'-(\d+)\.html', resp.text)]
        if nums:
            pagecount = max(nums)
        result['pagecount'] = pagecount
        result['total'] = pagecount * len(videos) if videos else 0
        return result

    # ------------------------------------------------------------------ #
    # 详情
    # ------------------------------------------------------------------ #
    def detailContent(self, ids):
        if not ids or not ids[0]:
            return {'list': []}
        vid = ids[0]
        resp = self._safe_get(f'{self.host}/detail/{vid}.html')
        if not resp:
            return {'list': []}
        html = resp.text
        vod = {'vod_id': vid, 'vod_name': '', 'vod_pic': '', 'vod_remarks': ''}

        m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S)
        if m:
            vod['vod_name'] = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', m.group(1))).strip()
        # 海报（myui-content__thumb 里的图）
        m = re.search(r'class="myui-content__thumb[^"]*"[^>]*>.*?<img[^>]+data-original="([^"]+)"', html, re.S)
        if m:
            vod['vod_pic'] = m.group(1)
        else:
            m = re.search(r'class="myui-content__thumb[^"]*"[^>]*>.*?<img[^>]+src="([^"]+)"', html, re.S)
            if m:
                vod['vod_pic'] = m.group(1)

        # 详情信息（多个 <p class="data">，一个 p 可含多个 label:value）
        info = {}
        for mm in re.finditer(r'<p class="data"[^>]*>(.*?)</p>', html, re.S):
            phtml = mm.group(1)
            # 按 label span 切分：parts[0]前缀, [1]label, [2]值, [3]label, [4]值...
            parts = re.split(r'<span class="text-muted[^"]*">([^<]*)</span>', phtml)
            for i in range(1, len(parts), 2):
                label = parts[i].strip().rstrip('：:')
                if label not in ('分类', '地区', '年份', '主演', '导演'):
                    continue
                valhtml = parts[i + 1] if i + 1 < len(parts) else ''
                value = ' '.join(re.findall(r'<(?:a|span)[^>]*>([^<]{1,60})</(?:a|span)>', valhtml))
                value = re.sub(r'\s+', ' ', value).strip()
                if value:
                    info[label] = value
        vod['vod_year'] = info.get('年份', '')
        vod['vod_area'] = info.get('地区', '')
        vod['vod_director'] = info.get('导演', '')
        vod['vod_actor'] = info.get('主演', '')
        vod['type_name'] = info.get('分类', '')
        cm = re.search(r'class="detail-content[^"]*"[^>]*>(.*?)</', html, re.S)
        vod['vod_content'] = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', cm.group(1))).strip() if cm else ''

        # 播放列表（多线路）
        play_from, play_url = [], []
        for pid, name in re.findall(r'href="#(playlist\d+)"[^>]*>([^<]*)</a>', html):
            bm = re.search(r'id="%s"[^>]*>(.*?)</div>' % re.escape(pid), html, re.S)
            if not bm:
                continue
            eps = []
            for href, ep in re.findall(r'<a[^>]+href="(/play/[^"]+)"[^>]*>([^<]*)</a>', bm.group(1)):
                if href:
                    eps.append(f'{ep.strip()}${self.host}{href}')
            if eps:
                play_from.append(name)
                play_url.append('#'.join(eps))
        if not play_url:
            return {'list': []}
        vod['vod_play_from'] = '$$$'.join(play_from)
        vod['vod_play_url'] = '$$$'.join(play_url)
        return {'list': [vod]}

    # ------------------------------------------------------------------ #
    # 搜索
    # ------------------------------------------------------------------ #
    def searchContent(self, key, quick, pg="1"):
        result = {'list': []}
        try:
            url = f'{self.host}/search/{quote(str(key))}-------------.html'
            resp = self.session.get(url, headers={'Referer': self.host + '/'}, timeout=self.timeout)
            resp.encoding = 'utf-8'
            result['list'] = self._parse_videos(resp.text)
        except:
            pass
        return result

    # ------------------------------------------------------------------ #
    # 播放（smart-play 解密链）
    # ------------------------------------------------------------------ #
    @staticmethod
    def _decrypt_aes(data_b64, key_hex, iv_hex):
        if AES is None:
            return ''
        cipher = AES.new(key_hex.encode(), AES.MODE_CBC, iv_hex.encode())
        pt = cipher.decrypt(base64.b64decode(data_b64))
        pad = pt[-1]
        if 1 <= pad <= 16:
            pt = pt[:-pad]
        return pt.decode('utf-8', 'ignore')

    def _resolve_play(self, play_url):
        """/play/xxx.html -> 真实播放地址"""
        h = {'Referer': self.host + '/'}
        # 1) 播放页
        resp = self._safe_get(play_url, h)
        if not resp:
            return ''
        html = resp.text
        i = html.find('player_aaaa=')
        if i < 0:
            return ''
        start = html.find('{', i)
        if start < 0:
            return ''
        depth = 0; j = start
        while j < len(html):
            if html[j] == '{': depth += 1
            elif html[j] == '}':
                depth -= 1
                if depth == 0: break
            j += 1
        try:
            p = json.loads(html[start:j + 1])
        except:
            return ''
        enc_url = p.get('url', '')
        if not enc_url:
            return ''

        # 2) artplayer 页（取 vkey/code/timestamp）
        art = self._safe_get(f'{self.host}/static/player/artplayer/?url={enc_url}', {'Referer': play_url})
        if not art:
            return ''
        ah = art.text
        vkey = re.search(r'const playPageUrl\s*=\s*"([^"]+)"', ah)
        code = re.search(r'const secretKeySeed\s*=\s*"([^"]+)"', ah)
        ts = re.search(r'const timestamp\s*=\s*"([^"]+)"', ah)
        if not (vkey and code and ts):
            return ''
        vkey, code, ts = vkey.group(1), code.group(1), ts.group(1)

        # 3) smart-play 校验接口
        t = int(time.time())
        sig = hashlib.md5(str(t).encode()).hexdigest()
        try:
            r = self.session.post(_API_URL, json={'vkey': vkey, 'code': code, 't': t, 'signature': sig},
                                  headers={'Referer': art.url, 'Origin': self.host,
                                           'Content-Type': 'application/json'}, timeout=self.timeout)
            enc = r.json().get('url', '')
        except:
            return ''

        # 4) AES 解密
        md = hashlib.md5((ts + _SALT).encode()).hexdigest()
        real = self._decrypt_aes(enc, md[16:32], md[0:16])
        if real.startswith('http'):
            return real
        return ''

    def playerContent(self, flag, id, vipFlags):
        h = {'User-Agent': self.header['User-Agent'], 'Referer': self.host + '/'}
        real = self._resolve_play(id)
        if real:
            return {'parse': 0, 'url': real, 'header': h, 'playUrl': ''}
        return {'parse': 1, 'url': id, 'header': h, 'playUrl': ''}

    def fetch(self, url):
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.encoding = 'utf-8'
            return resp.text if resp.status_code == 200 else None
        except:
            return None

    def localProxy(self, param):
        return None
