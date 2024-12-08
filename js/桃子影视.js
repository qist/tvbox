import {load} from 'cheerio';
import CryptoJS from 'crypto-js';
import axios from "axios";


let url = 'https://www.taozi007.com';

global = {
    location: true,
    navigator: {
        webdriver: false
    }
};

var oooo = 992212, ooe;
if (oooo = oooo >> 12 ^ 213, ooe = global.location && global.navigator.webdriver) {
    var i = 9;
    for (oooo = oooo ^ i; i < oooo | 9; i > 0) {
        ooe.href = ooe.href + "?" + i;
    }
}

function b(input) {
    return btoa(input);
}

function x(input, _0x56ee7b) {
    let output = "";
    var _0x56ee7b = _0x56ee7b + "PTNo2n3Ev5";
    for (let _0x4e905d = 0; _0x4e905d < input.length; _0x4e905d++) {
        const charCode = input.charCodeAt(_0x4e905d) ^ _0x56ee7b.charCodeAt(_0x4e905d % _0x56ee7b.length);
        output += String.fromCharCode(charCode);
    }
    return output;
}

function setRet(_0x132031) {
    var _0x1db96b = _0x132031.substr(0, 8);
    var _0x6339b6 = parseInt(_0x132031.substr(12));
    typeof global === "undefined" && (_0x6339b6 = 2);
    var _0x56549e = _0x6339b6 * 2 + 18 - 2;
    var encrypted = x(_0x56549e.toString(), _0x1db96b);
    var guard_encrypted = encrypted.toString();
    return "guardret=" + b(guard_encrypted);
}
async function setcookie() {
    let res = await axios({url:url});
    let guard = res.headers['set-cookie'][0].replace(/;.*/, "");
    let ret = setRet(guard.replace("guard=", ""))
    let resp = await axios({url:url ,
        headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
            'Cookie': `${guard}; ${ret}`
        }
    });
    return resp.headers['set-cookie'][0];
}
let cookie = ''

async function init(inReq, _outResp) {
    cookie = await setcookie();
    return {};
}

async function request(reqUrl,headers) {
        let resp = await axios({url:reqUrl ,
            headers: headers===undefined?{
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
                'Cookie': cookie
            }:headers
        });
        return resp.data;

}

async function home(inReq, _outResp) {
    let classes = [{
        type_id: '1',
        type_name: '电影',
    },{
        type_id: '2',
        type_name: '剧集',
    },{
        type_id: '3',
        type_name: '动漫',
    },{
        type_id: '4',
        type_name: '综艺',
    },{
        type_id: '5',
        type_name: '短剧',
    }];
    return JSON.stringify({
        class: classes,
    });
}


async function category(inReq, _outResp) {
    const tid = inReq.body.id;
    let pg = inReq.body.page;
    if (pg <= 0) pg = 1;
    const html = await request(`${url}/show/${tid}--------${pg}---.html`);
    let videos = [];
    const $ = load(html)
    for (const it of $('div.content .module-item')) {
        const img = $(it).find('.module-item-pic img')[0]
        videos.push({
            vod_id: it.attribs.href,
            vod_name: it.attribs.title,
            vod_pic: img.attribs['data-original'],
        })
    }

    const hasMore = $('.page > a:contains(下一页)').length > 0;
    const pgCount = hasMore ? parseInt(pg) + 1 : parseInt(pg);
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: 24,
        total: 24 * pgCount,
        list: videos,
    });
}

async function detail(inReq, _outResp) {
    const id = inReq.body.id;
    const html = await request(`${url}${id}`);
    const $ =load(html)
    var vod = {
        vod_id: id,
        vod_name: $('h1').text().trim(),
        vod_pic: $('div.module-item-pic img')[0].attribs['data-original'],
        vod_content:$('div.module-info-introduction-content p').text(),
        vod_remarks:$('div.module-info-item-content')[2].children[0].data
    };
    let playlist=$('div.module-play-list-content')
    let tabs = $('div.module-tab-item:gt(0) span')
    let playmap={};
    tabs.each((i,tab)=>{
        const form = tab.children[0].data
        const list = playlist[i]
        const a = $(list).find('a')
        a.each((i,it)=>{
            let title =it.children[0].children[0].data;
            let urls = it.attribs.href;
            if(!playmap.hasOwnProperty(form)){
                playmap[form]=[];
            }
            playmap[form].push(title+"$"+urls);
        });
    });

    vod.vod_play_from = Object.keys(playmap).join('$$$');
    const urls = Object.values(playmap);
    const playUrls=urls.map((urllist)=>{
        return urllist.join("#")
    });
    vod.vod_play_url = playUrls.join('$$$');
    return JSON.stringify({
        list: [vod],
    });
}

function decryptVideoUrl(encryptedUrl, uid) {
    const key = CryptoJS.enc.Utf8.parse('2890' + uid + 'tB959C');
    const iv = CryptoJS.enc.Utf8.parse('2F131BE91247866E');
    const decrypted = CryptoJS.AES.decrypt(encryptedUrl, key, {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
    });
    return CryptoJS.enc.Utf8.stringify(decrypted);
}

function js_decrypt(str, key, iv) {
    var keydata = CryptoJS.enc.Utf8.parse(key);
    var ivdata = CryptoJS.enc.Utf8.parse(iv);
    var decrypted_data = CryptoJS.AES.decrypt(str, keydata, {
        iv: ivdata,
        padding: CryptoJS.pad.Pkcs7
    }).toString(CryptoJS.enc.Utf8);
    return decrypted_data
}

