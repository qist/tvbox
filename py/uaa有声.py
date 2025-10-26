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
import base64

class Spider(Spider):
    def getName(self):
        return "UAA[听]"
    
    def init(self, extend):
        pass
        
    def homeContent(self, filter):
        result = {}
        cateManual = {
            "有声小说": "有声小说",
            "淫词艳曲": "淫词艳曲",
            "激情骚麦": "激情骚麦",
            "寸止训练": "寸止训练",
            "ASMR": "ASMR"
        }
        classes = []
        for key in cateManual:
            classes.append({
                'type_name': key,
                'type_id': cateManual[key]
            })
        result['class'] = classes
        return result

    def homeVideoContent(self):
        result = {}
        return result

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        url = 'https://www.uaa001.com/api/audio/app/audio/search?category={0}&orderType=1&page={1}&searchType=1&size=42'.format(tid, pg)
        rsp = self.fetch(url)
        content = rsp.text
        videos = []
        data = json.loads(content)
        for item in data['model']['data']:
            videos.append({
                "vod_id": item['id'],
                "vod_name": item['title'],
                "vod_pic": item['coverUrl'],
                "vod_remarks": item['categories']
            })
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 42
        result['total'] = 999999
        return result

    def detailContent(self, array):
        tid = array[0]
        url = 'https://www.uaa001.com/api/audio/app/audio/intro?id={0}'.format(tid)
        rsp = self.fetch(url)
        content = rsp.text
        data = json.loads(content)
        model = data['model']
        
        # 构建播放列表
        play_list = []
        if 'chapters' in model and model['chapters']:
            for chapter in model['chapters']:
                chapter_id = chapter.get('id', '')
                chapter_title = chapter.get('title', '第{}集'.format(chapter.get('order', 1)))
                # 获取章节播放链接
                chapter_url = self.getChapterUrl(chapter_id)
                if chapter_url:
                    play_list.append('{}${}'.format(chapter_title, chapter_url))
        
        # 如果没有章节信息，使用默认播放链接
        if not play_list and 'latestReadChapterUrl' in model:
            play_list.append('第1集${}'.format(model['latestReadChapterUrl']))
        
        play_url = '#'.join(play_list) if play_list else ''
        
        # 构建详细信息
        vod_actor = model.get('author', '未知')  # CV信息
        vod_area = model.get('categories', '')   # 分类信息
        
        # 构建备注信息，包含收听量和收藏量
        remarks_parts = []
        if 'playCount' in model:
            play_count = self.format_count(model['playCount'])
            remarks_parts.append(f'收听:{play_count}')
        if 'collectCount' in model:
            collect_count = self.format_count(model['collectCount'])
            remarks_parts.append(f'收藏:{collect_count}')
        
        vod_remarks = ' | '.join(remarks_parts) if remarks_parts else model.get('updateState', '')
        
        vod = {
            "vod_id": tid,
            "vod_name": model['title'],
            "vod_pic": model['coverUrl'],
            "vod_content": model.get('intro', ''),
            "vod_actor": vod_actor,      # 显示CV信息
            "vod_area": vod_area,        # 显示分类信息
            "vod_remarks": vod_remarks,  # 显示收听量和收藏量
            "vod_play_from": "UAA",
            "vod_play_url": play_url
        }
        result = {
            'list': [vod]
        }
        return result

    def format_count(self, count):
        """格式化数字显示，如18200显示为18.2K"""
        try:
            count = int(count)
            if count >= 10000:
                return f"{count/10000:.1f}万"
            elif count >= 1000:
                return f"{count/1000:.1f}K"
            else:
                return str(count)
        except:
            return str(count)

    def getChapterUrl(self, chapter_id):
        """获取章节播放链接"""
        if not chapter_id:
            return ''
        
        try:
            url = 'https://www.uaa001.com/api/audio/app/audio/chapter?id={}'.format(chapter_id)
            rsp = self.fetch(url)
            data = json.loads(rsp.text)
            if data.get('model') and data['model'].get('chapterUrl'):
                return data['model']['chapterUrl']
        except:
            pass
        
        return ''

    def searchContent(self, key, quick, page='1'):
        result = {}
        url = 'https://www.uaa001.com/api/audio/app/audio/search?category=&keyword={0}&orderType=1&orderType=1&origin=&page=1&searchType=1&size=32&tag='.format(urllib.parse.quote(key))
        rsp = self.fetch(url)
        content = rsp.text
        videos = []
        data = json.loads(content)
        for item in data['model']['data']:
            videos.append({
                "vod_id": item['id'],
                "vod_name": item['title'],
                "vod_pic": item['coverUrl'],
                "vod_remarks": item['categories']
            })
        result['list'] = videos
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {}
        
        # 直接从播放链接播放，不需要额外解析
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = id
        result["header"] = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://www.uaa001.com/"
        }
        
        return result

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def localProxy(self, param):
        action = {}
        return [200, "video/MP2T", action, ""]