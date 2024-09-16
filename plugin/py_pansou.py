#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider

class Spider(Spider):
	def getDependence(self):
		return ['py_ali']
	def getName(self):
		return "py_pansou"
	def init(self,extend):
		self.ali = extend[0]
		print("============py_pansou============")
		pass
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
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

	def detailContent(self,array):
		tid = array[0]
		print(self.getName())
		pattern = '(https:\\/\\/www.aliyundrive.com\\/s\\/[^\\\"]+)'
		url = self.regStr(tid,pattern)
		if len(url) > 0:
			return self.ali.detailContent(array)

		rsp = self.fetch('https://www.alipansou.com'+tid)
		url = self.regStr(rsp.text,pattern)
		if len(url) == 0:
			return ""
		url = url.replace('\\','')
		newArray = [url]
		print(newArray)
		return self.ali.detailContent(newArray)


	def searchContent(self,key,quick):
		map = {
			'7':'文件夹',
			'1':'视频'
		}
		ja = []
		for tKey in map.keys():
			url = "https://www.alipansou.com/search?k={0}&t={1}".format(key,tKey)
			rsp = self.fetch(url)
			root = self.html(self.cleanText(rsp.text))
			aList = root.xpath("//van-row/a")
			for a in aList:
				title = ''
				# title = a.xpath('string(.//template/div)')
				# title = self.cleanText(title).strip()

				divList = a.xpath('.//template/div')
				for div in divList:
					t = div.xpath('string(.)')
					t = self.cleanText(t).strip()
					title = title + t
				if key in title:
					pic = 'https://www.alipansou.com'+ self.xpText(a,'.//van-card/@thumb')
					jo = {
						'vod_id': a.xpath('@href')[0],
						'vod_name': '[{0}]{1}'.format(key,title),
						'vod_pic': pic
					}
					ja.append(jo)
		result = {
			'list':ja
		}
		return result

	def playerContent(self,flag,id,vipFlags):
		return self.ali.playerContent(flag,id,vipFlags)

	config = {
		"player": {},
		"filter": {}
	}
	header = {}

	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]