/*
* @File     : cntv.js
* @Author   : jade
* @Date     : 2024/4/25 10:26
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/
import {Spider} from "./spider.js";
import {_} from "../lib/cat.js";
import * as Utils from "../lib/utils.js";
import {VodDetail, VodShort} from "../lib/vod.js";

class CNTVSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://tv.cctv.com/m/index.shtml"
        this.apiUrl = "https://api.app.cctv.com"
        this.liveJsonUrl = "https://gh.con.sh/https://github.com/jadehh/LiveSpider/blob/main/json/live.json"

    }

    getName() {
        return "🤵‍♂️┃中央影视┃🤵‍♂️"
    }

    getAppName() {
        return "中央影视"
    }

    getJSName() {
        return "cntv"
    }

    getType() {
        return 3
    }

    async spiderInit() {
        await super.spiderInit();
        this.liveJson = JSON.parse(await this.fetch(this.liveJsonUrl, null, null))
    }

    async init(cfg) {
        await super.init(cfg);
        await this.spiderInit()
    }

    async getFilterByLive(dataList) {
        let extend_list = []
        let extend_dic = {"key": "live", "name": "直播", "value": []}
        for (const data of dataList) {
            if (data["appBarTitle"] !== "最近常看") {
                extend_dic["value"].push({"n": data["appBarTitle"], "v": data["pageId"]})
            }
        }
        extend_list.push(extend_dic)
        return extend_list
    }

    arrayIsinclude(str, items) {
        let isInclude = false
        for (const data of items) {
            if (str === data["title"]) {
                return true
            }
        }
        return isInclude
    }

    async getFilterByTv(dataList) {
        let extend_list = []
        for (const data of dataList) {
            let add_year_status = false
            let extend_dic = {"key": data["classname"], "name": data["title"], "value": []}
            for (const extendData of data["items"]) {
                if (data["classname"] === "nianfen") {
                    if (!this.arrayIsinclude("2024", data["items"]) && extendData["title"] !== "全部" && !add_year_status) {
                        extend_dic["value"].push({"n": "2024", "v": "2024"})
                        add_year_status = true
                    }
                }
                extend_dic["value"].push({"n": extendData["title"], "v": extendData["title"]})
            }
            extend_list.push(extend_dic)
        }
        return extend_list
    }

    async setClasses() {
        let liveTypeId = "cctvlive"
        let liveApi = this.apiUrl + `/api/navigation/iphone/AppStore/7.9.4/${liveTypeId}`
        let liveJson = JSON.parse(await this.fetch(liveApi, null, this.getHeader()))
        let extend_list = await this.getFilterByLive(liveJson["data"]["templates"])
        let defaultLiveId = extend_list[0]["value"][0]["v"]
        this.classes.push(this.getTypeDic("直播", defaultLiveId))
        this.filterObj[defaultLiveId] = extend_list
        let tvApi = "https://cbox.cctv.com/cboxpcvip/online2022/yxg/data1.jsonp?=pk"
        let tvContent = await this.fetch(tvApi, null, this.getHeader())
        let tvJSon = JSON.parse(tvContent.replaceAll("pk(", "").replaceAll(")", ""))
        for (const data of tvJSon["data"]) {
            let typeName = data["title"]
            this.classes.push(this.getTypeDic(typeName, typeName))
            this.filterObj[typeName] = await this.getFilterByTv(data["templates"])

        }
    }

    parseVodShortByJson(items) {
        let vod_list = []
        for (const item of items) {
            let vodShort = new VodShort()
            vodShort.vod_pic = item["img1"]
            if (_.isEmpty(vodShort.vod_pic)) {
                vodShort.vod_pic = item["epgHorizontalPic"]
                vodShort.vod_id = "live-" + item["epgChnlChar"] + "-" + vodShort.vod_pic
            } else {
                vodShort.vod_id = "play-" + item["playid"] + "-" + vodShort.vod_pic
                vodShort.vod_pic = item["img1"]
            }
            vodShort.vod_name = item["title"]
            vod_list.push(vodShort)
        }
        return vod_list
    }

    parseVodShortByTvJson(items) {
        let vod_list = []
        for (const item of items) {
            let vodShort = new VodShort()
            //关键是如何获取GUID 2d3224585904496ea837f682da0c4aa6
            vodShort.vod_id = "url-" + item["vsetid"]
            vodShort.vod_name = item["title"]
            vodShort.vod_pic = item["image"]
            vodShort.vod_remarks = item["sc"]
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodShortListFromJson(objList) {
        let vod_list = []
        let top_status = false
        for (const data of objList) {
            if (data["title"] === "今日热点") {
                top_status = true
            } else if (!_.isEmpty(data["title"])) {
                if (top_status) {
                    break
                }
            }
            if (top_status) {
                vod_list = [...vod_list, ...this.parseVodShortByJson(data["items"])]
            }
        }
        return vod_list
    }

    async getLiveUrl(channel_id, obj) {
        let liveApiUrl = `https://vdn.live.cntv.cn/api2/live.do?channel=pd://cctv_p2p_hd${channel_id}&client=iosapp`
        let liveResponse = await req(liveApiUrl, {"headers": this.getHeader()})
        let liveJson = JSON.parse(liveResponse["content"])
        let playList = {}
        let channelName = obj["channelName"].split(" ")[0].replaceAll("-", "").toLowerCase()
        let liveUrl = this.liveJson[channelName] ?? liveJson["hls_url"]["hls2"]
        playList["直播"] = ["点击播放$" + liveUrl]
        await this.jadeLog.info(`liveJson:${JSON.stringify(liveJson)}`)
        let vod_items = []
        if (this.liveJson[channelName] !== undefined) {

        } else {
            for (const data of obj["program"]) {
                let episodeName = data["showTime"] + "-" + data["t"]
                let episodeUrl = liveUrl + `?begintimeabs=${data["st"] * 1000}&endtimeabs=${data["et"] * 1000}`
                vod_items.push(episodeName + "$" + episodeUrl)
            }
        }
        if (vod_items.length > 0){
            playList["点播"] = vod_items.join("#")
        }
        return playList
    }


    async getVideoUrl(guid) {
        return {"中央影视": ['点击播放' + '$' + guid].join("#")}
    }

    async parseVodDetailfromJson(id, obj, pic) {
        let vodDetail = new VodDetail()
        let $;
        let guid;
        if (obj["url"] !== undefined) {
            vodDetail.vod_name = obj["title"]
            vodDetail.vod_pic = obj["img"]
            vodDetail.type_name = obj["tags"]
            vodDetail.vod_year = obj["time"]
            vodDetail.vod_content = obj["vset_brief"]
            vodDetail.vod_director = obj["vset_title"]
            $ = await this.getHtml(obj["url"])
        } else {
            if (_.isEmpty(obj["lvUrl"])) {
                vodDetail.vod_name = obj["channelName"]
                vodDetail.vod_pic = pic
            } else {
                $ = await this.getHtml(obj["lvUrl"])
                vodDetail.vod_name = $('[property$=title]')[0].attribs.content
                vodDetail.vod_content = $('[property$=description]')[0].attribs.content
                let pic = $('[property$=image]')[0].attribs.content
                if (!pic.startsWith("http")) {
                    pic = "https:" + pic
                }
                vodDetail.vod_pic = pic
            }

        }
        if (!_.isEmpty($)) {
            guid = Utils.getStrByRegex(/var guid = "(.*?)"/, $.html())
        }
        let playlist
        if (_.isEmpty(guid) && obj["url"] === undefined) {
            playlist = await this.getLiveUrl(id, obj)
        } else {
            playlist = await this.getVideoUrl(guid)
        }
        vodDetail.vod_play_url = _.values(playlist).join('$$$');
        vodDetail.vod_play_from = _.keys(playlist).join('$$$');
        return vodDetail
    }

    async parseVodDetailFromJsonByTv(obj) {
        let vodDetail = new VodDetail()
        vodDetail.vod_name = obj["videoSetInfo"]["title"]
        vodDetail.type_name = obj["videoSetInfo"]["sc"]
        vodDetail.vod_pic = obj["videoSetInfo"]["image"]
        vodDetail.vod_content = obj["videoSetInfo"]["brief"]
        vodDetail.vod_area = obj["videoSetInfo"]["area"]
        let playlist = {}
        let vodItems = []
        for (const data of obj["videoRoughCut"]) {
            let title = data["title"].split("》").slice(-1)[0]
            vodItems.push(title + "$" + data["guid"])
        }
        playlist["中央影视"] = vodItems.join("#")
        vodDetail.vod_play_url = _.values(playlist).join('$$$');
        vodDetail.vod_play_from = _.keys(playlist).join('$$$');
        return vodDetail
    }

    async setHomeVod() {
        let resJson = JSON.parse(await this.fetch(this.apiUrl + "/api/page/iphone/HandheldApplicationSink/7.0.0/158", null, this.getHeader()))
        this.homeVodList = await this.parseVodShortListFromJson(resJson["data"]["templates"])
    }

    getExtendValue(extend, key) {
        if (extend[key] !== undefined && extend[key] !== "全部") {
            return extend[key]
        }
        return ""
    }

    async setCategory(tid, pg, filter, extend) {
        if (Utils.isNumeric(tid)) {
            tid = extend["live"] ?? tid
            let url = this.apiUrl + `/api/page/iphone/HandheldApplicationSink/7.0.0/${tid}`
            let response = JSON.parse(await this.fetch(url, null, this.getHeader()))
            this.vodList = this.parseVodShortByJson(response["data"]["templates"][0]["items"])
        } else {
            let letter = this.getExtendValue(extend, "zimu")
            let area = this.getExtendValue(extend, "diqu")
            let type = this.getExtendValue(extend, "leixing")
            let year = this.getExtendValue(extend, "nianfen")
            const limit = 12
            let url = "https://api.cntv.cn" + `/newVideoset/getCboxVideoAlbumList`
            let params = {
                "channelid": "",
                "sc": type,
                "fc": tid,
                "p": pg,
                "n": limit,
                "fl": letter,
                "area": area,
                "year": year,
                "serviceId": "cbox"
            }
            let resJson = JSON.parse(await this.fetch(url, params, this.getHeader()))
            this.vodList = this.parseVodShortByTvJson(resJson["data"]["list"])
        }

    }

    async setDetail(id) {
        //区分直播还是点播
        let aList = id.split("-")
        let playType = aList[0]
        let pic = aList[2]
        id = aList[1]
        if (playType === "play") {
            let resJson = JSON.parse(await this.fetch(`https://api.cntv.cn/video/videoinfoByGuid?serviceId=cbox&guid=${id}`, null, this.getHeader()))
            this.vodDetail = await this.parseVodDetailfromJson(id, resJson, pic)
        } else if (playType === "url") {
            let url = `https://api.app.cctv.com/api/getVideoPageDetail?videoSetContentId=${id}`
            let resJson = JSON.parse(await this.fetch(url, null, this.getHeader()))
            this.vodDetail = await this.parseVodDetailFromJsonByTv(resJson["data"])
        } else {
            let content = (await this.fetch(`https://api.cntv.cn/epg/epginfo3?serviceId=shiyi&c=${id}&cb=LiveTileShow.prototype.getEpg`, null, this.getHeader())).replaceAll("LiveTileShow.prototype.getEpg(", "").replaceAll(");", "")
            this.vodDetail = await this.parseVodDetailfromJson(id, JSON.parse(content)[id], pic)
        }

    }

    async setSearch(wd, quick, pg) {

    }

    async setPlay(flag, id, flags) {
        if (id.startsWith("http")) {
            this.playUrl = id
            let headers = this.getHeader()
            headers["Referer"] = "https://tv.cctv.com/"
            this.result.header = headers
        } else {
            this.playUrl = 'https://hls.cntv.myhwcdn.cn/asp/hls/2000/0303000a/3/default/' + id + '/2000.m3u8'
        }
    }
}

let spider = new CNTVSpider()

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

export {spider, CNTVSpider}