var rule = {
	title:'团长资源',
	host:'https://t-rex.tzfile.com',
	homeUrl:'/',
	url: '/fyclass/page/fypage?',
	filter_url:'{{fl.class}}',
	filter:{
	},
	searchUrl: '/?s=**&type=post',
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
	推荐:'*',
	一级:`js:
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
let d = [];
log("tzfiles input>>>>>>>>>>>>>>"+input);
let html = request(input);
//log("tzfiles 1level html>>>>>>>>>>>>>>"+html);
let list = pdfa(html, '#primary-home ul li:has(img)');
list.forEach(function(it) {
	d.push({
		title: pdfh(it, 'img&&alt'),
		desc: pdfh(it, 'div.post-info .post-list-cat&&Text'),
		pic_url: 'http://127.0.0.1:10079/i/0/s/'+pd(it, 'img&&src', HOST),
		url: pd(it, 'a&&href', HOST)
	});
})
setResult(d);
`,
	二级:{
		title:"#primary-home h1&&Text",
		img:"#primary-home article div.entry-content img&&src",
		desc:"#primary-home .post-meta li.single-date&&Text",
		content:"#primary-home article .entry-content&&Text",
		tabs:`js:
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
TABS=[];
let d = pdfa(html, '#primary-home article div.entry-content p');
let tabsq=[];
d.forEach(function(it) {
	let purl = pd(it, 'a&&href', HOST);
	if (purl.includes("pan.quark.cn")){
		tabsq.push("夸克網盤");
	} else if (burl.startsWith("https://www.aliyundrive.com/s/") || burl.startsWith("https://www.alipan.com/s/")){
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
let d = pdfa(html, '#primary-home article div.entry-content p');
d.forEach(function(it) {
	let purl = pd(it, 'a&&href', HOST);
	if (/(pan.quark.cn|www.aliyundrive.com|www.alipan.com)/.test(purl)){
		let type="ali";
		if (purl.includes("pan.quark.cn")){
			type="quark";
		} else if (purl.includes("www.aliyundrive.com") || purl.includes("www.alipan.com")){
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
	搜索:`js:
//'#primary-home ul li:has(img);img&&alt;img&&src;div.post-info .post-list-cat&&Text;a&&href',
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
let html = request(input);
let d=[];
let dlist = pdfa(html, '#primary-home ul li:has(img)');
dlist.forEach(function(it){
	let title=pdfh(it, 'img&&alt');
	if (title.includes(KEY)){
		if (searchObj.quick === true){
			title = KEY;
		}
		let img='http://127.0.0.1:10079/i/0/s/' + pd(it, 'img&&src',HOST);
		let content=pdfh(it, 'div.text_info h2&&Text');
		let url=pd(it, 'a&&href', HOST);
		let desc=pdfh(it, 'p.info&&Text');
		d.push({
			title:title,
			img:img,
			content:content,
			desc:desc,
			url:url
			})
	}
});
setResult(d);
`,
}
