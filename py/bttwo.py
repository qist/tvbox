#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File  : 两个BT.py
# Author: DaShenHan&道长-----先苦后甜，任凭晚风拂柳颜------
# Author's Blog: https://blog.csdn.net/qq_32394351
# Date  : 2024/1/8

import os.path
import sys

sys.path.append('..')
try:
    # from base.spider import Spider as BaseSpider
    from base.spider import BaseSpider
except ImportError:
    from t4.base.spider import BaseSpider
import json
import time
import base64
import re
from pathlib import Path
import io
import tokenize
from urllib.parse import quote
from Crypto.Cipher import AES, PKCS1_v1_5 as PKCS1_cipher
from Crypto.Util.Padding import unpad

"""
配置示例:
t4的配置里ext节点会自动变成api对应query参数extend,但t4的ext字符串不支持路径格式，比如./开头或者.json结尾
api里会自动含有ext参数是base64编码后的选中的筛选条件
 {
    "key":"hipy_t4_两个BT",
    "name":"两个BT(hipy_t4)",
    "type":4,
    "api":"http://192.168.31.49:5707/api/v1/vod/两个BT?api_ext={{host}}/txt/hipy/两个BT.json",
    "searchable":1,
    "quickSearch":0,
    "filterable":1,
    "ext":"两个BT"
},
{
    "key": "hipy_t3_两个BT",
    "name": "两个BT(hipy_t3)",
    "type": 3,
    "api": "{{host}}/txt/hipy/两个BT.py",
    "searchable": 1,
    "quickSearch": 0,
    "filterable": 1,
    "ext": "{{host}}/txt/hipy/两个BT.json"
},
"""


