import sys
import json
import time
import os
import re
import hmac
import hashlib
import base64
import urllib.parse
import urllib.request

sys.path.append('..')
from base.spider import Spider as BaseSpider


class Spider(BaseSpider):
    def init(self, extend=''):
        try:
            cfg = json.loads(extend) if isinstance(extend, str) and extend else extend or {}
        except Exception:
            cfg = {}
        if not isinstance(cfg, dict):
            cfg = {}
        self.db_host = 'https://frodo.douban.com/api/v2'
        self.db_key = '0ac44ae016490db2204ce0a042db2916'
        self.site_url = 'https://souju.ai'
        self.api_secret = 'f39d73aa7a6426203cdee1ef17b31d3b7ea8c23f4c59c62a3a8aa0f39ee5e79d'
        self.ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        self.db_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat', 'Referer': 'https://servicewechat.com/wx2f9b06c1de1ccfca/84/page-frame.html', 'Accept': 'application/json'}
        self.headers = {'User-Agent': self.ua, 'Referer': self.site_url + '/', 'Origin': self.site_url, 'Accept': 'application/json'}
        if cfg.get('cookie'):
            self.headers['Cookie'] = str(cfg['cookie'])
        self.prefer = cfg.get('prefer', 'direct')
        self.debug = cfg.get('debug') in (True, 1, 'true', '1')
        self.playback_referer = cfg.get('playback_referer')
        self.count = 24
        self._cache = {}
        self.last_error = ''
        self.categories = [('hot_gaia', '热门电影'), ('tv_hot', '热播剧集'), ('show_hot', '热播综艺'), ('movie', '电影筛选'), ('tv', '电视筛选'), ('rank_list_movie', '电影榜单'), ('rank_list_tv', '剧综榜单')]
        self.filters = self._filters()

    def getName(self):
        return '豆播AI'

    def _log(self, s):
        if self.debug:
            print('[豆播AI] ' + str(s))

    @staticmethod
    def _choice(key, name, pairs):
        return {'key': key, 'name': name, 'value': [{'n': n, 'v': v} for n, v in pairs]}

    def _filters(self):
        f = self._choice
        common = [f('genre', '类型', [('全部', '')] + [(g, g) for g in ['剧情', '喜剧', '爱情', '动作', '科幻', '动画', '悬疑', '犯罪', '恐怖', '古装', '战争', '纪录片']]), f('area', '地区', [('全部', '')] + [(a, a) for a in ['中国大陆', '中国香港', '中国台湾', '美国', '日本', '韩国', '英国', '法国', '印度', '泰国']]), f('year', '年代', [('全部', '')] + [(str(y), str(y)) for y in range(time.localtime().tm_year + 1, 2015, -1)] + [(y, y) for y in ['2010年代', '2000年代', '90年代']]), f('sort', '排序', [('综合', 'T'), ('热度', 'U'), ('最新', 'R'), ('评分', 'S')])]
        return {'hot_gaia': [f('area', '地区', [(x, x) for x in ['全部', '华语', '欧美', '韩国', '日本']]), f('sort', '排序', [('热度', 'recommend'), ('最新', 'time'), ('评分', 'rank')])], 'tv_hot': [f('type', '分类', [('综合', 'tv_hot'), ('国产剧', 'tv_domestic'), ('欧美剧', 'tv_american'), ('日剧', 'tv_japanese'), ('韩剧', 'tv_korean'), ('动画', 'tv_animation')])], 'show_hot': [f('type', '分类', [('综合', 'show_hot'), ('国内', 'show_domestic'), ('国外', 'show_foreign')])], 'movie': common, 'tv': [f('subtype', '形式', [('全部', ''), ('电视剧', '电视剧'), ('综艺', '综艺')])] + common, 'rank_list_movie': [f('rank', '榜单', [('实时热门', 'movie_real_time_hotest'), ('一周口碑', 'movie_weekly_best'), ('Top250', 'movie_top250')])], 'rank_list_tv': [f('rank', '榜单', [('实时热门', 'tv_real_time_hotest'), ('华语剧集', 'tv_chinese_best_weekly'), ('全球剧集', 'tv_global_best_weekly'), ('国内综艺', 'show_chinese_best_weekly'), ('国外综艺', 'show_global_best_weekly')])]}

    def _request(self, url, headers, payload=None):
        try:
            if payload is None:
                r = self.fetch(url, headers=headers, timeout=20)
            else:
                body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
                post = getattr(self, 'post', None)
                if callable(post):
                    r = post(url, headers=headers, data=body, timeout=25)
                else:
                    req = urllib.request.Request(url, data=body, headers=headers, method='POST')
                    with urllib.request.urlopen(req, timeout=25) as r:
                        return json.loads(r.read().decode('utf-8-sig'))
            status = getattr(r, 'status_code', 200)
            if not 200 <= status < 300:
                raise ValueError('HTTP ' + str(status))
            text = r.text
            if isinstance(text, bytes):
                text = text.decode('utf-8-sig')
            obj = json.loads(text.lstrip('\ufeff'))
            return obj if isinstance(obj, dict) else {}
        except Exception as e:
            self.last_error = urllib.parse.urlsplit(url).path[:70] + ': ' + str(e)[:100]
            self._log(self.last_error)
            return {}

    def _db(self, path, params=None):
        q = dict(params or {})
        q['apiKey'] = self.db_key
        return self._request(self.db_host + path + '?' + urllib.parse.urlencode(q), self.db_headers)

    def _sign_headers(self, method, path):
        ts, nonce = str(int(time.time() * 1000)), os.urandom(16).hex()
        h = dict(self.headers)
        sig = hmac.new(self.api_secret.encode(), '\n'.join([method, path, ts, nonce]).encode(), hashlib.sha256).hexdigest()
        h.update({'x-ai-movie-timestamp': ts, 'x-ai-movie-nonce': nonce, 'x-ai-movie-signature': sig})
        return h

    def _sj(self, path, payload=None):
        h = self._sign_headers('POST' if payload is not None else 'GET', path)
        if payload is not None:
            h['Content-Type'] = 'application/json'
        return self._request(self.site_url + path, h, payload)

    def _memo(self, key, fn):
        c = self._cache.get(key)
        if c and time.time() - c[0] < 300:
            return c[1]
        obj = fn()
        if obj:
            if len(self._cache) >= 200:
                self._cache.clear()
            self._cache[key] = (time.time(), obj)
        return obj

    @staticmethod
    def _pack(prefix, obj):
        return prefix + base64.urlsafe_b64encode(json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode()).decode().rstrip('=')

    @staticmethod
    def _unpack(value, prefix):
        data = value[len(prefix):]
        return json.loads(base64.urlsafe_b64decode(data + '=' * (-len(data) % 4)).decode())

    @staticmethod
    def _join(arr):
        if isinstance(arr, str):
            return arr
        return ' / '.join(str(x.get('name', '') if isinstance(x, dict) else x) for x in arr or [])

    @staticmethod
    def _clean(s):
        return re.sub(r'[#$\r\n]', ' ', str(s or '')).strip()

    def _pic(self, obj):
        p = obj.get('pic') or {}
        u = p.get('large') or p.get('normal') or obj.get('cover_url') or ''
        return u + '@Referer=https://www.douban.com/@User-Agent=' + urllib.parse.quote(self.ua, safe='') if u else ''

    def _db_card(self, raw):
        o = raw.get('target') or raw
        kind = o.get('type') or raw.get('target_type') or ''
        m = re.search(r'douban.com/(movie|tv)/', o.get('uri') or '')
        if m:
            kind = m.group(1)
        if kind not in ('movie', 'tv') or not o.get('id'):
            return None
        return {'vod_id': self._pack('db:', {'id': str(o['id']), 'kind': kind, 'title': o.get('title') or '', 'year': str(o.get('year') or '')}), 'vod_name': o.get('title') or '', 'vod_pic': self._pic(o), 'vod_remarks': str((o.get('rating') or {}).get('value') or '暂无评分'), 'vod_year': str(o.get('year') or '')}

    def _db_list(self, data):
        return [c for c in (self._db_card(x) for x in data.get('items') or data.get('subject_collection_items') or []) if c]

    def _paged(self, data, page):
        videos = self._db_list(data)
        total = int(data.get('total') or ((page - 1) * self.count + len(videos)))
        return {'list': videos, 'page': page, 'pagecount': max(1, (total + self.count - 1) // self.count), 'limit': self.count, 'total': total}

    def homeContent(self, filter):
        r = {'class': [{'type_id': k, 'type_name': v} for k, v in self.categories]}
        if filter:
            r['filters'] = self.filters
        r.update(self.homeVideoContent())
        return r

    def homeVideoContent(self):
        data = self._db('/subject_collection/subject_real_time_hotest/items', {'start': 0, 'count': self.count})
        videos = self._db_list(data)
        if not videos:
            videos = self._db_list(self._db('/movie/hot_gaia', {'area': '全部', 'sort': 'recommend', 'start': 0, 'count': self.count}))
        return {'list': videos}

    def categoryContent(self, tid, pg, filter, extend):
        page = max(1, int(pg or 1))
        e = extend if isinstance(extend, dict) else {}
        p = {'start': (page - 1) * self.count, 'count': self.count}
        if tid == 'hot_gaia':
            p.update({'area': e.get('area') or '全部', 'sort': e.get('sort') or 'recommend'})
            path = '/movie/hot_gaia'
        elif tid in ('movie', 'tv'):
            selected = {'类型': e.get('genre') or '', '地区': e.get('area') or ''}
            if tid == 'tv':
                selected = {'类型': e.get('subtype') or '', '形式': e.get('genre') or '', '地区': e.get('area') or ''}
            p.update({'sort': e.get('sort') or 'T', 'refresh': 0, 'tags': ','.join(e[k] for k in ('subtype', 'genre', 'area', 'year') if e.get(k)), 'selected_categories': json.dumps(selected, ensure_ascii=False)})
            path = '/' + tid + '/recommend'
        else:
            defaults = {'tv_hot': 'tv_hot', 'show_hot': 'show_hot', 'rank_list_movie': 'movie_real_time_hotest', 'rank_list_tv': 'tv_real_time_hotest'}
            c = e.get('type') or e.get('rank') or e.get('榜单') or defaults.get(tid)
            if not c:
                return self._paged({}, page)
            path = '/subject_collection/' + urllib.parse.quote(c, safe='') + '/items'
        return self._paged(self._db(path, p), page)

    def searchContent(self, key, quick, pg='1'):
        page = max(1, int(pg or 1))
        return self._paged(self._db('/search/movie', {'q': key, 'start': (page - 1) * self.count, 'count': self.count}), page)

    @staticmethod
    def _norm(s):
        s = str(s or '').lower()
        for i, c in enumerate('一二三四五六七八九十', 1):
            s = s.replace('第' + c + '季', '第' + str(i) + '季')
        s = re.sub(r'[（(](?:粤语|国语|普通话|剧版|电影版)[）)]', '', s)
        return re.sub(r'[\s\W_]', '', s)

    @staticmethod
    def _season_number(s):
        m = re.search(r'第([0-9一二三四五六七八九十]+)[季部]', str(s or ''))
        if not m:
            return 0
        t = m.group(1)
        chars = '一二三四五六七八九十'
        return int(t) if t.isdigit() else chars.index(t) + 1 if t in chars else 0

    def _score(self, card, db):
        a, b = self._norm(card.get('title')), self._norm(db.get('title'))
        aliases = [self._norm(x) for x in (db.get('aka') or []) + [db.get('original_title') or '']]
        if not a or not b:
            return -999
        if a == b:
            score = 65
        elif a in aliases:
            score = 55
        elif min(len(a), len(b)) >= 2 and (a in b or b in a):
            score = 30
        else:
            return -999
        ds, cs = self._season_number(db.get('title')), self._season_number(card.get('title'))
        if ds and cs and ds != cs:
            return -999
        if ds and cs == ds:
            score += 15
        if '粤语' in str(card.get('title')) and '粤语' not in str(db.get('title')):
            score -= 18
        try:
            delta = abs(int(card.get('year')) - int(db.get('year')))
            score += 25 if delta == 0 else 6 if delta == 1 else -min(35, delta * 8)
        except (TypeError, ValueError):
            pass
        kind = card.get('content_kind')
        if db.get('is_show') or '真人秀' in (db.get('genres') or []):
            score += 15 if kind == 'variety' else -15
        elif db.get('type') == 'movie':
            score += 15 if kind == 'movie' else -25
        else:
            score += 15 if kind in ('series', 'anime') else -15
        return score

    def _match(self, db):
        queries = [db.get('title') or ''] + (db.get('aka') or [])[:2] + [db.get('original_title') or '']
        seen = set()
        for q in queries:
            if not q or q in seen:
                continue
            seen.add(q)
            path = '/v1/browse/catalog?q=' + urllib.parse.quote(q, safe='') + '&page=1&limit=20'
            result = self._memo('s:' + q, lambda: self._sj(path))
            candidates = []
            for card in result.get('cards') or []:
                variants = card.get('seasons') or []
                if not variants:
                    candidates.append(card)
                for v in variants:
                    if not v.get('variant_id') or v.get('has_playback') is False:
                        continue
                    c = dict(card)
                    c.update({'id': v['variant_id'], 'title': v.get('title') or card.get('title'), 'year': v.get('year') or card.get('year')})
                    candidates.append(c)
            if candidates:
                best = max(candidates, key=lambda c: self._score(c, db))
                if self._score(best, db) >= 55:
                    return best
        return None

    @staticmethod
    def _line_key(o):
        return str(o.get('provider_id') or ''), str(o.get('play_from') or '')

    def _lines(self, token):
        return self._sj('/v1/playback/resolve/' + urllib.parse.quote(token, safe='')).get('line_options') or []

    def _rank_lines(self, lines, include_empty=False):
        def rank(o):
            ticket = o.get('url_kind') == 'resolve_ticket' or str(o.get('url') or '').startswith('resolve://')
            preferred = ticket if self.prefer == 'official' else not ticket
            return not preferred, -float(o.get('preference_weight') or 0)
        return sorted((o for o in lines if o.get('url') or include_empty), key=rank)

    def detailContent(self, ids):
        if not ids:
            return {'list': []}
        vid = str(ids[0])
        try:
            if vid.startswith('db:'):
                meta = self._unpack(vid, 'db:')
            else:
                kind, sid = vid.split('$', 1)
                meta = {'kind': kind, 'id': sid}
            kind = 'tv' if meta.get('kind') == 'tv' else 'movie'
            db = self._memo('d:' + kind + str(meta['id']), lambda: self._db('/' + kind + '/' + urllib.parse.quote(str(meta['id']), safe='')))
            db = dict(db if db.get('title') else meta)
            db['type'] = kind
            vod = {'vod_id': vid, 'vod_name': db.get('title') or '豆瓣影片', 'vod_pic': self._pic(db), 'vod_year': str(db.get('year') or ''), 'vod_area': self._join(db.get('countries')), 'vod_type': self._join(db.get('genres')), 'vod_actor': self._join(db.get('actors')), 'vod_director': self._join(db.get('directors')), 'vod_content': db.get('intro') or '', 'vod_remarks': '豆瓣 ' + str((db.get('rating') or {}).get('value') or '暂无评分'), 'vod_play_from': '', 'vod_play_url': ''}
            target = self._match(db)
            if not target:
                vod['vod_content'] += '\n\n搜剧AI暂无准确匹配的片源，或接口请求失败。'
                return {'list': [vod]}
            cid = str(target['id'])
            info = self._memo('c:' + cid, lambda: self._sj('/v1/catalog/' + urllib.parse.quote(cid, safe='')))
            episodes = info.get('episodes') or self._sj('/v1/catalog/' + urllib.parse.quote(cid, safe='') + '/episodes').get('episodes') or []
            episodes = [e for e in episodes if e.get('token')]
            if not episodes:
                vod['vod_content'] += '\n\n已匹配到片源，但暂无可用选集。'
                return {'list': [vod]}
            vod['vod_content'] += '\n\n搜剧AI片源：%s (%s)' % (target.get('title') or '', target.get('year') or '')
            chosen = self._rank_lines(self._lines(episodes[0]['token']), include_empty=True)
            chosen.sort(key=lambda o: not (o.get('url_kind') == 'resolve_ticket' or str(o.get('url') or '').startswith('resolve://')))
            chosen = [{'auto': True}] + chosen
            names, urls, used = [], [], set()
            for i, o in enumerate(chosen):
                name = self._clean(o.get('provider_name') or o.get('label') or '自动线路')
                if name in used:
                    name += '·' + str(i + 1)
                used.add(name)
                eps = []
                for j, ep in enumerate(episodes):
                    label = self._clean(ep.get('title') or '第%s集' % (ep.get('number') or j + 1))
                    p = {'t': ep['token'], 'p': o.get('provider_id') or '', 'f': o.get('play_from') or '', 'n': o.get('provider_name') or o.get('label') or '', 'a': bool(o.get('auto'))}
                    eps.append(label + '$' + self._pack('play:', p))
                names.append(name)
                urls.append('#'.join(eps))
            vod['vod_play_from'], vod['vod_play_url'] = '$$$'.join(names), '$$$'.join(urls)
            return {'list': [vod]}
        except Exception as e:
            self._log('详情异常：' + str(e))
            return {'list': []}

    @staticmethod
    def _video_url(url):
        if not re.match(r'^https?://', str(url or ''), re.I):
            return False
        path = urllib.parse.urlsplit(url).path.lower()
        return not re.search(r'\.(?:jpe?g|png|gif|webp|bmp|svg)(?:$|[.~])|\.image(?:$|[.~])', path)

    def _play_headers(self, *objects):
        header = {'User-Agent': self.ua}
        if self.playback_referer is not None:
            header['Referer'] = str(self.playback_referer)
        for obj in objects:
            for key in ('headers', 'header', 'request_headers', 'http_headers'):
                value = obj.get(key)
                if isinstance(value, str):
                    try:
                        value = json.loads(value)
                    except Exception:
                        value = None
                if isinstance(value, dict):
                    for k, v in value.items():
                        if str(k).lower() not in ('host', 'content-length') and v is not None:
                            header[str(k)] = str(v)
            if obj.get('referer') is not None:
                header['Referer'] = str(obj['referer'])
        return header

    def playerContent(self, flag, id, vipFlags):
        raw = str(id or '').strip()
        if raw.startswith('http') and self._video_url(raw):
            return {'parse': 0, 'jx': 0, 'url': raw, 'header': self._play_headers()}
        error = '所选线路暂时没有可用地址，请手动切换其他线路'
        try:
            if raw.startswith('play:'):
                pick = self._unpack(raw, 'play:')
            else:
                token, _, provider = raw.partition('@@')
                pick = {'t': token, 'p': provider, 'f': ''}
            if not pick.get('t'):
                raise ValueError('选集token为空')
            options = self._rank_lines(self._lines(pick['t']))
            if pick.get('a'):
                options.sort(key=lambda o: (not bool(o.get('selected') or o.get('default_priority')), not (o.get('url_kind') == 'resolve_ticket' or str(o.get('url') or '').startswith('resolve://'))))
            elif pick.get('p') or pick.get('f') or pick.get('n'):
                options = [o for o in options
                           if (not pick.get('p') or o.get('provider_id') == pick['p'])
                           and (not pick.get('f') or o.get('play_from') == pick['f'])
                           and (not pick.get('n') or (o.get('provider_name') or o.get('label')) == pick['n'])]
            elif flag and flag != '自动线路':
                matched = [o for o in options if (o.get('provider_name') or o.get('label')) == flag]
                options = matched
            for o in options:
                url = o.get('url') or ''
                media = {}
                response = {}
                if o.get('url_kind') == 'resolve_ticket' or url.startswith('resolve://'):
                    response = self._sj('/v1/playback/resolve-line', {'ticket': url.replace('resolve://', '', 1), 'line': o.get('playback_source_id') or '', 'provider_id': o.get('provider_id') or '', 'play_from': o.get('play_from') or ''})
                    media = response.get('line') or {}
                    url = media.get('url') or ''
                    if not url and ('401' in self.last_error or '403' in self.last_error):
                        error = '所选官方线路需要有效登录或播放权限，请选择其他线路'
                if self._video_url(url):
                    kind = media.get('url_kind') or o.get('url_kind') or ''
                    result = {'parse': 0, 'jx': 0, 'url': url, 'header': self._play_headers(o, response, media)}
                    if kind in ('m3u8', 'hls') or '.m3u8' in urllib.parse.urlsplit(url).path.lower():
                        result['format'] = 'application/vnd.apple.mpegurl'
                    elif kind == 'mp4':
                        result['format'] = 'video/mp4'
                    return result
        except Exception as e:
            self._log('播放异常：' + str(e))
        self._log(error)
        return {'parse': 0, 'jx': 0, 'url': '', 'header': {}, 'msg': error}

    def isVideoFormat(self, url):
        return bool(re.search(r'\.(m3u8|mp4|flv|mkv)(?:[?#]|$)', str(url), re.I))

    def manualVideoCheck(self):
        return False

    def localProxy(self, param):
        return [404, 'text/plain', 'Not Found']

    def destroy(self):
        self._cache.clear()
