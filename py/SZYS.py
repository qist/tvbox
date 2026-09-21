# -*- coding: utf-8 -*-
# by @嗷呜
import json
import random
import sys
from base64 import b64encode, b64decode
from concurrent.futures import ThreadPoolExecutor

# 引入 RSA 加解密所需模块
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

sys.path.append('..')
from base.spider import Spider

class Spider(Spider):

    def init(self, extend=""):
        did = self.getdid()
        self.headers.update({'deviceId': did})
        token = self.gettk()
        self.headers.update({'token': token})

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    # 1. 修改为主机域名
    host = 'http://qkys.qukanwh.com'

    # 2. 同步原脚本的配置请求头
    headers = {
        'HOST': 'qkys.qukanwh.com',
        'User-Agent': 'okhttp/4.12.0',
        'client': 'app',
        'deviceType': 'Android',
        'Referer': ''
    }

    # 3. 导入原脚本中的 RSA 密钥对与配置
    publicKey_str = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCoYt0BP77U+DM08BiI/QbSRIfxijXo85BTPqIM1Ow8BNwhLETzRIZ+dEwdWDbydG/PspgBAfRpGaYVdJYtvaC2JnoO8+Ik6qMWojfEJxSFLa0Pb0A892tun4gsxoEMjcreZ+YGyaBxAfqX0BSMfdrOgIYaZQjYrw9TRLlUT31QoQIDAQAB\n-----END PUBLIC KEY-----"
    privateKey_str = "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCquQQ5r6+yJI8CDFkXRp8vUsdD45ov8EP12ooLs56ca2DQXaSNGS9910bAPVA9chkp0mKIvKqjAsHz5Tl9EeNPblarGEeJUIxpxZtiSqNTpvtiD/TjhpzuHYic7RAfQ/h7p/ypE8ymU42pYjsB5t26Mv6XgkLV+jzrSf73HlCuS0iMyLmt6zz3Mw9izM13EpB8iFLtfbbYymycKTx4RAmPQLwhNGex/AlUIYxXP4R2yyaa4W6mEtc6aME2QuzJFxPgP3HJ9NBx/LWVn4skxWjZ7zg+VRQRHnjyVaSLu3Z5gN5ITWCyE32qaHJa6WBahZj5jWhRyAG1bQ+xKJa8lBL5AgMBAAECggEAUwv9SjJ0PSwbhNuM2w23kcWquROWhYtTA91zGY4esehqB/IFgb2mpIh8Gje5OKqwIu/8jpd4SiOlRYdUF8sD0DfUYRZGdj2AkFNX6tBz8tVfo6wvbB6naA1lzzBij1L5JO3qsjS3cJFkb+kg2yP66AC2Z+0tpfk8eRhdtshAZwfcd1DEGt1uAvYL1eaUK9HRvpt9lPeGcHERDl2hBd4uyaF0K1O+zF9y59nYbTySWPxRZq3sFEE85xRMlstD7YZi7W2gKvMFRD4/FKmrZ3m7aKJRITtyKOyyPcYmepNv3Qv7kk59Pg38n2WWQ0Ra/bCH3E48YNCnQvZMpitkTfJhoQKBgQDbnROOYTP8OTJ6f/qhoGjxeO3x1VOaOp8l0x7b0SCfoqNGS0Cyiqj72BmJtPMPqSTjn6MmNzqbg1KOdhXyzNozs+i5ccW1M56j96mr5I/Z0FpE3oyIHNfDDBlf9M8YQqEF9oYxniYYft9oapO7cRQkHER6qpvnHTavwlv4m78CXwKBgQDHAjs2YlpKDdI1lcbZJCc7TwtH+Pd2bUki8YXafWNcPhITQHbOZjr310eK1QJC6GJncjkOqbX7yv3ivvTO35FZTQhuA1xEG1P00FG8bE0tHYPIwQHi9y0eA5cieMdo8E6XYria1mw/3fqSQEsfZyJlR32JQIoGAipM8iO1X2nZpwKBgDkMFIhnt5lNQk+P7wsNIDWZtDWdtJnboHuy29E+Abt2A/O+mI/IdRz2hau/1WO8DFkUnszOi+rZshhPlGP90rCbi1igtTrcrdjp/KkqNjPea5R4OwkgdOu1uOG0NheXNzzVTQaWjk7Opjn5dWa7eP/oV+GFb/oZHJuLYVizHGsBAoGADA7rjZEKDYCm4w5PPSr+oY5ZjaPdQrS+gLqHtMRyN82fBMGcMUdqfUfzEstzVqCEDeaS5HuOBlK3bXzKkppjUTjksN3NQmcxgBz7RuJ9DqXCLXDcb2cwuafYCYOt+YLOEEgwDVm+t2P44dG5e46hO+fICH/7nP+WlpD5buz4GfMCgYB57r3g/6hi9WUDnfc7ZAzWMqR0EhJVYKYy+KFEtdIPzhkkIHq5RASe88E9kzoGoZFdb3tIjvGZWcHerirrqWkMsuQtP/Qi0zjieid5tAPj+r4kbiCVTw0E0jnmPBzGInQi7lpeTTKnG1fbyS5lBS+WmHfIuzpECgCkxhaT+LJJkg==\n-----END PRIVATE KEY-----"

    # RSA 公钥加密实现
    def rsa_encrypt(self, text):
        try:
            key = RSA.import_key(self.publicKey_str)
            cipher = PKCS1_v1_5.new(key)
            cipher_text = cipher.encrypt(text.encode('utf-8'))
            return b64encode(cipher_text).decode('utf-8')
        except Exception as e:
            print(f"RSA加密失败: {e}")
            return ""

    # RSA 私钥解密实现
    def rsa_decrypt(self, text):
        try:
            key = RSA.import_key(self.privateKey_str)
            cipher = PKCS1_v1_5.new(key)
            raw_bytes = b64decode(text.encode('utf-8'))
            
            decrypted = b""
            offset = 0
            while offset < len(raw_bytes):
                chunk = raw_bytes[offset:offset + 256]
                decrypted += cipher.decrypt(chunk, None)
                offset += 256
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"RSA解密失败: {e}")
            return ""

    def homeContent(self, filter):
        data = self.post(f"{self.host}/api/v1/app/screen/screenType", headers=self.headers).json()
        result = {}
        cate = {
            "类型": "type",
            "地区": "area",
            "年份": "year"
        }
        sort = {
            'key': 'sort',
            'name': '排序',
            'value': [{'n': '最新', 'v': 'NEWEST'}, {'n': '热门', 'v': 'HOT'}, {'n': '收藏', 'v': 'COLLECT'}]
        }
        classes = []
        filters = {}
        for k in data.get('data', []):
            classes.append({
                'type_name': k['name'],
                'type_id': str(k['id'])
            })
            filters[str(k['id'])] = []
            for v in k.get('children', []):
                if v['name'] in cate:
                    filters[str(k['id'])].append({
                        'name': v['name'],
                        'key': cate[v['name']],
                        'value': [{'n': i['name'], 'v': i['name']} for i in v.get('children', [])]
                    })
            filters[str(k['id'])].append(sort)
        result['class'] = classes
        result['filters'] = filters
        return result

    def homeVideoContent(self):
        jdata = {
            "condition": {
                "sreecnTypeEnum": "NEWEST"
            },
            "pageNum": 1,
            "pageSize": 40
        }
        data = self.post(f"{self.host}/api/v1/app/screen/screenMovie", headers=self.headers, json=jdata).json()
        return {'list': self.getlist(data.get('data', {}).get('records', []))}

    def categoryContent(self, tid, pg, filter, extend):
        # 保持最纯粹的条件字段，移除任何空字符串占位
        condition = {
            'sreecnTypeEnum': 'NEWEST',
            'typeId': int(tid) if str(tid).isdigit() else tid
        }
        
        if extend:
            if 'sort' in extend:
                condition['sreecnTypeEnum'] = extend.pop('sort')
            condition.update(extend)
            
        jdata = {
            'condition': condition,
            'pageNum': int(pg),
            'pageSize': 40,
        }
        
        try:
            data = self.post(f"{self.host}/api/v1/app/screen/screenMovie", headers=self.headers, json=jdata).json()
            result = {}
            if data and data.get('data') and 'records' in data['data']:
                result['list'] = self.getlist(data['data']['records'])
            else:
                result['list'] = []
            result['page'] = pg
            result['pagecount'] = 9999
            result['limit'] = 40
            result['total'] = 999999
            return result
        except Exception as e:
            print(f"分类获取错误: {e}")
            return {'list': [], 'page': pg}

    def detailContent(self, ids):
        ids = ids[0].split('@@')
        jdata = {"id": int(ids[0]), "typeId": ids[-1]}
        v = self.post(f"{self.host}/api/v1/app/play/movieDesc", headers=self.headers, json=jdata).json()
        v = v.get('data', {})
        vod = {
            'type_name': v.get('typeId', ''),
            'vod_year': v.get('year', ''),
            'vod_area': v.get('area', ''),
            'vod_actor': v.get('star', ''),
            'vod_director': v.get('director', ''),
            'vod_content': v.get('introduce', ''),
            'vod_play_from': '',
            'vod_play_url': ''
        }

        play_params = {
            "id": int(ids[0]),
            "source": 0,
            "typeId": ids[-1]
        }
        encrypt_payload = {"key": self.rsa_encrypt(json.dumps(play_params))}
        
        c_res = self.post(f"{self.host}/api/v1/app/play/movieDetails", headers=self.headers, json=encrypt_payload).json()
        decrypted_play_str = self.rsa_decrypt(c_res.get('data', ''))
        if not decrypted_play_str:
            return {'list': [vod]}
            
        decrypted_play_data = json.loads(decrypted_play_str)
        l = decrypted_play_data.get('moviePlayerList', [])
        if not l:
            return {'list': [vod]}
            
        n = {str(i['id']): i['moviePlayerName'] for i in l}
        
        m = play_params.copy()
        m.update({'playerId': l[0]['id']})
        
        first_source_payload = {"key": self.rsa_encrypt(json.dumps(m))}
        first_res = self.post(f"{self.host}/api/v1/app/play/movieDetails", headers=self.headers, json=first_source_payload).json()
        
        decrypted_first_str = self.rsa_decrypt(first_res.get('data', ''))
        if decrypted_first_str:
            decrypted_first_episode = json.loads(decrypted_first_str)
            pd = self.getv(m, decrypted_first_episode.get('episodeList', []))
        else:
            pd = {}
        
        if len(l) > 1:
            with ThreadPoolExecutor(max_workers=len(l)-1) as executor:
                future_to_player = {executor.submit(self.getd, play_params, player): player for player in l[1:]}
                for future in future_to_player:
                    try:
                        o, p = future.result()
                        if p:
                            pd.update(self.getv(o, p))
                    except Exception as e:
                        print(f"多线路请求失败: {e}")
        w, e = [], []
        for i, x in pd.items():
            if x:
                w.append(n.get(i, '未知线路'))
                e.append(x)
        vod['vod_play_from'] = '$$$'.join(w)
        vod['vod_play_url'] = '$$$'.join(e)
        return {'list': [vod]}

    def searchContent(self, key, quick, pg="1"):
        jdata = {
            "condition": {
                "value": str(key)
            },
            "pageNum": int(pg),
            "pageSize": 40
        }
        try:
            data = self.post(f"{self.host}/api/v1/app/search/searchMovie", headers=self.headers, json=jdata).json()
            return {'list': self.getlist(data.get('data', {}).get('records', [])), 'page': pg}
        except Exception as e:
            print(f"搜索请求失败: {e}")
            return {'list': [], 'page': pg}

    def playerContent(self, flag, id, vipFlags):
        raw_id_str = self.d64(id)
        if not raw_id_str:
            return {'parse': 0, 'url': ''}
        jdata = json.loads(raw_id_str)
        encrypt_payload = {"key": self.rsa_encrypt(json.dumps(jdata))}
        data = self.post(f"{self.host}/api/v1/app/play/movieDetails", headers=self.headers, json=encrypt_payload).json()
        
        try:
            decrypted_url_data = json.loads(self.rsa_decrypt(data.get('data', '')))
            playerUrl = decrypted_url_data.get('url', '')
            if not playerUrl:
                return {'parse': 0, 'url': ''}
            
            params = {'playerUrl': playerUrl, 'playerId': jdata['playerId']}
            pd = self.fetch(f"{self.host}/api/v1/app/play/analysisMovieUrl", headers=self.headers, params=params).json()
            url, p = pd.get('data', ''), 0
        except Exception as e:
            print(f"解析流媒体直链失败: {e}")
            url, p = "", 0
        return {'parse': p, 'url': url, 'header': {'User-Agent': 'okhttp/4.12.0'}, 'danmaku': 'http://127.0.0.1:9978/proxy?do=diydanmu'}

    def localProxy(self, param):
        pass

    def liveContent(self, url):
        pass

    def gettk(self):
        self.headers.update({'deviceId': self.getdid()})
        try:
            data = self.fetch(f"{self.host}/api/v1/app/user/visitorInfo", headers=self.headers).json()
            return data.get('data', {}).get('token', '')
        except:
            return ""

    def getdid(self):
        did = self.getCache('ldid')
        if not did:
            hex_chars = '0123456789abcdef'
            did = ''.join(random.choice(hex_chars) for _ in range(16))
            self.setCache('ldid', did)
        return did

    def getd(self, jdata, player):
        x = jdata.copy()
        x.update({'playerId': player['id']})
        encrypt_payload = {"key": self.rsa_encrypt(json.dumps(x))}
        response = self.post(f"{self.host}/api/v1/app/play/movieDetails", headers=self.headers, json=encrypt_payload).json()
        decrypted_str = self.rsa_decrypt(response.get('data', ''))
        if decrypted_str:
            decrypted_episode = json.loads(decrypted_str)
            return x, decrypted_episode.get('episodeList', [])
        return x, []

    def getv(self, d, c):
        f = {str(d['playerId']): ''}
        g = []
        for i in c:
            j = d.copy()
            j.update({'episodeId': i['id']})
            g.append(f"{i['episode']}${self.e64(json.dumps(j))}")
        f[str(d['playerId'])] = '#'.join(g)
        return f

    def getlist(self, data):
        videos = []
        for i in data:
            if not i.get('id'):
                continue
            videos.append({
                'vod_id': f"{i['id']}@@{i.get('typeId', '')}",
                'vod_name': i.get('name', ''),
                'vod_pic': i.get('cover', ''),
                'vod_year': i.get('year', ''),
                'vod_remarks': i.get('totalEpisode', '')
            })
        return videos

    def e64(self, text):
        try:
            return b64encode(text.encode('utf-8')).decode('utf-8')
        except:
            return ""

    def d64(self, encoded_text):
        try:
            return b64decode(encoded_text.encode('utf-8')).decode('utf-8')
        except:
            return ""
