var rule = {
    title:'爱车MV',
    host:'https://www.ichemv.com',
    homeUrl:'/mv/',
    url:'/mv/fyclass_fypage.html',
    searchUrl:'/search.php?key=**&pages=fypage',
    searchable:2,
    quickSearch:0,
    class_parse:'.lei_fl&&li;a&&Text;a&&href;.*/(\\d+)_1.html',
    headers:{
        'User-Agent':'MOBILE_UA'
    },
    timeout:5000,
    play_parse:true,
    lazy:'',
    limit:6,
    double:false,
    图片来源:'@Referer=https://www.ichemv.com/',
    推荐:'*',
    一级: '.mv_list&&li;a&&title;img&&data-src;;a&&href',
    二级:'*',
    搜索:'.sp_list&&li;a&&title;img&&data-src;.singer&&Text;a&&href;.hits&&Text',
}
