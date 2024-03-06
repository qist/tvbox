// 网站搜索异常
import { load, _ } from './lib/cat.js';

let key = '爱上你听书网';
let HOST = 'https://wap.230ts.net';
let siteKey = '';
let siteType = 0;
const MOBILE_UA = 'Mozilla/5.0 (Linux; Android 11; M2007J3SC Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045714 Mobile Safari/537.36';

async function request(reqUrl, agentSp) {
    let res = await req(reqUrl, {
        method: 'get',
        headers: {
            'User-Agent': agentSp || MOBILE_UA,
            'Referer': HOST
        },
    });
    return res.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
}

async function home(filter) {
    const html = await request(HOST + '/sort/');
    const $ = load(html);
    let filterObj = {};
    const class_parse = $('dl.pd-class:first > dd > a[href*=sort]');
    let classes = [];
    classes = _.map(class_parse, (cls) => {
        let typeId = cls.attribs['href'];
        typeId = typeId.replace(/.*?\/sort\/(.*).html/g, '$1');
        return {
            type_id: typeId,
            type_name: cls.children[0].data,
        };
    });
    const sortName = ['玄幻有声', '灵异有声', '综艺娱乐', '长篇评书', '都市有声', '军事有声', '职场有声', '其他有声'];
    classes = _.sortBy(classes, (c) => {
        const index = sortName.indexOf(c.type_name);
        return index === -1 ? sortName.length : index;
    });
    return JSON.stringify({
        class: classes,
        filters: filterObj,
    });
}

async function homeVod() {
    const link = HOST + '/top/lastupdate/1.html';
    const html = await request(link);
    const $ = load(html);
    const items = $('ul.list-ul > li');
    let videos = _.map(items, (item) => {
        const it = $(item).find('a:first')[0];
        const img = $(item).find('img:first')[0];
        const remarks = $($(item).find('p.module-slide-author')[0]).text().trim();
        return {
            vod_id: it.attribs.href.replace(/.*?\/tingshu\/(.*)/g, '$1'),
            vod_name: it.attribs.title.replace('有声小说',''),
            vod_pic: HOST + img.attribs['data-original'],
            vod_remarks: remarks || '',
        };
    });
    return JSON.stringify({
        list: videos,
    });
}

async function category(tid, pg, filter, extend) {
    if (pg <= 0) pg = 1;
    const link = HOST + '/sort/' + tid +'/' + (`${pg}`) + '.html';
    const html = await request(link);
    const $ = load(html);
    const items = $('ul.book-ol > li');
    let videos = _.map(items, (item) => {
        const it = $(item).find('a:first')[0];
        const img = $(item).find('img:first')[0];
        const remarks = $($(item).find('div.book-meta')[0]).text().trim();
        return {
            vod_id: it.attribs.href.replace(/.*?\/tingshu\/(.*)/g, '$1'),
            vod_name: it.attribs.title.replace('有声小说',''),
            vod_pic: HOST + img.attribs['data-original'],
            vod_remarks: remarks.replace('佚名（著）','').replace('佚名（播）','').replace('未知（著）','').replace('未知（播）','') || '',
        };
    });
    const hasMore = $('div.paging > a:contains(下一页)').length > 0;
    const pgCount = hasMore ? parseInt(pg) + 1 : parseInt(pg);
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: 24,
        total: 24 * pgCount,
        list: videos,
    });
}

