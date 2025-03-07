var rule = {
    类型: '影视',//影视|听书|漫画|小说
    title: '爱看短剧[盘]',
    host: 'https://ys.110t.cn/',
    homeUrl: '/api/ajax.php?act=recommend',
    homeUrl: '/api/ajax.php?act=Daily',
    url: '/api/ajax.php?act=fyclass',
    searchUrl: '/api/ajax.php?act=search&name=**',
    searchable: 1,
    quickSearch: 0,
    filterable: 0,
    headers: {
        'User-Agent': 'MOBILE_UA',
    },
    hikerListCol: "text_1",
    hikerClassListCol: "text_1",
    timeout: 5000,
    class_name: '全部',
    class_url: 'yingshilist',
    play_parse: true,
    lazy: $js.toString(() => {
        input = "push://" + input;
    }),
    double: false,
    推荐: '*',
    一级: 'json:data;name;;addtime;url',
    二级: '*',
    搜索: '*',
}