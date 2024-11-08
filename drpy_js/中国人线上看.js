var rule = {
	title: '中国人线上看',
	host: 'https://chinaqtv.co',
	url: '/vodtype/fyclass.html',
	//https://chinaqtv.co/vodsearch/.html?wd=4
	searchUrl: '/vodsearch/.html?wd=**',
	searchable: 2,//是否启用全局搜索,
	quickSearch: 0,//是否启用快速搜索,
	filterable: 0,//是否启用分类筛选,
	headers: { 'User-Agent': 'MOBILE_UA' },
	class_parse: '.menu-list&&li:gt(0);a&&Text;a&&href;/(\\d+).html',
	play_parse: true,
	pagecount: {"13":1,"14":1,"15":1,"20":1,"21":1,"22":1,"3":1},
	lazy: '',
	limit: 6,
	推荐: 'body&&.content;div.drama;*;*;*;*',
	double: true,
	一级: '.content&&div.drama;.title&&Text;.imgcover&&style;p&&Text;a&&href',
	二级: {
		"title": ".title&&Text",
		"content": "pre&&Text",
		"tabs": "div.title:contains(片源)",
		"tab_text": "body&&Text",
		"lists": "div.episode.sizing&&ul:eq(#id) li"
	},
}