var rule = {
    author: '小可乐/240526/第一版',
    title: '动漫巴士',
    host: 'http://dm84.site',
    hostJs: 'print(HOST);let html=request(HOST,{headers:{"User-Agent":MOBILE_UA}});let src= jsp.pdfh(html,"ul&&a:eq(0)&&href");print(src);HOST=src',
    headers: {'User-Agent': 'MOBILE_UA'},
    编码: 'utf-8',
    timeout: 5000,

    homeUrl: '/',
    url: '/show-fyclass--fyfilter-fypage.html',
    filter_url: '{{fl.by}}-{{fl.class}}--{{fl.year}}',
    detailUrl: '',
    searchUrl: '/s-**---------fypage.html',
    searchable: 1,
    quickSearch: 1,
    filterable: 1,

    class_name: '国产动漫&日本动漫&欧美动漫&电影',
    class_url: '1&2&3&4',
    filter_def: {},

    proxy_rule: '',
    sniffer: 0,
    isVideo: '',
    play_parse: true,
    parse_url: '',
    lazy: `js:
let html = request(input);
let kurl = pdfh(html,'body&&iframe').match(/src="(.*?)"/)[1];
input= kurl
`,

    limit: 9,
    double: false,
    推荐: '*',
//列表;标题;图片;描述;链接;详情(可不写)
    一级: '.v_list li;a&&title;a&&data-bg;.desc&&Text;a&&href',
    二级: {
//名称;类型
        "title": "h1&&Text;meta[name*=class]&&content",
//图片
        "img": "img&&src",
//主要描述;年份;地区;演员;导演
        "desc": "meta[name*=update_date]&&content;meta[name*=release_date]&&content;meta[name*=area]&&content;meta[name*=actor]&&content;meta[name*=director]&&content",
//简介
        "content": "p:eq(-2)&&Text",
//线路数组
        "tabs": ".tab_control&&li",
//线路标题
        "tab_text": "body&&Text",
//播放数组 选集列表
        "lists": ".play_list:eq(#id)&&a",
//选集标题
        "list_text": "body&&Text",
//选集链接
        "list_url": "a&&href"
    },
    搜索: '*',

    filter: 'H4sIAAAAAAAAA+2WbUsqQRTH3+/HmNe+0LWn21eJXlgIRU+Q3UBEsLTaCrYtSm9cb2RQ2YOVFUFa9mWcGf0Wjc6cMxPFstDlcgXf7e/39+zo2XPUlEUiZHTMSpGZeJKMksnZWCJBQmQ+NhcXyKt1erQteDk2+1OIsRSZF5quldvZckcLIOmQsqcb9LmurALImPOL5QsqUwAZd3O6TgFmF2+tpy3IJGB2vmvUScDzKmfNxjGcJwHrspVWKQN1EiBrZV55w1WZArynd8Svd+GeEvCzb5VZZoW9XPF97ICp0uPpEDY5GY8t6h6zwlO78Biwx3bYHlCue2n4qPZR00e0j5je1t42fVj7sOEjP9CLS8OPaD9i+mHth00/pP2Q6Qe1H/zYr4mk0S13j9Z2PnVLN1HA0rR4Kdy5Wauxu32VTE0vJfSzvs1RZ10licmFxXjnWGs8ZBH7r+3E+l778AImQkKQnfDbJeq59OYKMgl6Dqv0rYAT2AU877hEf1fgPAlBdoIVa+LdQZ2EIDvBVq95HjMJmN3XWc6BTAK+l8MG9SBTgHUrHsvkoU4CZm6Ze/A8Fei6be5Usa4LmD2U2n9O+MElxMj9re2prY3+z1vr92vlW+e3mT7b9+UW9ee5l+Z54F/Ms/ib0nwt6v8sHfj2POeLdPMc6iQE+eb3nWenyrJrcJ6E/jz3zjxb6XeqCRqqbAwAAA=='
}