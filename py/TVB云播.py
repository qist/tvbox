# -*- coding: utf-8 -*-
# by @Qist
"""
TVB云播
"""
import re
import json
import base64
import zlib
import requests
from Crypto.Cipher import AES
from base.spider import Spider  # 继承基础Spider类


# ------------------------------------------------------------------ #
# 响应解密（AES-128-CBC + gzip），key/iv 来自 libnmmp.so
# ------------------------------------------------------------------ #
_AES_KEY = b"MickwrKuMickwrKu"
_AES_IV = b"MickwrKuMickwrKu"


def _decrypt_data(b64text):
    """data 字段(base64) -> 明文 JSON 字符串"""
    if not b64text:
        return None
    try:
        raw = base64.b64decode(b64text)
        pt = AES.new(_AES_KEY, AES.MODE_CBC, _AES_IV).decrypt(raw)
        pad = pt[-1]
        if 1 <= pad <= 16:
            pt = pt[:-pad]
        try:
            return zlib.decompress(pt, 16 + zlib.MAX_WBITS).decode('utf-8', 'ignore')
        except Exception:
            return pt.decode('utf-8', 'ignore')
    except Exception as e:
        print(f"[hktv] decrypt fail: {e}")
        return None


# 线路名 -> 中文显示名（源站返回的是英文/拼音缩写）
_LINE_CN = {
    'mp4': 'MP4 高清',
    'YYNB': '优优牛播',
    'wsym3u8': '微视云 M3U8',
    'bfzym3u8': '暴风影视 M3U8',
    'lzm3u8': '量子 M3U8',
    'hkm3u8': '港剧 M3U8',
    '1080zyk': '1080 自愈库',
}


def _line_cn(name):
    """线路名转中文显示；未知线路保留原名。"""
    return _LINE_CN.get(name, name)


