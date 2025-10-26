# -*- coding: utf-8 -*-
import requests
import re
import json
import traceback
import sys
from urllib.parse import quote

sys.path.append('../../')
try:
    from base.spider import Spider
except ImportError:
    # 定义一个基础接口类，用于本地测试
    class Spider:
        def init(self, extend=""):
            pass

class Spider(Spider):
    def __init__(self):
        self.siteUrl = "https://www.kuaikaw.cn"
        self.cateManual = {
            "甜宠": "462",
            "古装仙侠": "1102",
            "现代言情": "1145",
            "青春": "1170",
            "豪门恩怨": "585",
            "逆袭": "417-464",
            "重生": "439-465",
            "系统": "1159",
            "总裁": "1147",
            "职场商战": "943"
        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Referer": self.siteUrl,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        
    def getName(self):
        return "河马短剧"
    
    def init(self, extend=""):
        return
    
    def fetch(self, url, headers=None, retry=2):
        """统一的网络请求接口"""
        if headers is None:
            headers = self.headers
        
        for i in range(retry + 1):
            try:
                response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
                response.raise_for_status()
                return response
            except Exception as e:
                if i == retry:
                    print(f"请求异常: {url}, 错误: {str(e)}")
                    return None
                continue
    
    def isVideoFormat(self, url):
        video_formats = ['.mp4', '.mkv', '.avi', '.wmv', '.m3u8', '.flv', '.rmvb']
        return any(format in url.lower() for format in video_formats)
    
    def manualVideoCheck(self):
        return False
    
    def homeContent(self, filter):
        result = {}
        classes = [{'type_name': k, 'type_id': v} for k, v in self.cateManual.items()]
        result['class'] = classes
        
        try:
            result['list'] = self.homeVideoContent()['list']
        except:
            result['list'] = []
        return result
    
    def homeVideoContent(self):
        videos = []
        try:
            response = self.fetch(self.siteUrl)
            if not response:
                return {'list': []}
                
            html_content = response.text
            next_data_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
            next_data_match = re.search(next_data_pattern, html_content, re.DOTALL)
            if not next_data_match:
                return {'list': []}
                
            next_data_json = json.loads(next_data_match.group(1))
            page_props = next_data_json.get("props", {}).get("pageProps", {})
            
            # 处理轮播图数据
            if "bannerList" in page_props:
                for banner in page_props["bannerList"]:
                    if banner.get("bookId"):
                        videos.append({
                            "vod_id": f"/drama/{banner['bookId']}",
                            "vod_name": banner.get("bookName", ""),
                            "vod_pic": banner.get("coverWap", ""),
                            "vod_remarks": f"{banner.get('statusDesc', '')} {banner.get('totalChapterNum', '')}集".strip()
                        })
            
            # 处理SEO分类推荐
            if "seoColumnVos" in page_props:
                for column in page_props["seoColumnVos"]:
                    for book in column.get("bookInfos", []):
                        if book.get("bookId"):
                            videos.append({
                                "vod_id": f"/drama/{book['bookId']}",
                                "vod_name": book.get("bookName", ""),
                                "vod_pic": book.get("coverWap", ""),
                                "vod_remarks": f"{book.get('statusDesc', '')} {book.get('totalChapterNum', '')}集".strip()
                            })
            
            # 去重处理
            seen = set()
            unique_videos = []
            for video in videos:
                key = (video["vod_id"], video["vod_name"])
                if key not in seen:
                    seen.add(key)
                    unique_videos.append(video)
        
        except Exception as e:
            print(f"获取首页推荐内容出错: {e}")
            unique_videos = []
        
        return {'list': unique_videos}
    
    def categoryContent(self, tid, pg, filter, extend):
        result = {'list': [], 'page': pg, 'pagecount': 1, 'limit': 20, 'total': 0}
        url = f"{self.siteUrl}/browse/{tid}/{pg}"
        
        response = self.fetch(url)
        if not response:
            return result
            
        html_content = response.text
        next_data_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_content, re.DOTALL)
        if not next_data_match:
            return result
            
        try:
            next_data_json = json.loads(next_data_match.group(1))
            page_props = next_data_json.get("props", {}).get("pageProps", {})
            
            current_page = page_props.get("page", 1)
            total_pages = page_props.get("pages", 1)
            book_list = page_props.get("bookList", [])
            
            videos = []
            for book in book_list:
                if book.get("bookId"):
                    videos.append({
                        "vod_id": f"/drama/{book['bookId']}",
                        "vod_name": book.get("bookName", ""),
                        "vod_pic": book.get("coverWap", ""),
                        "vod_remarks": f"{book.get('statusDesc', '')} {book.get('totalChapterNum', '')}集".strip()
                    })
            
            result.update({
                'list': videos,
                'page': int(current_page),
                'pagecount': total_pages,
                'limit': len(videos),
                'total': len(videos) * total_pages if videos else 0
            })
            
        except Exception as e:
            print(f"分类内容获取出错: {e}")
            
        return result
    
    def searchContent(self, key, quick, pg=1):
        return self.searchContentPage(key, quick, pg)
    
    def searchContentPage(self, key, quick, pg=1):
        result = {'list': [], 'page': pg, 'pagecount': 1, 'limit': 20, 'total': 0}
        search_url = f"{self.siteUrl}/search?searchValue={quote(key)}&page={pg}"
        
        response = self.fetch(search_url)
        if not response:
            return result
            
        html_content = response.text
        next_data_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_content, re.DOTALL)
        if not next_data_match:
            return result
            
        try:
            next_data_json = json.loads(next_data_match.group(1))
            page_props = next_data_json.get("props", {}).get("pageProps", {})
            
            total_pages = page_props.get("pages", 1)
            book_list = page_props.get("bookList", [])
            
            videos = []
            for book in book_list:
                if book.get("bookId"):
                    videos.append({
                        "vod_id": f"/drama/{book['bookId']}",
                        "vod_name": book.get("bookName", ""),
                        "vod_pic": book.get("coverWap", ""),
                        "vod_remarks": f"{book.get('statusDesc', '')} {book.get('totalChapterNum', '')}集".strip()
                    })
            
            result.update({
                'list': videos,
                'pagecount': total_pages,
                'total': len(videos) * total_pages if videos else 0
            })
            
        except Exception as e:
            print(f"搜索内容出错: {e}")
            
        return result

    def detailContent(self, ids):
        result = {'list': []}
        if not ids:
            return result
            
        vod_id = ids[0]
        if not vod_id.startswith('/drama/'):
            vod_id = f'/drama/{vod_id}'
        
        drama_url = f"{self.siteUrl}{vod_id}"
        response = self.fetch(drama_url)
        if not response:
            return result
            
        html = response.text
        next_data_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
        if not next_data_match:
            return result
            
        try:
            next_data = json.loads(next_data_match.group(1))
            page_props = next_data.get("props", {}).get("pageProps", {})
            book_info = page_props.get("bookInfoVo", {})
            chapter_list = page_props.get("chapterList", [])
            
            if not book_info.get("bookId"):
                return result
            
            # 基本信息
            categories = [c.get("name", "") for c in book_info.get("categoryList", [])]
            performers = [p.get("name", "") for p in book_info.get("performerList", [])]
            
            vod = {
                "vod_id": vod_id,
                "vod_name": book_info.get("title", ""),
                "vod_pic": book_info.get("coverWap", ""),
                "type_name": ",".join(categories),
                "vod_year": "",
                "vod_area": book_info.get("countryName", ""),
                "vod_remarks": f"{book_info.get('statusDesc', '')} {book_info.get('totalChapterNum', '')}集".strip(),
                "vod_actor": ", ".join(performers),
                "vod_director": "",
                "vod_content": book_info.get("introduction", "")
            }
            
            # 处理剧集
            play_urls = self.processEpisodes(vod_id, chapter_list)
            if play_urls:
                vod['vod_play_from'] = '河马剧场'
                vod['vod_play_url'] = '$$$'.join(play_urls)
            
            result['list'] = [vod]
            
        except Exception as e:
            print(f"详情页解析出错: {e}")
            traceback.print_exc()
            
        return result
    
    def processEpisodes(self, vod_id, chapter_list):
        play_urls = []
        episodes = []
        
        for chapter in chapter_list:
            chapter_id = chapter.get("chapterId", "")
            chapter_name = chapter.get("chapterName", "")
            
            if not chapter_id or not chapter_name:
                continue
                
            # 尝试获取直接视频链接
            video_url = self.getDirectVideoUrl(chapter)
            if video_url:
                episodes.append(f"{chapter_name}${video_url}")
                continue
                
            # 回退方案
            episodes.append(f"{chapter_name}${vod_id}${chapter_id}${chapter_name}")
        
        if episodes:
            play_urls.append("#".join(episodes))
        
        return play_urls
    
    def getDirectVideoUrl(self, chapter):
        if "chapterVideoVo" not in chapter or not chapter["chapterVideoVo"]:
            return None
            
        video_info = chapter["chapterVideoVo"]
        for key in ["mp4", "mp4720p", "vodMp4Url"]:
            if key in video_info and video_info[key] and ".mp4" in video_info[key].lower():
                return video_info[key]
        return None

    def playerContent(self, flag, id, vipFlags):
        result = {
            "parse": 0,
            "url": id,
            "header": json.dumps(self.headers)
        }
        
        # 如果已经是视频链接直接返回
        if 'http' in id and ('.mp4' in id or '.m3u8' in id):
            return result
            
        # 解析参数
        parts = id.split('$')
        if len(parts) < 2:
            return result
            
        drama_id = parts[0].replace('/drama/', '')
        chapter_id = parts[1]
        
        # 尝试获取视频链接
        video_url = self.getEpisodeVideoUrl(drama_id, chapter_id)
        if video_url:
            result["url"] = video_url
            
        return result
    
    def getEpisodeVideoUrl(self, drama_id, chapter_id):
        episode_url = f"{self.siteUrl}/episode/{drama_id}/{chapter_id}"
        response = self.fetch(episode_url)
        if not response:
            return None
            
        html = response.text
        
        # 方法1: 从NEXT_DATA提取
        next_data_match = re.search(r'<script id="__NEXT_DATA__".*?>(.*?)</script>', html, re.DOTALL)
        if next_data_match:
            try:
                next_data = json.loads(next_data_match.group(1))
                page_props = next_data.get("props", {}).get("pageProps", {})
                chapter_info = page_props.get("chapterInfo", {})
                
                if chapter_info and "chapterVideoVo" in chapter_info:
                    video_info = chapter_info["chapterVideoVo"]
                    for key in ["mp4", "mp4720p", "vodMp4Url"]:
                        if key in video_info and video_info[key] and ".mp4" in video_info[key].lower():
                            return video_info[key]
            except:
                pass
                
        # 方法2: 直接从HTML提取
        mp4_matches = re.findall(r'(https?://[^"\']+\.mp4)', html)
        if mp4_matches:
            for url in mp4_matches:
                if chapter_id in url or drama_id in url:
                    return url
            return mp4_matches[0]
            
        return None

    def localProxy(self, param):
        return [200, "video/MP2T", {}, param]

    def destroy(self):
        pass