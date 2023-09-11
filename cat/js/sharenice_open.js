// 搜索滑块验证
import { load, _ } from './lib/cat.js';

let key = '短视频';
let HOST = 'http://www.sharenice.net';
let siteKey = '';
let siteType = 0;
let PC_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36';

async function request(reqUrl, agentSp) {
    let res = await req(reqUrl, {
        method: 'get',
        headers: {
            'User-Agent': agentSp || PC_UA,
        },
    });
    return res.content;
}

async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
}

function clsjoin(cls) {
    _.each(cls, (s) => {
        let typeId = s.attribs['href'];
        typeId = typeId.substring(typeId.lastIndexOf('t/') + 2);
        classes.push({
            type_id: typeId,
            type_name: s.children[0].data,
        });
    });
}

let classes = [];
async function home(filter) {
    let filterObj = {};
    let html = await request(HOST);
    let $ = load(html);
    let series = $('div.nav > ul > li > a[href*=net/]');
    let tag = $('div.hot-tags-list > a[href*=net]');
    clsjoin(series);
    clsjoin(tag);
    return JSON.stringify({
        class: classes,
        filters: filterObj,
    });
}

async function homeVod() {
    let link = HOST + '/t-576O5aWz';
    let html = await request(link);
    let $ = load(html);
    let items = $('div.item-box ul li');
    let videos = _.map(items, (item) => {
        let a = $(item).find('a:first')[0];
        let img = $(item).find('img:first')[0];
        return {
            vod_id: a.attribs.href,
            vod_name: a.attribs.title,
            vod_pic: img.attribs['data-original'],
            vod_remarks: '',
        };
    });
    return JSON.stringify({
        list: videos,
    });
}

async function category(tid, pg, filter, extend) {
    if (pg <= 0 || typeof(pg) == 'undefined') pg = 1;
    let link = HOST + '/' + tid + '?page=' + pg;
    let html = await request(link);
    let $ = load(html);
    let items = $('div.item-box ul li');
    let videos = _.map(items, (item) => {
        let a = $(item).find('a:first')[0];
        let img = $(item).find('img:first')[0];
        return {
            vod_id: a.attribs.href,
            vod_name: a.attribs.title,
            vod_pic: img.attribs['data-original'],
            vod_remarks: '',
        };
    });
    let hasMore = $('ul.pagination > li > a:contains(»)').length > 0;
    let pgCount = hasMore ? parseInt(pg) + 1 : parseInt(pg);
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: 16,
        total: 16 * pgCount,
        list: videos,
    });
}

async function detail(id) {
    let vod = {
        vod_id: id,
        vod_remarks: '',
    };
    let playlist = ['观看视频' + '$' + id];
    vod.vod_play_from = '道长在线';
    vod.vod_play_url = playlist.join('#');
    return JSON.stringify({
        list: [vod],
    });
}

async function play(flag, id, flags) {
    let html = await request(id);
    let $ = load(html);
    let playUrl = $('div.video-play-box').find('video:first')[0].attribs.src + '#.mp4';
    return JSON.stringify({
        parse: 0,
        url: playUrl,
    });
}

async function search(wd, quick, pg) {
    return '{}';
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