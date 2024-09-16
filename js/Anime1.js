// 注意事项:此源仅支持 影视TV 及 爱佬版tvbox最新版
// 注意事项:此源仅支持 影视TV 及 爱佬版tvbox最新版
// 注意事项:此源仅支持 影视TV 及 爱佬版tvbox最新版
// 3个set-Cookie

var rule = {
	title:'Anime1动畫',
	host:'https://anime1.me',
	url: '/fyclass',
	detailUrl:'/?cat=fyid',
	searchUrl: '/page/fypage?s=**',
	searchable:2,
	quickSearch:0,
	headers:{'User-Agent': 'PC_UA'},
	timeout:5000,
    class_name:'連載中&2024&2023&2022&2021&2020&2019&2018&更早',
    class_url:'連載中&2024&2023&2022&2021&2020&2019&2018&2017',
	play_parse:true,
	lazy:`js:
		var apiurl = 'https://v.anime1.me/api';
		var html = request(apiurl, {
			headers: {
				'Referer': HOST,
			},
			body: 'd=' + input,
			method: 'POST',
			withHeaders: true
		});
		let json = JSON.parse(html);
		print(json);
		log(Object.keys(json));
		let setCk = Object.keys(json).filter(it => it.toLowerCase() === "set-cookie");
		let cookie = setCk ? json[setCk] : "";
		// 3个set-Cookie
		if (Array.isArray(cookie)) {
			cookie = cookie.join(';');
		}
		cookie = cookie.split(';').filter(function(it) {
			return ['e', 'p', 'h'].includes(it.split('=')[0])
		}).join(';');
		log(cookie);
		var purl = JSON.parse(json.body).s[0].src;
		if (purl.startsWith('/')) {
			purl = 'https:' + purl
		}
		input = {
			jx: 0,
			url: purl,
			parse: 0,
			header: JSON.stringify({
				'referer': HOST,
				'Cookie': cookie,
				'user-agent': PC_UA
			}),
		}
	`,
	limit:6,
	推荐: `js:
		var d = [];
		function stripHtmlTag(src) {
			return src.replace(/<\\/?[^>]+(>|$)/g, '').replace(/&.{1,5};/g, '').replace(/\\s{2,}/g, ' ');
		}
		var timestamp = new Date().getTime();
		var json = request('https://d1zquzjgwo9yb.cloudfront.net/?_=' + timestamp);
		var list = JSON.parse(json);
		let playKeys = Object.values(list).filter(function(x) {
			return x[2].includes('連載中');
		});
		playKeys.forEach(function(it) {
			d.push({
				title: stripHtmlTag(it[1]),
				img: 'https://sta.anicdn.com/playerImg/8.jpg',
				desc: it[2],
				url: it[0],
			});
		});
		setResult(d);
	`,
	一级: `js:
		var d = [];
		function stripHtmlTag(src) {
			return src.replace(/<\\/?[^>]+(>|$)/g, '').replace(/&.{1,5};/g, '').replace(/\\s{2,}/g, ' ');
		}
		var timestamp = new Date().getTime();
		var json = request('https://d1zquzjgwo9yb.cloudfront.net/?_=' + timestamp);
		var list = JSON.parse(json);
		let playKeys = Object.values(list).filter(function(x) {
			if (MY_CATE === '連載中') return x[2].includes(MY_CATE);
			else if (MY_CATE === '2017') return x[3] <= MY_CATE;
			else return x[3] == MY_CATE;
		});
		playKeys.forEach(function(it) {
			d.push({
				title: stripHtmlTag(it[1]),
				img: 'https://sta.anicdn.com/playerImg/8.jpg',
				desc: it[2],
				url: it[0],
			});
		});
		setResult(d);
	`,
	二级: `js:
		pdfh = jsp.pdfh; pdfa = jsp.pdfa; pd = jsp.pd;
		var html = request(input);
		var timestamp = new Date().getTime();
		var json = request('https://d1zquzjgwo9yb.cloudfront.net/?_=' + timestamp);
		var list = JSON.parse(json);
		var vid = input.split('=')[1];
		let playKeys = Object.values(list).find(function(x) {
			return x[0] === parseInt(vid);
		});
		VOD = {
			vod_pic: 'https://sta.anicdn.com/playerImg/8.jpg',
			vod_id: playKeys[0],
			vod_name: playKeys[1],
			vod_content: playKeys[2],
			vod_year: playKeys[3],
			type_name: playKeys[4],
			vod_actor: playKeys[5],
		};
		var pageurl = pd(html, '.cat-links&&a&&href');
		var pagenum = 1;
		let vod_tab_list = [];
		let vlist = [];
		for (let p = 1; p < parseInt(pagenum) + 1; p++) {
			let phtml = request(pageurl + '/page/' + pagenum);
			let new_vod_list = [];
			let vodList = [];
			vodList = pdfa(phtml, '.site-main&&article');
			for (let i = 0; i < vodList.length; i++) {
				let it = vodList[i];
				let ptitle = pdfh(it, '.entry-title&&Text').replace(/\\[(.*)\\]/, '$1');
				let purl = pd(it, '.video-js&&data-apireq');
				new_vod_list.push(ptitle + '$' + purl);
			}
			vlist = vlist.concat(new_vod_list);
			try {
				pagenum = pd(phtml, '.nav-previous&&a&&href').split('/page/')[1];
			} catch(e) {}
		}
		let vlist2 = vlist.reverse().join("#");
		vod_tab_list.push(vlist2);
		VOD.vod_play_from = '道长在线';
		VOD.vod_play_url = vod_tab_list.join("$$$");
	`,
	搜索: `js:
		var d = [];
		function stripHtmlTag(src) {
			return src.replace(/<\\/?[^>]+(>|$)/g, '').replace(/&.{1,5};/g, '').replace(/\\s{2,}/g, ' ');
		}
		var timestamp = new Date().getTime();
		var json = request('https://d1zquzjgwo9yb.cloudfront.net/?_=' + timestamp);
		var list = JSON.parse(json);
		var wd = input.split('=')[1];
		let playKeys = Object.values(list).filter(function(x) {
			return x[1].includes(wd);
		});
		log(playKeys);
		playKeys.forEach(function(it) {
			d.push({
				title: stripHtmlTag(it[1]),
				img: 'https://sta.anicdn.com/playerImg/8.jpg',
				desc: it[2],
				url: it[0],
			});
		});
		setResult(d);
	`,
}