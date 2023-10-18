import { _ } from 'assets://js/lib/cat.js';

let host = 'http://live.yj1211.work';
let categories = '';
let siteKey = '';
let siteType = 0;

const MOBILE_UA = 'Mozilla/5.0 (Linux; Android 11; M2007J3SC Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045714 Mobile Safari/537.36';

async function requestRaw(reqUrl, redirect) {
    let resRaw = await req(reqUrl, {
        method: 'get',
        headers: {
            'User-Agent': MOBILE_UA,
        },
        redirect: redirect,
    });
    return resRaw;
}

async function request(reqUrl) {
    let resRaw = await requestRaw(reqUrl, 1)
    return resRaw.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
    if (cfg.hasOwnProperty('ext')) {
        if (cfg.ext.hasOwnProperty('categories')) {
            categories = cfg.ext.categories;
        }
        if (cfg.ext.hasOwnProperty('host')) {
            host = cfg.ext.host;
        }
    }
}

async function home(filter) {
    let classes = [];
    if (categories.length > 0) {
        classes = categories.split('#');
    }
    classes.unshift('首页');
    const filterObj = {};
    return JSON.stringify({
        class: _.map(classes, (it) => {
            return {
                type_id: it,
                type_name: it,
                land: 1,
                ratio: 1.78,
            }
        }),
        filters: filterObj,
    });
}

async function homeVod() {
    return '{}';
}

async function category(tid, pg, filter, extend) {
    if (pg <= 0 || typeof pg == 'undefined') pg = 1;
    let url = '';
    if (tid == '首页') {
        url = host + '/api/live/getRecommendByPlatform?platform=douyu&size=20&page=' + pg;
    } else {
        url = host + '/api/live/getRecommendByPlatformArea?platform=douyu&size=20&area=' + tid + '&page=' + pg;
    }
    const data = JSON.parse(await request(url));
    let videos = _.map(data.data, (it) => {
        return {
            vod_id: it.roomId,
            vod_name: it.roomName,
            vod_pic: it.roomPic,
            vod_remarks: it.ownerName,
        }
    });
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: 9999,
        limit: 90,
        total: 999999,
        list: videos,
    });
}

async function detail(id) {
    const data = JSON.parse(await request(host + '/api/live/getRoomInfo?platform=douyu&roomId=' + id));
    const video = data.data;
    let vod = {
        vod_id: video.roomId,
        vod_name: video.roomName,
        vod_pic: video.roomPic,
        vod_remarks: video.categoryName,
        type_name: video.categoryName,
        vod_director: video.ownerName,
        vod_actor: '',
        vod_content: video.online + '人在线',
        vod_year: '',
        vod_area: '',   
    };
    vod.vod_play_from = video.platForm;
    vod.vod_play_url = 'Live$' + id;
    return JSON.stringify({
        list: [vod],
    });
}

async function play(flag, id, flags) {
    const resp = await requestRaw('https://getplayurl.lmteam.repl.co/live?platform=douyu&rid=' + id, 0);
    const headers = resp.headers;
    let url = "";
    if (headers.hasOwnProperty('location')) {
        url = headers.location;
    }
    return JSON.stringify({
        parse: 0,
        url: url,
    });
}

async function search(wd, quick) {
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