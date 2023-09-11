// 无搜索功能
import { _ } from './lib/cat.js';
let key = '🐯贝乐虎';
let HOST = 'https://vd.ubestkid.com';
let siteKey = '';
let siteType = 0;
const MOBILE_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1';

async function request(reqUrl, referer, mth, data, hd) {
    const headers = {
        "User-Agent": MOBILE_UA,
    };
    if (referer) headers.referer = encodeURIComponent(referer);
    let res = await req(reqUrl, {
        method: mth || "get",
        headers: headers,
        data: data,
        postType: mth === "post" ? "json" : "",
    });
    return res.content;
}

async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype
}

async function home(filter) {
    const classes = [{ type_id: 65, type_name: '🐯最新上架' }, { type_id: 113, type_name: '🐯人气热播' }, { type_id: 56, type_name: '🐯经典童谣' }, { type_id: 137, type_name: '🐯开心贝乐虎' }, { type_id: 53, type_name: '🐯律动儿歌' }, { type_id: 59, type_name: '🐯经典儿歌' }, { type_id: 101, type_name: '🐯超级汽车1' }, { type_id: 119, type_name: '🐯超级汽车第二季' }, { type_id: 136, type_name: '🐯超级汽车第三季' }, { type_id: 95, type_name: '🐯三字经' }, { type_id: 133, type_name: '🐯幼儿手势舞' }, { type_id: 117, type_name: '🐯哄睡儿歌' }, { type_id: 70, type_name: '🐯英文儿歌' }, { type_id: 116, type_name: '🐯节日与节气' }, { type_id: 97, type_name: '🐯恐龙世界' }, { type_id: 55, type_name: '🐯动画片儿歌' }, { type_id: 57, type_name: '🐯流行歌曲' }, { type_id: 118, type_name: '🐯贝乐虎入园记' }, { type_id: 106, type_name: '🐯贝乐虎大百科' }, { type_id: 62, type_name: '🐯经典古诗' }, { type_id: 63, type_name: '🐯经典故事' }, { type_id: 128, type_name: '🐯萌虎学功夫' }, { type_id: 100, type_name: '🐯绘本故事' }, { type_id: 121, type_name: '🐯开心贝乐虎英文版' }, { type_id: 96, type_name: '🐯嗨贝乐虎情商动画' }, { type_id: 108, type_name: '🐯动物音乐派对' }, { type_id: 126, type_name: '🐯动物音乐派对英文版' }, { type_id: 105, type_name: '🐯奇妙的身体' }, { type_id: 124, type_name: '🐯奇妙的身体英文版' }, { type_id: 64, type_name: '🐯认知卡片' }, { type_id: 109, type_name: '🐯趣味简笔画' }, { type_id: 78, type_name: '🐯数字儿歌' }, { type_id: 120, type_name: '🐯识字体验版' }, { type_id: 127, type_name: '🐯启蒙系列体验版' }];
    const filterObj = {};
    return JSON.stringify({
        class: _.map(classes, (cls) => {
            cls.land = 1;
            cls.ratio = 1.78;
            return cls;
        }),
        filters: filterObj,
    })
}

async function homeVod() {
    const link = HOST + "/api/v1/bv/video";
    const pdata = { age: 1, appver: "6.1.9", egvip_status: 0, svip_status: 0, vps: 60, subcateId: 56, "p": 1 };
    const jo = JSON.parse(await request(link, "", "post", pdata)).result;
    const videos = [];
    _.each(jo.items, (it) => {
        videos.push({
            vod_id: it.url,
            vod_name: it.title,
            vod_pic: it.image,
            vod_remarks: '👀' + it.viewcount || '',
        })
    });
    return JSON.stringify({
        list: videos,
    })
}

async function category(tid, pg, filter, extend) {
    if (pg <= 0 || typeof pg == 'undefined') pg = 1;
    const link = HOST + "/api/v1/bv/video";
    const pdata = { age: 1, appver: "6.1.9", egvip_status: 0, svip_status: 0, vps: 60, subcateId: tid, "p": pg };
    const jo = JSON.parse(await request(link, "", "post", pdata)).result;
    const videos = [];
    _.each(jo.items, (it) => {
        videos.push({
            vod_id: it.url,
            vod_name: it.title,
            vod_pic: it.image,
            vod_remarks: '👀' + it.viewcount || '',
        })
    });
    const pgCount = pg * 60 > jo.total ? parseInt(pg) : parseInt(pg) + 1;
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: 60,
        total: jo.total,
        list: videos,
    })
}

async function detail(id) {
    const vod = {
        vod_id: id,
        vod_remarks: '',
    };
    const playlist = ['点击播放' + '$' + id];
    vod.vod_play_from = "道长在线";
    vod.vod_play_url = playlist.join('#');
    return JSON.stringify({
        list: [vod],
    });
}

async function play(flag, id, flags) {
    // console.debug('贝乐虎 id =====>' + id); // js_debug.log
    return JSON.stringify({
        parse: 0,
        url: id,
    });
}

async function search(wd, quick) {
    return '{}'
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
    }
}