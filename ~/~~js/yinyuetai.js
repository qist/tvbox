import { Crypto, load, _ } from './lib/cat.js';

let siteKey = '';
let siteType = 0;
let headers = {
	'Vi': '1.0.0;11;101',
	'Wua': 'YYT/1.0.0 (WEB;web;11;zh-CN;OUN7HHDoKgoDlMN3Z2oQH)',
};
async function request(reqUrl, postData, get) {
    let res = await req(reqUrl, {
        method: get ? 'get' : 'post',
        headers: headers,
        data: postData || {},
    });
    let content = res.content;
    return content;
}

async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
}

async function home(filter) {
	let st = Math.floor(Date.now() / 1e3);
	let pp = Ea('st' + st);
	let url ='https://video-api.yinyuetai.com/video/explore/channels';
	let res = JSON.parse((await req(url, {
		'method': 'get',
		'headers': {
			'Vi': '1.0.0;11;101',
			'Wua': 'YYT/1.0.0 (WEB;web;11;zh-CN;OUN7HHDoKgoDlMN3Z2oQH)',
			'St': st,
			'Pp': pp
		}
	})).content);
	//console.log(res);
	const classes = _.map(res.data, n => {
		return {
			type_id: n.id,
			type_name: n.channelName,
		}
	});
   
    return JSON.stringify({
        class: classes,
    });
}

async function homeVod() {
    
}

async function category(tid, pg, filter, extend) {
	if(!pg || pg <=0) pg = 1;
	`https://video-api.yinyuetai.com/video/explore/channelVideos?channelId=${tid}&detailType=2&size=20&offset=${20 * (pg-1)}`
	let url = `https://video-api.yinyuetai.com/video/explore/channelVideos?channelId=${tid}&detailType=2&size=20&offset=${20 * (pg-1)}`;
    let st = Math.floor(Date.now() / 1e3);
	let d = `channelId${tid}detailType2offset${20 * (pg-1)}size20st${st}`
	//console.log(d);
	let pp = Ea(d);
    let res = JSON.parse((await req(url, {
		'method': 'get',
		'headers': {
			'Vi': '1.0.0;11;101',
			'Wua': 'YYT/1.0.0 (WEB;web;11;zh-CN;OUN7HHDoKgoDlMN3Z2oQH)',
			'St': st,
			'Pp': pp
		}
	})).content);
	let videos = _.map(res.data, n => {
		return {
			vod_id: n.fullClip.videoId,
			vod_name: n.title,
			vod_pic: n.headImg,
		}
	});
    return JSON.stringify({
        list: videos,
        page: pg,
        limit: 20,
    });
}

async function detail(id) {
	let url = 'https://video-api.yinyuetai.com/video/get?id=' + id;
    try {
		let res = JSON.parse((await req(url, {
		'method': 'get',
	})).content).data;
        let vod = {
            vod_id: id,
            vod_name: res.title,
            vod_play_from: _.map(res.fullClip.urls, n => {return n.display}).join('$$$'),
			vod_play_url: _.map(res.fullClip.urls, n => {return '播放$' + n.url}).join('$$$'),
            vod_content: '关注公众号“东方精英汇”，获取最新接口，加qq群783264601防迷失！【东辰影视】提醒您：该资源来源于网络，请勿传播，仅供技术学习使用，请在学习后24小时内删除！',
        };
        return JSON.stringify({
            list: [vod],
        });
    } catch (e) {
       console.log('err', e);
    }
    return null;
}

async function search(wd, quick, pg) {
	let url = 'https://search-api.yinyuetai.com/search/get_search_result.json';
	let params = {
		searchType: 'MV',
		key: wd,
		sinceId: 0,
		size: 20,
		requestTagRows: [],
	}
	let res = JSON.parse((await req(url, {
		'method': 'post',
		'headers': {
			'Content-Type':'application/json'
		},
		'data': params,
	})).content);
	let videos = _.map(res.data, n => {
		return {
			vod_id: n.fullClip.videoId,
			vod_name: n.title,
			vod_pic: n.headImg,
		}
	});

    return JSON.stringify({
        list: videos,
    });
}

async function play(flag, id, flags) {
    return JSON.stringify({
        parse: 0,
        url: id
    });
}

