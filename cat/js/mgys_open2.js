import { Crypto, load, _ } from './lib/cat.js';

let key = 'mgys';
let HOST = 'https://www.moguys.xyz';
let siteKey = '';
let siteType = 0;

const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1';

async function request(reqUrl, timeout = 60000) {
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
    let classes = [{"type_id":"1","type_name":"电影"},{"type_id":"2","type_name":"电视剧"},{"type_id":"3","type_name":"动漫"},{"type_id":"4","type_name":"综艺"}];
    let filterObj = {
        "1":[{"key":"class","name":"剧情","init":"","value":[{"n":"全部","v":""},{"n":"动作","v":"动作"},{"n":"爱情","v":"爱情"},{"n":"喜剧","v":"喜剧"},{"n":"科幻","v":"科幻"},{"n":"恐怖","v":"恐怖"},{"n":"战争","v":"战争"},{"n":"武侠","v":"武侠"},{"n":"剧情","v":"剧情"},{"n":"动画","v":"动画"},{"n":"惊悚","v":"惊悚"},{"n":"灾难","v":"灾难"},{"n":"悬疑","v":"悬疑"},{"n":"冒险","v":"冒险"},{"n":"犯罪","v":"犯罪"},{"n":"纪录","v":"纪录"},{"n":"古装","v":"古装"},{"n":"奇幻","v":"奇幻"}]},{"key":"area","name":"地区","init":"","value":[{"n":"全部","v":""},{"n":"🇨🇳中国","v":"大陆"},{"n":"🇰🇷韩国","v":"韩国"},{"n":"🇺🇸美国","v":"美国"},{"n":"🇭🇰香港","v":"香港"},{"n":"🇹🇼台湾","v":"台湾"},{"n":"🇯🇵日本","v":"日本"},{"n":"泰国","v":"泰国"},{"n":"英国","v":"英国"},{"n":"新加坡","v":"新加坡"},{"n":"其他","v":"其他"}]},{"key":"year","name":"年份","init":"","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"}]},{"key":"lang","name":"语言","init":"","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"法语","v":"法语"},{"n":"德语","v":"德语"},{"n":"其它","v":"其它"}]},{"key":"by","name":"排序","init":"","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
        "2":[{"key":"class","name":"剧情","init":"","value":[{"n":"全部","v":""},{"n":"古装","v":"古装"},{"n":"奇幻","v":"奇幻"},{"n":"动作","v":"动作"},{"n":"爱情","v":"爱情"},{"n":"喜剧","v":"喜剧"},{"n":"科幻","v":"科幻"},{"n":"恐怖","v":"恐怖"},{"n":"战争","v":"战争"},{"n":"武侠","v":"武侠"},{"n":"惊悚","v":"惊悚"},{"n":"悬疑","v":"悬疑"},{"n":"冒险","v":"冒险"},{"n":"犯罪","v":"犯罪"}]},{"key":"area","name":"地区","init":"","value":[{"n":"全部","v":""},{"n":"🇨🇳中国","v":"大陆"},{"n":"🇰🇷韩国","v":"韩国"},{"n":"🇺🇸美国","v":"美国"}]},{"key":"year","name":"年份","init":"","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"}]},{"key":"lang","name":"语言","init":"","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]},{"key":"by","name":"排序","init":"","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
        "3":[{"key":"class","name":"剧情","init":"","value":[{"n":"全部","v":""},{"n":"选秀","v":"选秀"},{"n":"情感","v":"情感"},{"n":"访谈","v":"访谈"},{"n":"播报","v":"播报"},{"n":"旅游","v":"旅游"},{"n":"音乐","v":"音乐"},{"n":"美食","v":"美食"},{"n":"纪实","v":"纪实"},{"n":"曲艺","v":"曲艺"},{"n":"生活","v":"生活"},{"n":"游戏互动","v":"游戏互动"},{"n":"财经","v":"财经"},{"n":"求职","v":"求职"}]},{"key":"area","name":"地区","init":"","value":[{"n":"全部","v":""},{"n":"🇨🇳中国","v":"大陆"},{"n":"🇰🇷韩国","v":"韩国"},{"n":"🇺🇸美国","v":"美国"},{"n":"🇭🇰香港","v":"香港"},{"n":"🇹🇼台湾","v":"台湾"},{"n":"🇯🇵日本","v":"日本"},{"n":"泰国","v":"泰国"},{"n":"英国","v":"英国"},{"n":"新加坡","v":"新加坡"},{"n":"其他","v":"其他"}]},{"key":"year","name":"年份","init":"","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"}]},{"key":"lang","name":"语言","init":"","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]},{"key":"by","name":"排序","init":"","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
        "4":[{"key":"class","name":"剧情","init":"","value":[{"n":"全部","v":""},{"n":"情感","v":"情感"},{"n":"科幻","v":"科幻"},{"n":"热血","v":"热血"},{"n":"推理","v":"推理"},{"n":"搞笑","v":"搞笑"},{"n":"冒险","v":"冒险"},{"n":"萝莉","v":"萝莉"},{"n":"校园","v":"校园"},{"n":"动作","v":"动作"},{"n":"机战","v":"机战"},{"n":"运动","v":"运动"},{"n":"战争","v":"战争"},{"n":"少年","v":"少年"},{"n":"少女","v":"少女"},{"n":"社会","v":"社会"},{"n":"原创","v":"原创"},{"n":"亲子","v":"亲子"},{"n":"益智","v":"益智"},{"n":"励志","v":"励志"},{"n":"其他","v":"其他"}]},{"key":"area","name":"地区","init":"","value":[{"n":"全部","v":""},{"n":"🇨🇳中国","v":"大陆"},{"n":"🇰🇷韩国","v":"韩国"},{"n":"🇺🇸美国","v":"美国"},{"n":"🇭🇰香港","v":"香港"},{"n":"🇹🇼台湾","v":"台湾"},{"n":"🇯🇵日本","v":"日本"},{"n":"泰国","v":"泰国"},{"n":"英国","v":"英国"},{"n":"新加坡","v":"新加坡"},{"n":"其他","v":"其他"}]},{"key":"year","name":"年份","init":"","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"}]},{"key":"lang","name":"语言","init":"","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]},{"key":"by","name":"排序","init":"","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}]
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
    const link = HOST + '/vodshow/' + tid + '-' + (extend.area || '') + '-' + (extend.by || '') + '-' + (extend.class || '') + '-' + (extend.lang || '') + '----' + page + '---' + (extend.year || '') + '.html';//https://www.moguys.xyz/vodshow/1-%E5%A4%A7%E9%99%86-time-%E5%8A%A8%E4%BD%9C-%E5%9B%BD%E8%AF%AD----2---2023.html
    const html = await request(link);
    const $ = load(html);
    const items = $('.leo-video-item');
    let videos = _.map(items, (item) => {
        const it = $(item).find('a:first')[0];
        const img = $(item).find('img:first')[0];
        const remarks = $($(item).find('div.leo-video-remark')[0]).text().trim();
        return {
            vod_id: it.attribs.href.replace(/.*?\/voddetail\/(.*).html/g, '$1'),
            vod_name: it.attribs.title,
            vod_pic: img.attribs['data-original'],
            vod_remarks: remarks || '',
        };
    });
    const hasMore = $('a.leo-page-elem:contains(下一页)').length > 0;
    const pgCount = hasMore ? parseInt(pg) + 1 : parseInt(pg);
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: 24,
        total: 24 * pgCount,
        list: videos,
    });
}

