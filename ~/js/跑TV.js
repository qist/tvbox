var rule = {
    title:'跑TV',
    host:'https://paotv.net',
    // homeUrl:'/',
    url:'/show/fyclass/page/fypage.html',
    //searchUrl:'/search-**----------fypage---/',
    searchable:0,//是否启用全局搜索,
    quickSearch:0,//是否启用快速搜索,
    filterable:0,//是否启用分类筛选,
    headers:{//网站的请求头,完整支持所有的,常带ua和cookies
        'User-Agent':'MOBILE_UA',
        // "Cookie": "searchneed=ok"
    },
    //class_parse:'.nav-menu-items&&li;a&&title;a&&href;/(\\d+).html',
    class_name:'国产&亚洲&欧美&伦理&动漫',
    class_url:'1&2&3&21&22',
    play_parse:true,
    lazy:'',
    limit:6,
    //推荐:'a.module-poster-item.module-item;a&&title;img&&data-original;.module-item-note&&Text;a&&href',
    推荐:'.tab-list.active;.module-poster-item.module-item;.module-poster-item-title&&Text;img&&data-original;.module-item-note&&Text;a&&href',
    double:true, // 推荐内容是否双层定位
    一级:'.module-poster-item.module-item;a&&title;img&&data-original;.module-item-note&&Text;a&&href',
    二级:{"title":"h1&&Text;.module-info-tag-link:eq(2)&&Text","img":".module-item-pic&&img&&data-original","desc":".module-info-content&&.module-info-item:eq(-2)&&Text;.module-info-content&&.module-info-item:eq(-4)&&Text;.module-info-content&&.module-info-item:eq(5)&&Text;.module-info-content&&.module-info-item:eq(3)&&.module-info-item-content&&Text;.module-info-content&&.module-info-item:eq(1)&&.module-info-item-content&&Text","content":".module-info-introduction-content&&Text","tabs":".module-tab-items-box:eq(0)&&.module-tab-item","lists":".module-list:eq(#id)&&.module-play-list-content a"},
    //搜索:'.module-card-item.module-item;.module-card-item-title&&Text;img&&data-src;.module-item-note&&Text;a.play-btn-o&&href',
}
