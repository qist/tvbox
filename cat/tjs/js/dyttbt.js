/*
* @File     : freeok.js
* @Author   : jade
* @Date     : 2024/1/19 10:26
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 电影天堂(已失效)
*/
import {_, load} from '../lib/cat.js';
import {VodDetail, VodShort} from "../lib/vod.js"
import * as Utils from "../lib/utils.js";
import {Spider} from "./spider.js";


class DyttSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://www.dy2018.com"
        this.dyttReconnectTimes = 0

    }

    getName() {
        return `👼┃电影天堂BT┃👼`
    }

    getAppName() {
        return "电影天堂BT"
    }
    getJSName() {
        return "dyttbt"
    }

    getType() {
        return 3
    }

    // getHeader() {
    //      return {"User-Agent": "PostmanRuntime/7.36.1", "Host":"www.dy2018.com"};
    // }

    async getHtml(url = this.siteUrl, headers = this.getHeader()) {
        try {
            let buffer = await this.fetch(url, null, headers, false, false, 1)
            let html = Utils.decode(buffer, "gb2312")
            if (!_.isEmpty(html) && Utils.getStrByRegex(/<script src="(.*?)"><\/script>/, html) !== "/_guard/auto.js") {
                return load(html)
            } else {
                if (this.dyttReconnectTimes < this.maxReconnectTimes) {
                    Utils.sleep(2)
                    this.dyttReconnectTimes = this.dyttReconnectTimes + 1
                    return await this.getHtml(url, headers)
                } else {
                    await this.jadeLog.error(`html获取失败`, true)
                }
            }
        } catch (e) {
            await this.jadeLog.error(`获取html出错,出错原因为${e}`)
        }

    }


    async setFilterObj() {

    }

    async setClasses() {
        let $ = await this.getHtml()
        let vodShortElements = $("[class=\"title_all\"]")
        for (const vodShortElement of vodShortElements) {
            let spanElement = $(vodShortElement).find("span")[0]
            let aElement = $(vodShortElement).find("a")[0]
            let type_name = $(spanElement).text()
            let type_id = aElement.attribs["href"]
            if (type_id.indexOf("https:") === -1 && type_id.indexOf("http:") === -1) {
                type_id = this.siteUrl + type_id
            }
            this.classes.push(this.getTypeDic(type_name, type_id))
        }
        let containElements = $($("[id=\"menu\"]").find("[class=\"contain\"]")).find("a").slice(0, -3)
        for (const contaElement of containElements) {
            let type_name = $(contaElement).text()
            let type_id = contaElement.attribs["href"]
            if (type_id.indexOf("https:") === -1 && type_id.indexOf("http:") === -1) {
                type_id = this.siteUrl + type_id
            }
            this.classes.push(this.getTypeDic(type_name, type_id))
        }
    }

    async parseVodShortListFromDocByCategory($) {
        let vod_list = []
        let vodShortElements = $($("[class=\"co_content8\"]")[0]).find("tbody")
        for (const vodShortElement of vodShortElements) {
            let vodShort = new VodShort()
            let vodElements = $(vodShortElement).find("tr")
            vodShort.vod_name = Utils.getStrByRegex(/《(.*?)》/, $(vodElements[1]).text())
            vodShort.vod_id = $(vodElements[1]).find("a").slice(-1)[0].attribs.href
            vodShort.vod_remarks = "日期:" + Utils.getStrByRegex(/日期：(.*?) /, $(vodElements[2]).text()) + " 热度:" + Utils.getStrByRegex(/点击：(.*?) /, $(vodElements[2]).text())
            vodShort.vod_pic = Utils.RESOURCEURL + "/resources/dytt.jpg"
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodShortListFromDoc($) {
        let vod_list = []
        let vodShortElements = $($("[class=\"co_area2\"]")[0]).find("li").slice(1)
        for (const vodShortElement of vodShortElements) {
            let vodShort = new VodShort()
            let vodElement = $(vodShortElement).find("a")[0]
            vodShort.vod_id = vodElement.attribs["href"]
            vodShort.vod_name = Utils.getStrByRegex(/《(.*?)》/, vodElement.attribs["title"])
            vodShort.vod_remarks = $($(vodShortElement).find("span")).text().replaceAll("", "")
            vodShort.vod_pic = Utils.RESOURCEURL + "/resources/dytt.jpg"
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodDetailFromDoc($) {
        let vodDetail = new VodDetail()
        vodDetail.vod_name = Utils.getStrByRegex(/《(.*?)》/, Utils.getStrByRegex(/<title>(.*?)<\/title>/, $.html()))
        let zoomElement = $("[id=\"Zoom\"]")
        vodDetail.vod_pic = $(zoomElement).find("img")[0].attribs.src
        let content = $(zoomElement).text()
        vodDetail.vod_year = Utils.getStrByRegex(/年　　代　(.*?)◎/, content)
        vodDetail.type_name = Utils.getStrByRegex(/类　　别　(.*?)◎/, content)
        vodDetail.vod_area = Utils.getStrByRegex(/产　　地　(.*?)◎/, content)
        vodDetail.vod_director = Utils.getStrByRegex(/导　　演　(.*?)◎/, content)
        vodDetail.vod_content = Utils.getStrByRegex(/简　　介　(.*?)◎/, content)
        vodDetail.vod_actor = Utils.getStrByRegex(/主　　演(.*?)◎/, content).replaceAll("　　　　　　", "*")
        vodDetail.vod_remarks = Utils.getStrByRegex(/豆瓣评分　(.*?)\//, content)
        vodDetail.vod_play_from = "磁力链接"
        let playList = $(zoomElement).find("[class=\"player_list\"]").find("a")
        let vodItems = []
        for (const playEle of playList) {
            vodItems.push($(playEle).text() + "$" + playEle.attribs.href);
        }
        vodDetail.vod_play_url = [vodItems.join("#")].join("$$$")
        return vodDetail
    }

    async setHomeVod() {
        let $ = await this.getHtml()
        this.homeVodList = await this.parseVodShortListFromDoc($)
    }

    async setCategory(tid, pg, filter, extend) {
        let cateUrl = tid
        if (tid.indexOf("index") > -1){
            cateUrl = tid.split(".html")[0] + "_" + pg + ".html"
        }
        let $ = await this.getHtml(cateUrl)
        this.vodList = await this.parseVodShortListFromDocByCategory($)
    }

    async setDetail(id) {
        let $ = await this.getHtml(this.siteUrl + id)
        this.vodDetail = await this.parseVodDetailFromDoc($)
    }


}

let spider = new DyttSpider()

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
        proxy: proxy,
        search: search,
    };
}
export {spider}