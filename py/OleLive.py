# -*- coding: utf-8 -*-
# by @Qist
"""
欧乐影院 - 海外华人影视 内容均从互联网收集而来 仅供交流学习使用 严禁用于商业用途 请于24小时内删除
"""
import base64
import hashlib
import json
import time
import urllib.parse
from datetime import datetime

import requests
from base.spider import Spider

try:
    from Crypto.Cipher import AES
except ImportError:
    AES = None


class Spider(Spider):
    def getName(self):
        return '欧乐影院'

    def init(self, extend=""):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    def __init__(self):
        self.name = '欧乐影院'
        self.host = 'https://olelive.com'
        self.api = 'https://api.olelive.com'
        self.image_base = 'https://static.olelive.com'
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
            'Referer': 'https://olelive.com/',
            'Origin': 'https://olelive.com',
        }
        self.timeout = 20
        self._types = []

    def _sign(self):
        """生成接口签名 _vv"""
        ts = str(int(time.time()))
        r = [[], [], [], []]
        for ch in ts:
            b = bin(ord(ch))[2:]
            r[0].append(b[2:3])
            r[1].append(b[3:4])
            r[2].append(b[4:5])
            r[3].append(b[5:])
        a = []
        for i in range(4):
            hx = hex(int(''.join(r[i]) or '0', 2))[2:]
            if len(hx) == 2:
                hx = '0' + hx
            elif len(hx) == 1:
                hx = '00' + hx
            elif len(hx) == 0:
                hx = '000'
            a.append(hx)
        n = hashlib.md5(ts.encode()).hexdigest()
        return n[:3] + a[0] + n[6:11] + a[1] + n[14:19] + a[2] + n[22:27] + a[3] + n[30:]

    def _decrypt(self, data):
        if AES is None:
            return data
        date_str = datetime.now().strftime('%Y-%m-%d')
        key = hashlib.md5(date_str.encode()).hexdigest()[8:24]
        cipher = AES.new(key.encode(), AES.MODE_CBC, iv=key.encode())
        plain = cipher.decrypt(base64.b64decode(data))
        return plain.rstrip(b'\x00').decode('utf-8', 'ignore')

    def _api_get(self, path, params=None):
        p = dict(params or {})
        p['_vv'] = self._sign()
        try:
            r = requests.get(self.api + path, headers=self.header, params=p, timeout=self.timeout)
            if r.status_code == 200:
                js = r.json()
                if js.get('code') == 0:
                    d = js.get('data')
                    if isinstance(d, str):
                        try:
                            return json.loads(d)
                        except:
                            try:
                                return json.loads(self._decrypt(d))
                            except:
                                return d
                    return d
        except:
            pass
        return None

    def _load_types(self):
        if self._types:
            return
        data = self._api_get('/v1/pub/vod/list/type')
        if not data:
            return
        for item in data:
            # 屏蔽直播/非点播分类
            if item.get('typeEn') == 'chengren':
                continue
            if '直播' in item.get('typeName', '') or 'live' in (item.get('typeEn') or '').lower():
                continue
            children = []
            for c in (item.get('children') or []):
                if '直播' in c.get('typeName', '') or 'live' in (c.get('typeEn') or '').lower():
                    continue
                children.append({'type_name': c.get('typeName', ''), 'type_id': str(c.get('typeId'))})
            self._types.append({
                'type_name': item.get('typeName', ''),
                'type_id': str(item.get('typeId')),
                'children': children,
                'area': item.get('area') or [],
                'year': item.get('year') or [],
            })

    def _get_filters(self):
        """每个主分类的筛选维度：类型/地区/年代"""
        filters = {}
        for t in self._types:
            out = []
            # 类型 = 子分类
            items = [{'n': '全部', 'v': ''}]
            for c in (t.get('children') or []):
                items.append({'n': c['type_name'], 'v': c['type_id']})
            if len(items) > 1:
                out.append({'key': 'class', 'name': '类型', 'value': items})
            # 地区
            items = [{'n': '全部', 'v': ''}]
            for a in t.get('area') or []:
                items.append({'n': a, 'v': a})
            if len(items) > 1:
                out.append({'key': 'area', 'name': '地区', 'value': items})
            # 年代
            items = [{'n': '全部', 'v': ''}]
            for y in t.get('year') or []:
                items.append({'n': y, 'v': y})
            if len(items) > 1:
                out.append({'key': 'year', 'name': '年代', 'value': items})
            if out:
                filters[t['type_id']] = out
        return filters

    def _pic(self, s):
        pic = s.get('picThumb') or s.get('pic') or ''
        if not pic:
            return ''
        if pic.startswith('http'):
            return pic
        if pic.startswith('/'):
            return self.image_base + pic
        return self.image_base + '/' + pic

    def _make_vod(self, s):
        return {
            'vod_id': str(s.get('id', '')),
            'vod_name': s.get('name', ''),
            'vod_pic': self._pic(s),
            'vod_remarks': s.get('remarks', ''),
        }

    def homeContent(self, filter):
        result = {'class': [], 'list': []}
        self._load_types()
        for t in self._types:
            result['class'].append({'type_name': t['type_name'], 'type_id': t['type_id']})
        if filter:
            result['filters'] = self._get_filters()
        data = self._api_get('/v1/pub/index/vod/data/2')
        if data:
            result['list'] = [self._make_vod(s) for s in data.get('list', [])]
        return result

    def homeVideoContent(self):
        return {}

    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg)
        result = {'list': [], 'page': pg, 'pagecount': 999, 'limit': 24, 'total': 0}
        extend = extend or {}
        typeId = extend.get('class') or '0'
        area = extend.get('area') or '0'
        year = extend.get('year') or '0'
        data = self._api_get(f'/v1/pub/vod/list/1/3/0/{area}/{tid}/{typeId}/{year}/update/{pg}/24')
        if data:
            result['list'] = [self._make_vod(s) for s in data.get('list', [])]
            result['total'] = data.get('total', 0)
            result['pagecount'] = (result['total'] + 23) // 24
        return result

    def detailContent(self, ids):
        if not ids or not ids[0]:
            return {'list': []}
        vid = ids[0]
        data = self._api_get(f'/v1/pub/vod/detail/{vid}/1')
        if not data:
            return {'list': []}
        hd, uhd = [], []
        for u in data.get('urls') or []:
            ep_name = u.get('title', '') or f"第{u.get('index', '')}集"
            url = u.get('url', '')
            if url:
                hd.append(f'{ep_name}${url}')
            if u.get('vip_urls'):
                vip_url = u['vip_urls'][0].get('url', '')
                if vip_url:
                    uhd.append(f'{ep_name}${vip_url}')
        if not hd:
            return {'list': []}
        play_from = ['欧乐高清']
        play_url = ['#'.join(hd)]
        # 超清有多少显示多少
        if uhd:
            play_from.append('欧乐超清')
            play_url.append('#'.join(uhd))
        return {'list': [{
            'vod_id': vid,
            'vod_name': data.get('name', ''),
            'vod_pic': self._pic(data),
            'vod_remarks': data.get('remarks', ''),
            'vod_year': str(data.get('year', '')),
            'vod_area': data.get('area', ''),
            'type_name': data.get('typeId1Name', ''),
            'vod_actor': data.get('actor', ''),
            'vod_director': data.get('director', ''),
            'vod_content': data.get('content', '') or data.get('blurb', ''),
            'vod_play_from': '$$$'.join(play_from),
            'vod_play_url': '$$$'.join(play_url),
        }]}

    def searchContent(self, key, quick, pg="1"):
        result = {'list': [], 'page': pg}
        kw = urllib.parse.quote(str(key))
        data = self._api_get(f'/v1/pub/index/search/{kw}/vod/0/{pg}/24')
        if data:
            for g in data.get('data') or []:
                if g.get('type') == 'vod':
                    result['list'].extend(self._make_vod(s) for s in g.get('list') or [])
        return result

    def playerContent(self, flag, id, vipFlags):
        h = {'User-Agent': self.header['User-Agent'], 'Referer': self.host + '/'}
        return {'parse': 0, 'url': id, 'header': h, 'playUrl': ''}

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
