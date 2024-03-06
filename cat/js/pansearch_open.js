import { load, _ } from 'assets://js/lib/cat.js';
import { log } from './lib/utils.js';
import { initAli, detailContent, playContent } from './lib/ali.js';

let siteKey = 'pansearch';
let siteType = 0;
let siteUrl = 'https://www.pansearch.me';
let patternAli = /(https:\/\/www\.(aliyundrive|alipan)\.com\/s\/[^"]+)/

const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1';

async function requestRaw(reqUrl, headers) {
    let res = await req(reqUrl, {
        method: 'get',
        headers: headers || {
            'User-Agent': UA,
            'Referer': siteUrl,
        },
    });
    return res;
}

async function request(reqUrl) {
    let resRaw = await requestRaw(reqUrl)
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
    let offsetParam = '';
    const offset = (pg - 1) * limit;
    if (offset > 0) {
        offsetParam = '&offset=' + offset;
    }
    const html = await request(siteUrl);
    const $ = load(html);
    const script = $('script#__NEXT_DATA__')[0];
    const data = script.children[0].data;
    const buildId = JSON.parse(data).buildId;
    const url = siteUrl + "/_next/data/" + buildId + "/search.json?keyword=" + encodeURIComponent(wd) + offsetParam + "&pan=aliyundrive";
    const result = await requestRaw(url, getSearchHeader());
    const json = JSON.parse(result.content).pageProps.data;
    const total = json.total;
    const videoIdSet = new Set();
    const videos = [];
    for (const item of json.data) {
        const content = item.content;
        const img = item.image || siteUrl + "/favicon.png";
        const splits = content.split('\n');
        if (_.isEmpty(splits)) continue;
        if (content.includes('1、')) {
            for (const line of splits) {
                if (_.isEmpty(line)) continue;
                const vodId = parseVideo(line, videoIdSet);
                if (!vodId) continue;
                videos.push({
                    vod_id: vodId,
                    vod_name: line.replaceAll(/<\/?[^>]+>/g, "").replace(/[0-9]*、/g, '').replace(/:http.*/g, ''),
                    vod_pic: img,
                    vod_remarks: item.time
                });
            }
        } else {
            const vodId = parseVideo(content, videoIdSet);
            if (!vodId) continue;
            videos.push({
                vod_id: vodId,
                vod_name: splits[0].replaceAll(/<\/?[^>]+>/g, "").replace('名称：', ''),
                vod_pic: img,
                vod_remarks: item.time
            });
        }
    }
    const pgCount = parseInt(total / limit) + 1;
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: limit,
        total: total,
        list: videos,
    });
}

function parseVideo(content, videoIdSet) {
    const matches = content.match(patternAli);
    if (_.isEmpty(matches)) return;
    const vodId = matches[1];
    if (videoIdSet.has(vodId)) return;
    videoIdSet.add(vodId);
    return vodId;
}

function getSearchHeader() {
    return {
        "x-nextjs-data": "1",
        "Referer": siteUrl,
    };
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