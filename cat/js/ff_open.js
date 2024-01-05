import { Crypto, load, _, jinja2 } from './lib/cat.js';

let key = 'ff';
let HOST = 'https://cj.ffzyapi.com';
let siteKey = '';
let siteType = 0;

const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1';

async function request(reqUrl, agentSp) {
    let res = await req(reqUrl, {
        method: 'get',
        headers: {
            'User-Agent': agentSp || UA,
            'Referer': HOST
        },
    });
    return res.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
}

async function home(filter) {
    let classes = [{"type_id":1,"type_name":"电影"},{"type_id":2,"type_name":"追剧"},{"type_id":3,"type_name":"综艺"},{"type_id":4,"type_name":"动漫"}];
    let filterObj = {
		"2":[{"key":"cateId","name":"类型","value":[{"n":"全部","v":"2"},{"n":"短剧","v":"36"},{"n":"陆剧","v":"13"},{"n":"韩剧","v":"15"},{"n":"欧美剧","v":"16"},{"n":"港剧","v":"14"},{"n":"台剧","v":"21"},{"n":"日剧","v":"22"},{"n":"海外剧","v":"23"},{"n":"泰剧","v":"24"},{"n":"纪录片","v":"20"}]}],
		"1":[{"key":"cateId","name":"类型","value":[{"n":"全部","v":"1"},{"n":"动作片","v":"6"},{"n":"喜剧片","v":"7"},{"n":"爱情片","v":"8"},{"n":"科幻片","v":"9"},{"n":"恐怖片","v":"10"},{"n":"剧情片","v":"11"},{"n":"战争片","v":"12"}]}],
		"3":[{"key":"cateId","name":"类型","value":[{"n":"全部","v":"3"},{"n":"国综","v":"25"},{"n":"港综","v":"26"},{"n":"韩日综","v":"27"},{"n":"欧美综","v":"28"}]}],
		"4":[{"key":"cateId","name":"类型","value":[{"n":"全部","v":"4"},{"n":"国漫","v":"29"},{"n":"日韩动漫","v":"30"},{"n":"欧美动漫","v":"31"},{"n":"港漫","v":"32"},{"n":"海外动漫","v":"33"}]}]
	};

    return JSON.stringify({
        class: classes,
        filters: filterObj,
    });
}

async function homeVod() {}

async function category(tid, pg, filter, extend) {
    if (pg <= 0) pg = 1;
    let data = JSON.parse(await request(HOST + '/index.php/ajax/data?mid=1&tid=' + (extend.cateId || tid) + '&page=' + pg + '&limit=20'));
   
    let videos = [];
    for (const vod of data.list) {
        videos.push({
            vod_id: vod.vod_id,
            vod_name: vod.vod_name,
            vod_pic: vod.vod_pic,
            vod_remarks: '',
        });
    }
    return JSON.stringify({
        page: parseInt(data.page),
        pagecount: data.pagecount,
        limit: 20,
        total: data.total,
        list: videos,
    });
}

async function detail(id) {
    var html = await request( HOST + '/index.php/vod/detail/id/' + id + '.html');
    var $ = load(html);
    var vod = {
        vod_id: id,
        vod_name: $('h1:first').text().trim(),
        vod_type: $('.stui-content__detail p:first a').text(),
        vod_actor: $('.stui-content__detail p:nth-child(3)').text().replace('主演：',''),
        vod_pic: $('.stui-content__thumb img:first').attr('data-original'),
        vod_remarks : $('.stui-content__detail p:nth-child(5)').text() || '',
        vod_content: $('span.detail-content').text().trim(),
    };
     const playlist = _.map($('div.ffm3u8 > li > a[target*=_blank]'), (it) => {
        return it.attribs.title + '$' + it.attribs.href;
    });
    vod.vod_play_from = "非凡直达";
    vod.vod_play_url = playlist.join('#');
    return JSON.stringify({
        list: [vod],
    });
}
async function play(flag, id, flags) {
    return JSON.stringify({
        parse: 0,
        url: id,
    });
}

async function search(wd, quick, pg) {
      if (pg <= 0) pg = 1;
    let data = JSON.parse(await request(HOST + '/api.php/provide/vod/?wd=' + wd + '&pg=' +pg + '&ac=detail'));///api.php/provide/vod/?wd=搜索词&pg=翻页&ac=detail

    let videos = [];
    for (const vod of data.list) {
        videos.push({
            vod_id: vod.vod_id,
            vod_name: vod.vod_name,
            vod_pic: vod.vod_pic,
            vod_remarks: '',
        });
    }
    return JSON.stringify({
        page: parseInt(data.page),
        pagecount: data.pagecount,
        limit: 20,
        total: data.total,
        list: videos,
    });
}

export function __jsEvalReturn() {
    return {
        init: init,
        home: home,
        homeVod: homeVod,
        category: category,
        detail: detail,
        play: play,
        search: search,
    };
}