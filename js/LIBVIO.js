// 永久网址：https://libvio.app
muban.首图2.二级.title = 'h1&&Text;.data:eq(0)&&Text'
muban.首图2.二级.desc = '.data.hidden-xs&&Text;;;.data:eq(1)&&Text;.data:eq(4)&&Text'
muban.首图2.二级.content = '.detail-content&&Text'
var rule = {
	title:'LIBVIO',
	模板:'首图2',
	// host:'https://tv.libvio.cc',
	host:'https://tv.libvio.cc',
	//hostJs:'print(HOST);let html=request(HOST,{headers:{"User-Agent":PC_UA}});let src=jsp.pdfh(html,"li:eq(0)&&a:eq(0)&&href");print(src);HOST=src',
	// url:'/type/fyclass-fypage.html',
	url:'/show/fyclassfyfilter.html',
	// url:'/show_fyclassfyfilter.html',
	filterable:1,//是否启用分类筛选,
	filter_url:'-{{fl.area}}-{{fl.by}}--{{fl.lang}}----fypage---{{fl.year}}',
	filter: {
		"1":[{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"中国大陆","v":"中国大陆"},{"n":"中国香港","v":"中国香港"},{"n":"中国台湾","v":"中国台湾"},{"n":"美国","v":"美国"},{"n":"法国","v":"法国"},{"n":"英国","v":"英国"},{"n":"日本","v":"日本"},{"n":"韩国","v":"韩国"},{"n":"德国","v":"德国"},{"n":"泰国","v":"泰国"},{"n":"印度","v":"印度"},{"n":"意大利","v":"意大利"},{"n":"西班牙","v":"西班牙"},{"n":"加拿大","v":"加拿大"},{"n":"其他","v":"其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"法语","v":"法语"},{"n":"德语","v":"德语"},{"n":"其它","v":"其它"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
		"2":[{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"中国大陆","v":"中国大陆"},{"n":"中国台湾","v":"中国台湾"},{"n":"中国香港","v":"中国香港"},{"n":"韩国","v":"韩国"},{"n":"日本","v":"日本"},{"n":"美国","v":"美国"},{"n":"泰国","v":"泰国"},{"n":"英国","v":"英国"},{"n":"新加坡","v":"新加坡"},{"n":"其他","v":"其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
		"4":[{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"中国","v":"中国"},{"n":"日本","v":"日本"},{"n":"欧美","v":"欧美"},{"n":"其他","v":"其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
		"27":[{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
		"15":[{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"日本","v":"日本"},{"n":"韩国","v":"韩国"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
		"16":[{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"美国","v":"美国"},{"n":"英国","v":"英国"},{"n":"德国","v":"德国"},{"n":"加拿大","v":"加拿大"},{"n":"其他","v":"其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}]
	},
	headers:{//网站的请求头,完整支持所有的,常带ua和cookies
		'User-Agent':'MOBILE_UA'
	},
	class_parse:'.stui-header__menu li:gt(0):lt(7);a&&Text;a&&href;/(\\d+).html',
	// class_parse:'.stui-header__menu li;a&&Text;a&&href;/.*_(\\d+).html',
	tab_exclude: '百度',
	pagecount:{"27":1},
	二级: {
		"title": ".stui-content__detail .title&&Text;.stui-content__detail p:eq(-2)&&Text",
		"img": ".stui-content__thumb .lazyload&&data-original",
		"desc": ".stui-content__detail p:eq(0)&&Text;.stui-content__detail p:eq(1)&&Text;.stui-content__detail p:eq(2)&&Text",
		"content": ".detail&&Text",
		"tabs": `js:
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
TABS=[];
let tabsq=[];
let tabsm3u8=[];
let d = pdfa(html, 'div.stui-vodlist__head');
d.forEach(function(it) {
	let name = pdfh(it, 'h3&&Text');
	if (!/(猜你|喜欢|剧情|热播)/.test(name)){
		log("libvio tabs name>>>>>>>>>>>>>>>" + name);
		if (name.includes("夸克")){
			tabsq.push("夸克雲盤");
		}else if (name.includes("阿里")){
			tabsq.push("阿里雲盤");
		}else{
			tabsm3u8.push(name);
		}
	}
});
if (tabsq.length==1){
	TABS=TABS.concat(tabsq);
}else{
	let tmpIndex=1;
	tabsq.forEach(function(it){
		TABS.push(it+tmpIndex);
		tmpIndex++;
	});
}
TABS=TABS.concat(tabsm3u8);
log('libvio TABS >>>>>>>>>>>>>>>>>>' + TABS);
`,
		"lists":`js:
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
LISTS = [];
let listq=[];
let listm3u8=[];
let d = pdfa(html, 'div.stui-vodlist__head');
d.forEach(function(it){
	let name = pdfh(it, 'h3&&Text');
	if (!/(猜你|喜欢|剧情|热播)/.test(name)){
		log("libvio tabs name>>>>>>>>>>>>>>>" + name);
		let durl = pdfa(it, 'ul li');
		let dd = [];
		durl.forEach(function(it1){
			let dhref = pd(it1, 'a&&href', HOST);
			let dname = pdfh(it1, 'a&&Text');
			dd.push(dname + "$" + dhref);
		});
		if (/(夸克|阿里)/.test(name)){
			listq.push(dd);
		}else{
			listm3u8.push(dd);
		}
	}
});
LISTS=LISTS.concat(listq);
LISTS=LISTS.concat(listm3u8);
`,
	},
	lazy:`js: 
log("libvio lazy player input>>>>>>>>>>>>"+input);
var html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
log("libvio lazy player json>>>>>>>>>>>>"+JSON.stringify(html));
var url = html.url;
var from = html.from;
var next = html.link_next;
var id = html.id;
var nid = html.nid;
if (/(www.aliyundrive.com|pan.quark.cn)/.test(url)){
	let confirm = "";
	if (TABS.length==1){
		confirm="&confirm=0";
	}
	let type="ali";
	if (url.includes("www.aliyundrive.com")){
		type = "ali";
	}else if (url.includes("pan.quark.cn")){
		type = "quark";
	}
	input = {
		jx: 0,
		url: 'http://127.0.0.1:9978/proxy?do=' + type +'&type=push' + confirm + '&url=' + encodeURIComponent(url),
		parse: 0
	}
}else{
	var paurl = request("https://libvio.cc/static/player/" + from + ".js").match(/ src="(.*?)'/)[1];
	if (/https/.test(paurl)) {
		var purl = paurl + url + "&next=" + next + "&id=" + id + "&nid=" + nid;
		input = {
			jx: 0,
			url: request(purl).match(/var .* = '(.*?)'/)[1],
			parse: 0
		}
	}
}
`,
	searchUrl:'/index.php/ajax/suggest?mid=1&wd=**&limit=50',
	detailUrl:'/detail/fyid.html', //非必填,二级详情拼接链接
	// detailUrl:'/detail_fyid.html', //非必填,二级详情拼接链接
	// searchUrl:'/search/**----------fypage---.html',
	搜索:'json:list;name;pic;;id',
}
