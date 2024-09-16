var rule={
    title:'快看',
    host:'https://www.kuaikanys.net',
    // homeUrl:'/',
    url:'/s/fyfilter/page/fypage.html',
	filterable:1,//是否启用分类筛选,
	filter_url:'{{fl.cateId}}',
	filter: {"dianying":[{"key":"cateId","name":"类型","value":[{"n":"全部","v":"dianying"},{"n":"动作片","v":"dongzuopian"},{"n":"喜剧片","v":"xijupian"},{"n":"爱情片","v":"aiqingpian"},{"n":"科幻片","v":"kehuanpian"},{"n":"言情片","v":"yanqingpian"},{"n":"恐怖片","v":"kongbupian"},{"n":"剧情片","v":"juqingpian"},{"n":"战争片","v":"zhanzhengpian"}]}],"lianxuju":[{"key":"cateId","name":"类型","value":[{"n":"全部","v":"lianxuju"},{"n":"国产剧","v":"guochanju"},{"n":"港台剧","v":"gangtaiju"},{"n":"日韩剧","v":"rihanju"},{"n":"欧美剧","v":"oumeiju"},{"n":"其他剧","v":"qitaju"}]}]},
	filter_def:{
		dianying:{cateId:'dianying'},
		lianxuju:{cateId:'lianxuju'},
		zongyi:{cateId:'zongyi'},
		dongman:{cateId:'dongman'}
	},
    searchUrl:'/vodsearch/-------------.html?wd=**&submit=',
    searchable:2,//是否启用全局搜索,
    quickSearch:0,//是否启用快速搜索,
    headers:{//网站的请求头,完整支持所有的,常带ua和cookies
        'User-Agent':'MOBILE_UA',
        // "Cookie": "searchneed=ok"
    },
    class_parse:'nav ul li;a&&Text;a&&href;.*/(.*?)\.html',
	cate_exclude:'专题',
    play_parse:true,
    lazy:'',
    limit:6,
    推荐:'.show:eq(1);ul&&li;*;*;*;*',
    double:true, // 推荐内容是否双层定位
    一级:'.show&&ul&&li;a&&title;img&&src;.score&&Text;a&&href',
    // 二级:{"title":"h1&&Text;.info&&ul&&p&&Text","img":"img&&src","desc":".info&&ul&&p:eq(-2)&&Text;.info&&ul&&p:eq(-1)&&Text;.info&&ul&&p:eq(0)&&Text;.info&&ul&&p:eq(1)&&Text;.info&&ul&&p:eq(2)&&Text;.info&&ul&&p:eq(3)&&Text","content":".text&&Text","tabs":".play&&span","lists":".playlist&&ul:eq(#id) li"},
    二级:{
	    "title":"h1&&Text;.info&&ul&&p&&Text",
	    "img":"img&&src",
	    "desc":";;;.info ul li:eq(0)&&Text;.info ul li:eq(1)&&Text;.info&&ul&&p:eq(3)&&Text",
	    // "content":".text p&&Text",
	    "content":".text&&Text",
	    "tabs":".play&&span",
	    "lists":".playlist&&ul:eq(#id) li"
	},
    搜索:'*',
    // 搜索:'*;*;*;*;*',
}
