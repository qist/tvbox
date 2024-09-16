#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import json
import time
import base64

class Spider(Spider):  # 元类 默认的元类 type
	def getName(self):
		return "哔哩"
	def init(self,extend=""):
		print("============{0}============".format(extend))
		pass
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def homeContent(self,filter):
		result = {}
		cateManual = {
"选美":"选美",
"模特":"模特",
"泳装":"泳装",
"内衣":"内衣",
"腾讯直播":"腾讯直播",
"腾讯演唱会":"腾讯演唱会",
"腾讯音乐会":"腾讯音乐会",
"舞蹈":"舞蹈",
"宅舞":"宅舞",
"街舞":"街舞",
"明星舞蹈":"明星舞蹈",
"韩舞":"韩舞",
"古典舞":"古典舞",
"翻跳":"翻跳",
"中国舞":"中国舞",
"古风舞":"古风舞",
"现代舞":"现代舞",
"爵士舞":"爵士舞",
"芭蕾":"芭蕾",
"编舞":"编舞",
"POPPING":"POPPING",
"极乐净土":"极乐净土",
"桃源恋歌":"桃源恋歌",
"新宝岛":"新宝岛",
"拉丁舞":"拉丁舞",
"蹦迪":"蹦迪",
"民族舞":"民族舞",
"抖肩舞":"抖肩舞",
"齐舞":"齐舞",
"机械舞":"机械舞",
"广场舞":"广场舞",
"BDF":"BDF",
"练习室":"练习室",
"美女舞蹈":"美女舞蹈",
"牛仔裤":"牛仔裤",
"黑丝":"黑丝",
"超短裤":"超短裤",
"超短裙":"超短裙",
"舞蹈综合":"舞蹈综合",
"舞蹈教程":"舞蹈教程",
"华语现场":"华语现场",
"欧美现场":"欧美现场",
"日语现场":"日语现场",
"韩语现场":"韩语现场",
"国语现场":"国语现场",
"粤语现场":"粤语现场",
"live":"live",
"音乐剧":"音乐剧",
"演唱会":"演唱会",
"音乐节":"音乐节",
"MV":"MV",
"华语MV":"华语MV",
"欧美MV":"欧美MV",
"日语MV":"日语MV",
"韩语MV":"韩语MV",
"国语MV":"国语MV",
"粤语MV":"粤语MV",
"闽南语MV":"闽南语MV",
"东南亚MV":"东南亚MV",
"英语MV":"英语MV",
"俄语MV":"俄语MV",
"印度MV":"印度MV",
"自制MV":"自制MV",
"韩国女星MV":"韩国女星MV",
"李孝利MV":"李孝利MV",
"李知恩MV":"李知恩MV",
"林允儿MV":"林允儿MV",
"金泫雅MV":"金泫雅MV",
"金泰妍MV":"金泰妍MV",
"李宣美MV":"李宣美MV",
"崔雪莉MV":"崔雪莉MV",
"安喜延MV":"安喜延MV",
"金亚荣MV":"金亚荣MV",
"李知恩MV":"李知恩MV",
"李贞贤MV":"李贞贤MV",
"洪真英MV":"洪真英MV",
"日本女星MV":"日本女星MV",
"YUIMV":"YUIMV",
"幸田来未MV":"幸田来未MV",
"安室奈美惠MV":"安室奈美惠MV",
"滨崎步MV":"滨崎步MV",
"古谷仁美MV":"古谷仁美MV",
"宇多田光MV":"宇多田光MV",
"伊藤由奈MV":"伊藤由奈MV",
"玉置成实MV":"玉置成实MV",
"仓木麻衣MV":"仓木麻衣MV",
"AngelaAkiMV":"AngelaMV",
"中岛美雪MV":"中岛美雪MV",
"女星MV":"女星MV",
"戴佩妮MV":"戴佩妮MV",
"邓紫棋MV":"邓紫棋MV",
"张韶涵MV":"张韶涵MV",
"蔡健雅MV":"蔡健雅MV",
"莫文蔚MV":"莫文蔚MV",
"刘若英MV":"刘若英MV",
"邓丽君MV":"邓丽君MV",
"蔡依林MV":"蔡依林MV",
"李宇春MV":"李宇春MV",
"徐佳莹MV":"徐佳莹MV",
"杨千嬅MV":"杨千嬅MV",
"张靓颖MV":"张靓颖MV",
"杨丞琳MV":"杨丞琳MV",
"萧亚轩MV":"萧亚轩MV",
"容祖儿MV":"容祖儿MV",
"梅艳芳MV":"梅艳芳MV",
"孙燕姿MV":"孙燕姿MV",
"袁娅维MV":"袁娅维MV",
"王菲MV":"王菲MV",
"梁静茹MV":"梁静茹MV",
"周慧敏MV":"周慧敏MV",
"张惠妹MV":"张惠妹MV",
"周笔畅MV":"周笔畅MV",
"谭维维MV":"谭维维MV",
"陈慧娴MV":"陈慧娴MV",
"郭静MV":"郭静MV",
"那英MV":"那英MV",
"韩红MV":"韩红MV",
"林忆莲MV":"林忆莲MV",
"李玟MV":"李玟MV",
"徐小凤MV":"徐小凤MV",
"卓依婷MV":"卓依婷MV",
"郁可唯MV":"郁可唯MV",
"田震MV":"田震MV",
"凤飞飞MV":"凤飞飞MV",
"谭晶MV":"谭晶MV",
"叶倩文MV":"叶倩文MV",
"王心凌MV":"王心凌MV",
"郭采洁MV":"郭采洁MV",
"阿黛尔MV":"阿黛尔MV",
"LadyGagaMV":"LadyGagaMV",
"布兰妮MV":"布兰妮MV",
"洛天依MV":"洛天依MV",
"初音未来MV":"初音未来MV",
"女团":"女团",
"中国女团":"中国女团",
"SNH48":"SNH48",
"S.H.E":"S.H.E",
"Twins":"Twins",
"火箭少女101":"火箭少女101",
"BY2":"BY2",
"S.I.N.G":"S.I.N.G",
"3unshine":"3unshine",
"蜜蜂少女队":"蜜蜂少女队",
"七朵组合":"七朵组合",
"GNZ48":"GNZ48",
"韩国女团":"韩国女团",
"TWICE":"TWICE",
"4MINUTE":"4MINUTE",
"EXID":"EXID",
"KARA":"KARA",
"TARA":"TARA",
"BLACKPINK":"BLACKPINK",
"LOONA":"LOONA",
"ITZY":"ITZY",
"RedVelvet":"RedVelvet",
"Everglow":"Everglow",
"Mamamoo":"Mamamoo",
"少女时代":"少女时代",
"S.E.S":"S.E.S",
"FIN.K.L":"FIN.K.L",
"2NE1":"2NE1",
"WonderGirls":"WonderGirls",
"IZ*ONE":"IZ*ONE",
"Sistar":"Sistar",
"Apink":"Apink",
"AOA":"AOA",
"GFRIEND":"GFRIEND",
"f(x)":"f(x)",
"(G)I-DLE":"(G)I-DLE",
"Itzy":"Itzy",
"Oh!GG":"Oh!GG",
"GirlCrush":"GirlCrush",
"日本女团":"日本女团",
"AKB48":"AKB48",
"SKE48":"SKE48",
"NMB48":"NMB48",
"JKT48":"JKT48",
"HKT48":"HKT48",
"AKB48TeamTP":"AKB48TeamTP",
"Perfume":"Perfume",
"桃色幸运草Z":"桃色幸运草Z",
"乃木坂46乃":"乃木坂46乃",
"樱坂46":"樱坂46",
"日向坂46":"日向坂46",
"E-girls":"E-girls",
"NiziU":"NiziU",
"BiSH":"BiSH",
"早安少女组":"早安少女组",
"戏曲":"戏曲",
"演唱会":"演唱会",
"相声小品":"相声小品",
"动物世界":"动物世界",
"儿童少儿":"儿童少儿"
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
		result = {
			'list':[]
		}
		return result
	cookies = ''
	def getCookie(self):
		rsp = self.fetch("https://www.bilibili.com/")
		self.cookies = rsp.cookies
		return rsp.cookies
	def categoryContent(self,tid,pg,filter,extend):		
		result = {}
		url = 'https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={0}&duration=4&page={1}'.format(tid,pg)
		if len(self.cookies) <= 0:
			self.getCookie()
		rsp = self.fetch(url,cookies=self.cookies)
		content = rsp.text
		jo = json.loads(content)
		if jo['code'] != 0:			
			rspRetry = self.fetch(url,cookies=self.getCookie())
			content = rspRetry.text		
		jo = json.loads(content)
		videos = []
		vodList = jo['data']['result']
		for vod in vodList:
			aid = str(vod['aid']).strip()
			title = vod['title'].strip().replace("<em class=\"keyword\">","").replace("</em>","")
			img = 'https:' + vod['pic'].strip()
			remark = str(vod['duration']).strip()
			videos.append({
				"vod_id":aid,
				"vod_name":title,
				"vod_pic":img,
				"vod_remarks":remark
			})
		result['list'] = videos
		result['page'] = pg
		result['pagecount'] = 9999
		result['limit'] = 90
		result['total'] = 999999
		return result
	def cleanSpace(self,str):
		return str.replace('\n','').replace('\t','').replace('\r','').replace(' ','')
	def detailContent(self,array):
		aid = array[0]
		url = "https://api.bilibili.com/x/web-interface/view?aid={0}".format(aid)

		rsp = self.fetch(url,headers=self.header)
		jRoot = json.loads(rsp.text)
		jo = jRoot['data']
		title = jo['title'].replace("<em class=\"keyword\">","").replace("</em>","")
		pic = jo['pic']
		desc = jo['desc']
		typeName = jo['tname']
		vod = {
			"vod_id":aid,
			"vod_name":title,
			"vod_pic":pic,
			"type_name":typeName,
			"vod_year":"",
			"vod_area":"",
			"vod_remarks":"",
			"vod_actor":"",
			"vod_director":"",
			"vod_content":desc
		}
		ja = jo['pages']
		playUrl = ''
		for tmpJo in ja:
			cid = tmpJo['cid']
			part = tmpJo['part']
			playUrl = playUrl + '{0}${1}_{2}#'.format(part,aid,cid)

		vod['vod_play_from'] = 'B站'
		vod['vod_play_url'] = playUrl

		result = {
			'list':[
				vod
			]
		}
		return result
	def searchContent(self,key,quick):
		result = {
			'list':[]
		}
		return result
	def playerContent(self,flag,id,vipFlags):
		# https://www.555dianying.cc/vodplay/static/js/playerconfig.js
		result = {}

		ids = id.split("_")
		url = 'https://api.bilibili.com:443/x/player/playurl?avid={0}&cid=%20%20{1}&qn=112'.format(ids[0],ids[1])
		rsp = self.fetch(url)
		jRoot = json.loads(rsp.text)
		jo = jRoot['data']
		ja = jo['durl']
		
		maxSize = -1
		position = -1
		for i in range(len(ja)):
			tmpJo = ja[i]
			if maxSize < int(tmpJo['size']):
				maxSize = int(tmpJo['size'])
				position = i

		url = ''
		if len(ja) > 0:
			if position == -1:
				position = 0
			url = ja[position]['url']

		result["parse"] = 0
		result["playUrl"] = ''
		result["url"] = url
		result["header"] = {
			"Referer":"https://www.bilibili.com",
			"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
		}
		result["contentType"] = 'video/x-flv'
		return result

	config = {
		"player": {},
		"filter": {}
	}
	header = {}

	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]