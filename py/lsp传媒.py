import re
import sys
import urllib.parse
from pyquery import PyQuery as pq

sys.path.append('..')
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        return "lsp传媒（优）"
    
    def init(self, extend):
        pass
        
    def homeContent(self, filter):
        result = {}
        classes = []
        try:
            rsp = self.fetch("https://xn--oq2a.lspcm48.lat/index.php")
            if rsp and rsp.text:
                doc = pq(rsp.text)
                items = doc('.tabs li a')
                for item in items.items():
                    name = item.text()
                    href = item.attr('href')
                    if name and href:
                        match = re.search(r'/(\d+).html', href)
                        if match:
                            classes.append({
                                'type_name': name,
                                'type_id': match.group(1)
                            })
        except:
            pass
            
        result['class'] = classes
        return result

    def homeVideoContent(self):
        result = {}
        return result

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        videos = []
        try:
            url = "https://xn--oq2a.lspcm48.lat/index.php/vod/type/id/{}/page/{}.html".format(tid, pg)
            rsp = self.fetch(url)
            if rsp and rsp.text:
                doc = pq(rsp.text)
                items = doc('.grid .grid__item')
                for item in items.items():
                    a = item.find('a')
                    href = a.attr('href')
                    name = item.find('h3').text()
                    if not name or not href:
                        continue
                        
                    img = item.find('img').attr('data-original') or item.find('img').attr('src')
                    desc = item.find('.duration-video').text() or ''
                    
                    videos.append({
                        'vod_id': href,
                        'vod_name': name,
                        'vod_pic': img,
                        'vod_remarks': desc
                    })
        except:
            pass
            
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, array):
        result = {}
        if not array or not array[0]:
            return result
            
        try:
            aid = array[0]
            url = "https://xn--oq2a.lspcm48.lat" + aid if aid.startswith('/') else "https://xn--oq2a.lspcm48.lat/" + aid
            rsp = self.fetch(url)
            if not rsp or not rsp.text:
                return result
                
            html = rsp.text
            doc = pq(html)
            
            # 提取视频信息
            vod = {
                'vod_id': aid,
                'vod_name': doc('.section-header__title--video').text() or '',
                'vod_pic': doc('.xgplayer-poster').attr('style') or '',
                'vod_remarks': doc('.video-footer__description').text() or '',
                'vod_content': doc('.video-footer__description').text() or '',
                'vod_play_from': '',
                'vod_play_url': ''
            }
            
            # 清理封面图片URL
            if 'background-image:' in vod['vod_pic']:
                match = re.search(r'url\(["\']?(.*?)["\']?\)', vod['vod_pic'])
                if match:
                    vod['vod_pic'] = match.group(1)
            
            # 提取播放URL - 从JavaScript中提取m3u8地址
            play_url = ""
            
            # 方法1: 从HlsJsPlayer配置中提取
            player_match = re.search(r'let player = new HlsJsPlayer\s*\(\s*({.*?})\s*\)', html, re.DOTALL)
            if player_match:
                player_config = player_match.group(1)
                url_match = re.search(r'"url"\s*:\s*"([^"]+)"', player_config)
                if url_match:
                    play_url = url_match.group(1)
            
            # 方法2: 直接搜索m3u8链接
            if not play_url:
                m3u8_match = re.search(r'https?://[^\s"\']+\.m3u8[^\s"\']*', html)
                if m3u8_match:
                    play_url = m3u8_match.group(0)
            
            # 方法3: 从script标签中查找
            if not play_url:
                scripts = doc('script')
                for script in scripts.items():
                    script_text = script.text()
                    if 'm3u8' in script_text:
                        m3u8_match = re.search(r'https?://[^\s"\']+\.m3u8[^\s"\']*', script_text)
                        if m3u8_match:
                            play_url = m3u8_match.group(0)
                            break
            
            # 如果有播放链接，构造播放信息
            if play_url:
                vod['vod_play_from'] = '默认线路'
                vod['vod_play_url'] = '正片$' + play_url
            else:
                # 如果没有找到m3u8链接，尝试查找其他播放源
                # 查找iframe或embed标签
                iframe_src = doc('iframe').attr('src') or doc('embed').attr('src')
                if iframe_src:
                    vod['vod_play_from'] = '默认线路'
                    vod['vod_play_url'] = '正片$' + iframe_src
            
            result['list'] = [vod]
        except Exception as e:
            print(f"detailContent error: {e}")
            import traceback
            traceback.print_exc()
            
        return result

    def searchContent(self, key, quick, page='1'):
        result = {}
        videos = []
        try:
            if not key:
                return result
                
            url = "https://xn--oq2a.lspcm48.lat/index.php/vod/search/wd/{}/page/1.html".format(urllib.parse.quote(key))
            rsp = self.fetch(url)
            if rsp and rsp.text:
                doc = pq(rsp.text)
                items = doc('.grid .grid__item')
                for item in items.items():
                    a = item.find('a')
                    href = a.attr('href')
                    name = item.find('h3').text()
                    if not name or not href:
                        continue
                        
                    img = item.find('img').attr('data-original') or item.find('img').attr('src')
                    desc = item.find('.duration-video').text() or ''
                    
                    videos.append({
                        'vod_id': href,
                        'vod_name': name,
                        'vod_pic': img,
                        'vod_remarks': desc
                    })
        except:
            pass
            
        result['list'] = videos
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {}
        try:
            if not id:
                return result
                
            # 如果id已经是完整的m3u8链接，直接使用
            if id.startswith('http') and '.m3u8' in id:
                result["parse"] = 0  # 不解析，直接播放
                result["playUrl"] = ''
                result["url"] = id
                result["header"] = {
                    'User-Agent': 'MOBILE_UA',
                    'Referer': 'https://xn--oq2a.lspcm48.lat/'
                }
            else:
                # 否则认为id是详情页路径，需要重新获取
                url = "https://xn--oq2a.lspcm48.lat" + id if id.startswith('/') else "https://xn--oq2a.lspcm48.lat/" + id
                rsp = self.fetch(url)
                if rsp and rsp.text:
                    html = rsp.text
                    
                    # 从HTML中提取m3u8链接
                    play_url = ""
                    player_match = re.search(r'let player = new HlsJsPlayer\s*\(\s*({.*?})\s*\)', html, re.DOTALL)
                    if player_match:
                        player_config = player_match.group(1)
                        url_match = re.search(r'"url"\s*:\s*"([^"]+)"', player_config)
                        if url_match:
                            play_url = url_match.group(1)
                    
                    if not play_url:
                        m3u8_match = re.search(r'https?://[^\s"\']+\.m3u8[^\s"\']*', html)
                        if m3u8_match:
                            play_url = m3u8_match.group(0)
                    
                    if play_url:
                        result["parse"] = 0
                        result["playUrl"] = ''
                        result["url"] = play_url
                        result["header"] = {
                            'User-Agent': 'MOBILE_UA',
                            'Referer': url
                        }
                    else:
                        result["parse"] = 1
                        result["playUrl"] = ''
                        result["url"] = id
                        result["header"] = {
                            'User-Agent': 'MOBILE_UA'
                        }
        except Exception as e:
            print(f"playerContent error: {e}")
            
        return result

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def localProxy(self, param):
        return {}