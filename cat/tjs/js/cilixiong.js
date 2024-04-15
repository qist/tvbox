/*
* @File     : cilixiong.js
* @Author   : jade
* @Date     : 2024/4/13 14:52
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/
import {_, load} from '../lib/cat.js';
import {VodDetail, VodShort} from "../lib/vod.js"
import * as Utils from "../lib/utils.js";
import {Spider} from "./spider.js"

class CiliXiongSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://www.cilixiong.com"
        this.cateObj = {"/movie/": "1", "/drama/": "2"}
    }

    getAppName() {
        return "磁力熊"
    }

    getName() {
        return "🐻┃磁力熊┃🐻"
    }

    getJSName() {
        return "cilixiong"
    }

    getType() {
        return 3
    }

    async setClasses() {
        let $ = await this.getHtml()
        let navElements = $("[class=\"nav col-12 col-lg-auto me-lg-auto mb-2 justify-content-center mb-md-0\"]").find("li")
        for (const navElement of navElements) {
            let element = $(navElement).find("a")[0]
            let type_name = $(element).text()
            let type_id = element.attribs.href
            if (type_name !== "首页" && type_name !== "榜单" && type_name !== "留言") {
                this.classes.push(this.getTypeDic(type_name, type_id))
            }
        }
    }

    async getFilter($) {
        let extend_list = []
        let filerElements = $("[class=\"nav small\"]")
        let i = 1
        for (const filetElement of filerElements) {
            let extend_name = $($(filetElement).find("li")[0]).text().replaceAll("：", "")
            let extend_dic = {"key": (i).toString(), "name": extend_name, "value": []}
            for (const typeElement of $(filetElement).find("li").slice(1)) {
                let element = $(typeElement).find("a")[0]
                let type_id = element.attribs.href.split("-")[i]
                extend_dic["value"].push({"n": $(element).text(), "v": type_id})
            }
            i = i + 1
            extend_list.push(extend_dic)
        }
        return extend_list
    }

    async setFilterObj() {
        for (const type_dic of this.classes) {
            let type_id = type_dic["type_id"]
            if (type_id !== "最近更新") {
                let $ = await this.getHtml(this.siteUrl + type_id)
                this.filterObj[type_id] = await this.getFilter($)
            }
        }
    }

    async parseVodShortListFromDoc($) {
        let vod_list = []
        let vodElements = $("[class=\"col\"]")
        for (const vodElement of vodElements) {
            let vodShort = new VodShort()
            vodShort.vod_id = $(vodElement).find("a")[0].attribs.href
            vodShort.vod_pic = Utils.getStrByRegex(/background-image: url\('(.*?)'\)/, $(vodElement).find("[class=\"card-img\"]")[0].attribs["style"])
            vodShort.vod_name = $($(vodElement).find("h2")).text()
            let remarks = $($(vodElement).find("[class=\"rank bg-success p-1\"]")).text()
            vodShort.vod_remarks = "评分:" + remarks
            if (remarks !== "AD") {
                vod_list.push(vodShort)
            }

        }
        return vod_list
    }

    async parseVodShortListFromDocBySearch($) {
        let vod_list = []
        let vodElements = $("[class=\"card card-cover h-100 overflow-hidden text-bg-dark rounded-4 shadow-lg position-relative\"]")
        for (const  vodElement of vodElements){
            let vodShort= new VodShort()
            vodShort.vod_id = $(vodElement).find("a")[0].attribs.href
            vodShort.vod_name = $($(vodElement).find("[class=\"pt-5 lh-1 pb-2 h4\"]")).text()
            vodShort.vod_pic = Utils.getStrByRegex(/background-image: url\('(.*?)'\)/,$(vodElement).find("[class=\"card-img\"]")[0].attribs.style)
            vodShort.vod_remarks = "评分:" +  $($(vodElement).find("[class=\"rank bg-success p-1\"]")).text()
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodDetailFromDoc($) {
        let vodDetail = new VodDetail()
        let vodDetailElement = $("[class=\"row row-cols-1 row-cols-lg-3 align-items-stretch g-4 p-5 text-white\"]")
        vodDetail.vod_pic = $(vodDetailElement).find("img")[0].attribs.src
        vodDetail.vod_name = $($(vodDetailElement).find("h1")).text()
        let vodContentElements = $(vodDetailElement).find("[class=\"mb-2\"]").slice(1)
        for (const contentElement of vodContentElements) {
            let name = $(contentElement).text()
            if (name.indexOf("豆瓣评分") > -1) {
                vodDetail.vod_remarks = name
            }
            if (name.indexOf("类型") > -1) {
                vodDetail.type_name = name.replaceAll("：", "").replace("类型", "").replaceAll(":", "")
            }
            if (name.indexOf("上映地区") > -1) {
                vodDetail.vod_area = name.replaceAll("：", "").replace("上映地区", "").replaceAll(":", "")
            }
            if (name.indexOf("主演") > -1) {
                vodDetail.vod_actor = name.replaceAll("：", "").replace("主演", "").replaceAll(":", "")
            }
            if (name.indexOf("上映日期") > -1){
                vodDetail.vod_year = name.replaceAll("：", "").replace("上映日期", "").replaceAll(":", "")
            }

        }
        vodDetail.vod_content = $($(vodDetailElement).find("[class=\"mv_card_box\"]")).text()
        let playerMap = {}
        let emebedVideoElements = $("[class=\"row col-md-12 embed_video\"]")
        let index = 1
        for (const emebedVideoElement of emebedVideoElements){
            let vodItems = []
            let playUrl = $($(emebedVideoElement).find("iframe"))[0].attribs["src"]
            vodItems.push("播放" + "$" + playUrl);
            playerMap["在线播放" + index.toString()+ "第一集在线播放预览"] = vodItems.join("#")
            index = index + 1
        }
        let mangetIndex = 1
        let mangetElements = $("[class=\"row col-md-12 text-white p-3 pt-1\"]").find("[class=\"container\"]")
        for (const mangenment of mangetElements){
            let vodItems = []
            let playElement = $($(mangenment).find("a"))[0]
            let playUrl = playElement.attribs.href
            let playName = $(playElement).text()
            if (playUrl.startsWith("magnet")){
               vodItems.push(playName + "$" + playUrl);
            }
            if (vodItems.length > 0){
                playerMap["磁力链接" + "-" + mangetIndex] = vodItems.join("#")
                mangetIndex = mangetIndex + 1
            }
        }

        vodDetail.vod_play_from = Object.keys(playerMap).join("$$$");
        vodDetail.vod_play_url = Object.values(playerMap).join("$$$");
        return vodDetail
    }

    async setHomeVod() {
        let $ = await this.getHtml()
        this.homeVodList = await this.parseVodShortListFromDoc($)
    }

    async setCategory(tid, pg, filter, extend) {
        let type = extend["1"] ?? "0"
        let area = extend["2"] ?? "0"
        let page = parseInt(pg) - 1
        let url = this.siteUrl + "/" + this.cateObj[tid] + `-${type}-${area}-${page}.html`
        await this.jadeLog.debug(`分类URL:${url}`)
        let $ = await this.getHtml(url)
        this.vodList = await this.parseVodShortListFromDoc($)
    }

    async setDetail(id) {
        let $ = await this.getHtml(this.siteUrl + id)
        this.vodDetail = await this.parseVodDetailFromDoc($)
    }


    async setPlay(flag, id, flags) {
        if (flag.indexOf("在线播放") > -1){
            let $ = await this.getHtml(this.siteUrl + id)
            this.playUrl = Utils.getStrByRegex(/const source = '(.*?)'/,$.html())
        }else{
            this.playUrl = id
        }
    }

    async setSearch(wd, quick) {
        let params = {"classid":"1,2","show":"title","tempid":"1","keyboard":wd}
        let response = await this.post(this.siteUrl + "/e/search/index.php",params,this.getHeader())
        let $ = load(response)
        this.vodList = await this.parseVodShortListFromDocBySearch($)
    }

}

let spider = new CiliXiongSpider()

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