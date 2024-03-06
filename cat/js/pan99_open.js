import { Crypto, load, _ } from 'assets://js/lib/cat.js';
import { log } from './lib/utils.js';
import { initAli, detailContentVodPlayFrom, detailContentVodPlayUrl, playContent } from './lib/ali.js';

let siteKey = 'pan99';
let siteType = 0;
const siteUrl = 'https://pan99.xyz';
const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1';

async function request(reqUrl) {
    const res = await req(reqUrl, {
        method: 'get',
        headers: {
            'User-Agent': UA,
            'Referer': siteUrl,
        },
    });
    return res.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    try {
        siteKey = cfg.skey;
        siteType = cfg.stype;
        await initAli(cfg.ext);
    } catch (e) {
        await log('init:' + e.message + ' line:' + e.lineNumber);
    }
}

async function home(filter) {
    const classes = [{'type_id':'dy','type_name':'电影'},{'type_id':'tv','type_name':'完结剧集'},{'type_id':'tv/geng','type_name':'追更剧集'},{'type_id':'tv/netflix','type_name':'Netflix'}];
    const filterObj = {};
    return JSON.stringify({
        class: classes,
        filters: filterObj,
    });
}

async function homeVod() {}

async function category(tid, pg, filter, extend) {
    let page = '';
    if (pg > 1) {
        page = 'page/' + pg + '/';
    }
    const cateUrl = siteUrl + '/category/' + tid + '/' + page;
    const html = await request(cateUrl);
    const $ = load(html);
    const list = $('.post-item');
    const jsBase = await js2Proxy(true, siteType, siteKey, 'img/', {});
    const videos = _.map(list, (vid) => {
        const $vid = $(vid);
        const $link = $vid.find('.media-img');
        const $entry = $vid.find('.entry-cat-dot');
        return {
            vod_id: decodeURIComponent($link.attr('href').replace(/.*\/\/.*\/(.*\/.*)\//g, '$1')),
            vod_name: $link.attr('title'),
            vod_pic: jsBase + base64Encode($link.attr("data-bg")),
            vod_remarks: $entry.text().trim(),
        };
    });
    const limit = 50;
    const curPage = parseInt(pg);
    const hasMore = videos.length == limit;
    const pgCount = hasMore ? curPage + 1 : curPage;
    return JSON.stringify({
        page: curPage,
        pagecount: pgCount,
        limit: limit,
        total: limit * pgCount,
        list: videos,
    });
}

async function detail(id) {
    const detailUrl = siteUrl + '/' + id;
    const html = await request(detailUrl);
    const $ = load(html);
    const $cards = $('.card p a:not([href*=quark])');
    const shareLinks = _.map($cards, (card) => {
        return $(card).attr('href').trim();
    });
    const content = $('.post-content').text();
    const jsBase = await js2Proxy(true, siteType, siteKey, 'img/', {});
    const vod = {
        vod_id: id,
        vod_name: $('.post-title.mb-2.mb-lg-3').text().trim(),
        vod_director: matchDetailContent(content, /◎导　　演([\w\W]*?)◎/),
        vod_actor: matchDetailContent(content, /◎演　　员([\w\W]*?)◎/),
        vod_year: matchDetailContent(content, /◎年　　代(.*)/),
        vod_area: matchDetailContent(content, /◎产　　地(.*)/),
        vod_type: matchDetailContent(content, /◎类　　别(.*)/),
        vod_pic: jsBase + base64Encode($('img.alignnone.size-medium').attr('src')),
        vod_content: matchDetailContent(content, /◎简　　介([\w\W]*)资源失效/),
        vod_remarks: $('.meta-cat-dot').text().trim(),
    };
    try {
        vod.vod_play_from = detailContentVodPlayFrom(shareLinks);
        vod.vod_play_url = await detailContentVodPlayUrl(shareLinks);
    } catch (e) {
        await log('detail:' + e.message + ' line:' + e.lineNumber);
    }
    return JSON.stringify({
        list: [vod],
    });
}

function matchDetailContent(contentText, regex) {
    const matches = contentText.match(regex);
    if (!_.isEmpty(matches)) {
        const index = matches.length - 1;
        return matches[index].trim();
    }
    return '';
}

function base64Encode(text) {
    return Crypto.enc.Base64.stringify(Crypto.enc.Utf8.parse(text));
}

function base64Decode(text) {
    return Crypto.enc.Utf8.stringify(Crypto.enc.Base64.parse(text));
}

async function proxy(segments, headers) {
    const what = segments[0];
    const url = base64Decode(segments[1]);
    if (what == 'img') {
        const resp = await req(url, {
            buffer: 2,
            headers: {
                'Referer': 'https://api.douban.com/',
                'User-Agent': UA,
            },
        });
        return JSON.stringify({
            code: resp.code,
            buffer: 2,
            content: resp.content,
            headers: resp.headers,
        });
    }
    return JSON.stringify({
        code: 500,
        content: '',
    });
}

async function play(flag, id, flags) {
    try {
        return await playContent(flag, id, flags);
    } catch (e) {
        await log('play:' + e.message + ' line:' + e.lineNumber);
    }
}

async function search(wd, quick, pg) {
    let page = '';
    if (pg > 1) {
        page = 'page/' + pg + '/';
    }
    const searchUrl = siteUrl + '/' + page + '?cat=&s=' + encodeURIComponent(wd);
    const html = await request(searchUrl);
    const $ = load(html);
    const list = $('.post-item');
    const jsBase = await js2Proxy(true, siteType, siteKey, 'img/', {});
    const videos = _.map(list, (vid) => {
        const $vid = $(vid);
        const $link = $vid.find('.media-img');
        const $entry = $vid.find('.entry-cat-dot');
        return {
            vod_id: decodeURIComponent($link.attr('href').replace(/.*\/\/.*\/(.*\/.*)\//g, '$1')),
            vod_name: $link.attr('title'),
            vod_pic: jsBase + base64Encode($link.attr("data-bg")),
            vod_remarks: $entry.text().trim(),
        };
    });
    const limit = 50;
    const curPage = parseInt(pg);
    const hasMore = videos.length == limit;
    const pgCount = hasMore ? curPage + 1 : curPage;
    return JSON.stringify({
        page: curPage,
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
        proxy: proxy,
        search: search,
    };
}