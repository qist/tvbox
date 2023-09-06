var rule = {
    title: 'kk小站',
    host: 'http://127.0.0.1:10079',
    homeUrl: '/p/0/socks5:%252F%252F192.168.101.1:1080/https://kkxz.vip/',
    url: '/p/0/socks5:%252F%252F192.168.101.1:1080/https://kkxz.vip/t/fyclass?',
    filter_url: '{{fl.class}}',
    filter: {},
    searchUrl: '/p/0/socks5:%252F%252F192.168.101.1:1080/https://kkxz.vip/?q=**',
    searchable: 2,
    quickSearch: 1,
    filterable: 0,
    headers: {
        'User-Agent': PC_UA,
        'Accept': '*/*',
	'Cookie':'http://127.0.0.1:9978/file:///tvbox/JS/lib/kkxz.txt',
        'Referer': 'https://kkxz.vip/'
    },

    class_name: '電視劇&電影',
    class_url: 'tv&movie',
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
    一级: 'div.DiscussionList li;h3&&Text;img&src;;a&&href',
    二级: {
        title: "h2&&Text",
        img: "img&&src",
        desc: "p&&Text",
        content: "p&&Text",
        tabs: `js: pdfh = jsp.pdfh;
        pdfa = jsp.pdfa;
        pd = jsp.pd;
        TABS = [];
        let d = pdfa(html, '.Post-body p a');
        let tabsa = [];
        let tabsq = [];
        let tabsm = false;
        let tabse = false;
        d.forEach(function(it) {
            let burl = pdfh(it, 'a&&href');
            if (burl.startsWith("https://www.aliyundrive.com/s/")) {
                tabsa.push("阿里云盤");
            } else if (burl.startsWith("https://pan.quark.cn/s/")) {
                tabsq.push("夸克云盤");
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
        let d = pdfa(html, '.Post-body p a');
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
                    burl = "http://127.0.0.1:9978/proxy?do=quark&type=push&confirm=0&url=" + encodeURIComponent(burl);
                } else {
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
    搜索: 'div.Discussionlist li;h3&&Text;img&&src;span.TagLabel-text;a&&href',
}
