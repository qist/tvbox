# -*- coding: utf-8 -*-
# by @Qist
"""
ITalkBB TV - 海外华人影视
"""
import time
import uuid
import requests
from base.spider import Spider


class Spider(Spider):
    def getName(self):
        return 'ITalkBB TV'

    def init(self, extend=""):
        self._login()

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    def __init__(self):
        self.name = 'ITalkBB TV'
        self.host = 'https://www.italkbbtv.com'
        self.api = 'https://api.italkbbtv.com/classictv'
        self.token = ''
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
            'Referer': 'https://www.italkbbtv.com/',
            'Origin': 'https://www.italkbbtv.com',
        }
        self.timeout = 20
        self._token = ''
        self._expire = 0
        self._device_id = str(uuid.uuid4())

    def _login(self):
        now = int(time.time() * 1000)
        if self._token and now < self._expire - 60000:
            return
        data = {
            'login_type': 'password', 'grant_type': 'tv_login_in',
            'device_id': self._device_id,
            'login_name': f'{self._device_id}@web.visitor.italkbb.com',
            'password': 'visitor_secret',
            'device_type': 'web', 'device_model': 'Chrome148', 'app_version': '305013',
        }
        try:
            r = requests.post('https://api.italkbbtv.com/auth/v1/token', headers=self.header, data=data, timeout=self.timeout)
            if r.status_code == 200:
                self._set_token(r.json().get('access', {}))
        except:
            pass

    def _set_token(self, acc):
        self._token = acc.get('token', '')
        self._expire = acc.get('expire_time', 0)
        if self._token:
            self.header['Authorization'] = 'Bearer ' + self._token

        self.cats = {
            'drama': ('62ac4df64beefe53586474ff', '62c670dc1dca2d424404499c'),
            'movie': ('62ac4e644beefe535864785c', '62ac4ef36e0b5a13ed291544'),
            'variety': ('62ac4e1f4beefe5358647642', '62ce7417c7daaa4a5d3fea14'),
            'cartoon': ('62ac4e6a4beefe53586478a5', '62ac4e6e4beefe53586478ca'),
            'shorts': ('66a9e3e49f7e8378f2152312', '66b1d25cf2dde82c215f9b59'),
        }
        self.class_names = '电视剧&电影&综艺&动画&短剧&直播频道'.split('&')
        self.class_urls = 'drama&movie&variety&cartoon&shorts&live'.split('&')

    def _api_get(self, path, params=None):
        self._login()
        try:
            r = requests.get(self.api + path, headers=self.header, params=params, timeout=self.timeout)
            if r.status_code == 200:
                return r.json()
        except:
            pass
        return None

    def _get_live_stream(self, ch_id):
        self._login()
        try:
            r = requests.get('https://api.italkbbtv.com/playauth/v1/live', headers=self.header, params={'series_id': ch_id, 'hl': 'zh_CN'}, timeout=self.timeout)
            if r.status_code == 200:
                return r.json().get('manifest', '')
        except:
            pass
        return ''

    def _make_vod(self, s):
        sid = s.get('id', '')
        name = s.get('name', '')
        images = s.get('images', {}) or {}
        poster = (images.get('poster') or [''])[0] if images.get('poster') else ''
        landscape = (images.get('landscape') or [''])[0] if images.get('landscape') else ''
        pic = poster or landscape
        ep_count = s.get('episode_count', 0) or 0
        latest = s.get('latest_episode_shortname', '') or s.get('latest_episode_name', '')
        if ep_count and ep_count > 1:
            remarks = f'更新至{latest}' if latest else f'{ep_count}集'
        elif ep_count == 1:
            remarks = '全1集'
        else:
            remarks = latest
        return {'vod_id': sid, 'vod_name': name, 'vod_pic': pic, 'vod_remarks': remarks}

    def homeContent(self, filter):
        result = {'class': [], 'list': []}
        for name, cid in zip(self.class_names, self.class_urls):
            result['class'].append({'type_name': name, 'type_id': cid})
        data = self._api_get('/vod/v1/series', {'root_id': self.cats['drama'][0], 'category_id': self.cats['drama'][1], 'page': 1, 'size': 24, 'hl': 'zh_CN'})
        if data:
            result['list'] = [self._make_vod(s) for s in data.get('series', [])]
        return result

    def homeVideoContent(self):
        return {}

    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg)
        result = {'list': [], 'page': pg, 'pagecount': 999, 'limit': 24, 'total': 0}

        # 直播频道
        if tid == 'live':
            data = self._api_get('/live/v1/lives', {'root_id': '62ac4e2e4beefe535864769d', 'category_id': '62ac4e314beefe53586476c2', 'page': 1, 'size': 100, 'hl': 'zh_CN'})
            if data:
                vods = []
                for ch in data.get('lives', []):
                    ch_id = ch.get('id', '')
                    ch_name = ch.get('name', '')
                    images = ch.get('images', {}) or {}
                    icon = (images.get('icon') or [''])[0] if images.get('icon') else ''
                    vods.append({'vod_id': 'live@' + ch_id, 'vod_name': ch_name, 'vod_pic': icon, 'vod_remarks': '直播'})
                result['list'] = vods
                result['total'] = len(vods)
                result['pagecount'] = 1
            return result

        # 点播
        cat = self.cats.get(tid)
        if not cat:
            return result
        root_id, cat_id = cat
        data = self._api_get('/vod/v1/series', {'root_id': root_id, 'category_id': cat_id, 'page': pg, 'size': 24, 'hl': 'zh_CN'})
        if data:
            result['list'] = [self._make_vod(s) for s in data.get('series', [])]
            result['total'] = data.get('total', 0)
            result['pagecount'] = (result['total'] + 23) // 24
        return result

    def detailContent(self, ids):
        if not ids or not ids[0]:
            return {'list': []}
        vid = ids[0]

        # 直播频道
        if vid.startswith('live@'):
            ch_id = vid.replace('live@', '')
            stream = self._get_live_stream(ch_id)
            return {'list': [{
                'vod_id': vid, 'vod_name': ch_id, 'vod_pic': '',
                'vod_play_from': 'ITalkBB直播',
                'vod_play_url': f'直播${stream}' if stream else '',
            }]}

        # 点播
        series_data = self._api_get(f'/vod/v1/series/{vid}', {'hl': 'zh_CN'})
        s = (series_data or {}).get('series', {})
        name = s.get('name', '')
        desc = s.get('description', '')
        images = s.get('images', {}) or {}
        pic = (images.get('poster') or [''])[0] if images.get('poster') else ''
        stars = s.get('stars', {}) or {}
        actor = '/'.join([a.get('name', '') for a in (stars.get('actor') or [])[:5]])
        director = '/'.join([d.get('name', '') for d in (stars.get('director') or [])])

        eps_data = self._api_get(f'/vod/v1/series/{vid}/episodes', {'hl': 'zh_CN'})
        eps = eps_data if isinstance(eps_data, list) else (eps_data or {}).get('episodes', [])

        play_urls = []
        for ep in eps:
            ep_name = ep.get('shortname', '') or ep.get('name', '') or ep.get('id', '')[-4:]
            ep_id = ep.get('id', '')
            play_urls.append(f'{ep_name}$play@{vid}@{ep_id}')

        if not play_urls:
            play_urls.append(f'播放$play@{vid}@')

        return {'list': [{
            'vod_id': vid, 'vod_name': name, 'vod_pic': pic,
            'vod_remarks': '', 'vod_year': '', 'type_name': '',
            'vod_content': desc, 'vod_actor': actor, 'vod_director': director,
            'vod_play_from': 'ITalkBB', 'vod_play_url': '#'.join(play_urls),
        }]}

    def searchContent(self, key, quick, pg="1"):
        result = {'list': []}
        for tid in self.cats:
            cat = self.cats[tid]
            data = self._api_get('/vod/v1/series', {'root_id': cat[0], 'category_id': cat[1], 'page': 1, 'size': 50, 'hl': 'zh_CN'})
            if data:
                for s in data.get('series', []):
                    if key in s.get('name', ''):
                        result['list'].append(self._make_vod(s))
        seen = set()
        unique = []
        for v in result['list']:
            if v['vod_id'] not in seen:
                seen.add(v['vod_id'])
                unique.append(v)
        result['list'] = unique
        return result

    def playerContent(self, flag, id, vipFlags):
        h = {'User-Agent': self.header['User-Agent']}
        # 直播: 直接用m3u8地址
        if id.startswith('live@'):
            m3u8 = id.replace('live@', '')
            if m3u8.startswith('http'):
                return {'parse': 0, 'url': m3u8, 'header': h, 'playUrl': ''}
            stream = self._get_live_stream(m3u8)
            return {'parse': 0, 'url': stream, 'header': h, 'playUrl': ''}
        # m3u8直链
        if id.startswith('http'):
            return {'parse': 0, 'url': id, 'header': h, 'playUrl': ''}
        # 点播
        parts = id.split('@')
        route = parts[0] if len(parts) > 1 else 'play'
        sid = parts[1] if len(parts) > 1 else ''
        eid = parts[2] if len(parts) > 2 else ''
        url = f'{self.host}/{route}/{sid}'
        if eid:
            url += f'?ep={eid}'
        return {'parse': 1, 'url': url, 'header': self.header, 'playUrl': ''}

    def fetch(self, url):
        try:
            resp = requests.get(url, headers=self.header, timeout=self.timeout)
            resp.encoding = 'utf-8'
            if resp.status_code == 200:
                return resp.text
            return None
        except:
            return None

    def localProxy(self, param):
        return None
