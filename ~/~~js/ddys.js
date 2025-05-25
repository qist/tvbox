var lists = `js:
log(TABS);
let d = [];
pdfh = jsp.pdfh;
pdfa = jsp.pdfa;
if (typeof play_url === "undefined") {
	var play_url = ""
}

function getLists(html) 
{
	let src = pdfh(html, ".wp-playlist-script&&Html");
	src = JSON.parse(src).tracks;
	let list1 = [];
	let list2 = [];
	let url1 = "";
	let url2 = "";
	src.forEach(function(it) {
		let src0 = it.src0;
		let src1 = it.src1;
		let title = it.caption;
		url1 = "https://v.ddys.pro" + src0;
		url2 = "https://ddys.pro/getvddr2/video?id=" + src1 + "&type=mix";
		let zm = "https://ddys.pro/subddr/" + it.subsrc;
		list1.push({
			title: title,
			url: url1,
			desc: zm
		});
		list2.push({
			title: title,
			url: url2,
			desc: zm
		})
	});
	return {
		list1: list1,
		list2: list2
	}
}
var data = getLists(html);
var list1 = data.list1;
var list2 = data.list2;
let nums = pdfa(html, "body&&.post-page-numbers");
nums.forEach
(function(it) 
{
	let num = pdfh(it, "body&&Text");
	log(num);
	let nurl = input + num + "/";
	if (num == 1) {
		return
	}
	log(nurl);
	let html = request(nurl);
	let data = getLists(html);
	list1 = list1.concat(data.list1);
	list2 = list2.concat(data.list2)
});


list1 = list1.map(function(item) {
	return item.title + "$" + play_url + urlencode(item.url + "|" + input + "|" + item.desc)
});
list2 = list2.map(function(item) {
	return item.title + "$" + play_url + urlencode(item.url + "|" + input + "|" + item.desc)
});
LISTS=[];
let dd = pdfa(html, 'div.wp-playlist~a');
dd.forEach(function(it){
	let burl = pd(it, 'a&&href', HOST);
	if (/(pan.quark.cn|www.aliyundrive.com|www.alipan.com)/.test(burl)){
		let type="ali";
		if (burl.includes("www.aliyundrive.com") || burl.includes("www.alipan.com")){
			type = "ali";
		}else if (burl.includes("pan.quark.cn")){
			type = "quark";
		}
		LISTS.push([burl+ '$' + play_url + urlencode('http://127.0.0.1:9978/proxy?do='+type+'&type=push&url='+encodeURIComponent(burl)) + '||']);
	}
});
LISTS = LISTS.concat([list1, list2]);
`;

var lazy = `js:
let purl = input.split("|")[0];
let referer = input.split("|")[1];
let zm = input.split("|")[2];
print("purl:" + purl);
print("referer:" + referer);
print("zm:" + zm);
if (/getvddr/.test(purl)) {
    let html = request(purl, {
        headers: {
            Referer: HOST,
            "User-Agent": MOBILE_UA
        }
    });
    print(html);
    try {
        input = {jx:0,url:JSON.parse(html).url,parse:0} || {}
    } catch (e) {
        input = purl
    }
} else {
    input = {
        jx: 0,
        url: purl,
        parse: 0,
        header: JSON.stringify({
            'user-agent': MOBILE_UA,
            'referer': HOST
        })
    }
}
`;

// 网址发布页 https://ddys.site
// 网址发布页 https://ddys.wiki
var rule={
    title:'ddys',
    // host:'https://ddys.wiki', 
    // hostJs:'print(HOST);let html=request(HOST,{headers:{"User-Agent":MOBILE_UA}});HOST = jsp.pdfh(html,"a:eq(1)&&href")',
    host:'https://ddys.pro',
    // host:'https://ddys.mov',
    url:'/fyclass/page/fypage/',
    searchUrl:'/?s=**&post_type=post',
    searchable:2,
    quickSearch:0,
    filterable:0,
    headers:{
        'User-Agent':'MOBILE_UA',
    },
    class_parse:'#primary-menu li.menu-item;a&&Text;a&&href;\.pro/(.*)',
    cate_exclude:'站长|^其他$|关于|^电影$|^剧集$|^类型$',
    play_parse:true,
    // lazy:'js:let purl=input.split("|")[0];let referer=input.split("|")[1];let zm=input.split("|")[2];print("purl:"+purl);print("referer:"+referer);print("zm:"+zm);let myua="okhttp/3.15";if(/ddrkey/.test(purl)){let ret=request(purl,{Referer:referer,withHeaders:true,"User-Agent":myua});log(ret);input=purl}else{let html=request(purl,{headers:{Referer:referer,"User-Agent":myua}});print(html);try{input=JSON.parse(html).url||{}}catch(e){input=purl}}',
    lazy:lazy,
    limit:6,
    推荐:'*',
    double:true, // 推荐内容是否双层定位
    一级:'.post-box-list&&article;a:eq(-1)&&Text;.post-box-image&&style;a:eq(0)&&Text;a:eq(-1)&&href',
    二级:{
        "title":".post-title&&Text;.cat-links&&Text",
        "img":".doulist-item&&img&&data-cfsrc",
        "desc":".published&&Text",
        "content":".abstract&&Text",
        "tabs":`js:
TABS=[];
let d = pdfa(html, 'div.wp-playlist~a');
let tabsq=[];
d.forEach(function(it){
	let burl = pd(it, 'a&&href', HOST);
	if (burl.includes("pan.quark.cn")){
		tabsq.push("夸克網盤");
	}else if (burl.includes("www.aliyundrive.com") || burl.includes("www.alipan.com")){
		tabsq.push("阿里雲盤");
	}
});
if (tabsq.length == 1){
	TABS=TABS.concat(tabsq);
}else{
	let tmpIndex=1;
	tabsq.forEach(function(it){
		TABS.push(it+tmpIndex);
		tmpIndex++;
	});
}
TABS=TABS.concat(['国内(改Exo播放器)','国内2']);
`,
        "lists":lists
    },
    搜索:'#main&&article;.post-title&&Text;;.published&&Text;a&&href'
}
