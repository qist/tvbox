import { Crypto, load, _ } from 'assets://js/lib/cat.js';
/**
 * 直播源
 * author：Leospring
 */

let siteUrl = 'http://api.maiyoux.com:81/mf/';
let siteKey = '';
let siteType = 0;
let cateList = {};
async function request(reqUrl, postData, post) {

    let res = await req(reqUrl, {
        method: post ? 'post' : 'get',
        data: postData || {},
        postType: post ? 'form' : '',
    });
    let content = res.content;
    return content;
}

async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
    if (cfg.ext) {
        siteUrl = cfg.ext;
    }
    cateList = JSON.parse(await request(siteUrl + 'json.txt'));
}

async function home(filter) {
    let classes = [];
    Object.keys(cateList).forEach(function(key) {
        classes.push({
            type_id: key,
            type_name: key,
        });
    });
    return JSON.stringify({
        class: classes,
       // filters: filterObj
    });
}

async function category(tid, pg, filter, ext) {
    let videos = _.map(cateList[tid], (item) => {
        return {
            vod_id: item['address'],
            vod_name: item['title'],
            vod_pic: item['xinimg'],
            vod_remarks: item['Number']
        }
    })
    return JSON.stringify({
        list: videos,
        page: pg,
        pagecount: 1,
        total: videos.length
    });
}

async function detail(id) {
    try {
        const res = JSON.parse(await request(siteUrl + id))['zhubo'];
        let playUrls = _.map(res, (vod) => {
            return vod.title + '$' + vod.address;
        }).join('#');
        const video = {
            vod_play_from: 'Leospring',
            vod_play_url: playUrls,
            vod_content: '作者：Leospring 公众号：蚂蚁科技杂谈',
        };
        const list = [video];
        const result = { list };
        return JSON.stringify(result);
    } catch (e) {
    console.log('err', e);
    }
    return null;
}

async function play(flag, id, flags) {
    let playUrl = id;
    return JSON.stringify({
        parse: 0,
        url: playUrl,
    });
}

export function __jsEvalReturn() {
    return {
        init: init,
        home: home,
        category: category,
        detail: detail,
        play: play,
    };
}