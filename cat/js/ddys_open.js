import { Crypto, load, _ } from 'assets://js/lib/cat.js';

const key = 'ddys';
let DOMAIN = 'ddys.pro';
let HOST = 'https://' + DOMAIN;
let PLAY_HOST = 'https://v.' + DOMAIN;
const FROM_DIRECT = '直连';
const FROM_PARSE = '解析';
let siteKey = '';
let siteType = 0;

const UA = 'Mozilla/5.0 (Linux; Android 11; M2007J3SC Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045714 Mobile Safari/537.36';

async function request(reqUrl) {
    const res = await req(reqUrl, {
        method: 'get',
        headers: {
            'Host': HOST.match(/.*\:\/\/(.*)/)[1],
            'User-Agent': UA,
            'Referer': HOST,
            'Accept-Encoding': 'gzip',
        },
    });
    return res.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
    if (cfg.hasOwnProperty('ext')) {
        if (cfg.ext.hasOwnProperty('domain')) {
            DOMAIN = cfg.ext.domain;
            HOST = 'https://' + DOMAIN;
            PLAY_HOST = 'https://v.' + DOMAIN;
        }
    }
}

async function home(filter) {
    const classes = [{'type_id':'class','type_name':'类型'},{'type_id':'movie','type_name':'电影'},{'type_id':'airing','type_name':'热映中'},{'type_id':'drama','type_name':'剧集'},{'type_id':'anime','type_name':'动画'},{'type_id':'documentary','type_name':'纪录片'},{'type_id':'variety','type_name':'综艺'}];
    const filterObj = {
        'class':[{'key':'tag','name':'标签','init':'recommend','value':[{'n':'站长推荐','v':'recommend'},{'n':'动作','v':'action'},{'n':'喜剧','v':'comedy'},{'n':'爱情','v':'romance'},{'n':'科幻','v':'sci-fi'},{'n':'犯罪','v':'crime'},{'n':'悬疑','v':'mystery'},{'n':'恐怖','v':'horror'}]}],
        'movie':[{'key':'type','name':'分类','init':'','value':[{'n':'全部','v':''},{'n':'欧美电影','v':'western-movie'},{'n':'日韩电影','v':'asian-movie'},{'n':'华语电影','v':'chinese-movie'}]}],
        'drama':[{'key':'type','name':'分类','init':'','value':[{'n':'全部','v':''},{'n':'欧美剧','v':'western-drama'},{'n':'日剧','v':'jp-drama'},{'n':'韩剧','v':'kr-drama'},{'n':'华语剧','v':'cn-drama'},{'n':'其他地区','v':'other'}]}],
        'anime':[{'key':'type','name':'分类','init':'','value':[{'n':'全部','v':''},{'n':'本季新番','v':'new-bangumi'}]}]
    };
    return JSON.stringify({
        class: classes,
        filters: filterObj,
    });
}

async function homeVod() {}

async function category(tid, pg, filter, extend) {
    if (pg <= 0) pg = 1;
    let path = '';
    if (extend.tag) {
        path = '/tag/' + extend.tag;
    } else {
        path = '/category/' + tid;
        if (!_.isEmpty(extend.type)) {
            path += '/' + extend.type;
        }
    }
    let page = '';
    if (pg > 1) {
        page = 'page/' + pg + '/';
    }
    const link = HOST + path + '/' + page;
    const html = await request(link);
    const $ = load(html);
    const items = $('.post-box-list article');
    const videos = _.map(items, (item) => {
        const $item = $(item);
        const title = $item.find('.post-box-title a');
        const name = title.text();
        const url = title.attr('href');
        const image = $item.find('.post-box-image').attr('style').replace(/.*url\((.*)\);/g, '$1');
        const remarks = $item.find('.post-box-meta').text();
        return {
            vod_id: url.replace(/.*\/\/.*\/(.*)\//g, '$1'),
            vod_name: name,
            vod_pic: image,
            vod_remarks: remarks || '',
        };
    });
    const limit = 28;
    const hasMore = $('nav.navigation a.next').length > 0;
    const pgCount = hasMore ? parseInt(pg) + 1 : parseInt(pg);
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: limit,
        total: limit * pgCount,
        list: videos,
    });
}

