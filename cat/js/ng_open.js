import { Crypto, jinja2, _ } from './lib/cat.js';

let key = '南瓜影视';
let HOST = 'http://ys.changmengyun.com';
let siteKey = '';
let siteType = 0;
let MOBILE_UA = 'okhttp/4.6.0'

async function request(reqUrl) {
    let t = new Date().getTime().toString();
    let res = await req(reqUrl, {
        method: 'get',
        headers: {
            'version_name': '1.0.6',
            'version_code': '6',
            'package_name': 'com.app.nanguatv',
            'sign': Crypto.MD5('c431ea542cee9679#uBFszdEM0oL0JRn@' + t).toString().toLowerCase(),
            'imei': 'c431ea542cee9679',
            'timeMillis': t,
            'User-Agent': MOBILE_UA
        },
    });
    return res.content;
}

async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
}

async function home(filter) {
    let data = JSON.parse(await request(HOST + '/api.php/provide/home_nav'));
    let classes = [];
    for (const key in data) {
        if (data[key].name != '精选')
            classes.push({
                type_id: data[key].id,
                type_name: data[key].name,
            });
    }
    let filterObj = {
        "2":[{"key":"class","name":"类型","value":[{"n":"全部","v":"类型"},{"n":"国产剧","v":"国产剧"},{"n":"港台剧","v":"港台剧"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":"地区"},{"n":"内地","v":"内地"},{"n":"香港地区","v":"香港地区"},{"n":"台湾地区","v":"台湾地区"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":"年份"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"10年代","v":"10年代"},{"n":"00年代","v":"00年代"},{"n":"90年代","v":"90年代"},{"n":"80年代","v":"80年代"}]},{"key":"by","name":"排序","value":[{"n":"热播榜","v":"热播榜"},{"n":"好评榜","v":"好评榜"},{"n":"新上线","v":"新上线"}]}],
        "1":[{"key":"class","name":"类型","value":[{"n":"全部","v":"类型"},{"n":"动作片","v":"动作片"},{"n":"喜剧片","v":"喜剧片"},{"n":"爱情片","v":"爱情片"},{"n":"科幻片","v":"科幻片"},{"n":"恐怖片","v":"恐怖片"},{"n":"剧情片","v":"剧情片"},{"n":"战争片","v":"战争片"},{"n":"惊悚片","v":"惊悚片"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":"地区"},{"n":"华语","v":"华语"},{"n":"香港地区","v":"香港地区"},{"n":"美国","v":"美国"},{"n":"欧洲","v":"欧洲"},{"n":"韩国","v":"韩国"},{"n":"日本","v":"日本"},{"n":"台湾地区","v":"台湾地区"},{"n":"泰国","v":"泰国"},{"n":"台湾地区","v":"台湾地区"},{"n":"印度","v":"印度"},{"n":"其它","v":"其它"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":"年份"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"10年代","v":"10年代"},{"n":"00年代","v":"00年代"},{"n":"90年代","v":"90年代"},{"n":"80年代","v":"80年代"}]},{"key":"by","name":"排序","value":[{"n":"热播榜","v":"热播榜"},{"n":"好评榜","v":"好评榜"},{"n":"新上线","v":"新上线"}]}],
        "4":[{"key":"class","name":"类型","value":[{"n":"全部","v":"类型"},{"n":"国产漫","v":"国产漫"},{"n":"欧美漫","v":"欧美漫"},{"n":"日韩漫","v":"日韩漫"},{"n":"港台漫","v":"港台漫"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":"地区"},{"n":"中国大陆","v":"中国大陆"},{"n":"日本","v":"日本"},{"n":"韩国","v":"韩国"},{"n":"欧美","v":"欧美"},{"n":"其它","v":"其它"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":"年份"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"10年代","v":"10年代"},{"n":"00年代","v":"00年代"},{"n":"90年代","v":"90年代"},{"n":"80年代","v":"80年代"}]},{"key":"by","name":"排序","value":[{"n":"热播榜","v":"热播榜"},{"n":"新上线","v":"新上线"}]},{"key":"total","name":"状态","value":[{"n":"全部","v":"状态"},{"n":"连载","v":"连载"},{"n":"完结","v":"完结"}]}],
        "3":[{"key":"class","name":"类型","value":[{"n":"全部","v":"类型"},{"n":"大陆","v":"大陆"},{"n":"港台","v":"港台"},{"n":"日韩","v":"日韩"},{"n":"欧美","v":"欧美"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":"地区"},{"n":"内地","v":"内地"},{"n":"港台","v":"港台"},{"n":"日韩","v":"日韩"},{"n":"欧美","v":"欧美"},{"n":"其它","v":"其它"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":"年份"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"10年代","v":"10年代"},{"n":"00年代","v":"00年代"},{"n":"90年代","v":"90年代"},{"n":"80年代","v":"80年代"}]},{"key":"by","name":"排序","value":[{"n":"热播榜","v":"热播榜"},{"n":"新上线","v":"新上线"}]}],
        "46":[{"key":"class","name":"类型","value":[{"n":"全部","v":"类型"},{"n":"日韩剧","v":"日韩剧"},{"n":"欧美剧","v":"欧美剧"},{"n":"海外剧","v":"海外剧"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":"地区"},{"n":"韩国","v":"韩国"},{"n":"美剧","v":"美剧"},{"n":"日本","v":"日本"},{"n":"泰国","v":"泰国"},{"n":"英国","v":"英国"},{"n":"新加坡","v":"新加坡"},{"n":"其他","v":"其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":"年份"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"10年代","v":"10年代"},{"n":"00年代","v":"00年代"},{"n":"90年代","v":"90年代"},{"n":"80年代","v":"80年代"}]},{"key":"by","name":"排序","value":[{"n":"热播榜","v":"热播榜"},{"n":"好评榜","v":"好评榜"},{"n":"新上线","v":"新上线"}]}]
    };
    return JSON.stringify({
        class: classes,
        filters: filterObj,
    });
}

async function homeVod() {
    let data = JSON.parse(await request(HOST + '/api.php/provide/vod_rank?app=ylys&sort_type=month&imei=c431ea542cee9679&id=2&page=1'));
    let videos = [];
    data.forEach(function(it) {
        videos.push({
            vod_id: it.id,
            vod_name: it.name,
            vod_pic: it.img,
            vod_remarks: it.remarks,
        });
    });
    return JSON.stringify({
        list: videos,
    });
}

async function category(tid, pg, filter, extend) {
    if (pg <= 0 || typeof(pg) == 'undefined') pg = 1;
    let reqUrl = HOST + '/api.php/provide/vod_list?app=ylys&id=' + tid + '&page=' + pg + '&imei=c431ea542cee9679&';
    reqUrl += jinja2('area={{ext.area}}&year={{ext.year}}&type={{ext.class}}&total={{ext.total}}&order={{ext.by}}', { ext: extend });
    // let data = JSON.parse(await request(reqUrl));
    let data = JSON.parse(await request(reqUrl)).list;
    let videos = [];
    data.forEach(function(it) {
        videos.push({
            vod_id: it.id,
            vod_name: it.name,
            vod_pic: it.img,
            vod_remarks: it.remarks,
        });
    });
    let pgChk = JSON.parse(await request(HOST + '/api.php/provide/vod_list?app=ylys&id=' + tid + '&page=' + (parseInt(pg) + 1) + '&imei=c431ea542cee9679&')).msg;
    const pgCount = (pgChk == 'ok') ? parseInt(pg) + 1 : parseInt(pg);
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: 20,
        total: 20 * pgCount,
        list: videos,
    });
}

async function detail(id) {
    let data = JSON.parse(await request(HOST + '/api.php/provide/vod_detail?app=ylys&imei=c431ea542cee9679&id=' + id)).data;
    let vod = {
        vod_id: data.id,
        vod_name: data.name,
        vod_pic: data.img,
        type_name: data.type,
        vod_year: data.year,
        vod_remarks: '更新至: ' + data.msg + ' / 评分: ' + data.score,
        vod_content: stripHtmlTag(data.info),
    };
    let episodes = data.player_info;
    let playlist = {};
    episodes.forEach(function(it) {
        let playurls = it.video_info;
        playurls.forEach(function(playurl) {
            let source = it.show;
            let t = formatPlayUrl(vod.vod_name, playurl.name);
            if (t.length == 0) t = playurl.name.trim();
            if (!playlist.hasOwnProperty(source)) {
                playlist[source] = [];
            }
            playlist[source].push(t + '$' + playurl.url);
        });
    });
    vod.vod_play_from = _.keys(playlist).join('$$$');
    let urls = _.values(playlist);
    let vod_play_url = [];
    urls.forEach(function(it) {
        vod_play_url.push(it.join('#'));
    });
    vod.vod_play_url = vod_play_url.join('$$$');
    return JSON.stringify({
        list: [vod],
    });
}

async function play(flag, id, flags) {
    try {
        if (id.indexOf('m3u8') != -1) {
            let mjurl = id.split('url=')[1]
            return JSON.stringify({
                parse: 0,
                url: mjurl,
            });
        } else if (id.indexOf(',') != -1) {
            let mjurl = id.split(',')[1]
            let jData = JSON.parse(await request(mjurl));
            return JSON.stringify({
                parse: 0,
                url: jData.data.url,
            });
        } else {
            let mjurl = 'http://43.154.104.152:1234/jhapi/cs.php?url=' + id.split('url=')[1]
            let jData = JSON.parse(await request(mjurl));
            return JSON.stringify({
                parse: 0,
                url: jData.data.url,
            });
        }
    } catch (e) {
        return JSON.stringify({
            parse: 0,
            url: id,
        });
    }
}

async function search(wd, quick, pg) {
    if (pg <= 0 || typeof(pg) == 'undefined') pg = 1;
    let data = JSON.parse(await request(HOST + '/api.php/provide/search_result_more?app=ylys&video_name=' + wd + '&pageSize=20&tid=0&imei=c431ea542cee9679&page=' + pg, 'okhttp/4.6.0')).data;
    let videos = [];
    data.forEach(function(it) {
        videos.push({
            vod_id: it.id,
            vod_name: it.video_name,
            vod_pic: it.img,
            vod_remarks: it.qingxidu + '/' + it.category,
        });
    });
    let pgChk = JSON.parse(await request(HOST + '/api.php/provide/search_result_more?app=ylys&video_name=' + wd + '&pageSize=20&tid=0&imei=c431ea542cee9679&page=' + (parseInt(pg) + 1), 'okhttp/4.6.0')).msg;
    const pgCount = (pgChk == 'ok') ? parseInt(pg) + 1 : parseInt(pg);
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: 20,
        total: 20 * pgCount,
        list: videos,
    });
}

function stripHtmlTag(src) {
    return src
        .replace(/<\/?[^>]+(>|$)/g, '')
        .replace(/&.{1,5};/g, '')
        .replace(/\s{2,}/g, ' ');
}

function formatPlayUrl(src, name) {
    return name
        .trim()
        .replaceAll(src, '')
        .replace(/<|>|《|》/g, '')
        .replace(/\$|#/g, ' ')
        .trim();
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
