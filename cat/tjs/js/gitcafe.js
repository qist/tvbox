/*
* @File     : gitcafe.js
* @Author   : jade
* @Date     : 2024/1/18 9:56
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 阿里纸条
*/

import {_, load} from "../lib/cat.js";
import {Spider} from "./spider.js";
import { detailContent,initCloud,playContent,getHeaders} from "../lib/cloud.js";
import * as Utils from "../lib/utils.js";
import {VodDetail, VodShort} from "../lib/vod.js";

class GitCafeSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://ali.gitcafe.ink"
    }

    getName() {
        return "🦊┃阿里纸条┃🦊"
    }

    getAppName() {
        return "阿里纸条"
    }

    getJSName() {
        return "gitcafe"
    }

    getType() {
        return 3
    }

    async getApiUrl() {
        let html = await this.fetch(this.siteUrl, null, this.getHeader())
        if (!_.isEmpty(html)) {
            let paper_js_url = Utils.getStrByRegex(/<script src='(.*?)'><\/script>/, html)
            let paper_js_content = await this.fetch(paper_js_url, null, this.getHeader())
            return {
                "api": "https:" + Utils.getStrByRegex(/ return '(.*?)' \+ /, paper_js_content) + new Date().getTime(),
                "search_api": Utils.getStrByRegex(/const SEARCH_API = '(.*?)';/, paper_js_content)

            }
        }
    }

    async getContentJson() {
        let url_json = await this.getApiUrl()
        let content = await this.fetch(url_json["api"], null, this.getHeader())
        this.search_api = url_json["search_api"]
        if (!_.isEmpty(content)) {
            return JSON.parse(content)
        }
    }

    async spiderInit() {
        this.content_json = await this.getContentJson()
        this.token_dic = await this.load_cache()
    }

    async init(cfg) {
        await this.spiderInit()
        await super.init(cfg);
        await initCloud(this.cfgObj);
    }


    async parseClassFromJson(obj) {
        let data_list = Object.keys(obj["data"]).slice(0, 19)
        for (const data_key of data_list) {
            this.classes.push({"type_name": obj["data"][data_key]["name"], "type_id": data_key})
        }
    }


    async parseVodShortListFromJson(obj) {
        let vod_list = []
        let class_id_list = this.getClassIdList()
        for (const data_obj of obj) {
            let vodShort = new VodShort()
            if (class_id_list.includes(data_obj["cat"])) {
                vodShort.vod_id = JSON.stringify(data_obj)
                vodShort.vod_name = data_obj["title"]
                vodShort.vod_remarks = data_obj["date"]
                vod_list.push(vodShort)
            }
        }
        return vod_list

    }

    async parseVodDetailfromJson(obj) {
        let classNamesList = this.getClassNameList()
        let classIdList = this.getClassIdList()
        let vodDetail = new VodDetail()
        vodDetail.vod_name = obj["title"]
        vodDetail.vod_remarks = obj["creatime"] ?? obj["date"]
        vodDetail.type_name = classNamesList[classIdList.indexOf(obj["cat"])]
        vodDetail.vod_content = obj["des"]
        let ali_url = "https://www.aliyundrive.com/s/" + obj["alikey"]
        let playVod = await detailContent([ali_url],vodDetail.type_name)
        vodDetail.vod_play_from = _.keys(playVod).join('$$$');
        vodDetail.vod_play_url = _.values(playVod).join('$$$');

        
        return vodDetail
    }

    async setClasses() {
        await this.parseClassFromJson(this.content_json)
    }


    async setHomeVod() {
        this.homeVodList = await this.parseVodShortListFromJson(this.content_json["info"]["new"])
    }


    async setDetail(id) {
        let content_json = JSON.parse(id)
        this.vodDetail = await this.parseVodDetailfromJson(content_json)
    }

    async setCategory(tid, pg, filter, extend) {
        this.vodList = await this.parseVodShortListFromJson(this.content_json["data"][tid]["catdata"])
    }

    async setSearch(wd, quick) {
        await this.refreshToken();
        let params = {
            "action": "search", "from": "web", "token": this.token_dic["token"], "keyword": wd
        }
        let content = await this.post(this.search_api, params, this.getHeader())
        if (!_.isEmpty(content)) {
            let content_json = JSON.parse(content)
            this.vodList = await this.parseVodShortListFromJson(content_json["data"])
        }
    }

    async refreshToken() {
        let this_time = new Date().getTime()
        if (_.isEmpty(this.token_dic["token"])) {
            await this.get_token()
            await this.jadeLog.debug("Token为空,刷新Token")
        } else if (this_time - parseInt(this.token_dic["date"]) > 24 * 60 * 60 * 1000) {
            await this.jadeLog.debug(`Token到期,上次获取Token时间为:${this_time},当前时间为:${parseInt(this.token_dic["date"])},刷新Token`)
            await this.get_token()
        } else {
            await this.jadeLog.debug(`Token仍然有效,无需刷新`, true)
        }
    }

    async get_token() {

        try {
            let params = {
                "action": "get_token", "from": "web",
            }
            let content = await this.post(this.search_api, params, this.getHeader())
            if (!_.isEmpty(content)) {
                let content_json = JSON.parse(content)
                let this_time = new Date().getTime()
                this.token_dic["token"] = content_json["data"]
                this.token_dic["date"] = this_time.toString()
                await this.write_cache()
            }
        } catch (e) {
            await this.jadeLog.error("获取Token失败,失败原因为:" + e)
        }
    }

    async write_cache() {
        await local.set("gitcafe_token", "token", JSON.stringify(this.token_dic))
    }

    async load_cache() {
        try {
            let str = await local.get("gitcafe_token", "token")
            return JSON.parse(str)
        } catch (e) {
            return {"token": "", "date": ""}
        }
    }
    async setPlay(flag, id, flags) {
        this.playUrl = await playContent(flag, id, flags);
        this.result.setHeader(getHeaders(flag))
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