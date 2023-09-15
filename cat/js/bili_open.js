import { Crypto, jinja2, _ } from 'assets://js/lib/cat.js';

let siteKey = '';
let siteType = 0;

let cookie = '';
let login = '';
let vip = false;
let extendObj = {};
let bili_jct = '';
let vod_audio_id = {
    30280: 192000,
    30232: 132000,
    30216: 64000,
};

let vod_codec = {
    // 13: 'AV1',
    12: 'HEVC',
    7: 'AVC',
};

const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36';

async function request(reqUrl, ua, buffer) {
    let res = await req(reqUrl, {
        method: 'get',
        headers: ua ? ua : { 'User-Agent': UA },
        timeout: 60000,
        buffer: buffer ? 1 : 0,
    });
    return res.content;
}

async function post(reqUrl, postData, ua, posttype) {
    let res = await req(reqUrl, {
        method: 'post',
        headers: ua ? ua : { 'User-Agent': UA },
        data: postData,
        timeout: 60000,
        postType: posttype,
    });
    return res.content;
}

function getHeaders() {
    const headers = {
        'User-Agent': UA,
    };
    if (!_.isEmpty(cookie)) {
        headers.cookie = cookie;
    }
    return headers;
}

async function getCookie() {
    let result = await req('https://www.bilibili.com', {
        method: 'get',
        headers: { 'User-Agent': UA },
        timeout: 60000,
    });
    const setCookieHeaders = result.headers['set-cookie'];
    cookie = setCookieHeaders.map((kk) => kk.split(';')[0] + ';').join('');
}

async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
    let extend = cfg.ext;

    if (cfg.ext.hasOwnProperty('categories')) extend = cfg.ext.categories;
    if (cfg.ext.hasOwnProperty('cookie')) cookie = cfg.ext.cookie;
    // 获取csrf
    const cookies = cookie.split(';');
    cookies.forEach(cookie => {
        if (cookie.includes('bili_jct')) {
            bili_jct = cookie.split('=')[1];
        }
    });

    if (_.isEmpty(cookie)) await getCookie();
    let result = JSON.parse(await request('https://api.bilibili.com/x/web-interface/nav', getHeaders()));
    login = result.data.isLogin;
    vip = result.data.vipStatus;
    const ext = extend.split('#');
    const jsonData = [
        {
            key: 'order',
            name: '排序',
            value: [
                { n: '综合排序', v: '0' },
                { n: '最多点击', v: 'click' },
                { n: '最新发布', v: 'pubdate' },
                { n: '最多弹幕', v: 'dm' },
                { n: '最多收藏', v: 'stow' },
            ],
        },
        {
            key: 'duration',
            name: '时长',
            value: [
                { n: '全部时长', v: '0' },
                { n: '60分钟以上', v: '4' },
                { n: '30~60分钟', v: '3' },
                { n: '10~30分钟', v: '2' },
                { n: '10分钟以下', v: '1' },
            ],
        },
    ];
    const newarr = [];
    const d = {};
    const sc = {
        type_name: "首页",
        type_id: "首页",
        land: 1,
        ratio: 1.33,
    }
    newarr.push(sc);
    for (const kk of ext) {
        const c = {
            type_name: kk,
            type_id: kk,
            land: 1,
            ratio: 1.33,
        };
        newarr.push(c);
        d[kk] = jsonData;
    }
    if (!_.isEmpty(bili_jct)) {
        const hc = {
            type_name: "历史记录",
            type_id: "历史记录",
            land: 1,
            ratio: 1.33,
        }
        newarr.push(hc);
    }
    extendObj = {
        classes: newarr,
        filter: d,
    };
}

function home(filter) {
    try {
        const jSONObject = {
            class: extendObj.classes,
        };
        if (filter) {
            jSONObject.filters = extendObj.filter;
        }
        return JSON.stringify(jSONObject);
    } catch (e) {
        return '';
    }
}

async function homeVod() {
    try {
        const list = [];
        const url = 'https://api.bilibili.com/x/web-interface/index/top/rcmd?ps=14&fresh_idx=1&fresh_idx_1h=1';

        const response = await request(url, getHeaders());
        const responseData = JSON.parse(response);
        const vods = responseData.data.item;

        for (const item of vods) {
            const vod = {};
            let imageUrl = item.pic;
            if (imageUrl.startsWith('//')) {
                imageUrl = 'https:' + imageUrl;
            }
            let cd = getFullTime(item.duration);

            vod.vod_id = item.bvid;
            vod.vod_name = removeTags(item.title);
            vod.vod_pic = imageUrl;
            vod.vod_remarks = cd;
            vod.style = {
                type: 'rect',
                ratio: 1.33,
            },
                list.push(vod);
        }

        const result = { list: list };
        return JSON.stringify(result);
    } catch (e) { }
}

