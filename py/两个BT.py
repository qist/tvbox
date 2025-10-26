# coding=utf-8
# !/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import json
import time
import urllib.parse
import re
import base64

class Spider(Spider):
    
    def getName(self):
        return "两个BT"
    
    def init(self, extend=""):
        self.host = "https://www.bttwoo.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': self.host
        }
        self.log(f"两个BT爬虫初始化完成，主站: {self.host}")

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        """首页内容 - TVBox标准实现"""
        result = {}
        
        # 1. 定义分类 - 基于实际网站结构
        classes = [
            {'type_id': 'movie_bt_tags/xiju', 'type_name': '喜剧'},
            {'type_id': 'movie_bt_tags/aiqing', 'type_name': '爱情'},
            {'type_id': 'movie_bt_tags/adt', 'type_name': '冒险'},
            {'type_id': 'movie_bt_tags/at', 'type_name': '动作'},
            {'type_id': 'movie_bt_tags/donghua', 'type_name': '动画'},
            {'type_id': 'movie_bt_tags/qihuan', 'type_name': '奇幻'},
            {'type_id': 'movie_bt_tags/xuanni', 'type_name': '悬疑'},
            {'type_id': 'movie_bt_tags/kehuan', 'type_name': '科幻'},
            {'type_id': 'movie_bt_tags/juqing', 'type_name': '剧情'},
            {'type_id': 'movie_bt_tags/kongbu', 'type_name': '恐怖'},
            {'type_id': 'meiju', 'type_name': '美剧'},
            {'type_id': 'gf', 'type_name': '高分电影'}
        ]
        result['class'] = classes
        
        # 2. 添加筛选配置
        result['filters'] = self._get_filters()
        
        # 3. 获取首页推荐内容
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
        """兼容性方法 - 提供分类定义"""
        return {
            'class': [
                {'type_id': 'movie_bt_tags/xiju', 'type_name': '喜剧'},
                {'type_id': 'movie_bt_tags/aiqing', 'type_name': '爱情'},
                {'type_id': 'movie_bt_tags/adt', 'type_name': '冒险'},
                {'type_id': 'movie_bt_tags/at', 'type_name': '动作'},
                {'type_id': 'movie_bt_tags/donghua', 'type_name': '动画'},
                {'type_id': 'movie_bt_tags/qihuan', 'type_name': '奇幻'},
                {'type_id': 'movie_bt_tags/xuanni', 'type_name': '悬疑'},
                {'type_id': 'movie_bt_tags/kehuan', 'type_name': '科幻'},
                {'type_id': 'movie_bt_tags/juqing', 'type_name': '剧情'},
                {'type_id': 'movie_bt_tags/kongbu', 'type_name': '恐怖'},
                {'type_id': 'meiju', 'type_name': '美剧'},
                {'type_id': 'gf', 'type_name': '高分电影'}
            ],
            'filters': self._get_filters()
        }

    def categoryContent(self, tid, pg, filter, extend):
        """分类内容 - 支持筛选功能"""
        try:
            # 合并filter和extend参数
            if filter and isinstance(filter, dict):
                if not extend:
                    extend = {}
                extend.update(filter)
            
            self.log(f"分类请求: tid={tid}, pg={pg}, extend={extend}")
            
            url = self._build_url(tid, pg, extend)
            if not url:
                return {'list': []}
            
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
        """搜索功能 - 智能过滤"""
        try:
            search_url = f"{self.host}/xssssearch?q={urllib.parse.quote(key)}"
            if pg and pg != "1":
                search_url += f"&p={pg}"
            
            self.log(f"搜索URL: {search_url}")
            rsp = self.fetch(search_url, headers=self.headers)
            doc = self.html(rsp.text)
            
            videos = []
            seen_ids = set()
            
            # 搜索结果选择器
            elements = doc.xpath('//li[contains(@class,"") and .//a[contains(@href,"/movie/")]]')
            self.log(f"找到 {len(elements)} 个搜索结果元素")
            
            for elem in elements:
                video = self._extract_video_info(elem, is_search=True)
                if video and video['vod_id'] not in seen_ids:
                    # 添加相关性检查
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
        """播放链接"""
        try:
            self.log(f"获取播放链接: flag={flag}, id={id}")
            
            # 解码Base64播放ID
            try:
                decoded_id = base64.b64decode(id).decode('utf-8')
                self.log(f"解码播放ID: {decoded_id}")
            except:
                decoded_id = id
            
            play_url = f"{self.host}/v_play/{id}.html"
            
            # 返回播放页面URL，让播放器处理
            return {'parse': 1, 'playUrl': '', 'url': play_url}
        except Exception as e:
            self.log(f"播放链接获取出错: {str(e)}")
            return {'parse': 1, 'playUrl': '', 'url': f"{self.host}/v_play/{id}.html"}

    # ========== 辅助方法 ==========
    
    def _get_filters(self):
        """获取筛选配置 - TVBox兼容版"""
        base_filters = [
            {
                'key': 'area',
                'name': '地区',
                'value': [
                    {'n': '全部', 'v': ''},
                    {'n': '中国大陆', 'v': '中国大陆'},
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
            }
        ]
        
        # 为每个分类提供筛选配置
        filters = {}
        category_ids = [
            'movie_bt_tags/xiju', 'movie_bt_tags/aiqing', 'movie_bt_tags/adt',
            'movie_bt_tags/at', 'movie_bt_tags/donghua', 'movie_bt_tags/qihuan',
            'movie_bt_tags/xuanni', 'movie_bt_tags/kehuan', 'movie_bt_tags/juqing',
            'movie_bt_tags/kongbu', 'meiju', 'gf'
        ]
        
        for category_id in category_ids:
            filters[category_id] = base_filters
        
        return filters

    def _build_url(self, tid, pg, extend):
        """构建URL - 支持筛选"""
        try:
            # 基础分类URL映射
            if tid.startswith('movie_bt_tags/'):
                url = f"{self.host}/{tid}"
            elif tid == 'meiju':
                url = f"{self.host}/meiju"
            elif tid == 'gf':
                url = f"{self.host}/gf"
            else:
                url = f"{self.host}/{tid}"

            # 添加分页
            if pg and pg != '1':
                if '?' in url:
                    url += f"&paged={pg}"
                else:
                    url += f"?paged={pg}"

            return url
        except Exception as e:
            self.log(f"构建URL出错: {str(e)}")
            return f"{self.host}/movie_bt_tags/xiju"

    def _get_videos(self, doc, limit=None):
        """获取视频列表"""
        try:
            videos = []
            seen_ids = set()

            # 尝试多种选择器
            selectors = [
                '//li[.//a[contains(@href,"/movie/")]]',
                '//div[contains(@class,"item")]//li[.//a[contains(@href,"/movie/")]]'
            ]

            for selector in selectors:
                elements = doc.xpath(selector)
                if elements:
                    for elem in elements:
                        video = self._extract_video_info(elem)
                        if video and video['vod_id'] not in seen_ids:
                            videos.append(video)
                            seen_ids.add(video['vod_id'])
                    break

            return videos[:limit] if limit and videos else videos
        except Exception as e:
            self.log(f"获取视频列表出错: {str(e)}")
            return []

    def _extract_video_info(self, element, is_search=False):
        """提取视频信息"""
        try:
            # 提取链接
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
            title_selectors = [
                './/h3/a/text()',
                './/h3/text()',
                './/a/@title',
                './/a/text()'
            ]
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
            pic = self._extract_image(element, is_search, vod_id)

            # 提取备注
            remarks = self._extract_remarks(element)

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

    def _extract_image(self, element, is_search=False, vod_id=None):
        """图片提取 - 处理懒加载"""
        pic_selectors = [
            './/img/@data-original',
            './/img/@data-src',
            './/img/@src'
        ]

        for selector in pic_selectors:
            pics = element.xpath(selector)
            for p in pics:
                # 跳过懒加载占位符
                if (p and not p.endswith('blank.gif') and
                    not p.startswith('data:image/') and 'base64' not in p):
                    if p.startswith('//'):
                        return 'https:' + p
                    elif p.startswith('/'):
                        return self.host + p
                    elif p.startswith('http'):
                        return p

        # 搜索页面特殊处理：从详情页面获取
        if is_search and vod_id:
            return self._get_image_from_detail(vod_id)

        return ''

    def _extract_remarks(self, element):
        """提取备注信息"""
        remarks_selectors = [
            './/span[contains(@class,"rating")]/text()',
            './/div[contains(@class,"rating")]/text()',
            './/span[contains(@class,"status")]/text()',
            './/div[contains(@class,"status")]/text()',
            './/span[contains(text(),"集")]/text()',
            './/span[contains(text(),"1080p")]/text()',
            './/span[contains(text(),"HD")]/text()'
        ]

        for selector in remarks_selectors:
            remarks_list = element.xpath(selector)
            for r in remarks_list:
                if r and r.strip():
                    return r.strip()

        return ''

    def _get_image_from_detail(self, vod_id):
        """从详情页面获取图片"""
        try:
            detail_url = f"{self.host}/movie/{vod_id}.html"
            rsp = self.fetch(detail_url, headers=self.headers)
            doc = self.html(rsp.text)

            # 详情页图片选择器
            pic_selectors = [
                '//img[contains(@class,"poster")]/@src',
                '//div[contains(@class,"poster")]//img/@src',
                '//img[contains(@alt,"")]/@src'
            ]

            for selector in pic_selectors:
                pics = doc.xpath(selector)
                for p in pics:
                    if p and not p.endswith('blank.gif'):
                        if p.startswith('//'):
                            return 'https:' + p
                        elif p.startswith('/'):
                            return self.host + p
                        elif p.startswith('http'):
                            return p
        except:
            pass

        return ''

    def _is_relevant_search_result(self, title, search_key):
        """检查搜索结果是否与搜索关键词相关"""
        if not title or not search_key:
            return False

        title_lower = title.lower()
        search_key_lower = search_key.lower()

        # 直接包含搜索关键词的肯定相关
        if search_key_lower in title_lower:
            return True

        # 字符匹配
        search_chars = set(search_key_lower.replace(' ', ''))
        title_chars = set(title_lower.replace(' ', ''))

        if len(search_chars) > 0:
            match_ratio = len(search_chars & title_chars) / len(search_chars)
            if match_ratio >= 0.6:
                return True

        # 短搜索词要求严格匹配
        if len(search_key_lower) <= 2:
            return search_key_lower in title_lower

        return False

    def _get_detail(self, doc, vod_id):
        """获取详情信息"""
        try:
            # 提取标题
            title_selectors = [
                '//h1/text()',
                '//h2/text()',
                '//title/text()'
            ]
            title = ''
            for selector in title_selectors:
                titles = doc.xpath(selector)
                for t in titles:
                    if t and t.strip():
                        title = t.strip()
                        break
                if title:
                    break

            # 提取图片
            pic_selectors = [
                '//img[contains(@class,"poster")]/@src',
                '//div[contains(@class,"poster")]//img/@src',
                '//img/@src'
            ]
            pic = ''
            for selector in pic_selectors:
                pics = doc.xpath(selector)
                for p in pics:
                    if p and not p.endswith('blank.gif'):
                        if p.startswith('//'):
                            pic = 'https:' + p
                        elif p.startswith('/'):
                            pic = self.host + p
                        elif p.startswith('http'):
                            pic = p
                        break
                if pic:
                    break

            # 提取描述
            desc_selectors = [
                '//div[contains(@class,"intro")]//text()',
                '//div[contains(@class,"description")]//text()',
                '//p[contains(@class,"desc")]//text()'
            ]
            desc = ''
            for selector in desc_selectors:
                descs = doc.xpath(selector)
                desc_parts = []
                for d in descs:
                    if d and d.strip():
                        desc_parts.append(d.strip())
                if desc_parts:
                    desc = ' '.join(desc_parts)
                    break

            # 提取演员
            actor_selectors = [
                '//li[contains(text(),"主演")]/text()',
                '//span[contains(text(),"主演")]/following-sibling::text()',
                '//div[contains(@class,"actor")]//text()'
            ]
            actor = ''
            for selector in actor_selectors:
                actors = doc.xpath(selector)
                for a in actors:
                    if a and a.strip() and '主演' in a:
                        actor = a.strip().replace('主演：', '').replace('主演', '')
                        break
                if actor:
                    break

            # 提取导演
            director_selectors = [
                '//li[contains(text(),"导演")]/text()',
                '//span[contains(text(),"导演")]/following-sibling::text()',
                '//div[contains(@class,"director")]//text()'
            ]
            director = ''
            for selector in director_selectors:
                directors = doc.xpath(selector)
                for d in directors:
                    if d and d.strip() and '导演' in d:
                        director = d.strip().replace('导演：', '').replace('导演', '')
                        break
                if director:
                    break

            # 提取播放源
            play_sources = self._parse_play_sources(doc, vod_id)

            return {
                'vod_id': vod_id,
                'vod_name': title,
                'vod_pic': pic,
                'type_name': '',
                'vod_year': '',
                'vod_area': '',
                'vod_remarks': '',
                'vod_actor': actor,
                'vod_director': director,
                'vod_content': desc,
                'vod_play_from': '$$$'.join([source['name'] for source in play_sources]),
                'vod_play_url': '$$$'.join([source['episodes'] for source in play_sources])
            }
        except Exception as e:
            self.log(f"获取详情出错: {str(e)}")
            return None

    def _parse_play_sources(self, doc, vod_id):
        """解析播放源"""
        try:
            play_sources = []

            # 查找播放链接
            episode_selectors = [
                '//a[contains(@href,"/v_play/")]',
                '//div[contains(@class,"play")]//a'
            ]

            episodes = []
            for selector in episode_selectors:
                episode_elements = doc.xpath(selector)
                if episode_elements:
                    for ep in episode_elements:
                        ep_title = ep.xpath('./text()')[0] if ep.xpath('./text()') else ''
                        ep_url = ep.xpath('./@href')[0] if ep.xpath('./@href') else ''

                        if ep_title and ep_url:
                            # 提取播放ID
                            play_id = self.regStr(r'/v_play/([^.]+)\.html', ep_url)
                            if play_id:
                                episodes.append(f"{ep_title.strip()}${play_id}")
                    break

            if episodes:
                play_sources.append({
                    'name': '默认播放',
                    'episodes': '#'.join(episodes)
                })
            else:
                # 默认播放源
                play_sources.append({
                    'name': '默认播放',
                    'episodes': f'第1集$bXZfMTM0NTY4LW5tXzE='
                })

            return play_sources
        except Exception as e:
            self.log(f"解析播放源出错: {str(e)}")
            return [{'name': '默认播放', 'episodes': f'第1集$bXZfMTM0NTY4LW5tXzE='}]
