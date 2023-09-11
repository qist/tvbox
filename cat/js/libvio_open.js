// 自动从 地址发布页 获取&跳转url地址
import { load, _ } from './lib/cat.js';

var key = 'libvio';
var HOST = 'https://libvio.app'; // 地址发布页
var host = '';
var siteKey = '';
var siteType = 0;

const MOBILE_UA = 'Mozilla/5.0 (Linux; Android 11; M2007J3SC Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045714 Mobile Safari/537.36';

async function request(reqUrl, agentSp) {
    var res = await req(reqUrl, {
        method: 'get',
        headers: {
            'User-Agent': agentSp || MOBILE_UA,
            'Referer': host
        },
    });
    return res.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
    var html = await request(HOST);
    var $ = load(html);
    host = $('div.content-top > ul > li').find('a:first')[0].attribs.href;
    // console.debug('libvio跳转地址 =====>' + urls); // js_debug.log
}

async function home(filter) {
    var html = await request(host);
    var $ = load(html);
    var class_parse = $('ul.stui-header__menu > li > a[href*=type]');
    var classes = [];
    classes = _.map(class_parse, (cls) => {
        var typeId = cls.attribs['href'];
        typeId = typeId.substring(typeId.lastIndexOf('/') + 1).replace('.html','');
        return {
            type_id: typeId,
            type_name: cls.children[0].data,
        };
    });
    var filterObj = {
        1:[{key:'area',name:'地区',value:[{n:'全部',v:''},{n:'中国大陆',v:'中国大陆'},{n:'中国香港',v:'中国香港'},{n:'中国台湾',v:'中国台湾'},{n:'美国',v:'美国'},{n:'法国',v:'法国'},{n:'英国',v:'英国'},{n:'日本',v:'日本'},{n:'韩国',v:'韩国'},{n:'德国',v:'德国'},{n:'泰国',v:'泰国'},{n:'印度',v:'印度'},{n:'意大利',v:'意大利'},{n:'西班牙',v:'西班牙'},{n:'加拿大',v:'加拿大'},{n:'其他',v:'其他'}]},{key:'year',name:'年份',value:[{n:'全部',v:''},{n:'2023',v:'2023'},{n:'2022',v:'2022'},{n:'2021',v:'2021'},{n:'2020',v:'2020'},{n:'2019',v:'2019'},{n:'2018',v:'2018'},{n:'2017',v:'2017'},{n:'2016',v:'2016'},{n:'2015',v:'2015'},{n:'2014',v:'2014'},{n:'2013',v:'2013'},{n:'2012',v:'2012'},{n:'2011',v:'2011'},{n:'2010',v:'2010'}]},{key:'lang',name:'语言',value:[{n:'全部',v:''},{n:'国语',v:'国语'},{n:'英语',v:'英语'},{n:'粤语',v:'粤语'},{n:'闽南语',v:'闽南语'},{n:'韩语',v:'韩语'},{n:'日语',v:'日语'},{n:'法语',v:'法语'},{n:'德语',v:'德语'},{n:'其它',v:'其它'}]},{key:'by',name:'排序',value:[{n:'时间',v:'time'},{n:'人气',v:'hits'},{n:'评分',v:'score'}]}],
        2:[{key:'area',name:'地区',value:[{n:'全部',v:''},{n:'中国大陆',v:'中国大陆'},{n:'中国台湾',v:'中国台湾'},{n:'中国香港',v:'中国香港'},{n:'韩国',v:'韩国'},{n:'日本',v:'日本'},{n:'美国',v:'美国'},{n:'泰国',v:'泰国'},{n:'英国',v:'英国'},{n:'新加坡',v:'新加坡'},{n:'其他',v:'其他'}]},{key:'year',name:'年份',value:[{n:'全部',v:''},{n:'2023',v:'2023'},{n:'2022',v:'2022'},{n:'2021',v:'2021'},{n:'2020',v:'2020'},{n:'2019',v:'2019'},{n:'2018',v:'2018'},{n:'2017',v:'2017'},{n:'2016',v:'2016'},{n:'2015',v:'2015'},{n:'2014',v:'2014'},{n:'2013',v:'2013'},{n:'2012',v:'2012'},{n:'2011',v:'2011'},{n:'2010',v:'2010'}]},{key:'lang',name:'语言',value:[{n:'全部',v:''},{n:'国语',v:'国语'},{n:'英语',v:'英语'},{n:'粤语',v:'粤语'},{n:'闽南语',v:'闽南语'},{n:'韩语',v:'韩语'},{n:'日语',v:'日语'},{n:'其它',v:'其它'}]},{key:'by',name:'排序',value:[{n:'时间',v:'time'},{n:'人气',v:'hits'},{n:'评分',v:'score'}]}],
        4:[{key:'area',name:'地区',value:[{n:'全部',v:''},{n:'中国',v:'中国'},{n:'日本',v:'日本'},{n:'欧美',v:'欧美'},{n:'其他',v:'其他'}]},{key:'year',name:'年份',value:[{n:'全部',v:''},{n:'2023',v:'2023'},{n:'2022',v:'2022'},{n:'2021',v:'2021'},{n:'2020',v:'2020'},{n:'2019',v:'2019'},{n:'2018',v:'2018'},{n:'2017',v:'2017'},{n:'2016',v:'2016'},{n:'2015',v:'2015'},{n:'2014',v:'2014'},{n:'2013',v:'2013'},{n:'2012',v:'2012'},{n:'2011',v:'2011'},{n:'2010',v:'2010'},{n:'2009',v:'2009'},{n:'2008',v:'2008'},{n:'2007',v:'2007'},{n:'2006',v:'2006'},{n:'2005',v:'2005'},{n:'2004',v:'2004'}]},{key:'lang',name:'语言',value:[{n:'全部',v:''},{n:'国语',v:'国语'},{n:'英语',v:'英语'},{n:'粤语',v:'粤语'},{n:'闽南语',v:'闽南语'},{n:'韩语',v:'韩语'},{n:'日语',v:'日语'},{n:'其它',v:'其它'}]},{key:'by',name:'排序',value:[{n:'时间',v:'time'},{n:'人气',v:'hits'},{n:'评分',v:'score'}]}],
        27:[{key:'by',name:'排序',value:[{n:'时间',v:'time'},{n:'人气',v:'hits'},{n:'评分',v:'score'}]}],
        15:[{key:'area',name:'地区',value:[{n:'全部',v:''},{n:'日本',v:'日本'},{n:'韩国',v:'韩国'}]},{key:'year',name:'年份',value:[{n:'全部',v:''},{n:'2023',v:'2023'},{n:'2022',v:'2022'},{n:'2021',v:'2021'},{n:'2020',v:'2020'},{n:'2019',v:'2019'},{n:'2018',v:'2018'},{n:'2017',v:'2017'},{n:'2016',v:'2016'},{n:'2015',v:'2015'},{n:'2014',v:'2014'},{n:'2013',v:'2013'},{n:'2012',v:'2012'},{n:'2011',v:'2011'},{n:'2010',v:'2010'}]},{key:'lang',name:'语言',value:[{n:'全部',v:''},{n:'国语',v:'国语'},{n:'英语',v:'英语'},{n:'粤语',v:'粤语'},{n:'闽南语',v:'闽南语'},{n:'韩语',v:'韩语'},{n:'日语',v:'日语'},{n:'其它',v:'其它'}]},{key:'by',name:'排序',value:[{n:'时间',v:'time'},{n:'人气',v:'hits'},{n:'评分',v:'score'}]}],
        16:[{key:'area',name:'地区',value:[{n:'全部',v:''},{n:'美国',v:'美国'},{n:'英国',v:'英国'},{n:'德国',v:'德国'},{n:'加拿大',v:'加拿大'},{n:'其他',v:'其他'}]},{key:'year',name:'年份',value:[{n:'全部',v:''},{n:'2023',v:'2023'},{n:'2022',v:'2022'},{n:'2021',v:'2021'},{n:'2020',v:'2020'},{n:'2019',v:'2019'},{n:'2018',v:'2018'},{n:'2017',v:'2017'},{n:'2016',v:'2016'},{n:'2015',v:'2015'},{n:'2014',v:'2014'},{n:'2013',v:'2013'},{n:'2012',v:'2012'},{n:'2011',v:'2011'},{n:'2010',v:'2010'}]},{key:'lang',name:'语言',value:[{n:'全部',v:''},{n:'国语',v:'国语'},{n:'英语',v:'英语'},{n:'粤语',v:'粤语'},{n:'闽南语',v:'闽南语'},{n:'韩语',v:'韩语'},{n:'日语',v:'日语'},{n:'其它',v:'其它'}]},{key:'by',name:'排序',value:[{n:'时间',v:'time'},{n:'人气',v:'hits'},{n:'评分',v:'score'}]}]
    };
    return JSON.stringify({
        class: classes,
        filters: filterObj,
    });
}

