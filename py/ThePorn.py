# -*- coding: utf-8 -*-
import re
import sys
from pyquery import PyQuery as pq
sys.path.append('..')
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        return "ThePorn"

    def init(self, extend=""):
        pass

    def homeContent(self, filter):
        result = {}
        try:
            rsp = self.fetch("https://theporn.cc/categories")
            root = pq(rsp.text)
            classes = []
            
            main_categories = {
                "影片": "categories/all", "日本AV": "jav", "欧美": "eu", "VR": "vr",
                "最佳影片": "video/best", "日本无码": "jav/uncensored"
            }
            
            for name, cid in main_categories.items():
                classes.append({'type_name': name, 'type_id': cid})
            
            for item in root('.categories_list .categorie_item').items():
                a_tag = item.find('a')
                if a_tag:
                    name = a_tag.text().strip()
                    href = a_tag.attr('href')
                    if href and name:
                        classes.append({
                            'type_name': name,
                            'type_id': f"categories/{href.split('/')[-1]}"
                        })
            
            seen = set()
            result['class'] = [cls for cls in classes if not (key := (cls['type_name'], cls['type_id'])) in seen and not seen.add(key)]
            
        except Exception as e:
            cateManual = {
                "影片": "categories/all", "日本AV": "jav", "欧美": "eu", "VR": "vr",
                "最佳影片": "video/best", "日本无码": "jav/uncensored"
            }
            result['class'] = [{'type_name': k, 'type_id': v} for k, v in cateManual.items()]
            
        return result

    def homeVideoContent(self):
        rsp = self.fetch("https://theporn.cc/")
        return {'list': [self.parseVideoItem(item) for item in pq(rsp.text)('.video-list .avdata-outer').items()]}

    def parseVideoItem(self, item):
        try:
            a_tag = item.find('a.av-link')
            href = a_tag.attr('href')
            img_tag = item.find('img.cover-img')
            cover = img_tag.attr('data-src') or img_tag.attr('src')
            return {
                "vod_id": href.split('/')[-1],
                "vod_name": item.find('.av_data_title').text(),
                "vod_pic": cover if cover.startswith('http') else "https://theporn.cc" + cover,
                "vod_remarks": item.find('.duration').text()
            } if href else None
        except:
            return None

    def categoryContent(self, tid, pg, filter, extend):
        # 修复翻页逻辑
        if int(pg) == 1:
            url = f"https://theporn.cc/{tid}"
        else:
            url = f"https://theporn.cc/{tid}/{pg}"
        
        rsp = self.fetch(url)
        root = pq(rsp.text)
        
        videos = []
        for selector in ['.video-list .avdata-outer', '.avdata-outer', '.video-list .card']:
            video_list = root(selector)
            if video_list.length > 0:
                videos = [self.parseVideoItem(item) for item in video_list.items()]
                break
        
        # 尝试获取总页数
        pagecount = 9999
        try:
            pagination = root('.pagination')
            if pagination.length > 0:
                page_links = pagination.find('a')
                if page_links.length > 0:
                    last_page = 1
                    for link in page_links.items():
                        href = link.attr('href')
                        if href:
                            # 从URL中提取页码
                            match = re.search(r'/(\d+)$', href)
                            if match:
                                page_num = int(match.group(1))
                                last_page = max(last_page, page_num)
                    pagecount = last_page
        except:
            pass
        
        return {
            'list': videos,
            'page': int(pg),
            'pagecount': pagecount,
            'limit': 90,
            'total': 999999
        }

    def detailContent(self, array):
        tid = array[0]
        rsp = self.fetch(f"https://theporn.cc/video/{tid}")
        root = pq(rsp.text)
        
        title = root('title').text().replace(' - ThePorn', '') or root('.av-big-title .inner-title').text()
        cover = root('.cover-img').attr('src')
        if not cover:
            match = re.search(r'background-image:\s*url\("([^"]+)"\)', root('.vjs-poster').attr('style') or '')
            cover = match.group(1) if match else ''
        
        return {'list': [{
            'vod_id': tid,
            'vod_name': title,
            'vod_pic': cover,
            'vod_content': title,
            'vod_actor': '未知演员',
            'vod_director': '未知导演',
            'vod_area': '未知地区', 
            'vod_year': '2024',
            'vod_remarks': root('.duration').text() or '未知时长',
            'vod_play_from': 'ThePorn',
            'vod_play_url': f'第1集${tid}'
        }]}

    def searchContent(self, key, quick, page='1'):
        # 搜索页面的翻页逻辑
        if int(page) == 1:
            url = f"https://theporn.cc/search/{key}"
        else:
            url = f"https://theporn.cc/search/{key}/{page}"
            
        rsp = self.fetch(url)
        root = pq(rsp.text)
        
        for selector in ['.search-results .video-item', '.video-list .avdata-outer', '.avdata-outer']:
            video_list = root(selector)
            if video_list.length > 0:
                return {'list': [self.parseVideoItem(item) for item in video_list.items()]}
        
        return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        rsp = self.fetch(f"https://theporn.cc/video/{id}")
        root = pq(rsp.text)
        
        hash_id = ""
        for script in root('script').items():
            script_text = script.text()
            if 'hash_id' in script_text:
                match = re.search(r'"hash_id":\s*"([a-f0-9]+)"', script_text)
                if match:
                    hash_id = match.group(1)
                    break
        
        if hash_id:
            src = f"https://b2.bttss.cc/videos/{hash_id}/g.m3u8?h=3121efe8979c635"
        else:
            video_tag = root('video#video-player_html5_api')
            src = video_tag.attr('src') if video_tag else ""
        
        return {
            "parse": 0,
            "playUrl": "",
            "url": src,
            "header": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://theporn.cc/",
                "Origin": "https://theporn.cc"
            }
        }

    def isVideoFormat(self, url):
        return any(fmt in url.lower() for fmt in ['.m3u8', '.mp4', '.avi', '.mkv', '.flv', '.webm']) if url else False

    def manualVideoCheck(self):
        pass

    def localProxy(self, param):
        return [200, "video/MP2T", {}, ""]