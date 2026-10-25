
import hashlib
import json
import os
import re
import sys
import tempfile
import time
import uuid

import requests as N

sys.path.append('..')
try:
    from base.spider import Spider as A          # 影视仓 / T3 内置 python
except Exception:
    try:
        from base.spider import BaseSpider as A  # hipy-server T4
    except Exception:
        try:
            from t4.base.spider import BaseSpider as A
        except Exception:
            class A(object):                     # 兜底: 独立加载不报错
                def __init__(self):
                    pass

UA = 'TingShiJie/1.8.8 (m.i275.com)'
APP_UA = 'okhttp/4.9.3'
DEFAULT_BASE = 'https://app.365ting.com/listen/Apitzg2025/'
CONFIG_URLS = ['http://101.43.48.231:8090/config/tingchina2025.txt']
API = 'https://api.365ting.com'
TY = API + '/tingyou-app'
PLAY_FLAG = '拾音盘'
NATIVE_FLAG = '275听书'
# AppGetChapterUrl2023 签名盐 (逆向自 java 版)
SIGN_KEY = 'J9gSpfUlzYxE8Hn5IXiGaD2jVMrwAm0K'
SEARCH_TOKEN = 'abcSEARCH-2025'
SRC_TTL = 300  # 275 播放地址缓存时长 (auth_key 实测过期后仍可播, 5 分钟很安全)
PAGE_SIZE = 120
DEVICE_PREFIX = 'tvbox-tingshijie-'
# 落盘缓存: 固定 device_id + 专辑映射, 让重复打开详情页走快路径
CACHE_FILE = os.path.join(tempfile.gettempdir(), 'tvbox_tingshijie_cache.json')
META_KEYS = ('id', 'title', 'cover_url', 'teller', 'author', 'count', 'description')

CLASSES = [
    ('6', '玄幻奇幻'), ('7', '都市言情'), ('8', '宫斗女频'), ('9', '官场商战'),
    ('10', '武侠仙侠'), ('11', '刑侦推理'), ('12', '探险科幻'), ('13', '重生穿越'),
    ('14', '恐怖惊悚'), ('15', '文学历史'), ('49', '两性情感'),
]


def LOG(msg):
    try:
        print('[听书世界]', msg)
    except Exception:
        pass


def _md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()


