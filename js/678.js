var rule = {
    title:'闪雷影视',
    编码:'gb2312',
    host: 'http://114.100.48.52:18008',

    // ⚠️ 首页直接用一个真实列表页
    homeUrl: '/jdl/List.asp?ClassID=10',

    // 分类页
    url: '/jdl/List.asp?ClassID=fyclass',

    // ===== 搜索 =====
    searchable: 1,
    quickSearch: 0,
    searchUrl: '/jdl/List.asp?ClassId=30&type=&searchword=**',

    headers: {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'http://114.100.48.52:18008'
    },

    timeout: 8000,

    // ===== 分类 =====
    class_name: '大陆地区&港台地区&日韩地区&欧美地区&其他地区&动作片&喜剧片&恐怖片&科幻片&战争片&动画片&爱情片&综艺片&剧情片&MTV&连续剧',
    class_url:  '20&21&22&23&24&1&2&3&4&5&6&7&8&9&12&10',

    // ===== 一级（⚠️ 最关键）=====
    一级: `
        a[href*="movie.asp?ClassID="];
        a&&Text;
        img&&src;
        ;
        a&&href
    `,

    // ===== 二级 =====
    二级: {
        title: 'font&&Text',
        img: 'img&&src',
        desc: ';;font:eq(1)&&Text;font:eq(2)&&Text;font:eq(3)&&Text',
        content: 'td&&Text',
        tabs: 'font',
        lists: 'a[href*="PlayMov.asp"]'
    },

    // ===== 播放 =====
    play_parse: true,
    lazy: `
        var html = request(input);
        var url = html.match(/(http[^'"]+\\.(m3u8|mp4|flv))/i);
        if (url) {
            input = url[1];
        }
    `,

    limit: 6
};
