var rule = {
    title: '新闪雷',
    编码: 'gb2312',
    host: 'http://114.100.48.52:18008',
    ip: '114.100.48.52',
    filterable: 0,
    url: '/jdl/List.asp?ClassId=fyclass&searchword=&page=fypage',
    searchable: 2,
    quickSearch: 1,
    searchUrl: '/jdl/List.asp?ClassId=30&type=&searchword=**&page=fypage',

    headers: {
        'User-Agent': 'MOBILE_UA',
    },

    timeout: 20000,

    class_name: '电视剧&大陆地区&港台地区&日韩地区&欧美地区&其他地区&动作片&喜剧片&恐怖片&科幻片&战争片&动画片&爱情片&综艺片&剧情片&MTV',
    class_url: '10&20&21&22&23&24&1&2&3&4&5&6&7&8&9&12',

    /* =============== 一级列表（关键修正） =============== */
    一级: `
    dl:has(dd[classid=h4]);
    dd[classid=h4] a&&Text;
    dt img&&src;
    dt img&&alt;
    dd[classid=h4] a&&href
    `,


    // 图片路径修复
    图片处理: $js.toString((src) => {
        if (src.startsWith('../')) {
            return rule.host + '/' + src.replace('../', '');
        }
        return src;
    }),

    /* =============== 二级详情页（关键修正） =============== */
    二级: {
        title: 'li[classid=h4]&&Text',
        img: '.intro .img img&&src',
        desc: 'li:contains(主　　演)&&Text',
        content: 'li:contains(状　　态),li:contains(类　　型),li:contains(拍摄地区),li:contains(更新时间),li:contains(单集时长)',
        tabs: '',
        lists: 'div.listt a',
        list_url: 'a&&href',
        list_text: 'a&&Text'
    },

    搜索: '*',

    /* =============== 播放解析（稳定版） =============== */
    // ===== 播放解析 =====
    play_parse: true,
    lazy: $js.toString(() => {
        var html = rule.host + '/PlayMov.asp?ClassId=' + input.split(",")[2] + '&video=2&exe=0&down=0&movNo=' + input.split(",")[3] + '&vgver=undefined&ClientIP='+ rule.ip;
        var url = request(html).match(/videoarr\.push\('(.*?)'/)[1]
        url = url.replace(/https?:\/\/(?:[\d.]+|[\w\-]+)(?::\d+)?\//, rule.host + '/');
        input = {
            jx: 0,
            url: url,
            parse: 0
        };
    }),
    limit: 6,
};
