import { Crypto, load, _, dayjs } from 'assets://js/lib/cat.js';

let key = 'jiohub';
let url = 'https://jiohub.top';
let siteKey = '';
let siteType = 0;

const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1';

const cookie = {};

async function request(reqUrl, referer, mth, data, hd) {
    const headers = {
        'User-Agent': UA,
        Cookie: _.map(cookie, (value, key) => {
            return `${key}=${value}`;
        }).join(';'),
    };
    if (referer) headers.referer = encodeURIComponent(referer);
    let res = await req(reqUrl, {
        method: mth || 'get',
        headers: headers,
        data: data,
        postType: mth === 'post' ? 'form' : '',
    });
    return res.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
}

async function home(filter) {
    const html = await request(url);
    const $ = load(html);
    const series = $('.nav-list a[href*=/video]');
    let classes = _.map(series, (s) => {
        let typeId = s.attribs['href'];
        let typeName = typeId.match(/\/video\/(.*)\?/)[1];
        typeName = decodeURIComponent(typeName);
        return {
            type_id: typeName,
            type_name: typeName,
        };
    });
    return JSON.stringify({
        class: classes,
    });
}

async function homeVod() {
    return '{}';
}

async function category(tid, pg, filter, extend) {
    let page = pg || 1;
    if (page == 0) page = 1;
    const link = url + '/video/' + tid + "?page=" + page + '&size=18';
    const html = await request(link);
    const $ = load(html);
    const items = $('div.content-body > a');
    let videos = _.map(items, (item) => {
        const img = $(item).find('img:first')[0].attribs['src'];
        const a = item.attribs['href'].match(/\/watch\/(.*)/)[1];
        const n = ($(item).find('p.card-title')[0]).children[0].data;
        let speed = ($(item).find('p.item-speed')[0]).children[0].data || '';
        const score = ($(item).find('p.score')[0]).children[0].data || '';
        if (speed == tid) speed = '';
        return {
            vod_id: a,
            vod_name: n,
            vod_pic: img,
            vod_remarks: speed || score || '',
        };
    });

    let total = 18;
    const pag = $('ui-pagination');
    if (pag.length > 0) {
        try {
            total = parseInt(pag[0].attribs['total']);
        } catch (error) {

        }
    }

    return JSON.stringify({
        page: page,
        pagecount: _.ceil(total / 18),
        list: videos,
    });
}

function stripHtmlTag(src) {
    return src
        .replace(/<\/?[^>]+(>|$)/g, '')
        .replace(/&.{1,5};/g, '')
        .replace(/\s{2,}/g, ' ');
}

async function detail(id) {
    const html = await request(url + '/watch/' + id);
    const $ = load(html);
    const detail = $('div.content-detail > p');
    let vod = {
        vod_id: id,
        vod_content: stripHtmlTag($('div.content-detail span.detail-sketch').html()).trim(),
    };
    for (const info of detail) {
        const i = $(info).text().trim();
        if (i.startsWith('地区：')) {
            vod.vod_area = i.substring(3);
        } else if (i.startsWith('年份：')) {
            vod.vod_year = i.substring(3);
        } else if (i.startsWith('类型：')) {
            vod.vod_type = i.substring(3);
        } else if (i.startsWith('导演：')) {
            vod.vod_director = i.substring(3);
        } else if (i.startsWith('主演：')) {
            vod.vod_actor = i.substring(3);
        } else if (i.startsWith('语言：')) {
            vod.vod_lang = i.substring(3);
        }
    }

    const urls = html.match(/let urls = \"(.*)\";/)[1].replace(/_/g, '/').replace(/-/g, '+');
    var key = Crypto.enc.Utf8.parse("cf2d1a-6a4d-9ef8");
    var playlist = Crypto.AES.decrypt(urls, key, { iv: key, padding: Crypto.pad.Pkcs7 });
    playlist = Crypto.enc.Utf8.stringify(playlist).split('\n');
    vod.vod_play_from = 'JOJO';
    vod.vod_play_url = playlist.join('#');
    return JSON.stringify({
        list: [vod],
    });
}

function playPid() {
    var key = Crypto.enc.Utf8.parse('VSmJTRRE'+dayjs().format('YYYYMMDD'));
    var iv = Crypto.enc.Hex.parse("00000000000000000000000000000000");
    var pid = Crypto.AES.encrypt(dayjs().format('YYYY-MM-DD HH:mm'), key, { iv: iv, padding: Crypto.pad.Pkcs7 });
    pid = pid.toString().replace(/\+/g, '-');
    return pid;
}

async function play(flag, id, flags) {
    return JSON.stringify({
        parse: 0,
        url: id + '?pid=' + playPid(),
        header: {
            'User-Agent': UA,
        },
    });
}

async function search(wd, quick, pg) {
    let page = pg || 1;
    if (page == 0) page = 1;
    const link = url + '/video/search?q=' + wd + "&page=" + page + '&size=18&pid=' + playPid();
    const html = await request(link);
    const $ = load(html);
    const items = $('div.content-body > a');
    let videos = _.map(items, (item) => {
        const img = $(item).find('img:first')[0].attribs['src'];
        const a = item.attribs['href'].match(/\/watch\/(.*)/)[1];
        const n = ($(item).find('p.card-title')[0]).children[0].data;
        let speed = ($(item).find('p.item-speed')[0]).children[0].data || '';
        const score = ($(item).find('p.score')[0]).children[0].data || '';
        if (speed == '电影') speed = '';
        return {
            vod_id: a,
            vod_name: n,
            vod_pic: img,
            vod_remarks: speed || score || '',
        };
    });

    let total = 18;
    const pag = $('ui-pagination');
    if (pag.length > 0) {
        try {
            total = parseInt(pag[0].attribs['total']);
        } catch (error) {

        }
    }

    return JSON.stringify({
        page: page,
        pagecount: _.ceil(total / 18),
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
