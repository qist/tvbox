/*
* @File     : hanxiucao.js
* @Author   : jade
* @Date     : 2024/04/13 19:38
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/
import {_, Crypto} from '../lib/cat.js';
import {VodDetail, VodShort} from "../lib/vod.js"
import {Spider} from "./spider.js";
import * as Utils from "../lib/utils.js";


function He(e, {key: t, iv: s} = {}) {
    let VITE_APP_AES_KEY = "B77A9FF7F323B5404902102257503C2F"
    let VITE_APP_AES_IV = "B77A9FF7F323B5404902102257503C2F"
    var o = Crypto.enc.Utf8.parse(e)
        , A = Crypto.AES.encrypt(o, Crypto.enc.Utf8.parse(t || VITE_APP_AES_KEY), {
        iv: Crypto.enc.Utf8.parse(s || VITE_APP_AES_IV),
        mode: Crypto.mode.CBC,
        padding: Crypto.pad.Pkcs7
    });
    return Crypto.enc.Base64.stringify(A.ciphertext)
}

function Kt() {
    const e = new Date;
    return He(parseInt(e.getTime() / 1e3) + e.getTimezoneOffset() * 60 + -1)
}

function bt(e) {
    const wA = "46cc793c53dc451b"
    let t = Crypto.enc.Utf8.parse(wA)
        , s = Crypto.AES.decrypt(e, t, {
        mode: Crypto.mode.ECB,
        padding: Crypto.pad.Pkcs7
    });
    return Crypto.enc.Utf8.stringify(s).toString()
}

class HanXiuCaoSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://api.qianyuewenhua.xyz"
    }

    async spiderInit(inReq = null) {
        if (inReq !== null) {
            this.jsBase = await js2Proxy(inReq, "imgBt", this.getHeader());
        } else {
            this.jsBase = await js2Proxy(true, this.siteType, this.siteKey, 'imgBt/', this.getHeader());
        }

    }

    async init(cfg) {
        await super.init(cfg);
        this.danmuStaus = true
        await this.spiderInit(null)
    }

    getAppName() {
        return "含羞草"
    }

    getName() {
        return "🔞┃含羞草┃🔞"
    }

    getJSName() {
        return "hanxiucao"
    }

    getType() {
        return 3
    }

    getParams(params) {
        return {"endata": He(JSON.stringify(params)), "ents": Kt()}
    }

    async setClasses() {
        let params = this.getParams({"channel": "pc"})
        let response = await this.post(this.siteUrl + "/panel/list", params, this.getHeader(), "")
        let resJson = JSON.parse(response)
        for (const data of resJson["data"]["list"]) {
            let type_id = data["panelId"]
            let type_name = data["panelName"]
            if (type_name !== "首页") {
                this.classes.push(this.getTypeDic(type_name, type_id))
            }
        }
    }

    async getFilter(Layouts) {
        let extend_list = []
        for (const data of Layouts) {
            let layoutObj = JSON.parse(data["layoutContent"])
            for (const layout of layoutObj["sortKeys"]) {
                let extend_dic = {}
                if (layout["label"] !== "综合排序") {
                    extend_dic = {"key": "sorts", "name": layout["label"].toString(), value: []}
                    extend_dic["value"].push({"n": "升序", "v": layout["value"].toString() + "-" + "升序"})
                    extend_dic["value"].push({"n": "降序", "v": layout["value"].toString() + "-" + "降序"})
                } else {
                    extend_dic = {"key": "sorts", "name": "排序", value: []}
                    extend_dic["value"].push({"n": layout["label"].toString(), "v": layout["value"].toString()})
                }
                extend_list.push(extend_dic)
            }
        }

        return extend_list
    }


    async getNvYouFilter(Layouts) {
        let extend_list = []
        let params = {
            "uids": [],
            "page": 1,
            "length": 20
        }
        for (let i = 0; i < Layouts.length; i++) {
            let data = Layouts[i]
            let layoutObj = JSON.parse(data["layoutContent"])
            params["uids"] = layoutObj["list"]
            let resJson = JSON.parse(await this.post(this.siteUrl + "/user/getUpList", this.getParams(params), this.getHeader(), ""))
            let extend_dic = {"key": `tags`, "name": data["layoutName"], value: []}
            for (const layout of resJson["data"]["list"]) {
                extend_dic["value"].push({"n": layout["user_nicename"], "v": JSON.stringify(layout)})
            }
            extend_list.push(extend_dic)
        }
        let sort_list = [
            {
                "key": "sorts",
                "name": "发布时间",
                "value": [
                    {
                        "n": "升序",
                        "v": "1-升序"
                    },
                    {
                        "n": "降序",
                        "v": "1-降序"
                    }
                ]
            },
            {
                "key": "sorts",
                "name": "点赞数量",
                "value": [
                    {
                        "n": "升序",
                        "v": "5-升序"
                    },
                    {
                        "n": "降序",
                        "v": "5-降序"
                    }
                ]
            },
            {
                "key": "sorts",
                "name": "收藏数量",
                "value": [
                    {
                        "n": "升序",
                        "v": "6-升序"
                    },
                    {
                        "n": "降序",
                        "v": "6-降序"
                    }
                ]
            }
        ]
        return [...extend_list, ...sort_list]
    }

    async getZhuanTiFilter(Layouts) {
        let extend_list = []
        let params = {
            "page": 1,
            "length": 36,
            "subjectIds": []
        }
        for (let i = 0; i < Layouts.length; i++) {
            let data = Layouts[i]
            let layoutObj = JSON.parse(data["layoutContent"])
            params["subjectIds"] = layoutObj["list"]
            let resJson = JSON.parse(await this.post(this.siteUrl + "/subject/list", this.getParams(params), this.getHeader(), ""))
            let extend_dic = {"key": `tags`, "name": data["layoutName"], value: []}
            for (const layout of resJson["data"]["list"]) {
                extend_dic["value"].push({"n": layout["name"], "v": JSON.stringify(layout)})
            }
            extend_list.push(extend_dic)
        }
        let sort_dic = {
            "key": "sorts",
            "name": "排序",
            "value": [
                {
                    "n": "推荐",
                    "v": "8"
                },
                {
                    "n": "最新",
                    "v": "1"
                },
                {
                    "n": "最热",
                    "v": "2"
                }
            ]
        }
        extend_list.push(sort_dic)
        return extend_list
    }

    async getChuanMeiFilter(Layouts) {
        let extend_list = []
        let extend_dic = {"key": `tags`, "name": "传媒", value: []}
        for (let i = 0; i < Layouts.length; i++) {
            let data = Layouts[i]
            extend_dic["value"].push({"n": data["layoutName"], "v": data["layoutContent"]})
        }
        extend_list.push(extend_dic)

        for (const layout of JSON.parse(Layouts[0]["layoutContent"])["moreOrderType"]) {
            extend_dic = {"key": "sorts", "name": layout["label"].toString(), value: []}
            extend_dic["value"].push({"n": "升序", "v": layout["value"].toString() + "-" + "升序"})
            extend_dic["value"].push({"n": "降序", "v": layout["value"].toString() + "-" + "降序"})
            extend_list.push(extend_dic)
        }

        extend_list.push(extend_dic)
        return extend_list
    }

    async getHeJiFilter(Layouts) {
        let extend_list = []
        let params = {
            "page": 1,
            "length": 24,
            "gatherType": 1,
            "gatherIds": []
        }
        let extend_dic = {"key": `tags`, "name": "合集", value: []}
        let resJson = JSON.parse(await this.post(this.siteUrl + "/gather/getList", this.getParams(params), this.getHeader(), ""))
        for (const data of resJson["data"]["list"]) {
            extend_dic["value"].push({"n": data["name"], "v": data["gatherId"].toString()})
        }
        extend_list.push(extend_dic)
        return extend_list
    }

    async setFilterObj() {
        for (let i = 0; i < this.classes.length; i++) {
            let type_dic = this.classes[i]
            let type_id = type_dic["type_id"]
            let type_name = type_dic["type_name"]
            let filterList = []
            if (type_id !== "最近更新") {
                type_id = parseInt(type_id)
                let params = this.getParams({"panelId": type_id})
                let response = await this.post(this.siteUrl + "/panel/get", params, this.getHeader(), "")
                let resJson = JSON.parse(response)
                let layoutList = resJson["data"]["info"]["Layouts"]
                let layOutObj = JSON.parse(resJson["data"]["info"]["Layouts"][0]["layoutContent"])
                if (type_id > 174 && type_id < 181) {
                    let layOutObj = JSON.parse(resJson["data"]["info"]["Layouts"][0]["layoutContent"])
                    type_id = type_id + "$" + JSON.stringify(layOutObj)
                    filterList = await this.getFilter(layoutList)
                } else {
                    switch (type_id) {
                        case 172:
                            filterList = await this.getHeJiFilter(layoutList)
                            type_id = type_id + "$" + filterList[0]["value"][0]["v"]
                            break
                        case 173:
                            filterList = await this.getChuanMeiFilter(layoutList)
                            type_id = type_id + "$" + JSON.stringify(layOutObj)
                            break
                        case 182:
                            filterList = await this.getNvYouFilter(layoutList)
                            type_id = type_id + "$" + filterList[0]["value"][0]["v"]
                            break
                        case 209:
                            filterList = await this.getZhuanTiFilter(layoutList)
                            type_id = type_id + "$" + filterList[0]["value"][0]["v"]
                            break
                        default:
                            break
                    }
                }
                this.classes[i] = this.getTypeDic(type_name, type_id)
                this.filterObj[type_id] = filterList
            }
        }
    }

    async parseVodShortListFromJson(obj) {
        let vod_list = []
        for (const data of obj) {
            let vodShort = new VodShort()
            vodShort.vod_id = data["id"]
            vodShort.vod_name = data["name"]
            vodShort.vod_pic = this.jsBase + Utils.base64Encode(data["coverImgUrl"])
            if (data["hot"] === undefined) {
                vodShort.vod_remarks = "观看:" + (data["seeCount"] / 10000).toFixed(1).toString() + "W"
            } else {
                vodShort.vod_remarks = "热度:" + (data["hot"] / 1000).toFixed(1).toString() + "K"
            }
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodShortListFromGatherJson(obj) {
        let vod_list = []
        for (const data of obj) {
            let vodShort = new VodShort()
            vodShort.vod_id = data["gatherId"]
            vodShort.vod_name = data["name"]
            vodShort.vod_pic = this.jsBase + Utils.base64Encode(data["coverImgUrl"])
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodDetailFromDoc(detailObj) {
        let vodDetail = new VodDetail()
        vodDetail.vod_name = detailObj["name"]
        vodDetail.vod_year = detailObj["addTime"]
        vodDetail.vod_pic = this.jsBase + Utils.base64Encode(detailObj["coverImgUrl"])
        vodDetail.type_name = detailObj["typeName"]
        vodDetail.vod_content = detailObj["tags"]
        let vodItems = []
        let params = {
            "videoId": detailObj["id"]
        }
        let resJson = JSON.parse(await this.post(this.siteUrl + "/videos/getPreUrl", this.getParams(params), this.getHeader(), ""))
        let playList = resJson["data"]["url"].split("?")
        let playUrl = playList[0] + "?sign" + playList[1].split("&sign").slice(-1)[0]
        vodItems.push(vodDetail.vod_name + "$" + playUrl)
        let playObj = {"线路1": vodItems.join("#")}
        vodDetail.vod_play_url = _.values(playObj).join('$$$');
        vodDetail.vod_play_from = _.keys(playObj).join('$$$');
        return vodDetail

    }

    async getHomeVod(params) {
        let params_str = this.getParams(params)
        let response = await this.post(this.siteUrl + "/videos/getList", params_str, this.getHeader(), "")
        return await this.parseVodShortListFromJson(JSON.parse(response)["data"]["list"])
    }


    async setHomeVod() {
        let vod_list1 = await this.getHomeVod({
            "page": 1,
            "length": 16,
            "offset": 0,
            "typeIds": [],
            "orderType": 1,
            "payType": [3, 4]
        })
        let vod_list2 = await this.getHomeVod({
            "page": 1,
            "length": 16,
            "offset": 0,
            "typeIds": [],
            "orderType": 3,
            "payType": [
                1
            ]
        })
        let vod_list3 = await this.getHomeVod({
            "page": 1,
            "length": 32,
            "offset": 0,
            "typeIds": [],
            "orderType": 1,
            "payType": [
                3
            ]
        })
        this.homeVodList = [...vod_list1, ...vod_list2, ...vod_list3];
    }


    getSortParams(params, extend) {
        let orderTypeStr = extend["sorts"] ?? ""
        if (!_.isEmpty(orderTypeStr)) {
            let orderType = orderTypeStr.split("-")[0]
            params["orderType"] = parseInt(orderType)
            let orderModeStr = orderTypeStr.split("-")[1]
            let orderMode = 0
            if (orderModeStr === "升序") {
                orderMode = "1"
            } else {
                orderMode = "0"
            }
            params["orderMode"] = parseInt(orderMode)
        }
        return params
    }

    getTopParams(type_id, layOutObj, pg, extend) {
        let defaultOderType
        if (type_id === 180) {
            defaultOderType = "1"
        } else {
            defaultOderType = "7"
        }
        let orderMode = "1"
        let orderType
        let orderTypeStr = extend["sorts"] ?? defaultOderType
        let isOrderModel = false
        if (orderTypeStr.indexOf("-") > -1) {
            orderType = orderTypeStr.split("-")[0]
            let orderModeStr = orderTypeStr.split("-")[1]
            if (orderModeStr === "升序") {
                orderMode = "1"
            } else {
                orderMode = "0"
            }
            isOrderModel = true
        } else {
            orderType = defaultOderType
        }
        let params = {
            "orderType": parseInt(orderType), //或者7
            "tags": [],
            "length": 11,
            "page": parseInt(pg),
            "typeIds": layOutObj["classs"],
            "payType": layOutObj["payType"],
        }
        if (isOrderModel) {
            params["orderMode"] = parseInt(orderMode)
        }
        return params
    }

    getChuanMeiParams(layOutObj, pg, extend) {
        let obj
        if (!_.isEmpty(extend["tags"])) {
            obj = JSON.parse(extend["tags"])
        } else {
            obj = layOutObj
        }
        let params = {
            "page": parseInt(pg),
            "length": 32,
            "offset": 32 * parseInt(pg - 1),
            "tag": obj["videoLables"].join(","),
            "typeIds": obj["classs"],
            "orderType": obj["orderType"],
            "payType": obj["payType"]
        }
        params = this.getSortParams(params, extend)
        return params
    }

    getNvYouParams(layoutObj, pg, extend) {
        let obj
        if (!_.isEmpty(extend["tags"])) {
            obj = JSON.parse(extend["tags"])
        } else {
            obj = layoutObj
        }
        let params = {"videoSort": 1, "touid": obj["id"], "page": parseInt(pg), "length": 12, "orderType": 1}
        params = this.getSortParams(params, extend)
        return params
    }

    getZhuantiParams(layoutObj, pg, extend) {
        let obj
        if (!_.isEmpty(extend["tags"])) {
            obj = JSON.parse(extend["tags"])
        } else {
            obj = layoutObj
        }
        let orderType = extend["sorts"] ?? "8"
        return {
            "page": parseInt(pg),
            "length": 12,
            "offset": 12 * (parseInt(pg) - 1),
            "orderType": parseInt(orderType),
            "subjectId": obj["id"]
        }
    }

    async setCategory(tid, pg, filter, extend) {
        let tid_list = tid.split("$")
        let type_id = parseInt(tid_list[0])
        let layOutObj = JSON.parse(tid_list[1])
        let params = {}
        let url = "/videos/getList"
        if (type_id > 174 && type_id < 181) {
            params = this.getTopParams(type_id, layOutObj, pg, extend)
        } else {
            switch (type_id) {
                case 173:
                    params = this.getChuanMeiParams(layOutObj, pg, extend)
                    break
                case 182:
                    params = this.getNvYouParams(layOutObj, pg, extend)
                    url = "/user/getSpaceVideo"
                    break
                case  209:
                    params = this.getZhuantiParams(layOutObj, pg, extend)
                    break
                case 172:
                    let gatherId = extend["tags"] ?? layOutObj
                    params = {
                        "gatherId": parseInt(gatherId)
                    }
                    url = "/gather/getDetail"
                    break
                default:
                    break
            }

        }
        let resJson = JSON.parse(await this.post(this.siteUrl + url, this.getParams(params), this.getHeader(), ""))
        if (type_id === 172) {
            this.vodList = await this.parseVodShortListFromJson(resJson["data"]["info"]["videos"])
        } else {
            this.vodList = await this.parseVodShortListFromJson(resJson["data"]["list"])
        }
    }


    async setDetail(id) {
        let params = {
            "videoId": parseInt(id),
            "videoSort": 1
        }
        let resJson = JSON.parse(await this.post(this.siteUrl + "/videos/getInfo", this.getParams(params), this.getHeader(), ""))
        this.vodDetail = await this.parseVodDetailFromDoc(resJson["data"]["info"])
    }


    async proxy(segments, headers) {
        let what = segments[0];
        let url = Utils.base64Decode(segments[1]);
        if (what === 'imgBt') {
            let response = await req(url, {buffer: 0});
            return JSON.stringify({
                code: 200,
                buffer: 2,
                content: bt(response.content).replaceAll("data:image/jpeg;base64,", "").replaceAll("data:image/jpg;base64,", "").replaceAll("data:image/png;base64", ""),
                headers: headers,
            });
        }
    }


    async setSearch(wd, quick, pg) {
        let params = {
            "page": parseInt(pg),
            "length": 12,
            "type": 1,
            "key": wd
        }
        let resJson = JSON.parse(await this.post(this.siteUrl + "/base/globalSearch", this.getParams(params), this.getHeader(), ""))
        this.vodList = await this.parseVodShortListFromJson(resJson["data"]["infos"])
        this.result.setPage(parseInt(pg), resJson["data"]["count"] / 12, 12, resJson["data"]["count"])
    }
}

let spider = new HanXiuCaoSpider()

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

export {spider, bt}