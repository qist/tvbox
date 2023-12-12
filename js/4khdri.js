var rule = {
	title:'4KHDR[磁]',
	host:'https://www.4khdr.cn',
        homeUrl: "/forum.php?mod=forumdisplay&fid=2&page=1",
	url: '/forum.php?mod=forumdisplay&fid=2&filter=typeid&typeid=fyclass&page=fypage',
	filter_url:'{{fl.class}}',
	filter:{
	},
	searchUrl: '/search.php#searchsubmit=yes&srchtxt=**;post',
	searchable:2,
	quickSearch:1,
	filterable:0,
	headers:{
		'User-Agent': 'PC_UA',
         	'Cookie':'hvLw_2132_saltkey=TIHLl6lF; hvLw_2132_lastvisit=1692640733; hvLw_2132_visitedfid=2; hvLw_2132_sendmail=1; _clck=bmvlfv|2|fec|0|1328; hvLw_2132_seccodecSAH73=7547.d0a543395de43bfa49; hvLw_2132_ulastactivity=1692644363%7C0; hvLw_2132_auth=8608dKQC6bKMZh5FKg09ZhhWjbrygDZw3i%2FXQTK6RYYYKIhxi%2FVywBubisxssBZlQ%2BNfz9nK3ZiCNnUvF9HlL%2Fehrg; hvLw_2132_lastcheckfeed=99213%7C1692644363; hvLw_2132_checkfollow=1; hvLw_2132_lip=163.204.43.186%2C1692644363; hvLw_2132_sid=0; hvLw_2132_checkpm=1; hvLw_2132_noticeTitle=1; _clsk=x9bivq|1692644368391|2|1|x.clarity.ms/collect; hvLw_2132_lastact=1692644370%09index.php%09forumdisplay; hvLw_2132_st_t=99213%7C1692644370%7Ceeabd9f3f324a9138f1be3cc46fdcd01; hvLw_2132_forum_lastvisit=D_2_1692644370',
	},
	timeout:5000,
	class_name: "4K电影&4K美剧&4K华语&4K动画&4K纪录片&4K日韩印&蓝光电影&蓝光美剧&蓝光华语&蓝光动画&蓝光日韩印",
	class_url:"3&8&15&6&11&4&29&31&33&32&34",
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
	推荐:'ul#waterfall li;a&&title;img&&src;div.auth.cl&&Text;a&&href',
	一级:'ul#waterfall li;a&&title;img&&src;div.auth.cl&&Text;a&&href',
	二级:{
		title:"#thead_subject&&Text",
		img:"img.zoom&&src",
		desc:'td[id^="postmessage_"] font&&Text',
		content:'td[id^="postmessage_"] font&&Text',
		tabs:`js:
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
TABS=[]
let d = pdfa(html, 'table.t_table');
let aliIndex=1;
d.forEach(function(it) {
	let burl = pdfh(it, 'a&&href');
	log("burl >>>>>>" + burl);
	if (burl.startsWith("https://www.aliyundrive.com/s/")){
		TABS.push("aliyun"+aliIndex);
		aliIndex = aliIndex + 1;
	}
});
d = pdfa(html, 'table.t_table a[href^="magnet"]');
if (d.length>0){
	TABS.push("磁力");
}
log('4khdr TABS >>>>>>>>>>>>>>>>>>' + TABS);
`,
		lists:`js:
log(TABS);
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
LISTS = [];
let d = pdfa(html, 'table.t_table');
d.forEach(function(it){
	let burl = pdfh(it, 'a&&href');
	if (burl.startsWith("https://www.aliyundrive.com/s/")){
		let title = pdfh(it, 'a&&Text');
		log('title >>>>>>>>>>>>>>>>>>>>>>>>>>' + title);
		burl = "http://127.0.0.1:9978/proxy?do=ali&type=push&url=" + encodeURIComponent(burl);
		log('burl >>>>>>>>>>>>>>>>>>>>>>>>>>' + burl);
		let loopresult = title + '$' + burl;
		LISTS.push([loopresult]);
	}
});
let listm = [];
d.forEach(function(it){
	let burl = pdfh(it, 'a&&href');
	if (burl.startsWith("magnet")){
		let title = pdfh(it, 'a&&Text');
		log('title >>>>>>>>>>>>>>>>>>>>>>>>>>' + title);
		log('burl >>>>>>>>>>>>>>>>>>>>>>>>>>' + burl);
		let loopresult = title + '$' + burl;
		listm.push(loopresult);
	}
});
if (listm.length>0){
	LISTS.push(listm);
}
`,

	},
	一级:'ul#waterfall li;a&&title;img&&src;div.auth.cl&&Text;a&&href',
	搜索:`js:
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
if (rule_fetch_params.headers.Cookie.startsWith("http")){
	rule_fetch_params.headers.Cookie=fetch(rule_fetch_params.headers.Cookie);
	let cookie = rule_fetch_params.headers.Cookie;
	setItem(RULE_CK, cookie);
};
log('4khdr search cookie>>>>>>>>>>>>>>>' + rule_fetch_params.headers.Cookie);
let new_host= HOST + '/search.php';
let new_html=request(new_host);
let formhash = pdfh(new_html, 'input[name="formhash"]&&value');
log("4khdr formhash>>>>>>>>>>>>>>>" + formhash);
let params = 'formhash=' + formhash + '&searchsubmit=yes&srchtxt=' + KEY;
let _fetch_params = JSON.parse(JSON.stringify(rule_fetch_params));
let postData = {
    body: params
};
Object.assign(_fetch_params, postData);
log("4khdr search postData>>>>>>>>>>>>>>>" + JSON.stringify(_fetch_params));
let search_html = post( HOST + '/search.php', _fetch_params)
//log("4khdr search result>>>>>>>>>>>>>>>" + search_html);
let d=[];
let dlist = pdfa(search_html, 'div#threadlist ul li');
dlist.forEach(function(it){
	let title = pdfh(it, 'h3&&Text');
	if (searchObj.quick === true){
		if (title.includes(KEY)){
			title = KEY;
		}
	}
	let img = "";
	let content = pdfh(it, 'p:eq(3)&&Text');
	let desc = pdfh(it, 'p:eq(2)&&Text');
	let url = pd(it, 'a&&href', HOST);
	d.push({
		title:title,
		img:img,
		content:content,
		desc:desc,
		url:url
		})
});
setResult(d);
	`,
}