# coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import json
import time
import urllib.parse
import re
import requests
from lxml import etree
import base64

class Spider(Spider):
    def getName(self):
        return "韩国色情电影"

    def init(self, extend):
        print("=============韩国色情电影初始化===========")

    def homeContent(self, filter):
        result = {}
        cateManual = {
            "最新视频": "latest",
            "最长的视频": "longest", 
            "随机视频": "random"
        }
        classes = []
        for k in cateManual:
            classes.append({
                'type_name': k,
                'type_id': cateManual[k]
            })

        result['class'] = classes
        return result

    def homeVideoContent(self):
        result = {}
        videos = self.getVideos('https://koreanpornmovie.com/', 1)
        result['list'] = videos
        return result

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        
        # 将 pg 转换为整数
        try:
            page_num = int(pg)
        except (ValueError, TypeError):
            page_num = 1
        
        url = 'https://koreanpornmovie.com/'
        if tid == 'longest':
            url = 'https://koreanpornmovie.com/?filter=longest'
        elif tid == 'random':
            url = 'https://koreanpornmovie.com/?filter=random'
        
        if page_num > 1:
            url = url + 'page/{0}/'.format(page_num)
        
        videos = self.getVideos(url, page_num)
        result['list'] = videos
        result['page'] = page_num
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, array):
        tid = array[0]
        url = 'https://koreanpornmovie.com/{0}'.format(tid)
        rsp = self.fetch(url)
        html = rsp.text

        # 获取视频信息
        video = self.getDetail(html, url)
        
        # 获取播放地址
        play_url = self.getPlayUrl(html, url)
        
        # 构建播放列表
        playFrom = ['韩国色情电影']
        playList = [play_url] if play_url else []
        
        result = {
            'list': [
                {
                    'vod_id': tid,
                    'vod_name': video['title'],
                    'vod_pic': video['pic'],
                    'type_name': video['type'],
                    'vod_year': video['year'],
                    'vod_area': "韩国",
                    'vod_remarks': video['remarks'],
                    'vod_actor': video['actor'],
                    'vod_director': video['director'],
                    'vod_content': video['content'],
                    'vod_play_from': '$$$'.join(playFrom),
                    'vod_play_url': '$$$'.join(playList)
                }
            ]
        }
        return result

    def searchContent(self, key, quick, page='1'):
        result = {}
        url = 'https://koreanpornmovie.com/?s={0}'.format(urllib.parse.quote(key))
        videos = self.getVideos(url, 1)
        result['list'] = videos
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {}
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = id
        result["header"] = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
            "Referer": "https://koreanpornmovie.com/"
        }
        return result

    def getVideos(self, url, pg):
        videos = []
        try:
            rsp = self.fetch(url)
            html = rsp.text
            root = etree.HTML(html)
            
            # 解析视频列表
            video_list = root.xpath('//article[contains(@class, "thumb-block")]')
            for item in video_list:
                try:
                    # 获取视频链接
                    link = item.xpath('.//a/@href')[0]
                    vid = link.split('/')[-2] if link.endswith('/') else link.split('/')[-1]
                    
                    # 获取缩略图
                    img = item.xpath('.//img[@class="video-main-thumb"]/@src')[0]
                    
                    # 获取标题
                    title = item.xpath('.//header[@class="entry-header"]/span/text()')[0].strip()
                    
                    # 获取时长
                    duration = item.xpath('.//span[@class="duration"]/text()')
                    remarks = duration[0].strip() if duration else ''
                    
                    videos.append({
                        "vod_id": vid,
                        "vod_name": title,
                        "vod_pic": img,
                        "vod_remarks": remarks
                    })
                except Exception as e:
                    print(f"解析视频项时出错: {e}")
                    continue
        except Exception as e:
            print(f"获取视频列表时出错: {e}")
                    
        return videos

    def getDetail(self, html, url):
        root = etree.HTML(html)
        detail = {
            'title': '',
            'pic': '',
            'type': '韩国情色',
            'year': '',
            'actor': '',
            'director': '',
            'content': '',
            'remarks': ''
        }
        
        try:
            # 标题
            title_elem = root.xpath('//h1[@class="entry-title"]/text()')
            if title_elem:
                detail['title'] = title_elem[0].strip()
            
            # 缩略图
            pic_elem = root.xpath('//meta[@property="og:image"]/@content')
            if pic_elem:
                detail['pic'] = pic_elem[0]
            
            # 演员信息
            actors = root.xpath('//div[@id="video-actors"]//a/text()')
            if actors:
                detail['actor'] = ' / '.join(actors)
            
            # 内容描述
            content_elem = root.xpath('//div[@class="video-description"]//p/text()')
            if content_elem:
                detail['content'] = content_elem[0].strip()
            
            # 时长
            duration_elem = root.xpath('//span[@class="duration"]/text()')
            if duration_elem:
                detail['remarks'] = duration_elem[0].strip()
                
        except Exception as e:
            print(f"获取详情时出错: {e}")
            
        return detail

    def getPlayUrl(self, html, url):
        play_url = ''
        
        # 方法1: 从meta标签中提取contentURL
        meta_pattern = r'<meta\s+itemprop="contentURL"\s+content="([^"]+)"'
        meta_match = re.search(meta_pattern, html)
        if meta_match:
            play_url = meta_match.group(1)
            print(f"从meta标签找到播放链接: {play_url}")
            return play_url
        
        # 方法2: 从iframe的src中提取base64编码的视频链接
        if not play_url:
            iframe_pattern = r'<iframe[^>]+src="[^"]*\?q=([^"]+)"[^>]*>'
            iframe_match = re.search(iframe_pattern, html)
            if iframe_match:
                base64_str = iframe_match.group(1)
                try:
                    decoded = base64.b64decode(base64_str).decode('utf-8')
                    # 从解码后的内容中提取mp4链接
                    mp4_pattern = r'src="([^"]+\.mp4)"'
                    mp4_match = re.search(mp4_pattern, decoded)
                    if mp4_match:
                        play_url = mp4_match.group(1)
                        print(f"从iframe解码找到播放链接: {play_url}")
                except Exception as e:
                    print(f"解码base64时出错: {e}")
        
        # 方法3: 直接搜索mp4链接
        if not play_url:
            mp4_pattern = r'https?://[^\s"\']+\.mp4'
            mp4_matches = re.findall(mp4_pattern, html)
            if mp4_matches:
                # 优先选择koreanporn.stream域名的链接
                for mp4_url in mp4_matches:
                    if 'koreanporn.stream' in mp4_url:
                        play_url = mp4_url
                        break
                if not play_url and mp4_matches:
                    play_url = mp4_matches[0]
                print(f"直接搜索找到播放链接: {play_url}")
        
        # 方法4: 从JavaScript变量中提取
        if not play_url:
            js_patterns = [
                r'file\s*:\s*["\']([^"\']+\.mp4)["\']',
                r'src\s*:\s*["\']([^"\']+\.mp4)["\']',
                r'videoSrc\s*:\s*["\']([^"\']+\.mp4)["\']'
            ]
            for pattern in js_patterns:
                js_match = re.search(pattern, html)
                if js_match:
                    play_url = js_match.group(1)
                    print(f"从JS变量找到播放链接: {play_url}")
                    break
        
        # 如果找到播放链接，确保是完整的URL
        if play_url and not play_url.startswith('http'):
            if play_url.startswith('//'):
                play_url = 'https:' + play_url
            else:
                # 尝试从当前页面URL构造完整URL
                from urllib.parse import urljoin
                play_url = urljoin(url, play_url)
        
        return play_url

    def isVideoFormat(self, url):
        video_formats = ['.mp4', '.m3u8', '.avi', '.mov', '.wmv', '.flv', '.mkv']
        return any(format in url.lower() for format in video_formats)

    def manualVideoCheck(self):
        return True

    def localProxy(self, param):
        action = {}
        return []