import { Crypto, _ } from 'assets://js/lib/cat.js'

let host = '';
let header = {
    'User-Agent': 'okhttp/3.12.11'
};
let siteKey = '';
let siteType = '';
let siteJx = '';

const urlPattern1 = /api\.php\/.*?\/vod/;
const urlPattern2 = /api\.php\/.+?\.vod/;
const parsePattern = /\/.+\\?.+=/;
const parsePattern1 = /.*(url|v|vid|php\?id)=/;
const parsePattern2 = /https?:\/\/[^\/]*/;

const htmlVideoKeyMatch = [
    /player=new/,
    /<div id="video"/,
    /<div id="[^"]*?player"/,
    /\/\/视频链接/,
    /HlsJsPlayer\(/,
    /<iframe[\s\S]*?src="[^"]+?"/,
    /<video[\s\S]*?src="[^"]+?"/,
];


async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
    host = cfg.ext;
    if (cfg.ext.hasOwnProperty('host')) { // for custom jx
        host = cfg.ext.host;
        siteJx = cfg.ext;
    }
};

async function request(reqUrl, ua, timeout = 60000) {
    let res = await req(reqUrl, {
        method: 'get',
        headers: ua ? ua : {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'},
        timeout: timeout,
    });
    return res.content;
}

async function home(filter) {
    try {
        let url = getCateUrl(host);

        let jsonArray = null;

        if (url) {
            const json = await request(url, getHeaders(url));
            const obj = JSON.parse(json);
            if (obj.hasOwnProperty("list") && Array.isArray(obj.list)) {
                jsonArray = obj.list;
            } else if (
                obj.hasOwnProperty("data") &&
                obj.data.hasOwnProperty("list") &&
                Array.isArray(obj.data.list)
            ) {
                jsonArray = obj.data.list;
            } else if (obj.hasOwnProperty("data") && Array.isArray(obj.data)) {
                jsonArray = obj.data;
            }
        } else {
            // 通过filter列表读分类
            const filterStr = getFilterTypes(url, null);
            const classes = filterStr.split("\n")[0].split("+");
            jsonArray = [];
            for (let i = 1; i < classes.length; i++) {
                const kv = classes[i].trim().split("=");
                if (kv.length < 2) continue;
                const newCls = {
                    type_name: kv[0].trim(),
                    type_id: kv[1].trim(),
                };
                jsonArray.push(newCls);
            }
        }

        const result = { class: [] };
        if (jsonArray != null) {
            for (let i = 0; i < jsonArray.length; i++) {
                const jObj = jsonArray[i];
                const typeName = jObj.type_name;
                if (isBan(typeName)) continue;
                const typeId = jObj.type_id;
                const newCls = {
                    type_id: typeId,
                    type_name: typeName,
                };
                const typeExtend = jObj.type_extend;
                if (filter) {
                    const filterStr = getFilterTypes(url, typeExtend);

                    const filters = filterStr.split("\n");
                    const filterArr = [];
                    for (let k = (url) ? 1 : 0; k < filters.length; k++) {
                        const l = filters[k].trim();
                        if (!l) continue;
                        const oneLine = l.split("+");

                        let type = oneLine[0].trim();
                        let typeN = type;
                        if (type.includes("筛选")) {
                            type = type.replace(/筛选/g, "");
                            if (type === "class") typeN = "类型";
                            else if (type === "area") typeN = "地区";
                            else if (type === "lang") typeN = "语言";
                            else if (type === "year") typeN = "年份";
                        }
                        const jOne = {
                            key: type,
                            name: typeN,
                            value: [],
                        };
                        for (let j = 1; j < oneLine.length; j++) {
                            const kv = oneLine[j].trim();
                            const sp = kv.indexOf("=");

                            if (sp === -1) {
                                if (isBan(kv)) continue;
                                jOne.value.push({ n: kv, v: kv });
                            } else {
                                const n = kv.substring(0, sp);
                                if (isBan(n)) continue;
                                jOne.value.push({
                                    n: n.trim(),
                                    v: kv.substring(sp + 1).trim(),
                                });
                            }
                        }
                        filterArr.push(jOne);
                    }
                    if (!result.hasOwnProperty("filters")) {
                        result.filters = {};
                    }
                    result.filters[typeId] = filterArr;
                }
                result.class.push(newCls);
            }
        }

        return JSON.stringify(result);
    } catch (e) {

    }
    return "";
}

async function homeVod() {
    try {
        const apiUrl = host;
        let url = getRecommendUrl(apiUrl);
        let isTV = false;

        if (!url) {
            url = getCateFilterUrlPrefix(apiUrl) + "movie&page=1&area=&type=&start=";
            isTV = true;
        }
        const json = await request(url, getHeaders(url));
        const obj = JSON.parse(json);
        const videos = [];
        if (isTV) {
            const jsonArray = obj.data;
            for (let i = 0; i < jsonArray.length; i++) {
                const vObj = jsonArray[i];
                const v = {
                    vod_id: vObj.nextlink,
                    vod_name: vObj.title,
                    vod_pic: vObj.pic,
                    vod_remarks: vObj.state,
                };
                videos.push(v);
            }
        } else {
            const arrays = [];
            findJsonArray(obj, "vlist", arrays);
            if (arrays.length === 0) {
                findJsonArray(obj, "vod_list", arrays);
            }
            const ids = [];
            for (const jsonArray of arrays) {
                for (let i = 0; i < jsonArray.length; i++) {
                    const vObj = jsonArray[i];
                    const vid = vObj.vod_id;
                    if (ids.includes(vid)) continue;
                    ids.push(vid);
                    const v = {
                        vod_id: vid,
                        vod_name: vObj.vod_name,
                        vod_pic: vObj.vod_pic,
                        vod_remarks: vObj.vod_remarks,
                    };
                    videos.push(v);
                }
            }
        }

        const result = {
            list: videos,
        };
        return JSON.stringify(result);
    } catch (e) {
    }
    return "";
}

async function category(tid, pg, filter, extend) {
    try {
        const apiUrl = host;

        let url = getCateFilterUrlPrefix(apiUrl) + tid + getCateFilterUrlSuffix(apiUrl);
        url = url.replace(/#PN#/g, pg);
        url = url.replace(/筛选class/g, extend?.class ?? "");
        url = url.replace(/筛选area/g, extend?.area ?? "");
        url = url.replace(/筛选lang/g, extend?.lang ?? "");
        url = url.replace(/筛选year/g, extend?.year ?? "");
        url = url.replace(/排序/g, extend?.排序 ?? "");


        const json = await request(url, getHeaders(url));
        const obj = JSON.parse(json);

        let totalPg = Infinity;
        try {
            if (obj.totalpage !== undefined && typeof obj.totalpage === "number") {
                totalPg = obj.totalpage;
            } else if (
                obj.pagecount !== undefined &&
                typeof obj.pagecount === "number"
            ) {
                totalPg = obj.pagecount;
            } else if (
                obj.data !== undefined &&
                typeof obj.data === "object" &&
                obj.data.total !== undefined &&
                typeof obj.data.total === "number" &&
                obj.data.limit !== undefined &&
                typeof obj.data.limit === "number"
            ) {
                const limit = obj.data.limit;
                const total = obj.data.total;
                totalPg = total % limit === 0 ? total / limit : Math.floor(total / limit) + 1;
            }
        } catch (e) {

        }

        const jsonArray =
            obj.list !== undefined
                ? obj.list
                : obj.data !== undefined && obj.data.list !== undefined
                    ? obj.data.list
                    : obj.data;
        const videos = [];

        if (jsonArray !== undefined) {
            for (let i = 0; i < jsonArray.length; i++) {
                const vObj = jsonArray[i];
                const v = {
                    vod_id: vObj.vod_id !== undefined ? vObj.vod_id : vObj.nextlink,
                    vod_name: vObj.vod_name !== undefined ? vObj.vod_name : vObj.title,
                    vod_pic: vObj.vod_pic !== undefined ? vObj.vod_pic : vObj.pic,
                    vod_remarks: vObj.vod_remarks !== undefined ? vObj.vod_remarks : vObj.state,
                };
                videos.push(v);
            }
        }

        const result = {
            page: pg,
            pagecount: totalPg,
            limit: 90,
            total: Infinity,
            list: videos,
        };

        return JSON.stringify(result);
    } catch (e) {
        SpiderDebug.log(e);
    }
    return "";
}

async function detail(ids) {
    try {
        const apiUrl = host;
        const url = getPlayUrlPrefix(apiUrl) + ids;

        const json = await request(url, getHeaders(url));
        const obj = JSON.parse(json);
        const result = {
            list: [],
        };
        const vod = {};
        genPlayList(apiUrl, obj, json, vod, ids);
        result.list.push(vod);
        return JSON.stringify(result);
    } catch (e) {

    }
    return "";
}

const parseUrlMap = new Map();

function genPlayList(URL, object, json, vod, vid) {
    const playUrls = [];
    const playFlags = [];
    
    if (URL.includes("lfytyl.com")) {
        const data = object.data;
        vod.vod_id = data.vod_id || vid;
        vod.vod_name = data.vod_name;
        vod.vod_pic = data.vod_pic;
        vod.type_name = data.vod_class || "";
        vod.vod_year = data.vod_year || "";
        vod.vod_area = data.vod_area || "";
        vod.vod_remarks = data.vod_remarks || "";
        vod.vod_actor = data.vod_actor || "";
        vod.vod_director = data.vod_director || "";
        vod.vod_content = data.vod_content || "";
        
        vod.vod_play_from = data.vod_play_from;
        vod.vod_play_url = data.vod_play_url;
        return;
    }

    if (URL.includes("api.php/app")) {
        const data = object.data;
        vod.vod_id = data.vod_id || vid;
        vod.vod_name = data.vod_name;
        vod.vod_pic = data.vod_pic;
        vod.type_name = data.vod_class || "";
        vod.vod_year = data.vod_year || "";
        vod.vod_area = data.vod_area || "";
        vod.vod_remarks = data.vod_remarks || "";
        vod.vod_actor = data.vod_actor || "";
        vod.vod_director = data.vod_director || "";
        vod.vod_content = data.vod_content || "";

        const vodUrlWithPlayer = data.vod_url_with_player;
        for (let i = 0; i < vodUrlWithPlayer.length; i++) {
            const from = vodUrlWithPlayer[i];
            let flag = from.code.trim();
            if (flag === "") flag = from.name.trim();
            playFlags.push(flag);
            playUrls.push(from.url);
            
            let purl = from.parse_api;           
            const parseUrls = parseUrlMap.get(flag) || [];
            if (purl && !parseUrls.includes(purl)) {
                parseUrls.push(purl);
            }
            parseUrlMap.set(flag, parseUrls); 
            
        }
    } else if (URL.includes("xgapp")) {
        const data = object.data.vod_info;
        vod.vod_id = data.vod_id || vid;
        vod.vod_name = data.vod_name;
        vod.vod_pic = data.vod_pic;
        vod.type_name = data.vod_class || "";
        vod.vod_year = data.vod_year || "";
        vod.vod_area = data.vod_area || "";
        vod.vod_remarks = data.vod_remarks || "";
        vod.vod_actor = data.vod_actor || "";
        vod.vod_director = data.vod_director || "";
        vod.vod_content = data.vod_content || "";

        const vodUrlWithPlayer = data.vod_url_with_player;
        for (let i = 0; i < vodUrlWithPlayer.length; i++) {
            const from = vodUrlWithPlayer[i];
            let flag = from.code.trim();
            if (flag === "") flag = from.name.trim();
            playFlags.push(flag);
            playUrls.push(from.url);

            const purl = from.parse_api.trim();
            const parseUrls = parseUrlMap.get(flag) || [];
            if (purl && !parseUrls.includes(purl)) {
                parseUrls.push(purl);
            }
            parseUrlMap.set(flag, parseUrls);
        }
    } else if (URL.includes(".vod")) {
        const data = object.data;
        vod.vod_id = data.vod_id || vid;
        vod.vod_name = data.vod_name;
        vod.vod_pic = data.vod_pic;
        vod.type_name = data.vod_class || "";
        vod.vod_year = data.vod_year || "";
        vod.vod_area = data.vod_area || "";
        vod.vod_remarks = data.vod_remarks || "";
        vod.vod_actor = data.vod_actor || "";
        vod.vod_director = data.vod_director || "";
        vod.vod_content = data.vod_content || "";

        const vodUrlWithPlayer = data.vod_play_list;
        for (let i = 0; i < vodUrlWithPlayer.length; i++) {
            const from = vodUrlWithPlayer[i];
            let flag = from.player_info.from.trim();
            if (flag === "") flag = from.player_info.show.trim();
            playFlags.push(flag);
            playUrls.push(from.url);

            try {
                const parses = [];
                const parse1 = from.player_info.parse.split(",");
                const parse2 = from.player_info.parse2.split(",");
                parses.push(...parse1, ...parse2);
                const parseUrls = parseUrlMap.get(flag) || [];
                for (const purl of parses) {
                    if (purl.includes("http")) {
                        const match = purl.match(parsePattern1);
                        if (match) {
                            parseUrls.push(match[0]);
                        }
                    } else if (purl.includes("//")) {
                        const match = purl.match(parsePattern1);
                        if (match) {
                            parseUrls.push("http:" + match[0]);
                        }
                    } else {
                        const urlMatch = URL.match(parsePattern2);
                        if (urlMatch) {
                            const match = URL.match(parsePattern1);
                            if (match) {
                                parseUrls.push(urlMatch[0] + match[0]);
                            }
                        }
                    }
                    if (purl.includes("..")) purl = purl.replace(/\.\./g, ".").trim();

                    if (purl && !parseUrls.includes(purl)) {
                        parseUrls.push(purl);
                    }
                }
                parseUrlMap.set(flag, parseUrls);
            } catch (e) {

            }
        }
    } else if (URLPattern1.matcher(URL).find()) {
        // Same implementation as the previous cases
    }

    vod.vod_play_from = playFlags.join("$$$");
    vod.vod_play_url = playUrls.join("$$$");
}


async function play(flag, id, vipFlags) {
    try {
        // let parseUrls = parseUrlMap.get(flag); 
        let parseUrls = siteJx[flag]; // custom sitejx
        if (!parseUrls) {
            if (siteJx.hasOwnProperty('*')) { // all jx
                parseUrls = siteJx['*'];
            } else {
                parseUrls = [];
            }
        }

        if (parseUrls.length > 0) {
            const result = await getFinalVideo(flag, parseUrls, id);
            if (result !== null) {
                return JSON.stringify(result);
            }
        }

        if (isVideo(id)) {
            const result = {
                parse: 0,
                playUrl: "",
                url: id
            };
            return JSON.stringify(result);
        } else {
            const result = {
                parse: 1,
                jx: "1",
                url: id
            };
            return JSON.stringify(result);
        }
    } catch (e) {
        // Handle any error here
    }
    return "";
}

async function search(key, quick) {
    try {
        const apiUrl = host;
        const url = getSearchUrl(apiUrl, encodeURIComponent(key));
        const json = await request(url, getHeaders(url));
        const obj = JSON.parse(json);
        let jsonArray = null;
        const videos = [];

        if (obj.list instanceof Array) {
            jsonArray = obj.list;
        } else if (obj.data instanceof Object && obj.data.list instanceof Array) {
            jsonArray = obj.data.list;
        } else if (obj.data instanceof Array) {
            jsonArray = obj.data;
        }

        if (jsonArray !== null) {
            for (const vObj of jsonArray) {
                if (vObj.vod_id) {
                    const v = {
                        vod_id: vObj.vod_id,
                        vod_name: vObj.vod_name,
                        vod_pic: vObj.vod_pic,
                        vod_remarks: vObj.vod_remarks
                    };
                    videos.push(v);
                } else {
                    const v = {
                        vod_id: vObj.nextlink,
                        vod_name: vObj.title,
                        vod_pic: vObj.pic,
                        vod_remarks: vObj.state
                    };
                    videos.push(v);
                }
            }
        }

        const result = { list: videos };
        return JSON.stringify(result);
    } catch (error) {

    }
    return "";
}



async function getFinalVideo(flag, parseUrls, url) {
    let htmlPlayUrl = "";
    for (const parseUrl of parseUrls) {
        if (parseUrl === "" || parseUrl === "null") {
            continue;
        }
        const playUrl = parseUrl + url;
        const content = await request(playUrl, null, 10000); // 10秒请求，能更好过滤webjx
        let tryJson = null;
        try {
            tryJson = jsonParse(url, content);
        } catch (error) { }

        if (tryJson !== null && tryJson.hasOwnProperty("url") && tryJson.hasOwnProperty("header")) {
            tryJson.header = JSON.stringify(tryJson.header);
            return tryJson;
        }

        if (content.includes("<html")) {
            let sniffer = false;
            for (const p of htmlVideoKeyMatch) {
                if (p.test(content)) {
                    sniffer = true;
                    break;
                }
            }
            if (sniffer) {
                htmlPlayUrl = parseUrl;
            }
        }
    }

    if (htmlPlayUrl !== "") { // 不支持sniffer
        const result = {
                parse: 0,
                playUrl: "",
                url: url
            };
        return JSON.stringify(result);
    }

    return null;
}

function jsonParse(input, json) {
    try {
        // 处理解析接口返回的报文，如果返回的报文中包含header信息，就加到返回值中
        let jsonPlayData = JSON.parse(json);
        // 处理293的解析结果url在data字段的解析
        if (jsonPlayData.hasOwnProperty("data") && typeof jsonPlayData.data === "object" && !jsonPlayData.hasOwnProperty("url")) {
            jsonPlayData = jsonPlayData.data;
        }

        let url = jsonPlayData.url;

        if (url.startsWith("//")) {
            url = "https:" + url;
        }
        if (!url.trim().startsWith("http")) {
            return null;
        }
        if (url === input) {
            if (isVip(url) || !isVideoFormat(url)) {
                return null;
            }
        }
        if (isBlackVodUrl(input, url)) {
            return null;
        }

        let headers = {};
        if (jsonPlayData.hasOwnProperty("header")) {
            headers = jsonPlayData.header;
        } else if (jsonPlayData.hasOwnProperty("Header")) {
            headers = jsonPlayData.Header;
        } else if (jsonPlayData.hasOwnProperty("headers")) {
            headers = jsonPlayData.headers;
        } else if (jsonPlayData.hasOwnProperty("Headers")) {
            headers = jsonPlayData.Headers;
        }

        let ua = "";
        if (jsonPlayData.hasOwnProperty("user-agent")) {
            ua = jsonPlayData["user-agent"];
        } else if (jsonPlayData.hasOwnProperty("User-Agent")) {
            ua = jsonPlayData["User-Agent"];
        }
        if (ua.trim().length > 0) {
            headers["User-Agent"] = " " + ua;
        }

        let referer = "";
        if (jsonPlayData.hasOwnProperty("referer")) {
            referer = jsonPlayData.referer;
        } else if (jsonPlayData.hasOwnProperty("Referer")) {
            referer = jsonPlayData.Referer;
        }
        if (referer.trim().length > 0) {
            headers["Referer"] = " " + referer;
        }

        headers = fixJsonVodHeader(headers, input, url);

        const taskResult = {
            header: headers,
            url: url,
            parse: "0"
        };

        return taskResult;
    } catch (error) {

    }
    return null;
}

function isVip(url) {
    try {
        let isVip = false;
        const host = new URL(url).hostname;
        const vipWebsites = ["iqiyi.com", "v.qq.com", "youku.com", "le.com", "tudou.com", "mgtv.com", "sohu.com", "acfun.cn", "bilibili.com", "baofeng.com", "pptv.com"];
        for (let b = 0; b < vipWebsites.length; b++) {
            if (host.includes(vipWebsites[b])) {
                if (vipWebsites[b] === "iqiyi.com") {
                    // 爱奇艺需要特殊处理
                    if (url.includes("iqiyi.com/a_") || url.includes("iqiyi.com/w_") || url.includes("iqiyi.com/v_")) {
                        isVip = true;
                        break;
                    }
                } else {
                    isVip = true;
                    break;
                }
            }
        }
        return isVip;
    } catch (e) {
    }
    return false;
}


function isBlackVodUrl(input, url) {
    return url.includes("973973.xyz") || url.includes(".fit:");
}


function fixJsonVodHeader(headers, input, url) {
    if (headers === null) {
        headers = {};
    }

    if (input.includes("www.mgtv.com")) {
        headers["Referer"] = " ";
        headers["User-Agent"] = " Mozilla/5.0";
    } else if (url.includes("titan.mgtv")) {
        headers["Referer"] = " ";
        headers["User-Agent"] = " Mozilla/5.0";
    } else if (input.includes("bilibili")) {
        headers["Referer"] = " https://www.bilibili.com/";
        headers["User-Agent"] = " " + Misc.UaWinChrome;
    }

    return headers;
}





const snifferMatch = /http((?!http).){26,}?\.(m3u8|mp4|flv|avi|mkv|rm|wmv|mpg)\?.*|http((?!http).){26,}\.(m3u8|mp4|flv|avi|mkv|rm|wmv|mpg)|http((?!http).){26,}\/m3u8\?pt=m3u8.*|http((?!http).)*?default\.ixigua\.com\/.*|http((?!http).)*?cdn-tos[^\?]*|http((?!http).)*?\/obj\/tos[^\?]*|http.*?\/player\/m3u8play\.php\?url=.*|http.*?\/player\/.*?[pP]lay\.php\?url=.*|http.*?\/playlist\/m3u8\/\?vid=.*|http.*?\.php\?type=m3u8&.*|http.*?\/download.aspx\?.*|http.*?\/api\/up_api.php\?.*|https.*?\.66yk\.cn.*|http((?!http).)*?netease\.com\/file\/.*/;

function isVideoFormat(url) {
    if (snifferMatch.test(url)) {
        return !url.includes("cdn-tos") || !url.includes(".js");
    }
    return false;
    
}

function isVideo(url) {
    if (!url.includes(".mp4") || !url.includes(".m3u8")) {
        return true;
    }
    return false;
}




function UA(url) {
    if (url.includes(".vod")) {
        return "okhttp/4.1.0";
    }
}

function getCateUrl(URL) {
    if (URL.includes("api.php/app") || URL.includes("xgapp")) {
        return URL + "nav?token=";
    } else if (URL.includes(".vod")) {
        return URL + "/types";
    } else {
        return "";
    }
}

function getPlayUrlPrefix(URL) {
    if (URL.includes("api.php/app") || URL.includes("xgapp")) {
        return URL + "video_detail?id=";
    } else if (URL.includes(".vod")) {
        return URL + "/detail?vod_id=";
    } else {
        return "";
    }
}

function getRecommendUrl(URL) {
    if (URL.includes("api.php/app") || URL.includes("xgapp")) {
        return URL + "index_video?token=";
    } else if (URL.includes(".vod")) {
        return URL + "/vodPhbAll";
    } else {
        return "";
    }
}

function getFilterTypes(URL, typeExtend) {
    let str = "";

    if (typeExtend !== null) {
        for (let key in typeExtend) {
            if (key === "class" || key === "area" || key === "lang" || key === "year") {
                try {

                    str += "筛选" + key + "+全部=+" + typeExtend[key].replace(/,/g, "+") + "\n";
                } catch (e) { }
            }
        }
    }

    if (URL.includes(".vod")) {
        str += "\n" + "排序+全部=+最新=time+最热=hits+评分=score";
    } else if (URL.includes("api.php/app") || URL.includes("xgapp")) {
        // Do nothing, leave the string as it is.
    } else {
        str = "分类+全部=+电影=movie+连续剧=tvplay+综艺=tvshow+动漫=comic+4K=movie_4k+体育=tiyu\n筛选class+全部=+喜剧+爱情+恐怖+动作+科幻+剧情+战争+警匪+犯罪+动画+奇幻+武侠+冒险+枪战+恐怖+悬疑+惊悚+经典+青春+文艺+微电影+古装+历史+运动+农村+惊悚+惊悚+伦理+情色+福利+三级+儿童+网络电影\n筛选area+全部=+大陆+香港+台湾+美国+英国+法国+日本+韩国+德国+泰国+印度+西班牙+加拿大+其他\n筛选year+全部=+2023+2022+2021+2020+2019+2018+2017+2016+2015+2014+2013+2012+2011+2010+2009+2008+2007+2006+2005+2004+2003+2002+2001+2000";
    }

    return str;
}

function getCateFilterUrlSuffix(URL) {
    if (URL.includes("api.php/app") || URL.includes("xgapp")) {
        return "&class=筛选class&area=筛选area&lang=筛选lang&year=筛选year&limit=18&pg=#PN#";
    } else if (URL.includes(".vod")) {
        return "&class=筛选class&area=筛选area&lang=筛选lang&year=筛选year&by=排序&limit=18&page=#PN#";
    } else {
        return "&page=#PN#&area=筛选area&type=筛选class&start=筛选year";
    }
}

function getCateFilterUrlPrefix(URL) {
    if (URL.includes("api.php/app") || URL.includes("xgapp")) {
        return URL + "video?tid=";
    } else if (URL.includes(".vod")) {
        return URL + "?type=";
    } else {
        return URL + "?ac=list&class=";
    }
}

function isBan(key) {
    return key === "伦理" || key === "情色" || key === "福利";
}

function getSearchUrl(URL, KEY) {
    if (URL.includes(".vod")) {
        return URL + "?wd=" + KEY + "&page=";
    } else if (URL.includes("api.php/app") || URL.includes("xgapp")) {
        return URL + "search?text=" + KEY + "&pg=";
    } else if (urlPattern1.test(URL)) {
        return URL + "?ac=list&zm=" + KEY + "&page=";
    }
    return "";
}

function findJsonArray(obj, match, result) {
    Object.keys(obj).forEach((k) => {
        try {
            const o = obj[k];
            if (k === match && Array.isArray(o)) {
                result.push(o);
            }
            if (typeof o === "object" && o !== null) {
                if (Array.isArray(o)) {
                    o.forEach((item) => {
                        if (typeof item === "object" && item !== null) {
                            findJsonArray(item, match, result);
                        }
                    });
                } else {
                    findJsonArray(o, match, result);
                }
            }
        } catch (e) {
        }
    });
}

function jsonArr2Str(array) {
    const strings = [];
    for (let i = 0; i < array.length; i++) {
        try {
            strings.push(array[i]);
        } catch (e) {
        }
    }
    return strings.join(",");
}

function getHeaders(URL) {
    const headers = {};
    headers["User-Agent"] = UA(URL);
    return headers;
}

function isJsonString(str) {
    try {
        JSON.parse(str);
    } catch (e) {
        return false;
    }
    return true;
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

