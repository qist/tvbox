/*
* @File     : lovemovie18.js
* @Author   : jade
* @Date     : 2024/4/29 09:36
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 爱情电影网
*/
import {LoveMovieSpider} from "./lovemovie.js";
import {VodShort} from "../lib/vod.js";

class LoveMovie18Spider extends LoveMovieSpider {
    constructor() {
        super();
        this.siteUrl = "https://b.aqdyje.com"
        this.removeKey = "骑兵营"
    }

    getName() {
        return "🔞┃爱情电影网18+┃🔞"
    }

    getAppName() {
        return "爱情电影网18+"
    }

    getJSName() {
        return "lovemovie18"
    }

    getType() {
        return 3
    }

    async parseVodShortListFromDocBySearch($) {
        let vodElements = $("[class=\"show-list\"]").find("li")
        let vod_list = []
        for (const vodElement of vodElements) {
            let vodShort = new VodShort()
            vodShort.vod_id = $(vodElement).find("a")[0].attribs.href
            let imgElement = $(vodElement).find("img")[0]
            vodShort.vod_pic = imgElement.attribs.src
            vodShort.vod_name = imgElement.attribs.alt
            vodShort.vod_remarks = $($(vodElement).find("[class=\"type fn-left\"]")).text().replace("类型：", "")
            if (vodShort.vod_remarks === "社处片" || vodShort.vod_remarks === "社保片" || vodShort.vod_remarks === "撸丝片" || vodShort.vod_remarks === "撸丝动漫") {
                vod_list.push(vodShort)
            }
        }
        return vod_list
    }


    async getFilter(type_id) {
        let $ = await this.getHtml(this.siteUrl + type_id)
        let extend_list = []
        let extend_dic = {"key": "class", "name": "类型", "value": []}
        for (const navElement of $("[class=\"subnav-tv fn-left\"]").find("a")) {
            let type_name = $(navElement).text()
            let type_id = navElement.attribs.href
            extend_dic["value"].push(this.getFliterDic(type_name, type_id))
        }
        if (extend_dic["value"].length > 1) {
            extend_list.push(extend_dic)
        }
        return extend_list
    }

    async setClasses() {
        let $ = await this.getHtml()
        let navElements = $("[class=\"nav-item drop-down \"]")
        this.classes = []
        for (const navElement of navElements) {
            let element = $(navElement).find("a")[0]
            let type_name = $(element).text()
            let type_id = element.attribs.href
            if (type_name === this.removeKey) {
                this.classes.push(this.getTypeDic(type_name, type_id))
                this.filterObj[type_id] = await this.getFilter(type_id)
            }
        }
    }

    async setCategory(tid, pg, filter, extend) {
        let classes = this.getExtend(extend) ?? tid
        let url
        if (parseInt(pg) === 1) {
            url = this.siteUrl + classes
        } else {
            url = this.siteUrl + classes + `index${pg}.html`
        }
        let $ = await this.getHtml(url)
        this.vodList = await this.parseVodShortListFromDoc($)
    }

}

let spider = new LoveMovie18Spider()

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