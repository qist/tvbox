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
            let tabsb = [];
            let tabsm = false;
            let tabse = false;
            
            d.forEach(function(it) {
                let burl = pdfh(it, 'a&&href');
                if (burl.includes("pan.quark.cn/s/")) {
                    tabsq.push("夸克网盘");
                } else if (burl.includes("pan.baidu.com/s/")) {
                    tabsb.push("百度网盘");
                } else if (burl.startsWith("magnet")) {
                    tabsm = true;
                } else if (burl.startsWith("ed2k")) {
                    tabse = true;
                }
            });
            
            
            if (tabsb.length > 0) TABS.push("百度网盘");
            if (tabsq.length > 0) TABS.push("夸克网盘");
            if (tabsm) TABS.push("磁力");
            if (tabse) TABS.push("电驴");
            log('生成TABS: ' + JSON.stringify(TABS));`,
        lists: `js:
            pdfh = jsp.pdfh;
            pdfa = jsp.pdfa;
            pd = jsp.pd;
            LISTS = [];
            let d = pdfa(html, 'span a');
            let listm = [];
            let liste = [];
            let listq = [];
            let listb = [];
            
            d.forEach(function(it) {
                let burl = pdfh(it, 'a&&href');
                let title = pdfh(it, 'a&&Text');
                let loopresult = title + '$' + burl;
                
                if (burl.includes("pan.quark.cn/s/")) {
                    burl = burl.split("?")[0]; 
                    loopresult = title + '$' + burl;
                    listq.push(loopresult);
                } else if (burl.includes("pan.baidu.com/s/")) {
                    let codeMatch = title.match(/提取码[：:]?\s*(\w{4})|(\w{4})(?=提取|百度|网盘)/i);
                    if (codeMatch) {
                        let code = codeMatch[1] || codeMatch[2];
                        burl += '#' + code;
                    }
                    loopresult = title + '$' + burl;
                    listb.push(loopresult);
                } else if (burl.startsWith("magnet")) {
                    listm.push(loopresult);
                } else if (burl.startsWith("ed2k")) {
                    liste.push(loopresult);
                }
            });
            
            
            if (listb.length > 0) LISTS.push(listb);
            if (listq.length > 0) LISTS.push(listq);
            if (listm.length > 0) LISTS.push(listm);
            if (liste.length > 0) LISTS.push(liste);
            
            
            if (LISTS.length === 0 && listq.length > 0) {
                LISTS = [listq];
            }`,
    },
    搜索: 'li:has(img);h2&&Text;img&&data-original;.tags&&Text;a&&href',
};