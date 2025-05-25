var rule = {
	title:'JangoIndex',
	// host:'https://jango-index.ml',
	host:'https://jango-index.tk',
	url: 'fyclass',
	searchUrl: '/?search=**',
	searchable:2,
	quickSearch:0,
	filterable:0,
	headers:{
		'User-Agent': 'MOBILE_UA'
	},
	timeout:5000,//网站的全局请求超时,默认是3000毫秒
    class_name:'网站限制，只显示最新前百首歌曲，可利用搜索获取其他歌曲',//静态分类名称拼接
    class_url:'/',
	play_parse:true,
	pagecount:{"/":1},
	lazy:'',
	limit:6,
	推荐: '*',
	// 一级:'js:pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;var d=[];var html=request(input);var list=pdfa(html,"body&&table:gt(1)");list.forEach(function(it){d.push({title:pdfh(it,"audio&&title").split(" -")[0],desc:"🎤"+pdfh(it,"img&&title"),img:pd(it,"img&&data-src"),url:pd(it,"a&&href")})});setResult(d);',
	一级: 'body&&table:gt(1);audio&&title;img&&data-src;img&&title;a&&href',
	二级: '*',
	搜索: '*',
}