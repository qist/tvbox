/*
* @File     : xb6v.js
* @Author   : jade
* @Date     : 2023/12/26 10:13
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/

import * as Utils from "../lib/utils.js";
import {_, load} from "../lib/cat.js";
import {VodDetail, VodShort} from "../lib/vod.js";
import {Spider} from "./spider.js";


class Xb6vSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://www.xb6v.com";
    }

    getName() {
        return "🧲┃磁力新6V┃🧲"
    }

    getAppName() {
        return "磁力新6V"
    }

    getJSName() {
        return "xb6v"
    }

    getType() {
        return 3
    }

    async redirect(response) {
        await this.jadeLog.debug(`重定向回复值为:${response.content}`)
        let matcher = /<a HREF=(.*?)>/.exec(response.content)
        if (matcher.length > 1) {
            let new_url = this.siteUrl + "/e/search/" + matcher[1].replaceAll("\\", "").replaceAll("\"", "")
            await this.jadeLog.info(`重定向url为:${new_url}`)
            return await this.fetch(new_url, null, this.getHeader())
        }
    }

    getActorOrDirector(pattern, str) {
        return Utils.getStrByRegex(pattern, str)
            .replace(/<br>/g, "")
            .replace(/&nbsp;./g, "")
            .replace(/&amp;/g, "")
            .replace(/middot;/g, "・")
            .replace(/　　　　　/g, ",")
            .replace(/　　　　 　/g, ",")
            .replace(/　/g, "");
    }

    getDescription(pattern, str) {
        return Utils.getStrByRegex(pattern, str)
            .replace(/<\/?[^>]+>/g, "")
            .replace(/\n/g, "")
            .replace(/&amp;/g, "")
            .replace(/middot;/g, "・")
            .replace(/ldquo;/g, "【")
            .replace(/rdquo;/g, "】")
            .replace(/　/g, "");
    }


    async parseVodShortListFromDoc($) {
        let items = $("#post_container .post_hover");
        let vod_list = []
        for (const item of items) {
            let element = $(item).find("[class=zoom]")[0];
            let vodShort = new VodShort()
            vodShort.vod_id = element.attribs["href"];
            vodShort.vod_name = element.attribs["title"].replaceAll(/<\\?[^>]+>/g, "");
            vodShort.vod_pic = $(element).find("img")[0].attribs["src"];
            vodShort.vod_remarks = $(item).find("[rel=\"category tag\"]").text().replaceAll("\n", "").replaceAll(" ", "");
            vod_list.push(vodShort)
        }
        return vod_list;
    }

    async parseVodDetailFromDoc($) {
        let sourceList = $("#post_content");
        let play_form_list = []
        let play_url_list = []
        if (!this.catOpenStatus) {
            let i = 0
            let circuitName = "磁力线路";
            for (const source of sourceList) {
                let aList = $(source).find("table a")
                let vodItems = []
                for (const a of aList) {
                    let episodeUrl = a.attribs["href"]
                    let episodeName = a.children[0].data
                    if (!episodeUrl.toLowerCase().startsWith("magnet")) continue;
                    vodItems.push(episodeName + "$" + episodeUrl);
                }
                if (vodItems.length > 0) {
                    i++;
                    play_form_list.push(circuitName + i)
                    play_url_list.push(vodItems.join("#"))
                }
            }
        }
        let playSourceList = $($(".mainleft")).find("[class=\"widget box row\"]")
        for (const source of playSourceList) {
            let play_format = $(source).find("h3").text()
            let vodItems = []
            if (!_.isEmpty(play_format)) {
                let urlSourceList = $(source).find("a")
                for (const url_source of urlSourceList) {
                    vodItems.push(url_source.attribs["title"] + "$" + url_source.attribs["href"])
                }
                play_form_list.push(play_format)
                play_url_list.push(vodItems.join("#"))
            }
        }
        let partHTML = $(".context").html();
        let vodDetail = new VodDetail();
        vodDetail.vod_name = $(".article_container > h1").text();
        vodDetail.vod_pic = $("#post_content img").attr("src");
        vodDetail.type_name = Utils.getStrByRegex(/◎类　　别　(.*?)<br>/, partHTML);
        if (_.isEmpty(vodDetail.type_name)) vodDetail.type_name = $("[rel=\"category tag\"]").text();
        vodDetail.vod_year = Utils.getStrByRegex(/◎年　　代　(.*?)<br>/, partHTML);
        if (_.isEmpty(vodDetail.vod_year)) vodDetail.vod_year = Utils.getStrByRegex(/首播:(.*?)<br>"/, partHTML);
        vodDetail.vod_area = Utils.getStrByRegex(/◎产　　地　(.*?)<br>/, partHTML);
        if (_.isEmpty(vodDetail.vod_year)) vodDetail.vod_area = Utils.getStrByRegex(/地区:(.*?)<br>"/, partHTML);
        vodDetail.vod_remarks = Utils.getStrByRegex(/◎上映日期　(.*?)<br>/, partHTML);
        vodDetail.vod_actor = this.getActorOrDirector(/◎演　　员　(.*?)<\/p>/, partHTML);
        if (_.isEmpty(vodDetail.vod_actor)) vodDetail.vod_actor = this.getActorOrDirector(/◎主　　演　(.*?)<\/p>/, partHTML);
        if (_.isEmpty(vodDetail.vod_actor)) vodDetail.vod_actor = this.getActorOrDirector(/主演:(.*?)<br>/, partHTML);
        vodDetail.vod_director = this.getActorOrDirector(/◎导　　演　(.*?)<br>/, partHTML);
        if (_.isEmpty(vodDetail.vod_director)) vodDetail.vod_director = this.getActorOrDirector(/导演:(.*?)<br>/, partHTML);
        vodDetail.vod_content = this.getDescription(/◎简　　介(.*?)<hr>/gi, partHTML);
        if (_.isEmpty(vodDetail.vod_content)) vodDetail.vod_content = this.getDescription(/简介(.*?)<\/p>/gi, partHTML);
        if (_.isEmpty(vodDetail.vod_content)) vodDetail.vod_content = this.getDescription(/◎简　　介(.*?)<br>/gi, partHTML);
        vodDetail.vod_play_from = play_form_list.join("$$$")
        vodDetail.vod_play_url = play_url_list.join("$$$")
        return vodDetail
    }

    async parseVodPlayFromDoc(flag, $) {
        let play_url = ""
        let html = $.html()
        switch (flag) {
            case "播放地址（无插件 极速播放）":
            case "播放地址三":
                play_url = $($(".video")).find("iframe")[0].attribs["src"] + "/index.m3u8"
                break
            case "播放地址（无需安装插件）":
                let matchers2 = /url: '(.*?)',/gs.exec(html)
                if (matchers2.length > 1) {
                    play_url = matchers2[1]
                }
                break
            case "播放地址四":
                let matchers4 = /source: "(.*?)",/gs.exec(html)
                if (matchers4.length > 1) {
                    play_url = matchers4[1]
                }
                break
            default:
                await this.jadeLog.warning(`暂不支持当前格式,当前格式为:${flag}`)
                break
        }
        return play_url
    }


    async setClasses() {
        let html = await this.fetch(this.siteUrl, null, this.getHeader());
        if (!_.isEmpty(html)) {
            let $ = load(html);
            let elements = $('#menus > li > a');
            for (let i = 0; i < elements.length; i++) {
                let element = elements[i]
                if (i < 2 || i === elements.length - 1) continue;
                let typeName = element.children[0].data;
                let typeId = element.attribs["href"];
                this.classes.push({"type_name": typeName, "type_id": typeId})
                if (typeName === "电视剧") {
                    let values = [{"n": "不限", "v": ""}]
                    for (const a of $(element.next).find("a")) {
                        values.push({"n": a.children[0].data, "v": a.attribs["href"].replaceAll(typeId, "")})
                    }
                    this.filterObj[typeId] = [{
                        "key": "cateId", "name": "类型", "value": values
                    }]
                }
            }
        }
    }
    async setHomeVod() {
        let html = await this.fetch(this.siteUrl, null, this.getHeader());
        if (!_.isEmpty(html)) {
            let $ = load(html);
            this.homeVodList = await this.parseVodShortListFromDoc($)
        } else {
            await this.jadeLog.info("首页类别解析失败", true)
        }
    }


    async setCategory(tid, pg, filter, extend) {
        let cateId = extend["cateId"] ?? "";
        let cateUrl = this.siteUrl + tid + cateId;
        this.page = parseInt(pg)
        this.count = 0
        this.limit = 18;
        this.total = 0;
        if (this.page !== 1) {
            cateUrl += "index_" + pg + ".html";
        }
        let html = await this.fetch(cateUrl, null, this.getHeader());
        if (!_.isEmpty(html)) {
            let $ = load(html)
            let href_elements = $(".pagination > a")
            if (href_elements.length > 0) {
                let href = href_elements.slice(-1)[0].attribs["href"];
                let patternPageCount = /index_(.*?).html/
                let matches = patternPageCount.exec(href)
                this.count = parseInt(matches[1])
                let items = $("#post_container .post_hover");
                this.total = this.page === this.count ? (this.page - 1) * this.limit + items.length : this.count * this.limit;
            }
            this.vodList = await this.parseVodShortListFromDoc($)
        }
    }

    async setSearch(wd, quick) {
        let searchUrl = this.siteUrl + "/e/search/index.php";
        let params = {
            "show": "title", "tempid": "1", "tbname": "article", "mid": "1", "dopost": "search", "keyboard": wd,
        }
        let html = await this.post(searchUrl, params, this.getHeader())
        if (!_.isEmpty(html)) {
            let $ = load(html)
            this.vodList = await this.parseVodShortListFromDoc($)
        }
    }


    async setDetail(id) {
        let detailUrl = this.siteUrl + id;
        let html = await this.fetch(detailUrl, null, this.getHeader())
        if (!_.isEmpty(html)) {
            let $ = load(html);
            this.vodDetail = await this.parseVodDetailFromDoc($)
        }
    }

    async setPlay(flag, id, flags) {
        if (id.toLowerCase().startsWith("magnet")) {
            this.playUrl = id
        } else {
            let playUrl = this.siteUrl + id
            let html = await this.fetch(playUrl, null, this.getHeader())
            let $ = load(html)
            this.playUrl = await this.parseVodPlayFromDoc(flag, $)

        }
    }
}

let spider = new Xb6vSpider()

async function init(cfg) {
    await spider.init(cfg)
}

async function home(filter) {
    return await spider.home(filter)
}

async function homeVod() {
    return await spider.homeVod()
}

async function category(tid, pg, filter, extend) {
    return await spider.category(tid, pg, filter, extend)
}

async function detail(id) {
    return await spider.detail(id)
}

async function play(flag, id, flags) {
    return await spider.play(flag, id, flags)
}

async function search(wd, quick) {
    return await spider.search(wd, quick)
}

export function __jsEvalReturn() {
    return {
        init: init, home: home, homeVod: homeVod, category: category, detail: detail, play: play, search: search,
    };
}
export {spider}