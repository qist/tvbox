# -*- coding: utf-8 -*-
# by @嗷呜
import json
import sys
from base64 import b64decode, b64encode
from pyquery import PyQuery as pq
from requests import Session
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):

    def init(self, extend=""):
        self.host = self.gethost()
        self.headers['referer'] = f'{self.host}/'
        self.session = Session()
        self.session.headers.update(self.headers)

    def getName(self):
        return "minijj"

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-full-version': '"133.0.6943.98"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"19.0.0"',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-full-version-list': '"Not(A:Brand";v="99.0.0.0", "Google Chrome";v="133.0.6943.98", "Chromium";v="133.0.6943.98"',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'priority': 'u=0, i'
    }

    def homeContent(self, filter):
        result = {}
        cateManual = {
            "電影": "1",
            "電視劇": "2",
            "經典動漫": "3",
            "綜藝娛樂": "4",
        }
        classes = []
        filters = {}
        
        for k in cateManual:
            classes.append({
                'type_name': k,
                'type_id': cateManual[k]
            })

        filters = {
            '1': [{'key': 'type', 'name': '類型', 'value': [{'n': '全部', 'v': '1'}, {'n': '動作片', 'v': '8'}, {'n': '喜劇片', 'v': '9'}, {'n': '愛情片', 'v': '10'}, {'n': '科幻片', 'v': '11'}, {'n': '恐怖片', 'v': '12'}, {'n': '戰爭片', 'v': '13'}, {'n': '劇情片', 'v': '14'}]},
                  {'key': 'area', 'name': '地區', 'value': [{'n': '全部', 'v': ''}, {'n': '大陸', 'v': 'dalu'}, {'n': '美國', 'v': 'meiguo'}, {'n': '香港', 'v': 'xianggang'}, {'n': '台灣', 'v': 'taiwan'}, {'n': '韓國', 'v': 'hanguo'}, {'n': '日本', 'v': 'riben'}, {'n': '泰國', 'v': 'taiguo'}, {'n': '新加坡', 'v': 'xinjiapo'}, {'n': '馬來西亞', 'v': 'malaixiya'}, {'n': '印度', 'v': 'yindu'}, {'n': '英國', 'v': 'yingguo'}, {'n': '法國', 'v': 'faguo'}, {'n': '加拿大', 'v': 'jianada'}]},
                  {'key': 'year', 'name': '年份', 'value': [{'n': '全部', 'v': ''}, {'n': '2025', 'v': '2025'}, {'n': '2024', 'v': '2024'}, {'n': '2023', 'v': '2023'}, {'n': '2022', 'v': '2022'}, {'n': '2021', 'v': '2021'}, {'n': '2020', 'v': '2020'}, {'n': '2019', 'v': '2019'}, {'n': '2018', 'v': '2018'}, {'n': '2017', 'v': '2017'}, {'n': '2016', 'v': '2016'}, {'n': '2015', 'v': '2015'}, {'n': '2014', 'v': '2014'}, {'n': '2013', 'v': '2013'}, {'n': '90後', 'v': '1990,1999'}, {'n': '80後', 'v': '1980,1989'}, {'n': '更早', 'v': '1900,1980'}]}],
            '2': [{'key': 'type', 'name': '類型', 'value': [{'n': '全部', 'v': '2'}, {'n': '大陸劇', 'v': '15'}, {'n': '香港劇', 'v': '16'}, {'n': '台灣劇', 'v': '918'}, {'n': '日劇', 'v': '18'}, {'n': '韓劇', 'v': '915'}, {'n': '美劇', 'v': '916'}, {'n': '英劇', 'v': '923'}, {'n': '歐美劇', 'v': '17'}, {'n': '泰劇', 'v': '922'}, {'n': '亞洲劇', 'v': '19'}]},
                  {'key': 'area', 'name': '地區', 'value': [{'n': '全部', 'v': ''}, {'n': '大陸', 'v': 'dalu'}, {'n': '美國', 'v': 'meiguo'}, {'n': '香港', 'v': 'xianggang'}, {'n': '台灣', 'v': 'taiwan'}, {'n': '韓國', 'v': 'hanguo'}, {'n': '日本', 'v': 'riben'}, {'n': '泰國', 'v': 'taiguo'}, {'n': '新加坡', 'v': 'xinjiapo'}, {'n': '馬來西亞', 'v': 'malaixiya'}, {'n': '印度', 'v': 'yindu'}, {'n': '英國', 'v': 'yingguo'}, {'n': '法國', 'v': 'faguo'}, {'n': '加拿大', 'v': 'jianada'}]},
                  {'key': 'year', 'name': '年份', 'value': [{'n': '全部', 'v': ''}, {'n': '2025', 'v': '2025'}, {'n': '2024', 'v': '2024'}, {'n': '2023', 'v': '2023'}, {'n': '2022', 'v': '2022'}, {'n': '2021', 'v': '2021'}, {'n': '2020', 'v': '2020'}, {'n': '2019', 'v': '2019'}, {'n': '2018', 'v': '2018'}, {'n': '2017', 'v': '2017'}, {'n': '2016', 'v': '2016'}, {'n': '2015', 'v': '2015'}, {'n': '2014', 'v': '2014'}, {'n': '2013', 'v': '2013'}, {'n': '90後', 'v': '1990,1999'}, {'n': '80後', 'v': '1980,1989'}, {'n': '更早', 'v': '1900,1980'}]}],
            '3': [{'key': 'type', 'name': '類型', 'value': [{'n': '全部', 'v': '3'}, {'n': '國漫', 'v': '906'}, {'n': '日漫', 'v': '904'}, {'n': '美漫', 'v': '905'}, {'n': '其他動漫', 'v': '903'}]},
                  {'key': 'area', 'name': '地區', 'value': [{'n': '全部', 'v': ''}, {'n': '大陸', 'v': 'dalu'}, {'n': '美國', 'v': 'meiguo'}, {'n': '日本', 'v': 'riben'}]},
                  {'key': 'year', 'name': '年份', 'value': [{'n': '全部', 'v': ''}, {'n': '2025', 'v': '2025'}, {'n': '2024', 'v': '2024'}, {'n': '2023', 'v': '2023'}, {'n': '2022', 'v': '2022'}, {'n': '2021', 'v': '2021'}, {'n': '2020', 'v': '2020'}, {'n': '2019', 'v': '2019'}, {'n': '2018', 'v': '2018'}, {'n': '2017', 'v': '2017'}, {'n': '2016', 'v': '2016'}, {'n': '2015', 'v': '2015'}, {'n': '2014', 'v': '2014'}, {'n': '2013', 'v': '2013'}, {'n': '90後', 'v': '1990,1999'}, {'n': '80後', 'v': '1980,1989'}, {'n': '更早', 'v': '1900,1980'}]}],
            '4': [{'key': 'type', 'name': '類型', 'value': [{'n': '全部', 'v': '4'}, {'n': '大陸綜藝', 'v': '911'}, {'n': '港台綜藝', 'v': '907'}, {'n': '韓綜', 'v': '908'}, {'n': '日綜', 'v': '912'}, {'n': '泰綜', 'v': '913'}, {'n': '歐美綜藝', 'v': '909'}]},
                  {'key': 'area', 'name': '地區', 'value': [{'n': '全部', 'v': ''}, {'n': '大陸', 'v': 'dalu'}, {'n': '美國', 'v': 'meiguo'}, {'n': '香港', 'v': 'xianggang'}, {'n': '台灣', 'v': 'taiwan'}, {'n': '韓國', 'v': 'hanguo'}, {'n': '日本', 'v': 'riben'}, {'n': '泰國', 'v': 'taiguo'}]},
                  {'key': 'year', 'name': '年份', 'value': [{'n': '全部', 'v': ''}, {'n': '2025', 'v': '2025'}, {'n': '2024', 'v': '2024'}, {'n': '2023', 'v': '2023'}, {'n': '2022', 'v': '2022'}, {'n': '2021', 'v': '2021'}, {'n': '2020', 'v': '2020'}, {'n': '2019', 'v': '2019'}, {'n': '2018', 'v': '2018'}, {'n': '2017', 'v': '2017'}, {'n': '2016', 'v': '2016'}, {'n': '2015', 'v': '2015'}, {'n': '2014', 'v': '2014'}, {'n': '2013', 'v': '2013'}, {'n': '90後', 'v': '1990,1999'}, {'n': '80後', 'v': '1980,1989'}, {'n': '更早', 'v': '1900,1980'}]}]
        }

        result['class'] = classes
        result['filters'] = filters
        return result

    def homeVideoContent(self):
        data = self.getpq()
        return {'list': self.getlist(data(".update_area_lists .i_list"))}

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        _type = extend.get('type', tid)
        _area = extend.get('area', '')
        _year = extend.get('year', '')

        # 構建篩選 URL，根據網站實際格式
        # 基礎格式：/lm/{type}/sx---{year}-----{page}.html
        # 如果有地區：/lm/{type}/sx------{area}--{page}.html
        # 如果年份和地區同時存在：/lm/{type}/sx---{year}---{area}--{page}.html
        if _year and _area:
            url = f'{self.host}/lm/{_type}/sx---{_year}---{_area}--{pg}.html'
        elif _year:
            url = f'{self.host}/lm/{_type}/sx---{_year}-----{pg}.html'
        elif _area:
            url = f'{self.host}/lm/{_type}/sx------{_area}--{pg}.html'
        else:
            url = f'{self.host}/lm/{_type}/sx--------{pg}.html'

        print(f"篩選 URL: {url}")  # 調試用，確認 URL 是否正確

        data = self.getpq(url)
        vdata = self.getlist(data(".update_area_lists .i_list"))
        pagecount = 9999
        try:
            pagination = data('.pagination .page-numbers')
            last_page = pagination[-2].text if len(pagination) > 1 else '1'
            pagecount = int(last_page) if last_page.isdigit() else 9999
        except:
            pass
        result['list'] = vdata
        result['page'] = pg
        result['pagecount'] = pagecount
        result['limit'] = 24
        result['total'] = pagecount * 24 if pagecount != 9999 else 999999
        return result

    def detailContent(self, ids):
        data = self.getpq(ids[0])
        full_title = data('title').text().split(' - ')[0]
        vn = full_title.split('線上觀看')[0].split('手機播放')[0].rstrip(',')

        vod = {
            'vod_id': ids[0],
            'vod_name': vn,
            'vod_pic': data('.vod-pic').attr('data-original') or '',
            'vod_remarks': data('.meta-post').eq(0).text().replace('', '').replace('', '').strip() or '',
            'vod_play_from': '',
            'vod_play_url': ''
        }

        play_from_list = []
        play_url_list = []
        
        tabs = data('#sea-tab li a')
        for tab in tabs.items():
            play_from = tab.text().strip().replace('\n', '').split('</span>')[-1]
            play_from_list.append(play_from)
        
        tab_contents = data('#sea-tab-content .tab-pane')
        for i, content in enumerate(tab_contents.items()):
            episodes = []
            play_links = content('.play-list a')
            for link in play_links.items():
                ep_name = link.text() or f"第 {len(episodes) + 1} 集"
                ep_url = f"{self.host}{link.attr('href')}"
                episodes.append(f"{ep_name}${ep_url}")
            episodes.reverse()
            play_url_list.append('#'.join(episodes))

        vod['vod_play_from'] = '$$$'.join(play_from_list)
        vod['vod_play_url'] = '$$$'.join(play_url_list)

        return {'list': [vod]}

    def searchContent(self, key, quick, pg="1"):
        data = self.getpq(f'/ss.html?wd={key}&page={pg}')
        return {'list': self.getlist(data(".update_area_lists .i_list")), 'page': pg}

    def playerContent(self, flag, id, vipFlags):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5410.0 Safari/537.36',
            'Referer': f'{self.host}/',
            'Origin': self.host,
        }
        
        data = self.getpq(id)
        
        iframe_url = data('iframe').attr('src')
        if iframe_url:
            if not iframe_url.startswith('http'):
                iframe_url = f"{self.host}{iframe_url}"
            if iframe_url.endswith('.m3u8') or iframe_url.endswith('.mp4'):
                return {'parse': 0, 'url': iframe_url, 'header': headers}
            return {'parse': 1, 'url': iframe_url, 'header': headers}
        
        video_url = data('video source').attr('src')
        if video_url:
            if not video_url.startswith('http'):
                video_url = f"{self.host}{video_url}"
            return {'parse': 0, 'url': video_url, 'header': headers}
        
        scripts = data('script')
        for script in scripts.items():
            script_text = script.text()
            if 'var player_data' in script_text or '.m3u8' in script_text or '.mp4' in script_text:
                import re
                urls = re.findall(r'(https?://[^\s\'"]+\.(m3u8|mp4))', script_text)
                if urls:
                    return {'parse': 0, 'url': urls[0][0], 'header': headers}
        
        return {'parse': 1, 'url': id, 'header': headers}

    def localProxy(self, param):
        pass

    def gethost(self):
        try:
            response = self.fetch('https://www.minijj.com', headers=self.headers, allow_redirects=False)
            return response.headers.get('Location', 'https://www.minijj.com')
        except Exception as e:
            print(f"獲取主頁失敗: {str(e)}")
            return "https://www.minijj.com"

    def e64(self, text):
        try:
            text_bytes = text.encode('utf-8')
            encoded_bytes = b64encode(text_bytes)
            return encoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Base64編碼錯誤: {str(e)}")
            return ""

    def d64(self, encoded_text):
        try:
            encoded_bytes = encoded_text.encode('utf-8')
            decoded_bytes = b64decode(encoded_bytes)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Base64解碼錯誤: {str(e)}")
            return ""

    def getlist(self, data):
        vlist = []
        for i in data.items():
            vlist.append({
                'vod_id': i('a').attr('href'),
                'vod_name': i('.meta-title').text(),
                'vod_pic': i('img').attr('data-original'),
                'vod_remarks': i('.meta-post').text().replace('', '').replace('', '').strip(),
            })
        return vlist

    def getpq(self, path=''):
        h = '' if path.startswith('http') else self.host
        response = self.session.get(f'{h}{path}')
        response.encoding = 'utf-8'
        text = response.text
        try:
            return pq(text)
        except Exception as e:
            print(f"解析 HTML 失敗: {str(e)}")
            return pq(text.encode('utf-8'))