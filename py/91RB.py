#author Kyle
import re, sys, time, urllib.parse
sys.path.append('..')
from base.spider import Spider as BaseSpider
class Spider(BaseSpider):
    def __init__(self):
        super().__init__(); self.base = 'https://www.91rb.com'; self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36', 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8', 'Referer': self.base + '/'}
    def getName(self): return '91热爆'
    def init(self, extend=""): self.extend = extend or ''; return {'class': 'movie'}
    def isVideoFormat(self, url): return bool(re.search(r'\.(m3u8|mp4)(\?|$)', url))
    def manualVideoCheck(self): return False
    def destroy(self): pass
    def homeContent(self, filter): return {'class': [{'type_name': '最新上传', 'type_id': 'latest-updates'}, {'type_name': '热门视频', 'type_id': 'most-popular'}, {'type_name': '收藏最多', 'type_id': 'most-favourited'}, {'type_name': '日本AV', 'type_id': 'tags/av2/'}, {'type_name': 'jav', 'type_id': 'tags/jav/'}, {'type_name': '韩国', 'type_id': 'tags/20c3f16d021b069ce3af1da50b15bd83/'}]}
    def homeVideoContent(self):
        try: return self._listPage(self._buildListUrl('latest-updates', '1'))
        except Exception as e: self.log(f'homeVideoContent error: {e}'); return {'list': []}
    def categoryContent(self, tid, pg, filter, extend):
        try: return self._listPage(self._buildListUrl(tid, pg), page=pg)
        except Exception as e: self.log(f'categoryContent error: {e}'); return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 48, 'total': 0}
    def detailContent(self, ids):
        vid = self._ensure_id(ids[0]); detail_url = f"{self.base}/videos/{vid}/"; name = f'视频 {vid}'; pic = ''
        try:
            r = self.fetch(detail_url, headers=self.headers, timeout=10, allow_redirects=True)
            if r and hasattr(r, 'text'):
                doc = self.html(r.text)
                if doc:
                    name = ''.join(doc.xpath('//h1//text()')).strip() or name
                    ogs = doc.xpath('//meta[@property="og:image"]/@content'); tws = doc.xpath('//meta[@name="twitter:image"]/@content')
                    pic = ogs[0].strip() if ogs else (tws[0].strip() if tws else '')
                    if pic: pic = self._abs_url(pic)
        except Exception as e: self.log(f'detailContent fetch error: {e}')
        if not pic: pic = self._cover_fallback(vid)
        vod = {'vod_id': str(vid), 'vod_name': name, 'vod_pic': pic, 'type_name': '', 'vod_year': '', 'vod_remarks': '', 'vod_content': '', 'vod_play_from': '91RB', 'vod_play_url': f'正片${vid}'}
        return {'list': [vod]}
    def searchContent(self, key, quick, pg="1"):
        key_enc = urllib.parse.quote(key); url = f"{self.base}/search/{key_enc}/"
        if pg != '1': url = url.rstrip('/') + f'/{pg}/'
        try: return self._listPage(url, page=pg)
        except Exception as e: self.log(f'searchContent error: {e}'); return {'list': [], 'page': pg, 'pagecount': 1, 'total': 0}
    def playerContent(self, flag, id, vipFlags):
        vid = self._ensure_id(id); group = int(vid) - (int(vid) % 1000)
        m3u8 = f"https://91rbnet.gslb-al.com/hls/contents/videos/{group}/{vid}/{vid}.mp4/index.m3u8"
        try:
            r = self.fetch(m3u8, headers=self.headers, timeout=5, allow_redirects=True, verify=True, stream=True)
            if r.status_code >= 400: self.log(f'm3u8 head status={r.status_code}, fallback to direct anyway')
        except Exception as e: self.log(f'playerContent HEAD error: {e}')
        return {'parse': 0, 'playUrl': '', 'url': m3u8, 'header': self.headers}
    def localProxy(self, param): return None
    def _buildListUrl(self, tid, pg):
        path = tid.strip('/') or 'latest-updates'; page_suffix = f"/{pg}/" if str(pg) != '1' else '/'
        if path.startswith('categories') or path in ['latest-updates', 'most-popular', 'most-favourited']: return f"{self.base}/{path}{page_suffix}"
        return f"{self.base}/{path}{page_suffix}"
    def _abs_url(self, url):
        if not url: return url
        u = url.strip()
        return 'https:' + u if u.startswith('//') else (self.base + u if u.startswith('/') else u)
    def _parse_srcset_first(self, srcset):
        if not srcset: return ''
        return srcset.split(',')[0].strip().split(' ')[0]
    def _cover_fallback(self, vid):
        try: iv = int(vid); group = iv - (iv % 1000); return f'https://rimg.iomycdn.com/videos_screenshots/{group}/{iv}/preview.jpg'
        except Exception: return ''
    def _listPage(self, url, page='1'):
        doc = self.html(self.fetch(url, headers=self.headers, timeout=10).text)
        if doc is None: return {'list': [], 'page': page, 'pagecount': 1, 'total': 0}
        nodes, videos, seen = doc.xpath('//main//a[contains(@href, "/videos/")]'), [], set()
        for a in nodes:
            href = a.get('href') or ''; m = re.search(r'/videos/(\d+)/', href)
            if not m or '/login' in href: continue
            vid = m.group(1);
            if vid in seen: continue
            seen.add(vid); title = ''; img = a.xpath('.//img')
            if img:
                im = img[0]; title = (im.get('alt') or '').strip()
                pic = (im.get('src') or im.get('data-src') or im.get('data-original') or '').strip()
                if not pic: pic = self._parse_srcset_first(im.get('data-srcset') or im.get('srcset') or '')
                pic = self._abs_url(pic)
            else: title = (a.text or '').strip(); pic = ''
            title = title or f'视频 {vid}'
            if not pic or pic.startswith('data:'): pic = self._cover_fallback(vid)
            videos.append({'vod_id': vid, 'vod_name': title, 'vod_pic': pic, 'vod_remarks': ''})
        return {'list': videos, 'page': str(page), 'pagecount': 9999, 'limit': 48, 'total': 0}
    def _ensure_id(self, s):
        m = re.search(r'(\d+)', str(s)); return m.group(1) if m else str(s)