var rule = {
    title: 'dydhhy',
    host: 'http://www.dydhhy.com',
    homeUrl: '/',
    url: '/tag/fyclass/page/fypage?',
    filter_url: '{{fl.class}}',
    filter: {},
    searchUrl: '/?s=**',
    searchable: 2,
    quickSearch: 1,
    filterable: 0,
    headers: {
        'User-Agent': 'MOBILE_UA',
        'Cookie': ''
    },
    timeout: 5000,
    class_name: '电视剧&电影&美剧&韩剧&日剧&英剧&2023&2022&2021',
    class_url: 'tv&movie&美剧&韩剧&日剧&英剧&2023&2022&2021',
    play_parse: true,
    play_json: [{
        re: '*',
        json: {
            parse: 0,
            jx: 0
        }
    }],
    lazy: '',
    limit: 6,
    推荐: 'div.clear:gt(1):has(img);.entry-title&&Text;img&&src;;a&&href',
    一级: 'div.clear:gt(1):has(img);.entry-title&&Text;img&&src;;a&&href',
    二级: {
        title: ".single-excerpt&&Text",
        img: "img&&src",
        desc: ".entry-date&&Text",
        content: "p&&Text",
        tabs: `js: pdfh = jsp.pdfh;
        pdfa = jsp.pdfa;
        pd = jsp.pd;
TABS=[]
let d = pdfa(html, 'fieldset p a');
let tabsa = [];
let tabsq = [];
let tabsm = false;
let tabse = false;
d.forEach(function(it) {
	let burl = pdfh(it, 'a&&href');
	if (burl.startsWith("https://www.aliyundrive.com/s/")){
		tabsa.push("阿里云盤");
	}else if (burl.startsWith("https://pan.quark.cn/s/")){
		tabsq.push("夸克云盤");
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
if (false && tabsa.length + tabsq.length > 1){
	TABS.push("選擇右側綫路");
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
log('xzys TABS >>>>>>>>>>>>>>>>>>' + TABS);`,
lists: `js: log(TABS);
pdfh = jsp.pdfh;
pdfa = jsp.pdfa;
pd = jsp.pd;
LISTS = [];
let d = pdfa(html, 'fieldset p a');
let lista = [];
let listq = [];
let listm = [];
let liste = [];
d.forEach(function(it){
	let burl = pdfh(it, 'a&&href');
	let title = pdfh(it, 'a&&Text');
	log('dygang title >>>>>>>>>>>>>>>>>>>>>>>>>>' + title);
	log('dygang burl >>>>>>>>>>>>>>>>>>>>>>>>>>' + burl);
	let loopresult = title + '$' + burl;
	if (burl.startsWith("https://www.aliyundrive.com/s/")){
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
if (false && lista.length + listq.length > 1){
	LISTS.push(["選擇右側綫路，或3秒後自動跳過$http://127.0.0.1:10079/delay/"]);
}
lista.forEach(function(it){
	LISTS.push([it]);
});
listq.forEach(function(it){
	LISTS.push([it]);

});`,

}, 搜索: 'div.clear:gt(0):has(img);img&&alt;img&&data-src;;a&&href',
}
