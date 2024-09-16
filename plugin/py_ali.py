#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import json
import requests
import time
import re

class Spider(Spider):  # 元类 默认的元类 type
	def getName(self):
		return "阿里云盘"
	def init(self,extend=""):
		print("============{0}============".format(extend))
		pass
	def homeContent(self,filter):
		result = {}
		return result
	def homeVideoContent(self):
		result = {}
		return result
	def categoryContent(self,tid,pg,filter,extend):
		result = {}
		return result
	def searchContent(self,key,quick):
		result = {}
		return result
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def playerContent(self,flag,id,vipFlags):
		if flag == 'AliYun':
			return self.originContent(flag,id,vipFlags)
		elif flag == 'AliYun原画':
			return self.fhdContent(flag,id,vipFlags)
		else:
			return 	{}		
	def fhdContent(self,flag,id,vipFlags):
		self.login()
		ids = id.split('+')
		shareId = ids[0]
		shareToken = ids[1]
		fileId = ids[2]
		category = ids[3]
		url = self.getDownloadUrl(shareId,shareToken,fileId,category)
		print(url)

		noRsp = requests.get(url,headers=self.header, allow_redirects=False,verify = False)
		realUrl = ''
		if 'Location' in noRsp.headers:
			realUrl = noRsp.headers['Location']
		if 'location' in noRsp.headers and len(realUrl) == 0 :
			realUrl = noRsp.headers['location']
		newHeader = {
			"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
			"referer":"https://www.aliyundrive.com/",
		}
		result = {
			'parse':'0',
			'playUrl':'',
			'url':realUrl,
			'header':newHeader
		}
		return result
	def originContent(self,flag,id,vipFlags):
		self.login()
		ids = id.split('+')
		shareId = ids[0]
		shareToken = ids[1]
		fileId = ids[2]
		url = '{0}?do=push_agent&api=python&type=m3u8&share_id={1}&file_id={2}'.format(self.localProxyUrl,shareId,fileId)

		result = {
			'parse':'0',
			'playUrl':'',
			'url':url,
			'header':''
		}

		# shareToken = self.getToken(shareId,'')
		# self.getMediaSlice(shareId,shareToken,fileId)


		# map = {
		# 	'share_id':'p1GJYEqgeb2',
		# 	'file_id':'62ed1b95b1048d60ffc246669f5e0999e90b8c2f',
		# 	'media_id':'1'
		# }

		# self.proxyMedia(map)

		return result

	def detailContent(self,array):
		tid = array[0]
		# shareId = self.regStr(href,'www.aliyundrive.com\\/s\\/([^\\/]+)(\\/folder\\/([^\\/]+))?')
		# todo =========================================================================================
		m = re.search('www.aliyundrive.com\\/s\\/([^\\/]+)(\\/folder\\/([^\\/]+))?', tid)
		col = m.groups()
		shareId = col[0]
		fileId = col[2]

		infoUrl = 'https://api.aliyundrive.com/adrive/v3/share_link/get_share_by_anonymous'

		infoForm = {'share_id':shareId}
		infoRsp = requests.post(infoUrl,json = infoForm,headers=self.header)
		infoJo = json.loads(infoRsp.text)

		infoJa = []
		if 'file_infos' in infoJo:
			infoJa = infoJo['file_infos']
		if len(infoJa) <= 0 :
			return ''
		fileInfo = {}
		# todo
		fileInfo = infoJa[0]
		print(fileId)
		if fileId == None or len(fileId) <= 0:
			fileId = fileInfo['file_id']

		vodList = {
			'vod_id':tid,
			'vod_name':infoJo['share_name'],
			'vod_pic':infoJo['avatar'],
			'vod_content':tid,
			'vod_play_from':'AliYun原画'
		}
		fileType = fileInfo['type']
		if fileType != 'folder':
			if fileType != 'file' or fileInfo['category'] != video:
				return ''
			fileId = 'root'

		shareToken = self.getToken(shareId,'')
		hashMap = {}
		self.listFiles(hashMap,shareId,shareToken,fileId)

		sortedMap = sorted(hashMap.items(), key=lambda x: x[0])
		arrayList = []
		playList = []

		for sm in sortedMap:
			arrayList.append(sm[0]+'$'+sm[1])
		playList.append('#'.join(arrayList))
		playList.append('#'.join(arrayList))
		vodList['vod_play_url'] = '$$$'.join(playList)

		result = {
			'list':[vodList]
		}
		return result
		
	authorization = ''
	timeoutTick = 0
	localTime = 0
	expiresIn = 0
	shareTokenMap = {}
	expiresMap = {}
	localMedia = {}
	header = {
		"Referer":"https://www.aliyundrive.com/",
		"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36"
	}
	localProxyUrl = 'http://127.0.0.1:UndCover/proxy'

	def redirectResponse(tUrl):
		rsp = requests.get(tUrl, allow_redirects=False,verify = False)
		if 'Location' in rsp.headers:
			return redirectResponse(rsp.headers['Location'])
		else:
			return rsp

	def getDownloadUrl(self,shareId,token,fileId,category):
		lShareId = shareId
		lFileId = fileId
		params = {
			"share_id": lShareId,
			"category": "live_transcoding",
			"file_id": lFileId,
			"template_id": ""
		}
		customHeader = self.header.copy()
		customHeader['x-share-token'] = token
		customHeader['authorization'] = self.authorization
		url = 'https://api.aliyundrive.com/v2/file/get_share_link_video_preview_play_info'
		if category == 'video':
			rsp = requests.post(url,json = params,headers=customHeader)
			rspJo = json.loads(rsp.text)
			lShareId = rspJo['share_id']
			lFileId = rspJo['file_id']
		jo = {

		}
		if category == 'video':
			jo['share_id'] = lShareId
			jo['file_id'] = lFileId
			jo['expire_sec'] = 600
		if category == 'audio':
			jo['share_id'] = lShareId
			jo['file_id'] = lFileId
			jo['get_audio_play_info'] = True
		downloadUrl = 'https://api.aliyundrive.com/v2/file/get_share_link_download_url'
		downloadRsp = requests.post(downloadUrl,json = jo,headers=customHeader)
		resultJo = json.loads(downloadRsp.text)
		return resultJo['download_url']

	def getMediaSlice(self,shareId,token,fileId):
		params = {
			"share_id": shareId,
			"category": "live_transcoding",
			"file_id": fileId,
			"template_id": ""
		}
		customHeader = self.header.copy()
		customHeader['x-share-token'] = token
		customHeader['authorization'] = self.authorization
		url = 'https://api.aliyundrive.com/v2/file/get_share_link_video_preview_play_info'

		rsp = requests.post(url,json = params,headers=customHeader)
		rspJo = json.loads(rsp.text)

		quality = ['FHD','HD','SD']
		videoList = rspJo['video_preview_play_info']['live_transcoding_task_list']
		highUrl = ''
		for q in quality:
			if len(highUrl) > 0:
				break
			for video in videoList:
				if(video['template_id'] == q):
					highUrl = video['url']
					break
			if len(highUrl) == 0:
				highUrl = videoList[0]['url']

		noRsp = requests.get(highUrl,headers=self.header, allow_redirects=False,verify = False)
		m3u8Url = ''
		if 'Location' in noRsp.headers:
			m3u8Url = noRsp.headers['Location']
		if 'location' in noRsp.headers and len(m3u8Url) == 0 :
			m3u8Url = noRsp.headers['location']
		m3u8Rsp = requests.get(m3u8Url,headers=self.header)
		m3u8Content = m3u8Rsp.text

		tmpArray = m3u8Url.split('/')[0:-1]
		host = '/'.join(tmpArray) + '/'

		m3u8List = []
		mediaMap = {}
		slices = m3u8Content.split("\n")
		count = 0
		for slice in slices:
			tmpSlice = slice
			if 'x-oss-expires' in tmpSlice:
				count = count + 1
				mediaMap[str(count)] = host+tmpSlice

				tmpSlice = "{0}?do=push_agent&api=python&type=media&share_id={1}&file_id={2}&media_id={3}".format(self.localProxyUrl,shareId,fileId,count)
			m3u8List.append(tmpSlice)

		self.localMedia[fileId] = mediaMap
		
		return '\n'.join(m3u8List)

	def proxyMedia(self,map):
		shareId = map['share_id']
		fileId = map['file_id']
		mediaId = map['media_id']
		shareToken = self.getToken(shareId,'')

		refresh = False
		url = ''
		ts = 0
		if fileId in self.localMedia:
			fileMap = self.localMedia[fileId]
			if mediaId in fileMap:
				url = fileMap[mediaId]
		if len(url) > 0:
			ts = int(self.regStr(url,"x-oss-expires=(\\d+)&"))

		# url = self.localMedia[fileId][mediaId]
		
		# ts = int(self.regStr(url,"x-oss-expires=(\\d+)&"))

		self.localTime = int(time.time())

		if ts - self.localTime <= 60:
			self.getMediaSlice(shareId,shareToken,fileId)
			url = self.localMedia[fileId][mediaId]
			
		action = {
			'url':url,
			'header':self.header,
			'param':'',
			'type':'stream',
			'after':''
		}
		print(action)
		return [200, "video/MP2T", action, ""]

	def proxyM3U8(self,map):
		shareId = map['share_id']
		fileId = map['file_id']

		shareToken = self.getToken(shareId,'')
		content = self.getMediaSlice(shareId,shareToken,fileId)

		action = {
			'url':'',
			'header':'',
			'param':'',
			'type':'string',
			'after':''
		}

		return [200, "application/octet-stream", action, content]

	def localProxy(self,param):
		typ = param['type']
		if typ == "m3u8":
			return self.proxyM3U8(param)
		if typ == "media":
			return self.proxyMedia(param)
		return None

	def getToken(self,shareId,sharePwd):
		self.localTime = int(time.time())
		shareToken = ''
		if shareId in self.shareTokenMap:
			shareToken = self.shareTokenMap[shareId]
			# todo
			expire = self.expiresMap[shareId]
			if len(shareToken) > 0 and expire - self.localTime > 600:
				return shareToken
		params = {
			'share_id':shareId,
			'share_pwd':sharePwd
		}
		url = 'https://api.aliyundrive.com/v2/share_link/get_share_token'
		rsp = requests.post(url,json = params,headers=self.header)
		jo = json.loads(rsp.text)
		newShareToken = jo['share_token']
		self.expiresMap[shareId] = self.localTime + int(jo['expires_in'])
		self.shareTokenMap[shareId] = newShareToken

		print(self.expiresMap)
		print(self.shareTokenMap)

		return newShareToken

	def listFiles(self,map,shareId,shareToken,fileId):
		url = 'https://api.aliyundrive.com/adrive/v3/file/list'
		newHeader = self.header.copy()
		newHeader['x-share-token'] = shareToken
		params = {
			'image_thumbnail_process':'image/resize,w_160/format,jpeg',
			'image_url_process':'image/resize,w_1920/format,jpeg',
			'limit':200,
			'order_by':'updated_at',
			'order_direction':'DESC',
			'parent_file_id':fileId,
			'share_id':shareId,
			'video_thumbnail_process':'video/snapshot,t_1000,f_jpg,ar_auto,w_300'
		}
		maker = ''
		arrayList = []
		for i in range(1,51):
			if i >= 2 and len(maker) == 0:
				break
			params['marker'] = maker			
			rsp = requests.post(url,json = params,headers=newHeader)
			jo = json.loads(rsp.text)
			ja = jo['items']
			for jt in ja:
				if jt['type'] == 'folder':
					arrayList.append(jt['file_id'])
				else:
					if 'video' in jt['mime_type'] or 'video' in jt['category']:
						repStr = jt['name'].replace("#", "_").replace("$", "_")
						map[repStr] = shareId + "+" + shareToken + "+" + jt['file_id'] + "+" + jt['category']
						# print(repStr,shareId + "+" + shareToken + "+" + jt['file_id'])
			maker = jo['next_marker']
			i = i + 1

		for item in arrayList:
			self.listFiles(map,shareId,shareToken,item)

	def login(self):
		self.localTime = int(time.time())
		url = 'https://api.aliyundrive.com/token/refresh'
		if len(self.authorization) == 0 or self.timeoutTick - self.localTime <= 600:
			form = {
				'refresh_token':'81461f2e9d0b4ffb86612db403824b8a'
			}
			rsp = requests.post(url,json = form,headers=self.header)
			jo = json.loads(rsp.text)
			self.authorization = jo['token_type'] + ' ' + jo['access_token']
			self.expiresIn = int(jo['expires_in'])
			self.timeoutTick = self.localTime + self.expiresIn

			# print(self.authorization)
			# print(self.timeoutTick)
			# print(self.localTime)
			# print(self.expiresIn)