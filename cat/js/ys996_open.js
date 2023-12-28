import { Crypto, load, _ } from './lib/cat.js';

let siteUrl = 'https://www.cs1369.com';
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
        type_id: '1',
        type_name: '电影',
    },{
        type_id: '2',
        type_name: '电视',
    },{
        type_id: '3',
        type_name: '动漫',
    }];

    let filterObj = genFilterObj();
    return JSON.stringify({
        class: classes,
        filters: filterObj
    });
}

async function homeVod() {
    let videos = await getVideos(siteUrl);
    return JSON.stringify({
        list: videos,
    });
}

async function category(tid, pg, filter, extend) {
    let url = siteUrl;
    if (filter) {
        url = url + '/show';
        let area = extend['area'];
        if (area && area != '') {
            url = url + '/area/' + area;
        }
        let clazz = extend['class']
        if (clazz && clazz != '') {
            url = url + '/class/' + clazz;
        }
        let id = extend['id'];
        if(id && id != '') {
            url = url + '/id/' + id;
        } else {
            url = url + '/id/' + tid;
        }
        let year = extend['year'];
        if (year && year != '') {
            url = url + '/year/' + year;
        }
        if (pg && pg > 1) {
            url = url + '/page/' + pg;
        }
        url = url + '.html';
    } else {
        url = url + '/vod/type';
        url = url + '/id/' + tid;
        if (pg && pg > 1) {
            url = url + '/page/' + pg;
        }
        url = url + '.html';
    }
    //console.log('cate page url:', url);

    let videos = await getVideos(url);
    return JSON.stringify({
        list: videos,
        page: pg
    });
}