async function category(tid, page, filter, ext) {
    if (page < 1) page = 1;
    try {
        if (Object.keys(ext).length > 0 && ext.hasOwnProperty('tid') && ext['tid'].length > 0) {
            tid = ext['tid'];
        }
        let url = '';
        url = `https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword=${encodeURIComponent(tid)}`;

        if (Object.keys(ext).length > 0) {
            for (const k in ext) {
                if (k == 'tid') {
                    continue;
                }
                url += `&${encodeURIComponent(k)}=${encodeURIComponent(ext[k])}`;
            }
        }

        url += `&page=${encodeURIComponent(page)}`;

        if (tid == "首页") {
            url = "https://api.bilibili.com/x/web-interface/index/top/rcmd?ps=14&fresh_idx=" + page + "&fresh_idx_1h=" + page;
        } else if (tid == "历史记录") {
            url = "https://api.bilibili.com/x/v2/history?pn=" + page;
        }

        const data = JSON.parse(await request(url, getHeaders())).data;
        let items = data.result;
        if (tid == "首页") {
            items = data.item;
        } else if (tid == "历史记录") {
            items = data;
        }

        const videos = [];
        for (const item of items) {
            const video = {};
            let pic = item.pic;
            if (pic.startsWith('//')) {
                pic = 'https:' + pic;
            }
            let cd = getFullTime(item.duration);

            video.vod_remarks = cd;
            video.vod_id = item.bvid;
            video.vod_name = removeTags(item.title);
            video.vod_pic = pic;

            video.style = {
                type: 'rect',
                ratio: 1.33,
            },
                videos.push(video);
        }

        const result = {
            page: page,
            pagecount: data.numPages ?? (page + 1),
            limit: videos.length,
            total: videos.length * (page + 1),
            list: videos,
        };

        return JSON.stringify(result);
    } catch (e) { }
    return null;
}

async function detail(ids) {
    try {
        const bvid = ids;
        const detailUrl = `https://api.bilibili.com/x/web-interface/view?bvid=${bvid}`;

        const detailData = JSON.parse(await request(detailUrl, getHeaders())).data;
        // 记录历史
        if (!_.isEmpty(bili_jct)) {
            const historyReport = 'https://api.bilibili.com/x/v2/history/report';
            let dataPost = {
                aid: detailData.aid,
                cid: detailData.cid,
                csrf: bili_jct,
            }
            await post(historyReport, dataPost, getHeaders(), 'form');
        }
        let cd = getFullTime(detailData.duration);
        const aid = detailData.aid;
        const video = {
            vod_id: bvid,
            vod_name: detailData.title,
            vod_pic: detailData.pic,
            type_name: detailData.tname,
            vod_year: '',
            vod_area: '',
            vod_remarks: cd,
            vod_actor: '',
            vod_director: '',
            vod_content: detailData.desc,
        };

        const playurldata = 'https://api.bilibili.com/x/player/playurl?avid=' + aid + '&cid=' + detailData.cid + '&qn=127&fnval=4048&fourk=1';
        const playurldatas = JSON.parse(await request(playurldata, getHeaders()));

        const playurldatalist = playurldatas.data;
        const accept_quality = playurldatalist.accept_quality;
        const accept_description = playurldatalist.accept_description;
        const qualitylist = [];
        const descriptionList = [];

        for (let i = 0; i < accept_quality.length; i++) {
            if (!vip) {
                if (!login) {
                    if (accept_quality[i] > 32) continue;
                } else {
                    if (accept_quality[i] > 80) continue;
                }
            }
            descriptionList.push(base64Encode(accept_description[i]));
            qualitylist.push(accept_quality[i]);
        }

        let treeMap = {};
        const jSONArray = detailData.pages;
        let playList = [];
        for (let j = 0; j < jSONArray.length; j++) {
            const jSONObject6 = jSONArray[j];
            const cid = jSONObject6.cid;
            const playUrl = j + '$' + aid + '+' + cid + '+' + qualitylist.join(':') + '+' + descriptionList.join(':');
            playList.push(playUrl);
        }
        treeMap['dash'] = playList.join('#');
        treeMap['mp4'] = playList.join('#');

        const relatedUrl = 'https://api.bilibili.com/x/web-interface/archive/related?bvid=' + bvid;
        const relatedData = JSON.parse(await request(relatedUrl, getHeaders())).data;
        playList = [];
        for (let j = 0; j < relatedData.length; j++) {
            const jSONObject6 = relatedData[j];
            const cid = jSONObject6.cid;
            const title = jSONObject6.title;
            const aaid = jSONObject6.aid;
            const playUrl = title + '$' + aaid + '+' + cid + '+' + qualitylist.join(':') + '+' + descriptionList.join(':');
            playList.push(playUrl);
        }
        treeMap['相关'] = playList.join('#');

        video.vod_play_from = Object.keys(treeMap).join("$$$");
        video.vod_play_url = Object.values(treeMap).join("$$$");

        const list = [video];
        const result = { list };
        return JSON.stringify(result);
    } catch (e) { }
    return null;
}

