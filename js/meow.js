var rule = {
	title:'meow.tg[搜]',
	host:'https://meow.tg',
	homeUrl:'/',
	url:'*',
	filter_url:'{{fl.class}}',
	filter:{
	},
	searchUrl: '/api/results/query?page=fypage&perPage=20&keyword=**',
	searchable:2,
	quickSearch:0,
	filterable:0,
	headers:{
		'User-Agent': PC_UA,
		'Accept': '*/*',
		'Referer': 'https://meow.tg/',
	},
	timeout:5000,
	class_name:'',
	class_url:'',
	play_parse:true,
	play_json:[{
		re:'*',
		json:{
			parse:0,
			jx:0
		}
	}],
	lazy:'',
	limit:6,
	推荐:'',
	一级:'',
	二级:`js:
VOD.vod_play_from = "雲盤";
VOD.vod_remarks = detailUrl;
VOD.vod_actor = "沒有二級，只有一級鏈接直接推送播放";
VOD.vod_content = MY_URL;
VOD.vod_play_url = "雲盤$" + detailUrl;
`,
	搜索:`js:
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
let newurl = rule.homeUrl + 'api/results/query?page=' + MY_PAGE+ '&perPage=20&keyword=' + encodeURIComponent(KEY);
let _fetch_params = JSON.parse(JSON.stringify(rule_fetch_params));
log("meow search param>>>>>>>>>>>>>>>" + JSON.stringify(_fetch_params));
let new_html=request(newurl, _fetch_params);
let json=JSON.parse(new_html);
let d=[];
for(const it in json.finalList){
	if (json.finalList.hasOwnProperty(it)){
		//log("meow search it>>>>>>>>>>>>>>>" + JSON.stringify(json.finalList[it]));
		let text = json.finalList[it]["results"]["text"];
		let high = json.finalList[it]["results"]["highLight"];
		if (/(www.aliyundrive.com|pan.quark.cn|www.alipan.com)/.test(text)){
			text = text;
		}else if (/(www.aliyundrive.com|pan.quark.cn|www.alipan.com)/.test(high)){
			text = high;
		}else{
			text = "";
		}
		if (text.length>0){
			let title = "";
			if (/.*名称(:|：)([^\\n]*)/.test(text)){
				title = text.match(/.*名称(:|：)([^\\n]*)/)[2].trim();
			}
			let content = "";
			if (/.*描述(:|：)([^\\n]*)/.test(text)){
				content = text.match(/.*描述(:|：)([^\\n]*)/)[2].trim();
			}
			let desc = json.finalList[it]["source"]["name_zh"];
			let img = json.finalList[it]["source"]["avatar"];
			let matches = text.match(/(www.aliyundrive.com|pan.quark.cn|www.alipan.com)([\\/0-9a-zA-Z\\+\\-_]*)/);
			let burl = "https://" + matches[1] + matches[2];
			if (title.includes(KEY)){
				log("meow search title,url,img>>>>>>>>>>>>>>>" + title + ",[" + burl + "], " + img);
				if (searchObj.quick === true){
					title = KEY;
				}
				d.push({
					title:title,
					img:img,
					content:content,
					desc:desc,
					url:'push://'+burl
				});
			}
		}
	}
}
setResult(d);
`,
}
