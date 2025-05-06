# -*- coding: utf-8 -*-
# @Author  : Doubebly
# @Time    : 2025/3/23 21:55
import base64
import sys
import time
import json
import requests
import re
from datetime import datetime
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):
    def getName(self):
        return "Litv"

    def init(self, extend):
        self.extend = extend
        try:
            self.extendDict = json.loads(extend)
        except:
            self.extendDict = {}

        proxy = self.extendDict.get('proxy', None)
        if proxy is None:
            self.is_proxy = False
        else:
            self.proxy = proxy
            self.is_proxy = True
        pass

    def getDependence(self):
        return []

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def liveContent(self, url):
        m3u_content = ['#EXTM3U']
        
        try:

            starttime = datetime.now().strftime("%Y-%m-%d")
            api_url = f"https://kzb29rda.com/prod-api/match/list/new?isfanye=1&type=0&cid=0&ishot=1&pn=1&ps=50&level=&name=&langtype=zh&starttime={starttime}&pid=4&zoneId=Asia%2FShanghai&zhuboType=1"
            

            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            data = response.json()


            for match in data.get("data", {}).get("topList", []):

                hteam = match.get("hteam_name", "Unknown Home")
                ateam = match.get("ateam_name", "Unknown Away")
                name = match.get("name", "Unnamed Match")
                matchtime = match.get("matchtime", "Unknown Time")
                status = match.get("status_up_name", "Unknown Status")
                

                for url_info in match.get("live_urls", []):
                    url = url_info.get("url", "")
                    if url:

                        extinf = f'#EXTINF:-1 tvg-name="{name}({hteam}-{ateam}){status}{matchtime}" group-title="{name}",({hteam}-{ateam}){status}{matchtime}'
                        m3u_content.extend([extinf, url])
            for match in data.get("data", {}).get("dataList", []):

                hteam = match.get("hteam_name", "Unknown Home")
                ateam = match.get("ateam_name", "Unknown Away")
                name = match.get("name", "Unnamed Match")
                matchtime = match.get("matchtime", "Unknown Time")
                status = match.get("status_up_name", "Unknown Status")
                

                for url_info in match.get("live_urls", []):
                    url = url_info.get("url", "")
                    if url:

                        extinf = f'#EXTINF:-1 tvg-name="{name}({hteam}-{ateam}){status}{matchtime}" group-title="{name}",({hteam}-{ateam}){status}{matchtime}'
                        m3u_content.extend([extinf, url])

        except requests.exceptions.RequestException as e:
            print(f"网络请求异常: {str(e)}")
            m3u_content.append('# 错误：无法获取直播数据')
        except json.JSONDecodeError:
            print("响应内容不是有效的JSON")
            m3u_content.append('# 错误：无效的API响应格式')
        except Exception as e:
            print(f"未知错误: {str(e)}")
            m3u_content.append('# 错误：数据处理异常')

        return '\n'.join(m3u_content)

    def homeContent(self, filter):
        return {}

    def homeVideoContent(self):
        return {}

    def categoryContent(self, cid, page, filter, ext):
        return {}

    def detailContent(self, did):
        return {}

    def searchContent(self, key, quick, page='1'):
        return {}

    def searchContentPage(self, keywords, quick, page):
        return {}

    def playerContent(self, flag, pid, vipFlags):
        return {}

    def localProxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        if params['type'] == "ts":
            return self.get_ts(params)
        return [302, "text/plain", None, {'Location': 'https://sf1-cdn-tos.huoshanstatic.com/obj/media-fe/xgplayer_doc_video/mp4/xgplayer-demo-720p.mp4'}]
    def proxyM3u8(self, params):
        pid = params['pid']
        info = pid.split(',')
        a = info[0]
        b = info[1]
        c = info[2]
        timestamp = int(time.time() / 4 - 355017625)
        t = timestamp * 4
        m3u8_text = f'#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:4\n#EXT-X-MEDIA-SEQUENCE:{timestamp}\n'
        for i in range(10):
            url = f'https://ntd-tgc.cdn.hinet.net/live/pool/{a}/litv-pc/{a}-avc1_6000000={b}-mp4a_134000_zho={c}-begin={t}0000000-dur=40000000-seq={timestamp}.ts'
            if self.is_proxy:
                url = f'http://127.0.0.1:9978/proxy?do=py&type=ts&url={self.b64encode(url)}'

            m3u8_text += f'#EXTINF:4,\n{url}\n'
            timestamp += 1
            t += 4
        return [200, "application/vnd.apple.mpegurl", m3u8_text]

    def get_ts(self, params):
        url = self.b64decode(params['url'])
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, stream=True, proxies=self.proxy)
        return [206, "application/octet-stream", response.content]

    def destroy(self):
        return '正在Destroy'

    def b64encode(self, data):
        return base64.b64encode(data.encode('utf-8')).decode('utf-8')

    def b64decode(self, data):
        return base64.b64decode(data.encode('utf-8')).decode('utf-8')


if __name__ == '__main__':
    pass