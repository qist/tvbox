#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import json

class Spider(Spider):  # 元类 默认的元类 type
	def getName(self):
		return "我爱跟剧"
	def init(self,extend=""):
		print("============{0}============".format(extend))
		pass
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def homeContent(self,filter):
		# genmov
		# https://www.genmov.com/v/yinyue.html
		result = {}
		cateManual = {
			"电影":"dianying",
			"连续剧":"lianxuju",
			"动漫":"dongman",
			"综艺":"zongyi",
			"少儿":"shaoer",
			"音乐":"yinyue"
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
		rsp = self.fetch("https://www.genmov.com/",headers=self.header)
		root = self.html(rsp.text)
		aList = root.xpath("//div[@class='module module-wrapper']//div[@class='module-item']")
		videos = []
		for a in aList:
			name = a.xpath(".//div[@class='module-item-pic']/a/@title")[0]
			pic = a.xpath(".//div[@class='module-item-pic']/img/@data-src")[0]
			mark = a.xpath("./div[@class='module-item-text']/text()")[0]
			sid = a.xpath(".//div[@class='module-item-pic']/a/@href")[0]
			sid = self.regStr(sid,"/video/(\\S+).html")
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
		url = 'https://www.genmov.com/vodshow/{0}.html'.format(params)
		rsp = self.fetch(url,headers=self.header)
		root = self.html(rsp.text)
		aList = root.xpath("//div[@class='module-items']/div[@class='module-item']")
		videos = []
		for a in aList:
			name = a.xpath(".//div[@class='module-item-pic']/a/@title")[0]
			pic = a.xpath(".//div[@class='module-item-pic']/img/@data-src")[0]
			mark = a.xpath("./div[@class='module-item-text']/text()")[0]
			sid = a.xpath(".//div[@class='module-item-pic']/a/@href")[0]
			sid = self.regStr(sid,"/video/(\\S+).html")			
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
		# video-info-header
		tid = array[0]
		url = 'https://www.genmov.com/video/{0}.html'.format(tid)
		rsp = self.fetch(url,headers=self.header)
		root = self.html(rsp.text)
		title = root.xpath(".//h1[@class='page-title']/text()")[0]
		pic = root.xpath(".//div[@class='video-cover']//img/@data-src")[0]
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
		infoArray = root.xpath(".//div[@class='video-info-items']")
		for info in infoArray:
			content = info.xpath('string(.)')
		# 	if content.startswith('类型'):
		# 		vod['type_name'] = content
		# 	if content.startswith('年份'):
		# 		vod['vod_year'] = content
		# 	if content.startswith('地区'):
		# 		vod['vod_area'] = content
			if content.startswith('集数'):
				vod['vod_remarks'] = content
			if content.startswith('主演'):
				vod['vod_actor'] = content
			if content.startswith('导演'):
				vod['vod_director'] = content
			if content.startswith('剧情'):
				vod['vod_content'] = content

		vod_play_from = '$$$'
		playFrom = []
		vodHeader = root.xpath(".//main[@id='main']//div[@class='module-heading']//div[contains(@class,'module-tab-item')]/span/text()")
		for v in vodHeader:
			playFrom.append(v)
		vod_play_from = vod_play_from.join(playFrom)
		
		vod_play_url = '$$$'
		playList = []
		vodList = root.xpath(".//main[@id='main']//div[contains(@class,'module-list')]//div[@class='sort-item']")
		for vl in vodList:
			vodItems = []
			aList = vl.xpath('./a')
			for tA in aList:
				href = tA.xpath('./@href')[0]
				name = tA.xpath('./span/text()')[0]
				tId = self.regStr(href,'/play/(\\S+).html')
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
		result = {}
		return result
	def playerContent(self,flag,id,vipFlags):
		# https://www.genmov.com/play/301475-1-1.html
		# https://www.genmov.com/static/js/playerconfig.js
		url = 'https://www.genmov.com/play/{0}.html'.format(id)
		rsp = self.fetch(url,headers=self.header)
		root = self.html(rsp.text)
		scripts = root.xpath("//script/text()")
		jo = {}
		for script in scripts:
			if(script.startswith("var player_")):
				target = script[script.index('{'):]
				jo = json.loads(target)
				break;
		result = {}
		parseUrl = ""
		playerConfig = self.config['player']
		if jo['from'] in self.config['player']:
			parser = self.config['player'][jo['from']]
			originUrl = jo['url']
			parseUrl = parser['parse']

			result["parse"] = parser['ps']
			result["playUrl"] = parseUrl
			result["url"] = originUrl
			result["header"] = ''
		return result

	cookie = {}
	config = {
		"player": {"dplayer":{"show":"默认","des":"","ps":"1","parse":"https://vip.2ktvb.com/player/?url="},"qqy":{"show":"预告专用","des":"","ps":"1","parse":"https://vip.2ktvb.com/player/?url="},"qiyi":{"show":"爱奇艺","des":"qiyi.com","ps":"1","parse":"https://vip.2ktvb.com/player/sg.php?url="},"youku":{"show":"优酷","des":"youku.com","ps":"1","parse":"https://vip.2ktvb.com/player/sg.php?url="},"qq":{"show":"腾讯","des":"qq.com","ps":"1","parse":"https://vip.2ktvb.com/player/sg.php?url="},"mgtv":{"show":"芒果","des":"mgtv.com","ps":"1","parse":"https://vip.2ktvb.com/player/sg.php?url="},"letv":{"show":"乐视","des":"","ps":"1","parse":"https://jx.quanmingjiexi.com/?url="},"m1905":{"show":"电影网","des":"","ps":"1","parse":"https://vip.2ktvb.com/player/sg.php?url="},"bilibili":{"show":"哔哩哔哩","des":"","ps":"1","parse":"https://jx.bozrc.com:4433/player/?url="},"sohu":{"show":"搜狐","des":"","ps":"1","parse":"https://vip.2ktvb.com/player/sg.php?url="},"lzm3u8":{"show":"量子资源1","des":"支持手机电脑在线播放","ps":"0","parse":""},"ss4m3u8":{"show":"松鼠资源4","des":"支持手机电脑在线播放","ps":"0","parse":""},"ss3m3u8":{"show":"松鼠资源3","des":"支持手机电脑在线播放","ps":"0","parse":""},"ss2m3u8":{"show":"松鼠资源2","des":"支持手机电脑在线播放","ps":"0","parse":""},"ss1m3u8":{"show":"松鼠资源1","des":"支持手机电脑在线播放","ps":"0","parse":""},"jinyingm3u8":{"show":"金鹰资源②","des":"支持手机电脑在线播放","ps":"0","parse":""},"cmpyun":{"show":"冠军资源①","des":"支持手机电脑在线播放","ps":"0","parse":""},"kcm3u8":{"show":"快车资源①","des":"支持手机电脑在线播放","ps":"0","parse":""},"xlm3u8":{"show":"新浪资源2","des":"支持手机电脑在线播放","ps":"0","parse":""},"ssyun":{"show":"神速资源1","des":"支持手机电脑在线播放","ps":"0","parse":""},"ssm3u8":{"show":"神速资源2","des":"支持手机电脑在线播放","ps":"0","parse":""},"wolong":{"show":"卧龙资源","des":"支持手机电脑在线播放","ps":"1","parse":"https://vip.2ktvb.com/?url="},"ptzy":{"show":"葡萄资源","des":"支持手机电脑在线播放","ps":"0","parse":""},"zgzy":{"show":"猪哥播放器","des":"支持手机电脑在线播放","ps":"0","parse":""},"ukm3u8":{"show":"U酷点播","des":"支持手机电脑在线播放","ps":"0","parse":""},"fsm3u8":{"show":"飞速播放器","des":"支持手机电脑在线播放","ps":"0","parse":""},"mim3u8":{"show":"大米播放器","des":"支持手机电脑在线播放","ps":"0","parse":""},"if101":{"show":"if101播放器","des":"支持手机电脑在线播放","ps":"0","parse":""},"sgm3u8":{"show":"速更播放器","des":"支持手机电脑在线播放","ps":"0","parse":""},"kdm3u8":{"show":"酷点播放器","des":"支持手机电脑在线播放","ps":"0","parse":""},"xiuse":{"show":"秀色播放","des":"支持手机电脑在线播放","ps":"0","parse":""},"swm3u8":{"show":"丝袜播放器","des":"支持手机电脑在线播放","ps":"0","parse":""},"bdxm3u8":{"show":"北斗星m3u8","des":"支持手机电脑在线播放","ps":"0","parse":""},"hjm3u8":{"show":"花椒播放器","des":"支持手机电脑在线播放","ps":"0","parse":""},"kbzy":{"show":"快播云播","des":"支持手机电脑在线播放","ps":"0","parse":""},"88zym3u8":{"show":"88在线","des":"支持手机电脑在线播放","ps":"0","parse":""},"lezy":{"show":"乐库云播","des":"支持手机电脑在线播放","ps":"0","parse":""},"kkyun":{"show":"酷酷云播","des":"支持手机电脑在线播放","ps":"0","parse":""},"kkm3u8":{"show":"KK在线","des":"支持手机电脑在线播放","ps":"0","parse":""},"tpm3u8":{"show":"淘片播放器","des":"支持手机电脑在线播放","ps":"0","parse":""},"ckm3u8":{"show":"ck资源","des":"支持手机电脑在线播放","ps":"0","parse":""},"bjyun":{"show":"八戒云播","des":"支持手机电脑在线播放","ps":"0","parse":""},"gsm3u8":{"show":"光速云资源②","des":"支持手机电脑在线播放","ps":"0","parse":""},"m3u8":{"show":"m3u8在线","des":"支持手机电脑在线播放","ps":"0","parse":""},"videojs":{"show":"videojs-H5播放器","des":"videojs.com","ps":"0","parse":""},"iva":{"show":"iva-H5播放器","des":"videojj.com","ps":"0","parse":""},"iframe":{"show":"外链数据","des":"iframe外链数据","ps":"0","parse":""},"link":{"show":"外链数据","des":"外部网站播放链接","ps":"0","parse":""},"swf":{"show":"Flash文件","des":"swf","ps":"0","parse":""},"flv":{"show":"Flv文件","des":"flv","ps":"0","parse":""},"pptv":{"show":"PPTV","des":"pptv","ps":"1","parse":"https://vip.2ktvb.com/player/sg.php?url="},"migu":{"show":"咪咕","des":"migu","ps":"0","parse":"https://vip.2ktvb.com/player/sg.php?url="},"cctv":{"show":"cctv","des":"cctv","ps":"1","parse":"https://vip.2ktvb.com/player/sg.php?url="},"cntv":{"show":"cntv","des":"cntv","ps":"1","parse":"https://vip.2ktvb.com/player/?url="},"funshion":{"show":"风行","des":"funshion","ps":"1","parse":"hhttps://vip.2ktvb.com/player/sg.php?url="},"wasu":{"show":"华数","des":"wasu","ps":"1","parse":"https://vip.2ktvb.com/player/sg.php?url="},"605m3u8":{"show":"605线","des":"支持手机电脑在线播放","ps":"1","parse":"https://vip.2ktvb.com/player/?url="},"bjm3u8":{"show":"八戒","des":"","ps":"1","parse":"https://vip.2ktvb.com/player/?url="},"dbm3u8":{"show":"百度线","des":"","ps":"1","parse":"https://vip.2ktvb.com/player/?url="},"hnm3u8":{"show":"牛牛线","des":"","ps":"1","parse":"https://vip.2ktvb.com/player/?url="},"igen":{"show":"爱跟线","des":"","ps":"1","parse":"https://vip.2ktvb.com/player/?url="},"kbm3u8":{"show":"快播线","des":"","ps":"1","parse":"https://vip.2ktvb.com/player/?url="},"lajiao":{"show":"辣椒","des":"","ps":"1","parse":"https://lajiaoapi.com/watch?url="},"tkm3u8":{"show":"天空线","des":"","ps":"1","parse":"https://vip.2ktvb.com/player/?url="},"tsm3u8":{"show":"Ts线","des":"","ps":"1","parse":"https://vip.2ktvb.com/player/?url="},"wjm3u8":{"show":"无尽线","des":"","ps":"1","parse":"https://vip.2ktvb.com/player/?url="},"xigua":{"show":"西瓜线","des":"","ps":"1","parse":"https://vip.2ktvb.com/player/sg.php?url="},"xkm3u8":{"show":"想看线","des":"","ps":"1","parse":"https://vip.2ktvb.com/player/?url="},"jhyun":{"show":"聚合云","des":"","ps":"1","parse":"https://vip.2ktvb.com/player/?url="},"sdm3u8":{"show":"闪电线","des":"支持手机电脑在线播放","ps":"1","parse":"https://vip.2ktvb.com/player/?url="},"ddzy":{"show":"极速多线","des":"","ps":"1","parse":"https://bo.dd520.cc//xmplayer/?url="},"jscq":{"show":"极速超清","des":"","ps":"1","parse":"https://vip.2ktvb.com/player/?xf=languang&url="},"jslg":{"show":"极速蓝光","des":"","ps":"1","parse":"https://vip.2ktvb.com/player/?xf=languang&url="}},
		"filter": {"dianying":[{"key":3,"name":"分类","value":[{"n":"全部","v":""},{"n":"喜剧","v":"喜剧"},{"n":"动作","v":"动作"},{"n":"爱情","v":"爱情"},{"n":"惊悚","v":"惊悚"},{"n":"犯罪","v":"犯罪"},{"n":"冒险","v":"冒险"},{"n":"科幻","v":"科幻"},{"n":"悬疑","v":"悬疑"},{"n":"剧情","v":"剧情"},{"n":"动画","v":"动画"},{"n":"仙侠","v":"仙侠"},{"n":"武侠","v":"武侠"},{"n":"战争","v":"战争"},{"n":"歌舞","v":"歌舞"},{"n":"奇幻","v":"奇幻"},{"n":"传记","v":"传记"},{"n":"警匪","v":"警匪"},{"n":"历史","v":"历史"},{"n":"运动","v":" 运动"},{"n":"伦理","v":"伦理"},{"n":"灾难","v":"灾难"},{"n":"西部","v":"西部"},{"n":"魔幻","v":"魔幻"},{"n":"枪战","v":"枪战"},{"n":"恐怖","v":"恐怖"},{"n":"记录","v":"记录"},{"n":"情色","v":"情色"}]},{"key":1,"name":"地区","value":[{"n":"全部","v":""},{"n":"🇨🇳中国","v":"大陆"},{"n":"🇺🇸美国","v":"美国"},{"n":"🇭🇰香港","v":"香港"},{"n":"🇰🇷韩国","v":"韩国"},{"n":"英国","v":"英国"},{"n":"🇹🇼台湾","v":"台湾"},{"n":"🇯🇵日本","v":"日本"},{"n":"法国","v":"法国"},{"n":"意大利","v":"意大利"},{"n":"德国","v":"德国"},{"n":"西班牙","v":"西班牙"},{"n":"泰国","v":"泰国"},{"n":"其它","v":"其它"}]},{"key":4,"name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"法语","v":"法语"},{"n":"德语","v":"德语"},{"n":"其它","v":"其它"}]},{"key":11,"name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"}]},{"key":5,"name":"字母","value":[{"n":"字母","v":""},{"n":"A","v":"A"},{"n":"B","v":"B"},{"n":"C","v":"C"},{"n":"D","v":"D"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]},{"key":2,"name":"排序","value":[{"n":"最新","v":"time"},{"n":"最热","v":"hits"},{"n":"评分","v":"score"}]}],"lianxuju":[{"key":3,"name":"分类","value":[{"n":" 全部","v":""},{"n":"古装","v":"古装"},{"n":"动作","v":"动作"},{"n":"都市","v":"都市"},{"n":"偶像","v":"偶像"},{"n":"家庭","v":"家庭"},{"n":"警匪","v":"警匪"},{"n":"言情","v":"言情"},{"n":"军事","v":"军事"},{"n":"武侠","v":"武侠"},{"n":"悬疑","v":"悬疑"},{"n":"历史","v":"历史"},{"n":"农村","v":"农村"},{"n":"都市","v":"都市"},{"n":"神话","v":"神话"},{"n":"科幻","v":"科幻"},{"n":"少儿","v":"少儿"},{"n":"搞笑","v":"搞笑"},{"n":"谍战","v":"谍战"},{"n":"战争","v":"战争"},{"n":"年代","v":"年代"},{"n":"犯罪","v":"犯 罪"},{"n":"恐怖","v":"恐怖"},{"n":"惊悚","v":"惊悚"},{"n":"爱情","v":"爱情"},{"n":"剧情","v":"剧情"},{"n":"奇幻","v":"奇幻"},{"n":"仙侠","v":"仙侠"}]},{"key":1,"name":"地区","value":[{"n":"全部","v":""},{"n":"🇨🇳中国","v":"大陆"},{"n":"🇰🇷韩国","v":"韩国"},{"n":"🇭🇰香港","v":"香港"},{"n":"🇹🇼台湾","v":"台湾"},{"n":"🇯🇵日本","v":"日本"},{"n":"🇺🇸美国","v":"美国"},{"n":"泰国","v":"泰国"},{"n":"英国","v":"英国"},{"n":"新加坡","v":"新加坡"}]},{"key":4,"name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]},{"key":11,"name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"}]},{"key":5,"name":"字母","value":[{"n":"字母","v":""},{"n":"A","v":"A"},{"n":"B","v":"B"},{"n":"C","v":"C"},{"n":"D","v":"D"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]},{"key":2,"name":"排序","value":[{"n":"最新","v":"time"},{"n":"最热","v":"hits"},{"n":"评分","v":"score"}]}],"dongman":[{"key":3,"name":"分类","value":[{"n":"全部","v":""},{"n":"番剧","v":"番剧"},{"n":"国创","v":"国创"},{"n":"热血","v":"热血"},{"n":"科幻","v":"科幻"},{"n":"动画","v":"动画"},{"n":"仙侠","v":"仙侠"},{"n":"修仙","v":"修仙"},{"n":"推理","v":"推理"},{"n":"搞笑","v":"搞笑"},{"n":"冒险","v":"冒险"},{"n":"校园","v":"校园"},{"n":"动作","v":"动作"},{"n":"机战","v":"机战"},{"n":"运动","v":"运动"},{"n":"战争","v":"战争"},{"n":"少年","v":"少年"},{"n":"少女","v":"少女"},{"n":"社会","v":"社会"},{"n":"原创","v":"原创"},{"n":"亲子","v":"亲子"},{"n":"益智","v":"益智"},{"n":"励志","v":"励志"},{"n":"其他","v":"其他"}]},{"key":1,"name":"地区","value":[{"n":"全部","v":""},{"n":"🇨🇳中国","v":"大陆"},{"n":"🇯🇵日本","v":"日本"},{"n":"欧美","v":"欧美"},{"n":"其他","v":"其他"}]},{"key":4,"name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]},{"key":11,"name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"}]},{"key":5,"name":"字母","value":[{"n":"字母","v":""},{"n":"A","v":"A"},{"n":"B","v":"B"},{"n":"C","v":"C"},{"n":"D","v":"D"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]},{"key":2,"name":"排序","value":[{"n":"最新","v":"time"},{"n":"最热","v":"hits"},{"n":"评分","v":"score"}]}],"zongyi":[{"key":3,"name":"分类","value":[{"n":"全部","v":""},{"n":"真人秀","v":"真人秀"},{"n":"访谈","v":"访谈"},{"n":"情感","v":"情感"},{"n":"选秀","v":"选秀"},{"n":"旅游","v":"旅游"},{"n":"美食","v":"美食"},{"n":"口秀","v":"口秀"},{"n":"曲艺","v":"曲艺"},{"n":"搞笑","v":"搞笑"},{"n":"游戏","v":"游戏"},{"n":"歌舞","v":"歌舞"},{"n":"生活","v":"生活"},{"n":"音乐","v":"音乐"},{"n":"时尚","v":"时尚"},{"n":"益智","v":"益智"},{"n":"职场","v":"职场"},{"n":"少儿","v":"少儿"},{"n":"纪实","v":"纪实"},{"n":"盛会","v":"盛会"},{"n":"音乐MV","v":"音乐MV"}]},{"key":1,"name":"地区","value":[{"n":"全部","v":""},{"n":"🇨🇳中国","v":"大陆"},{"n":"🇰🇷韩国","v":"韩国"},{"n":"🇭🇰香港","v":"香港"},{"n":"🇹🇼台湾","v":"台湾"},{"n":"🇺🇸美国","v":"美国"},{"n":"其它","v":"其它"}]},{"key":4,"name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]},{"key":11,"name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"}]},{"key":5,"name":"字母","value":[{"n":"字母","v":""},{"n":"A","v":"A"},{"n":"B","v":"B"},{"n":"C","v":"C"},{"n":"D","v":"D"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]},{"key":2,"name":"排序","value":[{"n":"最新","v":"time"},{"n":"最热","v":"hits"},{"n":"评分","v":"score"}]}],"shaoer":[{"key":3,"name":"分类","value":[{"n":"全部","v":""},{"n":"历险","v":"历险"},{"n":"奇幻","v":"奇幻"},{"n":"教育","v":"教 育"},{"n":"搞笑","v":"搞笑"},{"n":"教育","v":"教育"},{"n":"益智","v":"益智"}]},{"key":1,"name":"地区","value":[{"n":"全部","v":""},{"n":"🇨🇳中国","v":"大陆"},{"n":"🇺🇸美国","v":"美国"},{"n":"🇭🇰香港","v":"香港"},{"n":"🇰🇷韩国","v":"韩国"},{"n":"英国","v":"英国"},{"n":"🇹🇼台湾","v":"台湾"},{"n":"🇯🇵日本","v":"日本"},{"n":"法国","v":"法国"},{"n":"意大利","v":"意大利"},{"n":"德国","v":"德国"},{"n":"西班牙","v":"西班牙"},{"n":"泰国","v":"泰国"},{"n":"其它","v":"其它"}]},{"key":4,"name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"法语","v":"法语"},{"n":"德语","v":"德语"},{"n":"其它","v":"其它"}]},{"key":11,"name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"}]},{"key":5,"name":"字母","value":[{"n":"字母","v":""},{"n":"A","v":"A"},{"n":"B","v":"B"},{"n":"C","v":"C"},{"n":"D","v":"D"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]},{"key":2,"name":"排序","value":[{"n":"最新","v":"time"},{"n":"最热","v":"hits"},{"n":"评分","v":"score"}]}],"yinyue":[{"key":3,"name":"分类","value":[{"n":"全部","v":""},{"n":"MV","v":"MV"},{"n":"演唱会","v":"演唱会"},{"n":"音频","v":"音频"}]},{"key":1,"name":"地区","value":[{"n":"全部","v":""},{"n":"🇨🇳中国","v":"大陆"},{"n":"🇰🇷韩国","v":"韩国"},{"n":"🇭🇰香港","v":"香港"},{"n":"🇹🇼台湾","v":"台湾"}]},{"key":4,"name":"语言","value":[{"n":"全部","v":""},{"n":"韩语","v":"韩语"},{"n":"粤语","v":"粤语"},{"n":"日语","v":"日语"},{"n":"英语","v":"英语"},{"n":"泰语","v":"泰语"},{"n":"国语","v":"国语"}]},{"key":11,"name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"}]},{"key":5,"name":"字母","value":[{"n":"字母","v":""},{"n":"A","v":"A"},{"n":"B","v":"B"},{"n":"C","v":"C"},{"n":"D","v":"D"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]},{"key":2,"name":"排序","value":[{"n":"最新","v":"time"},{"n":"最热","v":"hits"},{"n":"评分","v":"score"}]}]}
	}
	header = {
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.47'
	}

	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]