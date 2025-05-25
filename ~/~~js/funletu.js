var rule = {
	title:'趣盘搜[夸]',
	host:'https://v.funletu.com',
	homeUrl:'/',
	url: '/forum-fyclass-fypage.html?',
	filter_url:'{{fl.class}}',
	filter:{
	},
	searchUrl: 'json:/search#{"style":"get","datasrc":"search","query":{"id":"","datetime":"","commonid":1,"parmid":"","fileid":"","reportid":"","validid":"","searchtext":"**"},"page":{"pageSize":10,"pageIndex":1},"order":{"prop":"id","order":"desc"},"message":"请求资源列表数据"};postjson',
	searchable:2,
	quickSearch:0,
	filterable:0,
	headers:{
		'User-Agent': PC_UA,
		'Accept': '*/*',
		'Referer': 'https://pan.funletu.com/'
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
VOD.vod_play_from = "夸克網盤";
VOD.vod_remarks = detailUrl;
VOD.vod_actor = "沒有二級，只有一級鏈接直接推送播放";
VOD.vod_content = MY_URL;
VOD.vod_play_url = "夸克網盤$" + detailUrl;
`,
	搜索:`js:
let postJson = {
	style:"get",
	datasrc:"search",
	query:{
		id:"",
		datetime:"",
		commonid:1,
		parmid:"",
		fileid:"",
		reportid:"",
		validid:"",
		searchtext: KEY
	},
	page:{ pageSize:20, pageIndex: MY_PAGE },
	order:{prop:"id",order:"desc"},
	message:"请求资源列表数据"
};
let postData = {
    method: "POST",
    body: postJson
};
log("funletu search postData1>>>>>>>>>>>>>>>" + JSON.stringify(postData));
let _fetch_params = JSON.parse(JSON.stringify(rule_fetch_params));
Object.assign(_fetch_params, postData);
log("funletu search postData>>>>>>>>>>>>>>>" + JSON.stringify(_fetch_params));
let new_html=post(rule.homeUrl + 'search', _fetch_params);
//log("funletu search result>>>>>>>>>>>>>>>" + new_html);
let json=JSON.parse(new_html);
let d=[]
for(const it in json["data"]){
	if (json.data.hasOwnProperty(it)){
		log("funletu search it>>>>>>>>>>>>>>>" + JSON.stringify(json.data[it]));
		if (json.data[it].valid === 0){		
			d.push({
				title:json.data[it].title,
				img:'',
				content:json.data[it].updatetime,
				desc:json.data[it].updatetime,
				url:'push://'+json.data[it].url.split("?")[0]
				});
		}
	}
}
setResult(d);
`,
}
