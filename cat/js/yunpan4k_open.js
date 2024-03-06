import { load, _ } from 'assets://js/lib/cat.js';
import { log } from './lib/utils.js';
import { initAli, detailContent, playContent } from './lib/ali.js';

let siteKey = 'yunpan4k';
let siteType = 0;
let siteUrl = 'https://www.codelicence.cn';
let patternAli = /(https:\/\/www\.(aliyundrive|alipan)\.com\/s\/[^"]+)/;

const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1';

async function requestRaw(reqUrl, method, data, redirect) {
    let res = await req(reqUrl, {
        method: method || 'get',
        headers: {
            'User-Agent': UA,
            'Referer': siteUrl,
        },
        data: data,
        postType: method === 'post' ? 'form' : '',
        redirect: redirect == 0 ? 0 : 1,
    });
    return res;
}

async function request(reqUrl, method, data) {
    let resRaw = await requestRaw(reqUrl, method, data);
    return resRaw.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    try {
        siteKey = _.isEmpty(cfg.skey) ? '' : cfg.skey;
        siteType = _.isEmpty(cfg.stype) ? '' : cfg.stype;
        await initAli(cfg.ext);
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
        if (!_.isEmpty(matches)) return await detailContent(matches[1]);
        const html = await request(siteUrl + id);
        const $ = load(html);
        const href = $('div.down a:first').attr('href');
        const data = await requestRaw(siteUrl + href, 'get', null, 0);
        const headers = data.headers;
        let url = '';
        if (headers.hasOwnProperty('location')) {
            url = headers['location'];
        }
        matches = url.match(patternAli);
        if (!_.isEmpty(matches)) return await detailContent(matches[1]);
        return '';
    } catch (e) {
        await log('detail:' + e.message + ' line:' + e.lineNumber);
    }
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
    const limit = 20;
    const param = {
        keyboard: wd,
    };
    const data = await requestRaw(siteUrl + '/search', 'post', param);
    let html = '';
    const headers = data.headers;
    if (headers.hasOwnProperty('location')) {
        const url = headers['location'] + '?p=' + pg;
        html = await request(url);
    }

    const $ = load(html);
    const elements = $('ul#url');
    const videos = _.map(elements, (item) => {
        const element = $(item);
        const href = element.find('a.l').attr('href');
        if (!href) return undefined;
        const name = element.text().trim();
        const remark = element.find('li.r').attr('data_size');
        console.debug('vod_id:' + href);
        return {
            vod_id: href,
            vod_name: name,
            vod_pic: "https://pic.rmb.bdstatic.com/bjh/6a2278365c10139b5b03229c2ecfeea4.jpeg",
            vod_remarks: remark,
        };
    });
    const nextPage = $('.pages_search .nex:contains(下一页)');
    const hasMore = !_.isEmpty(nextPage);
    const pgCount = hasMore ? parseInt(pg) + 1 : parseInt(pg);
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: limit,
        total: limit * pgCount,
        list: videos.filter(item => item !== undefined),
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