async function homeVod() {
    var link = host + '/show/1--hits---------.html';
    var html = await request(link);
    var $ = load(html);
    var items = $('ul.stui-vodlist > li');
    let videos = _.map(items, (item) => {
        var a = $(item).find('a:first')[0];
        var remarks = $($(item).find('span.pic-text')[0]).text().trim();
        return {
            vod_id: a.attribs.href.replace(/.*?\/detail\/(.*).html/g, '$1'),
            vod_name: a.attribs.title,
            vod_pic: a.attribs['data-original'],
            vod_remarks: remarks || '',
        };
    });
    return JSON.stringify({
        list: videos,
    });
}

async function category(tid, pg, filter, extend) {
    if (pg <= 0 || typeof(pg) == 'undefined') pg = 1;
    var link = host + '/show/' + tid + '-' + (extend.area || '') + '-' + (extend.by || 'time') + '--' + (extend.lang || '') + '----' + pg + '---' + (extend.year || '') + '.html';
    var html = await request(link);
    var $ = load(html);
    var items = $('ul.stui-vodlist > li');
    let videos = _.map(items, (item) => {
        var a = $(item).find('a:first')[0];
        var remarks = $($(item).find('span.pic-text')[0]).text().trim();
        return {
            vod_id: a.attribs.href.replace(/.*?\/detail\/(.*).html/g, '$1'),
            vod_name: a.attribs.title,
            vod_pic: a.attribs['data-original'],
            vod_remarks: remarks || '',
        };
    });
    var hasMore = $('ul.stui-page__item > li > a:contains(下一页)').length > 0;
    var pgCount = hasMore ? parseInt(pg) + 1 : parseInt(pg);
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: 24,
        total: 24 * pgCount,
        list: videos,
    });
}

