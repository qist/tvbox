/*
* @File     : hscangku.js
* @Author   : jade
* @Date     : 2024/01/03 19:19
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/
import {load} from "../lib/cat.js";
import {VodDetail, VodShort} from "../lib/vod.js";
import {Spider} from "./spider.js";


class HsCangkuSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://hsck12.shop/"
    }

    getName() {
        return "🔞┃黄色仓库┃🔞"
    }

    getAppName() {
        return "黄色仓库"
    }
    getJSName() {
        return "hscangku"
    }

    getType() {
        return 3
    }

    async parseVodShortListFromDoc($) {
        let vod_list = []
        let vodElements = $("[class=\"stui-vodlist clearfix\"]").find("li")
        for (const vod_element of vodElements) {
            let vodShort = new VodShort()
            let vodElement = $(vod_element).find("a")[0]
            vodShort.vod_id = vodElement.attribs["href"]
            vodShort.vod_name = vodElement.attribs["title"]
            vodShort.vod_pic = vodElement.attribs["data-original"]
            vod_list.push(vodShort)
        }

        return vod_list
    }

    async parseVodDetailFromDoc($) {
        let vodDetail = new VodDetail()
        let element = $($("[class=\"stui-pannel__head clearfix\"]")[1]).find("h3")
        let stui_pannel_bd_element = $("div.stui-pannel-bd > div")
        let video_element = stui_pannel_bd_element.find("video")[0]
        vodDetail.vod_name = element.text()
        vodDetail.vod_pic = video_element.attribs["poster"]
        vodDetail.vod_play_from = "黄色仓库"
        vodDetail.vod_play_url = $(video_element).find("source")[0].attribs["src"]
        return vodDetail
    }

    async setClasses() {
        this.classes = [
            {
                "type_name": "国产视频",
                "type_id": "?type=gc"
            },
            {
                "type_name": "国产新片",
                "type_id": "?type=ycgc"
            },
            {
                "type_name": "无码中文字幕",
                "type_id": "?type=wz"
            },
            {
                "type_name": "有码中文字幕",
                "type_id": "?type=yz"
            },
            {
                "type_name": "日本无码",
                "type_id": "?type=rw"
            }
        ]
    }
    async setCategory(tid, pg, filter, extend) {
        let url = this.siteUrl + tid + "&p=" + pg.toString()
        let html = await this.fetch(url, null,this.getHeader())
        this.limit = 40;
        if (html !== null) {
            let $ = load(html)
            this.vodList = await this.parseVodShortListFromDoc($)
            this.total = parseInt($("[class=\"active\"]").find("span").text())
        }
    }

    async setDetail(id) {
        let url = this.siteUrl + id
        let html = await this.fetch(url,null,this.getHeader())
        if (html !== null) {
            let $ = load(html)
            this.vodDetail = await this.parseVodDetailFromDoc($)
        }
    }

    async setPlay(flag, id, flags) {
        this.playUrl = id
        this.playHeader = {}
    }
}

let spider = new HsCangkuSpider()

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
        init: init,
        home: home,
        homeVod: homeVod,
        category: category,
        detail: detail,
        play: play,
        search: search,
    };
}
export {spider}