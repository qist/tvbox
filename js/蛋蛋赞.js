var rule = {
    title: '蛋蛋赞',
    host: 'https://www.ddzvod.com',
    // url:'/fyclass/index_fypage.html[/fyclass/index.html]', 
    // url: '/index.php/vod/show/id/fyclass/page/fypage.html',
    url: '/index.php/vod/show/id/fyfilter.html',
    filterable: 1,//是否启用分类筛选,
    filter_url: '{{fl.cateId}}{{fl.area}}{{fl.by or "/by/time"}}/page/fypage{{fl.year}}',
    filter: {
        "1": [{ "key": "cateId", "name": "分类", "value": [{ "n": "全部", "v": "1" }, { "n": "动作片", "v": "6" }, { "n": "喜剧片", "v": "7" }, { "n": "爱情片", "v": "8" }, { "n": "科幻片", "v": "9" }, { "n": "恐怖片", "v": "10" }, { "n": "剧情片", "v": "11" }, { "n": "奇幻片", "v": "30" }, { "n": "战争片", "v": "12" }, { "n": "犯罪片", "v": "54" }, { "n": "动漫电影", "v": "55" }] }, { "key": "area", "name": "地区", "value": [{ "n": "全部", "v": "" }, { "n": "大陆", "v": "/area/大陆" }, { "n": "香港", "v": "/area/香港" }, { "n": "台湾", "v": "/area/台湾" }, { "n": "美国", "v": "/area/美国" }, { "n": "法国", "v": "/area/法国" }, { "n": "英国", "v": "/area/英国" }, { "n": "日本", "v": "/area/日本" }, { "n": "韩国", "v": "/area/韩国" }, { "n": "德国", "v": "/area/德国" }, { "n": "泰国", "v": "/area/泰国" }, { "n": "印度", "v": "/area/印度" }, { "n": "意大利", "v": "/area/意大利" }, { "n": "西班牙", "v": "/area/西班牙" }, { "n": "加拿大", "v": "/area/加拿大" }, { "n": "其他", "v": "/area/其他" }] }, { "key": "year", "name": "年代", "value": [{ "n": "全部", "v": "" }, { "n": "2024", "v": "/year/2024" }, { "n": "2023", "v": "/year/2023" }, { "n": "2022", "v": "/year/2022" }, { "n": "2021", "v": "/year/2021" }, { "n": "2020", "v": "/year/2020" }, { "n": "2019", "v": "/year/2019" }, { "n": "2018", "v": "/year/2018" }, { "n": "2017", "v": "/year/2017" }, { "n": "2016", "v": "/year/2016" }, { "n": "2015", "v": "/year/2015" }, { "n": "2014", "v": "/year/2014" }, { "n": "2013", "v": "/year/2013" }, { "n": "2012", "v": "/year/2012" }, { "n": "2011", "v": "/year/2011" }, { "n": "2010", "v": "/year/2010" }] }, { "key": "by", "name": "排序", "value": [{ "n": "时间", "v": "/by/time" }, { "n": "人气", "v": "/by/hits" }, { "n": "评分", "v": "/by/score" }] }],
        "2": [{ "key": "cateId", "name": "分类", "value": [{ "n": "全部", "v": "2" }, { "n": "国产剧", "v": "13" }, { "n": "港台剧", "v": "14" }, { "n": "日韩剧", "v": "15" }, { "n": "欧美剧", "v": "16" }, { "n": "海外剧", "v": "31" }, { "n": "纪录片", "v": "20" }] }, { "key": "area", "name": "地区", "value": [{ "n": "全部", "v": "" }, { "n": "内地", "v": "/area/内地" }, { "n": "韩国", "v": "/area/韩国" }, { "n": "香港", "v": "/area/香港" }, { "n": "台湾", "v": "/area/台湾" }, { "n": "日本", "v": "/area/日本" }, { "n": "美国", "v": "/area/美国" }, { "n": "泰国", "v": "/area/泰国" }, { "n": "英国", "v": "/area/英国" }, { "n": "新加坡", "v": "/area/新加坡" }, { "n": "其他", "v": "/area/其他" }] }, { "key": "year", "name": "年代", "value": [{ "n": "全部", "v": "" }, { "n": "2024", "v": "/year/2024" }, { "n": "2023", "v": "/year/2023" }, { "n": "2022", "v": "/year/2022" }, { "n": "2021", "v": "/year/2021" }, { "n": "2020", "v": "/year/2020" }, { "n": "2019", "v": "/year/2019" }, { "n": "2018", "v": "/year/2018" }, { "n": "2017", "v": "/year/2017" }, { "n": "2016", "v": "/year/2016" }, { "n": "2015", "v": "/year/2015" }, { "n": "2014", "v": "/year/2014" }, { "n": "2013", "v": "/year/2013" }, { "n": "2012", "v": "/year/2012" }, { "n": "2011", "v": "/year/2011" }, { "n": "2010", "v": "/year/2010" }, { "n": "2009", "v": "/year/2009" }, { "n": "2008", "v": "/year/2008" }, { "n": "2006", "v": "/year/2006" }, { "n": "2005", "v": "/year/2005" }, { "n": "2004", "v": "/year/2004" }] }, { "key": "by", "name": "排序", "value": [{ "n": "时间", "v": "/by/time" }, { "n": "人气", "v": "/by/hits" }, { "n": "评分", "v": "/by/score" }] }],
        "3": [{ "key": "cateId", "name": "分类", "value": [{ "n": "全部", "v": "3" }, { "n": "国产综艺", "v": "27" }, { "n": "日韩综艺", "v": "28" }, { "n": "欧美综艺", "v": "29" }] }, { "key": "area", "name": "地区", "value": [{ "n": "全部", "v": "" }, { "n": "内地", "v": "/area/内地" }, { "n": "港台", "v": "/area/港台" }, { "n": "日韩", "v": "/area/日韩" }, { "n": "欧美", "v": "/area/欧美" }] }, { "key": "year", "name": "年代", "value": [{ "n": "全部", "v": "" }, { "n": "2024", "v": "/year/2024" }, { "n": "2023", "v": "/year/2023" }, { "n": "2022", "v": "/year/2022" }, { "n": "2021", "v": "/year/2021" }, { "n": "2020", "v": "/year/2020" }, { "n": "2019", "v": "/year/2019" }, { "n": "2018", "v": "/year/2018" }, { "n": "2017", "v": "/year/2017" }, { "n": "2016", "v": "/year/2016" }, { "n": "2015", "v": "/year/2015" }, { "n": "2014", "v": "/year/2014" }, { "n": "2013", "v": "/year/2013" }, { "n": "2012", "v": "/year/2012" }, { "n": "2011", "v": "/year/2011" }, { "n": "2010", "v": "/year/2010" }, { "n": "2009", "v": "/year/2009" }, { "n": "2008", "v": "/year/2008" }, { "n": "2007", "v": "/year/2007" }, { "n": "2006", "v": "/year/2006" }, { "n": "2005", "v": "/year/2005" }, { "n": "2004", "v": "/year/2004" }] }, { "key": "by", "name": "排序", "value": [{ "n": "时间", "v": "/by/time" }, { "n": "人气", "v": "/by/hits" }, { "n": "评分", "v": "/by/score" }] }],
        "4": [{ "key": "cateId", "name": "分类", "value": [{ "n": "全部", "v": "4" }, { "n": "国产动漫", "v": "24" }, { "n": "日韩动漫", "v": "25" }, { "n": "欧美动漫", "v": "26" }] }, { "key": "area", "name": "地区", "value": [{ "n": "全部", "v": "" }, { "n": "国产", "v": "/area/国产" }, { "n": "日本", "v": "/area/日本" }, { "n": "欧美", "v": "/area/欧美" }, { "n": "其他", "v": "/area/其他" }] }, { "key": "year", "name": "年代", "value": [{ "n": "全部", "v": "" }, { "n": "2024", "v": "/year/2024" }, { "n": "2023", "v": "/year/2023" }, { "n": "2022", "v": "/year/2022" }, { "n": "2021", "v": "/year/2021" }, { "n": "2020", "v": "/year/2020" }, { "n": "2019", "v": "/year/2019" }, { "n": "2018", "v": "/year/2018" }, { "n": "2017", "v": "/year/2017" }, { "n": "2016", "v": "/year/2016" }, { "n": "2015", "v": "/year/2015" }, { "n": "2014", "v": "/year/2014" }, { "n": "2013", "v": "/year/2013" }, { "n": "2012", "v": "/year/2012" }, { "n": "2011", "v": "/year/2011" }, { "n": "2010", "v": "/year/2010" }, { "n": "2009", "v": "/year/2009" }, { "n": "2008", "v": "/year/2008" }, { "n": "2007", "v": "/year/2007" }, { "n": "2006", "v": "/year/2006" }, { "n": "2005", "v": "/year/2005" }, { "n": "2004", "v": "/year/2004" }] }, { "key": "by", "name": "排序", "value": [{ "n": "时间", "v": "/by/time" }, { "n": "人气", "v": "/by/hits" }, { "n": "评分", "v": "/by/score" }] }]
    },
    filter_def: {
        1: { cateId: '1' },
        2: { cateId: '2' },
        3: { cateId: '3' },
        4: { cateId: '4' }
    },
    searchUrl: '/index.php/vod/search/page/fypage/wd/**.html',
    searchable: 2,//是否启用全局搜索,
    quickSearch: 0,//是否启用快速搜索,
    headers: {
        'User-Agent': 'MOBILE_UA',
    },
    class_parse: 'div.nav&&li:gt(0):lt(5);a&&Text;a&&href;(\\d+).html',
    play_parse: true,
    lazy: `js:
        var html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
        var url = html.url;
        if (html.encrypt == '1') {
            url = unescape(url)
        } else if (html.encrypt == '2') {
            url = unescape(base64Decode(url))
        }
        if (/\\.m3u8|\\.mp4/.test(url)) {
            input = {
                jx: 0,
                url: url,
                parse: 0
            }
        } else {
            input
        }
    `,
    推荐: 'div.bd:eq(0);.lists-content:eq(0)&&li;*;*;*;*',
    一级: '.lists-content:eq(1)&&li;a&&title;a&&data-original;.note&&Text;a&&href',
    double: true, // 推荐内容是否双层定位
    二级: {
        "title": ".product-title--span&&Text;.product-excerpt:eq(2)&&span&&Text",
        "img": ".thumb&&src",
        "desc": ".product-excerpt:eq(3)&&Text;;;.product-excerpt:eq(1)&&span&&Text;.product-excerpt:eq(0)&&span&&Text",
        "content": ".product-excerpt:eq(4)&&Text",
        "tabs": "#slider dt",
        "lists": ".playlist:eq(#id) li"
    },
    搜索: '.lists-content&&li;*;*;*;*',
}