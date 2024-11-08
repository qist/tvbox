var rule = {
    title:'乐鱼影视',
    // host:'https://www.leyupro.com',
    host:'https://www.yu992.com',
    // url:'/lys/fyclass/page/fypage.html',
    url: '/lys/fyclassfyfilter.html',
    filterable:1,//是否启用分类筛选,
    filter_url:'{{fl.area}}{{fl.by}}{{fl.class}}/page/fypage{{fl.year}}',
    filter:{
        "lyMovie":[{"key":"class","name":"类型","value":[{"n":"全部","v":""},{"n":"喜剧","v":"/class/喜剧"},{"n":"爱情","v":"/class/爱情"},{"n":"恐怖","v":"/class/恐怖"},{"n":"动作","v":"/class/动作"},{"n":"科幻","v":"/class/科幻"},{"n":"剧情","v":"/class/剧情"},{"n":"战争","v":"/class/战争"},{"n":"犯罪","v":"/class/犯罪"},{"n":"动画","v":"/class/动画"},{"n":"奇幻","v":"/class/奇幻"},{"n":"冒险","v":"/class/冒险"},{"n":"恐怖","v":"/class/恐怖"},{"n":"悬疑","v":"/class/悬疑"},{"n":"惊悚","v":"/class/惊悚"},{"n":"历史","v":"/class/历史"},{"n":"运动","v":"/class/运动"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"/area/大陆"},{"n":"香港","v":"/area/香港"},{"n":"台湾","v":"/area/台湾"},{"n":"美国","v":"/area/美国"},{"n":"法国","v":"/area/法国"},{"n":"英国","v":"/area/英国"},{"n":"日本","v":"/area/日本"},{"n":"韩国","v":"/area/韩国"},{"n":"德国","v":"/area/德国"},{"n":"泰国","v":"/area/泰国"},{"n":"印度","v":"/area/印度"},{"n":"意大利","v":"/area/意大利"},{"n":"西班牙","v":"/area/西班牙"},{"n":"加拿大","v":"/area/加拿大"},{"n":"其他","v":"/area/其他"}]},{"key":"year","name":"年代","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"2013","v":"/year/2013"},{"n":"2012","v":"/year/2012"},{"n":"2011","v":"/year/2011"},{"n":"2010","v":"/year/2010"}]},{"key":"by","name":"排序","value":[{"n":"按时间","v":"/by/time"},{"n":"按人气","v":"/by/hits"},{"n":"按评分","v":"/by/score"}]}],
        "lyTv":[{"key":"class","name":"类型","value":[{"n":"全部","v":""},{"n":"古装","v":"/class/古装"},{"n":"喜剧","v":"/class/喜剧"},{"n":"偶像","v":"/class/偶像"},{"n":"家庭","v":"/class/家庭"},{"n":"警匪","v":"/class/警匪"},{"n":"言情","v":"/class/言情"},{"n":"武侠","v":"/class/武侠"},{"n":"悬疑","v":"/class/悬疑"},{"n":"历史","v":"/class/历史"},{"n":"农村","v":"/class/农村"},{"n":"都市","v":"/class/都市"},{"n":"神话","v":"/class/神话"},{"n":"科幻","v":"/class/科幻"},{"n":"搞笑","v":"/class/搞笑"},{"n":"谍战","v":"/class/谍战"},{"n":"战争","v":"/class/战争"},{"n":"年代","v":"/class/年代"},{"n":"爱情","v":"/class/爱情"},{"n":"剧情","v":"/class/剧情"},{"n":"奇幻","v":"/class/奇幻"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"/area/大陆"},{"n":"韩国","v":"/area/韩国"},{"n":"香港","v":"/area/香港"},{"n":"台湾","v":"/area/台湾"},{"n":"日本","v":"/area/日本"},{"n":"美国","v":"/area/美国"},{"n":"泰国","v":"/area/泰国"},{"n":"英国","v":"/area/英国"},{"n":"新加坡","v":"/area/新加坡"},{"n":"其他","v":"/area/其他"}]},{"key":"year","name":"年代","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"2013","v":"/year/2013"},{"n":"2012","v":"/year/2012"},{"n":"2011","v":"/year/2011"},{"n":"2010","v":"/year/2010"}]},{"key":"by","name":"排序","value":[{"n":"按时间","v":"/by/time"},{"n":"按人气","v":"/by/hits"},{"n":"按评分","v":"/by/score"}]}],
        "lyCartoon":[{"key":"class","name":"类型","value":[{"n":"全部","v":""},{"n":"科幻","v":"/class/科幻"},{"n":"热血","v":"/class/热血"},{"n":"推理","v":"/class/推理"},{"n":"搞笑","v":"/class/搞笑"},{"n":"冒险","v":"/class/冒险"},{"n":"萝莉","v":"/class/萝莉"},{"n":"校园","v":"/class/校园"},{"n":"机战","v":"/class/机战"},{"n":"运动","v":"/class/运动"},{"n":"战争","v":"/class/战争"},{"n":"少女","v":"/class/少女"},{"n":"社会","v":"/class/社会"},{"n":"原创","v":"/class/原创"},{"n":"益智","v":"/class/益智"},{"n":"励志","v":"/class/励志"},{"n":"其他","v":"/class/其他"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"/area/大陆"},{"n":"韩国","v":"/area/韩国"},{"n":"日本","v":"/area/日本"},{"n":"美国","v":"/area/美国"},{"n":"其他","v":"/area/其他"}]},{"key":"year","name":"年代","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"2013","v":"/year/2013"},{"n":"2012","v":"/year/2012"},{"n":"2011","v":"/year/2011"},{"n":"2010","v":"/year/2010"}]},{"key":"by","name":"排序","value":[{"n":"按时间","v":"/by/time"},{"n":"按人气","v":"/by/hits"},{"n":"按评分","v":"/by/score"}]}],
        "lyVariety":[{"key":"class","name":"类型","value":[{"n":"全部","v":""},{"n":"音乐","v":"/class/音乐"},{"n":"真人","v":"/class/真人"},{"n":"访谈","v":"/class/访谈"},{"n":"播报","v":"/class/播报"},{"n":"旅游","v":"/class/旅游"},{"n":"美食","v":"/class/美食"},{"n":"纪实","v":"/class/纪实"},{"n":"生活","v":"/class/生活"},{"n":"游戏","v":"/class/游戏"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"/area/大陆"},{"n":"香港","v":"/area/香港"},{"n":"台湾","v":"/area/台湾"},{"n":"日本","v":"/area/日本"},{"n":"韩国","v":"/area/韩国"},{"n":"美国","v":"/area/美国"}]},{"key":"year","name":"年代","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"2013","v":"/year/2013"},{"n":"2012","v":"/year/2012"},{"n":"2011","v":"/year/2011"},{"n":"2010","v":"/year/2010"}]},{"key":"by","name":"排序","value":[{"n":"按时间","v":"/by/time"},{"n":"按人气","v":"/by/hits"},{"n":"按评分","v":"/by/score"}]}],
        "lydocumentary":[{"key":"class","name":"类型","value":[{"n":"全部","v":""},{"n":"社会","v":"/class/社会"},{"n":"动物","v":"/class/动物"},{"n":"文化","v":"/class/文化"},{"n":"自然","v":"/class/自然"},{"n":"人文","v":"/class/人文"},{"n":"军事","v":"/class/军事"},{"n":"历史","v":"/class/历史"},{"n":"记录","v":"/class/记录"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"/area/大陆"},{"n":"日本","v":"/area/日本"},{"n":"美国","v":"/area/美国"},{"n":"国外","v":"/area/国外"},{"n":"其他","v":"/area/其他"}]},{"key":"year","name":"年代","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"2013","v":"/year/2013"},{"n":"2012","v":"/year/2012"},{"n":"2011","v":"/year/2011"},{"n":"2010","v":"/year/2010"}]},{"key":"by","name":"排序","value":[{"n":"按时间","v":"/by/time"},{"n":"按人气","v":"/by/hits"},{"n":"按评分","v":"/by/score"}]}],
        "lyLive":[{"key":"class","name":"类型","value":[{"n":"全部","v":""},{"n":"体育","v":"/class/体育"},{"n":"电视","v":"/class/电视"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"/area/大陆"},{"n":"美国","v":"/area/美国"}]},{"key":"year","name":"年代","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"}]},{"key":"by","name":"排序","value":[{"n":"按时间","v":"/by/time"},{"n":"按人气","v":"/by/hits"},{"n":"按评分","v":"/by/score"}]}]
    },
    searchUrl:'/lyso/page/fypage/wd/**.html',
    searchable:2,//是否启用全局搜索,
    quickSearch:0,//是否启用快速搜索,
    headers:{
        'User-Agent':'MOBILE_UA'
    },
    class_name:'电影&电视剧&综艺&动漫&纪录片',
    class_url:'lyMovie&lyTv&lyVariety&lyCartoon&lydocumentary',
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
    一级:'.gcol;a&&title;.eclazy&&data-original;.packscore&&Text;a&&href',
    二级:{
        "title":"h1&&Text;.detailinfo&&p--span:eq(0)&&Text",
        "img":".detailpic&&img&&src",
        "desc":".detailinfo&&p:eq(7)&&Text;;;.detailinfo&&p--span:eq(2)&&Text;.detailinfo&&p--span:eq(1)&&Text",
        "content":".tjuqing&&Text",
        "tabs":".downtitle:eq(1)&&li",
        "lists":".videolist:eq(#id) a"
    },
    搜索:'.search;*;img&&src;.list&&span:eq(1)&&Text;*',
}