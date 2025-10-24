# coding=utf-8
# !/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import json
import time
import urllib.parse
import re

class Spider(Spider):
    
    def getName(self):
        return "厂长资源"
    
    def init(self, extend=""):
        self.host = "https://www.cz233.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': self.host
        }
        self.log(f"厂长资源爬虫初始化完成，主站: {self.host}")

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        """获取首页内容和分类 - 修复版"""
        result = {}

        # 定义分类 - 基于实际网站结构（移除不存在的电视剧分类）
        classes = [
            {'type_id': 'movie_bt', 'type_name': '全部影片'},
            {'type_id': 'dyy', 'type_name': '电影'},
            {'type_id': 'guochanju', 'type_name': '国产剧'},
            {'type_id': 'mj', 'type_name': '美剧'},
            {'type_id': 'hj', 'type_name': '韩剧'},
            {'type_id': 'rj', 'type_name': '日剧'},
            {'type_id': 'hwj', 'type_name': '海外剧'},
            {'type_id': 'fjj', 'type_name': '番剧'},
            {'type_id': 'zuixindianying', 'type_name': '最新电影'},
            {'type_id': 'dbtop250', 'type_name': '豆瓣Top250'},
            {'type_id': 'dongmanjuchangban', 'type_name': '动漫剧场版'}
        ]
        result['class'] = classes

        # 添加筛选配置
        result['filters'] = self._get_filters()

        # 获取首页推荐内容
        try:
            rsp = self.fetch(self.host, headers=self.headers)
            doc = self.html(rsp.text)
            videos = self._get_videos(doc, limit=50)
            result['list'] = videos
        except Exception as e:
            self.log(f"首页获取出错: {str(e)}")
            result['list'] = []

        return result

    def homeVideoContent(self):
        """分类定义 - 兼容性方法"""
        return {
            'class': [
                {'type_id': 'movie_bt', 'type_name': '全部影片'},
                {'type_id': 'dyy', 'type_name': '电影'},
                {'type_id': 'guochanju', 'type_name': '国产剧'},
                {'type_id': 'mj', 'type_name': '美剧'},
                {'type_id': 'hj', 'type_name': '韩剧'},
                {'type_id': 'rj', 'type_name': '日剧'},
                {'type_id': 'hwj', 'type_name': '海外剧'},
                {'type_id': 'fjj', 'type_name': '番剧'},
                {'type_id': 'zuixindianying', 'type_name': '最新电影'},
                {'type_id': 'dbtop250', 'type_name': '豆瓣Top250'},
                {'type_id': 'dongmanjuchangban', 'type_name': '动漫剧场版'}
            ],
            'filters': self._get_filters()
        }

    def categoryContent(self, tid, pg, filter, extend):
        """分类内容 - 支持筛选功能"""
        try:
            # 处理筛选参数 - 将filter参数合并到extend中
            if filter and isinstance(filter, dict):
                if not extend:
                    extend = {}
                extend.update(filter)

            self.log(f"分类请求: tid={tid}, pg={pg}, extend={extend}")

            url = self._build_url(tid, pg, extend)
            if not url:
                return {'list': []}

            self.log(f"访问分类URL: {url}")
            rsp = self.fetch(url, headers=self.headers)
            doc = self.html(rsp.text)
            videos = self._get_videos(doc, limit=20)

            return {
                'list': videos,
                'page': int(pg),
                'pagecount': 999,
                'limit': 20,
                'total': 19980
            }
        except Exception as e:
            self.log(f"分类内容获取出错: {str(e)}")
            return {'list': []}

    def searchContent(self, key, quick, pg="1"):
        """搜索功能 - 智能过滤版"""
        try:
            search_url = f"{self.host}/xsss1O1?q={urllib.parse.quote(key)}"
            self.log(f"搜索URL: {search_url}")
            rsp = self.fetch(search_url, headers=self.headers)
            doc = self.html(rsp.text)

            videos = []
            seen_ids = set()
            elements = doc.xpath('//li[contains(@class,"") and .//a[contains(@href,"/movie/")]]')
            self.log(f"找到 {len(elements)} 个搜索结果元素")

            for elem in elements:
                video = self._extract_video(elem)
                if video and video['vod_id'] not in seen_ids:
                    if self._is_relevant_search_result(video['vod_name'], key):
                        videos.append(video)
                        seen_ids.add(video['vod_id'])
                        self.log(f"✅ 相关视频: {video['vod_name']} (ID: {video['vod_id']})")
                    else:
                        self.log(f"❌ 过滤无关: {video['vod_name']} (搜索: {key})")

            self.log(f"最终搜索结果: {len(videos)} 个视频")
            return {'list': videos}
        except Exception as e:
            self.log(f"搜索出错: {str(e)}")
            return {'list': []}

    def detailContent(self, ids):
        """详情页面"""
        try:
            vid = ids[0]
            detail_url = f"{self.host}/movie/{vid}.html"
            rsp = self.fetch(detail_url, headers=self.headers)
            doc = self.html(rsp.text)
            
            video_info = self._get_detail(doc, vid)
            return {'list': [video_info]} if video_info else {'list': []}
        except Exception as e:
            self.log(f"详情获取出错: {str(e)}")
            return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        """播放链接 - 包含解密功能"""
        try:
            self.log(f"获取播放链接: flag={flag}, id={id}")
            start_time = time.time()

            play_url = f"{self.host}/v_play/{id}.html"
            play_headers = self.headers.copy()
            play_headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'identity',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            })

            rsp = self.fetch(play_url, headers=play_headers)
            
            # 智能解码页面内容
            try:
                html = rsp.text if rsp.encoding else rsp.content.decode('utf-8', errors='ignore')
            except:
                try:
                    html = rsp.content.decode('gbk', errors='ignore')
                except:
                    html = rsp.content.decode('latin-1', errors='ignore')

            # 提取真实播放链接
            real_url = self._extract_real_video_url(html, play_url)

            end_time = time.time()
            self.log(f"播放链接获取完成，耗时{end_time-start_time:.2f}秒")

            # 根据获取结果返回不同的解析方式
            if real_url and any(ext in real_url.lower() for ext in ['.m3u8', '.mp4', '.flv', '.avi']):
                return {'parse': 0, 'playUrl': '', 'url': real_url}
            elif real_url and real_url.startswith('http'):
                return {'parse': 1, 'playUrl': '', 'url': real_url}
            else:
                return {'parse': 1, 'playUrl': '', 'url': play_url}
        except Exception as e:
            self.log(f"播放链接获取出错: {str(e)}")
            return {'parse': 1, 'playUrl': '', 'url': f"{self.host}/v_play/{id}.html"}

    # ========== 核心辅助方法 ==========
    
    def _is_relevant_search_result(self, title, search_key):
        """智能搜索相关性检查"""
        if not title or not search_key:
            return False

        title_lower = title.lower()
        search_key_lower = search_key.lower()

        # 直接包含搜索关键词
        if search_key_lower in title_lower:
            return True

        # 特定作品严格匹配
        specific_works = {
            '碧蓝之海': ['碧蓝之海', '碧蓝', 'grand blue'],
            '海贼王': ['海贼王', '海贼', '航海王', 'one piece'],
            '火影忍者': ['火影忍者', '火影', '忍者', 'naruto'],
            '死神': ['死神', 'bleach'],
            '进击的巨人': ['进击的巨人', '进击', '巨人'],
            '鬼灭之刃': ['鬼灭之刃', '鬼灭', '炭治郎'],
            '龙珠': ['龙珠', '悟空', 'dragon ball'],
            '蜘蛛侠': ['蜘蛛侠', 'spider-man', 'spiderman'],
            '钢铁侠': ['钢铁侠', 'iron man'],
            '复仇者联盟': ['复仇者联盟', '复仇者', 'avengers'],
            '变形金刚': ['变形金刚', 'transformers'],
            '哈利波特': ['哈利波特', 'harry potter'],
            '指环王': ['指环王', '魔戒', 'lord of the rings'],
            '星球大战': ['星球大战', '星战', 'star wars']
        }

        for work, keywords in specific_works.items():
            if work in search_key_lower:
                return any(keyword in title_lower for keyword in keywords)

        # 过滤明显不相关的内容
        irrelevant_patterns = [
            (r'海', ['盒中之海', '寂静之海', '永生之海', '石之海']),
            (r'王', ['霸王', '君王', '王者', '国王', '女王']),
            (r'龙', ['追龙', '卧虎藏龙', '龙门', '龙虎'])
        ]

        for pattern, irrelevant_list in irrelevant_patterns:
            if pattern in search_key_lower:
                for irrelevant in irrelevant_list:
                    if irrelevant in title_lower and search_key_lower not in title_lower:
                        return False

        # 字符匹配（高阈值）
        search_chars = set(search_key_lower.replace(' ', ''))
        title_chars = set(title_lower.replace(' ', ''))

        if len(search_chars) > 0:
            match_ratio = len(search_chars & title_chars) / len(search_chars)
            if match_ratio >= 0.8:
                return True

        # 短搜索词要求严格匹配
        if len(search_key_lower) <= 2:
            return search_key_lower in title_lower

        return False

    def _get_filters(self):
        """筛选配置 - TVBox兼容版"""
        # 基础筛选配置
        base_filters = [
            {
                'key': 'area',
                'name': '地区',
                'value': [
                    {'n': '全部', 'v': ''},
                    {'n': '中国大陆', 'v': '中国大陆'},
                    {'n': '中国香港', 'v': '中国香港'},
                    {'n': '中国台湾', 'v': '中国台湾'},
                    {'n': '美国', 'v': '美国'},
                    {'n': '韩国', 'v': '韩国'},
                    {'n': '日本', 'v': '日本'},
                    {'n': '英国', 'v': '英国'},
                    {'n': '法国', 'v': '法国'},
                    {'n': '德国', 'v': '德国'},
                    {'n': '其他', 'v': '其他'}
                ]
            },
            {
                'key': 'year',
                'name': '年份',
                'value': [
                    {'n': '全部', 'v': ''},
                    {'n': '2025', 'v': '2025'},
                    {'n': '2024', 'v': '2024'},
                    {'n': '2023', 'v': '2023'},
                    {'n': '2022', 'v': '2022'},
                    {'n': '2021', 'v': '2021'},
                    {'n': '2020', 'v': '2020'},
                    {'n': '2019', 'v': '2019'},
                    {'n': '2018', 'v': '2018'}
                ]
            },
            {
                'key': 'type',
                'name': '类型',
                'value': [
                    {'n': '全部', 'v': ''},
                    {'n': '动作', 'v': '动作'},
                    {'n': '喜剧', 'v': '喜剧'},
                    {'n': '爱情', 'v': '爱情'},
                    {'n': '科幻', 'v': '科幻'},
                    {'n': '恐怖', 'v': '恐怖'},
                    {'n': '剧情', 'v': '剧情'},
                    {'n': '悬疑', 'v': '悬疑'},
                    {'n': '惊悚', 'v': '惊悚'},
                    {'n': '战争', 'v': '战争'},
                    {'n': '犯罪', 'v': '犯罪'}
                ]
            },
            {
                'key': 'tag',
                'name': '标签',
                'value': [
                    {'n': '全部', 'v': ''},
                    {'n': '1080P', 'v': '1080P'},
                    {'n': '4K', 'v': '4K'},
                    {'n': '720P', 'v': '720P'},
                    {'n': 'HD', 'v': 'HD'},
                    {'n': '剧场版', 'v': '剧场版'},
                    {'n': '国产剧', 'v': '国产剧'},
                    {'n': '韩剧', 'v': '韩剧'},
                    {'n': '美剧', 'v': '美剧'},
                    {'n': '日剧', 'v': '日剧'},
                    {'n': '番剧', 'v': '番剧'}
                ]
            }
        ]

        # 为每个分类提供筛选配置
        filters = {}
        category_ids = ['movie_bt', 'dyy', 'guochanju', 'mj', 'hj', 'rj', 'hwj', 'fjj', 'zuixindianying', 'dbtop250', 'dongmanjuchangban']

        for category_id in category_ids:
            if category_id == 'movie_bt':
                # 全部影片分类提供完整筛选
                filters[category_id] = base_filters
            elif category_id in ['dyy', 'zuixindianying', 'dbtop250', 'dongmanjuchangban']:
                # 电影相关分类提供地区、年份、类型筛选
                filters[category_id] = [
                    base_filters[0],  # 地区
                    base_filters[1],  # 年份
                    base_filters[2]   # 类型
                ]
            else:
                # 剧集分类提供地区、年份筛选
                filters[category_id] = [
                    base_filters[0],  # 地区
                    base_filters[1]   # 年份
                ]

        return filters

    def _build_url(self, tid, pg, extend):
        """构建URL - 修复版（基于实际网站结构）"""
        try:
            self.log(f"构建URL: tid={tid}, pg={pg}, extend={extend}")

            # 基础分类映射
            category_map = {
                'movie_bt': '/movie_bt',
                'zuixindianying': '/zuixindianying',
                'dbtop250': '/dbtop250',
                'fanju': '/fanju',
                'hanjutv': '/hanjutv',
                'meijutt': '/meijutt',
                'gcj': '/gcj',
                'dongmanjuchangban': '/dongmanjuchangban',
                'riju': '/riju',
                'haiwaijuqita': '/haiwaijuqita'
            }

            # 特殊分类映射（基于实际网站结构）
            special_categories = {
                'dyy': '/movie_bt_series/dyy',  # 电影
                'guochanju': '/movie_bt_series/guochanju',  # 国产剧
                'mj': '/movie_bt_series/mj',    # 美剧
                'hj': '/movie_bt_series/hj',    # 韩剧
                'rj': '/movie_bt_series/rj',    # 日剧
                'hwj': '/movie_bt_series/hwj',  # 海外剧
                'fjj': '/movie_bt_view_cat/fjj' # 番剧
            }

            # 处理筛选参数 - 基于实际网站结构
            if extend and tid == 'movie_bt':
                # 根据筛选条件选择合适的分类
                if extend.get('tag'):
                    tag = extend['tag']
                    if tag == '国产剧':
                        url = f"{self.host}/movie_bt_series/guochanju"
                    elif tag == '美剧':
                        url = f"{self.host}/movie_bt_series/mj"
                    elif tag == '韩剧':
                        url = f"{self.host}/movie_bt_series/hj"
                    elif tag == '日剧':
                        url = f"{self.host}/movie_bt_series/rj"
                    elif tag == '番剧':
                        url = f"{self.host}/movie_bt_view_cat/fjj"
                    else:
                        # 其他标签使用基础分类
                        url = f"{self.host}/movie_bt"
                elif extend.get('type'):
                    # 类型筛选暂时使用基础分类
                    url = f"{self.host}/movie_bt"
                elif extend.get('area'):
                    # 地区筛选暂时使用基础分类
                    url = f"{self.host}/movie_bt"
                elif extend.get('year'):
                    # 年份筛选暂时使用基础分类
                    url = f"{self.host}/movie_bt"
                else:
                    url = f"{self.host}/movie_bt"
            else:
                # 检查是否为特殊分类
                if tid in special_categories:
                    url = f"{self.host}{special_categories[tid]}"
                else:
                    # 普通分类
                    base_url = category_map.get(tid)
                    if not base_url:
                        self.log(f"未知的分类ID: {tid}")
                        return None
                    url = f"{self.host}{base_url}"

            # 添加分页
            if pg and pg != '1':
                url = f"{url}/page/{pg}"

            self.log(f"构建的URL: {url}")
            return url

        except Exception as e:
            self.log(f"构建URL出错: {str(e)}")
            return f"{self.host}/movie_bt"

    def _get_videos(self, doc, limit=None):
        """获取视频列表"""
        try:
            videos = []
            seen_ids = set()

            # 查找视频元素
            selectors = [
                '//div[contains(@class,"bt_img")]//li',
                '//ul[contains(@class,"bt_img")]//li'
            ]

            for selector in selectors:
                elements = doc.xpath(selector)
                if elements:
                    for elem in elements:
                        video = self._extract_video(elem)
                        if video and video['vod_id'] not in seen_ids:
                            videos.append(video)
                            seen_ids.add(video['vod_id'])
                    break

            return videos[:limit] if limit and videos else videos
        except Exception as e:
            self.log(f"获取视频列表出错: {str(e)}")
            return []

    def _extract_video(self, element):
        """提取视频信息"""
        try:
            # 提取链接和ID
            links = element.xpath('.//a[contains(@href,"/movie/")]/@href')
            if not links:
                return None

            link = links[0]
            if link.startswith('/'):
                link = self.host + link

            vod_id = self.regStr(r'/movie/(\d+)\.html', link)
            if not vod_id:
                return None

            # 提取标题
            title_selectors = ['.//h3/a/text()', './/h3/text()', './/a/@title', './/a/text()']
            title = ''
            for selector in title_selectors:
                titles = element.xpath(selector)
                for t in titles:
                    if t and t.strip() and len(t.strip()) > 1:
                        title = t.strip()
                        break
                if title:
                    break

            if not title:
                return None

            # 提取图片
            pic_selectors = ['.//img/@data-src', './/img/@src', './/img/@data-original']
            pic = ''
            for selector in pic_selectors:
                pics = element.xpath(selector)
                for p in pics:
                    if (p and not p.endswith('blank.gif') and
                        not p.startswith('data:image/') and 'base64' not in p):
                        if p.startswith('//'):
                            pic = 'https:' + p
                        elif p.startswith('/'):
                            pic = self.host + p
                        elif p.startswith('http'):
                            pic = p
                        break
                if pic:
                    break

            # 提取备注
            remarks_selectors = [
                './/span[contains(@class,"rating")]/text()',
                './/div[contains(@class,"rating")]/text()',
                './/span[contains(@class,"status")]/text()'
            ]
            remarks = ''
            for selector in remarks_selectors:
                remarks_list = element.xpath(selector)
                for r in remarks_list:
                    if r and r.strip():
                        remarks = r.strip()
                        break
                if remarks:
                    break

            return {
                'vod_id': vod_id,
                'vod_name': title,
                'vod_pic': pic,
                'vod_remarks': remarks,
                'vod_year': ''
            }
        except Exception as e:
            self.log(f"提取视频信息出错: {str(e)}")
            return None

    def _get_detail(self, doc, vid):
        """获取详情信息"""
        try:
            # 基本信息
            title = self._get_text(doc, ['//h1/text()', '//title/text()'])
            pic = self._get_text(doc, ['//div[@class="dyimg"]//img/@src', '//img[@class="poster"]/@src'])

            if pic and pic.startswith('/'):
                pic = self.host + pic

            # 描述信息
            desc = self._get_text(doc, ['//div[@class="yp_context"]/text()', '//div[@class="introduction"]//text()'])

            # 演员和导演
            actor = self._get_text(doc, ['//span[contains(text(),"主演")]/following-sibling::*/text()'])
            director = self._get_text(doc, ['//span[contains(text(),"导演")]/following-sibling::*/text()'])

            # 播放源
            play_from = []
            play_urls = []

            # 查找播放源
            source_elements = doc.xpath('//div[@class="mi_paly_box"]')
            for i, source_elem in enumerate(source_elements):
                source_name = f"播放源{i+1}"

                # 获取播放链接
                episodes = []
                episode_links = source_elem.xpath('.//a')

                for ep_link in episode_links:
                    ep_title = ep_link.xpath('./text()')
                    ep_href = ep_link.xpath('./@href')

                    if ep_title and ep_href:
                        ep_title = ep_title[0].strip()
                        ep_href = ep_href[0]

                        # 提取播放ID
                        play_id = self.regStr(r'/v_play/([^/]+)\.html', ep_href)
                        if play_id:
                            episodes.append(f"{ep_title}${play_id}")

                if episodes:
                    play_from.append(source_name)
                    play_urls.append('#'.join(episodes))

            return {
                'vod_id': vid,
                'vod_name': title,
                'vod_pic': pic,
                'type_name': '',
                'vod_year': '',
                'vod_area': '',
                'vod_remarks': '',
                'vod_actor': actor,
                'vod_director': director,
                'vod_content': desc,
                'vod_play_from': '$$$'.join(play_from),
                'vod_play_url': '$$$'.join(play_urls)
            }
        except Exception as e:
            self.log(f"获取详情出错: {str(e)}")
            return None

    def _get_text(self, doc, selectors):
        """通用文本提取"""
        for selector in selectors:
            texts = doc.xpath(selector)
            for text in texts:
                if text and text.strip():
                    return text.strip()
        return ''

    def _extract_real_video_url(self, html, play_page_url):
        """提取真实视频播放链接 - 精简版"""
        try:
            self.log("开始分析播放页面，提取真实视频链接...")

            # 1. 查找iframe的src属性
            iframe_pattern = r'<iframe[^>]+src="([^"]+)"'
            iframe_matches = re.findall(iframe_pattern, html, re.IGNORECASE)

            for iframe_src in iframe_matches:
                self.log(f"找到iframe src: {iframe_src}")

                try:
                    iframe_headers = self.headers.copy()
                    iframe_headers['Referer'] = play_page_url

                    if iframe_src.startswith('./'):
                        base_url = '/'.join(play_page_url.split('/')[:-1])
                        iframe_url = f"{base_url}/{iframe_src[2:]}"
                    elif iframe_src.startswith('/'):
                        iframe_url = f"{self.host}{iframe_src}"
                    else:
                        iframe_url = iframe_src

                    self.log(f"获取iframe内容: {iframe_url}")
                    iframe_rsp = self.fetch(iframe_url, headers=iframe_headers)
                    iframe_html = iframe_rsp.text

                    # 在iframe内容中查找真实视频链接
                    video_url = self._extract_from_iframe_content(iframe_html, iframe_url)
                    if video_url:
                        return video_url

                except Exception as e:
                    self.log(f"获取iframe内容失败: {str(e)}")
                    continue

            # 2. 直接查找播放器URL
            player_url_patterns = [
                r'https://[^"\'\\s]+\.php\?[^"\'\\s]*url=([^"\'\\s&]+)',
                r'url=(https://[^"\'\\s&]+\.(?:m3u8|mp4|flv)[^"\'\\s]*)',
                r'url=([^"\'\\s&]+\.(?:m3u8|mp4|flv)[^"\'\\s]*)'
            ]

            for pattern in player_url_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    for match in matches:
                        decoded_url = urllib.parse.unquote(match)
                        if (decoded_url.startswith('http') and
                            any(ext in decoded_url.lower() for ext in ['.m3u8', '.mp4', '.flv'])):
                            self.log(f"从播放器URL提取到真实视频链接: {decoded_url}")
                            return decoded_url

            # 3. 查找129服务器的视频链接
            direct_129_patterns = [
                r'https://129\.[^"\'\\s]+\.(?:m3u8|mp4|flv)[^"\'\\s]*',
                r'https://129[^"\'\\s]+/[^"\'\\s]*\.(?:m3u8|mp4|flv)[^"\'\\s]*'
            ]

            for pattern in direct_129_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    for match in matches:
                        self.log(f"找到129服务器直接视频链接: {match}")
                        return match

            # 4. 查找任何视频文件链接
            video_file_patterns = [
                r'https?://[^"\'\\s]+\.m3u8[^"\'\\s]*',
                r'https?://[^"\'\\s]+\.mp4[^"\'\\s]*',
                r'https?://[^"\'\\s]+\.flv[^"\'\\s]*'
            ]

            for pattern in video_file_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    for match in matches:
                        if not any(skip in match.lower() for skip in ['blank.gif', 'logo', 'thumb']):
                            self.log(f"找到视频文件链接: {match}")
                            return match

            self.log("未找到任何有效的视频播放链接")
            return ''

        except Exception as e:
            self.log(f"提取真实视频链接出错: {str(e)}")
            return ''

    def _extract_from_iframe_content(self, iframe_html, iframe_url):
        """从iframe内容中提取真实视频链接 - 精简版"""
        try:
            # 1. 查找JavaScript中的视频URL变量
            js_video_patterns = [
                r'const\s+mysvg\s*=\s*["\']([^"\']+)["\']',
                r'var\s+mysvg\s*=\s*["\']([^"\']+)["\']',
                r'art\.url\s*=\s*["\']([^"\']+)["\']',
                r'video\.src\s*=\s*["\']([^"\']+)["\']'
            ]

            for pattern in js_video_patterns:
                matches = re.findall(pattern, iframe_html, re.IGNORECASE)
                if matches:
                    for match in matches:
                        if (match.startswith('http') and
                            any(ext in match.lower() for ext in ['.m3u8', '.mp4', '.flv'])):
                            self.log(f"从JavaScript变量找到视频链接: {match}")
                            return match

            # 2. 查找HTML注释中的原始URL
            comment_pattern = r'<!-- saved from url=\([^)]+\)([^>]+) -->'
            comment_match = re.search(comment_pattern, iframe_html)
            if comment_match:
                saved_url = comment_match.group(1)
                self.log(f"从HTML注释找到保存的URL: {saved_url}")

                # 从保存的URL中提取url参数
                url_match = re.search(r'url=([^&\s]+)', saved_url)
                if url_match:
                    encoded_url = url_match.group(1)
                    decoded_url = urllib.parse.unquote(encoded_url)
                    if any(ext in decoded_url.lower() for ext in ['.m3u8', '.mp4', '.flv']):
                        self.log(f"从HTML注释成功提取视频链接: {decoded_url}")
                        return decoded_url

            # 3. 查找iframe URL本身的url参数
            if 'url=' in iframe_url:
                url_match = re.search(r'url=([^&\s]+)', iframe_url)
                if url_match:
                    encoded_url = url_match.group(1)
                    decoded_url = urllib.parse.unquote(encoded_url)

                    # 如果是明文视频链接，直接返回
                    if any(ext in decoded_url.lower() for ext in ['.m3u8', '.mp4', '.flv']):
                        self.log(f"从iframe URL参数提取视频链接: {decoded_url}")
                        return decoded_url

                    # 如果是加密字符串，尝试解密
                    elif decoded_url.startswith('videos') and len(decoded_url) > 50:
                        self.log(f"发现加密的视频URL参数: {decoded_url[:50]}...")
                        # 尝试简单的字符替换解密
                        decrypt_attempts = [
                            decoded_url.replace('videos', 'https://129.211.209.237:9091/hls3/hls/'),
                            decoded_url.replace('videos', 'https://129.211.209.237/hls/'),
                            decoded_url.replace('videos', 'https://129.211.209.237:9091/')
                        ]

                        for attempt in decrypt_attempts:
                            if any(ext in attempt.lower() for ext in ['.m3u8', '.mp4', '.flv']):
                                self.log(f"尝试字符替换解密: {attempt}")
                                return attempt

            # 4. 查找iframe内容中的129服务器链接
            server_129_patterns = [
                r'https://129[^"\'\\s]+\.(?:m3u8|mp4|flv)[^"\'\\s]*',
                r'https://129[^"\'\\s]+/[^"\'\\s]*\.(?:m3u8|mp4|flv)',
                r'129\.[^"\'\\s]+\.(?:m3u8|mp4|flv)[^"\'\\s]*'
            ]

            for pattern in server_129_patterns:
                matches = re.findall(pattern, iframe_html, re.IGNORECASE)
                if matches:
                    for match in matches:
                        if not match.startswith('http'):
                            match = f"https://{match}"
                        self.log(f"从iframe内容找到129服务器链接: {match}")
                        return match

            return None

        except Exception as e:
            self.log(f"从iframe内容提取视频链接出错: {str(e)}")
            return None
