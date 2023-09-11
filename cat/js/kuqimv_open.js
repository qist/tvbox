// 修正：分类改静态 (网站频繁变动分类)
import { load, _ } from "assets://js/lib/cat.js";

let key = "酷奇MV";
let HOST = "https://www.kuqimv.com";
let siteKey = "";
let siteType = 0;
const PC_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36";

async function request(reqUrl, referer, mth, data, hd) {
    const headers = {
        "User-Agent": PC_UA,
    };
    if (referer) headers.referer = encodeURIComponent(referer);
    let res = await req(reqUrl, {
        method: mth || "get",
        headers: headers,
        data: data,
        postType: mth === "post" ? "form" : "",
    });
    return res.content;
}

async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
}

async function home(filter) {
    var classes = [{ "type_id": "1", "type_name": "华语高清" }, { "type_id": "2", "type_name": "日韩精选" }, { "type_id": "3", "type_name": "欧美MV" }, { "type_id": "4", "type_name": "高清现场" }, { "type_id": "5", "type_name": "影视MV" }, { "type_id": "6", "type_name": "夜店视频" }, { "type_id": "7", "type_name": "车模视频" }, { "type_id": "8", "type_name": "热舞视频" }, { "type_id": "9", "type_name": "美女写真" }, { "type_id": "10", "type_name": "美女打碟" }];
    // const html = await request(HOST);
    // const $ = load(html);
    // const class_parse = $(".lei_fl > a[href*=play]");
    // const classes = [];
    // classes = _.map(class_parse, (cls) => {
    //     const typeId = cls.attribs["href"];
    //     typeId = typeId.substring(typeId.lastIndexOf("/") + 1).replace(".html", "");
    //     return {
    //         type_id: typeId,
    //         type_name: cls.children[0].data,
    //     };
    // });
    const filterObj = {};
    return JSON.stringify({
        class: _.map(classes, (cls) => {
            cls.land = 1;
            cls.ratio = 1.78;
            return cls;
        }),
        filters: filterObj,
    });
}

async function homeVod() {
    const link = HOST + "/play/9_1.html";
    const html = await request(link);
    const $ = load(html);
    const items = $("div.mv_list > li");
    let videos = _.map(items, (it) => {
        const a = $(it).find("a:first")[0];
        const img = $(it).find("img:first")[0];
        const singer = $($(it).find("div.singer")[0]).text().trim();
        const remarks = $($(it).find("span.lei_03")[0]).text().trim();
        return {
            vod_id: a.attribs.href.replace(/.*?\/play\/(.*).html/g, "$1"),
            vod_name: a.attribs.title,
            vod_pic: img.attribs["src"],
            vod_remarks: "🎤" + singer + "｜" + remarks || "",
        };
    });
    return JSON.stringify({
        list: videos,
    });
}

async function category(tid, pg, filter, extend) {
    if (pg <= 0 || typeof pg == "undefined") pg = 1;
    const link = HOST + "/play/" + tid + "_" + pg + ".html";
    const html = await request(link);
    const $ = load(html);
    const items = $("div.mv_list > li");
    let videos = _.map(items, (it) => {
        const a = $(it).find("a:first")[0];
        const img = $(it).find("img:first")[0];
        const singer = $($(it).find("div.singer")[0]).text().trim();
        const remarks = $($(it).find("span.lei_03")[0]).text().trim();
        return {
            vod_id: a.attribs.href.replace(/.*?\/play\/(.*).html/g, "$1"),
            vod_name: a.attribs.title,
            vod_pic: img.attribs["src"],
            vod_remarks: "🎤" + singer + "｜" + remarks || "",
        };
    });
    const hasMore = $("div.lei_page > a:contains(下一页)").length > 0;
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
    const vod = {
        vod_id: id,
        vod_remarks: "",
    };
    const playlist = ["观看视频" + "$" + id];
    vod.vod_play_from = "道长在线";
    vod.vod_play_url = playlist.join("#");
    return JSON.stringify({
        list: [vod],
    });
}

async function play(flag, id, flags) {
    const link = HOST + "/skin/kuqimv/play.php";
    const ref = HOST + "/play/" + id + ".html";
    const pdata = { id: id };
    const playUrl = JSON.parse(await request(link, ref, "post", pdata)).url;
    const headers = {
        Referer: HOST,
    };
    return JSON.stringify({
        parse: 0,
        url: playUrl,
        header: headers,
    });
}

async function search(wd, quick, pg) {
    if (pg <= 0 || typeof pg == "undefined") pg = 1;
    const link = HOST + "/search.php?key=" + wd + "&pages=" + pg;
    const html = await request(link);
    const $ = load(html);
    const items = $("div.video_list > li");
    let videos = _.map(items, (it) => {
        const a = $(it).find("a:first")[0];
        const singer = $($(it).find("div.singer")[0]).text().trim();
        const remarks = $($(it).find("span.lei_04")[0]).text().trim();
        return {
            vod_id: a.attribs.href.replace(/.*?\/play\/(.*).html/g, "$1"),
            vod_name: a.attribs.title,
            vod_pic: "https://www.kuqimv.com/static/images/cover/singer.jpg",
            vod_remarks: "🎤" + singer + "｜" + remarks || "",
        };
    });
    const hasMore = $("div.lei_page > a:contains(>)").length > 0;
    const pgCount = hasMore ? parseInt(pg) + 1 : parseInt(pg);
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: 20,
        total: 20 * pgCount,
        list: videos,
        land: 1,
        ratio: 1.78,
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