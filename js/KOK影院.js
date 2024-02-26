var rule = {
    title:'KOK影院',
    // host:'https://www.kokyy.com',
    host:'https://www.pzjzyy.com',
    // url:'/koks/fyclass/page/fypage.html',
    url:'/koks/fyclassfyfilter.html',
    filterable:1,//是否启用分类筛选,
    filter_url:'{{fl.area}}{{fl.by or "/by/time"}}{{fl.class}}/page/fypage{{fl.year}}',
    filter: {
        "kokdy":[{"key":"class","name":"类型","value":[{"n":"全部","v":""},{"n":"喜剧","v":"/class/喜剧"},{"n":"爱情","v":"/class/爱情"},{"n":"恐怖","v":"/class/恐怖"},{"n":"动作","v":"/class/动作"},{"n":"科幻","v":"/class/科幻"},{"n":"剧情","v":"/class/剧情"},{"n":"战争","v":"/class/战争"},{"n":"警匪","v":"/class/警匪"},{"n":"犯罪","v":"/class/犯罪"},{"n":"动画","v":"/class/动画"},{"n":"奇幻","v":"/class/奇幻"},{"n":"武侠","v":"/class/武侠"},{"n":"冒险","v":"/class/冒险"},{"n":"枪战","v":"/class/枪战"},{"n":"恐怖","v":"/class/恐怖"},{"n":"悬疑","v":"/class/悬疑"},{"n":"惊悚","v":"/class/惊悚"},{"n":"经典","v":"/class/经典"},{"n":"青春","v":"/class/青春"},{"n":"文艺","v":"/class/文艺"},{"n":"微电影","v":"/class/微电影"},{"n":"古装","v":"/class/古装"},{"n":"历史","v":"/class/历史"},{"n":"运动","v":"/class/运动"},{"n":"农村","v":"/class/农村"},{"n":"儿童","v":"/class/儿童"},{"n":"网络电影","v":"/class/网络电影"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"/area/大陆"},{"n":"香港","v":"/area/香港"},{"n":"台湾","v":"/area/台湾"},{"n":"美国","v":"/area/美国"},{"n":"法国","v":"/area/法国"},{"n":"英国","v":"/area/英国"},{"n":"日本","v":"/area/日本"},{"n":"韩国","v":"/area/韩国"},{"n":"德国","v":"/area/德国"},{"n":"泰国","v":"/area/泰国"},{"n":"印度","v":"/area/印度"},{"n":"意大利","v":"/area/意大利"},{"n":"西班牙","v":"/area/西班牙"},{"n":"加拿大","v":"/area/加拿大"},{"n":"其他","v":"/area/其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"2013","v":"/year/2013"},{"n":"2012","v":"/year/2012"},{"n":"2011","v":"/year/2011"},{"n":"2010","v":"/year/2010"},{"n":"2009","v":"/year/2009"},{"n":"2008","v":"/year/2008"},{"n":"2007","v":"/year/2007"},{"n":"2006","v":"/year/2006"},{"n":"2005","v":"/year/2005"},{"n":"2004","v":"/year/2004"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"/by/time"},{"n":"人气","v":"/by/hits"},{"n":"评分","v":"/by/score"}]}],
        "kokds":[{"key":"class","name":"类型","value":[{"n":"全部","v":""},{"n":"古装","v":"/class/古装"},{"n":"战争","v":"/class/战争"},{"n":"青春","v":"/class/青春"},{"n":"喜剧","v":"/class/喜剧"},{"n":"家庭","v":"/class/家庭"},{"n":"犯罪","v":"/class/犯罪"},{"n":"动作","v":"/class/动作"},{"n":"奇幻","v":"/class/奇幻"},{"n":"剧情","v":"/class/剧情"},{"n":"历史","v":"/class/历史"},{"n":"经典","v":"/class/经典"},{"n":"乡村","v":"/class/乡村"},{"n":"情景","v":"/class/情景"},{"n":"商战","v":"/class/商战"},{"n":"网剧","v":"/class/网剧"},{"n":"其他","v":"/class/其他"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"/area/大陆"},{"n":"韩国","v":"/area/韩国"},{"n":"香港","v":"/area/香港"},{"n":"台湾","v":"/area/台湾"},{"n":"日本","v":"/area/日本"},{"n":"美国","v":"/area/美国"},{"n":"泰国","v":"/area/泰国"},{"n":"英国","v":"/area/英国"},{"n":"新加坡","v":"/area/新加坡"},{"n":"其他","v":"/area/其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"2013","v":"/year/2013"},{"n":"2012","v":"/year/2012"},{"n":"2011","v":"/year/2011"},{"n":"2010","v":"/year/2010"},{"n":"2009","v":"/year/2009"},{"n":"2008","v":"/year/2008"},{"n":"2007","v":"/year/2007"},{"n":"2006","v":"/year/2006"},{"n":"2005","v":"/year/2005"},{"n":"20042023","v":"/year/20042023"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"/by/time"},{"n":"人气","v":"/by/hits"},{"n":"评分","v":"/by/score"}]}],
        "kokzy":[{"key":"class","name":"类型","value":[{"n":"全部","v":""},{"n":"选 秀","v":"/class/选秀"},{"n":"情感","v":"/class/情感"},{"n":"访谈","v":"/class/访谈"},{"n":"播报","v":"/class/播报"},{"n":"旅游","v":"/class/旅游"},{"n":"音乐","v":"/class/音乐"},{"n":"美食","v":"/class/美食"},{"n":"纪实","v":"/class/纪实"},{"n":"曲艺","v":"/class/曲艺"},{"n":"生活","v":"/class/生活"},{"n":"游戏互动","v":"/class/游戏互动"},{"n":"财经","v":"/class/财经"},{"n":"求职","v":"/class/求职"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"/area/大陆"},{"n":"韩国","v":"/area/韩国"},{"n":"香港","v":"/area/香港"},{"n":"日本","v":"/area/日本"},{"n":"美国","v":"/area/美国"},{"n":"其他","v":"/area/其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"2013","v":"/year/2013"},{"n":"2012","v":"/year/2012"},{"n":"2011","v":"/year/2011"},{"n":"2010","v":"/year/2010"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"/by/time"},{"n":"人气","v":"/by/hits"},{"n":"评分","v":"/by/score"}]}],
        "kokdm":[{"key":"class","name":"类型","value":[{"n":"全部","v":""},{"n":"情感","v":"/class/情感"},{"n":"科幻","v":"/class/科幻"},{"n":"热血","v":"/class/热血"},{"n":"推理","v":"/class/推理"},{"n":"搞笑","v":"/class/搞笑"},{"n":"冒险","v":"/class/冒险"},{"n":"萝莉","v":"/class/萝莉"},{"n":"校园","v":"/class/校园"},{"n":"动作","v":"/class/动作"},{"n":"机战","v":"/class/机战"},{"n":"运动","v":"/class/运动"},{"n":"战争","v":"/class/战争"},{"n":"少年","v":"/class/少年"},{"n":"少女","v":"/class/少女"},{"n":"社会","v":"/class/社会"},{"n":"原创","v":"/class/原创"},{"n":"亲子","v":"/class/亲子"},{"n":"益智","v":"/class/益智"},{"n":"励志","v":"/class/励志"},{"n":"其他","v":"/class/其他"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"/area/大陆"},{"n":"日本","v":"/area/日本"},{"n":"欧美","v":"/area/欧美"},{"n":"其他","v":"/area/其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"2013","v":"/year/2013"},{"n":"2012","v":"/year/2012"},{"n":"2011","v":"/year/2011"},{"n":"2010","v":"/year/2010"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"/by/time"},{"n":"人气","v":"/by/hits"},{"n":"评分","v":"/by/score"}]}],
        "kokjl":[{"key":"class","name":"类型","value":[{"n":"全部","v":""},{"n":"社会","v":"/class/社会"},{"n":"动物","v":"/class/动物"},{"n":"文化","v":"/class/文化"},{"n":"自然","v":"/class/自然"},{"n":"人文","v":"/class/人文"},{"n":"军事","v":"/class/军事"},{"n":"历史","v":"/class/历史"},{"n":"记录","v":"/class/记录"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"/area/大陆"},{"n":"日本","v":"/area/日本"},{"n":"美国","v":"/area/美国"},{"n":"国外","v":"/area/国外"},{"n":"其他","v":"/area/其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2019","v":"/year/2019"},{"n":"2018","v":"/year/2018"},{"n":"2017","v":"/year/2017"},{"n":"2016","v":"/year/2016"},{"n":"2015","v":"/year/2015"},{"n":"2014","v":"/year/2014"},{"n":"2013","v":"/year/2013"},{"n":"2012","v":"/year/2012"},{"n":"2011","v":"/year/2011"},{"n":"2010","v":"/year/2010"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"/by/time"},{"n":"人气","v":"/by/hits"},{"n":"评分","v":"/by/score"}]}]
    },
    searchable:2,
    quickSearch:0,
    headers:{
        'User-Agent':'MOBILE_UA'
    },
    class_name:'电影&电视剧&综艺&动漫&记录',
    class_url:'kokdy&kokds&kokzy&kokdm&kokjl',
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
    play_parse:true,
    limit:6,
    推荐:'*',
    一级:`js:
        var d = [];
        pdfh = jsp.pdfh;pdfa = jsp.pdfa;pd = jsp.pd;
        var html = request(input, {
            withHeaders: true
        });
        let json = JSON.parse(html);
        let setCk = Object.keys(json).find(it => it.toLowerCase() === "set-cookie");
        let cookie = setCk ? json[setCk].split(";")[0] : "";
        fetch_params.headers.Cookie = cookie;
        html = JSON.parse(html).body;
        if (/检测中/.test(html)) {
            html = request(input + "?btwaf" + html.match(/btwaf(.*?)\"/)[1], fetch_params)
        }
        let list = pdfa(html, ".movie-list-body&&.movie-list-item");
        list.forEach(it => {
            d.push({
                title: pdfh(it, ".movie-title&&Text"),
                desc: pdfh(it, ".movie-rating&&Text"),
                pic_url: pd(it, ".movie-post-lazyload&&data-original"),
                url: pd(it, "a&&href")
            })
        });
        setResult(d)
    `,
    二级:`js:
        pdfh = jsp.pdfh;pdfa = jsp.pdfa;pd = jsp.pd;
        VOD = {};
        var html = request(input, {
            withHeaders: true
        });
        let json = JSON.parse(html);
        let setCk = Object.keys(json).find((it) => it.toLowerCase() === "set-cookie");
        let cookie = setCk ? json[setCk].split(";")[0] : "";
        fetch_params.headers.Cookie = cookie;
        html = JSON.parse(html).body;
        if (/检测中/.test(html)) {
            html = request(input + "?btwaf" + html.match(/btwaf(.*?)\"/)[1], fetch_params)
        }
        VOD.vod_name = pdfh(html, "h1&&Text");
        VOD.type_name = pdfh(html, ".scroll-content&&a:eq(1)&&Text");
        VOD.vod_pic = pd(html, ".poster&&img&&src");
        VOD.vod_remarks = pdfh(html, ".cr3:eq(0)&&Text");
        VOD.vod_year = pdfh(html, ".scroll-content&&a:eq(2)&&Text");
        VOD.vod_area = pdfh(html, ".scroll-content&&a:eq(0)&&Text");
        VOD.vod_actor = pdfh(html, ".cr3.starLink&&Text").replace("演员：", "");
        VOD.vod_director = pdfh(html, ".play-select:eq(2)&&p:eq(4)&&Text").replace("导演:", "");
        VOD.vod_content = pdfh(html, ".detailsTxt&&Text");
        let playFrom = [];
        let vod_tab_list = [];
        let tabs = pdfa(html, "body .swiper-wrapper&&a");
        tabs.forEach((it) => {
            playFrom.push(pdfh(it, "a&&Text"))
        });
        for (let i = 0; i < playFrom.length; i++) {
            let p1 = ".content_playlist:eq(#id)&&li".replaceAll("#id", i);
            let new_vod_list = [];
            let vodList = [];
            try {
                vodList = pdfa(html, p1)
            } catch (e) {}
            for (let i = 0; i < vodList.length; i++) {
                let it = vodList[i];
                new_vod_list.push(pdfh(it, "body&&Text").trim() + "$" + pd(it, "a&&href"))
            }
            let vlist = new_vod_list.join("#");
            vod_tab_list.push(vlist)
        }
        VOD.vod_play_from = playFrom.join("$$$");
        VOD.vod_play_url = vod_tab_list.join("$$$");
    `,
    searchUrl:'/kokso/page/fypage/wd/**.html',
    搜索:`js:
        var d = [];
        pdfh = jsp.pdfh;pdfa = jsp.pdfa;pd = jsp.pd;
        var html = request(input, {
            withHeaders: true
        });
        let json = JSON.parse(html);
        let setCk = Object.keys(json).find(it => it.toLowerCase() === "set-cookie");
        let cookie = setCk ? json[setCk].split(";")[0] : "";
        fetch_params.headers.Cookie = cookie;
        html = JSON.parse(html).body;
        if (/检测中/.test(html)) {
            html = request(input + "?btwaf" + html.match(/btwaf(.*?)\"/)[1], fetch_params)
        }
        let list = pdfa(html, ".movie-list-body.flex&&.vod-search-list");
        list.forEach(it => {
            d.push({
                title: pdfh(it, ".movie-title&&title"),
                desc: pdfh(it, ".meta:eq(0)&&Text"),
                pic_url: pd(it, ".movie-post-lazyload&&data-original"),
                url: pd(it, "a&&href")
            })
        });
        setResult(d)
    `,
}