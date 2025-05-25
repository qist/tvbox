var rule = {
	title:'啦啦DJ',
	host:'http://www.laladj.com',
	// url: '/dance/id-fyclass-fypage.html',
	url: '/fyclass-0-0-fypage',
	searchUrl: '/search?search=**&page=fypage',
	searchable:2,
	quickSearch:0,
	headers:{
		'User-Agent': 'PC_UA'
	},
	timeout:5000,//网站的全局请求超时,默认是3000毫秒
	class_parse:'.navbar&&.xcls0;a&&Text;a&&href;com/(.*)',
	play_parse:true,
	lazy:'js:input=input.replace("www","m")',
	limit:6,
	推荐: '.center_fl&&.recommended-list;li;img&&alt;img&&src;.index-music-hit--b&&Text;a&&href',
	double: true, // 推荐内容是否双层定位
	一级:'.list_musiclist&&.sbg;.t1&&Text;img&&src;.sc_2:eq(0)&&Text;a&&href',
	二级: "*",
	搜索: "*",
}