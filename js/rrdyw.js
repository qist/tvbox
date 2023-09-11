var rule = {
    title: 'RRDY網',
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
    class_name: '影视&電視劇&老電影&動漫',
    class_url: 'movie/list_2&dianshiju/list_6&zongyi/list_10&dongman/list_13',
    play_parse: true,
    play_json: [{
        re: '*',
        json: {
            parse: 0,
            jx: 0
        }
    }],
    lazy: '',
    limit: 6,
    推荐: '',
    一级: 'li:has(img);img&&alt;img&&data-original;;a&&href',
    二级: {
        title: "h1&&Text",
        img: "img&&src",
        desc: "",
        content: "span&&Text",
        tabs: `js: pdfh = jsp.pdfh;
        pdfa = jsp.pdfa;
        pd = jsp.pd;
        TABS = []
        let d = pdfa(html, 'span a');
        let tabsa = [];
        let tabsq = [];
        let tabsm = false;
        let tabse = false;
        d.forEach(function(it) {
            let burl = pdfh(it, 'a&&href');
            if (burl.startsWith("https://www.aliyundrive.com/s/")) {
                tabsa.push("阿里雲盤");
            } else if (burl.startsWith("https://pan.quark.cn/s/")) {
                tabsq.push("夸克網盤");
            } else if (burl.startsWith("magnet")) {
                tabsm = true;
            } else if (burl.startsWith("ed2k")) {
                tabse = true;
            }
        });
        if (tabsm === true) {
            TABS.push("磁力");
        }
        if (tabse === true) {
            TABS.push("電驢");
        }
        let tmpIndex;
        tmpIndex = 1;
        tabsa.forEach(function(it) {
            TABS.push(it + tmpIndex);
            tmpIndex = tmpIndex + 1;
        });
        tmpIndex = 1;
        tabsq.forEach(function(it) {
            TABS.push(it + tmpIndex);
            tmpIndex = tmpIndex + 1;
        });
        log('alyps TABS >>>>>>>>>>>>>>>>>>' + TABS);`,
        lists: `js: log(TABS);
        pdfh = jsp.pdfh;
        pdfa = jsp.pdfa;
        pd = jsp.pd;
        LISTS = [];
        let d = pdfa(html, 'span a');
        let lista = [];
        let listq = [];
        let listm = [];
        let liste = [];
        d.forEach(function(it) {
            let burl = pdfh(it, 'a&&href');
            let title = pdfh(it, 'a&&Text');
            log('alyps title >>>>>>>>>>>>>>>>>>>>>>>>>>' + title);
            log('alyps burl >>>>>>>>>>>>>>>>>>>>>>>>>>' + burl);
            let loopresult = title + '$' + burl;
            if (burl.startsWith("https://www.aliyundrive.com/s/")) {
                if (TABS.length == 1) {
                    burl = "http://127.0.0.1:9978/proxy?do=ali&type=push&confirm=0&url=" + encodeURIComponent(burl);
                } else {
                    burl = "http://127.0.0.1:9978/proxy?do=ali&type=push&url=" + encodeURIComponent(burl);
                }
                loopresult = title + '$' + burl;
                lista.push(loopresult);
            } else if (burl.startsWith("https://pan.quark.cn/s/")) {
                if (TABS.length == 1) {
                    burl = burl.replace("?entry=sjss", ""),
                    burl = "http://127.0.0.1:9978/proxy?do=quark&type=push&confirm=0&url=" + encodeURIComponent(burl);
                } else {
                    burl = burl.replace("?entry=sjss", ""),
                    burl = "http://127.0.0.1:9978/proxy?do=quark&type=push&url=" + encodeURIComponent(burl);
                }
                loopresult = title + '$' + burl;
                listq.push(loopresult);
            } else if (burl.startsWith("magnet")) {
                listm.push(loopresult);
            } else if (burl.startsWith("ed2k")) {
                liste.push(loopresult);
            }
        });
        if (listm.length > 0) {
            LISTS.push(listm.reverse());
        }
        if (liste.length > 0) {
            LISTS.push(liste.reverse());
        }
        lista.forEach(function(it) {
            LISTS.push([it]);
        });
        listq.forEach(function(it) {
            LISTS.push([it]);
        });`,

    },
    搜索: 'li:has(img);h2&&Text;img&&data-original;.tags&&Text;a&&href',
}
