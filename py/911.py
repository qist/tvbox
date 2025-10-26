# coding=utf-8
# !/python
import sys
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from base.spider import Spider
import time

sys.path.append('..')

# 全局配置
xurl = "https://911blw.com"
backup_urls = ["https://hlj.fun", "https://911bl16.com"]
headerx = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
    "Referer": "https://911blw.com",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
}
IMAGE_FILTER = ["/usr/themes/ads-close.png", "close", "icon", "logo"]

class Spider(Spider):
    def getName(self):
        return "911爆料网"

    def init(self, extend):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def fetch_page(self, url, use_backup=False):
        global xurl
        original_url = url
        if use_backup:
            for backup in backup_urls:
                test_url = url.replace(xurl, backup)
                try:
                    time.sleep(1)
                    res = requests.get(test_url, headers=headerx, timeout=10)
                    res.raise_for_status()
                    res.encoding = "utf-8"
                    text = res.text
                    if len(text) > 1000:
                        print(f"[DEBUG] 使用备用 {backup}: {test_url}")
                        return text
                except:
                    continue
            print(f"[ERROR] 所有备用失败，回退原 URL")
        
        try:
            time.sleep(1)
            res = requests.get(original_url, headers=headerx, timeout=10)
            res.raise_for_status()
            res.encoding = "utf-8"
            text = res.text
            doc = BeautifulSoup(text, "html.parser")
            title = doc.title.string if doc.title else "无标题"
            print(f"[DEBUG] 页面 {original_url}: 长度={len(text)}, 标题={title}")
            if len(text) < 1000:
                print(f"[DEBUG] 内容过短，尝试备用域名")
                return self.fetch_page(original_url, use_backup=True)
            return text
        except Exception as e:
            print(f"[ERROR] 请求失败 {original_url}: {e}")
            return None

    def extract_content(self, html, url):
        videos = []
        if not html:
            return videos

        doc = BeautifulSoup(html, "html.parser")
        containers = doc.select("ul.row li, div.article-item, article, .post-item, div[class*='item']")
        print(f"[DEBUG] 找到 {len(containers)} 个容器")

        for i, vod in enumerate(containers[:20], 1):
            try:
                # 标题
                title_elem = vod.select_one("h2.headline, .headline, a[title]")
                name = title_elem.get("title") or title_elem.get_text(strip=True) if title_elem else ""
                if not name:
                    name_match = re.search(r'headline">(.+?)<', str(vod))
                    name = name_match.group(1).strip() if name_match else ""

                # 链接
                link_elem = vod.select_one("a")
                id = urljoin(xurl, link_elem["href"]) if link_elem else ""

                # 备注
                remarks_elem = vod.select_one("span.small, time, .date")
                remarks = remarks_elem.get_text(strip=True) if remarks_elem else ""
                if not remarks:
                    remarks_match = re.search(r'datePublished[^>]*>(.+?)<', str(vod))
                    remarks = remarks_match.group(1).strip() if remarks_match else ""

                # 图片 - 扩展属性
                img = vod.select_one("img")
                pic = None
                if img:
                    # 检查多种图片属性
                    for attr in ["data-lazy-src", "data-original", "data-src", "src"]:
                        pic = img.get(attr)
                        if pic:
                            break
                    # 检查背景图片
                    if not pic:
                        bg_div = vod.select_one("div[style*='background-image']")
                        if bg_div and "background-image" in bg_div.get("style", ""):
                            bg_match = re.search(r'url\([\'"]?(.+?)[\'"]?\)', bg_div["style"])
                            pic = bg_match.group(1) if bg_match else None
                    if pic:
                        pic = urljoin(xurl, pic)
                        alt = img.get("alt", "").lower() if img else ""
                        if any(f in pic.lower() or f in alt for f in IMAGE_FILTER):
                            pic = None
                        print(f"[DEBUG] 项 {i} 图片: {pic}, 属性={img.attrs if img else '无img'}")

                # 简介
                desc_match = re.search(r'og:description" content="(.+?)"', html)
                description = desc_match.group(1) if desc_match else ""

                if name and id:
                    video = {
                        "vod_id": id,
                        "vod_name": name[:100],
                        "vod_pic": pic,
                        "vod_remarks": remarks,
                        "vod_content": description
                    }
                    videos.append(video)
                    print(f"[DEBUG] 项 {i}: 标题={name[:50]}..., 链接={id}, 图片={pic}")
            except Exception as e:
                print(f"[DEBUG] 项 {i} 错误: {e}")
                continue

        print(f"[DEBUG] 提取 {len(videos)} 个项")
        return videos

    def homeVideoContent(self):
        url = f"{xurl}/category/jrgb/1/"
        html = self.fetch_page(url)
        videos = self.extract_content(html, url)
        return {'list': videos}

    def homeContent(self, filter):
        result = {'class': []}
        categories = [
            {"type_id": "/category/jrgb/", "type_name": "最新爆料"},
            {"type_id": "/category/rmgb/", "type_name": "精选大瓜"},
            {"type_id": "/category/blqw/", "type_name": "猎奇吃瓜"},
            {"type_id": "/category/rlph/", "type_name": "TOP5大瓜"},
            {"type_id": "/category/ssdbl/", "type_name": "社会热点"},
            {"type_id": "/category/hjsq/", "type_name": "海角社区"},
            {"type_id": "/category/mrds/", "type_name": "每日大赛"},
            {"type_id": "/category/xyss/", "type_name": "校园吃瓜"},
            {"type_id": "/category/mxhl/", "type_name": "明星吃瓜"},
            {"type_id": "/category/whbl/", "type_name": "网红爆料"},
            {"type_id": "/category/bgzq/", "type_name": "反差爆料"},
            {"type_id": "/category/fljq/", "type_name": "网黄福利"},
            {"type_id": "/category/crfys/", "type_name": "午夜剧场"},
            {"type_id": "/category/thjx/", "type_name": "探花经典"},
            {"type_id": "/category/dmhv/", "type_name": "禁漫天堂"},
            {"type_id": "/category/slec/", "type_name": "吃瓜精选"},
            {"type_id": "/category/zksr/", "type_name": "重口调教"},
            {"type_id": "/category/crlz/", "type_name": "精选连载"}
        ]
        result['class'] = categories
        return result

    def categoryContent(self, cid, pg, filter, ext):
        url = f"{xurl}{cid}{pg}/" if pg != "1" else f"{xurl}{cid}"
        html = self.fetch_page(url)
        videos = self.extract_content(html, url)
        return {
            'list': videos,
            'page': pg,
            'pagecount': 9999,
            'limit': 90,
            'total': 999999
        }

    def detailContent(self, ids):
        videos = []
        did = ids[0]
        html = self.fetch_page(did)
        if html:
            source_match = re.search(r'"url":"(.*?)"', html)
            purl = source_match.group(1).replace("\\", "") if source_match else ""
            videos.append({
                "vod_id": did,
                "vod_play_from": "爆料",
                "vod_play_url": purl,
                "vod_content": re.search(r'og:description" content="(.+?)"', html).group(1) if re.search(r'og:description" content="(.+?)"', html) else ""
            })
        return {'list': videos}

    def playerContent(self, flag, id, vipFlags):
        return {"parse": 0, "playUrl": "", "url": id, "header": headerx}

    def searchContent(self, key, quick):
        return self.searchContentPage(key, quick, "1")

    def searchContentPage(self, key, quick, page):
        url = f"{xurl}/search/{key}/{page}/"
        html = self.fetch_page(url)
        videos = self.extract_content(html, url)
        return {'list': videos, 'page': page, 'pagecount': 9999, 'limit': 90, 'total': 999999}

    def localProxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        elif params['type'] == "media":
            return self.proxyMedia(params)
        elif params['type'] == "ts":
            return self.proxyTs(params)
        return None

if __name__ == "__main__":
    spider = Spider()
    # 测试首页推荐
    result = spider.homeVideoContent()
    print(f"测试首页推荐: {len(result['list'])} 个项")
    for item in result['list'][:3]:
        print(item)
    # 测试分类
    for cate in ["jrgb", "rmgb", "blqw"]:
        result = spider.categoryContent(f"/category/{cate}/", "1", False, {})
        print(f"测试分类 {cate}: {len(result['list'])} 个项")
        for item in result['list'][:2]:
            print(item)