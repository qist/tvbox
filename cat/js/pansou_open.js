import { load, _ } from 'assets://js/lib/cat.js';
import { log } from './lib/utils.js';
import { initAli, detailContent, playContent } from './lib/ali.js';

let siteKey = 'pansou';
let siteType = 0;
let siteUrl = 'https://www.alipansou.com';
let patternAli = /(https:\/\/www\.(aliyundrive|alipan)\.com\/s\/[^"]+)/

const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1';

async function requestRaw(reqUrl, headers, redirect) {
    let res = await req(reqUrl, {
        method: 'get',
        headers: headers || {
            'User-Agent': UA,
            'Referer': siteUrl,
        },
        redirect: redirect,
    });
    return res;
}

async function request(reqUrl) {
    let resRaw = await requestRaw(reqUrl);
    return resRaw.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    try {
        siteKey = _.isEmpty(cfg.skey) ? '' : cfg.skey;
        siteType = _.isEmpty(cfg.stype) ? '' : cfg.stype;
        await initAli(cfg);
    } catch (e) {
        await log('init:' + e.message + ' line:' + e.lineNumber);
    }
}

async function home(filter) {
    return '{}';
}

async function homeVod() {}

async function category(tid, pg, filter, extend) {
    return '{}';
}

async function detail(id) {
    try {
        let matches = id.match(patternAli);
        if (!_.isEmpty(matches)) return await detailContent(matches[0]);
        let url = siteUrl + id.replace("/s/", "/cv/");
        const data = await requestRaw(url, getHeaders(id), 0);
        const headers = data.headers;
        const resp = data.content;
        if (headers.hasOwnProperty('location')) {
            url = headers['location'].replace('/redirect?visit=', 'https://www.aliyundrive.com/s/');
            return await detailContent(url);
        } else if (!_.isEmpty(resp)) {
            const $ = load(resp);
            url = $('a:first').attr('href').replace('/redirect?visit=', 'https://www.aliyundrive.com/s/');
            return await detailContent(url);
        }
        return '';
    } catch (e) {
        await log('detail:' + e.message + ' line:' + e.lineNumber);
    }
}

function getHeaders(id) {
    return {
        "User-Agent": UA,
        "Referer": siteUrl + id,
        "_bid": "6d14a5dd6c07980d9dc089a693805ad8",
    };
}

async function play(flag, id, flags) {
    try {
        return await playContent(flag, id, flags);
    } catch (e) {
        await log('play:' + e.message + ' line:' + e.lineNumber);
    }
}

async function search(wd, quick, pg) {
    if (pg <= 0) pg = 1;
    const limit = 10;
    const html = await request(siteUrl + "/search?k=" + encodeURIComponent(wd) + "&page=" + pg + "&s=0&t=-1");
    const $ = load(html);
    const items = $('van-row > a');
    const videos = _.map(items, (item) => {
        let title = $(item).find('template:first').text().trim();
        return {
            vod_id: item.attribs.href,
            vod_name: title,
            vod_pic: 'https://inews.gtimg.com/newsapp_bt/0/13263837859/1000',
        };
    });
    const pageCount = $('van-pagination').attr('page-count') || pg;
    const pgCount = parseInt(pageCount);
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: limit,
        total: limit * pgCount,
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