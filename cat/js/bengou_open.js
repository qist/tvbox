import { Crypto, _, load } from 'assets://js/lib/cat.js';

let key = 'bengou';
let HOST = 'https://www.bengou.co';

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
    const classes = [{'type_id':'all','type_name':'all'}];
    const filterObj = {
        'all':[
            {'key':'type','name':'进度','init':'all','value':[{'n':'全部','v':'all'},{'n':'连载','v':'lianzai'},{'n':'完结','v':'wanjie'}]},
            {'key':'type','name':'地区','init':'all','value':[{'n':'日韩','v':'rihan'},{'n':'内地','v':'neidi'},{'n':'港台','v':'gangntai'},{'n':'欧美','v':'oumei'},{'n':'其他','v':'qita'}]},
            {'key':'type','name':'读者','init':'all','value':[{'n':'少年','v':'shaonianqu'},{'n':'少女','v':'shaonvqu'},{'n':'青年','v':'qingnian'},{'n':'少儿','v':'shaoer'}]},
            {'key':'type','name':'题材','init':'all','value':[{'n':'热血','v':'rexue'},{'n':'格斗','v':'gedou'},{'n':'科幻','v':'kehuan'},{'n':'竞技','v':'jingji'},{'n':'搞笑','v':'gaoxiao'},{'n':'推理','v':'tuili'},{'n':'恐怖','v':'kongbu'},{'n':'耽美','v':'danmei'},{'n':'少女','v':'shaonv'},{'n':'恋爱','v':'lianai'},{'n':'生活','v':'shenghuo'},{'n':'战争','v':'zhanzheng'},{'n':'故事','v':'gushi'},{'n':'冒险','v':'maoxian'},{'n':'魔幻','v':'mohuan'},{'n':'玄幻','v':'xuanhuan'},{'n':'校园','v':'xiaoyuan'},{'n':'悬疑','v':'xuanyi'},{'n':'萌系','v':'mengxi'},{'n':'穿越','v':'chuanyue'},{'n':'后宫','v':'hougong'},{'n':'都市','v':'dushi'},{'n':'武侠','v':'wuxia'},{'n':'历史','v':'lishi'},{'n':'同人','v':'tongren'},{'n':'励志','v':'lizhi'},{'n':'百合','v':'baihe'},{'n':'治愈','v':'zhiyu'},{'n':'机甲','v':'jijia'},{'n':'纯爱','v':'chunai'},{'n':'美食','v':'meishi'},{'n':'血腥','v':'xuexing'},{'n':'僵尸','v':'jiangshi'},{'n':'恶搞','v':'egao'},{'n':'虐心','v':'nuexin'},{'n':'动作','v':'dongzuo'},{'n':'惊险','v':'jingxian'},{'n':'唯美','v':'weimei'},{'n':'震撼','v':'zhenhan'},{'n':'复仇','v':'fuchou'},{'n':'侦探','v':'zhentan'},{'n':'脑洞','v':'naodong'},{'n':'奇幻','v':'qihuan'},{'n':'宫斗','v':'gongdou'},{'n':'爆笑','v':'baoxiao'},{'n':'运动','v':'yundong'},{'n':'青春','v':'qingchun'},{'n':'灵异','v':'lingyi'},{'n':'古风','v':'gufeng'},{'n':'权谋','v':'quanmou'},{'n':'节操','v':'jiecao'},{'n':'明星','v':'mingxing'},{'n':'暗黑','v':'anhei'},{'n':'社会','v':'shehui'},{'n':'浪漫','v':'langman'},{'n':'栏目','v':'lanmu'},{'n':'仙侠','v':'xianxia'}]},
            {'key':'type','name':'字母','init':'all','value':[{'n':'A','v':'lettera'},{'n':'B','v':'letterb'},{'n':'C','v':'letterc'},{'n':'D','v':'letterd'},{'n':'E','v':'lettere'},{'n':'F','v':'letterf'},{'n':'G','v':'letterg'},{'n':'H','v':'letterh'},{'n':'I','v':'letteri'},{'n':'J','v':'letterj'},{'n':'K','v':'letterk'},{'n':'L','v':'letterl'},{'n':'M','v':'letterm'},{'n':'N','v':'lettern'},{'n':'O','v':'lettero'},{'n':'P','v':'letterp'},{'n':'Q','v':'letterq'},{'n':'R','v':'letterr'},{'n':'S','v':'letters'},{'n':'T','v':'lettert'},{'n':'U','v':'letteru'},{'n':'V','v':'letterv'},{'n':'W','v':'letterw'},{'n':'X','v':'letterx'},{'n':'Y','v':'lettery'},{'n':'Z','v':'letterz'}]},
        ],
    };
    return JSON.stringify({
        class: classes,
        filters: filterObj,
    });
}

