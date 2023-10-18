import { Crypto, _ } from 'assets://js/lib/cat.js';

let host = 'http://live.yj1211.work';
let categories = '';
let siteKey = '';
let siteType = 0;

const MOBILE_UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36';

async function requestRaw(reqUrl, headers) {
    let resRaw = await req(reqUrl, {
        method: 'get',
        headers: headers,
    });
    return resRaw;
}

async function request(reqUrl) {
    let defHeader = {
        'User-Agent': MOBILE_UA,
    };
    let resRaw = await requestRaw(reqUrl, defHeader);
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
        url = host + '/api/live/getRecommendByPlatform?platform=huya&size=20&page=' + pg;
    } else {
        url = host + '/api/live/getRecommendByPlatformArea?platform=huya&size=20&area=' + tid + '&page=' + pg;
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
    const headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': MOBILE_UA,
    };
    const resp = await requestRaw('https://www.huya.com/' + id, headers);
    let liveData = null;
    let streamInfo = resp.content.match(/stream: ([\s\S]*?)\n/);
    if (streamInfo) {
        liveData = JSON.parse(streamInfo[1]);
    } else {
        streamInfo = resp.content.match(/"stream": "([\s\S]*?)"/);
        if (streamInfo) {
            let liveDataBase64 = streamInfo[1];
            liveData = JSON.parse(base64Decode(liveDataBase64));
        }
    }
    const vodData = liveData.data[0];
    const liveInfo = vodData.gameLiveInfo;
    let vod = {
        vod_id: id,
        vod_name: liveInfo.introduction,
        vod_pic: liveInfo.screenshot,
        vod_remarks: liveInfo.gameFullName,
        type_name: liveInfo.gameFullName,
        vod_director: liveInfo.nick,
        vod_actor: '',
        vod_content: liveInfo.activityCount + '人在线',
        vod_year: '',
        vod_area: '',
    };
    let streamInfoList = vodData.gameStreamInfoList;
    let vodList = [];
    let playUrl = '';
    for (const streamInfo of streamInfoList) {
        const hlsUrl = streamInfo.sHlsUrl + '/' + streamInfo.sStreamName + '.' + streamInfo.sHlsUrlSuffix;
        const srcAntiCode = unescape(streamInfo.sHlsAntiCode);
        let codeList = srcAntiCode.split('&');
        codeList = codeList.filter(code => code != '');
        let cryptoInfo = {};
        for (const code of codeList) {
          const [k, v] = code.split('=');
          cryptoInfo[k] = v;
        }
        const fm = unquote(cryptoInfo.fm);
        const fmDecoded = base64Decode(fm);
        const hashPrefix = fmDecoded.split('_')[0];
        const ctype = cryptoInfo.ctype || '';
        const txyp = cryptoInfo.txyp || '';
        const fs = cryptoInfo.fs || '';
        const t = cryptoInfo.t || '';
        const u = 1463993859134;
        const curTime = Date.now();
        const seqid = Math.floor(curTime + u);
        const wsTime = (Math.floor(curTime / 1e3) + 3600).toString(16);
        const v0 = seqid + '|' + ctype + '|' + t;
        const v1 = md5Encode(v0);
        const v2 = hashPrefix + '_' + u + '_' + streamInfo.sStreamName + '_' + v1 + '_' + wsTime;
        const hash = md5Encode(v2);
        const ratio = ''
        const purl = `${hlsUrl}?wsSecret=${hash}&wsTime=${wsTime}&seqid=${seqid}&ctype=${ctype}&ver=1&txyp=${txyp}&fs=${fs}&ratio=${ratio}&u=${u}&t=${t}&sv=2107230339`;
        playUrl += `${streamInfo.sCdnType}$${purl}#`;
    }
    vod.vod_play_from = 'huya';
    vod.vod_play_url = playUrl.replace(/#$/g, '');
    return JSON.stringify({
        list: [vod],
    });
}

async function play(flag, id, flags) {
    return JSON.stringify({
        parse: 0,
        url: id,
        header: {
            "User-Agent": MOBILE_UA,
        },
    });
}

async function search(wd, quick) {
    return '{}';
}

function unquote(str) {
    return str.replace(/^"(.*)"$/, '$1');
}

function md5Encode(text) {
    return Crypto.MD5(Crypto.enc.Utf8.parse(text)).toString();
}

function base64Decode(text) {
    return Crypto.enc.Utf8.stringify(Crypto.enc.Base64.parse(text));
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