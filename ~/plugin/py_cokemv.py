#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import json
import requests
import base64

class Spider(Spider):  # 元类 默认的元类 type
	def getName(self):
		return "Cokemv"
	def init(self,extend=""):
		print("============{0}============".format(extend))
		pass
	def homeContent(self,filter):
		result = {}
		cateManual = {
			"抖音电影":"5",
			"电视剧":"2",
			"电影":"1",
			"动漫":"4",
			"综艺":"3"
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
		rsp = self.fetch("https://cokemv.me/")
		root = self.html(rsp.text)
		aList = root.xpath("//div[@class='main']//div[contains(@class,'module-items')]/a")

		videos = []
		for a in aList:
			name = a.xpath('./@title')[0]
			pic = a.xpath('.//img/@data-original')[0]
			mark = a.xpath(".//div[@class='module-item-note']/text()")[0]
			sid = a.xpath("./@href")[0]
			sid = self.regStr(sid,"/voddetail/(\\S+).html")
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

		urlParams = ["", "", "", "", "", "", "", "", "", "", "", ""]
		urlParams[0] = tid
		urlParams[8] = pg
		for key in extend:
			urlParams[int(key)] = extend[key]
		params = '-'.join(urlParams)
		url = 'https://cokemv.me/vodshow/{0}.html'.format(params)
		rsp = self.fetch(url)
		root = self.html(rsp.text)
		aList = root.xpath("//div[contains(@class, 'module-items')]/a")
		videos = []
		for a in aList:
			name = a.xpath('./@title')[0]
			pic = a.xpath('.//img/@data-original')[0]
			mark = a.xpath(".//div[contains(@class,'module-item-note')]/text()")[0]
			sid = a.xpath("./@href")[0]
			sid = self.regStr(sid,"/voddetail/(\\d+).html")
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
		url = 'https://cokemv.me/voddetail/{0}.html'.format(tid)
		rsp = self.fetch(url)
		root = self.html(rsp.text)
		divContent = root.xpath("//div[@class='module-info-main']")[0]
		title = divContent.xpath('.//h1/text()')[0]
		year = divContent.xpath('.//div/div/div[1]/a/text()')[0]
		area = divContent.xpath('.//div/div/div[2]/a/text()')[0]
		typ = divContent.xpath('.//div/div/div[3]/a/text()')
		type = ', '.join(typ)
		dir = divContent.xpath(".//div[@class='module-info-items']/div[2]/div[1]/a/text()")[0]
		act = divContent.xpath(".//div[@class='module-info-items']/div[4]/div/a/text()")
		actor = ', '.join(act)
		pic = root.xpath(".//div[@class='module-poster-bg']//img/@data-original")[0]
		detail = root.xpath(".//div[@class='module-info-introduction-content']/p/text()")[0]
		vod = {
			"vod_id":tid,
			"vod_name":title,
			"vod_pic":pic,
			"type_name":type,
			"vod_year":year,
			"vod_area":area,
			"vod_remarks":"",
			"vod_actor":actor,
			"vod_director":dir,
			"vod_content":detail
		}

		vod_play_from = '$$$'
		playFrom = []
		vodHeader = root.xpath("//div[@class='module-tab-item tab-item']/span/text()")
		for v in vodHeader:
			playFrom.append(v)
		vod_play_from = vod_play_from.join(playFrom)
		
		vod_play_url = '$$$'
		playList = []
		vodList = root.xpath("//div[@class='module-play-list']")
		for vl in vodList:
			vodItems = []
			aList = vl.xpath('./div/a')
			for tA in aList:
				href = tA.xpath('./@href')[0]
				name = tA.xpath('.//span/text()')[0]
				tId = self.regStr(href,'/vodplay/(\\S+).html')
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

	def verifyCode(self, url):
		retry = 5
		header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"}
		while retry:
			try:
				session = requests.session()
				img = session.get('https://cokemv.me/index.php/verify/index.html?', headers=header).content
				code = session.post('https://api.nn.ci/ocr/b64/text', data=base64.b64encode(img).decode()).text
				res = session.post(url=f"https://cokemv.me/index.php/ajax/verify_check?type=search&verify={code}", headers=header).json()
				if res["msg"] == "ok":
					return session
			except Exception as e:
				print(e)
			finally:
				retry = retry - 1

	def searchContent(self, key, quick):
		url = 'https://cokemv.me/vodsearch/-------------.html?wd={0}'.format(key)
		session = self.verifyCode(url)
		rsp = session.get(url)
		root = self.html(rsp.text)
		vodList = root.xpath("//div[@class='module-card-item module-item']/a[@class='module-card-item-poster']")
		videos = []
		for vod in vodList:
			name = vod.xpath(".//img/@alt")[0]
			pic = vod.xpath(".//img/@data-original")[0]
			mark = vod.xpath(".//div[@class='module-item-note']/text()")[0]
			sid = vod.xpath("./@href")[0]
			sid = self.regStr(sid,"/voddetail/(\\S+).html")
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

	config = {
		"player": {"cokemv0555":{"show":"COKEMV","des":"","ps":"0","parse":""},"cokeqie01":{"show":"極速路線","des":"","ps":"0","parse":""},"xin":{"show":"高速路線","des":"","ps":"0","parse":""},"90mm":{"show":"COKEMV(測試)","des":"","ps":"0","parse":""},"toutiao":{"show":"海外路線","des":"","ps":"0","parse":""},"age01":{"show":"動漫一線","des":"","ps":"0","parse":""},"mahua":{"show":"海外(禁國內)","des":"","ps":"0","parse":""},"age02":{"show":"動漫二線","des":"","ps":"0","parse":""}},
		"filter": {"5":[{"key":3,"name":"剧情","value":[{"n":"全部","v":""},{"n":"喜劇","v":"喜劇"},{"n":"愛情","v":"愛情"},{"n":"恐怖","v":"恐怖"},{"n":"動作","v":"動作"},{"n":"科幻","v":"科幻"},{"n":"劇情","v":"劇情"},{"n":"戰爭","v":"戰爭"},{"n":"犯罪","v":"犯罪"},{"n":"動畫","v":"動畫"},{"n":"奇幻","v":"奇幻"},{"n":"恐怖","v":"恐怖"},{"n":"懸疑","v":"懸疑"},{"n":"微電影","v":"微電影"}]},{"key":4,"name":"语言","value":[{"n":"全部","v":""},{"n":"國語","v":"國語"},{"n":"英語","v":"英語"},{"n":"粵語","v":"粵語"},{"n":" 閩南語","v":"閩南語"},{"n":"韓語","v":"韓語"},{"n":"日語","v":"日語"},{"n":"法語","v":"法語"},{"n":"德語","v":"德語"},{"n":"其它","v":"其它"}]},{"key":11,"name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"}]},{"key":5,"name":"字母","value":[{"n":"字母","v":""},{"n":"A","v":"A"},{"n":"B","v":"B"},{"n":"C","v":"C"},{"n":"D","v":"D"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]},{"key":2,"name":"排序","value":[{"n":"时间排序","v":"time"},{"n":"人气排序","v":"hits"},{"n":"评分排序","v":"score"}]}],"2":[{"key":0,"name":"类型","value":[{"n":"全部","v":"2"},{"n":"大陸劇","v":"13"},{"n":"香港劇","v":"14"},{"n":"韓國劇","v":"15"},{"n":"歐美劇","v":"16"},{"n":"日本劇","v":"20"},{"n":"台灣劇","v":"21"},{"n":"泰國劇","v":"22"}]},{"key":1,"name":"地区","value":[{"n":"全部","v":""},{"n":"🇨🇳中国","v":"中国大陆"},{"n":"🇰🇷韩国","v":"韩国"},{"n":"🇭🇰香港","v":"中国香港"},{"n":"🇹🇼台湾","v":"中国台湾"},{"n":"🇯🇵日本","v":"日本"},{"n":"🇺🇸美国","v":"美国"},{"n":"加拿大","v":"加拿大"},{"n":"泰国","v":"泰国"},{"n":"英国","v":"英国"},{"n":"新加坡","v":"新加坡"},{"n":"其他","v":"其他"}]},{"key":4,"name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]},{"key":11,"name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"}]},{"key":5,"name":"字母","value":[{"n":"字母","v":""},{"n":"A","v":"A"},{"n":"B","v":"B"},{"n":"C","v":"C"},{"n":"D","v":"D"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]},{"key":2,"name":"排序","value":[{"n":"时间排序","v":"time"},{"n":"人气排序","v":"hits"},{"n":"评分排序","v":"score"}]}],"1":[{"key":0,"name":"类型","value":[{"n":"全部","v":"1"},{"n":"動作片","v":"6"},{"n":"喜劇片","v":"7"},{"n":"愛情片","v":"8"},{"n":"科幻片","v":"9"},{"n":"恐怖片","v":"10"},{"n":"劇情片","v":"11"},{"n":"戰爭片","v":"12"},{"n":"犯罪片","v":"23"},{"n":"奇幻片","v":"24"},{"n":"懸疑片","v":"25"},{"n":"記錄片","v":"27"}]},{"key":1,"name":"地区","value":[{"n":"全部","v":""},{"n":"🇨🇳中国","v":"中国大陆"},{"n":"🇰🇷韩国","v":"韩国"},{"n":"🇭🇰香港","v":"中国香港"},{"n":"🇹🇼台湾","v":"中国台湾"},{"n":"🇯🇵日本","v":"日本"},{"n":"🇺🇸美国","v":"美国"},{"n":"加拿大","v":"加拿大"},{"n":"泰国","v":"泰国"},{"n":"英国","v":"英国"},{"n":"新加坡","v":"新加坡"},{"n":"其他","v":"其他"}]},{"key":4,"name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"法语","v":"法语"},{"n":"德语","v":"德语"},{"n":"其它","v":"其它"}]},{"key":11,"name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"}]},{"key":5,"name":"字母","value":[{"n":"字母","v":""},{"n":"A","v":"A"},{"n":"B","v":"B"},{"n":"C","v":"C"},{"n":"D","v":"D"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]},{"key":2,"name":"排序","value":[{"n":"时间排序","v":"time"},{"n":"人气排序","v":"hits"},{"n":"评分排序","v":"score"}]}],"4":[{"key":0,"name":"类型","value":[{"n":"全部","v":"4"},{"n":"動畫電影","v":"41"}]},{"key":1,"name":"地区","value":[{"n":"全部","v":""},{"n":"🇨🇳中国","v":"中国大陆"},{"n":"🇯🇵日本","v":"日本"},{"n":"🇺🇸美国","v":"美国"}]},{"key":4,"name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]},{"key":11,"name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"}]},{"key":5,"name":"字母","value":[{"n":"字母","v":""},{"n":"A","v":"A"},{"n":"B","v":"B"},{"n":"C","v":"C"},{"n":"D","v":"D"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]},{"key":2,"name":"排序","value":[{"n":"时间排序","v":"time"},{"n":"人气排序","v":"hits"},{"n":"评分排序","v":"score"}]}],"3":[{"key":1,"name":"地区","value":[{"n":"全部","v":""},{"n":"🇨🇳中国","v":"中国大陆"},{"n":"🇰🇷韩国","v":" 韩国"}]},{"key":4,"name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩 语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]},{"key":11,"name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"}]},{"key":5,"name":"字母","value":[{"n":"字母","v":""},{"n":"A","v":"A"},{"n":"B","v":"B"},{"n":"C","v":"C"},{"n":"D","v":"D"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]},{"key":2,"name":"排序","value":[{"n":" 时间排序","v":"time"},{"n":"人气排序","v":"hits"},{"n":"评分排序","v":"score"}]}]}
	}
	header = {
		"origin":"https://cokemv.me",
		"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
		"Accept":" */*",
		"Accept-Language":"zh-CN,zh;q=0.9,en-US;q=0.3,en;q=0.7",
		"Accept-Encoding":"gzip, deflate"
	}
	def playerContent(self,flag,id,vipFlags):
		url = 'https://cokemv.me/vodplay/{0}.html'.format(id)
		rsp = self.fetch(url)
		root = self.html(rsp.text)
		scripts = root.xpath("//script/text()")
		jo = {}
		result = {}
		for script in scripts:
			if(script.startswith("var player_")):
				target = script[script.index('{'):]
				jo = json.loads(target)
				break;
		parseUrl = ""
		playerConfig = self.config['player']		
		if jo['from'] in self.config['player']:
			playerConfig = self.config['player'][jo['from']]
			videoUrl = jo['url']
			playerUrl = playerConfig['parse']
			result["parse"] = playerConfig['ps']
			result["playUrl"] = playerUrl
			result["url"] = videoUrl
			result["header"] = json.dumps(self.header)
		return result
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]