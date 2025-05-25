muban.首图2.二级.desc = ';;;.stui-content__detail p:eq(1)&&Text;.stui-content__detail p:eq(2)&&Text';
//muban.首图2.二级.tabs = '.stui-pannel__head.bottom-line.active.clearfix h3';
muban.首图2.二级.tabs = 'ul.nav-tabs.active&&li';
var rule = {
	title:'真不卡',
	模板:'首图2',
	host:'http://www.hootop.com/',
	//发布地址 http://52kan.info/
//	hostJs:'print(HOST);let html=request(HOST,{headers:{"User-Agent":PC_UA}});let src=jsp.pdfh(html,"li:eq(0)&&a:eq(0)&&href");print(src);HOST=src',
	url:'/films/fyclass_fypage.html',
    class_name:'电影&剧集&综艺&动漫',
	class_url:'1&2&4&3',
	headers:{
    'User-Agent' : 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/537.36  (KHTML, like Gecko) Version/13.0 Mobile/15E148 Safari/537.36',
    'searchword' : '**',
    'Referer': 'http://www.hootop.com/search.php',
    'Origin': 'http://www.hootop.com',
               'Cookie':'__51cke__=; every_24h_tips=true; __tins__21745431={"sid": 1722093845023, "vd": 3, "expires": 1722095681560}; __51laig__=17',

    
  },
	//class_parse:'.stui-header__menu .dropdown li:gt(0):lt(5);a&&Text;a&&href;.*/(.*?).html',
	searchUrl:'/search.php',
}