async function category(tid, pg, filter, extend) {
    if (pg == 0) pg = 1;
    let page = '';
    if (pg > 1) {
        page = `${pg}.html`;
    }
    const link = HOST + `/${extend.type || 'all'}/${page}`;
    const html = await request(link);
    const $ = load(html);
    const list = $('.dmList li');
    const books = _.map(list, (item) => {
        const $item = $(item);
        const $a = $item.find('dt a:first');
        const $img = $item.find('img:first');
        const $span = $item.find('span:first');
        return {
            book_id: $a.attr('href'),
            book_name: $a.text(),
            book_pic: $img.attr('src'),
            book_remarks: $span.text(),
        };
    });
    const hasMore = $('.NewPages a:contains(下一页)').length > 0;
    return {
        page: pg,
        pagecount: hasMore ? pg + 1 : pg,
        list: books,
    };
}

async function detail(id) {
    const html = await request(HOST + id);
    const $ = load(html);
    const book = {
        book_name: $('.title h1').text(),
        book_director: $('.info p:contains(原著作者) a').text().trim(),
        book_content: $('.introduction').text().trim(),
        book_remarks: $('.title a:first').text(),
    };
    const list = $('.plist a');
    const urls = _.map(list, (item) => {
        const $item = $(item);
        let title = $item.text().trim();
        if (_.isEmpty(title)) {
            title = '观看'
        }
        const href = $item.attr('href');
        return title + '$' + href;
    }).join('#');
    book.volumes = '笨狗';
    book.urls = urls;

    return {
        list: [book],
    };
}

async function play(flag, id, flags) {
    try {
        const html = await request(HOST + id);
        const matches = html.match(/var qTcms_S_m_murl_e=\"(.*)\";/);
        const decoded = base64Decode(matches[1]);
        const picList = decoded.split('$');
        const content = [];
        for (let i = 0; i < picList.length; i += 2) {
            content.push(picList[i]);
        }
        return {
            content: content,
        };
    } catch (e) {
        console.debug('error: ' + e);
        return {
            content: '',
        };
    }
}

function base64Decode(text) {
    return Crypto.enc.Utf8.stringify(Crypto.enc.Base64.parse(text));
}

async function search(wd, quick, pg) {
    if (pg == 0) pg = 1;
    let page = '';
    if (pg > 1) {
        page = `&page=${pg}`;
    }
    const link = HOST + `/statics/search.aspx?key=${encodeURIComponent(wd)}${page}`;
    const html = await request(link);
    const $ = load(html);
    const list = $('.dmList li');
    const books = _.map(list, (item) => {
        const $item = $(item);
        const $a = $item.find('dt a:first');
        const $img = $item.find('img:first');
        const $span = $item.find('span:first');
        return {
            book_id: $a.attr('href'),
            book_name: $a.text(),
            book_pic: $img.attr('src'),
            book_remarks: $span.text(),
        };
    });
    const hasMore = $('.NewPages a:contains(下一页)').length > 0;
    return {
        page: pg,
        pagecount: hasMore ? pg + 1 : pg,
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
