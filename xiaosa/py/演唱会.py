# -*- coding: utf-8 -*-
"""
哔哩哔哩「音乐·演唱会」Python 源 —— OK影视 / FongMi 专用

【为什么之前"拉取没数据、播放没数据"】照着 OK影视 包内 py 外壳（assets/chaquopy/app.py）的实际调用方式逐条对齐：
 1. 外壳调用的是 homeContent(filter)，原写法 homeContent(self) 会直接 TypeError —— 首页连分类都出不来。
    现在写成 homeContent(*args) 兼容两种调用。
 2. 外壳 playerContent(ru, flag, id, vipFlags) 是 (flag, id) 顺序，原写法按 (ids, flag) 取，
    BV 号被当成 flag 丢掉，于是播放返回空 —— 现在自动从所有参数里识别 BV 号，两种顺序都吃。
 3. 外壳会自己 json.dumps，所以 py 必须返回 dict / list；返回 JSON 字符串会被二次编码，解析失败。
 4. extend、ids 外壳已用 str2json 还原成 dict / list 再传入，这里仍保留兼容分支，两种都认。
 5. B站搜索有 IP 频控，同一分类时有时无（实测同词 20 条 → 0 条 → 20 条）：现在三接口轮询 + 退避重试 +
    关键词变体，仍为空则用音乐区排行榜兜底，分类页不再空白。
 6. B站 CDN 硬要求 Referer：只带 UA 一律 403，带 Referer 才 206 —— 播放返回的 header 已内置 UA+Referer。

【放置】接口配置同目录的 py 子文件夹：./py/演唱会.py
【接口条目】直接沿用 演唱会接口.json：{"key":"py_演唱会","name":"演唱会 • 哔哩哔哩","type":3,"api":"./py/演唱会.py"}
【可选】SESSDATA 填登录态可解锁更高画质；不填也能出 720P 直链。
"""
import hashlib
import json
import random
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

try:
    import requests as _REQ
except Exception:
    _REQ = None

SESSDATA = ""            # 选填：B站 Cookie 里的 SESSDATA
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
BUVID = "buvid3=84B0395D-C9F2-C490-E92E-A09AB48FE26E71636infoc"
PIC_PROXY = ""           # 封面 403 时可填 "https://images.weserv.nl/?url="

CLASSES = [{'type_name': '演唱会筛选', 'type_id': '演唱会超清'}, {'type_name': '粤语', 'type_id': '粤语歌曲超清'}, {'type_name': 'KTV热门', 'type_id': 'KTV热门歌曲'}, {'type_name': '民谣歌曲', 'type_id': '民谣歌曲超清'}, {'type_name': '经典老歌', 'type_id': '经典老歌超清'}, {'type_name': '网红翻唱', 'type_id': '网红翻唱歌曲超清'}, {'type_name': 'DJ', 'type_id': 'DJ歌曲超清'}, {'type_name': '网易云经典', 'type_id': '网易云经典歌曲'}, {'type_name': '滚石经典', 'type_id': '滚石歌曲'}, {'type_name': '古风歌曲', 'type_id': '古风歌曲'}, {'type_name': '闽南语歌曲', 'type_id': '闽南语歌曲'}, {'type_name': '电子琴纯音乐', 'type_id': '电子琴纯音乐'}, {'type_name': '抖音DJ', 'type_id': '抖音DJ'}, {'type_name': '无损音乐', 'type_id': '无损音乐'}, {'type_name': '时光音乐会', 'type_id': '时光音乐会MV'}, {'type_name': '2026年热榜', 'type_id': '2026年热门歌曲'}, {'type_name': '2025年热榜', 'type_id': '2025年热门歌曲'}, {'type_name': '2024年热榜', 'type_id': '2024年热门歌曲'}, {'type_name': '00年代经典', 'type_id': '00年代经典歌曲'}, {'type_name': '90年代经典', 'type_id': '90年代经典歌曲'}, {'type_name': '80年代经典', 'type_id': '80年代经典歌曲'}, {'type_name': '70年代经典', 'type_id': '70年代经典歌曲'}, {'type_name': '60年代经典', 'type_id': '60年代经典歌曲'}]

