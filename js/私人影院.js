var rule={
    title:'私人影院(被窝电影)',
    // host:'https://www.bei5dy.com',
    host:'https://www.bei5dy.net',
    url:'/show/fyfilter/',
    filterable:1,//是否启用分类筛选,
    filter_url:'{{fl.cateId}}-{{fl.area}}-{{fl.by}}-{{fl.class}}-{{fl.lang}}-{{fl.letter}}---fypage---{{fl.year}}',
    filter:{
        "dianying":[{"key":"cateId","name":"类型","value":[{"n":"全部","v":"dianying"},{"n":"动作片","v":"dongzuopian"},{"n":"喜剧片","v":"xijupian"},{"n":"爱情片","v":"aiqingpian"},{"n":"科幻片","v":"kehuanpian"},{"n":"恐怖片","v":"kongbupian"},{"n":"剧情片","v":"juqingpian"},{"n":"战争片","v":"zhanzhengpian"},{"n":"综合片","v":"lunlipian"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"🇨🇳中国","v":"大陆"},{"n":"🇭🇰香港","v":"香港"},{"n":"🇹🇼台湾","v":"台湾"},{"n":"🇺🇸美国","v":"美国"},{"n":"法国","v":"法国"},{"n":"英国","v":"英国"},{"n":"🇯🇵日本","v":"日本"},{"n":"🇰🇷韩国","v":"韩国"},{"n":"德国","v":"德国"},{"n":"泰国","v":"泰国"},{"n":"印度","v":"印度"},{"n":"意大利","v":"意大利"},{"n":"西班牙","v":"西班牙"},{"n":"加拿大","v":"加拿大"},{"n":"其他","v":"其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2025","v":"2025"},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010~2001","v":"2010~2001"},{"n":"2000~1991","v":"2000~1991"},{"n":"1990~1960","v":"1990~1960"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"法语","v":"法语"},{"n":"德语","v":"德语"},{"n":"其它","v":"其它"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
        "dianshiju":[{"key":"cateId","name":"类型","value":[{"n":"全部","v":"dianshiju"},{"n":"国产剧","v":"guochanju"},{"n":"港台剧","v":"gangtaiju"},{"n":"日韩剧","v":"rihanju"},{"n":"欧美剧","v":"oumeiju"},{"n":"其他剧","v":"qitaju"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"🇨🇳中国","v":"大陆"},{"n":"🇰🇷韩国","v":"韩国"},{"n":"🇭🇰香港","v":"香港"},{"n":"🇹🇼台湾","v":"台湾"},{"n":"🇯🇵日本","v":"日本"},{"n":"🇺🇸美国","v":"美国"},{"n":"泰国","v":"泰国"},{"n":"英国","v":"英国"},{"n":"新加坡","v":"新加坡"},{"n":"其他","v":"其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2025","v":"2025"},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010~2001","v":"2010~2001"},{"n":"2000~1991","v":"2000~1991"},{"n":"1990~1960","v":"1990~1960"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
        "zongyi":[{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"🇨🇳中国","v":"大陆"},{"n":"港台","v":"港台"},{"n":"日韩","v":"日韩"},{"n":"欧美","v":"欧美"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2025","v":"2025"},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010~2001","v":"2010~2001"},{"n":"2000~1991","v":"2000~1991"},{"n":"1990~1960","v":"1990~1960"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
        "dongman":[{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"🇨🇳中国","v":"大陆"},{"n":"🇯🇵日本","v":"日本"},{"n":"欧美","v":"欧美"},{"n":"其他","v":"其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2025","v":"2025"},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010~2001","v":"2010~2001"},{"n":"2000~1991","v":"2000~1991"},{"n":"1990~1960","v":"1990~1960"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}]
    },
	filter_def:{
		dianying:{cateId:'dianying'},
		dianshiju:{cateId:'dianshiju'},
		zongyi:{cateId:'zongyi'},
		dongman:{cateId:'dongman'}
	},
    searchUrl:'/search/**----------fypage---/',
    searchable:2,
    quickSearch:0,
    headers:{
        'User-Agent':'MOBILE_UA'
    },
    timeout:5000,//网站的全局请求超时,默认是3000毫秒
    // class_parse: '.stui-header__menu&&li;a&&Text;a&&href;.*/(\\w+)/',
    class_name:'电影&电视剧&动漫&综艺',
    class_url:'dianying&dianshiju&zongyi&dongman',
    play_parse:true,
	lazy:`js:
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
        var phtml = JSON.parse(html.match(/r player_.*?=(.*?)</)[1]);
        var url = phtml.url;
        if (phtml.encrypt == '1') {
            url = unescape(url)
        } else if (phtml.encrypt == '2') {
            url = unescape(base64Decode(url))
        }
        if (/m3u8|mp4/.test(url)) {
            input = url
        } else {
            input
        }
    `,
    推荐:'*',
    一级:`js:
        var d = [];
        pdfh = jsp.pdfh;
        pdfa = jsp.pdfa;
        pd = jsp.pd;
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
        let list = pdfa(html, "ul.stui-vodlist&&li");
        list.forEach(it => {
            d.push({
                title: pdfh(it, "a&&title"),
                desc: pdfh(it, ".pic-text&&Text"),
                pic_url: pd(it, ".lazyload&&data-original"),
                url: pd(it, "a&&href")
            })
        });
        setResult(d)
    `,
    二级:`js:
        pdfh = jsp.pdfh;
        pdfa = jsp.pdfa;
        pd = jsp.pd;
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
        VOD.vod_name = pdfh(html, ".stui-content__detail&&h1--span&&Text");
        VOD.type_name = pdfh(html, ".data--span:eq(0)&&Text");
        VOD.vod_pic = pd(html, ".stui-content__thumb&&img&&data-original");
        VOD.vod_remarks = pdfh(html, ".stui-content__thumb&&pic-text&&Text");
        VOD.vod_actor = pdfh(html, ".data--span:eq(1)&&Text");
        VOD.vod_director = pdfh(html, ".data--span:eq(2)&&Text");
        VOD.vod_content = pdfh(html, ".desc.hidden-xs--a&&Text");
        let playFrom = [];
        let vod_tab_list = [];
        let tabs = pdfa(html, "body .stui-pannel__head.bottom-line");
        tabs.forEach((it) => {
            playFrom.push(pdfh(it, "h3&&Text"))
        });
        for (let i = 0; i < playFrom.length; i++) {
            let p1 = ".stui-content__playlist:eq(#id)&&li".replaceAll("#id", i);
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
    搜索:`js:
        var d = [];
        pdfh = jsp.pdfh;
        pdfa = jsp.pdfa;
        pd = jsp.pd;
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
        let list = pdfa(html, ".stui-vodlist__media&&li");
        list.forEach(it => {
            d.push({
                title: pdfh(it, "a&&title"),
                desc: pdfh(it, ".pic-text&&Text"),
                pic_url: pd(it, ".lazyload&&data-original"),
                url: pd(it, "a&&href")
            })
        });
        setResult(d)
    `,
}