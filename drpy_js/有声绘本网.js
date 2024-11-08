var rule = {
	title:'有声绘本网',
	host:'https://www.youshenghuiben.com',
	url: '/fyclass/fypage',
	searchUrl: '/search.php?&q=**&page=fypage',
	searchable:2,
	quickSearch:0,
	filterable:0,
	headers:{
		'User-Agent': 'MOBILE_UA'
	},
	timeout:5000,//网站的全局请求超时,默认是3000毫秒
	class_parse:'#menu-main&&li:gt(0):lt(7);a&&Text;a&&href;com/(\\w+)',
	play_parse:true,
	limit:6,
	推荐: '*',
	一级: 'article.excerpt-c5;a&&title;img&&src;.post-like&&Text;a&&href',
	二级:'*',
	搜索: 'article.excerpt-tw;*;*;time&&Text;*',
}