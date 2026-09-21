# -*- coding: utf-8 -*-
# by @Qist
"""
厂长资源 (4kcz.com) - 在线超清播放
"""
import re
import json
import base64
import requests
from urllib.parse import quote, unquote
from base.spider import Spider

try:
    from Crypto.Cipher import AES
except ImportError:
    AES = None


class Spider(Spider):
    def getName(self):
        return '厂长资源'

    def init(self, extend=""):
        self.host = 'https://www.4kcz.com'
        if extend and extend.strip():
            try:
                r = requests.get(extend.strip(), headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
                m = re.search(r'推荐访问<a href="(//[^"]+)"', r.text)
                if m:
                    self.host = 'https:' + m.group(1).rstrip('/')
            except:
                pass
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
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

    # ------------------------------------------------------------------ #
    # 通用解析
    # ------------------------------------------------------------------ #
    @staticmethod
    def _strip_tags(html):
        return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', html)).strip()

    def _parse_videos(self, html):
        """解析 .bt_img.mi_ne_kd ul li 视频列表"""
        videos = []
        seen = set()
        block = re.search(r'class="bt_img[^"]*mi_ne_kd[^"]*"[^>]*>(.*?)</ul>', html, re.S)
        if not block:
            return videos
        for li in re.findall(r'<li[^>]*>(.*?)</li>', block.group(1), re.S):
            m = re.search(r'<a[^>]+href="([^"]+)"', li)
            if not m:
                continue
            url = m.group(1)
            name_m = re.search(r'class="dytit"[^>]*>.*?<a[^>]*>(.*?)</a>', li, re.S)
            name = self._strip_tags(name_m.group(1)) if name_m else ''
            if not name or url in seen:
                continue
            seen.add(url)
            pic = ''
            pm = re.search(r'<img[^>]+(?:data-original|src)="([^"]+)"', li)
            if pm:
                pic = pm.group(1)
            remarks = ''
            rm = re.search(r'class="jidi[^"]*"[^>]*>\s*<span[^>]*>([^<]*)</span>', li, re.S) \
                or re.search(r'class="hdinfo[^"]*"[^>]*>\s*<span[^>]*>([^<]*)</span>', li, re.S)
            if rm:
                remarks = rm.group(1).strip()
            mid = re.search(r'/movie/(\d+)\.html$', url)
            videos.append({
                'vod_id': mid.group(1) if mid else url,
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
        resp = self._safe_get(self.host + '/')
        if not resp:
            return result
        html = resp.text
        # 分类：导航菜单 + 常用细分分类
        nav = re.search(r'class="navlist[^"]*"[^>]*>(.*?)</ul>', html, re.S)
        if nav:
            for a in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', nav.group(1), re.S):
                url, name = a[0], self._strip_tags(a[1])
                if not name or name == '首页' or not url.startswith('/'):
                    continue
                result['class'].append({'type_name': name, 'type_id': url.lstrip('/')})
        # 补充细分分类（电影/剧集等）
        for name, cid in [
            ('电影', 'movie_bt_series/dyy'), ('电视剧', 'movie_bt_series/dianshiju'),
            ('动画', 'movie_bt_series/dohua'), ('国产剧', 'movie_bt_series/guochanju'),
            ('日剧', 'movie_bt_series/rj'), ('韩剧', 'movie_bt_series/hj'),
            ('美剧', 'movie_bt_series/mj'), ('华语电影', 'movie_bt_series/huayudianying'),
            ('欧美电影', 'movie_bt_series/meiguodianying'), ('日本电影', 'movie_bt_series/ribendianying'),
            ('韩国电影', 'movie_bt_series/hanguodianying'),
        ]:
            if not any(c['type_id'] == cid for c in result['class']):
                result['class'].append({'type_name': name, 'type_id': cid})
        # 首页推荐（取分类页 20 条）
        cat = self._safe_get(f'{self.host}/movie_bt/')
        if cat:
            result['list'] = self._parse_videos(cat.text)[:20]
        else:
            result['list'] = self._parse_videos(html)[:20]
        if filter and result['class']:
            # 类型/分类筛选（movie_bt 主分类，按站点标签）
            result['filters'] = {
                'movie_bt': [
                    {'key': 'class', 'name': '类型', 'value': [
                        {'n': '全部', 'v': ''}, {'n': '动作', 'v': '/movie_bt_tags/dozuo'},
                        {'n': '喜剧', 'v': '/movie_bt_tags/xiju'}, {'n': '爱情', 'v': '/movie_bt_tags/aiqing'},
                        {'n': '科幻', 'v': '/movie_bt_tags/kh'}, {'n': '剧情', 'v': '/movie_bt_tags/juqing'},
                        {'n': '恐怖', 'v': '/movie_bt_tags/kubu'}, {'n': '悬疑', 'v': '/movie_bt_tags/xuanyi'},
                        {'n': '动画', 'v': '/movie_bt_tags/dhh'}, {'n': '纪录片', 'v': '/movie_bt_tags/jlpp'},
                        {'n': '战争', 'v': '/movie_bt_tags/zhanzhen'}, {'n': '武侠', 'v': '/movie_bt_tags/wuxia'},
                        {'n': '犯罪', 'v': '/movie_bt_tags/fanzui'}, {'n': '奇幻', 'v': '/movie_bt_tags/qihuan'},
                    ]},
                    {'key': 'area', 'name': '分类', 'value': [
                        {'n': '全部', 'v': ''}, {'n': '电影', 'v': '/movie_bt_series/dyy'},
                        {'n': '电视剧', 'v': '/movie_bt_series/dianshiju'}, {'n': '动画', 'v': '/movie_bt_series/dohua'},
                        {'n': '国产剧', 'v': '/movie_bt_series/guochanju'}, {'n': '美剧', 'v': '/movie_bt_series/mj'},
                        {'n': '日剧', 'v': '/movie_bt_series/rj'}, {'n': '韩剧', 'v': '/movie_bt_series/hj'},
                        {'n': '华语电影', 'v': '/movie_bt_series/huayudianying'},
                        {'n': '欧美电影', 'v': '/movie_bt_series/meiguodianying'},
                        {'n': '日本电影', 'v': '/movie_bt_series/ribendianying'},
                        {'n': '韩国电影', 'v': '/movie_bt_series/hanguodianying'},
                        {'n': '会员专区', 'v': '/movie_bt_series/huiyuanzhuanqu'},
                    ]},
                ],
            }
        return result

    def homeVideoContent(self):
        return {}

    # ------------------------------------------------------------------ #
    # 分类
    # ------------------------------------------------------------------ #
    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg)
        result = {'list': [], 'page': pg, 'pagecount': 999, 'limit': 0, 'total': 0}
        tid = str(tid).strip('/')
        extend = extend or {}
        sub = (extend.get('class') or extend.get('area') or '').strip('/') if tid == 'movie_bt' else ''
        path = f'{tid}/{sub}'.strip('/') if sub else tid
        resp = self._safe_get(f'{self.host}/{path}/page/{pg}')
        if not resp:
            return result
        videos = self._parse_videos(resp.text)
        result['list'] = videos
        result['limit'] = len(videos)
        pagecount = 999
        nums = [int(x) for x in re.findall(r'[^"]*page/(\d+)[^"]*"[^>]*>(?:»|>|下一页)', resp.text)]
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
        resp = self._safe_get(f'{self.host}/movie/{vid}.html')
        if not resp:
            return {'list': []}
        html = resp.text

        vod = {'vod_id': vid}
        m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S)
        vod['vod_name'] = self._strip_tags(m.group(1)) if m else ''
        m = re.search(r'class="dyimg[^"]*"[^>]*>\s*<img[^>]+src="([^"]+)"', html, re.S)
        vod['vod_pic'] = m.group(1) if m else ''
        vod['vod_remarks'] = ''

        # 详情信息
        info = {}
        for m in re.finditer(r'<li[^>]*>(.*?)</li>', html, re.S):
            text = self._strip_tags(m.group(1))
            for k, label in [('类型', '类型'), ('地区', '地区'), ('年份', '年份'),
                             ('导演', '导演'), ('主演', '主演'), ('语言', '语言')]:
                if text.startswith(label + '：') or text.startswith(label + ':'):
                    info[k] = text.split('：', 1)[-1].split(':', 1)[-1].strip()
                    break
        vod['vod_year'] = info.get('年份', '')
        vod['vod_area'] = info.get('地区', '')
        vod['vod_director'] = info.get('导演', '')
        vod['vod_actor'] = info.get('主演', '')
        vod['type_name'] = info.get('类型', '')
        m = re.search(r'class="yp_context[^"]*"[^>]*>(.*?)</div>', html, re.S)
        vod['vod_content'] = self._strip_tags(m.group(1)) if m else ''

        # 播放列表
        play_urls = []
        for m in re.finditer(r'class="paly_list_btn[^"]*"[^>]*>(.*?)</div>', html, re.S):
            for a in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', m.group(1), re.S):
                href, name = a[0], self._strip_tags(a[1])
                if href and name:
                    if href.startswith('/'):
                        href = self.host + href
                    play_urls.append(f'{name}${href}')
        if not play_urls:
            return {'list': []}
        vod['vod_play_from'] = '厂长资源'
        vod['vod_play_url'] = '#'.join(play_urls)
        return {'list': [vod]}

    # ------------------------------------------------------------------ #
    # 搜索（slg 人机验证拦截时返回空）
    # ------------------------------------------------------------------ #
    def searchContent(self, key, quick, pg="1"):
        result = {'list': []}
        try:
            url = f'{self.host}/boss1O1?q={quote(str(key))}'
            resp = self.session.get(url, headers={'Referer': self.host + '/'}, timeout=self.timeout)
            resp.encoding = 'utf-8'
            html = resp.text
            if 'slg-' in html or '.bt_img' not in html:
                return result
            result['list'] = self._parse_videos(html)
        except:
            pass
        return result

    # ------------------------------------------------------------------ #
    # 播放
    # ------------------------------------------------------------------ #
    @staticmethod
    def _decrypt_aes(data, key, iv):
        if AES is None:
            return ''
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plain = cipher.decrypt(base64.b64decode(data))
        pad = plain[-1]
        if 1 <= pad <= 16:
            plain = plain[:-pad]
        return plain.decode('utf-8', 'ignore')

    def playerContent(self, flag, id, vipFlags):
        h = {'User-Agent': self.header['User-Agent'], 'Referer': self.host + '/'}
        resp = self._safe_get(id, {'Referer': id})
        if not resp:
            return {'parse': 1, 'url': id, 'header': h, 'playUrl': ''}
        html = resp.text

        # 1) 播放页内联 mysvg 直链
        m = re.search(r"const mysvg\s*=\s*'([^']+)'", html)
        if m and m.group(1).startswith('http'):
            return {'parse': 0, 'url': m.group(1), 'header': h, 'playUrl': ''}

        # 2) Cloud 播放器（dncry AES 解密）
        m = re.search(r'"([^"]+)";var [\d\w]+=function dncry.*?md5\.enc\.Utf8\.parse\("([\d\w]+)".*?md5\.enc\.Utf8\.parse\(([\d]+)\)', html)
        if m:
            url = self._decrypt_aes(m.group(1), m.group(2).encode(), m.group(3).encode())
            mm = re.search(r'video: \{url: "([^"]+)"', url)
            if mm and mm.group(1):
                return {'parse': 0, 'url': mm.group(1), 'header': h, 'playUrl': ''}

        # 3) iframe 解析（py1080p / result_v2）
        iframe = re.search(r'<iframe[^>]+src="([^"]+)"', html)
        if iframe:
            src = iframe.group(1)
            if src.startswith('//'):
                src = 'https:' + src
            fresp = self._safe_get(src, {'Referer': id})
            if fresp:
                fhtml = fresp.text
                m = re.search(r"const mysvg\s*=\s*'([^']+)'", fhtml)
                if m and m.group(1).startswith('http'):
                    return {'parse': 0, 'url': m.group(1), 'header': h, 'playUrl': ''}
                m = re.search(r'var result_v2 = (\{.*?\});', fhtml)
                if m:
                    try:
                        real = unquote(json.loads(m.group(1)).get('data', '')[::-1])
                        if real.startswith('http'):
                            return {'parse': 0, 'url': real, 'header': h, 'playUrl': ''}
                    except:
                        pass

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
