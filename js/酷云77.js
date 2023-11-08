// 注意事项:此源仅支持tvbox的js1以及c#版drpy的js0，暂不支持drpy官方py版的js0

// 注入全局方法,方便
globalThis.getTime = function(){
let ts= Math.round(new Date().getTime()/1000).toString();
log('获取时间戳:'+ts);
return ts
}

globalThis.getHeaders= function(input,ts){
let tkstr=input.split('?')[1].split('&').map(function(it){
    return it.split('=')[1]
}).join('');
tkstr=input.split('?')[0].replace('https://api.tyun77.cn','')+tkstr+ts+'XSpeUFjJ';
log('tk加密前:'+tkstr);
let TK=md5(tkstr);
log('tk加密后:'+TK);
let headers={
    "User-Agent":"okhttp/3.12.0",
    "TK":TK
};
return headers
}

var rule = {
    title:'酷云77',
    host:'https://api.tyun77.cn',
    hostJs:'let html=request(HOST+"/api.php/provide/getDomain");',
    homeUrl:'/api.php/provide/homeBlock?type_id=0',
    searchUrl:'/api.php/provide/searchVideo?searchName=**',
    searchable:2,
    quickSearch:0,
    filterable:1,
    multi:1,
    // 分类链接fypage参数支持1个()表达式
    // url:'/api.php/provide/searchFilter?type_id=fyclass&pagesize=24&pagenum=fypage', // 旧的写法注释掉
    url:'/api.php/provide/searchFilter?devid=453CA5D864457C7DB4D0EAA93DE96E66&package=com.sevenVideo.app.android&pagenum=fypage&pagesize=24&version=&sj=$ts&type_id=fyclass',
    // detailUrl:'/api.php/provide/videoDetail?devid=453CA5D864457C7DB4D0EAA93DE96E66&package=com.sevenVideo.app.android&version=&ids=fyid', //旧的写法注释掉
    detailUrl:'/api.php/provide/videoDetail?devid=453CA5D864457C7DB4D0EAA93DE96E66&ids=fyid&package=com.sevenVideo.app.android&version=',
    filter_url:'year={{fl.y}}&category={{fl.scat}}&area={{fl.a}}',
    filter:{0: [{'key': 'y', 'name': '年代', 'value': [{'n': '全部', 'v': ''},{'n': '2023', 'v': '2023'}, {'n': '2022', 'v': '2022'}, {'n': '2021', 'v': '2021'}, {'n': '2020', 'v': '2020'}, {'n': '2019', 'v': '2019'}, {'n': '2018', 'v': '2018'}, {'n': '2017', 'v': '2017'}, {'n': '2016', 'v': '2016'}, {'n': '2015', 'v': '2015'}, {'n': '2015之前', 'v': 'lt|2015'}]}, {'key': 'a', 'name': '地区', 'value': [{'n': '全部', 'v': ''}, {'n': '中国大陆', 'v': '中国大陆'}, {'n': '美国', 'v': '美国'}, {'n': '日本', 'v': '日本'}, {'n': '中国香港', 'v': '中国香港'}, {'n': '中国台湾', 'v': '中国台湾'}, {'n': '韩国', 'v': '韩国'}, {'n': '欧洲', 'v': '欧洲'}, {'n': '其他', 'v': '泰国'}]}, {'key': 'scat', 'name': '类型', 'value': [{'n': '全部', 'v': ''}, {'n': '剧情', 'v': '剧情'}, {'n': '动作', 'v': '动作'}, {'n': '科幻', 'v': '科幻'}, {'n': '喜剧', 'v': '喜剧'}, {'n': '战争', 'v': '战争'}, {'n': '爱情', 'v': '爱情'}, {'n': '恐怖', 'v': '恐怖'}, {'n': '伦理', 'v': '伦理'}]}], 1: [{'key': 'y', 'name': '年代', 'value': [{'n': '全部', 'v': ''},{'n': '2023', 'v': '2023'}, {'n': '2022', 'v': '2022'}, {'n': '2021', 'v': '2021'}, {'n': '2020', 'v': '2020'}, {'n': '2019', 'v': '2019'}, {'n': '2018', 'v': '2018'}, {'n': '2017', 'v': '2017'}, {'n': '2016', 'v': '2016'}, {'n': '2015', 'v': '2015'}, {'n': '2015之前', 'v': 'lt|2015'}]}, {'key': 'a', 'name': '地区', 'value': [{'n': '全部', 'v': ''}, {'n': '中国大陆', 'v': '中国大陆'}, {'n': '美国', 'v': '美国'}, {'n': '日本', 'v': '日本'}, {'n': '中国香港', 'v': '中国香港'}, {'n': '中国台湾', 'v': '中国台湾'}, {'n': '韩国', 'v': '韩国'}, {'n': '欧洲', 'v': '欧洲'}, {'n': '其他', 'v': '泰国'}]}, {'key': 'scat', 'name': '类型', 'value': [{'n': '全部', 'v': ''}, {'n': '剧情', 'v': '剧情'}, {'n': '动作', 'v': '动作'}, {'n': '科幻', 'v': '科幻'}, {'n': '喜剧', 'v': '喜剧'}, {'n': '战争', 'v': '战争'}, {'n': '爱情', 'v': '爱情'}, {'n': '恐怖', 'v': '恐怖'}, {'n': '伦理', 'v': '伦理'}]}], 2: [{'key': 'y', 'name': '年代', 'value': [{'n': '全部', 'v': ''},{'n': '2023', 'v': '2023'}, {'n': '2022', 'v': '2022'}, {'n': '2021', 'v': '2021'}, {'n': '2020', 'v': '2020'}, {'n': '2019', 'v': '2019'}, {'n': '2018', 'v': '2018'}, {'n': '2017', 'v': '2017'}, {'n': '2016', 'v': '2016'}, {'n': '2015', 'v': '2015'}, {'n': '2015之前', 'v': 'lt|2015'}]}, {'key': 'a', 'name': '地区', 'value': [{'n': '全部', 'v': ''}, {'n': '中国大陆', 'v': '中国大陆'}, {'n': '美国', 'v': '美国'}, {'n': '日本', 'v': '日本'}, {'n': '中国香港', 'v': '中国香港'}, {'n': '中国台湾', 'v': '中国台湾'}, {'n': '韩国', 'v': '韩国'}, {'n': '欧洲', 'v': '欧洲'}, {'n': '其他', 'v': '泰国'}]}, {'key': 'scat', 'name': '类型', 'value': [{'n': '全部', 'v': ''}, {'n': '剧情', 'v': '剧情'}, {'n': '动作', 'v': '动作'}, {'n': '科幻', 'v': '科幻'}, {'n': '喜剧', 'v': '喜剧'}, {'n': '战争', 'v': '战争'}, {'n': '爱情', 'v': '爱情'}, {'n': '恐怖', 'v': '恐怖'}, {'n': '伦理', 'v': '伦理'}]}], 3: [{'key': 'y', 'name': '年代', 'value': [{'n': '全部', 'v': ''},{'n': '2023', 'v': '2023'}, {'n': '2022', 'v': '2022'}, {'n': '2021', 'v': '2021'}, {'n': '2020', 'v': '2020'}, {'n': '2019', 'v': '2019'}, {'n': '2018', 'v': '2018'}, {'n': '2017', 'v': '2017'}, {'n': '2016', 'v': '2016'}, {'n': '2015', 'v': '2015'}, {'n': '2015之前', 'v': 'lt|2015'}]}, {'key': 'a', 'name': '地区', 'value': [{'n': '全部', 'v': ''}, {'n': '中国大陆', 'v': '中国大陆'}, {'n': '美国', 'v': '美国'}, {'n': '日本', 'v': '日本'}, {'n': '中国香港', 'v': '中国香港'}, {'n': '中国台湾', 'v': '中国台湾'}, {'n': '韩国', 'v': '韩国'}, {'n': '欧洲', 'v': '欧洲'}, {'n': '其他', 'v': '泰国'}]}, {'key': 'scat', 'name': '类型', 'value': [{'n': '全部', 'v': ''}, {'n': '剧情', 'v': '剧情'}, {'n': '动作', 'v': '动作'}, {'n': '科幻', 'v': '科幻'}, {'n': '喜剧', 'v': '喜剧'}, {'n': '战争', 'v': '战争'}, {'n': '爱情', 'v': '爱情'}, {'n': '恐怖', 'v': '恐怖'}, {'n': '伦理', 'v': '伦理'}]}], 4: [{'key': 'y', 'name': '年代', 'value': [{'n': '全部', 'v': ''},{'n': '2023', 'v': '2023'}, {'n': '2022', 'v': '2022'}, {'n': '2021', 'v': '2021'}, {'n': '2020', 'v': '2020'}, {'n': '2019', 'v': '2019'}, {'n': '2018', 'v': '2018'}, {'n': '2017', 'v': '2017'}, {'n': '2016', 'v': '2016'}, {'n': '2015', 'v': '2015'}, {'n': '2015之前', 'v': 'lt|2015'}]}, {'key': 'a', 'name': '地区', 'value': [{'n': '全部', 'v': ''}, {'n': '中国大陆', 'v': '中国大陆'}, {'n': '美国', 'v': '美国'}, {'n': '日本', 'v': '日本'}, {'n': '中国香港', 'v': '中国香港'}, {'n': '中国台湾', 'v': '中国台湾'}, {'n': '韩国', 'v': '韩国'}, {'n': '欧洲', 'v': '欧洲'}, {'n': '其他', 'v': '泰国'}]}, {'key': 'scat', 'name': '类型', 'value': [{'n': '全部', 'v': ''}, {'n': '剧情', 'v': '剧情'}, {'n': '动作', 'v': '动作'}, {'n': '科幻', 'v': '科幻'}, {'n': '喜剧', 'v': '喜剧'}, {'n': '战争', 'v': '战争'}, {'n': '爱情', 'v': '爱情'}, {'n': '恐怖', 'v': '恐怖'}, {'n': '伦理', 'v': '伦理'}]}]},
    headers:{
		"User-Agent":"okhttp/3.12.0"
	},
    timeout:5000,
    class_name:'全部&电影&电视剧&综艺&动漫',
    class_url:'0&1&2&3&4',
    limit:20,
    play_parse:true,
    play_json:0,
    // 手动调用解析请求json的url,此lazy不方便
    // lazy:'js:input={parse:1,url:input};',
    lazy:'',
    lazy:'js:function GetPlayUrl(playUrl){let realPlay={parse:0,url:playUrl};if(/mgtv|sohu/.test(playUrl)){realPlay.headers={"User-Agent":"Mozilla/5.0"}}else if(/bili/.test(playUrl)){realPlay.headers={"User-Agent":"Mozilla/5.0",Referer:"https://www.bilibili.com"}}else if(/ixigua/.test(playUrl)){realPlay.headers={"User-Agent":"Mozilla/5.0",Referer:"https://www.ixigua.com"}}return realPlay}if(/\\.m3u8|\\.mp4/.test(input)){input={parse:0,url:input}}else{try{let jxUrl="http://api.tyun77.cn/api.php/provide/parserUrl?url=";var t=Math.floor((new Date).getTime()/1e3).toString();let jxExt="&retryNum=0&pcode=010110002&version=2.1&devid=f9c9ce5bb5827a266829383718e6131a&package=com.sevenVideo.app.android&sys=android&sysver=12&brand=Xiaomi&model=Mi_10_Pro&sj="+t;let url=jxUrl+input+jxExt;let TK="/api.php/provide/parserUrl"+"Xiaomif9c9ce5bb5827a266829383718e6131aMi_10_Procom.sevenVideo.app.android010110002"+0+t+"android12"+encodeURIComponent(vipUrl)+"2.1"+t+"XSpeUFjJ";let html=request(url,{headers:{Referer:jxUrl,"User-Agent":"okhttp/3.12.0",TK:md5(TK)}});let urll=JSON.parse(html).data.url;let playhtml=request(urll);let playurl=JSON.parse(playhtml).url;input=GetPlayUrl(playurl)}catch(e){input={parse:1,jx:1,url:input}}}',
    推荐:'json:data.blocks;contents;title;videoCover;msg;id',
    double:true,
    // 一级:'json:data.result;title;videoCover;msg;id', 旧的写法注释掉
    一级:`js:
    var d=[];
    let ts= getTime();
    input=input.replace('$ts',ts);
	let html = request(input,{
	headers:getHeaders(input,ts)
	});
	//print(html);
	html = JSON.parse(html);
    html.data.result.forEach(function(it){
    d.push({
    title:it.title,
    img:it.videoCover,
    desc:it.msg,
    url:it.id
    })
    });
    setResult(d);
    `,
    二级:`js: var d = [];
    VOD = {
        vod_id: input
    };
    let ts= getTime();
try {
    input=input+'&sj='+ts;
	let html = request(input,{
	headers:getHeaders(input,ts)
	});
	//print(html);
	html = JSON.parse(html);
	let node = html.data;
	VOD = {
		vod_id: node["id"],
		vod_name: node["videoName"],
		vod_pic: node["videoCover"],
		type_name: node["subCategory"],
		vod_year: node["year"],
		vod_area: node["area"],
		vod_remarks: node["msg"],
		vod_actor: node["actor"],
		vod_director: node["director"],
		vod_content: node["brief"].strip()
	};
	let tid = input.split("ids=")[1].split('&')[0];
	let listUrl='https://api.tyun77.cn/api.php/provide/videoPlaylist?devid=453CA5D864457C7DB4D0EAA93DE96E66&ids='+tid+'&package=com.sevenVideo.app.android&version=&sj='+ts;
	html = request(listUrl,{
	headers:getHeaders(listUrl,ts)
	});
	html = JSON.parse(html);
	let episodes = html.data.episodes;
	let playMap = {};
	if (typeof play_url === "undefined") {
		var play_url = ""
	}
	play_url = play_url.replace("&play_url=", "&type=json&play_url=");
	episodes.forEach(function(ep) {
		let playurls = ep["playurls"];
		playurls.forEach(function(playurl) {
			let source = playurl["playfrom"];
			if (!playMap.hasOwnProperty(source)) {
				playMap[source] = []
			}
			playMap[source].append(playurl["title"].strip() + "$" + play_url + urlencode(playurl["playurl"]))
		})
	});
	let playFrom = [];
	let playList = [];
	Object.keys(playMap)
		.forEach(function(key) {
			playFrom.append(key);
			playList.append(playMap[key].join("#"))
		});
	let vod_play_from = playFrom.join("$$$");
	let vod_play_url = playList.join("$$$");
	VOD["vod_play_from"] = vod_play_from;
	VOD["vod_play_url"] = vod_play_url
} catch (e) {
	log("获取二级详情页发生错误:" + e.message)
}`,
    搜索:'',
    搜索:'json:data;videoName;videoCover;msg;id',
}