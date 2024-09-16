#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import requests
import json

class Spider(Spider):
	def getDependence(self):
		return ['py_ali']
	def getName(self):
		return "py_gitcafe"
	def init(self,extend):
		self.ali = extend[0]
		print("============py_gitcafe============")
		pass
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def homeContent(self,filter):
		result = {}
		cateManual = {			
			"华语电视" :"hyds",
			"日韩电视" :"rhds",
			"欧美电视" :"omds",
			"其他电视" :"qtds",
			"华语电影" :"hydy",
			"日韩电影" :"rhdy",
			"欧美电影" :"omdy",
			"其他电影" :"qtdy",
			"华语动漫" :"hydm",
			"日韩动漫" :"rhdm",
			"欧美动漫" :"omdm",
			"纪录片" :"jlp",
			"综艺片" :"zyp",
			"教育培训" :"jypx",
			"其他视频" :"qtsp",
			"华语音乐" :"hyyy",
			"日韩音乐" :"rhyy",
			"欧美音乐" :"omyy",
			"其他音乐" :"qtyy"
		}
		classes = []
		for k in cateManual:
			classes.append({
				'type_name':k,
				'type_id':cateManual[k]
			})
		result['class'] = classes
		if filter:
			result['filter'] = self.config['filter']
		return result
	def homeVideoContent(self):
		result = {}
		if len(self.homeData.keys()) == 0:
			url = self.baseUrl+'/alipaper/home.json'
			self.homeData = self.fetch(url,headers=self.header).json()
		cateList = self.homeData['data']
		videos = []
		for cate in cateList:
			if cate['info']['code'] in self.category:
				vodList = cate['data']		
				for vod in vodList:
					videos.append({
						"vod_id":"https://www.aliyundrive.com/s/" + vod['key'],
						"vod_name":vod['title'],
						"vod_pic":'https://txc.gtimg.com/data/375895/2022/0214/d6b96cc3799b6417d30e4715d2973f64.png',
						"vod_remarks":''
					})
		result['list']=videos
		return result
	def categoryContent(self,tid,pg,filter,extend):
		result = {}
		url = self.baseUrl+'/tool/alipaper/'
		form = {
			"action": "viewcat",
			"cat": tid,
			"num":pg
		}
		
		rsp = requests.post(url,headers=self.header,data=form)
		vodList = json.loads(self.cleanText(rsp.text))
		videos = []
		for vod in vodList:
			videos.append({
				"vod_id": 'https://www.aliyundrive.com/s/'+vod["key"],
				"vod_name": vod["title"],
				"vod_pic": "https://txc.gtimg.com/data/375895/2022/0214/d6b96cc3799b6417d30e4715d2973f64.png",
				"vod_remarks": vod['cat']
			})
		result['list'] = videos
		result['page'] = pg
		result['pagecount'] = 9999
		result['limit'] = 90
		result['total'] = 999999
		return result
	category = ['hydm','hyds','hydy','omdm','omds','omdy','rhdm','rhds','rhdy','qtds','qtdy','qtsp','jlp','zyp']
	def detailContent(self,array):
		return self.ali.detailContent(array)
	def searchContent(self,key,quick):
		result = {}
		url = self.baseUrl+'/tool/alipaper/'
		form = {
			"action": "search",
			"keyword": key
		}
		vodList = requests.post(url,headers=self.header,data=form).json()
		videos = []
		for vod in vodList:
			videos.append({
				"vod_id": 'https://www.aliyundrive.com/s/'+vod["key"],
				"vod_name": vod["title"],
				"vod_pic": "https://txc.gtimg.com/data/375895/2022/0214/d6b96cc3799b6417d30e4715d2973f64.png",
				"vod_remarks": vod['cat']
			})
		result = {
			'list':videos
		}
		return result
	def playerContent(self,flag,id,vipFlags):
		return self.ali.playerContent(flag,id,vipFlags)

	homeData = {}
	baseUrl = 'https://gitcafe.net'
	config = {
		"player": {},
		"filter": {}
	}
	header = {
		"User-Agent": "Mozilla/5.0 (Linux; Android 12; V2049A Build/SP1A.210812.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36",
        "Referer": "https://u.gitcafe.net/"
	}
	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]