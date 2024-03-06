import { Crypto, _, load } from './lib/cat.js';

let key = 'copymanga';
let url = 'https://www.mangacopy.com';

let siteKey = '';
let siteType = 0;

const PC_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36';

async function request(reqUrl) {
    let resp = await req(reqUrl, {
        headers: {
            'User-Agent': PC_UA,
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
    var html = await request(url + '/comics');
    const $ = load(html);
    let filterObj = {};

    let region = {
        key: 'region',
        name: '地區',
        init: '',
    };
    let regionValues = [];
    regionValues.push({ n: '全部', v: '' });
    regionValues.push({ n: '日漫', v: '0' });
    regionValues.push({ n: '韓漫', v: '1' });
    regionValues.push({ n: '美漫', v: '2' });
    region['value'] = regionValues;

    let ordering = {
        key: 'ordering',
        name: '排序',
        init: '-datetime_updated',
    };
    let orderingValues = [];
    orderingValues.push({ n: '更新時間↓', v: '-datetime_updated' });
    orderingValues.push({ n: '更新時間↑', v: 'datetime_updated' });
    orderingValues.push({ n: '熱門↓', v: '-popular' });
    orderingValues.push({ n: '熱門↑', v: 'popular' });
    ordering['value'] = orderingValues;

    let status = {
        key: 'sort',
        name: '狀態',
        init: '',
    };
    let statusValues = [];
    statusValues.push({ n: '全部', v: '' });
    statusValues.push({ n: '連載中', v: '0' });
    statusValues.push({ n: '已完結', v: '1' });
    statusValues.push({ n: '短篇', v: '2' });
    status['value'] = statusValues;

    filterObj['c1'] = [];

    let themeValues = [{ n: '全部', v: '' }];
    for (const a of $('div.classify-right>a[href*="theme="]')) {
        themeValues.push({
            n: $(a).text().trim(),
            v: a.attribs.href.match(/.*?theme=(.*)&/)[1],
        });
    }

    _.each(_.chunk(themeValues, 11), (vals) => {
        let theme = {
            key: 'theme',
            name: '',
            init: '',
            value: vals,
        };
        filterObj['c1'].push(theme);
    });

    filterObj['c1'].push(region);
    filterObj['c1'].push(status);
    filterObj['c1'].push(ordering);

    return {
        class: [{ type_name: 'all', type_id: 'c1' }],
        filters: filterObj,
    };
}

async function category(tid, pg, filter, extend) {
    if (pg == 0) pg = 1;
    let link = url + `/comics?theme=${extend.theme || ''}&region=${extend.region || ''}&status=${extend.status || ''}&ordering=${extend.ordering || '-datetime_updated'}`;
    if (pg > 1) {
        link += '&offset=' + (pg - 1) * 50 + '&limit=50';
    }
    var html = await request(link);
    const $ = load(html);
    const list = eval($('div[class="row exemptComic-box"]')[0].attribs.list);
    let books = [];
    for (const book of list) {
        books.push({
            book_id: book.path_word,
            book_name: book.name,
            book_pic: book.cover,
            book_remarks: book.author ? book.author[0].name : '',
        });
    }
    return {
        page: pg,
        pagecount: list.length == 50 ? pg + 1 : pg,
        list: books,
    };
}

async function detail(id) {
    var html = await request(url + `/comic/${id}`);
    const $ = load(html);
    let book = {
        book_name: $('h6').text().trim(),
        book_director: _.map($('span.comicParticulars-right-txt>a[href*="/author/"]'), (a) => $(a).text().trim()).join('/'),
        book_content: $('p.intro').text().trim(),
    };

    const data = JSON.parse(await request(url + `/comicdetail/${id}/chapters`)).results;
    var key = Crypto.enc.Utf8.parse('xxxmanga.woo.key');
    var iv = Crypto.enc.Utf8.parse(data.substr(0, 16));
    var src = Crypto.enc.Hex.parse(data.substr(16));
    var dst = Crypto.AES.decrypt({ ciphertext: src }, key, { iv: iv, padding: Crypto.pad.Pkcs7 });
    dst = Crypto.enc.Utf8.stringify(dst);

    const groups = JSON.parse(dst).groups;

    let urls = _.map(groups.default.chapters, (c) => {
        return c.name + '$' + id + '|' + c.id;
    }).join('#');
    book.volumes = '默認';
    book.urls = urls;

    return {
        list: [book],
    };
}

async function play(flag, id, flags) {
    try {
        var info = id.split('|');
        var html = await request(url + `/comic/${info[0]}/chapter/${info[1]}`);
        const $ = load(html);
        const data = $('div.imageData')[0].attribs.contentkey;
        var key = Crypto.enc.Utf8.parse('xxxmanga.woo.key');
        var iv = Crypto.enc.Utf8.parse(data.substr(0, 16));
        var src = Crypto.enc.Hex.parse(data.substr(16));
        var dst = Crypto.AES.decrypt({ ciphertext: src }, key, { iv: iv, padding: Crypto.pad.Pkcs7 });
        dst = Crypto.enc.Utf8.stringify(dst);
        const list = JSON.parse(dst);
        var content = [];
        for (let index = 0; index < list.length; index++) {
            const element = list[index];
            content[index] = element.url;
        }
        return {
            content: content,
        };
    } catch (e) {
        return {
            content: '',
        };
    }
}

async function search(wd, quick, pg) {
    if (pg == 0) pg = 1;
    const link = `${url}/api/kb/web/searcha/comics?offset=${pg > 1 ? ((pg - 1) * 12).toString() : ''}&platform=2&limit=12&q=${wd}&q_type=`;
    var list = JSON.parse(await request(link)).results.list;
    const books = [];
    for (const book of list) {
        books.push({
            book_id: book.path_word,
            book_name: book.name,
            book_pic: book.cover,
            book_remarks: book.author ? book.author[0].name : '',
        });
    }
    return {
        page: pg,
        pagecount: list.length == 12 ? pg + 1 : pg,
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
