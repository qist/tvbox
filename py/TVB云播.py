# -*- coding: utf-8 -*-
# by @Qist
"""
TVB云播
"""
import re
import json
import requests
from pyquery import PyQuery as pq
from bs4 import BeautifulSoup
from base.spider import Spider  # 继承基础Spider类


class Spider(Spider):  # 直接继承Spider基类
    def getName(self):
        return 'TVB云播'

    def init(self, extend=""):
        pass

    def __init__(self):
        self.name = 'TVB云播'
        self.host = 'http://www.tvyb03.com'
        self.timeout = 25
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        
        # 分类映射
        self.class_names = '电影&电视剧&综艺&动漫&日韩剧&国产剧&欧美剧&港台剧'.split('&')
        self.class_urls = '1&2&3&4&16&13&15&14'.split('&')
        
        # 过滤条件映射
        self.filter_map = {
            "1": [
                {"key": "cateId", "name": "类型", "value": [{"n": "全部", "v": "1"}, {"n": "动作片", "v": "6"}, {"n": "喜剧片", "v": "7"}, {"n": "爱情片", "v": "8"}, {"n": "科幻片", "v": "9"}, {"n": "恐怖片", "v": "10"}, {"n": "剧情片", "v": "11"}, {"n": "战争片", "v": "12"}]},
                {"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "喜剧", "v": "/class/喜剧"}, {"n": "爱情", "v": "/class/爱情"}, {"n": "恐怖", "v": "/class/恐怖"}, {"n": "动作", "v": "/class/动作"}, {"n": "科幻", "v": "/class/科幻"}, {"n": "剧情", "v": "/class/剧情"}, {"n": "战争", "v": "/class/战争"}, {"n": "警匪", "v": "/class/警匪"}, {"n": "犯罪", "v": "/class/犯罪"}, {"n": "动画", "v": "/class/动画"}, {"n": "奇幻", "v": "/class/奇幻"}, {"n": "武侠", "v": "/class/武侠"}, {"n": "冒险", "v": "/class/冒险"}, {"n": "枪战", "v": "/class/枪战"}, {"n": "悬疑", "v": "/class/悬疑"}, {"n": "惊悚", "v": "/class/惊悚"}, {"n": "经典", "v": "/class/经典"}, {"n": "青春", "v": "/class/青春"}, {"n": "文艺", "v": "/class/文艺"}, {"n": "微电影", "v": "/class/微电影"}, {"n": "古装", "v": "/class/古装"}, {"n": "历史", "v": "/class/历史"}, {"n": "运动", "v": "/class/运动"}, {"n": "农村", "v": "/class/农村"}, {"n": "儿童", "v": "/class/儿童"}, {"n": "网络电影", "v": "/class/网络电影"}]},
                {"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n": "大陆", "v": "/area/大陆"}, {"n": "香港", "v": "/area/香港"}, {"n": "台湾", "v": "/area/台湾"}, {"n": "美国", "v": "/area/美国"}, {"n": "法国", "v": "/area/法国"}, {"n": "英国", "v": "/area/英国"}, {"n": "日本", "v": "/area/日本"}, {"n": "韩国", "v": "/area/韩国"}, {"n": "德国", "v": "/area/Germany"}, {"n": "泰国", "v": "/area/Thailand"}, {"n": "India", "v": "/area/India"}, {"n": "Italy", "v": "/area/Italy"}, {"n": "Spain", "v": "/area/Spain"}, {"n": "Canada", "v": "/area/Canada"}, {"n": "Other", "v": "/area/Other"}]},
                {"key": "lang", "name": "语言", "value": [{"n": "全部", "v": ""}, {"n": "国语", "v": "/lang/国语"}, {"n": "英语", "v": "/lang/英语"}, {"n": "粤语", "v": "/lang/粤语"}, {"n": "韩语", "v": "/lang/韩语"}, {"n": "日语", "v": "/lang/日语"}, {"n": "法语", "v": "/lang/法语"}, {"n": "德语", "v": "/lang/德语"}, {"n": "其它", "v": "/lang/其它"}]},
                {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2026", "v": "/year/2026"}, {"n": "2025", "v": "/year/2025"}, {"n": "2024", "v": "/year/2024"}, {"n": "2023", "v": "/year/2023"}, {"n": "2022", "v": "/year/2022"}, {"n": "2021", "v": "/year/2021"}, {"n": "2020", "v": "/year/2020"}, {"n": "2019", "v": "/year/2019"}, {"n": "2018", "v": "/year/2018"}, {"n": "2017", "v": "/year/2017"}, {"n": "2016", "v": "/year/2016"}, {"n": "2015", "v": "/year/2015"}, {"n": "2014", "v": "/year/2014"}, {"n": "2013", "v": "/year/2013"}, {"n": "2012", "v": "/year/2012"}, {"n": "2011", "v": "/year/2011"}, {"n": "2010", "v": "/year/2010"}, {"n": "2009", "v": "/year/2009"}, {"n": "2008", "v": "/year/2008"}, {"n": "2007", "v": "/year/2007"}, {"n": "2006", "v": "/year/2006"}, {"n": "2005", "v": "/year/2005"}, {"n": "2004", "v": "/year/2004"}]},
                {"key": "by", "name": "排序", "value": [{"n": "全部", "v": ""}, {"n": "时间", "v": "/by/time"}, {"n": "人气", "v": "/by/hits"}, {"n": "评分", "v": "/by/score"}]}
            ],
            "2": [
                {"key": "cateId", "name": "类型", "value": [{"n": "全部", "v": "2"}, {"n": "国产剧", "v": "13"}, {"n": "港台剧", "v": "14"}, {"n": "日韩剧", "v": "15"}, {"n": "欧美剧", "v": "16"}]},
                {"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "古装", "v": "/class/古装"}, {"n": "青春", "v": "/class/青春"}, {"n": "偶像", "v": "/class/偶像"}, {"n": "喜剧", "v": "/class/喜剧"}, {"n": "家庭", "v": "/class/家庭"}, {"n": "犯罪", "v": "/class/犯罪"}, {"n": "动作", "v": "/class/动作"}, {"n": "奇幻", "v": "/class/奇幻"}, {"n": "剧情", "v": "/class/剧情"}, {"n": "历史", "v": "/class/历史"}, {"n": "经典", "v": "/class/经典"}, {"n": "乡村", "v": "/class/乡村"}, {"n": "情景", "v": "/class/情景"}, {"n": "商战", "v": "/class/商战"}, {"n": "网剧", "v": "/class/网剧"}, {"n": "其他", "v": "/class/其他"}]},
                {"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n": "内地", "v": "/area/内地"}, {"n": "韩国", "v": "/area/韩国"}, {"n": "香港", "v": "/area/香港"}, {"n": "台湾", "v": "/area/台湾"}, {"n": "日本", "v": "/area/日本"}, {"n": "美国", "v": "/area/美国"}, {"n": "泰国", "v": "/area/泰国"}, {"n": "英国", "v": "/area/英国"}, {"n": "Singapore", "v": "/area/Singapore"}, {"n": "Other", "v": "/area/Other"}]},
                {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2026", "v": "/year/2026"}, {"n": "2025", "v": "/year/2025"}, {"n": "2024", "v": "/year/2024"}, {"n": "2023", "v": "/year/2023"}, {"n": "2022", "v": "/year/2022"}, {"n": "2021", "v": "/year/2021"}, {"n": "2020", "v": "/year/2020"}, {"n": "2019", "v": "/year/2019"}, {"n": "2018", "v": "/year/2018"}, {"n": "2017", "v": "/year/2017"}, {"n": "2016", "v": "/year/2016"}, {"n": "2015", "v": "/year/2015"}, {"n": "2014", "v": "/year/2014"}, {"n": "2013", "v": "/year/2013"}, {"n": "2012", "v": "/year/2012"}, {"n": "2011", "v": "/year/2011"}, {"n": "2010", "v": "/year/2010"}, {"n": "2009", "v": "/year/2009"}, {"n": "2008", "v": "/year/2008"}, {"n": "2007", "v": "/year/2007"}, {"n": "2006", "v": "/year/2006"}, {"n": "2005", "v": "/year/2005"}, {"n": "2004", "v": "/year/2004"}]},
                {"key": "lang", "name": "语言", "value": [{"n": "全部", "v": ""}, {"n": "国语", "v": "/lang/国语"}, {"n": "英语", "v": "/lang/英语"}, {"n": "粤语", "v": "/lang/粤语"}, {"n": "韩语", "v": "/lang/韩语"}, {"n": "日语", "v": "/lang/日语"}, {"n": "其它", "v": "/lang/其它"}]},
                {"key": "by", "name": "排序", "value": [{"n": "全部", "v": ""}, {"n": "时间", "v": "/by/time"}, {"n": "人气", "v": "/by/hits"}, {"n": "评分", "v": "/by/score"}]}
            ],
            "3": [
                {"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "选秀", "v": "/class/选秀"}, {"n": "情感", "v": "/class/情感"}, {"n": "访谈", "v": "/class/访谈"}, {"n": "播报", "v": "/class/播报"}, {"n": "旅游", "v": "/class/旅游"}, {"n": "音乐", "v": "/class/音乐"}, {"n": "美食", "v": "/class/美食"}, {"n": "纪实", "v": "/class/纪实"}, {"n": "曲艺", "v": "/class/曲艺"}, {"n": "生活", "v": "/class/生活"}, {"n": "游戏互动", "v": "/class/游戏互动"}, {"n": "财经", "v": "/class/财经"}, {"n": "求职", "v": "/class/求职"}]},
                {"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n": "内地", "v": "/area/内地"}, {"n": "港台", "v": "/area/港台"}, {"n": "日韩", "v": "/area/日韩"}, {"n": "欧美", "v": "/area/欧美"}]},
                {"key": "lang", "name": "语言", "value": [{"n": "全部", "v": ""}, {"n": "国语", "v": "/lang/国语"}, {"n": "英语", "v": "/lang/英语"}, {"n": "粤语", "v": "/lang/粤语"}, {"n": "韩语", "v": "/lang/韩语"}, {"n": "日语", "v": "/lang/日语"}, {"n": "其它", "v": "/lang/其它"}]},
                {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2026", "v": "/year/2026"}, {"n": "2025", "v": "/year/2025"}, {"n": "2024", "v": "/year/2024"}, {"n": "2023", "v": "/year/2023"}, {"n": "2022", "v": "/year/2022"}, {"n": "2021", "v": "/year/2021"}, {"n": "2020", "v": "/year/2020"}, {"n": "2019", "v": "/year/2019"}, {"n": "2018", "v": "/year/2018"}, {"n": "2017", "v": "/year/2017"}, {"n": "2016", "v": "/year/2016"}, {"n": "2015", "v": "/year/2015"}, {"n": "2014", "v": "/year/2014"}, {"n": "2013", "v": "/year/2013"}, {"n": "2012", "v": "/year/2012"}, {"n": "2011", "v": "/year/2011"}, {"n": "2010", "v": "/year/2010"}, {"n": "2009", "v": "/year/2009"}, {"n": "2008", "v": "/year/2008"}, {"n": "2007", "v": "/year/2007"}, {"n": "2006", "v": "/year/2006"}, {"n": "2005", "v": "/year/2005"}, {"n": "2004", "v": "/year/2004"}]},
                {"key": "by", "name": "排序", "value": [{"n": "全部", "v": ""}, {"n": "时间", "v": "/by/time"}, {"n": "人气", "v": "/by/hits"}, {"n": "评分", "v": "/by/score"}]}
            ],
            "4": [
                {"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "情感", "v": "/class/情感"}, {"n": "科幻", "v": "/class/科幻"}, {"n": "热血", "v": "/class/热血"}, {"n": "推理", "v": "/class/推理"}, {"n": "搞笑", "v": "/class/搞笑"}, {"n": "冒险", "v": "/class/冒险"}, {"n": "萝莉", "v": "/class/萝莉"}, {"n": "校园", "v": "/class/校园"}, {"n": "动作", "v": "/class/动作"}, {"n": "机战", "v": "/class/机战"}, {"n": "运动", "v": "/class/运动"}, {"n": "战争", "v": "/class/战争"}, {"n": "少年", "v": "/class/少年"}, {"n": "少女", "v": "/class/少女"}, {"n": "社会", "v": "/class/社会"}, {"n": "原创", "v": "/class/原创"}, {"n": "亲子", "v": "/class/亲子"}, {"n": "益智", "v": "/class/益智"}, {"n": "励志", "v": "/class/励志"}, {"n": "其它", "v": "/class/其他"}]},
                {"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n": "国产", "v": "/area/国产"}, {"n": "日本", "v": "/area/日本"}, {"n": "欧美", "v": "/area/欧美"}, {"n": "Other", "v": "/area/Other"}]},
                {"key": "lang", "name": "语言", "value": [{"n": "全部", "v": ""}, {"n": "国语", "v": "/lang/国语"}, {"n": "英语", "v": "/lang/英语"}, {"n": "粤语", "v": "/lang/粤语"}, {"n": "韩语", "v": "/lang/韩语"}, {"n": "日语", "v": "/lang/日语"}, {"n": "其它", "v": "/lang/其它"}]},
                {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2026", "v": "/year/2026"}, {"n": "2025", "v": "/year/2025"}, {"n": "2024", "v": "/year/2024"}, {"n": "2023", "v": "/year/2023"}, {"n": "2022", "v": "/year/2022"}, {"n": "2021", "v": "/year/2021"}, {"n": "2020", "v": "/year/2020"}, {"n": "2019", "v": "/year/2019"}, {"n": "2018", "v": "/year/2018"}, {"n": "2017", "v": "/year/2017"}, {"n": "2016", "v": "/year/2016"}, {"n": "2015", "v": "/year/2015"}, {"n": "2014", "v": "/year/2014"}, {"n": "2013", "v": "/year/2013"}, {"n": "2012", "v": "/year/2012"}, {"n": "2011", "v": "/year/2011"}, {"n": "2010", "v": "/year/2010"}, {"n": "2009", "v": "/year/2009"}, {"n": "2008", "v": "/year/2008"}, {"n": "2007", "v": "/year/2007"}, {"n": "2006", "v": "/year/2006"}, {"n": "2005", "v": "/year/2005"}, {"n": "2004", "v": "/year/2004"}]},
                {"key": "by", "name": "排序", "value": [{"n": "全部", "v": ""}, {"n": "时间", "v": "/by/time"}, {"n": "人气", "v": "/by/hits"}, {"n": "评分", "v": "/by/score"}]}
            ]
        }

    def homeContent(self, filter):
        """
        获取首页内容
        """
        try:
            result = {'class': [], 'list': []}
            
            # 添加分类
            for name, cid in zip(self.class_names, self.class_urls):
                result['class'].append({
                    'type_name': name,
                    'type_id': cid
                })

            # 如果启用了筛选功能，添加筛选条件
            if filter:
                result['filters'] = {}
                for cid in self.class_urls:
                    result['filters'][cid] = self.get_filter_data(cid)

            # 获取推荐内容
            url = f"{self.host}/index.php/vod/show/id/1.html"
            response = self.fetch(url)
            if response:
                data = pq(response)
                
                # 使用推荐选择器: ul.myui-vodlist;li;*;*;*;*
                ul_items = data('ul.myui-vodlist li')
                for item in ul_items.items():
                    title = item('a:first').attr('title') or ''
                    pic = item('.lazyload').attr('data-original') or ''
                    if pic and not pic.startswith('http'):
                        pic = self.host + pic
                    href = item('a:first').attr('href') or ''
                    if href and not href.startswith('http'):
                        href = self.host + href
                    remarks = item('.tag').text() or ''

                    if title and href:
                        result['list'].append({
                            'vod_id': self.get_id_from_href(href),
                            'vod_name': title,
                            'vod_pic': pic,
                            'vod_remarks': remarks
                        })

            return result
        except Exception as e:
            print(f"Error in homeContent: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'class': [], 'list': []}

    def get_filter_data(self, tid):
        """
        获取筛选数据，与JS规则一致，动态从页面获取筛选条件
        """
        try:
            # 根据JS中的filter_map直接返回对应的筛选条件
            # 因为JS规则中是预定义的筛选条件，所以我们根据分类ID返回对应的预定义条件
            if tid in self.filter_map:
                return self.filter_map[tid]
            elif tid == '13':  # 国产剧
                return self.filter_map["2"]
            elif tid == '14':  # 港台剧
                return self.filter_map["2"]
            elif tid == '15':  # 日韩剧
                return self.filter_map["2"]
            elif tid == '16':  # 欧美剧
                return self.filter_map["2"]
            else:
                # 默认返回电影的筛选条件
                return self.filter_map["1"]
        except Exception as e:
            print(f"Error in get_filter_data: {str(e)}")
            return []

    def categoryContent(self, tid, pg, filter, extend):
        """
        获取分类内容
        对应JS中的url: 'vod/show/id/fyfilter.html'
        """
        try:
            # 构建过滤URL
            filter_str = ""
            if extend:
                for key, value in extend.items():
                    if value:
                        filter_str += value

            url = f"{self.host}/index.php/vod/show/id/{tid}{filter_str}/page/{pg}.html"
            response = self.fetch(url)
            
            if not response:
                return {'list': [], 'page': pg, 'pagecount': 0, 'limit': 0, 'total': 0}

            data = pq(response)
            videos = []

            # 使用一级选择器: .myui-vodlist__box;a&&title;.lazyload&&data-original;.tag&&Text;a&&href
            items = data('.myui-vodlist__box, ul.myui-vodlist li')
            for item in items.items():
                title = item('a').attr('title') or item('a').text()
                pic = item('.lazyload').attr('data-original')
                if pic and not pic.startswith('http'):
                    pic = self.host + pic
                remarks = item('.tag').text() or item('.pic-text').text() or ''
                href = item('a').attr('href')
                if href and not href.startswith('http'):
                    href = self.host + href

                if title and href:
                    # 检查是否已有相同ID的视频，避免重复
                    vid = self.get_id_from_href(href)
                    if not any(v['vod_id'] == vid for v in videos):
                        videos.append({
                            'vod_id': vid,
                            'vod_name': title,
                            'vod_pic': pic,
                            'vod_remarks': remarks
                        })

            return {
                'list': videos,
                'page': int(pg),
                'pagecount': 999,  # 假设很多页
                'limit': len(videos),
                'total': 999999
            }
        except Exception as e:
            print(f"Error in categoryContent: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'list': [], 'page': pg, 'pagecount': 0, 'limit': 0, 'total': 0}

    def detailContent(self, ids):
        """
        获取详情内容
        对应JS中的二级规则
        """
        try:
            if not ids or not ids[0]:
                return {'list': []}

            vid = ids[0]
            url = f"{self.host}/index.php/vod/detail/id/{vid}.html"
            response = self.fetch(url)

            if not response:
                return {'list': []}

            data = pq(response)

            # 解析详情页
            vod = {
                'vod_id': vid,
                'vod_name': data('h1:first').text() or data('.data a:first').text(),
                'vod_pic': '',
                'vod_remarks': '',
                'vod_year': '',
                'vod_area': '',
                'vod_director': '',
                'vod_actor': '',
                'vod_content': ''
            }

            # 图片
            img = data('.lazyload').attr('data-original')
            if img:
                if not img.startswith('http'):
                    img = self.host + img
                vod['vod_pic'] = img

            # 描述信息
            data_items = data('.data').items()
            data_list = list(data_items)
            if len(data_list) >= 1:
                # 提取各种信息
                data_text = data('.data').text()
                # 年份、地区、导演、演员等信息通常在.data内
                # 根据JS规则: ";.data:eq(0) a:eq(2)&&Text;.data:eq(0) a:eq(1)&&Text;.data:eq(2)&&Text;.data:eq(3)&&Text"
                if len(data_list) > 0:
                    links = data_list[0]('a')
                    if len(links) > 2:
                        # 假设第3个链接是年代，第2个是地区，第1个是演员（反向对应）
                        if len(links) > 2:
                            vod['vod_year'] = links.eq(2).text()
                        if len(links) > 1:
                            vod['vod_area'] = links.eq(1).text()
                        if len(links) > 0:
                            vod['vod_actor'] = links.eq(0).text()

            # 内容描述
            content_elem = data('.text-collapse span')
            if content_elem:
                vod['vod_content'] = content_elem.text()


            # 处理播放线路和播放列表，确保每个线路分开
            play_from = []
            play_urls = []

            # 查找所有播放源标签
            tabs = data('.myui-panel__head h3')
            for tab in tabs.items():
                tab_text = tab.text().strip()
                if tab_text and any(keyword in tab_text.lower() for keyword in ['播放', '线路', '云播', '在线', '资源', '高清', '极速', '备用', '专享', '秒播']):
                    play_from.append(tab_text)

            # 获取所有播放列表
            all_lists = data('.myui-content__list')
            for idx in range(len(play_from)):
                urls = []
                list_items = all_lists.eq(idx)('li') if idx < len(all_lists) else []
                for item in list_items.items():
                    a = item('a')
                    href = a.attr('href')
                    if href and not href.startswith('http'):
                        href = self.host + href
                    title = a.text().strip()
                    if title and href:
                        urls.append(f"{title}${href}")
                play_urls.append('#'.join(urls))

            # 如果没有找到任何播放线路，尝试获取所有列表作为一个播放线路
            if not play_from or not any(play_urls):
                urls = []
                list_items = data('.myui-content__list:first li')
                for item in list_items.items():
                    a = item('a')
                    href = a.attr('href')
                    if href and not href.startswith('http'):
                        href = self.host + href
                    title = a.text().strip()
                    if title and href:
                        urls.append(f"{title}${href}")
                if urls:
                    play_from = ['播放源']
                    play_urls = ['#'.join(urls)]

            # 补齐长度，确保一一对应
            if len(play_urls) < len(play_from):
                while len(play_urls) < len(play_from):
                    play_urls.append('')
            elif len(play_from) < len(play_urls):
                play_urls = play_urls[:len(play_from)]

            # 过滤掉空线路和空地址，确保前端能正确识别独立线路
            play_from_clean = []
            play_urls_clean = []
            for f, u in zip(play_from, play_urls):
                if f.strip() and u.strip():
                    play_from_clean.append(f.strip())
                    play_urls_clean.append(u.strip())
            if play_from_clean and play_urls_clean:
                vod['vod_play_from'] = '$$$'.join(play_from_clean)
                vod['vod_play_url'] = '$$$'.join(play_urls_clean)
            else:
                vod['vod_play_from'] = 'TVB云播'
                vod['vod_play_url'] = '播放$' + url

            return {"list": [vod]}
        except Exception as e:
            print(f"Error in detailContent: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"list": []}

    def searchContent(self, key, quick, pg="1"):
        """
        搜索内容
        """
        try:
            url = f"{self.host}/index.php/vod/search.html?wd={key}&submit="
            response = self.fetch(url)

            if not response:
                return {'list': []}

            data = pq(response)
            videos = []

            # 使用搜索选择器: 'ul.myui-vodlist__media li;*;*;*;*'
            items = data('ul.myui-vodlist__media li, ul.myui-vodlist li')
            for item in items.items():
                title = item('a:first').attr('title') or item('a:first').text()
                pic = item('.lazyload').attr('data-original')
                if pic and not pic.startswith('http'):
                    pic = self.host + pic
                href = item('a:first').attr('href')
                if href and not href.startswith('http'):
                    href = self.host + href
                remarks = item('.tag').text() or item('.pic-text').text() or ''

                if title and href:
                    # 检查是否已有相同ID的视频，避免重复
                    vid = self.get_id_from_href(href)
                    if not any(v['vod_id'] == vid for v in videos):
                        videos.append({
                            'vod_id': vid,
                            'vod_name': title,
                            'vod_pic': pic,
                            'vod_remarks': remarks
                        })

            return {'list': videos}
        except Exception as e:
            print(f"Error in searchContent: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        """
        获取播放URL
        """
        try:
            # 直接返回播放页URL，让播放器自行处理
            return {
                'parse': 1,
                'url': id,
                'header': self.header,
                'playUrl': ''
            }
        except Exception as e:
            print(f"Error in playerContent: {str(e)}")
            return {
                'parse': 0,
                'url': '',
                'header': {},
                'playUrl': ''
            }

    def fetch(self, url):
        """
        发送HTTP请求
        """
        try:
            response = requests.get(url, headers=self.header, timeout=self.timeout)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None

    def get_id_from_href(self, href):
        """
        从链接中提取ID
        """
        # 例如从 /index.php/vod/detail/id/123.html 提取 123
        match = re.search(r'/id/(\d+)', href)
        if match:
            return match.group(1)
        # 或者从 /vod-detail-id-123.html 提取 123
        match = re.search(r'-id-(\d+)', href)
        if match:
            return match.group(1)
        return href