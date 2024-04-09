/*
* @File     : jiujiuliu.js
* @Author   : jade
* @Date     : 2024/1/4 14:15
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 996影视
*/

import {Spider} from "./spider.js";
import {_, Crypto, load} from "../lib/cat.js";
import {VodDetail, VodShort} from "../lib/vod.js";
import * as Utils from "../lib/utils.js";

class JiuJiuLiuSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://www.cs1369.com"
    }

    getName() {
        return "🥃┃九九六影视┃🥃"
    }

    getAppName() {
        return "九九六影视"
    }
    getJSName() {
        return "jiujiuliu"
    }

    getType() {
        return 3
    }

    async parseVodShortListFromDoc($) {
        let vod_list = []
        let vodElements = $("[class=\"stui-vodlist clearfix\"]").find("li")
        for (const vodElement of vodElements) {
            let resource = $(vodElement).find("[class=\"stui-vodlist__thumb lazyload\"]")[0]
            let vodShort = new VodShort()
            vodShort.vod_id = resource.attribs["href"]
            vodShort.vod_name = resource.attribs["title"]
            vodShort.vod_pic = resource.attribs["data-original"]
            vodShort.vod_remarks = $($(resource).find("[class=\"pic-text text-right\"]")[0]).text()
            vod_list.push(vodShort)
        }
        return vod_list
    }


    async parseVodShortListFromDocBySearch($) {
        let vod_list = []
        let vodElements = $("[class=\"stui-pannel_bd\"]").find("li")
        for (const vodElement of vodElements) {
            let resource = $($(vodElement).find("[class=\"thumb\"]")[0]).find("a")[0]
            let vodShort = new VodShort()
            vodShort.vod_id = resource.attribs["href"]
            vodShort.vod_name = resource.attribs["title"]
            vodShort.vod_pic = resource.attribs["data-original"]
            vodShort.vod_remarks = Utils.getStrByRegex(/类型：(.*?)地区/, $($(vodElement).find("[class=\"hidden-mi\"]")[0]).text())
            vod_list.push(vodShort)
        }
        return vod_list

    }

    async parseVodDetailFromDoc($) {
        let vodDetail = new VodDetail()
        let vodElement = $("[class=\"col-pd clearfix\"]")[1]
        let vodShortElement = $(vodElement).find("[class=\"stui-content__thumb\"]")[0]
        let vodItems = []
        for (const playElement of $("[class=\"stui-content__playlist clearfix\"]").find("a")) {
            let episodeUrl = this.siteUrl + playElement.attribs["href"];
            let episodeName = $(playElement).text();
            vodItems.push(episodeName + "$" + episodeUrl);
        }
        vodDetail.vod_name = $(vodShortElement).find("[class=\"stui-vodlist__thumb picture v-thumb\"]")[0].attribs["title"]
        vodDetail.vod_pic = $(vodShortElement).find("img")[0].attribs["data-original"]
        vodDetail.vod_remarks = $($(vodShortElement).find("[class=\"pic-text text-right\"]")[0]).text()
        let data_str = $($(vodElement).find("[class=\"data\"]")).text().replaceAll(" ", " ")
        vodDetail.type_name = Utils.getStrByRegex(/类型：(.*?) /, data_str)
        vodDetail.vod_area = Utils.getStrByRegex(/地区：(.*?) /, data_str)
        vodDetail.vod_year = Utils.getStrByRegex(/年份：(.*?) /, data_str)
        vodDetail.vod_actor = Utils.getStrByRegex(/主演：(.*?) /, data_str)
        vodDetail.vod_director = Utils.getStrByRegex(/导演：(.*?) /, data_str)
        vodDetail.vod_content = $($("[class=\"stui-pannel_bd\"]").find("[class=\"col-pd\"]")).text()
        vodDetail.vod_play_from = ["996"].join("$$$")
        vodDetail.vod_play_url = [vodItems.join("#")].join("$$$")
        return vodDetail
    }

    async setClasses() {
        let html = await this.fetch(this.siteUrl, null, this.getHeader())
        if (html !== null) {
            let $ = load(html)
            let menuElements = $("[class=\"stui-header__menu type-slide\"]").find("a")
            for (const menuElement of menuElements) {
                let type_dic = {
                    "type_name": $(menuElement).text(),
                    "type_id": "/show/id/" + menuElement.attribs["href"].split("/").slice(-1)[0].split(".")[0]
                }
                if ($(menuElement).text() !== "首页") {
                    this.classes.push(type_dic)
                }

            }
        }
    }

    async getFilter($) {
        let hdElements = $("[class=\"stui-pannel_hd\"]")
        let extend_list = []
        let index = 0
        for (let i = 0; i < 2; i++) {
            let cateElemet = hdElements[i]
            let typeElements = $(cateElemet).find("ul")
            if (i === 0) {
                for (const typeElement of typeElements) {
                    let extend_dic = {
                        "key": (index + 1).toString(), "name": $($(typeElement).find("li")[0]).text(), "value": []
                    }
                    for (const ele of $(typeElement).find("li").slice(1)) {
                        if (!_.isEmpty($(ele).text())) {
                            if (index === 0) {
                                extend_dic["value"].push({
                                    "n": $(ele).text(),
                                    "v": $(ele).find("a")[0].attribs["href"].split("/").slice(-1)[0].split(".")[0]
                                })
                            } else {
                                extend_dic["value"].push({"n": $(ele).text(), "v": $(ele).text()})
                            }
                        }
                    }
                    extend_list.push(extend_dic)
                    index = index + 1
                }
            } else {
                let extend_dic = {
                    "key": (index + 1).toString(), "name": $($(cateElemet).find("li")[0]).text(), "value": []
                }
                extend_dic["value"].push({"n": "全部", "v": "time"})
                for (const ele of $(cateElemet).find("li").slice(1)) {
                    if (!_.isEmpty($(ele).text())) {
                        extend_dic["value"].push({
                            "n": $(ele).text(), "v": $(ele).find("a")[0].attribs["href"].split("/")[3]
                        })
                    }
                }
                extend_list.push(extend_dic)
            }
        }
        return extend_list
    }

    async setFilterObj() {
        for (const type_dic of this.classes) {
            let type_id = type_dic["type_id"]
            if (type_id !== "/" && type_id !== "最近更新") {
                let url = this.siteUrl + type_id + ".html"
                let html = await this.fetch(url, null, this.getHeader())
                if (html != null) {
                    let $ = load(html)
                    this.filterObj[type_id] = await this.getFilter($)
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

    getParams(params, value) {
        let x = value ?? "全部"
        if (x === "全部" || x === undefined) {
            return ""
        } else {
            return params + value
        }

    }

    async setCategory(tid, pg, filter, extend) {
        let typeName = this.getParams("/id/", extend["1"])
        if (_.isEmpty(typeName)) {
            typeName = "/id/" + tid.split("/").slice(-1)[0]
        }
        let plot = this.getParams("/class/", extend["2"])
        let area = this.getParams("/area/", extend["3"])
        let year = this.getParams("/year/", extend["4"])
        let language = this.getParams("/lang/ ", extend["5"])
        let letter = this.getParams("/letter/ ", extend["6"])
        let time = this.getParams("/by/", extend["7"])
        let cateUrl = this.siteUrl + `/show${area}${time}${plot}${typeName}${language}${letter}${year}/page/${pg.toString()}.html`
        await this.jadeLog.info(`类别URL为:${cateUrl}`)
        this.limit = 36
        let html = await this.fetch(cateUrl, null, this.getHeader())
        if (html != null) {
            let $ = load(html)
            this.vodList = await this.parseVodShortListFromDoc($)
        }
    }

    async setDetail(id) {
        let detailUrl = this.siteUrl + id
        let html = await this.fetch(detailUrl, null, this.getHeader())
        if (html != null) {
            let $ = load(html)
            this.vodDetail = await this.parseVodDetailFromDoc($)
        }
    }

    async setSearch(wd, quick) {
        let searchUrl = this.siteUrl + `/search.html?wd=${wd}`
        let html = await this.fetch(searchUrl, null, this.getHeader())
        if (html != null) {
            let $ = load(html)
            this.vodList = await this.parseVodShortListFromDocBySearch($)
        }

        let x = 0

    }

    async setPlay(flag, id, flags) {
        let html = await this.fetch(id, null, this.getHeader())
        if (html !== null) {
            let matcher = Utils.getStrByRegex(/player_aaaa=(.*?)<\/script>/, html)
            let player = JSON.parse(matcher);
            try {
                this.playUrl = decodeURIComponent(Crypto.enc.Utf8.stringify(Crypto.enc.Base64.parse(player["url"])))
                this.header = this.getHeader()
            } catch (e) {
                this.playUrl = player["url"]
            }
        }
    }
}

let spider = new JiuJiuLiuSpider()

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