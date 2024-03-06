import { Crypto, _ } from 'assets://js/lib/cat.js';
import { log } from './lib/utils.js';
import { initAli, detailContent, playContent } from './lib/ali.js';

let siteKey = 'yiso';
let siteType = 0;
let siteUrl = 'https://yiso.fun';
let patternAli = /(https:\/\/www\.(aliyundrive|alipan)\.com\/s\/[^"]+)/;
let cookie = '';

const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1';


async function request(reqUrl) {
    let res = await req(reqUrl, {
        method: 'get',
        headers: {
            'User-Agent': UA,
            'Referer': siteUrl,
            'Cookie': cookie,
        },
    });
    return res.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    try {
        siteKey = _.isEmpty(cfg.skey) ? '' : cfg.skey;
        siteType = _.isEmpty(cfg.stype) ? '' : cfg.stype;
        const ext = _.isEmpty(cfg.ext) ? '' : cfg.ext;
        const configs = ext.split('$$$');
        if (configs.length == 2) {
            cookie = configs[1];
        }
        const token = {
            ext: configs[0]
        };
        await initAli(token);
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
    const limit = 10;
    const resp = await request(siteUrl + "/api/search?name=" + encodeURIComponent(wd) + '&pageNo=' + pg + '&from=ali');
    const json = JSON.parse(resp).data;
    const total = json.total;
    const videos = _.map(json.list, (item) => {
        const name = item.fileInfos[0].fileName;
        const remark = item.gmtCreate;
        const url = decryptUrl(item.url);
        return {
            vod_id: url,
            vod_name: name,
            vod_pic: "https://inews.gtimg.com/newsapp_bt/0/13263837859/1000",
            vod_remarks: remark,
        };
    });
    const pgCount = parseInt(total / limit) + 1;
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: limit,
        total: total,
        list: videos,
    });
}

function decryptUrl(url) {
    const data = {
        ciphertext: Crypto.enc.Base64.parse(url),
    };
    const key = Crypto.enc.Utf8.parse('4OToScUFOaeVTrHE');
    const iv = Crypto.enc.Utf8.parse('9CLGao1vHKqm17Oz');
    const mode = Crypto.mode.CBC;
    const padding = Crypto.pad.Pkcs7;
    const decrypted = Crypto.AES.decrypt(data, key, {
        'iv': iv,
        'mode': mode,
        'padding': padding
    });
    const decryptedUrl = Crypto.enc.Utf8.stringify(decrypted);
    return decryptedUrl;
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