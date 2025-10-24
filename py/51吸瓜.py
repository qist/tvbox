# -*- coding: utf-8 -*-
# by @嗷呜
import colorsys
import json
import random
import re
import sys
import threading
import time
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from pyquery import PyQuery as pq
from base64 import b64decode, b64encode
from pprint import pprint
from urllib.parse import urlparse, quote, unquote
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):

    def init(self, extend="{}"):
        self.domin='https://cg51.com'
        self.proxies = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="134", "Google Chrome";v="134"',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        self.host=self.host_late(self.gethosts())
        self.headers.update({'Origin': self.host, 'Referer': f"{self.host}/"})
        thread = threading.Thread(target=self.getcnh)
        thread.start()

        pass

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    def homeContent(self, filter):
        data=pq(requests.get(self.host, headers=self.headers,proxies=self.proxies).content)
        result = {}
        classes = []
        for k in list(data('.navbar-nav.mr-auto').children('li').items())[1:-3]:
            if k('ul'):
                for j in k('ul li').items():
                    classes.append({
                        'type_name': j('a').text(),
                        'type_id': j('a').attr('href').strip(),
                    })
            else:
                classes.append({
                    'type_name': k('a').text(),
                    'type_id': k('a').attr('href').strip(),
                })
        result['class'] = classes
        result['list'] = self.getlist(data('#index article a'))
        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        if '@folder' in tid:
            id=tid.replace('@folder','')
            videos=self.getfod(id)
        else:
            data=pq(requests.get(f"{self.host}{tid}{pg}", headers=self.headers,proxies=self.proxies).content)
            videos=self.getlist(data('#archive article a'),tid)
        result = {}
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 1 if '@folder' in tid else 99999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        url=ids[0] if ids[0].startswith("http") else f"{self.host}{ids[0]}"
        data=pq(requests.get(url, headers=self.headers,proxies=self.proxies).content)
        vod = {'vod_play_from': '51吸瓜'}
        did = data('script[data-api]').attr('data-api')
        try:
            clist = []
            if data('.tags .keywords a'):
                for k in data('.tags .keywords a').items():
                    title = k.text()
                    href = k.attr('href')
                    clist.append('[a=cr:' + json.dumps({'id': href, 'name': title}) + '/]' + title + '[/a]')
            vod['vod_content'] = ' '.join(clist)
        except:
            vod['vod_content'] = data('.post-title').text()
        try:
            plist=[]
            if data('.dplayer'):
                for c, k in enumerate(data('.dplayer').items(), start=1):
                    config = json.loads(k.attr('data-config'))
                    plist.append(f"视频{c}${did}_dm_{config['video']['url']}")
            vod['vod_play_url']='#'.join(plist)
        except:
            vod['vod_play_url']=f"可能没有视频${url}"
        return {'list':[vod]}

    def searchContent(self, key, quick, pg="1"):
        data=pq(requests.get(f"{self.host}/search/{key}/{pg}", headers=self.headers,proxies=self.proxies).content)
        return {'list':self.getlist(data('#archive article a')),'page':pg}

    def playerContent(self, flag, id, vipFlags):
        did,pid=id.split('_dm_')
        p=0 if re.search(r'\.(m3u8|mp4|flv|ts|mkv|mov|avi|webm)', pid) else 1
        if not p:
            pid=f"{self.getProxyUrl()}&pdid={quote(id)}&type=m3u8"
        return  {'parse': p, 'url': pid, 'header': self.headers}

    def localProxy(self, param):
        try:
            xtype=param.get('type','')
            if 'm3u8' in xtype:
                path,url=unquote(param['pdid']).split('_dm_')
                data=requests.get(url, headers=self.headers,proxies=self.proxies,timeout=10).text
                lines = data.strip().split('\n')
                times=0.0
                for i in lines:
                    if i.startswith('#EXTINF:'):
                        times+=float(i.split(':')[-1].replace(',',''))
                thread = threading.Thread(target=self.some_background_task, args=(path,int(times)))
                thread.start()
                print('[INFO] 获取视频时长成功', times)
                return [200, 'text/plain', data]
            elif 'xdm' in xtype:
                url=f"{self.host}{unquote(param['path'])}"
                res = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=10).json()
                dms=[]
                for k in res:
                    text=k.get('text')
                    children=k.get('children')
                    if text:dms.append(text.strip())
                    if children:
                        for j in children:
                            ctext=j.get('text')
                            if ctext:
                                ctext=ctext.strip()
                                if "@" in ctext:
                                    dms.append(ctext.split(' ',1)[-1].strip())
                                else:
                                    dms.append(ctext)
                return self.xml(dms,int(param['times']))
            url=self.d64(param['url'])
            match = re.search(r"loadBannerDirect\('([^']*)'", url)
            if match:
                url=match.group(1)
            res = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=10)
            return [200, res.headers.get('Content-Type'), self.aesimg(res.content)]
        except Exception as e:
            print(e)
            return [500, 'text/html', '']

    def some_background_task(self,path,times):
        try:
            time.sleep(1)
            purl=f"{self.getProxyUrl()}&path={quote(path)}&times={times}&type=xdm"
            self.fetch(f"http://127.0.0.1:9978/action?do=refresh&type=danmaku&path={quote(purl)}")
        except Exception as e:
            print(e)

    def xml(self, dms,times):
        try:
            tsrt=f'共有{len(dms)}条弹幕来袭！！！'
            danmustr = f'<?xml version="1.0" encoding="UTF-8"?>\n<i>\n\t<chatserver>chat.xtdm.com</chatserver>\n\t<chatid>88888888</chatid>\n\t<mission>0</mission>\n\t<maxlimit>99999</maxlimit>\n\t<state>0</state>\n\t<real_name>0</real_name>\n\t<source>k-v</source>\n'
            danmustr += f'\t<d p="0,5,25,16711680,0">{tsrt}</d>\n'
            for i in range(len(dms)):
                base_time = (i / len(dms)) * times
                dm0 = base_time + random.uniform(-3, 3)
                dm0 = round(max(0, min(dm0, times)), 1)
                dm2 = self.get_color()
                dm4 = re.sub(r'[<>&\u0000\b]', '', dms[i])
                tempdata = f'\t<d p="{dm0},1,25,{dm2},0">{dm4}</d>\n'
                danmustr += tempdata
            danmustr += '</i>'
            return [200, "text/xml", danmustr]
        except Exception as e:
            print(e)
            return [500, 'text/html', '']

    def get_color(self):
        # 10% 概率随机颜色, 90% 概率白色
        if random.random() < 0.1:
            h = random.random()
            s = random.uniform(0.7, 1.0)
            v = random.uniform(0.8, 1.0)
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            r = int(r * 255)
            g = int(g * 255)
            b = int(b * 255)
            decimal_color = (r << 16) + (g << 8) + b
            return str(decimal_color)
        else:
            return '16777215'

    def e64(self, text):
        try:
            text_bytes = text.encode('utf-8')
            encoded_bytes = b64encode(text_bytes)
            return encoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Base64编码错误: {str(e)}")
            return ""

    def d64(self, encoded_text):
        try:
            encoded_bytes = encoded_text.encode('utf-8')
            decoded_bytes = b64decode(encoded_bytes)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Base64解码错误: {str(e)}")
            return ""

    def gethosts(self):
        url=self.domin
        curl=self.getCache('host_51cn')
        if curl:
            try:
                data=pq(requests.get(curl, headers=self.headers, proxies=self.proxies).content)('a').attr('href')
                if data:
                    parsed_url = urlparse(data)
                    url = parsed_url.scheme + "://" + parsed_url.netloc
            except:
                pass
        try:
            html = pq(requests.get(url, headers=self.headers, proxies=self.proxies).content)
            html_pattern = r"Base64\.decode\('([^']+)'\)"
            html_match = re.search(html_pattern, html('script').eq(-1).text(), re.DOTALL)
            if not html_match:raise Exception("未找到html")
            html = pq(b64decode(html_match.group(1)).decode())('script').eq(-4).text()
            return self.hstr(html)
        except Exception as e:
            self.log(f"获取: {str(e)}")
            return ""

    def getcnh(self):
        data=pq(requests.get(f"{self.host}/homeway.html", headers=self.headers,proxies=self.proxies).content)
        url=data('.post-content[itemprop="articleBody"] blockquote p').eq(0)('a').attr('href')
        parsed_url = urlparse(url)
        host = parsed_url.scheme + "://" + parsed_url.netloc
        self.setCache('host_51cn',host)

    def hstr(self, html):
        pattern = r"(backupLine\s*=\s*\[\])\s+(words\s*=)"
        replacement = r"\1, \2"
        html = re.sub(pattern, replacement, html)
        data = f"""
        var Vx = {{
            range: function(start, end) {{
                const result = [];
                for (let i = start; i < end; i++) {{
                    result.push(i);
                }}
                return result;
            }},

            map: function(array, callback) {{
                const result = [];
                for (let i = 0; i < array.length; i++) {{
                    result.push(callback(array[i], i, array));
                }}
                return result;
            }}
        }};

        Array.prototype.random = function() {{
            return this[Math.floor(Math.random() * this.length)];
        }};

        var location = {{
            protocol: "https:"
        }};

        function executeAndGetResults() {{
            var allLines = lineAry.concat(backupLine);
            var resultStr = JSON.stringify(allLines);
            return resultStr;
        }};
        {html}
        executeAndGetResults();
        """
        return self.p_qjs(data)

    def p_qjs(self, js_code):
        try:
            from com.whl.quickjs.wrapper import QuickJSContext
            ctx = QuickJSContext.create()
            result_json = ctx.evaluate(js_code)
            ctx.destroy()
            return json.loads(result_json)
    
        except Exception as e:
            self.log(f"执行失败: {e}")
            return []

    def get_domains(self):
        html = pq(requests.get(self.domin, headers=self.headers,proxies=self.proxies).content)
        html_pattern = r"Base64\.decode\('([^']+)'\)"
        html_match = re.search(html_pattern, html('script').eq(-1).text(), re.DOTALL)
        if not html_match:
            raise Exception("未找到html")
        html = b64decode(html_match.group(1)).decode()
        words_pattern = r"words\s*=\s*'([^']+)'"
        words_match = re.search(words_pattern, html, re.DOTALL)
        if not words_match:
            raise Exception("未找到words")
        words = words_match.group(1).split(',')
        main_pattern = r"lineAry\s*=.*?words\.random\(\)\s*\+\s*'\.([^']+)'"
        domain_match = re.search(main_pattern, html, re.DOTALL)
        if not domain_match:
            raise Exception("未找到主域名")
        domain_suffix = domain_match.group(1)
        domains = []
        for _ in range(3):
            random_word = random.choice(words)
            domain = f"https://{random_word}.{domain_suffix}"
            domains.append(domain)
        return domains

    def getfod(self, id):
        url = f"{self.host}{id}"
        data = pq(requests.get(url, headers=self.headers, proxies=self.proxies).content)
        vdata=data('.post-content[itemprop="articleBody"]')
        r=['.txt-apps','.line','blockquote','.tags','.content-tabs']
        for i in r:vdata.remove(i)
        p=vdata('p')
        videos=[]
        for i,x in enumerate(vdata('h2').items()):
            c=i*2
            videos.append({
                'vod_id': p.eq(c)('a').attr('href'),
                'vod_name': p.eq(c).text(),
                'vod_pic': f"{self.getProxyUrl()}&url={self.e64(p.eq(c+1)('img').attr('data-xkrkllgl'))}",
                'vod_remarks':x.text()
                })
        return videos

    def host_late(self, url_list):
        if isinstance(url_list, str):
            urls = [u.strip() for u in url_list.split(',')]
        else:
            urls = url_list

        if len(urls) <= 1:
            return urls[0] if urls else ''

        results = {}
        threads = []

        def test_host(url):
            try:
                start_time = time.time()
                response = requests.head(url,headers=self.headers,proxies=self.proxies,timeout=1.0, allow_redirects=False)
                delay = (time.time() - start_time) * 1000
                results[url] = delay
            except Exception as e:
                results[url] = float('inf')

        for url in urls:
            t = threading.Thread(target=test_host, args=(url,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        return min(results.items(), key=lambda x: x[1])[0]

    def getlist(self,data,tid=''):
        videos = []
        l='/mrdg' in tid
        for k in data.items():
            a=k.attr('href')
            b=k('h2').text()
            c=k('span[itemprop="datePublished"]').text()
            if a and b and c:
                videos.append({
                    'vod_id': f"{a}{'@folder' if l else ''}",
                    'vod_name': b.replace('\n', ' '),
                    'vod_pic': f"{self.getProxyUrl()}&url={self.e64(k('script').text())}&type=img",
                    'vod_remarks': c,
                    'vod_tag':'folder' if l else '',
                    'style': {"type": "rect", "ratio": 1.33}
                })
        return videos

    def aesimg(self, word):
        key = b'f5d965df75336270'
        iv = b'97b60394abc2fbe1'
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(word), AES.block_size)
        return decrypted