FILTERS = {'演唱会超清': [{'key': 'order', 'name': '排序', 'value': [{'n': '综合排序', 'v': '0'}, {'n': '最多点击', 'v': 'click'}, {'n': '最新发布', 'v': 'pubdate'}, {'n': '最多弹幕', 'v': 'dm'}, {'n': '最多收藏', 'v': 'stow'}]}, {'key': 'tid', 'name': '分类', 'value': [{'n': '全部', 'v': '演唱会超清'}, {'n': 'A阿杜', 'v': '阿杜演唱会超清'}, {'n': 'A阿黛尔', 'v': '阿黛尔演唱会超清'}, {'n': 'BBeyond', 'v': 'Beyond演唱会超清'}, {'n': 'BBy2', 'v': 'By2演唱会超清'}, {'n': 'BBIGBANG', 'v': 'BIGBANG演唱会超清'}, {'n': 'B布兰妮', 'v': '布兰妮演唱会超清'}, {'n': 'B坂井泉水', 'v': '坂井泉水演唱会超清'}, {'n': 'C陈奕迅', 'v': '陈奕迅演唱会超清'}, {'n': 'C蔡依林', 'v': '蔡依林演唱会超清'}, {'n': 'C初音未来', 'v': '初音未来演唱会超清'}, {'n': 'C蔡健雅', 'v': '蔡健雅演唱会超清'}, {'n': 'C陈小春', 'v': '陈小春演唱会超清'}, {'n': 'C草蜢', 'v': '草蜢演唱会超清'}, {'n': 'C陈慧娴', 'v': '陈慧娴演唱会超清'}, {'n': 'C崔健', 'v': '崔健演唱会超清'}, {'n': 'C仓木麻衣', 'v': '仓木麻衣演唱会超清'}, {'n': 'D戴荃', 'v': '戴荃演唱会超清'}, {'n': 'D动力火车', 'v': '动力火车演唱会超清'}, {'n': 'D邓丽君', 'v': '邓丽君演唱会超清'}, {'n': 'D丁当', 'v': '丁当演唱会超清'}, {'n': 'D刀郎', 'v': '刀郎演唱会超清'}, {'n': 'D邓紫棋', 'v': '邓紫棋演唱会超清'}, {'n': 'D戴佩妮', 'v': '戴佩妮演唱会超清'}, {'n': 'D邓丽君', 'v': '邓丽君演唱会超清'}, {'n': 'F飞儿乐队', 'v': '飞儿乐队演唱会超清'}, {'n': 'F费玉清', 'v': '费玉清演唱会超清'}, {'n': 'F费翔', 'v': '费翔演唱会超清'}, {'n': 'F方大同', 'v': '方大同演唱会超清'}, {'n': 'F房东的猫', 'v': '房东的猫演唱会超清'}, {'n': 'F凤飞飞', 'v': '凤飞飞演唱会超清'}, {'n': 'F凤凰传奇', 'v': '凤凰传奇演唱会超清'}, {'n': 'G郭采洁', 'v': '郭采洁演唱会超清'}, {'n': 'G光良', 'v': '光良演唱会超清'}, {'n': 'G郭静', 'v': '郭静演唱会超清'}, {'n': 'G郭富城', 'v': '郭富城演唱会超清'}, {'n': 'H胡彦斌', 'v': '胡彦斌演唱会超清'}, {'n': 'H胡夏', 'v': '胡夏演唱会超清'}, {'n': 'H韩红', 'v': '韩红演唱会超清'}, {'n': 'H黄品源', 'v': '黄品源演唱会超清'}, {'n': 'H黄小琥', 'v': '黄小琥演唱会超清'}, {'n': 'H花儿乐队', 'v': '花儿乐队演唱会超清'}, {'n': 'H黄家强', 'v': '黄家强演唱会超清'}, {'n': 'H后街男孩', 'v': '后街男孩演唱会超清'}, {'n': 'J经典老歌', 'v': '经典老歌演唱会超清'}, {'n': 'J贾斯丁比伯', 'v': '贾斯丁比伯演唱会超清'}, {'n': 'J金池', 'v': '金池演唱会超清'}, {'n': 'J金志文', 'v': '金志文演唱会超清'}, {'n': 'J焦迈奇', 'v': '焦迈奇演唱会超清'}, {'n': 'K筷子兄弟', 'v': '筷子兄弟演唱会超清'}, {'n': 'L李玟', 'v': '李玟演唱会超清'}, {'n': 'L林忆莲', 'v': '林忆莲演唱会超清'}, {'n': 'L李克勤', 'v': '李克勤演唱会超清'}, {'n': 'L刘宪华', 'v': '刘宪华演唱会超清'}, {'n': 'L李圣杰', 'v': '李圣杰演唱会超清'}, {'n': 'L林宥嘉', 'v': '林宥嘉演唱会超清'}, {'n': 'L梁静茹', 'v': '梁静茹演唱会超清'}, {'n': 'L李健', 'v': '李健演唱会超清'}, {'n': 'L林俊杰', 'v': '林俊杰演唱会超清'}, {'n': 'L李玉刚', 'v': '李玉刚演唱会超清'}, {'n': 'L林志炫', 'v': '林志炫演唱会超清'}, {'n': 'L李荣浩', 'v': '李荣浩演唱会超清'}, {'n': 'L李宇春', 'v': '李宇春演唱会超清'}, {'n': 'L洛天依', 'v': '洛天依演唱会超清'}, {'n': 'L林子祥', 'v': '林子祥演唱会超清'}, {'n': 'L李宗盛', 'v': '李宗盛演唱会超清'}, {'n': 'L黎明', 'v': '黎明演唱会超清'}, {'n': 'L刘德华', 'v': '刘德华演唱会超清'}, {'n': 'L罗大佑', 'v': '罗大佑演唱会超清'}, {'n': 'L林肯公园', 'v': '林肯公园演唱会超清'}, {'n': 'LLadyGaga', 'v': 'LadyGaga演唱会超清'}, {'n': 'L旅行团乐队', 'v': '旅行团乐队演唱会超清'}, {'n': 'M莫文蔚', 'v': '莫文蔚演唱会超清'}, {'n': 'M毛不易', 'v': '毛不易演唱会超清'}, {'n': 'M梅艳芳', 'v': '梅艳芳演唱会超清'}, {'n': 'M迈克尔杰克逊', 'v': '迈克尔杰克逊演唱会超清'}, {'n': 'N南拳妈妈', 'v': '南拳妈妈演唱会超清'}, {'n': 'P朴树', 'v': '朴树演唱会超清'}, {'n': 'Q齐秦', 'v': '齐秦演唱会超清'}, {'n': 'Q青鸟飞鱼', 'v': '青鸟飞鱼演唱会超清'}, {'n': 'R容祖儿', 'v': '容祖儿演唱会超清'}, {'n': 'R任贤齐', 'v': '任贤齐演唱会超清'}, {'n': 'S水木年华', 'v': '水木年华演唱会超清'}, {'n': 'S孙燕姿', 'v': '孙燕姿演唱会超清'}, {'n': 'S苏打绿', 'v': '苏打绿演唱会超清'}, {'n': 'SSHE', 'v': 'SHE演唱会超清'}, {'n': 'S孙楠', 'v': '孙楠演唱会超清'}, {'n': 'T陶喆', 'v': '陶喆演唱会超清'}, {'n': 'T谭咏麟', 'v': '谭咏麟演唱会超清'}, {'n': 'T田馥甄', 'v': '田馥甄演唱会超清'}, {'n': 'T谭维维', 'v': '谭维维演唱会超清'}, {'n': 'T逃跑计划', 'v': '逃跑计划演唱会超清'}, {'n': 'T田震', 'v': '田震演唱会超清'}, {'n': 'T谭晶', 'v': '谭晶演唱会超清'}, {'n': 'T屠洪刚', 'v': '屠洪刚演唱会超清'}, {'n': 'T泰勒·斯威夫特', 'v': '泰勒·斯威夫特演唱会超清'}, {'n': 'W王力宏', 'v': '王力宏演唱会超清'}, {'n': 'W王杰', 'v': '王杰演唱会超清'}, {'n': 'W吴克群', 'v': '吴克群演唱会超清'}, {'n': 'W王心凌', 'v': '王心凌演唱会超清'}, {'n': 'W王靖雯', 'v': '好声音王靖雯演唱会超清'}, {'n': 'W汪峰', 'v': '汪峰演唱会超清'}, {'n': 'W伍佰', 'v': '伍佰演唱会超清'}, {'n': 'W王菲', 'v': '王菲演唱会超清'}, {'n': 'W五月天', 'v': '五月天演唱会超清'}, {'n': 'W汪苏泷', 'v': '汪苏泷演唱会超清'}, {'n': 'X徐佳莹', 'v': '徐佳莹演唱会超清'}, {'n': 'X弦子', 'v': '弦子演唱会超清'}, {'n': 'X萧亚轩', 'v': '萧亚轩演唱会超清'}, {'n': 'X许巍', 'v': '许巍演唱会超清'}, {'n': 'X薛之谦', 'v': '薛之谦演唱会超清'}, {'n': 'X许嵩', 'v': '许嵩演唱会超清'}, {'n': 'X小虎队', 'v': '小虎队演唱会超清'}, {'n': 'X萧敬腾', 'v': '萧敬腾演唱会超清'}, {'n': 'X谢霆锋', 'v': '谢霆锋演唱会超清'}, {'n': 'X徐小凤', 'v': '徐小凤演唱会超清'}, {'n': 'X信乐队', 'v': '信乐队演唱会超清'}, {'n': 'Y夜愿乐队', 'v': '夜愿乐队演唱会超清'}, {'n': 'Y羽泉', 'v': '羽泉演唱会超清'}, {'n': 'Y郁可唯', 'v': '郁可唯演唱会超清'}, {'n': 'Y叶倩文', 'v': '叶倩文演唱会超清'}, {'n': 'Y杨坤', 'v': '杨坤演唱会超清'}, {'n': 'Y庾澄庆', 'v': '庾澄庆演唱会超清'}, {'n': 'Y尤长靖', 'v': '尤长靖演唱会超清'}, {'n': 'Y易烊千玺', 'v': '易烊千玺演唱会超清'}, {'n': 'Y袁娅维', 'v': '袁娅维演唱会超清'}, {'n': 'Y杨丞琳', 'v': '杨丞琳演唱会超清'}, {'n': 'Y杨千嬅', 'v': '杨千嬅演唱会超清'}, {'n': 'Y杨宗纬', 'v': '杨宗纬演唱会超清'}, {'n': 'Z郑秀文', 'v': '郑秀文演唱会超清'}, {'n': 'Z周杰伦', 'v': '周杰伦演唱会超清'}, {'n': 'Z张学友', 'v': '张学友演唱会超清'}, {'n': 'Z张信哲', 'v': '张信哲演唱会超清'}, {'n': 'Z张宇', 'v': '张宇演唱会超清'}, {'n': 'Z周华健', 'v': '周华健演唱会超清'}, {'n': 'Z张韶涵', 'v': '张韶涵演唱会超清'}, {'n': 'Z周深', 'v': '周深演唱会超清'}, {'n': 'Z纵贯线', 'v': '纵贯线演唱会超清'}, {'n': 'Z赵雷', 'v': '赵雷演唱会超清'}, {'n': 'Z周传雄', 'v': '周传雄演唱会超清'}, {'n': 'Z张国荣', 'v': '张国荣演唱会超清'}, {'n': 'Z周慧敏', 'v': '周慧敏演唱会超清'}, {'n': 'Z张惠妹', 'v': '张惠妹演唱会超清'}, {'n': 'Z周笔畅', 'v': '周笔畅演唱会超清'}, {'n': 'Z郑中基', 'v': '郑中基演唱会超清'}, {'n': 'Z张艺兴', 'v': '张艺兴演唱会超清'}, {'n': 'Z张震岳', 'v': '张震岳演唱会超清'}, {'n': 'Z张雨生', 'v': '张雨生演唱会超清'}, {'n': 'Z郑智化', 'v': '郑智化演唱会超清'}, {'n': 'Z卓依婷', 'v': '卓依婷演唱会超清'}, {'n': 'Z中岛美雪', 'v': '中岛美雪演唱会超清'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], '粤语歌曲超清': [{'key': 'tid', 'name': '分类', 'value': [{'n': '全部', 'v': '歌曲'}, {'n': '男歌手', 'v': '粤语热歌男歌手'}, {'n': '女歌手', 'v': '粤语热歌女歌手'}]}, {'key': 'tid', 'name': '年代', 'value': [{'n': '全部', 'v': '歌曲'}, {'n': '20245年', 'v': '2025年粤语热歌'}, {'n': '2024年', 'v': '2024年粤语热歌'}, {'n': '2023年', 'v': '2023年粤语热歌'}, {'n': '2022年', 'v': '2022年粤语热歌'}, {'n': '2021年', 'v': '2021年粤语热歌'}, {'n': '2020年', 'v': '2020年粤语热歌'}, {'n': '2019年', 'v': '2019年粤语热歌'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], 'KTV热门歌曲': [{'key': 'tid', 'name': '分类', 'value': [{'n': '全部', 'v': '歌曲'}, {'n': '男歌手', 'v': 'KTV男歌手MV'}, {'n': '女歌手', 'v': 'KTV男歌手MV'}]}, {'key': 'tid', 'name': '年代', 'value': [{'n': '全部', 'v': '歌曲'}, {'n': '2025年', 'v': '2025年KTV热门MV'}, {'n': '2024年', 'v': '2024年KTV热门MV'}, {'n': '2023年', 'v': '2023年KTV热门MV'}, {'n': '2022年', 'v': '2022年KTV热门MV'}, {'n': '2021年', 'v': '2021年KTV热门MV'}, {'n': '2020年', 'v': '2020年KTV热门MV'}, {'n': '2019年', 'v': '2019年KTV热门MV'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], '民谣歌曲超清': [{'key': 'order', 'name': '排序', 'value': [{'n': '综合排序', 'v': '0'}, {'n': '最多点击', 'v': 'click'}, {'n': '最新发布', 'v': 'pubdate'}, {'n': '最多弹幕', 'v': 'dm'}, {'n': '最多收藏', 'v': 'stow'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], '经典老歌超清': [{'key': 'tid', 'name': '分类', 'value': [{'n': '全部', 'v': '歌曲'}, {'n': '男歌手', 'v': '男歌手经典老歌'}, {'n': '女歌手', 'v': '女歌手经典老歌'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], '网红翻唱歌曲超清': [{'key': 'tid', 'name': '分类', 'value': [{'n': '全部', 'v': '歌曲'}, {'n': '男歌手', 'v': '男歌手网红翻唱MV'}, {'n': '女歌手', 'v': '女歌手网红翻唱MV'}]}, {'key': 'tid', 'name': '年代', 'value': [{'n': '全部', 'v': '歌曲'}, {'n': '2025年', 'v': '2025年网红翻唱MV'}, {'n': '2024年', 'v': '2024年网红翻唱MV'}, {'n': '2023年', 'v': '2023年网红翻唱MV'}, {'n': '2022年', 'v': '2022年网红翻唱MV'}, {'n': '2021年', 'v': '2021年网红翻唱MV'}, {'n': '2020年', 'v': '2020年网红翻唱MV'}, {'n': '2019年', 'v': '2019年网红翻唱MV'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], 'DJ歌曲超清': [{'key': 'order', 'name': '排序', 'value': [{'n': '综合排序', 'v': '0'}, {'n': '最多点击', 'v': 'click'}, {'n': '最新发布', 'v': 'pubdate'}, {'n': '最多弹幕', 'v': 'dm'}, {'n': '最多收藏', 'v': 'stow'}]}, {'key': 'tid', 'name': '分类1', 'value': [{'n': '全部', 'v': 'Dj歌曲'}, {'n': 'DJ合集', 'v': 'DJ合集'}, {'n': '情歌DJ', 'v': '情歌DJ'}, {'n': '电音DJ', 'v': '电音DJ'}, {'n': '劲爆DJ音乐', 'v': '劲爆DJ音乐'}, {'n': '嘻哈舞曲DJ', 'v': '嘻哈舞曲DJ'}, {'n': '流行舞曲DJ', 'v': '流行舞曲DJ'}, {'n': '民族舞曲DJ', 'v': '民族舞曲DJ'}, {'n': '车载舞曲DJ', 'v': '车载舞曲DJ'}, {'n': '抖音热歌DJ', 'v': '抖音热歌DJ'}]}, {'key': 'tid', 'name': '年代', 'value': [{'n': '全部', 'v': '歌曲'}, {'n': '2025年', 'v': '2025年DJ音乐'}, {'n': '2024年', 'v': '2024年DJ音乐'}, {'n': '2023年', 'v': '2023年DJ音乐'}, {'n': '2022年', 'v': '2022年DJ音乐'}, {'n': '2021年', 'v': '2021年DJ音乐'}, {'n': '2020年', 'v': '2020年DJ音乐'}, {'n': '2019年', 'v': '2019年DJ音乐'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], '网易云经典歌曲': [{'key': 'order', 'name': '排序', 'value': [{'n': '综合排序', 'v': '0'}, {'n': '最多点击', 'v': 'click'}, {'n': '最新发布', 'v': 'pubdate'}, {'n': '最多弹幕', 'v': 'dm'}, {'n': '最多收藏', 'v': 'stow'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], '滚石歌曲': [{'key': 'tid', 'name': '分类', 'value': [{'n': '全部', 'v': '歌曲'}, {'n': '男歌手', 'v': '男歌手滚石MV'}, {'n': '女歌手', 'v': '女歌手滚石MV'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], '古风歌曲': [{'key': 'tid', 'name': '分类', 'value': [{'n': '全部', 'v': '歌曲'}, {'n': '男歌手', 'v': '男歌手古风MV'}, {'n': '女歌手', 'v': '女歌手古风MV'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], '闽南语歌曲': [{'key': 'tid', 'name': '分类', 'value': [{'n': '全部', 'v': '歌曲'}, {'n': '男歌手', 'v': '男歌手闽南语MV'}, {'n': '女歌手', 'v': '女歌手闽南语MV'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], '电子琴纯音乐': [{'key': 'order', 'name': '排序', 'value': [{'n': '综合排序', 'v': '0'}, {'n': '最多点击', 'v': 'click'}, {'n': '最新发布', 'v': 'pubdate'}, {'n': '最多弹幕', 'v': 'dm'}, {'n': '最多收藏', 'v': 'stow'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], '抖音DJ': [{'key': 'order', 'name': '排序', 'value': [{'n': '综合排序', 'v': '0'}, {'n': '最多点击', 'v': 'click'}, {'n': '最新发布', 'v': 'pubdate'}, {'n': '最多弹幕', 'v': 'dm'}, {'n': '最多收藏', 'v': 'stow'}]}, {'key': 'tid', 'name': '年代', 'value': [{'n': '全部', 'v': '歌曲'}, {'n': '2025年', 'v': '2025年抖音热歌'}, {'n': '2024年', 'v': '2024年抖音热歌'}, {'n': '2023年', 'v': '2023年抖音热歌'}, {'n': '2022年', 'v': '2022年抖音热歌'}, {'n': '2021年', 'v': '2021年抖音热歌'}, {'n': '2020年', 'v': '2020年抖音热歌'}, {'n': '2019年', 'v': '2019年抖音热歌'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], '无损音乐': [{'key': 'tid', 'name': '分类', 'value': [{'n': '全部', 'v': '歌曲'}, {'n': '男歌手', 'v': '男声无损音乐'}, {'n': '女歌手', 'v': '女声无损音乐'}, {'n': '儿童歌手', 'v': '童声无损音乐'}, {'n': 'DJ', 'v': 'DJ无损音乐'}, {'n': '轻音乐', 'v': '轻音乐无损音乐'}, {'n': '钢琴曲', 'v': '钢琴曲无损音乐'}, {'n': '萨克斯', 'v': '萨克斯无损音乐'}, {'n': '小提琴', 'v': '小提琴无损音乐'}, {'n': '摇滚', 'v': '摇滚无损音乐'}, {'n': '环绕', 'v': '环绕无损音乐'}]}, {'key': 'tid', 'name': '年代', 'value': [{'n': '全部', 'v': '歌曲'}, {'n': '2025年', 'v': '2025年DJ音乐'}, {'n': '2024年', 'v': '2024年DJ音乐'}, {'n': '2023年', 'v': '2023年DJ音乐'}, {'n': '2022年', 'v': '2022年DJ音乐'}, {'n': '2021年', 'v': '2021年DJ音乐'}, {'n': '2020年', 'v': '2020年DJ音乐'}, {'n': '2019年', 'v': '2019年DJ音乐'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], '时光音乐会MV': [{'key': 'tid', 'name': '年代', 'value': [{'n': '全部', 'v': '歌曲'}, {'n': '2025年', 'v': '2025年时光音乐会MV'}, {'n': '2024年', 'v': '2024年时光音乐会MV'}, {'n': '2023年', 'v': '2023年时光音乐会MV'}, {'n': '2022年', 'v': '2022年时光音乐会MV'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], '2026年热门歌曲': [{'key': 'order', 'name': '排序', 'value': [{'n': '综合排序', 'v': '0'}, {'n': '最多点击', 'v': 'click'}, {'n': '最新发布', 'v': 'pubdate'}, {'n': '最多弹幕', 'v': 'dm'}, {'n': '最多收藏', 'v': 'stow'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], '2025年热门歌曲': [{'key': 'order', 'name': '排序', 'value': [{'n': '综合排序', 'v': '0'}, {'n': '最多点击', 'v': 'click'}, {'n': '最新发布', 'v': 'pubdate'}, {'n': '最多弹幕', 'v': 'dm'}, {'n': '最多收藏', 'v': 'stow'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], '2024年热门歌曲': [{'key': 'order', 'name': '排序', 'value': [{'n': '综合排序', 'v': '0'}, {'n': '最多点击', 'v': 'click'}, {'n': '最新发布', 'v': 'pubdate'}, {'n': '最多弹幕', 'v': 'dm'}, {'n': '最多收藏', 'v': 'stow'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], '00年代经典歌曲': [{'key': 'order', 'name': '排序', 'value': [{'n': '综合排序', 'v': '0'}, {'n': '最多点击', 'v': 'click'}, {'n': '最新发布', 'v': 'pubdate'}, {'n': '最多弹幕', 'v': 'dm'}, {'n': '最多收藏', 'v': 'stow'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], '90年代经典歌曲': [{'key': 'order', 'name': '排序', 'value': [{'n': '综合排序', 'v': '0'}, {'n': '最多点击', 'v': 'click'}, {'n': '最新发布', 'v': 'pubdate'}, {'n': '最多弹幕', 'v': 'dm'}, {'n': '最多收藏', 'v': 'stow'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], '80年代经典歌曲': [{'key': 'order', 'name': '排序', 'value': [{'n': '综合排序', 'v': '0'}, {'n': '最多点击', 'v': 'click'}, {'n': '最新发布', 'v': 'pubdate'}, {'n': '最多弹幕', 'v': 'dm'}, {'n': '最多收藏', 'v': 'stow'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], '70年代经典歌曲': [{'key': 'order', 'name': '排序', 'value': [{'n': '综合排序', 'v': '0'}, {'n': '最多点击', 'v': 'click'}, {'n': '最新发布', 'v': 'pubdate'}, {'n': '最多弹幕', 'v': 'dm'}, {'n': '最多收藏', 'v': 'stow'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}], '60年代经典歌曲': [{'key': 'order', 'name': '排序', 'value': [{'n': '综合排序', 'v': '0'}, {'n': '最多点击', 'v': 'click'}, {'n': '最新发布', 'v': 'pubdate'}, {'n': '最多弹幕', 'v': 'dm'}, {'n': '最多收藏', 'v': 'stow'}]}, {'key': 'duration', 'name': '时长', 'value': [{'n': '全部', 'v': '0'}, {'n': '60分钟以上', 'v': '4'}, {'n': '30~60分钟', 'v': '3'}, {'n': '10~30分钟', 'v': '2'}, {'n': '10分钟以下', 'v': '1'}]}]}

MIXIN_KEY_ENC_TAB = [46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52]



# ============================== 基础工具 ==============================
def _ret(obj):
    """统一出口：OK影视 的 py 外壳(app.py) 自己会 json.dumps，
    所以这里必须返回原生 dict / list；返回字符串会被二次编码，解析必失败。"""
    return obj


def _ctx():
    try:
        c = ssl._create_unverified_context()
        return c
    except Exception:
        return None


def _headers():
    h = {"User-Agent": UA,
         "Referer": "https://www.bilibili.com/",
         "Origin": "https://www.bilibili.com",
         "Accept": "application/json, text/plain, */*",
         "Accept-Language": "zh-CN,zh;q=0.9"}
    ck = BUVID
    if SESSDATA:
        ck = ck + "; SESSDATA=" + SESSDATA
    h["Cookie"] = ck
    return h


def _http_json(url, params=None, timeout=12):
    """GET + JSON。优先 requests，没有或失败就 urllib（忽略证书校验，安卓证书链常不全）。"""
    try:
        if params:
            url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
        if _REQ is not None:
            try:
                r = _REQ.get(url, headers=_headers(), timeout=timeout, verify=False)
                if r is not None and r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        req = urllib.request.Request(url, headers=_headers())
        ctx = _ctx()
        if ctx:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                return json.loads(resp.read().decode("utf-8", "ignore"))
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", "ignore"))
    except Exception:
        return None


_WBI_KEYS = None


def _get_wbi_keys():
    global _WBI_KEYS
    if _WBI_KEYS:
        return _WBI_KEYS
    try:
        r = _http_json("https://api.bilibili.com/x/web-interface/nav")
        img = r["data"]["wbi_img"]["img_url"].rsplit("/", 1)[-1].split(".")[0]
        sub = r["data"]["wbi_img"]["sub_url"].rsplit("/", 1)[-1].split(".")[0]
        raw = img + sub
        _WBI_KEYS = "".join(raw[i] for i in MIXIN_KEY_ENC_TAB)[:32]
    except Exception:
        _WBI_KEYS = ""
    return _WBI_KEYS


def _wbi_sign(params):
    mixin = _get_wbi_keys()
    if not mixin:
        return params
    p = dict(params)
    p["wts"] = int(time.time())
    q = urllib.parse.urlencode(sorted(p.items()))
    p["w_rid"] = hashlib.md5((q + mixin).encode("utf-8")).hexdigest()
    return p


def _clean_title(s):
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'")
    return s.strip()


def _fmt_count(v):
    try:
        v = int(v)
    except Exception:
        return ""
    if v >= 100000000:
        return "%.1f亿" % (v / 100000000.0)
    if v >= 10000:
        return "%.1f万" % (v / 10000.0)
    return str(v)


def _pic(url):
    if not url:
        return ""
    if url.startswith("//"):
        url = "https:" + url
    if PIC_PROXY:
        return PIC_PROXY + urllib.parse.quote(url, safe="")
    return url


# ============================== B站接口 ==============================
def _norm(items):
    """把 search/type 或 search/all/v2 的视频条目统一成同一种结构。"""
    out = []
    for it in items or []:
        if not it or not it.get("bvid"):
            continue
        out.append({
            "vod_id": it.get("bvid"),
            "vod_name": _clean_title(it.get("title", "")),
            "vod_pic": _pic(it.get("pic", "")),
            "vod_remarks": it.get("duration", "") or "",
            "vod_actor": it.get("author", "") or "",
            "vod_content": it.get("description", "") or "",
        })
    return out


def _search_once(endpoint, keyword, pg, order, duration, signed):
    if endpoint.endswith("search/all/v2"):
        params = {"keyword": keyword, "page": pg}
        r = _http_json(endpoint, params=params)
        if not r or r.get("code") != 0:
            return [], 1
        data = r.get("data") or {}
        blocks = data.get("result") or []
        vids = []
        for b in blocks:
            if isinstance(b, dict) and b.get("result_type") == "video":
                vids = b.get("data") or []
                break
        return _norm(vids), int(data.get("numPages") or 1)
    params = {"search_type": "video", "keyword": keyword, "page": pg, "page_size": 20}
    if order and order != "0":
        params["order"] = {"0": "totalrank", "click": "click", "pubdate": "pubdate",
                           "dm": "dm", "stow": "stow"}.get(order, "totalrank")
    if duration and duration != "0":
        params["duration"] = duration
    p = _wbi_sign(params) if signed else params
    r = _http_json(endpoint, params=p)
    if not r or r.get("code") != 0:
        return [], 1
    data = r.get("data") or {}
    return _norm(data.get("result") or []), int(data.get("numPages") or 1)


def _bili_search(keyword, pg=1, order="0", duration="0"):
    """三接口轮询 + 两轮退避。B站对同 IP 有频控，空结果不代表真没有。"""
    eps = [("https://api.bilibili.com/x/web-interface/search/type", True),
           ("https://api.bilibili.com/x/web-interface/search/all/v2", False),
           ("https://api.bilibili.com/x/web-interface/search/type", False)]
    best = ([], 1)
    for rnd in range(2):
        for ep, signed in eps:
            try:
                vlist, pages = _search_once(ep, keyword, pg, order, duration, signed)
            except Exception:
                vlist, pages = [], 1
            if vlist:
                return vlist, max(pages, 1)
            time.sleep(0.6 + random.random() * 0.4)
        time.sleep(1.0)
    return best


def _ranking():
    """音乐区(rid=3)排行榜：搜索被风控时的兜底，保证分类页有内容。"""
    for rid in ("3", "1", "4"):
        r = _http_json("https://api.bilibili.com/x/web-interface/ranking/v2",
                       params={"rid": rid, "type": "all"})
        if r and r.get("code") == 0:
            lst = ((r.get("data") or {}).get("list")) or []
            if lst:
                items = []
                for it in lst:
                    if not it.get("bvid"):
                        continue
                    items.append({
                        "vod_id": it.get("bvid"),
                        "vod_name": _clean_title(it.get("title", "")),
                        "vod_pic": _pic(it.get("pic", "")),
                        "vod_remarks": "热门",
                        "vod_actor": (it.get("owner") or {}).get("name", ""),
                        "vod_content": it.get("desc", "") or "",
                    })
                return items
    return []


def _view(bvid, p=1):
    params = {"bvid": bvid}
    if p and p > 1:
        params["p"] = p
    r = _http_json("https://api.bilibili.com/x/web-interface/view", params=params)
    if r and r.get("code") == 0 and r.get("data"):
        return r["data"]
    # 详情被限流时，至少拿到 cid，播放还能走
    r2 = _http_json("https://api.bilibili.com/x/player/pagelist", params={"bvid": bvid})
    if r2 and r2.get("code") == 0 and r2.get("data"):
        pages = r2["data"]
        idx = min(max(p - 1, 0), len(pages) - 1)
        return {"bvid": bvid, "cid": pages[idx].get("cid", 0), "pages": pages,
                "title": pages[idx].get("part", ""), "pic": ""}
    return {}


def _playurl(bvid, cid):
    """逐级降清晰度，取 durl 的 MP4 直链（fnval=1 只返回 MP4，兼容所有播放器）。"""
    for qn in ([80, 64, 32, 16] if SESSDATA else [64, 32, 16]):
        r = _http_json("https://api.bilibili.com/x/player/playurl",
                       params={"bvid": bvid, "cid": cid, "qn": qn,
                               "fnval": 1, "fnver": 0, "fourk": 1})
        if not r or r.get("code") != 0:
            continue
        data = r.get("data") or {}
        durl = data.get("durl") or []
        if durl and durl[0].get("url"):
            return durl[0]["url"], qn
        # 部分视频只给 dash，退 fnval=0
        r2 = _http_json("https://api.bilibili.com/x/player/playurl",
                        params={"bvid": bvid, "cid": cid, "qn": qn,
                                "fnval": 0, "fnver": 0, "fourk": 1})
        durl2 = (((r2 or {}).get("data") or {}).get("durl")) or []
        if durl2 and durl2[0].get("url"):
            return durl2[0]["url"], qn
    return "", 0


# ============================== Spider ==============================
def _as_obj(v):
    """把 OK影视 传来的 JSON 字符串 / dict / list 统一还原成 Python 对象。"""
    if isinstance(v, (dict, list)):
        return v
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return None
        try:
            return json.loads(s)
        except Exception:
            return None
    return None


class Spider:

    def getName(self):
        return "哔哩哔哩-音乐演唱会"

    def init(self, *args):
        global SESSDATA
        for a in args:
            obj = _as_obj(a)
            if isinstance(obj, dict):
                ck = obj.get("cookies") or obj.get("cookie") or ""
                m = re.search(r"SESSDATA=([^;]+)", str(ck))
                if m:
                    SESSDATA = m.group(1).strip()
                if obj.get("sessdata"):
                    SESSDATA = str(obj["sessdata"]).strip()
        return ""

    def homeContent(self, *args):
        return _ret({"class": CLASSES, "filters": FILTERS, "list": []})

    def homeVideoContent(self, *args):
        try:
            return _ret({"list": _ranking()})
        except Exception:
            return _ret({"list": []})

    def categoryContent(self, tid, pg, *args):
        try:
            pg = str(pg or "1")
            ext = {}
            for a in args:
                obj = _as_obj(a)
                if isinstance(obj, dict):
                    ext = obj
                    break
            keyword = str(ext.get("tid") or tid or "").strip()
            order = str(ext.get("order") or "0")
            duration = str(ext.get("duration") or "0")
            vlist, pages = _bili_search(keyword, pg, order, duration)
            if not vlist and pg in ("1", 1):
                # 关键词变体重试：B站对某些词会偶发 0 条，换写法常常立刻有 20 条
                for alt in (keyword + "超清", keyword.replace("超清", "").strip(), keyword + " MV"):
                    if not alt or alt == keyword:
                        continue
                    vlist, pages = _bili_search(alt, pg, order, duration)
                    if vlist:
                        break
            if not vlist and pg in ("1", 1):
                vlist = _ranking()          # 仍为空则用音乐区排行榜兜底，别让分类空白
            if not vlist:
                vlist = []
            return _ret({"list": vlist, "page": pg, "pagecount": max(pages, 1),
                           "limit": 20, "total": len(vlist)})
        except Exception:
            return _ret({"list": [], "page": "1", "pagecount": 1})

    def detailContent(self, ids):
        try:
            arr = _as_obj(ids)
            if isinstance(arr, list):
                vid = str(arr[0]) if arr else ""
            elif isinstance(arr, dict):
                vid = str(arr.get("id") or arr.get("vod_id") or "")
            else:
                vid = str(ids or "")
            vid = vid.strip().strip('"').strip("'")
            bvid = vid.split("?")[0].split("$")[0].strip()
            if not bvid:
                return _ret({"list": []})
            info = _view(bvid, 1)
            pages = info.get("pages") or []
            if len(pages) <= 1:
                play = "正片$" + bvid
            else:
                eps = []
                for i, p in enumerate(pages, 1):
                    name = (p.get("part") or "").strip() or ("第%d集" % i)
                    eps.append("%s$%s?p=%d" % (name, bvid, i))
                play = "#".join(eps)
            stat = info.get("stat") or {}
            remark = ""
            if stat:
                remark = "播放:" + _fmt_count(stat.get("view", 0)) + " 弹幕:" + _fmt_count(stat.get("danmaku", 0))
            year = ""
            try:
                if info.get("pubdate"):
                    year = str(datetime.fromtimestamp(info["pubdate"]).year)
            except Exception:
                year = ""
            vod = {
                "vod_id": bvid,
                "vod_name": info.get("title", "") or bvid,
                "vod_pic": _pic(info.get("pic", "")),
                "type_name": "音乐/演唱会",
                "vod_year": year,
                "vod_area": "哔哩哔哩",
                "vod_remarks": remark,
                "vod_actor": (info.get("owner") or {}).get("name", ""),
                "vod_director": "",
                "vod_content": info.get("desc", "") or "",
                "vod_play_from": "哔哩哔哩",
                "vod_play_url": play,
            }
            return _ret({"list": [vod]})
        except Exception:
            return _ret({"list": []})

    def searchContent(self, *args):
        try:
            key = ""
            for a in args:
                if isinstance(a, str) and a.strip():
                    key = a.strip()
                    break
            pg = "1"
            if len(args) >= 3 and isinstance(args[2], str) and args[2].strip().isdigit():
                pg = args[2].strip()
            vlist, pages = _bili_search(key, pg, "totalrank", "0")
            return _ret({"list": vlist, "page": pg, "pagecount": max(pages, 1)})
        except Exception:
            return _ret({"list": [], "page": "1", "pagecount": 1})

    def playerContent(self, *args):
        """OK影视: (flag, id, vipFlags)；影视仓: (id, flag, vipFlags)。自动识别哪一个是 BV 号。"""
        bvid, p = "", 1
        for a in args:
            obj = _as_obj(a)
            cand = ""
            if isinstance(obj, list):
                cand = str(obj[0]) if obj else ""
            elif isinstance(a, str):
                cand = a
            m = re.search(r"(BV[0-9A-Za-z]{8,})", cand)
            if m:
                bvid = m.group(1)
                mp = re.search(r"[?&]p=(\d+)", cand)
                if mp:
                    p = int(mp.group(1))
                break
        header = {"User-Agent": UA, "Referer": "https://www.bilibili.com/"}
        if not bvid:
            return _ret({"parse": 0, "url": "", "header": header})
        try:
            info = _view(bvid, p)
            cid = info.get("cid", 0)
            pages = info.get("pages") or []
            if not cid and pages:
                cid = pages[min(p - 1, len(pages) - 1)].get("cid", 0)
            if cid:
                url, qn = _playurl(bvid, cid)
                if url:
                    return _ret({"parse": 0, "url": url, "header": header, "format": "mp4"})
        except Exception:
            pass
        return _ret({"parse": 0,
                       "url": "https://www.bilibili.com/video/" + bvid + ("?p=%d" % p if p > 1 else ""),
                       "header": header})

    def manualVideoCheck(self, *args):
        return False

    def localProxy(self, param):
        return None
