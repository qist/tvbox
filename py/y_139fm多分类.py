

import re
import sys
import json
import base64
import string
from urllib.parse import urlencode
from bs4 import BeautifulSoup

sys.path.append('..')
from base.spider import Spider as BaseSpider


class Spider(BaseSpider):
    def __init__(self):
        super().__init__()
        self.base = 'https://139fm.cyou'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # 分类映射
        self.category_map = {
            "1": "长篇有声",
            "2": "短篇有声",
            "3": "自慰催眠",
            "4": "ASMR专区"
        }
        
        # 主播映射
        self.anchor_map = {
            "小苮儿": "小苮儿",
            "步非烟团队": "步非烟团队",
            "小野猫": "小野猫",
            "戴逸": "戴逸",
            "姽狐": "姽狐",
            "小咪": "小咪",
            "浅浅": "浅浅",
            "季姜": "季姜",
            "丽莎": "丽莎",
            "雅朵": "雅朵",
            "曼曼": "曼曼",
            "小窈": "小窈",
            "ASMR专区": "ASMR专区"
        }

    def getName(self):
        return '139FM有声小说'

    def init(self, extend=""):
        self.extend = extend or ''
        return {'class': 'audio'}

    def isVideoFormat(self, url):
        return bool(re.search(r'\.(m3u8|mp3|m4a)(\?|$)', str(url)))

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    # ROT13字符转换
    def rot13_char(self, char):
        """对单个字符进行ROT13转换"""
        if 'a' <= char <= 'z':
            return chr(((ord(char) - ord('a') + 13) % 26) + ord('a'))
        elif 'A' <= char <= 'Z':
            return chr(((ord(char) - ord('A') + 13) % 26) + ord('A'))
        else:
            return char

    def ee2(self, text):
        """对字母字符进行ROT13转换"""
        result = []
        for char in text:
            if 'a' <= char <= 'z' or 'A' <= char <= 'Z':
                result.append(self.rot13_char(char))
            else:
                result.append(char)
        return ''.join(result)

    def dd0(self, encrypted_text, default_value=''):
        """主解密函数：ROT13 -> Base64 -> ROT13"""
        try:
            # 第一步: ROT13解码
            step1 = self.ee2(encrypted_text)
            # 第二步: Base64解码
            step2 = base64.b64decode(step1).decode('utf-8')
            # 第三步: 再次ROT13解码
            step3 = self.ee2(step2)
            return step3
        except Exception as e:
            self.log(f"解密失败: {e}")
            return default_value

    def extract_conf_from_html(self, html):
        """从JavaScript代码中提取_conf对象"""
        # 先检查是否存在 _conf
        if 'var _conf' not in html and 'var\xa0_conf' not in html:
            self.log("HTML中不包含 var _conf")
            return None
        
        # 查找 _conf 所在的位置附近的内容
        conf_pos = html.find('var _conf')
        if conf_pos != -1:
            snippet = html[conf_pos:conf_pos+500]
            self.log(f"找到_conf位置，附近内容: {snippet[:300]}")
        
        # 尝试多种模式匹配（支持单引号和双引号）
        patterns = [
            r"var\s+_conf\s*=\s*\{\s*a\s*:\s*\[((?:'[^']*'\s*,?\s*)*)\]",  # a: ['...'] 单引号
            r'var\s+_conf\s*=\s*\{\s*a\s*:\s*\[((?:"[^"]*"\s*,?\s*)*)\]',  # a: ["..."] 双引号
            r"_conf\s*=\s*\{\s*a\s*:\s*\[((?:'[^']*'\s*,?\s*)*)\]",  # 不带var 单引号
            r'_conf\s*=\s*\{\s*a\s*:\s*\[((?:"[^"]*"\s*,?\s*)*)\]',  # 不带var 双引号
            r"a\s*:\s*\[((?:'[^']*'\s*,?\s*)*)\]",  # 只匹配 a: ['...']
            r'a\s*:\s*\[((?:"[^"]*"\s*,?\s*)*)\]',  # 只匹配 a: ["..."]
        ]
        
        for i, pattern in enumerate(patterns):
            a_match = re.search(pattern, html, re.DOTALL)
            if a_match:
                try:
                    # 获取数组内容
                    array_content = a_match.group(1)
                    self.log(f"使用模式{i+1}成功匹配，数组内容: {array_content[:200]}")
                    
                    # 提取所有单引号或双引号字符串
                    # 先尝试单引号
                    strings = re.findall(r"'([^']*)'", array_content)
                    if not strings:
                        # 再尝试双引号
                        strings = re.findall(r'"([^"]*)"', array_content)
                    
                    self.log(f"成功提取 {len(strings)} 个加密字符串")
                    
                    if strings:
                        return {'a': strings, 'c': ''}
                        
                except Exception as e:
                    self.log(f"模式{i+1}解析失败: {e}")
                    continue
        
        self.log("所有模式都未找到a数组")
        return None

    def decrypt_all(self, conf_data):
        """解密所有配置数据"""
        results = []
        if conf_data and 'a' in conf_data and isinstance(conf_data['a'], list):
            for encrypted_str in conf_data['a']:
                if encrypted_str:  # 只处理非空字符串
                    result = self.dd0(encrypted_str, conf_data.get('c', ''))
                    results.append(result)
        return results

    def homeContent(self, filter):
        """首页内容"""
        try:
            url = f"{self.base}/podcasts"
            r = self.fetch(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            categories = []
            
            # 解析分类
            areas_div = soup.find('dl', id='areas')
            if areas_div:
                for dd in areas_div.find_all('dd'):
                    data_val = dd.get('data-val')
                    if data_val and data_val != '-1':
                        categories.append({
                            'type_id': data_val,
                            'type_name': dd.get_text().strip()
                        })
            
            # 解析主播分类
            tags_dl = soup.find('dl', id='tags')
            if tags_dl:
                for dd in tags_dl.find_all('dd'):
                    data_val = dd.get('data-val')
                    if data_val and data_val != '全部' and data_val in self.anchor_map:
                        categories.append({
                            'type_id': f'anchor_{data_val}',
                            'type_name': f'主播-{data_val}'
                        })
            
            # 获取首页音频列表
            audios = []
            items = soup.find_all('div', class_='mh-item')
            self.log(f"找到 {len(items)} 个音频项")
            
            for item in items:
                a_tag = item.find('a', href=True)
                if not a_tag:
                    continue
                    
                href = a_tag.get('href', '')
                
                cover_p = item.find('p', class_='mh-cover')
                cover_url = ''
                if cover_p and cover_p.get('style'):
                    match = re.search(r'url\((.*?)\)', cover_p.get('style'))
                    if match:
                        cover_url = match.group(1).strip('\'"')
                
                # 注意：标题在 h2 标签中，class="title"
                title_h2 = item.find('h2', class_='title')
                title = ''
                if title_h2:
                    title_a = title_h2.find('a')
                    if title_a:
                        title = title_a.get_text().strip()
                
                chapter_p = item.find('p', class_='chapter')
                chapter = chapter_p.get_text().strip() if chapter_p else ''
                
                if href and title:
                    vod_id = href.split('/')[-1]
                    audios.append({
                        'vod_id': vod_id,
                        'vod_name': title,
                        'vod_pic': cover_url,
                        'vod_remarks': chapter or '暂无简介'
                    })
            
            self.log(f"成功解析 {len(audios)} 个音频")
            
            return {
                'class': categories,
                'list': audios
            }
        except Exception as e:
            self.log(f"Home error: {e}")
            import traceback
            self.log(traceback.format_exc())
            return {
                'class': [],
                'list': []
            }

    def homeVideoContent(self):
        """首页推荐视频"""
        try:
            result = self.homeContent(False)
            return {'list': result.get('list', [])}
        except Exception as e:
            self.log(f'homeVideoContent error: {e}')
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        """分类内容"""
        try:
            url = f"{self.base}/podcasts"
            params = {}
            
            if tid and tid.startswith("anchor_"):
                # 主播分类
                anchor = tid.replace("anchor_", "")
                params['tag'] = anchor
            elif tid and tid in self.category_map:
                # 内容分类
                params['area'] = tid
            
            if pg and int(pg) > 1:
                params['page'] = pg
            
            if params:
                url = f"{url}?{urlencode(params)}"
            
            r = self.fetch(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            audios = []
            items = soup.find_all('div', class_='mh-item')
            self.log(f"分类页找到 {len(items)} 个音频项")
            
            for item in items:
                a_tag = item.find('a', href=True)
                if not a_tag:
                    continue
                    
                href = a_tag.get('href', '')
                
                cover_p = item.find('p', class_='mh-cover')
                cover_url = ''
                if cover_p and cover_p.get('style'):
                    match = re.search(r'url\((.*?)\)', cover_p.get('style'))
                    if match:
                        cover_url = match.group(1).strip('\'"')
                
                # 注意：标题在 h2 标签中，class="title"
                title_h2 = item.find('h2', class_='title')
                title = ''
                if title_h2:
                    title_a = title_h2.find('a')
                    if title_a:
                        title = title_a.get_text().strip()
                
                chapter_p = item.find('p', class_='chapter')
                chapter = chapter_p.get_text().strip() if chapter_p else ''
                
                if href and title:
                    vod_id = href.split('/')[-1]
                    audios.append({
                        'vod_id': vod_id,
                        'vod_name': title,
                        'vod_pic': cover_url,
                        'vod_remarks': chapter or '暂无简介'
                    })
            
            self.log(f"分类页成功解析 {len(audios)} 个音频")
            
            # 解析分页信息
            pagecount = 1
            pagination = soup.find('div', class_='pagination')
            if pagination:
                for a_tag in pagination.find_all('a', title=True):
                    href = a_tag.get('href', '')
                    match = re.search(r'page=(\d+)', href)
                    if match:
                        page_num = int(match.group(1))
                        pagecount = max(pagecount, page_num)
            
            return {
                'list': audios,
                'page': int(pg) if pg else 1,
                'pagecount': pagecount,
                'limit': 48,
                'total': len(audios) * pagecount
            }
        except Exception as e:
            self.log(f"Category error: {e}")
            import traceback
            self.log(traceback.format_exc())
            return {
                'list': [],
                'page': int(pg) if pg else 1,
                'pagecount': 1,
                'limit': 48,
                'total': 0
            }

    def detailContent(self, ids):
        """详情内容"""
        result = {'list': []}
        
        for id_ in ids:
            try:
                url = f"{self.base}/podcast/{id_}"
                r = self.fetch(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(r.text, 'html.parser')
                
                # 提取_conf对象并解密音频URL
                _conf = self.extract_conf_from_html(r.text)
                decrypted_urls = []
                
                if _conf:
                    self.log(f"找到_conf对象: {_conf}")
                    decrypted_urls = self.decrypt_all(_conf)
                    self.log(f"解密后的URL列表数量: {len(decrypted_urls)}")
                
                # 基本信息
                title_tag = soup.find('title')
                title = title_tag.get_text().replace('-139FM', '').strip() if title_tag else f'音频_{id_}'
                
                # 获取封面
                cover_url = ''
                cover_img = soup.find('img', {'data-amplitude-song-info': 'cover_art_url'})
                if cover_img and cover_img.get('src'):
                    cover_url = cover_img.get('src')
                
                if not cover_url:
                    cover_div = soup.find(class_='mh-cover')
                    if cover_div and cover_div.get('style'):
                        match = re.search(r'url\((.*?)\)', cover_div.get('style'))
                        if match:
                            cover_url = match.group(1).strip('\'"')
                
                # 解析播放列表
                episodes = []
                songs = soup.find_all('div', class_='song')
                for index, song in enumerate(songs):
                    title_div = song.find('div', class_='song-title')
                    episode_title = title_div.get_text().strip() if title_div else f'第{index+1}集'
                    
                    artist_div = song.find('div', class_='song-artist')
                    episode_artist = artist_div.get_text().strip() if artist_div else ''
                    
                    require_buy = song.get('data-require-buy') == '1'
                    chapter_id = song.get('data-chapter-id', '')
                    
                    # 获取对应的解密URL
                    audio_url = decrypted_urls[index] if index < len(decrypted_urls) else ''
                    
                    episodes.append({
                        'name': episode_title,
                        'artist': episode_artist,
                        'requireBuy': require_buy,
                        'chapterId': chapter_id,
                        'url': audio_url
                    })
                
                # 解析详情信息
                desc_match = re.search(r'"desc":\s*"([^"]*)"', r.text)
                area_match = re.search(r'"area":\s*"([^"]*)"', r.text)
                tag_match = re.search(r'"tag":\s*"([^"]*)"', r.text)
                clicks_match = re.search(r'"clicks":\s*"([^"]*)"', r.text)
                
                vod_content = '暂无简介'
                if desc_match:
                    vod_content = desc_match.group(1).replace('简介：', '')
                
                vod_remarks = ''
                if clicks_match:
                    vod_remarks = clicks_match.group(1).replace('热度：', '热度:')
                
                type_name = ''
                if area_match:
                    type_name = self.removeHtmlTags(area_match.group(1)).replace('类型：', '').strip()
                
                vod_actor = ''
                if tag_match:
                    vod_actor = self.removeHtmlTags(tag_match.group(1)).replace('主播：', '').strip()
                
                # 构建播放源
                play_from = '139FM'
                
                # 构建播放URL - 格式：剧集1$URL1#剧集2$URL2
                play_url_parts = []
                for index, ep in enumerate(episodes):
                    episode_name = ep['name']
                    if ep['requireBuy']:
                        episode_name += '[付费]'
                    
                    episode_url = ep['url']
                    if not episode_url:
                        # 如果没有解密URL，使用组合ID格式
                        episode_url = f"{id_}_{ep['chapterId']}_{index}"
                    
                    play_url_parts.append(f"{episode_name}${episode_url}")
                
                play_url = '#'.join(play_url_parts)
                
                result['list'].append({
                    'vod_id': id_,
                    'vod_name': title.replace('全集免费高清无修在线阅读', '').strip(),
                    'vod_pic': cover_url,
                    'type_name': type_name,
                    'vod_actor': vod_actor,
                    'vod_director': f'共{len(episodes)}集' if episodes else '',
                    'vod_content': vod_content,
                    'vod_remarks': vod_remarks,
                    'vod_play_from': play_from,
                    'vod_play_url': play_url
                })
                
            except Exception as e:
                self.log(f"Detail error for {id_}: {e}")
                import traceback
                self.log(traceback.format_exc())
                result['list'].append({
                    'vod_id': id_,
                    'vod_name': '获取失败',
                    'vod_pic': '',
                    'vod_content': f'获取详情失败: {str(e)}'
                })
        
        return result

    def searchContent(self, key, quick, pg="1"):
        """搜索内容"""
        try:
            params = {'keyword': key}
            if pg and int(pg) > 1:
                params['page'] = pg
            
            url = f"{self.base}/search?{urlencode(params)}"
            r = self.fetch(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            audios = []
            items = soup.find_all('div', class_='mh-item')
            self.log(f"搜索页找到 {len(items)} 个音频项")
            
            for item in items:
                a_tag = item.find('a', href=True)
                if not a_tag:
                    continue
                    
                href = a_tag.get('href', '')
                
                cover_p = item.find('p', class_='mh-cover')
                cover_url = ''
                if cover_p and cover_p.get('style'):
                    match = re.search(r'url\((.*?)\)', cover_p.get('style'))
                    if match:
                        cover_url = match.group(1).strip('\'"')
                
                # 注意：标题在 h2 标签中，class="title"
                title_h2 = item.find('h2', class_='title')
                title = ''
                if title_h2:
                    title_a = title_h2.find('a')
                    if title_a:
                        title = title_a.get_text().strip()
                
                chapter_p = item.find('p', class_='chapter')
                chapter = chapter_p.get_text().strip() if chapter_p else ''
                
                if href and title:
                    vod_id = href.split('/')[-1]
                    audios.append({
                        'vod_id': vod_id,
                        'vod_name': title,
                        'vod_pic': cover_url,
                        'vod_remarks': chapter or '暂无简介'
                    })
            
            self.log(f"搜索页成功解析 {len(audios)} 个音频")
            
            return {
                'list': audios,
                'page': int(pg) if pg else 1,
                'pagecount': 1,
                'total': len(audios)
            }
        except Exception as e:
            self.log(f"Search error: {e}")
            import traceback
            self.log(traceback.format_exc())
            return {
                'list': [],
                'page': int(pg) if pg else 1,
                'pagecount': 1,
                'total': 0
            }

    def playerContent(self, flag, id, vipFlags):
        """播放内容"""
        try:
            # 如果id已经是完整的URL（解密后的），直接使用
            if id.startswith('http'):
                return {
                    'parse': 0,
                    'playUrl': '',
                    'url': id,
                    'header': {
                        'Referer': self.base,
                        'User-Agent': self.headers['User-Agent'],
                        'Accept': '*/*',
                        'Range': 'bytes=0-'
                    }
                }
            
            # id格式: podcastId_chapterId_index
            parts = id.split('_')
            if len(parts) >= 3:
                podcast_id, chapter_id, index = parts[0], parts[1], parts[2]
                
                # 获取详情页面来解密音频URL
                url = f"{self.base}/podcast/{podcast_id}"
                r = self.fetch(url, headers=self.headers, timeout=10)
                _conf = self.extract_conf_from_html(r.text)
                
                if _conf:
                    decrypted_urls = self.decrypt_all(_conf)
                    audio_index = int(index)
                    
                    if audio_index < len(decrypted_urls) and decrypted_urls[audio_index]:
                        return {
                            'parse': 0,
                            'playUrl': '',
                            'url': decrypted_urls[audio_index],
                            'header': {
                                'Referer': f'{self.base}/podcast/{podcast_id}',
                                'User-Agent': self.headers['User-Agent'],
                                'Accept': '*/*',
                                'Range': 'bytes=0-'
                            }
                        }
            
            # 如果无法解析，返回空
            return {
                'parse': 0,
                'playUrl': '',
                'url': '',
                'header': {}
            }
            
        except Exception as e:
            self.log(f"Play error: {e}")
            import traceback
            self.log(traceback.format_exc())
            return {
                'parse': 0,
                'playUrl': '',
                'url': '',
                'header': {}
            }

    def localProxy(self, param):
        """本地代理"""
        return dict(param)


if __name__ == '__main__':
    sp = Spider()
    print('init:', sp.init(''))
    print('\n=== 测试首页内容 ===')
    home = sp.homeContent(False)
    print(f"分类数量: {len(home.get('class', []))}")
    print(f"首页音频数量: {len(home.get('list', []))}")
    if home.get('class'):
        print(f"第一个分类: {home['class'][0]}")
    if home.get('list'):
        print(f"第一个音频: {home['list'][0]}")

