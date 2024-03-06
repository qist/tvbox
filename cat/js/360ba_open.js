import { Crypto, load, _ } from './lib/cat.js';

let siteUrl = 'https://m.360ba.co/';
let siteKey = '';
let siteType = 0;
let headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Redmi K30 Build/SKQ1.210908.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/96.0.4664.104 Mobile Safari/537.36',
    'Referer': siteUrl,
    'Origin': siteUrl,
};

async function request(reqUrl, postData, post) {

    let res = await req(reqUrl, {
        method: post ? 'post' : 'get',
        headers: headers,
        data: postData || {},
        postType: post ? 'form' : '',
    });

    let content = res.content;
    return content;
}

async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
}

async function home(filter) {
    let classes = [{
        type_id: '1',
        type_name: '全部',
    },{
        type_id: '2',
        type_name: '足球',
    },{
        type_id: '3',
        type_name: '篮球',
    },{
        type_id: '99',
        type_name: '综合',
    }];
    //let filterObj = genFilterObj();
    return JSON.stringify({
        class: classes,
       // filters: filterObj
    });
}

async function category(tid, pg, filter, extend) {
    let url = siteUrl + 'api/web/live_lists/' + tid;
    let videos = await getVideos(url);
    return JSON.stringify({
        list: videos,
        page: 1,
        pagecount: 1,
        limit: 0,
        total: videos.length
    });
}

async function detail(id) {
    try {
        const video = {
            vod_play_from: 'Leospring',
            vod_play_url: '播放' + '$' + id,
            vod_content: '该资源由LeoSpring采集分享，公众号【蚂蚁科技杂谈】',
        };
        const list = [video];
        const result = { list };
        return JSON.stringify(result);
    } catch (e) {
       //console.log('err', e);
    }
    return null;
}

async function search(wd, quick, pg) {
    let url = siteUrl + 'api/web/search?keyword=' + wd;
    const data = JSON.parse(await request(url))['data']['ball'];
    
    let videos = _.map(data, (n) => {
        let id = n['url'];
        let name = n['league_name_zh'] + ' ' + n['home_team_zh'] + ' VS ' + n['away_team_zh'];
        let pic = n['cover'];
        let remarks = 'LIVING';
        return {
            vod_id: id,
            vod_name: name,
            vod_pic: pic,
            vod_remarks: remarks,
        };
    });
    return JSON.stringify({
        list: videos,
    });
}

async function play(flag, id, flags) {
    return JSON.stringify({
        parse: 0,
        url: id,
        header: headers
    });
}

async function getVideos(url) {
    const data = JSON.parse(await request(url))['data']['data'];
    
    let videos = _.map(data, (n) => {
        let id = n['url'];
        let name = n['league_name_zh'] + ' ' + n['home_team_zh'] + ' VS ' + n['away_team_zh'];
        let pic = n['cover'];
        let remarks = 'LIVING';
        return {
            vod_id: id,
            vod_name: name,
            vod_pic: pic,
            vod_remarks: remarks,
        };
    });
    return videos;
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