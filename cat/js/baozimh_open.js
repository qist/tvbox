import { Crypto, _, load } from './lib/cat.js';

let key = 'baozimh';
let url = 'https://cn.baozimh.com';
const img = 'https://static-tw.baozimh.com/cover/';

const img2 = '?w=285&h=375&q=100';

let siteKey = '';
let siteType = 0;

const UA = 'Mozilla/5.0 (Linux; Android 11; M2007J3SC Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045714 Mobile Safari/537.36';

async function request(reqUrl) {
    let resp = await req(reqUrl, {
        headers: {
            'User-Agent': UA,
        },
    });
    return resp.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
}

async function home(filter) {
    var html = await request(url + '/classify');
    const $ = load(html);

    let filterObj = { c1: [] };

    for (const nav of $('div.classify div.nav')) {
        const as = $(nav).find('a.item');
        const checkUrl = decodeURIComponent(as[1].attribs.href);
        const reg = /type=(.*)&region=(.*)&state=(.*)&filter=(.*)/;
        const matchs = checkUrl.match(reg);
        let typeKey = '';
        let typeIdx = 1;
        if (matchs[1] != 'all') {
            typeKey = 'type';
            typeIdx = 1;
        } else if (matchs[2] != 'all') {
            typeKey = 'region';
            typeIdx = 2;
        } else if (matchs[3] != 'all') {
            typeKey = 'state';
            typeIdx = 3;
        } else if (matchs[4] != '*') {
            typeKey = 'filter';
            typeIdx = 4;
        }
        const tvals = [];
        for (const a of as) {
            tvals.push({
                n: $(a).text().trim(),
                v: decodeURIComponent(a.attribs.href).match(reg)[typeIdx],
            });
        }
        filterObj['c1'].push({
            key: typeKey,
            name: '',
            wrap: typeIdx == 1 ? 1 : 0,
            init: typeIdx == 4 ? '*' : 'all',
            value: tvals,
        });
    }

    return {
        class: [{ type_name: 'all', type_id: 'c1' }],
        filters: filterObj,
    };
}

async function category(tid, pg, filter, extend) {
    if (pg == 0) pg = 1;
    let link = `${url}/api/bzmhq/amp_comic_list?type=${extend.type || 'all'}&region=${extend.region || 'all'}&state=${extend.state || 'all'}&filter=${extend.filter || '*'}`;
    link += '&page=' + pg + '&limit=36&language=cn';
    var html = await request(link);
    const data = JSON.parse(html);
    let books = [];
    for (const book of data.items) {
        books.push({
            book_id: book.comic_id,
            book_name: book.name,
            book_pic: img + book.topic_img + img2,
            book_remarks: book.author || '',
        });
    }
    return {
        page: pg,
        pagecount: books.length == 36 ? pg + 1 : pg,
        list: books,
    };
}

async function detail(id) {
    var html = await request(`${url}/comic/${id}`);
    const $ = load(html);
    let book = {
        book_director: $('[data-hid$=og:novel:author]')[0].attribs.content || '',
        book_content: $('[data-hid$=og:description]')[0].attribs.content || '',
    };

    const formatUrl = (a) => {
        return $(a).text().replace(/\$|#/g, ' ').trim() + '$' + decodeURIComponent(a.attribs.href);
    };

    let urls = _.map($('div#chapter-items a.comics-chapters__item'), formatUrl);
    urls.push(..._.map($('div#chapters_other_list a.comics-chapters__item'), formatUrl));
    if (urls.length == 0) {
        urls = _.reverse(_.map($('div.pure-g a.comics-chapters__item'), formatUrl));
    }
    book.volumes = '默認';
    book.urls = urls.join('#');

    return {
        list: [book],
    };
}

async function play(flag, id, flags) {
    try {
        var html = await request(url + id);
        const $ = load(html);

        var content = [];
        for (const img of $('amp-img')) {
            content.push(img.attribs.src);
        }
        return {
            content: content,
        };
    } catch (e) {}
    return {
        content: [],
    };
}

async function search(wd, quick, pg) {
    var html = await request(`${url}/search?q=${wd}`);
    const $ = load(html);
    const books = [];
    for (const a of $('div.classify-items a.comics-card__poster')) {
        books.push({
            book_id: a.attribs.href.replace('/comic/', ''),
            book_name: a.attribs.title,
            book_pic: $(a).find('amp-img:first')[0].attribs.src,
            book_remarks: '',
        });
    }
    return {
        page: 1,
        pagecount: 1,
        list: books,
    };
}

export function __jsEvalReturn() {
    return {
        init: init,
        home: home,
        category: category,
        detail: detail,
        play: play,
        search: search,
    };
}
