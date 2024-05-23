/*
* @File     : alipansou.js
* @Author   : jade
* @Date     : 2024/1/18 13:20
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 猫狸盘搜
*/

import {_, load} from "../lib/cat.js";
import {Spider} from "./spider.js";
import { detailContent,initCloud,playContent,getHeaders } from "../lib/cloud.js";
import {VodDetail, VodShort} from "../lib/vod.js";
import * as Utils from "../lib/utils.js";

class GitCafeSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://www.alipansou.com"
    }
    getHeaders(id) {
        let headers = this.getHeader()
        headers["Referer"] = this.siteUrl + id
        headers["_bid"] = "6d14a5dd6c07980d9dc089a693805ad8"
        headers["Cookie"] = "_egg=70463dec0ec843b682ce18c36ec9ce91e"
        return headers
    }


    getName() {
        return "😸┃阿里猫狸┃😸"
    }

    getAppName() {
        return "阿里猫狸"
    }
    getJSName() {
        return "alipansou"
    }

    getType() {
        return 3
    }

    getHeader() {
        return {
            "User-Agent":Utils.CHROME,
            "Connection": "keep-alive"
        }
    }

    async getContentHtml() {
        let html = await this.fetch(this.siteUrl, null, this.getHeader())
        if (!_.isEmpty(html)) {
            return load(html)
        }
    }

    async spiderInit() {
        this.content_html = await this.getContentHtml()
    }

    async init(cfg) {
        await this.spiderInit()
        await super.init(cfg);
        await initCloud(this.cfgObj);
    }

    async parseClassFromDoc($) {
        let tap_elemets = $($("[id=\"app\"]")[0]).find("van-tab")
        let index = 0
        for (const tap_element of tap_elemets) {
            let type_name = tap_element.attribs["title"]
            if (type_name.indexOf("热搜") === -1 && type_name !== "游戏" && type_name !== "小说") {
                this.classes.push({"type_name": type_name, "type_id": index})
            }
            index = index + 1
        }
    }

    async parseVodShortListFromDoc(doc) {
        let vod_list = []
        let elements = this.content_html(doc).find("a")
        for (const element of elements) {
            let vodShort = new VodShort()
            vodShort.vod_id = element.attribs["href"]
            vodShort.vod_name = this.content_html(element).text().split(".").slice(-1)[0]
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async getAliUrl(id) {
        let url = this.siteUrl + id.replace("/s/", "/cv/")
        let headers = this.getHeaders(id)
        let content = await req(url,{postType:"get",headers:headers,redirect:2})
        await this.jadeLog.debug(`回复内容为:${JSON.stringify(content)}`)
        // let url = await this.fetch(this.siteUrl + id.replace("/s/", "/cv/"), null, headers, true)
        return content.headers.location
    }

    async parseVodDetailfromJson(obj) {
        let vodDetail = new VodDetail();
        vodDetail.vod_name = obj["name"]
        vodDetail.vod_remarks = obj["remarks"]
        let ali_url = await this.getAliUrl(obj["id"])
        await this.jadeLog.debug(`阿里分享链接为:${ali_url}`)
        if (!_.isEmpty(ali_url)) {
            let playVod = await detailContent([ali_url],vodDetail.type_name)
            vodDetail.vod_play_from = _.keys(playVod).join('$$$');
            vodDetail.vod_play_url = _.values(playVod).join('$$$');
        }
        return vodDetail
    }


    async parseVodShortListFromDocBySearch($) {
        let elements = $($($("[id=\"app\"]")[0]).find("van-row")).find("a")
        let vod_list = []
        for (const element of elements) {
            let id = element.attribs["href"]
            let matches = id.match(/(\/s\/[^"])/);
            if (!_.isEmpty(matches) && id.indexOf("https") === -1) {
                let text = $(element).text().replaceAll("\n", "").replaceAll(" ", "")
                if (text.indexOf("时间") > -1 && text.indexOf("文件夹") > -1) {
                    let textList = text.split("时间")
                    let vodShort = new VodShort()
                    vodShort.vod_name = textList[0]
                    vodShort.vod_remarks = textList[1].split("格式")[0].replaceAll(":", "").replaceAll(" ", "").replaceAll("﻿", "").replaceAll(" ", "")
                    vodShort.vod_id = JSON.stringify({
                        "name": vodShort.vod_name, "remarks": vodShort.vod_remarks, "id": id
                    })
                    vod_list.push(vodShort)
                }
            }
        }
        return vod_list
    }

    async setClasses() {
        await this.parseClassFromDoc(this.content_html)
    }


    async setHomeVod() {
        let tap_elemets = this.content_html(this.content_html("[id=\"app\"]")[0]).find("van-tab")
        this.homeVodList = await this.parseVodShortListFromDoc(tap_elemets[0])
    }


    async setDetail(id) {
        if (id.indexOf("search") > -1) {
            let url = this.siteUrl + "/search"
            let params = {"k":decodeURIComponent(id.split("search?k=").slice(-1)[0]) }
            let html = await this.fetch(url, params, this.getHeader())
            if (!_.isEmpty(html)) {
                let $ = load(html)
                let vod_list = await this.parseVodShortListFromDocBySearch($)
                if (vod_list.length > 0) {
                    id = vod_list[0]["vod_id"]
                } else {
                    id = ""
                }
            }
        }
        if (!_.isEmpty(id)) {
            let json_content = JSON.parse(id)
            this.vodDetail = await this.parseVodDetailfromJson(json_content)
        }

    }

    async setCategory(tid, pg, filter, extend) {
        let tap_elemets = this.content_html(this.content_html("[id=\"app\"]")[0]).find("van-tab")
        this.vodList = await this.parseVodShortListFromDoc(tap_elemets[parseInt(tid)])
    }

    async setSearch(wd, quick) {
        let url = this.siteUrl + "/search"
        let params = {"k": wd}
        let html = await this.fetch(url, params, this.getHeader())
        if (!_.isEmpty(html)) {
            let $ = load(html)
            this.vodList = await this.parseVodShortListFromDocBySearch($)
        }
    }

    async setPlay(flag, id, flags) {
        this.playUrl = await playContent(flag, id, flags);
        this.result.setHeader(getHeaders(flag))
    }
}

let spider = new GitCafeSpider()

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