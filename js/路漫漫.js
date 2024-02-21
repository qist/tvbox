var rule = {
	title:'路漫漫',
	// host:'https://www.96ba.com',
	host:'https://www.wzwt369.com',
	// url:'/vod/show/id/fyclass/page/fypage.html',
	url:'/vod/show/id/fyclassfyfilter.html',
	filterable:1,//是否启用分类筛选,
	filter_url:'{{fl.by}}/page/fypage{{fl.year}}',
	filter:{
		"ribendongman":[{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"更早","v":"/year/2013-1980"}]},{"key":"by","name":"排序","value":[{"n":"更新","v":"/by/time"},{"n":"人气","v":"/by/hits"},{"n":"评分","v":"/by/score"},{"n":"点赞","v":"/by/up"}]}],
		"guochandongman":[{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"更早","v":"/year/2013-1980"}]},{"key":"by","name":"排序","value":[{"n":"更新","v":"/by/time"},{"n":"人气","v":"/by/hits"},{"n":"评分","v":"/by/score"},{"n":"点赞","v":"/by/up"}]}],
		"oumeidongman":[{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"更早","v":"/year/2013-1980"}]},{"key":"by","name":"排序","value":[{"n":"更新","v":"/by/time"},{"n":"人气","v":"/by/hits"},{"n":"评分","v":"/by/score"},{"n":"点赞","v":"/by/up"}]}],
		"ribendonghuadianying":[{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"更早","v":"/year/2013-1980"}]},{"key":"by","name":"排序","value":[{"n":"更新","v":"/by/time"},{"n":"人气","v":"/by/hits"},{"n":"评分","v":"/by/score"},{"n":"点赞","v":"/by/up"}]}],
		"guochandonghuadianying":[{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"更早","v":"/year/2013-1980"}]},{"key":"by","name":"排序","value":[{"n":"更新","v":"/by/time"},{"n":"人气","v":"/by/hits"},{"n":"评分","v":"/by/score"},{"n":"点赞","v":"/by/up"}]}],
		"oumeidonghuadianying":[{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"更早","v":"/year/2013-1980"}]},{"key":"by","name":"排序","value":[{"n":"更新","v":"/by/time"},{"n":"人气","v":"/by/hits"},{"n":"评分","v":"/by/score"},{"n":"点赞","v":"/by/up"}]}]
	},
	searchUrl:'/vod/search/page/fypage/wd/**.html',
	searchable: 2,//是否启用全局搜索,
	quickSearch: 0,//是否启用快速搜索,
	headers: {
		'User-Agent': 'MOBILE_UA',
	},
	class_parse:'.container&&.tag.text-light;a&&Text;a&&href;.*/(.*?).html',
	play_parse: true,
	lazy:`js:
		var html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
		var url = html.url;
		var from = html.from;
		if (/m3u8/.test(url)) {
			input = url.split("&")[0]
		} else {
			input
		}
	`,
	limit: 6,
	推荐:'.owl-theme-jable .item;*;*;*;*',
	一级:'#mdym .col-6;h6&&Text;.lazyload&&data-src;.label&&Text;a&&href',
	二级:{
		"title":"h1&&Text;.video-info-aux&&Text",
		"img":".url_img&&src",
		"desc":".video-info-items--span:eq(3)&&Text;;;.video-info-actor:eq(1)&&Text;.video-info-actor:eq(0)&&Text",
		"content":".content-text&&Text",
		"tabs":".module-tab-content .tab-item",
		"lists":".scroll-content:eq(#id) a"
	},
	搜索:'*',
}