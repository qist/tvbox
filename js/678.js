var rule = {
    title: '闪雷影视',
    编码: 'gb2312',
    host: 'http://114.100.48.52:18008/jdl',
    url: '/List.asp?ClassID=fyclass&page=fypage',

    class_name: '动作片&喜剧片&恐怖片&科幻片&战争片&动画片&爱情片&综艺&剧情片&连续剧',
    class_url: '1&2&3&4&5&6&7&8&9&10',

    searchUrl: '/List.asp?ClassID=30&searchword=**&page=fypage',
    searchable: 2,
    quickSearch: 1,

    headers: {
        'User-Agent': 'MOBILE_UA',
    },

    play_parse: true,

    lazy: $js.toString(() => {
        // input: movie.asp?ClassID=578050
        let cid = input.match(/ClassID=(\d+)/)[1];
        let html = rule.host + '/PlayMov.asp?ClassId=' + cid +
            '&video=2&exe=0&down=0&movNo=1&vgver=2009&ClientIP=121.16.47.94';

        let page = request(html);
        let url = page.match(/push\('(.*?)'/)[1];

        // 修正为站内路径
        url = url.replace(/https?:\/\/[^\/]+\//, rule.host + '/');

        input = {
            jx: 0,
            parse: 0,
            url: url
        };
    }),

    limit: 6,

    推荐: '.text li;a&&Text;;span.num&&Text;a&&href',

    一级: 'a[href^="movie.asp"]&&Text;;a&&href',

    二级: {
        title: 'ul&&li:eq(0)&&Text',
        img: '.intro img&&src',
        desc: 'ul&&li:eq(1)&&Text;ul&&li:eq(2)&&Text;ul&&li:eq(4)&&Text;ul&&li:eq(5)&&Text',
        content: '.textnr&&Text',
        tabs: '',
        lists: '.listt a',
        list_url: 'a&&href',
        list_text: 'a&&Text'
    },

    搜索: 'a[href^="movie.asp"]&&Text;;a&&href'
};
