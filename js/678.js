var rule = {
    title:'闪雷影视',
    编码:'gb2312',
    host: 'http://114.100.48.52:18008',

    homeUrl: '/jdl/List.asp?ClassID=10',
    url: '/jdl/List.asp?ClassID=fyclass',

    searchable: 1,
    quickSearch: 0,
    searchUrl: '/jdl/List.asp?ClassId=30&type=&searchword=**',

    headers: {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'http://114.100.48.52:18008'
    },

    timeout: 8000,

    class_name: '大陆地区&港台地区&日韩地区&欧美地区&其他地区&动作片&喜剧片&恐怖片&科幻片&战争片&动画片&爱情片&综艺片&剧情片&MTV&连续剧',
    class_url:  '20&21&22&23&24&1&2&3&4&5&6&7&8&9&12&10',

    // ===== 一级 =====
    一级: `
        a[href*="movie.asp?ClassID="];
        a&&Text;
        img&&src;
        ;
        a&&href
    `,

    // ===== 二级（⚠️ 关键修正）=====
    二级: {
        title: 'font&&Text',
        img: 'img&&src',
        desc: ';;font:eq(1)&&Text;font:eq(2)&&Text;font:eq(3)&&Text',
        content: 'td&&Text',

        tabs: '',

        // ❗ 不再找 PlayMov.asp
        lists: 'a[onclick^="senfe"]',
        list_url: 'a&&onclick',
        list_text: 'a&&Text'
    },

    // ===== 播放（⚠️ 关键修正）=====
    play_parse: true,
    lazy: `
        // input: senfe('578027',1)
        var m = input.match(/senfe\\('([^']+)',\\s*(\\d+)\\)/);
        if (!m) {
            input = { parse: 1, url: input };
            return;
        }

        var classId = m[1];
        var movNo = m[2];

        var playUrl =
            rule.host +
            '/PlayMov.asp?ClassId=' +
            classId +
            '&video=2&exe=0&down=0&movNo=' +
            movNo;

        var html = request(playUrl);

        var real = html.match(/push\\(['"]([^'"]+)['"]\\)/);
        if (!real) {
            input = { parse: 1, url: playUrl };
            return;
        }

        var url = real[1];
        if (!/^https?:\\/\\//.test(url)) {
            url = rule.host + '/' + url.replace(/^\\//, '');
        }

        input = {
            jx: 0,
            parse: 0,
            url: url
        };
    `,

    limit: 6
};
