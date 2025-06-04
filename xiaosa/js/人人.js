var rule = {
	title:'人人影视[搜]',
	host:'https://yyets.click',
	homeUrl:'/',
	url:'*',
	filter_url:'{{fl.class}}',
	filter:{
	},
	searchUrl: '*',
	searchable:2,
	quickSearch:0,
	filterable:0,
	headers:{
		'User-Agent': PC_UA,
		'Accept': '*/*',
		'Referer': 'https://yyets.click/',
         	'Cookie':'http://127.0.0.1:9978/file:///tvbox/JS/lib/yyets.txt',
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
VOD.vod_play_from = "人人分享站";
VOD.vod_remarks = detailUrl;
VOD.vod_actor = "沒有二级，只有一级链接直接推送播放";
VOD.vod_content = MY_URL;
VOD.vod_play_url = "人人分享站$" + detailUrl;
`,
	搜索:`js:
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
if (rule_fetch_params.headers.Cookie.startsWith("http")){
	rule_fetch_params.headers.Cookie=fetch(rule_fetch_params.headers.Cookie);
	let cookie = rule_fetch_params.headers.Cookie;
	setItem(RULE_CK, cookie);
};
log('yyets search cookie>>>>>>>>>>>>>>>' + rule_fetch_params.headers.Cookie);
let _fetch_params = JSON.parse(JSON.stringify(rule_fetch_params));
_fetch_params.headers.Referer = 'http://yyets.click/search?keyword=' + encodeURIComponent(KEY) + '&type=default';
log('yyets search params>>>>>>>>>>>>>>>' + JSON.stringify(_fetch_params));
let new_html=request(rule.homeUrl + 'api/resource?keyword=' + encodeURIComponent(KEY) + '&type=default', _fetch_params);
//log("yyets search result>>>>>>>>>>>>>>>" + new_html);
let json=JSON.parse(new_html);
let d=[];
for(const it in json.comment){
	if (json.comment.hasOwnProperty(it)){
		log("yyets search it>>>>>>>>>>>>>>>" + JSON.stringify(json.comment[it]));
		if (/(www.aliyundrive.com|pan.quark.cn|www.alipan.com)/.test(json.comment[it].comment)){
			let its = json.comment[it].comment.split("\\n");
			let i=0;
			while(i<its.length){
				let title=its[i].trim().replaceAll(/\\s+/g," ");
				if (title.length==0){
					i++;
					continue;
				}
				let urls=[];
				log("yyets search title>>>>>>>>>>>>>>>" + title);
				while(++i<its.length){
					log("yyets search url>>>>>>>>>>>>>>>" + its[i]);
					let burl = its[i].trim().split(" ")[0];
					if (burl.length==0){
						continue;
					}
					if (burl.includes("https://")){
						urls.push("https:"+burl.split("https:")[1]);
					}else{
						break;
					}
				}
				if (urls.length>0){
					log("yyets search title,urls>>>>>>>>>>>>>>>" + title + ",[" + JSON.stringify(urls) + "]");
					if (title.includes(KEY)){
						urls.forEach(function (url) {
							d.push({
								title:title,
								img:'',
								content:json.comment[it].comment,
								desc:json.comment[it].date,
								url:'push://'+url
								});
						});
					}
				}
			}
		}
	}
}
setResult(d);
`,
}
