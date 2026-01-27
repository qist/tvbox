# -*- coding: utf-8 -*-
# by @Qist
import re
import sys
import json
import time
from pyquery import PyQuery as pq
from base.spider import Spider
import requests
from bs4 import BeautifulSoup


class Spider(Spider):
    def getName(self):
        return "闪雷影视"

    def init(self, extend=""):
        pass

    host = 'http://60.6.229.145:88'
    ip = '60.6.229.145'
    header = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Mobile Safari/537.36',
    }
    encoding = 'gb2312'

    class_names = '电视剧&大陆地区&港台地区&日韩地区&欧美地区&其他地区&动作片&喜剧片&恐怖片&科幻片&战争片&动画片&爱情片&综艺片&剧情片&MTV'.split('&')
    class_urls = '10&20&21&22&23&24&1&2&3&4&5&6&7&8&9&12'.split('&')

    def homeContent(self, filter):
        """
        获取首页内容
        """
        try:
            result = {'class': [], 'list': []}
            for name, cid in zip(self.class_names, self.class_urls):
                result['class'].append({'type_name': name, 'type_id': cid})

            # 获取首页推荐影片
            url = f"{self.host}/jdl/List.asp?ClassId=10"
            resp = self.fetch(url, headers=self.header)
            data = self.getpq(resp.text)
            
            videos = []
            # 使用更兼容的选择器 - 先选所有的dl，然后过滤有classid=h4的dd的dl
            all_dls = data('dl')
            for dl in all_dls.items():
                h4_dd = dl('dd[classid="h4"]')
                if h4_dd.length > 0:
                    title = h4_dd('a').text()
                    pic = dl('dt img').attr('src')
                    if pic and pic.startswith('../'):
                        pic = self.host + '/' + pic.replace('../', '')
                    elif pic and not pic.startswith('http'):
                        pic = self.host + '/' + pic.lstrip('/')
                    
                    href = h4_dd('a').attr('href')
                    if href:
                        # 从href中提取ClassId
                        vid_match = re.search(r'[Cc]lass[Ii][Dd]=(\d+)', href)
                        vid = vid_match.group(1) if vid_match else href
                        videos.append({
                            'vod_id': vid,
                            'vod_name': title,
                            'vod_pic': pic,
                            'vod_remarks': ''
                        })
            
            result['list'] = videos[:10]  # 只取前10个
            return result
        except Exception as e:
            print(f"Error in homeContent: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"class": [], "list": []}

    def categoryContent(self, tid, pg, filter, extend):
        """
        获取分类内容
        """
        try:
            url = f"{self.host}/jdl/List.asp?ClassId={tid}&searchword=&page={pg}"
            resp = self.fetch(url, headers=self.header)
            data = self.getpq(resp.text)
            
            result = {}
            videos = []
            
            # 使用相同的选择器逻辑
            all_dls = data('dl')
            for dl in all_dls.items():
                h4_dd = dl('dd[classid="h4"]')
                if h4_dd.length > 0:
                    title = h4_dd('a').text()
                    pic = dl('dt img').attr('src')
                    if pic and pic.startswith('../'):
                        pic = self.host + '/' + pic.replace('../', '')
                    elif pic and not pic.startswith('http'):
                        pic = self.host + '/' + pic.lstrip('/')
                    
                    href = h4_dd('a').attr('href')
                    if href:
                        # 从href中提取ClassId
                        vid_match = re.search(r'[Cc]lass[Ii][Dd]=(\d+)', href)
                        vid = vid_match.group(1) if vid_match else href
                        videos.append({
                            'vod_id': vid,
                            'vod_name': title,
                            'vod_pic': pic,
                            'vod_remarks': ''
                        })
            
            result['list'] = videos
            result['page'] = int(pg)
            result['pagecount'] = 999  # 假设有很多页
            result['limit'] = len(videos)
            result['total'] = 999999
            return result
        except Exception as e:
            print(f"Error in categoryContent: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"list": [], "page": 1, "pagecount": 1, "limit": 0, "total": 0}

    def detailContent(self, ids):
        """
        获取影片详情
        """
        try:
            url = f"{self.host}/jdl/movie.asp?ClassId={ids[0]}"
            resp = self.fetch(url, headers=self.header)
            data = self.getpq(resp.text)
            
            vod = {
                'vod_id': ids[0],
                'vod_name': data('li[classid="h4"]').text(),
                'vod_pic': '',
                'vod_remarks': '',
                'vod_year': '',
                'vod_area': '',
                'vod_director': '',
                'vod_actor': '',
                'vod_content': ''
            }
            
            # 获取封面
            cover_img = data('.intro .img img').attr('src')
            if cover_img and cover_img.startswith('../'):
                vod['vod_pic'] = f"{self.host}/{cover_img[3:]}"
            elif cover_img and not cover_img.startswith('http'):
                vod['vod_pic'] = f"{self.host}/{cover_img}"
            else:
                vod['vod_pic'] = cover_img
            
            # 获取演员信息
            actor_info = data('li:contains("主　　演")').text()
            if actor_info:
                vod['vod_actor'] = actor_info.replace('主　　演：', '').strip()
            
            # 获取内容信息
            content_parts = []
            selectors = ['li:contains("状　　态")', 'li:contains("类　　型")', 'li:contains("拍摄地区")', 'li:contains("更新时间")', 'li:contains("单集时长")']
            for sel in selectors:
                part = data(sel).text()
                if part:
                    content_parts.append(part)
            vod['vod_content'] = '\n'.join(content_parts)
            
            # 获取播放列表
            play_urls = []
            # 根据j.js中的规则: div.listt a
            for a in data('div.listt a').items():
                title = a.text()
                href = a.attr('href')
                if title and href:
                    # 从href构造播放地址
                    play_link = f"{self.host}{href}"
                    play_urls.append(f"{title}${play_link}")
            
            vod['vod_play_from'] = '闪雷影视'
            vod['vod_play_url'] = '#'.join(play_urls) if play_urls else '无播放源'
            
            result = {"list": [vod]}
            return result
        except Exception as e:
            print(f"Error in detailContent: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"list": []}

    def searchContent(self, key, quick, pg="1"):
        """
        搜索内容
        """
        try:
            url = f"{self.host}/jdl/List.asp?ClassId=30&type=&searchword={key}&page={pg}"
            resp = self.fetch(url, headers=self.header)
            data = self.getpq(resp.text)
            
            videos = []
            # 使用相同的选择器逻辑
            all_dls = data('dl')
            for dl in all_dls.items():
                h4_dd = dl('dd[classid="h4"]')
                if h4_dd.length > 0:
                    title = h4_dd('a').text()
                    pic = dl('dt img').attr('src')
                    if pic and pic.startswith('../'):
                        pic = self.host + '/' + pic.replace('../', '')
                    elif pic and not pic.startswith('http'):
                        pic = self.host + '/' + pic.lstrip('/')
                    
                    href = h4_dd('a').attr('href')
                    if href:
                        # 从href中提取ClassId
                        vid_match = re.search(r'[Cc]lass[Ii][Dd]=(\d+)', href)
                        vid = vid_match.group(1) if vid_match else href
                        videos.append({
                            'vod_id': vid,
                            'vod_name': title,
                            'vod_pic': pic,
                            'vod_remarks': ''
                        })
            
            return {'list': videos, 'page': pg}
        except Exception as e:
            print(f"Error in searchContent: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'list': [], 'page': pg}

    def playerContent(self, flag, id, vipFlags):
        """
        播放内容
        """
        try:
            # id 现在是播放页面的完整URL，格式类似: ClassId,xx,xx,movNo
            if ',' in id:
                parts = id.split(',')
                classid = parts[2]
                movno = parts[3]
                play_url = f"{self.host}/PlayMov.asp?ClassId={classid}&video=2&exe=0&down=0&movNo={movno}&vgver=undefined&ClientIP={self.ip}"
            else:
                play_url = id  # 已经是完整的播放页面URL

            # 获取播放页面内容
            resp = self.fetch(play_url, headers=self.header)
            html = resp.text
            
            # 根据j.js中的lazy规则进行解析
            # var url = request(html).match(/videoarr\.push\('(.*?)'/)[1]
            video_match = re.search(r"videoarr\.push\(['\"](.*?)['\"]\)", html)
            if video_match:
                video_url = video_match.group(1)
                # 处理URL，替换域名部分
                # url = url.replace(/https?:\/\/(?:[\d.]+|[\w\-]+)(?::\d+)?\//, rule.host + '/')
                video_url = re.sub(r'https?://(?:[\d.]+|[\w\-]+)(?::\d+)?/', f'{self.host}/', video_url)
                
                result = {
                    "parse": 0,
                    "url": video_url,
                    "header": self.header,
                    "playUrl": ""
                }
                return result
            else:
                print(f"Warning: Could not extract video URL from {play_url}")
                # 尝试寻找其他可能的视频URL
                # 匹配 player.open("...") 调用
                js_open_matches = re.findall(r'player\.open\s*\(\s*["\']([^"\']+)["\']\s*\)', html)
                if js_open_matches:
                    video_url = js_open_matches[0]
                    if not video_url.startswith('http'):
                        video_url = self.host + '/' + video_url.lstrip('/')
                    result = {
                        "parse": 0,
                        "url": video_url,
                        "header": self.header,
                        "playUrl": ""
                    }
                    return result
                    
                # 如果还是找不到，返回错误
                return {
                    "parse": 1,
                    "url": play_url
                }
        except Exception as e:
            print(f"Error in playerContent: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "parse": 1,
                "url": id
            }

    def getpq(self, data):
        try:
            return pq(data)
        except Exception as e:
            print(f"Error parsing data: {str(e)}")
            return pq(data.encode('utf-8'))

    def fetch(self, url, headers=None):
        """
        发送HTTP请求
        """
        session = requests.Session()
        if headers:
            session.headers.update(headers)
        else:
            session.headers.update(self.header)
        
        # 增加超时时间以适应响应较慢的服务
        response = session.get(url, timeout=25)
        response.encoding = self.encoding
        return response

    def post(self, url, headers=None, data=None):
        """
        发送POST请求
        """
        session = requests.Session()
        if headers:
            session.headers.update(headers)
        else:
            session.headers.update(self.header)
        
        response = session.post(url, data=data, timeout=25)
        response.encoding = self.encoding
        return response