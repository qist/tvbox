var rule = {
    title:'88看球',
    // host:'http://www.88kanqiu.cc',
    host:'http://www.88kanqiu.bar/',
    url: "/match/fyclass/live",
    searchUrl: "",
    searchable: 0,
    quickSearch: 0,
    class_parse: ".nav-pills li;a&&Text;a&&href;/match/(\\d+)/live",
    headers: {
        "User-Agent": "PC_UA",
    },
    timeout: 5000,
    play_parse: true,
    pagecount:{"1":1,"2":1,"4":1,"22":1,"8":1,"9":1,"10":1,"14":1,"15":1,"12":1,"13":1,"16":1,"28":1,"7":1,"11":1,"33":1,"27":1,"23":1,"26":1,"3":1,"21":1,"18":1},
    lazy: `js:
        if(/embed=/.test(input)) {
            let url = input.match(/embed=(.*?)&/)[1];
            url = base64Decode(url);
            input = {
                jx:0,
                url: url.split('#')[0],
                parse: 0
            }
        } else if (/\?url=/.test(input)){
            input = {
                jx:0,
                url: input.split('?url=')[1].split('#')[0],
                parse: 0
            }
        } else {
            input
        }
    `,
    limit: 6,
    double: false,
    推荐: "*",
    一级: ".list-group .group-game-item;.d-none&&Text;img&&src;.btn&&Text;a&&href",
    二级: {
        title: ".game-info-container&&Text;.customer-navbar-nav li&&Text",
        img: "img&&src",
        desc: ";;;div.team-name:eq(0)&&Text;div.team-name:eq(1)&&Text",
        content: "div.game-time&&Text",
        tabs: "js:TABS=['实时直播']",
        lists: `js:
            LISTS = [];
            let html = request(input.replace('play', 'play-url'));
            let pdata = JSON.parse(html).data;
            pdata = pdata.slice(6);
            pdata = pdata.slice(0, -2);
            pdata = base64Decode(pdata);
            // log(pdata);
            let jo = JSON.parse(pdata).links;
            let d = jo.map(function (it) {
                return it.name + '$' + urlencode(it.url)
            });
            LISTS.push(d)
        `,
    },
    搜索: "",
};