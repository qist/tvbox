# coding=utf-8
import re
import json
import time
from urllib.parse import quote, urljoin, urlparse, parse_qs
import sys
# 导入外部库
from bs4 import BeautifulSoup
import gzip
sys.path.append("..")
from base.spider import Spider

class Spider(Spider):
    def __init__(self):
        self.name = "小鸭子看看"
        self.hosts = {
            "main": "https://xiaoyakankan.com",
            "tw": "https://tw.xiaoyakankan.com"
        }
        self.default_host = "tw"
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        # 视频格式支持
        self.VIDEO_FORMATS = ['.m3u8', '.mp4', '.flv', '.avi', '.mkv', '.mov']

    def getName(self):
        return self.name

    def init(self, extend=""):
        if extend:
            try:
                config = json.loads(extend)
                if config.get("host") in self.hosts:
                    self.default_host = config["host"]
                    self.log(f"已切换默认域名至：{self.hosts[self.default_host]}", "INFO")
            except:
                self.log("初始化参数解析失败，使用默认tw子域名", "WARNING")

    def log(self, msg, level="INFO"):
        print(f"[{level}] [{self.name}] {time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}")

    def get_current_host(self):
        return self.hosts[self.default_host]

    def homeContent(self, filter):
        result = {}
        result['class'] = [
            {"type_name": "电影", "type_id": "10", "land": "1", "filters": [
                {"key": "class", "name": "类型", "value": [
                    {"n": "全部", "v": "10"},
                    {"n": "动作片", "v": "1001"},
                    {"n": "喜剧片", "v": "1002"},
                    {"n": "爱情片", "v": "1003"},
                    {"n": "科幻片", "v": "1004"},
                    {"n": "恐怖片", "v": "1005"},
                    {"n": "剧情片", "v": "1006"},
                    {"n": "战争片", "v": "1007"},
                    {"n": "纪录片", "v": "1008"},
                    {"n": "微电影", "v": "1009"},
                    {"n": "动漫电影", "v": "1010"},
                    {"n": "奇幻片", "v": "1011"},
                    {"n": "动画片", "v": "1013"},
                    {"n": "犯罪片", "v": "1014"},
                    {"n": "悬疑片", "v": "1016"},
                    {"n": "欧美片", "v": "1017"},
                    {"n": "邵氏电影", "v": "1019"},
                    {"n": "同性片", "v": "1021"},
                    {"n": "家庭片", "v": "1024"},
                    {"n": "古装片", "v": "1025"},
                    {"n": "历史片", "v": "1026"},
                    {"n": "4K电影", "v": "1027"}
                ]}
            ]},
            {"type_name": "连续剧", "type_id": "11", "land": "1", "filters": [
                {"key": "class", "name": "地区类型", "value": [
                    {"n": "全部", "v": "11"},
                    {"n": "国产剧", "v": "1101"},
                    {"n": "香港剧", "v": "1102"},
                    {"n": "台湾剧", "v": "1105"},
                    {"n": "韩国剧", "v": "1103"},
                    {"n": "欧美剧", "v": "1104"},
                    {"n": "日本剧", "v": "1106"},
                    {"n": "泰国剧", "v": "1108"},
                    {"n": "港台剧", "v": "1110"},
                    {"n": "日韩剧", "v": "1111"},
                    {"n": "东南亚剧", "v": "1112"},
                    {"n": "海外剧", "v": "1107"}
                ]}
            ]},
            {"type_name": "综艺", "type_id": "12", "land": "1", "filters": [
                {"key": "class", "name": "地区类型", "value": [
                    {"n": "全部", "v": "12"},
                    {"n": "内地综艺", "v": "1201"},
                    {"n": "港台综艺", "v": "1202"},
                    {"n": "日韩综艺", "v": "1203"},
                    {"n": "欧美综艺", "v": "1204"},
                    {"n": "国外综艺", "v": "1205"}
                ]}
            ]},
            {"type_name": "动漫", "type_id": "13", "land": "1", "filters": [
                {"key": "class", "name": "地区类型", "value": [
                    {"n": "全部", "v": "13"},
                    {"n": "国产动漫", "v": "1301"},
                    {"n": "日韩动漫", "v": "1302"},
                    {"n": "欧美动漫", "v": "1303"},
                    {"n": "海外动漫", "v": "1305"},
                    {"n": "里番", "v": "1307"}
                ]}
            ]},
            {"type_name": "福利", "type_id": "15", "land": "1", "filters": [
                {"key": "class", "name": "地区类型", "value": [
                    {"n": "全部", "v": "15"},
                    {"n": "韩国情色片", "v": "1551"},
                    {"n": "日本情色片", "v": "1552"},
                    {"n": "大陆情色片", "v": "1555"},
                    {"n": "香港情色片", "v": "1553"},
                    {"n": "台湾情色片", "v": "1554"},
                    {"n": "美国情色片", "v": "1556"},
                    {"n": "欧洲情色片", "v": "1557"},
                    {"n": "印度情色片", "v": "1558"},
                    {"n": "东南亚情色片", "v": "1559"},
                    {"n": "其它情色片", "v": "1550"}
                ]}
            ]}
        ]
        
        # 将所有筛选器数据添加进 result['filters'] 中
        result['filters'] = {
            "10": result['class'][0]['filters'],
            "11": result['class'][1]['filters'],
            "12": result['class'][2]['filters'],
            "13": result['class'][3]['filters'],
            "15": result['class'][4]['filters'],
        }

        return result

    def homeVideoContent(self):
        try:
            url = self.get_current_host()
            r = self.fetch(url, headers={"User-Agent": self.ua})
            
            if r.status_code != 200:
                self.log(f"首页推荐请求失败，状态码：{r.status_code}", "ERROR")
                return {'list': []}
            
            # 使用新的正则表达式来获取视频列表项
            pattern = r'<a class="link" href="(/post/[^"]+\.html)".*?<img[^>]*data-src="([^"]+)".*?alt="([^"]+)".*?(?:<div class="tag1[^>]*>([^<]+)</div>)?.*?(?:<div class="tag2">([^<]+)</div>)?'
            matches = re.findall(pattern, r.text, re.DOTALL)
            
            video_list = []
            for match in matches[:12]:  # 限制12个结果
                try:
                    link, img_src, title, tag1, tag2 = match
                    vod_id_match = re.search(r'/post/(.*?)\.html', link)
                    if not vod_id_match:
                        continue
                    
                    vod_id = vod_id_match.group(1)
                    
                    # 组合备注信息
                    remarks = []
                    if tag1:
                        remarks.append(tag1.strip())
                    if tag2:
                        remarks.append(tag2.strip())

                    vod_remarks = " / ".join(remarks) if remarks else "最新"
                    
                    # 处理图片URL
                    if img_src.startswith('//'):
                        img_url = 'https:' + img_src
                    elif not img_src.startswith('http'):
                        img_url = urljoin(self.get_current_host(), img_src)
                    else:
                        img_url = img_src
                    
                    vod = {
                        'vod_id': vod_id,
                        'vod_name': title.strip(),
                        'vod_pic': img_url,
                        'vod_remarks': vod_remarks
                    }
                    
                    video_list.append(vod)
                except Exception as e:
                    self.log(f"首页推荐项解析失败：{str(e)}", "ERROR")
                    continue
            
            self.log(f"首页推荐成功解析{len(video_list)}个项", "INFO")
            return {'list': video_list}
        except Exception as e:
            self.log(f"首页推荐内容获取失败：{str(e)}", "ERROR")
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        result = {'list': [], 'page': pg, 'pagecount': 1, 'limit': 40, 'total': 0}
        try:
            # 修复：检查 extend 参数，以支持筛选功能
            filter_tid = tid
            if extend and 'class' in extend and extend['class']:
                filter_tid = extend['class']
            
            # 修复分类URL构建，使用 filter_tid
            url = f"{self.get_current_host()}/cat/{filter_tid}"
            if int(pg) > 1:
                url = f"{url}-{pg}"
            url = f"{url}.html"
            
            r = self.fetch(url, headers={"User-Agent": self.ua})
            if r.status_code != 200:
                self.log(f"分类页请求失败，URL：{url}，状态码：{r.status_code}", "ERROR")
                return result
            
            # 修复：使用更健壮的正则来提取所有视频列表项
            items = re.findall(r'<div class="item">(.*?)<a class="title"', r.text, re.DOTALL)
            
            for item in items:
                try:
                    link_match = re.search(r'<a class="link" href="(/post/[^"]+\.html)"', item)
                    img_match = re.search(r'<img[^>]*data-src="([^"]+)"', item)
                    title_match = re.search(r'data-src="[^"]+" alt="([^"]+)"', item)
                    tag1_match = re.search(r'<div class="tag1[^>]*>([^<]+)</div>', item)
                    tag2_match = re.search(r'<div class="tag2">([^<]+)</div>', item)
                    
                    if not link_match or not img_match or not title_match:
                        continue
                    
                    link = link_match.group(1)
                    img_src = img_match.group(1)
                    title = title_match.group(1).strip()
                    vod_id = re.search(r'/post/(.*?)\.html', link).group(1)
                    
                    remarks = []
                    if tag1_match:
                        remarks.append(tag1_match.group(1).strip())
                    if tag2_match:
                        remarks.append(tag2_match.group(1).strip())
                    
                    vod_remarks = " / ".join(remarks) if remarks else "分类内容"
                    
                    # 处理图片URL
                    if img_src.startswith('//'):
                        img_url = 'https:' + img_src
                    elif not img_src.startswith('http'):
                        img_url = urljoin(self.get_current_host(), img_src)
                    else:
                        img_url = img_src
                    
                    vod = {
                        'vod_id': vod_id,
                        'vod_name': title,
                        'vod_pic': img_url,
                        'vod_remarks': vod_remarks
                    }
                    
                    result['list'].append(vod)
                except Exception as e:
                    self.log(f"分类项解析失败：{str(e)}", "ERROR")
                    continue
            
            # 修复：使用更健壮的正则来提取分页信息
            page_pattern = r'/cat/\d+-(\d+)\.html'
            page_matches = re.findall(page_pattern, r.text)
            
            if page_matches:
                page_nums = [int(num) for num in page_matches if num.isdigit()]
                result['pagecount'] = max(page_nums) if page_nums else 1
            else:
                result['pagecount'] = int(pg)

            self.log(f"分类{tid}第{pg}页：解析{len(result['list'])}项", "INFO")
            return result
        except Exception as e:
            self.log(f"分类内容获取失败：{str(e)}", "ERROR")
            return result

    def detailContent(self, ids):
        result = {"list": []}
        if not ids:
            return result
        
        vod_id = ids[0]
        try:
            detail_url = f"{self.get_current_host()}/post/{vod_id}.html"
            r = self.fetch(detail_url, headers={"User-Agent": self.ua})
            if r.status_code != 200:
                self.log(f"详情页请求失败，状态码：{r.status_code}", "ERROR")
                return result
            
            soup = BeautifulSoup(r.text, 'html.parser')

            # 提取标题
            title_tag = soup.find('title')
            title = title_tag.text.replace(" - 小鴨看看", "").strip() if title_tag else "未知标题"
            
            # 提取封面图
            cover_tag = soup.find('img', {'data-poster': True})
            cover_url = ""
            if cover_tag and cover_tag.get('data-poster'):
                cover_url = cover_tag['data-poster']
                if cover_url.startswith('//'):
                    cover_url = 'https:' + cover_url
                elif not cover_url.startswith('http'):
                    cover_url = urljoin(self.get_current_host(), cover_url)
            
            # 提取描述
            desc_tag = soup.find('meta', {'name': 'description'})
            desc = desc_tag['content'].strip() if desc_tag and desc_tag.get('content') else ""

            # 提取播放线路和剧集
            play_sources = []
            play_urls = []
            
            # 从JavaScript中提取播放信息
            pp_data = None
            script_pattern = re.search(r'var pp\s*=\s*({.*?});', r.text, re.DOTALL)
            if script_pattern:
                try:
                    pp_data = json.loads(script_pattern.group(1))
                except Exception as e:
                    self.log(f"解析JavaScript播放信息失败：{str(e)}", "ERROR")
            
            # 查找所有播放线路的容器
            source_blocks = soup.find_all('div', class_='source')

            for idx, block in enumerate(source_blocks):
                source_name_tag = block.find('span', class_='name')
                source_name = source_name_tag.text.strip() if source_name_tag else f"线路{idx+1}"
                
                resolution_tag = block.find('span', class_='res')
                resolution = resolution_tag.text.strip() if resolution_tag else ""
                
                # 组合线路名称和分辨率
                full_source_name = f"{source_name} ({resolution})" if resolution else source_name
                play_sources.append(full_source_name)
                
                episodes = []
                if pp_data and 'lines' in pp_data and len(pp_data['lines']) > idx:
                    urls = pp_data['lines'][idx][3]
                    
                    if isinstance(urls, list) and urls:
                        for ep_idx, url in enumerate(urls):
                            if isinstance(url, str) and any(url.endswith(fmt) for fmt in self.VIDEO_FORMATS):
                                # 修复集数命名逻辑
                                episode_name_match = re.search(r'ep-([\d\w]+)', url)
                                if episode_name_match:
                                    episode_name = f"第{episode_name_match.group(1)}集"
                                elif len(urls) == 1:
                                    episode_name = "全集"
                                else:
                                    episode_name = f"第{ep_idx+1}集"
                                    
                                episodes.append(f"{episode_name}${url}")
                
                if episodes:
                    play_urls.append("#".join(episodes))
                else:
                    play_urls.append("")

            vod = {
                "vod_id": vod_id,
                "vod_name": title,
                "vod_pic": cover_url,
                "vod_content": desc,
                "vod_play_from": "$$$".join(play_sources) if play_sources else "",
                "vod_play_url": "$$$".join(play_urls) if play_urls else ""
            }
            
            result["list"].append(vod)
            self.log(f"详情页解析成功，ID：{vod_id}", "INFO")
            return result
        except Exception as e:
            self.log(f"详情页解析失败，ID：{vod_id}，错误：{str(e)}", "ERROR")
            return result

    def playerContent(self, flag, id, vipFlags):
        try:
            # 如果id已经是URL，直接返回
            if id.startswith('http'):
                return {
                    "parse": 0,
                    "playUrl": '',
                    "url": id,
                    "header": {
                        "User-Agent": self.ua,
                        "Referer": self.get_current_host() + "/"
                    }
                }
            
            # 这是一个简单的播放器URL解析，如果原始URL本身就是有效的播放地址，就直接返回
            return {
                "parse": 0,
                "playUrl": '',
                "url": id,
                "header": {
                    "User-Agent": self.ua,
                    "Referer": self.get_current_host() + "/"
                }
            }
        except Exception as e:
            self.log(f"播放地址解析失败：{str(e)}", "ERROR")
            return {"parse": 0, "playUrl": '', "url": id, "header": {"User-Agent": self.ua}}

    def searchContent(self, key, quick):
        result = {"list": []}
        try:
            # 构造Google搜索URL（带站点限定）
            google_search_url = f"https://www.google.com/search?q={quote(key)}&sitesearch=xiaoyakankan.com"
            self.log(f"构造Google搜索URL: {google_search_url}")
            
            # 伪装更多请求头
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://www.google.com/",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive"
            }
            
            r = self.fetch(google_search_url, headers=headers, timeout=10)
            if r.status_code != 200:
                self.log(f"Google搜索请求失败，状态码：{r.status_code}，内容：{r.text[:200]}", "ERROR")
                return result
            
            # 处理gzip压缩响应
            if 'gzip' in r.headers.get('Content-Encoding', ''):
                r._content = gzip.decompress(r.content)
            
            try:
                soup = BeautifulSoup(r.text, 'html.parser')
                # 寻找所有包含搜索结果的a标签
                all_links = soup.find_all('a', href=re.compile(r'/url\?q='))

                for a_tag in all_links[:15]:  # 限制最多15个结果
                    link = a_tag['href']
                    
                    # 解析真实URL
                    parsed_url = urlparse(link)
                    query_params = parse_qs(parsed_url.query)
                    
                    if 'q' in query_params:
                        real_link = query_params['q'][0]
                        
                        # 检查链接是否属于目标站点
                        if self.get_current_host() in real_link:
                            # 尝试从链接中提取影片ID
                            vod_id_match = re.search(r'/post/([^/]+)\.html', real_link)
                            if not vod_id_match:
                                continue
                            
                            vod_id = vod_id_match.group(1)
                            
                            # 获取标题和图片（这里因为Google搜索结果没有图片，所以图片留空）
                            title_tag = a_tag.find('h3')
                            if not title_tag:
                                # 有时标题在父级或其他元素中
                                title_tag = a_tag.find('div', class_='g')
                            
                            title = title_tag.text.strip() if title_tag else "未知标题"

                            vod = {
                                "vod_id": vod_id,
                                "vod_name": title,
                                "vod_pic": "",
                                "vod_remarks": "Google搜索结果"
                            }
                            
                            result["list"].append(vod)
                
            except Exception as e:
                self.log(f"解析Google搜索结果失败：{str(e)}", "ERROR")
                return result
            
            self.log(f"Google搜索成功解析{len(result['list'])}个项", "INFO")
            return result
        except Exception as e:
            self.log(f"搜索内容获取失败：{str(e)}", "ERROR")
            return result

    def isVideoFormat(self, url):
        """判断是否为视频格式"""
        return any(url.lower().endswith(fmt) for fmt in self.VIDEO_FORMATS)

    def manualVideoCheck(self):
        pass

    def localProxy(self, param):
        pass