class Spider(BaseSpider):  # 元类 默认的元类 type
    api: str = 'https://www.bttwo.net'
    api_ext_file: str = api + '/movie_bt/'

    def getName(self):
        return "规则名称如:基础示例"

    def init_api_ext_file(self):
        """
        这个函数用于初始化py文件对应的json文件，用于存筛选规则。
        执行此函数会自动生成筛选文件
        @return:
        """
        ext_file = __file__.replace('.py', '.json')
        print(f'ext_file:{ext_file}')

        # 全部电影网页: https://www.bttwo.net/movie_bt/
        # ==================== 获取全部电影筛选条件 ======================
        r = self.fetch(self.api_ext_file)
        html = r.text
        html = self.html(html)

        filter_movie_bt = []
        lis = html.xpath('//*[@id="beautiful-taxonomy-filters-tax-movie_bt_cat"]/a')
        li_value = []
        for li in lis:
            li_value.append({
                'n': ''.join(li.xpath('./text()')),
                'v': ''.join(li.xpath('@cat-url')).replace(self.api, ''),
            })
        # print(li_value)
        filter_movie_bt.append({
            "key": "cat",
            "name": "地区",
            "value": li_value
        })

        lis = html.xpath('//*[@id="beautiful-taxonomy-filters-tax-movie_bt_year"]/a')
        li_value = []
        for li in lis:
            li_value.append({
                'n': ''.join(li.xpath('./text()')),
                'v': ''.join(li.xpath('@cat-url')).replace(self.api, ''),
            })
        # print(li_value)
        filter_movie_bt.append({
            "key": "year",
            "name": "年份",
            "value": li_value
        })

        lis = html.xpath('//*[@id="beautiful-taxonomy-filters-tax-movie_bt_tags"]/a')
        li_value = []
        for li in lis:
            li_value.append({
                'n': ''.join(li.xpath('./text()')),
                'v': ''.join(li.xpath('@cat-url')).replace(self.api, ''),
            })
        # print(li_value)
        filter_movie_bt.append({
            "key": "tags",
            "name": "影片类型",
            "value": li_value
        })

        print(filter_movie_bt)

        ext_file_dict = {
            "movie_bt": filter_movie_bt,
        }
        with open(ext_file, mode='w+', encoding='utf-8') as f:
            f.write(json.dumps(ext_file_dict, ensure_ascii=False))

    def init(self, extend=""):
        """
        初始化加载extend，一般与py文件名同名的json文件作为扩展筛选
        @param extend:
        @return:
        """

        def init_file(ext_file):
            """
            根据与py对应的json文件去扩展规则的筛选条件
            """
            ext_file = Path(ext_file).as_posix()
            if os.path.exists(ext_file):
                with open(ext_file, mode='r', encoding='utf-8') as f:
                    try:
                        ext_dict = json.loads(f.read())
                        self.config['filter'].update(ext_dict)
                    except Exception as e:
                        print(f'更新扩展筛选条件发生错误:{e}')

        ext = self.extend
        print(f"============{extend}============")
        if isinstance(ext, str):
            if ext.startswith('./'):
                ext_file = os.path.join(os.path.dirname(__file__), ext)
                init_file(ext_file)
            elif ext.startswith('http'):
                try:
                    r = self.fetch(ext)
                    self.config['filter'].update(r.json())
                except Exception as e:
                    print(f'更新扩展筛选条件发生错误:{e}')
            elif not ext.startswith('./') and not ext.startswith('http'):
                ext_file = os.path.join(os.path.dirname(__file__), './' + ext + '.json')
                init_file(ext_file)

        # 装载模块，这里只要一个就够了
        if isinstance(extend, list):
            for lib in extend:
                if '.Spider' in str(type(lib)):
                    self.module = lib
                    break

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filterable=False):
        """
        获取首页分类及筛选数据
        @param filterable: 能否筛选，跟t3/t4配置里的filterable参数一致
        @return:
        """
        class_name = '影片库&最新电影&热门下载&本月热门&国产剧&美剧&日韩剧'  # 静态分类名称拼接
        class_url = 'movie_bt&new-movie&hot&hot-month&zgjun&meiju&jpsrtv'  # 静态分类标识拼接

        result = {}
        classes = []

        if all([class_name, class_url]):
            class_names = class_name.split('&')
            class_urls = class_url.split('&')
            cnt = min(len(class_urls), len(class_names))
            for i in range(cnt):
                classes.append({
                    'type_name': class_names[i],
                    'type_id': class_urls[i]
                })

        result['class'] = classes
        if filterable:
            result['filters'] = self.config['filter']
        return result

    def homeVideoContent(self):
        """
        首页推荐列表
        @return:
        """
        r = self.fetch(self.api)
        html = r.text
        html = self.html(html)
        d = []

        lis = html.xpath('//*[contains(@class,"leibox")]/ul/li')
        print(len(lis))
        for li in lis:
            d.append({
                'vod_name': ''.join(li.xpath('h3//text()')),
                'vod_id': ''.join(li.xpath('a/@href')),
                'vod_pic': ''.join(li.xpath('.//img//@data-original')),
                'vod_remarks': ''.join(li.xpath('.//*[contains(@class,"jidi")]//text()')),
            })
        result = {
            'list': d
        }
        return result

    def categoryContent(self, tid, pg, filterable, extend):
        """
        返回一级列表页数据
        @param tid: 分类id
        @param pg: 当前页数
        @param filterable: 能否筛选
        @param extend: 当前筛选数据
        @return:
        """
        page_count = 24  # 默认赋值一页列表24条数据
        if tid != 'movie_bt':
            url = self.api + f'/{tid}/page/{pg}'
        else:
            fls = extend.keys()  # 哪些刷新数据
            url = self.api + f'/{tid}'
            if 'cat' in fls:
                url += extend['cat']
            if 'year' in fls:
                url += extend['year']
            if 'tags' in fls:
                url += extend['tags']
            url += f'/page/{pg}'
        print(url)

        r = self.fetch(url)
        html = r.text
        html = self.html(html)
        d = []
        lis = html.xpath('//*[contains(@class,"bt_img")]/ul/li')
        # print(len(lis))
        for li in lis:
            d.append({
                'vod_name': ''.join(li.xpath('h3//text()')),
                'vod_id': ''.join(li.xpath('a/@href')),
                'vod_pic': ''.join(li.xpath('.//img//@data-original')),
                'vod_remarks': ''.join(li.xpath('.//*[contains(@class,"hdinfo")]//text()')),
            })

        result = {
            'list': d,
            'page': pg,
            'pagecount': 9999 if len(d) >= page_count else pg,
            'limit': 90,
            'total': 999999,
        }
        return result

    def detailContent(self, ids):
        """
        返回二级详情页数据
        @param ids: 一级传过来的vod_id列表
        @return:
        """
        vod_id = ids[0]
        r = self.fetch(vod_id)
        html = r.text
        html = self.html(html)
        lis = html.xpath('//*[contains(@class,"dytext")]/ul/li')
        plis = html.xpath('//*[contains(@class,"paly_list_btn")]/a')
        vod = {"vod_id": vod_id,
               "vod_name": ''.join(html.xpath('//*[contains(@class,"dytext")]//h1//text()')),
               "vod_pic": ''.join(html.xpath('//*[contains(@class,"dyimg")]/img/@src')),
               "type_name": ''.join(lis[0].xpath('.//text()')) if len(lis) > 0 else '',
               "vod_year": ''.join(lis[2].xpath('.//text()')) if len(lis) > 2 else '',
               "vod_area": ''.join(lis[1].xpath('.//text()')) if len(lis) > 1 else '',
               "vod_remarks": ''.join(lis[4].xpath('.//text()')) if len(lis) > 4 else '',
               "vod_actor": ''.join(lis[7].xpath('.//text()')) if len(lis) > 7 else '',
               "vod_director": ''.join(lis[5].xpath('.//text()')) if len(lis) > 5 else '',
               "vod_content": ''.join(html.xpath('//*[contains(@class,"yp_context")]/p//text()')),
               "vod_play_from": '在线播放',
               "vod_play_url": '选集播放1$1.mp4#选集播放2$2.mp4$$$选集播放3$3.mp4#选集播放4$4.mp4'}
        vod_play_urls = []
        for pli in plis:
            vname = ''.join(pli.xpath('./text()'))
            vurl = ''.join(pli.xpath('./@href'))
            vod_play_urls.append(vname + '$' + vurl)
        vod['vod_play_url'] = '#'.join(vod_play_urls)
        result = {
            'list': [vod]
        }
        return result

    def searchContent(self, wd, quick=False, pg=1):
        """
        返回搜索列表
        @param wd: 搜索关键词
        @param quick: 是否来自快速搜索。t3/t4配置里启用了快速搜索，在快速搜索在执行才会是True
        @return:
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
            "Host": "www.bttwo.net",
            "Referer": self.api
        }

        url = f'{self.api}/xssearch?q={quote(wd)}'
        r = self.fetch(url, headers=headers)
        cookies = ['myannoun=1']
        for key, value in r.headers.items():
            if str(key).lower() == 'set-cookie':
                cookies.append(value.split(';')[0])
        new_headers = {
            'Cookie': ';'.join(cookies),
            # 'Pragma': 'no-cache',
            # 'Origin': 'https://www.bttwo.net',
            # 'Referer': url,
            # 'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            # 'Sec-Ch-Ua-Mobile': '?0',
            # 'Sec-Ch-Ua-Platform': '"Windows"',
            # 'Sec-Fetch-Dest': 'document',
            # 'Sec-Fetch-Mode': 'navigate',
            # 'Sec-Fetch-Site': 'same-origin',
            # 'Sec-Fetch-User': '?1',
            # 'Upgrade-Insecure-Requests': '1',
        }
        headers.update(new_headers)
        # print(headers)
        html = self.html(r.text)
        captcha = ''.join(html.xpath('//*[@class="erphp-search-captcha"]/form/text()')).strip()
        # print('验证码:', captcha)
        answer = self.eval_computer(captcha)
        # print('回答:', captcha, answer)
        data = {'result': str(answer)}
        # print('待post数据:', data)
        self.post(url, data=data, headers=headers, cookies=None)
        r = self.fetch(url, headers=headers)
        # print(r.text)
        html = self.html(r.text)
        lis = html.xpath('//*[contains(@class,"search_list")]/ul/li')
        print('搜索结果数:', len(lis))
        d = []
        if len(lis) < 1:
            d.append({
                'vod_name': wd,
                'vod_id': 'index.html',
                'vod_pic': 'https://gitee.com/CherishRx/imagewarehouse/raw/master/image/13096725fe56ce9cf643a0e4cd0c159c.gif',
                'vod_remarks': '测试搜索',
            })
        else:
            for li in lis:
                d.append({
                    'vod_name': ''.join(li.xpath('h3//text()')),
                    'vod_id': ''.join(li.xpath('a/@href')),
                    'vod_pic': ''.join(li.xpath('a/img/@data-original')),
                    'vod_remarks': ''.join(li.xpath('p//text()')),
                })
        result = {
            'list': d
        }
        # print(result)
        return result

    def playerContent(self, flag, id, vipFlags):
        """
        解析播放,返回json。壳子视情况播放直链或进行嗅探
        @param flag: vod_play_from 播放来源线路
        @param id: vod_play_url 播放的链接
        @param vipFlags: vip标识
        @return:
        """
        r = self.fetch(id)
        html = r.text
        text = html.split('window.wp_nonce=')[1].split('eval')[0]
        # print(text)
        code = self.regStr(text, 'var .*?=.*?"(.*?)"')
        key = self.regStr(text, 'var .*?=md5.enc.Utf8.parse\\("(.*?)"')
        iv = self.regStr(text, 'var iv=.*?\\((\\d+)')
        text = self.aes_cbs_decode(code, key, iv)
        # print(code)
        # print(key,iv)
        # print(text)
        url = self.regStr(text, 'url: "(.*?)"')
        # print(url)
        parse = 0
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux；； Android 11；； M2007J3SC Build/RKQ1.200826.002；； wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/99.0.4844.48 Mobile Safari/537.36',
            'Referer': url,
        }
        result = {
            'parse': parse,  # 1=嗅探,0=播放
            'playUrl': '',  # 解析链接
            'url': url,  # 直链或待嗅探地址
            'header': headers,  # 播放UA
        }
        print(result)
        return result

    config = {
        "player": {},
        "filter": {}
    }
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
        "Host": "www.bttwo.net",
        "Referer": "https://www.bttwo.net/"
    }

    def localProxy(self, params):
        return [200, "video/MP2T", ""]

    # -----------------------------------------------自定义函数-----------------------------------------------
    def eval_computer(self, text):
        """
        自定义的字符串安全计算器
        @param text:字符串的加减乘除
        @return:计算后得到的值
        """
        localdict = {}
        self.safe_eval(f'ret={text.replace("=", "")}', localdict)
        ret = localdict.get('ret') or None
        return ret

    def safe_eval(self, code: str = '', localdict: dict = None):
        code = code.strip()
        if not code:
            return {}
        if localdict is None:
            localdict = {}
        builtins = __builtins__
        if not isinstance(builtins, dict):
            builtins = builtins.__dict__.copy()
        else:
            builtins = builtins.copy()
        for key in ['__import__', 'eval', 'exec', 'globals', 'dir', 'copyright', 'open', 'quit']:
            del builtins[key]  # 删除不安全的关键字
        # print(builtins)
        global_dict = {'__builtins__': builtins,
                       'json': json, 'print': print,
                       're': re, 'time': time, 'base64': base64
                       }  # 禁用内置函数,不允许导入包
        try:
            self.check_unsafe_attributes(code)
            exec(code, global_dict, localdict)
            return localdict
        except Exception as e:
            return {'error': f'执行报错:{e}'}

    # ==================== 静态函数 ======================
    @staticmethod
    def aes_cbs_decode(ciphertext, key, iv):
        # 将密文转换成byte数组
        ciphertext = base64.b64decode(ciphertext)
        # 构建AES解密器
        decrypter = AES.new(key.encode(), AES.MODE_CBC, iv.encode())
        # 解密
        plaintext = decrypter.decrypt(ciphertext)
        # 去除填充
        plaintext = unpad(plaintext, AES.block_size)
        # 输出明文
        # print(plaintext.decode('utf-8'))
        return plaintext.decode('utf-8')

    @staticmethod
    def check_unsafe_attributes(string):
        """
        安全检测需要exec执行的python代码
        :param string:
        :return:
        """
        g = tokenize.tokenize(io.BytesIO(string.encode('utf-8')).readline)
        pre_op = ''
        for toktype, tokval, _, _, _ in g:
            if toktype == tokenize.NAME and pre_op == '.' and tokval.startswith('_'):
                attr = tokval
                msg = "access to attribute '{0}' is unsafe.".format(attr)
                raise AttributeError(msg)
            elif toktype == tokenize.OP:
                pre_op = tokval


if __name__ == '__main__':
    from t4.core.loader import t4_spider_init

    spider = Spider()
    t4_spider_init(spider)
    spider.init_api_ext_file()  # 生成筛选对应的json文件

    # print(spider.homeVideoContent())
    # print(spider.categoryContent('movie_bt', 1, True, {}))
    # print(spider.searchContent('斗罗大陆'))
    # print(spider.detailContent(['https://www.bttwo.net/movie/20107.html']))
    # print(spider.playerContent('在线播放', 'https://www.bttwo.net/v_play/bXZfMTMyNjA2LW5tXzE=.html', None))

    # ciphertext = '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'
    # key = 'ae05c73de8a193cf'
    # iv = '1234567890983456'
    # print(spider.aes_cbs_decode(ciphertext, key, iv))
