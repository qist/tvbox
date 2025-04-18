#coding=utf-8
#!/usr/bin/python
import sys
import json
import time
from datetime import datetime
from difflib import SequenceMatcher
from urllib.parse import quote, unquote
sys.path.append('..')
from base.spider import Spider

class Spider(Spider):  # 元类 默认的元类 type
	def getName(self):
		return "B站番剧"

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

	def homeContent(self, filter):
		result = {}
		cateManual = {
			"番剧": "1",
			"国创": "4",
			"电影": "2",
			"综艺": "7",
			"电视剧": "5",
		}
		classes = []
		for k in cateManual:
			classes.append({
				'type_name': k,
				'type_id': cateManual[k]
			})
		result['class'] = classes
		if filter:
			result['filters'] = self.config['filter']
			currentYear = datetime.now().year
			for resultfilter in result['filters']:
				for rf in result['filters'][resultfilter]:
					if rf['key'] == 'year':
						for rfv in rf['value']:
							if rfv['n'].isdigit():
								if int(rfv['n']) < currentYear:
									pos = rf['value'].index(rfv)
									for year in range(currentYear, int(rfv['n']), -1):
										rf['value'].insert(pos, {'v': f'[{str(year)},{str(year+1)})', 'n': str(year)})
										pos += 1
									break
								else:
									break
					elif rf['key'] == 'release_date':
						for rfv in rf['value']:
							if rfv['n'].isdigit():
								if int(rfv['n']) < currentYear:
									pos = rf['value'].index(rfv)
									for year in range(currentYear, int(rfv['n']), -1):
										rf['value'].insert(pos, {'v': f'[{str(year)}-01-01 00:00:00,{str(year+1)}-01-01 00:00:00)', 'n': str(year)})
										pos += 1
									break
								else:
									break
		return result

	def homeVideoContent(self):
		return self.categoryContent('1', '1', False, {})

	def categoryContent(self, cid, page, filter, ext):
		page = int(page)
		result = {}
		videos = []
		cookie, _, _ = self.getCookie('{}')
		url = 'https://api.bilibili.com/pgc/season/index/result?order=2&sort=0&pagesize=20&type=1&st={}&season_type={}&page={}'.format(cid, cid, page)
		for key in ext:
			url += f'&{key}={quote(ext[key])}'
		r = self.fetch(url, headers=self.header, cookies=cookie, timeout=5)
		data = json.loads(self.cleanText(r.text))
		vodList = data['data']['list']
		for vod in vodList:
			aid = str(vod['season_id']).strip()
			title = self.removeHtmlTags(self.cleanText(vod['title']))
			img = vod['cover'].strip()
			remark = vod['index_show'].strip()
			videos.append({
				"vod_id": aid,
				"vod_name": title,
				"vod_pic": img,
				"vod_remarks": remark
			})
		lenvideos = len(videos)
		if data['data']['has_next'] == 1:
			pagecount = page + 1
		else:
			pagecount = page
		result['list'] = videos
		result['page'] = page
		result['pagecount'] = pagecount
		result['limit'] = lenvideos
		result['total'] = lenvideos
		return result

	def detailContent(self, did):
		did = did[0]
		url = "http://api.bilibili.com/pgc/view/web/season?season_id={0}".format(did)
		r = self.fetch(url, headers=self.header, timeout=10)
		data = json.loads(self.cleanText(r.text))
		vod = {
			"vod_id": did,
			"vod_name": self.removeHtmlTags(data['result']['title']),
			"vod_pic": data['result']['cover'],
			"type_name": data['result']['share_sub_title'],
			"vod_actor": data['result']['actors'].replace('\n', '，'),
			"vod_content": self.removeHtmlTags(data['result']['evaluate'])
		}
		videoList = data['result']['episodes']
		playUrl = ''
		for video in videoList:
			eid = video['id']
			cid = video['cid']
			name = self.removeHtmlTags(video['share_copy']).replace("#", "-").replace('$', '*')
			remark = time.strftime('%H:%M:%S', time.gmtime(video['duration']/1000))
			if remark.startswith('00:'):
				remark = remark[3:]
			playUrl = playUrl + '[{}]/{}${}_{}#'.format(remark, name, eid, cid)
		vod['vod_play_from'] = 'B站番剧'
		vod['vod_play_url'] = playUrl.strip('#')
		result = {
			'list': [
				vod
			]
		}
		return result

	def searchContent(self, key, quick):
		return self.searchContentPage(key, quick, '1')

	def searchContentPage(self, key, quick, page):
		videos = []
		cookie = ''
		if 'cookie' in self.extendDict:
			cookie = self.extendDict['cookie']
		if 'json' in self.extendDict:
			r = self.fetch(self.extendDict['json'], timeout=10)
			if 'cookie' in r.json():
				cookie = r.json()['cookie']
		if cookie == '':
			cookie = '{}'
		elif type(cookie) == str and cookie.startswith('http'):
			cookie = self.fetch(cookie, timeout=10).text.strip()
		try:
			if type(cookie) == dict:
				cookie = json.dumps(cookie, ensure_ascii=False)
		except:
			pass
		cookie, _, _ = self.getCookie(cookie)
		url = f'https://api.bilibili.com/x/web-interface/search/type?search_type=media_bangumi&keyword={key}&page={page}'
		r = self.fetch(url, headers=self.header, cookies=cookie, timeout=5)
		data = json.loads(self.cleanText(r.text))
		if 'result' not in data['data']:
			return {'list': videos}, 1
		vodList = data['data']['result']
		for vod in vodList:
			sid = str(vod['season_id']).strip()
			title = self.removeHtmlTags(self.cleanText(vod['title']))
			if SequenceMatcher(None, title, key).ratio() < 0.6 and key not in title:
				continue
			img = vod['eps'][0]['cover'].strip()
			remark = self.removeHtmlTags(vod['index_show']).strip()
			videos.append({
				"vod_id": sid,
				"vod_name": title,
				"vod_pic": img,
				"vod_remarks": remark
			})
		result = {
			'list': videos
		}
		return result

	def playerContent(self, flag, pid, vipFlags):
		result = {}
		pidList = pid.split("_")
		aid = pidList[0]
		cid = pidList[1]
		url = 'https://api.bilibili.com/pgc/player/web/playurl?ep_id={0}&cid={1}&qn=120&fnval=4048&fnver=0&fourk=1'.format(aid, cid)
		cookie = ''
		extendDict = self.extendDict
		if 'cookie' in extendDict:
			cookie = extendDict['cookie']
		if 'json' in extendDict:
			r = self.fetch(extendDict['json'], timeout=10)
			if 'cookie' in r.json():
				cookie = r.json()['cookie']
		if cookie == '':
			cookie = '{}'
		elif type(cookie) == str and cookie.startswith('http'):
			cookie = self.fetch(cookie, timeout=10).text.strip()
		try:
			if type(cookie) == dict:
				cookie = json.dumps(cookie, ensure_ascii=False)
		except:
			pass
		cookiesDict, _, _ = self.getCookie(cookie)
		cookies = quote(json.dumps(cookiesDict))
		if 'thread' in extendDict:
			thread = str(extendDict['thread'])
		else:
			thread = '0'
		result["parse"] = '0'
		result["playUrl"] = ''
		result["url"] = f'http://127.0.0.1:9978/proxy?do=py&type=mpd&cookies={cookies}&url={quote(url)}&aid={aid}&cid={cid}&thread={thread}'
		result["header"] = self.header
		result['danmaku'] = 'https://api.bilibili.com/x/v1/dm/list.so?oid={}'.format(cid)
		result["format"] = 'application/dash+xml'
		return result

	def localProxy(self, params):
		if params['type'] == "mpd":
			return self.proxyMpd(params)
		if params['type'] == "media":
			return self.proxyMedia(params)
		return None

	def proxyMpd(self, params):
		content, durlinfos, mediaType = self.getDash(params)
		if mediaType == 'mpd':
			return [200, "application/dash+xml", content]
		else:
			url = content
			durlinfo = durlinfos['durl'][0]['backup_url']
			try:
				r = self.fetch(url, headers=self.header, stream=True, timeout=1)
				statusCode = r.status_code
				try:
					r.close()
				except:
					pass
			except:
				try:
					r.close()
				except:
					pass
				statusCode = 404
				for url in durlinfo:
					try:
						r = self.fetch(url, headers=self.header, stream=True, timeout=1)
						statusCode = r.status_code
					except:
						statusCode = 404
					if statusCode == 200:
						break
					try:
						r.close()
					except:
						pass
			if statusCode != 200 and self.retry == 0:
				self.retry += 1
				self.proxyMedia(params, True)
			header = self.header.copy()
			if 'range' in params:
				header['Range'] = params['range']
			if '127.0.0.1:7777' in url:
				header['Location'] = url
				return [302, "video/MP2T", None, header]
			return [206, "application/octet-stream", self.fetch(content, headers=header, stream=True).content]

	def proxyMedia(self, params, forceRefresh=False):
		_, dashinfos, _ = self.getDash(params)
		if 'videoid' in params:
			videoid = int(params['videoid'])
			dashinfo = dashinfos['video'][videoid]
			url = dashinfo['baseUrl']
		elif 'audioid' in params:
			audioid = int(params['audioid'])
			dashinfo = dashinfos['audio'][audioid]
			url = dashinfo['baseUrl']
		else:
			return [404, "text/plain", ""]
		try:
			r = self.fetch(url, headers=params['headers'], stream=True)
			statusCode = r.status_code
			try:
				r.close()
			except:
				pass
		except:
			try:
				r.close()
			except:
				pass
			statusCode = 404
			for url in dashinfo['backupUrl']:
				try:
					r = self.fetch(url, headers=self.header, stream=True, timeout=1)
					statusCode = r.status_code
				except:
					statusCode = 404
				if statusCode == 200:
					break
				try:
					r.close()
				except:
					pass
		if statusCode != 200 and self.retry == 0:
			self.retry += 1
			self.proxyMedia(params, True)
		header = self.header.copy()
		if 'range' in params:
			header['Range'] = params['range']
		return [206, "application/octet-stream", self.fetch(url, headers=header, stream=True).content]

	def getDash(self, params, forceRefresh=False):
		aid = params['aid']
		cid = params['cid']
		url = unquote(params['url'])
		if 'thread' in params:
			thread = params['thread']
		else:
			thread = 0
		header = self.header.copy()
		self.setCache('debug', params['cookies'])
		cookieDict = json.loads(params['cookies'])
		key = f'bilimdmpdCache_{aid}_{cid}'
		if forceRefresh:
			self.delCache(key)
		else:
			data = self.getCache(key)
			if data:
				return data['content'], data['dashinfos'], data['type']

		cookies = cookieDict.copy()
		r = self.fetch(url, cookies=cookies, headers=header, timeout=5)
		data = json.loads(self.cleanText(r.text))
		if data['code'] != 0:
			return '', {}, ''
		if not 'dash' in data['result']:
			purl = data['result']['durl'][0]['url']
			try:
				expiresAt = int(self.regStr(reg='deadline=(\d+)', src=purl).group(1)) - 60
			except:
				expiresAt = int(time.time()) + 600
			if int(thread) > 0:
				try:
					self.fetch('http://127.0.0.1:7777')
				except:
					self.fetch('http://127.0.0.1:9978/go')
				purl = f'http://127.0.0.1:7777?url={quote(purl)}&thread={thread}'
			self.setCache(key, {'content': purl, 'type': 'mp4', 'dashinfos': data['result'], 'expiresAt': expiresAt})
			return purl, data['result'], 'mp4'

		dashinfos = data['result']['dash']
		duration = dashinfos['duration']
		minBufferTime = dashinfos['minBufferTime']
		videoinfo = ''
		videoid = 0
		deadlineList = []
		# videoList = sorted(dashinfos['video'], key=lambda x: x['bandwidth'], reverse=True)
		for video in dashinfos['video']:
			try:
				deadline = int(self.regStr(reg='deadline=(\d+)', src=video['baseUrl']).group(1))
			except:
				deadline = int(time.time()) + 600
			deadlineList.append(deadline)
			codecs = video['codecs']
			bandwidth = video['bandwidth']
			frameRate = video['frameRate']
			height = video['height']
			width = video['width']
			void = video['id']
			vidparams = params.copy()
			vidparams['videoid'] = videoid
			baseUrl = f'http://127.0.0.1:9978/proxy?do=py&type=media&cookies={quote(json.dumps(cookies))}&url={quote(url)}&aid={aid}&cid={cid}&videoid={videoid}'
			videoinfo = videoinfo + f"""	      <Representation bandwidth="{bandwidth}" codecs="{codecs}" frameRate="{frameRate}" height="{height}" id="{void}" width="{width}">
	        <BaseURL>{baseUrl}</BaseURL>
	        <SegmentBase indexRange="{video['SegmentBase']['indexRange']}">
	        <Initialization range="{video['SegmentBase']['Initialization']}"/>
	        </SegmentBase>
	      </Representation>\n"""
			videoid += 1
		audioinfo = ''
		audioid = 0
		# audioList = sorted(dashinfos['audio'], key=lambda x: x['bandwidth'], reverse=True)
		for audio in dashinfos['audio']:
			try:
				deadline = int(self.regStr(reg='deadline=(\d+)', src=audio['baseUrl']).group(1))
			except:
				deadline = int(time.time()) + 600
			deadlineList.append(deadline)
			bandwidth = audio['bandwidth']
			codecs = audio['codecs']
			aoid = audio['id']
			aidparams = params.copy()
			aidparams['audioid'] = audioid
			baseUrl = f'http://127.0.0.1:9978/proxy?do=py&type=media&cookies={quote(json.dumps(cookies))}&url={quote(url)}&aid={aid}&cid={cid}&audioid={audioid}'
			audioinfo = audioinfo + f"""	      <Representation audioSamplingRate="44100" bandwidth="{bandwidth}" codecs="{codecs}" id="{aoid}">
	        <BaseURL>{baseUrl}</BaseURL>
	        <SegmentBase indexRange="{audio['SegmentBase']['indexRange']}">
	        <Initialization range="{audio['SegmentBase']['Initialization']}"/>
	        </SegmentBase>
	      </Representation>\n"""
			audioid += 1
		mpd = f"""<?xml version="1.0" encoding="UTF-8"?>
	<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" profiles="urn:mpeg:dash:profile:isoff-on-demand:2011" type="static" mediaPresentationDuration="PT{duration}S" minBufferTime="PT{minBufferTime}S">
	  <Period>
	    <AdaptationSet mimeType="video/mp4" startWithSAP="1" scanType="progressive" segmentAlignment="true">
	      {videoinfo.strip()}
	    </AdaptationSet>
	    <AdaptationSet mimeType="audio/mp4" startWithSAP="1" segmentAlignment="true" lang="und">
	      {audioinfo.strip()}
	    </AdaptationSet>
	  </Period>
	</MPD>"""
		expiresAt = min(deadlineList) - 60
		self.setCache(key, {'type': 'mpd', 'content': mpd.replace('&', '&amp;'), 'dashinfos': dashinfos, 'expiresAt': expiresAt})
		return mpd.replace('&', '&amp;'), dashinfos, 'mpd'

	def getCookie(self, cookie):
		if '{' in cookie and '}' in cookie:
			cookies = json.loads(cookie)
		else:
			cookies = dict([co.strip().split('=', 1) for co in cookie.strip(';').split(';')])
		bblogin = self.getCache('bblogin')
		if bblogin:
			imgKey = bblogin['imgKey']
			subKey = bblogin['subKey']
			return cookies, imgKey, subKey

		header = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36"
		}
		r = self.fetch("http://api.bilibili.com/x/web-interface/nav", cookies=cookies, headers=header, timeout=10)
		data = json.loads(r.text)
		code = data["code"]
		if code == 0:
			imgKey = data['data']['wbi_img']['img_url'].rsplit('/', 1)[1].split('.')[0]
			subKey = data['data']['wbi_img']['sub_url'].rsplit('/', 1)[1].split('.')[0]
			self.setCache('bblogin', {'imgKey': imgKey, 'subKey': subKey, 'expiresAt': int(time.time()) + 1200})
			return cookies, imgKey, subKey
		r = self.fetch("https://www.bilibili.com/", headers=header, timeout=5)
		cookies = r.cookies.get_dict()
		imgKey = ''
		subKey = ''
		return cookies, imgKey, subKey

	def removeHtmlTags(self, src):
		from re import sub, compile
		clean = compile('<.*?>')
		return sub(clean, '', src)

	retry = 0
	header = {
		"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
		"Referer": "https://www.bilibili.com"
	}
	config = {
		"filter": {"1":[{"key":"season_version","name":"类型","value":[{"v":'-1',"n":"全部"},{"v":'1',"n":"正片"},{"v":'2',"n":"电影"},{"v":'3',"n":"其他"}]},{"key":"area","name":"地区","value":[{"v":'-1',"n":"全部"},{"v":'2',"n":"日本"},{"v":'3',"n":"美国"},{"v":"1,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70","n":"其他"}]},{"key":"is_finish","name":"状态","value":[{"v":'-1',"n":"全部"},{"v":'1',"n":"完结"},{"v":'0',"n":"连载"}]},{"key":"copyright","name":"版权","value":[{"v":'-1',"n":"全部"},{"v":'3',"n":"独家"},{"v":"1,2,4","n":"其他"}]},{"key":"season_status","name":"付费","value":[{"v":'-1',"n":"全部"},{"v":'1',"n":"免费"},{"v":"2,6","n":"付费"},{"v":"4,6","n":"大会员"}]},{"key":"season_month","name":"季度","value":[{"v":'-1',"n":"全部"},{"v":'1',"n":"1月"},{"v":'4',"n":"4月"},{"v":'7',"n":"7月"},{"v":'10',"n":"10月"}]},{"key":"year","name":"年份","value":[{"v":'-1',"n":"全部"},{"v":"[2023,2024)","n":"2023"},{"v":"[2022,2023)","n":"2022"},{"v":"[2021,2022)","n":"2021"},{"v":"[2020,2021)","n":"2020"},{"v":"[2019,2020)","n":"2019"},{"v":"[2018,2019)","n":"2018"},{"v":"[2017,2018)","n":"2017"},{"v":"[2016,2017)","n":"2016"},{"v":"[2015,2016)","n":"2015"},{"v":"[2010,2015)","n":"2014-2010"},{"v":"[2005,2010)","n":"2009-2005"},{"v":"[2000,2005)","n":"2004-2000"},{"v":"[1990,2000)","n":"90年代"},{"v":"[1980,1990)","n":"80年代"},{"v":"[,1980)","n":"更早"}]},{"key":"style_id","name":"风格","value":[{"v":'-1',"n":"全部"},{"v":'10010',"n":"原创"},{"v":'10011',"n":"漫画改"},{"v":'10012',"n":"小说改"},{"v":'10013',"n":"游戏改"},{"v":'10102',"n":"特摄"},{"v":'10015',"n":"布袋戏"},{"v":'10016',"n":"热血"},{"v":'10017',"n":"穿越"},{"v":'10018',"n":"奇幻"},{"v":'10020',"n":"战斗"},{"v":'10021',"n":"搞笑"},{"v":'10022',"n":"日常"},{"v":'10023',"n":"科幻"},{"v":'10024',"n":"萌系"},{"v":'10025',"n":"治愈"},{"v":'10026',"n":"校园"},{"v":'10027',"n":"少儿"},{"v":'10028',"n":"泡面"},{"v":'10029',"n":"恋爱"},{"v":'10030',"n":"少女"},{"v":'10031',"n":"魔法"},{"v":'10032',"n":"冒险"},{"v":'10033',"n":"历史"},{"v":'10034',"n":"架空"},{"v":'10035',"n":"机战"},{"v":'10036',"n":"神魔"},{"v":'10037',"n":"声控"},{"v":'10038',"n":"运动"},{"v":'10039',"n":"励志"},{"v":'10040',"n":"音乐"},{"v":'10041',"n":"推理"},{"v":'10042',"n":"社团"},{"v":'10043',"n":"智斗"},{"v":'10044',"n":"催泪"},{"v":'10045',"n":"美食"},{"v":'10046',"n":"偶像"},{"v":'10047',"n":"乙女"},{"v":'10048',"n":"职场"}]}],"4":[{"key":"season_version","name":"类型","value":[{"v":'-1',"n":"全部"},{"v":'1',"n":"正片"},{"v":'2',"n":"电影"},{"v":'3',"n":"其他"}]},{"key":"area","name":"地区","value":[{"v":'-1',"n":"全部"},{"v":'2',"n":"日本"},{"v":'3',"n":"美国"},{"v":"1,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70","n":"其他"}]},{"key":"is_finish","name":"状态","value":[{"v":'-1',"n":"全部"},{"v":'1',"n":"完结"},{"v":'0',"n":"连载"}]},{"key":"copyright","name":"版权","value":[{"v":'-1',"n":"全部"},{"v":'3',"n":"独家"},{"v":"1,2,4","n":"其他"}]},{"key":"season_status","name":"付费","value":[{"v":'-1',"n":"全部"},{"v":'1',"n":"免费"},{"v":"2,6","n":"付费"},{"v":"4,6","n":"大会员"}]},{"key":"year","name":"年份","value":[{"v":'-1',"n":"全部"},{"v":"[2023,2024)","n":"2023"},{"v":"[2022,2023)","n":"2022"},{"v":"[2021,2022)","n":"2021"},{"v":"[2020,2021)","n":"2020"},{"v":"[2019,2020)","n":"2019"},{"v":"[2018,2019)","n":"2018"},{"v":"[2017,2018)","n":"2017"},{"v":"[2016,2017)","n":"2016"},{"v":"[2015,2016)","n":"2015"},{"v":"[2010,2015)","n":"2014-2010"},{"v":"[2005,2010)","n":"2009-2005"},{"v":"[2000,2005)","n":"2004-2000"},{"v":"[1990,2000)","n":"90年代"},{"v":"[1980,1990)","n":"80年代"},{"v":"[,1980)","n":"更早"}]},{"key":"style_id","name":"风格","value":[{"v":'-1',"n":"全部"},{"v":'10010',"n":"原创"},{"v":'10011',"n":"漫画改"},{"v":'10012',"n":"小说改"},{"v":'10013',"n":"游戏改"},{"v":'10014',"n":"动态漫"},{"v":'10015',"n":"布袋戏"},{"v":'10016',"n":"热血"},{"v":'10018',"n":"奇幻"},{"v":'10019',"n":"玄幻"},{"v":'10020',"n":"战斗"},{"v":'10021',"n":"搞笑"},{"v":'10078',"n":"武侠"},{"v":'10022',"n":"日常"},{"v":'10023',"n":"科幻"},{"v":'10024',"n":"萌系"},{"v":'10025',"n":"治愈"},{"v":'10057',"n":"悬疑"},{"v":'10026',"n":"校园"},{"v":'10027',"n":"少儿"},{"v":'10028',"n":"泡面"},{"v":'10029',"n":"恋爱"},{"v":'10030',"n":"少女"},{"v":'10031',"n":"魔法"},{"v":'10033',"n":"历史"},{"v":'10035',"n":"机战"},{"v":'10036',"n":"神魔"},{"v":'10037',"n":"声控"},{"v":'10038',"n":"运动"},{"v":'10039',"n":"励志"},{"v":'10040',"n":"音乐"},{"v":'10041',"n":"推理"},{"v":'10042',"n":"社团"},{"v":'10043',"n":"智斗"},{"v":'10044',"n":"催泪"},{"v":'10045',"n":"美食"},{"v":'10046',"n":"偶像"},{"v":'10047',"n":"乙女"},{"v":'10048',"n":"职场"},{"v":'10049',"n":"古风"}]}],"2":[{"key":"area","name":"地区","value":[{"v":'-1',"n":"全部"},{"v":'1',"n":"中国大陆"},{"v":"6,7","n":"中国港台"},{"v":'3',"n":"美国"},{"v":'2',"n":"日本"},{"v":'8',"n":"韩国"},{"v":'9',"n":"法国"},{"v":'4',"n":"英国"},{"v":'15',"n":"德国"},{"v":'10',"n":"泰国"},{"v":'35',"n":"意大利"},{"v":'13',"n":"西班牙"},{"v":"5,11,12,14,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70","n":"其他"}]},{"key":"season_status","name":"付费","value":[{"v":'-1',"n":"全部"},{"v":'1',"n":"免费"},{"v":"2,6","n":"付费"},{"v":"4,6","n":"大会员"}]},{"key":"style_id","name":"风格","value":[{"v":'-1',"n":"全部"},{"v":'10104',"n":"短片"},{"v":'10050',"n":"剧情"},{"v":'10051',"n":"喜剧"},{"v":'10052',"n":"爱情"},{"v":'10053',"n":"动作"},{"v":'10054',"n":"恐怖"},{"v":'10023',"n":"科幻"},{"v":'10055',"n":"犯罪"},{"v":'10056',"n":"惊悚"},{"v":'10057',"n":"悬疑"},{"v":'10018',"n":"奇幻"},{"v":'10058',"n":"战争"},{"v":'10059',"n":"动画"},{"v":'10060',"n":"传记"},{"v":'10061',"n":"家庭"},{"v":'10062',"n":"歌舞"},{"v":'10033',"n":"历史"},{"v":'10032',"n":"冒险"},{"v":'10063',"n":"纪实"},{"v":'10064',"n":"灾难"},{"v":'10011',"n":"漫画改"},{"v":'10012',"n":"小说改"}]},{"key":"release_date","name":"年份","value":[{"v":'-1',"n":"全部"},{"v":"[2023-01-01 00:00:00,2024-01-01 00:00:00)","n":"2023"},{"v":"[2022-01-01 00:00:00,2023-01-01 00:00:00)","n":"2022"},{"v":"[2021-01-01 00:00:00,2022-01-01 00:00:00)","n":"2021"},{"v":"[2020-01-01 00:00:00,2021-01-01 00:00:00)","n":"2020"},{"v":"[2019-01-01 00:00:00,2020-01-01 00:00:00)","n":"2019"},{"v":"[2018-01-01 00:00:00,2019-01-01 00:00:00)","n":"2018"},{"v":"[2017-01-01 00:00:00,2018-01-01 00:00:00)","n":"2017"},{"v":"[2016-01-01 00:00:00,2017-01-01 00:00:00)","n":"2016"},{"v":"[2010-01-01 00:00:00,2016-01-01 00:00:00)","n":"2015-2010"},{"v":"[2005-01-01 00:00:00,2010-01-01 00:00:00)","n":"2009-2005"},{"v":"[2000-01-01 00:00:00,2005-01-01 00:00:00)","n":"2004-2000"},{"v":"[1990-01-01 00:00:00,2000-01-01 00:00:00)","n":"90年代"},{"v":"[1980-01-01 00:00:00,1990-01-01 00:00:00)","n":"80年代"},{"v":"[,1980-01-01 00:00:00)","n":"更早"}]}],"5":[{"key":"area","name":"地区","value":[{"v":'-1',"n":"全部"},{"v":"1,6,7","n":"中国"},{"v":'2',"n":"日本"},{"v":'3',"n":"美国"},{"v":'4',"n":"英国"},{"v":'10',"n":"泰国"},{"v":"5,8,9,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70","n":"其他"}]},{"key":"season_status","name":"付费","value":[{"v":'-1',"n":"全部"},{"v":'1',"n":"免费"},{"v":"2,6","n":"付费"},{"v":"4,6","n":"大会员"}]},{"key":"style_id","name":"风格","value":[{"v":'-1',"n":"全部"},{"v":'10021',"n":"搞笑"},{"v":'10018',"n":"奇幻"},{"v":'10058',"n":"战争"},{"v":'10078',"n":"武侠"},{"v":'10079',"n":"青春"},{"v":'10103',"n":"短剧"},{"v":'10080',"n":"都市"},{"v":'10081',"n":"古装"},{"v":'10082',"n":"谍战"},{"v":'10083',"n":"经典"},{"v":'10084',"n":"情感"},{"v":'10057',"n":"悬疑"},{"v":'10039',"n":"励志"},{"v":'10085',"n":"神话"},{"v":'10017',"n":"穿越"},{"v":'10086',"n":"年代"},{"v":'10087',"n":"农村"},{"v":'10088',"n":"刑侦"},{"v":'10050',"n":"剧情"},{"v":'10061',"n":"家庭"},{"v":'10033',"n":"历史"},{"v":'10089',"n":"军旅"},{"v":'10023',"n":"科幻"}]},{"key":"release_date","name":"年份","value":[{"v":'-1',"n":"全部"},{"v":"[2023-01-01 00:00:00,2024-01-01 00:00:00)","n":"2023"},{"v":"[2022-01-01 00:00:00,2023-01-01 00:00:00)","n":"2022"},{"v":"[2021-01-01 00:00:00,2022-01-01 00:00:00)","n":"2021"},{"v":"[2020-01-01 00:00:00,2021-01-01 00:00:00)","n":"2020"},{"v":"[2019-01-01 00:00:00,2020-01-01 00:00:00)","n":"2019"},{"v":"[2018-01-01 00:00:00,2019-01-01 00:00:00)","n":"2018"},{"v":"[2017-01-01 00:00:00,2018-01-01 00:00:00)","n":"2017"},{"v":"[2016-01-01 00:00:00,2017-01-01 00:00:00)","n":"2016"},{"v":"[2010-01-01 00:00:00,2016-01-01 00:00:00)","n":"2015-2010"},{"v":"[2005-01-01 00:00:00,2010-01-01 00:00:00)","n":"2009-2005"},{"v":"[2000-01-01 00:00:00,2005-01-01 00:00:00)","n":"2004-2000"},{"v":"[1990-01-01 00:00:00,2000-01-01 00:00:00)","n":"90年代"},{"v":"[1980-01-01 00:00:00,1990-01-01 00:00:00)","n":"80年代"},{"v":"[,1980-01-01 00:00:00)","n":"更早"}]}],"7":[{"key":"season_status","name":"付费","value":[{"v":'-1',"n":"全部"},{"v":'1',"n":"免费"},{"v":"2,6","n":"付费"},{"v":"4,6","n":"大会员"}]},{"key":"style_id","name":"风格","value":[{"v":'-1',"n":"全部"},{"v":'10040',"n":"音乐"},{"v":'10090',"n":"访谈"},{"v":'10091',"n":"脱口秀"},{"v":'10092',"n":"真人秀"},{"v":'10094',"n":"选秀"},{"v":'10045',"n":"美食"},{"v":'10095',"n":"旅游"},{"v":'10098',"n":"晚会"},{"v":'10096',"n":"演唱会"},{"v":'10084',"n":"情感"},{"v":'10051',"n":"喜剧"},{"v":'10097',"n":"亲子"},{"v":'10100',"n":"文化"},{"v":'10048',"n":"职场"},{"v":'10069',"n":"萌宠"},{"v":'10099',"n":"养成"}]}]}
	}