async function detail(id) {
    const html = await request(HOST + '/voddetail/' + id + '.html');
    const $ = load(html);
    const vod = {
        vod_id: id,
        vod_name: $('font.leo-col-6').text(),
        vod_type: $('.leo-detail-media li:contains(分类：) a:eq(1)').text().trim(),
        vod_year: $('.leo-detail-media li:contains(年代：) a:first').text().trim(),
        vod_area: $('.leo-detail-media li:contains(地区：) a:first').text().trim(),
        vod_director: $('.leo-detail-media li:contains(导演：)').text().trim().substring(3),
        vod_actor: $('.leo-detail-media li:contains(主演：)').text().trim().substring(3),
        vod_pic: $('.leo-detail-cover').attr('data-original'),
        vod_remarks : $('.leo-detail-media h1:first').text().split('|')[1] || '',
        vod_content: $('#leo-detail-info').text().trim().substring(5).trim(),
    };
    let playMap = {};
    let tabs = $('.leo-source-cho li');
    let playlists = $('.leo-play-num');
    _.each(tabs, (tab, i) => {
        let from = tab.children[1].data;
        let list = playlists[i];
        list = $(list).find('a');
        _.each(list, (it) => {
            let title = 'HD';
            if (it.children.length > 0) {
                title = it.children[0].data.trim();
            }
            let playUrl = it.attribs.href.replace(/.*?\/vodplay\/(.*).html/g, '$1');
            if (!playMap.hasOwnProperty(from)) {
                playMap[from] = [];
            }
            playMap[from].push(title + '$' + playUrl);
        });
    });
    vod.vod_play_from = _.keys(playMap).join('$$$');
    let urls = _.values(playMap);
    let vod_play_url = _.map(urls, (urlist) => {
        return urlist.join('#');
    });
    vod.vod_play_url = vod_play_url.join('$$$');
    return JSON.stringify({
        list: [vod],
    });
}

async function play(flag, id, flags) {
    const link = HOST + '/vodplay/' + id + '.html';
    const html = await request(link);
    const $ = load(html);
    let json = $('script:contains(player_aaaa)').text().replace('var player_aaaa=','');
    let js = JSON.parse(json);
    let playUrl = js.url;
    if (js.encrypt == 1) {
        playUrl = unescape(playUrl);
    } else if (js.encrypt == 2) {
        playUrl = unescape(base64Decode(playUrl));
    }
    let playHtml = await request('https://player.moguys.work/player/ec.php?code=pl&if=1&url=' + playUrl);
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