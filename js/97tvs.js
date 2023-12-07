var rule = {
	title:'高清MP4吧',
	host:'https://www.97tvs.com',
        homeUrl: '/',
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
         	'Cookie':'',
		'Referer': 'http://www.97tvs.com/'
	},
	图片来源:'@Headers={"Accept":"*/*","Referer":"https://www.97tvs.com/","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"}',
	timeout:5000,
  	class_name: "动作片&科幻片&爱情片&喜剧片&剧情片&惊悚片&战争片&灾难片&罪案片&动画片&综艺&电视剧",
  	class_url: "action&science&love&comedy&story&thriller&war&disaster&crime&cartoon&variety&sitcoms",
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
let list = pdfa(html, 'div.mainleft ul#post_container li');
list.forEach(it => {
	d.push({
		title: pdfh(it, 'div.thumbnail img&&alt'),
		desc: pdfh(it, 'div.info&&span.info_date&&Text') + ' / ' + pdfh(it, 'div.info&&span.info_category&&Text'),
		pic_url: pd(it, 'div.thumbnail img&&src', HOST),
		url: pd(it, 'div.thumbnail&&a&&href',HOST)
	});
});
setResult(d);
	`,
	一级:`js:
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
let d = [];
let html = request(input);
let list = pdfa(html, 'div.mainleft ul#post_container li');
list.forEach(it => {
	d.push({
		title: pdfh(it, 'div.thumbnail img&&alt'),
		desc: pdfh(it, 'div.info&&span.info_date&&Text') + ' / ' + pdfh(it, 'div.info&&span.info_category&&Text'),
		pic_url: pd(it, 'div.thumbnail img&&src', HOST),
		url: pd(it, 'div.thumbnail&&a&&href',HOST)
	});
})
setResult(d);
`,
	二级:{
		title:"div.article_container h1&&Text",
		img:"div#post_content img&&src",
		desc:"div#post_content&&Text",
		content:"div#post_content&&Text",
		tabs:`js:
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
TABS=[]
let d = pdfa(html, 'div#post_content p');
let tabsa = [];
let tabsq = [];
let tabsm = false;
let tabse = false;
let tabm3u8 = [];
d.forEach(function(it) {
	let burl = pdfh(it, 'a&&href');
	if (burl.startsWith("https://www.aliyundrive.com/s/") || burl.startsWith("https://www.alipan.com/s/")){
		tabsa.push("阿里雲盤");
	}else if (burl.startsWith("https://pan.quark.cn/s/")){
		tabsq.push("夸克網盤");
	}else if (burl.startsWith("magnet")){
		tabsm = true;
	}else if (burl.startsWith("ed2k")){
		tabse = true;
	}
});
if (tabsm === true){
	TABS.push("磁力");
}
if (tabse === true){
	TABS.push("電驢");
}
let tmpIndex;
tmpIndex=1;
tabsa.forEach(function(it){
	TABS.push(it + tmpIndex);
	tmpIndex = tmpIndex + 1;
});
tmpIndex=1;
tabsq.forEach(function(it){
	TABS.push(it + tmpIndex);
	tmpIndex = tmpIndex + 1;
});
tabm3u8.forEach(function(it){
	TABS.push(it);
});
log('97tvs TABS >>>>>>>>>>>>>>>>>>' + TABS);
`,
		lists:`js:
log(TABS);
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
LISTS = [];
let d = pdfa(html, 'div#post_content p');
let lista = [];
let listq = [];
let listm = [];
let liste = [];
let listm3u8 = {};
d.forEach(function(it){
	let burl = pdfh(it, 'a&&href');
	let title = pdfh(it, 'a&&Text');
	log('97tvs title >>>>>>>>>>>>>>>>>>>>>>>>>>' + title);
	log('97tvs burl >>>>>>>>>>>>>>>>>>>>>>>>>>' + burl);
	let loopresult = title + '$' + burl;
	if (burl.startsWith("https://www.aliyundrive.com/s/") || burl.startsWith("https://www.alipan.com/s/")){
		if (true){
		if (TABS.length==1){
			burl = "http://127.0.0.1:9978/proxy?do=ali&type=push&confirm=0&url=" + encodeURIComponent(burl);
		}else{
			burl = "http://127.0.0.1:9978/proxy?do=ali&type=push&url=" + encodeURIComponent(burl);
		}
		}else{
                        burl = "push://" + burl;
                }
		loopresult = title + '$' + burl;
		lista.push(loopresult);
	}else if (burl.startsWith("https://pan.quark.cn/s/")){
		if (true){
		if (TABS.length==1){
			burl = "http://127.0.0.1:9978/proxy?do=quark&type=push&confirm=0&url=" + encodeURIComponent(burl);
		}else{
			burl = "http://127.0.0.1:9978/proxy?do=quark&type=push&url=" + encodeURIComponent(burl);
		}
		}else{
                        burl = "push://" + burl;
                }
		loopresult = title + '$' + burl;
		listq.push(loopresult);
	}else if (burl.startsWith("magnet")){
		listm.push(loopresult);
	}else if (burl.startsWith("ed2k")){
		liste.push(loopresult);
	}
});
if (listm.length>0){
	LISTS.push(listm);
}
if (liste.length>0){
	LISTS.push(liste);
}
lista.forEach(function(it){
	LISTS.push([it]);
});
listq.forEach(function(it){
	LISTS.push([it]);
});
for ( const key in listm3u8 ){
	if (listm3u8.hasOwnProperty(key)){
		LISTS.push(listm3u8[key]);
	}
};
`,

	},
	搜索:`js:
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
let search_html = request(input)
//log("97tvs search result>>>>>>>>>>>>>>>" + search_html);
let d=[];
let dlist = pdfa(search_html, 'div.mainleft ul#post_container li');
dlist.forEach(function(it){
	let title = pdfh(it, 'div.thumbnail img&&alt').replace( /(<([^>]+)>)/ig, '');
	if (title.includes(KEY)){
		if (searchObj.quick === true){
			title = KEY;
		}
		let img = pd(it, 'div.thumbnail img&&src', HOST);
		let content = pdfh(it, 'div.article div.entry_post&&Text');
		let desc = pdfh(it, 'div.info&&span.info_date&&Text');
		let url = pd(it, 'div.thumbnail&&a&&href', HOST);
		d.push({
			title:title,
			img:img,
			content:content,
			desc:desc,
			url:url
			});
	}
});
setResult(d);
`,
}
