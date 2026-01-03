var rule = {
    title: '人人电影网',
    host: 'https://www.rrdynb.com',
    homeUrl: '/',
    url: '/fyclass_fypage.html?',
    filter_url: '{{fl.class}}',
    filter: {},
    searchUrl: '/plus/search.php?q=**&pagesize=10&submit=',
    searchable: 2,
    quickSearch: 1,
    filterable: 0,
    headers: {
        'User-Agent': 'PC_UA',
        'Cookie': ''
    },
    timeout: 5000,
    class_name: '影视&电视剧&老电影&动漫',
    class_url: 'movie/list_2&dianshiju/list_6&zongyi/list_10&dongman/list_13',
    play_parse: true,
    play_json: [{
        re: '*',
        json: {
            parse: 0,
            jx: 0
        }
    }],
    lazy: "js:\n        input = 'push://' + input;\n    ",
    limit: 6,
    推荐: '',
    一级: 'li:has(img);img&&alt;img&&data-original;;a&&href',
    二级: {
        title: "h1&&Text",
        img: "img&&src",
        desc: ".info:eq(0)&&Text",
        content: ".content&&Text",
        tabs: `js:
        pdfh = jsp.pdfh;
        pdfa = jsp.pdfa;
        pd = jsp.pd;
        TABS = [];
        let d = pdfa(html, 'span a');
        let tabsq = [];
        
        d.forEach(function(it) {
            let burl = pdfh(it, 'a&&href');
            if (burl && burl.includes("pan.quark.cn/s/")) {
                tabsq.push("夸克网盘");
            }
        });
        
        if (tabsq.length > 0) TABS.push("夸克网盘");
        log('生成TABS: ' + JSON.stringify(TABS));`,
        lists: `js:
        pdfh = jsp.pdfh;
        pdfa = jsp.pdfa;
        pd = jsp.pd;
        LISTS = [];
        let d = pdfa(html, 'span a');
        let listq = [];
        
        d.forEach(function(it) {
            let burl = pdfh(it, 'a&&href');
            let title = pdfh(it, 'a&&Text');
            
            if (burl && burl.includes("pan.quark.cn/s/")) {
                // 同时删除 ? 和 # 后面的内容
                burl = burl.split('?')[0].split('#')[0];
                let loopresult = title + '$' + burl;
                listq.push(loopresult);
            }
        });
        
        if (listq.length > 0) {
            LISTS = [listq];  // 修复重复添加的问题
        }`,
    },
    搜索: 'li:has(img);h2&&Text;img&&data-original;.tags&&Text;a&&href',
};
