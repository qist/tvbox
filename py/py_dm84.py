# coding=utf-8
# !/usr/bin/python

import sys
import requests
from lxml import etree
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):
    def getName(self):
        return "dm84"

    def init(self, extend):
        self.home_url = 'https://dmbus.cc'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

    def getDependence(self):
        return []

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        return {
            'class': [{'type_id': '1', 'type_name': '国产动漫'},
                      {'type_id': '2', 'type_name': '日本动漫'},
                      {'type_id': '3', 'type_name': '欧美动漫'},
                      {'type_id': '4', 'type_name': '电影'}],
            'filters': {
                '1': [{'key': 'type',
                       'name': '类型',
                       'value': [{'n': '全部', 'v': ''},
                                 {'n': '奇幻', 'v': '奇幻'},
                                 {'n': '战斗', 'v': '战斗'},
                                 {'n': '玄幻', 'v': '玄幻'},
                                 {'n': '穿越', 'v': '穿越'},
                                 {'n': '科幻', 'v': '科幻'},
                                 {'n': '武侠', 'v': '武侠'},
                                 {'n': '热血', 'v': '热血'},
                                 {'n': '耽美', 'v': '耽美'},
                                 {'n': '搞笑', 'v': '搞笑'},
                                 {'n': '动态漫画', 'v': '动态漫画'}]},
                      {'key': 'year',
                       'name': '时间',
                       'value': [{'n': '全部', 'v': ''},
                                 {'n': '2024', 'v': '2024'},
                                 {'n': '2023', 'v': '2023'},
                                 {'n': '2022', 'v': '2022'},
                                 {'n': '2021', 'v': '2021'},
                                 {'n': '2020', 'v': '2020'},
                                 {'n': '2019', 'v': '2019'},
                                 {'n': '2018', 'v': '2018'},
                                 {'n': '2017', 'v': '2017'},
                                 {'n': '2016', 'v': '2016'},
                                 {'n': '2015', 'v': '2015'}]},
                      {'key': 'by',
                       'name': '排序',
                       'value': [{'n': '按时间', 'v': 'time'},
                                 {'n': '按人气', 'v': 'hits'},
                                 {'n': '按评分', 'v': 'score'}]}],
                '2': [{'key': 'type',
                       'name': '类型',
                       'value': [{'n': '全部', 'v': ''},
                                 {'n': '冒险', 'v': '冒险'},
                                 {'n': '奇幻', 'v': '奇幻'},
                                 {'n': '战斗', 'v': '战斗'},
                                 {'n': '后宫', 'v': '后宫'},
                                 {'n': '热血', 'v': '热血'},
                                 {'n': '励志', 'v': '励志'},
                                 {'n': '搞笑', 'v': '搞笑'},
                                 {'n': '校园', 'v': '校园'},
                                 {'n': '机战', 'v': '机战'},
                                 {'n': '悬疑', 'v': '悬疑'},
                                 {'n': '治愈', 'v': '治愈'},
                                 {'n': '百合', 'v': '百合'},
                                 {'n': '恐怖', 'v': '恐怖'},
                                 {'n': '泡面番', 'v': '泡面番'},
                                 {'n': '恋爱', 'v': '恋爱'},
                                 {'n': '推理', 'v': '推理'}]},
                      {'key': 'year',
                       'name': '时间',
                       'value': [{'n': '全部', 'v': ''},
                                 {'n': '2024', 'v': '2024'},
                                 {'n': '2023', 'v': '2023'},
                                 {'n': '2022', 'v': '2022'},
                                 {'n': '2021', 'v': '2021'},
                                 {'n': '2020', 'v': '2020'},
                                 {'n': '2019', 'v': '2019'},
                                 {'n': '2018', 'v': '2018'},
                                 {'n': '2017', 'v': '2017'},
                                 {'n': '2016', 'v': '2016'},
                                 {'n': '2015', 'v': '2015'}]},
                      {'key': 'by',
                       'name': '排序',
                       'value': [{'n': '按时间', 'v': 'time'},
                                 {'n': '按人气', 'v': 'hits'},
                                 {'n': '按评分', 'v': 'score'}]}],
                '3': [{'key': 'type',
                       'name': '类型',
                       'value': [{'n': '全部', 'v': ''},
                                 {'n': '科幻', 'v': '科幻'},
                                 {'n': '冒险', 'v': '冒险'},
                                 {'n': '战斗', 'v': '战斗'},
                                 {'n': '百合', 'v': '百合'},
                                 {'n': '奇幻', 'v': '奇幻'},
                                 {'n': '热血', 'v': '热血'},
                                 {'n': '搞笑', 'v': '搞笑'}]},
                      {'key': 'year',
                       'name': '时间',
                       'value': [{'n': '全部', 'v': ''},
                                 {'n': '2024', 'v': '2024'},
                                 {'n': '2023', 'v': '2023'},
                                 {'n': '2022', 'v': '2022'},
                                 {'n': '2021', 'v': '2021'},
                                 {'n': '2020', 'v': '2020'},
                                 {'n': '2019', 'v': '2019'},
                                 {'n': '2018', 'v': '2018'},
                                 {'n': '2017', 'v': '2017'},
                                 {'n': '2016', 'v': '2016'},
                                 {'n': '2015', 'v': '2015'}]},
                      {'key': 'by',
                       'name': '排序',
                       'value': [{'n': '按时间', 'v': 'time'},
                                 {'n': '按人气', 'v': 'hits'},
                                 {'n': '按评分', 'v': 'score'}]}],
                '4': [{'key': 'type',
                       'name': '类型',
                       'value': [{'n': '全部', 'v': ''},
                                 {'n': '搞笑', 'v': '搞笑'},
                                 {'n': '奇幻', 'v': '奇幻'},
                                 {'n': '治愈', 'v': '治愈'},
                                 {'n': '科幻', 'v': '科幻'},
                                 {'n': '喜剧', 'v': '喜剧'},
                                 {'n': '冒险', 'v': '冒险'},
                                 {'n': '动作', 'v': '动作'},
                                 {'n': '爱情', 'v': '爱情'}]},
                      {'key': 'year',
                       'name': '时间',
                       'value': [{'n': '全部', 'v': ''},
                                 {'n': '2024', 'v': '2024'},
                                 {'n': '2023', 'v': '2023'},
                                 {'n': '2022', 'v': '2022'},
                                 {'n': '2021', 'v': '2021'},
                                 {'n': '2020', 'v': '2020'},
                                 {'n': '2019', 'v': '2019'},
                                 {'n': '2018', 'v': '2018'},
                                 {'n': '2017', 'v': '2017'},
                                 {'n': '2016', 'v': '2016'},
                                 {'n': '2015', 'v': '2015'}]},
                      {'key': 'by',
                       'name': '排序',
                       'value': [{'n': '按时间', 'v': 'time'},
                                 {'n': '按人气', 'v': 'hits'},
                                 {'n': '按评分', 'v': 'score'}]}]
            }
        }

    def homeVideoContent(self):
        data = self.get_data(self.home_url)
        return {'list': data, 'parse': 0, 'jx': 0}

    def categoryContent(self, cid, page, filter, ext):
        _type = ext.get('type') if ext.get('type') else ''
        _year = ext.get('year') if ext.get('year') else ''
        _by = ext.get('by') if ext.get('by') else ''
        url = f'{self.home_url}/show-{cid}--{_by}-{_type}--{_year}-{page}.html'
        data = self.get_data(url)
        return {'list': data, 'parse': 0, 'jx': 0}
        # return {"list": [], "msg": "来自py_dependence的categoryContent"}

    def detailContent(self, did):
        ids = did[0]
        video_list = []
        try:
            res = requests.get(f'{self.home_url}/v/{ids}.html', headers=self.headers)
            root = etree.HTML(res.text)
            vod_play_from = '$$$'.join(root.xpath(
                '//ul[contains(@class, "play_from")]/li/text()'))  # //ul[contains(@class, "abc")]  [@class="tab_control play_from"]
            play_list = root.xpath('//ul[contains(@class, "play_list")]')
            vod_play_url = []
            for i in play_list:
                name_list = i.xpath('./li/a/text()')
                url_list = i.xpath('./li/a/@href')
                vod_play_url.append(
                    '#'.join([_name + '$' + _url for _name, _url in zip(name_list, url_list)])
                )
            video_list.append(
                {
                    'type_name': '',
                    'vod_id': ids,
                    'vod_name': '',
                    'vod_remarks': '',
                    'vod_year': '',
                    'vod_area': '',
                    'vod_actor': '',
                    'vod_director': '沐辰_为爱发电',
                    'vod_content': '',
                    'vod_play_from': vod_play_from,
                    'vod_play_url': '$$$'.join(vod_play_url)

                }
            )
            return {"list": video_list, 'parse': 0, 'jx': 0}
        except requests.RequestException as e:
            return {'list': [], 'msg': e}

        # return {"list": [], "msg": "来自py_dependence的detailContent"}

    def searchContent(self, key, quick, page='1'):
        if page != '1':
            return {'list': [], 'parse': 0, 'jx': 0}
        url = f'{self.home_url}/s----------.html?wd={key}'
        data = self.get_data(url)
        return {'list': data, 'parse': 0, 'jx': 0}
        # return {"list": [], "msg": "来自py_dependence的searchContent"}

    def playerContent(self, flag, pid, vipFlags):
        play_url = 'https://gitee.com/dobebly/my_img/raw/c1977fa6134aefb8e5a34dabd731a4d186c84a4d/x.mp4'
        try:
            res = requests.get(f'{self.home_url}{pid}', headers=self.headers)
            root = etree.HTML(res.text)
            urls = root.xpath('//iframe/@src')
            if len(urls) == 0:
                return {'url': play_url, 'parse': 0, 'jx': 0}
            return {'url': urls[0], 'parse': 1, 'jx': 0}

        except requests.RequestException as e:
            print(e)
            return {'url': play_url, 'parse': 0, 'jx': 0}
        # return {"list": [], "msg": "来自py_dependence的playerContent"}

    def localProxy(self, params):
        pass

    def destroy(self):
        return '正在Destroy'
    def get_data(self, url):
        data = []
        try:
            res = requests.get(url, headers=self.headers)
            root = etree.HTML(res.text)
            data_list = root.xpath('//li/div[@class="item"]')
            for i in data_list:
                data.append(
                    {
                        'vod_id': i.xpath('./a[2]/@href')[0].split('/')[-1].split('.')[0],
                        'vod_name': i.xpath('./a[2]/@title')[0],
                        'vod_pic': i.xpath('./a[1]/@data-bg')[0],
                        'vod_remarks': i.xpath('./span/text()')[0]
                    }
                )
        except requests.RequestException as e:
            return data
        return data