class Spider(A):

    def __init__(self):
        super().__init__()
        self.name = '听书世界'
        self.error_play_url = ''
        self.extend = {}
        self._app = None
        self.base = DEFAULT_BASE
        self._uid = None
        self._device_id = ''
        self._album_map = {}    # 275 bookId -> 拾音盘专辑 id
        self._plat_map = {}     # 拾音盘专辑 id -> 平台歌单 id (已提取过)
        self._info_cache = {}   # 拾音盘专辑 id -> {tracks,...} 进程内缓存
        self._ty_meta = {}      # 拾音盘专辑 id -> 搜索结果元数据 (标题兜底)
        self._src_cache = {}    # 275 播放地址短期缓存 (键 -> (url, 时间))
        self._book_cache = {}   # 275 bookId -> bookData (进程内, 重复打开秒出)
        self._chap_cache = {}   # 275 bookId -> (chapters, total)
        self._ty_miss = set()   # 拾音盘确认没这本书的 bookId (本会话不再白搜)
        self._disk = None       # 落盘缓存 (懒加载)

    def getName(self):
        return self.name

    def init(self, extend='{}'):
        try:
            self.extend = json.loads(extend) if extend else {}
            if not isinstance(self.extend, dict):
                self.extend = {}
        except Exception as e:
            LOG('init extend 解析失败: %s' % e)
            self.extend = {}
        if self.extend.get('name'):
            self.name = self.extend.get('name')
        self._boot()

    # ==================== 启动 / 落盘缓存 ====================
    def _boot(self):
        """懒启动: 即使运行时没调 init 也不会挂"""
        if self._app is None:
            self._disk = self._loadDisk()
            self._device_id = self._disk.get('device_id') or ''
            self._album_map = dict(self._disk.get('album_map') or {})
            self._plat_map = dict(self._disk.get('plat_map') or {})
            self._ty_meta = dict(self._disk.get('meta') or {})
            self._app = N.Session()
            self._app.headers.update({'User-Agent': APP_UA, 'Content-Type': 'application/json'})
            self.base = self._resolveBase()
            LOG('base = %s (device=%s, 映射缓存 %d 条)'
                % (self.base, self._device_id or 'new', len(self._album_map)))

    @staticmethod
    def _loadDisk():
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                d = json.load(f)
            if isinstance(d, dict):
                return d
        except Exception:
            pass
        return {}

    def _saveDisk(self):
        try:
            d = {
                'device_id': self._device_id or '',
                'album_map': self._album_map,
                'plat_map': self._plat_map,
                'meta': self._ty_meta,
            }
            tmp = CACHE_FILE + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False)
            os.replace(tmp, CACHE_FILE)
        except Exception as e:
            LOG('cache 落盘失败: %s' % e)

    def _resolveBase(self):
        def probe(c):
            try:
                r = N.get(c + 'appHomeByCategory?categoryId=6&page=1&size=1',
                          timeout=4, headers={'User-Agent': UA})
                return r.json().get('status') == 0
            except Exception:
                return False
        # 默认地址直接探活; 分发服务器(常年失效)只在默认地址挂掉时才去查
        if probe(DEFAULT_BASE):
            return DEFAULT_BASE
        for u in CONFIG_URLS:
            try:
                text = N.get(u, timeout=2, headers={'User-Agent': UA}).text.strip()
                if text and len(text) <= 200 and re.match(r'^https?://[^\s"\'<>]+$', text):
                    c = text if text.endswith('/') else text + '/'
                    if probe(c):
                        return c
            except Exception:
                pass
        return DEFAULT_BASE

    # ==================== 带重试的 HTTP (详情页健壮性核心) ====================
    def _req(self, method, url, tries=3, **kw):
        """网络抖动/超时/429/5xx 自动退避重试, 全部失败才抛异常"""
        kw.setdefault('timeout', 15)
        last = None
        for i in range(tries):
            try:
                r = self._app.request(method, url, **kw)
                if r.status_code in (429, 500, 502, 503, 504) and i < tries - 1:
                    last = RuntimeError('HTTP %d' % r.status_code)
                    time.sleep(0.6 * (i + 1))
                    continue
                r.raise_for_status()
                return r
            except Exception as e:
                last = e
                time.sleep(0.6 * (i + 1))
        raise last

    def _json(self, method, url, **kw):
        r = self._req(method, url, **kw)
        try:
            return r.json()
        except Exception:
            raise RuntimeError('响应非 JSON: %s' % url)

    def _uidGet(self):
        if not self._uid:
            if not self._device_id:  # 固定设备号: 跨启动同一账号, 已提取专辑直接命中
                self._device_id = DEVICE_PREFIX + uuid.uuid4().hex[:12]
                self._saveDisk()
            j = self._json('POST', API + '/api/auth/device-login',
                           json={'device_id': self._device_id}, timeout=15)
            uid = (j.get('data') or {}).get('user_id')
            if not uid:
                raise RuntimeError('device-login 无 user_id: %s' % str(j)[:120])
            self._uid = uid
        return self._uid

    # ==================== 275 官方书单接口 ====================
    def _api275(self, path, timeout=10):
        return self._json('GET', self.base + path,
                          headers={'User-Agent': UA}, timeout=timeout)

    def _item(self, x):
        return {
            'vod_id': '275_' + str(x.get('id') or ''),
            'vod_name': x.get('bookTitle') or '',
            'vod_pic': x.get('bookImage') or '',
            'vod_remarks': x.get('bookAnchor') or '',
        }

    def _listByCat(self, tid, pg, size=PAGE_SIZE):
        data = self._api275('appHomeByCategory?categoryId=%s&page=%d&size=%d'
                            % (tid, int(pg or 1), size)).get('data') or []
        return [self._item(x) for x in data]

    # ==================== 拾音盘接口 ====================
    def _tySearch(self, keyword):
        j = self._json('GET', TY + '/search', params={'keyword': keyword}, timeout=15)
        items = (j.get('data') or {}).get('items') or []
        added = False
        for it in items:
            if it.get('id'):
                k = str(it['id'])
                if k not in self._ty_meta:
                    added = True
                self._ty_meta[k] = {x: it.get(x) for x in META_KEYS}
        if added:
            self._saveDisk()
        return items

    def _tyMatch(self, title, teller):
        """标题真正对得上才认; 对不上返回 None 走 275 原生兜底。
        不再拿 items[0] 硬凑 —— 否则 TME 独家书会错绑到别的演播版本。"""
        items = self._tySearch(title or '') or []
        title = re.sub(r'\s+', '', title or '')
        if not title or not items:
            return None

        def ok(it):
            t = re.sub(r'\s+', '', it.get('title') or '')
            return bool(t) and (t.startswith(title) or title in t or t in title)

        for it in items:  # 标题+演播都对上最优先
            if ok(it) and teller and teller in (it.get('teller') or ''):
                return it
        for it in items:  # 标题对上即可
            if ok(it):
                return it
        return None

    def _albumMeta(self, uid, ty_id):
        """查用户歌单拿专辑元数据 (title/cover), 拿不到返回 {}"""
        try:
            j = self._json('GET', API + '/api/users/%d/albums' % uid, timeout=15)
            for a in j.get('data') or []:
                if str(a.get('external_id')) == str(ty_id):
                    return a
        except Exception as e:
            LOG('用户歌单查询失败(忽略): %s' % e)
        return {}

    def _doImport(self, uid, ty_id, rounds=2):
        """提交提取任务并轮询; 轮询单次异常不中断, 失败再提交一轮. 返回 plat id 或 None"""
        for _ in range(rounds):
            try:
                j = self._json('POST', TY + '/import',
                               json={'user_id': uid, 'album_id': ty_id}, timeout=30)
                task = (j.get('data') or {}).get('task_id')
            except Exception as e:
                LOG('提取提交异常(重试): %s' % e)
                time.sleep(1)
                continue
            if not task:
                LOG('提取任务无 task_id: %s' % str(j)[:120])
                time.sleep(1)
                continue
            deadline = time.time() + 20      # 服务端冷门书抓取上限
            plat, failed = None, False
            while time.time() < deadline:
                try:
                    st = (self._json('GET', TY + '/import/status',
                                     params={'task_id': task}, timeout=10).get('data')) or {}
                except Exception as e:
                    LOG('状态轮询异常(继续等): %s' % e)  # 抖动不中断提取
                    time.sleep(1)
                    continue
                if st.get('status') == 'done':
                    plat = st.get('album_id')
                    break
                if st.get('status') == 'failed':
                    failed = True
                    break
                time.sleep(0.5)               # 先查后睡: 热门书克隆缓存常秒回
            if plat:
                return plat
            LOG('提取%s (task=%s)' % ('失败' if failed else '超时', task))
            time.sleep(1)
        return None

    def _getTracks(self, plat, uid, tries=3):
        """拉曲目列表: 瞬时异常/空列表都重试 (服务端 status=done 后曲目可能还没就绪)"""
        tracks = []
        for i in range(tries):
            try:
                j = self._json('GET', API + '/api/albums/%s/tracks' % plat,
                               params={'user_id': uid}, timeout=20)
                tracks = j.get('data') or []
                if not isinstance(tracks, list):
                    tracks = tracks.get('tracks') or tracks.get('list') or []
            except Exception as e:
                tracks = []
                LOG('曲目获取异常: %s' % e)
            if tracks:
                return tracks
            time.sleep(0.8)
        return []

    def _ensureAlbum(self, ty_id, _retried=False):
        """返回 {platform_id, title, cover, desc, teller, count, tracks}, 带缓存"""
        ty_id = str(ty_id)
        if ty_id in self._info_cache:
            return self._info_cache[ty_id]
        uid = self._uidGet()
        meta = {}
        plat = self._plat_map.get(ty_id)   # 落盘快路径: 该专辑已提取过
        if plat is None:                   # 兜底: 从歌单里找 (老缓存/别处提取的)
            meta = self._albumMeta(uid, ty_id)
            plat = meta.get('id')
        if plat is None:                   # 提交提取任务 (内部自带重试)
            plat = self._doImport(uid, ty_id)
            if plat is None:
                raise RuntimeError('提取未完成, 稍后重试')
            self._plat_map[ty_id] = plat
            self._saveDisk()
        if not meta and ty_id not in self._ty_meta:
            meta = self._albumMeta(uid, ty_id)  # 仅缺元数据时才回查 (历史记录直开)
        tracks = self._getTracks(plat, uid)
        if not tracks and not _retried:
            # 盘缓存的 plat 失效 (服务端重建歌单等): 重置缓存重新提取一次
            LOG('曲目为空, 重置提取缓存重试: %s' % ty_id)
            self._plat_map.pop(ty_id, None)
            self._saveDisk()
            return self._ensureAlbum(ty_id, _retried=True)
        cached = self._ty_meta.get(ty_id) or {}
        info = {
            'platform_id': plat, 'ty_id': ty_id,
            'title': meta.get('title') or cached.get('title') or '',
            'cover': meta.get('cover_url') or cached.get('cover_url') or '',
            'desc': meta.get('description') or cached.get('description') or '',
            'teller': cached.get('teller') or '',
            'count': int(meta.get('count') or cached.get('count') or 0),
            'tracks': tracks,
        }
        if tracks:  # 空曲目不落缓存 (服务端还没抓好时, 下次进来还能再试)
            self._info_cache[ty_id] = info
        return info

    # ==================== 275 原生兜底 (拾音盘没有的书) ====================
    def _bookData(self, bid):
        if bid in self._book_cache:
            return self._book_cache[bid]
        try:
            data = (self._api275('book?bookId=' + bid).get('data') or {}).get('bookData') or {}
        except Exception as e:
            LOG('275 book 获取失败: %s' % e)
            return {}
        if data:
            if len(self._book_cache) > 32:
                self._book_cache.clear()
            self._book_cache[bid] = data
        return data

    def _bookChapters(self, bid, max_pages=8):
        """275 官方章节列表 -> (章节列表, 总数)"""
        if bid in self._chap_cache:
            return self._chap_cache[bid]
        out, page, total = [], 1, 0
        while page <= max_pages:
            d = self._api275('chapter?size=1000&page=%d&sort=asc&bookId=%s' % (page, bid),
                             timeout=20).get('data') or {}
            lst = d.get('list') or []
            out.extend(lst)
            total = int(d.get('count') or 0)
            if not lst or len(out) >= total or len(lst) < 1000:
                break
            page += 1
        if out:
            if len(self._chap_cache) > 8:   # 章节列表大, 少存点
                self._chap_cache.clear()
            self._chap_cache[bid] = (out, total)
        return out, total

    def _bookNative(self, bid, book):
        """拾音盘拿不到时用 275 原生章节造详情 (TME 独家书也能出选集)"""
        try:
            chapters, total = self._bookChapters(bid)
        except Exception as e:
            LOG('275 章节获取失败 [%s]: %s' % (bid, e))
            return None
        if not chapters:
            LOG('275 章节为空: %s' % bid)
            return None
        return {
            'native': True, 'bid': str(bid), 'ty_id': '', 'platform_id': '',
            'title': book.get('bookTitle') or '',
            'cover': book.get('bookImage') or '',
            'desc': book.get('bookDesc') or '',
            'teller': book.get('bookAnchor') or '',
            'count': total or len(chapters),
            'tracks': [], 'chapters': chapters,
        }

    def _bookToAlbum(self, bid):
        """拾音盘优先; 搜不到/提取失败/曲目为空 -> 275 原生章节兜底, 详情永不出空"""
        book = self._bookData(bid)
        info = None
        if bid in self._album_map:
            try:  # 已有映射: 书名拿不到也不影响播放
                info = self._ensureAlbum(self._album_map[bid])
            except Exception as e:
                LOG('拾音盘缓存专辑失败, 转275原生: %s' % e)
        elif book.get('bookTitle'):
            hit = None
            if bid in self._ty_miss:      # 会话内已确认拾音盘没有, 直接走原生
                LOG('拾音盘已知无此书, 走275原生: %s' % book.get('bookTitle'))
            else:
                hit = self._tyMatch(book.get('bookTitle', ''), book.get('bookAnchor') or '')
                if hit:
                    ty_id = str(hit['id'])
                    self._album_map[bid] = ty_id
                    self._saveDisk()
                    try:
                        info = self._ensureAlbum(ty_id)
                    except Exception as e:
                        LOG('拾音盘提取失败, 转275原生: %s' % e)
                else:
                    self._ty_miss.add(bid)
                    LOG('拾音盘未匹配到专辑, 走275原生: %s' % book.get('bookTitle'))
        if info and info.get('tracks'):
            # 275 侧的书名/封面/简介更干净, 优先使用
            info['title'] = book.get('bookTitle') or info['title']
            info['cover'] = book.get('bookImage') or info['cover']
            info['desc'] = book.get('bookDesc') or info['desc']
            info['teller'] = book.get('bookAnchor') or info.get('teller') or ''
            return info
        if info:
            LOG('拾音盘曲目为空, 转275原生: %s' % book.get('bookTitle'))
        if not book.get('bookTitle'):
            LOG('275 book 无数据: %s' % bid)
            return info
        native = self._bookNative(bid, book)
        if native:
            return native
        return info  # 原生也拿不到才退回按集数合成

    # ==================== 模板接口 ====================
    def homeContent(self, filter):
        S = {'class': [], 'filters': {}, 'list': [], 'parse': 0, 'jx': 0}
        try:
            self._boot()
            S['class'] = [{'type_id': tid, 'type_name': name} for tid, name in CLASSES]
            S['list'] = self._listByCat('6', 1, 12)  # 首页推荐 (玄幻热门)
        except Exception as e:
            LOG('homeContent 失败: %s' % e)
        return S

    def homeVideoContent(self):
        try:
            self._boot()
            return {'list': self._listByCat('6', 1, 12)}
        except Exception as e:
            LOG('homeVideoContent 失败: %s' % e)
            return {'list': []}

    def categoryContent(self, cid, page, filter, ext):
        S = {'list': [], 'page': int(page or 1), 'pagecount': int(page or 1),
             'limit': PAGE_SIZE, 'total': 0, 'parse': 0, 'jx': 0}
        try:
            self._boot()
            S['list'] = self._listByCat(cid, page)
            if len(S['list']) >= PAGE_SIZE:
                S['pagecount'] = int(page or 1) + 1
            S['total'] = S['pagecount'] * PAGE_SIZE
        except Exception as e:
            LOG('categoryContent 失败: %s' % e)
        return S

    @staticmethod
    def _buildVod(raw, info):
        """三路出选集: 拾音盘 tracks / 275 原生章节 / 按集数合成 (详情永不出空)"""
        eps, flag = [], PLAY_FLAG
        if info.get('native'):
            bid = info['bid']
            for i, ch in enumerate(info.get('chapters') or []):
                cid = ch.get('chapterId') or ch.get('url')
                if not cid:
                    continue
                name = re.sub(r'[#$]', ' ', ch.get('title') or '') or ('第%d集' % (i + 1))
                eps.append('%s$275|%s|%s' % (name, bid, cid))
            if not eps:
                return None
            flag = NATIVE_FLAG
        else:
            ty_id = info['ty_id']
            tracks = info.get('tracks') or []
            if tracks:
                for i, t in enumerate(tracks):
                    idx = t.get('track_no') or i + 1
                    name = re.sub(r'[#$]', ' ', t.get('title') or '') or ('第%d集' % idx)
                    eps.append('%s$%s|%s' % (name, ty_id, idx))
            else:
                count = int(info.get('count') or 0)
                if count <= 0:
                    return None
                LOG('曲目列表不可用, 按集数合成选集兜底: %s x%d' % (ty_id, count))
                eps = ['第%d集$%s|%d' % (n, ty_id, n) for n in range(1, count + 1)]
        return {
            'vod_id': raw,
            'vod_name': info.get('title') or '',
            'vod_pic': info.get('cover') or '',
            'vod_remarks': info.get('teller') or '',
            'vod_content': info.get('desc') or '',
            'vod_play_from': flag,
            'vod_play_url': '#'.join(eps),
        }

    def detailContent(self, did):
        raw = str(did[0]).strip()
        S = {'list': [], 'parse': 0, 'jx': 0}
        t0 = time.time()
        for attempt in (1, 2):  # 整体重试一轮: 瞬时失败时第一轮往往已把各环节缓存焐热
            info, vod = None, None
            try:
                self._boot()
                if raw.startswith('ty_'):
                    info = self._ensureAlbum(raw[3:])
                else:
                    info = self._bookToAlbum(raw.replace('275_', ''))
                if info:
                    vod = self._buildVod(raw, info)
            except Exception as e:
                LOG('detailContent 异常(第%d次) [%s]: %s' % (attempt, raw, e))
            if vod:
                S['list'].append(vod)
                LOG('detail %s: %d集 %.2fs (第%d次)'
                    % (raw, vod['vod_play_url'].count('#') + 1, time.time() - t0, attempt))
                return S
            if attempt < 2:
                time.sleep(0.8)
        LOG('detailContent 失败 [%s] %.2fs' % (raw, time.time() - t0))
        return S

    def searchContent(self, key, quick, page='1'):
        S = {'list': [], 'page': 1, 'pagecount': 1, 'limit': 20, 'total': 0,
             'parse': 0, 'jx': 0}
        try:
            self._boot()
            seen = set()
            for it in self._tySearch(key) or []:
                name = it.get('title') or ''
                seen.add(re.sub(r'\s+', '', name))
                S['list'].append({
                    'vod_id': 'ty_' + str(it.get('id') or ''),
                    'vod_name': name,
                    'vod_pic': it.get('cover_url') or '',
                    'vod_remarks': '%s·%s集' % (it.get('teller') or it.get('author') or '',
                                                it.get('count') or '?'),
                })
            # 275 官方搜索: 拾音盘没有的书 (TME 独家等) 也能搜到
            try:
                j = self._json('GET', self.base + 'appSearch',
                               params={'client': 'babala-android', 'search': key,
                                       'app_token': SEARCH_TOKEN},
                               headers={'User-Agent': UA}, timeout=15)
                for x in (j.get('data') or {}).get('bookData') or []:
                    name = x.get('bookTitle') or ''
                    k = re.sub(r'\s+', '', name)
                    if not k or k in seen:
                        continue
                    seen.add(k)
                    S['list'].append({
                        'vod_id': '275_' + str(x.get('id') or ''),
                        'vod_name': name,
                        'vod_pic': x.get('bookImage') or '',
                        'vod_remarks': x.get('bookAnchor') or '',
                    })
            except Exception as e:
                LOG('275 搜索失败(忽略): %s' % e)
            S['total'] = len(S['list'])
        except Exception as e:
            LOG('searchContent 失败 [%s]: %s' % (key, e))
        return S

    def _nativeSrc(self, bid, cid):
        """275 原生播放地址: timeStamp+盐 双重 md5 签名 (缺签名服务端回 data:null)。
        主用老接口 AppGetChapterUrl (xmcdn 源, 实测 12/12 稳定);
        AppGetChapterUrl2023 (自家 audio.tingshijie.com 源) 经常 status:1
        "分集地址解析失败", 只当备用。拿到后短期缓存, 复播不再打接口。"""
        key = '%s|%s' % (bid, cid)
        c = self._src_cache.get(key)
        if c and time.time() - c[1] < SRC_TTL:
            return c[0]
        for i in range(3):
            for path in ('AppGetChapterUrl', 'AppGetChapterUrl2023'):
                try:
                    ts = str(int(time.time() * 1000))
                    sign = _md5(_md5(ts + SIGN_KEY) + SIGN_KEY)
                    j = self._json('GET', self.base + path,
                                   params={'timeStamp': ts, 'uid': '', 'chapterId': cid,
                                           'addItParapet': sign, 'bookId': bid},
                                   headers={'User-Agent': APP_UA}, tries=2, timeout=10)
                    src = j.get('src')
                    if src:
                        self._src_cache[key] = (src, time.time())
                        if len(self._src_cache) > 64:
                            self._src_cache.clear()
                        return src
                    LOG('275 播放地址为空[%s]: %s/%s %s' % (path[-4:], bid, cid, str(j)[:70]))
                except Exception as e:
                    LOG('275 播放地址获取异常[%s]: %s' % (path[-4:], e))
            time.sleep(1.0 * (i + 1))   # 抖动/频控冷却
        return ''

    def playerContent(self, flag, pid, vipFlags):
        # 直链由 album+idx 规则拼出, 不做探活: 探活请求一旦抖动就返回空 url,
        # 播放器必然报"暂无播放数据" —— 交给播放器自己拉流即可。
        # header 用 okhttp UA: audio.tingshijie.com 会拦截官方 UA
        # (Access Denied: Please use the official App), okhttp/浏览器 UA 放行
        S = {'parse': 0, 'jx': 0, 'playUrl': '', 'url': '', 'header': {'User-Agent': APP_UA}}
        try:
            parts = str(pid).split('|')
            if len(parts) == 3 and parts[0] == '275':        # 275 原生章节
                S['url'] = self._nativeSrc(parts[1], parts[2])
                if not S['url']:
                    LOG('playerContent 275 播放地址获取失败: %s' % pid)
            elif len(parts) == 2 and parts[1].isdigit():     # 拾音盘直链
                S['url'] = '%s/tingyou/stream?album=%s&idx=%s' % (API, parts[0], parts[1])
            else:
                LOG('playerContent 参数异常: %s' % pid)
        except Exception as e:
            LOG('playerContent 参数异常 [%s]: %s' % (pid, e))
        return S

    def localProxy(self, params):
        return 0

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def destroy(self):
        try:
            self._app.close()
        except Exception:
            pass


if __name__ == '__main__':
    0
