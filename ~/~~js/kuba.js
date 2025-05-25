var rule = {
	title:'酷吧[磁]',
	host:'https://www.kuba222.com',
        homeUrl: '/',
	url: '/vodtypehtml/fyclass.html?',
	filter_url:'{{fl.class}}',
	filter:{
	},
	searchUrl: '/search/**-1.html',
	searchable:2,
	quickSearch:0,
	filterable:0,
	headers:{
		'User-Agent': 'PC_UA',
		'Referer': 'https://www.kuba222.com/'
	},
	timeout:5000,
	class_name: '最新&4K&电影&动作片&喜剧片&爱情片&科幻片&恐怖片&剧情片&战争片&微电影&电视剧&动漫&纪录片',
	class_url: 'new&4K&1&5&6&7&8&9&10&11&21&31&4&16',
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
	推荐:`js:
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
let d = [];
let html = request(input);
let list = pdfa(html, 'ul.stui-vodlist li');
list.forEach(function (it){
	d.push({
		title: pdfh(it, 'a&&title'),
		desc: pdfh(it, 'li&&div&&a&&span&&Text'),
		pic_url: pd(it, 'a&&data-original', HOST),
		url: pdfh(it, 'a&&href')
	});
});
setResult(d);
`,
	一级:`js:
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
let d = [];
if (MY_CATE === '4K'){
	let turl = (MY_PAGE === 1)? '' : '-' + MY_PAGE;
	input = rule.homeUrl + 'vodtopichtml/' + '11' + turl + '.html';
}else if (MY_CATE === 'new'){
	input = rule.homeUrl + MY_CATE  + '.html';
}else{
	let turl = (MY_PAGE === 1)? '' : '-' + MY_PAGE;
	input = rule.homeUrl + 'vodtypehtml/' + MY_CATE + turl + '.html';
}
let html = request(input);
let list = pdfa(html, 'ul.stui-vodlist li');
list.forEach(function (it){
	d.push({
		title: pdfh(it, 'a&&title'),
		desc: pdfh(it, 'li&&div&&a&&span&&Text'),
		pic_url: pd(it, 'a&&data-original', HOST),
		url: pdfh(it, 'a&&href')
	});
});
setResult(d);
`,
	二级:{
		title:"div.stui-content h3&&Text",
		img:"div.stui-content a.lazyload img&&src",
		desc:'div.stui-content a span&&Text',
		content:'div.stui-content p.data&&Text',
		tabs:`js:
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
TABS=[]
let vodUrls=[];
try{
	vodUrls.push(html.match(/var GvodUrls1 *= *"([^"]*)"/)[1]);
	vodUrls.push(html.match(/var GvodUrls2 *= *"([^"]*)"/)[1]);
	vodUrls.push(html.match(/var GvodUrls3 *= *"([^"]*)"/)[1]);
	vodUrls.push(html.match(/var GvodUrls4 *= *"([^"]*)"/)[1]);
	vodUrls.push(html.match(/var GvodUrls5 *= *"([^"]*)"/)[1]);
}catch(e){
}
let index=1;
vodUrls.forEach(function (it) {
	TABS.push("磁力"+index);
	index = index + 1;
});
log('kuba TABS >>>>>>>>>>>>>>>>>>' + TABS);
`,
		lists:`js:
log(TABS);
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
LISTS = [];
let vodUrls=[];
//log("kuba html>>>>>>>>>>>>>>>>>>>>>>" + html);
try{
	vodUrls.push(html.match(/var GvodUrls1 *= *"([^"]*)"/)[1]);
	vodUrls.push(html.match(/var GvodUrls2 *= *"([^"]*)"/)[1]);
	vodUrls.push(html.match(/var GvodUrls3 *= *"([^"]*)"/)[1]);
	vodUrls.push(html.match(/var GvodUrls4 *= *"([^"]*)"/)[1]);
	vodUrls.push(html.match(/var GvodUrls5 *= *"([^"]*)"/)[1]);
}catch(e){
	log('kuba tabs e>>>>>>>>>>>>>>>>>>..' + e);
}
vodUrls.forEach(function (it) {
	let epos = it.split("###");
	let d=[];
	epos.forEach(function (it1){
		if (it1.length>0){
			d.push(it1);
		}
	});
	LISTS.push(d.reverse());
});
`,

	},
	搜索:`js:
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
let cookie="";
if (false){
let new_html=request(HOST, {withHeaders:true});
let json=JSON.parse(new_html);
let setCk=Object.keys(json).find(it=>it.toLowerCase()==="set-cookie");
if (typeof setCk !== "undefined"){
	let d=[];
	for(const key in json[setCk]){
		if (typeof json[setCk][key] === "string"){
			log("kuba header setCk key>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" + json[setCk][key] + " " + (typeof json[setCk][key]));
			d.push(json[setCk][key].split(";")[0]);
		}
	}
	cookie=d.join(";");
}
fetch_params.headers.Cookie=cookie;
rule_fetch_params.headers.Cookie=cookie;
}
log('kuba search cookie >>>>>>>>>>>>>>>>>>>>>' + cookie);

let params = 'wd='+ encodeURIComponent(KEY) + '&submit=';
let _fetch_params = JSON.parse(JSON.stringify(rule_fetch_params));
let postData = {
    body: params
};
Object.assign(_fetch_params, postData);
log("kuba search postData>>>>>>>>>>>>>>>" + JSON.stringify(_fetch_params));
let search_html = post( HOST + '/index.php?m=vod-search', _fetch_params)
search_html = search_html.replace(/<script>.*?<\\/script>/g,"");
//log("kuba search result>>>>>>>>>>>>>>>" + search_html.substring(4096));
let d=[];
let dlist = pdfa(search_html, 'li.activeclearfix');
log("kuba search dlist.length>>>>>>>>>>>>>" + dlist.length);
dlist.forEach(function(it){
	let title = pdfh(it, 'a&&title');
	let img = pd(it, 'a&&data-original', HOST);
	let content = pdfh(it, 'a&&Text');
	let desc = pdfh(it, 'div.detail&&Text');
	let url = pd(it, 'a&&href', HOST);
	d.push({
		title:title,
		img:img,
		content:content,
		desc:desc,
		url:url
		});
});
dlist = pdfa(search_html, 'li.active.clearfix');
log("kuba search dlist.length>>>>>>>>>>>>>" + dlist.length);
dlist.forEach(function(it){
	let title = pdfh(it, 'a&&title');
	let img = pd(it, 'a&&data-original', HOST);
	let content = pdfh(it, 'a&&Text');
	let desc = pdfh(it, 'div.detail&&Text');
	let url = pd(it, 'a&&href', HOST);
	d.push({
		title:title,
		img:img,
		content:content,
		desc:desc,
		url:url
		});
});
setResult(d);
`,
}