async function play(inReq, _outResp) {
    const id = inReq.body.id;
    const html = await request(url+id);
    const $ = load(html);
    const js = JSON.parse($('script:contains(player_)').html().replace('var player_aaaa=', ''));
    if (js.encrypt === '1') {
        url = unescape(js.url);
        return JSON.stringify({
            parse: 0,
            url: url,
        });
    } else if (js.encrypt === '2') {
        url = unescape(atob(js.url));
        return JSON.stringify({
            parse: 0,
            url: url,
        });
    }
    if(/feidaozy|1080zyk|subm3u8/.test(js.from)){
        return JSON.stringify({
            parse: 0,
            url: js.url,
        });
    }else if (/qiyi|qq|youku|mgtv|ffm3u8|heimuer/.test(js.from)){
        let api="https://jx.taozi007.com/player/ec.php?code=tz&if=1&url="
        let req=await request(api+ js.url,{
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
        })
        let config={};
        let link =req.match(/let ConFig.*}/)[0]
        eval(link + '\nconfig=ConFig');
        let video = decryptVideoUrl(config.url,config.config.uid)
        return JSON.stringify({
            parse: 0,
            url: video,
            header:{
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
            }
        });
    } else if (/ty/.test(js.from)){
        let api = 'https://www.taozi007.com/player/?url='+js.url;
        let reqty=await request(api)
        let rand= reqty.match(/var rand = "(.*?)";/)[1];
        let player= reqty.match(/var player = "(.*?)";/)[1];
        const ur = JSON.parse(js_decrypt(player, 'VFBTzdujpR9FWBhe', rand)).url;
        if(ur.startsWith('https')){
            return JSON.stringify({
                parse: 0,
                url: ur,
            });
        }else {
            return JSON.stringify({
                parse: 0,
                url: 'https://m.m3u8.cloud'+ur,
            });
        }
    }else if(/yy/.test(js.from)){
        let api = 'https://www.taozi007.com/player/?url='+js.url;
        let content = await request(api)
        const $ = load(content)
        const src = $('#myiframe').attr('src').split('=')[1]
        return JSON.stringify({
            parse: 0,
            url: src,
        });

    }

}


async function search(inReq, _outResp) {
    const wd = inReq.body.wd;
    let html = await request(`${url}/dm/search/q-${wd}`);
    const $ = load(html);
    let videos = [];
    for (const item of $('.stui-vodlist__box')) {
        const a = $(item).find('a')[0];
        videos.push({
            vod_id: a.attribs.href,
            vod_name: a.attribs.title,
            vod_pic: a.attribs['data-echo-background']
        });
    }
    return JSON.stringify({
        list: videos,
    });
}

async function test(inReq, outResp) {
    try {
        const printErr = function (json) {
            if (json.statusCode && json.statusCode === 500) {
                console.error(json);
            }
        };
        const prefix = inReq.server.prefix;
        const dataResult = {};
        let resp = await inReq.server.inject().post(`${prefix}/init`);
        dataResult.init = resp.json();
        printErr(resp.json());
        resp = await inReq.server.inject().post(`${prefix}/home`);
        dataResult.home = resp.json();
        printErr(resp.json());
        if (dataResult.home.class.length > 0) {
            resp = await inReq.server.inject().post(`${prefix}/category`).payload({
                id: dataResult.home.class[0].type_id,
                page: 1,
                filter: true,
                filters: {},
            });
            dataResult.category = resp.json();
            printErr(resp.json());
            if (dataResult.category.list.length > 0) {
                resp = await inReq.server.inject().post(`${prefix}/detail`).payload({
                    id: dataResult.category.list[0].vod_id, // dataResult.category.list.map((v) => v.vod_id),
                });
                dataResult.detail = resp.json();
                printErr(resp.json());
                if (dataResult.detail.list && dataResult.detail.list.length > 0) {
                    dataResult.play = [];
                    for (const vod of dataResult.detail.list) {
                        const flags = vod.vod_play_from.split('$$$');
                        const ids = vod.vod_play_url.split('$$$');
                        for (let j = 0; j < flags.length; j++) {
                            const flag = flags[j];
                            const urls = ids[j].split('#');
                            for (let i = 0; i < urls.length && i < 2; i++) {
                                resp = await inReq.server
                                    .inject()
                                    .post(`${prefix}/play`)
                                    .payload({
                                        flag: flag,
                                        id: urls[i].split('$')[1],
                                    });
                                dataResult.play.push(resp.json());
                            }
                        }
                    }
                }
            }
        }
        resp = await inReq.server.inject().post(`${prefix}/search`).payload({
            wd: '爱',
            page: 1,
        });
        dataResult.search = resp.json();
        printErr(resp.json());
        return dataResult;
    } catch (err) {
        console.error(err);
        outResp.code(500);
        return {err: err.message, tip: 'check debug console output'};
    }
}

export default {
    meta: {
        key: 'tao',
        name: '桃子影视',
        type: 3,
    },
    api: async (fastify) => {
        fastify.post('/init', init);
        fastify.post('/home', home);
        fastify.post('/category', category);
        fastify.post('/detail', detail);
        fastify.post('/play', play);
        fastify.post('/search', search);
        fastify.get('/test', test);
    },
};