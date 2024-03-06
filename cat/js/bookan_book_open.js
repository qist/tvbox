import { _ } from './lib/cat.js';

let key = 'bookan';
let url = 'https://api.bookan.com.cn';
let siteKey = '';
let siteType = 0;

async function request(reqUrl, agentSp) {
    let res = await req(reqUrl, {
        method: 'get',
    });
    return res.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
}

async function home(filter) {
    return JSON.stringify({
        class: [
            { type_id: '1305', type_name: '少年读物' },
            { type_id: '1304', type_name: '儿童文学' },
            { type_id: '1320', type_name: '国学经典' },
            { type_id: '1306', type_name: '文艺少年' },
            { type_id: '1309', type_name: '育儿心经' },
            { type_id: '1310', type_name: '心理哲学' },
            { type_id: '1307', type_name: '青春励志' },
            { type_id: '1312', type_name: '历史小说' },
            { type_id: '1303', type_name: '故事会' },
            { type_id: '1317', type_name: '音乐戏剧' },
            { type_id: '1319', type_name: '相声评书' },
        ],
    });
}

async function category(tid, pg, filter, extend) {
    pg = pg || 1;
    if (pg == 0) pg = 1;
    let content = await request(`${url}/voice/book/list?instance_id=25304&page=${pg}&category_id=${tid}&num=24`);
    let data = JSON.parse(content).data;
    let books = [];
    for (const book of data.list) {
        books.push({
            book_id: book.id,
            book_name: book.name,
            book_pic: book.cover,
            book_remarks: book.extra.author,
        });
    }
    return JSON.stringify({
        page: data.current_page,
        pagecount: data.last_page,
        limit: 24,
        total: data.total,
        list: books,
    });
}

async function detail(id) {
    let content = await request(`${url}/voice/album/units?album_id=${id}&page=1&num=200&order=1`);
    let data = JSON.parse(content).data;

    let book = {
		audio:1,
        book_id: id,
        type_name: '',
        book_year: '',
        book_area: '',
        book_remarks: '',
        book_actor: '',
        book_director: '',
        book_content: '',
    };
    let us = _.map(data.list, function (b) {
        return formatPlayUrl(b.title) + '$' + b.file;
    }).join('#');
    book.volumes = '书卷';
    book.urls = us;

    return JSON.stringify({
        list: [book],
    });
}

function formatPlayUrl(name) {
    return name
        .trim()
        .replace(/<|>|《|》/g, '')
        .replace(/\$|#/g, ' ')
        .trim();
}

async function proxy(segments, headers) {}

async function play(flag, id, flags) {
    return JSON.stringify({
        parse: 0,
        url: id,
    });
}

async function search(wd, quick, pg) {
    pg = pg || 1;
    if (pg == 0) pg = 1;
    let content = await request(`https://es.bookan.com.cn/api/v3/voice/book?instanceId=25304&keyword=${wd}&pageNum=${pg}&limitNum=20`);
    let data = JSON.parse(content).data;
    let books = [];
    for (const book of data.list) {
        books.push({
            book_id: book.id,
            book_name: book.name,
            book_pic: book.cover,
            book_remarks: book.extra.author,
        });
    }
    return JSON.stringify({
        page: data.current_page,
        pagecount: data.last_page,
        limit: 20,
        total: data.total,
        list: books,
    });
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
