import { Crypto, load, _ } from 'assets://js/lib/cat.js';

let key = 'zxzj';
let HOST = 'https://www.zxzj.site'; // 地址发布页
let host = 'https://www.zxzja.com';
let siteKey = '';
let siteType = 0;

const MOBILE_UA = 'Mozilla/5.0 (Linux; Android 11; M2007J3SC Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045714 Mobile Safari/537.36';

async function request(reqUrl, extHeader) {
    let headers = {
        'User-Agent': MOBILE_UA,
        'Referer': host,
    };
    if (extHeader) {
        headers = _.merge(headers, extHeader);
    }
    const res = await req(reqUrl, {
        method: 'get',
        headers: headers,
    });
    return res.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
    const html = await request(HOST);
    const $ = load(html);
    host = $('div.content-top > ul > li').find('a:first')[0].attribs.href;
    console.debug('在线之家 跳转地址 =====>' + host); // js_debug.log
}

async function home(filter) {
    const html = await request(host);
    const $ = load(html);
    const class_parse = $('ul.stui-header__menu > li > a[href*=list]');
    let classes = _.map(class_parse, (cls) => {
        let typeId = cls.attribs['href'];
        typeId = typeId.substring(typeId.lastIndexOf('/') + 1).replace('.html', '');
        return {
            type_id: typeId,
            type_name: cls.children[0].data,
        };
    });
    const filterObj = {
        1: [{ key: 'class', name: '剧情', init: '', value: [{ n: '全部', v: '' }, { n: '喜剧', v: '喜剧' }, { n: '爱情', v: '爱情' }, { n: '恐怖', v: '恐怖' }, { n: '动作', v: '动作' }, { n: '科幻', v: '科幻' }, { n: '剧情', v: '剧情' }, { n: '战争', v: '战争' }, { n: '警匪', v: '警匪' }, { n: '犯罪', v: '犯罪' }, { n: '动画', v: '动画' }, { n: '奇幻', v: '奇幻' }, { n: '冒险', v: '冒险' }] }, { key: 'area', name: '地区', init: '', value: [{ n: '全部', v: '' }, { n: '大陆', v: '大陆' }, { n: '香港', v: '香港' }, { n: '台湾', v: '台湾' }, { n: '欧美', v: '欧美' }, { n: '韩国', v: '韩国' }, { n: '日本', v: '日本' }, { n: '泰国', v: '泰国' }, { n: '印度', v: '印度' }, { n: '俄罗斯', v: '俄罗斯' }, { n: '其他', v: '其他' }] }],
        2: [{ key: 'class', name: '剧情', init: '', value: [{ n: '全部', v: '' }, { n: '剧情', v: '剧情' }, { n: '喜剧', v: '喜剧' }, { n: '爱情', v: '爱情' }, { n: '动作', v: '动作' }, { n: '悬疑', v: '悬疑' }, { n: '恐怖', v: '恐怖' }, { n: '奇幻', v: '奇幻' }, { n: '惊悚', v: '惊悚' }, { n: '犯罪', v: '犯罪' }, { n: '科幻', v: '科幻' }, { n: '音乐', v: '音乐' }, { n: '其他', v: '其他' }] }],
        3: [{ key: 'class', name: '剧情', init: '', value: [{ n: '全部', v: '' }, { n: '剧情', v: '剧情' }, { n: '喜剧', v: '喜剧' }, { n: '爱情', v: '爱情' }, { n: '动作', v: '动作' }, { n: '悬疑', v: '悬疑' }, { n: '恐怖', v: '恐怖' }, { n: '奇幻', v: '奇幻' }, { n: '惊悚', v: '惊悚' }, { n: '犯罪', v: '犯罪' }, { n: '科幻', v: '科幻' }, { n: '音乐', v: '音乐' }, { n: '其他', v: '其他' }] }],
        4: [{ key: 'class', name: '剧情', init: '', value: [{ n: '全部', v: '' }, { n: '剧情', v: '剧情' }, { n: '喜剧', v: '喜剧' }, { n: '爱情', v: '爱情' }, { n: '动作', v: '动作' }, { n: '悬疑', v: '悬疑' }, { n: '恐怖', v: '恐怖' }, { n: '奇幻', v: '奇幻' }, { n: '惊悚', v: '惊悚' }, { n: '犯罪', v: '犯罪' }, { n: '科幻', v: '科幻' }, { n: '音乐', v: '音乐' }, { n: '其他', v: '其他' }] }],
        6: [{ key: 'class', name: '剧情', init: '', value: [{ n: '全部', v: '' }, { n: '情感', v: '情感' }, { n: '科幻', v: '科幻' }, { n: '热血', v: '热血' }, { n: '推理', v: '推理' }, { n: '搞笑', v: '搞笑' }, { n: '冒险', v: '冒险' }, { n: '萝莉', v: '萝莉' }, { n: '校园', v: '校园' }, { n: '动作', v: '动作' }, { n: '机战', v: '机战' }, { n: '运动', v: '运动' }, { n: '战争', v: '战争' }, { n: '少年', v: '少年' }] }, { key: 'area', name: '地区', init: '', value: [{ n: '全部', v: '' }, { n: '国产', v: '国产' }, { n: '日本', v: '日本' }, { n: '欧美', v: '欧美' }, { n: '其他', v: '其他' }] }]
    };
    let filYer = { key: 'year', name: '年份', init: '', value: [{ n: '全部', v: '' }, { n: '2024', v: '2024' }, { n: '2023', v: '2023' }, { n: '2022', v: '2022' }, { n: '2021', v: '2021' }, { n: '2020', v: '2020' }, { n: '2019', v: '2019' }, { n: '2018', v: '2018' }, { n: '2017', v: '2017' }, { n: '2016', v: '2016' }, { n: '2015', v: '2015' }, { n: '2014', v: '2014' }, { n: '2013', v: '2013' }, { n: '2012', v: '2012' }, { n: '2011', v: '2011' }] };
    let filBy = { key: 'by', name: '排序', value: [{ n: '时间', v: 'time' }, { n: '人气', v: 'hits' }, { n: '评分', v: 'score' }] };
    return JSON.stringify({
        class: _.map(classes, (cls) => {
            if (filterObj[cls.type_id]) {
                filterObj[cls.type_id].push(filYer, filBy);
                filterObj[cls.type_id][0]['init'] = filterObj[cls.type_id][0].value[0].v;
            } else {
                filterObj[cls.type_id] = [];
                filterObj[cls.type_id].push(filYer, filBy)
            }
            return cls;
        }),
        filters: filterObj,
    });
}

