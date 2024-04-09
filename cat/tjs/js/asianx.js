/*
 * @Author: samples jadehh@live.com
 * @Date: 2023-12-14 11:03:04
 * @LastEditors: samples jadehh@live.com
 * @LastEditTime: 2023-12-14 11:03:04
 * @FilePath: js/asianx.js
 * @Description: asianx
 */


import {Spider} from "./spider.js";
import {Crypto, _, load} from "../lib/cat.js";
import {VodDetail, VodShort} from "../lib/vod.js";
import * as Utils from "../lib/utils.js";

class AsianXSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://cn.asianx.tube/"
    }


    getName() {
        return "🔞┃海外宅┃🔞"
    }

    getAppName() {
        return "海外宅"
    }
    getJSName() {
        return "asianx"
    }

    getType() {
        return 3
    }

    async getFilter($) {
        let navElements = $($("[class=\"menu m-0 mb-2 mb-lg-0\"]")).find("a").slice(6)
        let extend_dic = {"key": "1", "name": "分类", "value": [{"n": "全部", "v": "全部"}]}
        for (const navElement of navElements) {
            let type_name = $($(navElement).find("span")).text()
            let type_id = navElement.attribs["href"]
            extend_dic["value"].push({"n": type_name, "v": type_id})
        }
        return [extend_dic]
    }

    async parseVodShortListFromDoc($,is_home=false) {
        let vod_list = []
        let vodShortElements;
        if (is_home){
             vodShortElements = $($("[class=\"gal-box\"]")).slice(12)
        }else{
            vodShortElements = $($("[class=\"gal-box\"]"))
        }
        for (const vodShortElement of vodShortElements) {
            let vodShort = new VodShort()
            let vodElements = $(vodShortElement).find("a")
            vodShort.vod_id = vodElements[0].attribs["href"]
            vodShort.vod_pic = $(vodElements[0]).find("img")[0].attribs["data-src"]
            vodShort.vod_name = vodElements[1].attribs["title"]
            vodShort.vod_remarks = $($(vodShortElement).find("[class=\"meta text-muted text-truncate\"]")).text()
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodDetailFromDoc(html) {
        let vodDetail = new VodDetail();
        let content = Utils.getStrByRegex(/<script type="application\/ld\+json">(.*?)<\/script>/,html)
        let content_json = JSON.parse(content)
        let textList =  content_json["name"].split(" ")
        vodDetail.vod_name = textList[0]
        vodDetail.vod_play_from = ["未加密线路","加密线路"].join("$$$")
        let playUrl1 =  content_json["contentUrl"]
        let playUrl2 =  content_json["embedUrl"]
        vodDetail.vod_play_url = [`${textList[0]}$${playUrl1}`,`${textList[0]}$${playUrl2}`].join("$$$")
        vodDetail.vod_remarks = content_json["uploadDate"]
        vodDetail.vod_content = content_json["description"]
        return vodDetail
    }

    async setClasses() {
        this.classes = []
        this.classes.push({"type_name": "首页", "type_id": "/"})
        let html = await this.fetch(this.siteUrl, null, this.getHeader())
        if (!_.isEmpty(html)) {
            let $ = load(html)
            let navElements = $($("[class=\"menu m-0 mb-2 mb-lg-0\"]")).find("a").slice(0, 5)
            for (const navElement of navElements) {
                let type_name = $($(navElement).find("span")).text()
                let type_id = navElement.attribs["href"]
                this.classes.push({"type_name": type_name, "type_id": type_id})
            }
            this.filterObj[this.classes[0].type_id] = await this.getFilter($)
        }
    }

    async setHomeVod() {
        let html = await this.fetch(this.siteUrl, null, this.getHeader())
        if (!_.isEmpty(html)) {
            let $ = load(html)
            this.homeVodList = await this.parseVodShortListFromDoc($,true)
        }
    }


    getExtend(pg,extend){
        if (extend["1"] !== undefined){
            if (extend["1"] === "全部"){
                return this.siteUrl
            }else{
                return this.siteUrl + extend["1"] + "/" + pg
            }
        }else{
            return this.siteUrl
        }
    }

    async setDetail(id) {
        let html = await this.fetch(id,null,this.getHeader())
        if (!_.isEmpty(html)){
            this.vodDetail = await this.parseVodDetailFromDoc(html)
        }
    }
    async setCategory(tid, pg, filter, extend) {
        let url;
        if (tid === "/") {
            url = this.getExtend(pg,extend)
        } else {
            url = this.siteUrl + tid + "/" + pg
        }
        let html = await this.fetch(url, null, this.getHeader())
            if (!_.isEmpty(html)) {
                let $ = load(html)
                this.vodList = await this.parseVodShortListFromDoc($,false)
            }
    }
}

let spider = new AsianXSpider()

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