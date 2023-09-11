import { Crypto, dayjs, jinja2, _ } from './lib/cat.js';

let key = 'kkys';
let url = 'https://api1.baibaipei.com:8899';
let device = {};
let siteKey = '';
let siteType = 0;

async function request(reqUrl, postData, agentSp, get) {
    let ts = dayjs().valueOf().toString();
    let rand = randStr(32);
    let sign = Crypto.MD5('abcdexxxdd2daklmn25129_' + ts + '_' + rand)
        .toString()
        .toLowerCase();
    let headers = {
        'user-agent': agentSp || device.ua,
    };
    if (reqUrl.includes('baibaipei')) {
        headers['device-id'] = device.id;
        headers['push-token'] = '';
        headers['sign'] = sign;
        headers['time'] = ts;
        headers['md5'] = rand;
        headers['version'] = '2.1.0';
        headers['system-model'] = device.model;
        headers['system-brand'] = device.brand;
        headers['system-version'] = device.release;
    }
    let res = await req(reqUrl, {
        method: get ? 'get' : 'post',
        headers: headers,
        data: postData || {},
        postType: get ? '' : 'form',
    });

    let content = res.content;
    // console.log(content);
    return content;
}

async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
    var deviceKey = 'device';
    var deviceInfo = await local.get(key, deviceKey);
    if (deviceInfo.length > 0) {
        try {
            device = JSON.parse(deviceInfo);
        } catch (error) {}
    }
    if (_.isEmpty(device)) {
        device = randDevice();
        device.id = randStr(33).toLowerCase();
        device.ua = 'okhttp/4.1.0';
        await local.set(key, deviceKey, JSON.stringify(device));
    }
}

async function home(filter) {
    // await req('https://www.facebook.com', {});
    let data = JSON.parse(await request(url + '/api.php/Index/getTopVideoCategory')).data;
    let classes = [];
    let filterObj = {};
    for (const type of data) {
        let typeName = type.nav_name;
        if (typeName == '推荐') continue;
        let typeId = type.nav_type_id.toString();
        classes.push({
            type_id: typeId,
            type_name: typeName,
        });
        if (!filter) continue;
        try {
            let filterAll = [];
            let filterData = JSON.parse(await request(url + '/api.php/Video/getFilterType', { type: typeId })).data;
            for (let key of Object.keys(filterData)) {
                let itemValues = filterData[key];
                if (key === 'plot') key = 'class';
                let typeExtendName = '';
                switch (key) {
                    case 'class':
                        typeExtendName = '类型';
                        break;
                    case 'area':
                        typeExtendName = '地区';
                        break;
                    case 'lang':
                        typeExtendName = '语言';
                        break;
                    case 'year':
                        typeExtendName = '年代';
                        break;
                    case 'sort':
                        typeExtendName = '排序';
                        break;
                }
                if (typeExtendName.length === 0) continue;
                let newTypeExtend = {
                    key: key,
                    name: typeExtendName,
                };
                let newTypeExtendKV = [];
                for (let j = 0; j < itemValues.length; j++) {
                    const name = itemValues[j];
                    let value = key === 'sort' ? j + '' : name === '全部' ? '0' : name;
                    newTypeExtendKV.push({ n: name, v: value });
                }
                newTypeExtend['init'] = key === 'sort' ? '1' : newTypeExtendKV[0]['v'];
                newTypeExtend.value = newTypeExtendKV;
                filterAll.push(newTypeExtend);
            }
            if (!_.isEmpty(filterAll)) {
                filterObj[typeId] = filterAll;
            }
        } catch (e) {
            console.log(e);
        }
    }
    // console.log(await homeVod());
    // console.log(classes);
    // console.log(filterObj);
    return JSON.stringify({
        class: classes,
        filters: filterObj,
    });
}

async function homeVod() {
    let jsonArray = JSON.parse(await request(url + '/api.php/Index/getHomePage', { type: 1, p: 1 })).data.video;
    let videos = [];
    for (const item of jsonArray) {
        if (item.title.styleType !== 0) continue;
        for (const vObj of item.list) {
            videos.push({
                vod_id: vObj.vod_id,
                vod_name: vObj.vod_name,
                vod_pic: vObj.vod_pic,
                vod_remarks: vObj.vod_remarks || vObj.vod_score || '',
            });
        }
    }
    return JSON.stringify({
        list: videos,
    });
}

async function category(tid, pg, filter, extend) {
    if (pg == 0) pg = 1;
    let reqUrl = url + '/api.php/Video/getFilterVideoList';
    var formData = JSON.parse(
        jinja2(
            `{
        "type": "{{tid}}",
        "p": "{{pg}}",
        "area": "{{ext.area|default(0)}}",
        "year": "{{ext.year|default(0)}}",
        "sort": "{{ext.sort|default(0)}}",
        "class": "{{ext.class|default(0)}}"
    }`,
            { ext: extend, tid: tid, pg: pg }
        )
    );
    console.log(formData);
    let data = JSON.parse(await request(reqUrl, formData)).data;
    let videos = [];
    for (const vod of data.data) {
        videos.push({
            vod_id: vod.vod_id,
            vod_name: vod.vod_name,
            vod_pic: vod.vod_pic,
            vod_remarks: vod.vod_remarks || vod.vod_score || '',
        });
    }
    return JSON.stringify({
        page: parseInt(data.current_page),
        pagecount: parseInt(data.last_page),
        limit: parseInt(data.per_page),
        total: parseInt(data.total),
        list: videos,
    });
}

