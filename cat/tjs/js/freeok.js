/*
* @File     : freeok.js
* @Author   : jade
* @Date     : 2024/1/19 10:26
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : OK资源网 已失效
*/
import {_} from '../lib/cat.js';
import {VodDetail, VodShort} from "../lib/vod.js"
import * as Utils from "../lib/utils.js";
import {Spider} from "./spider.js";
import {player} from "../lib/freeok_setttings.js";
const OCR_API = 'https://api.nn.ci/ocr/b64/text';//ocr在线识别接口


class OkSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://www.freeok.vip"
    }

    getName() {
        return `🆗┃OK资源网┃🆗`
    }

    getAppName() {
        return `OK资源网`
    }
    getJSName() {
        return "freeok"
    }

    getType() {
        return 3
    }
    async init(cfg) {
        this.cookie = await this.load_cache()
        await super.init(cfg);
    }


    async parseVodShortListFromDoc($) {
        let vod_list = []
        let vodElements = $($("[class=\"module\"]")).find("a").slice(0, 12)
        for (const vodElement of vodElements) {
            vod_list.push(this.parseVodShortFromElement($, vodElement))
        }
        return vod_list
    }

    parseVodShortFromElement($, element) {
        let vodShort = new VodShort();
        vodShort.vod_name = element.attribs["title"]
        vodShort.vod_id = element.attribs["href"]
        vodShort.vod_remarks = $($(element).find("[class=\"module-item-note\"]")).text()
        vodShort.vod_pic = $(element).find("[class=\"lazy lazyload\"]")[0].attribs["data-original"]
        return vodShort
    }

    async parseVodShortListFromDocByCategory($) {
        let vod_list = []
        let itemElements = $($("[class=\"module-items module-poster-items-base \"]")).find("a")
        for (const itemElement of itemElements) {
            vod_list.push(this.parseVodShortFromElement($, itemElement))
        }
        return vod_list
    }
      async parseVodShortListFromJson(obj) {
        let vod_list = []
        for (const result of obj["Data"]["result"]){
            let vodShort = new VodShort()
            vodShort.vod_id = result["vod_url"].replaceAll(this.siteUrl,"")
            vodShort.vod_pic = result["vod_pic"]
            vodShort.vod_name = result["vod_name"]
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodShortListFromDocByHot($) {
        let vod_list = []
        let itemElement = $($("[class=\"module-items module-card-items\"]"))[0]
        let titleElements = $(itemElement).find("[class=\"module-card-item-title\"]").find("a")
        let infoElements = $(itemElement).find("[class=\"module-card-item-info\"]")
        let picElements = $(itemElement).find("[class=\"module-item-pic\"]").find("img")

        for (let i = 0; i < titleElements.length; i++) {
            let vodShort = new VodShort();
            vodShort.vod_id = titleElements[i].attribs["href"]
            vodShort.vod_name = $(titleElements[i]).text()
            vodShort.vod_pic = picElements[i].attribs["data-original"]
            vodShort.vod_remarks = $($(infoElements[i])).text().split("\n")[5]
            vod_list.push(vodShort)

        }
        return vod_list
    }

    async parseVodDetailFromDoc($) {
        let vodDetail = new VodDetail();
        let moudleElements = $("[class=\"module-info-tag-link\"]").find("a")
        let mobilePlay = $("[class=\"module-mobile-play\"]").find("a")[0]
        vodDetail.vod_name = mobilePlay.attribs["title"].replaceAll("立刻播放", "")
        vodDetail.vod_content = $($("[class=\"module-info-introduction-content\"]")).text().replaceAll("\n", "").replaceAll(" ", "")
        let type_list = []
        for (const moudleElement of moudleElements.slice(2)) {
            type_list.push($(moudleElement).text())
        }
        vodDetail.type_name = type_list.join("/")
        vodDetail.vod_year = $(moudleElements[0]).text()
        vodDetail.vod_area = $(moudleElements[1]).text()
        let itemElements = $("[class=\"module-info-item\"]")
        let itemText = ""
        for (const itemElement of itemElements) {
            itemText = itemText + $(itemElement).text().replaceAll("\n", "").replaceAll("：", ":") + "\n"
        }
        vodDetail.vod_pic = $("[class=\"module-item-pic\"]").find("img")[0].attribs["data-original"]
        vodDetail.vod_director = Utils.getStrByRegex(/导演:(.*?)\n/, itemText)
        vodDetail.vod_actor = Utils.getStrByRegex(/主演:(.*?)\n/, itemText)
        vodDetail.vod_year = Utils.getStrByRegex(/上映:(.*?)\n/, itemText)
        vodDetail.vod_remarks = Utils.getStrByRegex(/备注:(.*?)\n/, itemText)
        if (_.isEmpty(vodDetail.vod_remarks)) {
            vodDetail.vod_remarks = Utils.getStrByRegex(/集数:(.*?)\n/, itemText)
        }
        let playElements = $($("[class=\"module-tab-items-box hisSwiper\"]")).find("span")
        let play_from_list = []
        let playUrlElements = $("[class=\"module-list sort-list tab-list his-tab-list\"]")
        let play_url_list = []
        for (let i = 0; i < playElements.length; i++) {
            let text = $(playElements[i]).text()
            if (text.indexOf("夸克") === -1) {
                let playDetailElements = $(playUrlElements[i]).find("a")
                let vodItems = []
                for (const playDetailElement of playDetailElements) {
                    let play_name = playDetailElement.attribs["title"].replaceAll("播放", "").replaceAll(vodDetail.vod_name, "")
                    let play_url = playDetailElement.attribs["href"]
                    vodItems.push(`${play_name}$${play_url}`)
                }
                play_url_list.push(vodItems.join("#"))
                play_from_list.push($(playElements[i]).text())
            }
        }
        vodDetail.vod_play_from = play_from_list.join("$$$")
        vodDetail.vod_play_url = play_url_list.join("$$$")
        return vodDetail
    }


    async setClasses() {
        let $ = await this.getHtml(this.siteUrl, this.getHeader())
        let navElements = $($("[class=\"navbar-items swiper-wrapper\"]")).find("a")
        let type_name = $(navElements.slice(0, 8).slice(-1)[0]).text().replaceAll("\n", "")
        let type_id = navElements.slice(0, 8).slice(-1)[0].attribs["href"]
        this.classes.push({"type_name": type_name, "type_id": type_id})
        for (const navElement of navElements.slice(0, 8)) {
            let type_name = $(navElement).text().replaceAll("\n", "")
            if (type_name !== "首页" && type_name !== "热榜") {
                let type_id = navElement.attribs["href"].split("/").slice(-1)[0].split(".")[0]
                this.classes.push({"type_name": type_name, "type_id": type_id})
            }
        }
    }

    async getFilter($) {
        let titleElements = $("[class=\"module-item-title\"]")
        let boxElements = $("[class=\"module-item-box\"]")
        let extend_list = []
        let type_id_dic = {"类型": 1, "剧情": 4, "地区": 2, "语言": 5, "年份": 12, "排序": 3}
        for (let i = 0; i < titleElements.length; i++) {
            let extend_dic = {"key": (i + 1).toString(), "name": $(titleElements[i]).text(), "value": []}
            let typeElements = $(boxElements[i]).find("a")
            for (let j = 0; j < typeElements.length; j++) {
                let type_name = $(typeElements[j]).text()
                let type_id = decodeURIComponent(typeElements[j].attribs["href"].split("-")[type_id_dic[$(titleElements[i]).text()]]).replaceAll(".html", "")
                extend_dic["value"].push({"n": type_name, "v": $(titleElements[i]).text() + "-" + type_id})
            }
            extend_list.push(extend_dic)

        }
        return extend_list;
    }

    async setFilterObj() {
        for (const class_dic of this.classes) {
            if (class_dic["type_name"] !== "最近更新" && class_dic["type_name"] !== "热榜") {
                let cateUrl = this.siteUrl + `/vod-show/${class_dic["type_id"]}--------1---.html`
                let $ = await this.getHtml(cateUrl, this.getHeader())
                this.filterObj[class_dic["type_id"]] = await this.getFilter($)
            }
        }
    }

    async setHomeVod() {
        let $ = await this.getHtml(this.siteUrl, this.getHeader())
        this.homeVodList = await this.parseVodShortListFromDoc($)
    }

    getCateUrl(tid, pg, extend) {
        let value_list = Object.values(extend)
        let type_id_dic = {"类型": 1, "剧情": 3, "地区": 1, "语言": 4, "年份": 11, "排序": 2}
        let urlParams = [tid.toString(), "", "","","", "", "", "", "", "", "",""]
        urlParams[8] = pg.toString()
        for (const value of value_list) {
            if (value.split("-")[0] === "类型") {
                urlParams[0] = value.split("-")[1].split("show/")[1].toString()
            } else {
                let type_index = type_id_dic[value.split("-")[0]]
                urlParams[type_index] = value.split("-")[1]
            }

        }
        return this.siteUrl + `/vod-show/` + urlParams.join("-") + ".html"
    }

    async setCategory(tid, pg, filter, extend) {
        let cateUrl
        if (tid.indexOf(".html") > -1) {
            cateUrl = this.siteUrl + tid
            let $ = await this.getHtml(cateUrl, this.getHeader());
            this.vodList = await this.parseVodShortListFromDocByHot($)
        } else {
            cateUrl = this.getCateUrl(tid, pg, extend)
            let $ = await this.getHtml(cateUrl, this.getHeader());
            this.vodList = await this.parseVodShortListFromDocByCategory($)
        }
    }

    async setSearch(wd, quick) {
        let url = `http://123.207.150.253/zxapi/public/?service=App.F.Fetch&req_p=${wd}&type=okys`
        let content = await this.fetch(url,null,this.getHeader())
        this.vodList = await this.parseVodShortListFromJson(JSON.parse(content))

    }

    async refreshCookie() {
        let passUrl = this.siteUrl + "/index.php/verify/index.html?"
        let passHtml = await this.fetch(passUrl,null,this.getHeader(),false,true)

        let response2 = await this.post(OCR_API,passHtml["content"],this.getHeader())
        this.cookie = Utils.getStrByRegex(/(.*?);/,passHtml["cookie"])
        let verifyUrl = this.siteUrl + "/index.php/ajax/verify_check?type=search&verify=5286"
        let headers = this.getHeader()
        headers["cookie"] = this.cookie
        let response = await this.post(verifyUrl,null,headers)
        await this.write_cache()
    }



    async load_cache() {
        try {
            return  await local.get("freeok_cookie", "cookie")
        } catch (e) {
            return ""
        }
    }

    async write_cache() {
        await local.set("freeok_cookie", "cookie", JSON.stringify(this.cookie))
    }



    async setDetail(id) {
        let $ = await this.getHtml(this.siteUrl + id, this.getHeader())
        this.vodDetail = await this.parseVodDetailFromDoc($)
    }

    async setPlay(flag, id, flags) {
        let $ = await this.getHtml(this.siteUrl + id, this.getHeader())
        const js = JSON.parse($('script:contains(player_)').html().replace('var player_aaaa=', ''));
        let url = this.siteUrl + "/okplayer/"
        let params = {
            "url": decodeURIComponent(js.url), "next": decodeURIComponent(js.url_next), "title": js.vod_data.vod_name
        }
        let playHtml = await this.fetch(url, params, this.getHeader());
        let view_port_id = Utils.getStrByRegex(/<meta name="viewport"(.*?)>/, playHtml).split("id=\"")[1].replaceAll("now_", "")
        let player_id = Utils.getStrByRegex(/meta charset="UTF-8" id="(.*?)">/, playHtml).replaceAll("now_", "")
        let player_url = Utils.getStrByRegex(/"url": "(.*?)",/, playHtml)
        this.playUrl = player(player_url, view_port_id, player_id)
    }
}


let spider = new OkSpider()

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