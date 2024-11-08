var rule = {
    author: '小可乐/240525/第一版',
    title: '短剧天堂',
    host: 'https://duanjutt.tv',
    hostJs: '',
    headers: {'User-Agent': 'MOBILE_UA'},
    编码: 'utf-8',
    timeout: 5000,

    homeUrl: '/',
    url: '/vodshow/fyfilter---fypage---.html',
    filter_url: '{{fl.cateId}}--{{fl.by}}---{{fl.letter}}',
    detailUrl: '',
    searchUrl: '/vodsearch/**----------fypage---.html',
    searchable: 1,
    quickSearch: 1,
    filterable: 1,

    class_name: '逆袭(1组)&都市(2组)&神医(3组)&脑洞(4组)',
    class_url: '1&20&25&30',
    filter_def: {
        1: {cateId: '1'},
        20: {cateId: '20'},
        25: {cateId: '25'},
        30: {cateId: '30'}
    },

    play_parse: true,
    parse_url: '',
    lazy: `js:
var kcode = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
var kurl = kcode.url;
input = {
parse: 0, url: kurl, header: {"User-Agent": 'MOBILE_UA', "Referer":"https://duanjutt.tv"}
}`,

    limit: 9,
    double: false,
    推荐: '*;*;*;*;*',
    一级: '.myui-vodlist li;a&&title;a&&data-original;.text-right&&Text;a&&href',
    二级: {
//名称;类型
        "title": "h1&&Text;.data:eq(0)&&a:eq(0)&&Text",
//图片
        "img": ".picture&&img&&data-original",
//主要描述;年份;地区;演员;导演
        "desc": ".data:eq(1)&&Text;.data:eq(0)&&a:eq(-1)&&Text;.data:eq(0)&&a:eq(-2)&&Text;.data--span:eq(2)&&Text;.data--span:eq(3)&&Text",
//简介
        "content": ".data:eq(-1)&&Text",
//线路数组
        "tabs": ".nav-tabs:has(li)&&a",
//线路标题
        "tab_text": "body&&Text",
//播放数组 选集列表
        "lists": ".myui-content__list:eq(#id)&&a",
//选集标题
        "list_text": "body&&Text",
//选集链接
        "list_url": "a&&href"
    },
    搜索: '.myui-vodlist__media .thumb;*;*;*;*',

    filter: 'H4sIAAAAAAAAA+3WW0sbQRQH8Pf9GPOcQkxMrb55N97vV3xI7UJFa0HXgoRA2k1UqolWgrFQY1sVYiFewIY2i/hlMruTb+GG/ueMJW95C+zbzm92z8zD+XM2qrEm1ragRdmKvsXa2FLE0MNvmI+tRd7p7tq5s3huz11/iKxuurAQZWsuV+Lb4mehyu6iicV8/9jJfOPX38EBYvH10P64Bw6qt68eRfEzuJm4spNyMmfgEIstxnx0vVXdMPR1dT1eyNo3qZrr8WS+YuZRggq3A9pJOiAdJJ2QTpIuSBdJN6SbpAfSQ9IL6SXpg/SRhCFhkn5IP8kAZIBkEDJIMgQZIhmGDJOMQEZIRiGjJGOQMZJxyDjJBGSCZBIySTIFmSKZhkyTzEBmSGYhsyRzkDmSecg8if9FK6z69F+vvN5SfWKnj3jpoKZP7Gyxkr1HAWPZfVXWLZdK9m0GO2+XjQ3VzDcJvruNnY2l9+t69Vht0aexgL+eKJkP/M8nmRm/Skf6tmydi3zcNpNyVyWNH1yIc/LAc6/5SiXO3j1xLnPSm71sedlqmGyF6siW2+x835L9HlLZusyJu1/SX6rzi0lhPkhvUX64z69Ppb9SabtIla0d6a1enrw8NUqegvXMKpH4Yt/L+RFUs0r8PuFXj9Kf/Q+mE/yvzF9QTSnHLIgfcelqPvFksWwdS/fmk5enxsiTFnsC8UnvbkgNAAA='
}