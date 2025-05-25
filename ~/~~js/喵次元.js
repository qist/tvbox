globalThis.getTime = function(){
let ts= Math.round(new Date().getTime()/1000).toString();
log('获取时间戳:'+ts);
return ts
}

globalThis.signUrl=function(json){
// 获取所有节点的名称并按字母顺序排序
let json1=JSON.parse(json);
var sortedKeys = Object.keys(json1).sort();
// 遍历排好序的节点名称列表，并打印相应的值
let s='';
for (let key in sortedKeys){
	let value=json1[sortedKeys[key]];
	if(value!=undefined){
	s=s+value;
	}
}
//log(s);
//log(md5(s+"alskeuscli"));
s=json.slice(0,-1)+",\"sign\":\""+md5(s+"alskeuscli")+"\"\}";
log(s);
return s;
}

globalThis.posturl=function(url,json){
	let html= fetch(url, {
		body: JSON.parse(signUrl(json)),
		headers: {"User-Agent": "okhttp/3.12.3"},
		method: "POST"
	}, true);
	return JSON.parse(html);
}
var rule = {
	title: '喵次元[APP]',
	host: 'https://cym.fengche.tv/api.php/',
	hostJs:`
	var json2 = '{"versionName":"5.6.9","uuid":"9cc01079c64e2495","version":"4835d0a2","versionCode":"35","ctime":"'+getTime()+'"}';
	let url="https://cym.fengche.tv/api.php/type/get_list";
	let jo=posturl(url,json2).data.list;
	let filters = {};
       let cb={"class":"类型","area":"地区","lang":"语言","year":"年份","star":"演员","director":"导演","state":"状态","version":"版本"};
       let class1=[];
       jo.forEach(function(tp) {
       	rule.class_name=rule.class_name +"&"+tp['type_name'];
       	rule.class_url=rule.class_url +"&"+tp['type_id'];
       	let ep=tp['type_extend'];
       	let classes = [];
       	for (let key in ep){
       		let value=ep[key];
       		
       		if (value.length>1){
       			class1.append(key);
       			//写成{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"🇨🇳中国","v":"大陆"}]}这种格式
       			let dd=value.toString().split(',');
       			var s=[];
       			dd.forEach(function(i){
       				s.append({'n':i,'v':i});
       				})
       			let ss={"key":key,"name":cb[key],"value":s};
       			classes.append(ss);
       			}
       		}
       	filters[tp['type_id']]=classes;
	});
	class1=Array.from(new Set(class1)).sort();
	let s=""
	class1.forEach(function(tp) {
	 	s=s+"&" + tp +"={{fl."+tp+"}}";
	 })
	log(s);
	rule.filter_url=s;
	rule.filter=filters;
	log(rule.filter);
	log(rule.class_name);
	log(rule.class_url);
`,

	homeUrl:'?hpindigo=**&page=fypage',
	url:'?t=fyclass&page=fypage',
	filter_url:'',
	filter: {},
	detailUrl:'?ids=',
	searchUrl: '?hpindigo=**&page=fypage',
	searchable: 2,
	quickSearch: 0,
	filterable:1,//是否启用分类筛选,
	headers:{'User-Agent':'MOBILE_UA'},
	timeout:10000,
	class_name:'全部', // 分类筛选 /api.php/app/nav
	class_url:'0',
	play_parse:true,
    lazy:`js:
	log("*************测试*************");
	let dd=input.split("&");
	let ju_id=dd[0];
	let plyer=dd[1];
	let video_id=dd[2];
	var json2 = '{"player_id":"'+plyer+'","ju_id":"'+ju_id+'","vod_id":"'+video_id+'","versionName":"5.6.9","uuid":"3899af59c0b12b98","version":"4835d0a2","versionCode":"35","ctime":"'+getTime()+'"}';
	let url="https://cym.fengche.tv/api.php/video/get_definition";
	let html = posturl(url,json2).data[0].url.trim();
	log(html);
	//input=aesX("AES/CBC/PKCS7",false,html,true,"sLunqcoH85Nm/jDmFKns7A==","fedcba9876543210",false);
	//log(input);
	eval(getCryptoJS);
	var key = CryptoJS.enc.Hex.parse("734C756E71636F4838354E6D2F6A446D464B6E7337413D3D0000000000000000");
	var iv = CryptoJS.enc.Utf8.parse("fedcba9876543210");
	input=(CryptoJS.AES.decrypt(html, key, {
		iv: iv,
		mode: CryptoJS.mode.CBC,
		padding: CryptoJS.pad.Pkcs7
	})).toString(CryptoJS.enc.Utf8)
	log(input)
	`,
    //lazy:'js:input=/m3u8|mp4|flv/.test(input)?{jx:0,url:input,parse:0}:{jx:1,url:input,parse:1}',
	limit:6,
	// 推荐:'json:items;*;*;*;*',
	推荐:'json:data.sections[0].items;*;*;*;*',
	推荐:`js:
	log(input);
	let page=input.split("&")[1].split("=")[1];
	log(page);
	var json2 = '{"page":"'+page+'","versionName":"5.6.9","uuid":"9cc01079c64e2495","version":"4835d0a2","versionCode":"35","ctime":"'+getTime()+'"}';
	let url="https://cym.fengche.tv/api.php/video/index";
	let jo = posturl(url,json2);
	let vodList = jo.data;
	log(vodList);
	let videos=[];
	vodList.forEach(function(vod) {
		vod.video.forEach(function(vod1) {
		let aid = (vod1["vod_id"]);
		let title = vod1["vod_name"];
		let img = vod1["vod_pic"];
		let remark = vod1["vod_remarks"];
		videos.push({
			vod_id: aid,
			vod_name: title,
			vod_pic: img,
			vod_remarks: remark
			})
		})
	})
	
	VODS=videos;
	`,
	一级:`js:
	log(input);
	let canshu=input.split("?")[1].split("&");
	let dd={};
	canshu.forEach(function(key){
		log(key);
		let k=key.split("=");
		dd[k[0]]=k[1];
	})
	var json2 = '{"type_id":"'+dd["t"]+'","vod_year":"'+dd["year"]+'","limit":"20","orderby":"","vod_area":"'+dd["area"]+'","vod_class":"'+dd["class"]+'","page":"'+dd["page"]+'","versionName":"5.6.9","uuid":"9cc01079c64e2495","version":"4835d0a2","vod_name":"","versionCode":"35","ctime":"'+getTime()+'"}';
	log(json2);
	let url="https://cym.fengche.tv/api.php/video/get_list";
	let jo = posturl(url,json2);
	var d=[];
	jo.data.list.forEach(function(it){
	d.push({
	title:it.vod_name,
	img:it.vod_pic,
	desc:it.vod_remarks,
	url:it.vod_id,
	content:it.vod_blurb})
	});
	setResult(d);
    `,
	二级:`js: 
	log(orId);
	var json2 = '{"vod_id":"'+orId+'","versionName":"5.6.9","uuid":"3899af59c0b12b98","version":"4835d0a2","versionCode":"35","ctime":"'+getTime()+'"}';
	log(json2);
	let url="https://cym.fengche.tv/api.php/video/get_detail";
	let jo = posturl(url,json2);
	let node = jo.data;
	VOD = {
		vod_id: node["vod_id"],
		vod_name: node["vod_name"],
		vod_pic: node["vod_pic"],
		type_name: node["vod_class"],
		vod_year: node["vod_year"],
		vod_area: node["vod_area"],
		vod_remarks: node["vod_remarks"],
		vod_actor: node["vod_actor"],
		vod_director: node["vod_director"],
		vod_content: node["vod_content"]
	};
	let episodes = node.player;
	let playMap = {};
	episodes.forEach(function(ep) {
		let playurls = ep["code"];
		let source = ep["name"];
		log (playurls);
		log (source);
		//这里分别获取线路
		var json2 = '{"limit":"5000","vod_id":"'+orId+'","page":"1","versionName":"5.6.9","uuid":"9cc01079c64e2495","version":"4835d0a2","versionCode":"35","player":"'+playurls+'","ctime":"'+getTime()+'"}';
		log(json2);
		let url="https://cym.fengche.tv/api.php/video/get_player";
		let jo1 = posturl(url,json2);
		jo1.data.list.forEach(function(playurl) {
			if (!playMap.hasOwnProperty(source)) {
				playMap[source] = []
			}
			playMap[source].append(playurl["drama"]+"$"+playurl["ju_id"]+"&"+playurl["plyer"]+"&"+playurl["video_id"])
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
	`,
	搜索:`js:
	let page=input.split("&")[1].split("=")[1];
	log(page);
	var json2 = '{"vod_year":"","limit":"20","orderby":"up","vod_area":"","vod_class":"","page":"'+page+'","versionName":"5.6.9","uuid":"9cc01079c64e2495","version":"4835d0a2","vod_name":"'+KEY+'","versionCode":"35","ctime":"'+getTime()+'"}';
	let url="https://cym.fengche.tv/api.php/video/get_list";
	let jo = posturl(url,json2);
    var d=[];
    jo.data.list.forEach(function(it){
    d.push({
    title:it.vod_name,
    img:it.vod_pic,
    desc:it.vod_remarks,
    url:it.vod_id})
    });
    setResult(d);`,
}