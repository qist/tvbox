var rule = {
    title:'闪雷影视',
    编码:'gb2312',
    host: 'http://114.100.48.52:18008',

    // 首页
    homeUrl: '/jdl/index.asp',

    // 分类页
    url: '/jdl/List.asp?ClassID=fyclass&page=fypage',

    // ================= 搜索 =================
    // ClassId=30 是搜索页，关键词为 GBK
    searchUrl: '/jdl/List.asp?ClassId=30&type=&searchword=**&page=fypage',
    searchable: 1,
    quickSearch: 0,

    headers: {
        'User-Agent': 'PC_UA',
        'Referer': 'http://114.100.48.52:18008'
    },

    timeout: 5000,

    // ================= 分类 =================
    class_name: '大陆地区&港台地区&日韩地区&欧美地区&其他地区&动作片&喜剧片&恐怖片&科幻片&战争片&动画片&爱情片&综艺片&剧情片&MTV&连续剧',
    class_url:  '20&21&22&23&24&1&2&3&4&5&6&7&8&9&12&10',

    // ================= 列表页（分类 & 搜索通用） =================
    一级: `
        table tr;
        a&&Text;
        img&&src;
        ;
        a&&href
    `,

    // ================= 详情页 =================
    二级: {
        title: 'h1&&Text',
        img: 'img&&src',
        desc: ';;span:eq(0)&&Text;span:eq(1)&&Text;span:eq(2)&&Text',
        content: 'td&&Text',
        tabs: '.playtitle',
        lists: 'a'
    },

    // ================= 播放页 =================
    play_parse: true,
    lazy: `
        var html = request(input);

        // 兼容 ASP 老站播放变量
        var url = html.match(/(http[^'"]+\\.(m3u8|mp4))/i);

        if (url) {
            input = url[1];
        }
    `,

    limit: 6
};
