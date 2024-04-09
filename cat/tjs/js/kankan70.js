/*
* @File     : kankan70.js
* @Author   : jade
* @Date     : 2023/12/29 15:33
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/
import * as Utils from "../lib/utils.js";
import {_, load} from "../lib/cat.js";
import {VodDetail, VodShort} from "../lib/vod.js";
import {Spider} from "./spider.js";

function get_qp_name44(qp_type) {
    if (qp_type === 'zd') return '最大';
    if (qp_type === 'yj') return '永久';
    if (qp_type === 'hn') return '牛牛';
    if (qp_type === 'gs') return '光波';
    if (qp_type === 'sn') return '新朗';
    if (qp_type === 'wl') return '涡轮';
    if (qp_type === 'lz') return '良子';
    if (qp_type === 'fs') return 'F速';
    if (qp_type === 'ff') return '飞飞';
    if (qp_type === 'bd') return '百度';
    if (qp_type === 'uk') return '酷U';
    if (qp_type === 'wj') return '无天';
    if (qp_type === 'bj') return '八戒';
    if (qp_type === 'tk') return '天空';
    if (qp_type === 'ss') return '速速';
    if (qp_type === 'kb') return '酷播';
    if (qp_type === 'sd') return '闪电';
    if (qp_type === 'xk') return '看看';
    if (qp_type === 'tp') return '淘淘';
    if (qp_type === 'jy') return '精英';

    return qp_type;
}


class Kankan70Spider extends Spider {
    constructor() {
        super();
        this.siteUrl = "http://cqdb6.com";
    }

    getName() {
        return "📺┃70看看┃📺"
    }

    getAppName() {
        return "70看看"
    }

    getJSName() {
        return "kankan70"
    }

    getType() {
        return 3
    }

    paraseUrlObject(js_str) {
        let content_list = js_str.split(";")
        let urlObject = {}
        let js_name = ""
        let play_id = 0
        let pldy_id = 0
        let js_key = ""
        for (let i = 0; i < content_list.length; i++) {
            let content = content_list[i]
            if (content.indexOf("var lianzaijs") > -1) {
                js_name = content.split("=")[0].split(" ")[1]
                js_key = js_name.split("_")[1]
            } else if (content.indexOf("pl_id=") > -1) {
                play_id = content.split("=")[1]
                urlObject[js_name] = {"play_id": play_id, "list": [], "pl_dy": pldy_id}
            } else if (content.indexOf("var pl_dy") > -1) {
                pldy_id = content.split("=")[1]
            }
            if (content.indexOf(`playarr_${js_key}[`) > -1) {
                let play_url = content.split("=\"")[1].split(",")[0]
                urlObject[js_name]["list"].push(play_url)
            }
        }
        let play_url_list = [], play_format_list = [];
        for (const key of Object.keys(urlObject)) {
            if (key.indexOf("_") > -1) {
                let play_format_name = get_qp_name44(key.split("_")[1])
                play_format_list.push(play_format_name)
                let vodItems = []
                let index = 0
                for (const play_url of urlObject[key]["list"]) {
                    index = index + 1
                    vodItems.push("第" + index.toString() + "集" + "$" + play_url)
                }
                play_url_list.push(vodItems.join("#"))
            }
        }
        return {"play_format": play_format_list.join("$$$"), "play_url": play_url_list.join("$$$")}
    }

    async parseVodShortListFromDoc($) {
        let vod_list = []
        let vod_elements = $("a.li-hv")
        for (const vod_element of vod_elements) {
            let vodShort = new VodShort()
            vodShort.vod_id = "/" + vod_element.attribs["href"]
            vodShort.vod_name = vod_element.attribs["title"]
            vodShort.vod_pic = $(vod_element).find("img")[0].attribs["data-original"]
            let remarkEle = $(vod_element).find("p.bz")[0]
            if (remarkEle.length > 0) {
                vodShort.vod_remarks = remarkEle.children[0].data
            }
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodDetailFromDoc($) {
        let vodDetail = new VodDetail()
        let infoElement = $("[class=info]")
        let dtElement = $(infoElement).find("dt.name")[0]
        vodDetail.vod_name = dtElement.children[0].data
        vodDetail.vod_remarks = dtElement.children[1].children[0].data
        let ddString = $(infoElement).find("dd").text()
        vodDetail.vod_area = Utils.getStrByRegex(/地区：(.*?) /, ddString)
        vodDetail.vod_year = Utils.getStrByRegex(/年代：(.*?)\n/, ddString)
        vodDetail.type_name = Utils.getStrByRegex(/类型：(.*?)\n/, ddString)
        vodDetail.vod_content = $(infoElement).find("[class=des2]").text().replaceAll("\n", "").replaceAll("剧情：", "")
        vodDetail.vod_pic = $("img.lazy")[0].attribs["data-original"]

        return vodDetail
    }

    async parseVodShortListFromJson(obj) {
        let vod_list = []
        for (const vod_object of obj) {
            let vodShort = new VodShort()
            vodShort.vod_id = vod_object["url"]
            vodShort.vod_pic = vod_object["thumb"]
            vodShort.vod_remarks = vod_object["time"]
            vodShort.vod_name = vod_object["title"]
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async setClasses() {
        let html = await this.fetch(this.siteUrl, null, this.getHeader())
        if (!_.isEmpty(html)) {
            let $ = load(html)
            let elements = $("[class=index-list-l]")
            for (const element of elements) {
                let typeElement = $($(element).find("[class=\"h1 clearfix\"]")[0]).find("a")
                let type_id = typeElement[0].attribs["href"]
                let type_name = $(typeElement[1]).text()
                if (!_.isEmpty(type_name)) {
                    this.classes.push({"type_id": type_id, "type_name": type_name})
                }
            }
        }
    }

    async getFilter(type_id) {
        let url = this.siteUrl + type_id
        let html = await this.fetch(url, null, this.getHeader())
        let extend_list = []
        if (!_.isEmpty(html)) {
            let $ = load(html)
            let elements = $("[class=\"sy scon clearfix\"]").find("dl")
            let i = 0
            for (const element of elements) {
                let type_name = $($(element).find("dt")).text().replace("按", "").replace("：", "")
                let extend_dic = {
                    "key": (i + 1).toString(), "name": type_name, "value": []
                }
                let type_elements = $(element).find("a")
                let index = 0
                if (type_name === "剧情") {
                    index = 3
                } else if (type_name === "年代") {
                    index = 2
                } else if (type_name === "地区") {
                    index = 4
                }
                for (const type_element of type_elements) {
                    let type_id_list = type_element.attribs["href"].split("/")
                    extend_dic["value"].push({"n": $(type_element).text(), "v": type_id_list[index]})
                }
                extend_list.push(extend_dic)
                i = i + 1
            }
        }
        return extend_list
    }

    async setFilterObj() {
        for (const class_dic of this.classes) {
            let type_id = class_dic["type_id"]
            if (type_id !== "最近更新") {
                this.filterObj[type_id] = await this.getFilter(type_id)
            }
        }
    }

    async setHomeVod() {
        let html = await this.fetch(this.siteUrl, null, this.getHeader())
        if (!_.isEmpty(html)) {
            let $ = load(html)
            this.homeVodList = await this.parseVodShortListFromDoc($)
        }
    }

    async setCategory(tid, pg, filter, extend) {
        let url = this.siteUrl + tid
        let html = await this.fetch(url, null, this.getHeader())
        if (!_.isEmpty(html)) {
            let class_name = tid.split("/")[1]
            let id = tid.split("/")[2]
            let api_str = Utils.getStrByRegex(/var _yu_gda_s="(.*?)";/, html)
            let params = {
                "action": class_name,
                "page": parseInt(pg),
                "year": extend["2"] ?? "0",
                "area": extend["3"] ?? "all",
                "class": extend["1"] ?? "0",
                "dect": "",
                "id": id
            }
            let cate_html = await this.fetch(api_str, params, this.getHeader())
            if (cate_html !== null) {
                let $ = load(cate_html)
                this.vodList = await this.parseVodShortListFromDoc($)
            }
        }

    }

    async setDetail(id) {
        let detailUrl = this.siteUrl + id
        let html = await this.fetch(detailUrl, null, this.getHeader())
        if (!_.isEmpty(html)) {
            let $ = load(html)
            this.vodDetail = await this.parseVodDetailFromDoc($)
            let mather = /<script type="text\/javascript" src="http:\/\/test.gqyy8.com:8077\/ne2(.*?)"><\/script>/g.exec(html)
            let js_url = "http://test.gqyy8.com:8077/ne2" + mather[1]
            let js_str = await this.fetch(js_url, null, this.getHeader())
            if (!_.isEmpty(js_str)) {
                let playObject = this.paraseUrlObject(js_str)
                this.vodDetail.vod_play_url = playObject["play_url"]
                this.vodDetail.vod_play_from = playObject["play_format"]
            }
        }
    }

    async setSearch(wd, quick) {
        let url = this.siteUrl + "/search.php"
        let html = await this.fetch(url, null, this.getHeader())
        if (!_.isEmpty(html)) {
            let params = {
                "top": 10, "q": wd,
            }
            let api_url = Utils.getStrByRegex(/var my_search='(.*?)';/, html)
            let content = await this.fetch(api_url, params, this.getHeader())
            if (!_.isEmpty(content)) {
                let content_json = JSON.parse(content.replaceAll("﻿",""))
                this.vodList = await this.parseVodShortListFromJson(content_json)
            }
        }
    }
}

let spider = new Kankan70Spider()

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