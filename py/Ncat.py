# -*- coding: utf-8 -*-
# by @Qist
"""
网飞猫 (ncat25.com / ncat1.app) - Netflix/韩剧在线观看
cdndefend 反爬：SHA1 工作量证明，每域名 hash 不同，动态求解
"""
import re
import time
import hashlib
import requests
from urllib.parse import quote
from base.spider import Spider


class Spider(Spider):
    def getName(self):
        return '网飞猫'

    def init(self, extend=""):
        # 多域名，按顺序尝试（CDN 可能封 IP）
        self.hosts = ['https://www.ncat25.com', 'https://www.ncat1.app']
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        self.timeout = 20
        self.session = requests.Session()
        self.session.headers.update(self.header)
        self._token = ''
        self.host = self.hosts[0]
        self._ensure_host()

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    def _crack(self, host):
        """对指定域名解 cdndefend 挑战，成功返回 True"""
        try:
            r = self.session.get(host + '/', timeout=self.timeout, allow_redirects=False)
        except:
            return False
        m = re.search(r"a0_0x2a54=\['([0-9A-F]{40})'", r.text)
        if not m:
            # 没有挑战页，说明 cookie 已生效或无需挑战
            return True
        h = m.group(1)
        n1 = int(h[0], 16)
        i = 0
        while True:
            d = hashlib.sha1((h + str(i)).encode()).digest()
            if d[n1] == 0xb0 and d[n1 + 1] == 0x0b:
                break
            i += 1
            if i > 20000000:
                return False
        domain = host.split('//')[1].split('/')[0]
        self.session.cookies.set('cdndefend_js_cookie', h + str(i), domain=domain)
        r2 = self.session.get(host + '/', timeout=self.timeout)
        return 'cdndefend' not in r2.text and 'a0_0x2a54' not in r2.text

    def _ensure_host(self):
        """选择第一个可用域名并解挑战"""
        for h in self.hosts:
            self.host = h
            self.header['Referer'] = h + '/'
            self.session.headers['Referer'] = h + '/'
            if self._crack(h):
                return

    def _safe_get(self, url, headers=None):
        try:
            resp = self.session.get(url, headers=headers, timeout=self.timeout)
            resp.encoding = 'utf-8'
            if resp.status_code == 200:
                return resp
        except:
            pass
        return None

    def _get_token(self):
        """搜索所需的 t token（从首页搜索表单提取）"""
        if self._token:
            return self._token
        resp = self._safe_get(self.host + '/')
        if resp:
            m = re.search(r'name="t" value="([^"]+)"', resp.text)
            if m:
                self._token = m.group(1)
        return self._token

    def _pic(self, src):
        if not src:
            return ''
        if src.startswith('http'):
            return src
        return self.host + src

    def _parse_videos(self, html):
        """解析 module-item 列表 / search-result-item 搜索项"""
        videos = []
        seen = set()
        # 频道/首页列表
        for m in re.finditer(
            r'<div class="module-item">\s*<a href="(/detail/(\d+)\.html)"[^>]*>'
            r'.*?<div class="v-item-bottom">\s*<span>\s*([^<]*?)\s*</span>.*?'
            r'<div class="v-item-title">([^<]*)</div>',
            html, re.S):
            url, vid, remarks, name = m.group(1), m.group(2), m.group(3), m.group(4)
            name = name.strip()
            if not name or vid in seen:
                continue
            seen.add(vid)
            # 封面：取真实图（跳过 logo 占位）
            pic = ''
            pm = re.search(r'data-original="([^"]+)"', m.group(0))
            while pm:
                p = pm.group(1)
                if 'logo_placeholder' not in p and 'vod_pc_static_ncat' not in p:
                    pic = p
                    break
                pm = re.search(r'data-original="([^"]+)"', m.group(0)[pm.end():])
            videos.append({
                'vod_id': vid,
                'vod_name': name,
                'vod_pic': self._pic(pic),
                'vod_remarks': remarks.strip(),
            })
        # 搜索项
        if not videos:
            for m in re.finditer(
                r'<a href="(/detail/(\d+)\.html)" class="search-result-item">'
                r'.*?<img[^>]+data-original="([^"]+)"[^>]*>',
                html, re.S):
                url, vid, pic = m.group(1), m.group(2), m.group(3)
                if vid in seen:
                    continue
                seen.add(vid)
                nm = re.search(r'<img[^>]+alt="([^"]+)"', m.group(0))
                videos.append({
                    'vod_id': vid,
                    'vod_name': nm.group(1) if nm else '',
                    'vod_pic': self._pic(pic),
                    'vod_remarks': '',
                })
        return videos

    # ------------------------------------------------------------------ #
    # 首页
    # ------------------------------------------------------------------ #
    def homeContent(self, filter):
        result = {'class': [], 'list': []}
        for tid, name in [('1', '电影'), ('2', '连续剧'), ('3', '动漫'), ('4', '综艺纪录'), ('6', '短剧')]:
            result['class'].append({'type_name': name, 'type_id': tid})
        resp = self._safe_get(self.host + '/')
        if resp:
            result['list'] = self._parse_videos(resp.text)[:30]
        return result

    def homeVideoContent(self):
        return {}

    # ------------------------------------------------------------------ #
    # 分类（每频道固定 48 条，无分页）
    # ------------------------------------------------------------------ #
    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg)
        result = {'list': [], 'page': pg, 'pagecount': 1, 'limit': 0, 'total': 0}
        resp = self._safe_get(f'{self.host}/channel/{tid}.html')
        if not resp:
            return result
        videos = self._parse_videos(resp.text)
        result['list'] = videos
        result['limit'] = len(videos)
        result['total'] = len(videos)
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

        # 标题（.detail-title 里的 strong，排除水印域名）
        name = ''
        dm = re.search(r'class="detail-title[^"]*"[^>]*>(.*?)</div>', html, re.S)
        if dm:
            for m in re.finditer(r'<strong[^>]*>([^<]{2,60})</strong>', dm.group(1)):
                t = m.group(1).strip()
                # 水印用数学字母（U+1D400 起）伪装域名，排除之
                if t and not any('\U0001D400' <= ch <= '\U0001D7FF' for ch in t) and not re.search(r'[a-zA-Z0-9]{2,}\.', t):
                    name = t
                    break

        # 封面
        pic = ''
        m = re.search(r'data-original="(/vod1/vod/cover/[^"]+)"', html)
        if m:
            pic = m.group(1)

        # 详情信息
        info = {}
        for m in re.finditer(r'class="detail-info-row-side">([^<]*)</div>\s*<div class="detail-info-row-main">(.*?)</div>', html, re.S):
            side = m.group(1).strip().rstrip('：:')
            main = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', m.group(2))).strip()
            if side in ('导演', '演员', '首映', '备注'):
                info[side] = main

        vod = {
            'vod_id': vid,
            'vod_name': name,
            'vod_pic': self._pic(pic),
            'vod_remarks': info.get('备注', ''),
            'vod_year': (info.get('首映') or '')[:4],
            'vod_director': info.get('导演', ''),
            'vod_actor': info.get('演员', ''),
            'vod_content': '',
        }

        # 播放列表：source-item 线路名 + episode-list 集数
        sources = re.findall(r'<span class="source-item-label">([^<]*)</span>', html)
        box = re.search(r'<div class="episode-list-box-main[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>', html, re.S)
        play_from, play_url = [], []
        if box and sources:
            lists = re.findall(r'<div class="episode-list[^"]*"[^>]*>(.*?)</div>', box.group(1), re.S)
            for idx, src in enumerate(sources):
                if idx >= len(lists):
                    break
                eps = re.findall(r'href="(/play/[^"]+)"[^>]*class="episode-item"[^>]*>\s*<span>([^<]*)</span>', lists[idx])
                if not eps:
                    continue
                play_from.append(src)
                play_url.append('#'.join(f'{ep}$' + self.host + href for href, ep in eps))
        if not play_url:
            return {'list': []}
        vod['vod_play_from'] = '$$$'.join(play_from)
        vod['vod_play_url'] = '$$$'.join(play_url)
        return {'list': [vod]}

    # ------------------------------------------------------------------ #
    # 搜索（需首页 t token）
    # ------------------------------------------------------------------ #
    def searchContent(self, key, quick, pg="1"):
        result = {'list': []}
        token = self._get_token()
        if not token:
            return result
        try:
            url = f'{self.host}/search?k={quote(str(key))}&t={quote(token)}'
            resp = self.session.get(url, headers={'Referer': self.host + '/'}, timeout=self.timeout)
            resp.encoding = 'utf-8'
            result['list'] = self._parse_videos(resp.text)
        except:
            pass
        return result

    # ------------------------------------------------------------------ #
    # 播放（明文 m3u8 直接嵌在播放页 JS）
    # ------------------------------------------------------------------ #
    def playerContent(self, flag, id, vipFlags):
        h = {'User-Agent': self.header['User-Agent'], 'Referer': self.host + '/'}
        resp = self._safe_get(id, {'Referer': id})
        if not resp:
            return {'parse': 1, 'url': id, 'header': h, 'playUrl': ''}
        html = resp.text
        m = re.search(r'playSource\s*=\s*\{\s*src:\s*"([^"]+)"', html)
        if m and m.group(1).startswith('http'):
            return {'parse': 0, 'url': m.group(1), 'header': h, 'playUrl': ''}
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
