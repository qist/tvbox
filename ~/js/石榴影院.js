var rule={
    title:'石榴电影',
    //host:'https://hei19.com',
    host:'https://hei17.com',
    // url:'/catalog?column=fyclass&sort=1&per_page=72&page=fypage',
    url: '/catalog?column=fyclassfyfilter&per_page=72&page=fypage&sort=1',
 //   https://hei17.com/catalog?column=2&type=8&area=1&year=52&sort=1
    filterable:1,//是否启用分类筛选,
    filter_url:'&{{fl.class}}&{{fl.area}}&{{fl.year}}',
    filter: {
        "1":[{"key":"class","name":"类型","value":[{"n":"全部","v":""},{"n":"剧情","v":"type=1"},{"n":"惊悚","v":"type=2"},{"n":"动作","v":"type=5"},{"n":"科幻","v":"type=9"},{"n":"奇幻","v":"type=11"},{"n":"爱情","v":"type=24"},{"n":"喜剧","v":"type=26"},{"n":"冒险","v":"type=27"},{"n":"犯罪","v":"type=28"},{"n":"战争","v":"type=29"},{"n":"动画","v":"type=34"},{"n":"同性","v":"type=44"},{"n":"历史","v":"type=45"},{"n":"恐怖","v":"type=47"},{"n":"悬疑","v":"type=48"},{"n":"传记","v":"type=49"},{"n":"纪录片","v":"type=53"},{"n":"古装","v":"type=57"},{"n":"家庭","v":"type=58"},{"n":"古装","v":"type=57"},{"n":"伦理","v":"type=85"}]},{"key":"area","name":"地区","value":[{"n":"不限","v":""},{"n":"中国大陆","v":"area=1"},{"n":"中国香港","v":"area=3"},{"n":"美国","v":"area=6"},{"n":"韩国","v":"area=9"},{"n":"日本","v":"area=10"},{"n":"印度","v":"area=11"},{"n":"英国","v":"area=12"},{"n":"法国","v":"area=13"},{"n":"俄罗斯","v":"area=16"},{"n":"丹麦","v":"area=22"},{"n":"澳大利亚","v":"area=23"},{"n":"德国","v":"area=24"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"year=50"},{"n":"2022","v":"year=51"},{"n":"2021","v":"year=52"},{"n":"2020","v":"year=53"},{"n":"2019","v":"year=54"},{"n":"2018","v":"year=55"},{"n":"2017","v":"year=56"},{"n":"2016","v":"year=57"},{"n":"2015","v":"year=58"},{"n":"2014","v":"year=59"},{"n":"2013","v":"year=60"},{"n":"2012","v":"year=61"},{"n":"2011","v":"year=62"}]}],
        "2":[{"key":"class","name":"类型","value":[{"n":"全部","v":""},{"n":"爱情","v":"type=7"},{"n":"喜剧","v":"type=8"},{"n":"犯罪","v":"type=10"},{"n":"奇幻","v":"type=15"},{"n":"悬疑","v":"type=17"},{"n":"剧情","v":"type=18"},{"n":"科幻","v":"type=21"},{"n":"恐怖","v":"type=22"},{"n":"惊悚","v":"type=23"},{"n":"历史","v":"type=25"},{"n":"动作","v":"type=31"},{"n":"同性","v":"type=32"},{"n":"战争","v":"type=35"},{"n":"传记","v":"type=38"},{"n":"运动","v":"type=42"},{"n":"音乐","v":"type=43"},{"n":"冒险","v":"type=50"},{"n":"纪录片","v":"type=52"},{"n":"家庭","v":"type=59"},{"n":"古装","v":"type=76"}]},{"key":"area","name":"地区","value":[{"n":"不限","v":""},{"n":"中国大陆","v":"area=1"},{"n":"中国台湾","v":"area=2"},{"n":"中国香港","v":"area=3"},{"n":"美国","v":"area=6"},{"n":"韩国","v":"area=9"},{"n":"日本","v":"area=10"},{"n":"英国","v":"area=12"},{"n":"法国","v":"area=13"},{"n":"乌克兰","v":"area=17"},{"n":"西班牙","v":"area=18"},{"n":"泰国","v":"area=25"},{"n":"加拿大","v":"area=32"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"year=50"},{"n":"2022","v":"year=51"},{"n":"2021","v":"year=52"},{"n":"2020","v":"year=53"},{"n":"2019","v":"year=54"},{"n":"2018","v":"year=55"},{"n":"2017","v":"year=56"},{"n":"2016","v":"year=57"},{"n":"2015","v":"year=58"},{"n":"2014","v":"year=59"},{"n":"2013","v":"year=60"},{"n":"2012","v":"year=61"},{"n":"2011","v":"year=62"}]}],
        "3":[{"key":"class","name":"类型","value":[{"n":"全部","v":""},{"n":"选秀","v":"type=12"},{"n":"情感","v":"type=61"},{"n":"美食","v":"type=62"},{"n":"音乐","v":"type=63"},{"n":"真人秀","v":"type=77"},{"n":"喜剧","v":"type=79"},{"n":"奇幻","v":"type=80"},{"n":"冒险","v":"type=81"},{"n":"脱口秀","v":"type=82"},{"n":"爱情","v":"type=83"},{"n":"家庭","v":"type=84"},{"n":"歌舞","v":"type=88"}]},{"key":"area","name":"地区","value":[{"n":"不限","v":""},{"n":"中国大陆","v":"area=1"},{"n":"中国台湾","v":"area=2"},{"n":"美国","v":"area=6"},{"n":"韩国","v":"area=9"},{"n":"日本","v":"area=10"},{"n":"西班牙","v":"area=18"},{"n":"巴西","v":"area=20"},{"n":"德国","v":"area=24"},{"n":"墨西哥","v":"area=29"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"year=50"},{"n":"2022","v":"year=51"},{"n":"2021","v":"year=52"},{"n":"2020","v":"year=53"},{"n":"2019","v":"year=54"},{"n":"2018","v":"year=55"},{"n":"2017","v":"year=56"},{"n":"2016","v":"year=57"},{"n":"2015","v":"year=58"},{"n":"2014","v":"year=59"},{"n":"2009","v":"year=32"},{"n":"2008","v":"year=33"},{"n":"2007","v":"year=34"}]}],
        "4":[{"key":"class","name":"类型","value":[{"n":"全部","v":""},{"n":"国漫","v":"type=13"},{"n":"日漫","v":"type=60"},{"n":"美漫","v":"type=65"},{"n":"动画","v":"type=66"},{"n":"奇幻","v":"type=67"},{"n":"冒险","v":"type=68"},{"n":"喜剧","v":"type=69"},{"n":"动作","v":"type=70"},{"n":"剧情","v":"type=71"},{"n":"古装","v":"type=72"},{"n":"同性","v":"type=73"},{"n":"武侠","v":"type=84"},{"n":"爱情","v":"type=75"},{"n":"惊悚","v":"type=92"}]},{"key":"area","name":"地区","value":[{"n":"不限","v":""},{"n":"中国大陆","v":"area=1"},{"n":"美国","v":"area=6"},{"n":"日本","v":"area=10"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"year=50"},{"n":"2022","v":"year=51"},{"n":"2021","v":"year=52"},{"n":"2020","v":"year=53"},{"n":"2019","v":"year=54"},{"n":"2018","v":"year=55"},{"n":"2017","v":"year=56"},{"n":"2016","v":"year=57"},{"n":"2015","v":"year=58"},{"n":"2014","v":"year=59"},{"n":"2013","v":"year=60"},{"n":"2012","v":"year=61"},{"n":"2011","v":"year=62"}]}]
    },
    class_name:'电影&连续剧&综艺&动漫',
    class_url:'1&2&3&4',
    searchUrl:'/search?type=1&keywords=**&page=fypage',
    searchable:2,//是否启用全局搜索,
    quickSearch:0,//是否启用快速搜索,
    headers:{//网站的请求头,完整支持所有的,常带ua和cookies
        'User-Agent':'Dalvik/2.1.0 (Linux; U; Android 6.0; NEM-AL10 Build/HONORNEM-AL10) iPhone/8.0',
        'Cookie':'_ga=GA1.1.514069628.1721637839; _ga_KE8Y66ZM58=GS1.1.1721637839.1.1.1721639171.0.0.0'
        // "Cookie": "searchneed=ok"
    },
//    class_parse:'.nav li;a&&Text;a&&href;./(\\d+)',
    play_parse:true,
    play_json:[{re:'*', json:{jx:0, parse:0}}],
//    lazy:'',
    lazy:'js:let ep=input.match(/ep=(\\d+)/)[1];let html=request(input);let jsonA=jsp.pdfh(html,"#__NEXT_DATA__&&Html");let data=JSON.parse(jsonA).props.pageProps.videoDetail.videoepisode.data;let realUrl=data.filter(function(it){return it.episode==ep})[0].url;input=realUrl;',
    limit:6,
    // double:true, // 推荐内容是否双层定位
    推荐:'.media-list-1 li;a&&title;img&&src;.tag&&Text;a&&href',
 //  推荐:'js:let d=[];let html=request(input);let jsonA=JSON.parse(html.match(/__NEXT_DATA__.*?({.*})/)[1]);print(jsonA);jsonA=jsonA.props.pageProps.rankSectionData;jsonA.forEach(function(it){d.push({title:it.name,img:it.cover,url:"https://hei17.com/detail/"+it.id,desc:it.tag})});setResult(d);',
     一级:'.media-list-2 li;a&&title;img&&src;.tag&&Text;a&&href',
  //  一级:'js:let d=[];let html=request(input);let jsonA=JSON.parse(html.match(/__NEXT_DATA__.*?({.*})/)[1]);print(jsonA);jsonA=jsonA.props.pageProps.mediaData.data;jsonA.forEach(function(it){d.push({title:it.name,img:it.cover,url:"https://hei17.com/detail/"+it.id,desc:it.tag})});setResult(d);',
    二级:{
        "title":".video-name&&Text;.video-desc-item div:lt(3)&&Text",
        "img":"img&&src",
        "desc":";;;.video-desc-starring&&Text;.video-desc-director&&Text",
        "content":".video-desc-single&&Text",
        "tabs":".play-box-mobile h2",
        "lists":".play-list:eq(#id) li"
    },
    // 搜索:'.hl-list-wrap&&ul&&li;.hl-item-thumb&&title;.hl-lazy&&data-original;.hl-pic-text&&Text;a&&href',
    搜索:'js:let d=[];let html=request(input);let jsonA=JSON.parse(html.match(/__NEXT_DATA__.*?({.*})/)[1]);print(jsonA);jsonA=jsonA.props.pageProps.searchMovieList.data;jsonA.forEach(function(it){d.push({title:it.name,img:it.pic,url:"https://hei17.com/detail/"+it.id,desc:it.resolution})});setResult(d);',
}