async function play(flag, id, flags) {
    try {
        const playHeaders = { Referer: 'https://www.bilibili.com', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36' };
        const ids = id.split('+');
        const aid = ids[0];
        const cid = ids[1];
        const qualityIds = ids[2].split(':');
        const qualityName = ids[3].split(':');
        const dan = 'https://api.bilibili.com/x/v1/dm/list.so?oid=' + cid;
        if (flag == 'dash' || flag == '相关') {
            // dash mpd 代理
            const js2Base = await js2Proxy(true, siteType, siteKey, 'dash/', {});
            let urls = [];
            for (let i = 0; i < qualityIds.length; i++) {
                urls.push(base64Decode(qualityName[i]), js2Base + base64Encode(aid + '+' + cid + '+' + qualityIds[i]));
            }
            return JSON.stringify({
                parse: 0,
                url: urls,
                danmaku: dan,
                header: playHeaders,
            });
        } else if (flag == 'mp4') {
            // 直链
            let urls = [];
            for (let i = 0; i < qualityIds.length; i++) {
                const url = `https://api.bilibili.com/x/player/playurl?avid=${aid}&cid=${cid}&qn=${qualityIds[i]}&fourk=1`;
                const resp = JSON.parse(await request(url, getHeaders()));
                const data = resp.data;
                if (data.quality != qualityIds[i]) continue;
                let durl = data.durl[0].url;
                urls.push(base64Decode(qualityName[i]), durl);
            }

            return JSON.stringify({
                parse: 0,
                url: urls,
                danmaku: dan,
                header: playHeaders,
            });
        } else {
            // 音频外挂
            let urls = [];
            let audios = [];
            for (let i = 0; i < qualityIds.length; i++) {
                const url = `https://api.bilibili.com/x/player/playurl?avid=${aid}&cid=${cid}&qn=${qualityIds[i]}&fnval=4048&fourk=1`;
                let resp = JSON.parse(await request(url, getHeaders()));
                const dash = resp.data.dash;
                const video = dash.video;
                const audio = dash.audio;
                for (let j = 0; j < video.length; j++) {
                    const dashjson = video[j];
                    if (dashjson.id == qualityIds[i]) {
                        for (const key in vod_codec) {
                            if (dashjson.codecid == key) {
                                urls.push(base64Decode(qualityName[i]) + ' ' + vod_codec[key], dashjson.baseUrl);
                            }
                        }
                    }
                }
                if (audios.length == 0) {
                    for (let j = 0; j < audio.length; j++) {
                        const dashjson = audio[j];
                        for (const key in vod_audio_id) {
                            if (dashjson.id == key) {
                                audios.push({
                                    title: _.floor(parseInt(vod_audio_id[key]) / 1024) + 'Kbps',
                                    bit: vod_audio_id[key],
                                    url: dashjson.baseUrl,
                                });
                            }
                        }
                    }
                    audios = _.sortBy(audios, 'bit');
                }
            }

            return JSON.stringify({
                parse: 0,
                url: urls,
                extra: {
                    audio: audios,
                },
                header: playHeaders,
            });
        }
    } catch (e) { }
    return null;
}

async function search(key, quick, pg) {
    let page = pg || 1;
    if (page == 0) page = 1;
    try {
        const ext = {
            duration: '0',
        };
        let resp = JSON.parse(await category(key, page, true, ext));
        const catVideos = resp.list;
        const pageCount = resp.pagecount;
        const videos = [];
        for (let i = 0; i < catVideos.length; ++i) {
            videos.push(catVideos[i]);
        }
        const result = {
            page: page,
            pagecount: pageCount,
            land: 1,
            ratio: 1.33,
            list: videos,
        };
        return JSON.stringify(result);
    } catch (e) { }
    return null;
}

async function proxy(segments, headers) {
    let what = segments[0];
    let url = base64Decode(segments[1]);
    if (what == 'dash') {
        const ids = url.split('+');
        const aid = ids[0];
        const cid = ids[1];
        const str5 = ids[2];
        const urls = `https://api.bilibili.com/x/player/playurl?avid=${aid}&cid=${cid}&qn=${str5}&fnval=4048&fourk=1`;
        let videoList = '';
        let audioList = '';

        let resp = JSON.parse(await request(urls, getHeaders()));
        const dash = resp.data.dash;
        const video = dash.video;
        const audio = dash.audio;

        for (let i = 0; i < video.length; i++) {
            // if (i > 0) continue; // 只取一个
            const dashjson = video[i];
            if (dashjson.id == str5) {
                videoList += getDashMedia(dashjson);
            }
        }

        for (let i = 0; i < audio.length; i++) {
            // if (i > 0) continue;
            const ajson = audio[i];
            for (const key in vod_audio_id) {
                if (ajson.id == key) {
                    audioList += getDashMedia(ajson);
                }
            }
        }

        let mpd = getDash(resp, videoList, audioList);

        return JSON.stringify({
            code: 200,
            content: mpd,
            headers: {
                'Content-Type': 'application/dash+xml',
            },
        });
    }
    return JSON.stringify({
        code: 500,
        content: '',
    });
}

function getDashMedia(dash) {
    try {
        let qnid = dash.id;
        const codecid = dash.codecid;
        const media_codecs = dash.codecs;
        const media_bandwidth = dash.bandwidth;
        const media_startWithSAP = dash.startWithSap;
        const media_mimeType = dash.mimeType;
        const media_BaseURL = dash.baseUrl.replace(/&/g, '&amp;');
        const media_SegmentBase_indexRange = dash.SegmentBase.indexRange;
        const media_SegmentBase_Initialization = dash.SegmentBase.Initialization;
        const mediaType = media_mimeType.split('/')[0];
        let media_type_params = '';

        if (mediaType == 'video') {
            const media_frameRate = dash.frameRate;
            const media_sar = dash.sar;
            const media_width = dash.width;
            const media_height = dash.height;
            media_type_params = `height='${media_height}' width='${media_width}' frameRate='${media_frameRate}' sar='${media_sar}'`;
        } else if (mediaType == 'audio') {
            for (const key in vod_audio_id) {
                if (qnid == key) {
                    const audioSamplingRate = vod_audio_id[key];
                    media_type_params = `numChannels='2' sampleRate='${audioSamplingRate}'`;
                }
            }
        }
        qnid += '_' + codecid;

        return `<AdaptationSet lang="chi">
        <ContentComponent contentType="${mediaType}"/>
        <Representation id="${qnid}" bandwidth="${media_bandwidth}" codecs="${media_codecs}" mimeType="${media_mimeType}" ${media_type_params} startWithSAP="${media_startWithSAP}">
          <BaseURL>${media_BaseURL}</BaseURL>
          <SegmentBase indexRange="${media_SegmentBase_indexRange}">
            <Initialization range="${media_SegmentBase_Initialization}"/>
          </SegmentBase>
        </Representation>
      </AdaptationSet>`;
    } catch (e) {
        // Handle exceptions here
    }
}

function getDash(ja, videoList, audioList) {
    const duration = ja.data.dash.duration;
    const minBufferTime = ja.data.dash.minBufferTime;
    return `<MPD xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:mpeg:dash:schema:mpd:2011" xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd" type="static" mediaPresentationDuration="PT${duration}S" minBufferTime="PT${minBufferTime}S" profiles="urn:mpeg:dash:profile:isoff-on-demand:2011">
      <Period duration="PT${duration}S" start="PT0S">
        ${videoList}
        ${audioList}
      </Period>
    </MPD>`;
}


function base64Encode(text) {
    return Crypto.enc.Base64.stringify(Crypto.enc.Utf8.parse(text));
}

function base64Decode(text) {
    return Crypto.enc.Utf8.stringify(Crypto.enc.Base64.parse(text));
}



function removeTags(input) {
    return input.replace(/<[^>]*>/g, '');
}

function getFullTime(numberSec) {
    let totalSeconds = '';
    try {
        var timeParts = numberSec.split(":");
        var min = parseInt(timeParts[0]);
        var sec = parseInt(timeParts[1]);  
        totalSeconds = min * 60 + sec;        
    } catch (e) {
        totalSeconds = parseInt(numberSec);
    }
    if (isNaN(totalSeconds)) {
        return '无效输入';
    }
    if (totalSeconds >= 3600) {
        const hours = Math.floor(totalSeconds / 3600);
        const remainingSecondsAfterHours = totalSeconds % 3600;
        const minutes = Math.floor(remainingSecondsAfterHours / 60);
        const seconds = remainingSecondsAfterHours % 60;
        return `${hours}小时 ${minutes}分钟 ${seconds}秒`;
    } else {
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        return `${minutes}分钟 ${seconds}秒`;
    }
}

export function __jsEvalReturn() {
    return {
        init: init,
        home: home,
        homeVod: homeVod,
        category: category,
        detail: detail,
        play: play,
        proxy: proxy,
        search: search,
    };
}

