#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import json

import time
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
import ddddocr
import urllib3
import re
import hashlib
from Crypto.Cipher import AES
from binascii import b2a_hex
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms
import zlib
import base64


urllib3.util.timeout.Timeout._validate_timeout = lambda *args: 5 if args[2] != 'total' else None

Tag = "bdys01"
Tag_name = "哔滴影视"
siteUrl = "https://www.bdys01.com"


def getHeaders(url):
    headers = {}
    if url:
        headers.setdefault("Referer", url)
    headers.setdefault("Accept-Encoding", "gzip, deflate, br")
    headers.setdefault("DNT", "1")
    headers.setdefault("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0")
    headers.setdefault("Accept", "*/*")
    headers.setdefault("Accept-Language", "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2")
    return headers


def cacu(code):
    if "=" in code:
        code = code[:code.find("=")]
    elif code[-1] == "2" or code[-1] == "7":
        code = code[:-1]
        if code[-1] == "4" or code[-1] == "-":
            code = code[:-1]
    code = code.replace("I", "1")
    code = code.replace("l", "1")
    if code.isdigit():
        if len(code) > 4:
            code = code[:4]
        return int(code[:2]) - int(code[2:])
    elif "+" in code:
        code = code.split("+")
        return int(code[0]) + int(code[1])
    elif "-" in code:
        code = code.split("-")
        return int(code[0]) - int(code[1])
    elif "x" in code:
        code = code.split("x")
        return int(code[0]) * int(code[1])


def verifyCode(key):
    retry = 5
    while retry:
        try:
            session = requests.session()
            ocr = ddddocr.DdddOcr()
            img = session.get(
                url=f"https://www.bdys01.com/search/verifyCode?t={str(int(round(time.time() * 1000)))}",
                headers=getHeaders(siteUrl)
            ).content
            # with open("verifyCode.jpg", 'wb') as f:
            #     f.write(img)
            code = cacu(ocr.classification(img))
            url = f"{siteUrl}/search/{quote_plus(key)}?code={code}"
            res = session.get(
                url=url,
                headers=getHeaders(url.split("?")[0])
            ).text
            if "/search/verifyCode?t=" not in res:
                return res
            # time.sleep(1)
        except Exception as e:
            print(e)
            if e.__class__.__name__ == 'ConnectTimeout':
                break
        finally:
            retry = retry - 1


def pkcs7_padding(data):
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    return padded_data


def encrypt(text, key):
    cryptor = AES.new(key.encode('utf-8'), AES.MODE_ECB)
    ciphertext = cryptor.encrypt(pkcs7_padding(text.encode('utf-8')))
    return b2a_hex(ciphertext).decode().upper()


def get_lines(path):
    try:
        lines = []
        pid = re.search("pid = (\d*)", requests.get(url=f'{siteUrl}{path}', headers=getHeaders(siteUrl)).text).group(1)
        t = str(int(round(time.time() * 1000)))
        key = hashlib.md5(f"{pid}-{t}".encode(encoding='UTF-8')).hexdigest()[0:16]
        sg = encrypt(f"{pid}-{t}", key)
        play_url = f"{siteUrl}/lines?t={t}&sg={sg}&pid={pid}"
        data = requests.get(url=play_url, headers=getHeaders(play_url)).json()["data"]
        if len(data) == 1:
            play_line = requests.post(
                url=f"{siteUrl}/god/{pid}",
                data={
                    "t": t,
                    "sg": sg,
                    "verifyCode": 666
                },
                headers=getHeaders(siteUrl)
            ).json().get("url", "")
            if not play_line:
                play_line = requests.post(
                    url=f"{siteUrl}/god/{pid}?type=1",
                    data={
                        "t": t,
                        "sg": sg,
                        "verifyCode": 888
                    },
                    headers=getHeaders(siteUrl)
                ).json().get("url", "")
            if "rkey" in play_line:
                realurl = play_line.replace("?rkey", str(int(round(time.time() * 1000))) + ".mp4?ver=6010&rkey")
            elif "ixigua" in play_line:
                realurl = play_line
            else:
                realurl = play_line.replace("http:", "https:") + "/" + str(int(round(time.time() * 1000))) + ".mp4"
            lines.append(realurl)
        else:
            for item in data:
                if item == "m3u8_2" or item == "m3u8":
                    play_lines = data[item].split(",")
                    for line in play_lines:
                        if "mp4" in line:
                            lines.append(line)
                        else:
                            lines.append(line.replace("www.bde4.cc", "www.bdys01.com"))
                elif item == "url3":
                    if "mp4" in data[item]:
                        lines.append(data[item])
                    else:
                        lines.append(data[item])
        return lines
    except Exception as e:
        print(e)
        return []


def add_domain(matched):
    url = "https://vod.bdys.me/" + matched.group(0)
    return url


