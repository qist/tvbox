var rule={
    title:'异世界动漫',
    host:'https://www.lldm.net',
    homeUrl:'/index.php/vod/show/id/22.html',
    // url:'/index.php/vod/show/class/fyclass/id/20/page/fypage.html',
    url:'/index.php/vod/show/fyclassfyfilter.html',
    filterable:1,
    filter_url:'{{fl.type}}/id/20/page/fypage{{fl.year}}',
    filter: {
        "area/日本":[{"key":"type","name":"类型","value":[{"n":"全部","v":""},{"n":"OVA","v":"/class/OVA"},{"n":"剧场版","v":"/class/剧场版"},{"n":"无修","v":"/class/BD无修"},{"n":"萝莉","v":"/class/萝莉"},{"n":"学園","v":"/class/学園"},{"n":"后宫","v":"/class/后宫"},{"n":"恋爱","v":"/class/恋爱"},{"n":"热血","v":"/class/热血"},{"n":"神魔","v":"/class/神魔"},{"n":"奇幻","v":"/class/奇幻"},{"n":"治愈","v":"/class/治愈"},{"n":"搞笑","v":"/class/搞笑"},{"n":"百合","v":"/class/百合"},{"n":"冒险","v":"/class/冒险"},{"n":"魔法","v":"/class/魔法"},{"n":"机战","v":"/class/机战"},{"n":"战争","v":"/class/战争"},{"n":"犯罪","v":"/class/犯罪"},{"n":"悬疑","v":"/class/悬疑"},{"n":"推理","v":"/class/推理"},{"n":"科幻","v":"/class/科幻"},{"n":"竞技","v":"/class/竞技"},{"n":"运动","v":"/class/运动"},{"n":"耽美","v":"/class/耽美"},{"n":"其他","v":"/class/其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"2013","v":"/year/2013"},{"n":"2012","v":"/year/2012"},{"n":"2011","v":"/year/2011"},{"n":"2010","v":"/year/2010"},{"n":"2009","v":"/year/2009"},{"n":"2008","v":"/year/2008"}]}],
        "area/中國":[{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"2013","v":"/year/2013"},{"n":"2012","v":"/year/2012"},{"n":"2011","v":"/year/2011"},{"n":"2010","v":"/year/2010"},{"n":"2009","v":"/year/2009"},{"n":"2008","v":"/year/2008"}]}]
    },
    searchUrl:'/index.php/vod/search/page/fypage/wd/**.html',
    searchable:2,
    quickSearch:0,
    headers:{
        'User-Agent':'MOBILE_UA'
    },
    timeout:5000,//网站的全局请求超时,默认是3000毫秒
    class_name:'日漫&国漫',
    class_url:'area/日本&area/中國',
    play_parse:true,
	lazy:`js:
        var html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
        var url = html.url;
        var from = html.from;
        if (html.encrypt == '1') {
            url = unescape(url)
        } else if (html.encrypt == '2') {
            url = unescape(base64Decode(url))
        }
        if (/m3u8|mp4/.test(url)) {
            input = url
        } else {
            var MacPlayerConfig={};
            eval(fetch(HOST + "/static/js/playerconfig.js").replace('var Mac','Mac'));
            var jx = MacPlayerConfig.player_list[from].parse;
            if (jx == '') {
                jx = MacPlayerConfig.parse
            };
            if (jx.startsWith("/")) {
                jx = "https:" + jx;
            }
            input={
                jx:0,
                url:jx+url,
                parse:1,
                header: JSON.stringify({
                    'referer': HOST
                })
            }
        }
    `,
    limit:6,
    // 图片来源:'@Referer=https://api.douban.com/@User-Agent=Mozilla/5.0%20(Windows%20NT%2010.0;%20Win64;%20x64)%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/113.0.0.0%20Safari/537.36',
    推荐:'*',
    一级:'.vodlist_wi&&li;.lazyload&&title;.lazyload&&data-original;.pic_text&&Text;a&&href',
    二级:{
        "title": "h2&&Text;li.data--span:eq(0)&&Text",
        "img": ".lazyload&&data-original",
        "desc": "li.data--span:eq(1)&&Text;;;li.data--span:eq(2)&&Text;li.data--span:eq(3)&&Text",
        "content": ".full_text&&span&&Text",
        "tabs": `js:
            TABS = [];
            let tabs = pdfa(html, '#NumTab&&a');
            tabs.forEach((it) => {
                TABS.push(pdfh(it, 'a&&alt'))
            });
        `,
        // "lists": ".content_playlist:not(.list_scroll):eq(#id) a"
        "lists": "div.playlist_full:eq(#id) li"
    },
    搜索:'li.searchlist_item;*;*;*;*',
}