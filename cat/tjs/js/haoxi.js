/*
* @File     : haoxi.js
* @Author   : jade
* @Date     : 2024/2/7 14:24
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 好戏追剧 已失效
*/
import {VodDetail, VodShort} from "../lib/vod.js"
import * as Utils from "../lib/utils.js";
import {Spider} from "./spider.js";

class HaoXiSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://haoxi.vip"
    }

    getAppName() {
        return `好戏追剧`
    }

    getName() {
        return `🌿┃好戏追剧┃🌿`
    }
    getJSName() {
        return "haoxi"
    }

    getType() {
        return 3
    }
    parseVodShortFromElement($, element) {
        let vodShort = new VodShort();
        vodShort.vod_id = $(element).find("a")[0].attribs.href
        vodShort.vod_name = $(element).find("a")[0].attribs.title
        if (vodShort.vod_name === undefined) {
            vodShort.vod_name = $($($(element).find("[class=\"thumb-txt cor4 hide\"]")).find("a")).html()
        }
        vodShort.vod_pic = $(element).find("img")[0].attribs["data-src"]
        vodShort.vod_remarks = $($(element).find("[class=\"public-list-prb hide ft2\"]")).html()
        return vodShort
    }

    async parseVodShortListFromDoc($) {
        let vod_list = []
        let vodElements = $("[class=\"flex bottom4\"]").find("[class=\"public-list-box public-pic-a [swiper]\"]")
        for (const vodElement of vodElements) {
            let vodShort = this.parseVodShortFromElement($, vodElement)
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodShortListFromDocByCategory($) {
        let vod_list = []
        let vodElements = $("[class=\"public-list-box public-pic-b [swiper]\"]")
        for (const vodElement of vodElements) {
            let vodShort = this.parseVodShortFromElement($, vodElement)
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodShortListFromDocBySearch($) {
        let vod_list = []
        let vodElements = $("[class=\"public-list-box search-box flex rel\"]")
        for (const vodElement of vodElements) {
            let vodShort = this.parseVodShortFromElement($, vodElement)
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodDetailFromDoc($) {
        let vodDetailElement = $("[class=\"vod-detail style-detail rel cor1 hader0\"]")
        let vodDetail = new VodDetail();
        vodDetail.vod_pic = $(vodDetailElement).find("img")[0].attribs.src
        vodDetail.vod_name = $($(vodDetailElement).find("[class=\"slide-info-title hide\"]")).html()
        let elements = $(vodDetailElement).find("[class=\"slide-info hide\"]")
        vodDetail.vod_year = $($($(elements[0]).find("[class=\"slide-info-remarks\"]")[0]).find("a")[0]).html()
        vodDetail.vod_area = $($($(elements[0]).find("[class=\"slide-info-remarks\"]")[1]).find("a")[0]).html()
        vodDetail.type_name = $($($(elements[0]).find("[class=\"slide-info-remarks\"]")[2]).find("a")[0]).html()
        vodDetail.vod_remarks = $(elements[1]).text().replaceAll("备注 :", "")
        vodDetail.vod_director = $(elements[2]).text().replaceAll("导演 :", "")
        vodDetail.vod_actor = $(elements[3]).text().replaceAll("演员 :", "")
        vodDetail.vod_content = $($("[class=\"text cor3\"]")).text()
        let playElements = $("[class=\"box-width cor5\"]")
        let playFormatElements = playElements.find("[class=\"swiper-slide\"]")
        let playUrlElements = playElements.find("[class=\"anthology-list-box none\"]")
        let vod_play_from_list = []
        let vod_play_list = []
        for (let i = 0; i < playFormatElements.length; i++) {
            let playFormatElement = playFormatElements[i]
            let format_name = playFormatElement.children[1].data
            format_name = format_name.replaceAll(" ", "")
            vod_play_from_list.push(format_name)
            let vodItems = []
            if (format_name === "http下载") {
                for (const playUrlElement of $(playUrlElements[i]).find("a")) {
                    let episodeName = $(playUrlElement).text()
                    let episodeUrl = playUrlElement.attribs.href
                    if (episodeName !== "复制地址") {
                        vodItems.push(episodeName + "$" + episodeUrl)
                    }
                }
            } else {
                for (const playUrlElement of $(playUrlElements[i]).find("a")) {
                    let episodeName = $(playUrlElement).text()
                    let episodeUrl = playUrlElement.attribs.href
                    vodItems.push(episodeName + "$" + episodeUrl)
                }
            }
            vod_play_list.push(vodItems.join("#"))

        }
        vodDetail.vod_play_from = vod_play_from_list.join("$$$")
        vodDetail.vod_play_url = vod_play_list.join("$$$")
        return vodDetail
    }

    async setClasses() {
        let $ = await this.getHtml()
        let navElements = $("[class=\"head flex between no-null header_nav0\"]").find("li")
        for (const navElement of navElements) {
            let type_name = $($(navElement).find("a")).text()
            let type_id = Utils.getStrByRegex(/\/vodtype\/(.*?)\//, $(navElement).find("a")[0].attribs.href)
            if (Utils.isNumeric(type_id)) {
                this.classes.push(this.getTypeDic(type_name, type_id))
            }
        }
    }

    async getFilter($) {
        let elements = $("[class=\"nav-swiper rel\"]")
        let extend_list = []
        for (let i = 0; i < elements.length; i++) {
            let extend_dic = {"key": (i + 1).toString(), "name": "", "value": []}
            let name = $($($(elements[i]).find("[class=\"filter-text bj cor5\"]")[0]).find("span")).html()
            if (name !== "已选" && name !== "频道") {
                extend_dic["name"] = name
                for (const ele of $(elements[i]).find("li")) {
                    extend_dic["value"].push({"n": $(ele).text(), "v": $(ele).text()})
                }
                extend_list.push(extend_dic)
            }
        }
        let sortElments = $("[class=\"site-tabs b-b br\"]")
        let extend_dic = {"key": (elements.length + 1).toString(), "name": "排序", "value": []}
        extend_dic["value"].push({"n": "全部", "v": "/"})
        for (const ele of $(sortElments).find("a")) {
            let type_id_list = ele.attribs.href.split("-")
            extend_dic["value"].push({"n": $(ele).text(), "v": type_id_list[2]})
        }
        extend_list.push(extend_dic)

        return extend_list
    }


    async setFilterObj() {
        for (const class_dic of this.classes) {
            let type_id = class_dic["type_id"]
            if (Utils.isNumeric(type_id)) {
                let url = this.siteUrl + `/vodshow/${type_id}-----------`
                let $ = await this.getHtml(url)
                this.filterObj[type_id] = await this.getFilter($)
            }
        }
    }

    async setHomeVod() {
        let $ = await this.getHtml()
        this.homeVodList = await this.parseVodShortListFromDoc($)
    }

    get_extend_sort_dic(tid) {
        return {
            "3": 3, "4": 1, "5": 11, "6": 4, "9": 5, "10": 2,
        }
    }

    async setCategory(tid, pg, filter, extend) {
        // "1-大陆-hits-Netflix-英语-A----正片--2023/version/4K/"
        let urlParams = [tid.toString(), "", "", "", "", "", "", "", pg.toString(), "", "", ""]
        let extend_dic = this.get_extend_sort_dic(parseInt(tid))
        for (const key of Object.keys(extend_dic)) {
            if (extend[key] === "0") {
                urlParams[extend_dic[key]] = ""
            } else {
                if (extend[key] !== "全部") {
                    urlParams[extend_dic[key]] = extend[key]
                }
            }
        }
        let reqUrl = this.siteUrl + '/vodshow/' + urlParams.join("-");
        if (extend[7] !== undefined && extend[7] !== "全部") {
            reqUrl = reqUrl + `/version/${extend[7]}/`
        }
        await this.jadeLog.debug(`分类URL:${reqUrl}`)
        let $ = await this.getHtml(reqUrl)
        this.vodList = await this.parseVodShortListFromDocByCategory($)
    }

    async setDetail(id) {
        let $ = await this.getHtml(this.siteUrl + id)
        this.vodDetail = await this.parseVodDetailFromDoc($)
    }

    async setSearch(wd, quick) {
        let $ = await this.getHtml(this.siteUrl + `/vodsearch/-------------/?wd=${wd}`)
        this.vodList = await this.parseVodShortListFromDocBySearch($)
    }

    async setPlay(flag, id, flags) {
        if (flag !== "http下载") {
            let $ = await this.getHtml(this.siteUrl + id)
            let playConfig = JSON.parse(Utils.getStrByRegex(/var player_aaaa=(.*?)<\/script>/, $.html()))
            this.playUrl = playConfig['url']
        } else {
            this.playUrl = id
        }
    }

}

let spider = new HaoXiSpider()

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