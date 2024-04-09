/*
* @File     : doll.js
* @Author   : jade
* @Date     : 2024/1/4 14:15
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : doll
*/

import {Spider} from "./spider.js";
import {Crypto, load} from "../lib/cat.js";
import {VodDetail, VodShort} from "../lib/vod.js";
import * as Utils from "../lib/utils.js";

class Doll extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://hongkongdollvideo.com"
    }


    getName() {
        return "🔞┃玩偶姐姐┃🔞"
    }

    getAppName() {
        return "玩偶姐姐"
    }

    getJSName() {
        return "doll"
    }

    getType() {
        return 3
    }

    async parseVodShortListFromDoc($) {
        let vod_list = []
        let vodElements = $("[class=\"row\"]").find("[class=\"video-detail\"]")
        for (const vodElement of vodElements) {
            let vodShort = new VodShort()
            vodShort.vod_id = $(vodElement).find("a")[0].attribs["href"]
            let videoInfoElements = $($(vodElement).find("[class=\"video-info\"]")).find("a")
            vodShort.vod_name = videoInfoElements[0].attribs["title"]
            vodShort.vod_remarks = $(videoInfoElements[1]).text()
            vodShort.vod_pic = $(vodElement).find("img")[0].attribs["data-src"]
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodDetailFromDoc($, key) {
        let vodDetail = new VodDetail()
        let vodElement = $("[class=\"container-fluid\"]")
        vodDetail.vod_name = $($(vodElement).find("[class=\"page-title\"]")[0]).text()
        vodDetail.vod_remarks = $(vodElement).find("[class=\"tag my-1 text-center\"]")[0].attribs["href"].replaceAll("/", "")
        vodDetail.vod_pic = $(vodElement).find("video")[0].attribs["poster"]
        let html = $.html()
        let voteTag = Utils.getStrByRegex(/var voteTag="(.*?)";/g, html)
        let videoInfo = JSON.parse(Utils.getStrByRegex(/<script type="application\/ld\+json">(.*?)<\/script>/g, html))
        //
        // try {
        //     let play_url_1 = await this.fetch(videoInfo["contentUrl"], null, this.getHeader())
        //     await this.jadeLog.debug(`播放链接为:${play_url_1}`)
        // } catch (e) {
        //     await this.jadeLog.error(e)
        // }


        voteTag = Crypto.enc.Utf8.stringify(Crypto.enc.Base64.parse(voteTag))
        let code = []
        for (let i = 0; i < voteTag.length; i++) {
            let k = i % key.length;
            code.push(String.fromCharCode(voteTag.charCodeAt(i) ^ key.charCodeAt(k)))
        }
        let play_url_2 = decodeURIComponent(Crypto.enc.Utf8.stringify(Crypto.enc.Base64.parse(code.join(""))))
        vodDetail.vod_play_from = "玩偶姐姐"
        vodDetail.vod_play_url = "玩偶姐姐" + "$" + play_url_2
        return vodDetail
    }

    async setClasses() {
        let html = await this.fetch(this.siteUrl, null, this.getHeader())
        if (html !== null) {
            let $ = load(html)
            let navElements = $("[class=\"list-unstyled topnav-menu d-flex d-lg-block align-items-center justify-content-center flex-fill topnav-menu-left m-0\"]").find("li")
            let index = 1
            let class_id = index.toString()
            this.classes = []
            this.classes.push({"type_name": "首页", "type_id": "1"})
            this.filterObj[class_id] = []
            for (const navElement of navElements) {
                let type_list = $(navElement).text().split("\n")
                let valueElements = $(navElement).find("a")
                let valueList = [{"n": "全部", "v": class_id}]
                let type_id = index.toString()
                for (const valueElement of valueElements) {
                    let title = $(valueElement).text().replaceAll("\n", "")
                    let href = valueElement.attribs["href"]
                    if (href !== undefined) {
                        valueList.push({"n": title, "v": href})
                    }
                }
                type_list = type_list.filter(element => element !== "");
                this.filterObj[class_id].push({"key": type_id, "name": type_list[0], "value": valueList})

                //下面这段是为了切割使用
                // let new_value_list = []
                // for (let i = 0; i < valueList.length; i++) {
                //     new_value_list.push(valueList[i])
                //     if (i % 8 === 0 && i !== 0) {
                //         this.filterObj[class_id].push({"key": type_id, "name": type_list[0], "value": new_value_list})
                //         new_value_list = []
                //     }
                // }
                // this.filterObj[class_id].push({"key": type_id, "name": type_list[0], "value": new_value_list})

            }
            let menuElements = $("[id=\"side-menu\"]").find("li")
            for (const menuElement of menuElements) {
                let type_id = $(menuElement).find("a")[0].attribs["href"]
                if (type_id !== undefined && type_id.indexOf(this.siteUrl) > -1) {
                    let type_dic = {
                        "type_name": $(menuElement).text(), "type_id": type_id
                    }
                    this.classes.push(type_dic)
                }
            }
        }

    }

    async setHomeVod() {
        let html = await this.fetch(this.siteUrl, null, this.getHeader())
        if (html != null) {
            let $ = load(html)
            this.homeVodList = await this.parseVodShortListFromDoc($)
        }
    }

    async setCategory(tid, pg, filter, extend) {
        if (extend["1"] !== undefined) {
            if (extend["1"] !== "1") {
                tid = extend[1]
            }
        }
        await this.jadeLog.info(`tid = ${tid}`)
        let cateUrl = ""
        if (tid.indexOf(this.siteUrl) > -1) {
            cateUrl = tid + pg.toString() + ".html"
        } else {
            cateUrl = this.siteUrl
        }
        this.limit = 36
        let html = await this.fetch(cateUrl, null, this.getHeader())
        if (html != null) {
            let $ = load(html)
            this.vodList = await this.parseVodShortListFromDoc($)
        }
    }

    async setDetail(id) {
        let html = await this.fetch(id, null, this.getHeader())
        if (html != null) {
            let $ = load(html)
            let key = Utils.getStrByRegex(/video\/(\w+).html/, id)
            this.vodDetail = await this.parseVodDetailFromDoc($, key)
        }
    }

    async setPlay(flag, id, flags) {
        this.playUrl = id
        this.playHeader = {}
    }

    async setSearch(wd, quick) {
        let searchUrl = this.siteUrl + "search/" + encodeURIComponent(wd)
        let html = await this.fetch(searchUrl, null, this.getHeader())
        if (html !== null) {
            let $ = load(html)
            this.vodList = await this.parseVodShortListFromDoc($)
        }
    }
}

let spider = new Doll()

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