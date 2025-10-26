# coding=utf-8
# !/usr/bin/python
import sys, re
import base64
import hashlib
import requests
from typing import Tuple
from base.spider import Spider
from datetime import datetime, timedelta
from urllib.parse import quote, unquote
from urllib3.util.retry import Retry
sys.path.append('..')

# 搜索用户名，关键词格式为“类别+空格+关键词”
# 类别在标签上已注明，比如“女主播g”，则搜索类别为“g”
# 搜索“g per”，则在“女主播”中搜索“per”, 关键词不区分大小写，但至少3位，否则空结果

class Spider(Spider):

    def init(self, extend="{}"):
        origin = 'https://zh.stripchat.com'
        self.host = origin
        self.headers = {
            'Origin': origin,
            'Referer': f"{origin}/",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0'
        }
        self.stripchat_key = self.decode_key_compact()
        # 缓存字典
        self._hash_cache = {}
        self.create_session_with_retry()

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    def homeContent(self, filter):
        CLASSES = [{'type_name': '女主播g', 'type_id': 'girls'}, {'type_name': '情侣c', 'type_id': 'couples'}, {'type_name': '男主播m', 'type_id': 'men'}, {'type_name': '跨性别t', 'type_id': 'trans'}]
        VALUE = ({'n': '中国', 'v': 'tagLanguageChinese'}, {'n': '亚洲', 'v': 'ethnicityAsian'}, {'n': '白人', 'v': 'ethnicityWhite'}, {'n': '拉丁', 'v': 'ethnicityLatino'}, {'n': '混血', 'v': 'ethnicityMultiracial'}, {'n': '印度', 'v': 'ethnicityIndian'}, {'n': '阿拉伯', 'v': 'ethnicityMiddleEastern'}, {'n': '黑人', 'v': 'ethnicityEbony'})
        VALUE_MEN = ({'n': '情侣', 'v': 'sexGayCouples'}, {'n': '直男', 'v': 'orientationStraight'})
        TIDS = ('girls', 'couples', 'men', 'trans')
        filters = {
            tid: [{'key': 'tag', 'value': VALUE_MEN + VALUE if tid == 'men' else VALUE}]
            for tid in TIDS
        }
        return {
            'class': CLASSES,
            'filters': filters
        }

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        limit = 60
        offset = limit * (int(pg) - 1)
        url = f"{self.host}/api/front/models?improveTs=false&removeShows=false&limit={limit}&offset={offset}&primaryTag={tid}&sortBy=stripRanking&rcmGrp=A&rbCnGr=true&prxCnGr=false&nic=false"
        if 'tag' in extend:
            url += "&filterGroupTags=%5B%5B%22" + extend['tag'] + "%22%5D%5D"
        rsp = self.fetch(url).json()
        videos = [
            {
                "vod_id": str(vod['username']).strip(),
                "vod_name": f"{self.country_code_to_flag(str(vod['country']).strip())}{str(vod['username']).strip()}",
                "vod_pic": f"https://img.doppiocdn.net/thumbs/{vod['snapshotTimestamp']}/{vod['id']}",
                "vod_remarks": "" if vod.get('status') == "public" else "🎫"
            }
            for vod in rsp.get('models', [])
        ]
        total = int(rsp.get('filteredCount', 0))
        return {
            "list": videos,
            "page": pg,
            "pagecount": (total + limit - 1) // limit,
            "limit": limit,
            "total": total
        }

    def detailContent(self, array):
        username = array[0]
        rsp = self.fetch(f"{self.host}/api/front/v2/models/username/{username}/cam").json()
        info = rsp['cam']
        user = rsp['user']['user']
        id = str(user['id'])
        country = str(user['country']).strip()
        isLive = "" if user['isLive'] else " 已下播"
        flag = self.country_code_to_flag(country)
        remark, startAt = '', ''
        if show := info.get('show'):
            startAt = show.get('createdAt')
        elif show := info.get('groupShowAnnouncement'):
            startAt = show.get('startAt')
        if startAt:
            BJtime = (datetime.strptime(startAt, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8)).strftime("%m月%d日 %H:%M")
            remark = f"🎫 始于 {BJtime}"
        vod = {
            "vod_id": id,
            "vod_name": str(info['topic']).strip(), 
            "vod_pic": str(user['avatarUrl']),
            "vod_director": f"{flag}{username}{isLive}",
            "vod_remarks": remark,
            'vod_play_from': '老僧酿酒',
            'vod_play_url': f"{id}${id}"
        }
        return {'list': [vod]}

    def process_key(self, key: str) -> Tuple[str, str]:
        tags = {'G': 'girls', 'C': 'couples', 'M': 'men', 'T': 'trans'}
        parts = key.split(maxsplit=1)  # 仅分割第一个空格
        if len(parts) > 1 and (tag := tags.get(parts[0].upper())):
            return tag, parts[1].strip()
        return 'girls', key.strip()

    def searchContent(self, key, quick, pg="1"):
        result = {}
        if int(pg) > 1:
            return result
        tag, key = self.process_key(key)
        url = f"{self.host}/api/front/v4/models/search/group/username?query={key}&limit=900&primaryTag={tag}"
        rsp = self.fetch(url).json()
        result['list'] = [
            {
                "vod_id": str(user['username']).strip(),
                "vod_name": f"{self.country_code_to_flag(str(user['country']).strip())}{user['username']}",
                "vod_pic": f"https://img.doppiocdn.net/thumbs/{user['snapshotTimestamp']}/{user['id']}",
                "vod_remarks": "" if user['status'] == "public" else "🎫"
            }
            for user in rsp.get('models', []) 
            if user['isLive']  # 过滤条件
        ]
        return result

    def playerContent(self, flag, id, vipFlags):
        url = f"https://edge-hls.doppiocdn.net/hls/{id}/master/{id}_auto.m3u8?playlistType=lowLatency"
        rsp = self.fetch(url)
        lines = rsp.text.strip().split('\n')
        psch, pkey = '', ''
        url = []
        for i, line in enumerate(lines):
            if line.startswith('#EXT-X-MOUFLON:'):
                if parts := line.split(':'):
                    if len(parts) >= 4:
                        psch, pkey = parts[2], parts[3]
            if '#EXT-X-STREAM-INF' in line:
                name_start = line.find('NAME="') + 6
                name_end = line.find('"', name_start)
                qn = line[name_start:name_end]
                # URL在下一行
                url_base = lines[i + 1]
                # 组合最终的URL，并加上psch和pkey参数
                full_url = f"{url_base}&psch={psch}&pkey={pkey}"
                proxy_url = f"{self.getProxyUrl()}&url={quote(full_url)}"
                # 将画质和URL添加到列表中
                url.extend([qn, proxy_url])
        return {
            "url": url,
            "parse": '0',
            "contentType": '',
            "header": self.headers
        }

    def localProxy(self, param):
        url = unquote(param['url'])
        data = self.fetch(url)
        if data.status_code == 403:
            data = self.fetch(re.sub(r'\d+p\d*\.m3u8', '160p_blurred.m3u8', url))
        if data.status_code != 200:
            return [404, "text/plain", ""]
        data = data.text
        if "#EXT-X-MOUFLON:FILE" in data:
            data = self.process_m3u8_content_v2(data)
        return [200, "application/vnd.apple.mpegur", data]

    def process_m3u8_content_v2(self, m3u8_content):
        lines = m3u8_content.strip().split('\n')
        for i, line in enumerate(lines):
            if (line.startswith('#EXT-X-MOUFLON:FILE:') and 'media.mp4' in lines[i + 1]):
                encrypted_data = line.split(':', 2)[2].strip()
                try:
                    decrypted_data = self.decrypt(encrypted_data, self.stripchat_key)
                except Exception as e:
                    decrypted_data = self.decrypt(encrypted_data, "Zokee2OhPh9kugh4")
                lines[i + 1] = lines[i + 1].replace('media.mp4', decrypted_data)
        return '\n'.join(lines)

    def country_code_to_flag(self, country_code):
        if len(country_code) != 2 or not country_code.isalpha():
            return country_code
        flag_emoji = ''.join([chr(ord(c.upper()) - ord('A') + 0x1F1E6) for c in country_code])
        return flag_emoji

    def decode_key_compact(self):
        base64_str = "NTEgNzUgNjUgNjEgNmUgMzQgNjMgNjEgNjkgMzkgNjIgNmYgNGEgNjEgMzUgNjE="
        decoded = base64.b64decode(base64_str).decode('utf-8')
        key_bytes = bytes(int(hex_str, 16) for hex_str in decoded.split(" "))
        return key_bytes.decode('utf-8')

    def compute_hash(self, key: str) -> bytes:
        """计算并缓存SHA-256哈希"""
        if key not in self._hash_cache:
            sha256 = hashlib.sha256()
            sha256.update(key.encode('utf-8'))
            self._hash_cache[key] = sha256.digest()
        return self._hash_cache[key]

    def decrypt(self, encrypted_b64: str, key: str) -> str:
        # 修复Base64填充
        padding = len(encrypted_b64) % 4
        if padding:
            encrypted_b64 += '=' * (4 - padding)
    
        # 计算哈希并解密
        hash_bytes = self.compute_hash(key)
        encrypted_data = base64.b64decode(encrypted_b64)

        # 异或解密
        decrypted_bytes = bytearray()
        for i, cipher_byte in enumerate(encrypted_data):
            key_byte = hash_bytes[i % len(hash_bytes)]
            decrypted_bytes.append(cipher_byte ^ key_byte)
        return decrypted_bytes.decode('utf-8')

    def create_session_with_retry(self):
        self.session = requests.Session()
        retry_strategy = Retry(
            total = 3,
            backoff_factor = 0.3,
            status_forcelist = [429, 500, 502, 503, 504]  # 需要重试的状态码
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def fetch(self, url):
        return self.session.get(url, headers=self.headers, timeout=10)