async function detail(id) {
    const html = await request(HOST + '/' + id + '/');
    const $ = load(html);
    const abstract = $('div.abstract')[0].children;
    const vod = {
        vod_id: id,
        vod_name: $('h1.post-title').text(),
        vod_type: findAbstractText(abstract, '类型:'),
        vod_year: findAbstractText(abstract, '年份:'),
        vod_area: findAbstractText(abstract, '制片国家/地区:'),
        vod_director: findAbstractText(abstract, '导演:'),
        vod_actor: findAbstractText(abstract, '演员:'),
        vod_pic: $('div.post img:first').attr('data-cfsrc'),
        vod_remarks : $('span.cat-links').text().trim(),
        vod_content: findAbstractText(abstract, '简介:'),
    };
    const playMap = {};
    parseAndUpdateUrls($, playMap);
    const links = $('div.page-links a');
    if (!_.isEmpty(links)) {
        const promiseList = _.map(links, (link) => {
            const url = $(link).attr('href');
            return request(url);
        });
        const respList = await Promise.all(promiseList);
        _.each(respList, (resp) => {
            try {
                const $ = load(resp);
                parseAndUpdateUrls($, playMap);
            } catch(e) {
            }
        });
    }
    vod.vod_play_from = _.keys(playMap).join('$$$');
    const urls = _.values(playMap);
    const vod_play_url = _.map(urls, (urlist) => {
        return urlist.join('#');
    });
    vod.vod_play_url = vod_play_url.join('$$$');
    return JSON.stringify({
        list: [vod],
    });
}

function findAbstractText(children, keyword) {
    for (const item of children) {
        if (item.type == 'text' && item.data && item.data.startsWith(keyword)) {
            return item.data.substring(keyword.length).trim();
        }
    }
    return '';
}

function parseAndUpdateUrls($, playMap) {
    const trackText = $('script.wp-playlist-script').text();
    const tracks = JSON.parse(trackText).tracks;
    _.each(tracks, (track) => {
        const title = track.caption;
        const directUrl = track.src0;
        if (!playMap.hasOwnProperty(FROM_DIRECT)) {
            playMap[FROM_DIRECT] = [];
        }
        playMap[FROM_DIRECT].push(title + '$' + directUrl);
        if (!_.isEmpty(track.src1)) {
            if (!playMap.hasOwnProperty(FROM_PARSE)) {
                playMap[FROM_PARSE] = [];
            }
            playMap[FROM_PARSE].push(title + '$' + track.src1);
        }
    });
}

async function play(flag, id, flags) {
    let playUrl;
    if (flag == FROM_PARSE) {
        const resp = await request(HOST + '/getvddr2/video?id=' + id + '&type=json');
        playUrl = JSON.parse(resp).url;
    } else {
        playUrl = PLAY_HOST + id;
    }
    const headers = {
        'User-Agent': UA,
        'Referer': HOST,
        'Icy-MetaData': '1',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'video',
    };
    return JSON.stringify({
        parse: 0,
        url: playUrl,
        header: headers,
    });
}

async function search(wd, quick, pg) {
    let page = '';
    if (pg > 1) {
        page = '/page/' + pg;
    }
    const html = await request(HOST + page + '/?s=' + wd + '&post_type=post');
    const $ = load(html);
    const list = $('div.post-content');
    const videos = _.map(list, (item) => {
        const $item = $(item);
        const title = $item.find('.post-title a');
        const name = title.text();
        const url = title.attr('href');
        const remarks = $item.find('.cat-links').text();
        return {
            vod_id: url.replace(/.*\/\/.*\/(.*)\//g, '$1'),
            vod_name: name,
            vod_pic: HOST + '/android-chrome-512x512.png',
            vod_remarks: remarks,
        };
    });
    const limit = 100;
    const hasMore = $('nav.navigation a.next').length > 0;
    const pgCount = hasMore ? parseInt(pg) + 1 : parseInt(pg);
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