import { Crypto, load, _ } from 'assets://js/lib/cat.js';

let key = 'star';
let host = 'https://www.histar.tv';
let apiHost = 'https://aws.ulivetv.net';
let types = {};
// let ver = '';
let siteKey = '';
let siteType = 0;

const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1';

async function request(reqUrl, method, data) {
    const headers =  {
        'User-Agent': UA,
    };
    if (method == 'post') {
        headers['Content-Type'] = 'application/json';
    } else {
        headers['Cookie'] = 'userIP=127.0.0.1; aws-waf-token=';
        headers['Referer'] = host;
    }
    const res = await req(reqUrl, {
        method: method || 'get',
        headers: headers,
        data: data,
    });
    return res.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
    types = {
        'movie': '电影',
        'drama': '电视剧',
        'animation': '动漫',
        'variety': '综艺',
        'documentary': '纪录片',
    };
    // ver = await getVer();
}

// async function getVer() {
//     const html = await request(host);
//     const $ = load(html);
//     const srcAttr = $('script[src*=\'buildManifest.js\']').attr('src');
//     return srcAttr.split('/')[3];
// }

async function home(filter) {
    const typeList = _.keys(types);
    const classes = _.map(typeList, (item) => {
        return { type_id: item, type_name: types[item] };
    });
    const filterConfig = {};
    const jsonData = JSON.stringify(typeList);
    for (const typeId of typeList) {
        const html = await request(host + '/' + typeId + '/all/all/all');
        const $ = load(html);
        const json = $('#__NEXT_DATA__')[0].children[0].data;
        const obj = JSON.parse(json).props.pageProps.filterCondition;
        const label = convertTypeData(obj, 'label', '类型');
        const country = convertTypeData(obj, 'country', '地区');
        const time = convertTypeData(obj, 'time', '年份');
        const filterArray = [label, country, time];
        filterConfig[typeId] = filterArray;
    };
    return JSON.stringify({
        class: classes,
        filters: filterConfig,
    });
}

function convertTypeData(typeData, key, name) {
    if (!typeData || !typeData[key] || typeData[key].length <= 2) {
        return null;
    }
    let valueList = typeData[key];
    if (key == 'time') {
        valueList = valueList.sort((a, b) => { return b - a;});
        valueList.pop();
    }
    const values = _.map(valueList, (item) => {
        let name;
        let value;
        if (item instanceof Array) {
            name = item[0];
            value = item[0];
        } else {
            name = item.toString();
            value = item.toString();
        }
        return {
            n: name,
            v: value,
        };
    });
    values.unshift({
        n: '全部',
        v: '',
    });
    const typeClass = {
        key: key,
        name: name,
        init: '',
        value: values,
    };
    return typeClass;
}

async function homeVod() {
    const html = await request(host);
    const $ = load(html);
    const json = $('#__NEXT_DATA__')[0].children[0].data;
    const obj = JSON.parse(json).props.pageProps.cards;
    const videos = [];
    _.each(obj, (cards) => {
        if (cards.name == '电视直播') return;
        _.each(cards.cards, (card) => {
            const v = {
                vod_id: card.id,
                vod_name: card.name,
                vod_pic: card.img,
                vod_remarks: card.countStr,
            };
            videos.push(v);
        });
    });
    return JSON.stringify({
        list: videos,
    });
}

async function category(tid, pg, filter, extend) {
    const limit = 16;
    const param = {
        chName: types[tid],
        page: pg,
        pageSize: limit,
        label: extend.label,
        country: extend.country,
    };
    if (extend.time) {
        const year = parseInt(extend.time);
        param.startTime = year;
        param.endTime = year;
    }
    const json = await request(apiHost + '/v3/web/api/filter', 'post', JSON.stringify(param));
    const data = JSON.parse(json).data;
    const videos = _.map(data.list, (card) => {
        return {
            vod_id: card.id,
            vod_name: card.name,
            vod_pic: card.img,
            vod_remarks: card.countStr,
        };
    });
    const page = parseInt(pg);
    const count = parseInt(data.total / limit);
    return JSON.stringify({
        page: page,
        pagecount: count,
        limit: limit,
        total: data.total,
        list: videos,
    });
}

async function detail(id) {
    const html = await request(host + '/vod/detail/' + id);
    const $ = load(html);
    const json = $('#__NEXT_DATA__')[0].children[0].data;
    const obj = JSON.parse(json).props.pageProps;
    const vObj = obj.pageData;
    const vodAtom = {
        vod_id: id,
        vod_name: vObj.name,
        vod_type: vObj.chname,
        vod_pic: vObj.picurl,
        vod_area: vObj.country,
        vod_lang: vObj.language,
        vod_remarks: vObj.countStr,
        vod_actor: vObj.actor,
        vod_director: vObj.director,
        vod_content: vObj.desc,
    }
    const playInfo = obj.videosGroup;
    const playVod = {};
    _.each(playInfo, (info) => {
        const sourceName = info.name;
        let playList = '';
        const videoInfo = info.videos;
        const vodItems = _.map(videoInfo, (epObj) => {
            const epName = epObj.epInfo;
            const playUrl = epObj.purl
            return epName + '$' + playUrl;
        });
        if (_.isEmpty(vodItems)) return;
        playList = vodItems.join('#');
        playVod[sourceName] = playList;
    });
    vodAtom.vod_play_from = _.keys(playVod).join('$$$');
    vodAtom.vod_play_url = _.values(playVod).join('$$$');
    return JSON.stringify({
        list: [vodAtom],
    });
}

async function play(flag, id, flags) {
    let playUrl = id;
    return JSON.stringify({
        parse: 0,
        url: playUrl,
    });
}

async function search(wd, quick, pg) {
    // const limit = 10;
    // const json = await request(host + '/_next/data/' + ver + '/search.json?word=' + encodeURIComponent(wd) + '&page=' + pg);
    // const data = JSON.parse(json).pageProps;
    // const videos = _.map(data.initList, (card) => {
    //     return {
    //         vod_id: card.id,
    //         vod_name: card.name,
    //         vod_pic: card.picurl,
    //         vod_remarks: card.countStr,
    //     };
    // });
    // const page = parseInt(pg);
    // const count = parseInt(data.total / limit);
    // return JSON.stringify({
    //     page: page,
    //     pagecount: count,
    //     limit: limit,
    //     total: data.total,
    //     list: videos,
    // });
    const limit = 10;
    const param = {
        word: wd,
        page: pg,
        pageSize: limit,
    };
    const json = await request(apiHost + '/v3/web/api/search', 'post', JSON.stringify(param));
    const data = JSON.parse(json).data;
    const videos = _.map(data.list, (card) => {
        return {
            vod_id: card.id,
            vod_name: card.name,
            vod_pic: card.picurl,
            vod_remarks: card.countStr,
        };
    });
    const page = parseInt(pg);
    const count = parseInt(data.total / limit);
    return JSON.stringify({
        page: page,
        pagecount: count,
        limit: limit,
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