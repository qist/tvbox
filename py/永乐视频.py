# coding=utf-8
#!/usr/bin/env python3

import re
import sys
import urllib.parse
import requests
import json
import time
import random
from bs4 import BeautifulSoup

# 禁用SSL证书验证警告
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.append('..')
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        return "永乐视频"
    
    def init(self, extend=""):
        self.host = "https://www.ylys.tv"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': self.host
        }
        self.encoding = "UTF-8"
        self.last_search_key = ""
        
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update(self.headers)
        
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def fetch(self, url, headers=None, timeout=30):
        try:
            if headers is None:
                headers = self.headers
            time.sleep(random.uniform(0.5, 1.5))
            response = self.session.get(url, headers=headers, timeout=timeout, verify=False)
            if response.encoding == 'ISO-8859-1':
                response.encoding = self.encoding
            return response
        except Exception as e:
            self.log(f"请求失败: {str(e)}")
            return None

    def homeContent(self, filter):
        result = {
            "class": [
                {'type_id': '1', 'type_name': '电影'},
                {'type_id': '2', 'type_name': '剧集'},
                {'type_id': '3', 'type_name': '综艺'},
                {'type_id': '4', 'type_name': '动漫'}
            ],
            "filters": self._get_filters(),
            "list": []
        }
        try:
            rsp = self.fetch(self.host)
            if rsp and rsp.status_code == 200:
                html = rsp.text
                videos = self._extract_videos_from_html(html, limit=20)
                result['list'] = videos
        except Exception as e:
            self.log(f"首页获取出错: {str(e)}")
        return result

    def categoryContent(self, tid, pg, filter, extend):
        result = {"list": [], "page": int(pg), "pagecount": 99, "limit": 20, "total": 1980}
        try:
            class_filter = extend.get('class', '') if extend else ''
            area_filter = extend.get('area', '') if extend else ''
            lang_filter = extend.get('lang', '') if extend else ''
            year_filter = extend.get('year', '') if extend else ''
            letter_filter = extend.get('letter', '') if extend else ''
            sort_filter = extend.get('sort', '') if extend else ''
            
            if class_filter:
                main_id = class_filter
            else:
                main_id = tid
            
            # 根据示例URL格式构建参数列表：11个参数位，对应索引0-10
            # 格式: /vodshow/{main_id}-{area}-{sort}--{lang}-------{year}/
            params = [
                area_filter,   # 索引0: 地区
                sort_filter,   # 索引1: 排序
                "",            # 索引2: 预留位
                lang_filter,   # 索引3: 语言
                letter_filter, # 索引4: 字母
                "",            # 索引5: 预留位
                "",            # 索引6: 预留位
                "",            # 索引7: 预留位
                "",            # 索引8: 预留位
                "",            # 索引9: 预留位
                year_filter    # 索引10: 年份
            ]
            
            param_str = "-".join(params)
            
            if int(pg) == 1:
                url = f"{self.host}/vodshow/{main_id}-{param_str}/"
            else:
                url = f"{self.host}/vodshow/{main_id}-{param_str}/page/{pg}/"
            
            self.log(f"请求分类URL: {url}")
            rsp = self.fetch(url)
            
            if rsp and rsp.status_code == 200:
                html = rsp.text
                videos = self._extract_videos_with_bs(html)
                result['list'] = videos
                self.log(f"分类{main_id}第{pg}页提取到{len(videos)}条数据")
            else:
                status = rsp.status_code if rsp else "无响应"
                self.log(f"分类页请求失败，状态码: {status}")
                
        except Exception as e:
            self.log(f"分类内容获取出错: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
        return result

    def searchContent(self, key, quick, pg=1):
        result = {"list": []}
        try:
            self.last_search_key = key
            search_key = urllib.parse.quote(key)
            search_url = f"{self.host}/vodsearch/{search_key}-------------/" if int(pg) == 1 else f"{self.host}/vodsearch/{search_key}-------------/page/{pg}/"
            self.log(f"搜索URL: {search_url}")
            
            rsp = self.fetch(search_url)
            if rsp and rsp.status_code == 200:
                html = rsp.text
                videos = self._extract_search_results_with_bs(html)
                result['list'] = videos
                self.log(f"搜索'{key}'第{pg}页提取到{len(videos)}条数据")
            else:
                self.log(f"搜索请求失败，状态码: {rsp.status_code if rsp else '无响应'}")
        except Exception as e:
            self.log(f"搜索出错: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
        return result

    def detailContent(self, ids):
        result = {"list": []}
        try:
            vid = ids[0]
            detail_url = f"{self.host}/voddetail/{vid}/"
            self.log(f"请求详情页: {detail_url}")
            
            rsp = self.fetch(detail_url)
            if not rsp or rsp.status_code != 200:
                return result
                
            html = rsp.text

            play_from = []
            play_url = []
            
            line_pattern = r'<(?:div|a)[^>]*class="[^"]*module-tab-item[^"]*"[^>]*>(?:.*?<span>([^<]+)</span>.*?<small>(\d+)</small>|.*?<span>([^<]+)</span>.*?<small class="no">(\d+)</small>)</(?:div|a)>'
            line_matches = re.findall(line_pattern, html, re.S | re.I)
            
            for match in line_matches:
                if match[0]:
                    line_name, ep_total = match[0], match[1]
                else:
                    line_name, ep_total = match[2], match[3]
                
                if line_name in play_from:
                    continue
                    
                play_from.append(line_name)
                
                line_id_pattern = r'<a[^>]*href="/play/%s-(\d+)-1/"[^>]*>.*?<span>%s</span>' % (vid, re.escape(line_name))
                line_id_match = re.search(line_id_pattern, html, re.S | re.I)
                
                if line_id_match:
                    line_id = line_id_match.group(1)
                else:
                    line_id_map = {
                        "全球3线": "3",
                        "大陆0线": "1",
                        "大陆3线": "4",
                        "大陆5线": "2",
                        "大陆6线": "3"
                    }
                    line_id = line_id_map.get(line_name, "1")
                
                ep_pattern = r'<a class="module-play-list-link" href="/play/%s-%s-(\d+)/"[^>]*>.*?<span>([^<]+)</span></a>' % (vid, line_id)
                ep_matches = re.findall(ep_pattern, html, re.S | re.I)
                
                eps = [f"{ep_name.strip()}${vid}-{line_id}-{ep_num.strip()}" for ep_num, ep_name in ep_matches]
                play_url.append("#".join(eps))

            title_match = re.search(r'<meta property="og:title" content="([^"]+)-[^-]+$"', html, re.S | re.I)
            if not title_match:
                title_match = re.search(r'<h1>.*?<a href="/voddetail/\d+/" title="([^"]+)">', html, re.S | re.I)
            title = title_match.group(1).strip() if title_match else ""

            pic_match = re.search(r'<meta property="og:image" content="([^"]+)"', html, re.S | re.I)
            if not pic_match:
                pic_match = re.search(r'<div class="module-item-pic">.*?data-original="([^"]+)"', html, re.S | re.I)
            pic = pic_match.group(1).strip() if pic_match else ""
            if pic and pic.startswith('/'):
                pic = self.host + pic

            desc_match = re.search(r'<meta property="og:description" content="([^"]+)"', html, re.S | re.I)
            desc = desc_match.group(1).strip() if desc_match else "暂无简介"

            year_match = re.search(r'<a title="(\d+)" href="/vodshow/\d+-----------\1/">', html, re.S | re.I)
            year = year_match.group(1) if year_match else "未知年份"
            area_match = re.search(r'<a title="([^"]+)" href="/vodshow/\d+-%E5%A2%A8%E8%A5%BF%E5%93%A5----------/">', html, re.S | re.I)
            area = area_match.group(1) if area_match else "未知产地"
            type_match = re.search(r'vod_class":"([^"]+)"', html, re.S | re.I)
            type_str = type_match.group(1).replace(",", "/") if type_match else "未知类型"
            remarks = f"{year} | {area} | {type_str} | 共{ep_total}集完结"

            if play_from:
                result['list'] = [{
                    'vod_id': vid,
                    'vod_name': title,
                    'vod_pic': pic,
                    'vod_content': desc,
                    'vod_remarks': remarks,
                    'vod_play_from': "$$$".join(play_from),
                    'vod_play_url': "$$$".join(play_url)
                }]
                self.log(f"详情页提取到{len(play_from)}条线路: {play_from}")
            else:
                self.log("详情页未提取到播放线路")
            
        except Exception as e:
            self.log(f"详情获取出错: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {"parse": 1, "playUrl": "", "url": ""}
        try:
            if "-" not in id:
                return result
            vid, line_id, ep_id = id.split("-")[:3]
            
            line_name_map = {
                "1": "大陆0线",
                "2": "大陆5线",
                "3": "大陆6线",
                "4": "大陆3线"
            }
            play_from = line_name_map.get(line_id, f"线路{line_id}")
            
            play_url = f"{self.host}/play/{id}/"
            self.log(f"请求{play_from}第{ep_id}集播放页: {play_url}")
            
            rsp = self.fetch(play_url)
            if not rsp or rsp.status_code != 200:
                return result
                
            html = rsp.text

            real_url_pattern = r'var player_aaaa=.*?"url":"([^"]+\.m3u8)"'
            real_url_match = re.search(real_url_pattern, html, re.S | re.I)
            
            if real_url_match:
                real_url = real_url_match.group(1).strip()
                real_url = real_url.replace(r'\u002F', '/').replace(r'\/', '/')
                result["parse"] = 0
                result["url"] = real_url
                self.log(f"成功提取{play_from}第{ep_id}集播放地址: {real_url[:60]}...")
            else:
                result["parse"] = 1
                result["url"] = play_url
                self.log("未提取到直接播放地址，返回播放页URL")

        except Exception as e:
            self.log(f"播放链接获取出错: {str(e)}")
            result["url"] = f"{self.host}/play/{id}/" if "-" in id else f"{self.host}/voddetail/{id}/"
            
        return result

    def _get_filters(self):
        return {
            "1": [{"key": "class", "name": "类型", "value": [
                {"n": "全部", "v": ""}, {"n": "动作片", "v": "6"}, {"n": "喜剧片", "v": "7"},
                {"n": "爱情片", "v": "8"}, {"n": "科幻片", "v": "9"}, {"n": "恐怖片", "v": "10"},
                {"n": "剧情片", "v": "11"}, {"n": "战争片", "v": "12"}, {"n": "纪录片", "v": "13"},
                {"n": "动画片", "v": "14"}, {"n": "悬疑片", "v": "15"}, {"n": "冒险片", "v": "16"},
                {"n": "犯罪片", "v": "17"}, {"n": "惊悚片", "v": "18"}, {"n": "歌舞片", "v": "19"},
                {"n": "灾难片", "v": "20"}, {"n": "网络片", "v": "21"}
            ]},
            {"key": "area", "name": "地区", "value": [
                {"n": "全部", "v": ""}, {"n": "大陆", "v": "大陆"},
                {"n": "香港", "v": "香港"}, {"n": "台湾", "v": "台湾"},
                {"n": "美国", "v": "美国"}, {"n": "法国", "v": "法国"},
                {"n": "英国", "v": "英国"}, {"n": "日本", "v": "日本"},
                {"n": "韩国", "v": "韩国"}, {"n": "德国", "v": "德国"},
                {"n": "泰国", "v": "泰国"}, {"n": "印度", "v": "印度"},
                {"n": "意大利", "v": "意大利"}, {"n": "西班牙", "v": "西班牙"},
                {"n": "加拿大", "v": "加拿大"}, {"n": "其他", "v": "其他"}
            ]},
            {"key": "lang", "name": "语言", "value": [
                {"n": "全部", "v": ""}, {"n": "国语", "v": "国语"},
                {"n": "英语", "v": "英语"}, {"n": "粤语", "v": "粤语"},
                {"n": "闽南语", "v": "闽南语"}, {"n": "韩语", "v": "韩语"},
                {"n": "日语", "v": "日语"}, {"n": "西班牙语", "v": "西班牙语"},
                {"n": "德语", "v": "德语"}, {"n": "泰语", "v": "泰语"},
                {"n": "其它", "v": "其它"}
            ]},
            {"key": "year", "name": "年份", "value": [
                {"n": "全部", "v": ""}, {"n": "2025", "v": "2025"}, {"n": "2024", "v": "2024"},
                {"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"},
                {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"},
                {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"},
                {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, {"n": "2012", "v": "2012"},
                {"n": "2011", "v": "2011"}, {"n": "更早", "v": "更早"}
            ]},
            {"key": "letter", "name": "字母", "value": [
                {"n": "全部", "v": ""}, {"n": "A", "v": "A"}, {"n": "B", "v": "B"},
                {"n": "C", "v": "C"}, {"n": "D", "v": "D"}, {"n": "E", "v": "E"},
                {"n": "F", "v": "F"}, {"n": "G", "v": "G"}, {"n": "H", "v": "H"},
                {"n": "I", "v": "I"}, {"n": "J", "v": "J"}, {"n": "K", "v": "K"},
                {"n": "L", "v": "L"}, {"n": "M", "v": "M"}, {"n": "N", "v": "N"},
                {"n": "O", "v": "O"}, {"n": "P", "v": "P"}, {"n": "Q", "v": "Q"},
                {"n": "R", "v": "R"}, {"n": "S", "v": "S"}, {"n": "T", "v": "T"},
                {"n": "U", "v": "U"}, {"n": "V", "v": "V"}, {"n": "W", "v": "W"},
                {"n": "X", "v": "X"}, {"n": "Y", "v": "Y"}, {"n": "Z", "v": "Z"},
                {"n": "0-9", "v": "0-9"}
            ]},
            {"key": "sort", "name": "排序", "value": [
                {"n": "添加时间", "v": "time_add"}, {"n": "更新时间", "v": "time_update"},
                {"n": "人气排序", "v": "hits"}, {"n": "评分排序", "v": "score"}
            ]}],
            "2": [{"key": "class", "name": "类型", "value": [
                {"n": "全部", "v": ""}, {"n": "国产剧", "v": "13"}, {"n": "港台剧", "v": "14"},
                {"n": "日剧", "v": "15"}, {"n": "韩剧", "v": "33"}, {"n": "欧美剧", "v": "16"},
                {"n": "东南亚剧", "v": "44"}, {"n": "其它剧", "v": "18"}
            ]},
            {"key": "area", "name": "地区", "value": [
                {"n": "全部", "v": ""}, {"n": "大陆", "v": "大陆"},
                {"n": "香港", "v": "香港"}, {"n": "台湾", "v": "台湾"},
                {"n": "美国", "v": "美国"}, {"n": "英国", "v": "英国"},
                {"n": "日本", "v": "日本"}, {"n": "韩国", "v": "韩国"},
                {"n": "泰国", "v": "泰国"}, {"n": "新加坡", "v": "新加坡"},
                {"n": "其他", "v": "其他"}
            ]},
            {"key": "year", "name": "年份", "value": [
                {"n": "全部", "v": ""}, {"n": "2025", "v": "2025"}, {"n": "2024", "v": "2024"},
                {"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"},
                {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"},
                {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"},
                {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, {"n": "2012", "v": "2012"},
                {"n": "2011", "v": "2011"}, {"n": "更早", "v": "更早"}
            ]}],
            "3": [{"key": "class", "name": "类型", "value": [
                {"n": "全部", "v": ""}, {"n": "内地综艺", "v": "27"}, {"n": "港台综艺", "v": "28"},
                {"n": "日本综艺", "v": "29"}, {"n": "韩国综艺", "v": "36"}, {"n": "欧美综艺", "v": "30"}
            ]},
            {"key": "year", "name": "年份", "value": [
                {"n": "全部", "v": ""}, {"n": "2025", "v": "2025"}, {"n": "2024", "v": "2024"},
                {"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"},
                {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"},
                {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"},
                {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, {"n": "2012", "v": "2012"},
                {"n": "2011", "v": "2011"}, {"n": "更早", "v": "更早"}
            ]}],
            "4": [{"key": "class", "name": "类型", "value": [
                {"n": "全部", "v": ""}, {"n": "国产动漫", "v": "31"}, {"n": "日本动漫", "v": "32"},
                {"n": "欧美动漫", "v": "42"}, {"n": "其他动漫", "v": "43"}
            ]},
            {"key": "year", "name": "年份", "value": [
                {"n": "全部", "v": ""}, {"n": "2025", "v": "2025"}, {"n": "2024", "v": "2024"},
                {"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"},
                {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"},
                {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"},
                {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, {"n": "2012", "v": "2012"},
                {"n": "2011", "v": "2011"}, {"n": "更早", "v": "更早"}
            ]}]
        }

    def _extract_videos_from_html(self, html, limit=None):
        videos = []
        try:
            pattern = r'<a href="/voddetail/(\d+)/".*?title="([^"]+)".*?<div class="module-item-note">([^<]+)</div>.*?data-original="([^"]+)"'
            matches = re.findall(pattern, html, re.S | re.I)
            
            for vid, title, remark, pic in matches:
                if pic and pic.startswith('/'):
                    pic = self.host + pic
                videos.append({
                    'vod_id': vid.strip(),
                    'vod_name': title.strip(),
                    'vod_pic': pic.strip(),
                    'vod_remarks': remark.strip()
                })
                
            if not videos:
                pattern = r'<a href="/voddetail/(\d+)/".*?data-original="([^"]+)".*?title="([^"]+)".*?<div class="module-item-note">([^<]+)</div>'
                matches = re.findall(pattern, html, re.S | re.I)
                
                for vid, pic, title, remark in matches:
                    if pic and pic.startswith('/'):
                        pic = self.host + pic
                    videos.append({
                        'vod_id': vid.strip(),
                        'vod_name': title.strip(),
                        'vod_pic': pic.strip(),
                        'vod_remarks': remark.strip()
                    })
                    
            if limit and len(videos) > limit:
                videos = videos[:limit]
                    
        except Exception as e:
            self.log(f"列表提取出错: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
        return videos

    def _extract_videos_with_bs(self, html):
        videos = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            card_items = soup.select('.module-card-item')
            
            self.log(f"找到{len(card_items)}个卡片项")
            
            seen_ids = set()
            
            for item in card_items:
                link = item.select_one('a[href^="/voddetail/"]')
                if not link:
                    continue
                    
                href = link.get('href', '')
                vid_match = re.search(r'/voddetail/(\d+)/', href)
                if not vid_match:
                    continue
                    
                vid = vid_match.group(1)
                if vid in seen_ids:
                    continue
                    
                seen_ids.add(vid)
                
                title_elem = item.select_one('.module-card-item-title strong')
                title = title_elem.get_text(strip=True) if title_elem else ""
                
                img_elem = item.select_one('img')
                pic = img_elem.get('data-original') or img_elem.get('src') if img_elem else ""
                if pic and pic.startswith('/'):
                    pic = self.host + pic
                    
                note_elem = item.select_one('.module-item-note')
                remark = note_elem.get_text(strip=True) if note_elem else ""
                
                videos.append({
                    'vod_id': vid.strip(),
                    'vod_name': title.strip(),
                    'vod_pic': pic.strip(),
                    'vod_remarks': remark.strip()
                })
                
            if not videos:
                links = soup.select('a[href^="/voddetail/"]')
                seen_ids = set()
                
                for link in links:
                    href = link.get('href', '')
                    vid_match = re.search(r'/voddetail/(\d+)/', href)
                    if not vid_match:
                        continue
                        
                    vid = vid_match.group(1)
                    if vid in seen_ids:
                        continue
                        
                    seen_ids.add(vid)
                    
                    title = link.get('title', '') or link.get_text(strip=True)
                    
                    img_elem = link.select_one('img')
                    pic = img_elem.get('data-original') or img_elem.get('src') if img_elem else ""
                    if pic and pic.startswith('/'):
                        pic = self.host + pic
                        
                    note_elem = link.find_next(class_='module-item-note')
                    remark = note_elem.get_text(strip=True) if note_elem else ""
                    
                    videos.append({
                        'vod_id': vid.strip(),
                        'vod_name': title.strip(),
                        'vod_pic': pic.strip(),
                        'vod_remarks': remark.strip()
                    })
                
            self.log(f"最终提取到{len(videos)}条数据")
            
        except Exception as e:
            self.log(f"列表提取出错: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
        return videos

    def _extract_search_results_with_bs(self, html):
        videos = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            card_items = soup.select('.module-card-item')
            
            self.log(f"找到{len(card_items)}个卡片项")
            
            seen_ids = set()
            
            for item in card_items:
                link = item.select_one('a[href^="/voddetail/"]')
                if not link:
                    continue
                    
                href = link.get('href', '')
                vid_match = re.search(r'/voddetail/(\d+)/', href)
                if not vid_match:
                    continue
                    
                vid = vid_match.group(1)
                if vid in seen_ids:
                    continue
                    
                seen_ids.add(vid)
                
                title_elem = item.select_one('.module-card-item-title strong')
                title = title_elem.get_text(strip=True) if title_elem else ""
                
                img_elem = item.select_one('img')
                pic = img_elem.get('data-original') or img_elem.get('src') if img_elem else ""
                if pic and pic.startswith('/'):
                    pic = self.host + pic
                    
                note_elem = item.select_one('.module-item-note')
                remark = note_elem.get_text(strip=True) if note_elem else ""
                
                videos.append({
                    'vod_id': vid.strip(),
                    'vod_name': title.strip(),
                    'vod_pic': pic.strip(),
                    'vod_remarks': remark.strip()
                })
                
            if not videos:
                links = soup.select('a[href^="/voddetail/"]')
                seen_ids = set()
                
                for link in links:
                    href = link.get('href', '')
                    vid_match = re.search(r'/voddetail/(\d+)/', href)
                    if not vid_match:
                        continue
                        
                    vid = vid_match.group(1)
                    if vid in seen_ids:
                        continue
                        
                    seen_ids.add(vid)
                    
                    title = link.get('title', '') or link.get_text(strip=True)
                    
                    img_elem = link.select_one('img')
                    pic = img_elem.get('data-original') or img_elem.get('src') if img_elem else ""
                    if pic and pic.startswith('/'):
                        pic = self.host + pic
                        
                    note_elem = link.find_next(class_='module-item-note')
                    remark = note_elem.get_text(strip=True) if note_elem else ""
                    
                    videos.append({
                        'vod_id': vid.strip(),
                        'vod_name': title.strip(),
                        'vod_pic': pic.strip(),
                        'vod_remarks': remark.strip()
                    })
                
            self.log(f"最终提取到{len(videos)}条搜索结果")
            
        except Exception as e:
            self.log(f"搜索列表提取出错: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
        return videos

# 本地测试
if __name__ == "__main__":
    spider = Spider()
    spider.init()
    
    # 测试分类内容
    print("=== 测试分类内容 ===")
    # 测试示例URL: 科幻片(9) + 英国 + time_update排序 + 英语 + 2021年
    extend_params = {
        'class': '9',  # 科幻片
        'area': '英国',
        'sort': 'time_update',
        'lang': '英语',
        'year': '2021'
    }
    category_result = spider.categoryContent("1", "1", {}, extend_params)
    if category_result['list']:
        print(f"筛选结果数量: {len(category_result['list'])}")
        for i, video in enumerate(category_result['list'][:3]):
            print(f"筛选结果{i+1}: {video['vod_name']} - {video['vod_remarks']}")
    else:
        print("筛选功能获取失败")
    
    # 测试其他功能
    print("\n=== 测试首页内容 ===")
    home_result = spider.homeContent({})
    if home_result['list']:
        print(f"首页推荐数量: {len(home_result['list'])}")
        print(f"第一个推荐: {home_result['list'][0]['vod_name']}")
    
    print("\n=== 测试搜索功能 ===")
    search_result = spider.searchContent("仙逆", False, 1)
    if search_result['list']:
        print(f"搜索结果数量: {len(search_result['list'])}")
        for i, video in enumerate(search_result['list']):
            print(f"结果{i+1}: {video['vod_name']} - {video['vod_remarks']}")
    else:
        print("未搜索到结果")