async function detail(id) {
    var html = await request(host + '/detail/' + id + '.html');
    var $ = load(html);
    var vod = {
        vod_id: id,
        vod_name: $('h1:first').text().trim(),
        vod_type: $('.stui-content__detail p:first a').text(),
        vod_actor: $('.stui-content__detail p:nth-child(3)').text().replace('主演：',''),
        vod_pic: $('.stui-content__thumb img:first').attr('data-original'),
        vod_remarks : $('.stui-content__detail p:nth-child(5)').text() || '',
        vod_content: $('span.detail-content').text().trim(),
    };
    var playMap = {};
    var tabs = $('div.stui-pannel__head > h3[class*=iconfont]');
    var playlists = $('ul.stui-content__playlist');
    _.each(tabs, (tab, i) => {
        var from = tab.children[0].data;
        var list = playlists[i];
        list = $(list).find('a');
        _.each(list, (it) => {
            var title = it.children[0].data;
            var playUrl = it.attribs.href;
            if (title.length == 0) title = it.children[0].data.trim();
            if (!playMap.hasOwnProperty(from)) {
                playMap[from] = [];
            }
            playMap[from].push( title + '$' + playUrl);
        });
    });
    vod.vod_play_from = _.keys(playMap).join('$$$');
    var urls = _.values(playMap);
    var vod_play_url = _.map(urls, (urlist) => {
        return urlist.join('#');
    });
    vod.vod_play_url = vod_play_url.join('$$$');
    return JSON.stringify({
        list: [vod],
    });
}

async function play(flag, id, flags) {
    var html = await request(host + id);
    html = html.match(/r player_.*?=(.*?)</)[1];
    var js = JSON.parse(html);
    var url = js.url;
    var from = js.from;
    var next = js.link_next;
    var id = js.id;
    var nid = js.nid;
    var paurl = await request(host +'/static/player/' + from + '.js');
    paurl = paurl.match(/ src="(.*?)'/)[1];
    var purl = paurl + url + '&next=' + next + '&id=' + id + '&nid=' + nid;
    var playUrl = await request(purl);
    playUrl = playUrl.match(/var .* = '(.*?)'/)[1];
    // console.debug('libvio playUrl =====>' + playUrl); // js_debug.log
    return JSON.stringify({
        parse: 0,
        url: playUrl,
    });
}

async function search(wd, quick) {
    var data = JSON.parse(await request(host + '/index.php/ajax/suggest?mid=1&wd=' + wd + '&limit=50')).list;
    var videos = [];
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
        limit: 50,
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