async function detail(id) {
    try {
        let url = siteUrl + id;
        const html = await request(url);
        const $ = load(html);
        let actors = _.map($('div.stui-content__detail > p:nth-child(3) > a'), (n) => {
            return $(n).text();
        });
        let actor = actors.join(' ');
        let director = $('div.stui-content__detail > p:nth-child(4) > a').text();
        let title = $('div.stui-content__detail > h1.title').text();
        let content = $('div.stui-pannel_bd > p').text();
        const cards = $('div.stui-pannel_bd.col-pd.clearfix > ul > li > a');
        let playUrls = _.map(cards, (n) => {
            return $(n).text() + '$' + n.attribs['href'];
        });

        const video = {
            vod_actor: actor,
            vod_play_from: 'Leospring',
            vod_play_url: playUrls.join('#'),
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
    let url = siteUrl + '/search/wd/' + wd + '.html';
    //console.log('search url:', url);
    const html = await request(url);
    const $ = load(html);
    const cards = $('div.stui-pannel_bd > ul.stui-vodlist__media.col-pd.clearfix > li');
    let videos = _.map(cards, (n) => {
        let id = $($(n).find('div.thumb > a')[0]).attr('href');
        let name = $($(n).find('div.thumb > a')[0]).attr('title');
        let pic = $($(n).find('div.thumb > a')[0]).attr('data-original');
        let remark = $($(n).find('div.thumb > a > span:nth-child(2)')[0]).text();

        return {
            vod_id: id,
            vod_name: name,
            vod_pic: pic,
            vod_remarks: remark,
        };
    });
    return JSON.stringify({
        list: videos,
    });
}

async function play(flag, id, flags) {
    let url = siteUrl + id;
    const html = await request(url);
    const $ = load(html);
    let info = '';
    for(const n of $('script')) {
        if($(n).text().indexOf('player_aaaa=') > 0) {
            info = $(n).text().split('player_aaaa=')[1];
            break;
        }
    }
    //console.log('info', info);
    let obj = JSON.parse(info);
    let playUrl = obj.url;
    if(obj.encrypt == 1) {
        playUrl = unescape(playUrl);
    } else if (obj.encrypt == 2) {
        playUrl = unescape(base64Decode(playUrl))
    }
    return JSON.stringify({
        parse: 0,
        url: playUrl,
    });
}


function genFilterObj() {
    return {
        '1':[
            {
                key: 'id',
                name: '类型', 
                value: [{n:'全部',v:''},{n:'动作片',v:'6'},{n:'喜剧片',v:'7'},{n:'爱情片',v:'8'},{n:'科幻片',v:'9'},{n:'恐怖片',v:'10'},{n:'剧情片',v:'11'},{n:'战争片',v:'12'},{n:'动画片',v:'13'},{n:'纪录片',v:'14'}]
            },{
                key: 'class',
                name: '剧情', 
                value: [{n:'全部',v:''},{n:'喜剧',v:'喜剧'},{n:'爱情',v:'爱情'},{n:'恐怖',v:'恐怖'},{n:'动作',v:'动作'},{n:'科幻',v:'科幻'},{n:'剧情',v:'剧情'},{n:'战争',v:'战争'},{n:'警匪',v:'警匪'},{n:'犯罪',v:'犯罪'},{n:'动画',v:'动画'},{n:'奇幻',v:'奇幻'},{n:'武侠',v:'武侠'},{n:'冒险',v:'冒险'},{n:'枪战',v:'枪战'},{n:'悬疑',v:'悬疑'},{n:'惊悚',v:'惊悚'},{n:'经典',v:'经典'},{n:'青春',v:'青春'},{n:'文艺',v:'文艺'},{n:'微电影',v:'微电影'},{n:'古装',v:'古装'},{n:'历史',v:'历史'},{n:'运动',v:'运动'},{n:'农村',v:'农村'},{n:'儿童',v:'儿童'},{n:'网络电影',v:'网络电影'}]
            },{
                key: 'area',
                name: '地区', 
                value: [{n:'全部',v:''},{n:'中国大陆',v:'中国大陆'},{n:'中国香港',v:'中国香港'},{n:'中国台湾',v:'中国台湾'},{n:'美国',v:'美国'},{n:'韩国',v:'韩国'},{n:'日本',v:'日本'},{n:'泰国',v:'泰国'},{n:'新加坡',v:'新加坡'},{n:'马来西亚',v:'马来西亚'},{n:'印度',v:'印度'},{n:'英国',v:'英国'},{n:'法国',v:'法国'},{n:'加拿大',v:'加拿大'},{n:'西班牙',v:'西班牙'},{n:'俄罗斯',v:'俄罗斯'}]
            },{
                key: 'year',
                name: '年份', 
                value: [{n:'全部',v:''},{n:'2023',v:'2023'},{n:'2022',v:'2022'},{n:'2021',v:'2021'},{n:'2020',v:'2020'},{n:'2019',v:'2019'},{n:'2018',v:'2018'},{n:'2017',v:'2017'},{n:'2016',v:'2016'},{n:'2015',v:'2015'},{n:'2014',v:'2014'},{n:'2013',v:'2013'},{n:'2012',v:'2012'},{n:'2011',v:'2011'},{n:'2010',v:'2010'},{n:'2009',v:'2009'},{n:'2008',v:'2008'},{n:'2007',v:'2007'},{n:'2006',v:'2006'},{n:'2005',v:'2005'},{n:'2004',v:'2004'},{n:'2003',v:'2003'},{n:'2002',v:'2002'},{n:'2001',v:'2001'},{n:'2000',v:'2000'}]
            }],
        '2':[{
                key: 'id',
                name: '类型', 
                value: [{n:'全部',v:''},{n:'内地',v:'15'},{n:'美国',v:'16'},{n:'英国',v:'17'},{n:'韩国',v:'18'},{n:'泰国',v:'20'},{n:'日本',v:'21'},{n:'香港',v:'22'},{n:'台湾',v:'23'}]
            },{
                key: 'class',
                name: '剧情', 
                value: [{n:'全部',v:''},{n:'古装',v:'古装'},{n:'战争',v:'战争'},{n:'青春偶像',v:'青春偶像'},{n:'喜剧',v:'喜剧'},{n:'家庭',v:'家庭'},{n:'犯罪',v:'犯罪'},{n:'动作',v:'动作'},{n:'奇幻',v:'奇幻'},{n:'剧情',v:'剧情'},{n:'历史',v:'历史'},{n:'经典',v:'经典'},{n:'乡村',v:'乡村'},{n:'情景',v:'情景'},{n:'商战',v:'商战'},{n:'网剧',v:'网剧'}]
            },{
                key: 'area',
                name: '地区', 
                value: [{n:'全部',v:''},{n:'中国大陆',v:'中国大陆'},{n:'中国香港',v:'中国香港'},{n:'中国台湾',v:'中国台湾'},{n:'美国',v:'美国'},{n:'韩国',v:'韩国'},{n:'日本',v:'日本'},{n:'泰国',v:'泰国'},{n:'新加坡',v:'新加坡'},{n:'马来西亚',v:'马来西亚'},{n:'印度',v:'印度'},{n:'英国',v:'英国'},{n:'法国',v:'法国'},{n:'加拿大',v:'加拿大'},{n:'西班牙',v:'西班牙'},{n:'俄罗斯',v:'俄罗斯'}]
            },{
                key: 'year',
                name: '年份', 
                value: [{n:'全部',v:''},{n:'2023',v:'2023'},{n:'2022',v:'2022'},{n:'2021',v:'2021'},{n:'2020',v:'2020'},{n:'2019',v:'2019'},{n:'2018',v:'2018'},{n:'2017',v:'2017'},{n:'2016',v:'2016'},{n:'2015',v:'2015'},{n:'2014',v:'2014'},{n:'2013',v:'2013'},{n:'2012',v:'2012'},{n:'2011',v:'2011'},{n:'2010',v:'2010'},{n:'2009',v:'2009'},{n:'2008',v:'2008'},{n:'2007',v:'2007'},{n:'2006',v:'2006'},{n:'2005',v:'2005'},{n:'2004',v:'2004'},{n:'2003',v:'2003'},{n:'2002',v:'2002'},{n:'2001',v:'2001'},{n:'2000',v:'2000'}]
            }],
        '3':[{
            key: 'id',
            name: '类型', 
            value: [{n:'全部',v:''},{n:'内地',v:'25'},{n:'日漫',v:'26'},{n:'欧美',v:'27'},{n:'其他',v:'28'}]
        },{
            key: 'class',
            name: '剧情', 
            value: [{n:'全部',v:''},{n:'情感',v:'情感'},{n:'科幻',v:'科幻'},{n:'热血',v:'热血'},{n:'推理',v:'推理'},{n:'搞笑',v:'搞笑'},{n:'冒险',v:'冒险'},{n:'萝莉',v:'萝莉'},{n:'校园',v:'校园'},{n:'动作',v:'动作'},{n:'机战',v:'机战'},{n:'运动',v:'运动'},{n:'战争',v:'战争'},{n:'少年',v:'少年'},{n:'少女',v:'少女'},{n:'社会',v:'社会'},{n:'原创',v:'原创'},{n:'亲子',v:'亲子'},{n:'益智',v:'益智'},{n:'励志',v:'励志'}]
        },{
            key: 'area',
            name: '地区', 
            value: [{n:'全部',v:''},{n:'中国大陆',v:'中国大陆'},{n:'中国香港',v:'中国香港'},{n:'中国台湾',v:'中国台湾'},{n:'美国',v:'美国'},{n:'韩国',v:'韩国'},{n:'日本',v:'日本'},{n:'泰国',v:'泰国'},{n:'新加坡',v:'新加坡'},{n:'马来西亚',v:'马来西亚'},{n:'印度',v:'印度'},{n:'英国',v:'英国'},{n:'法国',v:'法国'},{n:'加拿大',v:'加拿大'},{n:'西班牙',v:'西班牙'},{n:'俄罗斯',v:'俄罗斯'}]
        },{
            key: 'year',
            name: '年份', 
            value: [{n:'全部',v:''},{n:'2023',v:'2023'},{n:'2022',v:'2022'},{n:'2021',v:'2021'},{n:'2020',v:'2020'},{n:'2019',v:'2019'},{n:'2018',v:'2018'},{n:'2017',v:'2017'},{n:'2016',v:'2016'},{n:'2015',v:'2015'},{n:'2014',v:'2014'},{n:'2013',v:'2013'},{n:'2012',v:'2012'},{n:'2011',v:'2011'},{n:'2010',v:'2010'},{n:'2009',v:'2009'},{n:'2008',v:'2008'},{n:'2007',v:'2007'},{n:'2006',v:'2006'},{n:'2005',v:'2005'},{n:'2004',v:'2004'},{n:'2003',v:'2003'},{n:'2002',v:'2002'},{n:'2001',v:'2001'},{n:'2000',v:'2000'}]
        }]
    }
}

async function getVideos(url) {
    const html = await request(url);
    const $ = load(html);
    const cards = $('div.stui-vodlist__box > a')
    let videos = _.map(cards, (n) => {
        let id = n.attribs['href'];
        let name = n.attribs['title'];
        let pic = n.attribs['data-original'];
        let remark = $($(n).find('span:nth-child(2)')[0]).text();
        return {
            vod_id: id,
            vod_name: name,
            vod_pic: pic,
            vod_remarks: remark,
        };
    });
    return videos;
}

function base64Encode(text) {
    return Crypto.enc.Base64.stringify(Crypto.enc.Utf8.parse(text));
}

function base64Decode(text) {
    return Crypto.enc.Utf8.stringify(Crypto.enc.Base64.parse(text));
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