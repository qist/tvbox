/*
* @File     : danmuSpider.js
* @Author   : jade
* @Date     : 2024/3/13 13:39
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/

import {_, load, Uri} from "./cat.js";
import * as Utils from "./utils.js";
import {JadeLogging} from "./log.js";
import {VodDetail, VodShort} from "./vod.js";
import {parseXML} from "./bilibili_ASS_Danmaku_Downloader.js";

class DanmuSpider {
    constructor() {
        this.siteUrl = "https://search.youku.com"
        this.reconnectTimes = 0
        this.maxReconnectTimes = 5
        this.jadeLog = new JadeLogging(this.getAppName(), "DEBUG")
    }

    getAppName() {
        return "弹幕"
    }

    getHeader() {
        return {"User-Agent": Utils.CHROME, "Referer": this.siteUrl + "/"};
    }

    async reconnnect(reqUrl, params, headers, redirect_url, return_cookie, buffer) {
        await this.jadeLog.error("请求失败,请检查url:" + reqUrl + ",两秒后重试")
        Utils.sleep(2)
        if (this.reconnectTimes < this.maxReconnectTimes) {
            this.reconnectTimes = this.reconnectTimes + 1
            return await this.fetch(reqUrl, params, headers, redirect_url, return_cookie, buffer)
        } else {
            await this.jadeLog.error("请求失败,重连失败")
            return null
        }
    }

    async getResponse(reqUrl, params, headers, redirect_url, return_cookie, buffer, response) {
        {
            if (response.headers["location"] !== undefined) {
                if (redirect_url) {
                    await this.jadeLog.debug(`返回重定向连接:${response.headers["location"]}`)
                    return response.headers["location"]
                } else {
                    return this.fetch(response.headers["location"], params, headers, redirect_url, return_cookie, buffer)
                }
            } else if (response.content.length > 0) {
                this.reconnectTimes = 0
                if (return_cookie) {
                    return {"cookie": response.headers["set-cookie"], "content": response.content}
                } else {
                    return response.content
                }
            } else if (buffer === 1) {
                this.reconnectTimes = 0
                return response.content
            } else {
                await this.jadeLog.error(`请求失败,请求url为:${reqUrl},回复内容为:${JSON.stringify(response)}`)
                return await this.reconnnect(reqUrl, params, headers, redirect_url, return_cookie, buffer)
            }
        }
    }


    async fetch(reqUrl, params, headers, redirect_url = false, return_cookie = false, buffer = 0) {
        let data = Utils.objectToStr(params)
        let url = reqUrl
        if (!_.isEmpty(data)) {
            url = reqUrl + "?" + data
        }
        let uri = new Uri(url);
        let response;
        response = await req(uri.toString(), {method: "get", headers: headers, buffer: buffer, data: null})
        if (response.code === 200 || response.code === 302 || response.code === 301 || return_cookie) {
            return await this.getResponse(reqUrl, params, headers, redirect_url, return_cookie, buffer, response)
        } else {
            await this.jadeLog.error(`请求失败,失败原因为:状态码出错,请求url为:${uri},回复内容为:${JSON.stringify(response)}`)
            return await this.reconnnect(reqUrl, params, headers, redirect_url, return_cookie, buffer)
        }
    }

    async getHtml(url = this.siteUrl, headers = this.getHeader()) {
        let html = await this.fetch(url, null, headers)
        if (!_.isEmpty(html)) {
            return load(html)
        } else {
            await this.jadeLog.error(`html获取失败`, true)
        }
    }

    async parseVodShortListFromJson(obj, vodDetail) {
        for (const componentObj of obj["pageComponentList"]) {
            if (componentObj["commonData"] !== undefined) {
                let searchVodDetail = new VodDetail()
                let commonData = componentObj["commonData"]
                searchVodDetail.type_name = commonData["feature"]
                if (commonData["notice"] !== undefined) {
                    searchVodDetail.vod_actor = commonData["notice"].replaceAll("演员：", "").replaceAll(" ", "")
                }
                if (commonData["director"] !== undefined) {
                    searchVodDetail.vod_director = commonData["director"].replaceAll("导演：", "").replaceAll(" ", "")
                }
                if (vodDetail.type_name === "电影") {
                    searchVodDetail.vod_id = commonData["leftButtonDTO"]["action"]["value"]
                } else {
                    searchVodDetail.vod_id = commonData["showId"]
                }
                searchVodDetail.vod_name = commonData["titleDTO"]["displayName"]
                if ( searchVodDetail.vod_name === vodDetail.vod_name || searchVodDetail.type_name.indexOf(vodDetail.vod_year) > -1 || searchVodDetail.type_name.indexOf(vodDetail.type_name) > -1   || searchVodDetail.vod_director === vodDetail.vod_director) {
                    await this.jadeLog.debug(`匹配视频网站成功,名称为:${searchVodDetail.vod_name},类型为:${searchVodDetail.type_name},导演为:${searchVodDetail.vod_director}`, true)
                    return searchVodDetail
                }
            }
        }
        await this.jadeLog.warning("没有匹配到弹幕网站")
        return null
    }

    async parseVodUrlFromJsonByEpisodeId(obj, episodeId) {
        for (const serises of obj["serisesList"]) {
            if (Utils.isNumeric(episodeId["episodeId"])) {
                if (parseInt(episodeId["episodeId"]).toString() === serises["displayName"]) {
                    return serises["action"]["value"]
                }
            }
        }
        await this.jadeLog.error("没有找到匹配的集数")
        return ""
    }

    async downloadDanmu(url) {
        let json = JSON.parse(await this.fetch(url, null, this.getHeader()))
        let xml = parseXML(json)
        let params = {"do": "set", "key": "danmu", "value": xml}
        await req("http://127.0.0.1:9978/cache", {method: "post", data: params, postType: "form-data"});
        return "http://127.0.0.1:9978/cache?do=get&key=danmu"
    }

    async search(vodDetail, episodeId) {
        let params = {"pg": "1", "keyword": vodDetail.vod_name}
        let searchObj = JSON.parse(await this.fetch(this.siteUrl + "/api/search", params, this.getHeader()))
        let searchDetail = await this.parseVodShortListFromJson(searchObj, vodDetail)
        if (!_.isEmpty(searchDetail)){
            return await this.getVideoUrl(searchDetail.vod_id, episodeId)
        }else{
            return ""
        }
    }

    async getVideoUrl(showId, episodeId) {
        let url = "";
        if (!_.isEmpty(showId)) {
            if (showId.startsWith("http")) {
                url = showId
            } else {
                let params = {"appScene": "show_episode", "showIds": showId}
                let matchObj = JSON.parse(await this.fetch(this.siteUrl + "/api/search", params, this.getHeader()))
                url = await this.parseVodUrlFromJsonByEpisodeId(matchObj, episodeId)
            }
            if (!_.isEmpty(url)) {
                await this.jadeLog.debug(`弹幕视频播放连接为:${url}`)
                return await this.downloadDanmu("https://dmku.thefilehosting.com/?ac=dm&url=" + url)
            }
        }
        return url

    }


    async getDammu(voddetail, episodeId) {
        return await this.search(voddetail, episodeId)
    }
}

export {DanmuSpider}