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
        this.siteUrl = "https://www.x9s8x.icu"  //  https://www.cs1369.com
    }

    getName() {
        return "🔞┃九九六影视┃🔞"
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
        let vodElements = $('[class="content-item"]')
        for (const vodElement of vodElements) {
            let vodShort = new VodShort()
            let videoElement = $(vodElement).find("a")[0]
            vodShort.vod_id = videoElement.attribs["href"]
            vodShort.vod_name = videoElement.attribs["title"]
            vodShort.vod_pic = $(videoElement).find("img")[0].attribs["data-original"]
            vodShort.vod_remarks = $($(vodElement).find('[class="note text-bg-r"]')).text()
            vod_list.push(vodShort)
        }
        return vod_list
    }



    async parseVodDetailFromDoc($) {
        let vodDetail = new VodDetail()
        let detailElement = $('[class="row film_info clearfix"]')
        vodDetail.vod_pic = $(detailElement).find("img")[0].attribs["data-original"]
        vodDetail.vod_name = $($(detailElement).find('[class="c_pink text-ellipsis"]')).text()
        let content = $( $(detailElement).find('[class="row"]')).text()
        vodDetail.type_name = Utils.getStrByRegex(/视频类型(.*?)\n/,content).replaceAll("：","")
        vodDetail.vod_area = Utils.getStrByRegex(/更新时间(.*?)\n/,content).replaceAll("：","")
        let playVod = {}
        let playElement = $('[class="btn btn-m btn-default"]')[0]

        let vodItems = []
        const epName = vodDetail.vod_name;
        const playUrl = playElement.attribs.href
        vodItems.push(epName + '$' + playUrl)
        playVod[playElement.attribs.title] = vodItems.join('#')
        vodDetail.vod_play_from = _.keys(playVod).join('$$$');
        vodDetail.vod_play_url = _.values(playVod).join('$$$');
        return vodDetail
    }

    async setClasses() {
        let $ = await this.getHtml(this.siteUrl,true);
        let menuElements = $('[class="row-item-title bg_red"]').find("a")
        for (const menuElement of menuElements) {
            let type_name = $(menuElement).text()
            let type_id = menuElement.attribs["href"]
            if (type_name.indexOf("小说") === -1){
                this.classes.push(this.getTypeDic(type_name, type_id))
            }
        }
    }

    async getFilter($,index) {
        let html = $.html()
        let extend_list = []
        let extendElement = $($($($('[class="row-item-content"]')[index])).find('[class="item"]')).find("a")
        let extend_dic = {"name":"排序","key":"sort","value":[]}
        for (const element of extendElement){
            let type_name = $(element).text()
            let type_id = element.attribs["href"]
            extend_dic["value"].push(this.getFliterDic(type_name,type_id))

        }
        extend_list.push(extend_dic)
        return extend_list
  
    }

    async setFilterObj() {
        let index = 0
        for (const type_dic of this.classes) {
            let type_id = type_dic["type_id"]
            if ( type_id !== "最近更新") {
                let $ = await this.getHtml(this.siteUrl,true)
                this.filterObj[type_id] = await this.getFilter($,index)
                index = index + 1
            }
        }
    }

    async setHomeVod() {
        let $ = await this.getHtml(this.siteUrl,true)
        this.homeVodList = await this.parseVodShortListFromDoc($)
    }



    async setCategory(tid, pg, filter, extend) {
        let $ = await this.getHtml(this.siteUrl + tid.replaceAll(".html",`/page/${pg}.html`),true)
        this.vodList = await this.parseVodShortListFromDoc($)
    }

    async setDetail(id) {
        let $ = await this.getHtml(this.siteUrl + id,true)
        this.vodDetail = await this.parseVodDetailFromDoc($)
    }


    async setPlay(flag, id, flags) {
        let $ = await this.getHtml(this.siteUrl+id,true)
        let playerConfig = JSON.parse(Utils.getStrByRegex(/var player_aaaa=(.*?)<\/script>/,$.html()))
        this.playUrl = playerConfig["url"]
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