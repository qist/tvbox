#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : Doubebly
# @Time    : 2025/12/21
# @file    : 新韩剧网

D = print
C = Exception
import re
import sys
import requests as B
from urllib import parse
from pyquery import PyQuery as F
from Crypto.Cipher import AES as A
from Crypto.Util.Padding import unpad
import base64 as I
sys.path.append('..')
from base.spider import Spider as E

class Spider(E):
    def __init__(A):
        super().__init__()
        A.debug = False
        A.name = '新韩剧网'
        A.error_play_url = 'https://kjjsaas-sh.oss-cn-shanghai.aliyuncs.com/u/3401405881/20240818-936952-fc31b16575e80a7562cdb1f81a39c6b0.mp4'
        A.home_url = 'https://www.hanju7.com'
        A.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36',
            'Referer': 'https://www.hanju7.com/'
        }

    def getName(A):
        return A.name

    def init(A, extend='{}'):
        A.extend = extend

    def homeContent(E, filter):
        G = {
            'class': [
                {'type_id': '1', 'type_name': '韩剧'},
                {'type_id': '3', 'type_name': '韩国电影'},
                {'type_id': '4', 'type_name': '韩国综艺'},
                {'type_id': 'hot', 'type_name': '排行榜'},
                {'type_id': 'new', 'type_name': '最新更新'}
            ],
            'filters': {
                '1': [
                    {'key': 'year', 'name': '按年份', 'value': [
                        {'n': '全部', 'v': ''}, {'n': '2025', 'v': '2025'}, {'n': '2024', 'v': '2024'},
                        {'n': '2023', 'v': '2023'}, {'n': '2022', 'v': '2022'}, {'n': '2021', 'v': '2021'},
                        {'n': '2020', 'v': '2020'}, {'n': '10后', 'v': '2010__2019'}, {'n': '00后', 'v': '2000__2009'},
                        {'n': '90后', 'v': '1990__1999'}, {'n': '80后', 'v': '1980__1989'}, {'n': '更早', 'v': '1900__1980'}
                    ]},
                    {'key': 'sort', 'name': '按排序', 'value': [{'n': '最新', 'v': 'newstime'}, {'n': '热门', 'v': 'onclick'}]}
                ],
                '3': [
                    {'key': 'year', 'name': '按年份', 'value': [
                        {'n': '全部', 'v': ''}, {'n': '2025', 'v': '2025'}, {'n': '2024', 'v': '2024'},
                        {'n': '2023', 'v': '2023'}, {'n': '2022', 'v': '2022'}, {'n': '2021', 'v': '2021'},
                        {'n': '2020', 'v': '2020'}, {'n': '10后', 'v': '2010__2019'}, {'n': '00后', 'v': '2000__2009'},
                        {'n': '90后', 'v': '1990__1999'}, {'n': '80后', 'v': '1980__1989'}, {'n': '更早', 'v': '1900__1980'}
                    ]},
                    {'key': 'sort', 'name': '按排序', 'value': [{'n': '最新', 'v': 'newstime'}, {'n': '热门', 'v': 'onclick'}]}
                ],
                '4': [
                    {'key': 'year', 'name': '按年份', 'value': [
                        {'n': '全部', 'v': ''}, {'n': '2025', 'v': '2025'}, {'n': '2024', 'v': '2024'},
                        {'n': '2023', 'v': '2023'}, {'n': '2022', 'v': '2022'}, {'n': '2021', 'v': '2021'},
                        {'n': '2020', 'v': '2020'}, {'n': '10后', 'v': '2010__2019'}, {'n': '00后', 'v': '2000__2009'},
                        {'n': '90后', 'v': '1990__1999'}, {'n': '80后', 'v': '1980__1989'}, {'n': '更早', 'v': '1900__1980'}
                    ]},
                    {'key': 'sort', 'name': '按排序', 'value': [{'n': '最新', 'v': 'newstime'}, {'n': '热门', 'v': 'onclick'}]}
                ]
            },
            'list': [],
            'parse': 0,
            'jx': 0
        }
        try:
            H = B.get(E.home_url, headers=E.headers)
            H.encoding = 'utf-8'
            I = F(H.text)
            for A in I('div.list ul li').items():
                pic_url = A('a').attr('data-original')
                pic_url = pic_url if pic_url.startswith(('https', 'http')) else 'https:' + pic_url
                G['list'].append({
                    'vod_id': A('a').attr('href'),
                    'vod_name': A('a').attr('title'),
                    'vod_pic': pic_url,
                    'vod_remarks': A('span.tip').text()
                })
        except C as J:
            D(J)
        return G

    def categoryContent(I, cid, page, filter, ext):
        H = int(page)
        G = cid
        E = {'list': [], 'parse': 0, 'jx': 0}
        M = ext.get('year', '')
        N = ext.get('sort', '')
        if G in ['hot', 'new']:
            J = I.home_url + f"/{G}.html"
        else:
            J = I.home_url + f"/list/{G}-{M}-{N}-{H-1}.html"
        try:
            K = B.get(J, headers=I.headers)
            K.encoding = 'utf-8'
            L = F(K.text)
            if G in ['hot', 'new']:
                for A in L('div.txt ul li').items():
                    O = A('a').attr('href')
                    if O is None:
                        continue
                    E['list'].append({
                        'vod_id': O,
                        'vod_name': A('a').text(),
                        'vod_pic': 'https://youke2.picui.cn/s1/2025/12/21/694796745c0c6.png',
                        'vod_remarks': A('#actor').text(),
                        'style': {'type': 'list'}
                    })
                E['pagecount'] = 1
                E['page'] = H
            else:
                for A in L('div.list ul li').items():
                    pic_url = A('a').attr('data-original')
                    pic_url = pic_url if pic_url.startswith(('https', 'http')) else 'https:' + pic_url
                    E['list'].append({
                        'vod_id': A('a').attr('href'),
                        'vod_name': A('a').attr('title'),
                        'vod_pic': pic_url,
                        'vod_remarks': A('span.tip').text()
                    })
        except C as P:
            D(P)
        return E

    def detailContent(E, did):
        G = {'list': [], 'parse': 0, 'jx': 0}
        H = did[0]
        try:
            I = B.get(E.home_url + H, headers=E.headers)
            I.encoding = 'utf-8'
            A = F(I.text)
            J = []
            for K in A('div.play ul li').items():
                L = K('a').text()
                onclick_match = re.search("'(.*?)'", K('a').attr('onclick') or '')
                M = onclick_match.group(1) if onclick_match else ''
                J.append(f"{L}${M}")
            N = {
                'type_name': A('div.detail div.info dl:eq(2) dd').text(),
                'vod_id': H,
                'vod_name': A('div.detail div.info dl:eq(0) dd').text(),
                'vod_remarks': A('div.detail div.info dl:eq(4) dd').text(),
                'vod_year': A('div.detail div.info dl:eq(5) dd').text(),
                'vod_area': '',
                'vod_actor': A('div.detail div.info dl:eq(1) dd').text(),
                'vod_director': '',
                'vod_content': A('div.juqing').text(),
                'vod_play_from': '恒轩',
                'vod_play_url': '#'.join(J)
            }
            G['list'].append(N)
        except C as O:
            D(O)
        return G

    def searchContent(G, key, quick, page='1'):
        A = {'list': [], 'parse': 0, 'jx': 0}
        try:
            H = G.headers.copy()
            H['Content-type'] = 'application/x-www-form-urlencoded'
            data = f"show=searchkey&keyboard={parse.quote(key)}"
            I = B.post(G.home_url + '/search/', headers=H, data=data)
            I.encoding = 'utf-8'
            J = F(I.text)
            for E in J('div.txt ul li').items():
                K = E('a').attr('href')
                if K is None:
                    continue
                A['list'].append({
                    'vod_id': K,
                    'vod_name': E('a').text(),
                    'vod_pic': 'https://youke2.picui.cn/s1/2025/12/21/694796745c0c6.png',
                    'vod_remarks': E('#actor').text(),
                    'style': {'type': 'list'}
                })
            A['pagecount'] = 1
            A['page'] = 1
        except C as L:
            D(L)
        return A

    def playerContent(E, flag, pid, vipFlags):
        F = {'url': E.error_play_url, 'parse': 0, 'jx': 0, 'header': {}}
        try:
            G = B.get(E.home_url + f"/u/u1.php?ud={pid}", headers=E.headers)
            if G.ok:
                J = bytes([109, 121, 45, 116, 111, 45, 110, 101, 119, 104, 97, 110, 45, 50, 48, 50, 53] + [0]*15)
                H = I.b64decode(G.text)
                K = H[:16]
                L = H[16:]
                M = A.new(J, A.MODE_CBC, K)
                N = unpad(M.decrypt(L), A.block_size).decode()
                F['url'] = N.strip()
        except C as O:
            D(O)
        return F

if __name__ == '__main__':
    pass