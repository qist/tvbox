"""
@header({
  searchable: 1,
  filterable: 1,
  quickSearch: 1,
  title: '菠菜园',
  lang: 'hipy',
})
"""

# coding=utf-8
"""
全网影视聚合爬虫 
适配 Fongmi / TVBox 规范
- 多源聚合（全球、极速、百度、优质、红牛、魔都等33个源）
- 已移除首页推荐视频列表（homeVideoContent 返回空）
- 弹幕自动匹配（播放时后台匹配 弹幕库并推送到本地）
"""
import sys
import json
import concurrent.futures
import re
import time
import threading
import requests
import urllib.parse
from urllib.parse import quote

sys.path.append('..')
from base.spider import Spider


class Spider(Spider):
    SOURCES = {
        '360': {'name': '️360', 'api': 'https://360zy.com/api.php/provide/vod/'},      
        '极速': {'name': '极速', 'api': 'https://jszyapi.com/api.php/provide/vod/from/jsm3u8/at/json'},     
        '百度': {'name': '️百度', 'api': 'https://api.apibdzy.com/api.php/provide/vod/'},
        '丫丫': {'name': '️丫丫', 'api': 'https://api.yyzy-tv.vip/inc/apijson.php'},       
        '红牛': {'name': '️红牛', 'api': 'https://www.hongniuzy3.com/api.php/provide/vod/from/hnm3u8/at/josn/'},        
         '厂长': {'name': '️厂长', 'api': 'https://api.changzhang.tv/api.php/provide/vod/from/changzhangm3u8/'},
        '母鸡': {'name': '️母鸡', 'api': 'https://mujiziyuan00.com/api.php/provide/vod/?ac=list'},
        '暴风': {'name': '️暴风', 'api': 'https://bfzyapi.com/api.php/provide/vod/'},
        '闪电': {'name': '️闪电', 'api': 'https://xsd.sdzyapi.com/api.php/provide/vod/'},
        '索尼': {'name': '️索尼', 'api': 'https://suoniapi.com/api.php/provide/vod/'},
        '量子': {'name': '️量子', 'api': 'https://cj.lziapi.com/api.php/provide/vod/from/lzm3u8/'},
        '非凡': {'name': '️非凡', 'api': 'http://cj.ffzyapi.com/api.php/provide/vod/'},
        '牛牛': {'name': '️牛牛', 'api': 'https://api.niuniuzy.me/api.php/provide/vod/'},
        '最大': {'name': '️最大', 'api': 'http://zuidazy.me/api.php/provide/vod/'},
        '无尽': {'name': '️无尽', 'api': 'https://api.wujinapi.me/api.php/provide/vod/'},
        '爱旦': {'name': '️爱旦', 'api': 'https://lovedan.net/api.php/provide/vod/'},
        '爱奇艺': {'name': '️爱奇艺', 'api': 'https://iqiyizyapi.com/api.php/provide/vod/'},
        '电影天堂': {'name': '️电影天堂', 'api': 'http://caiji.dyttzyapi.com/api.php/provide/vod/?ac=list'},
        '金鹰': {'name': '️金鹰', 'api': 'https://jinyingzy.com/api.php/provide/vod/'},
        '快车': {'name': '️快车', 'api': 'https://caiji.kuaichezy.org/api.php/provide/vod/?ac=list'},
        '猫眼': {'name': '️猫眼', 'api': 'https://api.maoyanapi.top/api.php/provide/vod/'},
        '蘑菇': {'name': '️蘑菇', 'api': 'https://www.5o5k.com/api.php/provide/vod/'},
        '速播': {'name': '️速播', 'api': 'https://subocaiji.com/api.php/provide/vod/from/subyun/at/json/'},
        '茅台': {'name': '️茅台', 'api': 'https://caiji.maotaizy.cc/api.php/provide/vod/'},
        '豪华': {'name': '️豪华', 'api': 'https://hhzyapi.com/api.php/provide/vod/'},
        'U酷': {'name': '️U酷', 'api': 'https://api.ukuapi88.com/api.php/provide/vod/'},
        '新浪': {'name': '️新浪', 'api': 'https://api.xinlangapi.com/xinlangapi.php/provide/vod/'},
        '樱花': {'name': '️樱花', 'api': 'https://m3u8.apiyhzy.com/api.php/provide/vod/'},
        '魔都': {'name': '️魔都', 'api': 'https://www.mdzyapi.com/api.php/provide/vod/'},  
        '无水印': {'name': '️无水印', 'api': 'https://api.wsyzy.net/api.php/provide/vod/?ac=list'},
        '海豚': {'name': '️海豚', 'api': 'https://hhzyapi.com/api.php/provide/vod/'},
        '天涯': {'name': '️天涯', 'api': 'https://tyyszyapi.com/api.php/provide/vod/'},
        '星球': {'name': '️星球', 'api': 'https://www.ysxq.cc/api.php/provide/vod/'}
    }

    # 衍生/附加内容关键词（弹幕匹配时对库内标题降权，避免配到花絮/会员版/浓缩版上）
    EXTRA_EP_WORDS = ('直拍', '花絮', '纯享', '竖屏', '观演', '纪录片', '预告', '彩蛋', '舞台纯享',
                      '训练室', '会员版', '加更', '浓缩版', '老友记', '专访', '幕后', '衍生', '精编版', '来了')

    def init(self, extend=""):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        }
        # ===== 弹幕完整配置 =====
        self.DANMAKU_API = "https://dm.999.team/87654321/api/v2"
        self.push_port = 9978
        self._anime_cache = {}
        self._episode_cache = {}
        self._last_req = 0
        self._lock = threading.Lock()
        self.vod_title = None
        self.cleaned_title = None
        self.vod_year = None
        self.vod_total = None
        self.vod_language = None
        self.ep_map = {}
        self.ep_title_map = {}
        self.ep_date_map = {}
        self.ep_realnum_map = {}   # 名称中的真实期号/集号（如"第4期"→4；"20260804下"→None）
        self.ep_infer_num_map = {} # 推断期号（库内整季同一日期时，按"上→中→下"播出结构反推）
        self.ep_part_map = {}      # 推断期号对应的分段（上/中/下，含复合分段如"中上"）

    # ==================== 核心爬虫方法 ====================
    def build_url(self, base, query):
        if '?' in base:
            if base.endswith('?') or base.endswith('&'):
                return base + query
            else:
                return base + '&' + query
        else:
            return base + '?' + query

    def fetch_json(self, url, timeout=10):
        try:
            resp = self.session.get(url, headers=self.headers, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def clean_item(self, item, source_key, source_name, is_detail=False):
        if not is_detail:
            item['vod_id'] = f"{source_key}@@{item['vod_id']}"
        old_remark = item.get('vod_remarks', '')
        item['vod_remarks'] = f"{source_name} | {old_remark}" if old_remark else source_name
        item.pop('vod_down_from', None)
        item.pop('vod_down_url', None)
        return item

    def homeContent(self, filter=False):
        classes = []
        filters = {}
        def fetch_class(source_key, source_info):
            url = self.build_url(source_info['api'], "ac=list")
            data = self.fetch_json(url, timeout=4)
            return source_key, source_info, data
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(fetch_class, k, v): k for k, v in self.SOURCES.items()}
            for future in concurrent.futures.as_completed(futures):
                source_key, source_info, data = future.result()
                classes.append({'type_id': source_key, 'type_name': source_info['name']})
                filter_values = [{'n': '全部(最新)', 'v': ''}]
                if data and 'class' in data:
                    for c in data['class']:
                        filter_values.append({'n': c['type_name'], 'v': c['type_id']})
                filters[source_key] = [{'key': 'cateId', 'name': '分类', 'value': filter_values}]
        return {'class': classes, 'filters': filters, 'list': []}

    def homeVideoContent(self):
        return {'list': []}

    def categoryContent(self, tid, pg=1, filter=False, extend=None):
        if tid not in self.SOURCES:
            return {'list': [], 'page': pg, 'pagecount': 0, 'limit': 20, 'total': 0}
        source = self.SOURCES[tid]
        if extend is None:
            extend = {}
        real_tid = extend.get('cateId', '')
        query = f"ac=detail&pg={pg}"
        if real_tid:
            query += f"&t={real_tid}"
        url = self.build_url(source['api'], query)
        data = self.fetch_json(url, timeout=10)
        if not data:
            return {'list': [], 'page': pg, 'pagecount': 0, 'limit': 20, 'total': 0}
        video_list = []
        for item in data.get('list', []):
            video_list.append(self.clean_item(item, tid, source['name'], is_detail=False))
        return {
            'list': video_list,
            'page': data.get('page', pg),
            'pagecount': data.get('pagecount', 0),
            'limit': data.get('limit', 20),
            'total': data.get('total', 0)
        }

    def detailContent(self, ids):
        if not ids:
            return {'list': []}
        full_id = ids[0]
        if '@@' not in full_id:
            return {'list': []}
        source_key, real_id = full_id.split('@@', 1)
        if source_key not in self.SOURCES:
            return {'list': []}
        source = self.SOURCES[source_key]
        url = self.build_url(source['api'], f"ac=detail&ids={real_id}")
        data = self.fetch_json(url, timeout=10)
        if not data or 'list' not in data:
            return {'list': []}
        result_list = []
        for item in data['list']:
            cleaned = self.clean_item(item, source_key, source['name'], is_detail=True)
            cleaned['vod_id'] = full_id
            result_list.append(cleaned)
        # 构建弹幕匹配上下文（剧集映射、标题、年份、总集数等）
        if result_list:
            self._build_danmaku_context(result_list[0])
        return {'list': result_list}

    def searchContent(self, key, quick=False, pg=1):
        keyword = key.strip()
        if not keyword:
            return {'list': [], 'page': pg, 'pagecount': 0, 'limit': 40, 'total': 0}
        encoded_keyword = quote(keyword)
        def search_source(source_key, source_info):
            test_urls = [
                self.build_url(source_info['api'], f"ac=detail&wd={encoded_keyword}&pg={pg}"),
                self.build_url(source_info['api'], f"ac=list&wd={encoded_keyword}&pg={pg}")
            ]
            for url in test_urls:
                data = self.fetch_json(url, timeout=8)
                if not data:
                    continue
                items = None
                if isinstance(data, dict):
                    if 'list' in data:
                        items = data['list']
                    elif 'data' in data and isinstance(data['data'], dict) and 'list' in data['data']:
                        items = data['data']['list']
                    elif 'data' in data and isinstance(data['data'], list):
                        items = data['data']
                if items:
                    return source_key, source_info, data, items
            return source_key, source_info, None, []
        all_items = []
        max_pagecount = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(search_source, k, v): k for k, v in self.SOURCES.items()}
            for future in concurrent.futures.as_completed(futures):
                source_key, source_info, data, items = future.result()
                if items:
                    for item in items:
                        cleaned = self.clean_item(item, source_key, source_info['name'], is_detail=False)
                        all_items.append(cleaned)
                    if data and data.get('pagecount', 0) > max_pagecount:
                        max_pagecount = data.get('pagecount', 0)
        seen = set()
        unique = []
        for v in all_items:
            if v['vod_id'] not in seen:
                seen.add(v['vod_id'])
                unique.append(v)
        return {
            'list': unique,
            'page': pg,
            'pagecount': max_pagecount if max_pagecount else 1,
            'limit': 40,
            'total': 9999
        }

    def playerContent(self, flag, id, vipFlags=None):
        # ===== 弹幕自动匹配（后台线程，不影响播放） =====
        try:
            self._match_danmaku(id)
        except Exception:
            pass
        return {
            'parse': 0,
            'url': id,
            'header': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            }
        }

    # ==================== 弹幕辅助方法（完整版） ====================

    def _rate_limit(self):
        with self._lock:
            now = time.time()
            if now - self._last_req < 1.0:
                time.sleep(1.0 - (now - self._last_req))
            self._last_req = time.time()

    def _clean_title(self, title):
        if not title:
            return ""
        s = title.strip()
        s = re.sub(r'[（(]?(国语|粤语|普通话|英语|日语|韩语|原声)版?[）)]?', '', s)
        s = re.sub(r'第\s*[0-9零一二三四五六七八九十百千]+\s*[集話话]', '', s)
        s = re.sub(r'[Ee][Pp]\s*\d+', '', s)
        s = re.sub(r'S\d+', '', s)
        s = re.sub(r'\d+[KkPp]', '', s)
        s = re.sub(r'4K', '', s)
        s = re.sub(r'\b(HD|BD|TC|TS|CAM|SCR|蓝光|杜比|BluRay|Dolby)\b', '', s, flags=re.I)
        s = re.sub(r'\[\d+[\.\d]*[MGT]\]', '', s)
        s = re.sub(r'\.(mp4|mkv|avi|rmvb|flv|web|dl|h265|h264|hevc)$', '', s)
        s = re.sub(r'[【\[（(].*?[】\]）)]', '', s)
        s = re.sub(r'[\\/:*"<>|丨]', '', s)
        s = re.sub(r'[:：]', ' ', s)
        s = re.sub(r'\d{4}$', '', s)
        cn = re.findall(r'[\u4e00-\u9fff0-9]+', s)
        return ''.join(cn) if cn else re.sub(r'\s+', ' ', s).strip()

    def _extract_year_from_text(self, text):
        if not text:
            return None
        m = re.search(r'[（(](\d{4})[）)]', text)
        if m:
            return m.group(1)
        m = re.search(r'(?<!\d)(\d{4})(?!\d)', text)
        if m:
            return m.group(1)
        m = re.search(r'\[(\d{4})\]', text)
        return m.group(1) if m else None

    def _extract_date_from_title(self, ep_title):
        if not ep_title:
            return None
        m = re.search(r'(\d{4}-\d{2}-\d{2})', ep_title)
        if m:
            return m.group(1)
        m = re.search(r'(\d{8})', ep_title)
        if m:
            d = m.group(1)
            try:
                y, mo, day = int(d[:4]), int(d[4:6]), int(d[6:8])
                if 1970 <= y <= 2099 and 1 <= mo <= 12 and 1 <= day <= 31:
                    return f"{y}-{mo:02d}-{day:02d}"
            except:
                pass
        m = re.search(r'第\s*(\d{6})\s*期', ep_title)
        if m:
            d = m.group(1)
            try:
                yy, mm, dd = int(d[:2]), d[2:4], d[4:6]
                y = 2000 + yy if 2000 + yy <= 2099 else 1900 + yy
                if 1 <= int(mm) <= 12 and 1 <= int(dd) <= 31:
                    return f"{y}-{mm}-{dd}"
            except:
                pass
        return None

    def _date_in_text(self, date_str, text):
        """日期包含匹配：同时兼容 2025-12-20 与 20251220 两种库内写法"""
        if not date_str or not text:
            return False
        if date_str in text:
            return True
        return date_str.replace('-', '') in text

    def _extract_episode_info(self, ep_title):
        info = {'date': None, 'episode_number': None, 'is_variety': False, 'clean_title': '', 'sub_part': None, 'keywords': []}
        if not ep_title:
            return info
        info['date'] = self._extract_date_from_title(ep_title)
        # 期号提取：跳过 8 位日期型期号（如"第20260803期"），取真实期号；分段信息照常保留
        for m_ in re.finditer(r'第\s*(\d+)\s*期([中上下半])?', ep_title):
            if m_.group(2) and not info['sub_part']:
                info['sub_part'] = m_.group(2)
            if int(m_.group(1)) >= 10000000:
                continue  # 8位日期（第20260803期）不当期号
            info['episode_number'] = int(m_.group(1))
            info['is_variety'] = True
            break
        m = re.search(r'第\s*(\d+)\s*集', ep_title)
        if m and not info['episode_number'] and int(m.group(1)) < 10000000:
            info['episode_number'] = int(m.group(1))
        bm = re.search(r'[（(]([^）)]+)[）)]', ep_title)
        if bm:
            content = bm.group(1).strip()
            if content:
                info['keywords'] = [kw.strip() for kw in re.split(r'[\s|,|，|、|丨]+', content) if kw.strip()]
        clean = ep_title
        clean = re.sub(r'【.*?】', '', clean)
        clean = re.sub(r'^\d{4}-\d{2}-\d{2}', '', clean)
        clean = re.sub(r'^\d{8}', '', clean)
        clean = re.sub(r'[（(][^）)]*[）)]', '', clean)
        clean = re.sub(r'第\s*\d+\s*[期集]', '', clean)
        clean = clean.strip()
        info['clean_title'] = clean
        return info

    def _get_episode_title_from_data(self, ep):
        if isinstance(ep, dict):
            for f in ['episodeTitle', 'title', 'ep_title', 'name']:
                v = ep.get(f)
                if v and str(v).strip():
                    return str(v).strip()
        return ''

    def _extract_language_keywords(self, title):
        if not title:
            return []
        kw = []
        for p in ['普通话', '国语', '粤语', '英语', '日语', '韩语', '川普', '原声', '纯享版']:
            if p in title:
                kw.append(p)
        return kw

    def _get_episode_number_from_url(self, url):
        if not url:
            return None
        for p in [r'/(\d+)\.m3u8', r'/(\d+)\.mp4', r'/ep(\d+)', r'/v_(\d+)/', r'[_-](\d{1,3})\.']:
            m = re.search(p, url)
            if m:
                return int(m.group(1))
        return None

    def _search_anime_list(self, keyword, year=None, total_ep=None, force_refresh=False, language=None):
        core = keyword
        core = re.sub(r'\d{4}$', '', core).strip()
        core = re.sub(r'[：:、，,，.。·\-_\(\)（）【】\s]', '', core)
        dialect_match = None
        if not language:
            dialect_match = re.search(r'(四川话|普通话|粤语|英语|原声|版)', core)
            if dialect_match:
                core = re.sub(r'(四川话|普通话|粤语|英语|原声|版)', '', core).strip()

        ck = f"{core}_{year}_{total_ep}_{language}"
        if not force_refresh and ck in self._anime_cache:
            cached = self._anime_cache[ck]
            return [] if cached == [] else cached

        url = f"{self.DANMAKU_API}/search/anime?keyword={urllib.parse.quote(core)}"
        try:
            self._rate_limit()
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
            if resp.status_code != 200:
                return []
            data = resp.json()
            animes = data.get('animes', [])
            if not animes:
                self._anime_cache[ck] = []
                return []

            src_pri = {'360': 10, 'tencent': 9, 'mgtv': 8, 'iqiyi': 7, 'bilibili': 6, 'youku': 5, 'hanjutv': 4}

            # 语言版本同义词与标记：源站"国语版"应对库内"[普通话版]/[中配版]"；
            # 源无语言标记（原版）时，避开带明确语言版本标记的条目，防止中日/中配错配
            LANG_SYN = {'国语': ('普通话', '中配', '国语'), '普通话': ('普通话', '国语', '中配'),
                        '粤语': ('粤语', '粤配'), '日语': ('日语', '日配'), '英语': ('英语', '英文'),
                        '韩语': ('韩语',), '原声': ('原声', '日语')}
            LANG_MARKS = ('普通话版', '日语版', '英语版', '粤语版', '韩语版', '原声版', '中配版')

            def norm_title(t):
                return re.sub(r'[·・～\-—\s【】\[\]()（）:：、，,。.]', '', t or '')

            def title_hit(tn):
                # 归一化后：核心词位于开头且紧跟年份/括号/结尾，视为精确命中
                return bool(re.match(r'^%s(?=\d|[（(【\[]|$)' % re.escape(core), tn))

            def score(anime):
                s = 0
                t = anime.get('title') or anime.get('animeTitle') or anime.get('name') or ''
                tn = norm_title(t)
                if t == core or title_hit(tn):
                    s += 10000
                elif core in t or core in tn:
                    s += 1000
                else:
                    s -= 2000
                if year:
                    ay = anime.get('year') or self._extract_year_from_text(t)
                    if ay:
                        try:
                            d = abs(int(ay) - int(year))
                            if d == 0:
                                s += 5000
                            elif d == 1:
                                s += 2000
                        except:
                            pass
                ec = anime.get('episodeCount', 0)
                if total_ep and total_ep == 1 and ec == 1:
                    s += 5000
                elif total_ep and total_ep > 0 and ec > 0 and abs(ec - total_ep) <= 3:
                    s += 800
                if language:
                    syns = LANG_SYN.get(language, (language,))
                    if any(x in t for x in syns):
                        s += 15000
                    elif any(mk in t for mk in LANG_MARKS):
                        s -= 10000   # 源标了语言但条目是别的语言版本，重罚
                else:
                    if any(mk in t for mk in LANG_MARKS):
                        s -= 10000   # 源无语言标记（原版），避开语言版本条目
                if dialect_match and dialect_match.group(1) in t:
                    s += 15000
                s += src_pri.get(anime.get('source', ''), 0)
                for pk in ['合集篇', '高光合集', '剧场版', '预告', '花絮', '纯享', '训练室', '直拍', 'OVA']:
                    if pk in t:
                        s -= 3000
                        break
                for bk in ['年番', '正片', '第一季', '第二季']:
                    if bk in t:
                        s += 500
                        break
                if any(w in t for w in ['舞台纯享', '训练室', '直拍', '花絮', '竖屏', '纯享']):
                    s -= 2000
                return s, t

            scored = [(score(a), a) for a in animes]
            scored.sort(key=lambda x: x[0][0] if isinstance(x[0], tuple) else x[0], reverse=True)
            if isinstance(scored[0][0], tuple):
                scored = [(s, a) for (s, _), a in scored]

            if scored and scored[0][0] < 0:
                self._anime_cache[ck] = []
                return []

            ids = []
            exact_ids = []
            for s, a in scored:
                if s < 0:
                    continue
                t = a.get('title') or a.get('animeTitle') or a.get('name') or ''
                tn = norm_title(t)
                base = re.match(r'^[\u4e00-\u9fffA-Za-z0-9]+', t)
                bt = base.group() if base else t
                aid = a.get('animeId')
                if bt == core or title_hit(tn):
                    exact_ids.append(aid)
                elif aid:
                    ids.append(aid)
            final = exact_ids + ids
            self._anime_cache[ck] = final
            return final
        except:
            return []

    def _fetch_bangumi_episodes(self, anime_id):
        """拉取 bangumi 详情的 episodes；库更新期间 detail 接口会间歇 404，
        重试若干次提升成功率（后台匹配线程执行，稍慢可接受）"""
        for attempt in range(3):
            try:
                self._rate_limit()
                resp = requests.get(f"{self.DANMAKU_API}/bangumi/{anime_id}",
                                    headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                if resp.status_code == 200:
                    return resp.json().get('bangumi', {}).get('episodes', [])
                if resp.status_code == 404 and attempt < 2:
                    time.sleep(2)
                    continue
                return None
            except:
                if attempt < 2:
                    time.sleep(2)
                    continue
                return None
        return None

    def _get_episode_id_by_title(self, anime_id, ep_title):
        if not ep_title:
            return None
        info = self._extract_episode_info(ep_title)
        date_str = info['date']
        ep_num = info['episode_number']
        sub_part = info.get('sub_part')
        keywords = info.get('keywords', [])
        clean_ep = ep_title.strip()
        low_quality = list(self.EXTRA_EP_WORDS)
        sub_markers = ['中', '上', '下', '半', '前篇', '后篇', '前', '后']

        try:
            episodes = self._fetch_bangumi_episodes(anime_id)
            if not episodes:
                return None

            # 精确匹配
            for ep in episodes:
                if self._get_episode_title_from_data(ep) == clean_ep:
                    return ep.get('episodeId')

            # 特殊版本匹配
            for kw in ['加更版', '纯享版', '精编版', '花絮', '预告']:
                if kw in clean_ep:
                    for ep in episodes:
                        api_t = self._get_episode_title_from_data(ep)
                        if kw in api_t:
                            if date_str and self._date_in_text(date_str, api_t):
                                return ep.get('episodeId')
                            return ep.get('episodeId')
                    break

            # 子集+日期+关键词
            if sub_part and date_str:
                if keywords:
                    for ep in episodes:
                        api_t = self._get_episode_title_from_data(ep)
                        if self._date_in_text(date_str, api_t) and sub_part in api_t and any(k in api_t for k in keywords):
                            return ep.get('episodeId')
                for ep in episodes:
                    api_t = self._get_episode_title_from_data(ep)
                    if self._date_in_text(date_str, api_t) and sub_part in api_t:
                        return ep.get('episodeId')

            # 日期+关键词
            if date_str and keywords:
                for ep in episodes:
                    api_t = self._get_episode_title_from_data(ep)
                    if self._date_in_text(date_str, api_t) and any(k in api_t for k in keywords):
                        return ep.get('episodeId')

            # 期数匹配
            candidates = []
            if ep_num:
                for ep in episodes:
                    api_t = self._get_episode_title_from_data(ep)
                    if not api_t:
                        continue
                    if re.search(r'第\s*0*%d\s*期' % ep_num, api_t):
                        sc = 0
                        if date_str and self._date_in_text(date_str, api_t):
                            sc += 20
                        if keywords and any(k in api_t for k in keywords):
                            sc += 15
                        if sub_part and sub_part in api_t:
                            sc += 10
                        if not any(m in api_t for m in sub_markers):
                            sc += 10
                        if not any(w in api_t for w in low_quality):
                            sc += 5
                        candidates.append((sc, ep.get('episodeId')))
                if candidates:
                    return max(candidates, key=lambda x: x[0])[1]

            # 日期匹配
            if date_str:
                best = None
                lib_dates = set()
                for ep in episodes:
                    api_t = self._get_episode_title_from_data(ep)
                    for dm_ in re.finditer(r'(\d{4}-\d{1,2}-\d{1,2})|(?<!\d)(\d{8})(?!\d)', api_t):
                        dv = (dm_.group(1) or dm_.group(2)).replace('-', '')
                        if len(dv) == 8:
                            lib_dates.add(dv)
                    if self._date_in_text(date_str, api_t):
                        if keywords and any(k in api_t for k in keywords):
                            return ep.get('episodeId')
                        if not best:
                            best = ep
                # 库内日期有区分度时才可由日期唯一确定；无区分度（整季同一日期）时不猜，
                # 交由调用方的期号/分段匹配裁决
                if best and len(lib_dates) > 1:
                    return best.get('episodeId')

            # 纯期数
            if ep_num:
                for ep in episodes:
                    api_t = self._get_episode_title_from_data(ep)
                    if re.search(r'第\s*0*%d\s*期' % ep_num, api_t):
                        return ep.get('episodeId')

            # 衍生特辑名称回退（如"20261005心动的旅行上" → 库内"心动的旅行上"）
            core_name = re.sub(r'^[\d\-年月日\.]+', '', clean_ep).strip()
            core_name = re.sub(r'^第\s*\d+\s*[期集話话]?\s*', '', core_name).strip()
            if len(core_name) >= 4 and not re.fullmatch(r'[上中下纯享加更陪看先导花絮彩蛋特辑预告正片全集]+', core_name):
                for ep in episodes:
                    api_t = self._get_episode_title_from_data(ep)
                    if not api_t:
                        continue
                    api_core = re.sub(r'^【[^】]*】\s*', '', api_t)
                    api_core = re.sub(r'\s*\d{4}-\d{1,2}-\d{1,2}期?\s*', ' ', api_core).strip()
                    api_core = re.sub(r'^第\s*\d+\s*[期集話话]\s*[上中下]?\s*[:：]?\s*', '', api_core).strip()
                    if len(api_core) >= 4 and (core_name in api_core or api_core in core_name):
                        return ep.get('episodeId')
        except:
            pass
        return None

    def _get_episode_id_by_index(self, anime_ids, episode_index, current_ep_title=None, lang_keywords=None, date_str=None, infer_num=None, part_hint=None):
        if not lang_keywords:
            lang_keywords = self._extract_language_keywords(current_ep_title or '')
        if not date_str and current_ep_title:
            date_str = self._extract_date_from_title(current_ep_title)

        for aid in anime_ids:
            ck = f"{aid}_{episode_index}_{current_ep_title}_{str(lang_keywords)}_{infer_num}_{part_hint}"
            if ck in self._episode_cache:
                return self._episode_cache[ck]

            try:
                episodes = self._fetch_bangumi_episodes(aid)
                if not episodes:
                    continue

                # 单集：语言关键词匹配
                if self.vod_total == 1:
                    dialect_kw = []
                    if current_ep_title:
                        for dk in ['四川话', '普通话', '粤语', '英语', '原声']:
                            if dk in current_ep_title:
                                dialect_kw.append(dk)
                    if not dialect_kw and self.vod_title:
                        for dk in ['四川话', '普通话', '粤语', '英语', '原声']:
                            if dk in self.vod_title:
                                dialect_kw.append(dk)
                    if dialect_kw:
                        for ep in episodes:
                            api_t = self._get_episode_title_from_data(ep)
                            if any(dk in api_t for dk in dialect_kw):
                                if date_str and not self._date_in_text(date_str, api_t):
                                    continue  # 方言候选也要过日期关
                                eid = ep.get('episodeId')
                                self._episode_cache[ck] = eid
                                return eid
                    if date_str:
                        # 源侧带日期（如综艺"第20240524期"）：只接受带该日期的候选，
                        # 库内没有本期日期时换下一个源，避免配错
                        for ep in episodes:
                            api_t = self._get_episode_title_from_data(ep)
                            if self._date_in_text(date_str, api_t):
                                eid = ep.get('episodeId')
                                self._episode_cache[ck] = eid
                                return eid
                        continue
                    eid = episodes[0].get('episodeId')
                    self._episode_cache[ck] = eid
                    return eid

                # 日期匹配（兼容 2025-12-20 与 20251220 两种库内格式）
                # 先统计库内日期的区分度：整季只标一个日期（如综艺统一标开播日）时无区分度
                lib_has_date = False
                all_dates = set()
                if date_str:
                    for ep in episodes:
                        api_t = self._get_episode_title_from_data(ep)
                        if re.search(r'\d{4}-\d{1,2}-\d{1,2}|(?<!\d)\d{8}(?!\d)', api_t):
                            lib_has_date = True
                        for dm_ in re.finditer(r'(\d{4}-\d{1,2}-\d{1,2})|(?<!\d)(\d{8})(?!\d)', api_t):
                            dv = (dm_.group(1) or dm_.group(2)).replace('-', '')
                            if len(dv) == 8:
                                all_dates.add(dv)
                # 库内日期有区分度（多个不同日期）时，本期日期不在其中才拒绝猜测
                strict_date = bool(date_str) and lib_has_date and len(all_dates) > 1
                date_first = None
                if date_str:
                    for ep in episodes:
                        api_t = self._get_episode_title_from_data(ep)
                        if self._date_in_text(date_str, api_t):
                            if strict_date:
                                # 库内日期有区分度：该日期唯一确定一集，直接返回
                                eid = ep.get('episodeId')
                                self._episode_cache[ck] = eid
                                return eid
                            if date_first is None:
                                date_first = ep
                            # 库内日期无区分度（整季同一日期）时交由下方期号/分段匹配裁决
                    if strict_date:
                        # 库内按日期组织且有区分度，但没有本期日期：不猜测，换下一个源
                        continue

                # 有效期号：名称真实期号 > 有日期时的推断期号 > 位置计数
                num_idx = None
                if infer_num and infer_num > 0 and date_str:
                    num_idx = infer_num
                elif episode_index and episode_index > 0:
                    num_idx = episode_index

                # 语言关键词 + 集数匹配
                if lang_keywords:
                    matched = None
                    for ep in episodes:
                        api_t = self._get_episode_title_from_data(ep)
                        has_num = re.search(r'(?<!\d)%d(?!\d)' % (num_idx or episode_index), api_t) or \
                                  re.search(r'第\s*%d\s*[集話期]' % (num_idx or episode_index), api_t)
                        if has_num:
                            for lk in lang_keywords:
                                if lk in api_t:
                                    matched = ep
                                    break
                            if matched:
                                break
                    if matched:
                        eid = matched.get('episodeId')
                        self._episode_cache[ck] = eid
                        return eid

                # 期号/集号匹配（优先于位置索引：库内列表常混入衍生/花絮/会员版，裸下标不可靠）
                if num_idx and num_idx > 0:
                    best_ep = None
                    best_sc = -999
                    for ep in episodes:
                        api_t = self._get_episode_title_from_data(ep)
                        if not api_t:
                            continue
                        # 库内日期有区分度时只接受带正确日期的候选；无区分度（整季同一日期）时不强求
                        if strict_date and not self._date_in_text(date_str, api_t):
                            continue
                        if re.search(r'第\s*0*%d\s*期' % num_idx, api_t):
                            sc = 30
                        elif re.search(r'第\s*0*%d\s*[集话話]' % num_idx, api_t):
                            sc = 20
                        elif re.search(r'(?<!\d)0*%d(?!\d)' % num_idx, api_t):
                            sc = 8
                        else:
                            continue
                        if date_str and self._date_in_text(date_str, api_t):
                            sc += 30
                        # 分段一致性（上/中/下）：库内日期无区分度时按播出结构反推期号，用于区分同期不同段
                        if part_hint:
                            m3 = re.search(r'第\s*0*%d\s*期\s*([上中下])' % num_idx, api_t)
                            if m3:
                                if m3.group(1) in part_hint:
                                    sc += 20
                                    # 复合分段（中上/中下）：库内"第N期中（上/下）"写法，检查后半段
                                    if len(part_hint) > 1 and part_hint[-1] in api_t[m3.end():m3.end() + 6]:
                                        sc += 10
                                else:
                                    sc -= 15
                        if any(w in api_t for w in self.EXTRA_EP_WORDS):
                            sc -= 25
                        # 裸编号条目（去掉来源前缀/编号/日期后无任何副标题，如"【hongguo】 第1集"）
                        # 可信度低：可能是另一部作品的简版条目。仅源侧带日期（综艺日期型选集）
                        # 时才降权——电视剧/动漫选集名不带日期，其库内"第N集"裸标题是正常正主，
                        # 降权会把精确命中退化成下标猜测
                        if date_str:
                            bare = re.sub(r'^【[^】]*】\s*', '', api_t)
                            bare = re.sub(r'第\s*0*%d\s*[期集话話]\s*[上中下]?' % num_idx, '', bare)
                            bare = re.sub(r'\d{4}-\d{1,2}-\d{1,2}期?', '', bare).strip(' ：:，,。.~～!！?？')
                            if len(bare) < 2:
                                sc -= 40
                        if lang_keywords and any(lk in api_t for lk in lang_keywords):
                            sc += 15
                        if sc > best_sc:
                            best_sc = sc
                            best_ep = ep
                    if best_ep is not None and best_sc > 0:
                        eid = best_ep.get('episodeId')
                        self._episode_cache[ck] = eid
                        return eid

                # 库内日期无区分度时的回退：期号/分段未命中，用第一个带本期日期的候选
                if date_first is not None:
                    eid = date_first.get('episodeId')
                    self._episode_cache[ck] = eid
                    return eid

                # 索引精确匹配
                if not date_str and 1 <= episode_index <= len(episodes):
                    target = episodes[episode_index - 1]
                    if lang_keywords:
                        matched = None
                        for offset in range(-2, 3):
                            idx = episode_index + offset - 1
                            if 0 <= idx < len(episodes):
                                api_t = self._get_episode_title_from_data(episodes[idx])
                                if any(lk in api_t for lk in lang_keywords):
                                    matched = episodes[idx]
                                    break
                        if matched:
                            eid = matched.get('episodeId')
                            self._episode_cache[ck] = eid
                            return eid
                        eid = target.get('episodeId')
                        self._episode_cache[ck] = eid
                        return eid
                    eid = target.get('episodeId')
                    self._episode_cache[ck] = eid
                    return eid

                # 数字匹配回退
                if episode_index and not date_str:
                    for ep in episodes:
                        api_t = self._get_episode_title_from_data(ep)
                        nm = re.search(r'(\d+)', api_t)
                        if nm and int(nm.group(1)) == episode_index:
                            if lang_keywords:
                                if any(lk in api_t for lk in lang_keywords):
                                    eid = ep.get('episodeId')
                                    self._episode_cache[ck] = eid
                                    return eid
                            eid = ep.get('episodeId')
                            self._episode_cache[ck] = eid
                            return eid
            except:
                pass
        return None

    def _fetch_danmaku(self, anime_id=None, episode_num=None, episode_id=None, retry=3):
        if episode_id:
            url = f"{self.DANMAKU_API}/comment/{episode_id}?format=xml"
        elif anime_id and episode_num:
            url = f"{self.DANMAKU_API}/comment?animeId={anime_id}&episode={episode_num}&format=xml"
        else:
            return None

        for attempt in range(retry):
            try:
                self._rate_limit()
                # 流式读取：只需验证弹幕存在（头部内容含<d标签），不必下载整个 XML
                # （大热综艺/电影弹幕可达 19MB，全量下载 30s+，而播放器会自行拉取，
                # 此处只回传 URL；读到第一个含<d的块即止。超时放宽到 20s：
                # 库数据迁移期间首字节可能 >15s）
                with requests.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': self.DANMAKU_API + '/',
                    'Accept': 'application/xml, text/xml, */*',
                }, timeout=20, stream=True) as resp:
                    if resp.status_code == 200:
                        head = b''
                        for chunk in resp.iter_content(chunk_size=8192):
                            head += chunk
                            if len(head) >= 16384 or b'<d' in head:
                                break
                        if b'<d' in head or b'<i>' in head:
                            return url
                    elif resp.status_code == 429:
                        time.sleep(5)
            except:
                if attempt < retry - 1:
                    time.sleep(2)
        return None

    def _push_danmaku(self, danmaku_url):
        if not danmaku_url:
            return
        try:
            requests.get(f"http://127.0.0.1:{self.push_port}/action?do=refresh&type=danmaku&path={urllib.parse.quote(danmaku_url)}", timeout=2)
        except:
            pass

    # ==================== 弹幕上下文构建与匹配（聚合源适配） ====================

    def _build_danmaku_context(self, item):
        """从 MacCMS 详情数据解析剧集信息，构建弹幕匹配上下文"""
        try:
            self.ep_map = {}
            self.ep_title_map = {}
            self.ep_date_map = {}
            self.ep_realnum_map = {}
            self.ep_infer_num_map = {}
            self.ep_part_map = {}

            # 派生/附加内容词：不属于正片期号序列（库内通常无对应条目或另有专门条目）
            DERIV_WORDS = ('先导', '纯享', '加更', '陪看', '彩蛋', '花絮', '特辑', '预告',
                           '复盘', '探班', '会员', '尊享', '加长', '未播', '直播回放',
                           '心动的旅行', '心动的周末', '全记录', '发布会', '导演版')
            # 有专门库内条目的衍生特辑：不继承正片期号（留给标题匹配）
            NO_INHERIT = ('心动的旅行', '心动的周末', '直播回放')

            def is_deriv(en):
                return any(w in en for w in DERIV_WORDS)

            def part_of(en):
                """分段判定：中上/中下（复合分段）优先，其次 中/上/下；无 → ''"""
                if '中上' in en:
                    return '中上'
                if '中下' in en:
                    return '中下'
                if '中' in en:
                    return '中'
                if '上' in en:
                    return '上'
                if '下' in en:
                    return '下'
                return ''

            CN_DIGIT = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
                        '六': 6, '七': 7, '八': 8, '九': 9}

            def cn_to_int(s):
                if not s:
                    return None
                if s == '十':
                    return 10
                m = re.match(r'^([一二三四五六七八九])?十([一二三四五六七八九])?$', s)
                if m:
                    tens = CN_DIGIT.get(m.group(1), 1) if m.group(1) else 1
                    ones = CN_DIGIT.get(m.group(2), 0) if m.group(2) else 0
                    return tens * 10 + ones
                return CN_DIGIT.get(s)

            def extract_ep_num(en):
                s = (en or '').strip()
                if not s:
                    return None
                if re.match(r'^\d{8}$', s):
                    return None  # 纯日期命名
                if s.upper() in ('HD', 'BD', '4K', '1080P', '720P', 'TC', 'TS', 'CAM', 'SCR', 'BLURAY', 'DOLBY'):
                    return 1
                m = re.search(r'[Ss]\d+[Ee](\d+)', s)  # S01E05
                if m:
                    return int(m.group(1))
                for m in re.finditer(r'第\s*(\d+)\s*[集期话話]', s):  # 跳过 8 位日期期号（第20260803期）
                    n = int(m.group(1))
                    if n < 10000000:
                        return n
                m = re.search(r'第\s*([一二三四五六七八九十]+)\s*[集期话話]', s)  # 第十二期
                if m:
                    n = cn_to_int(m.group(1))
                    if n:
                        return n
                if re.search(r'(1080|4K|720|HD|SD|高清|蓝光|超清|TC|TS|CAM|SCR|杜比)', s, re.I):
                    return None
                if self._extract_date_from_title(s):
                    return None  # 日期型命名不作为集号
                m = re.search(r'(?<!\d)(\d{1,3})(?!\d)', s)  # CJK 安全的独立数字
                if m:
                    n = int(m.group(1))
                    return None if 1000 <= n <= 2099 else n
                return None

            play_urls = str(item.get('vod_play_url', '') or '').split('$$$')
            first_count = 0
            line_seqs = []
            for idx, purl in enumerate(play_urls):
                if not purl:
                    continue
                ep_counter = 0
                lc = 0
                line_seq = []
                for ep in purl.split('#'):
                    if '$' not in ep:
                        continue
                    en, el = ep.split('$', 1)
                    en = en.strip()
                    el = el.strip()
                    if not en or not el:
                        continue
                    ep_counter += 1
                    lc += 1
                    key = el
                    key2 = el.split('?')[0].rstrip('/')
                    real_n = extract_ep_num(en)
                    ep_date = self._extract_date_from_title(en)
                    ep_n = real_n if real_n is not None else ep_counter
                    self.ep_map[key] = ep_n
                    self.ep_map[key2] = ep_n
                    self.ep_title_map[key] = en
                    self.ep_title_map[key2] = en
                    if ep_date:
                        self.ep_date_map[key] = ep_date
                        self.ep_date_map[key2] = ep_date
                    if real_n is not None:
                        self.ep_realnum_map[key] = real_n
                        self.ep_realnum_map[key2] = real_n
                    # [key, key2, 名称, 日期, 真实期号, 位置, 是否派生, 分段, 推断期号, 推断分段]
                    line_seq.append([key, key2, en, ep_date, real_n, ep_counter,
                                     is_deriv(en), part_of(en), None, None])
                if idx == 0:
                    first_count = lc
                line_seqs.append(line_seq)

            # 期号推断：库内常把整季标成同一日期（开播日），此时按"上→中→下"播出结构反推期号
            for line_seq in line_seqs:
                counter = 0
                last_part = None
                clean_by_date = {}
                for it in line_seq:
                    if it[6]:
                        continue  # 派生集不参与期号累加
                    part = it[7]
                    if part == '上':
                        counter += 1          # 新的"上"开启新的一期
                    elif part == '':
                        if last_part in ('', '下', None):
                            counter += 1      # 无分段且上一期已完结 → 新的一期
                    # 中/下/中上/中下 继承当前期号
                    if counter > 0:
                        it[8] = counter
                        it[9] = part
                        if it[3] and it[3] not in clean_by_date:
                            clean_by_date[it[3]] = (counter, part)
                    last_part = part
                # 派生集按日期继承同日期干净正集的（期号, 分段）；自带分段词优先
                for it in line_seq:
                    if it[6] and it[3] and it[3] in clean_by_date and not any(w in it[2] for w in NO_INHERIT):
                        num, cpart = clean_by_date[it[3]]
                        it[8] = num
                        it[9] = it[7] or cpart
                for it in line_seq:
                    if it[8]:
                        self.ep_infer_num_map[it[0]] = it[8]
                        self.ep_infer_num_map[it[1]] = it[8]
                        if it[9]:
                            self.ep_part_map[it[0]] = it[9]
                            self.ep_part_map[it[1]] = it[9]

            self.vod_title = item.get('vod_name', '') or ''
            self.cleaned_title = self._clean_title(self.vod_title)
            self.vod_year = str(item.get('vod_year', '') or '')
            self.vod_total = first_count if first_count > 0 else None
            self.vod_language = None
            if self.vod_title:
                lks = self._extract_language_keywords(self.vod_title)
                if lks:
                    self.vod_language = lks[0]
        except Exception:
            pass

    def _match_danmaku(self, play_url):
        """播放时后台自动匹配弹幕并推送（不影响播放返回）"""
        if not play_url:
            return
        url = play_url
        base = url.split('?')[0].rstrip('/')
        ep_num = self.ep_map.get(url) or self.ep_map.get(base)
        if not ep_num:
            ep_num = self._get_episode_number_from_url(url)
        if self.vod_total == 1:
            ep_num = 1
        date_str = self.ep_date_map.get(url) or self.ep_date_map.get(base)
        real_num = self.ep_realnum_map.get(url) or self.ep_realnum_map.get(base)
        infer_num = self.ep_infer_num_map.get(url) or self.ep_infer_num_map.get(base)
        part_hint = self.ep_part_map.get(url) or self.ep_part_map.get(base)

        cur_ep_title = self.ep_title_map.get(url) or self.ep_title_map.get(base)
        if cur_ep_title:
            fmt_kw = ['HD', 'BD', '4K', '1080P', '720P', 'DVD', 'HDRIP', 'WEBRIP', 'TC', 'TS', 'CAM', 'SCR', '蓝光', '杜比', 'BluRay', 'Dolby']
            if any(k in cur_ep_title.upper() for k in fmt_kw) and len(cur_ep_title) < 20:
                cur_ep_title = None
            elif cur_ep_title.upper() in fmt_kw:
                cur_ep_title = None
        if self.vod_total == 1 and cur_ep_title:
            if re.match(r'^第\s*\d+\s*[集話话]', cur_ep_title) or re.match(r'^\d+$', cur_ep_title.strip()):
                cur_ep_title = None

        if not self.vod_title or (ep_num is None and not date_str):
            return

        # 派生/附加集（先导/花絮/加更/陪看等）且无法推断期号：库内通常无对应条目，
        # 不匹配可避免把正片弹幕配到衍生集上
        DERIV_SKIP = ('先导', '陪看', '花絮', '特辑', '彩蛋', '加更', '探班', '复盘',
                      '直播回放', '发布会', '全记录', '尊享', '加长', '未播', '导演版')
        if cur_ep_title and any(w in cur_ep_title for w in DERIV_SKIP) and not infer_num:
            return

        def dm():
            try:
                lks = self._extract_language_keywords(self.vod_title)
                sn = self.cleaned_title or self.vod_title
                sn = re.sub(r'(电影版|电影|电视剧|系列|完整版|高清版)$', '', sn)
                sn = re.sub(r'\d{4}$', '', sn).strip()
                aids = self._search_anime_list(sn, year=self.vod_year, total_ep=self.vod_total, language=self.vod_language)
                if not aids and self.vod_title:
                    alt = re.sub(r'(电影版|电视剧|系列|完整版|高清版)$', '', self.vod_title)
                    alt = re.sub(r'\d{4}$', '', alt).strip()
                    aids = self._search_anime_list(alt, year=self.vod_year, total_ep=self.vod_total, force_refresh=True, language=self.vod_language)
                if not aids:
                    return
                eid = None
                if cur_ep_title:
                    is_generic = (not date_str) and (
                                 re.match(r'^第\s*\d+\s*[集話话]?$', cur_ep_title) or \
                                 re.match(r'^EP\s*\d+$', cur_ep_title, re.I) or \
                                 re.match(r'^\d+$', cur_ep_title.strip()))
                    if not is_generic:
                        for aid in aids:
                            eid = self._get_episode_id_by_title(aid, cur_ep_title)
                            if eid:
                                break
                if not eid and (ep_num is not None or date_str):
                    for aid in aids:
                        eid = self._get_episode_id_by_index([aid], ep_num or 0, cur_ep_title, lks,
                                                            date_str=date_str, infer_num=infer_num,
                                                            part_hint=part_hint)
                        if eid:
                            break
                if not eid and (real_num == 1 or self.vod_total == 1) and aids:
                    du = self._fetch_danmaku(aids[0], 1)
                    if du:
                        self._push_danmaku(du)
                        return
                    # 弹幕拉取失败（库迁移中 eid 失效等）：清掉匹配缓存，
                    # 下次重试走全流程重新搜索，拿到新 eid 自愈
                    self._episode_cache.clear()
                if eid:
                    du = self._fetch_danmaku(episode_id=eid)
                    if du:
                        self._push_danmaku(du)
                    else:
                        self._episode_cache.clear()
            except:
                pass
        threading.Thread(target=dm, daemon=True).start()

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass
