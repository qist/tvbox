import { Crypto, _ } from 'assets://js/lib/cat.js';
import { log } from './lib/utils.js';
import { initAli, detailContent, playContent } from './lib/ali.js';

let siteKey = 'upyun';
let siteType = 0;
let siteUrl = 'https://zyb.upyunso.com';
let patternAli = /(https:\/\/www\.(aliyundrive|alipan)\.com\/s\/[^"]+)/

async function request(reqUrl) {
    let res = await req(reqUrl, {
        method: 'get',
        headers: {
            'Referer': siteUrl,
        },
    });
    return res.content;
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
        return await detailContent(id);
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
    const limit = 25;
    const resp = await request(siteUrl + "/v15/search?keyword=" + encodeURIComponent(wd) + '&page=' + pg + '&s_type=2');
    const data = decrypt(resp);
    const items = JSON.parse(data).result.items;
    const videos = [];
    for(const item of items) {
        const url = decrypt(item.page_url);
        const matches = url.match(patternAli);
        if (_.isEmpty(matches)) continue;
        const title = _.isEmpty(item.content) ? item.title : item.content[0].title;
        videos.push({
            vod_id: url,
            vod_name: title.replaceAll(/<\/?[^>]+>/g, ""),
            vod_pic: "https://inews.gtimg.com/newsapp_bt/0/13263837859/1000",
            vod_remarks: item.insert_time,
        });
    }
    const hasMore = !_.isEmpty(items);
    const pgCount = hasMore ? parseInt(pg) + 1 : parseInt(pg);
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: limit,
        total: limit * pgCount,
        list: videos,
    });
}

function decrypt(text) {
    const data = {
        ciphertext: Crypto.enc.Hex.parse(text.toUpperCase()),
    };
    const key = Crypto.enc.Utf8.parse('qq1920520460qqzz');
    const iv = Crypto.enc.Utf8.parse('qq1920520460qqzz');
    const mode = Crypto.mode.CBC;
    const padding = Crypto.pad.Pkcs7;
    const decrypted = Crypto.AES.decrypt(data, key, {
        'iv': iv,
        'mode': mode,
        'padding': padding
    });
    const decryptedData = Crypto.enc.Utf8.stringify(decrypted);
    return decryptedData;
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