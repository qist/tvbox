// 原"幻听网听书"网站 已更名为 "58动漫"

// muban.首图2.二级.title = 'h1--span&&title;.data--span:eq(0)&&Text';
// muban.首图2.二级.desc = '.data--span:eq(3)&&Text;;;.data--span:eq(1)&&Text;.data--span:eq(2)&&Text';
// muban.首图2.二级.content = '.detail-content&&Text';
// muban.首图2.二级.tabs = '.stui-pannel__head.bottom-line&&h3';
muban.vfed.二级.title = 'h1&&Text;.fed-col-md3:eq(0)&&Text';
muban.vfed.二级.desc = '.fed-col-md3:eq(3)&&Text;;;.fed-col-md6--span:eq(0)&&Text;.fed-col-md6--span:eq(1)&&Text';
muban.vfed.二级.tabs = '.nav-tabs&&li';
muban.vfed.二级.lists = '.myui-content__list:eq(#id)&&li';
var rule = {
    // title:'幻听网听书',
    title:'58动漫',
    // 模板:'首图2',
    模板:'vfed',
    host:'http://www.ting38.com',
    // url:'/ting/fyclass-fypage.html',
    url:'/search.php?page=fypage&searchtype=5&tid=fyclassfyfilter',
	filterable:1,//是否启用分类筛选,
    filter_url:'&order={{fl.by}}&area={{fl.area}}&year={{fl.year}}',
    filter:{
        "1":[{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"more","v":"more"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hit"},{"n":"推荐","v":"commend"}]}],
        "2":[{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"more","v":"more"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hit"},{"n":"推荐","v":"commend"}]}],
        "3":[{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"more","v":"more"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hit"},{"n":"推荐","v":"commend"}]}],
        "4":[{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"🇨🇳中国","v":"大陆"},{"n":"🇭🇰香港","v":"香港"},{"n":"🇹🇼台湾","v":"台湾"},{"n":"🇯🇵日本","v":"日本"},{"n":"🇰🇷韩国","v":"韩国"},{"n":"欧美","v":"欧美"},{"n":"泰国","v":"泰国"},{"n":"其他","v":"其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"more","v":"more"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hit"},{"n":"推荐","v":"commend"}]}]
    },
	filter_def:{
		1:{cateId:'1'},
		2:{cateId:'2'},
		3:{cateId:'3'},
		4:{cateId:'4'}
	},
    searchUrl:'/search.php?page=fypage&searchword=**&searchtype=',
    // class_parse: '.stui-header__menu li:gt(0);a&&Text;a&&href;.*/(.*?).html',
    // class_parse: '.fed-pops-navbar&&ul.fed-part-rows&&a;a&&Text;a&&href;.*/(.*?).html',
    // cate_exclude:'导航',
    // 搜索:'.stui-vodlist__media:eq(0) li;a&&title;.lazyload&&data-original;p:eq(0)&&Text;a&&href;.pic-text&&Text',
    搜索: '.fed-list-item;a&&title;a&&data-original;.fed-list-remarks&&Text;a&&href',
}