# coding=utf-8
#!/usr/bin/env python3
# 影视工厂定制版 - 修复播放链接提取和搜索功能
import re
import sys
import time
import urllib.parse
import requests
from bs4 import BeautifulSoup
import json

# 禁用SSL证书验证警告
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.append('..')
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        return "影视工厂"
    
    def init(self, extend=""):
        self.host = "http://1.ysgc.top/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 
            'Referer': self.host
        }
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update(self.headers)
        # 添加重试机制
        self.retry_count = 3
        self.timeout = 30

    def fetch(self, url, timeout=None):
        if timeout is None:
            timeout = self.timeout
            
        for i in range(self.retry_count):
            try:
                response = self.session.get(url, timeout=timeout, verify=False)
                response.encoding = 'utf-8'
                if response.status_code == 200:
                    return response
                else:
                    print(f"请求失败，状态码: {response.status_code}")
            except Exception as e:
                print(f"请求失败 ({i+1}/{self.retry_count}): {e}")
                if i < self.retry_count - 1:
                    time.sleep(1)  # 等待1秒后重试
        return None

    def homeContent(self, filter):
        result = {
            "class": [
                {'type_id': '1', 'type_name': '电影'},
                {'type_id': '2', 'type_name': '连续剧'},
                {'type_id': '3', 'type_name': '综艺'},
                {'type_id': '4', 'type_name': '动漫'},
                {'type_id': '41', 'type_name': '短剧'},
                {'type_id': '40', 'type_name': '其他综合'}
            ],
            "filters": self._get_filters(),
            "list": []
        }
        
        rsp = self.fetch(self.host)
        if rsp and rsp.status_code == 200:
            result['list'] = self._extract_videos_from_html(rsp.text)
        return result

    def categoryContent(self, tid, pg, filter, extend):
        result = {"list": [], "page": int(pg), "pagecount": 99, "limit": 20, "total": 1980}
        url = f"{self.host}/vodtype/{tid}-{pg}.html" if int(pg) > 1 else f"{self.host}/vodtype/{tid}.html"
        
        # 处理筛选条件
        if extend and 'class' in extend:
            class_filter = extend['class']
            if class_filter:
                url = url.replace(f"{tid}-{pg}", f"{class_filter}-{pg}")
        
        rsp = self.fetch(url)
        if rsp and rsp.status_code == 200:
            result['list'] = self._extract_videos_from_html(rsp.text)
        return result

    def searchContent(self, key, quick, pg=1):
        result = {"list": []}
        search_key = urllib.parse.quote(key)
        
        # 只使用API接口进行搜索
        api_url = f"{self.host}/index.php/ajax/suggest?mid=1&wd={search_key}&limit=500"
        rsp = self.fetch(api_url)
        
        if rsp and rsp.status_code == 200:
            try:
                # 解析JSON响应
                data = json.loads(rsp.text)
                videos = []
                
                # 修复：正确获取列表数据
                if 'list' in data:
                    items = data['list']
                    print(f"搜索到 {len(items)} 条结果")  # 调试信息
                    
                    for item in items:
                        # 提取视频ID
                        vid = str(item.get('id', ''))
                        if not vid:
                            continue
                        
                        # 修复：正确获取标题字段
                        title = item.get('name', '')
                        
                        # 修复：正确获取图片
                        pic = item.get('pic', '')
                        if pic and not pic.startswith('http'):
                            if pic.startswith('//'):
                                pic = 'http:' + pic
                            elif pic.startswith('/'):
                                pic = self.host.rstrip('/') + pic
                            else:
                                pic = self.host + pic
                        
                        # 修复：正确获取备注
                        note = item.get('en', '')
                        
                        videos.append({
                            'vod_id': vid,
                            'vod_name': title,
                            'vod_pic': pic,
                            'vod_remarks': note
                        })
                
                # 分页处理
                page_size = 20
                start_idx = (int(pg) - 1) * page_size
                end_idx = start_idx + page_size
                
                result['list'] = videos[start_idx:end_idx]
                result['page'] = int(pg)
                result['pagecount'] = (len(videos) + page_size - 1) // page_size
                result['limit'] = page_size
                result['total'] = len(videos)
                
            except json.JSONDecodeError:
                print("JSON解析失败，搜索无结果")
                # 打印原始响应以便调试
                print(f"原始响应: {rsp.text[:200]}...")
            except Exception as e:
                print(f"搜索处理异常: {e}")
                # 打印原始响应以便调试
                print(f"原始响应: {rsp.text[:200]}...")
        else:
            print(f"API请求失败: 状态码 {rsp.status_code if rsp else '无响应'}")
        
        return result

    def detailContent(self, ids):
        result = {"list": []}
        vid = ids[0]
        url = f"{self.host}/voddetail/{vid}.html"
        rsp = self.fetch(url)
        if not rsp or rsp.status_code != 200:
            return result
            
        html = rsp.text
        play_from, play_url = self._extract_play_info(html, vid)
        
        if play_from and play_url:
            result['list'] = [{
                'vod_id': vid,
                'vod_name': self._extract_title(html),
                'vod_pic': self._extract_pic(html),
                'type_name': self._extract_category(html),
                'vod_year': self._extract_year(html),
                'vod_area': self._extract_area(html),
                'vod_actor': self._extract_actor(html),
                'vod_director': self._extract_director(html),
                'vod_content': self._extract_desc(html),
                'vod_remarks': self._extract_remarks(html),
                'vod_play_from': "$$$".join(play_from),
                'vod_play_url': "$$$".join(play_url)
            }]
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {"parse": 1, "playUrl": "", "url": ""}
        if "-" not in id:
            return result
            
        rsp = self.fetch(f"{self.host}/vodplay/{id}.html")
        if not rsp or rsp.status_code != 200:
            return result
            
        # 尝试从播放页面提取m3u8地址
        m3u8_match = re.search(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', rsp.text)
        if m3u8_match:
            result["parse"] = 0
            result["url"] = m3u8_match.group(1)
        else:
            # 尝试从JavaScript变量中提取
            js_matches = re.findall(r'(https?://[^"\']+\.m3u8[^"\']*)', rsp.text)
            if js_matches:
                result["parse"] = 0
                result["url"] = js_matches[0]
            else:
                # 如果没有找到直接链接，可能需要进一步解析
                result["url"] = f"{self.host}/vodplay/{id}.html"
        return result

    def _get_filters(self):
        return {
            "1": [{"key": "class", "name": "类型", "value": [
                {"n": "全部", "v": ""}, {"n": "动作片", "v": "6"}, {"n": "喜剧片", "v": "7"},
                {"n": "爱情片", "v": "8"}, {"n": "科幻片", "v": "9"}, {"n": "恐怖片", "v": "11"},
                {"n": "剧情片", "v": "10"}, {"n": "战争片", "v": "12"}, {"n": "纪录片", "v": "21"},
                {"n": "悬疑片", "v": "32"}, {"n": "动画片", "v": "33"}, {"n": "犯罪片", "v": "34"},
                {"n": "奇幻片", "v": "35"}, {"n": "其他片", "v": "60"}
            ]}],
            "2": [{"key": "class", "name": "类型", "value": [
                {"n": "全部", "v": ""}, {"n": "国产剧", "v": "13"}, {"n": "港台剧", "v": "14"},
                {"n": "日剧", "v": "15"}, {"n": "韩剧", "v": "33"}, {"n": "欧美剧", "v": "16"},
                {"n": "海外剧", "v": "17"}
            ]}],
            "3": [{"key": "class", "name": "类型", "value": [
                {"n": "全部", "v": ""}, {"n": "内地综艺", "v": "27"}, {"n": "港台综艺", "v": "28"},
                {"n": "日本综艺", "v": "29"}, {"n": "韩国综艺", "v": "36"}, {"n": "欧美综艺", "v": "30"}
            ]}],
            "4": [{"key": "class", "name": "类型", "value": [
                {"n": "全部", "v": ""}, {"n": "国产动漫", "v": "31"}, {"n": "日本动漫", "v": "32"},
                {"n": "欧美动漫", "v": "42"}, {"n": "其他动漫", "v": "43"}
            ]}]
        }

    def _extract_videos_from_html(self, html):
        videos = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # 修复：使用更通用的选择器匹配视频项
        # 根据实际网站结构调整选择器
        module_items = soup.select('.module-item, .module-card-item, .module-items .module-item, .module-list .module-item')
        
        # 如果以上选择器找不到，尝试更通用的选择器
        if not module_items:
            module_items = soup.select('.module-blocklist .module-blocklist-item, .module-list .module-item, .module-items .module-item')
        
        for item in module_items:
            # 查找链接
            link = item.select_one('a[href*="/vodplay/"], a[href*="/voddetail/"], .module-item-pic a, .module-item-titlebox a, .title a')
            
            if not link:
                continue
                
            href = link.get('href', '')
            # 提取视频ID
            vid_match = re.search(r'/vod(?:play|detail)/(\d+)(?:-|\d|\.)*', href)
            if not vid_match:
                continue
                
            vid = vid_match.group(1)
            
            # 提取标题
            title = ""
            title_elem = item.select_one('.module-item-title, .video-name, .title, .module-item-style.video-name, .module-item-titlebox .module-item-title')
            if title_elem:
                title = title_elem.get_text(strip=True)
            
            # 提取图片
            pic = ""
            img_elem = item.select_one('img, .module-item-pic img, .lazy, .cover img')
            if img_elem:
                pic = img_elem.get('data-src') or img_elem.get('src') or ""
                pic = self._fix_url(pic)
                    
            # 提取备注/年份/类型/地区
            note = ""
            note_elem = item.select_one('.module-item-text, .video-remarks, .remarks, .module-item-caption, .note')
            if note_elem:
                note = note_elem.get_text(strip=True)
            
            videos.append({
                'vod_id': vid,
                'vod_name': title,
                'vod_pic': pic,
                'vod_remarks': note
            })
        
        return videos

    def _extract_play_info(self, html, vid):
        play_from, play_url = [], []
        soup = BeautifulSoup(html, 'html.parser')
        
        # 核心修复：使用更简单直接的方式提取播放链接
        # 定位播放列表容器 - 优先查找特定类名
        playlist_container = soup.select_one('.module-blocklist.scroll-box.scroll-box-y')
        
        # 如果找不到特定容器，尝试备用选择器
        if not playlist_container:
            playlist_container = soup.select_one('.player-side-playlist, .player-box-side, .player-info')
        
        # 如果还是找不到，使用整个页面
        if not playlist_container:
            playlist_container = soup
        
        # 查找播放源名称（如"腾讯"）
        source_tabs = soup.select('.module-tab-name span, .module-tab-value')
        source_names = [tab.get_text(strip=True) for tab in source_tabs] if source_tabs else ["腾讯"]
        
        # 查找所有集数链接
        episode_links = playlist_container.select('a[href*="/vodplay/"]') if playlist_container else []
        
        # 按播放源分组
        if source_names:
            episodes = []
            for link in episode_links:
                href = link.get('href', '')
                # 确保链接包含当前视频ID
                if f'/vodplay/{vid}' in href:
                    # 提取集数标题 - 优先从span标签获取
                    span = link.select_one('span')
                    if span:
                        ep_name = span.get_text(strip=True)
                    else:
                        ep_name = link.get_text(strip=True) or f"第{len(episodes)+1}集"
                    
                    # 提取集数ID
                    ep_id = href.split('/')[-1].replace('.html', '')
                    
                    # 格式化播放项
                    episodes.append(f"{ep_name}${ep_id}")
            
            if episodes:
                play_from = source_names
                play_url = ["#".join(episodes)]
        
        return play_from, play_url

    def _extract_title(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        title_elem = soup.select_one('title, .video-info-title, .module-heading h1, .page-title, h1.video-title')
        if title_elem:
            title = title_elem.get_text(strip=True)
            # 移除网站名称部分
            return re.split(r'[-|_]', title)[0].strip()
        return "未知标题"

    def _extract_pic(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        img_elem = soup.select_one('.module-item-pic img, .video-cover img, .detail-pic img, .lazy, img[data-src], img[src]')
        if img_elem:
            pic = img_elem.get('data-src') or img_elem.get('src') or ""
            return self._fix_url(pic)
        return ""

    def _extract_category(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        category_elem = soup.select_one('.video-info-class, .video-category, .category, .module-item-caption .video-class')
        if category_elem:
            return category_elem.get_text(strip=True)
        return ""

    def _extract_year(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        # 尝试从详情信息中提取年份
        info_elems = soup.select('.video-info-items, .video-info, .info, .module-item-caption')
        for elem in info_elems:
            text = elem.get_text()
            year_match = re.search(r'年份[：:]\s*(\d{4})', text)
            if year_match:
                return year_match.group(1)
            
            # 尝试从文本中直接匹配年份
            year_match = re.search(r'\b(19|20)\d{2}\b', text)
            if year_match:
                return year_match.group(0)
        return ""

    def _extract_area(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        # 尝试从详情信息中提取地区
        info_elems = soup.select('.video-info-items, .video-info, .info, .module-item-caption')
        for elem in info_elems:
            text = elem.get_text()
            area_match = re.search(r'地区[：:]\s*([^\s]+)', text)
            if area_match:
                return area_match.group(1)
        return ""

    def _extract_actor(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        # 尝试从详情信息中提取演员
        info_elems = soup.select('.video-info-items, .video-info, .info, .video-tag')
        for elem in info_elems:
            text = elem.get_text()
            actor_match = re.search(r'主演[：:]\s*([^<]+)', text)
            if actor_match:
                return actor_match.group(1).strip()
            
            # 如果没有明确的主演标签，尝试提取所有演员
            actors = []
            actor_links = elem.select('a')
            for link in actor_links:
                actors.append(link.get_text(strip=True))
            if actors:
                return " / ".join(actors)
        return ""

    def _extract_director(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        # 尝试从详情信息中提取导演
        info_elems = soup.select('.video-info-items, .video-info, .info')
        for elem in info_elems:
            text = elem.get_text()
            director_match = re.search(r'导演[：:]\s*([^<]+)', text)
            if director_match:
                return director_match.group(1).strip()
        return ""

    def _extract_desc(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        desc_elem = soup.select_one('.video-info-content, .video-info-intro, .module-item-style.video-text, .desc, .video-text')
        if desc_elem:
            return desc_elem.get_text(strip=True)
        return "暂无简介"

    def _extract_remarks(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        remark_elem = soup.select_one('.video-info-remarks, .module-item-text, .video-remarks, .remarks')
        if remark_elem:
            return remark_elem.get_text(strip=True)
        return ""

    def _fix_url(self, url):
        if not url:
            return ""
        if url.startswith('//'):
            return 'http:' + url
        if url.startswith('/'):
            return self.host.rstrip('/') + url
        if not url.startswith('http'):
            return self.host + url
        return url

# 本地测试
if __name__ == "__main__":
    spider = Spider()
    spider.init()
    
    # 测试首页
    home_result = spider.homeContent({})
    print(f"首页分类: {[c['type_name'] for c in home_result['class']]}")
    print(f"首页视频数量: {len(home_result['list'])}")
    
    # 测试搜索功能
    print("\n测试搜索功能：")
    search_result = spider.searchContent("仙逆", False, 1)
    print(f"搜索结果数量: {len(search_result['list'])}")
    for i, item in enumerate(search_result['list'], 1):
        print(f"{i}. 标题: {item['vod_name']}, ID: {item['vod_id']}, 图片: {item['vod_pic']}")
    
    # 测试详情页（如果搜索结果存在）
    if search_result['list']:
        first_video = search_result['list'][0]
        detail_result = spider.detailContent([first_video['vod_id']])
        if detail_result['list']:
            video_info = detail_result['list'][0]
            print(f"\n视频详情:")
            print(f"标题: {video_info['vod_name']}")
            print(f"类型: {video_info['type_name']}")
            print(f"年份: {video_info['vod_year']}")
            print(f"地区: {video_info['vod_area']}")
            print(f"演员: {video_info['vod_actor']}")
            print(f"导演: {video_info['vod_director']}")
            print(f"简介: {video_info['vod_content'][:100]}...")
            print(f"播放源: {video_info['vod_play_from']}")
            print(f"播放列表: {video_info['vod_play_url']}")
