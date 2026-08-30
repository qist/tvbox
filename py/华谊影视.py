#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容均从互联网收集而来 仅供交流学习使用 严禁用于商业用途 请于24小时内删除
"""

import json
import time
import uuid
import random
import string
import struct
import base64
import re
import requests
from urllib.parse import quote
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA

try:
    from base.spider import Spider as _BaseSpider
except Exception:
    _BaseSpider = object


# ==================== 配置参数 ====================
CONFIG = {
    "appName": "华谊",
    "publicKey": "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCp9Ek4wIlQAtwFnuBRlsFiow2tr+4UOciGeNKbY7nL74etUqUb6fvpOSOHhFEfaWlfwUpOB17x3JEL3No19nfjCeVYrYPjlJcgoqUWH/tfIfFAQWvtxBIBlKazkhw8d3ChysWmeWRikKqkBsVRY4oqNPuj4sjm6Zult0U4I4prRQIDAQAB",
    "dataKey": "NDBYSZR1DMRRZ05NSUCWEJNIYWLBPT0=",
    "dataIv": "OC1A06E197EF10CF3F6058CA7A803B5E",
    "pkg": "com.muyue.tool",
    "version": "1.0.0.4",
    "decrypt": "1",
    "site": "https://vip.123pan.cn/1851089669/oss/az5.txt"
}

# 固定AES密钥 (用于publicParams头加密)
PARAMS_AES_KEY = "ed5fdsgucxumegqa"


# ==================== AES 加密工具 ====================

def pkcs7_pad(data, block_size=16):
    padding = block_size - (len(data) % block_size)
    return data + bytes([padding] * padding)

def pkcs7_unpad(data):
    if not data:
        return data
    padding = data[-1]
    if padding > 16 or padding == 0:
        return data
    return data[:-padding]

def aes_ecb_encrypt(plaintext, key):
    if isinstance(key, str):
        key = key.encode('utf-8')
    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')
    cipher = AES.new(key, AES.MODE_ECB)
    return base64.b64encode(cipher.encrypt(pkcs7_pad(plaintext))).decode('utf-8')

def aes_ecb_decrypt(ciphertext_b64, key):
    if isinstance(key, str):
        key = key.encode('utf-8')
    cipher = AES.new(key, AES.MODE_ECB)
    return pkcs7_unpad(cipher.decrypt(base64.b64decode(ciphertext_b64))).decode('utf-8')

def aes_cbc_encrypt(plaintext, key, iv):
    if isinstance(key, str):
        key = key.encode('utf-8')
    if isinstance(iv, str):
        iv = iv.encode('utf-8')
    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pkcs7_pad(plaintext))
    return ''.join(f'{b:02x}' for b in encrypted)

def rsa_encrypt(plaintext, public_key_b64):
    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')
    key_bytes = base64.b64decode(public_key_b64)
    key = RSA.import_key(key_bytes)
    cipher = PKCS1_v1_5.new(key)
    return base64.b64encode(cipher.encrypt(plaintext)).decode('utf-8')

def random_string(length):
    chars = string.digits + string.ascii_letters
    result = ''.join(random.choice(chars) for _ in range(length - 1))
    return result + '='


# ==================== Protobuf 编解码 ====================

def _encode_varint(value):
    result = b''
    if value < 0:
        value += (1 << 64)
    while value > 0x7F:
        result += bytes([0x80 | (value & 0x7F)])
        value >>= 7
    result += bytes([value & 0x7F])
    return result

def _decode_varint(data, pos):
    result = 0
    shift = 0
    while True:
        b = data[pos]
        result |= (b & 0x7F) << shift
        pos += 1
        if not (b & 0x80):
            break
        shift += 7
    return result, pos

def _encode_field(field_num, wire_type, value):
    tag = (field_num << 3) | wire_type
    result = _encode_varint(tag)
    if wire_type == 0:
        result += _encode_varint(value)
    elif wire_type == 2:
        if isinstance(value, str):
            value = value.encode('utf-8')
        result += _encode_varint(len(value))
        result += value
    elif wire_type == 5:
        result += struct.pack('<I', value)
    elif wire_type == 1:
        result += struct.pack('<Q', value)
    return result

def _parse_fields(data):
    fields = []
    pos = 0
    while pos < len(data):
        tag, pos = _decode_varint(data, pos)
        field_num = tag >> 3
        wire_type = tag & 0x07
        if wire_type == 0:
            value, pos = _decode_varint(data, pos)
            fields.append((field_num, wire_type, value))
        elif wire_type == 2:
            length, pos = _decode_varint(data, pos)
            fields.append((field_num, wire_type, data[pos:pos + length]))
            pos += length
        elif wire_type == 5:
            fields.append((field_num, wire_type, struct.unpack('<I', data[pos:pos + 4])[0]))
            pos += 4
        elif wire_type == 1:
            fields.append((field_num, wire_type, struct.unpack('<Q', data[pos:pos + 8])[0]))
            pos += 8
        else:
            break
    return fields

def _get_field(fields, field_num, default=None):
    for fn, wt, val in fields:
        if fn == field_num:
            if wt == 2:
                try:
                    return val.decode('utf-8')
                except:
                    return val
            return val
    return default


# ==================== Protobuf 消息编解码 ====================

def encode_secure_request(aes_encrypt1, aes_encrypt2, aes_fakestr, timestamp, random_str):
    data = b''
    data += _encode_field(1, 2, aes_encrypt1)
    data += _encode_field(2, 2, aes_encrypt2)
    data += _encode_field(3, 2, aes_fakestr)
    data += _encode_field(4, 0, timestamp)
    data += _encode_field(5, 2, random_str)
    return data

def encode_rsa_request(timestamp, sign, fake1, random_str, fake2):
    data = b''
    data += _encode_field(1, 0, timestamp)
    data += _encode_field(2, 2, sign)
    data += _encode_field(3, 2, fake1)
    data += _encode_field(4, 2, random_str)
    data += _encode_field(5, 2, fake2)
    return data

def decode_api_result(data):
    fields = _parse_fields(data)
    code = _get_field(fields, 1, 0)
    msg = _get_field(fields, 2, '')
    data_bytes = _get_field(fields, 3, b'')
    if isinstance(data_bytes, str):
        data_bytes = data_bytes.encode('utf-8')
    return code, msg, data_bytes

def decode_rsa_public(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    fields = _parse_fields(data)
    return {
        'str1': _get_field(fields, 1, ''),
        'str2': _get_field(fields, 2, ''),
        'str3': _get_field(fields, 3, ''),
        'str4': _get_field(fields, 4, ''),
        'str5': _get_field(fields, 5, '')
    }

def decode_drama_cover_image(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    fields = _parse_fields(data)
    return {
        'path': _get_field(fields, 1, ''),
        'thumbnail_path': _get_field(fields, 2, '')
    }

def decode_drama_bean(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    fields = _parse_fields(data)
    cover_data = _get_field(fields, 2)
    cover = decode_drama_cover_image(cover_data) if cover_data else {'path': '', 'thumbnail_path': ''}
    return {
        'area': _get_field(fields, 1, ''),
        'cover_image': cover,
        'id': _get_field(fields, 3, 0),
        'brief': _get_field(fields, 4, ''),
        'name': _get_field(fields, 5, ''),
        'stars': _get_field(fields, 6, 0.0),
        'director': _get_field(fields, 7, ''),
        'type': _get_field(fields, 8, 0),
        'remark': _get_field(fields, 13, ''),
        'year': _get_field(fields, 14, 0)
    }

def decode_drama_bean_page(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    fields = _parse_fields(data)
    return [decode_drama_bean(val) for fn, wt, val in fields if fn == 1]

def decode_drama_video_bean(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    fields = _parse_fields(data)
    return {
        'id': _get_field(fields, 1, 0),
        'title': _get_field(fields, 2, ''),
        'title_old': _get_field(fields, 3, ''),
        'path': _get_field(fields, 4, ''),
        'size': _get_field(fields, 5, 0),
        'time': _get_field(fields, 6, 0),
        'format': _get_field(fields, 7, ''),
        'type': _get_field(fields, 8, 0),
        'source': _get_field(fields, 9, ''),
        'source_cn': _get_field(fields, 10, ''),
        'source_old': _get_field(fields, 11, ''),
        'season': _get_field(fields, 12, 0),
        'episode': _get_field(fields, 13, 0),
        'is_vip': _get_field(fields, 14, False),
        'drama_id': _get_field(fields, 15, 0),
        'priority': _get_field(fields, 16, 0),
        'class_type': _get_field(fields, 17, 0),
        'sort': _get_field(fields, 18, 0)
    }

def decode_drama_detail_bean(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    fields = _parse_fields(data)
    cover_data = _get_field(fields, 2)
    cover = decode_drama_cover_image(cover_data) if cover_data else {'path': '', 'thumbnail_path': ''}
    videos = [decode_drama_video_bean(val) for fn, wt, val in fields if fn == 29]
    return {
        'area': _get_field(fields, 1, ''),
        'cover_image': cover,
        'id': _get_field(fields, 4, 0),
        'intro': _get_field(fields, 6, ''),
        'brief': _get_field(fields, 7, ''),
        'name': _get_field(fields, 9, ''),
        'stars': _get_field(fields, 10, 0.0),
        'director': _get_field(fields, 12, ''),
        'tag': _get_field(fields, 13, ''),
        'type': _get_field(fields, 14, 0),
        'year': _get_field(fields, 18, 0),
        'actor': _get_field(fields, 25, ''),
        'remark': _get_field(fields, 26, ''),
        'is_end': _get_field(fields, 27, False),
        'videos': videos
    }

def decode_parse_play_url(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    fields = _parse_fields(data)
    headers = {}
    for fn, wt, val in fields:
        if fn == 6:
            entry_fields = _parse_fields(val)
            key = _get_field(entry_fields, 1, '')
            value = _get_field(entry_fields, 2, '')
            if key:
                headers[key] = value
    return {
        'play_url': _get_field(fields, 1, ''),
        'fit_mode': _get_field(fields, 2, 0),
        'direct': _get_field(fields, 5, 0),
        'headers': headers,
        'msg': _get_field(fields, 9, '')
    }


# ==================== 核心爬虫类 ====================

def _source_priority(source_cn):
    """播放源画质优先级排序: 4K > 2K > 超清/高清 > 蓝光 > 臻彩 > 其他"""
    s = (source_cn or "").upper()
    if '4K' in s:
        return 0
    elif '2K' in s:
        return 1
    elif '超清' in s or '超高清' in s:
        return 2
    elif '蓝光' in s:
        return 3
    elif '臻彩' in s:
        return 4
    else:
        return 5


class Spider(_BaseSpider):
    def __init__(self):
        self.host = ""
        self.public_key = ""
        self.aes_key = PARAMS_AES_KEY
        self.zone_key = ""
        self.pkg = ""
        self.app_name = ""
        self.decrypt_flag = "1"
        self.data_key = ""
        self.data_iv = ""
        self.version = ""
        self.site = ""
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({'User-Agent': 'okhttp/3.12.1'})
        self.use_proto = False  # 是否使用protobuf端点

    def init(self, ext_text=""):
        if not ext_text:
            ext = CONFIG
        else:
            try:
                ext = json.loads(ext_text) if isinstance(ext_text, str) else ext_text
            except:
                ext = CONFIG
        if not isinstance(ext, dict):
            ext = CONFIG

        self.public_key = ext.get("publicKey", CONFIG["publicKey"])
        self.data_key = ext.get("dataKey", CONFIG["dataKey"])
        self.data_iv = ext.get("dataIv", CONFIG["dataIv"])
        self.pkg = ext.get("pkg", CONFIG["pkg"])
        self.app_name = ext.get("appName", CONFIG["appName"])
        self.decrypt_flag = ext.get("decrypt", CONFIG["decrypt"])
        self.version = ext.get("version", CONFIG["version"])
        self.site = ext.get("site", CONFIG["site"])
        self.host = ext.get("host", "")

        # 从 site URL 获取域名 (TVBox环境可能无法访问,失败则用默认)
        if not self.host and self.site:
            try:
                resp = self.session.get(self.site, timeout=10)
                domain = resp.json().get("domain", "")
                if domain:
                    self.host = domain
            except:
                pass

        if not self.host:
            self.host = "http://43.240.158.156:8002"

        # Protobuf端点使用publicKey直接签名即可工作
        # zone key获取失败不影响protobuf请求(publicKey作为fallback)
        self.use_proto = True
        try:
            self._get_zone_key()
        except Exception:
            pass

    def _get_device_info(self):
        uid = uuid.uuid4().hex.upper()
        v_app = self.version.replace(".", "")
        return {
            "country": "CN",
            "vName": self.version,
            "cpuId": "MT6893Z%2FCZA",
            "young": 0,
            "facturer": "Xiaomi",
            "pkg": self.pkg,
            "uuid": uid,
            "resolution": "1080x2272",
            "mac": "02%3A00%3A00%3A00%3A00%3A00",
            "abid": "397",
            "model": "M2012K11AC",
            "plat": "android",
            "udid": uid,
            "dpi": "440",
            "net": "1",
            "lang": "zh",
            "brand": "Xiaomi",
            "density": "2.75",
            "appName": self.app_name,
            "cpu": "arm64-v8a",
            "chid": "10000",
            "carrier": "%E8%81%94%E9%80%9A",
            "_vOsCode": 33,
            "vOs": "13",
            "v": 1,
            "tenantId": "",
            "vApp": v_app,
            "device": 0,
            "androidID": "a1b2c3d4e5f67890"
        }

    def _get_zone_key(self):
        timestamp = int(time.time() * 1000)
        random_str = random_string(16)
        sign = rsa_encrypt(f"{timestamp}{random_str}", self.public_key)
        rsa_req = encode_rsa_request(timestamp, sign, random_string(16), random_str, random_string(16))
        headers = self._build_proto_headers()
        resp = self.session.post(f"{self.host}/api/v5/find/app/zone", data=rsa_req, headers=headers, timeout=15)
        code, msg, data_bytes = decode_api_result(resp.content)
        if code != 200:
            raise Exception(f"zone key failed: {msg}")
        rsa_public = decode_rsa_public(data_bytes)
        self.zone_key = rsa_public['str2'] + rsa_public['str3'] + rsa_public['str4'] + rsa_public['str5']

    def _build_proto_headers(self):
        rsa_key = self.zone_key if self.zone_key else self.public_key
        device_info = self._get_device_info()
        timestamp = int(time.time() * 1000)
        random_str = random_string(16)
        v_app = device_info.get("vApp", "1009")
        sig = rsa_encrypt(f"{timestamp}{random_str}{v_app}", rsa_key)
        sig_encrypted = aes_ecb_encrypt(f"{timestamp}{random_str}", self.data_iv)
        device_info["sig"] = sig
        device_info["random_str"] = random_str
        device_info["timestamp"] = timestamp
        device_info["sig2"] = sig_encrypted[:8]
        device_info["sig3"] = sig_encrypted[8:]
        device_json = json.dumps(device_info, separators=(',', ':'), ensure_ascii=False)
        params_data = aes_cbc_encrypt(device_json, self.aes_key, self.aes_key)
        return {
            'User-Agent': 'okhttp/3.12.1',
            'Accept': 'application/x-protobuf',
            'Content-Type': 'application/x-protobuf',
            'publicParams': json.dumps({"paramsData": params_data}, separators=(',', ':'))
        }

    def _build_json_headers(self):
        device_info = self._get_device_info()
        device_json = json.dumps(device_info, separators=(',', ':'), ensure_ascii=False)
        params_data = aes_cbc_encrypt(device_json, self.aes_key, self.aes_key)
        return {
            'User-Agent': 'okhttp/3.12.1',
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=utf-8',
            'publicParams': json.dumps({"paramsData": params_data}, separators=(',', ':'))
        }

    def _build_request_body(self, params):
        timestamp = int(time.time() * 1000)
        random_str = random_string(8)
        fake_str = random_string(20)
        query_parts = []
        for key, value in params.items():
            if value is not None and str(value):
                query_parts.append(f"{key}={value}")
        query_string = "&".join(query_parts)
        encrypted = aes_ecb_encrypt(f"{query_string}{timestamp}", self.data_key)
        combined = random_str + encrypted
        return encode_secure_request(combined[:20], combined[20:], fake_str, timestamp, random_str)

    def _decrypt_response_data(self, data_str):
        if self.decrypt_flag == "0":
            return data_str
        intermediate = aes_ecb_decrypt(data_str, self.data_key)
        return aes_ecb_decrypt(intermediate, self.data_iv)

    def _get_json(self, path):
        url = f"{self.host}{path}"
        headers = self._build_json_headers()
        resp = self.session.get(url, headers=headers, timeout=15)
        return resp.text

    def _post_proto(self, path, params):
        url = f"{self.host}{path}"
        body = self._build_request_body(params)
        headers = self._build_proto_headers()
        resp = self.session.post(url, data=body, headers=headers, timeout=15)
        return resp.content

    def _get_json_decrypted(self, path):
        resp_text = self._get_json(path)
        data = json.loads(resp_text)
        data_val = data.get("data", "")
        # data 可能是加密字符串、明文JSON、列表或None
        if isinstance(data_val, str) and data_val and self.decrypt_flag != "0":
            return self._decrypt_response_data(data_val)
        return data_val

    # ==================== TVBox 接口实现 ====================

    def homeContent(self, filter):
        classes = []
        filters = {}

        try:
            data_val = self._get_json_decrypted("/api/v3/drama/getCategory?orderBy=type_id")
            if isinstance(data_val, str):
                categories = json.loads(data_val)
            elif isinstance(data_val, list):
                categories = data_val
            else:
                categories = []

            if isinstance(categories, list):
                filter_keys = ["class", "lang", "area", "year", "extend_sort"]
                filter_names = {"class": "类型", "lang": "语言", "area": "地区",
                                "year": "年份", "extend_sort": "排序"}

                for cat in categories:
                    cat_name = cat.get("name", "")
                    if cat_name == "公告":
                        continue
                    cat_id = str(cat.get("id", ""))
                    classes.append({"type_name": cat_name, "type_id": cat_id})

                    conver_url = cat.get("converUrl", "")
                    if conver_url:
                        try:
                            conver_data = json.loads(conver_url)
                            filter_list = []
                            for key in filter_keys:
                                if key in conver_data:
                                    values = conver_data[key]
                                    if values:
                                        items = [{"n": v, "v": v} for v in values.split(",")]
                                        filter_list.append({
                                            "key": key,
                                            "name": filter_names.get(key, key),
                                            "value": items
                                        })
                            if filter_list:
                                filters[cat_id] = filter_list
                        except:
                            pass
        except Exception as e:
            print(f"homeContent error: {e}")

        return {"class": classes, "filters": filters}

    def homeVideoContent(self):
        videos = []
        try:
            data_val = self._get_json_decrypted("/api/ex/v3/security/tag/list")
            tags = json.loads(data_val) if isinstance(data_val, str) else (data_val if isinstance(data_val, list) else [])
            if isinstance(tags, list):
                for tag in tags:
                    for section in tag.get("sections", []):
                        for vod in section.get("vodList", []):
                            cover = vod.get("coverImage", {})
                            videos.append({
                                "vod_id": str(vod.get("id", "")),
                                "vod_name": vod.get("name", ""),
                                "vod_pic": cover.get("path", ""),
                                "vod_remarks": vod.get("remark", "")
                            })
        except Exception as e:
            print(f"homeVideoContent error: {e}")
        return {"list": videos}

    def categoryContent(self, tid, pg, filter, extend):
        page = str(pg)
        videos = []

        try:
            if self.use_proto:
                params = {
                    "pagesize": "21",
                    "typeId1": str(tid),
                    "page": page,
                    "vodOrderBy": extend.get("extend_sort", "最新") if extend else "最新",
                    "vodArea": extend.get("area", "") if extend else "",
                    "vodLang": extend.get("lang", "") if extend else "",
                    "vodClass": extend.get("class", "") if extend else "",
                    "vodYear": extend.get("year", "") if extend else ""
                }
                resp_data = self._post_proto("/api/proto/v5/drama/category", params)
                code, msg, data_bytes = decode_api_result(resp_data)
                drama_list = decode_drama_bean_page(data_bytes)
                for drama in drama_list:
                    cover = drama.get("cover_image", {})
                    videos.append({
                        "vod_id": str(drama.get("id", "")),
                        "vod_name": drama.get("name", ""),
                        "vod_pic": cover.get("thumbnail_path", cover.get("path", "")),
                        "vod_remarks": drama.get("remark", "")
                    })
            else:
                params = f"typeId1={tid}&page={page}&pagesize=21"
                data_val = self._get_json_decrypted(f"/api/ex/v3/security/drama/list?{params}")
                d = json.loads(data_val) if isinstance(data_val, str) else (data_val if isinstance(data_val, dict) else {"list": []})
                for item in d.get("list", []):
                    cover = item.get("coverImage", {})
                    videos.append({
                        "vod_id": str(item.get("id", "")),
                        "vod_name": item.get("name", ""),
                        "vod_pic": cover.get("thumbnailPath", cover.get("path", "")),
                        "vod_remarks": item.get("remark", "")
                    })
        except Exception as e:
            print(f"categoryContent error: {e}")

        return {"list": videos, "page": int(page), "pagecount": 999, "limit": 21, "total": 999}

    def detailContent(self, ids):
        try:
            vod_id = str(ids[0])

            if self.use_proto:
                resp_data = self._post_proto("/api/proto/v5/drama/getDetail", {"id": vod_id})
                code, msg, data_bytes = decode_api_result(resp_data)
                detail = decode_drama_detail_bean(data_bytes)
                videos = detail.get("videos", [])
            else:
                data_val = self._get_json_decrypted(f"/api/ex/v3/security/drama/list?vodId={vod_id}&page=1&pagesize=1")
                d = json.loads(data_val) if isinstance(data_val, str) else (data_val if isinstance(data_val, dict) else {"list": []})
                items = d.get("list", [])
                if not items:
                    return {"list": []}
                item = items[0]
                detail = {
                    'id': item.get("id", 0),
                    'name': item.get("name", ""),
                    'area': item.get("area", ""),
                    'year': item.get("year", 0),
                    'director': item.get("director", ""),
                    'actor': item.get("actor", ""),
                    'intro': item.get("intro", ""),
                    'brief': item.get("brief", ""),
                    'tag': item.get("clazz", ""),
                    'remark': item.get("remark", ""),
                    'cover_image': item.get("coverImage", {}),
                    'videos': item.get("videos", []),
                }
                videos = detail.get("videos", [])

            # 构建播放源 - 按画质排序(4K优先)
            play_sources = {}
            for video in videos:
                source_cn = video.get("sourceCn") or video.get("source_cn") or "橘汁"
                if source_cn not in play_sources:
                    play_sources[source_cn] = []
                path = video.get("path", "")
                title = video.get("title", "")
                source = video.get("source") or video.get("sourceOld") or ""

                if re.match(r'(?i).*\.(mp4|m3u8|flv|mkv|avi|ts|mov|mpd|m4a|wmv)(\?.*)?$', path):
                    play_url = path
                else:
                    play_info = {"vodPlayFrom": source, "playUrl": path}
                    play_url = base64.b64encode(json.dumps(play_info, separators=(',', ':')).encode('utf-8')).decode('utf-8')
                play_sources[source_cn].append(f"{title}${play_url}")

            # 按画质优先级排序播放源
            sorted_sources = sorted(play_sources.keys(), key=_source_priority)
            play_from = "$$$".join(sorted_sources)
            play_url = "$$$".join(["#".join(play_sources[sc]) for sc in sorted_sources])

            cover = detail.get("cover_image", {})
            return {
                "list": [{
                    "vod_id": str(detail.get("id", "")),
                    "vod_name": detail.get("name", ""),
                    "vod_pic": cover.get("path", ""),
                    "vod_actor": detail.get("actor", ""),
                    "vod_director": detail.get("director", ""),
                    "vod_area": detail.get("area", ""),
                    "vod_year": str(detail.get("year", "")),
                    "vod_remarks": detail.get("remark", ""),
                    "vod_tag": detail.get("tag", ""),
                    "vod_content": detail.get("intro", detail.get("brief", "")),
                    "vod_play_from": play_from,
                    "vod_play_url": play_url
                }]
            }
        except Exception as e:
            print(f"detailContent error: {e}")
            return {"list": []}

    def searchContent(self, key, quick, pg="1"):
        return self.searchContentPage(key, quick, pg)

    def searchContentPage(self, key, quick, pg="1"):
        videos = []
        try:
            page = int(pg) if pg else 1
            if self.use_proto:
                resp_data = self._post_proto("/api/proto/v5/drama/search", {
                    "searchKeys": key, "page": str(page), "pagesize": "21"
                })
                code, msg, data_bytes = decode_api_result(resp_data)
                drama_list = decode_drama_bean_page(data_bytes)
                for drama in drama_list:
                    cover = drama.get("cover_image", {})
                    videos.append({
                        "vod_id": str(drama.get("id", "")),
                        "vod_name": drama.get("name", ""),
                        "vod_pic": cover.get("thumbnail_path", cover.get("path", "")),
                        "vod_remarks": drama.get("remark", "")
                    })
            else:
                encoded_key = quote(key)
                data_val = self._get_json_decrypted(
                    f"/api/ex/v3/security/drama/list?searchKeys={encoded_key}&page={page}&pagesize=21"
                )
                d = json.loads(data_val) if isinstance(data_val, str) else (data_val if isinstance(data_val, dict) else {"list": []})
                for item in d.get("list", []):
                    cover = item.get("coverImage", {})
                    videos.append({
                        "vod_id": str(item.get("id", "")),
                        "vod_name": item.get("name", ""),
                        "vod_pic": cover.get("thumbnailPath", cover.get("path", "")),
                        "vod_remarks": item.get("remark", "")
                    })
        except Exception as e:
            print(f"searchContent error: {e}")
        hasmore = 1 if len(videos) >= 21 else 0
        return {
            "list": videos,
            "page": page,
            "pagecount": page + 1 if hasmore else page,
            "limit": max(len(videos), 21),
            "total": len(videos)
        }

    def playerContent(self, flag, id, vipFlags):
        # 如果是直接播放链接，直接返回
        if re.match(r'(?i).*\.(mp4|m3u8|flv|mkv|avi|ts|mov|mpd|m4a|wmv)(\?.*)?$', id):
            return {"parse": 0, "url": id, "header": {}}

        try:
            play_info = json.loads(base64.b64decode(id).decode('utf-8'))
            vod_play_from = play_info.get("vodPlayFrom", "")
            play_url = play_info.get("playUrl", "")

            if self.use_proto:
                resp_data = self._post_proto("/api/proto/v5/videoUsableUrl", {
                    "vodPlayFrom": vod_play_from, "playUrl": play_url
                })
                code, msg, data_bytes = decode_api_result(resp_data)
                play_data = decode_parse_play_url(data_bytes)
                result_url = play_data.get("play_url", "")
                play_msg = play_data.get("msg", "")
                # 如果解析失败(返回原始path或错误信息),设置parse=1让播放器嗅探
                if result_url and result_url != play_url and not play_msg:
                    return {"parse": 0, "url": result_url, "header": play_data.get("headers", {})}
                else:
                    return {"parse": 1, "url": play_url, "header": {}}
            else:
                encoded_source = quote(vod_play_from)
                encoded_path = quote(play_url)
                data_val = self._get_json_decrypted(
                    f"/api/ex/v3/security/videoUsableUrl?vodPlayFrom={encoded_source}&playUrl={encoded_path}"
                )
                play_data = json.loads(data_val) if isinstance(data_val, str) else (data_val if isinstance(data_val, dict) else {})
                result_url = play_data.get("playUrl", play_data.get("play_url", ""))
                play_msg = play_data.get("msg", "")
                if result_url and result_url != play_url and not play_msg:
                    return {"parse": 0, "url": result_url, "header": play_data.get("headers", {})}
                else:
                    return {"parse": 1, "url": play_url, "header": {}}
        except Exception as e:
            print(f"playerContent error: {e}")
            return {"parse": 0, "url": id, "header": {}}


# ==================== TVBox 接口适配 ====================
# Spider类已继承base.spider.Spider，TVBox直接调用实例方法
# 以下模块级函数作为兼容层，返回Python dict

spider = None

def init(ext_text=""):
    global spider
    spider = Spider()
    spider.init(ext_text if ext_text else "")

def homeContent(filter):
    return spider.homeContent(filter)

def homeVideoContent():
    return spider.homeVideoContent()

def categoryContent(tid, pg, filter, extend):
    return spider.categoryContent(tid, pg, filter, extend)

def detailContent(ids):
    return spider.detailContent(ids)

def searchContent(key, quick, pg="1"):
    return spider.searchContent(key, quick, pg)

def searchContentPage(key, quick, pg="1"):
    return spider.searchContentPage(key, quick, pg)

def playerContent(flag, id, vipFlags):
    return spider.playerContent(flag, id, vipFlags)

def isVideoFormat(url):
    return bool(re.match(r'(?i).*\.(mp4|m3u8|flv|mkv|avi|ts|mov|mpd|m4a|wmv)(\?.*)?$', url))

def manualSniffer(needGoto):
    return False
