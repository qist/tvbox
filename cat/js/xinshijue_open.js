import { Crypto, load, _ } from 'assets://js/lib/cat.js';

let key = 'xinshijue';
let HOST = 'https://www.hdmyy.com';
let siteKey = '';
let siteType = 0;

const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1';

async function request(reqUrl, timeout = 20000) {
    let res = await req(reqUrl, {
        method: 'get',
        headers: {
            'User-Agent': UA,
            'Referer': HOST
        },
        timeout: timeout,
    });
    return res.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
}

async function home(filter) {
    let classes = [{'type_id':1,'type_name':'电影'},{'type_id':2,'type_name':'电视剧'},{'type_id':3,'type_name':'综艺'},{'type_id':4,'type_name':'动漫'},{'type_id':63,'type_name':'纪录片'}];
    let filterObj = {
        '1':[{'key':'class','name':'剧情','init':'','value':[{'n':'全部','v':''},{'n':'喜剧','v':'喜剧'},{'n':'爱情','v':'爱情'},{'n':'恐怖','v':'恐怖'},{'n':'动作','v':'动作'},{'n':'科幻','v':'科幻'},{'n':'剧情','v':'剧情'},{'n':'战争','v':'战争'},{'n':'警匪','v':'警匪'},{'n':'犯罪','v':'犯罪'},{'n':'动画','v':'动画'},{'n':'奇幻','v':'奇幻'},{'n':'武侠','v':'武侠'},{'n':'冒险','v':'冒险'},{'n':'枪战','v':'枪战'},{'n':'恐怖','v':'恐怖'},{'n':'悬疑','v':'悬疑'},{'n':'惊悚','v':'惊悚'},{'n':'经典','v':'经典'},{'n':'青春','v':'青春'},{'n':'文艺','v':'文艺'},{'n':'微电影','v':'微电影'},{'n':'古装','v':'古装'},{'n':'历史','v':'历史'},{'n':'运动','v':'运动'},{'n':'农村','v':'农村'},{'n':'儿童','v':'儿童'},{'n':'网络电影','v':'网络电影'}]},{'key':'area','name':'地区','init':'','value':[{'n':'全部','v':''},{'n':'中国大陆','v':'中国大陆'},{'n':'中国香港','v':'中国香港'},{'n':'中国台湾','v':'中国台湾'},{'n':'美国','v':'美国'},{'n':'法国','v':'法国'},{'n':'英国','v':'英国'},{'n':'日本','v':'日本'},{'n':'韩国','v':'韩国'},{'n':'德国','v':'德国'},{'n':'泰国','v':'泰国'},{'n':'印度','v':'印度'},{'n':'意大利','v':'意大利'},{'n':'西班牙','v':'西班牙'},{'n':'加拿大','v':'加拿大'},{'n':'其他','v':'其他'}]},{'key':'year','name':'年份','init':'','value':[{'n':'全部','v':''},{'n':'2023','v':'2023'},{'n':'2022','v':'2022'},{'n':'2021','v':'2021'},{'n':'2020','v':'2020'},{'n':'2019','v':'2019'},{'n':'2018','v':'2018'},{'n':'2017','v':'2017'},{'n':'2016','v':'2016'},{'n':'2015','v':'2015'},{'n':'2014','v':'2014'},{'n':'2013','v':'2013'},{'n':'2012','v':'2012'},{'n':'2011','v':'2011'},{'n':'2010','v':'2010'}]},{'key':'by','name':'排序','value':[{'n':'时间','v':'time'},{'n':'人气','v':'hits'},{'n':'评分','v':'score'}]}],
        '2':[{'key':'class','name':'剧情','init':'','value':[{'n':'全部','v':''},{'n':'爱情','v':'爱情'},{'n':'古装','v':'古装'},{'n':'悬疑','v':'悬疑'},{'n':'都市','v':'都市'},{'n':'喜剧','v':'喜剧'},{'n':'战争','v':'战争'},{'n':'剧情','v':'剧情'},{'n':'青春','v':'青春'},{'n':'历史','v':'历史'},{'n':'网剧','v':'网剧'},{'n':'奇幻','v':'奇幻'},{'n':'冒险','v':'冒险'},{'n':'励志','v':'励志'},{'n':'犯罪','v':'犯罪'},{'n':'商战','v':'商战'},{'n':'恐怖','v':'恐怖'},{'n':'穿越','v':'穿越'},{'n':'农村','v':'农村'},{'n':'人物','v':'人物'},{'n':'商业','v':'商业'},{'n':'生活','v':'生活'},{'n':'短剧','v':'短剧'},{'n':'其他','v':'其他'}]},{'key':'area','name':'地区','init':'','value':[{'n':'全部','v':''},{'n':'中国大陆','v':'中国大陆'},{'n':'中国香港','v':'中国香港'},{'n':'中国台湾','v':'中国台湾'},{'n':'韩国','v':'韩国'},{'n':'香港','v':'香港'},{'n':'台湾','v':'台湾'},{'n':'日本','v':'日本'},{'n':'美国','v':'美国'},{'n':'泰国','v':'泰国'},{'n':'英国','v':'英国'},{'n':'新加坡','v':'新加坡'},{'n':'其他','v':'其他'}]},{'key':'year','name':'年份','init':'','value':[{'n':'全部','v':''},{'n':'2023','v':'2023'},{'n':'2022','v':'2022'},{'n':'2021','v':'2021'},{'n':'2020','v':'2020'},{'n':'2019','v':'2019'},{'n':'2018','v':'2018'},{'n':'2017','v':'2017'},{'n':'2016','v':'2016'},{'n':'2015','v':'2015'},{'n':'2014','v':'2014'},{'n':'2013','v':'2013'},{'n':'2012','v':'2012'},{'n':'2011','v':'2011'},{'n':'2010','v':'2010'}]},{'key':'by','name':'排序','value':[{'n':'时间','v':'time'},{'n':'人气','v':'hits'},{'n':'评分','v':'score'}]}],
        '3':[{'key':'class','name':'剧情','init':'','value':[{'n':'全部','v':''},{'n':'音乐','v':'音乐'},{'n':'情感','v':'情感'},{'n':'生活','v':'生活'},{'n':'职场','v':'职场'},{'n':'真人秀','v':'真人秀'},{'n':'搞笑','v':'搞笑'},{'n':'公益','v':'公益'},{'n':'艺术','v':'艺术'},{'n':'访谈','v':'访谈'},{'n':'益智','v':'益智'},{'n':'体育','v':'体育'},{'n':'少儿','v':'少儿'},{'n':'时尚','v':'时尚'},{'n':'人物','v':'人物'},{'n':'其他','v':'其他'}]},{'key':'area','name':'地区','init':'','value':[{'n':'全部','v':''},{'n':'中国大陆','v':'中国大陆'},{'n':'港台','v':'港台'},{'n':'韩国','v':'韩国'},{'n':'欧美','v':'欧美'},{'n':'其他','v':'其他'}]},{'key':'year','name':'年份','init':'','value':[{'n':'全部','v':''},{'n':'2023','v':'2023'},{'n':'2022','v':'2022'},{'n':'2021','v':'2021'},{'n':'2020','v':'2020'},{'n':'2019','v':'2019'},{'n':'2018','v':'2018'},{'n':'2017','v':'2017'},{'n':'2016','v':'2016'},{'n':'2015','v':'2015'},{'n':'2014','v':'2014'},{'n':'2013','v':'2013'},{'n':'2012','v':'2012'},{'n':'2011','v':'2011'},{'n':'2010','v':'2010'}]},{'key':'by','name':'排序','value':[{'n':'时间','v':'time'},{'n':'人气','v':'hits'},{'n':'评分','v':'score'}]}],
        '4':[{'key':'class','name':'剧情','init':'','value':[{'n':'全部','v':''},{'n':'冒险','v':'冒险'},{'n':'战斗','v':'战斗'},{'n':'搞笑','v':'搞笑'},{'n':'经典','v':'经典'},{'n':'科幻','v':'科幻'},{'n':'玄幻','v':'玄幻'},{'n':'魔幻','v':'魔幻'},{'n':'武侠','v':'武侠'},{'n':'恋爱','v':'恋爱'},{'n':'推理','v':'推理'},{'n':'日常','v':'日常'},{'n':'校园','v':'校园'},{'n':'悬疑','v':'悬疑'},{'n':'真人','v':'真人'},{'n':'历史','v':'历史'},{'n':'竞技','v':'竞技'},{'n':'其他','v':'其他'}]},{'key':'area','name':'地区','init':'','value':[{'n':'全部','v':''},{'n':'中国大陆','v':'中国大陆'},{'n':'日本','v':'日本'},{'n':'韩国','v':'韩国'},{'n':'欧美','v':'欧美'},{'n':'其他','v':'其他'}]},{'key':'year','name':'年份','init':'','value':[{'n':'全部','v':''},{'n':'2023','v':'2023'},{'n':'2022','v':'2022'},{'n':'2021','v':'2021'},{'n':'2020','v':'2020'},{'n':'2019','v':'2019'},{'n':'2018','v':'2018'},{'n':'2017','v':'2017'},{'n':'2016','v':'2016'},{'n':'2015','v':'2015'},{'n':'2014','v':'2014'},{'n':'2013','v':'2013'},{'n':'2012','v':'2012'},{'n':'2011','v':'2011'},{'n':'2010','v':'2010'}]},{'key':'by','name':'排序','value':[{'n':'时间','v':'time'},{'n':'人气','v':'hits'},{'n':'评分','v':'score'}]}],
        '63':[{'key':'by','name':'排序','value':[{'n':'时间','v':'time'},{'n':'人气','v':'hits'},{'n':'评分','v':'score'}]}],
    };

    return JSON.stringify({
        class: classes,
        filters: filterObj,
    });
}

