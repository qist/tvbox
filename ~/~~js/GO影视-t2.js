var rule = {
    author: '小可乐/240701/第一版',
    title: 'GO影视',
    类型: '影视',
    host: 'https://www.goys.cc',
    hostJs: '',
    headers: {'User-Agent': 'MOBILE_UA'},
    编码: 'utf-8',
    timeout: 5000,

    homeUrl: '/',
    url: '/vodshow/fyfilter.html',
    filter_url: '{{fl.cateId}}-{{fl.area}}-{{fl.by}}-{{fl.class}}-{{fl.lang}}-{{fl.letter}}---fypage---{{fl.year}}',
    detailUrl: '',
    searchUrl: '/vodsearch/**----------fypage---.html',
    searchable: 1,
    quickSearch: 1,
    filterable: 1,

    class_name: '电影&剧集&综艺&动漫&短剧&番剧',
    class_url: '1&2&3&4&30&31',
    filter_def: {
        1: {cateId: '1'},
        2: {cateId: '2'},
        3: {cateId: '3'},
        4: {cateId: '4'},
        30: {cateId: '30'},
        31: {cateId: '31'}
    },

    play_parse: true,
    lazy: `js:
let kcode = JSON.parse(request(input).match(/var player_.*?=(.*?)</)[1]);
let kurl = kcode.url;
let kjiexi = HOST + '/paly/goys/?url=';
if (/\\.(m3u8|mp4)/.test(kurl)) {
input = { jx: 0, parse: 0, url: kurl };
} else {
input = { jx: 0, parse: 1, url: kjiexi + kurl };
}
`,

    limit: 9,
    double: false,
    推荐: '*',
    一级: '.module-item;a:eq(0)&&title;img&&data-src;.module-item-text&&Text;a:eq(0)&&href',
    二级: {
        title: 'h1&&Text;.tag-link:eq(1)&&Text',
        img: '.video-cover&&img&&data-src',
        desc: '.video-info-items:eq(-2)&&Text;.tag-link:eq(-2)&&Text;.tag-link:eq(-1)&&Text;.video-info-actor:eq(1)&&Text;.video-info-actor:eq(0)&&Text',
        content: '.vod_content&&span&&Text',
        tabs: '.tab-item span',
        tab_text: 'body&&Text',
        lists: '.sort-item:eq(#id)&&a',
        list_text: 'body&&Text',
        list_url: 'a&&href',
    },
    搜索: '.module-search-item;.video-serial&&title;*;.video-serial&&Text;.video-serial&&href',

    filter: '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'
}