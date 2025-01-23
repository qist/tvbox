#coding=utf-8
#!/usr/bin/python
import sys
import json
import time
import requests
from uuid import uuid4
from urllib.parse import quote

sys.path.append('..')
from base.spider import Spider

class Spider(Spider):
	def getName(self):
		return "EMBY"

	def init(self, extend):
		try:
			extendDict = json.loads(extend)
			self.baseUrl = extendDict['server'].strip('/')
			self.username = extendDict['username']
			self.password = extendDict['password']
			self.thread = extendDict['thread'] if 'thread' in extendDict else 0
		except:
			self.baseUrl = ''
			self.username = ''
			self.password = ''
			self.thread = 0

	def destroy(self):
		pass

	def isVideoFormat(self, url):
		pass

	def manualVideoCheck(self):
		pass

	def homeContent(self, filter):
		try:
			embyInfos = self.getAccessToken()
		except:
			return {'msg': '获取Emby服务器信息出错'}

		header = self.header.copy()
		header['Content-Type'] = "application/json; charset=UTF-8"
		url = f"{self.baseUrl}/emby/Users/{embyInfos['User']['Id']}/Views"
		params = {
			"X-Emby-Client": embyInfos['SessionInfo']['Client'],
			"X-Emby-Device-Name": embyInfos['SessionInfo']['DeviceName'],
			"X-Emby-Device-Id": embyInfos['SessionInfo']['DeviceId'],
			"X-Emby-Client-Version": embyInfos['SessionInfo']['ApplicationVersion'],
			"X-Emby-Token": embyInfos['AccessToken']
		}
		r = requests.get(url, params=params, headers=header, timeout=30)
		typeInfos = r.json()["Items"]
		classList = []
		for typeInfo in typeInfos:
			if "播放列表" in typeInfo['Name'] or '相机' in typeInfo['Name']:
				continue
			classList.append({"type_name": typeInfo['Name'], "type_id": typeInfo['Id']})
		result = {'class': classList}
		return result

	def homeVideoContent(self):
		return {}

	def categoryContent(self, cid, page, filter, ext):
		try:
			embyInfos = self.getAccessToken()
		except:
			return {'list': [], 'msg': '获取Emby服务器信息出错'}

		result = {}
		page = int(page)
		header = self.header.copy()
		header['Content-Type'] = "application/json; charset=UTF-8"
		url = f"{self.baseUrl}/emby/Users/{embyInfos['User']['Id']}/Items"
		params = {
			"X-Emby-Client": embyInfos['SessionInfo']['Client'],
			"X-Emby-Device-Name": embyInfos['SessionInfo']['DeviceName'],
			"X-Emby-Device-Id": embyInfos['SessionInfo']['DeviceId'],
			"X-Emby-Client-Version": embyInfos['SessionInfo']['ApplicationVersion'],
			"X-Emby-Token": embyInfos['AccessToken'],
			"SortBy": "DateLastContentAdded,SortName",
			"IncludeItemTypes": "Movie,Series",
			"SortOrder": "Descending",
			"ParentId": cid,
			"Recursive": "true",
			"Limit": "30",
			"ImageTypeLimit": 1,
			"StartIndex": str((page - 1) * 30),
			"EnableImageTypes": "Primary,Backdrop,Thumb,Banner",
			"Fields": "BasicSyncInfo,CanDelete,Container,PrimaryImageAspectRatio,ProductionYear,CommunityRating,Status,CriticRating,EndDate,Path",
			"EnableUserData": "true"
		}
		r = requests.get(url, params=params, headers=header, timeout=30)
		videoList = r.json()['Items']
		videos = []
		for video in videoList:
			name = self.cleanText(video['Name'])
			videos.append({
				"vod_id": video['Id'],
				"vod_name": name,
				"vod_pic": f"{self.baseUrl}/emby/Items/{video['Id']}/Images/Primary?maxWidth=400&tag={video['ImageTags']['Primary']}&quality=90" if 'Primary' in video['ImageTags'] else '',
				"vod_remarks": video['ProductionYear'] if 'ProductionYear' in video else ''
			})
		result['list'] = videos
		result['page'] = page
		result['pagecount'] = page + 1 if page * 30 < int(r.json()['TotalRecordCount']) else page
		result['limit'] = len(videos)
		result['total'] = int(r.json()['TotalRecordCount']) if "TotalRecordCount" in r.json() else 0
		return result

	def detailContent(self, did):
		try:
			embyInfos = self.getAccessToken()
		except:
			return {'list': [], 'msg': '获取Emby服务器信息出错'}

		header = self.header.copy()
		header['Content-Type'] = "application/json; charset=UTF-8"
		url = f"{self.baseUrl}/emby/Users/{embyInfos['User']['Id']}/Items/{did[0]}"
		params = {
			"X-Emby-Client": embyInfos['SessionInfo']['Client'],
			"X-Emby-Device-Name": embyInfos['SessionInfo']['DeviceName'],
			"X-Emby-Device-Id": embyInfos['SessionInfo']['DeviceId'],
			"X-Emby-Client-Version": embyInfos['SessionInfo']['ApplicationVersion'],
			"X-Emby-Token": embyInfos['AccessToken']
		}
		r = requests.get(url, params=params, headers=header, timeout=30)
		videoInfos = r.json()
		vod = {
			"vod_id": did[0],
			"vod_name": videoInfos['Name'],
			"vod_pic": f'{self.baseUrl}/emby/Items/{did[0]}/Images/Primary?maxWidth=400&tag={videoInfos["ImageTags"]["Primary"]}&quality=90' if 'Primary' in videoInfos['ImageTags'] else '',
			"type_name": videoInfos['Genres'][0] if len(videoInfos['Genres']) > 0 else '',
			"vod_year": videoInfos['ProductionYear'] if 'ProductionYear' in videoInfos else '',
			"vod_content": videoInfos['Overview'].replace('\xa0', ' ').replace('\n\n', '\n').strip() if 'Overview' in videoInfos else '',
			"vod_play_from": "EMBY"
		}
		playUrl = ''
		if not videoInfos['IsFolder']:
			playUrl += f"{videoInfos['Name'].strip()}${videoInfos['Id']}#"
		else:
			url = f"{self.baseUrl}/emby/Shows/{did[0]}/Seasons"
			params.update(
				{
					"UserId": embyInfos['User']['Id'],
					"EnableImages": "true",
					"Fields": "BasicSyncInfo,CanDelete,Container,PrimaryImageAspectRatio,ProductionYear,CommunityRating",
					"EnableUserData": "true",
					"EnableTotalRecordCount": "false"
				}
			)
			r = requests.get(url, params=params, headers=header, timeout=30)
			if r.status_code == 200:
				playInfos = r.json()['Items']
				for playInfo in playInfos:
					url = f"{self.baseUrl}/emby/Shows/{playInfo['Id']}/Episodes"
					params.update(
						{
							"SeasonId": playInfo['Id'],
							"Fields": "BasicSyncInfo,CanDelete,CommunityRating,PrimaryImageAspectRatio,ProductionYear,Overview"
						}
					)
					r = requests.get(url, params=params, headers=header, timeout=30)
					videoList = r.json()['Items']
					for video in videoList:
						playUrl += f"{playInfo['Name'].replace('#', '-').replace('$', '|').strip()}|{video['Name'].strip()}${video['Id']}#"
			else:
				url = f"{self.baseUrl}/emby/Users/{embyInfos['User']['Id']}/Items"
				params = {
					"ParentId": did[0],
					"Fields": "BasicSyncInfo,CanDelete,Container,PrimaryImageAspectRatio,ProductionYear,CommunityRating,CriticRating",
					"ImageTypeLimit": "1",
					"StartIndex": "0",
					"EnableUserData": "true",
					"X-Emby-Client": embyInfos['SessionInfo']['Client'],
					"X-Emby-Device-Name": embyInfos['SessionInfo']['DeviceName'],
					"X-Emby-Device-Id": embyInfos['SessionInfo']['DeviceId'],
					"X-Emby-Client-Version": embyInfos['SessionInfo']['ApplicationVersion'],
					"X-Emby-Token": embyInfos['AccessToken']
				}
				r = requests.get(url, params=params, headers=header, timeout=30)
				videoList = r.json()['Items']
				for video in videoList:
					playUrl += f"{video['Name'].replace('#', '-').replace('$', '|').strip()}${video['Id']}#"
		vod['vod_play_url'] = playUrl.strip('#')
		result = {'list': [vod]}
		return result

	def searchContent(self, key, quick):
		return self.searchContentPage(key, quick, '1')

	def searchContentPage(self, keywords, quick, page):
		try:
			embyInfos = self.getAccessToken()
		except:
			return {'list': [], 'msg': '获取Emby服务器信息出错'}
		page = int(page)
		header = self.header.copy()
		header['Content-Type'] = "application/json; charset=UTF-8"
		url = f"{self.baseUrl}/emby/Users/{embyInfos['User']['Id']}/Items"
		params = {
			"X-Emby-Client": embyInfos['SessionInfo']['Client'],
			"X-Emby-Device-Name": embyInfos['SessionInfo']['DeviceName'],
			"X-Emby-Device-Id": embyInfos['SessionInfo']['DeviceId'],
			"X-Emby-Client-Version": embyInfos['SessionInfo']['ApplicationVersion'],
			"X-Emby-Token": embyInfos['AccessToken'],
			"SortBy": "SortName",
			"SortOrder": "Ascending",
			"Fields": "BasicSyncInfo,CanDelete,Container,PrimaryImageAspectRatio,ProductionYear,Status,EndDate",
			"StartIndex": str(((page-1)*50)),
			"EnableImageTypes": "Primary,Backdrop,Thumb",
			"ImageTypeLimit": "1",
			"Recursive": "true",
			"SearchTerm": keywords,
			"IncludeItemTypes": "Movie,Series,BoxSet",
			"GroupProgramsBySeries": "true",
			"Limit": "50",
			"EnableTotalRecordCount": "true"
		}
		r = requests.get(url, params=params, headers=header, timeout=30)

		videos = []
		vodList = r.json()['Items']
		for vod in vodList:
			sid = vod['Id']
			name = self.cleanText(vod['Name'])
			pic = f'{self.baseUrl}/emby/Items/{sid}/Images/Primary?maxWidth=400&tag={vod["ImageTags"]["Primary"]}&quality=90' if 'Primary' in vod["ImageTags"] else ''
			videos.append({
				"vod_id": sid,
				"vod_name": name,
				"vod_pic": pic,
				"vod_remarks": vod['ProductionYear'] if 'ProductionYear' in vod else ''
			})
		result = {'list': videos}
		return result

	def playerContent(self, flag, pid, vipFlags):
		try:
			embyInfos = self.getAccessToken()
		except:
			return {'list': [], 'msg': '获取Emby服务器信息出错'}

		header = self.header.copy()
		header['Content-Type'] = "application/json; charset=UTF-8"
		url = f"{self.baseUrl}/emby/Items/{pid}/PlaybackInfo"
		params = {
			"UserId": embyInfos['User']['Id'],
			"IsPlayback": "false",
			"AutoOpenLiveStream": "false",
			"StartTimeTicks": 0,
			"MaxStreamingBitrate": "2147483647",
			"X-Emby-Client": embyInfos['SessionInfo']['Client'],
			"X-Emby-Device-Name": embyInfos['SessionInfo']['DeviceName'],
			"X-Emby-Device-Id": embyInfos['SessionInfo']['DeviceId'],
			"X-Emby-Client-Version": embyInfos['SessionInfo']['ApplicationVersion'],
			"X-Emby-Token": embyInfos['AccessToken']
		}
		data = "{\"DeviceProfile\":{\"SubtitleProfiles\":[{\"Method\":\"Embed\",\"Format\":\"ass\"},{\"Format\":\"ssa\",\"Method\":\"Embed\"},{\"Format\":\"subrip\",\"Method\":\"Embed\"},{\"Format\":\"sub\",\"Method\":\"Embed\"},{\"Method\":\"Embed\",\"Format\":\"pgssub\"},{\"Format\":\"subrip\",\"Method\":\"External\"},{\"Method\":\"External\",\"Format\":\"sub\"},{\"Method\":\"External\",\"Format\":\"ass\"},{\"Format\":\"ssa\",\"Method\":\"External\"},{\"Method\":\"External\",\"Format\":\"vtt\"},{\"Method\":\"External\",\"Format\":\"ass\"},{\"Format\":\"ssa\",\"Method\":\"External\"}],\"CodecProfiles\":[{\"Codec\":\"h264\",\"Type\":\"Video\",\"ApplyConditions\":[{\"Property\":\"IsAnamorphic\",\"Value\":\"true\",\"Condition\":\"NotEquals\",\"IsRequired\":false},{\"IsRequired\":false,\"Value\":\"high|main|baseline|constrained baseline\",\"Condition\":\"EqualsAny\",\"Property\":\"VideoProfile\"},{\"IsRequired\":false,\"Value\":\"80\",\"Condition\":\"LessThanEqual\",\"Property\":\"VideoLevel\"},{\"IsRequired\":false,\"Value\":\"true\",\"Condition\":\"NotEquals\",\"Property\":\"IsInterlaced\"}]},{\"Codec\":\"hevc\",\"ApplyConditions\":[{\"Property\":\"IsAnamorphic\",\"Value\":\"true\",\"Condition\":\"NotEquals\",\"IsRequired\":false},{\"IsRequired\":false,\"Value\":\"high|main|main 10\",\"Condition\":\"EqualsAny\",\"Property\":\"VideoProfile\"},{\"Property\":\"VideoLevel\",\"Value\":\"175\",\"Condition\":\"LessThanEqual\",\"IsRequired\":false},{\"IsRequired\":false,\"Value\":\"true\",\"Condition\":\"NotEquals\",\"Property\":\"IsInterlaced\"}],\"Type\":\"Video\"}],\"MaxStreamingBitrate\":40000000,\"TranscodingProfiles\":[{\"Container\":\"ts\",\"AudioCodec\":\"aac,mp3,wav,ac3,eac3,flac,opus\",\"VideoCodec\":\"hevc,h264,mpeg4\",\"BreakOnNonKeyFrames\":true,\"Type\":\"Video\",\"MaxAudioChannels\":\"6\",\"Protocol\":\"hls\",\"Context\":\"Streaming\",\"MinSegments\":2}],\"DirectPlayProfiles\":[{\"Container\":\"mov,mp4,mkv,hls,webm\",\"Type\":\"Video\",\"VideoCodec\":\"h264,hevc,dvhe,dvh1,h264,hevc,hev1,mpeg4,vp9\",\"AudioCodec\":\"aac,mp3,wav,ac3,eac3,flac,truehd,dts,dca,opus,pcm,pcm_s24le\"}],\"ResponseProfiles\":[{\"MimeType\":\"video/mp4\",\"Type\":\"Video\",\"Container\":\"m4v\"}],\"ContainerProfiles\":[],\"MusicStreamingTranscodingBitrate\":40000000,\"MaxStaticBitrate\":40000000}}"
		r = requests.post(url, params=params, data=data, headers=header, timeout=30)
		url = self.baseUrl + r.json()['MediaSources'][0]['DirectStreamUrl']
		if int(self.thread) > 0:
			try:
				self.fetch('http://127.0.0.1:7777', timeout=1)
			except:
				self.fetch('http://127.0.0.1:9978/go')
			url = f'http://127.0.0.1:7777/?url={quote(url)}&thread={self.thread}'
		result = {
			"url": url,
			"header": self.header,
			"parse": 0
		}
		return result

	def localProxy(self, params):
		pass

	def getAccessToken(self):
		key = f"emby_{self.baseUrl}_{self.username}_{self.password }"
		embyInfos = self.getCache(key)
		if embyInfos:
			return embyInfos

		header = self.header.copy()
		header['Content-Type'] = "application/json; charset=UTF-8"
		r = requests.post(f"{self.baseUrl}/emby/Users/AuthenticateByName", params={"Username": self.username, "Password": self.password , "Pw": self.password , "X-Emby-Client": "Yamby", "X-Emby-Device-Name": "Yamby", "X-Emby-Device-Id": str(uuid4()), "X-Emby-Client-Version": "1.0.2"}, headers=header, timeout=30)
		embyInfos = r.json()
		self.setCache(key, embyInfos)
		return embyInfos

	header = {"User-Agent": "Yamby/1.0.2(Android"}

