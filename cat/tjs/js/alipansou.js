/*
* @File     : alipansou.js
* @Author   : jade
* @Date     : 2024/1/18 13:20
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 猫狸盘搜
*/

import {_, load} from "../lib/cat.js";
import {Spider} from "./spider.js";
import {detailContent, initAli, playContent} from "../lib/ali.js";
import {VodDetail, VodShort} from "../lib/vod.js";
import * as Utils from "../lib/utils.js";

class GitCafeSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://www.alipansou.com"
    }
    getSearchHeader(id) {
        let headers = this.getHeader()
        headers["Referer"] = id
        headers["Postman-Token"] = "5f1bb291-ce30-44c7-8885-6db1f3a50785"
        headers["Host"] = "www.alipansou.com"
        return headers
    }


    getName() {
        return "😸┃阿里猫狸┃😸"
    }

    getAppName() {
        return "阿里猫狸"
    }
    getJSName() {
        return "alipansou"
    }

    getType() {
        return 3
    }

    getHeader() {

        return {
            "User-Agent":Utils.CHROME,
            "Connection": "keep-alive",
            "Cookie":"_ga=GA1.1.1506025676.1708225506;FCNEC=%5B%5B%22AKsRol9sCpH4JteOAAMprJLQxCHddrtkOFinxqt1cs8x3fKzbBZ5Ll76VvjATz1Ejf6NoayGSONFl2gfn6PbVAG97MlHjhp6cY5NFLQtLIUy0TuzI1_ThHnANe8fW03fHdU2-cx5yM3MftaHt4awEGBWhgtE9H_P5w%3D%3D%22%5D%5D;_cc_id=cc82bd83ea8936df45fe63c887a6f221;mysession=MTcwOTYyMjMxMHxEdi1CQkFFQ180SUFBUkFCRUFBQU1fLUNBQUVHYzNSeWFXNW5EQXdBQ25ObFlYSmphRjlyWlhrR2MzUnlhVzVuREJFQUQtV1JxT1draE9tWnBPUzRpZVd1c3c9PXyjHmLCdFvUlsW_gilBojjCq1ak-ffOud6aZKm3kxzJ4w==;Hm_lvt_02f69e0ba673e328ef49b5fb98dd4601=1708225506,1709622301,1710414091;_bid=28d3966abb8cf873ea912b715552f587;cf_clearance=6LuYs83fWIZlcwwzZkgRyYyFrP6Hndxe_CgByMe.pMs-1710414092-1.0.1.1-V44M.u7MNIozBytYixxp4Qe1OVr.CBH78.IEK2QJTWGQ7.HQBR0DoUgiSfpa23U.nxtOfhkrASpqogvz53knnw;cto_bundle=-WbYyl9VWGZjQkhzZ0gyQjE4VXNlcTJnYTNaV3dMaTdVV0xST3p5RkVnUTNxVWpxYVElMkZtNnVsaWtQSzdQU3JJY0slMkYxc3R5SXdyQlRzbkp1clVNZk84OElTR2MlMkJPeGx0bGtsUHk2VzhGdk1yYyUyRnB5eUNNblhKbWpzcjY1SVI1ODlWRGZXemgzUU51bGF5UWxFNVljcUZpd252bnVZZ1R1d0VXRmJ3S1FXQ1RCMXhVNCUzRA;Hm_lpvt_02f69e0ba673e328ef49b5fb98dd4601=1710416656;_ga_NYNC791BP2=GS1.1.1710414091.2.1.1710416656.0.0.0;_ga_0B2NFC7Z09=GS1.1.1710414091.2.1.1710416656.60.0.0;_egg=16a87a4666714be885e814217b225d50e"}
    }

    async getContentHtml() {
        let html = await this.fetch(this.siteUrl, null, this.getHeader())
        if (!_.isEmpty(html)) {
            return load(html)
        }
    }

    async spiderInit() {
        this.content_html = await this.getContentHtml()
    }

    async init(cfg) {
        await this.spiderInit()
        await super.init(cfg);
        await initAli(this.cfgObj["token"]);
    }

    async parseClassFromDoc($) {
        let tap_elemets = $($("[id=\"app\"]")[0]).find("van-tab")
        let index = 0
        for (const tap_element of tap_elemets) {
            let type_name = tap_element.attribs["title"]
            if (type_name.indexOf("热搜") === -1 && type_name !== "游戏" && type_name !== "小说") {
                this.classes.push({"type_name": type_name, "type_id": index})
            }
            index = index + 1
        }
    }

    async parseVodShortListFromDoc(doc) {
        let vod_list = []
        let elements = this.content_html(doc).find("a")
        for (const element of elements) {
            let vodShort = new VodShort()
            vodShort.vod_id = element.attribs["href"]
            vodShort.vod_name = this.content_html(element).text().split(".").slice(-1)[0]
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async getAliUrl(id) {
        let url = this.siteUrl + id.replace("/s/", "/cv/")
        let headers = this.getSearchHeader(url)
        let content = await req(url,{postType:"get",headers:headers,redirect:2})
        await this.jadeLog.debug(`回复内容为:${JSON.stringify(content)}`)
        // let url = await this.fetch(this.siteUrl + id.replace("/s/", "/cv/"), null, headers, true)
        return content.headers.location
    }

    async parseVodDetailfromJson(obj) {
        let vodDetail = new VodDetail();
        vodDetail.vod_name = obj["name"]
        vodDetail.vod_remarks = obj["remarks"]
        let ali_url = await this.getAliUrl(obj["id"])
        await this.jadeLog.debug(`阿里分享链接为:${ali_url}`)
        if (!_.isEmpty(ali_url)) {
            let aliVodDetail = await detailContent([ali_url])
            vodDetail.vod_play_url = aliVodDetail.vod_play_url
            vodDetail.vod_play_from = aliVodDetail.vod_play_from
        }
        return vodDetail
    }


    async parseVodShortListFromDocBySearch($) {
        let elements = $($($("[id=\"app\"]")[0]).find("van-row")).find("a")
        let vod_list = []
        for (const element of elements) {
            let id = element.attribs["href"]
            let matches = id.match(/(\/s\/[^"])/);
            if (!_.isEmpty(matches) && id.indexOf("https") === -1) {
                let text = $(element).text().replaceAll("\n", "").replaceAll(" ", "")
                if (text.indexOf("时间") > -1 && text.indexOf("文件夹") > -1) {
                    let textList = text.split("时间")
                    let vodShort = new VodShort()
                    vodShort.vod_name = textList[0]
                    vodShort.vod_remarks = textList[1].split("格式")[0].replaceAll(":", "").replaceAll(" ", "").replaceAll("﻿", "").replaceAll(" ", "")
                    vodShort.vod_id = JSON.stringify({
                        "name": vodShort.vod_name, "remarks": vodShort.vod_remarks, "id": id
                    })
                    vod_list.push(vodShort)
                }
            }
        }
        return vod_list
    }

    async setClasses() {
        await this.parseClassFromDoc(this.content_html)
    }


    async setHomeVod() {
        let tap_elemets = this.content_html(this.content_html("[id=\"app\"]")[0]).find("van-tab")
        this.homeVodList = await this.parseVodShortListFromDoc(tap_elemets[0])
    }


    async setDetail(id) {
        if (id.indexOf("search") > -1) {
            let url = this.siteUrl + "/search"
            let params = {"k":decodeURIComponent(id.split("search?k=").slice(-1)[0]) }
            let html = await this.fetch(url, params, this.getHeader())
            if (!_.isEmpty(html)) {
                let $ = load(html)
                let vod_list = await this.parseVodShortListFromDocBySearch($)
                if (vod_list.length > 0) {
                    id = vod_list[0]["vod_id"]
                } else {
                    id = ""
                }
            }
        }
        if (!_.isEmpty(id)) {
            let json_content = JSON.parse(id)
            this.vodDetail = await this.parseVodDetailfromJson(json_content)
        }

    }

    async setCategory(tid, pg, filter, extend) {
        let tap_elemets = this.content_html(this.content_html("[id=\"app\"]")[0]).find("van-tab")
        this.vodList = await this.parseVodShortListFromDoc(tap_elemets[parseInt(tid)])
    }

    async setSearch(wd, quick) {
        let url = this.siteUrl + "/search"
        let params = {"k": wd}
        let html = await this.fetch(url, params, this.getHeader())
        if (!_.isEmpty(html)) {
            let $ = load(html)
            this.vodList = await this.parseVodShortListFromDocBySearch($)
        }
    }

    async setPlay(flag, id, flags) {
        let playObjStr = await playContent(flag, id, flags);
        this.playUrl = JSON.parse(playObjStr)["url"]
    }
}

let spider = new GitCafeSpider()

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