async function detail(id) {
    const html = await request(HOST + '/tingshu/' + id);
    const $ = load(html);
    const detail = $('div.book-cell:first > div');
    let vod = {
        vod_id: id,
        vod_name: $('h1:first').text().trim().replace('有声小说',''),
        vod_pic: HOST + $('div.myui-content__thumb img:first').attr('data-original'),
        vod_content: $('div.ellipsis').text().trim(),
    };
    for (const info of detail) {
        const i = $(info).text().trim();
        if (i.startsWith('类型：')) {
            vod.vod_type = _.map($(info).find('a'), (a) => {
                return a.children[0].data;
            }).join('/');
        } else if (i.startsWith('作者：')) {
            vod.vod_director = _.map($(info).find('a'), (a) => {
                return a.children[0].data;
            }).join('/');
        } else if (i.startsWith('演播：')) {
            vod.vod_actor = _.map($(info).find('a'), (a) => {
                return a.children[0].data;
            }).join('/');
        } else if (i.startsWith('连载中')) {
            vod.vod_remarks = i.substring(3);
        }
    }
    const playlist = _.map($('#playlist > ul > li > a'), (it) => {
        return it.children[0].data + '$' + it.attribs.href.replace(/\/mp3\/(.*).html/g, '$1');
    });
    vod.vod_play_from = '道长在线';
    vod.vod_play_url = playlist.join('#');
    return JSON.stringify({
        list: [vod],
    });
}

async function play(flag, id, flags) {
    const link = HOST + '/mp3/' + id + '.html';
    const html = await request(link);
    const $ = load(html);
    const iframe = $('body iframe[src*=player]');
    const iframeHtml = (
        await req(HOST + iframe[0].attribs.src, {
            headers: {
                'Referer': link,
                'User-Agent': MOBILE_UA,
            },
        })
    ).content;
    const playUrl = iframeHtml.match(/mp3:'(.*?)'/)[1];
    if (playUrl.indexOf('m4a') >= 0 || playUrl.indexOf('mp3') >= 0 ) {
        return JSON.stringify({
            parse: 0,
            url: playUrl,
        });
    } else {
        try {
            const iframeHtml = (
                await req(HOST + iframe[0].attribs.src, {
                    headers: {
                        'Referer': link,
                        'User-Agent': MOBILE_UA,
                    },
                })
            ).content;
            const playUrl = playUrl + '.m4a' + iframeHtml.match(/(\?.*?)'/)[1];
            if (playUrl.indexOf('http') >= 0) {
                return JSON.stringify({
                    parse: 0,
                    url: playUrl,
                });
            } else {
                const iframeHtml = (
                    await req(HOST + iframe[0].attribs.src, {
                        headers: {
                            'Referer': link,
                            'User-Agent': MOBILE_UA,
                        },
                    })
                ).content;
                const playUrl2 = iframeHtml.match(/url[\s\S]*?(http.*?)'/)[1];
                if (playUrl2.indexOf('\?') >= 0) {
                    return JSON.stringify({
                        parse: 0,
                        url: playUrl2,
                    });
                } else {
                    const playUrl3 = playUrl2 + playUrl
                    return JSON.stringify({
                        parse: 0,
                        url: playUrl3,
                    });
                }
            }
        } catch (e) {}
        if (playUrl.indexOf('http') >= 0) {
            const playUrl = playUrl + '.m4a';
            return JSON.stringify({
                parse: 0,
                url: playUrl,
            });
        } else {
            const iframeHtml = (
                await req(HOST + iframe[0].attribs.src, {
                    headers: {
                        'Referer': link,
                        'User-Agent': MOBILE_UA,
                    },
                })
            ).content;
            const playUrl4 = iframeHtml.match(/url[\s\S]*?(http.*?)'/)[1];
            return JSON.stringify({
                parse: 0,
                url: playUrl4 + '.m4a',
            });
        }
    }
}

async function search(wd, quick) {
    const link = HOST + '/search.html?searchtype=name&searchword=' + wd +'&page=1';
    const html = await request(link);
    const $ = load(html);
    const items = $('ul.book-ol > li');
    let videos = _.map(items, (item) => {
        const it = $(item).find('a:first')[0];
        const img = $(item).find('img:first')[0];
        const remarks = $($(item).find('div.book-meta')[0]).text().trim();
        return {
            vod_id: it.attribs.href.replace(/.*?\/tingshu\/(.*)/g, '$1'),
            vod_name: it.attribs.title.replace('有声小说',''),
            vod_pic: img.attribs['data-original'],
            vod_remarks: remarks.replace('佚名（著）','').replace('佚名（播）','').replace('未知（著）','').replace('未知（播）','') || '',
        };
    });
    return JSON.stringify({
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