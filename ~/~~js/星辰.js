muban.首图2.二级.desc = '.data:eq(0)&&Text;;;.data--span:eq(2)&&Text;.data--span:eq(1)&&Text';
muban.首图2.二级.tabs = '.stui-pannel__head h3';
var rule = {
    title:'星辰',
    模板:'首图2',
    host:'http://www.40yb.com',
    // url:'/fyclass/indexfypage.html[/fyclass/index.html]',
    url:'/fyfilter/indexfypage.html[/fyfilter/index.html]',
    filterable:1,//是否启用分类筛选,
    filter_url:'{{fl.cateId}}',
    filter:{
        "dianying":[{"key":"cateId","name":"分类","value":[{"n":"全部","v":"dianying"},{"n":"动作片","v":"dongzuopian"},{"n":"爱情片","v":"aiqingpian"},{"n":"科幻片","v":"kehuanpian"},{"n":"恐怖片","v":"kongbupian"},{"n":"喜剧片","v":"xijupian"},{"n":"剧情片","v":"juqingpian"}]}],
        "dianshiju":[{"key":"cateId","name":"分类","value":[{"n":"全部","v":"dianshiju"},{"n":"国产剧","v":"guochanju"},{"n":"港台剧","v":"tangtaiju"},{"n":"欧美剧","v":"oumeiju"},{"n":"日韩剧","v":"rihanju"}]}]
    },
    filter_def:{
        dianying:{cateId:'dianying'},
        dianshiju:{cateId:'dianshiju'},
        zongyi:{cateId:'zongyi'},
        dongman:{cateId:'dongman'}
    },
    // searchUrl:'/search.php?page=fypage&searchword=**&searchtype=',
    searchUrl:'/search.php#searchword=**;post',
    class_parse:'.stui-header__menu li:gt(0):lt(7);a&&Text;a&&href;.*/(.*?)/.*html',
}