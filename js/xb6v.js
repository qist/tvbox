var rule = {
	title:'新版6V[磁]',
	host:'http://www.xb6v.com',
	homeUrl:'/',
	url: '/fyclass/index_fypage.html?',
	filter_url:'{{fl.class}}',
	filter:{
	},
	searchUrl: '/e/search/index.php#tempid=1&tbname=article&mid=1&dopost=search&submit=&keyborad=**;post',
	searchable:2,
	quickSearch:0,
	filterable:0,
	headers:{
		'User-Agent': 'PC_UA',
		'Referer': 'http://www.xb6v.com/'
	},
	timeout:5000,
	class_name:'最新50部&喜剧片&动作片&爱情片&科幻片&恐怖片&剧情片&战争片&纪录片&动画片&电视剧&综艺',
	class_url:'qian50m.html&xijupian&dongzuopian&aiqingpian&kehuanpian&kongbupian&juqingpian&zhanzhengpian&jilupian&donghuapian&dianshiju&ZongYi',
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
		url: pdfh(it, 'div.thumbnail&&a&&href')
	});
});
setResult(d);
	`,
	一级:'',
	一级:`js:
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
let d = [];
if (MY_CATE !== 'qian50m.html') {
	let turl = (MY_PAGE === 1)? '/' : '/index_'+ MY_PAGE + '.html';
	input = rule.homeUrl + MY_CATE + turl;
	let html = request(input);
	let list = pdfa(html, 'div.mainleft ul#post_container li');
	list.forEach(it => {
		d.push({
			title: pdfh(it, 'div.thumbnail img&&alt'),
			desc: pdfh(it, 'div.info&&span.info_date&&Text') + ' / ' + pdfh(it, 'div.info&&span.info_category&&Text'),
			pic_url: pd(it, 'div.thumbnail img&&src', HOST),
			url: pdfh(it, 'div.thumbnail&&a&&href')
		});
	})
}else{
	input = rule.homeUrl + MY_CATE;
	let html = request(input);
	let list = pdfa(html, 'div.container div#tab-content&&ul&&li');
	list.forEach(it => {
		let title = pdfh(it, 'a&&Text');
		if (title!==""){
			d.push({
				title: title,
				desc: pdfh(it, 'a&&Text'),
				pic_url: '',
				url: pdfh(it, 'a&&href')
			});
		}
	})
}
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
let d = pdfa(html, 'div#post_content table tbody tr a');
let tabsa = [];
let tabsq = [];
let tabsm = false;
let tabse = false;
let tabm3u8 = [];
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
if (false){
d = pdfa(html, 'div:has(>div#post_content) div.widget:has(>h3)');
d.forEach(function(it) {
	tabm3u8.push(pdfh(it, 'h3&&Text'));
});
}
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
tabm3u8.forEach(function(it){
	TABS.push(it);
});
log('xb6v TABS >>>>>>>>>>>>>>>>>>' + TABS);
`,
		lists:`js:
log(TABS);
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
LISTS = [];
let d = pdfa(html, 'div#post_content table tbody tr a');
let lista = [];
let listq = [];
let listm = [];
let liste = [];
let listm3u8 = {};
d.forEach(function(it){
	let burl = pdfh(it, 'a&&href');
	let title = pdfh(it, 'a&&Text');
	log('xb6v title >>>>>>>>>>>>>>>>>>>>>>>>>>' + title);
	log('xb6v burl >>>>>>>>>>>>>>>>>>>>>>>>>>' + burl);
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
if (false){
d = pdfa(html, 'div:has(>div#post_content) div.widget:has(>h3)');
d.forEach(function(it){
	let index = pdfh(it, 'h3&&Text');
	let burl = pd(it, 'a&&href', HOST);
	let title = pdfh(it, 'a&&Text');
	log('xb6v title >>>>>>>>>>>>>>>>>>>>>>>>>>' + title);
	log('xb6v burl >>>>>>>>>>>>>>>>>>>>>>>>>>' + burl);
	let m3u8_html = request(burl);
	let playerUrl = pd(m3u8_html, 'div.video&&iframe&&src', HOST);
	log('xb6v playerUrl >>>>>>>>>>>>>>>>>>>>>>>>>>' + playerUrl);
	if (!listm3u8.hasOwnProperty(index)){
		listm3u8[index] = [];
	}
	let loopresult = title + '$' + ' ';
	if (/(\\/player\\/|\\/share\\/)/.test(playerUrl)){
		let player_html = request(playerUrl);
		let m3u8Url="";
		try{
			m3u8Url = player_html.match(/'([^']*.m3u8)'/)[1];
		}catch(e){
			try{
				m3u8Url = player_html.match(/"([^"]*.m3u8)"/)[1];
			}catch(e){
				m3u8Url = "";
			}
		}
		if (m3u8Url !== ""){
			m3u8Url = urljoin2(playerUrl, m3u8Url);
			log('xb6v m3u8Url >>>>>>>>>>>>>>>>>>>>>>>>>>' + m3u8Url);
			loopresult = title + '$' + m3u8Url;
		}
	}
	listm3u8[index].push(loopresult);
});
}
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
let params = 'show=title&tempid=1&tbname=article&mid=1&dopost=search&submit=&keyboard=' + encodeURIComponent(KEY);
let _fetch_params = JSON.parse(JSON.stringify(rule_fetch_params));
let postData = {
    method: "POST",
    body: params
};
delete(_fetch_params.headers['Content-Type']);
Object.assign(_fetch_params, postData);
log("xb6v search postData>>>>>>>>>>>>>>>" + JSON.stringify(_fetch_params));
let search_html = request( HOST + '/e/search/index.php', _fetch_params, true);
//log("xb6v search result>>>>>>>>>>>>>>>" + search_html);
let d=[];
let dlist = pdfa(search_html, 'div.mainleft&&ul#post_container&&li');
dlist.forEach(function(it){
	let title = pdfh(it, 'div.thumbnail img&&alt').replace( /(<([^>]+)>)/ig, '');
	if (searchObj.quick === true){
		if (false && title.includes(KEY)){
			title = KEY;
		}
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
});
setResult(d);
`,
}
