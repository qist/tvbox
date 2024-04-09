/*
* @File     : yiqikan.js
* @Author   : jade
* @Date     : 2024/3/19 18:45
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 一起看
*/
import * as Utils from "../lib/utils.js";
import {_, load} from "../lib/cat.js";
import {VodDetail, VodShort} from "../lib/vod.js";
import {Spider} from "./spider.js";


class YiQiKanSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://api.gquaxhce.com"
        this.nextObj = {}
    }

    async init(cfg) {
        await super.init(cfg);
        this.danmuStaus = true;
    }

    getRequestId() {
        let strArr = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"];
        let sb = "";
        for (let i = 0; i < 32; i++) {
            sb = sb + strArr[_.random(0, strArr.length)];
        }
        return sb.toString();
    }


    getName() {
        return "🛫┃一起看┃🛫"
    }

    getAppName() {
        return "一起看"
    }

    getJSName() {
        return "yiqikan"
    }

    getType() {
        return 3
    }

    getHeader() {
        let headers = super.getHeader();
        headers["Connection"] = "keep-alive"
        headers["Host"] = "api.gquaxhce.com"
        return headers
    }

    getParams(ob_params = null) {
        let requestId = this.getRequestId()
        let appid = "e6ddefe09e0349739874563459f56c54"
        let reqDomain = "m.yqktv888.com"
        let udid = Utils.getUUID();
        let appKey = "3359de478f8d45638125e446a10ec541"
        let params = {"appId": appid}
        if (!_.isEmpty(ob_params)) {
            for (const ob_key of Object.keys(ob_params)) {
                if (!_.isEmpty(ob_params[ob_key]) && (ob_key === "epId" || ob_key === "nextCount" || ob_key === "nextVal" || ob_key === "queryValueJson" || ob_key === "keyword")) {
                    params[ob_key] = ob_params[ob_key]
                }
            }
        }
        params["reqDomain"] = reqDomain
        params["requestId"] = requestId
        params["udid"] = udid
        if (!_.isEmpty(ob_params)) {
            for (const ob_key of Object.keys(ob_params)) {
                if (!_.isEmpty(ob_params[ob_key]) && (ob_key === "vodId" || ob_key === "vodResolution")) {
                    params[ob_key] = ob_params[ob_key]
                }
            }
        }
        params["appKey"] = appKey
        params["sign"] = md5X(Utils.objectToStr(params))
        delete params["appKey"]
        return params
    }

    async setClasses() {
        let response = JSON.parse(await this.post(this.siteUrl + "/v1/api/home/header", this.getParams(), this.getHeader(), "raw"))
        for (const data of response["data"]["channelList"]) {
            this.classes.push(this.getTypeDic(data["channelName"], data["channelId"]))
        }
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
        vodDetail.vod_name = obj["vodName"]
        vodDetail.vod_content = obj["intro"]
        vodDetail.vod_area = obj["areaName"]
        vodDetail.vod_year = obj["year"]
        vodDetail.type_name = obj["channelName"]
        vodDetail.vod_remarks = "评分:" + obj["score"].toString()
        vodDetail.vod_pic = obj["coverImg"]
        vodDetail.vod_actor = Utils.objToList(obj["actorList"], "vodWorkerName")
        vodDetail.vod_director = Utils.objToList(obj["directorList"], "vodWorkerName")
        let playlist = {}
        for (const playDic of obj["playerList"]) {
            let vodItems = []
            for (const item of playDic["epList"]) {
                let playId = item["epId"]
                let playName = item["epName"]
                vodItems.push(playName + "$" + playId)
            }
            playlist[playDic["playerName"]] = vodItems.join("#")
        }
        vodDetail.vod_play_url = _.values(playlist).join('$$$');
        vodDetail.vod_play_from = _.keys(playlist).join('$$$');
        return vodDetail
    }

    async setHomeVod() {
        let response = await this.post(this.siteUrl + "/v1/api/home/body", this.getParams(), this.getHeader(), "raw")
        let resJson = JSON.parse(response)
        if (resJson["result"]) {
            this.homeVodList = await this.parseVodShortListFromJson(resJson["data"]["hotVodList"])
        } else {
            await this.jadeLog.error(`获取首页失败,失败原因为:${resJson["msg"]}`)
        }
    }

    async setCategory(tid, pg, filter, extend) {
        let url = this.siteUrl + "/v1/api/search/queryNow"
        this.limit = 18
        let ob_params = {}
        if (!_.isEmpty(this.nextObj[tid])) {
            ob_params["nextVal"] = this.nextObj[tid]
        }
        ob_params["nextCount"] = 18
        ob_params["queryValueJson"] = JSON.stringify([{
            "filerName": "channelId", "filerValue": tid.toString()
        }]).replaceAll("\\\\", "")
        let response = await this.post(url, this.getParams(ob_params), this.getHeader(), "raw")
        let resJson = JSON.parse(response)
        if (resJson["result"]) {
            if (resJson["data"]["hasNext"]) {
                this.nextObj[tid] = resJson["data"]["nextVal"]
            }
            this.vodList = await this.parseVodShortListFromJson(resJson["data"]["items"])
        } else {
            await this.jadeLog.error(`获取分类失败,失败原因为:${resJson["msg"]}`)
        }


    }

    async setDetail(id) {
        let url = this.siteUrl + "/v1/api/vodInfo/detail"
        let ob_params = {"vodId": id}
        let response = await this.post(url, this.getParams(ob_params), this.getHeader(), "raw")
        let resJson = JSON.parse(response)
        if (resJson["result"]) {
            this.vodDetail = await this.parseVodDetailfromJson(resJson["data"])
        } else {
            await this.jadeLog.error(`获取详情失败,失败原因为:${resJson["msg"]}`)
        }
    }

    async setPlay(flag, id, flags) {
        let url = this.siteUrl + "/v1/api/vodInfo/getEpDetail"
        let ob_params = {"epId": id}
        let ep_detail_response = await this.post(url, this.getParams(ob_params), this.getHeader(), "raw")
        let ep_detail_resJson = JSON.parse(ep_detail_response)
        let vodResolution = "1";
        if (ep_detail_resJson["result"]) {
            if (ep_detail_resJson["data"]["resolutionItems"].length > 0) {
                vodResolution = ep_detail_resJson["data"]["resolutionItems"].slice(-1)[0]["vodResolution"].toString()
                let playUrl = this.siteUrl + "/v1/api/vodInfo/getPlayUrl"
                let play_params = {"epId": id, "vodResolution": vodResolution}
                let play_response = await this.post(playUrl, this.getParams(play_params), this.getHeader(), "raw")
                let play_resJson = JSON.parse(play_response)
                if (play_resJson["result"]) {
                    this.playUrl = play_resJson["data"]
                }else{
                    await this.jadeLog.error(`获取播放链接失败,失败原因为:${ep_detail_resJson["msg"]}`)
                }
            }
        } else {
            await this.jadeLog.error(`获取播放详情失败,失败原因为:${ep_detail_resJson["msg"]}`)
        }
    }

    async setSearch(wd, quick) {
        let url = this.siteUrl + "/v1/api/search/search"
        let ob_prams = {"nextCount":15,"nextVal":"","keyword":wd}
        let esponse = await this.post(url, this.getParams(ob_prams), this.getHeader(), "raw")
        let resJson = JSON.parse(esponse)
        if (resJson["result"]) {
            this.vodList = await this.parseVodShortListFromJson(resJson["data"]["items"])
        } else {
            await this.jadeLog.error(`获取详情失败,失败原因为:${resJson["msg"]}`)
        }
    }

}

let spider = new YiQiKanSpider()

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