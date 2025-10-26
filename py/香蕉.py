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
from urllib.parse import urljoin

class Spider(Spider):
    
    def getName(self):
        return "苹果视频"
    
    def init(self, extend=""):
        self.host = "https://618041.xyz"
        self.api_host = "https://h5.xxoo168.org"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': self.host
        }
        # 定义特殊分区ID列表，包含所有需要特殊处理的分类
        self.special_categories = ['13', '14', '33',  '53', '32', '52', '9']
        self.log(f"苹果视频爬虫初始化完成，主站: {self.host}")

    def html(self, content):
        """将HTML内容转换为可查询的对象"""
        try:
            return etree.HTML(content)
        except:
            self.log("HTML解析失败")
            return None

    def regStr(self, pattern, string, index=1):
        """正则表达式提取字符串"""
        try:
            match = re.search(pattern, string, re.IGNORECASE)
            if match and len(match.groups()) >= index:
                return match.group(index)
        except:
            pass
        return ""

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        """获取首页内容和分类"""
        result = {}
        # 只保留指定的分类
        classes = [
            {'type_id': '618041.xyz_1', 'type_name': '全部视频'},
            {'type_id': '618041.xyz_13', 'type_name': '香蕉精品'},
            {'type_id': '618041.xyz_22', 'type_name': '制服诱惑'},
            {'type_id': '618041.xyz_6', 'type_name': '国产视频'},
            {'type_id': '618041.xyz_8', 'type_name': '清纯少女'},
            {'type_id': '618041.xyz_9', 'type_name': '辣妹大奶'},
            {'type_id': '618041.xyz_10', 'type_name': '女同专属'},
            {'type_id': '618041.xyz_11', 'type_name': '素人出演'},
            {'type_id': '618041.xyz_12', 'type_name': '角色扮演'},
            {'type_id': '618041.xyz_20', 'type_name': '人妻熟女'},
            {'type_id': '618041.xyz_23', 'type_name': '日韩剧情'},
            {'type_id': '618041.xyz_21', 'type_name': '经典伦理'},
            {'type_id': '618041.xyz_7', 'type_name': '成人动漫'},
            {'type_id': '618041.xyz_14', 'type_name': '精品二区'},
            {'type_id': '618041.xyz_53', 'type_name': '动漫中字'},
            {'type_id': '618041.xyz_52', 'type_name': '日本无码'},
            {'type_id': '618041.xyz_33', 'type_name': '中文字幕'},
            {'type_id': '618041.xyz_32', 'type_name': '国产自拍'}
        ]
        result['class'] = classes
        try:
            rsp = self.fetch(self.host, headers=self.headers)
            doc = self.html(rsp.text)
            videos = self._get_videos(doc, limit=20)
            result['list'] = videos
        except Exception as e:
            self.log(f"首页获取出错: {str(e)}")
            result['list'] = []
        return result

    def homeVideoContent(self):
        """分类定义 - 兼容性方法"""
        return {
            'class': [
                {'type_id': '618041.xyz_1', 'type_name': '全部视频'},
                {'type_id': '618041.xyz_13', 'type_name': '香蕉精品'},
                {'type_id': '618041.xyz_22', 'type_name': '制服诱惑'},
                {'type_id': '618041.xyz_6', 'type_name': '国产视频'},
                {'type_id': '618041.xyz_8', 'type_name': '清纯少女'},
                {'type_id': '618041.xyz_9', 'type_name': '辣妹大奶'},
                {'type_id': '618041.xyz_10', 'type_name': '女同专属'},
                {'type_id': '618041.xyz_11', 'type_name': '素人出演'},
                {'type_id': '618041.xyz_12', 'type_name': '角色扮演'},
                {'type_id': '618041.xyz_20', 'type_name': '人妻熟女'},
                {'type_id': '618041.xyz_23', 'type_name': '日韩剧情'},
                {'type_id': '618041.xyz_21', 'type_name': '经典伦理'},
                {'type_id': '618041.xyz_7', 'type_name': '成人动漫'},
                {'type_id': '618041.xyz_14', 'type_name': '精品二区'},
                {'type_id': '618041.xyz_53', 'type_name': '动漫中字'},
                {'type_id': '618041.xyz_52', 'type_name': '日本无码'},
                {'type_id': '618041.xyz_33', 'type_name': '中文字幕'},
                {'type_id': '618041.xyz_32', 'type_name': '国产自拍'}
            ]
        }

    def categoryContent(self, tid, pg, filter, extend):
        """分类内容 - 修改为使用固定页数设置"""
        try:
            domain, type_id = tid.split('_')
            url = f"https://{domain}/index.php/vod/type/id/{type_id}.html"
            if pg and pg != '1':
                url = url.replace('.html', f'/page/{pg}.html')
            self.log(f"访问分类URL: {url}")
            rsp = self.fetch(url, headers=self.headers)
            doc = self.html(rsp.text)
            # 在这里将 type_id 传递给 _get_videos 方法
            videos = self._get_videos(doc, category_id=type_id, limit=20)
            
            # 使用固定页数设置，而不是尝试从页面解析
            pagecount = 999
            total = 19980
            
            return {
                'list': videos,
                'page': int(pg),
                'pagecount': pagecount,
                'limit': 20,
                'total': total
            }
        except Exception as e:
            self.log(f"分类内容获取出错: {str(e)}")
            return {'list': []}

    def searchContent(self, key, quick, pg="1"):
        """搜索功能 - 完全修复版"""
        try:
            # 构造搜索URL
            search_url = f"{self.host}/index.php/vod/type/id/1/wd/{urllib.parse.quote(key)}/page/{pg}.html"
            self.log(f"搜索URL: {search_url}")
            
            # 发送请求
            rsp = self.fetch(search_url, headers=self.headers)
            if not rsp or rsp.status_code != 200:
                self.log("搜索请求失败")
                return {'list': []}
            
            # 解析HTML
            doc = self.html(rsp.text)
            if not doc:
                self.log("搜索页面解析失败")
                return {'list': []}
            
            # 提取搜索结果
            videos = self._get_videos(doc, limit=20)
            
            # 尝试从页面提取分页信息
            pagecount = 5  # 默认值
            total = 100    # 默认值
            
            # 尝试从分页元素中提取真实的分页信息
            page_elements = doc.xpath('//div[@class="mypage"]/a')
            if page_elements and len(page_elements) > 0:
                try:
                    # 查找尾页链接
                    last_page = None
                    for elem in page_elements:
                        href = elem.xpath('./@href')[0]
                        if '尾页' in elem.text or 'page/' in href:
                            last_page = href
                            break
                    
                    if last_page:
                        # 从尾页URL中提取页码
                        page_match = re.search(r'/page/(\d+)\.html', last_page)
                        if page_match:
                            pagecount = int(page_match.group(1))
                            total = pagecount * 20  # 估算总数
                except:
                    pass
            
            return {
                'list': videos,
                'page': int(pg),
                'pagecount': pagecount,
                'limit': 20,
                'total': total
            }
        except Exception as e:
            self.log(f"搜索出错: {str(e)}")
            return {'list': []}

    def detailContent(self, ids):
        """详情页面 - 特别处理特殊分区的链接"""
        try:
            vid = ids[0]
            
            # 检查是否是特殊分区的链接
            if vid.startswith('special_'):
                # 解析特殊分区ID格式: special_{category_id}_{video_id}_{encoded_url}
                parts = vid.split('_')
                if len(parts) >= 4:
                    category_id = parts[1]
                    video_id = parts[2]
                    encoded_url = '_'.join(parts[3:])
                    play_url = urllib.parse.unquote(encoded_url)
                    
                    self.log(f"特殊分区视频，直接使用链接: {play_url}")
                    
                    # 从播放链接中提取视频URL
                    parsed_url = urllib.parse.urlparse(play_url)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    video_url = query_params.get('v', [''])[0]
                    pic_url = query_params.get('b', [''])[0]
                    title_encrypted = query_params.get('m', [''])[0]
                    
                    # 解码标题
                    title = self._decrypt_title(title_encrypted)
                    
                    return {
                        'list': [{
                            'vod_id': vid,
                            'vod_name': title,
                            'vod_pic': pic_url,
                            'vod_remarks': '',
                            'vod_year': '',
                            'vod_play_from': '直接播放',
                            'vod_play_url': f"第1集${play_url}"
                        }]
                    }
            
            # 常规处理
            if '_' in vid and len(vid.split('_')) > 2:
                domain, category_id, video_id = vid.split('_')
            else:
                domain, video_id = vid.split('_')
            
            detail_url = f"https://{domain}/index.php/vod/detail/id/{video_id}.html"
            
            self.log(f"访问详情URL: {detail_url}")
            rsp = self.fetch(detail_url, headers=self.headers)
            doc = self.html(rsp.text)
            video_info = self._get_detail(doc, rsp.text, vid)
            return {'list': [video_info]} if video_info else {'list': []}
        except Exception as e:
            self.log(f"详情获取出错: {str(e)}")
            return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        """播放链接 - 特别处理特殊分区的链接"""
        try:
            self.log(f"获取播放链接: flag={flag}, id={id}")
            
            # 检查是否是特殊分区的链接
            if id.startswith('special_'):
                # 解析特殊分区ID格式: special_{category_id}_{video_id}_{encoded_url}
                parts = id.split('_')
                if len(parts) >= 4:
                    category_id = parts[1]
                    video_id = parts[2]
                    encoded_url = '_'.join(parts[3:])
                    play_url = urllib.parse.unquote(encoded_url)
                    
                    self.log(f"特殊分区视频，直接使用链接: {play_url}")
                    
                    # 从播放链接中提取视频URL
                    parsed_url = urllib.parse.urlparse(play_url)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    video_url = query_params.get('v', [''])[0]
                    
                    if video_url:
                        # 确保URL是完整的
                        if video_url.startswith('//'):
                            video_url = 'https:' + video_url
                        elif not video_url.startswith('http'):
                            video_url = urljoin(self.host, video_url)
                        
                        self.log(f"从特殊链接中提取到视频地址: {video_url}")
                        return {'parse': 0, 'playUrl': '', 'url': video_url}
            
            # 检查传入的ID是否为完整URL，如果是则直接解析
            if id.startswith('http'):
                self.log("ID 是一个完整URL，直接解析参数")
                parsed_url = urllib.parse.urlparse(id)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                
                # 尝试获取视频参数
                video_url = query_params.get('v', [''])[0]
                if not video_url:
                    # 尝试其他可能的参数名
                    for key in query_params:
                        if key in ['url', 'src', 'file']:
                            video_url = query_params[key][0]
                            break
                
                if video_url:
                    # 解码可能的URL编码
                    video_url = urllib.parse.unquote(video_url)
                    # 确保URL是完整的
                    if video_url.startswith('//'):
                        video_url = 'https:' + video_url
                    elif not video_url.startswith('http'):
                        # 尝试添加基本域名
                        video_url = urljoin(self.host, video_url)
                    
                    self.log(f"从 URL 参数中提取到视频地址: {video_url}")
                    return {'parse': 0, 'playUrl': '', 'url': video_url}
                else:
                    self.log("URL 中没有找到视频参数，尝试从页面提取")
                    # 请求页面并提取视频链接
                    rsp = self.fetch(id, headers=self.headers)
                    if rsp and rsp.status_code == 200:
                        video_url = self._extract_direct_video_url(rsp.text)
                        if video_url:
                            self.log(f"从页面提取到视频地址: {video_url}")
                            return {'parse': 0, 'playUrl': '', 'url': video_url}
                    
                    self.log("无法从页面提取视频链接，返回原始URL")
                    return {'parse': 1, 'playUrl': '', 'url': id}

            # 从新的 id 格式中提取视频ID和分类ID
            if id.count('_') >= 2:
                parts = id.split('_')
                video_id = parts[-1]
                category_id = parts[1]
            else:
                video_id = id.split('_')[-1]
                category_id = ''
            
            self.log(f"视频ID: {video_id}, 分类ID: {category_id}")
            
            # 对于特殊分类，使用直接解析播放页面的方式
            if category_id in self.special_categories:
                self.log("特殊分类，尝试从详情页提取直接播放链接")
                # 构造播放页面URL
                play_page_url = f"{self.host}/index.php/vod/play/id/{video_id}.html"
                
                # 请求播放页面
                rsp = self.fetch(play_page_url, headers=self.headers)
                if rsp and rsp.status_code == 200:
                    # 从页面提取视频链接
                    video_url = self._extract_direct_video_url(rsp.text)
                    if video_url:
                        self.log(f"从播放页面提取到视频地址: {video_url}")
                        return {'parse': 0, 'playUrl': '', 'url': video_url}
                
                # 如果提取失败，回退到API方式
                self.log("从播放页面提取失败，尝试API方式")
                return self._get_video_by_api(id, video_id)
            else:
                # 其他分类使用API方式
                self.log("使用API方式获取视频地址")
                return self._get_video_by_api(id, video_id)
                
        except Exception as e:
            self.log(f"播放链接获取出错: {str(e)}")
            if '_' in id:
                domain, play_id = id.split('_')
                play_url = f"https://{domain}/html/kkyd.html?m={play_id}"
            else:
                play_url = f"{self.host}/html/kkyd.html?m={id}"
            return {'parse': 1, 'playUrl': '', 'url': play_url}

    def _get_video_by_api(self, id, video_id):
        """通过API获取视频地址"""
        try:
            api_url = f"{self.api_host}/api/v2/vod/reqplay/{video_id}"
            self.log(f"请求API获取视频地址: {api_url}")
            
            api_headers = self.headers.copy()
            api_headers.update({
                'Referer': f"{self.host}/",
                'Origin': self.host,
                'X-Requested-With': 'XMLHttpRequest'
            })
            
            api_response = self.fetch(api_url, headers=api_headers)
            if api_response and api_response.status_code == 200:
                data = api_response.json()
                self.log(f"API响应: {data}")
                
                if data.get('retcode') == 3:
                    video_url = data.get('data', {}).get('httpurl_preview', '')
                else:
                    video_url = data.get('data', {}).get('httpurl', '')
                
                if video_url:
                    video_url = video_url.replace('?300', '')
                    self.log(f"从API获取到视频地址: {video_url}")
                    return {'parse': 0, 'playUrl': '', 'url': video_url}
                else:
                    self.log("API响应中没有找到视频地址")
            else:
                self.log(f"API请求失败，状态码: {api_response.status_code if api_response else '无响应'}")
                
            if '_' in id:
                domain, play_id = id.split('_')
                play_url = f"https://{domain}/html/kkyd.html?m={play_id}"
            else:
                play_url = f"{self.host}/html/kkyd.html?m={id}"
            self.log(f"API请求失败，回退到播放页面: {play_url}")
            return {'parse': 1, 'playUrl': '', 'url': play_url}
            
        except Exception as e:
            self.log(f"API方式获取视频出错: {str(e)}")
            if '_' in id:
                domain, play_id = id.split('_')
                play_url = f"https://{domain}/html/kkyd.html?m={play_id}"
            else:
                play_url = f"{self.host}/html/kkyd.html?m={id}"
            return {'parse': 1, 'playUrl': '', 'url': play_url}

    def _extract_direct_video_url(self, html_content):
        """从HTML内容中提取直接播放链接 (优化版)"""
        try:
            # 首先尝试提取明显的视频链接
            patterns = [
                r'v=([^&]+\.(?:m3u8|mp4))',
                r'"url"\s*:\s*["\']([^"\']+\.(?:mp4|m3u8))["\']',
                r'src\s*=\s*["\']([^"\']+\.(?:mp4|m3u8))["\']',
                r'http[^\s<>"\'?]+\.(?:mp4|m3u8)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    extracted_url = match.replace('\\', '')
                    extracted_url = urllib.parse.unquote(extracted_url)
                    
                    if extracted_url.startswith('//'):
                        extracted_url = 'https:' + extracted_url
                    elif extracted_url.startswith('http'):
                        return extracted_url
            
            return None
        except Exception as e:
            self.log(f"提取直接播放URL出错: {str(e)}")
            return None

    def _get_videos(self, doc, category_id=None, limit=None):
        """获取影片列表 - 根据实际网站结构"""
        try:
            videos = []
            elements = doc.xpath('//a[@class="vodbox"]')
            self.log(f"找到 {len(elements)} 个vodbox元素")
            for elem in elements:
                video = self._extract_video(elem, category_id)
                if video:
                    videos.append(video)
            return videos[:limit] if limit and videos else videos
        except Exception as e:
            self.log(f"获取影片列表出错: {str(e)}")
            return []

    def _extract_video(self, element, category_id=None):
        """提取影片信息 - 特别处理特殊分区的链接"""
        try:
            link = element.xpath('./@href')[0]
            if link.startswith('/'):
                link = self.host + link
            
            # 检查是否是特殊分区的链接
            is_special_link = 'ar-kk.html' in link or 'ar.html' in link
            
            # 对于特殊分区，直接使用链接本身作为ID
            if is_special_link and category_id in self.special_categories:
                # 提取链接中的参数
                parsed_url = urllib.parse.urlparse(link)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                
                # 获取视频ID（从v参数中提取）
                video_url = query_params.get('v', [''])[0]
                if video_url:
                    # 从视频URL中提取ID
                    video_id_match = re.search(r'/([a-f0-9-]+)/video\.m3u8', video_url)
                    if video_id_match:
                        video_id = video_id_match.group(1)
                    else:
                        # 如果没有匹配到，使用哈希值
                        video_id = str(hash(link) % 1000000)
                else:
                    video_id = str(hash(link) % 1000000)
                
                # 对于特殊分区，保留完整的链接作为vod_id的一部分
                final_vod_id = f"special_{category_id}_{video_id}_{urllib.parse.quote(link)}"
            else:
                # 常规处理
                vod_id = self.regStr(r'm=(\d+)', link)
                if not vod_id:
                    vod_id = str(hash(link) % 1000000)
                
                final_vod_id = f"618041.xyz_{vod_id}"
                if category_id:
                    final_vod_id = f"618041.xyz_{category_id}_{vod_id}"
            
            # 提取标题
            title_elem = element.xpath('.//p[@class="km-script"]/text()')
            if not title_elem:
                title_elem = element.xpath('.//p[contains(@class, "script")]/text()')
                if not title_elem:
                    title_elem = element.xpath('.//p/text()')
                    if not title_elem:
                        title_elem = element.xpath('.//h3/text()')
                        if not title_elem:
                            title_elem = element.xpath('.//h4/text()')
                            if not title_elem:
                                self.log(f"未找到标题元素，跳过该视频")
                                return None
            
            title_encrypted = title_elem[0].strip()
            title = self._decrypt_title(title_encrypted)
            
            # 提取图片
            pic_elem = element.xpath('.//img/@data-original')
            if not pic_elem:
                pic_elem = element.xpath('.//img/@src')
            pic = pic_elem[0] if pic_elem else ''
            
            if pic:
                if pic.startswith('//'):
                    pic = 'https:' + pic
                elif pic.startswith('/'):
                    pic = self.host + pic
            
            return {
                'vod_id': final_vod_id,
                'vod_name': title,
                'vod_pic': pic,
                'vod_remarks': '',
                'vod_year': ''
            }
        except Exception as e:
            self.log(f"提取影片信息出错: {str(e)}")
            return None

    def _decrypt_title(self, encrypted_text):
        """解密标题 - 使用网站的解密算法"""
        try:
            decrypted_chars = []
            for char in encrypted_text:
                code_point = ord(char)
                decrypted_code = code_point ^ 128
                decrypted_char = chr(decrypted_code)
                decrypted_chars.append(decrypted_char)
            
            decrypted_text = ''.join(decrypted_chars)
            return decrypted_text
        except Exception as e:
            self.log(f"标题解密失败: {str(e)}")
            return encrypted_text

    def _get_detail(self, doc, html_content, vid):
        """获取详情信息 (优化版) - 修复播放源提取问题"""
        try:
            title = self._get_text(doc, ['//h1/text()', '//title/text()'])
            pic = self._get_text(doc, ['//div[contains(@class,"dyimg")]//img/@src', '//img[contains(@class,"poster")]/@src'])
            if pic and pic.startswith('/'):
                pic = self.host + pic
            desc = self._get_text(doc, ['//div[contains(@class,"yp_context")]/text()', '//div[contains(@class,"introduction")]//text()'])
            actor = self._get_text(doc, ['//span[contains(text(),"主演")]/following-sibling::*/text()'])
            director = self._get_text(doc, ['//span[contains(text(),"导演")]/following-sibling::*/text()'])

            play_from = []
            play_urls = []
            
            # 使用更灵活的正则匹配来查找播放链接
            player_link_patterns = [
                re.compile(r'href="(.*?ar\.html.*?)"'),
                re.compile(r'href="(.*?kkyd\.html.*?)"'),
                re.compile(r'href="(.*?ar-kk\.html.*?)"')
            ]
            
            player_links = []
            for pattern in player_link_patterns:
                matches = pattern.findall(html_content)
                player_links.extend(matches)
            
            if player_links:
                episodes = []
                for link in player_links:
                    full_url = urljoin(self.host, link)
                    episodes.append(f"第1集${full_url}")

                if episodes:
                    play_from.append("默认播放源")
                    play_urls.append('#'.join(episodes))

            if not play_from:
                self.log("未找到播放源元素，无法定位播放源列表")
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
                    'vod_play_from': '默认播放源',
                    'vod_play_url': f"第1集${vid}"
                }

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
            try:
                texts = doc.xpath(selector)
                for text in texts:
                    if text and text.strip():
                        return text.strip()
            except:
                continue
        return ''

    def log(self, message):
        """日志输出"""
        print(f"[苹果视频] {message}")

    def fetch(self, url, headers=None, method='GET', data=None, timeout=10):
        """网络请求"""
        try:
            if headers is None:
                headers = self.headers
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout, verify=False)
            else:
                response = requests.post(url, headers=headers, data=data, timeout=timeout, verify=False)
            return response
        except Exception as e:
            self.log(f"网络请求失败: {url}, 错误: {str(e)}")
            return None

# 注册爬虫
if __name__ == '__main__':
    from base.spider import Spider as BaseSpider
    BaseSpider.register(Spider())