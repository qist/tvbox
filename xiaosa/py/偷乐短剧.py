#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 偷乐短剧爬虫

import sys
import json
import re
import time
import urllib.parse
import requests
from bs4 import BeautifulSoup

# 导入基础类
sys.path.append('../../')
try:
    from base.spider import Spider
except ImportError:
    # 本地调试时的替代实现
    class Spider:
        def init(self, extend=""):
            pass

class Spider(Spider):
    def __init__(self):
        # 网站主URL
        self.siteUrl = "https://www.toule.top"
        
        # 根据网站实际结构，分类链接格式为: /index.php/vod/show/class/分类名/id/1.html
        # 分类ID映射 - 从网站中提取的分类
        self.cateManual = {
            "男频": "/index.php/vod/show/class/%E7%94%B7%E9%A2%91/id/1.html",
            "女频": "/index.php/vod/show/class/%E5%A5%B3%E9%A2%91/id/1.html",
            "都市": "/index.php/vod/show/class/%E9%83%BD%E5%B8%82/id/1.html",
            "赘婿": "/index.php/vod/show/class/%E8%B5%98%E5%A9%BF/id/1.html",
            "战神": "/index.php/vod/show/class/%E6%88%98%E7%A5%9E/id/1.html",
            "古代言情": "/index.php/vod/show/class/%E5%8F%A4%E4%BB%A3%E8%A8%80%E6%83%85/id/1.html",
            "现代言情": "/index.php/vod/show/class/%E7%8E%B0%E4%BB%A3%E8%A8%80%E6%83%85/id/1.html",
            "历史": "/index.php/vod/show/class/%E5%8E%86%E5%8F%B2/id/1.html",
            "玄幻": "/index.php/vod/show/class/%E7%8E%84%E5%B9%BB/id/1.html",
            "搞笑": "/index.php/vod/show/class/%E6%90%9E%E7%AC%91/id/1.html",
            "甜宠": "/index.php/vod/show/class/%E7%94%9C%E5%AE%A0/id/1.html",
            "励志": "/index.php/vod/show/class/%E5%8A%B1%E5%BF%97/id/1.html",
            "逆袭": "/index.php/vod/show/class/%E9%80%86%E8%A2%AD/id/1.html",
            "穿越": "/index.php/vod/show/class/%E7%A9%BF%E8%B6%8A/id/1.html",
            "古装": "/index.php/vod/show/class/%E5%8F%A4%E8%A3%85/id/1.html"
        }
        
        # 请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Referer": "https://www.toule.top/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
         }
        
        
        # 缓存
        self.cache = {}
        self.cache_timeout = {}
    
    def getName(self):
        return "偷乐短剧"
    
    def init(self, extend=""):
        # 初始化方法，可以留空
        return
    
    def isVideoFormat(self, url):
        """判断是否为视频格式"""
        video_formats = ['.mp4', '.m3u8', '.ts', '.flv', '.avi', '.mkv', '.mov', '.rmvb', '.3gp']
        for format in video_formats:
            if format in url.lower():
                return True
        return False
    
    def manualVideoCheck(self):
        """是否需要手动检查视频"""
        return False
    
    # 工具方法 - 网络请求    
    def fetch(self, url, headers=None, data=None, method="GET"):
        """统一的网络请求方法"""
        try:
            if headers is None:
                headers = self.headers.copy()
                
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=data, timeout=10,verify=False)
            else:  # POST
                response = requests.post(url, headers=headers, data=data, timeout=10,verify=False)
                
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'
            return response
        except Exception as e:
            self.log(f"请求失败: {url}, 错误: {str(e)}", "ERROR")
            return None
    
    # 缓存方法
    def getCache(self, key, timeout=3600):
        """获取缓存数据"""
        if key in self.cache and key in self.cache_timeout:
            if time.time() < self.cache_timeout[key]:
                return self.cache[key]
            else:
                del self.cache[key]
                del self.cache_timeout[key]
        return None
    
    def setCache(self, key, value, timeout=3600):
        """设置缓存数据"""
        self.cache[key] = value
        self.cache_timeout[key] = time.time() + timeout
    
    # 日志方法
    def log(self, msg, level='INFO'):
        """记录日志"""
        levels = {
            'DEBUG': 0,
            'INFO': 1,
            'WARNING': 2,
            'ERROR': 3
        }
        
        current_level = 'INFO'  # 可以设置为DEBUG以获取更多信息
        
        if levels.get(level, 4) >= levels.get(current_level, 1):
            print(f"[{level}] {time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}")
    
    # 辅助方法 - 从URL中提取视频ID
    def extractVodId(self, url):
        """从URL中提取视频ID"""
        # 路径格式: /index.php/vod/play/id/9024/sid/1/nid/1.html
        match = re.search(r'/id/(\d+)/', url)
        if match:
            return match.group(1)
        return ""

    # 辅助方法 - 从网页内容中提取分类
    def extractCategories(self, text):
        """从网页内容中提取分类标签"""
        cats = []
        # 匹配标签字符串，例如: "男频,逆袭,亲情,短剧"
        if "," in text:
            parts = text.split(",")
            for part in parts:
                part = part.strip()
                if part and part != "短剧":
                    cats.append(part)
        return cats
    
    # 主要接口实现
    def homeContent(self, filter):
        """获取首页分类及内容"""
        result = {}
        classes = []
        
        # 从缓存获取
        cache_key = 'home_classes'
        cached_classes = self.getCache(cache_key)
        if cached_classes:
            classes = cached_classes
        else:
            # 使用预定义的分类
            for k, v in self.cateManual.items():
                classes.append({
                    'type_id': v,  # 使用完整URL路径作为type_id
                    'type_name': k
                })
            
            # 保存到缓存
            self.setCache(cache_key, classes, 24*3600)  # 缓存24小时
        
        result['class'] = classes
        
        # 获取首页推荐视频
        videos = self.homeVideoContent().get('list', [])
        result['list'] = videos
        
        return result
    
    def homeVideoContent(self):
        """获取首页推荐视频内容"""
        result = {'list': []}
        videos = []
        
        # 从缓存获取
        cache_key = 'home_videos'
        cached_videos = self.getCache(cache_key)
        if cached_videos:
            return {'list': cached_videos}
        
        try:
            response = self.fetch(self.siteUrl)
            if response and response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                
                # 查找最新更新区域
                latest_section = soup.find('h2', text=lambda t: t and '最新更新' in t)
                if latest_section:
                    container = latest_section.parent  # 获取容器
                    if container:
                        # 查找所有 li.item 元素
                        items = container.find_all('li', class_='item')
                        
                        for item in items:
                            try:
                                # 获取链接和标题
                                title_link = item.find('h3')
                                if not title_link:
                                    continue
                                
                                title = title_link.text.strip()
                                
                                # 获取第一个链接作为详情页链接
                                link_tag = item.find('a')
                                if not link_tag:
                                    continue
                                
                                link = link_tag.get('href', '')
                                if not link.startswith('http'):
                                    link = urllib.parse.urljoin(self.siteUrl, link)
                                
                                # 提取ID
                                vid = self.extractVodId(link)
                                if not vid:
                                    continue
                                
                                # 获取图片
                                img_tag = item.find('img')
                                img_url = ""
                                if img_tag:
                                    img_url = img_tag.get('src', img_tag.get('data-src', ''))
                                    if img_url and not img_url.startswith('http'):
                                        img_url = urllib.parse.urljoin(self.siteUrl, img_url)
                                
                                # 获取备注信息
                                remarks = ""
                                remarks_tag = item.find('span', class_='remarks')
                                if remarks_tag:
                                    remarks = remarks_tag.text.strip()
                                
                                # 获取标签信息
                                tags = ""
                                tags_tag = item.find('span', class_='tags')
                                if tags_tag:
                                    tags = tags_tag.text.strip()
                                
                                # 合并备注和标签
                                if remarks and tags:
                                    remarks = f"{remarks} | {tags}"
                                elif tags:
                                    remarks = tags
                                
                                # 构建视频项
                                videos.append({
                                    'vod_id': vid,
                                    'vod_name': title,
                                    'vod_pic': img_url,
                                    'vod_remarks': remarks
                                })
                            except Exception as e:
                                self.log(f"处理视频项时出错: {str(e)}", "ERROR")
                                continue
                
                # 保存到缓存
                self.setCache(cache_key, videos, 3600)  # 缓存1小时
        except Exception as e:
            self.log(f"获取首页视频内容发生错误: {str(e)}", "ERROR")
        
        result['list'] = videos
        return result
    
    def categoryContent(self, tid, pg, filter, extend):
        """获取分类内容"""
        result = {}
        videos = []
        
        # 处理页码
        if pg is None:
            pg = 1
        else:
            pg = int(pg)

        # 构建分类URL - tid是完整的URL路径
        if tid.startswith("/"):
            # 替换页码，URL格式可能像: /index.php/vod/show/class/男频/id/1.html
            if pg > 1:
                if "html" in tid:
                    category_url = tid.replace(".html", f"/page/{pg}.html")
                else:
                    category_url = f"{tid}/page/{pg}.html"
            else:
                category_url = tid
            
            full_url = urllib.parse.urljoin(self.siteUrl, category_url)
        else:
            # 如果tid不是URL路径，可能是旧版分类ID，尝试查找对应URL
            category_url = ""
            for name, url in self.cateManual.items():
                if name == tid:
                    category_url = url
                    break
            
            if not category_url:
                self.log(f"未找到分类ID对应的URL: {tid}", "ERROR")
                result['list'] = []
                result['page'] = pg
                result['pagecount'] = 1
                result['limit'] = 0
                result['total'] = 0
                return result
                
            # 处理页码
            if pg > 1:
                if "html" in category_url:
                    category_url = category_url.replace(".html", f"/page/{pg}.html")
                else:
                    category_url = f"{category_url}/page/{pg}.html"
            
            full_url = urllib.parse.urljoin(self.siteUrl, category_url)
        
        # 请求分类页
        try:
            response = self.fetch(full_url)
            if response and response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                
                # 查找视频项，根据实际HTML结构调整
                items = soup.find_all('li', class_='item')
                
                for item in items:
                    try:
                        # 获取链接和标题
                        title_tag = item.find('h3')
                        if not title_tag:
                            continue
                        
                        title = title_tag.text.strip()
                        
                        # 获取链接
                        link_tag = item.find('a')
                        if not link_tag:
                            continue
                        
                        link = link_tag.get('href', '')
                        if not link.startswith('http'):
                            link = urllib.parse.urljoin(self.siteUrl, link)
                        
                        # 提取ID
                        vid = self.extractVodId(link)
                        if not vid:
                            continue
                        
                        # 获取图片
                        img_tag = item.find('img')
                        img_url = ""
                        if img_tag:
                            img_url = img_tag.get('src', img_tag.get('data-src', ''))
                            if img_url and not img_url.startswith('http'):
                                img_url = urllib.parse.urljoin(self.siteUrl, img_url)
                        
                        # 获取备注信息
                        remarks = ""
                        remarks_tag = item.find('span', class_='remarks')
                        if remarks_tag:
                            remarks = remarks_tag.text.strip()
                        
                        # 获取标签信息
                        tags = ""
                        tags_tag = item.find('span', class_='tags')
                        if tags_tag:
                            tags = tags_tag.text.strip()
                        
                        # 合并备注和标签
                        if remarks and tags:
                            remarks = f"{remarks} | {tags}"
                        elif tags:
                            remarks = tags
                        
                        # 构建视频项
                        videos.append({
                            'vod_id': vid,
                            'vod_name': title,
                            'vod_pic': img_url,
                            'vod_remarks': remarks
                        })
                    except Exception as e:
                        self.log(f"处理分类视频项时出错: {str(e)}", "ERROR")
                        continue
                
                # 查找分页信息
                # 默认值
                total = len(videos)
                pagecount = 1
                limit = 20
                
                # 尝试查找分页元素
                pagination = soup.find('ul', class_='page')
                if pagination:
                    # 查找最后一页的链接
                    last_page_links = pagination.find_all('a')
                    for link in last_page_links:
                        page_text = link.text.strip()
                        if page_text.isdigit():
                            pagecount = max(pagecount, int(page_text))
        except Exception as e:
            self.log(f"获取分类内容发生错误: {str(e)}", "ERROR")
        
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = pagecount
        result['limit'] = limit
        result['total'] = total
        
        return result
    
    def detailContent(self, ids):
        """获取详情内容"""
        result = {}
        
        if not ids or len(ids) == 0:
            return result
            
        # 视频ID
        vid = ids[0]
        
        # 构建播放页URL
        play_url = f"{self.siteUrl}/index.php/vod/play/id/{vid}/sid/1/nid/1.html"
        
        try:
            response = self.fetch(play_url)
            if not response or response.status_code != 200:
                return result
                
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            # 提取视频基本信息
            # 标题
            title = ""
            title_tag = soup.find('h1', class_='items-title')
            if title_tag:
                title = title_tag.text.strip()
            
            # 图片
            pic = ""
            pic_tag = soup.find('img', class_='thumb')
            if pic_tag:
                pic = pic_tag.get('src', '')
                if pic and not pic.startswith('http'):
                    pic = urllib.parse.urljoin(self.siteUrl, pic)
            
            # 简介
            desc = ""
            desc_tag = soup.find('div', class_='text-content')
            if desc_tag:
                desc = desc_tag.text.strip()
            
            # 标签/分类
            tags = []
            tags_container = soup.find('span', class_='items-tags')
            if tags_container:
                tag_links = tags_container.find_all('a')
                for tag in tag_links:
                    tag_text = tag.text.strip()
                    if tag_text:
                        tags.append(tag_text)
            
            # 提取播放列表
            play_from = "偷乐短剧"
            play_list = []
            
            # 查找播放列表区域
            play_area = soup.find('div', class_='swiper-wrapper')
            if play_area:
                # 查找所有剧集链接
                episode_links = play_area.find_all('a')
                for ep in episode_links:
                    ep_title = ep.text.strip()
                    ep_url = ep.get('href', '')
                    
                    if ep_url:
                        # 直接使用URL作为ID
                        if not ep_url.startswith('http'):
                            ep_url = urllib.parse.urljoin(self.siteUrl, ep_url)
                        
                        # 提取集数信息
                        ep_num = ep_title
                        if ep_num.isdigit():
                            ep_num = f"第{ep_num}集"
                        
                        play_list.append(f"{ep_num}${ep_url}")
            
            # 如果没有找到播放列表，查找播放按钮
            if not play_list:
                play_btn = soup.find('a', class_='btn-play')
                if play_btn:
                    play_url = play_btn.get('href', '')
                    if play_url:
                        if not play_url.startswith('http'):
                            play_url = urllib.parse.urljoin(self.siteUrl, play_url)
                        
                        play_list.append(f"播放${play_url}")
            
            # 如果仍然没有找到播放链接，使用播放页URL
            if not play_list:
                play_url = f"{self.siteUrl}/index.php/vod/play/id/{vid}/sid/1/nid/1.html"
                play_list.append(f"播放${play_url}")
            
            # 提取更多信息（导演、演员等）
            director = ""
            actor = ""
            year = ""
            area = ""
            remarks = ""
            
            # 查找备注信息
            meta_items = soup.find_all('div', class_='meta-item')
            for item in meta_items:
                item_title = item.find('span', class_='item-title')
                item_content = item.find('span', class_='item-content')
                
                if item_title and item_content:
                    title_text = item_title.text.strip()
                    content_text = item_content.text.strip()
                    
                    if "导演" in title_text:
                        director = content_text
                    elif "主演" in title_text:
                        actor = content_text
                    elif "年份" in title_text:
                        year = content_text
                    elif "地区" in title_text:
                        area = content_text
                    elif "简介" in title_text:
                        if not desc:
                            desc = content_text
                    elif "状态" in title_text:
                        remarks = content_text
            
            # 如果没有从meta-item中获取到remarks
            if not remarks:
                remarks_tag = soup.find('span', class_='remarks')
                if remarks_tag:
                    remarks = remarks_tag.text.strip()
            
            # 构建标准数据结构
            vod = {
                "vod_id": vid,
                "vod_name": title,
                "vod_pic": pic,
                "vod_year": year,
                "vod_area": area,
                "vod_remarks": remarks,
                "vod_actor": actor,
                "vod_director": director,
                "vod_content": desc,
                "type_name": ",".join(tags),
                "vod_play_from": play_from,
                "vod_play_url": "#".join(play_list)
            }
            
            result = {
                'list': [vod]
            }
        except Exception as e:
            self.log(f"获取详情内容时出错: {str(e)}", "ERROR")
        
        return result
    
    def searchContent(self, key, quick, pg=1):
        """搜索功能"""
        result = {}
        videos = []
        
        # 构建搜索URL和参数
        search_url = f"{self.siteUrl}/index.php/vod/search.html"
        params = {"wd": key}
        
        try:
            response = self.fetch(search_url, data=params)
            if response and response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                
                # 查找搜索结果项
                search_items = soup.find_all('li', class_='item')
                
                for item in search_items:
                    try:
                        # 获取标题
                        title_tag = item.find('h3')
                        if not title_tag:
                            continue
                        
                        title = title_tag.text.strip()
                        
                        # 获取链接
                        link_tag = item.find('a')
                        if not link_tag:
                            continue
                        
                        link = link_tag.get('href', '')
                        if not link.startswith('http'):
                            link = urllib.parse.urljoin(self.siteUrl, link)
                        
                        # 提取视频ID
                        vid = self.extractVodId(link)
                        if not vid:
                            continue
                        
                        # 获取图片
                        img_tag = item.find('img')
                        img_url = ""
                        if img_tag:
                            img_url = img_tag.get('src', img_tag.get('data-src', ''))
                            if img_url and not img_url.startswith('http'):
                                img_url = urllib.parse.urljoin(self.siteUrl, img_url)
                        
                        # 获取备注信息
                        remarks = ""
                        remarks_tag = item.find('span', class_='remarks')
                        if remarks_tag:
                            remarks = remarks_tag.text.strip()
                        
                        # 获取标签信息
                        tags = ""
                        tags_tag = item.find('span', class_='tags')
                        if tags_tag:
                            tags = tags_tag.text.strip()
                        
                        # 合并备注和标签
                        if remarks and tags:
                            remarks = f"{remarks} | {tags}"
                        elif tags:
                            remarks = tags
                        
                        # 构建视频项
                        videos.append({
                            'vod_id': vid,
                            'vod_name': title,
                            'vod_pic': img_url,
                            'vod_remarks': remarks
                        })
                    except Exception as e:
                        self.log(f"处理搜索结果时出错: {str(e)}", "ERROR")
                        continue
        except Exception as e:
            self.log(f"搜索功能发生错误: {str(e)}", "ERROR")
        
        result['list'] = videos
        return result
    
    def searchContentPage(self, key, quick, pg=1):
        return self.searchContent(key, quick, pg)
    
    def playerContent(self, flag, id, vipFlags):
        """获取播放内容"""
        result = {}
        
        try:
            # 判断是否已经是视频URL
            if self.isVideoFormat(id):
                result["parse"] = 0
                result["url"] = id
                result["playUrl"] = ""
                result["header"] = json.dumps(self.headers)
                return result
            
            # 判断是否是完整的页面URL
            if id.startswith(('http://', 'https://')):
                play_url = id
            # 尝试作为相对路径处理
            elif id.startswith('/'):
                play_url = urllib.parse.urljoin(self.siteUrl, id)
            # 假设是视频ID，构建播放页面URL
            else:
                # 检查是否是"视频ID_集数"格式
                parts = id.split('_')
                if len(parts) > 1 and parts[0].isdigit():
                    vid = parts[0]
                    nid = parts[1]
                    play_url = f"{self.siteUrl}/index.php/vod/play/id/{vid}/sid/1/nid/{nid}.html"
                else:
                    # 直接当作视频ID处理
                    play_url = f"{self.siteUrl}/index.php/vod/play/id/{id}/sid/1/nid/1.html"
            
            # 访问播放页获取真实播放地址
            try:
                self.log(f"正在解析播放页面: {play_url}")
                response = self.fetch(play_url)
                if response and response.status_code == 200:
                    html = response.text
                    
                    # 查找player_aaaa变量
                    player_match = re.search(r'var\s+player_aaaa\s*=\s*({.*?});', html, re.DOTALL)
                    if player_match:
                        try:
                            player_data = json.loads(player_match.group(1))
                            if 'url' in player_data:
                                video_url = player_data['url']
                                if not video_url.startswith('http'):
                                    video_url = urllib.parse.urljoin(self.siteUrl, video_url)
                                
                                self.log(f"从player_aaaa获取到视频地址: {video_url}")
                                result["parse"] = 0
                                result["url"] = video_url
                                result["playUrl"] = ""
                                result["header"] = json.dumps(self.headers)
                                return result
                        except json.JSONDecodeError as e:
                            self.log(f"解析player_aaaa JSON出错: {str(e)}", "ERROR")
                    
                    # 如果player_aaaa解析失败，尝试其他方式
                    # 1. 查找video标签
                    video_match = re.search(r'<video[^>]*src=["\'](.*?)["\']', html)
                    if video_match:
                        video_url = video_match.group(1)
                        if not video_url.startswith('http'):
                            video_url = urllib.parse.urljoin(self.siteUrl, video_url)
                        
                        self.log(f"从video标签找到视频地址: {video_url}")
                        result["parse"] = 0
                        result["url"] = video_url
                        result["playUrl"] = ""
                        result["header"] = json.dumps(self.headers)
                        return result
                    
                    # 2. 查找iframe
                    iframe_match = re.search(r'<iframe[^>]*src=["\'](.*?)["\']', html)
                    if iframe_match:
                        iframe_url = iframe_match.group(1)
                        if not iframe_url.startswith('http'):
                            iframe_url = urllib.parse.urljoin(self.siteUrl, iframe_url)
                        
                        self.log(f"找到iframe，正在解析: {iframe_url}")
                        # 访问iframe内容
                        iframe_response = self.fetch(iframe_url)
                        if iframe_response and iframe_response.status_code == 200:
                            iframe_html = iframe_response.text
                            
                            # 在iframe内容中查找视频地址
                            iframe_video_match = re.search(r'(https?://[^\'"]+\.(mp4|m3u8|ts))', iframe_html)
                            if iframe_video_match:
                                video_url = iframe_video_match.group(1)
                                
                                self.log(f"从iframe中找到视频地址: {video_url}")
                                result["parse"] = 0
                                result["url"] = video_url
                                result["playUrl"] = ""
                                result["header"] = json.dumps({
                                    "User-Agent": self.headers["User-Agent"],
                                    "Referer": iframe_url
                                })
                                return result
                    
                    # 3. 查找任何可能的视频URL
                    url_match = re.search(r'(https?://[^\'"]+\.(mp4|m3u8|ts))', html)
                    if url_match:
                        video_url = url_match.group(1)
                        
                        self.log(f"找到可能的视频地址: {video_url}")
                        result["parse"] = 0
                        result["url"] = video_url
                        result["playUrl"] = ""
                        result["header"] = json.dumps(self.headers)
                        return result
            except Exception as e:
                self.log(f"解析播放地址时出错: {str(e)}", "ERROR")
            
            # 如果所有方式都失败，返回外部解析标志
            self.log("未找到直接可用的视频地址，需要外部解析", "WARNING")
            result["parse"] = 1  # 表示需要外部解析
            result["url"] = play_url  # 返回播放页面URL
            result["playUrl"] = ""
            result["header"] = json.dumps(self.headers)
            
        except Exception as e:
            self.log(f"获取播放内容时出错: {str(e)}", "ERROR")
        
        return result
    
    def localProxy(self, param):
        """本地代理"""
        return [404, "text/plain", {}, "Not Found"]
