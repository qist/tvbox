import { Crypto, load, _ } from './lib/cat.js';

let siteUrl = 'https://4kysxz.top';
let siteKey = '';
let siteType = 0;
let headers = {};

async function request(reqUrl, postData, agentSp, get) {

    let res = await req(reqUrl, {
        method: get ? 'get' : 'post',
        headers: headers,
        data: postData || {},
        postType: get ? '' : 'form',
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
        type_id: '16',
        type_name: '高清电影',
    },{
        type_id: '17',
        type_name: '高清剧集',
    }];

    //let filterObj = genFilterObj();
    return JSON.stringify({
        class: classes,
        //filters: filterObj
    });
}

async function homeVod() {
    let videos = await getVideos(siteUrl);
    return JSON.stringify({
        list: videos,
    });
}

async function category(tid, pg, filter, extend) {
    if (!pg) pg = 1;
    if (pg <= 0) pg = 1;
    let url = siteUrl + '/category-' + tid + '_' + pg + '.html';
    let videos = await getVideos(url);
    return JSON.stringify({
        list: videos,
        page: pg,
    });
}

async function detail(id) {
    try {
        const html = await request(id);
        const $ = load(html);
        

        let actors = _.map($('div.entry-content.u-text-format.u-clearfix > div:nth-child(10) > div > span > span'), (n) => {
            return $(n).text().split(' ')[0];
        });
        let actor = actors.join(' ');

        let directors = _.map($('div.entry-content.u-text-format.u-clearfix > div:nth-child(8) > div > span'), (n) => {
            return $(n).text().split(' ')[0];
        });
        let director = directors.join(' ');

        let title = $('div.site-content > section > div > header > h1').text().trim();

        let content = '该影视由【Leospring】采集分享';
        let playUrlStr = '';
        let playFromStr = '';
        //高清直播
        const cards = $('div.entry-content.u-text-format.u-clearfix > custag > ul > li > a');
        if (cards.length > 0) {
            let playUrls = _.map(cards, (n) => {
                let playUrl = n.attribs['href'];
                if (playUrl.indexOf('url=') > 0) {
                    playUrl = playUrl.split('url=')[1].split('&name')[0];
                }
                return $(n).text() + '$' + playUrl;
            });
            playUrlStr = playUrls.join('#');
            playFromStr = '高清直播';
        }

        //磁力链接
        const tbs = $('loginshow > table');
        let playFrom = '';
        let nameUrls = [];
        for(let i = 0;i< tbs.length;i++) {
            if (i%2 == 0) {
                playFrom = $(tbs[i]).find('tbody > tr >td').text().replaceAll('WEB', '磁力');
            } else if (i%2 == 1) {
                const tds = $(tbs[i]).find('tbody > tr >td');
                let nameUrl = '';
                for (let j = 0;j < tds.length;j++) {
                    if (j%2 == 0) {
                        nameUrl = $(tds[j]).text().split('.')[0].split(' ')[0];
                    } else if (j%2==1){
                        nameUrl = nameUrl + '$' + $(tds[j]).text().split('【')[0];
                        nameUrls.push(nameUrl);
                    }
                }
                if (playFromStr.length > 0) {
                    playFromStr += '$$$';
                    playUrlStr += '$$$';
                }
                playFromStr +=  playFrom;
                playUrlStr += nameUrls.join('#');
            }
        }


        const video = {
            vod_actor: actor,
            vod_play_from: playFromStr,
            vod_play_url: playUrlStr,
            vod_director: director,
            vod_content: content,
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
    let url = siteUrl + '/search.php?q=' + wd
    //console.log('search url:', url);
    let videos = await getVideos(url);
    return JSON.stringify({
        list: videos,
    });
}

async function play(flag, id, flags) {
    return JSON.stringify({
        parse: 0,
        url: id,
    });
}

async function getVideos(url) {
    const html = await request(url);
    const $ = load(html);
    const cards = $('div.row.posts-wrapper >div > article > div.entry-media > div > a')
    let videos = _.map(cards, (n) => {
        let id = n.attribs['href'];
        let name = $($(n).find('img')[0]).attr('alt').replaceAll('<strong>','').replaceAll('</strong>', '').split(' ')[0];
        let pic = $($(n).find('img')[0]).attr('data-src');
        return {
            vod_id: id,
            vod_name: name,
            vod_pic: pic,
            vod_remarks: '',
        };
    });
    return videos;
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