async function homeVod() {}

async function category(tid, pg, filter, extend) {
    if (pg <= 0) pg = 1;
    let page = '';
    if (pg > 1) {
        page = pg;
    }
    const link = HOST + '/vodshow/' + tid + '-' + (extend.area || '') + '-' + (extend.by || '') + '-' + (extend.class || '') + '-' + (extend.lang || '') + '-' + (extend.letter || '') + '---' + page + '---' + (extend.year || '') + '.html';
    const html = await request(link);
    const $ = load(html);
    const items = $('.module-list .module-item');
    const videos = _.map(items, (item) => {
        const $item = $(item);
        const link = $item.find('.module-item-content a:first').attr('href');
        const title = $item.find('.video-name').text().trim();
        const img = $item.find('.module-item-pic img:first').attr('data-src');
        const remarks = $item.find('.module-item-text').text().trim();
        return {
            vod_id: link.replace(/.*?\/video\/(.*).html/g, '$1'),
            vod_name: title,
            vod_pic: img,
            vod_remarks: remarks || '',
        };
    });
    const hasMore = $('#page a.page-next:contains(下一页)').length > 0;
    const pgCount = hasMore ? parseInt(pg) + 1 : parseInt(pg);
    const limit = 40;
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: limit,
        total: limit * pgCount,
        list: videos,
    });
}

