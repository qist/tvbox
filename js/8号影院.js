muban.首图2.二级.desc = ';;;.data--span:eq(0)&&Text;.data--span:eq(1)&&Text';
muban.首图2.二级.tabs = '.stui-pannel__head h3';
var rule={
	title:'8号影院',
	模板:'首图2',
	//host:'http://www.8hysw.com',
	host:'http://www.bahaoyy.com',
	// url:'/frim/fyclass-fypage.html',
	url:'/frim/fyfilter.html',
	filterable:1,//是否启用分类筛选,
	filter_url:'{{fl.cateId}}-fypage',
	filter: {"1":[{"key":"cateId","name":"分类","value":[{"n":"全部","v":"1"},{"n":"动作","v":"5"},{"n":"爱情","v":"6"},{"n":"科幻","v":"7"},{"n":"恐怖","v":"8"},{"n":"喜剧","v":"10"},{"n":"剧情","v":"12"},{"n":"在线直播","v":"28"}]}],"2":[{"key":"cateId","name":"分类","value":[{"n":"全部","v":"2"},{"n":"国产剧","v":"13"},{"n":"港台剧","v":"14"},{"n":"欧美剧","v":"15"},{"n":"日韩剧","v":"16"}]}]},
	filter_def:{
		1:{cateId:'1'},
		2:{cateId:'2'},
		3:{cateId:'3'},
		4:{cateId:'4'}
	},
	searchUrl:'/search.php?page=fypage&searchword=**&searchtype=',
	class_parse: '.stui-header__menu li:gt(0):lt(5);a&&Text;a&&href;.*/(.*?).html',
	搜索:muban.首图2.搜索2,
}