/*
* @File     : aliyunpanshare.js
* @Author   : jade
* @Date     : 2024/1/26 13:06
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 阿里云盘分享
*/
import {_, load} from '../lib/cat.js';
import {VodDetail, VodShort} from "../lib/vod.js"
import {detailContent, initAli, playContent} from "../lib/ali.js";
import * as Utils from "../lib/utils.js";
import {Spider} from "./spider.js";
import {patternAli} from "../lib/utils.js";

let remark_list = ["4k", "4K"]

class AliyunpanShare extends Spider {
    constructor() {
        super();
        this.siteUrl = 'https://www.alypw.com';
    }

    async init(cfg) {
        await super.init(cfg);
        await initAli(this.cfgObj["token"]);
    }

    getName() {
        return "🥏‍┃阿里云盘分享┃🥏‍"
    }

    getAppName() {
        return "阿里云盘分享"
    }

    getJSName() {
        return "aliyunpanshare"
    }

    getType() {
        return 3
    }

    getRemarks(name, title) {
        if (_.isEmpty(name)) {
            for (const remark of remark_list) {
                if (title.indexOf(remark) > -1) {
                    return remark
                }
            }
        } else {
            return name
        }
    }

    parseVodName(name) {
        let vod_name = Utils.getStrByRegex(/\[阿里云盘](.*?) /, name)
        if (name.indexOf("合集") > -1) {
            return ""
        }
        if (_.isEmpty(vod_name)) {
            vod_name = Utils.getStrByRegex(/\[阿里云盘](.*?)（/, name)
        }
        if (vod_name.indexOf("[") > -1) {
            vod_name = vod_name.split("[")[0]
        }
        if (vod_name.indexOf("【") > -1) {
            vod_name = vod_name.split("【")[0]
        }
        if (vod_name === "4K") {
            return ""
        }
        return vod_name
    }

    async parseVodShortListFromDoc($) {
        let vod_list = []
        let vodElements = $($("[class=\"hometab\"]").find("[class=\"box\"]")).find("li")
        for (const vodElement of vodElements) {
            let ele = $(vodElement).find("[class=\"imgr\"]")[0]
            let vodShort = new VodShort();
            vodShort.vod_id = $(ele).find("a")[0].attribs["href"]
            let name = $(ele).find("a")[0].attribs["title"]
            vodShort.vod_name = this.parseVodName(name)
            vodShort.vod_pic = $(vodElement).find("img")[0].attribs["src"]
            vodShort.vod_remarks = this.getRemarks(Utils.getStrByRegex(/【(.*?)】/, name), name)
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodShortListFromDocByCategory($) {
        let vod_list = []
        let mainElement = $("[class=\"main container\"]")
        let vodElements = $($(mainElement).find("[class=\"list\"]")).find("li")
        if (vodElements.length === 0) {
            vodElements = $(mainElement).find("li")
        }
        for (const vodElement of vodElements) {
            let name = $(vodElement).find("img")[0].attribs["alt"].replaceAll("<strong>", "").replaceAll("</strong>", "")
            let vodShort = new VodShort();
            vodShort.vod_id = $(vodElement).find("a")[0].attribs["href"]
            vodShort.vod_name = this.parseVodName(name)
            vodShort.vod_pic = $(vodElement).find("img")[0].attribs["src"]
            vodShort.vod_remarks = this.getRemarks(Utils.getStrByRegex(/【(.*?)】/, name), name)
            if (!_.isEmpty(vodShort.vod_name)) {
                vod_list.push(vodShort)
            }
        }
        return vod_list
    }

    async parseVodDetailFromDoc($) {
        let mainElements = $("[class=\"mainl\"]")
        let name = $($(mainElements).find("[class=\"title\"]")[0]).text()
        let vodDetail = new VodDetail();
        vodDetail.vod_name = Utils.getStrByRegex(/\[阿里云盘](.*?) /, name)
        vodDetail.vod_remarks = this.getRemarks(Utils.getStrByRegex(/【(.*?)】/, name), name)
        let articleElement = $(mainElements).find("[class=\"article_content\"]")
        vodDetail.vod_pic = $(articleElement).find("p>img")[0].attribs["src"]
        let articleElements = $(articleElement).find("p")
        let articleContent = ""
        for (const articleEle of articleElements) {
            articleContent = articleContent + $(articleEle).text() + "\n"
        }
        let share_ali_url_list = []
        let share_url_list = Utils.getStrByRegex(Utils.patternAli, articleContent).split("\n")
        for (const share_url of share_url_list) {
            let matches = share_url.match(Utils.patternAli);
            if (!_.isEmpty(matches)) share_ali_url_list.push(matches[1])
        }
        let aliVodDetail = await detailContent(share_ali_url_list)
        vodDetail.vod_play_url = aliVodDetail.vod_play_url
        vodDetail.vod_play_from = aliVodDetail.vod_play_from
        vodDetail.type_name = Utils.getStrByRegex(/标签(.*?)\n/, articleContent).replaceAll("：", "")
        vodDetail.vod_content = Utils.getStrByRegex(/描述(.*?)\n/, articleContent).replaceAll("：", "")
        return vodDetail
    }

    async setClasses() {
        let $ = await this.getHtml()
        let typeElements = $("[id^='navbar-category']").find("a")
        let key_list = ["影", "剧", "4K", "视", "音", "演", "动漫"]
        for (const typeElement of typeElements) {
            let type_name = $(typeElement).text()
            let type_id = typeElement.attribs["href"]
            let is_show = false
            for (const key of key_list) {
                if (type_name.indexOf(key) > -1) {
                    is_show = true
                }
            }
            if (is_show) {
                this.classes.push(this.getTypeDic(type_name, type_id))
            }
        }
    }


    async setHomeVod() {
        let $ = await this.getHtml()
        this.homeVodList = await this.parseVodShortListFromDoc($)
    }

    async setCategory(tid, pg, filter, extend) {
        let cateUrl = tid.split(".html")[0] + "_" + pg + ".html"
        let $ = await this.getHtml(cateUrl)
        this.vodList = await this.parseVodShortListFromDocByCategory($)
    }

    async setDetail(id) {
        let $ = await this.getHtml(id)
        this.vodDetail = await this.parseVodDetailFromDoc($)
    }

    async setPlay(flag, id, flags) {
        let playObjStr = await playContent(flag, id, flags);
        this.playUrl = JSON.parse(playObjStr)["url"]
    }

    async setSearch(wd, quick) {
        let url = this.siteUrl + `/search.php?q=${wd}`
        let $ = await this.getHtml(url)
        this.vodList = await this.parseVodShortListFromDocByCategory($)
    }

}

let spider = new AliyunpanShare()

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