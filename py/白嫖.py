#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import json
import base64
from urllib.parse import unquote
import re
from Crypto.Cipher import ARC4

class Spider(Spider):  # 元类 默认的元类 type
	def getName(self):
		return "白嫖影视"
	def init(self,extend=""):
		print("============{0}============".format(extend))
		pass
	def isVideoFormat(self,url):
		pass
	def rc4_decrypt(self,data, key1): 
		data = base64.b64decode(data)
		key = bytes(key1, encoding='utf-8')
		enc = ARC4.new(key)
		res = enc.decrypt(data)
		res = str(res,'utf-8')
		return res
	def manualVideoCheck(self):
		pass	
	def homeContent(self,filter):
		result = {}
		cateManual = {
			"电影":"1",
			"电视剧":"2",
			"动漫":"3",
			"爽文短剧":"4",
			"综艺":"5"
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
		rsp = self.fetch("https://www.baipiaoys.com:9092")
		root = self.html(rsp.text)
		aList = root.xpath("//div[@class='stui-vodlist__box']/a")

		videos = []
		for a in aList:
			name = a.xpath('./@title')[0]
			pic = a.xpath('./@data-original')[0]
			remark = a.xpath("./span[@class='pic-text text-right']/text()")[0]
			sid = a.xpath("./@href")[0]
			sid = self.regStr(sid,"/detail/(\\S+).html")
			videos.append({
				"vod_id":sid,
				"vod_name":name,
				"vod_pic":pic,
				"vod_remarks":remark
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
		filterParams = ["area", "by", "class", "id", "lang", "", "", "", "page", "", "", "year"]
		params = ["", "", "", "", "", "", "", "", "", "", "", ""]
		for idx in range(len(filterParams)):
			fp = filterParams[idx]
			if fp in extend.keys():
				params[idx] = fp + '/' + extend[fp]
		suffix = '/'.join(params)
		url = 'https://www.baipiaoys.com:9092/show/{0}.html'.format(suffix)
		rsp = self.fetch(url)
		root = self.html(rsp.text)
		aList = root.xpath("//div[@class='stui-vodlist__box']/a")
	
		videos = []
		for a in aList:
			name = a.xpath('./@title')[0]
			pic = a.xpath('./@data-original')[0]
			mark = a.xpath("./span[@class='pic-text text-right']/text()")[0]
			sid = a.xpath("./@href")[0]
			sid = self.regStr(sid,"/detail/(\\d+).html")
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
		url = 'https://www.baipiaoys.com:9092/detail/{0}.html'.format(tid)
		rsp = self.fetch(url)
		root = self.html(rsp.text)
		node = root.xpath("//div[@class='stui-pannel-box']//div[2]")[0]
		pic = node.xpath("//div[@class='stui-content__thumb']/a/img/@data-original")[0]
		title = node.xpath("//div[@class='stui-content__thumb']/a/@title")[0]
		# detail = node.xpath("//div[@class='stui-content__detail']/text()")[0]

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

		infoArray = node.xpath("//div[@class='stui-content__detail']/p")
		for info in infoArray:
			content = info.xpath('string(.)')
			if content.startswith('类型'):
				vod['type_name'] = content.replace('类型：','')
			# if content.startswith('年份'):
			# 	vod['vod_year'] = content
			# if content.startswith('地区'):
			# 	vod['vod_area'] = content
			# if content.startswith('更新'):
			# 	vod['vod_remarks'] = content.replace('\n','').replace('\t','')
			if content.startswith('主演'):
				vod['vod_actor'] = content.replace('\n','').replace('\t','').replace('主演：','').replace('演员：','')
			if content.startswith('导演'):
				vod['vod_director'] = content.replace('\n','').replace('\t','').replace('导演：','')
			if content.startswith('简介'):
				vod['vod_content'] = content.replace('\n','').replace('\t','').replace('简介：','')

		vod_play_from = '$$$'
		playFrom = []
		vodHeader = root.xpath("//div[@class='stui-pannel-box b playlist mb']/div[@class='stui-pannel_hd']/div/h3/text()")
		for v in vodHeader:
			playFrom.append(v)
		vod_play_from = vod_play_from.join(playFrom)
		
		vod_play_url = '$$$'
		host = 'https://www.baipiaoys.com:9092'
		playList = []
		vodList = root.xpath("//ul[contains(@class,'stui-content__playlist')]")
		for vl in vodList:
			vodItems = []
			aList = vl.xpath('./li/a')
			for tA in aList:
				href = tA.xpath('./@href')[0]
				name = tA.xpath('./text()')[0]
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
		url = 'https://www.baipiaoys.com:9092/search.html?wd={0}'.format(key)
		rsp = self.fetch(url)
		root = self.html(rsp.text)
		aList = root.xpath("//ul[@class='stui-vodlist__media col-pd clearfix']/li/div[1]/a")
		videos = []
		for a in aList:
			name = a.xpath('./@title')[0]
			pic = a.xpath('./@data-original')[0]
			mark = a.xpath("./span[@class='pic-text text-right']/text()")[0]
			sid = a.xpath("./@href")[0]
			sid = self.regStr(sid,"/detail/(\\S+).html")
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
		"player": {},
			#"baipiaom3u8": {
		#		"sh": "白嫖播放器",
		#		"pu": "https://www.baipiao-ys.cc:6062/player/?url=",
		#		"sn": 1,
		#		"or": 999
		#	}
	#	},
		"filter": {"1": [{"key": "id", "name": "类型", "value": [{"n": "全部", "v": "1"}, {"n": "动作", "v": "6"}, {"n": "喜剧", "v": "7"}, {"n": "爱情", "v": "8"}, {"n": "科幻", "v": "9"}, {"n": "恐怖", "v": "10"}, {"n": "剧情", "v": "11"}, {"n": "战争", "v": "12"}, {"n": "动画", "v": "13"}, {"n": "记录", "v": "14"}]}, {"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "喜剧", "v": "喜剧"}, {"n": "爱情", "v": "爱情"}, {"n": "恐怖", "v": "恐怖"}, {"n": "动作", "v": "动作"}, {"n": "科幻", "v": "科幻"}, {"n": "剧情", "v": "剧情"}, {"n": "战争", "v": "战争"}, {"n": "警匪", "v": "警匪"}, {"n": "犯罪", "v": "犯罪"}, {"n": "动画", "v": "动画"}, {"n": "奇幻", "v": "奇幻"}, {"n": "武侠", "v": "武侠"}, {"n": "冒险", "v": "冒险"}, {"n": "枪战", "v": "枪战"}, {"n": "恐怖", "v": "恐怖"}, {"n": "悬疑", "v": "悬疑"}, {"n": "惊悚", "v": "惊悚"}, {"n": "经典", "v": "经典"}, {"n": "青春", "v": "青春"}, {"n": "文艺", "v": "文艺"}, {"n": "微电影", "v": "微电影"}, {"n": "古装", "v": "古装"}, {"n": "历史", "v": "历史"}, {"n": "运动", "v": "运动"}, {"n": "农村", "v": "农村"}, {"n": "儿童", "v": "儿童"}, {"n": "网络电影", "v": "网络电影"}]}, {"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n":"🇨🇳中国", "v": "中国大陆"}, {"n":"🇭🇰香港", "v": "中国香港"}, {"n":"🇹🇼台湾", "v": "中国台湾"}, {"n":"🇺🇸美国", "v": "美国"}, {"n":"🇯🇵日本", "v": "日本"}, {"n":"🇰🇷韩国", "v": "韩国"}, {"n": "其他", "v": "其他"}]}, {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""},{"n": "2025", "v": "2025"}, {"n": "2024", "v": "2024"},{"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, {"n": "2012", "v": "2012"}, {"n": "2011", "v": "2011"}, {"n": "2010", "v": "2010"}]}, {"key": "by", "name": "排序", "value": [{"n": "全部", "v": ""}, {"n": "时间", "v": "time"}, {"n": "人气", "v": "hits"}, {"n": "评分", "v": "score"}]}],"2": [{"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "古装", "v": "古装"}, {"n": "战争", "v": "战争"}, {"n": "青春偶像", "v": "青春偶像"}, {"n": "喜剧", "v": "喜剧"}, {"n": "家庭", "v": "家庭"}, {"n": "犯罪", "v": "犯罪"}, {"n": "动作", "v": "动作"}, {"n": "奇幻", "v": "奇幻"}, {"n": "剧情", "v": "剧情"}, {"n": "历史", "v": "历史"}, {"n": "经典", "v": "经典"}, {"n": "乡村", "v": "乡村"}, {"n": "情景", "v": "情景"}, {"n": "商战", "v": "商战"}, {"n": "网剧", "v": "网剧"}, {"n": "其他", "v": "其他"}]}, {"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n":"🇨🇳中国", "v": "中国大陆"}, {"n":"🇭🇰香港", "v": "中国香港"}, {"n":"🇹🇼台湾", "v": "中国台湾"}, {"n":"🇺🇸美国", "v": "美国"}, {"n":"🇯🇵日本", "v": "日本"}, {"n":"🇰🇷韩国", "v": "韩国"}, {"n": "其他", "v": "其他"}]}, {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2024", "v": "2024"},{"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}]}, {"key": "by", "name": "排序", "value": [{"n": "全部", "v": ""}, {"n": "时间", "v": "time"}, {"n": "人气", "v": "hits"}, {"n": "评分", "v": "score"}]}], "3": [{"key": "id", "name": "类型", "value": [{"n": "全部", "v": "3"}, {"n": "国产动漫", "v": "25"}, {"n": "日韩动漫", "v": "26"}, {"n": "欧美动漫", "v": "27"}, {"n": "其他", "v": "28"}]},{"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "情感", "v": "情感"}, {"n": "科幻", "v": "科幻"}, {"n": "热血", "v": "热血"}, {"n": "推理", "v": "推理"}, {"n": "搞笑", "v": "搞笑"}, {"n": "冒险", "v": "冒险"}, {"n": "萝莉", "v": "萝莉"}, {"n": "校园", "v": "校园"}, {"n": "动作", "v": "动作"}, {"n": "机战", "v": "机战"}, {"n": "运动", "v": "运动"}, {"n": "战争", "v": "战争"}, {"n": "少年", "v": "少年"}, {"n": "少女", "v": "少女"}, {"n": "社会", "v": "社会"}, {"n": "原创", "v": "原创"}, {"n": "亲子", "v": "亲子"}, {"n": "益智", "v": "益智"}, {"n": "励志", "v": "励志"}, {"n": "其他", "v": "其他"}]}, {"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n":"🇨🇳中国", "v": "中国大陆"}, {"n":"🇭🇰香港", "v": "中国香港"}, {"n":"🇹🇼台湾", "v": "中国台湾"}, {"n":"🇺🇸美国", "v": "美国"}, {"n":"🇯🇵日本", "v": "日本"}, {"n":"🇰🇷韩国", "v": "韩国"}, {"n": "其他", "v": "其他"}]}, {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2024", "v": "2024"},{"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}]}, {"key": "by", "name": "排序", "value": [{"n": "全部", "v": ""}, {"n": "时间", "v": "time"}, {"n": "人气", "v": "hits"}, {"n": "评分", "v": "score"}]}],"5": [{"key": "id", "name": "类型", "value": [{"n": "全部", "v": "5"}, {"n": "大陆综艺", "v": "30"}, {"n": "日韩综艺", "v": "31"}, {"n": "港台综艺", "v": "32"}, {"n": "欧美综艺", "v": "33"}]},{"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n":"🇨🇳中国", "v": "中国大陆"}, {"n":"🇭🇰香港", "v": "中国香港"}, {"n":"🇹🇼台湾", "v": "中国台湾"}, {"n":"🇺🇸美国", "v": "美国"}, {"n":"🇯🇵日本", "v": "日本"}, {"n":"🇰🇷韩国", "v": "韩国"}, {"n": "其他", "v": "其他"}]}, {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2024", "v": "2024"},{"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}]}, {"key": "by", "name": "排序", "value": [{"n": "全部", "v": ""}, {"n": "时间", "v": "time"}, {"n": "人气", "v": "hits"}, {"n": "评分", "v": "score"}]}]}
	}
	header = {
		#"Referer":"https://www.baipiaoys.com:9092/",
		"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36"
	}
	def playerContent(self,flag,id,vipFlags):
		url = 'https://www.baipiaoys.com:9092/play/{0}.html'.format(id)
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
		videoUrl = jo['url']
		parseUrl = 'https://www.baipiao-ys.cc:6062/player/analysis.php?v=' + videoUrl			
		parseRsp = self.fetch(parseUrl)
		info = re.findall(r'"url":(.*?),',parseRsp.text,re.S)[0]
		data = info.replace('"','').strip()
		decUrl = self.rc4_decrypt(data, '202205051426239465')
		realUrl = unquote(decUrl)
		result["parse"] = 0
		result["playUrl"] = ''
		result["url"] = realUrl
		result["header"] = ''		
		return result 
	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]