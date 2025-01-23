#coding=utf-8
#!/usr/bin/python
import sys
import json
import time
import hashlib
from base64 import b64decode
from difflib import SequenceMatcher
from urllib.parse import quote, unquote
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append('..')
from base.spider import Spider


class Spider(Spider):  # 元类 默认的元类 type
	def getName(self):
		return "直播"

	def init(self, extend):
		try:
			self.extendDict = json.loads(extend)
		except:
			self.extendDict = {}

	def destroy(self):
		pass

	def isVideoFormat(self, url):
		pass

	def manualVideoCheck(self):
		pass

	def homeVideoContent(self):
		result = {}
	
		return result

	def homeContent(self, filter):
		result = {}
		try:
			url = self.extendDict['url']
			data = self.fetch(url, headers=self.header, timeout=5).json()
			result['class'] = data['classes']
			if filter:
				result['filters'] = data['filter']
		except:
			result['class'] = [{"type_id": 'douyu', "type_name": "斗鱼"}]
			result['filters'] = {'douyu': {'key': '斗鱼', 'name': '斗鱼', "value": [{"n": "一起看", "v": "208"}]}}
		return result

	def categoryContent(self, cid, page, filter, ext):
		result = {}
		videos = []
		header = self.header.copy()
		if cid == 'bilibili':
			if 'B站' in ext:
				tid = ext['B站']
			else:
				try:
					r = self.fetch(json.loads(self.extendDict)['url'], headers=header, timeout=5)
					tid = r.json()['filter'][cid][0]['value'][0]['v']
				except:
					tid = '1'
			url = f'https://api.live.bilibili.com/xlive/web-interface/v1/second/getList?platform=web&parent_area_id={tid}&page={page}'
			data = self.fetch(url, headers=header, timeout=5).json()
			vodList = data['data']['list']
			append = 'bilibili'
			imgnm = 'cover'
			vidnm = 'roomid'
			titlenm = 'title'
			remarknm = 'uname'
			if data['data']['has_more'] == 1:
				pagecount = page + 1
			else:
				pagecount = page
		elif cid == 'douyu':
			if '斗鱼' in ext:
				tid = ext['斗鱼']
			else:
				try:
					r = self.fetch(json.loads(self.extend)['url'], headers=header)
					tid = r.json()['filter'][cid][0]['value'][0]['v']
				except:
					tid = '208'
			url = f'https://www.douyu.com/gapi/rkc/directory/mixList/2_{tid}/{page}'
			r = self.fetch(url, headers=header, timeout=5)
			data = r.json()
			vodList = data['data']['rl']
			pagecount = data['data']['pgcnt']
			append = 'douyu'
			imgnm = 'rs1'
			vidnm = 'rid'
			titlenm = 'rn'
			remarknm = 'nn'
		elif cid == 'huya':
			if '虎牙' in ext:
				tid = ext['虎牙']
			else:
				try:
					r = self.fetch(json.loads(self.extend)['url'], headers=header)
					tid = r.json()['filter'][cid][0]['value'][0]['v']
				except:
					tid = '2135'
			header['Referer'] = 'https://www.huya.com/'
			url = f'https://www.huya.com/cache.php?m=LiveList&do=getLiveListByPage&gameId={tid}&tagAll=0&callback=getLiveListJsonpCallback&page={page}'
			r = self.fetch(url, headers=header, timeout=5)
			data = json.loads(self.regStr(reg="getLiveListJsonpCallback\((.*)\)", src=r.text))
			vodList = data['data']['datas']
			pagecount = data['data']['totalPage']
			append = 'huya'
			imgnm = 'screenshot'
			vidnm = 'profileRoom'
			titlenm = 'introduction'
			remarknm = 'nick'
		else:
			vodList = []
			pagecount = page
			append = ''
			imgnm = ''
			vidnm = ''
			titlenm = ''
			remarknm = ''
		for vod in vodList:
			img = vod[imgnm]
			vid = vod[vidnm]
			title = vod[titlenm]
			remark = vod[remarknm]
			videos.append({
				"vod_id": title + '###' + append + '###' + str(vid),
				"vod_name": title,
				"vod_pic": img,
				"vod_remarks": remark
			})
		lenvodList = len(vodList)
		result['list'] = videos
		result['page'] = page
		result['pagecount'] = pagecount
		result['limit'] = lenvodList
		result['total'] = lenvodList
		return result

	def detailContent(self, did):
		did = did[0]
		header = self.header.copy()
		didList = did.split('###')
		title = didList[0]
		if didList[1] == 'bilibili':
			url = f'https://api.live.bilibili.com/room/v1/Room/playUrl?cid={didList[2]}&qn=20000&platform=h5'
			data = self.fetch(url, headers=header).json()
			platformList = ['B站']
			playurlList = [data['data']['quality_description'][0]['desc'] + '$' + data['data']['durl'][0]['url']]
		elif didList[1] == 'douyu':
			params = quote(json.dumps({"rid": didList[2]}))
			#url = f'https://api-lmteam.koyeb.app/live/douyu?params={params}'
			url = f'http://maomao.kandiantv.cn/douyu1.php?id={didList[2]}'
			platformList = ['斗鱼']
			playurlList = [f'直播${url}']
		elif didList[1] == 'huya':
			import html
			header['Content-Type'] = 'application/x-www-form-urlencoded'
			url = 'https://www.huya.com/' + didList[2]
			r = self.fetch(url, headers=header, timeout=5)
			try:
				data = json.loads(self.regStr(reg='stream: ([\s\S]*?)\n', src=r.text))
			except:
				data = json.loads(b64decode(self.regStr(reg='"stream": "([\s\S]*?)"', src=r.text)).decode())
			platformList = []
			playurlList = []
			i = 1
			for pL in data['data'][0]['gameStreamInfoList']:
				platformList.append('虎牙{}'.format(str(i)))
				baseurl = pL['sHlsUrl'] + '/' + pL['sStreamName'] + '.' + pL['sHlsUrlSuffix']
				srcAntiCode = html.unescape(pL['sHlsAntiCode'])
				c = srcAntiCode.split('&')
				c = [i for i in c if i != '']
				n = {i.split('=')[0]: i.split('=')[1] for i in c}
				fm = unquote(n['fm'])
				u = b64decode(fm).decode('utf-8')
				hash_prefix = u.split('_')[0]
				ctype = n.get('ctype', '')
				txyp = n.get('txyp', '')
				fs = n.get('fs', '')
				t = n.get('t', '')
				seqid = str(int(time.time() * 1e3 + 1463993859134))
				wsTime = hex(int(time.time()) + 3600).replace('0x', '')
				hash = hashlib.md5('_'.join([hash_prefix, '1463993859134', pL['sStreamName'], hashlib.md5((seqid + '|' + ctype + '|' + t).encode('utf-8')).hexdigest(), wsTime]).encode('utf-8')).hexdigest()
				ratio = ''
				purl = "{}?wsSecret={}&wsTime={}&seqid={}&ctype={}&ver=1&txyp={}&fs={}&ratio={}&u={}&t={}&sv=2107230339".format(baseurl, hash, wsTime, seqid, ctype, txyp, fs, ratio, '1463993859134', t)
				playurlList.append('直播$' + purl)
				i += 1
		else:
			playurlList = []
			platformList = []
		vod = {
			"vod_id": didList[2],
			"vod_name": title,
		}
		vod['vod_play_from'] = '$$$'.join(platformList)
		vod['vod_play_url'] = '$$$'.join(playurlList)
		result = {'list': [vod]}
		return result

	def searchContent(self, key, quick):
		return self.searchContentPage(key, False, '1')

	def searchContentPage(self, key, quick, page):
		items = []
		page = int(page)
		keyword = key
		if page == 1:
			siteList = ['bb', 'dy', 'hy']
		else:
			siteList = self.getCache('livesiteList_{}_{}'.format(keyword, page))
			self.delCache('livesiteList_{}_{}'.format(keyword, page))
			if not siteList:
				return {'list': items}
		contents = []
		with ThreadPoolExecutor(max_workers=3) as executor:
			searchList = []
			try:
				for site in siteList:
					tag = site
					api = ''
					future = executor.submit(self.runSearch, keyword, tag, page, api)
					searchList.append(future)
				for future in as_completed(searchList, timeout=30):
					contents.append(future.result())
			except:
				executor.shutdown(wait=False)
		nextpageList = []
		for content in contents:
			if content is None:
				continue
			key = list(content.keys())[0]
			infos = content[key]
			items = items + content[key][0]
			nextpageList.append(infos[1])
			if not infos[1]:
				siteList.remove(key)
		self.setCache('livesiteList_{}_{}'.format(keyword, page+1), siteList)
		result = {
			'list': items
		}
		return result

	def runSearch(self, key, tag, page, api):
		try:
			defname = 'self.search' + tag
			result = eval(defname)(key, tag, page, api)
			return result
		except:
			pass

	def searchbb(self, key, tag, pg, api):
		items = []
		header = self.header.copy()
		header['Cookie'] = 'buvid3=0'
		url = f'https://api.bilibili.com/x/web-interface/search/type?page={pg}&page_size=10&order=online&search_type=live_user&keyword={key}'
		data = self.fetch(url, headers=header).json()
		vList = data['data']['result']
		for video in vList:
			if video['live_status'] == 0:
				continue
			title = self.removeHtmlTags(video['uname'])
			if SequenceMatcher(None, title, key).ratio() < 0.6 and key not in title:
				continue
			items.append({
				'vod_id': '{}###bilibili###{}'.format(title, video['roomid']),
				'vod_name': title,
				'vod_pic': 'https:' + video['uface'],
				"vod_remarks": 'B站直播'
			})
		return {tag: [items, pg * 10 < len(items)]}

	def searchdy(self, key, tag, pg, api):
		items = []
		header = self.header.copy()
		url = f'https://www.douyu.com/japi/search/api/searchUser?kw={key}&page={pg}&pageSize=10&filterType=1'
		data = self.fetch(url, headers=header, timeout=5).json()
		vList = data['data']['relateUser']
		for video in vList:
			if video['anchorInfo']['isLive'] != 1:
				continue
			title = video['anchorInfo']['nickName']
			if SequenceMatcher(None, title, key).ratio() < 0.6 and key not in title:
				continue
			items.append({
				'vod_id': '{}###douyu###{}'.format(title, video['anchorInfo']['rid']),
				'vod_name': title,
				'vod_pic': video['anchorInfo']['roomSrc'],
				"vod_remarks": '斗鱼直播'
			})
		return {tag: [items, pg * 10 < len(items)]}

	def searchhy(self, key, tag, pg, api):
		items = []
		header = self.header.copy()
		header['Cookie'] = 'buvid3=0'
		start = str((pg-1)*40)
		url = f'https://search.cdn.huya.com/?m=Search&do=getSearchContent&typ=-5&livestate=1&q={key}&start={start}&rows=40'
		r = self.fetch(url, headers=header)
		data = r.json()
		vList = data['response']['1']['docs']
		for video in vList:
			title = video['game_nick']
			if SequenceMatcher(None, title, key).ratio() < 0.6 and key not in title:
				continue
			items.append({
				'vod_id': '{}###huya###{}'.format(title, video['room_id']),
				'vod_name': title,
				'vod_pic': video['game_avatarUrl180'],
				"vod_remarks": '虎牙直播'
			})
		return {tag: [items, pg * 40 < len(items)]}

	def playerContent(self, flag, pid, vipFlags):
		result = {}
		header = self.header.copy()
		# header['Referer'] = "https://www.bilibili.com"
		result["parse"] = 0
		result["playUrl"] = ''
		result["url"] = pid
		result["header"] = header
		return result

	def localProxy(self, param):
		return [200, "video/MP2T", ""]

	def removeHtmlTags(self, src):
		from re import sub, compile
		clean = compile('<.*?>')
		return sub(clean, '', src)

	header = {
		"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36"
	}