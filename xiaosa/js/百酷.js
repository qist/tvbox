var rule = {
    title: '百酷短剧',
    host: 'https://api.kuleu.com/',
    hostJs: '',
    headers: {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36',
    },
    编码: 'utf-8',
    timeout: 5000,
    url: 'https://api.kuleu.com/fyclass',
    filter_url: '',
    detailUrl: '',
    searchUrl: 'https://api.kuleu.com/api/bddj?text=**',
    searchable: 1,
    quickSearch: 1,
    filterable: 1,
    class_name: '今日更新&百度短剧&每日更新&夸克短剧&每日更新',
    class_url: 'api/yingshi&api/bddj?list&api/bddj?today&api/action?list&api/action?today',
    proxy_rule: '',
    sniffer: false,
    isVideo: '',
    play_parse: true,
    parse_url: '',
    lazy: "js:\n        input = 'push://' + input;\n    ",
    limit: 9,
    double: false,
    // 推荐: '*',
    一级: $js.toString(() => {
    let cid = MY_CATE || '108';
    let pg = MY_PAGE || 1;
    let url = `https://api.kuleu.com/${cid}`;
    let khtml = fetch(url, {headers: rule.headers});
    let kjson = JSON.parse(khtml);
    VODS = [];
    kjson.data.forEach(it => {
        VODS.push({
            vod_name: it.name,
            vod_pic: `https://tse3-mm.cn.bing.net/th/id/OIP-C.rlQOYtsriwWKHwofGufJ_AHaQd?w=157&h=350&c=7&r=0&o=7&dpr=3.7&pid=1.7&rm=3`,
            vod_remarks: it.addtime,
            vod_id: `push://${it.viewlink}`
        });
    });
}),
    二级: '*',
    搜索:$js.toString(() => {
    let url = `https://api.kuleu.com/api/bddj?text=${KEY}`;
    let khtml = fetch(url);
    let kjson = JSON.parse(khtml);
    VODS = [];
    kjson.data.forEach(it => {
        VODS.push({
            vod_name: it.name,
            vod_pic: it.pPic,
            vod_remarks: it.addtime,
            vod_id: `push://${it.viewlink}`
        })
    })
}),
    cate_exclude: '首页|留言|APP|下载|资讯|新闻|动态',
    tab_exclude: '猜你|喜欢|下载|剧情|榜|评论',
    类型: '影视',
    homeUrl: 'https://www.lzpanx.com/',
    二级访问前: '',
    encoding: 'utf-8',
    search_encoding: '',
    图片来源: '',
    图片替换: '',
    play_json: [],
    pagecount: {},
    tab_remove: [],
    tab_order: [],
    tab_rename: {},
}