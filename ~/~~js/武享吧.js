var rule = {
	title:'武享吧',
	host:'https://www.hula8.net',
	url: '/fyclass/page/fypage',
	searchUrl: '/page/fypage/?s=**',
	searchable:2,
	quickSearch:0,
	headers:{
		'User-Agent': 'PC_UA',
		'Referer': 'https://www.hula8.net/',
		'Cookie':'esc_search_captcha=1;result=12'
	},
	timeout:5000,//网站的全局请求超时,默认是3000毫秒
	class_parse: '#menu-xinjian&&li;a&&Text;a&&href;net/(.*)',
	play_parse:true,
	cate_exclude:'首 页|赛事预告|美国格斗赛|亚洲格斗赛|其他格斗赛|日本搏击赛|裸拳赛',
	limit:6,
	推荐: 'div.apc-grid-item;*;*;.views&&Text;a&&href',
	一级: '.site-main&&article;img&&alt;img&&data-original;.grid-inf-l&&Text;a&&href',
	二级: {
		"title": "h1&&Text;.module-info-tag&&Text",
		"img": ".aligncenter&&data-original",
		"desc": ";;;.views:eq(0)&&Text;",
		"content": "h1&&Text",
		"tabs": "js:TABS=['道长在线']",
		"lists": `js:
			var html = JSON.parse(request(input).match(/var bevideo_vids_.*?=({[\\s\\S]*?});/)[1]);
			let list = [];
			list = html.m3u8dplayer.map(function(item) {
				return item.pre + "$" + item.video
			});
			LISTS = [list];
		`
	},
	搜索: '*;*;*;.entry-meta&&Text;*',
}