async function detail(id) {
    const html = await request(HOST + '/video/' + id + '.html');
    const $ = load(html);
    const vod = {
        vod_id: id,
        vod_name: $('h1.page-title').text().trim(),
        vod_type: $('.video-info-aux a.tag-link:first').text().trim(),
        vod_area: $('.video-info-aux a.tag-link:eq(2)').text().trim(),
        vod_year: $('.video-info-aux a.tag-link:eq(1)').text().trim(),
        vod_director: $('.video-info-main .video-info-items:contains(导演：)').text().substring(3).trim().replace(/(^\/|\/$)/g, '').trim(),
        vod_actor: $('.video-info-main .video-info-items:contains(主演：)').text().substring(3).trim().replace(/(^\/|\/$)/g, '').trim(),
        vod_pic: $('.video-cover img:first').attr('data-src'),
        vod_remarks : $('.video-info-main .video-info-items:contains(备注：)').text().substring(3) || '',
        vod_content: $('.video-info-main .video-info-items:contains(剧情：)').text().substring(3).trim().replace(/收起$/g, ''),
    };
    const playMap = {};
    const tabs = $('.module-player-tab .module-tab-item');
    const playlists = $('.module-player-list > .module-blocklist');
    _.each(tabs, (tab, i) => {
        const $tab = $(tab);
        const from = $tab.find('span:first').text().trim();
        if (from.includes('夸克')) return;
        let list = playlists[i];
        list = $(list).find('a');
        _.each(list, (it) => {
            const $it = $(it);
            const title = $it.find('span:first').text().trim();
            const playUrl = $it.attr('href');
            if (!playMap.hasOwnProperty(from)) {
                playMap[from] = [];
            }
            playMap[from].push(title + '$' + playUrl);
        });
    });
    vod.vod_play_from = _.keys(playMap).join('$$$');
    const urls = _.values(playMap);
    const vod_play_url = _.map(urls, (urlist) => {
        return urlist.join('#');
    });
    vod.vod_play_url = vod_play_url.join('$$$');
    return JSON.stringify({
        list: [vod],
    });
}

async function play(flag, id, flags) {
    const link = HOST + id;
    const html = await request(link);
    let $ = load(html);
    let json = $('script:contains(player_aaaa)').text().replace('var player_aaaa=','');
    let js = JSON.parse(json);
    let playUrl = js.url;
    if (js.encrypt == 1) {
        playUrl = unescape(playUrl);
    } else if (js.encrypt == 2) {
        playUrl = unescape(base64Decode(playUrl));
    }
    let playHtml = await request('https://jx3.xn--1lq90i13mxk5bolhm8k.xn--fiqs8s/player/ec.php?code=ak&if=1&url=' + playUrl);
    json = playHtml.match(/let ConFig = {([\w\W]*)},box/)[1];
    const jsConfig = JSON.parse('{' + json.trim() + '}');
    playUrl = decryptUrl(jsConfig);
    return JSON.stringify({
        parse: 0,
        url: playUrl,
        header: {
            'User-Agent': UA,
        }
    });
}

function decryptUrl(jsConfig) {
    const key = Crypto.enc.Utf8.parse('2890' + jsConfig.config.uid + 'tB959C');
    const iv = Crypto.enc.Utf8.parse('2F131BE91247866E');
    const mode = Crypto.mode.CBC;
    const padding = Crypto.pad.Pkcs7;
    const decrypted = Crypto.AES.decrypt(jsConfig.url, key, {
        'iv': iv,
        'mode': mode,
        'padding': padding
    });
    const decryptedUrl = Crypto.enc.Utf8.stringify(decrypted);
    return decryptedUrl;
}

function base64Decode(text) {
    return Crypto.enc.Utf8.stringify(Crypto.enc.Base64.parse(text));
}

async function search(wd, quick, pg) {
    let data = JSON.parse(await request(HOST + '/index.php/ajax/suggest?mid=1&limit=50&wd=' + wd)).list;
    let videos = [];
    for (const vod of data) {
        videos.push({
            vod_id: vod.id,
            vod_name: vod.name,
            vod_pic: vod.pic,
            vod_remarks: '',
        });
    }
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