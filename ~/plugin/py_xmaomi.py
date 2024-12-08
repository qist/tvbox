#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import json

class Spider(Spider):  # 元类 默认的元类 type
	def getName(self):
		return "x小猫咪"
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
			"电影":"1",
			"电视剧":"2",
			"综艺":"3",
			"动漫":"4",
			"纪录":"5"
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
		tmpRsp = self.fetch("https://xmaomi.net/")
		suffix = self.regStr(tmpRsp.text,"window.location.href =\"(\\S+)\"")
		url = "https://xmaomi.net"+suffix
		# self.cookie = rsp.cookies
		rsp = self.fetch(url,cookies=tmpRsp.cookies)
		root = self.html(rsp.text)
		print(rsp.text[0])
		print(root)
		aList = root.xpath("//ul[contains(@class,'hl-vod-list')]/li/a")
		videos = []
		for a in aList:
			name = a.xpath('./@title')[0]
			pic = a.xpath('./@data-original')[0]
			mark = a.xpath("./div[@class='hl-pic-text']/span/text()")[0]
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

		urlParams = ["", "", "", "", "", "", "", "", "", "", "", ""]
		urlParams[0] = tid
		urlParams[8] = pg
		for key in extend:
			urlParams[int(key)] = extend[key]
		params = '-'.join(urlParams)
		url = 'https://xmaomi.net/vod_____show/{0}.html'.format(params)
		tmpRsp = self.fetch(url)
		suffix = self.regStr(tmpRsp.text,"window.location.href =\"(\\S+)\"")
		url = 'https://xmaomi.net'+suffix
		rsp = self.fetch(url,cookies=tmpRsp.cookies)
		root = self.html(rsp.text)
		print(rsp.text[0])
		print(root)
		aList = root.xpath("//ul[contains(@class,'hl-vod-list')]/li/a")
		videos = []
		for a in aList:
			name = a.xpath('./@title')[0]
			pic = a.xpath('./@data-original')[0]
			mark = a.xpath("./div[@class='hl-pic-text']/span/text()")[0]
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
		url = 'https://xmaomi.net/{0}.html'.format(tid)
		tmpRsp = self.fetch(url)
		suffix = self.regStr(tmpRsp.text,"window.location.href =\"(\\S+)\"")
		url = "https://xmaomi.net"+suffix
		rsp = self.fetch(url,cookies=tmpRsp.cookies)
		root = self.html(rsp.text)
		print(rsp.text[0])
		print(root)
		divContent = root.xpath("//div[contains(@class,'hl-full-box')]")[0]
		title = divContent.xpath("./div[@class='hl-item-pic']/span/@title")[0]
		pic = divContent.xpath("./div[@class='hl-item-pic']/span/@data-original")[0]
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
		liArray = divContent.xpath(".//li")
		for li in liArray:
			content = li.xpath('string(.)')
			if content.startswith('类型'):
				vod['type_name'] = content
			if content.startswith('年份'):
				vod['vod_year'] = content
			if content.startswith('地区'):
				vod['vod_area'] = content
			if content.startswith('状态'):
				vod['vod_remarks'] = content
			if content.startswith('主演'):
				vod['vod_actor'] = content
			if content.startswith('导演'):
				vod['vod_director'] = content
			if content.startswith('简介'):
				vod['vod_content'] = content

		vod_play_from = '$$$'
		playFrom = []
		vodHeader = root.xpath("//div[contains(@class,'hl-rb-tips')]//span[@class='hl-text-site']/text()")
		for v in vodHeader:
			playFrom.append(v)
		vod_play_from = vod_play_from.join(playFrom)
		
		vod_play_url = '$$$'
		playList = []
		vodList = root.xpath(".//div[contains(@class,'hl-play-source')]//ul")
		for vl in vodList:
			vodItems = []
			aList = vl.xpath('./li/a')
			for tA in aList:
				href = tA.xpath('./@href')[0]
				name = tA.xpath('string(.)')
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
		url = 'https://xmaomi.net/v_search/{0}-------------.html'.format(key)
		tmpRsp = self.fetch(url)
		suffix = self.regStr(tmpRsp.text,"window.location.href =\"(\\S+)\"")
		url = "https://xmaomi.net"+suffix
		rsp = self.fetch(url,cookies=tmpRsp.cookies)
		root = self.html(rsp.text)
		print(rsp.text[0])
		print(root)
		aList = root.xpath("//ul[contains(@class,'hl-one-list')]/li//a[contains(@class,'hl-item-thumb')]")
		videos = []
		for a in aList:
			name = a.xpath('./@title')[0]
			print(name)
			pic = a.xpath('./@data-original')[0]
			print(pic)
			mark = a.xpath("./div[@class='hl-pic-text']/span/text()")[0]
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
	def playerContent(self,flag,id,vipFlags):
		url = 'https://xmaomi.net/{0}.html'.format(id)
		tmpRsp = self.fetch(url)
		suffix = self.regStr(tmpRsp.text,"window.location.href =\"(\\S+)\"")
		url = "https://xmaomi.net"+suffix
		rsp = self.fetch(url,cookies=tmpRsp.cookies)
		root = self.html(rsp.text)
		print(rsp.text[0])
		print(root)
		scripts = root.xpath("//script/text()")
		jo = {}
		for script in scripts:
			if(script.startswith("var player_")):
				target = script[script.index('{'):]
				jo = json.loads(target)
				break;
		parseUrl = ""
		print(jo)
		htmlUrl = 'https://play.fositv.com/?url={0}&tm={1}&key={2}&next=&title='.format(jo['url'],jo['tm'],jo['key'])
		htmlRsp = self.fetch(htmlUrl)
		htmlRoot = self.html(htmlRsp.text)
		configScripts = htmlRoot.xpath("//script/text()")
		configJo = {}
		for script in configScripts:
			if(script.strip().startswith("var config")):
				target = script[script.index('{'):(script.index('}')+1)]
				configJo = json.loads(target)
				break;
		param = {
			'url': configJo['url'],
			'time': configJo['time'],
			'key': configJo['key']
		}
		postRsp = self.post('https://play.fositv.com/API.php',param)
		resultJo = json.loads(postRsp.text)
		result = {
			'parse':0,
			'playUrl':'',
			'url':resultJo['url'],
			'header':{
				'User-Agent':resultJo['ua']
			}
		}
		return result

	cookie = {}
	config = {
		"player": {},
		"filter": {"1":[{"key":0,"name":"分类","value":[{"n":"全部","v":"1"},{"n":"动作","v":"101"},{"n":"喜剧","v":"102"},{"n":"爱情","v":"103"},{"n":"科幻","v":"104"},{"n":"剧情","v":"105"},{"n":"悬疑","v":"106"},{"n":"惊悚","v":"107"},{"n":"恐怖","v":"108"},{"n":"犯罪","v":"109"},{"n":"谍战","v":"110"},{"n":"冒险","v":"111"},{"n":"奇幻","v":"112"},{"n":"灾难","v":"113"},{"n":"战争","v":"114"},{"n":"动画","v":"115"},{"n":"歌舞","v":"116"},{"n":"历史","v":"117"},{"n":"传记","v":"118"},{"n":"纪录","v":"119"},{"n":"其他","v":"120"}]},{"key":1,"name":"地区","value":[{"n":"全部","v":""},{"n":"中国大陆","v":"中国大陆"},{"n":"中国香港","v":"中国香港"},{"n":"中国台湾","v":"中国台湾"},{"n":"美国","v":"美国"},{"n":"韩国","v":"韩国"},{"n":"日本","v":"日本"},{"n":"法国","v":"法国"},{"n":"英国","v":"英国"},{"n":"德国","v":"德国"},{"n":"泰国","v":"泰国"},{"n":" 印度","v":"印度"},{"n":"其他","v":"其他"}]},{"key":11,"name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"},{"n":"2003","v":"2003"},{"n":"2002","v":"2002"},{"n":"2001","v":"2001"},{"n":"2000","v":"2000"}]},{"key":5,"name":"字母","value":[{"n":"字母","v":""},{"n":"A","v":"A"},{"n":"B","v":"B"},{"n":"C","v":"C"},{"n":"D","v":"D"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]},{"key":2,"name":"排序","value":[{"n":"最新","v":"time"},{"n":"最热","v":"hits"},{"n":"评分","v":"score"}]}],"2":[{"key":0,"name":"分类","value":[{"n":"全部","v":"2"},{"n":"武侠","v":"201"},{"n":"喜剧","v":"202"},{"n":"爱情","v":"203"},{"n":"剧情","v":"204"},{"n":"青春","v":"205"},{"n":"悬疑","v":"206"},{"n":"科幻","v":"207"},{"n":"军事","v":"208"},{"n":"警匪","v":"209"},{"n":"谍战","v":"210"},{"n":"奇幻","v":"211"},{"n":"偶 像","v":"212"},{"n":"年代","v":"213"},{"n":"乡村","v":"214"},{"n":"都市","v":"215"},{"n":"家庭","v":"216"},{"n":"古装","v":"217"},{"n":"历史","v":"218"},{"n":"神话","v":"219"},{"n":"其他","v":"220"}]},{"key":1,"name":"地区","value":[{"n":"全部","v":""},{"n":"中国大陆","v":"中国大陆"},{"n":"中国香港","v":"中国香港"},{"n":"中国台湾","v":"中国台湾"},{"n":"美国","v":"美国"},{"n":"韩国","v":"韩国"},{"n":"日本","v":"日本"},{"n":"法国","v":"法国"},{"n":"英国","v":"英国"},{"n":"德国","v":"德国"},{"n":"泰国","v":"泰国"},{"n":"印度","v":"印 度"},{"n":"其他","v":"其他"}]},{"key":11,"name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"},{"n":"2003","v":"2003"},{"n":"2002","v":"2002"},{"n":"2001","v":"2001"},{"n":"2000","v":"2000"}]},{"key":5,"name":"字母","value":[{"n":"字母","v":""},{"n":"A","v":"A"},{"n":"B","v":"B"},{"n":"C","v":"C"},{"n":"D","v":"D"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]},{"key":2,"name":"排序","value":[{"n":"最新","v":"time"},{"n":"最热","v":"hits"},{"n":"评分","v":"score"}]}],"3":[{"key":0,"name":"分类","value":[{"n":"全部","v":"3"},{"n":"脱口秀","v":"301"},{"n":"真人秀","v":"302"},{"n":"搞笑","v":"303"},{"n":"访谈","v":"304"},{"n":"生活","v":"305"},{"n":"晚会","v":"306"},{"n":"美食","v":"307"},{"n":"游戏","v":"308"},{"n":"亲子","v":"309"},{"n":"旅游","v":"310"},{"n":"文化","v":"311"},{"n":"体育","v":"312"},{"n":"时尚","v":"313"},{"n":"纪实","v":"314"},{"n":"益智","v":"315"},{"n":"演艺","v":"316"},{"n":"歌舞","v":"317"},{"n":"音乐","v":"318"},{"n":"播报","v":"319"},{"n":"其他","v":"320"}]},{"key":1,"name":"地区","value":[{"n":"全部","v":""},{"n":"中国大陆","v":"中国大陆"},{"n":"中国香港","v":"中国香港"},{"n":"中国台湾","v":"中国台湾"},{"n":"美国","v":"美国"},{"n":"韩国","v":"韩国"},{"n":"日本","v":"日本"},{"n":"法国","v":"法国"},{"n":"英国","v":"英国"},{"n":"德国","v":"德国"},{"n":"泰国","v":"泰国"},{"n":"印度","v":"印度"},{"n":"其他","v":"其他"}]},{"key":11,"name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"},{"n":"2003","v":"2003"},{"n":"2002","v":"2002"},{"n":"2001","v":"2001"},{"n":"2000","v":"2000"}]},{"key":5,"name":"字母","value":[{"n":"字母","v":""},{"n":"A","v":"A"},{"n":"B","v":"B"},{"n":"C","v":"C"},{"n":"D","v":"D"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]},{"key":2,"name":"排序","value":[{"n":"最新","v":"time"},{"n":"最热","v":"hits"},{"n":"评分","v":"score"}]}],"4":[{"key":0,"name":"分类","value":[{"n":"全部","v":"4"},{"n":"热血","v":"401"},{"n":"格斗","v":"402"},{"n":"恋爱","v":"403"},{"n":"美少女","v":"404"},{"n":"校园","v":"405"},{"n":"搞笑","v":"406"},{"n":"LOLI","v":"407"},{"n":"神魔","v":"408"},{"n":"机战","v":"409"},{"n":"科幻","v":"410"},{"n":"真人","v":"411"},{"n":"青春","v":"412"},{"n":"魔法","v":"413"},{"n":"神话","v":"414"},{"n":"冒险","v":"415"},{"n":"运动","v":"416"},{"n":"竞技","v":"417"},{"n":"童话","v":"418"},{"n":"亲子","v":"419"},{"n":"教育","v":"420"}]},{"key":1,"name":"地区","value":[{"n":"全部","v":""},{"n":"中国大陆","v":"中国大陆"},{"n":"中国香港","v":"中国香港"},{"n":"中国台湾","v":"中国台湾"},{"n":"美国","v":"美国"},{"n":"韩国","v":"韩国"},{"n":"日本","v":"日本"},{"n":"法国","v":"法国"},{"n":"英国","v":"英国"},{"n":"德国","v":"德国"},{"n":"泰国","v":"泰国"},{"n":"印度","v":"印度"},{"n":"其他","v":"其他"}]},{"key":11,"name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"},{"n":"2003","v":"2003"},{"n":"2002","v":"2002"},{"n":"2001","v":"2001"},{"n":"2000","v":"2000"}]},{"key":5,"name":"字母","value":[{"n":"字母","v":""},{"n":"A","v":"A"},{"n":"B","v":"B"},{"n":"C","v":"C"},{"n":"D","v":"D"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]},{"key":2,"name":"排序","value":[{"n":"最新","v":"time"},{"n":"最热","v":"hits"},{"n":"评分","v":"score"}]}],"5":[{"key":0,"name":"分类","value":[{"n":"全部","v":"5"},{"n":"人物","v":"501"},{"n":"军事","v":"502"},{"n":"历史","v":"503"},{"n":"自然","v":"504"},{"n":"探险","v":"505"},{"n":"科技","v":"506"},{"n":"文化","v":"507"},{"n":"刑侦","v":"508"},{"n":"社会","v":"509"},{"n":"旅游","v":"510"},{"n":"其他","v":"511"}]},{"key":1,"name":"地区","value":[{"n":"全部","v":""},{"n":"中国大陆","v":"中国大陆"},{"n":"中国香港","v":"中国香港"},{"n":"中国台湾","v":"中国台湾"},{"n":"美国","v":"美国"},{"n":"韩国","v":"韩国"},{"n":"日本","v":"日本"},{"n":"法国","v":"法国"},{"n":"英国","v":"英国"},{"n":"德国","v":"德国"},{"n":"泰国","v":"泰国"},{"n":"印度","v":"印度"},{"n":"其他","v":"其他"}]},{"key":11,"name":"年份","value":[{"n":"全部","v":""},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"},{"n":"2003","v":"2003"},{"n":"2002","v":"2002"},{"n":"2001","v":"2001"},{"n":"2000","v":"2000"}]},{"key":5,"name":"字母","value":[{"n":"字母","v":""},{"n":"A","v":"A"},{"n":"B","v":"B"},{"n":"C","v":"C"},{"n":"D","v":"D"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]},{"key":2,"name":"排序","value":[{"n":"最新","v":"time"},{"n":"最热","v":"hits"},{"n":"评分","v":"score"}]}]}
	}
	header = {}

	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]