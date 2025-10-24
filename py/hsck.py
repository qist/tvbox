import re
import sys
import urllib.parse
import threading
import time
import requests
import base64
import gzip
import json
from io import BytesIO
from pyquery import PyQuery as pq

sys.path.append('..')
from base.spider import Spider

class Spider(Spider):
    def __init__(self):
        self.name = "黄色仓库"
        self.host = self.getDynamicHost()
        self.classes = self.preprocessClasses()
        
    def getName(self):
        return self.name
    
    def getDynamicHost(self):
        """动态获取主机地址"""
        try:
            # 解码base64获取初始主机
            initial_host = base64.b64decode('aHR0cDovL2hzY2submV0').decode('utf-8')
            
            # 获取初始页面
            response = requests.get(initial_host, headers=self.header)
            html = response.text
            
            # 匹配strU参数
            strU_match = re.search(r'strU="(.*?)"', html)
            if not strU_match:
                return initial_host
                
            strU = strU_match.group(1)
            locationU = strU + initial_host.rstrip('/') + '/&p=/'
            
            # 获取重定向地址
            redirect_response = requests.get(locationU, headers=self.header, allow_redirects=False)
            if 'location' in redirect_response.headers:
                return redirect_response.headers['location']
            else:
                # 尝试从JSON响应中获取
                try:
                    data = redirect_response.json()
                    return data.get('location', initial_host)
                except:
                    return initial_host
                    
        except Exception as e:
            print(f"获取动态主机失败: {e}")
            return "http://6590ck.cc/"

    def preprocessClasses(self):
        """预处理分类数据"""
        return [
            {"type_name": "日韩AV", "type_id": "1"},
            {"type_name": "国产系列", "type_id": "2"}, 
            {"type_name": "欧美", "type_id": "3"},
            {"type_name": "成人动漫", "type_id": "4"},
            {"type_name": "日本有码", "type_id": "7"},
            {"type_name": "一本道高清无码", "type_id": "8"},
            {"type_name": "有码中文字幕", "type_id": "9"},
            {"type_name": "日本无码", "type_id": "10"},
            {"type_name": "国产视频", "type_id": "15"},
            {"type_name": "欧美高清", "type_id": "21"},
            {"type_name": "动漫剧情", "type_id": "22"}
        ]
    
    def init(self, extend):
        pass
        
    def isVideoFormat(self, url):
        pass
        
    def manualVideoCheck(self):
        pass
        
    def homeContent(self, filter):
        result = {}
        result['class'] = self.classes
        return result

    def homeVideoContent(self):
        """推荐内容"""
        result = {}
        try:
            url = f"{self.host.rstrip('/')}/"
            rsp = self.fetch(url)
            root = pq(rsp.text)
            
            videos = []
            list_items = root('.stui-vodlist li')
            
            for item in list_items.items():
                vid = item.find('a').attr('href')
                if not vid or not vid.startswith('/vodplay/'):
                    continue
                    
                name = item.find('h4').text()
                img = item.find('a').attr('data-original')
                remark = item.find('.pic-text').text()
                
                if not name or not img:
                    continue
                
                videos.append({
                    "vod_id": vid,  # 只保存相对路径
                    "vod_name": name,
                    "vod_pic": self.getFullUrl(img),
                    "vod_remarks": remark
                })
            
            result['list'] = videos
        except Exception as e:
            print(f"获取推荐内容失败: {e}")
            result['list'] = []
            
        return result

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        try:
            url = f"{self.host.rstrip('/')}/vodtype/{tid}-{pg}.html"
            rsp = self.fetch(url)
            root = pq(rsp.text)
            
            videos = []
            list_items = root('.stui-vodlist li')
            
            for item in list_items.items():
                vid = item.find('a').attr('href')
                if not vid or not vid.startswith('/vodplay/'):
                    continue
                    
                name = item.find('h4').text()
                img = item.find('a').attr('data-original')
                remark = item.find('.pic-text').text()
                
                if not name or not img:
                    continue
                
                videos.append({
                    "vod_id": vid,  # 只保存相对路径
                    "vod_name": name,
                    "vod_pic": self.getFullUrl(img),
                    "vod_remarks": remark
                })
            
            result['list'] = videos
            result['page'] = int(pg)
            result['pagecount'] = 9999
            result['limit'] = 6
            result['total'] = 999999
            
        except Exception as e:
            print(f"获取分类内容失败: {e}")
            result['list'] = []
            result['page'] = 1
            result['pagecount'] = 1
            result['limit'] = 6
            result['total'] = 0
            
        return result

    def extractM3U8Url(self, script_text):
        """专门提取m3u8播放链接的方法"""
        m3u8_urls = []
        
        print("开始提取m3u8链接...")
        
        # 方法1: 从player_aaaa JavaScript变量中提取
        player_patterns = [
            r'var\s+player_aaaa\s*=\s*({.*?});',
            r'player_aaaa\s*=\s*({.*?});',
            r'var\s+player_aaaa\s*=\s*({.*?})\s*<\/script>',
            r'player_aaaa\s*=\s*({.*?})\s*<\/script>'
        ]
        
        for pattern in player_patterns:
            player_match = re.search(pattern, script_text, re.DOTALL)
            if player_match:
                try:
                    player_data_str = player_match.group(1)
                    print(f"找到player_aaaa数据: {player_data_str[:200]}...")
                    
                    # 修复JSON字符串
                    player_data_str = player_data_str.replace('\\/', '/')
                    player_data = json.loads(player_data_str)
                    
                    m3u8_url = player_data.get('url')
                    if m3u8_url and '.m3u8' in m3u8_url:
                        print(f"从player_aaaa提取到m3u8: {m3u8_url}")
                        # 确保URL完整
                        if not m3u8_url.startswith('http'):
                            if m3u8_url.startswith('//'):
                                m3u8_url = 'https:' + m3u8_url
                            else:
                                m3u8_url = self.getFullUrl(m3u8_url)
                        m3u8_urls.append(m3u8_url)
                        return m3u8_urls  # 找到就返回
                        
                except Exception as e:
                    print(f"解析player_aaaa失败: {e}")
        
        # 方法2: 直接搜索m3u8链接
        m3u8_patterns = [
            r'"url"\s*:\s*"([^"]+\.m3u8[^"]*)"',
            r'url\s*:\s*"([^"]+\.m3u8[^"]*)"',
            r'src\s*:\s*"([^"]+\.m3u8[^"]*)"',
            r'file\s*:\s*"([^"]+\.m3u8[^"]*)"',
            r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*'
        ]
        
        for pattern in m3u8_patterns:
            matches = re.findall(pattern, script_text)
            for match in matches:
                if '.m3u8' in match and match not in m3u8_urls:
                    print(f"从正则匹配提取到m3u8: {match}")
                    # 确保URL完整
                    if not match.startswith('http'):
                        if match.startswith('//'):
                            match = 'https:' + match
                        else:
                            match = self.getFullUrl(match)
                    m3u8_urls.append(match)
                    return m3u8_urls  # 找到就返回
        
        print("未找到m3u8播放链接")
        return m3u8_urls

    def detailContent(self, array):
        """二级详情页面解析 - 修复播放链接提取及简介使用标题"""
        result = {}
        try:
            vid = array[0]
            # 确保vid是完整URL
            if not vid.startswith('http'):
                vid = self.getFullUrl(vid)
            
            print(f"开始解析详情页面: {vid}")
            rsp = self.fetch(vid)
            root = pq(rsp.text)
            
            # 提取基本信息
            title = root('.stui-pannel__head .title').text()
            if not title:
                title = root('title').text().split(' - ')[0]
            
            # 提取封面图
            pic = root('.stui-vodlist__thumb').attr('data-original') or root('.stui-vodlist__thumb').attr('src')
            if not pic:
                pic = root('img').attr('src')
            
            # 获取所有script内容
            script_text = root('script').text()
            
            # 提取m3u8播放链接
            m3u8_urls = self.extractM3U8Url(script_text)
            
            # 构建播放链接
            play_urls = []
            if m3u8_urls:
                for i, m3u8_url in enumerate(m3u8_urls):
                    play_urls.append(f"线路{i+1}${m3u8_url}")
            else:
                # 如果没有找到m3u8链接，尝试从页面其他位置提取
                print("尝试从页面其他位置提取播放链接...")
                # 从iframe中提取
                iframe_src = root('iframe').attr('src')
                if iframe_src and 'm3u8' in iframe_src:
                    if not iframe_src.startswith('http'):
                        iframe_src = self.getFullUrl(iframe_src)
                    play_urls.append(f"iframe线路${iframe_src}")
                else:
                    # 最后使用详情页URL
                    play_urls.append(f"详情页线路${vid}")
            
            # 用视频标题作为简介，避免没有简介内容
            vod = {
                "vod_id": array[0],  # 保持原始ID
                "vod_name": title,
                "vod_pic": self.getFullUrl(pic) if pic else "",
                "vod_content": title,  # 用标题当简介
                "vod_play_from": "老僧酿酒",
                "vod_play_url": "#".join(play_urls)  # 使用#分隔多个播放源
            }
            
            result['list'] = [vod]
            print(f"详情页解析完成，播放链接: {vod['vod_play_url']}")
            
        except Exception as e:
            print(f"解析详情页面失败: {e}")
            import traceback
            traceback.print_exc()
            # 返回基础信息
            result['list'] = [{
                "vod_id": array[0],
                "vod_name": "未知标题",
                "vod_pic": "",
                "vod_content": "",
                "vod_play_from": "默认线路",
                "vod_play_url": f"详情页线路${array[0]}"
            }]
            
        return result

    def searchContent(self, key, quick):
        result = {}
        try:
            # 使用搜索URL
            search_url = f"{self.host.rstrip('/')}/vodsearch/-------------.html?wd={urllib.parse.quote(key)}"
            rsp = self.fetch(search_url)
            root = pq(rsp.text)
            
            videos = []
            list_items = root('.stui-vodlist li')
            
            for item in list_items.items():
                vid = item.find('a').attr('href')
                if not vid or not vid.startswith('/vodplay/'):
                    continue
                    
                name = item.find('h4').text()
                img = item.find('a').attr('data-original')
                remark = item.find('.pic-text').text()
                
                if not name or not img:
                    continue
                
                videos.append({
                    "vod_id": vid,  # 只保存相对路径
                    "vod_name": name,
                    "vod_pic": self.getFullUrl(img),
                    "vod_remarks": remark
                })
            
            result['list'] = videos
        except Exception as e:
            print(f"搜索失败: {e}")
            result['list'] = []
            
        return result

    def playerContent(self, flag, id, vipFlags):
        """播放页面解析 - 修复数组越界问题"""
        result = {}
        try:
            print(f"playerContent被调用: flag={flag}, id={id}")
            
            # 如果id已经是m3u8链接，直接返回
            if id.startswith('http') and '.m3u8' in id:
                result["parse"] = 0
                result["playUrl"] = ""
                result["url"] = id
                result["header"] = self.header
                print(f"直接返回m3u8链接: {id}")
                return result
            
            # 如果id是播放线路格式，提取m3u8链接
            if '#' in id:
                play_sources = id.split('#')
                for source in play_sources:
                    if '$' in source:
                        _, url = source.split('$', 1)
                        if '.m3u8' in url:
                            result["parse"] = 0
                            result["playUrl"] = ""
                            result["url"] = url
                            result["header"] = self.header
                            print(f"从播放线路提取到m3u8: {url}")
                            return result
            
            # 如果id是详情页链接，重新解析详情页
            print(f"重新解析详情页获取m3u8: {id}")
            detail_result = self.detailContent([id])
            
            if detail_result and 'list' in detail_result and detail_result['list']:
                vod = detail_result['list'][0]
                play_url = vod.get('vod_play_url', '')
                print(f"从详情页获取的播放链接: {play_url}")
                
                # 解析播放链接
                if '#' in play_url:
                    play_sources = play_url.split('#')
                    for source in play_sources:
                        if '$' in source:
                            _, url = source.split('$', 1)
                            if '.m3u8' in url:
                                result["parse"] = 0
                                result["playUrl"] = ""
                                result["url"] = url
                                result["header"] = self.header
                                print(f"最终提取到m3u8: {url}")
                                return result
                
                # 如果没有找到m3u8，使用第一个播放源
                if play_sources:
                    first_source = play_sources[0]
                    if '$' in first_source:
                        _, url = first_source.split('$', 1)
                        result["parse"] = 0
                        result["playUrl"] = ""
                        result["url"] = url
                        result["header"] = self.header
                        print(f"使用第一个播放源: {url}")
                        return result
            
            # 如果所有方法都失败，返回空结果
            print("无法提取播放链接，返回空结果")
            return {}
            
        except Exception as e:
            print(f"解析播放页面失败: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def getFullUrl(self, url):
        """获取完整的URL"""
        if not url:
            return ""
        if url.startswith('http'):
            return url
        if url.startswith('//'):
            return f"https:{url}"
        return f"{self.host.rstrip('/')}{url}"

    config = {
        "player": {},
        "filter": {}
    }
    header = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Referer": "https://hsck123.com/"
    }

    def localProxy(self, param):
        action = {}
        return action