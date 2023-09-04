var rule = {
	title:'团长资源',
	host:'https://t-rex.tzfile.com',
	homeUrl:'/',
	url: '/fyclass/page/fypage?',
	filter_url:'{{fl.class}}',
	filter:{
	},
	searchUrl: '/?s=**',
	searchable:2,
	quickSearch:0,
	filterable:0,
	headers:{
		'User-Agent': 'PC_UA',
		'Accept': '*/*',
		'Referer': 'https://t-rex.tzfile.com/'
	},
	图片来源:'@Headers={"Accept":"*/*","Referer":"https://t-rex.tzfile.com/","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"}',
	timeout:5000,
	class_name:'电影&电视剧&动画&纪录片演唱会&真人秀综艺',
	class_url:'movies&tvshow&animation&faction&show',
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
//	推荐:'main#main article:has(img);a&&title;img&&data-src;div.entry-wrapper a&&Text;a&&href',
	推荐:'*',
	一级:`js:
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
let d = [];
log("tzfiles input>>>>>>>>>>>>>>"+input);
let html = request(input);
//log("tzfiles 1level html>>>>>>>>>>>>>>"+html);
let list = pdfa(html, 'main#main article:has(img)');
list.forEach(function(it) {
	d.push({
		title: pdfh(it, 'a&&title'),
		desc: pdfh(it, 'div.entry-wrapper a&&Text'),
		pic_url: 'http://127.0.0.1:10079/i/0/s/'+pd(it, 'img&&data-src', HOST),
		url: pd(it, 'a&&href', HOST)
	});
})
setResult(d);
`,
	//一级:`js:
	//let html=request(input);
	//log("html>>>>>>>>>>>>>>>>"+html);
	//`,
	二级:{
		title:"#app .container header h1&&Text",
		img:"#main article div.entry-content img&&src",
		desc:"#app .container header .meta-date time&&datetime",
		content:"#main article .entry-content&&Text",
		tabs:`js:
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
TABS=[];
let d = pdfa(html, '#main article div.entry-content p');
let tabsq=[];
d.forEach(function(it) {
	let purl = pd(it, 'a&&href', HOST);
	if (purl.includes("pan.quark.cn")){
		tabsq.push("夸克雲盤");
	} else if (purl.includes("www.aliyundrive.com")){
		tabsq.push("阿里雲盤");
	}
});
if (tabsq.length==1){
	TABS=tabsq;
}else{
	let tmpIndex=1;
	tabsq.forEach(function(it){
		TABS.push(it+tmpIndex);
		tmpIndex++;
	});
}
log('tzfile TABS >>>>>>>>>>>>>>>>>>' + TABS);
`,
		lists:`js:
log(TABS);
LISTS=[];
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
let d = pdfa(html, '#main article div.entry-content p');
d.forEach(function(it) {
	let purl = pd(it, 'a&&href', HOST);
	if (/(pan.quark.cn|www.aliyundrive.com)/.test(purl)){
		let type="ali";
		if (purl.includes("pan.quark.cn")){
			type="quark";
		} else if (purl.includes("www.aliyundrive.com")){
			type="ali";
		}
		let confirm="";
		if (TABS.length==1){
			confirm="&confirm=0";
		}
		LISTS.push([purl+'$'+'http://127.0.0.1:9978/proxy?do='+type+'&type=push'+confirm+'&url='+encodeURIComponent(purl)]);
	}
});
`,

	},
	搜索:'main#main div.container article:has(img);a&&title;img&&data-src;div.entry-wrapper a&&Text;a&&href',
}
