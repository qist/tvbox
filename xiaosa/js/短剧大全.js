var rule = {
    类型: '影视', //影视|听书|漫画|小说
    title: '短剧',
    host: 'https://ai-img.ycubbs.cn/',
    homeUrl: '/api/duanju/list',
    url: '/api/duanju/list',
    searchUrl: 'https://api.kuleu.com/api/action?text=**',
    searchable: 1,
    quickSearch: 0,
    filterable: 0,
    headers: {
        'User-Agent': 'MOBILE_UA',
    },
    hikerListCol: "text_1",
    hikerClassListCol: "text_1",
    timeout: 5000,
    class_name: '',
    class_url: '',
    play_parse: true,
    lazy: $js.toString(() => {
        input = "push://" + input;
    }),
    double: false,
    推荐: '*',
    一级: 'json:data;name;;;url',
    二级: '*',
    搜索: 'json:data;name;;;viewlink',
}