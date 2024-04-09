/*
* @File     : tencentDanmu.js
* @Author   : jade
* @Date     : 2024/3/13 13:17
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/

import {DammuSpider} from "./danmuSpider.js";
import {VodDetail} from "./vod.js";
import * as Utils from "./utils.js";

class TencentDammuSpider extends DammuSpider {
    constructor() {
        super()
        this.siteUrl = "https://v.qq.com"
        this.reconnectTimes = 0
        this.maxReconnectTimes = 5
    }

    getAppName() {
        return "腾讯视频"
    }

    async parseVodShortListFromDoc($) {
        let vodElements = $("[class=\"_infos\"]")
        let vod_list = []
        for (const vodElement of vodElements) {
            let vodDetail = new VodDetail()
            let titleElement = $(vodElement).find("[class=\"result_title\"]")
            let infoItemEvenElenet = $(vodElement).find("[class=\"info_item info_item_even\"]")
            let infoItemOddElement = $(vodElement).find("[class=\"info_item info_item_odd\"]")
            let descElement = $(vodElement).find("[class=\"info_item info_item_desc\"]")
            vodDetail.vod_name = $($(titleElement).find("[class=\"hl\"]")).text()
            vodDetail.vod_year = $($(titleElement).find("[class=\"sub\"]")).text().replaceAll("\n","").replaceAll("(","").replaceAll(")","").replaceAll("\t","").split("/").slice(-1)[0]
            vodDetail.type_name = $($(titleElement).find("[class=\"type\"]")).text()
            vodDetail.vod_director = $($($(infoItemEvenElenet).find("[class=\"content\"]")).find("span")).text()
            let actorList = $( $(infoItemOddElement.slice(-1)[0]).find("[class=\"content\"]")).find("a")
            let  vodActorList = []
            for (const actorElement of actorList){
                vodActorList.push($(actorElement).text())
            }
            vodDetail.vod_actor = vodActorList.join(" * ")
            vodDetail.vod_content = $($(descElement).find("[class=\"desc_text\"]")[0]).text()
            let url = $(vodElement).find("a")[0].attribs.href
            if (url.indexOf("cover") > -1){
                let detail$ = await this.getHtml(url)
                let video_ids = JSON.parse(Utils.getStrByRegex(/"video_ids":(.*?),/,detail$.html()))
                vodDetail.vod_id = video_ids[0]
                vod_list.push(vodDetail)
            }
        }
        return vod_list
    }

    async search(wd) {
        await this.jadeLog.debug(`正在搜索:${wd}`, true)
        let searchUrl = this.siteUrl + `/x/search/?q=${wd}`
        let $ = await this.getHtml(searchUrl)
        return this.parseVodShortListFromDoc($)
    }

    parseDammu(id){

    }


    async getDammu(voddetail, episodeId) {
        let vod_list = await this.search(voddetail.vod_name)
        for (const searchVodDetail of vod_list){
            if (voddetail.vod_director === searchVodDetail.vod_director){
                await this.jadeLog.debug("搜索匹配成功",true)
                return
            }
        }
        await this.jadeLog.warning(`搜索匹配失败,原:${JSON.stringify(voddetail)},搜索:${JSON.stringify(vod_list)}`)
        return ""
    }
}

export {TencentDammuSpider}