async function detail(id) {
    let data = JSON.parse(await request(url + '/api.php/Video/getVideoInfo', { video_id: id })).data.video;
    let vod = {
        vod_id: data.vod_id,
        vod_name: data.vod_name,
        vod_pic: data.vod_pic,
        type_name: data.vod_class,
        vod_year: data.vod_year,
        vod_area: data.vod_area,
        vod_remarks: data.vod_remarks || '',
        vod_actor: data.vod_actor,
        vod_director: data.vod_director,
        vod_content: data.vod_content.trim(),
    };
    let playlist = {};
    for (const item of data.vod_play) {
        let from = item.playerForm;
        if (from === 'jp') continue;
        if (from === 'xg') continue;
        let urls = [];
        for (const u of item.url) {
            urls.push(formatPlayUrl(vod.vod_name, u.title) + '$' + u.play_url);
        }
        if (!playlist.hasOwnProperty(from) && urls.length > 0) {
            playlist[from] = urls;
        }
    }
    parse = data.parse || [];
    vod.vod_play_from = _.keys(playlist).join('$$$');
    let urls = _.values(playlist);
    let vod_play_url = [];
    for (const urlist of urls) {
        vod_play_url.push(urlist.join('#'));
    }
    vod.vod_play_url = vod_play_url.join('$$$');
    return JSON.stringify({
        list: [vod],
    });
}

var parse = [];

async function play(flag, id, flags) {
    try {
        if (id.indexOf('youku') >= 0 || id.indexOf('iqiyi') >= 0 || id.indexOf('v.qq.com') >= 0 || id.indexOf('pptv') >= 0 || id.indexOf('le.com') >= 0 || id.indexOf('1905.com') >= 0 || id.indexOf('mgtv') >= 0) {
            if (parse.length > 0) {
                for (let index = 0; index < parse.length; index++) {
                    try {
                        const p = parse[index];
                        let res = await req(p + id, {
                            headers: { 'user-agent': 'okhttp/4.1.0' },
                        });
                        var result = jsonParse(id, JSON.parse(res.content));
                        if (result.url) {
                            result.parse = 0;
                            return JSON.stringify(result);
                        }
                    } catch (error) {}
                }
            }
        }
        if (id.indexOf('jqq-') >= 0) {
            var jqqHeader = await request(url + '/jqqheader.json', null, null, true);
            var jqqHeaders = JSON.parse(jqqHeader);
            var ids = id.split('-');
            var jxJqq = await req('https://api.juquanquanapp.com/app/drama/detail?dramaId=' + ids[1] + '&episodeSid=' + ids[2] + '&quality=LD', { headers: jqqHeaders });
            var jqqInfo = JSON.parse(jxJqq.content);
            if (jqqInfo.data.playInfo.url) {
                return JSON.stringify({
                    parse: 0,
                    playUrl: '',
                    url: jqqInfo.data.playInfo.url,
                });
            }
        }
        let res = await request(url + '/video.php', { url: id });
        var result = jsonParse(id, JSON.parse(res).data);
        if (result.url) {
            result.parse = 0;
            return JSON.stringify(result);
        }
        return JSON.stringify({
            parse: 0,
            playUrl: '',
            url: id,
        });
    } catch (e) {
        console.log(e);
        return JSON.stringify({
            parse: 0,
            url: id,
        });
    }
}

async function search(wd, quick) {
    let data = JSON.parse(await request(url + '/api.php/Search/getSearch', { key: wd, type_id: 0, p: 1 })).data;
    let videos = [];
    for (const vod of data.data) {
        videos.push({
            vod_id: vod.vod_id,
            vod_name: vod.vod_name,
            vod_pic: vod.vod_pic,
            vod_remarks: vod.vod_remarks || vod.vod_score || '',
        });
    }
    return JSON.stringify({
        list: videos,
    });
}

const charStr = 'abacdefghjklmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ0123456789';
function randStr(len, withNum) {
    var _str = '';
    let containsNum = withNum === undefined ? true : withNum;
    for (var i = 0; i < len; i++) {
        let idx = _.random(0, containsNum ? charStr.length - 1 : charStr.length - 11);
        _str += charStr[idx];
    }
    return _str;
}

function randDevice() {
    return {
        brand: 'Huawei',
        model: 'HUAWEI Mate 20',
        release: '10',
        buildId: randStr(3, false).toUpperCase() + _.random(11, 99) + randStr(1, false).toUpperCase(),
    };
}

function formatPlayUrl(src, name) {
    return name
        .trim()
        .replaceAll(src, '')
        .replace(/<|>|《|》/g, '')
        .replace(/\$|#/g, ' ')
        .trim();
}

function jsonParse(input, json) {
    try {
        let url = json.url ?? '';
        if (url.startsWith('//')) {
            url = 'https:' + url;
        }
        if (!url.startsWith('http')) {
            return {};
        }
        let headers = json['headers'] || {};
        let ua = (json['user-agent'] || '').trim();
        if (ua.length > 0) {
            headers['User-Agent'] = ua;
        }
        let referer = (json['referer'] || '').trim();
        if (referer.length > 0) {
            headers['Referer'] = referer;
        }
        _.keys(headers).forEach((hk) => {
            if (!headers[hk]) delete headers[hk];
        });
        return {
            header: headers,
            url: url,
        };
    } catch (error) {
        console.log(error);
    }
    return {};
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