var rule = {
    title: "路漫漫",
    host: "https://m.lmm52.com",
    url: "/vod/show/id/fyclassfyfilter.html",
    searchUrl: "https://m.lmm52.com/vod/search/page/fypage/wd/**.html",
    searchable: 2,
    quickSearch: 0,
    filterable: 1,
    filter: "H4sIAAAAAAAAAO2Su04CURCG32XqNXu/wKsYitVsAlHRcEs2hISoECuJxqhRYqMFxkIKKFgLXoY9Lm/hHtB1mPqUU87//Tt7kvm6YEN5vwtHUQxlSBez1dcraFAPTyI8d8LjdrQp1mU8mKwvJjLOB+hp29QyLOc30+MobOibAFGbUhtTi1ILU5NSE1ODUgNRs0RoHiAaUBpg6lPqY+pR6mHqUuoWVDzPxMM75c6eWQryp1dkbXsRcX2bJqP/ixTz7kXEuJ8tb+TW++nf1oNYb9Xyj4p/jvvrj8dVkojpHepUa60m6WSfl+nVEHWah6eNnUXp29P3+SKbv6BS+0y+vKKBw0axUUqNctkoNkqpUR4bxUYpNcpno9gopUYFbBQbpdCo3g8SNsur7Q0AAA==",
    filter_url: "{{fl.排序}}{{fl.年代}}/page/fypage",
    filter_def: "",
    headers: {
        "User-Agent": "MOBILE_UA"
    },
    timeout: 5000,
    class_name: "日本动漫&国产动漫&欧美动漫&日本动画电影&国产动画电影&欧美动画电影",
    class_url: "6&7&8&3&4&5",
    class_parse: "",
    cate_exclude: "",
    play_parse: true,
    lazy: $js.toString(() => {
        input = {parse: 1, url: input, js: ''};
    }),
    double: false,
    推荐: "*",
    一级: ".video-img-box;h6.title&&Text;.lazyload&&data-src;.label&&Text;a&&href",
    二级: {
        title: ".page-title&&Text;.tag-link&&Text",
        img: ".module-item-pic&&.lazyload&&src",
        desc: ".video-info-items:eq(3)&&Text;.video-info-items:eq(2)&&Text;;.video-info-items:eq(1)&&Text;.video-info-items:eq(0)&&Text",
        content: ".video-info-content&&Text",
        tabs: ".module-tab-item.tab-item",
        lists: ".module-player-list:eq(#id) a",
        tab_text: "body&&Text",
        list_text: "body&&Text",
        list_url: "a&&href"
    },
    detailUrl: "",
    搜索: "*"
}