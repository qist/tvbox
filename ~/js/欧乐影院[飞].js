// 搜索功能关闭中

var rule = {
	title:'欧乐影院[飞]',
	host:'https://www.olevod.com',
	// url:'/index.php/vod/show/id/fyclass/page/fypage.html',
	url:'/index.php/vod/show/id/fyfilter.html',
	filterable:1,//是否启用分类筛选,
	filter_url:'{{fl.cateId}}{{fl.area}}{{fl.by}}{{fl.lang}}{{fl.letter}}/page/fypage{{fl.year}}',
	filter:{
		"1":[{"key":"cateId","name":"分类","value":[{"n":"全部","v":"1"},{"n":"动作片","v":"101"},{"n":"喜剧片","v":"102"},{"n":"爱情片","v":"103"},{"n":"科幻片","v":"104"},{"n":"恐怖片","v":"105"},{"n":"剧情片","v":"106"},{"n":"战争片","v":"107"},{"n":"动画片","v":"108"},{"n":"悬疑片","v":"109"},{"n":"惊悚片","v":"110"},{"n":"纪录片","v":"111"},{"n":"奇幻片","v":"112"},{"n":"犯罪片","v":"113"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"/area/大陆"},{"n":"香港","v":"/area/香港"},{"n":"台湾","v":"/area/台湾"},{"n":"美国","v":"/area/美国"},{"n":"韩国","v":"/area/韩国"},{"n":"日本","v":"/area/日本"},{"n":"印度","v":"/area/印度"},{"n":"英国","v":"/area/英国"},{"n":"法国","v":"/area/法国"},{"n":"加拿大","v":"/area/加拿大"},{"n":"西班牙","v":"/area/西班牙"},{"n":"德国","v":"/area/德国"},{"n":"俄罗斯","v":"/area/俄罗斯"},{"n":"意大利","v":"/area/意大利"},{"n":"泰国","v":"/area/泰国"},{"n":"新加坡","v":"/area/新加坡"},{"n":"马来西亚","v":"/area/马来西亚"},{"n":"其它","v":"/area/其它"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"2013","v":"/year/2013"},{"n":"2012","v":"/year/2012"},{"n":"2011","v":"/year/2011"},{"n":"2010","v":"/year/2010"},{"n":"2009","v":"/year/2009"},{"n":"2008","v":"/year/2008"},{"n":"2007","v":"/year/2007"},{"n":"2006","v":"/year/2006"},{"n":"2005","v":"/year/2005"},{"n":"2004","v":"/year/2004"},{"n":"2003","v":"/year/2003"},{"n":"2002","v":"/year/2002"},{"n":"2001","v":"/year/2001"},{"n":"2000","v":"/year/2000"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"/lang/国语"},{"n":"英语","v":"/lang/英语"},{"n":"粤语","v":"/lang/粤语"},{"n":"西语","v":"/lang/西语"},{"n":"韩语","v":"/lang/韩语"},{"n":"日语","v":"/lang/日语"},{"n":"法语","v":"/lang/法语"},{"n":"俄语","v":"/lang/俄语"},{"n":"意大利语","v":"/lang/意大利语"},{"n":"德语","v":"/lang/德语"},{"n":"印地语","v":"/lang/印地语"},{"n":"其它","v":"/lang/其它"}]},{"key":"letter","name":"字母","value":[{"n":"全部","v":""},{"n":"A","v":"/letter/A"},{"n":"B","v":"/letter/B"},{"n":"C","v":"/letter/C"},{"n":"D","v":"/letter/D"},{"n":"E","v":"/letter/E"},{"n":"F","v":"/letter/F"},{"n":"G","v":"/letter/G"},{"n":"H","v":"/letter/H"},{"n":"I","v":"/letter/I"},{"n":"J","v":"/letter/J"},{"n":"K","v":"/letter/K"},{"n":"L","v":"/letter/L"},{"n":"M","v":"/letter/M"},{"n":"N","v":"/letter/N"},{"n":"O","v":"/letter/O"},{"n":"P","v":"/letter/P"},{"n":"Q","v":"/letter/Q"},{"n":"R","v":"/letter/R"},{"n":"S","v":"/letter/S"},{"n":"T","v":"/letter/T"},{"n":"U","v":"/letter/U"},{"n":"V","v":"/letter/V"},{"n":"W","v":"/letter/W"},{"n":"X","v":"/letter/X"},{"n":"Y","v":"/letter/Y"},{"n":"Z","v":"/letter/Z"},{"n":"0-9","v":"/letter/0-9"}]},{"key":"by","name":"排序","value":[{"n":"按最新","v":"/by/time"},{"n":"按添加","v":"/by/time_add"},{"n":"按最热","v":"/by/hits"},{"n":"按评分","v":"/by/score"}]}],
		"2":[{"key":"cateId","name":"分类","value":[{"n":"全部","v":"2"},{"n":"国产剧","v":"202"},{"n":"欧美剧","v":"201"},{"n":"港台剧","v":"203"},{"n":"日韩剧","v":"204"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"/area/大陆"},{"n":"香港","v":"/area/香港"},{"n":"台湾","v":"/area/台湾"},{"n":"美国","v":"/area/美国"},{"n":"韩国","v":"/area/韩国"},{"n":"日本","v":"/area/日本"},{"n":"印度","v":"/area/印度"},{"n":"英国","v":"/area/英国"},{"n":"法国","v":"/area/法国"},{"n":"加拿大","v":"/area/加拿大"},{"n":"西班牙","v":"/area/西班牙"},{"n":"俄罗斯","v":"/area/俄罗斯"},{"n":"意大利","v":"/area/意大利"},{"n":"泰国","v":"/area/泰国"},{"n":"新加坡","v":"/area/新加坡"},{"n":"马来西亚","v":"/area/马来西亚"},{"n":"其它","v":"/area/其它"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"2013","v":"/year/2013"},{"n":"2012","v":"/year/2012"},{"n":"2011","v":"/year/2011"},{"n":"2010","v":"/year/2010"},{"n":"2009","v":"/year/2009"},{"n":"2008","v":"/year/2008"},{"n":"2007","v":"/year/2007"},{"n":"2006","v":"/year/2006"},{"n":"2005","v":"/year/2005"},{"n":"2004","v":"/year/2004"},{"n":"2003","v":"/year/2003"},{"n":"2002","v":"/year/2002"},{"n":"2001","v":"/year/2001"},{"n":"2000","v":"/year/2000"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"/lang/国语"},{"n":"英语","v":"/lang/英语"},{"n":"粤语","v":"/lang/粤语"},{"n":"西语","v":"/lang/西语"},{"n":"韩语","v":"/lang/韩语"},{"n":"日语","v":"/lang/日语"},{"n":"法语","v":"/lang/法语"},{"n":"俄语","v":"/lang/俄语"},{"n":"意大利语","v":"/lang/意大利语"},{"n":"德语","v":"/lang/德语"},{"n":"印地语","v":"/lang/印地语"},{"n":"其它","v":"/lang/其它"}]},{"key":"letter","name":"字母","value":[{"n":"全部","v":""},{"n":"A","v":"/letter/A"},{"n":"B","v":"/letter/B"},{"n":"C","v":"/letter/C"},{"n":"D","v":"/letter/D"},{"n":"E","v":"/letter/E"},{"n":"F","v":"/letter/F"},{"n":"G","v":"/letter/G"},{"n":"H","v":"/letter/H"},{"n":"I","v":"/letter/I"},{"n":"J","v":"/letter/J"},{"n":"K","v":"/letter/K"},{"n":"L","v":"/letter/L"},{"n":"M","v":"/letter/M"},{"n":"N","v":"/letter/N"},{"n":"O","v":"/letter/O"},{"n":"P","v":"/letter/P"},{"n":"Q","v":"/letter/Q"},{"n":"R","v":"/letter/R"},{"n":"S","v":"/letter/S"},{"n":"T","v":"/letter/T"},{"n":"U","v":"/letter/U"},{"n":"V","v":"/letter/V"},{"n":"W","v":"/letter/W"},{"n":"X","v":"/letter/X"},{"n":"Y","v":"/letter/Y"},{"n":"Z","v":"/letter/Z"},{"n":"0-9","v":"/letter/0-9"}]},{"key":"by","name":"排序","value":[{"n":"按最新","v":"/by/time"},{"n":"按添加","v":"/by/time_add"},{"n":"按最热","v":"/by/hits"},{"n":"按评分","v":"/by/score"}]}],
		"3":[{"key":"cateId","name":"分类","value":[{"n":"全部","v":"3"},{"n":"真人秀","v":"305"},{"n":"音乐","v":"302"},{"n":"搞笑","v":"304"},{"n":"家庭","v":"301"},{"n":"曲艺","v":"303"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"/area/大陆"},{"n":"香港","v":"/area/香港"},{"n":"台湾","v":"/area/台湾"},{"n":"美国","v":"/area/美国"},{"n":"韩国","v":"/area/韩国"},{"n":"日本","v":"/area/日本"},{"n":"印度","v":"/area/印度"},{"n":"英国","v":"/area/英国"},{"n":"法国","v":"/area/法国"},{"n":"加拿大","v":"/area/加拿大"},{"n":"西班牙","v":"/area/西班牙"},{"n":"俄罗斯","v":"/area/俄罗斯"},{"n":"意大利","v":"/area/意大利"},{"n":"泰国","v":"/area/泰国"},{"n":"新加坡","v":"/area/新加坡"},{"n":"马来西亚","v":"/area/马来西亚"},{"n":"其它","v":"/area/其它"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"2013","v":"/year/2013"},{"n":"2012","v":"/year/2012"},{"n":"2011","v":"/year/2011"},{"n":"2010","v":"/year/2010"},{"n":"2009","v":"/year/2009"},{"n":"2008","v":"/year/2008"},{"n":"2007","v":"/year/2007"},{"n":"2006","v":"/year/2006"},{"n":"2005","v":"/year/2005"},{"n":"2004","v":"/year/2004"},{"n":"2003","v":"/year/2003"},{"n":"2002","v":"/year/2002"},{"n":"2001","v":"/year/2001"},{"n":"2000","v":"/year/2000"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"/lang/国语"},{"n":"英语","v":"/lang/英语"},{"n":"粤语","v":"/lang/粤语"},{"n":"西语","v":"/lang/西语"},{"n":"韩语","v":"/lang/韩语"},{"n":"日语","v":"/lang/日语"},{"n":"法语","v":"/lang/法语"},{"n":"俄语","v":"/lang/俄语"},{"n":"意大利语","v":"/lang/意大利语"},{"n":"德语","v":"/lang/德语"},{"n":"印地语","v":"/lang/印地语"},{"n":"其它","v":"/lang/其它"}]},{"key":"letter","name":"字母","value":[{"n":"全部","v":""},{"n":"A","v":"/letter/A"},{"n":"B","v":"/letter/B"},{"n":"C","v":"/letter/C"},{"n":"D","v":"/letter/D"},{"n":"E","v":"/letter/E"},{"n":"F","v":"/letter/F"},{"n":"G","v":"/letter/G"},{"n":"H","v":"/letter/H"},{"n":"I","v":"/letter/I"},{"n":"J","v":"/letter/J"},{"n":"K","v":"/letter/K"},{"n":"L","v":"/letter/L"},{"n":"M","v":"/letter/M"},{"n":"N","v":"/letter/N"},{"n":"O","v":"/letter/O"},{"n":"P","v":"/letter/P"},{"n":"Q","v":"/letter/Q"},{"n":"R","v":"/letter/R"},{"n":"S","v":"/letter/S"},{"n":"T","v":"/letter/T"},{"n":"U","v":"/letter/U"},{"n":"V","v":"/letter/V"},{"n":"W","v":"/letter/W"},{"n":"X","v":"/letter/X"},{"n":"Y","v":"/letter/Y"},{"n":"Z","v":"/letter/Z"},{"n":"0-9","v":"/letter/0-9"}]},{"key":"by","name":"排序","value":[{"n":"按最新","v":"/by/time"},{"n":"按添加","v":"/by/time_add"},{"n":"按最热","v":"/by/hits"},{"n":"按评分","v":"/by/score"}]}],
		"4":[{"key":"cateId","name":"分类","value":[{"n":"全部","v":"4"},{"n":"日本","v":"401"},{"n":"国产","v":"402"},{"n":"欧美","v":"403"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"/area/大陆"},{"n":"香港","v":"/area/香港"},{"n":"台湾","v":"/area/台湾"},{"n":"美国","v":"/area/美国"},{"n":"韩国","v":"/area/韩国"},{"n":"日本","v":"/area/日本"},{"n":"印度","v":"/area/印度"},{"n":"英国","v":"/area/英国"},{"n":"法国","v":"/area/法国"},{"n":"加拿大","v":"/area/加拿大"},{"n":"西班牙","v":"/area/西班牙"},{"n":"俄罗斯","v":"/area/俄罗斯"},{"n":"意大利","v":"/area/意大利"},{"n":"泰国","v":"/area/泰国"},{"n":"新加坡","v":"/area/新加坡"},{"n":"马来西亚","v":"/area/马来西亚"},{"n":"其它","v":"/area/其它"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"2013","v":"/year/2013"},{"n":"2012","v":"/year/2012"},{"n":"2011","v":"/year/2011"},{"n":"2010","v":"/year/2010"},{"n":"2009","v":"/year/2009"},{"n":"2008","v":"/year/2008"},{"n":"2007","v":"/year/2007"},{"n":"2006","v":"/year/2006"},{"n":"2005","v":"/year/2005"},{"n":"2004","v":"/year/2004"},{"n":"2003","v":"/year/2003"},{"n":"2002","v":"/year/2002"},{"n":"2001","v":"/year/2001"},{"n":"2000","v":"/year/2000"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"/lang/国语"},{"n":"英语","v":"/lang/英语"},{"n":"粤语","v":"/lang/粤语"},{"n":"西语","v":"/lang/西语"},{"n":"韩语","v":"/lang/韩语"},{"n":"日语","v":"/lang/日语"},{"n":"法语","v":"/lang/法语"},{"n":"俄语","v":"/lang/俄语"},{"n":"意大利语","v":"/lang/意大利语"},{"n":"德语","v":"/lang/德语"},{"n":"印地语","v":"/lang/印地语"},{"n":"其它","v":"/lang/其它"}]},{"key":"letter","name":"字母","value":[{"n":"全部","v":""},{"n":"A","v":"/letter/A"},{"n":"B","v":"/letter/B"},{"n":"C","v":"/letter/C"},{"n":"D","v":"/letter/D"},{"n":"E","v":"/letter/E"},{"n":"F","v":"/letter/F"},{"n":"G","v":"/letter/G"},{"n":"H","v":"/letter/H"},{"n":"I","v":"/letter/I"},{"n":"J","v":"/letter/J"},{"n":"K","v":"/letter/K"},{"n":"L","v":"/letter/L"},{"n":"M","v":"/letter/M"},{"n":"N","v":"/letter/N"},{"n":"O","v":"/letter/O"},{"n":"P","v":"/letter/P"},{"n":"Q","v":"/letter/Q"},{"n":"R","v":"/letter/R"},{"n":"S","v":"/letter/S"},{"n":"T","v":"/letter/T"},{"n":"U","v":"/letter/U"},{"n":"V","v":"/letter/V"},{"n":"W","v":"/letter/W"},{"n":"X","v":"/letter/X"},{"n":"Y","v":"/letter/Y"},{"n":"Z","v":"/letter/Z"},{"n":"0-9","v":"/letter/0-9"}]},{"key":"by","name":"排序","value":[{"n":"按最新","v":"/by/time"},{"n":"按添加","v":"/by/time_add"},{"n":"按最热","v":"/by/hits"},{"n":"按评分","v":"/by/score"}]}]
	},
	filter_def:{
		1:{cateId:'1'},
		2:{cateId:'2'},
		3:{cateId:'3'},
		4:{cateId:'4'}
	},
	searchUrl:'/index.php/vod/search/page/fypage/wd/**.html',
	// searchable: 2,
	searchable: 0,
	quickSearch: 0,
	headers: {
		'User-Agent': 'MOBILE_UA',
	},
	timeout:5000,//网站的全局请求超时,默认是3000毫秒
	// class_parse:'.nav_list&&li;a--i&&Text;a&&href;.*/(\\d+).html',
	class_parse:'.top_nav&&li;a&&Text;a&&href;/(\\d+).html',
	cate_exclude:'午夜影院|电视直播|VIP蓝光影院',
	play_parse: true,
	lazy:`js:
		var html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
		var url = html.url;
		if (html.encrypt == "1") {
			url = unescape(url)
		} else if (html.encrypt == "2") {
			url = unescape(base64Decode(url))
		}
		if (/m3u8|mp4/.test(url)) {
			input = url
		} else {
			input
		}
	`,
	limit: 6,
	预处理:`
		let html = request(HOST);
		if (html.includes('_guard/auto.js')) {
			var _0x486ax7 = {
				"x": 616,
				"y": 288,
				"a": 904
			};
			let ghtml = request(HOST, {
				withHeaders: true
			});
			let json = JSON.parse(ghtml);
			let setCk = Object.keys(json).find(it => it.toLowerCase() === "set-cookie");
			let cookie = setCk ? json[setCk].split(";")[0] : "";
			var cook = "";
			function setRet(_0x486axd, _0x486ax7) {
				let jsf = request(HOST + "/_guard/encrypt.js");
				eval(jsf);
				var _0x486axe = _0x486axd["substr"](0, 8);
				var _0x486axf = cdn.MD5(_0x486axe);
				var _0x486ax10 = cdn["centos"]["encrypt"](JSON["stringify"](_0x486ax7), _0x486axf, {
					iv: _0x486axf
				});
				cook = "guardret=" + _0x486ax10.toString();
			}
			function t(_0x486ax7) {
				var co = cookie.split("guard=");
				var _0x486axd = co.pop().split(";").shift();
				if (!_0x486axd) {
					log("重载");
				} else {
					setRet(_0x486axd, _0x486ax7)
				}
			}
			t(_0x486ax7);
			rule_fetch_params.headers.Cookie = 'searchneed=ok; ' + cookie + '; ' + cook;
			setItem(RULE_CK, 'searchneed=ok; ' + cookie + '; ' + cook)
		};
	`,
	推荐:'.list_v12;li;*;*;.vodlist_top&&Text;*',
	double:true,//是否双层列表定位,默认false
	一级:'.vodlist li;a&&title;.lazyload&&data-original;.pic_text&&Text;a&&href',
	二级:{
		"title":".hd_tit&&Text;.data--span:eq(0)&&Text",
		"img":".lazyload&&data-original",
		"desc":".fn-left&&Text;;;.data--span:eq(2)&&Text;.data--span:eq(3)&&Text",
		"content":".context span&&Text",
		"tabs":".play_source_tab&&.active",
		"tab_text":"body--i&&Text",
		"lists":".content_playlist:eq(#id)&&li"
	},
	搜索:'*',
}