function base64Encode(text) {
    return Crypto.enc.Base64.stringify(Crypto.enc.Utf8.parse(text));
}

function base64Decode(text) {
    return Crypto.enc.Utf8.stringify(Crypto.enc.Base64.parse(text));
}

function base64ToHex(str) {
    for (var i = 0,
             bin = base64Decode(str.replace(/[ \r\n]+$/, "")), hex = []; i < bin.length; ++i) {
        var tmp = bin.charCodeAt(i).toString(16);
        if (tmp.length === 1) tmp = "0" + tmp;
        hex[hex.length] = tmp;
    }
    return hex.join("");
}

function Ea(e) {
    const t = e + "91fd6ee712437d42eeccdf545133039888d1cc77";
    return o(t);
}

function o(a, i) {
	var s = wordsToBytes(n(a));
	return i && i.asBytes ? s : i && i.asString ? bytesToString(s) : bytesToHex(s)
};
	
function n(a) {
	a = stringToBytes(a);
	var i = bytesToWords(a)
	  , s = a.length * 8
	  , l = []
	  , c = 1732584193
	  , u = -271733879
	  , p = -1732584194
	  , f = 271733878
	  , d = -1009589776;
	i[s >> 5] |= 128 << 24 - s % 32,
	i[(s + 64 >>> 9 << 4) + 15] = s;
	for (var v = 0; v < i.length; v += 16) {
		for (var y = c, S = u, g = p, C = f, A = d, w = 0; w < 80; w++) {
			if (w < 16)
				l[w] = i[v + w];
			else {
				var T = l[w - 3] ^ l[w - 8] ^ l[w - 14] ^ l[w - 16];
				l[w] = T << 1 | T >>> 31
			}
			var U = (c << 5 | c >>> 27) + d + (l[w] >>> 0) + (w < 20 ? (u & p | ~u & f) + 1518500249 : w < 40 ? (u ^ p ^ f) + 1859775393 : w < 60 ? (u & p | u & f | p & f) - 1894007588 : (u ^ p ^ f) - 899497514);
			d = f,
			f = p,
			p = u << 30 | u >>> 2,
			u = c,
			c = U
		}
		c += y,
		u += S,
		p += g,
		f += C,
		d += A
	}
	return [c, u, p, f, d]
}

function stringToBytes(e) {
	for (var t = [], r = 0; r < e.length; r++)
		t.push(e.charCodeAt(r) & 255);
	return t
}

function bytesToString(e) {
	for (var t = [], r = 0; r < e.length; r++)
		t.push(String.fromCharCode(e[r]));
	return t.join("")
}

function bytesToWords(r) {
	for (var n = [], o = 0, a = 0; o < r.length; o++,
	a += 8)
		n[a >>> 5] |= r[o] << 24 - a % 32;
	return n
}
function wordsToBytes(r) {
	for (var n = [], o = 0; o < r.length * 32; o += 8)
		n.push(r[o >>> 5] >>> 24 - o % 32 & 255);
	return n
}
function bytesToHex(r) {
	for (var n = [], o = 0; o < r.length; o++)
		n.push((r[o] >>> 4).toString(16)),
		n.push((r[o] & 15).toString(16));
	return n.join("")
}
function hexToBytes(r) {
	for (var n = [], o = 0; o < r.length; o += 2)
		n.push(parseInt(r.substr(o, 2), 16));
	return n
}
function bytesToBase64(r) {
	for (var n = [], o = 0; o < r.length; o += 3)
		for (var a = r[o] << 16 | r[o + 1] << 8 | r[o + 2], i = 0; i < 4; i++)
			o * 8 + i * 6 <= r.length * 8 ? n.push(e.charAt(a >>> 6 * (3 - i) & 63)) : n.push("=");
	return n.join("")
}
function base64ToBytes(r) {
	r = r.replace(/[^A-Z0-9+\/]/ig, "");
	for (var n = [], o = 0, a = 0; o < r.length; a = ++o % 4)
		a != 0 && n.push((e.indexOf(r.charAt(o - 1)) & Math.pow(2, -2 * a + 8) - 1) << a * 2 | e.indexOf(r.charAt(o)) >>> 6 - a * 2);
	return n
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