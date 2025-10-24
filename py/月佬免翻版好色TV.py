import re
import sys
import urllib.parse
import threading
import time
import requests
from pyquery import PyQuery as pq

sys.path.append('..')
from base.spider import Spider

class Spider(Spider):
    def __init__(self):
        # 基础配置
        self.name = '好色TV（优）'
        self.host = 'https://hsex.icu/'
        self.candidate_hosts = [
            "https://hsex.icu/",
            "https://hsex1.icu/",
            "https://hsex.tv/"
        ]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': self.host
        }
        self.timeout = 5000
        
        # 分类映射（关键修复：视频分类url_suffix设为空，适配list-{pg}.htm格式）
        self.class_map = {
            '视频': {'type_id': 'list', 'url_suffix': ''},  # 修复点1：视频分类后缀为空
            '周榜': {'type_id': 'top7', 'url_suffix': 'top7'},
            '月榜': {'type_id': 'top', 'url_suffix': 'top'},
            '5分钟+': {'type_id': '5min', 'url_suffix': '5min'},
            '10分钟+': {'type_id': 'long', 'url_suffix': 'long'}
        }

    def getName(self):
        return self.name

    def init(self, extend=""):
        # 尝试获取最快可用域名
        self.host = self.get_fastest_host()
        self.headers['Referer'] = self.host

    def isVideoFormat(self, url):
        if not url:
            return False
        return any(fmt in url.lower() for fmt in ['.mp4', '.m3u8', '.flv', '.avi'])

    def manualVideoCheck(self):
        def check(url):
            if not self.isVideoFormat(url):
                return False
            try:
                resp = self.fetch(url, headers=self.headers, method='HEAD', timeout=3)
                return resp.status_code in (200, 302) and 'video' in resp.headers.get('Content-Type', '')
            except:
                return False
        return check

    def get_fastest_host(self):
        """测试候选域名，返回最快可用的"""
        results = {}
        threads = []

        def test_host(url):
            try:
                start_time = time.time()
                resp = requests.head(url, headers=self.headers, timeout=2, allow_redirects=False)
                if resp.status_code in (200, 301, 302):
                    delay = (time.time() - start_time) * 1000
                    results[url] = delay
                else:
                    results[url] = float('inf')
            except:
                results[url] = float('inf')

        for host in self.candidate_hosts:
            t = threading.Thread(target=test_host, args=(host,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        valid_hosts = [(h, d) for h, d in results.items() if d != float('inf')]
        return valid_hosts[0][0] if valid_hosts else self.candidate_hosts[0]

    def homeContent(self, filter):
        result = {}
        # 构造分类列表
        classes = []
        for name, info in self.class_map.items():
            classes.append({
                'type_name': name,
                'type_id': info['type_id']
            })
        result['class'] = classes
        
        try:
            # 获取首页内容
            html = self.fetch_with_retry(self.host, retry=2, timeout=5).text
            data = pq(html)
            
            # 提取视频列表
            vlist = []
            items = data('.row .col-xs-6.col-md-3')
            for item in items.items():
                try:
                    title = item('h5').text().strip()
                    if not title:
                        continue
                    
                    # 提取图片URL
                    style = item('.image').attr('style') or ''
                    pic_match = re.search(r'url\(["\']?([^"\']+)["\']?\)', style)
                    vod_pic = pic_match.group(1) if pic_match else ''
                    if vod_pic and not vod_pic.startswith('http'):
                        vod_pic = f"{self.host.rstrip('/')}/{vod_pic.lstrip('/')}"
                    
                    # 提取时长备注
                    desc = item('.duration').text().strip() or '未知'
                    
                    # 提取视频ID
                    href = item('a').attr('href') or ''
                    if not href:
                        continue
                    vod_id = href.split('/')[-1]
                    if not vod_id.endswith('.htm'):
                        vod_id += '.htm'
                    
                    vlist.append({
                        'vod_id': vod_id,
                        'vod_name': title,
                        'vod_pic': vod_pic,
                        'vod_remarks': desc
                    })
                except Exception as e:
                    print(f"解析首页视频项失败: {e}")
                    continue
            
            result['list'] = vlist
        except Exception as e:
            print(f"首页解析失败: {e}")
            result['list'] = []
        return result

    def homeVideoContent(self):
        return []

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        try:
            # 匹配分类信息
            cate_info = None
            for name, info in self.class_map.items():
                if info['type_id'] == tid:
                    cate_info = info
                    break
            
            if not cate_info:
                result['list'] = []
                return result
            
            # 关键修复：区分视频分类与其他分类的URL格式
            if tid == 'list':  # 视频分类（type_id为list）
                url = f"{self.host}list-{pg}.htm"  # 格式：list-1.htm、list-2.htm
            else:  # 其他分类（周榜/月榜等）：xxx_list-{pg}.htm
                url = f"{self.host}{cate_info['url_suffix']}_list-{pg}.htm"
            
            # 请求分类页
            html = self.fetch(url, headers=self.headers, timeout=8).text
            html = html.encode('utf-8', errors='ignore').decode('utf-8')
            data = pq(html)
            
            # 提取视频列表
            vlist = []
            items = data('.row .col-xs-6.col-md-3')
            for item in items.items():
                try:
                    title = item('h5').text().strip()
                    if not title:
                        continue
                    
                    style = item('.image').attr('style') or ''
                    pic_match = re.search(r'url\(["\']?([^"\']+)["\']?\)', style)
                    vod_pic = pic_match.group(1) if pic_match else ''
                    if vod_pic and not vod_pic.startswith('http'):
                        vod_pic = f"{self.host.rstrip('/')}/{vod_pic.lstrip('/')}"
                    
                    desc = item('.duration').text().strip() or '未知'
                    
                    href = item('a').attr('href') or ''
                    if not href:
                        continue
                    vod_id = href.split('/')[-1]
                    if not vod_id.endswith('.htm'):
                        vod_id += '.htm'
                    
                    vlist.append({
                        'vod_id': vod_id,
                        'vod_name': title,
                        'vod_pic': vod_pic,
                        'vod_remarks': desc
                    })
                except Exception as e:
                    print(f"解析分类视频项失败: {e}")
                    continue
            
            # 提取总页数
            pagecount = 1
            try:
                pagination = data('.pagination1 li a')
                page_nums = []
                for a in pagination.items():
                    text = a.text().strip()
                    if text.isdigit():
                        page_nums.append(int(text))
                if page_nums:
                    pagecount = max(page_nums)
            except:
                pagecount = 1
            
            result['list'] = vlist
            result['page'] = pg
            result['pagecount'] = pagecount
            result['limit'] = len(vlist)
            result['total'] = 999999
        except Exception as e:
            print(f"分类解析失败: {e}")
            result['list'] = []
            result['page'] = pg
            result['pagecount'] = 1
            result['limit'] = 0
            result['total'] = 0
        return result

    def detailContent(self, ids):
        try:
            if not ids or not ids[0]:
                return {'list': []}
            
            vod_id = ids[0].strip()
            if not vod_id.endswith('.htm'):
                vod_id += '.htm'
            url = f"{self.host}{vod_id.lstrip('/')}"
            
            html = self.fetch_with_retry(url, retry=2, timeout=8).text
            html = html.encode('utf-8', errors='ignore').decode('utf-8')
            data = pq(html)
            
            # 提取标题
            title = data('.panel-title, .video-title, h1').text().strip() or '未知标题'
            
            # 提取封面图
            vod_pic = ''
            poster_style = data('.vjs-poster').attr('style') or ''
            pic_match = re.search(r'url\(["\']?([^"\']+)["\']?\)', poster_style)
            if pic_match:
                vod_pic = pic_match.group(1)
            if not vod_pic:
                vod_pic = data('.video-pic img, .vjs-poster img, .thumbnail img').attr('src') or ''
            if vod_pic and not vod_pic.startswith('http'):
                vod_pic = f"{self.host}{vod_pic.lstrip('/')}"
            
            # 提取时长和观看量
            duration = '未知'
            views = '未知'
            info_items = data('.panel-body .col-md-3, .video-info .info-item, .info p')
            for item in info_items.items():
                text = item.text().strip()
                if '时长' in text or 'duration' in text.lower():
                    duration = text.replace('时长：', '').replace('时长', '').strip()
                elif '观看' in text or 'views' in text.lower():
                    views_match = re.search(r'(\d+\.?\d*[kK]?)次观看', text)
                    if views_match:
                        views = views_match.group(1)
                    else:
                        views = text.replace('观看：', '').replace('观看', '').strip()
            remarks = f"{duration} | {views}"
            
            # 提取播放地址
            video_url = ''
            m3u8_match = re.search(r'videoUrl\s*=\s*["\']([^"\']+\.m3u8)["\']', html)
            if m3u8_match:
                video_url = m3u8_match.group(1)
            if not video_url:
                source = data('source[src*=".m3u8"], source[src*=".mp4"]')
                video_url = source.attr('src') or ''
            if not video_url:
                js_matches = re.findall(r'(https?://[^\s"\']+\.(?:m3u8|mp4))', html)
                if js_matches:
                    video_url = js_matches[0]
            
            if video_url and not video_url.startswith('http'):
                video_url = f"{self.host}{video_url.lstrip('/')}"
        
            vod = {
                'vod_id': vod_id,
                'vod_name': title,
                'vod_pic': vod_pic,
                'vod_remarks': remarks,
                'vod_play_from': '好色TV（优）',
                'vod_play_url': f'正片${video_url}' if video_url else '正片$暂无地址'
            }
            return {'list': [vod]}
        except Exception as e:
            print(f"详情解析失败: {e}")
            return {'list': []}

    def searchContent(self, key, quick, pg=1):
        try:
            # 关键词合法性校验
            if not key.strip():
                print("搜索关键词不能为空")
                return {'list': [], 'page': int(pg), 'pagecount': 1, 'limit': 0, 'total': 0}
            
            # 编码关键词
            encoded_key = urllib.parse.quote(key.strip(), encoding='utf-8', errors='replace')
            
            # 构造搜索URL
            search_url = f"{self.host}search.htm"
            params = {
                'search': encoded_key,
                'page': int(pg)
            }
            
            # 发起请求
            resp = self.fetch(
                url=search_url,
                headers=self.headers,
                params=params,
                timeout=8
            )
            if resp.status_code not in (200, 302):
                print(f"搜索页面请求失败，URL：{resp.url}，状态码：{resp.status_code}")
                return {'list': [], 'page': int(pg), 'pagecount': 1, 'limit': 0, 'total': 0}
            
            # 处理页面内容
            html = resp.text.encode('utf-8', errors='ignore').decode('utf-8')
            data = pq(html)
            
            # 检测无结果场景
            no_result_texts = ['没有找到相关视频', '无搜索结果', 'No results found', '未找到匹配内容']
            no_result = any(data(f'div:contains("{text}"), p:contains("{text}")').text() for text in no_result_texts)
            if no_result:
                print(f"搜索关键词「{key}」第{pg}页无结果")
                return {'list': [], 'page': int(pg), 'pagecount': 1, 'limit': 0, 'total': 0}
            
            # 解析搜索结果
            vlist = []
            items = data('.row .col-xs-6.col-md-3')
            for item in items.items():
                try:
                    title = item('h5').text().strip()
                    if not title:
                        continue
                    
                    style = item('.image').attr('style') or ''
                    pic_match = re.search(r'url\(["\']?([^"\']+)["\']?\)', style)
                    vod_pic = pic_match.group(1) if pic_match else ''
                    if vod_pic and not vod_pic.startswith(('http://', 'https://')):
                        vod_pic = f"{self.host.rstrip('/')}/{vod_pic.lstrip('/')}"
                    
                    desc = item('.duration').text().strip() or '未知时长'
                    
                    href = item('a').attr('href') or ''
                    if not href:
                        continue
                    vod_id = href.split('/')[-1]
                    if not vod_id.endswith('.htm'):
                        vod_id += '.htm'
                    
                    vlist.append({
                        'vod_id': vod_id,
                        'vod_name': title,
                        'vod_pic': vod_pic,
                        'vod_remarks': desc
                    })
                except Exception as e:
                    print(f"解析单条搜索结果失败：{e}（跳过该条）")
                    continue
            
            # 解析总页数
            pagecount = 1
            try:
                pagination = data('.pagination1 li a')
                page_nums = []
                for a in pagination.items():
                    text = a.text().strip()
                    if text.isdigit():
                        page_nums.append(int(text))
                if page_nums:
                    pagecount = max(page_nums)
                print(f"搜索关键词「{key}」分页解析完成，共{pagecount}页")
            except Exception as e:
                print(f"解析分页失败（默认单页）：{e}")
                pagecount = 1
            
            # 返回结果（修复点2：补全page键的引号，修正语法错误）
            total = len(vlist) * pagecount
            print(f"搜索关键词「{key}」第{pg}页处理完成，结果{len(vlist)}条，总页数{pagecount}")
            return {
                'list': vlist,
                'page': int(pg),  # 原代码此处缺少引号，导致语法错误
                'pagecount': pagecount,
                'limit': len(vlist),
                'total': total
            }
        except Exception as e:
            print(f"搜索功能整体异常：{e}")
            return {
                'list': [],
                'page': int(pg),                  'pagecount': 1,
                'limit': 0,
                'total': 0
            }

    def playerContent(self, flag, id, vipFlags):
        headers = self.headers.copy()
        headers.update({
            'Referer': self.host,
            'Origin': self.host.rstrip('/'),
            'Host': urllib.parse.urlparse(self.host).netloc,
        })
        
        # 根据rule中的double设置
        return {
            'parse': 1,  # 根据rule中的play_parse设置
            'url': id,
            'header': headers,
            'double': True  # 根据rule中的double设置
        }

    def localProxy(self, param):
        try:
            url = param['url']
            if url and not url.startswith(('http://', 'https://')):
                url = f"{self.host.rstrip('/')}/{url.lstrip('/')}"
            
            img_headers = self.headers.copy()
            img_headers.update({'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'})
            
            res = self.fetch(url, headers=img_headers, timeout=10)
            content_type = res.headers.get('Content-Type', 'image/jpeg')
            
            return [200, content_type, res.content]
        except Exception as e:
            print(f"图片代理失败: {e}")
            return [200, 'image/jpeg', b'']

    def fetch_with_retry(self, url, retry=2, timeout=5):
        for i in range(retry + 1):
            try:
                resp = self.fetch(f'https://vpsdn.leuse.top/proxy?single=true&url={urllib.parse.quote(url)}',headers=self.headers, timeout=timeout)
                if resp.status_code in (200, 301, 302):
                    return resp
                print(f"请求{url}返回状态码{resp.status_code}，重试中...")
            except Exception as e:
                print(f"第{i+1}次请求{url}失败: {e}")
            if i < retry:
                time.sleep(0.5)
        return type('obj', (object,), {'text': '', 'status_code': 404})

    def fetch(self, url, headers=None, timeout=5, method='GET', params=None):
        headers = headers or self.headers
        params = params or {}
        try:
            if method.upper() == 'GET':
                resp = requests.get(
                    f'https://vpsdn.leuse.top/proxy?single=true&url={urllib.parse.quote(url)}',
                    headers=headers, 
                    timeout=timeout, 
                    allow_redirects=True,
                    params=params  # 支持GET请求带参数，适配搜索分页
                )
            elif method.upper() == 'HEAD':
                resp = requests.head(
                   f'https://vpsdn.leuse.top/proxy?single=true&url={urllib.parse.quote(url)}',
                    headers=headers, 
                    timeout=timeout, 
                    allow_redirects=False,
                    params=params
                )
            else:
                resp = requests.get(  # 默认GET请求，兼容其他方法调用
                   f'https://vpsdn.leuse.top/proxy?single=true&url={urllib.parse.quote(url)}',
                    headers=headers, 
                    timeout=timeout, 
                    allow_redirects=True,
                    params=params
                )
            # 自动适配编码，避免中文乱码
            if 'charset' in resp.headers.get('Content-Type', '').lower():
                resp.encoding = resp.apparent_encoding
            else:
                resp.encoding = 'utf-8'
            return resp
        except Exception as e:
            print(f"网络请求失败({url}): {e}")
            # 返回统一格式空响应，避免后续逻辑崩溃
            return type('obj', (object,), {
                'text': '', 
                'status_code': 500, 
                'headers': {},
                'url': url
            })


# ------------------------------
# 可选测试代码（运行时注释或删除，用于验证功能）
# ------------------------------
if __name__ == "__main__":
    # 初始化爬虫
    spider = Spider()
    spider.init()
    
    # 测试首页内容
    print("=== 测试首页 ===")
    home_data = spider.homeContent(filter='')
    print(f"首页分类数：{len(home_data['class'])}")
    print(f"首页视频数：{len(home_data['list'])}")
    
    # 测试视频分类（修复后的数据获取）
    print("\n=== 测试视频分类（第1页） ===")
    cate_data = spider.categoryContent(tid='list', pg=1, filter='', extend='')
    print(f"视频分类第1页视频数：{len(cate_data['list'])}")
    print(f"视频分类总页数：{cate_data['pagecount']}")
    
    # 测试搜索功能（修复语法错误后）
    print("\n=== 测试搜索（关键词：测试） ===")
    search_data = spider.searchContent(key="测试", quick=False, pg=1)
    print(f"搜索结果数：{len(search_data['list'])}")
    print(f"搜索总页数：{search_data['pagecount']}")
