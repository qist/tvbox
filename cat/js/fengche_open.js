import { _, Uri, load } from 'assets://js/lib/cat.js';

let key = 'fengche';
let HOST = 'https://www.qyy158.com';

let siteKey = '';
let siteType = 0;

const PC_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36';

async function request(reqUrl) {
    const resp = await req(reqUrl, {
        headers: {
            'User-Agent': PC_UA,
        },
        buffer: 1,
    });
    return gbk.decode(resp.content);
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
}

async function home(filter) {
    const classes = [{'type_id':'all','type_name':'all'}];
    const filterObj = {
        'all':[{'key':'area','name':'地域','init':'','value':[{'n':'全部','v':''},{'n':'🇨🇳中国','v':'1'},{'n':'🇯🇵日本','v':'2'},{'n':'🇰🇷韩国','v':'3'},{'n':'欧美','v':'4'}]},{'key':'class','name':'类别','init':'','wrap':1,'value':[{'n':'全部','v':''},{'n':'霸总','v':'bazong'},{'n':'修真','v':'xiuzhen'},{'n':'恋爱','v':'lianai'},{'n':'校园','v':'xiaoyuan'},{'n':'冒险','v':'maoxian'},{'n':'搞笑','v':'gaoxiao'},{'n':'生活','v':'shenghuo'},{'n':'热血','v':'rexue'},{'n':'架空','v':'jiakong'},{'n':'后宫','v':'hougong'},{'n':'玄幻','v':'xuanhuan'},{'n':'悬疑','v':'xuanyi'},{'n':'恐怖','v':'kongbu'},{'n':'灵异','v':'lingyi'},{'n':'动作','v':'dongzuo'},{'n':'科幻','v':'kehuan'},{'n':'战争','v':'zhanzheng'},{'n':'古风','v':'gufeng'},{'n':'穿越','v':'chuanyue'},{'n':'竞技','v':'jingji'},{'n':'励志','v':'lizhi'},{'n':'同人','v':'tongren'},{'n':'真人','v':'zhenren'},{'n':'其他','v':'qita'},{'n':'总裁','v':'zongcai'},{'n':'异能','v':'yineng'},{'n':'韩漫','v':'hanman'},{'n':'剧情','v':'juqing'},{'n':'大女主','v':'danvzhu'},{'n':'都市','v':'dushi'},{'n':'格斗','v':'gedou'},{'n':'武侠','v':'wuxia'},{'n':'日常','v':'richang'},{'n':'纯爱','v':'chunai'},{'n':'国漫','v':'guoman'},{'n':'推理','v':'tuili'},{'n':'少年','v':'shaonain'},{'n':'奇幻','v':'qihuan'},{'n':'短篇','v':'duanpian'},{'n':'ABO','v':'abo'},{'n':'运动','v':'yundong'},{'n':'萌系','v':'mengxi'},{'n':'爆笑','v':'baoxiao'},{'n':'蔷薇','v':'qiangwei'},{'n':'百合','v':'baihe'},{'n':'BG','v':'bg'}]},{'key':'status','name':'状态','init':'','value':[{'n':'全部','v':''},{'n':'连载中','v':'1'},{'n':'已完结','v':'2'}]}],
    };
    return {
        class: classes,
        filters: filterObj,
    };
}

async function category(tid, pg, filter, extend) {
    if (pg == 0) pg = 1;
    const uri = new Uri(`${HOST}/sort/`);
    if (extend.class) {
        uri.addQueryParam('class', extend.class);
    }
    if (extend.area) {
        uri.addQueryParam('area', extend.area);
    }
    if (extend.status) {
        uri.addQueryParam('status', extend.status);
    }
    if (pg > 1) {
        uri.addQueryParam('page', pg);
    }
    const link = uri.toString();
    const html = await request(link);
    const $ = load(html);
    const list = $('.cartoon-block-box .cart-item');
    const books = _.map(list, (item) => {
        const $item = $(item);
        const $cover = $item.find('.cart-cover');
        const $img = $cover.find('img:first');
        const $p = $item.find('.cart-info p:first');
        const $remark = $item.find('.new-chapter');
        return {
            book_id: $cover.attr('href').replace(/.*\/info\/(.*)\//, '$1'),
            book_name: $p.text(),
            book_pic: $img.attr('src'),
            book_remarks: $remark.text(),
        };
    });
    const hasMore = $('.pagelink a.next').length > 0;
    return {
        page: pg,
        pagecount: hasMore ? pg + 1 : pg,
        list: books,
    };
}

async function detail(id) {
    const html = await request(`${HOST}/info/${id}/`);
    const $ = load(html);
    const book = {
        book_name: $('h1.title').text().trim(),
        book_director: $('.mt10:contains(作者)').text().substring(3).trim(),
        book_content: $('.line-clamp-4:contains(简介)').text().substring(3).trim(),
    };
    const list = $('.chapter-list li');
    const urls = _.map(list, (item) => {
        const $item = $(item).find('a');
        const title = $item.text();
        const href = `/info/${id}/${$item.attr('href')}`;
        return title + '$' + href;
    }).join('#');
    book.volumes = '章节';
    book.urls = urls;
    return {
        list: [book],
    };
}

async function play(flag, id, flags) {
    const html = await request(`${HOST}${id}`);
    const $ = load(html);
    const images = $('.chapter-content img');
    const content = _.map(images, (image) => {
        return $(image).attr('data-original');
    });
    return {
        content: content,
    };
}

async function search(wd, quick, pg) {
    if (pg == 0) pg = 1;
    const link = `${HOST}/search/${encodeURIComponent(wd)}/`;
    const html = await request(link);
    const $ = load(html);
    const list = $('.cartoon-block-box .cart-item');
    const books = _.map(list, (item) => {
        const $item = $(item);
        const $cover = $item.find('.cart-cover');
        const $img = $cover.find('img:first');
        const $p = $item.find('.cart-info p:first');
        const $remark = $item.find('.new-chapter');
        return {
            book_id: $cover.attr('href').replace(/.*\/info\/(.*)\//, '$1'),
            book_name: $p.text(),
            book_pic: $img.attr('src'),
            book_remarks: $remark.text(),
        };
    });
    return {
        page: pg,
        pagecount: pg,
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