async function homeVod() {
    const link = host + '/vodshow/1--hits---------2023.html';
    const html = await request(link);
    const $ = load(html);
    const js2Base = await js2Proxy(true, siteType, siteKey, 'img/', {});
    const items = $('ul.stui-vodlist > li');
    let videos = _.map(items, (item) => {
        const a = $(item).find('a:first')[0];
        const remarks = $($(item).find('span.pic-text')[0]).text().trim();
        return {
            vod_id: a.attribs.href.replace(/.*?\/detail\/(.*).html/g, '$1'),
            vod_name: a.attribs.title,
            vod_pic: js2Base + base64Encode(a.attribs['data-original']),
            vod_remarks: remarks || '',
        };
    });
    return JSON.stringify({
        list: videos,
    });
}

async function category(tid, pg, filter, extend) {
    if (pg <= 0 || typeof (pg) == 'undefined') pg = 1;
    const link = host + '/vodshow/' + tid + '-' + (extend.area || '') + '-' + (extend.by || 'time') + '-' + (extend.class || '') + '-' + (extend.lang || '') + '-' + (extend.letter || '') + '---' + pg + '---' + (extend.year || '') + '.html';
    const html = await request(link);
    const $ = load(html);
    const js2Base = await js2Proxy(true, siteType, siteKey, 'img/', {});
    const items = $('ul.stui-vodlist > li');
    let videos = _.map(items, (item) => {
        const a = $(item).find('a:first')[0];
        const remarks = $($(item).find('span.pic-text')[0]).text().trim();
        return {
            vod_id: a.attribs.href.replace(/.*?\/detail\/(.*).html/g, '$1'),
            vod_name: a.attribs.title,
            vod_pic: js2Base + base64Encode(a.attribs['data-original']),
            vod_remarks: remarks || '',
        };
    });
    const hasMore = $('ul.stui-page__item > li > a:contains(下一页)').length > 0;
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
    const html = await request(host + '/detail/' + id + '.html');
    const $ = load(html);
    const js2Base = await js2Proxy(true, siteType, siteKey, 'img/', {});
    const vod = {
        vod_id: id,
        vod_name: $('h1:first').text().trim(),
        vod_type: $('.stui-content__detail p:first a').text(),
        vod_actor: $('.stui-content__detail p:nth-child(3)').text().replace('主演：', ''),
        vod_director: $('.stui-content__detail p:nth-child(4)').text().replace('导演：', ''),
        vod_pic: js2Base + base64Encode($('.stui-content__thumb img:first').attr('data-original')),
        vod_remarks: $('.stui-content__detail p:nth-child(5)').text() || '',
        vod_content: $('span.detail-content').text().trim(),
    };
    let playMap = {};
    const tabs = $('div.stui-vodlist__head > h3');
    const playlists = $('ul.stui-content__playlist');
    _.each(tabs, (tab, i) => {
        const from = tab.children[0].data;
        let list = playlists[i];
        list = $(list).find('a');
        _.each(list, (it) => {
            const title = it.children[0].data;
            const playUrl = it.attribs.href;
            if (title.length == 0) title = it.children[0].data.trim();
            if (!playMap.hasOwnProperty(from)) {
                playMap[from] = [];
            }
            playMap[from].push(title + '$' + playUrl);
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
    const html = await request(host + id);
    const mhtml = html.match(/r player_.*?=(.*?)</)[1];
    const json = JSON.parse(mhtml);
    const url = json.url;
    const from = json.from;
    if (json.encrypt == '1') {
        url = unescape(url)
    } else if (json.encrypt == '2') {
        url = unescape(base64Decode(url))
    }
    if (url.includes('m3u8') || url.includes('mp4')) {
        // console.debug('在线之家url =====>' + url); // js_debug.log
        return JSON.stringify({
            parse: 0,
            url: url,
        });
    } else if (from.includes('line3') || from.includes('line4') || from.includes('line5')) {
        const extHeader = {
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-dest': 'iframe',
            'upgrade-insecure-requests': 1,
        };
        const ifrwy = await request(url, extHeader);
        const resultv2 = ifrwy.match(/var result_v2 = {(.*?)};/)[1];
        const data = JSON.parse('{' + resultv2 + '}').data;
        const code = data.split('').reverse();
        let temp = '';
        for (let i = 0x0; i < code.length; i = i + 0x2) {
            temp += String.fromCharCode(parseInt(code[i] + code[i + 0x1], 0x10))
        }
        const purl = temp.substring(0x0, (temp.length - 0x7) / 0x2) + temp.substring((temp.length - 0x7) / 0x2 + 0x7);
        // console.debug('在线之家purl =====>' + purl); // js_debug.log
        return JSON.stringify({
            parse: 0,
            url: purl,
        });
    } else {
        // console.debug('在线之家url =====>' + '空'); // js_debug.log
        return '{}';
    }
}

async function search(wd, quick) {
    var data = JSON.parse(await request(host + '/index.php/ajax/suggest?mid=1&wd=' + wd + '&limit=50')).list;
    const js2Base = await js2Proxy(true, siteType, siteKey, 'img/', {});
    let videos = _.map(data, (it) => {
        return {
            vod_id: it.id,
            vod_name: it.name,
            vod_pic: js2Base + base64Encode(it.pic),
            vod_remarks: '',
        }
    });
    return JSON.stringify({
        list: videos,
        limit: 50,
    });
}

function base64Encode(text) {
    return Crypto.enc.Base64.stringify(Crypto.enc.Utf8.parse(text));
}

function base64Decode(text) {
    return Crypto.enc.Utf8.stringify(Crypto.enc.Base64.parse(text));
}

async function proxy(segments, headers) {
    let what = segments[0];
    let url = base64Decode(segments[1]);
    if (what == 'img') {
        var resp = await req(url, {
            buffer: 2,
            headers: {
                Referer: 'https://api.douban.com/',
                'User-Agent': MOBILE_UA,
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