class Spider(Spider):
    def getName(self):
        return 'HKTV影视'

    def init(self, extend=""):
        if extend and extend.strip():
            self.host = extend.strip().rstrip('/')
        return self.host

    def __init__(self):
        self.name = 'HKTV影视'
        self.host = 'http://app.tuxianimg.com'
        self.timeout = 25
        # 注：Host / Content-Length 由 requests 按 URL 与 body 自动生成，不在此手动设置。
        self.header = {
            'App-Device-Id': '2c84565e46955353d875e3d964d87e1c6',
            'App-Os-Type': 'android',
            'App-Ui-Mode': 'light',
            'App-Version-Code': '100',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'okhttp/3.14.9',
        }
        # 由 playerContent 作为“全局播放 header”返回，框架会透传到所有直链请求。
        # 注：host 字段由 requests/框架按 URL 自动生成，不在此手动设置（否则跨域名会错）。
        self.play_header = {
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 15; ZXV10S100V7 Build/b5cc949.1)',
            'accept-encoding': 'gzip',
            'allowcrossprotocolredirects': 'true',
            'connection': 'Keep-Alive',
        }
        # 运行时由 init 接口填充
        self.class_names = []
        self.class_urls = []
        self.type_extend = {}   # type_id -> {class/area/lang/year/sort 选项}

    # ------------------------------------------------------------------ #
    # 内部：统一 API 请求 + 解密
    # ------------------------------------------------------------------ #
    def _api(self, endpoint, params=None):
        url = f"{self.host}/api/vod/{endpoint}"
        try:
            resp = requests.post(url, data=params or {}, headers=self.header,
                                 timeout=self.timeout, verify=False)
            resp.encoding = 'utf-8'
            if resp.status_code != 200:
                print(f"[hktv] {endpoint} HTTP {resp.status_code}")
                return None
            try:
                obj = resp.json()
            except Exception:
                m = re.search(r'\{.*\}', resp.text, re.S)
                obj = json.loads(m.group(0)) if m else None
            if not obj:
                return None
            plain = _decrypt_data(obj.get('data'))
            if not plain:
                return None
            return json.loads(plain)
        except Exception as e:
            print(f"[hktv] request {endpoint} failed: {e}")
            return None

    @staticmethod
    def _pic(pic):
        if not pic:
            return ''
        return pic if pic.startswith('http') else pic

    @staticmethod
    def _vod_item(v):
        pic = v.get('vod_pic') or v.get('vod_pic_slide') or ''
        return {
            'vod_id': str(v.get('vod_id', '') or ''),
            'vod_name': v.get('vod_name', '') or '',
            'vod_pic': Spider._pic(pic),
            'vod_remarks': v.get('vod_remarks', '') or '',
        }

    # ------------------------------------------------------------------ #
    # 框架接口（与 tvb.py 完全一致）
    # ------------------------------------------------------------------ #
    def homeContent(self, filter):
        try:
            result = {'class': [], 'list': []}
            init = self._api('init')
            if init:
                # 分类
                for c in init.get('type_list', []):
                    tid = str(c.get('type_id', ''))
                    tname = c.get('type_name', '')
                    if not tid or not tname:
                        continue
                    if tid == '0' and tname == '全部':
                        continue  # 跳过“全部”虚拟项
                    self.class_names.append(tname)
                    self.class_urls.append(tid)
                    # 解析筛选维度
                    ext = c.get('type_extend', '')
                    if ext:
                        try:
                            self.type_extend[tid] = json.loads(ext)
                        except Exception:
                            pass
                # 首页推荐
                for v in init.get('recommend_list', []):
                    item = self._vod_item(v)
                    if item['vod_id'] and item['vod_name']:
                        result['list'].append(item)

            for name, cid in zip(self.class_names, self.class_urls):
                result['class'].append({'type_name': name, 'type_id': cid})

            if filter:
                result['filters'] = {}
                for cid in self.class_urls:
                    result['filters'][cid] = self.get_filter_data(cid)

            return result
        except Exception as e:
            print(f"Error in homeContent: {e}")
            import traceback
            traceback.print_exc()
            return {'class': [], 'list': []}

    def get_filter_data(self, tid):
        """
        筛选维度来自 init 的 type_extend（真实数据）；无则用预定义兜底。
        维度：class(类型)/area(地区)/lang(语言)/year(年份)/sort(排序)
        """
        try:
            ext = self.type_extend.get(str(tid))
            if ext:
                out = []
                label_map = {'class': '类型', 'area': '地区', 'lang': '语言',
                             'year': '年份', 'sort': '排序', 'star': '明星',
                             'director': '导演', 'state': '状态', 'version': '版本'}
                for key, label in label_map.items():
                    vals = ext.get(key)
                    if not vals:
                        continue
                    items = [{'n': '全部', 'v': ''}]
                    for v in vals.split(','):
                        v = v.strip()
                        if v:
                            items.append({'n': v, 'v': v})
                    out.append({'key': key, 'name': label, 'value': items})
                if out:
                    return out
            # 兜底
            return [
                {'key': 'class', 'name': '类型', 'value': [{'n': '全部', 'v': ''}, {'n': '动作', 'v': '动作'}, {'n': '喜剧', 'v': '喜剧'}, {'n': '爱情', 'v': '爱情'}, {'n': '科幻', 'v': '科幻'}, {'n': '剧情', 'v': '剧情'}, {'n': '犯罪', 'v': '犯罪'}, {'n': '奇幻', 'v': '奇幻'}]},
                {'key': 'area', 'name': '地区', 'value': [{'n': '全部', 'v': ''}, {'n': '大陆', 'v': '大陆'}, {'n': '香港', 'v': '香港'}, {'n': '台湾', 'v': '台湾'}, {'n': '美国', 'v': '美国'}, {'n': '日本', 'v': '日本'}, {'n': '韩国', 'v': '韩国'}]},
                {'key': 'lang', 'name': '语言', 'value': [{'n': '全部', 'v': ''}, {'n': '国语', 'v': '国语'}, {'n': '英语', 'v': '英语'}, {'n': '粤语', 'v': '粤语'}]},
                {'key': 'year', 'name': '年份', 'value': [{'n': '全部', 'v': ''}, {'n': '2026', 'v': '2026'}, {'n': '2025', 'v': '2025'}, {'n': '2024', 'v': '2024'}, {'n': '2023', 'v': '2023'}]},
                {'key': 'sort', 'name': '排序', 'value': [{'n': '全部', 'v': ''}, {'n': '时间', 'v': 'time'}, {'n': '人气', 'v': 'hits'}, {'n': '评分', 'v': 'score'}]},
            ]
        except Exception as e:
            print(f"Error in get_filter_data: {e}")
            return []

    def categoryContent(self, tid, pg, filter, extend):
        try:
            params = {'type_id': tid, 'page': pg}
            if extend:
                for key in ('class', 'area', 'lang', 'year', 'sort'):
                    val = extend.get(key)
                    if val:
                        params[key] = val

            data = self._api('typeFilterVodList', params)
            if not data:
                return {'list': [], 'page': int(pg), 'pagecount': 0,
                        'limit': 0, 'total': 0}

            rows = data.get('recommend_list') or []
            videos = [self._vod_item(v) for v in rows
                      if v.get('vod_id') and v.get('vod_name')]

            seen = set()
            uniq = []
            for v in videos:
                if v['vod_id'] not in seen:
                    seen.add(v['vod_id'])
                    uniq.append(v)

            total = data.get('total', len(uniq))
            pagecount = data.get('page_count', data.get('pagecount', 999))
            return {
                'list': uniq,
                'page': int(pg),
                'pagecount': pagecount,
                'limit': len(uniq),
                'total': total,
            }
        except Exception as e:
            print(f"Error in categoryContent: {e}")
            import traceback
            traceback.print_exc()
            return {'list': [], 'page': int(pg), 'pagecount': 0,
                    'limit': 0, 'total': 0}

    def detailContent(self, ids):
        try:
            if not ids or not ids[0]:
                return {'list': []}
            vid = ids[0]
            data = self._api('vodDetail', {'vod_id': vid})
            if not data:
                return {'list': []}

            v = data.get('vod') or {}
            if not isinstance(v, dict):
                return {'list': []}

            vod = {
                'vod_id': str(v.get('vod_id', vid)),
                'vod_name': v.get('vod_name', '') or '',
                'vod_pic': self._pic(v.get('vod_pic') or v.get('vod_pic_slide') or ''),
                'vod_remarks': v.get('vod_remarks', '') or '',
                'vod_year': v.get('vod_year', '') or '',
                'vod_area': v.get('vod_area', '') or '',
                'vod_actor': v.get('vod_actor', '') or '',
                'vod_director': v.get('vod_director', '') or '',
                'vod_content': v.get('vod_content', '') or '',
            }

            # 线路：from_list 名 + url_list 集（url 在 vodParse 中解密）
            from_list = data.get('vod_play_from_list') or []
            url_list = data.get('vod_play_url_list') or []
            src_list = data.get('player_source_list') or []
            # player_code -> player_source_id
            code2id = {s.get('player_code'): s.get('id') for s in src_list if s.get('player_code')}

            play_from = []
            play_url = []
            for idx, src in enumerate(from_list):
                psid = code2id.get(src, '')
                episodes = []
                if idx < len(url_list):
                    for ep in url_list[idx].get('urls', []):
                        # 编码: 名称$player_source_id@episode_index@vod_id
                        episodes.append(f"{ep.get('name','')}${psid}@{ep.get('episode_index','')}@{vid}")
                play_from.append(_line_cn(src))
                play_url.append('#'.join(episodes))

            vod['vod_play_from'] = '$$$'.join(play_from)
            vod['vod_play_url'] = '$$$'.join(play_url)
            # 保存解析所需的 id 映射，供 playerContent 使用
            vod['_player_source'] = {src: code2id.get(src) for src in play_from}
            vod['_vod_id'] = vid
            return {'list': [vod]}
        except Exception as e:
            print(f"Error in detailContent: {e}")
            import traceback
            traceback.print_exc()
            return {'list': []}

    def searchContent(self, key, quick, pg="1"):
        try:
            # 真实搜索接口：searchList，参数 keywords / type_id / page
            data = self._api('searchList', {'keywords': key, 'type_id': '0', 'page': pg})
            if not data:
                return {'list': []}
            rows = data.get('search_list') or data.get('recommend_list') or []
            videos = []
            seen = set()
            for v in rows:
                item = self._vod_item(v)
                if item['vod_id'] and item['vod_name'] and item['vod_id'] not in seen:
                    seen.add(item['vod_id'])
                    videos.append(item)
            return {'list': videos}
        except Exception as e:
            print(f"Error in searchContent: {e}")
            import traceback
            traceback.print_exc()
            return {'list': []}

    def searchSuggestions(self, keyword):
        """
        搜索联想（实时补全）。参数 keyword。
        与 searchContent 共用同一套解密；返回建议名称列表。
        """
        try:
            data = self._api('searchSuggestions', {'keyword': keyword})
            if not data:
                return []
            out = []
            for it in data.get('list', []) or []:
                if it.get('vod_name'):
                    out.append(it['vod_name'])
            return out
        except Exception as e:
            print(f"Error in searchSuggestions: {e}")
            return []

    def playerContent(self, flag, id, vipFlags):
        """
        detailContent 中每集被编码为 "name$psid@epidx@vodid"，
        框架传入的 id 形态为 "psid@epidx@vodid"（不含名称）。
        经 vodParse 接口用 (vod_id, player_source_id, episode_index) 换取真实 play_url。
        """
        try:
            if not id or id.count('@') < 2:
                return {'parse': 0, 'url': '', 'header': {}, 'playUrl': ''}
            psid, ep_idx, vid = id.split('@', 2)
            data = self._api('vodParse', {
                'vod_id': vid,
                'player_source_id': psid,
                'episode_index': ep_idx,
            })
            if data and data.get('play_url'):
                return {
                    'parse': 1 if data['play_url'].startswith('http') else 0,
                    'url': data['play_url'],
                    'header': self.play_header,
                    'playUrl': '',
                }
            return {'parse': 0, 'url': '', 'header': {}, 'playUrl': ''}
        except Exception as e:
            print(f"Error in playerContent: {e}")
            return {'parse': 0, 'url': '', 'header': {}, 'playUrl': ''}

    def fetch(self, url):
        try:
            response = requests.get(url, headers=self.header, timeout=self.timeout)
            response.encoding = 'utf-8'
            return response.text if response.status_code == 200 else None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def get_id_from_href(self, href):
        if not href:
            return href
        m = re.search(r'[?&]id=(\d+)', href)
        if m:
            return m.group(1)
        m = re.search(r'/id/(\d+)', href)
        if m:
            return m.group(1)
        return href
