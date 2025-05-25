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
         	'Cookie':'hvLw_2132_saltkey=x89cF7aD; hvLw_2132_lastvisit=1691840602; hvLw_2132_visitedfid=2; hvLw_2132_sendmail=1; _clck=hvltzs|2|fe4|0|1234; hvLw_2132_seccodecS=5681.04cfefe37df21abe97; hvLw_2132_ulastactivity=1691933173%7C0; hvLw_2132_auth=e9f3f37HqkcIBFlhm8r%2FqsQJNVKy9x1%2BRzROV4QROggK5CuZMQ3pmPzm9JwrPr%2FCkV7PzN7Nvt0yW1yEQXQjasm3AQ; hvLw_2132_sid=0; hvLw_2132_st_t=99213%7C1691933177%7C1fa4611ff255a89678127a126372871e; hvLw_2132_forum_lastvisit=D_2_1691933177; hvLw_2132_lastact=1691933194%09search.php%09forum; _clsk=fhws28|1691933195886|4|1|r.clarity.ms/collect',
	},
	timeout:5000,
	class_name: "4K电影&4K美剧&4K华语&4K动画&4K纪录片&4K日韩印&蓝光电影&蓝光美剧&蓝光华语&蓝光动画&蓝光日韩印",
	class_url:"3&8&15&6&11&4&29&31&33&32&34",
	play_parse:false,
	lazy:'',
	limit:6,
	推荐:'ul#waterfall li;a&&title;img&&src;div.auth.cl&&Text;a&&href',
	一级:'ul#waterfall li;a&&title;img&&src;div.auth.cl&&Text;a&&href',
	二级:{
		title:"#thread_subject&&Text",
		img:"img.zoom&&src",
		desc:'td[id^="postmessage_"] font&&Text',
		content:'td[id^="postmessage_"] font&&Text',
		tabs:`js:
			pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
			TABS=[]
			var d = pdfa(html, 'table.t_table');
			let magnetIndex=0;
			let aliIndex=0;
			d.forEach(function(it) {
				let burl = pdfh(it, 'a&&href');
				log("burl >>>>>>" + burl);
				if (burl.startsWith("https://www.aliyundrive.com/s/")){
					let result = 'aliyun' + aliIndex;
					aliIndex = aliIndex + 1;
					TABS.push(result);
				}
			});
			d.forEach(function(it) {
				let burl = pdfh(it, 'a&&href');
				log("burl >>>>>>" + burl);
				if (burl.startsWith("magnet")){
					let result = 'magnet' + magnetIndex;
					magnetIndex = magnetIndex + 1;
					TABS.push(result);
				}
			});
			log('TABS >>>>>>>>>>>>>>>>>>' + TABS);
		`,
		lists:`js:
			log(TABS);
			pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
			LISTS = [];
			var d = pdfa(html, 'table.t_table');
			TABS.forEach(function(tab) {
				log('tab >>>>>>>>' + tab);
				if (/^aliyun/.test(tab)) {
					let targetindex = parseInt(tab.substring(6));
					let index = 0;
					d.forEach(function(it){
						let burl = pdfh(it, 'a&&href');
						if (burl.startsWith("https://www.aliyundrive.com/s/")){
							if (index == targetindex){
								let title = pdfh(it, 'a&&Text');
								log('title >>>>>>>>>>>>>>>>>>>>>>>>>>' + title);
								//burl = "http://127.0.0.1:9978/proxy?do=ali&type=push&url=" + encodeURIComponent(burl);
								burl = "push://" + encodeURIComponent(burl);
								log('burl >>>>>>>>>>>>>>>>>>>>>>>>>>' + burl);
								let loopresult = title + '$' + burl;
								LISTS.push([loopresult]);
							}
							index = index + 1;
						}
					});
				}
			});
			TABS.forEach(function(tab) {
				log('tab >>>>>>>>' + tab);
				if (/^magnet/.test(tab)) {
					let targetindex = parseInt(tab.substring(6));
					let index = 0;
					d.forEach(function(it){
						let burl = pdfh(it, 'a&&href');
						if (burl.startsWith("magnet")){
							if (index == targetindex){
								let title = pdfh(it, 'a&&Text');
								log('title >>>>>>>>>>>>>>>>>>>>>>>>>>' + title);
								log('burl >>>>>>>>>>>>>>>>>>>>>>>>>>' + burl);
								let loopresult = title + '$' + burl;
								LISTS.push([loopresult]);
							}
							index = index + 1;
						}
					});
				}
			});
			`,

	},
	一级:'ul#waterfall li;a&&title;img&&src;div.auth.cl&&Text;a&&href',
	搜索:'div#threadlist ul li;h3&&Text;;p:eq(3)&&Text;a&&href;p:eq(2)&&Text',
	预处理:`
    		if (rule_fetch_params.headers.Cookie.startsWith("http")){
			rule_fetch_params.headers.Cookie=fetch(rule_fetch_params.headers.Cookie);
			setItem(RULE_CK,cookie);
		};
		log('4khdr cookie>>>>>>>>>>>>>>>' + rule_fetch_params.headers.Cookie);
		let new_host='https://www.4khdr.cn/search.php';
		let new_html=request(new_host);
		pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
		let formhash = pdfh(new_html, 'input[name="formhash"]&&value');
		log("formhash>>>>>>>>>>>>>>>" + formhash);
		rule_fetch_params.formhash = formhash;
	`,
}