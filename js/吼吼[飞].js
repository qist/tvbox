muban.短视2.二级.img = '.detail-pic&&img&&data-src';
var rule = {
    title: '吼吼[飞]',
    模板:'短视2',
    host: 'https://ihoho.tv',
    homeUrl:'/label/rb.html',
	// url: '/index.php/api/vod#type=fyclass&page=fypage',
    url: '/index.php/api/vod#type=fyfilter&page=fypage',
    filterable:1,//是否启用分类筛选,
    filter_url:'{{fl.cateId}}',
    filter:{
        "1":[{"key":"cateId","name":"分类","value":[{"n":"全部","v":"1"},{"n":"动作片","v":"6"},{"n":"喜剧片","v":"7"},{"n":"爱情片","v":"8"},{"n":"科幻片","v":"9"},{"n":"恐怖片","v":"10"},{"n":"剧情片","v":"11"},{"n":"战争片","v":"12"},{"n":"灾难片","v":"29"},{"n":"悬疑片","v":"32"},{"n":"冒险片","v":"30"}]}],
        "2":[{"key":"cateId","name":"分类","value":[{"n":"全部","v":"2"},{"n":"国产剧","v":"13"},{"n":"港台剧","v":"14"},{"n":"日韩剧","v":"15"},{"n":"美剧","v":"16"}]}]
    },
    filter_def:{
        1:{cateId:'1'},
        2:{cateId:'2'},
        3:{cateId:'3'},
        4:{cateId:'4'},
        20:{cateId:'20'},
        37:{cateId:'37'}
    },
	class_name:'电影&连续剧&综艺&动漫&纪录片&电影解说',
    class_url:'1&2&3&4&20&37',
    headers:{
        'User-Agent':'PC_UA',
    },
    detailUrl:'/vod/detail/id/fyid.html',
    play_parse: true,
    lazy:`js:
        var html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
        var url = html.url;
        if (html.encrypt == '1') {
            url = unescape(url)
        } else if (html.encrypt == '2') {
            url = unescape(base64Decode(url))
        }
        if (/m3u8|mp4/.test(url)) {
            input = url
        } else {
            input
        }
    `,
    推荐:'.border-box .public-list-box;a&&title;.lazy&&data-src;.public-list-prb&&Text;a&&href',
    一级:`js:
        let body = input.split("#")[1];
        let t = Math.round(new Date / 1e3).toString();
        let key = md5("DS" + t + "DCC147D11943AF75");
        let url = input.split("#")[0];
        body = body + "&time=" + t + "&key=" + key;
        print(body);
        fetch_params.body = body;
        let html = post(url, fetch_params);
        let data = JSON.parse(html);
        VODS = data.list.map(function(it) {
            it.vod_pic = urljoin2(input.split("/in")[0], it.vod_pic);
            return it
        });
    `,
}