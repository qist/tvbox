/*
* @File     : dygangs.js
* @Author   : jade
* @Date     : 2024/2/21 15:06
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 电影港
*/

import {VodDetail, VodShort} from "../lib/vod.js"
import * as Utils from "../lib/utils.js";
import {Spider} from "./spider.js";
import {_, load} from "../lib/cat.js";


class MoviePortSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://www.dygangs.xyz"
    }

    getAppName() {
        return "电影港"
    }

    getName() {
        return "🏖️┃电影港┃🏖️"
    }

    getJSName() {
        return "dygangs"
    }

    getType() {
        return 3
    }


    async setClasses() {
        let $ = await this.getHtml()
        let navElements = $($("[class=\"top-nav\"]")[0]).find("a")
        for (const navElement of navElements) {
            let type_id = navElement.attribs.href.replaceAll(this.siteUrl, "")
            let type_name = $(navElement).text()
            if (type_id !== "/") {
                this.classes.push(this.getTypeDic(type_name, type_id))
            }
        }
    }


    async getFilter($, index) {
        let element = $("[class=\"nav-down-2 clearfix\"]")[index]
        let extend_list = []
        if (element !== undefined) {
            let name = "按类型"
            let extend_dic = {"key": name, "name": name, "value": []}
            extend_dic["name"] = name
            extend_dic["value"].push({"n": "全部", "v": "0"})
            for (const ele of $(element).find("a")) {
                let type_name = $(ele).html()
                let type_id = ele.attribs.href.split("/").slice(-2)[0]
                extend_dic["value"].push({"n": type_name, "v": type_id})
            }
            extend_list.push(extend_dic)
        }
        return extend_list
    }

    async setFilterObj() {
        let index = 0
        for (const type_dic of this.classes.slice(1, 5)) {
            let type_id = type_dic["type_id"]
            if (type_id !== "最近更新") {
                let url = this.siteUrl + `${type_id}`
                let $ = await this.getHtml(url)
                this.filterObj[type_id] = await this.getFilter($, index)
            }
            index = index + 1
        }
    }

    parseVodShortFromElement($, element) {
        let vodShort = new VodShort();
        vodShort.vod_id = element.attribs.href
        vodShort.vod_name = element.attribs.title
        vodShort.vod_pic = $(element).find("img")[0].attribs["data-original"]
        vodShort.vod_remarks = $($(element).find("i")[0]).text().replaceAll(" ", "").replaceAll("\n", "")
        if (_.isEmpty(vodShort.vod_pic)){
            vodShort.vod_pic =  Utils.RESOURCEURL + "/resources/dygang.jpg"
        }
        return vodShort
    }

    async parseVodShortListFromDoc($) {
        let vod_list = []
        let vodElements = $("[class=\"index-tj-l\"]").find("li")
        for (const vodElement of vodElements) {
            let vodShortElement = $(vodElement).find("a")[0]
            let vodShort = this.parseVodShortFromElement($, vodShortElement)
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodShortListFromDocByCategory($) {
        let vod_list = []
        let vodElements = $("[class=\"index-area clearfix\"]").find("li")
        for (const vodElement of vodElements) {
            let vodShortElement = $(vodElement).find("a")[0]
            let vodShort = this.parseVodShortFromElement($, vodShortElement)
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodDetailFromDoc($) {
        let vodDetail = new VodDetail();
        let vodDetailElement = $("[ class=\"ct mb clearfix\"]")
        vodDetail.vod_pic = $(vodDetailElement).find("img")[0].attribs["src"]
        vodDetail.vod_name = Utils.getStrByRegex(/◎片　　名　(.*?)<br>/, $(vodDetailElement).html())
        vodDetail.vod_area = Utils.getStrByRegex(/◎产　　地　(.*?)<br>/, $(vodDetailElement).html())
        vodDetail.vod_year = Utils.getStrByRegex(/◎年　　代　(.*?)<br>/, $(vodDetailElement).html())
        vodDetail.type_name = Utils.getStrByRegex(/◎类　　别　(.*?)<br>/, $(vodDetailElement).html())
        vodDetail.vod_remarks = Utils.getStrByRegex(/◎集　　数　(.*?)<br>/, $(vodDetailElement).html())
        let content = Utils.getStrByRegex(/◎主　　演　(.*?)<\/p>/s, $(vodDetailElement).html())
        if (_.isEmpty(content)) {
            content = Utils.getStrByRegex(/◎演　　员　(.*?)<\/p>/s, $(vodDetailElement).html())
        }
        let actor_list = []
        for (const actor of content.split("\n")) {
            actor_list.push(actor.replaceAll("　　　　&nbsp; 　", "").replaceAll("<br>", "").replaceAll("　　　　　", ""))
        }
        vodDetail.vod_actor = actor_list.join("/")
        vodDetail.vod_director = Utils.getStrByRegex(/◎导　　演　(.*?)<br>/, $(vodDetailElement).html())
        vodDetail.vod_content = Utils.getStrByRegex(/◎简　　介<\/p>(.*?)<br>/s, $(vodDetailElement).html()).replaceAll("<p>", "").replaceAll("\n", "")
        if (_.isEmpty(vodDetail.vod_content)) {
            vodDetail.vod_content = Utils.getStrByRegex(/◎简　　介<br>(.*?)<\/p>/s, $(vodDetailElement).html()).replaceAll("<p>", "").replaceAll("\n", "")

        }
        let vod_play_from_list = []
        let vod_play_list = []


        let playFormatElements = $("[class=\"playfrom tab8 clearfix\"]")
        let playUrlElements = $("[class=\"videourl clearfix\"]")
        for (let i = 0; i < playFormatElements.length; i++) {
            let playFormatElement = playFormatElements[i]
            let format_name = $($(playFormatElement).find("li")).html()
            vod_play_from_list.push(format_name.replaceAll("<i class=\"playerico ico-Azhan\"></i> ", ""))
            let vodItems = []
            for (const playUrlElement of $(playUrlElements[i]).find("a")) {
                let episodeName = playUrlElement.attribs.title
                let episodeUrl = playUrlElement.attribs.href
                vodItems.push(episodeName + "$" + episodeUrl)
            }
            vod_play_list.push(vodItems.join("#"))

        }
        let playFormatElement = $($(vodDetailElement).find("span")[0]).find("span")
        if (playFormatElement.length > 0) {
            let format_name = $(playFormatElement).html()
            vod_play_from_list.push(Utils.getStrByRegex(/【(.*?)】/, format_name.replaceAll("下载地址", "磁力链接")))
            let vodItems = []
            for (const playUrlElement of $($($(vodDetailElement).find("tbody")).find("tr")).find("a")) {
                let episodeName = $(playUrlElement).html().replaceAll(".mp4", "")
                let episodeUrl = playUrlElement.attribs.href
                vodItems.push(episodeName + "$" + episodeUrl)
            }
            vod_play_list.push(vodItems.join("#"))

        }
        vodDetail.vod_play_from = vod_play_from_list.join("$$$")
        vodDetail.vod_play_url = vod_play_list.join("$$$")
        return vodDetail

    }


    async setHomeVod() {
        let $ = await this.getHtml()
        this.homeVodList = await this.parseVodShortListFromDoc($)
    }


    async setCategory(tid, pg, filter, extend) {
        let url = this.siteUrl + tid
        if (extend["按类型"] !== undefined && extend["按类型"] !== "0") {
            url = url + `${extend["按类型"]}/`
        }
        if (parseInt(pg) > 1) {
            url = url + `index_${pg}.html`
        }
        let $ = await this.getHtml(url)
        this.vodList = await this.parseVodShortListFromDocByCategory($)
    }

    async setDetail(id) {
        let $ = await this.getHtml(id)
        this.vodDetail = await this.parseVodDetailFromDoc($)
    }

    async setSearch(wd, quick) {
        let url = this.siteUrl + "/e/search/index.php"
        let params = {"keyboard": wd, "submit": "搜 索", "show": "title,zhuyan", "tempid": "1"}
        let resp = await this.post(url, params, this.getHeader())
        let $ = load(resp)
        this.vodList = await this.parseVodShortListFromDocByCategory($)

    }

    async setPlay(flag, id, flags) {
        if (id.indexOf("http") > -1) {
            let $ = await this.getHtml(id)
            let url = Utils.getStrByRegex(/url: '(.*?)',/, $.html())
            if (_.isEmpty(url)) {
                let videoUrl = $($("[class=\"video\"]")[0]).find("iframe")[0].attribs["src"]
                let html = await this.fetch(videoUrl, null, {"User-Agent": Utils.CHROME})
                this.playUrl = Utils.getStrByRegex(/url: '(.*?)',/, html)
                if (_.isEmpty(this.playUrl)){
                    let urlHost = Utils.getHost(videoUrl)
                    this.playUrl = urlHost + Utils.getStrByRegex(/var main = "(.*?)";/, html)
                }
            } else {
                this.playUrl = url
            }
        } else {
            this.playUrl = id
        }
    }

}

let spider = new MoviePortSpider()

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

async function proxy(segments, headers) {
    return await spider.proxy(segments, headers)
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
        proxy: proxy
    };
}
export {spider}