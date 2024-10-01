var rule={
	title:'妮可动漫',
	host:'http://www.nicotv.xyz',
	url:'/video/fyclass/fyfilter.html',
	filterable:1,//是否启用分类筛选,
	filter_url:'{{fl.class}}-{{fl.area}}-{{fl.year}}----{{fl.by}}-fypage',
	filter: {"type3":[{"key":"class","name":"类型","value":[{"n":"全部","v":""},{"n":"热血","v":"热血"},{"n":"恋爱","v":"恋爱"},{"n":"科幻","v":"科幻"},{"n":"奇幻","v":"奇幻"},{"n":"百合","v":"百合"},{"n":"后宫","v":"后宫"},{"n":"励志","v":"励志"},{"n":"搞笑","v":"搞笑"},{"n":"冒险","v":"冒险"},{"n":"校园","v":"校园"},{"n":"战斗","v":"战斗"},{"n":"机战","v":"机战"},{"n":"运动","v":"运动"},{"n":"战争","v":"战争"},{"n":"萝莉","v":"萝莉"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"日本","v":"日本"},{"n":"大陆","v":"大陆"},{"n":"欧美","v":"欧美"},{"n":"其他","v":"其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2010-2000","v":"20002010"},{"n":"90年代","v":"19901999"},{"n":"更早","v":"18001989"}]},{"key":"by","name":"排序","value":[{"n":"最新","v":"addtime"},{"n":"热播","v":"hits"},{"n":"评分","v":"gold"}]}]},
	filter_def:{
		type3:{by:'addtime'}
	},
	searchUrl:'/vod-search-wd-**-p-fypage.html',
	searchable:2,//是否启用全局搜索,
	headers:{//网站的请求头,完整支持所有的,常带ua和cookies
		'User-Agent': 'MOBILE_UA',
	},
	class_name:'全部',
	class_url:'type3',
	play_parse: true,
	lazy:'js:let src=jsp.pd(request(input),"#cms_player&&script&&src");let cms_player=JSON.parse(request(src).match(/cms_player = (.*?);document/)[1]);/360lifan/.test(cms_player.name)?input={jx:0,url:cms_player.url+"&time="+cms_player.time+"&auth_key="+cms_player.auth_key,parse:1,header:JSON.stringify({"user-agent":"Mozilla/5.0"})}:/url=/.test(cms_player.url)?input=cms_player.url.split("url=")[1]:input={jx:0,url:cms_player.jiexi+cms_player.url+"&time="+cms_player.time+"&auth_key="+cms_player.auth_key,parse:1,header:JSON.stringify({"user-agent":"Mozilla/5.0"})}',
	limit:6,
	推荐:'*',
	一级:'.list-unstyled li;h2&&Text;img&&data-original;.continu&&Text;a&&href',
	二级:{
		"title":".media-body a&&Text;.ff-text-right:eq(2)&&Text",
		"img":".media-left&&img&&data-original",
		"desc":".ff-score&&Text;.ff-text-right:eq(4)&&Text;.ff-text-right:eq(3)&&Text;.ff-text-right:eq(0)&&Text;.ff-text-right:eq(1)&&Text",
		"content":".vod-content&&Text",
		"tabs":".nav.nav-tabs li",
		"lists":".tab-pane:eq(#id) li"
	},
	搜索:'*',
}