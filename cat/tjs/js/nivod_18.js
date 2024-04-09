/*
* @File     : nivod18.js
* @Author   : jade
* @Date     : 2023/12/19 14:23
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/
import {getHeader, createSign, desDecrypt, ChannelResponse, getVod} from "../lib/nivid_object.js"
import {VodDetail, VodShort} from "../lib/vod.js";
import {Spider} from "./spider.js";

class Nivod18Spider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://api.nivodz.com"

    }
    getName() {
        return "🔞┃泥视频18+┃🔞"
    }
    getAppName() {
        return "泥视频18+"
    }
    getJSName() {
        return "nivod_18"
    }

    getType() {
        return 3
    }


    async setClasses() {
        let url = this.siteUrl + "/show/channel/list/WEB/3.2" + await createSign()
        let content = desDecrypt(await this.post(url, null, getHeader()))
        if (content !== null) {
            let channelResponse = new ChannelResponse()
            channelResponse.fromJsonString(content, 2)
            let filterUrl = this.siteUrl + "/show/filter/condition/WEB/3.2" + await createSign()
            let filterContent = desDecrypt(await this.post(filterUrl, null, getHeader()))
            if (filterContent !== null) {
                channelResponse.setChannelFilters(filterContent)
                this.classes = channelResponse.getClassList()
                this.filterObj = channelResponse.getFilters()
            }
        }
    }
    async parseVodShortListFromJson(obj) {
        let vod_list = []
        for (const cate_dic of obj) {
            for (const row of cate_dic.rows) {
                for (const cells of row.cells) {
                    let vodShort = new VodShort()
                    vodShort.vod_id = cells.show["showIdCode"]
                    vodShort.vod_pic = cells.img
                    vodShort.vod_name = cells.title
                    vodShort.vod_remarks = this.getVodRemarks(cells.show["hot"], cells.show["playResolutions"])
                    vod_list.push(vodShort)
                }
            }
        }
        return vod_list
    }

    async parseVodDetailfromJson(vod_dic) {
        let vodDetail = new VodDetail()
        vodDetail.vod_id = vod_dic["showIdCode"]
        vodDetail.vod_name = vod_dic["showTitle"]
        vodDetail.vod_remarks = this.getVodRemarks(vod_dic["hot"], vod_dic["playResolutions"])
        vodDetail.vod_pic = vod_dic["showImg"]
        vodDetail.vod_director = vod_dic["director"]
        vodDetail.vod_actor = vod_dic["actors"]
        vodDetail.vod_year = vod_dic["postYear"]
        vodDetail.vod_content = vod_dic["showDesc"]
        vodDetail.type_name = vod_dic["showTypeName"]
        vodDetail.vod_area = vod_dic["regionName"]
        return vodDetail
    }


    getVodRemarks(hot, playResolutions) {
        let vod_remarks
        if (this.catOpenStatus) {
            vod_remarks = `清晰度:${playResolutions[0]}`
        } else {
            vod_remarks = `清晰度:${playResolutions[0]},热度:${(Math.floor(parseInt(hot) / 1000)).toString()}k`
        }
        return vod_remarks
    }

    getExtendDic(extend, params) {
        if (extend["5"] === undefined) {
            delete params.year_range
        } else {
            if (extend["5"] === "0") {
                delete params.year_range
            } else {
                params.year_range = extend["5"]
            }
        }
        if (extend["1"] !== undefined) {
            params.sort_by = extend["1"]
        }
        if (extend["2"] !== undefined) {
            params.show_type_id = extend["2"]
        }
        if (extend["3"] !== undefined) {
            params.region_id = extend["3"]
        }
        if (extend["4"] !== undefined) {
            params.lang_id = extend["4"]
        }
        return params
    }

    async setHomeVod() {
        let url = this.siteUrl + "/index/mobile/WAP/3.0" + await createSign()
        let content = desDecrypt(await this.post(url, null, getHeader()))
        if (content !== null) {
            let content_json = JSON.parse(content)
            let cate_list = content_json.list
            for (const cate_dic of cate_list) {
                for (const row of cate_dic.rows) {
                    for (const cells of row.cells) {
                        let vodShort = new VodShort()
                        vodShort.vod_id = cells.show["showIdCode"]
                        vodShort.vod_pic = cells.img
                        vodShort.vod_name = cells.title
                        vodShort.vod_remarks = this.getVodRemarks(cells.show["hot"], cells.show["playResolutions"])
                        this.homeVodList.push(vodShort)
                    }
                }
            }
        }
    }
    async setCategory(tid, pg, filter, extend) {
        let params = {
            "sort_by": "0",
            "channel_id": tid.toString(),
            "show_type_id": "0",
            "region_id": "0",
            "lang_id": "0",
            "year_range": "2023",
            "start": ((parseInt(pg) - 1) * 20).toString()
        }
        this.limit = 20;
        params = this.getExtendDic(extend, params)
        let url = this.siteUrl + "/show/filter/WEB/3.2" + await createSign(params)
        let content = desDecrypt(await this.post(url, params, getHeader()))
        if (content != null) {
            let content_json = JSON.parse(content)
            for (const vod_dic of content_json["list"]) {
                let vodShort = new VodShort()
                vodShort.vod_id = vod_dic["showIdCode"]
                vodShort.vod_name = vod_dic["showTitle"]
                vodShort.vod_pic = vod_dic["showImg"]
                vodShort.vod_remarks = this.getVodRemarks(vod_dic["hot"], vod_dic["playResolutions"])
                this.vodList.push(vodShort)
            }
        }
    }

    async setDetail(id) {
        let params = {
            "show_id_code": id.toString()
        }
        let url = this.siteUrl + "/show/detail/WEB/3.2" + await createSign(params)
        let content = desDecrypt(await this.post(url, params, getHeader()))
        if (content != null) {
            let content_json = JSON.parse(content)
            let vod_dic = content_json["entity"]
            this.vodDetail = await this.parseVodDetailfromJson(vod_dic)
            let niBaVodDetail = getVod(vod_dic["plays"], ["原画"], id.toString())
            this.vodDetail.vod_play_from = niBaVodDetail.vod_play_from
            this.vodDetail.vod_play_url = niBaVodDetail.vod_play_url
        }
    }
    async setSearch(wd, quick) {
        let params = {"cat_id": "1", "keyword": wd, "keyword_type": "0", "start": "0"}
        let url = this.siteUrl + "/show/search/WEB/3.2" + await createSign(params)
        let content = desDecrypt(await this.post(url, params, getHeader()))
        if (content != null) {
            let content_json = JSON.parse(content)
            for (const vod_dic of content_json["list"]) {
                let vod_detail = await this.parseVodDetailfromJson(vod_dic)
                this.vodList.push(vod_detail)
            }
        }
    }
    async setPlay(flag, id, flags) {
        let playId = id.split("@")[0]
        let showId = id.split("@")[1]
        let params = {
            "show_id_code": showId,
            "play_id_code": playId
        }
        let url = this.siteUrl + "/show/play/info/WEB/3.2" + await createSign(params)
        let content = desDecrypt(await this.post(url, params,getHeader()))
        if (content != null) {
            let content_json = JSON.parse(content)
            this.playUrl = content_json["entity"]["playUrl"]
        }
    }
}

let spider = new Nivod18Spider()

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