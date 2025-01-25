import { load, _ } from 'assets://js/lib/cat.js';
import { log } from './lib/utils.js';
import { initAli, detailContent, playContent } from './lib/ali.js';

let siteKey = 'xiaozhitiao';
let siteType = 0;
let siteUrl = 'https://gitcafe.net/tool/alipaper/';
let aliUrl = "https://www.aliyundrive.com/s/";
let token = '';
let date = new Date();

const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1';

async function request(reqUrl, data) {
    let res = await req(reqUrl, {
        method: 'post',
        headers: {
            'User-Agent': UA,
        },
        data: data,
        postType: 'form',
    });
    return res.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    try {
        siteKey = _.isEmpty(cfg.skey) ? '' : cfg.skey;
        siteType = _.isEmpty(cfg.stype) ? '' : cfg.stype;
        await initAli(cfg.ext);
    } catch (e) {
        await log('init:' + e.message + ' line:' + e.lineNumber);
    }
}

async function home(filter) {
    const classes = [{'type_id':'1','type_name':'电视'},{'type_id':'2','type_name':'电影'},{'type_id':'3','type_name':'动漫'},{'type_id':'4','type_name':'视频'},{'type_id':'5','type_name':'音乐'}];
    const filterObj = {
        '1':[{'key':'class','name':'类型','init':'hyds','value':[{'n':'华语','v':'hyds'},{'n':'日韩','v':'rhds'},{'n':'欧美','v':'omds'},{'n':'其他','v':'qtds'}]}],
        '2':[{'key':'class','name':'类型','init':'hydy','value':[{'n':'华语','v':'hydy'},{'n':'日韩','v':'rhdy'},{'n':'欧美','v':'omdy'},{'n':'其他','v':'qtdy'}]}],
        '3':[{'key':'class','name':'类型','init':'hydm','value':[{'n':'国漫','v':'hydm'},{'n':'🇯🇵日本','v':'rhdm'},{'n':'欧美','v':'omdm'}]}],
        '4':[{'key':'class','name':'类型','init':'jlp','value':[{'n':'纪录','v':'jlp'},{'n':'综艺','v':'zyp'},{'n':'教育','v':'jypx'},{'n':'其他','v':'qtsp'}]}],
        '5':[{'key':'class','name':'类型','init':'hyyy','value':[{'n':'华语','v':'hyyy'},{'n':'日韩','v':'rhyy'},{'n':'欧美','v':'omyy'},{'n':'其他','v':'qtyy'}]}],
   };
    return {
        class: classes,
        filters: filterObj,
    };
}

async function homeVod() {}

async function category(tid, pg, filter, extend) {
    if (pg <= 0) pg = 1;
    const params = {
        action: "viewcat",
        cat: extend.class,
        num: pg,
        token: await getToken(),
    };
    const resp = await request(siteUrl, params);
    const json = JSON.parse(resp);
    const videos = _.map(json.data, (item) => {
        return {
            vod_id: aliUrl + item.alikey,
            vod_name: item.title,
            vod_pic: "https://i2.100024.xyz/2024/01/31/xp4o7o.webp",
            vod_remarks: item.creatime
        };
    });
    const pgCount = _.isEmpty(videos) ? pg : pg + 1;
    const limit = 50;
    return {
        page: pg,
        pagecount: pgCount,
        limit: limit,
        total: limit * pgCount,
        list: videos,
    };
}

async function detail(id) {
    try {
        return await detailContent(id);
    } catch (e) {
        await log('detail:' + e.message + ' line:' + e.lineNumber);
    }
}

async function play(flag, id, flags) {
    try {
        return await playContent(flag, id, flags);
    } catch (e) {
        await log('play:' + e.message + ' line:' + e.lineNumber);
    }
}

async function search(wd, quick, pg) {
    if (pg <= 0) pg = 1;
    const params = {
        action: "search",
        from: "web",
        keyword: wd,
        token: await getToken(),
    };
    const resp = await request(siteUrl, params);
    const json = JSON.parse(resp);
    const videos = _.map(json.data, (item) => {
        return {
            vod_id: aliUrl + item.alikey,
            vod_name: item.title,
            vod_pic: "https://i2.100024.xyz/2024/01/31/xp4o7o.webp",
            vod_remarks: item.creatime
        };
    });
    return {
        list: videos,
    };
}

async function getToken() {
    const newDate = new Date();
    if (_.isEmpty(token) || newDate > date) {
        const params = {
            action: "get_token",
        };
        const resp = await request(siteUrl, params);
        const json = JSON.parse(resp);
        if (json.success) {
            token = json.data;
            date = newDate;
        }
    }
    return token;
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