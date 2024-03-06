import { load, _ } from 'assets://js/lib/cat.js';
import { log } from './lib/utils.js';
import { initAli, detailContent, playContent } from './lib/ali.js';

let siteKey = 'zhaozy';
let siteType = 0;
let siteUrl = 'https://zhaoziyuan.pw';
let patternAli = /(https:\/\/www\.(aliyundrive|alipan)\.com\/s\/[^"]+)/;
let patternVid = /(\\S+)/;
let username = '';
let password = '';
let cookie = '';

const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1';

async function requestRaw(reqUrl, headers, method, data) {
    let res = await req(reqUrl, {
        method: method || 'get',
        headers: headers,
        data: data,
        postType: method === 'post' ? 'form' : '',
    });
    return res;
}

async function request(reqUrl, headers) {
    let resRaw = await requestRaw(reqUrl, headers);
    return resRaw.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    try {
        siteKey = _.isEmpty(cfg.skey) ? '' : cfg.skey;
        siteType = _.isEmpty(cfg.stype) ? '' : cfg.stype;
        const ext = _.isEmpty(cfg.ext) ? '' : cfg.ext;
        const configs = ext.split('$$$');
        if (configs.length == 3) {
            username = configs[1];
            password = configs[2];
        }
        await initAli(configs[0]);
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
        const headers = await getHeaders();
        const data = await request(siteUrl + '/' + id, headers);
        matches = data.match(patternAli);
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
    const limit = 15;
    const headers = await getHeaders();
    const html = await request(siteUrl + '/so?filename=' + encodeURIComponent(wd) + '&page=' + pg, headers);
    const $ = load(html);
    const elements = $('div.li_con div.news_text');
    const videos = _.map(elements, (item) => {
        const element = $(item);
        const href = element.find('div.news_text a').attr('href');
        if (!href) return undefined;
        const matches = href.match(patternVid);
        if (!_.isEmpty(matches)) return undefined;
        const name = element.find("div.news_text a h3").text();
        const remark = element.find("div.news_text a p").text().split("|")[1].split("：")[1];
        return {
            vod_id: href,
            vod_name: name,
            vod_pic: "https://inews.gtimg.com/newsapp_bt/0/13263837859/1000",
            vod_remarks: remark
        };
    });
    const nextPage = $('.page a li:contains(下一页)');
    const hasMore = _.isEmpty(nextPage) ? false : nextPage.attr('class') != 'disabled';
    const pgCount = hasMore ? parseInt(pg) + 1 : parseInt(pg);
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: limit,
        total: limit * pgCount,
        list: videos.filter(item => item !== undefined),
    });
}

async function getHeaders() {
    if (!cookie) {
        cookie = await getCookie();
    }
    return {
        'User-Agent': UA,
        'Referer': siteUrl,
        'Cookie': cookie,
    };
}

async function getCookie() {
    const params = {
        "username": username,
        "password": password,
    };
    const headers = {
        "User-Agent": UA,
        "Referer": siteUrl + "/stop.html",
        "Origin": siteUrl,
    };
    const res = await requestRaw(siteUrl + "/logiu.html", headers, 'post', params);
    let result = '';
    for (const cookie of res.headers['set-cookie']) {
        result += cookie.split(";")[0] + ";";
    }
    return result;
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