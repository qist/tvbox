import { Crypto, load, _ } from 'assets://js/lib/cat.js';

const key = 'ggys';
const HOST = 'https://ggys.me';
const TYPE_MOVIE = 'movie';
const TYPE_TVSHOW = 'tv-show';
let siteKey = '';
let siteType = 0;

const UA = 'Mozilla/5.0 (Linux; Android 11; M2007J3SC Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045714 Mobile Safari/537.36';

async function request(reqUrl, method, data) {
    const res = await req(reqUrl, {
        method: method || 'get',
        headers: {
            'User-Agent': UA,
            'Referer': HOST,
        },
        data: data,
        postType: method === 'post' ? 'form' : '',
    });
    return res.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
    if (cfg.hasOwnProperty('ext')) {
        if (cfg.ext.hasOwnProperty('host')) {
            HOST = cfg.ext.host;
        }
    }
}

async function home(filter) {
    const classes = [{'type_id':'movies','type_name':'电影'},{'type_id':'tv-shows','type_name':'剧集'}];
    const filterObj = {
        'movies':[{'key':'class','name':'类型','init':'','value':[{'n':'全部','v':''},{'n':'欧美电影','v':'tag/欧美电影'},{'n':'华语电影','v':'tag/华语电影'},{'n':'日韩电影','v':'tag/日韩电影'},{'n':'其他地区','v':'tag/其他地区'},{'n':'冒险','v':'genre/冒险'},{'n':'剧情','v':'genre/剧情'},{'n':'动作','v':'genre/动作'},{'n':'动画','v':'genre/动画'},{'n':'历史','v':'genre/历史'},{'n':'喜剧','v':'genre/喜剧'},{'n':'奇幻','v':'genre/奇幻'},{'n':'家庭','v':'genre/家庭'},{'n':'恐怖','v':'genre/恐怖'},{'n':'悬疑','v':'genre/悬疑'},{'n':'惊悚','v':'genre/惊悚'},{'n':'战争','v':'genre/战争'},{'n':'爱情','v':'genre/爱情'},{'n':'犯罪','v':'genre/犯罪'},{'n':'科幻','v':'genre/科幻'},{'n':'纪录','v':'genre/纪录'},{'n':'音乐','v':'genre/音乐'}]}],
        'tv-shows':[{'key':'class','name':'类型','init':'','value':[{'n':'全部','v':''},{'n':'欧美剧','v':'tag/欧美剧'},{'n':'日韩剧','v':'tag/日韩剧'},{'n':'国产剧','v':'tag/国产剧'},{'n':'其他地区','v':'tag/其他地区'},{'n':'剧情','v':'genre/剧情'},{'n':'动作','v':'genre/动作'},{'n':'动画','v':'genre/动画'},{'n':'喜剧','v':'genre/喜剧'},{'n':'家庭','v':'genre/家庭'},{'n':'悬疑','v':'genre/悬疑'},{'n':'犯罪','v':'genre/犯罪'},{'n':'科幻','v':'genre/科幻'},{'n':'西部','v':'genre/西部'}]}],
    };
    return JSON.stringify({
        class: classes,
        filters: filterObj,
    });
}

async function homeVod() {}

async function category(tid, pg, filter, extend) {
    if (pg <= 0) pg = 1;
    let path = '';
    const prefixMap = {
        'movies': TYPE_MOVIE,
        'tv-shows': TYPE_TVSHOW,
    }
    const prefix = prefixMap[tid];
    if (extend.class) {
        path = '/' + prefix + '-' + extend.class;
    } else {
        path = '/' + tid;
    }
    let page = '';
    if (pg > 1) {
        page = 'page/' + pg + '/';
    }
    const link = HOST + path + '/' + page;
    const html = await request(link);
    const $ = load(html);
    const videos = [];
    parseVideoList($, prefix, false, videos);
    const limit = 20;
    const hasMore = $('.page-numbers a.next').length > 0;
    const pgCount = hasMore ? parseInt(pg) + 1 : parseInt(pg);
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: limit,
        total: limit * pgCount,
        list: videos,
    });
}

