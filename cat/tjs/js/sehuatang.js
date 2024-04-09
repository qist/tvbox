/*
* @File     : sehuatang
* @Author   : jade
* @Date     : 2024/1/24 16:47
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 色花堂BT
*/
import * as Utils from "../lib/utils.js";
import {Spider} from "./spider.js";
import {VodDetail, VodShort} from "../lib/vod.js";
import {_} from "../lib/cat.js";

class SHTSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://www.sehuatang.net"
    }

    getAppName() {
        return "色花堂BT"
    }
    getName() {
        return "🔞┃色花堂BT┃🔞"
    }
    getJSName() {
        return "sehuatang"
    }

    getType() {
        return 3
    }

    async init(cfg) {
        await super.init(cfg);
        this.jsBaseDetail = await js2Proxy(true, this.siteType, this.siteKey, 'detail/', {});
    }



    getHeader() {
        return {
            "User-Agent": "PostmanRuntime/7.36.1",
            "Host": "www.sehuatang.net",
            "Cookie": "cPNj_2132_saltkey=Q4BKEOEC; cf_clearance=6Gz2tvOXPkkJP2UhLnSsN4s0RrnDUy0jBN0kUvC5FNQ-1706109144-1-AebvwBnAURwWWQhj0QRBrRPku2n8xI73PIeuZVj2ckqY9zjQ7zFzDviX7Gkex1P1bUw9SXHGEYnkBB9nmWe6Nhk=; _safe=vqd37pjm4p5uodq339yzk6b7jdt6oich",
        }
    }

    async parseVodShortListFromDoc($) {
        let vod_list = []
        let vodShortElements = $("[id=\"portal_block_43_content\"]").find("li")
        for (const vodShortElement of vodShortElements) {
            let vodShort = new VodShort()
            vodShort.vod_remarks = $($(vodShortElement).find("a")[1]).text()
            vodShort.vod_id = $(vodShortElement).find("a")[2].attribs["href"]
            vodShort.vod_name = $(vodShortElement).find("a")[2].attribs["title"]
            vodShort.vod_pic = this.jsBaseDetail + Utils.base64Encode(vodShort.vod_id)
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodShortListFromDocByCategory($) {
        let vod_list = []
        let vodElements = $($("[class=\"bm_c\"]")[0]).find("tbody")
        for (const vodElement of vodElements) {
            let user_name = $($($(vodElement).find("cite")).find("a")[0]).text()
            if (user_name !== "admin" && user_name !== undefined && !_.isEmpty(user_name)) {
                let vodShort = new VodShort()
                vodShort.vod_id = $(vodElement).find("a")[0].attribs["href"]
                vodShort.vod_remarks = $($(vodElement).find("a")[2]).text()
                vodShort.vod_name = $($(vodElement).find("a")[3]).text()
                vodShort.vod_pic = this.jsBaseDetail + Utils.base64Encode(vodShort.vod_id)
                vod_list.push(vodShort)
            }

        }
        return vod_list
    }

    async parseVodDetailFromDoc($) {
        let vodDetail = new VodDetail();
        let vodElement = $("[class=\"t_f\"]")[0]
        let content = $(vodElement).text().replaceAll("：", ":").replaceAll("【", "").replaceAll("】", "")
        vodDetail.vod_pic = $(vodElement).find("img")[0].attribs["file"]
        vodDetail.vod_name = Utils.getStrByRegex(/影片名称(.*?)\n/, content).replaceAll(":", "").replaceAll("\n", "")
        vodDetail.vod_actor = Utils.getStrByRegex(/出演女优(.*?)\n/, content).replaceAll(":", "").replaceAll("\n", "")
        vodDetail.vod_remarks = Utils.getStrByRegex(/是否有码(.*?)\n/, content).replaceAll(":", "").replaceAll("\n", "")
        vodDetail.vod_play_from = "BT"
        vodDetail.vod_play_url = vodDetail.vod_name + "$" + Utils.getStrByRegex(/磁力链接: (.*)复制代码/, content)
        return vodDetail
    }

    async setClasses() {
        let $ = await this.getHtml()
        let tagElements = $("[id=\"category_1\"]").find("tr").slice(0, -1)
        for (const tagElement of tagElements) {
            let classElements = $($(tagElement).find("[class=\"fl_icn_g\"]")).find("a")
            for (const classElement of classElements) {
                let type_id = classElement.attribs["href"]
                let type_name = $(classElement).find("img")[0].attribs["alt"]
                this.classes.push(this.getTypeDic(type_name, type_id))
            }
        }
    }

    async getFilter($) {

        let extend_list = []
        let extend_dic1 = {"key": 1, "name": "类型", "value": []}
        let typeElements = $("[id=\"thread_types\"]").find("a")
        for (const typeElement of typeElements){
            let type_name = ""
            if (typeElement.children.length > 1){
                type_name = typeElement.children[0].data + ":" + $(typeElement.children[1]).text()
            }else{
                type_name = typeElement.children[0].data
            }
            extend_dic1["value"].push({"n":type_name,"v":typeElement.attribs["href"]})
        }
        extend_list.push(extend_dic1)
        let extend_dic2 = {"key": 1, "name": "主题", "value": []}
        let themeElements = $("[class=\"tf\"]").find("a")
        for (const themeElement of themeElements){
            let type_name = $(themeElement).text()
            if (type_name !== "更多" && type_name !== "显示置顶"){
                extend_dic2["value"].push({"n":$(themeElement).text(),"v":themeElement.attribs["href"]})
            }
        }
        extend_list.push(extend_dic2)
        return extend_list
    }

    async setFilterObj() {
        for (const class_dic of this.classes){
            let type_name = class_dic["type_name"]
            let type_id = class_dic["type_id"]
            if (type_name !== "最近更新"){
                let $ = await this.getHtml(this.siteUrl + '/' + type_id)
                this.filterObj[type_id] = await this.getFilter($)
            }
        }
    }

    async setHomeVod() {
        let $ = await this.getHtml()
        this.homeVodList = await this.parseVodShortListFromDoc($)
    }

    async setCategory(tid, pg, filter, extend) {
        if (extend["1"]!==undefined && extend[1] ==="javascript:;"){
        }else{
            tid = extend["1"] ?? tid
        }
        let cateUrl
        let tid_list = tid.split(".")[0].split("-")
        if (tid_list.length > 2){
            tid_list[2] = pg
            cateUrl = this.siteUrl + "/" + tid_list.join("-") + ".html"
        }else{
            cateUrl = this.siteUrl + "/" + tid + "&page=" + pg
        }

        let $ = await this.getHtml(cateUrl)
        this.vodList = await this.parseVodShortListFromDocByCategory($)
    }

    async setDetail(id) {
        let $ = await this.getHtml(this.siteUrl + "/" + id)
        this.vodDetail = await this.parseVodDetailFromDoc($)
    }

    async proxy(segments, headers) {
        await this.jadeLog.debug(`正在设置反向代理 segments = ${segments.join(",")},headers = ${JSON.stringify(headers)}`)
        let what = segments[0];
        let url = Utils.base64Decode(segments[1]);
        if (what === 'detail') {
            await this.jadeLog.debug(`反向代理ID为:${url}`)
            let $ = await this.getHtml(this.siteUrl + "/" + url)
            let vodDetail = await this.parseVodDetailFromDoc($)
            await this.jadeLog.debug(`图片地址为:${vodDetail.vod_pic}`)
            let resp;
            if (!_.isEmpty(headers)) {
                resp = await req(vodDetail.vod_pic, {
                    buffer: 2, headers: headers
                });
            } else {
                resp = await req(vodDetail.vod_pic, {
                    buffer: 2, headers: {
                        Referer: url, 'User-Agent': Utils.CHROME,
                    },
                });
            }
            return JSON.stringify({
                code: resp.code, buffer: 2, content: resp.content, headers: resp.headers,
            });
        }
        return JSON.stringify({
            code: 500, content: '',
        });
    }

}

let spider = new SHTSpider()

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
