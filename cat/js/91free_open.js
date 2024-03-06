import { Crypto, load, _ } from './lib/cat.js';

let key = '1free';
let HOST = 'https://91d.top';//歪片星球.com
let url = '';
let siteKey = '';
let siteType = 0;

const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13E230 Safari/601.1';

async function request(reqUrl, agentSp) {
    let res = await req(reqUrl, {
        method: 'get',
        headers: {
            'User-Agent': agentSp || UA,
            'Referer': HOST
        },
    });
    return res.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
    let html = await request(HOST);
       url = html.match(/<a href="(http.*www.*)" target=.*>/)[1]
    console.debug('跳转地址 =====>' + url); // js_debug.log
}

async function home(filter) {
    let classes = [{"type_id":1,"type_name":"电影"},{"type_id":2,"type_name":"追剧"},{"type_id":3,"type_name":"综艺"},{"type_id":4,"type_name":"动漫"}];
    let filterObj = {
        "1":[{"key":"cateId","name":"类型","value":[{"n":"全部","v":"1"},{"n":"纪录片","v":"20"},{"n":"动作片","v":"6"},{"n":"爱情片","v":"8"},{"n":"科幻片","v":"9"},{"n":"恐怖片","v":"10"},{"n":"剧情片","v":"11"},{"n":"战争片","v":"12"},{"n":"喜剧片","v":"7"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"中国大陆","v":"大陆"},{"n":"中国香港","v":"香港"},{"n":"中国台湾","v":"台湾"},{"n":"美国","v":"美国"},{"n":"法国","v":"法国"},{"n":"英国","v":"英国"},{"n":"日本","v":"日本"},{"n":"韩国","v":"韩国"},{"n":"德国","v":"德国"},{"n":"泰国","v":"泰国"},{"n":"印度","v":"印度"},{"n":"意大利","v":"意大利"},{"n":"西班牙","v":"西班牙"},{"n":"加拿大","v":"加拿大"},{"n":"其他","v":"其他"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"法语","v":"法语"},{"n":"德语","v":"德语"},{"n":"其它","v":"其它"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
		"2":[{"key":"cateId","name":"类型","value":[{"n":"全部","v":"2"},{"n":"国产剧","v":"13"},{"n":"欧美剧","v":"14"},{"n":"港台剧","v":"15"},{"n":"日韩剧","v":"16"},{"n":"泰剧","v":"21"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
		"3":[{"key":"cateId","name":"类型","value":[{"n":"全部","v":"3"},{"n":"大陆综艺","v":"22"},{"n":"港台综艺","v":"25"},{"n":"日韩综艺","v":"24"},{"n":"欧美综艺","v":"23"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
		"4":[{"key":"cateId","name":"类型","value":[{"n":"全部","v":"4"},{"n":"国产动漫","v":"26"},{"n":"日韩动漫","v":"28"},{"n":"欧美动漫","v":"27"},{"n":"港台动漫","v":"29"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}]
	};

    return JSON.stringify({
        class: classes,
        filters: filterObj,
    });
}

async function homeVod() {}

async function category(tid, pg, filter, extend) {
    if (pg <= 0) pg = 1;
    const link = url + '/vodshow/' + (extend.cateId || tid) + '-' + (extend.area || '') + '-' + (extend.by || 'time') + '--' + (extend.lang || '') + '----' + pg + '---' + (extend.year || '') + '.html';//https://91free.live/vodshow/6-%E7%BE%8E%E5%9B%BD-hits--%E8%8B%B1%E8%AF%AD----2---2022.html
    const html = await request(link);
    const $ = load(html);
    const items = $('div.module-items a.module-poster-item');
    let videos = _.map(items, (item) => {
        const it = $(item)[0];
        const k = $(item).find('img:first')[0];
        const remarks = $($(item).find('div.module-item-note')[0]).text().trim();
        return {
            vod_id: it.attribs.href.replace(/\/voddetail\/(.*?).html/g, '$1'),
            vod_name: k.attribs.alt,
            vod_pic: k.attribs['data-original'],
            vod_remarks: remarks || '',
        };
    });
    const hasMore = $('div#page > a:contains(下一页)').length > 0;
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
    const html = await request( url + '/voddetail/' + id + '.html');
    const $ = load(html);
    const vod = {
        vod_id: id,
        vod_name: $('h1:first').text().trim(),
        vod_type: $('.module-info-tag a').text(),
        vod_actor: $('.module-info-item-content').text(),
        vod_pic: $('.module-info img:first').attr('data-src'),
        vod_remarks : $('.stui-content__detail p:nth-child(5)').text() || '',
        vod_content: $('.module-info-introduction-content p').text().trim(),
    };
    let playMap = {};
    const tabs = $('div.module-tab-items-box div.module-tab-item span');
    const playlists = $('div.module-play-list-content');
    _.each(tabs, (tab, i) => {
        const from = $(tab).text();
        let list = playlists[i];
        list = $(list).find('a');
        _.each(list, (it) => {
            const title = $(it).text();
            const playUrl = it.attribs.href.replace(/\/vodplay\/(.*?).html/g, '$1');
            if (title.length == 0) title = it.children[0].data.trim();
            if (!playMap.hasOwnProperty(from)) {
                playMap[from] = [];
            }
            playMap[from].push( title + '$' + playUrl);
        });
    });
    vod.vod_play_from = _.keys(playMap).join('$$$');
    const urls = _.values(playMap);
    let vod_play_url = _.map(urls, (urlist) => {
        return urlist.join('#');
    });
    vod.vod_play_url = vod_play_url.join('$$$');
    return JSON.stringify({
        list: [vod],
    });
}
async function play(flag, id, flags) {
    const link = url + '/vodplay/' + id + '.html';
    const html = await request(link);
    const $ = load(html);
    const js = JSON.parse($('script:contains(player_)').html().replace('var player_aaaa=',''));
    const playUrl = js.url;
    return JSON.stringify({
        parse: 0,
        url: playUrl,
    });
}

function base64Encode(text) {
    return Crypto.enc.Base64.stringify(Crypto.enc.Utf8.parse(text));
}

function base64Decode(text) {
    return Crypto.enc.Utf8.stringify(Crypto.enc.Base64.parse(text));
}
async function search(wd, quick, pg) {
    if (pg <= 0) pg = 1;
    let data = await request(url + '/phsch/' + '/page/' + pg + '/wd/' + wd + '.html');//https://www.physkan.com/phsch/page/2/wd/%E6%88%91.html
    const $ = load(data);
    const items = $('div.module-items > div.module-item');
    let videos = _.map(items, (item) => {
        const it = $(item).find('a:first')[0];
        const k = $(item).find('img:first')[0];
        const remarks = $($(item).find('div.module-item-note')[0]).text().trim();
        return {
            vod_id: it.attribs.href.replace(/\/v\/(.*?).html/g, '$1'),
            vod_name: k.attribs.alt,
            vod_pic: k.attribs['data-original'],
            vod_remarks: remarks || '',
        };
    });
    const hasMore = $('div#page > a:contains(下一页)').length > 0;
    const pgCount = hasMore ? parseInt(pg) + 1 : parseInt(pg);
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: 24,
        total: 24 * pgCount,
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