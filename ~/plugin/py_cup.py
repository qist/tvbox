#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import json

class Spider(Spider):  # 元类 默认的元类 type
	def getName(self):
		return "茶杯狐"
	def init(self,extend=""):
		print("============{0}============".format(extend))
		pass
	def homeContent(self,filter):
		result = {}
		cateManual = {
			"电视剧":"20",
			"电影":"21",
			"动漫":"22",
			"综艺":"23",
			"纪录片":"24"
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
		rsp = self.fetch("http://www.qifudata.com/")
		root = self.html(rsp.text)
		aList = root.xpath("//div[@class='stui-vodlist__box']/a")

		videos = []
		for a in aList:
			name = a.xpath('./@title')[0]
			pic = a.xpath('./@data-original')[0]
			mark = a.xpath("./span[@class='pic-text text-right']/text()")[0]
			sid = a.xpath("./@href")[0]
			sid = self.regStr(sid,"/spx/(\\S+).html")
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
		if 'id' not in extend.keys():
			extend['id'] = tid
		extend['page'] = pg
		filterParams = ["id", "area", "by", "class", "lang", "", "", "", "page", "", "", "year"]
		params = ["", "", "", "", "", "", "", "", "", "", "", ""]
		for idx in range(len(filterParams)):
			fp = filterParams[idx]
			if fp in extend.keys():
				params[idx] = extend[fp]
		suffix = '-'.join(params)
		url = 'http://www.qifudata.com/vodshow/{0}.html'.format(suffix)
		rsp = self.fetch(url)
		root = self.html(rsp.text)
		aList = root.xpath("//div[@class='stui-vodlist__box']/a")
		videos = []
		for a in aList:
			name = a.xpath('./@title')[0]
			pic = a.xpath('./@data-original')[0]
			mark = a.xpath("./span[@class='pic-text text-right']/b/text()")[0]
			sid = a.xpath("./@href")[0]
			sid = self.regStr(sid,"/spx/(\\S+).html")
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
		url = 'http://www.qifudata.com/spx/{0}.html'.format(tid)
		rsp = self.fetch(url)
		root = self.html(rsp.text)
		node = root.xpath("//div[@class='stui-content']")[0]

		pic = node.xpath(".//img/@data-original")[0]
		title = node.xpath('.//h1/text()')[0]
		detail = node.xpath(".//span[@class='detail-content']/text()")[0]

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
			"vod_content":detail
		}

		infoArray = node.xpath(".//div[@class='stui-content__detail']/p")
		for info in infoArray:
			content = info.xpath('string(.)')
			if content.startswith('类型'):
				vod['type_name'] = content
			# if content.startswith('年份'):
			# 	vod['vod_year'] = content
			# if content.startswith('地区'):
			# 	vod['vod_area'] = content
			# if content.startswith('更新'):
			# 	vod['vod_remarks'] = content.replace('\n','').replace('\t','')
			if content.startswith('主演'):
				vod['vod_actor'] = content.replace('\n','').replace('\t','')
			if content.startswith('导演'):
				vod['vod_director'] = content.replace('\n','').replace('\t','')
			# if content.startswith('剧情'):
			# 	vod['vod_content'] = content.replace('\n','').replace('\t','')

		vod_play_from = '$$$'
		playFrom = []
		vodHeader = root.xpath("//div[@class='stui-vodlist__head']/h3/text()")
		for v in vodHeader:
			playFrom.append(v)
		vod_play_from = vod_play_from.join(playFrom)
		
		vod_play_url = '$$$'
		playList = []
		vodList = root.xpath("//ul[contains(@class,'stui-content__playlist')]")
		for vl in vodList:
			vodItems = []
			aList = vl.xpath('./li/a')
			for tA in aList:
				href = tA.xpath('./@href')[0]
				name = tA.xpath('./text()')[0]
				tId = self.regStr(href,'/sp/(\\S+).html')
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
		url = 'http://www.qifudata.com/index.php/ajax/suggest?mid=1&wd={0}'.format(key)
		# getHeader()
		rsp = self.fetch(url)
		jo = json.loads(rsp.text)
		result = {}
		jArray = []
		if int(jo['total']) > 0:
			for j in jo['list']:
				jArray.append({
					"vod_id": j['id'],
					"vod_name": j['name'],
					"vod_pic": j['pic'],
					"vod_remarks": ""
				})
		result = {
			'list':jArray
		}
		return result

	config = {
		"player": {
			"dpp": {
				"sh": "DP播放",
				"pu": "https://jx.qifudata.com/?url=",
				"sn": 1,
				"or": 999
			}
		},
		"filter": {"20": [{"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""},{"n": "剧情", "v": "剧情"},{"n": "古装", "v": "古装"},{"n": "武侠", "v": "武侠"},{"n": "奇幻", "v": "奇幻"},{"n": "科幻", "v": "科幻"},{"n": "动作", "v": "动作"},{"n": "喜剧", "v": "喜剧"},{"n": "爱情", "v": "爱情"},{"n": "励志", "v": "励志"},{"n": "冒险", "v": "冒险"},{"n": "歌舞", "v": "歌舞"},{"n": "音乐", "v": "音乐"},{"n": "恐怖", "v": "恐怖"},{"n": "惊悚", "v": "惊悚"},{"n": "丧尸", "v": "丧尸"},{"n": "战争", "v": "战争"},{"n": "传记", "v": "传记"},{"n": "纪录", "v": "纪录"},{"n": "犯罪", "v": "犯罪"},{"n": "悬疑", "v": "悬疑"},{"n": "西部", "v": "西部"},{"n": "灾难", "v": "灾难"},{"n": "家庭", "v": "家庭"},{"n": "短片", "v": "短片"},{"n": "校园", "v": "校园"},{"n": "文艺", "v": "文艺"},{"n": "运动", "v": "运动"},{"n": "青春", "v": "青春"},{"n": "同性", "v": "同性"},{"n": "人性", "v": "人性"},{"n": "美食", "v": "美食"},{"n": "女性", "v": "女性"},{"n": "治愈", "v": "治愈"},{"n": "历史", "v": "历史"}]}, {"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n": "大陆", "v": "大陆"}, {"n": "香港", "v": "香港"}, {"n": "台湾", "v": "台湾"}, {"n": "欧美", "v": "欧美"}, {"n": "韩国", "v": "韩国"}, {"n": "日本", "v": "日本"}, {"n": "泰国", "v": "泰国"}, {"n": "印度", "v": "印度"}, {"n": "俄罗斯", "v": "俄罗斯"}, {"n": "其他", "v": "其他"}]}, {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, {"n": "2012", "v": "2012"}, {"n": "2011", "v": "2011"}, {"n": "2010", "v": "2010"}, {"n": "2009", "v": "2009"}, {"n": "2008", "v": "2008"}, {"n": "2007", "v": "2007"}, {"n": "2006", "v": "2006"}, {"n": "2005", "v": "2005"}, {"n": "2004", "v": "2004"}, {"n": "2003", "v": "2003"}, {"n": "2002", "v": "2002"}, {"n": "2001", "v": "2001"}, {"n": "2000", "v": "2000"}]}, {"key": "lang", "name": "语言", "value": [{"n": "全部", "v": ""}, {"n": "英语", "v": "英语"}, {"n": "韩语", "v": "韩语"}, {"n": "日语", "v": "日语"}, {"n": "法语", "v": "法语"}, {"n": "泰语", "v": "泰语"}, {"n": "德语", "v": "德语"}, {"n": "印度语", "v": "印度语"}, {"n": "国语", "v": "国语"}, {"n": "粤 语", "v": "粤语"}, {"n": "俄语", "v": "俄语"}, {"n": "西班牙语", "v": "西班牙语"}, {"n": "意大利语", "v": "意大利语"}, {"n": "其它", "v": "其它"}]}, {"key": "by", "name": "排序", "value": [{"n": "最新", "v": "time"}, {"n": "最热", "v": "hits"}, {"n": "评分", "v": "score"}]}], "21": [{"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "剧情", "v": "剧情"},{"n": "古装", "v": "古装"},{"n": "武侠", "v": "武侠"},{"n": "奇幻", "v": "奇幻"},{"n": "科幻", "v": "科幻"},{"n": "动作", "v": "动作"},{"n": "喜剧", "v": "喜剧"},{"n": "爱情", "v": "爱情"},{"n": "励志", "v": "励志"},{"n": "冒险", "v": "冒险"},{"n": "歌舞", "v": "歌舞"},{"n": "音乐", "v": "音乐"},{"n": "恐怖", "v": "恐怖"},{"n": "惊悚", "v": "惊悚"},{"n": "丧尸", "v": "丧尸"},{"n": "战争", "v": "战争"},{"n": "传记", "v": "传记"},{"n": "纪录", "v": "纪录"},{"n": "犯罪", "v": "犯罪"},{"n": "悬疑", "v": "悬疑"},{"n": "西部", "v": "西部"},{"n": "灾难", "v": "灾难"},{"n": "家庭", "v": "家庭"},{"n": "短片", "v": "短片"},{"n": "校园", "v": "校园"},{"n": "文艺", "v": "文艺"},{"n": "运动", "v": "运动"},{"n": "青春", "v": "青春"},{"n": "同性", "v": "同性"},{"n": "人性", "v": "人性"},{"n": "美食", "v": "美食"},{"n": "女性", "v": "女性"},{"n": "治愈", "v": "治愈"},{"n": "历史", "v": "历史"}]}, {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, {"n": "2012", "v": "2012"}, {"n": "2011", "v": "2011"}, {"n": "2010", "v": "2010"}, {"n": "2009", "v": "2009"}, {"n": "2008", "v": "2008"}, {"n": "2006", "v": "2006"}, {"n": "2005", "v": "2005"}, {"n": "2004", "v": "2004"}]}, {"key": "lang", "name": "语言", "value": [{"n": "全部", "v": ""}, {"n": "英语", "v": "英语"}, {"n": "法语", "v": "法语"}]}, {"key": "by", "name": "排序", "value": [{"n": "最新", "v": "time"}, {"n": "最热", "v": "hits"}, {"n": "评分", "v": "score"}]}], "22": [{"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "冒险", "v": "冒险"},{"n": "玄幻", "v": "玄幻"},{"n": "魔幻", "v": "魔幻"},{"n": "武侠", "v": "武侠"},{"n": "恋爱", "v": "恋爱"},{"n": "推理", "v": "推理"},{"n": "日常", "v": "日常"},{"n": "校园", "v": "校园"},{"n": "悬疑", "v": "悬疑"},{"n": "剧情", "v": "剧情"},{"n": "萌系", "v": "萌系"},{"n": "科幻", "v": "科幻"},{"n": "日常", "v": "日常"},{"n": "战斗", "v": "战斗"},{"n": "战争", "v": "战争"},{"n": "热血", "v": "热血"},{"n": "机战", "v": "机战"},{"n": "游戏", "v": "游戏"},{"n": "搞笑", "v": "搞笑"},{"n": "恋爱", "v": "恋爱"},{"n": "后宫", "v": "后宫"},{"n": "百合", "v": "百合"},{"n": "基腐", "v": "基腐"},{"n": "冒险", "v": "冒险"},{"n": "儿童", "v": "儿童"},{"n": "歌舞", "v": "歌舞"},{"n": "音乐", "v": "音乐"},{"n": "奇幻", "v": "奇幻"},{"n": "恐怖", "v": "恐怖"},{"n": "惊悚", "v": "惊悚"},{"n": "犯罪", "v": "犯罪"},{"n": "西部", "v": "西部"},{"n": "灾难", "v": "灾难"},{"n": "古装", "v": "古装"},{"n": "泡面", "v": "泡面"},{"n": "运动", "v": "运动"},{"n": "体育", "v": "体育"},{"n": "青春", "v": "青春"},{"n": "美食", "v": "美食"},{"n": "治愈", "v": "治愈"},{"n": "致郁", "v": "致郁"},{"n": "励志", "v": "励志"},{"n": "历史", "v": "历史"},{"n": "真人", "v": "真人"},{"n": "竞技", "v": "竞技"},{"n": "其他", "v": "其他"}]}, {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, {"n": "2012", "v": "2012"}, {"n": "2011", "v": "2011"}, {"n": "2010", "v": "2010"}, {"n": "2009", "v": "2009"}, {"n": "2008", "v": "2008"}, {"n": "2007", "v": "2007"}, {"n": "2006", "v": "2006"}, {"n": "2005", "v": "2005"}, {"n": "2004", "v": "2004"}, {"n": "2003", "v": "2003"}, {"n": "2002", "v": "2002"}, {"n": "2001", "v": "2001"}, {"n": "2000", "v": "2000"}]}, {"key": "by", "name": "排序", "value": [{"n": "最新", "v": "time"}, {"n": "最热", "v": "hits"}, {"n": "评分", "v": "score"}]}], "23": [{"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "游戏", "v": "游戏"},{"n": "音乐", "v": "音乐"},{"n": "养成", "v": "养成"},{"n": "情感", "v": "情感"},{"n": "喜剧", "v": "喜剧"},{"n": "搞笑", "v": "搞笑"},{"n": "脱口秀", "v": "脱口秀"},{"n": "表演", "v": "表演"},{"n": "体验", "v": "体验"},{"n": "亲子", "v": "亲子"},{"n": "文化", "v": "文化"},{"n": "美食", "v": "美食"},{"n": "职场", "v": "职场"},{"n": "体育", "v": "体育"},{"n": "潮流文化", "v": "潮流文化"},{"n": "访谈", "v": "访谈"},{"n": "生活服务", "v": "生活服务"},{"n": "萌宠", "v": "萌宠"},{"n": "资讯", "v": "资讯"},{"n": "曲艺", "v": "曲艺"},{"n": "职场", "v": "职场"},{"n": "晚会", "v": "晚会"}]}, {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, {"n": "2012", "v": "2012"}, {"n": "2011", "v": "2011"}, {"n": "2010", "v": "2010"}, {"n": "2009", "v": "2009"}, {"n": "2008", "v": "2008"}, {"n": "2007", "v": "2007"}, {"n": "2006", "v": "2006"}, {"n": "2005", "v": "2005"}, {"n": "2004", "v": "2004"}, {"n": "2003", "v": "2003"}, {"n": "2002", "v": "2002"}, {"n": "2001", "v": "2001"}, {"n": "2000", "v": "2000"}]}, {"key": "by", "name": "排序", "value": [{"n": "最新", "v": "time"}, {"n": "最热", "v": "hits"}, {"n": "评分", "v": "score"}]}], "24": [{"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "纪录", "v": "纪录"},{"n": "真人秀", "v": "真人秀"},{"n": "自然", "v": "自然"},{"n": "传记", "v": "传记"},{"n": "文化", "v": "文化"},{"n": "情", "v": "情"},{"n": "运动", "v": "运动"}]}, {"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n": "国产", "v": "国产"}, {"n": "日本", "v": "日本"}, {"n": "欧美", "v": "欧美"}, {"n": "其他", "v": "其他"}]}, {"key": "lang", "name": "语言", "value": [{"n": "全部", "v": ""}, {"n": "国语", "v": "国语"}, {"n": "日语", "v": "日语"}, {"n": "英语", "v": "英语"}, {"n": "其他", "v": "其他"}]}, {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, {"n": "2012", "v": "2012"}, {"n": "2011", "v": "2011"}, {"n": "2010", "v": "2010"}, {"n": "2009", "v": "2009"}, {"n": "2008", "v": "2008"}, {"n": "2007", "v": "2007"}, {"n": "2006", "v": "2006"}, {"n": "2005", "v": "2005"}, {"n": "2004", "v": "2004"}, {"n": "2003", "v": "2003"}, {"n": "2002", "v": "2002"}, {"n": "2001", "v": "2001"}, {"n": "2000", "v": "2000"}]}, {"key": "by", "name": "排序", "value": [{"n": "最新", "v": "time"}, {"n": "最热", "v": "hits"}, {"n": "评分", "v": "score"}]}]}
	}
	header = {
		"origin":"http://www.qifudata.com/",
		"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
		"Accept":" */*",
		"Accept-Language":"zh-CN,zh;q=0.9,en-US;q=0.3,en;q=0.7",
		"Accept-Encoding":"gzip, deflate"
	}
	def playerContent(self,flag,id,vipFlags):
		result = {}
		url = 'http://www.qifudata.com/sp/{0}.html'.format(id)
		rsp = self.fetch(url)
		root = self.html(rsp.text)
		scripts = root.xpath("//script/text()")
		jo = {}
		for script in scripts:
			if(script.startswith("var player_")):
				target = script[script.index('{'):]
				jo = json.loads(target)
				break;
		parseUrl = ''
		# src="(\S+url=)
		# playerConfig = self.config['player']
		# if jo['from'] in self.config['player']:
		# 	playerConfig = self.config['player'][jo['from']]
		# 	parseUrl = playerConfig['pu'] + jo['url']
		scriptUrl = 'http://www.qifudata.com/static/js/playerconfig.js'
		scriptRsp = self.fetch(scriptUrl)
		scriptRsp = scriptRsp.text
		parseUrl = self.regStr(scriptRsp, 'player_list=(.*?),Mac')
		if len(parseUrl) > 0:
			jo1 = json.loads(parseUrl)
			jo1 = jo1[jo['from']]
			realUrl = jo['url']
			result["parse"] = 1
			result["playUrl"] = jo1['parse']
			result["url"] = realUrl
			result["header"] = json.dumps(self.header)
		return result
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]