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
	title: '路漫漫',
	// host:'https://www.96ba.com',
	host: 'https://www.wzwt369.com',
	// url:'/vod/show/id/fyclass/page/fypage.html',
	url: '/vod/show/id/fyclassfyfilter.html',
	filterable: 1,//是否启用分类筛选,
	filter_url: '{{fl.by}}/page/fypage{{fl.year}}',
	filter: {
		"ribendongman": [{ "key": "year", "name": "年份", "value": [{ "n": "全部", "v": "" }, { "n": "2024", "v": "/year/2024" }, { "n": "2023", "v": "/year/2023" }, { "n": "2022", "v": "/year/2022" }, { "n": "2021", "v": "/year/2021" }, { "n": "2020", "v": "/year/2020" }, { "n": "2019", "v": "/year/2019" }, { "n": "2018", "v": "/year/2018" }, { "n": "2017", "v": "/year/2017" }, { "n": "2016", "v": "/year/2016" }, { "n": "2015", "v": "/year/2015" }, { "n": "2014", "v": "/year/2014" }, { "n": "更早", "v": "/year/2013-1980" }] }, { "key": "by", "name": "排序", "value": [{ "n": "更新", "v": "/by/time" }, { "n": "人气", "v": "/by/hits" }, { "n": "评分", "v": "/by/score" }, { "n": "点赞", "v": "/by/up" }] }],
		"guochandongman": [{ "key": "year", "name": "年份", "value": [{ "n": "全部", "v": "" }, { "n": "2024", "v": "/year/2024" }, { "n": "2023", "v": "/year/2023" }, { "n": "2022", "v": "/year/2022" }, { "n": "2021", "v": "/year/2021" }, { "n": "2020", "v": "/year/2020" }, { "n": "2019", "v": "/year/2019" }, { "n": "2018", "v": "/year/2018" }, { "n": "2017", "v": "/year/2017" }, { "n": "2016", "v": "/year/2016" }, { "n": "2015", "v": "/year/2015" }, { "n": "2014", "v": "/year/2014" }, { "n": "更早", "v": "/year/2013-1980" }] }, { "key": "by", "name": "排序", "value": [{ "n": "更新", "v": "/by/time" }, { "n": "人气", "v": "/by/hits" }, { "n": "评分", "v": "/by/score" }, { "n": "点赞", "v": "/by/up" }] }],
		"oumeidongman": [{ "key": "year", "name": "年份", "value": [{ "n": "全部", "v": "" }, { "n": "2024", "v": "/year/2024" }, { "n": "2023", "v": "/year/2023" }, { "n": "2022", "v": "/year/2022" }, { "n": "2021", "v": "/year/2021" }, { "n": "2020", "v": "/year/2020" }, { "n": "2019", "v": "/year/2019" }, { "n": "2018", "v": "/year/2018" }, { "n": "2017", "v": "/year/2017" }, { "n": "2016", "v": "/year/2016" }, { "n": "2015", "v": "/year/2015" }, { "n": "2014", "v": "/year/2014" }, { "n": "更早", "v": "/year/2013-1980" }] }, { "key": "by", "name": "排序", "value": [{ "n": "更新", "v": "/by/time" }, { "n": "人气", "v": "/by/hits" }, { "n": "评分", "v": "/by/score" }, { "n": "点赞", "v": "/by/up" }] }],
		"ribendonghuadianying": [{ "key": "year", "name": "年份", "value": [{ "n": "全部", "v": "" }, { "n": "2024", "v": "/year/2024" }, { "n": "2023", "v": "/year/2023" }, { "n": "2022", "v": "/year/2022" }, { "n": "2021", "v": "/year/2021" }, { "n": "2020", "v": "/year/2020" }, { "n": "2019", "v": "/year/2019" }, { "n": "2018", "v": "/year/2018" }, { "n": "2017", "v": "/year/2017" }, { "n": "2016", "v": "/year/2016" }, { "n": "2015", "v": "/year/2015" }, { "n": "2014", "v": "/year/2014" }, { "n": "更早", "v": "/year/2013-1980" }] }, { "key": "by", "name": "排序", "value": [{ "n": "更新", "v": "/by/time" }, { "n": "人气", "v": "/by/hits" }, { "n": "评分", "v": "/by/score" }, { "n": "点赞", "v": "/by/up" }] }],
		"guochandonghuadianying": [{ "key": "year", "name": "年份", "value": [{ "n": "全部", "v": "" }, { "n": "2024", "v": "/year/2024" }, { "n": "2023", "v": "/year/2023" }, { "n": "2022", "v": "/year/2022" }, { "n": "2021", "v": "/year/2021" }, { "n": "2020", "v": "/year/2020" }, { "n": "2019", "v": "/year/2019" }, { "n": "2018", "v": "/year/2018" }, { "n": "2017", "v": "/year/2017" }, { "n": "2016", "v": "/year/2016" }, { "n": "2015", "v": "/year/2015" }, { "n": "2014", "v": "/year/2014" }, { "n": "更早", "v": "/year/2013-1980" }] }, { "key": "by", "name": "排序", "value": [{ "n": "更新", "v": "/by/time" }, { "n": "人气", "v": "/by/hits" }, { "n": "评分", "v": "/by/score" }, { "n": "点赞", "v": "/by/up" }] }],
		"oumeidonghuadianying": [{ "key": "year", "name": "年份", "value": [{ "n": "全部", "v": "" }, { "n": "2024", "v": "/year/2024" }, { "n": "2023", "v": "/year/2023" }, { "n": "2022", "v": "/year/2022" }, { "n": "2021", "v": "/year/2021" }, { "n": "2020", "v": "/year/2020" }, { "n": "2019", "v": "/year/2019" }, { "n": "2018", "v": "/year/2018" }, { "n": "2017", "v": "/year/2017" }, { "n": "2016", "v": "/year/2016" }, { "n": "2015", "v": "/year/2015" }, { "n": "2014", "v": "/year/2014" }, { "n": "更早", "v": "/year/2013-1980" }] }, { "key": "by", "name": "排序", "value": [{ "n": "更新", "v": "/by/time" }, { "n": "人气", "v": "/by/hits" }, { "n": "评分", "v": "/by/score" }, { "n": "点赞", "v": "/by/up" }] }]
	},
	searchUrl: '/vod/search/page/fypage/wd/**.html',
	searchable: 2,//是否启用全局搜索,
	quickSearch: 0,//是否启用快速搜索,
	headers: {
		'User-Agent': 'MOBILE_UA',
	},
	class_parse: '.container&&.tag.text-light;a&&Text;a&&href;.*/(.*?).html',
	play_parse: true,
	lazy: `js:
		var html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
		var url = html.url;
		var from = html.from;
		if (/m3u8/.test(url)) {
			input = url.split("&")[0]
		} else {
			input
		}
	`,
	limit: 6,
	推荐: '.owl-theme-jable .item;*;*;*;*',
	一级: '#mdym .col-6;h6&&Text;.lazyload&&data-src;.label&&Text;a&&href',
	二级: {
		"title": "h1&&Text;.video-info-aux&&Text",
		"img": ".url_img&&src",
		"desc": ".video-info-items--span:eq(3)&&Text;;;.video-info-actor:eq(1)&&Text;.video-info-actor:eq(0)&&Text",
		"content": ".content-text&&Text",
		"tabs": ".module-tab-content .tab-item",
		"lists": ".scroll-content:eq(#id) a"
	},
	搜索: '*',
}