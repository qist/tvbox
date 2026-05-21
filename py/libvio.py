# -*- coding: utf-8 -*-
# by @Qist
"""
LibVio (libvio.run) - 免费在线观影
"""
import re
import json
import requests
from urllib.parse import quote
from base.spider import Spider


class Spider(Spider):
    def getName(self):
        return "LibVio"

    def init(self, extend=""):
        self.host = 'https://www.libvio.run'
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': self.host + '/',
            'Origin': self.host,
        }
        self.timeout = 20
        self.session = requests.Session()
        self.session.headers.update(self.header)

    def _safe_get(self, url, max_retries=3):
        for attempt in range(max_retries):
            try:
                resp = self.session.get(url, timeout=self.timeout, verify=False)
                resp.encoding = 'utf-8'
                return resp
            except:
                import time
                time.sleep(1)
        return None

    def _parse_videos(self, html):
        videos = []
        seen = set()
        pattern = re.compile(
            r'href="/detail/(\d+)\.html"[^>]+title="([^"]*)"[^>]+data-original="([^"]*)"[^>]*>.*?'
            r'<span class="pic-text[^"]*">([^<]*)</span>.*?'
            r'<span class="pic-tag[^"]*">([^<]*)</span>',
            re.DOTALL
        )
        for m in pattern.finditer(html):
            vid = m.group(1)
            if vid in seen:
                continue
            seen.add(vid)
            vod_name = m.group(2)
            vod_pic = m.group(3)
            vod_remarks = m.group(4).strip()
            score = m.group(5).strip()
            if score and score != '0.0':
                vod_remarks = vod_remarks + '/' + score if vod_remarks else score
            videos.append({
                'vod_id': vid,
                'vod_name': vod_name,
                'vod_pic': vod_pic,
                'vod_remarks': vod_remarks,
            })
        return videos

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    def homeContent(self, filter):
        try:
            result = {'class': [], 'list': []}
            classes = [
                {'type_name': '电影', 'type_id': '1'},
                {'type_name': '剧集', 'type_id': '2'},
                {'type_name': '国剧', 'type_id': '13'},
                {'type_name': '动作片', 'type_id': '6'},
                {'type_name': '喜剧片', 'type_id': '7'},
                {'type_name': '爱情片', 'type_id': '8'},
                {'type_name': '科幻片', 'type_id': '9'},
                {'type_name': '恐怖片', 'type_id': '10'},
                {'type_name': '剧情片', 'type_id': '11'},
                {'type_name': '战争片', 'type_id': '12'},
                {'type_name': '动画片', 'type_id': '23'},
                {'type_name': '纪录片', 'type_id': '21'},
                {'type_name': '港台剧', 'type_id': '14'},
                {'type_name': '日韩剧', 'type_id': '15'},
                {'type_name': '欧美剧', 'type_id': '16'},
                {'type_name': '泰国剧', 'type_id': '24'},
                {'type_name': '综艺', 'type_id': '3'},
                {'type_name': '番剧', 'type_id': '4'},
            ]
            result['class'] = classes
            
            # 获取首页推荐视频
            resp = self._safe_get(self.host + '/')
            if resp and resp.status_code == 200:
                result['list'] = self._parse_videos(resp.text)[:10]
            
            filter_cfg = {
                '1': [
                    {"key": "area", "name": "地区", "value": [
                        {"n": "全部", "v": ""}, {"n": "中国大陆", "v": "中国大陆"},
                        {"n": "中国香港", "v": "中国香港"}, {"n": "中国台湾", "v": "中国台湾"},
                        {"n": "美国", "v": "美国"}, {"n": "韩国", "v": "韩国"},
                        {"n": "日本", "v": "日本"}, {"n": "泰国", "v": "泰国"},
                        {"n": "英国", "v": "英国"}, {"n": "其他", "v": "其他"},
                    ]},
                    {"key": "by", "name": "排序", "value": [
                        {"n": "最新", "v": "time"}, {"n": "人气", "v": "hits"},
                        {"n": "评分", "v": "score"},
                    ]},
                ],
                '6': [
                    {"key": "area", "name": "地区", "value": [
                        {"n": "全部", "v": ""}, {"n": "中国大陆", "v": "中国大陆"},
                        {"n": "中国香港", "v": "中国香港"}, {"n": "中国台湾", "v": "中国台湾"},
                        {"n": "美国", "v": "美国"}, {"n": "韩国", "v": "韩国"},
                        {"n": "日本", "v": "日本"}, {"n": "其他", "v": "其他"},
                    ]},
                    {"key": "by", "name": "排序", "value": [
                        {"n": "最新", "v": "time"}, {"n": "人气", "v": "hits"},
                        {"n": "评分", "v": "score"},
                    ]},
                ],
                '7': [
                    {"key": "area", "name": "地区", "value": [
                        {"n": "全部", "v": ""}, {"n": "中国大陆", "v": "中国大陆"},
                        {"n": "中国香港", "v": "中国香港"}, {"n": "中国台湾", "v": "中国台湾"},
                        {"n": "美国", "v": "美国"}, {"n": "韩国", "v": "韩国"},
                        {"n": "日本", "v": "日本"}, {"n": "其他", "v": "其他"},
                    ]},
                    {"key": "by", "name": "排序", "value": [
                        {"n": "最新", "v": "time"}, {"n": "人气", "v": "hits"},
                        {"n": "评分", "v": "score"},
                    ]},
                ],
                '8': [
                    {"key": "area", "name": "地区", "value": [
                        {"n": "全部", "v": ""}, {"n": "中国大陆", "v": "中国大陆"},
                        {"n": "中国香港", "v": "中国香港"}, {"n": "中国台湾", "v": "中国台湾"},
                        {"n": "美国", "v": "美国"}, {"n": "韩国", "v": "韩国"},
                        {"n": "日本", "v": "日本"}, {"n": "其他", "v": "其他"},
                    ]},
                    {"key": "by", "name": "排序", "value": [
                        {"n": "最新", "v": "time"}, {"n": "人气", "v": "hits"},
                        {"n": "评分", "v": "score"},
                    ]},
                ],
                '9': [
                    {"key": "area", "name": "地区", "value": [
                        {"n": "全部", "v": ""}, {"n": "中国大陆", "v": "中国大陆"},
                        {"n": "中国香港", "v": "中国香港"}, {"n": "中国台湾", "v": "中国台湾"},
                        {"n": "美国", "v": "美国"}, {"n": "韩国", "v": "韩国"},
                        {"n": "日本", "v": "日本"}, {"n": "其他", "v": "其他"},
                    ]},
                    {"key": "by", "name": "排序", "value": [
                        {"n": "最新", "v": "time"}, {"n": "人气", "v": "hits"},
                        {"n": "评分", "v": "score"},
                    ]},
                ],
                '10': [
                    {"key": "area", "name": "地区", "value": [
                        {"n": "全部", "v": ""}, {"n": "中国大陆", "v": "中国大陆"},
                        {"n": "中国香港", "v": "中国香港"}, {"n": "中国台湾", "v": "中国台湾"},
                        {"n": "美国", "v": "美国"}, {"n": "韩国", "v": "韩国"},
                        {"n": "日本", "v": "日本"}, {"n": "其他", "v": "其他"},
                    ]},
                    {"key": "by", "name": "排序", "value": [
                        {"n": "最新", "v": "time"}, {"n": "人气", "v": "hits"},
                        {"n": "评分", "v": "score"},
                    ]},
                ],
                '11': [
                    {"key": "area", "name": "地区", "value": [
                        {"n": "全部", "v": ""}, {"n": "中国大陆", "v": "中国大陆"},
                        {"n": "中国香港", "v": "中国香港"}, {"n": "中国台湾", "v": "中国台湾"},
                        {"n": "美国", "v": "美国"}, {"n": "韩国", "v": "韩国"},
                        {"n": "日本", "v": "日本"}, {"n": "其他", "v": "其他"},
                    ]},
                    {"key": "by", "name": "排序", "value": [
                        {"n": "最新", "v": "time"}, {"n": "人气", "v": "hits"},
                        {"n": "评分", "v": "score"},
                    ]},
                ],
                '12': [
                    {"key": "area", "name": "地区", "value": [
                        {"n": "全部", "v": ""}, {"n": "中国大陆", "v": "中国大陆"},
                        {"n": "中国香港", "v": "中国香港"}, {"n": "中国台湾", "v": "中国台湾"},
                        {"n": "美国", "v": "美国"}, {"n": "韩国", "v": "韩国"},
                        {"n": "日本", "v": "日本"}, {"n": "其他", "v": "其他"},
                    ]},
                    {"key": "by", "name": "排序", "value": [
                        {"n": "最新", "v": "time"}, {"n": "人气", "v": "hits"},
                        {"n": "评分", "v": "score"},
                    ]},
                ],
                '23': [
                    {"key": "area", "name": "地区", "value": [
                        {"n": "全部", "v": ""}, {"n": "中国大陆", "v": "中国大陆"},
                        {"n": "中国香港", "v": "中国香港"}, {"n": "中国台湾", "v": "中国台湾"},
                        {"n": "美国", "v": "美国"}, {"n": "日本", "v": "日本"},
                        {"n": "其他", "v": "其他"},
                    ]},
                    {"key": "by", "name": "排序", "value": [
                        {"n": "最新", "v": "time"}, {"n": "人气", "v": "hits"},
                        {"n": "评分", "v": "score"},
                    ]},
                ],
                '21': [
                    {"key": "area", "name": "地区", "value": [
                        {"n": "全部", "v": ""}, {"n": "中国大陆", "v": "中国大陆"},
                        {"n": "中国香港", "v": "中国香港"}, {"n": "中国台湾", "v": "中国台湾"},
                        {"n": "美国", "v": "美国"}, {"n": "日本", "v": "日本"},
                        {"n": "其他", "v": "其他"},
                    ]},
                    {"key": "by", "name": "排序", "value": [
                        {"n": "最新", "v": "time"}, {"n": "人气", "v": "hits"},
                        {"n": "评分", "v": "score"},
                    ]},
                ],
                '2': [
                    {"key": "area", "name": "地区", "value": [
                        {"n": "全部", "v": ""}, {"n": "中国大陆", "v": "中国大陆"},
                        {"n": "中国台湾", "v": "中国台湾"}, {"n": "中国香港", "v": "中国香港"},
                        {"n": "韩国", "v": "韩国"}, {"n": "日本", "v": "日本"},
                        {"n": "美国", "v": "美国"}, {"n": "泰国", "v": "泰国"},
                        {"n": "英国", "v": "英国"}, {"n": "新加坡", "v": "新加坡"},
                        {"n": "其他", "v": "其他"},
                    ]},
                    {"key": "by", "name": "排序", "value": [
                        {"n": "最新", "v": "time"}, {"n": "人气", "v": "hits"},
                        {"n": "评分", "v": "score"},
                    ]},
                ],
                '13': [
                    {"key": "area", "name": "地区", "value": [
                        {"n": "全部", "v": ""}, {"n": "中国大陆", "v": "中国大陆"},
                    ]},
                    {"key": "by", "name": "排序", "value": [
                        {"n": "最新", "v": "time"}, {"n": "人气", "v": "hits"},
                        {"n": "评分", "v": "score"},
                    ]},
                ],
                '14': [
                    {"key": "area", "name": "地区", "value": [
                        {"n": "全部", "v": ""}, {"n": "中国香港", "v": "中国香港"},
                        {"n": "中国台湾", "v": "中国台湾"},
                    ]},
                    {"key": "by", "name": "排序", "value": [
                        {"n": "最新", "v": "time"}, {"n": "人气", "v": "hits"},
                        {"n": "评分", "v": "score"},
                    ]},
                ],
                '15': [
                    {"key": "area", "name": "地区", "value": [
                        {"n": "全部", "v": ""}, {"n": "韩国", "v": "韩国"},
                        {"n": "日本", "v": "日本"},
                    ]},
                    {"key": "by", "name": "排序", "value": [
                        {"n": "最新", "v": "time"}, {"n": "人气", "v": "hits"},
                        {"n": "评分", "v": "score"},
                    ]},
                ],
                '16': [
                    {"key": "area", "name": "地区", "value": [
                        {"n": "全部", "v": ""}, {"n": "美国", "v": "美国"},
                        {"n": "英国", "v": "英国"}, {"n": "其他", "v": "其他"},
                    ]},
                    {"key": "by", "name": "排序", "value": [
                        {"n": "最新", "v": "time"}, {"n": "人气", "v": "hits"},
                        {"n": "评分", "v": "score"},
                    ]},
                ],
                '24': [
                    {"key": "area", "name": "地区", "value": [
                        {"n": "全部", "v": ""}, {"n": "泰国", "v": "泰国"},
                    ]},
                    {"key": "by", "name": "排序", "value": [
                        {"n": "最新", "v": "time"}, {"n": "人气", "v": "hits"},
                        {"n": "评分", "v": "score"},
                    ]},
                ],
                '3': [
                    {"key": "area", "name": "地区", "value": [
                        {"n": "全部", "v": ""}, {"n": "中国大陆", "v": "中国大陆"},
                        {"n": "中国香港", "v": "中国香港"}, {"n": "韩国", "v": "韩国"},
                        {"n": "日本", "v": "日本"}, {"n": "美国", "v": "美国"},
                        {"n": "其他", "v": "其他"},
                    ]},
                    {"key": "by", "name": "排序", "value": [
                        {"n": "最新", "v": "time"}, {"n": "人气", "v": "hits"},
                        {"n": "评分", "v": "score"},
                    ]},
                ],
                '4': [
                    {"key": "area", "name": "地区", "value": [
                        {"n": "全部", "v": ""}, {"n": "中国大陆", "v": "中国大陆"},
                        {"n": "日本", "v": "日本"}, {"n": "美国", "v": "美国"},
                        {"n": "其他", "v": "其他"},
                    ]},
                    {"key": "by", "name": "排序", "value": [
                        {"n": "最新", "v": "time"}, {"n": "人气", "v": "hits"},
                        {"n": "评分", "v": "score"},
                    ]},
                ],
            }
            result['filters'] = filter_cfg
            return result
        except Exception as e:
            print(f"Error in homeContent: {str(e)}")
            return {"class": [], "list": []}

    def homeVideoContent(self):
        try:
            resp = self._safe_get(self.host + '/')
            if not resp or resp.status_code != 200:
                return {}
            videos = self._parse_videos(resp.text)
            return {'list': videos[:30]}
        except Exception as e:
            print(f"Error in homeVideoContent: {str(e)}")
            return {}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            url = f"{self.host}/show/{tid}--------{pg}---.html"
            resp = self._safe_get(url)
            if not resp or resp.status_code != 200:
                return {'list': [], 'page': int(pg), 'pagecount': 1, 'limit': 0, 'total': 0}
            html = resp.text
            videos = self._parse_videos(html)
            pagecount_match = re.search(r'(\d+)/(\d+)', html)
            pagecount = int(pagecount_match.group(2)) if pagecount_match else 999
            last_page_match = re.search(r'class="page-link"[^>]*href="[^"]*-(\d+)---\.html"[^>]*>尾页', html)
            if last_page_match:
                pagecount = int(last_page_match.group(1))
            return {
                'list': videos,
                'page': int(pg),
                'pagecount': pagecount,
                'limit': len(videos),
                'total': pagecount * len(videos) if videos else 0,
            }
        except Exception as e:
            print(f"Error in categoryContent: {str(e)}")
            return {'list': [], 'page': int(pg), 'pagecount': 1, 'limit': 0, 'total': 0}

    def detailContent(self, ids):
        try:
            vid = ids[0]
            url = f"{self.host}/detail/{vid}.html"
            resp = self._safe_get(url)
            if not resp or resp.status_code != 200:
                return {'list': []}
            html = resp.text

            vod_name = ''
            h1_match = re.search(r'<h1[^>]*class="title"[^>]*>([^<]+)</h1>', html)
            if h1_match:
                vod_name = h1_match.group(1).strip()

            vod_pic = ''
            thumb_match = re.search(r'class="stui-content__thumb[^"]*"[^>]*>.*?data-original="([^"]+)"', html, re.DOTALL)
            if thumb_match:
                vod_pic = thumb_match.group(1)
            if not vod_pic:
                thumb_match2 = re.search(r'data-original="(https?://[^"]+)"', html)
                if thumb_match2:
                    vod_pic = thumb_match2.group(1)

            meta_items = re.findall(r'<span class="meta-item">([^<]+)</span>', html)
            type_name = ''
            vod_area = ''
            vod_year = ''
            for item in meta_items:
                item = item.strip()
                if re.match(r'^\d{4}$', item):
                    vod_year = item
                elif any(k in item for k in ['大陆', '香港', '台湾', '美国', '韩国', '日本', '泰国', '英国', '新加坡', '其他']):
                    vod_area = item
                elif ',' in item or '，' in item:
                    type_name = item

            vod_actor = ''
            vod_director = ''
            actor_match = re.search(r'主演[：:](.*?)</span>', html)
            if actor_match:
                vod_actor = actor_match.group(1).strip().rstrip('…')
            director_match = re.search(r'导演[：:](.*?)</span>', html)
            if director_match:
                vod_director = director_match.group(1).strip().rstrip('…')

            vod_content = ''
            content_match = re.search(r'<span class="detail-content"[^>]*>([^<]+)</span>', html)
            if content_match:
                vod_content = content_match.group(1).strip()
            if not vod_content:
                sketch_match = re.search(r'<span class="detail-sketch">([^<]+)</span>', html)
                if sketch_match:
                    vod_content = sketch_match.group(1).strip()

            vod = {
                'vod_id': vid,
                'vod_name': vod_name,
                'vod_pic': vod_pic,
                'vod_remarks': '',
                'vod_year': vod_year,
                'vod_area': vod_area,
                'vod_director': vod_director,
                'vod_actor': vod_actor,
                'vod_content': vod_content,
                'type_name': type_name,
            }

            play_from_list = []
            play_url_list = []

            sections = re.split(r'<h3>', html)
            for section in sections[1:]:
                h3_end = section.find('</h3>')
                if h3_end < 0:
                    continue
                source_name = section[:h3_end].strip()

                playlist_match = re.search(r'class="stui-content__playlist[^"]*"[^>]*>(.*?)</ul>', section[h3_end:], re.DOTALL)
                if playlist_match:
                    playlist_html = playlist_match.group(1)
                    episodes = re.findall(r'<a[^>]+href="(/w/[^"]+)"[^>]*>([^<]*)</a>', playlist_html)
                    if episodes:
                        play_from_list.append(source_name)
                        ep_urls = []
                        for ep_href, ep_name in episodes:
                            play_url = f"{self.host}{ep_href}"
                            ep_urls.append(f"{ep_name}${play_url}")
                        play_url_list.append('#'.join(ep_urls))
                else:
                    netdisk_items = re.findall(r'<a[^>]+class="netdisk-item"[^>]+href="([^"]+)"[^>]*>.*?<span class="netdisk-name">([^<]*)</span>', section[h3_end:], re.DOTALL)
                    if netdisk_items:
                        play_from_list.append(source_name)
                        ep_urls = []
                        for netdisk_url, text in netdisk_items:
                            netdisk_url = (netdisk_url or '').strip()
                            if netdisk_url.startswith('//'):
                                netdisk_url = 'https:' + netdisk_url
                            ep_name = text.strip() if text.strip() else '网盘下载'
                            ep_urls.append(f"{ep_name}${netdisk_url}")
                        play_url_list.append('#'.join(ep_urls))

            vod['vod_play_from'] = '$$$'.join(play_from_list)
            vod['vod_play_url'] = '$$$'.join(play_url_list)

            return {'list': [vod]}
        except Exception as e:
            print(f"Error in detailContent: {str(e)}")
            return {"list": []}

    def searchContent(self, key, quick, pg="1"):
        try:
            encoded_key = quote(key)
            url = f"{self.host}/search/{encoded_key}----------{pg}---.html"
            resp = self._safe_get(url)
            if not resp or resp.status_code != 200:
                return {'list': [], 'page': pg}
            videos = self._parse_videos(resp.text)
            return {'list': videos, 'page': pg}
        except Exception as e:
            print(f"Error in searchContent: {str(e)}")
            return {'list': [], 'page': pg}

    def playerContent(self, flag, id, vipFlags):
        try:
            if isinstance(id, str):
                id = id.strip()
                if id.startswith('//'):
                    id = 'https:' + id
                if id.startswith('magnet:') or id.startswith('thunder:') or id.startswith('ed2k:'):
                    return {
                        "parse": 1,
                        "url": id,
                        "header": dict(self.header),
                        "playUrl": ""
                    }
                if id.startswith('http') and not id.startswith(self.host):
                    return {
                        "parse": 1,
                        "url": id,
                        "header": dict(self.header),
                        "playUrl": ""
                    }

            resp = self._safe_get(id)
            if not resp or resp.status_code != 200:
                return {"parse": 1, "url": id, "header": dict(self.header), "playUrl": ""}

            html = resp.text
            player_match = re.search(r'var player_aaaa=(\{[^}]+\})', html)
            if player_match:
                try:
                    player_data = json.loads(player_match.group(1))
                    video_url = player_data.get('url', '')
                    if video_url:
                        video_url = video_url.replace('\\/', '/')
                        if video_url.endswith('.mp4') or '.m3u8' in video_url:
                            headers = dict(self.header)
                            headers['Referer'] = id
                            return {
                                "parse": 0,
                                "url": video_url,
                                "header": headers,
                                "playUrl": ""
                            }
                        else:
                            return {
                                "parse": 1,
                                "url": video_url,
                                "header": dict(self.header),
                                "playUrl": ""
                            }
                except:
                    pass

            return {"parse": 1, "url": id, "header": dict(self.header), "playUrl": ""}
        except Exception as e:
            print(f"Error in playerContent: {str(e)}")
            return {"parse": 1, "url": id, "header": dict(self.header), "playUrl": ""}

    def localProxy(self, param):
        return None
