// 搜索验证
var rule = {
    title:'B站影视',
    // host:'https://bzhanys.com',
    host:'https://bzhanyy.com',
    // url:'/index.php/vod/show/id/fyclass/page/fypage.html',
    url:'/index.php/vod/show/id/fyfilter.html',
    // url:'/api.php/xiao/vod?type=fyclass&page=fypage&limit=24',
    filterable:1,//是否启用分类筛选,
    filter_url:'{{fl.cateId}}{{fl.area}}{{fl.by or "/by/time"}}{{fl.class}}/page/fypage{{fl.year}}',
    filter:{
        "1":[{"key":"cateId","name":"类型","value":[{"n":"全部","v":"1"},{"n":"喜剧","v":"6"},{"n":"爱情","v":"7"},{"n":"恐怖","v":"8"},{"n":"科幻","v":"9"},{"n":"剧情","v":"10"},{"n":"战争","v":"11"},{"n":"犯罪","v":"12"},{"n":"武侠","v":"21"},{"n":"纪录","v":"20"},{"n":"理论片","v":"26"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"/area/大陆"},{"n":"香港","v":"/area/香港"},{"n":"台湾","v":"/area/台湾"},{"n":"美国","v":"/area/美国"},{"n":"法国","v":"/area/法国"},{"n":"英国","v":"/area/英国"},{"n":"日本","v":"/area/日本"},{"n":"韩国","v":"/area/韩国"},{"n":"德国","v":"/area/德国"},{"n":"泰国","v":"/area/泰国"},{"n":"印度","v":"/area/印度"},{"n":"意大利","v":"/area/意大利"},{"n":"西班牙","v":"/area/西班牙"},{"n":"加拿大","v":"/area/加拿大"},{"n":"其他","v":"/area/其他"}]},{"key":"year","name":"年代","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"2013","v":"/year/2013"},{"n":"2012","v":"/year/2012"},{"n":"2011","v":"/year/2011"},{"n":"2010","v":"/year/2010"},{"n":"2009","v":"/year/2009"},{"n":"2008","v":"/year/2008"},{"n":"2007","v":"/year/2007"},{"n":"2006","v":"/year/2006"},{"n":"2005","v":"/year/2005"},{"n":"2004","v":"/year/2004"},{"n":"2003","v":"/year/2003"},{"n":"2002","v":"/year/2002"},{"n":"2001","v":"/year/2001"},{"n":"2000","v":"/year/2000"}]},{"key":"by","name":"排序","value":[{"n":"按时间","v":"/by/time"},{"n":"按人气","v":"/by/hits"},{"n":"按评分","v":"/by/score"}]}],
        "2":[{"key":"cateId","name":"类型","value":[{"n":"全部","v":"2"},{"n":"国产剧","v":"13"},{"n":"港台剧","v":"14"},{"n":"日韩剧","v":"15"},{"n":"欧美剧","v":"16"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"内地","v":"/area/内地"},{"n":"韩国","v":"/area/韩国"},{"n":"香港","v":"/area/香港"},{"n":"台湾","v":"/area/台湾"},{"n":"日本","v":"/area/日本"},{"n":"美国","v":"/area/美国"},{"n":"泰国","v":"/area/泰国"},{"n":"英国","v":"/area/英国"},{"n":"新加坡","v":"/area/新加坡"},{"n":"其他","v":"/area/其他"}]},{"key":"year","name":"年代","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"2013","v":"/year/2013"},{"n":"2012","v":"/year/2012"},{"n":"2011","v":"/year/2011"},{"n":"2010","v":"/year/2010"},{"n":"2009","v":"/year/2009"},{"n":"2008","v":"/year/2008"},{"n":"2007","v":"/year/2007"},{"n":"2006","v":"/year/2006"},{"n":"2005","v":"/year/2005"},{"n":"2004","v":"/year/2004"},{"n":"2003","v":"/year/2003"},{"n":"2002","v":"/year/2002"},{"n":"2001","v":"/year/2001"},{"n":"2000","v":"/year/2000"}]},{"key":"by","name":"排序","value":[{"n":"按时间","v":"/by/time"},{"n":"按人气","v":"/by/hits"},{"n":"按评分","v":"/by/score"}]}],
        "3":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"选秀","v":"/class/选秀"},{"n":"情感","v":"/class/情感"},{"n":"访谈","v":"/class/访谈"},{"n":"播报","v":"/class/播报"},{"n":"旅游","v":"/class/旅游"},{"n":"音乐","v":"/class/音乐"},{"n":"美食","v":"/class/美食"},{"n":"纪实","v":"/class/纪实"},{"n":"曲艺","v":"/class/曲艺"},{"n":"生活","v":"/class/生活"},{"n":"游戏互动","v":"/class/游戏互动"},{"n":"财经","v":"/class/财经"},{"n":"求职","v":"/class/求职"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"内地","v":"/area/内地"},{"n":"港台","v":"/area/港台"},{"n":"日韩","v":"/area/日韩"},{"n":"欧美","v":"/area/欧美"}]},{"key":"year","name":"年代","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"2013","v":"/year/2013"},{"n":"2012","v":"/year/2012"},{"n":"2011","v":"/year/2011"},{"n":"2010","v":"/year/2010"},{"n":"2009","v":"/year/2009"},{"n":"2008","v":"/year/2008"},{"n":"2007","v":"/year/2007"},{"n":"2006","v":"/year/2006"},{"n":"2005","v":"/year/2005"},{"n":"2004","v":"/year/2004"},{"n":"2003","v":"/year/2003"},{"n":"2002","v":"/year/2002"},{"n":"2001","v":"/year/2001"},{"n":"2000","v":"/year/2000"}]},{"key":"by","name":"排序","value":[{"n":"按时间","v":"/by/time"},{"n":"按人气","v":"/by/hits"},{"n":"按评分","v":"/by/score"}]}],
        "4":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"情感","v":"/class/情感"},{"n":"科幻","v":"/class/科幻"},{"n":"热血","v":"/class/热血"},{"n":"推理","v":"/class/推理"},{"n":"搞笑","v":"/class/搞笑"},{"n":"冒险","v":"/class/冒险"},{"n":"萝莉","v":"/class/萝莉"},{"n":"校园","v":"/class/校园"},{"n":"动作","v":"/class/动作"},{"n":"机战","v":"/class/机战"},{"n":"运动","v":"/class/运动"},{"n":"战争","v":"/class/战争"},{"n":"少年","v":"/class/少年"},{"n":"少女","v":"/class/少女"},{"n":"社会","v":"/class/社会"},{"n":"原创","v":"/class/原创"},{"n":"亲子","v":"/class/亲子"},{"n":"益智","v":"/class/益智"},{"n":"励志","v":"/class/励志"},{"n":"其他","v":"/class/其他"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"国产","v":"/area/国产"},{"n":"日本","v":"/area/日本"},{"n":"欧美","v":"/area/欧美"},{"n":"其他","v":"/area/其他"}]},{"key":"year","name":"年代","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"2013","v":"/year/2013"},{"n":"2012","v":"/year/2012"},{"n":"2011","v":"/year/2011"},{"n":"2010","v":"/year/2010"},{"n":"2009","v":"/year/2009"},{"n":"2008","v":"/year/2008"},{"n":"2007","v":"/year/2007"},{"n":"2006","v":"/year/2006"},{"n":"2005","v":"/year/2005"},{"n":"2004","v":"/year/2004"},{"n":"2003","v":"/year/2003"},{"n":"2002","v":"/year/2002"},{"n":"2001","v":"/year/2001"},{"n":"2000","v":"/year/2000"}]},{"key":"by","name":"排序","value":[{"n":"按时间","v":"/by/time"},{"n":"按人气","v":"/by/hits"},{"n":"按评分","v":"/by/score"}]}]
    },
    filter_def:{
        1:{cateId:'1'},
        2:{cateId:'2'},
        3:{cateId:'3'},
        4:{cateId:'4'}
    },
    searchable:2,//是否启用全局搜索,
    quickSearch:0,//是否启用快速搜索,
    headers:{
        'User-Agent':'MOBILE_UA'
    },
    class_parse: '.fixed-nav&&.flex:lt(4);li&&Text;li&&data-id',
    play_parse:true,
    lazy:`js:
        var html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
        var url = html.url;
        if (html.encrypt == '1') {
            url = unescape(url)
        } else if (html.encrypt == '2') {
            url = unescape(base64Decode(url))
        }
        if (/\\.m3u8|\\.mp4/.test(url)) {
            input = {
                jx: 0,
                url: url,
                parse: 0
            }
        } else {
            input
        }
    `,
    limit:6,
    推荐:'*',
    // 推荐:'.movie-list-body&&.movie-list-item;.movie-title&&Text;.Lazy&&data-original;.movie-rating&&Text;a&&href',
    一级:'.movie-list-body&&.movie-list-item;.movie-title&&Text;.Lazy&&data-original;.movie-rating&&Text;a&&href',
    // 一级:'json:list;vod_name;vod_pic;vod_score;vod_id',
    二级访问前:'log(MY_URL);MY_URL=MY_URL.replace("/play/","/detail/").replace("/sid/1/nid/1","");log(MY_URL)',
    二级:{
        "title":"h1&&title;.scroll-content&&Text",
        "img":".poster&&img&&src",
        "desc":";;;.starLink&&Text;.cr3:eq(0)&&Text",
        "content":".detailsTxt--div&&Text",
        "tabs":".swiper-wrapper&&a",
        "lists":".content_playlist:eq(#id)&&li"
    },

    // searchUrl:'/index.php/vod/search/page/fypage/wd/**.html',
	searchUrl:'/index.php/ajax/suggest?mid=1&wd=**&limit=50',
	detailUrl:'/index.php/vod/detail/id/fyid.html',
    // 搜索:'.movie-list-body&&.vod-search-list;*;*;.getop&&Text;*',
	搜索:'json:list;name;pic;;id',
}