def searchContent(key, token):
    try:
        res = verifyCode(key)
        searchResult = BeautifulSoup(res, "html.parser")
        videos = []
        lists = searchResult.select("div.row.row-0")
        for vod in lists:
            vod_name = vod.select_one("div.card-body.py-0.pe-1").a["title"]
            if key in vod_name:
                videos.append({
                    "vod_id": f'{Tag}${vod.a["href"].split(".")[0]}',
                    "vod_name": vod_name,
                    "vod_pic": vod.img["src"],
                    "vod_remarks": Tag_name + " " + vod.select_one("div.card-body.py-0.pe-1").a.get_text()
                })
        return videos
    except Exception as e:
        print(e)
    return []


def detailContent(ids, token):
    try:
        id = ids.split("$")[-1]
        url = f"{siteUrl}/{id}.htm"
        doc = BeautifulSoup(requests.get(url=url, headers=getHeaders(siteUrl)).text, "html.parser").select_one(
            "div.container-xl.clear-padding-sm.my-3.py-1")
        # 取基本数据
        sourcediv = doc.select_one("div.card-body")
        module_info_items = sourcediv.select("p")
        director = ""
        actor = ""
        vod_remarks = ""
        type_name = ""
        vod_year = ""
        vod_area = ""
        for item in module_info_items:
            if item.strong:
                if "导演" in item.strong.get_text():
                    director = ",".join(i.get_text() for i in item.select("a"))
                elif "主演" in item.strong.get_text():
                    actor = ",".join(i.get_text() for i in item.select("a"))
                elif "摘要" in item.strong.get_text():
                    vod_remarks = item.span.get_text()
                elif "类型" in item.strong.get_text():
                    type_name = ",".join(i.get_text() for i in item.select("a"))
                elif "上映日期" in item.strong.get_text():
                    vod_year = ",".join(i.get_text() for i in item.select("a"))
                elif "制片国家/地区" in item.strong.get_text():
                    vod_area = item.get_text().replace("制片国家/地区", "").replace("[", "").replace("]", "")
        vodList = {
            "vod_id": f'{Tag}${id}',
            "vod_name": sourcediv.h2.get_text(),
            "vod_pic": sourcediv.img["src"],
            "type_name": type_name,
            "vod_year": vod_year,
            "vod_area": vod_area,
            "vod_remarks": vod_remarks,
            "vod_actor": actor,
            "vod_director": director,
            "vod_content": doc.select_one("div.card.collapse").select_one("div.card-body").get_text().strip(),
        }

        vod_play = {}
        # 取播放列表数据
        sources = doc.select("a.btn.btn-square")
        lines_count = 0
        for source in sources:
            lines_count = len(get_lines(source["href"]))
            if lines_count:
                break
        for i in range(lines_count):
            sourceName = f"线路{i + 1}"
            vodItems = []
            playList = ""
            for source in sources:
                vodItems.append(
                    source.get_text() + "$" + f"{Tag}___" + source["href"].split(".")[0] + f"__{(i + 1) % lines_count}")
                if len(vodItems):
                    playList = "#".join(vodItems)
            vod_play.setdefault(sourceName, playList)
        if len(vod_play):
            vod_play_from = "$$$".join(vod_play.keys())
            vod_play_url = "$$$".join(vod_play.values())
            vodList.setdefault("vod_play_from", vod_play_from)
            vodList.setdefault("vod_play_url", vod_play_url)
        return [vodList]
    except Exception as e:
        print(e)
    return []


def playerContent(ids, flag, token):
    try:
        ids = ids.split("___")
        url = ids[-1].split("__")[0]
        play_from = int(ids[-1].split("__")[-1])
        lines = get_lines(f"{url}.htm")
        m3u8_url = lines[play_from]
        if m3u8_url.endswith("m3u8"):
            data = list(requests.get(url=m3u8_url, headers=getHeaders("")).content)[3354:]
            data = zlib.decompress(bytes(data), 16 + zlib.MAX_WBITS).decode()
            m3u8_raw_data = re.sub(r".*?\.ts", add_domain, data)
            m3u8_url = f"data:application/vnd.apple.mpegurl;base64,{base64.b64encode(m3u8_raw_data.encode('utf-8')).decode()}"
        return {
            "header": "",
            "parse": "0",
            "playUrl": "",
            "url": m3u8_url
        }
    except Exception as e:
        print(e)
    return {}


if __name__ == '__main__':
    # res = searchContent("灰影人", "")
    # res = detailContent('bdys01$/dongzuo/22321', "")
    # func = "playerContent"
    res = playerContent("bdys01___/play/22321-0__0", "", "")
    # res = eval(func)("68614-1-1")
    # res = get_lines("/play/22321-0.htm")
    print(res)