function parseVideoList($, prefix, imgSrc, videos) {
    const items = $('.' + prefix);
    _.each(items, (item) => {
        const $item = $(item);
        const title = $item.find('.' + prefix + '__title:first').text();
        const url = $item.find('.' + prefix + '__actions a:first').attr('href');
        const imgAttr = imgSrc ? 'src' : 'data-lazy-src';
        const image = $item.find('.' + prefix + '__poster img:first').attr(imgAttr);
        const remarks = $item.find('.' + prefix + '__meta span:last').text();
        if (!url) return;
        const videoItem = {
            vod_id: decodeURIComponent(url.replace(/.*\/\/.*\/(.*\/.*)\//g, '$1')),
            vod_name: title,
            vod_pic: image,
            vod_remarks: remarks,
        };
        videos.push(videoItem);
    });
}

async function detail(id) {
    const isMovieType = id.startsWith(TYPE_MOVIE);
    const html = await request(HOST + '/' + id + '/');
    const $ = load(html);
    const prefix = isMovieType ? TYPE_MOVIE : TYPE_TVSHOW;
    const vod = {
        vod_id: id,
        vod_name: $('.' + prefix + '_title').text(),
        vod_actor: $('.' + prefix + '-casts').text().trim().substring(3).replace(/\s+\/\s+/g, '/'),
        vod_pic: $('.' + prefix + '__poster img:first').attr('data-lazy-src'),
        vod_remarks: $('.' + prefix + '__meta span:last').text(),
    };
    if (isMovieType) {
        vod.vod_type = $('.' + prefix + '__meta span:last').text();
        vod.vod_year = $('.' + prefix + '__meta span:first').text();
        vod.vod_content = $('.movie__description').text();
    } else {
        vod.vod_type = $('.' + prefix + '__meta span:first').text();
        vod.vod_content = $('.tv-show__info--body').text();
    }
    const from = 'ggys';
    const playMap = {};
    if (isMovieType) {
        const playId = $('.ggys-video-player').attr('data-source-id');
        const playCfg = playId + '@' + TYPE_MOVIE;
        playMap[from] = [ '全$' + playCfg ];
    } else {
        const tabs = $('.tv_show__season-tabs-wrap .nav-item');
        const episodes = $('.episodes');
        _.each(tabs, (tab, i) => {
            const titlePrefix = $(tab).text().trim();
            const episodeList = $(episodes[i]).find('.episode__body');
            _.each(episodeList, (episode) => {
                const $episode = $(episode);
                const title = titlePrefix + ' ' + $episode.text().trim();
                const url = $episode.find('a').attr('href');
                const playCfg = url + '@' + TYPE_TVSHOW;
                if (!playMap.hasOwnProperty(from)) {
                    playMap[from] = [];
                }
                playMap[from].push(title + '$' + playCfg);
            });
        });
    }
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
    const playCfg = id.split('@');
    const playType = playCfg[1];
    let playId = playCfg[0];
    let playUrl;
    if (playType == TYPE_TVSHOW) {
        const html = await request(playId);
        const $ = load(html);
        playId = $('.ggys-video-player').attr('data-source-id');
    }
    const param = {
        video_id: playId,
    };
    const resp = await request(HOST + '/wp-json/get_addr/v1/get_video_url', 'post', param);
    playUrl = JSON.parse(resp).video_url;
    const headers = {
        'User-Agent': UA,
        'Referer': HOST,
    };
    return JSON.stringify({
        parse: 0,
        url: playUrl,
        header: headers,
    });
}

async function search(wd, quick, pg) {
    let page = '';
    if (pg > 1) {
        page = '/page/' + pg;
    }
    const url = HOST + '/search/' + wd + page + '/?post_type=';
    const videos = [];
    let html = await request(url + 'movie');
    let $ = load(html);
    parseVideoList($, TYPE_MOVIE, true, videos);
    const hasMoreMovie = $('.page-numbers a.next').length > 0;
    html = await request(url + 'tv_show');
    $ = load(html);
    parseVideoList($, TYPE_TVSHOW, true, videos);
    const hasMoreTVShow = $('.page-numbers a.next').length > 0;
    const limit = 40;
    const hasMore = hasMoreMovie || hasMoreTVShow;
    const pgCount = hasMore ? parseInt(pg) + 1 : parseInt(pg);
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: limit,
        total: limit * pgCount,
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