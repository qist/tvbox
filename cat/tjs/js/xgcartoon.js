/*
* @Author: jadehh
* @Date: 2024-06-21 15:47:27
* @LastEditTime: 2024-06-21 16:20:30
* @LastEditors: jadehh
* @Description: 
* @FilePath: \TVSpider\js\xgcartoon.js
* @
*/
import * as Utils from "../lib/utils.js";
import {_, load} from "../lib/cat.js";
import {VodDetail, VodShort} from "../lib/vod.js";
import {Spider} from "./spider.js";


class XGCartoonSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://cn.xgcartoon.com/"
        this.nextObj = {}
    }


    getName() {
        return `🍉┃西瓜卡通┃🍉`
    }

    getAppName() {
        return "西瓜卡通"
    }
    

    getJSName() {
        return "xgcartoon"
    }

    getType() {
        return 3
    }


    async setClasses() {
      let $ = await this.getHtml(this.siteUrl)
      let navElements = $('[class="index-tab"]').find("a")
      for (const navElement of navElements){
        let type_name = $(navElement).text()
        let type_id = navElement.attribs.href
        this.classes.push(this.getTypeDic(type_name,type_id))
      }
      let x = 0
    }


    async parseVodShortListFromJson(obj) {
        let vod_list = []
        for (const data of obj) {
            let vodShort = new VodShort()
            vodShort.vod_id = data["vodId"]
            vodShort.vod_name = data["vodName"]
            vodShort.vod_remarks = data["watchingCountDesc"]
            vodShort.vod_pic = data["coverImg"]
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodDetailfromJson(obj) {
        let vodDetail = new VodDetail()
        
        return vodDetail
    }

    async setHomeVod() {

    }

    async setCategory(tid, pg, filter, extend) {
       


    }

    async setDetail(id) {

    }

    async setPlay(flag, id, flags) {
 
    }

    async setSearch(wd, quick) {
       
    }

}

let spider = new XGCartoonSpider()

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