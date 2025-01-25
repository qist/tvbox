#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import json

class Spider(Spider):  # 元类 默认的元类 type
	def getName(self):
		return "剧迷"
	def init(self,extend=""):
		print("============{0}============".format(extend))
		pass
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def homeContent(self,filter):
		# https://gimytv.co/
		result = {}
		cateManual = {
			"电影": "movies",
			"电视剧": "tvseries",
			"综艺": "tv_show",
			"动漫": "anime"
		}
		classes = []
		for k in cateManual:
			classes.append({
				'type_name':k,
				'type_id':cateManual[k]
			})
		result['class'] = classes
		if(filter):
			result['filters'] = self.config['filter']
		return result
	def homeVideoContent(self):
		rsp = self.fetch("https://gimytv.co/",headers=self.header)
		root = self.html(rsp.text)
		aList = root.xpath("//ul[@class='myui-vodlist clearfix']/li/div/a")
		videos = []
		for a in aList:
			name = a.xpath("./@title")[0]
			pic = a.xpath("./@data-original")[0]
			mark = a.xpath("./span[contains(@class, 'pic-text')]/text()")[0]
			sid = a.xpath("./@href")[0]
			sid = self.regStr(sid,"/(\\S+).html")
			videos.append({
				"vod_id":sid,
				"vod_name":name,
				"vod_pic":pic,
				"vod_remarks":mark
			})
		result = {
			'list':videos
		}
		return result
	def categoryContent(self,tid,pg,filter,extend):
		result = {}
		urlParams = ["", "", "", ""]
		urlParams[0] = tid
		urlParams[3] = pg
		suffix = ''
		for key in extend:
			if key == 4:
				suffix = '/by/'+extend[key]
			else:
				urlParams[int(key)] = extend[key]
		params = '-'.join(urlParams)+suffix
		# https://gimytv.co/genre/tvseries--2022-/by/hits_month.html
		url = 'https://gimytv.com/genre/{0}.html'.format(params)
		rsp = self.fetch(url,headers=self.header)
		root = self.html(rsp.text)
		aList = root.xpath("//ul[@class='myui-vodlist clearfix']/li/div/a")
		videos = []
		for a in aList:
			name = a.xpath("./@title")[0]
			pic = a.xpath("./@data-original")[0]
			mark = a.xpath("./span[contains(@class, 'pic-text')]/text()")[0]
			sid = a.xpath("./@href")[0]
			sid = self.regStr(sid,"/(\\S+).html")			
			videos.append({
				"vod_id":sid,
				"vod_name":name,
				"vod_pic":pic,
				"vod_remarks":mark
			})
		result['list'] = videos
		result['page'] = pg
		result['pagecount'] = 9999
		result['limit'] = 90
		result['total'] = 999999
		return result
	def detailContent(self,array):
		tid = array[0]
		url = 'https://gimytv.co/{0}.html'.format(tid)
		rsp = self.fetch(url,headers=self.header)
		root = self.html(rsp.text)
		node = root.xpath("//div[@class='container']")[0]
		title = node.xpath(".//div[@class='myui-content__thumb']/a/@title")[0]
		pic = node.xpath(".//div[@class='myui-content__thumb']/a/img/@data-original")[0]
		vod = {
			"vod_id":tid,
			"vod_name":title,
			"vod_pic":pic,
			"type_name":"",
			"vod_year":"",
			"vod_area":"",
			"vod_remarks":"",
			"vod_actor":"",
			"vod_director":"",
			"vod_content":""
		}
		infoArray = node.xpath(".//div[@class='myui-content__detail']/p")
		for info in infoArray:
			content = info.xpath('string(.)')
			if content.startswith('分類'):
				vod['type_name'] = content
			# if content.startswith('年份'):
			# 	vod['vod_year'] = content
			# if content.startswith('地区'):
			# 	vod['vod_area'] = content
			if content.startswith('狀態'):
				vod['vod_remarks'] = content
			if content.startswith('主演'):
				vod['vod_actor'] = content
			if content.startswith('導演'):
				vod['vod_director'] = content
			# if content.startswith('剧情'):
			# 	vod['vod_content'] = content
		vod['vod_content'] = node.xpath(".//div[contains(@class,'col-pd')]/p/text()")[0]

		vod_play_from = '$$$'
		playFrom = []
		vodHeader = root.xpath(".//div[@class='myui-panel_hd']/div/h3/text()[2]")
		for v in vodHeader:
			playFrom.append(v.strip())
		vod_play_from = vod_play_from.join(playFrom)
		
		vod_play_url = '$$$'
		playList = []
		vodList = root.xpath(".//ul[contains(@class,'myui-content__list')]")
		for vl in vodList:
			vodItems = []
			aList = vl.xpath('./li/a')
			for tA in aList:
				href = tA.xpath('./@href')[0]
				name = tA.xpath('./text()')[0]
				tId = self.regStr(href,'/(\\S+).html')
				vodItems.append(name + "$" + tId)
			joinStr = '#'
			joinStr = joinStr.join(vodItems)
			playList.append(joinStr)
		vod_play_url = vod_play_url.join(playList)

		vod['vod_play_from'] = vod_play_from
		vod['vod_play_url'] = vod_play_url

		result = {
			'list':[
				vod
			]
		}
		return result
	def searchContent(self,key,quick):
		url = "https://gimytv.co/search/-------------.html?wd={0}".format(key)
		rsp = self.fetch(url,headers=self.header)
		root = self.html(rsp.text)
		aList = root.xpath("//ul[contains(@class,'myui-vodlist__media')]/li")
		videos = []
		for a in aList:
			name = a.xpath(".//a/@title")[0]
			pic = a.xpath(".//a/@data-original")[0]
			mark = a.xpath(".//span[contains(@class, 'pic-text')]/text()")[0]
			sid = a.xpath(".//a/@href")[0]
			sid = self.regStr(sid,"/(\\S+).html")
			videos.append({
				"vod_id":sid,
				"vod_name":name,
				"vod_pic":pic,
				"vod_remarks":mark
			})
		result = {
			'list':videos
		}
		return result
	def playerContent(self,flag,id,vipFlags):
		url = 'https://gimytv.co/{0}.html'.format(id)
		rsp = self.fetch(url,headers=self.header)
		root = self.html(rsp.text)
		scripts = root.xpath("//script/text()")
		jo = {}
		for script in scripts:
			if(script.startswith("var player_")):
				target = script[script.index('{'):]
				jo = json.loads(target)
				break;
		url = jo['url']
		result = {}
		result["parse"] = 0
		result["playUrl"] = ''
		result["url"] = url
		result["header"] = ''
		return result

	cookie = {}
	config = {
		"player": {},
		"filter": {"movies":[{"key":0,"name":"分类","value":[{"n":"全部","v":""},{"n":"劇情片","v":"drama"},{"n":"動作片","v":"action"},{"n":"科幻片","v":"scifi"},{"n":"喜劇片","v":"comedymovie"},{"n":"愛情片","v":"romance"},{"n":"戰爭片","v":"war"},{"n":"恐怖片","v":"horror"},{"n":"動畫電影","v":"animation"}]},{"key":1,"name":"地区","value":[{"n":"全部","v":""},{"n":"美國","v":"美國"},{"n":"歐美","v":"歐美"},{"n":"大陸","v":"大陸"},{"n":"中國大陸","v":"中國大陸"},{"n":"韓國","v":"韓國"},{"n":"🇭🇰香港","v":"香港"},{"n":"🇯🇵日本","v":"日本"},{"n":"英國","v":"英國"}]},{"key":2,"name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"}]},{"key":4,"name":"排序","value":[{"n":"按更新","v":"time"},{"n":"周人气","v":"hits_week"},{"n":"月人气","v":"hits_month"}]}],"tvseries":[{"key":0,"name":"分类","value":[{"n":"全部","v":""},{"n":"陸劇","v":"cn"},{"n":"韓劇","v":"kr"},{"n":"美劇","v":"us"},{"n":"日劇","v":"jp"},{"n":"台劇","v":"tw"},{"n":"港劇","v":"hks"},{"n":"海外劇","v":"ot"},{"n":"紀錄片","v":"documentary"}]},{"key":2,"name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"}]},{"key":4,"name":"排序","value":[{"n":"按更新","v":"time"},{"n":"周人气","v":"hits_week"},{"n":"月人气","v":"hits_month"}]}],"anime":[{"key":1,"name":"地区","value":[{"n":"全部","v":""},{"n":"🇯🇵日本","v":"日本"},{"n":"美國","v":"美國"},{"n":"歐美","v":"歐美"},{"n":"大陸","v":"大陸"},{"n":"臺灣","v":"臺灣"},{"n":"🇭🇰香港","v":"香港"}]},{"key":2,"name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"}]},{"key":4,"name":"排序","value":[{"n":"按更新","v":"time"},{"n":"周人气","v":"hits_week"},{"n":"月人气","v":"hits_month"}]}],"tv_show":[{"key":0,"name":"分类","value":[{"n":"全部","v":""},{"n":"纪录片","v":"28"}]},{"key":1,"name":"地区","value":[{"n":"全部","v":""},{"n":"大陸","v":"大陸"},{"n":"中國大陸","v":"中國大陸"},{"n":"韓國","v":"韓國"},{"n":"臺灣","v":"臺灣"},{"n":"美國","v":"美國"},{"n":"歐美","v":"歐美"},{"n":"🇯🇵日本","v":"日本"},{"n":"🇭🇰香港","v":"香港"}]},{"key":2,"name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"}]},{"key":4,"name":"排序","value":[{"n":"按更新","v":"time"},{"n":"周人气","v":"hits_week"},{"n":"月人气","v":"hits_month"}]}]}
	}
	header = {
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.47'
	}

	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]