/*
* @File     : pipixia.js
* @Author   : jade
* @Date     : 2024/2/2 13:33
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 完成所有的功能开发(已失效)
*/
import {_, Crypto, load} from '../lib/cat.js';
import {VodDetail, VodShort} from "../lib/vod.js"
import * as Utils from "../lib/utils.js";
import {Spider} from "./spider.js";
import {pipixiaMd5} from "../lib/pipiXiaObject.js"

class PiPiXiaSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "http://aikun.tv/"
        this.pipixiaReconnectTimes = 0
    }

    getHeader() {
        let headers = super.getHeader();
        headers["Connection"] = "keep-alive"
        headers["Host"] = "pipixia.vip"
        return headers
    }


    getName() {
        return `🦐┃皮皮虾影视┃🦐`
    }

    getAppName() {
        return `皮皮虾影视`
    }

    getJSName() {
        return "pipixia"
    }

    getType() {
        return 3
    }

    async parseVodShortListFromDoc($) {
        let vod_list = []
        let vodElements = $($("[class=\"wow fadeInUp animated\"]")).find("[class=\"public-list-box public-pic-b\"]")
        for (const vodElement of vodElements) {
            let vodShort = new VodShort()
            vodShort.vod_id = Utils.getStrByRegex(/v\/(.*?).html/, $(vodElement).find("a")[0].attribs.href)
            vodShort.vod_name = $(vodElement).find("a")[0].attribs.title
            vodShort.vod_pic = this.baseProxy + Utils.base64Encode(this.siteUrl + "/" + $(vodElement).find("[class=\"lazy gen-movie-img mask-1\"]")[0].attribs["data-original"])
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodShortListFromDocBySearch($) {
        let vod_list = []
        let vodElements = $("[class=\"row-right hide\"]").find("[class=\"search-box flex rel\"]")
        for (const vodElement of vodElements) {
            let vodShort = new VodShort();
            vodShort.vod_pic = this.baseProxy + Utils.base64Encode(this.siteUrl + "/" + Utils.getStrByRegex(/url\((.*?)\);/, $(vodElement).find("[class=\"cover\"]")[0].attribs.style))
            vodShort.vod_remarks = $($(vodElement).find("[class=\"public-list-prb hide ft2\"]")).html()
            vodShort.vod_name = $($(vodElement).find("[class=\"thumb-txt cor4 hide\"]")).html()
            vodShort.vod_id = Utils.getStrByRegex(/v\/(.*?).html/, $(vodElement).find("[class=\"button\"]")[0].attribs.href)
            vod_list.push(vodShort)
        }
        return vod_list
    }


    async parseVodShortListFromJson(obj) {
        let vod_list = []
        for (const vod_json of obj["list"]) {
            let vodShort = new VodShort();
            vodShort.vod_name = vod_json["vod_name"]
            vodShort.vod_id = vod_json["vod_id"]
            vodShort.vod_pic = this.baseProxy + Utils.base64Encode(this.siteUrl + "/" + vod_json["vod_pic"])
            vodShort.vod_remarks = vod_json["vod_remarks"]
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodDetailFromDoc($) {
        let vodDetail = new VodDetail();
        let detailElement = $("[class=\"vod-detail style-detail rel box cor1\"]")
        vodDetail.vod_name = $($(detailElement).find("[class=\"slide-info-title hide\"]")).text()
        vodDetail.vod_pic = this.siteUrl + $(detailElement).find("[class=\"detail-pic lazy mask-1\"]")[0].attribs["data-original"]
        vodDetail.vod_remarks = $($($(detailElement).find("[class=\"slide-info hide\"]")[0]).find("[class=\"slide-info-remarks\"]")[0]).text()
        vodDetail.vod_year = $($($(detailElement).find("[class=\"slide-info hide\"]")[0]).find("[class=\"slide-info-remarks\"]")[1]).text()
        vodDetail.vod_area = $($($(detailElement).find("[class=\"slide-info hide\"]")[0]).find("[class=\"slide-info-remarks\"]")[2]).text()

        vodDetail.vod_director = $($($(detailElement).find("[class=\"slide-info hide\"]")[1]).find("a")).text()
        vodDetail.vod_actor = $($($(detailElement).find("[class=\"slide-info hide\"]")[2]).find("a")).text()
        let type_list = []
        for (const typeEle of $($(detailElement).find("[class=\"slide-info hide\"]")[3]).find("a")) {
            type_list.push($(typeEle).text())
        }
        vodDetail.type_name = type_list.join("/")
        vodDetail.vod_content = $($("[class=\"check text selected cor3\"]")).text()
        let playElemet = $("[class=\"anthology wow fadeInUp animated\"]")
        let playFormatElemets = $(playElemet).find("[class=\"swiper-slide\"]")
        let playUrlElements = $(playElemet).find("[class=\"anthology-list-play size\"]")
        let vod_play_from_list = []
        let vod_play_list = []
        for (let i = 0; i < playFormatElemets.length; i++) {
            let playFormatElement = playFormatElemets[i]
            vod_play_from_list.push(playFormatElement.children[1].data)
            let vodItems = []
            for (const playUrlElement of $(playUrlElements[i]).find("a")) {
                let episodeName = $(playUrlElement).text()
                let episodeUrl = playUrlElement.attribs.href
                vodItems.push(episodeName + "$" + episodeUrl)
            }
            vod_play_list.push(vodItems.join("#"))
        }
        vodDetail.vod_play_from = vod_play_from_list.join("$$$")
        vodDetail.vod_play_url = vod_play_list.join("$$$")
        return vodDetail
    }


    async getHtml(url = this.siteUrl, headers = this.getHeader()) {
        try {
            let html = await this.fetch(url, null, headers)
            if (!_.isEmpty(html) && html.indexOf("江苏反诈公益宣传") === -1) {
                return load(html)
            } else {
                if (this.pipixiaReconnectTimes < this.maxReconnectTimes) {
                    Utils.sleep(2)
                    this.pipixiaReconnectTimes = this.pipixiaReconnectTimes + 1
                    return await this.getHtml(url, headers)
                } else {
                    await this.jadeLog.error(`html获取失败`, true)
                }
            }
        } catch (e) {
            await this.jadeLog.error(`获取html出错,出错原因为${e}`)
        }

    }


    async setClasses() {
        let $ = await this.getHtml()
        this.classes = [this.getTypeDic("首页", "最近更新")]
        let $2 = await this.getHtml(this.siteUrl + "/s/1.html")
        let classElemets = $2("[class=\"nav-swiper rel\"]")[0]
        for (const classElement of $(classElemets).find("a")) {
            let type_id = Utils.getStrByRegex(/\/s\/(.*?).html/, classElement.attribs.href)
            let type_name = $(classElement).text()
            this.classes.push(this.getTypeDic(type_name, type_id))
        }
    }

    async getFilter($) {
        let elements = $("[class=\"nav-swiper rel\"]")
        let extend_list = []
        for (let i = 0; i < elements.length; i++) {
            let element = elements[i]
            let name = $($($(element).find("[class=\"filter-text bj cor5\"]")).find("span")).html()
            if (name !== "频道") {
                let extend_dic = {"key": (i + 1).toString(), "name": name, "value": []}
                for (const ele of $(element).find("a")) {
                    extend_dic["value"].push({"n": $(ele).text(), "v": $(ele).text()})
                }
                extend_list.push(extend_dic)
            }
        }
        return extend_list
    }

    async setFilterObj() {
        for (const type_dic of this.classes) {
            let type_id = type_dic["type_id"]
            if (Utils.isNumeric(type_id)) {
                let url = this.siteUrl + `/s/${type_id}.html`
                let $ = await this.getHtml(url)
                this.filterObj[type_id] = await this.getFilter($)
            }
        }
    }

    async setHomeVod() {
        let $ = await this.getHtml(this.siteUrl + "/map.html")
        this.homeVodList = await this.parseVodShortListFromDoc($)
    }

    getExtend(extend, key) {
        if (extend[key] !== undefined && extend[key] !== "全部") {
            return extend[key]
        } else {
            return null
        }
    }

    getExtendDic(params, extend) {
        let class_value = this.getExtend(extend, "2")
        if (class_value !== null) {
            params["class"] = class_value
        }
        let area_value = this.getExtend(extend, "3")
        if (area_value !== null) {
            params["area"] = area_value
        }
        let year_value = this.getExtend(extend, "4")
        if (year_value !== null) {
            params["year"] = year_value
        }
        let lang_value = this.getExtend(extend, "5")
        if (lang_value !== null) {
            params["lang"] = lang_value
        }
        let letter_value = this.getExtend(extend, "6")
        if (letter_value !== null) {
            params["letter"] = letter_value
        }
        return params
    }

    async setCategory(tid, pg, filter, extend) {
        if (Utils.isNumeric(tid)) {
            let url = this.siteUrl + "/index.php/api/vod"
            let time_1 = Math.floor(new Date().getTime() / 1000)
            let key_1 = pipixiaMd5(time_1)
            let params = {
                "type": tid, "page": pg, "time": time_1.toString(), "key": key_1
            }
            params = this.getExtendDic(params, extend)
            let content = await this.post(url, params, this.getHeader())
            if (!_.isEmpty(content)) {
                let content_json = JSON.parse(content)
                if (content_json["code"] === 1) {
                    this.vodList = await this.parseVodShortListFromJson(content_json)
                }
            }

        }
    }

    async setDetail(id) {
        let $ = await this.getHtml(this.siteUrl + `/v/${id}.html`)
        this.vodDetail = await this.parseVodDetailFromDoc($)
    }

    async getPlayConfig(element) {
        // let playJSUrl = this.siteUrl + element.attribs.src
        // let jsContent = await this.fetch(playJSUrl,null,null)
        // let playListConfig = JSON.parse(Utils.getStrByRegex(/MacPlayerConfig.player_list=(.*?),MacPlayerConfig/,jsContent))
        //
        let playListConfig = {
            "qq": {
                "show": "QQ虾线",
                "des": "",
                "ps": "1",
                "parse": "http://play.shijie.chat/player/ec.php?code=qq&if=1&url="
            }, "qiyi": {
                "show": "QY虾线",
                "des": "",
                "ps": "1",
                "parse": "http://play.shijie.chat/player/ec.php?code=qiyi&if=1&url="
            }, "youku": {
                "show": "YK虾线",
                "des": "",
                "ps": "1",
                "parse": "http://play.shijie.chat/player/ec.php?code=youku&if=1&url="
            }, "mgtv": {
                "show": "MG虾线",
                "des": "",
                "ps": "1",
                "parse": "http://play.shijie.chat/player/ec.php?code=mgtv&if=1&url="
            }, "NBY": {
                "show": "极速线路",
                "des": "",
                "ps": "1",
                "parse": "http://play.shijie.chat/player/ec.php?code=qq&if=1&url="
            }, "SLNB": {
                "show": "三路极速",
                "des": "",
                "ps": "1",
                "parse": "http://play.shijie.chat/player/ec.php?code=qq&if=1&url="
            }, "FYNB": {
                "show": "APP专享线路",
                "des": "",
                "ps": "0",
                "parse": "http://play.shijie.chat/player/ec.php?code=qq&if=1&url="
            }, "SPA": {
                "show": "极速A",
                "des": "",
                "ps": "0",
                "parse": "http://play.shijie.chat/player/ec.php?code=qq&if=1&url="
            }, "SPB": {
                "show": "极速B",
                "des": "",
                "ps": "1",
                "parse": "http://play.shijie.chat/player/ec.php?code=qq&if=1&url="
            }, "kyB": {
                "show": "极速直连",
                "des": "",
                "ps": "1",
                "parse": "http://play.shijie.chat/player/ec.php?code=qq&if=1&url="
            }, "JMZN": {
                "show": "极速直连",
                "des": "",
                "ps": "1",
                "parse": "http://play.shijie.chat/player/ec.php?code=qq&if=1&url="
            }, "ZNJSON": {
                "show": "极速直连",
                "des": "",
                "ps": "1",
                "parse": "http://play.shijie.chat/player/ec.php?code=qq&if=1&url="
            }, "znkan": {
                "show": "极速直连",
                "des": "",
                "ps": "1",
                "parse": "http://play.shijie.chat/player/ec.php?code=qq&if=1&url="
            }, "bilibili": {
                "show": "BLBL虾线",
                "des": "",
                "ps": "1",
                "parse": "http://play.shijie.chat/player/ec.php?code=qq&if=1&url="
            }, "pptv": {
                "show": "PP虾线", "des": "", "ps": "1", "parse": "http://play.shijie.chat/player/?url="
            }, "letv": {
                "show": "LE虾线", "des": "", "ps": "1", "parse": "http://play.shijie.chat/player/?url="
            }, "sohu": {
                "show": "SH虾线", "des": "", "ps": "1", "parse": "http://play.shijie.chat/player/?url="
            }, "DJMP4": {
                "show": "短剧专用",
                "des": "",
                "ps": "1",
                "parse": "http://play.shijie.chat/player/ec.php?code=qq&if=1&url="
            }, "CLDJ": {
                "show": "短剧①",
                "des": "",
                "ps": "1",
                "parse": "http://play.shijie.chat/player/ec.php?code=qq&if=1&url="
            }, "ChenXi": {
                "show": "短剧专用2",
                "des": "",
                "ps": "1",
                "parse": "http://play.shijie.chat/player/ec.php?code=qq&if=1&url="
            }, "HT-": {
                "show": "自营线",
                "des": "",
                "ps": "1",
                "parse": "http://play.shijie.chat/player/ec.php?code=qq&if=1&url="
            }, "htys": {
                "show": "解说线路", "des": "", "ps": "1", "parse": "http://play.shijie.chat/player/?url="
            }, "sgdj": {
                "show": "短剧③",
                "des": "",
                "ps": "1",
                "parse": "http://play.shijie.chat/player/ec.php?code=qq&if=1&url="
            }
        }
        return playListConfig
    }

    uic(url, uid) {
        let ut = Crypto.enc.Utf8.parse('2890' + uid + 'tB959C');
        let mm = Crypto.enc.Utf8.parse("2F131BE91247866E");
        let decrypted = Crypto.AES.decrypt(url, ut, {iv: mm, mode: Crypto.mode.CBC, padding: Crypto.pad.Pkcs7});
        return Crypto.enc.Utf8.stringify(decrypted);
    }

    async setVideoProxy(playUrl){
        let urls = []
        urls.push('proxy');
        urls.push(playUrl);
        const pUrls = urls
        for (let index = 1; index < pUrls.length; index += 2) {
            pUrls[index] = js2Proxy(false, this.siteType, this.siteKey, 'hls/' + encodeURIComponent(pUrls[index]), {});
        }
        pUrls.push('original');
        pUrls.push(playUrl);
        return pUrls
    }

    async setPlay(flag, id, flags) {
        let $ = await this.getHtml(this.siteUrl + id)
        let playElements = $("[class=\"player-left\"]")
        let scriptElements = $(playElements).find("script")
        await this.jadeLog.debug($(scriptElements[0]).html())
        let playConfig = JSON.parse($(scriptElements[0]).html().replaceAll("var player_aaaa=", ""))
        let playListConfig = await this.getPlayConfig(scriptElements[1])
        let jiexiUrl = playListConfig[playConfig["from"]]["parse"] + playConfig["url"]
        let jiexi$ = await this.getHtml(jiexiUrl, {"User-Agent": Utils.CHROME})
        let ConFig = JSON.parse(Utils.getStrByRegex(/let ConFig = (.*?),box = /, jiexi$.html()))
        let playUrl = this.uic(ConFig["url"], ConFig.config.uid)
        await this.jadeLog.debug(`播放链接为:${playUrl}`)
        if (flag.indexOf("极速") > -1) {
            this.playUrl = playUrl
        } else {
            if (this.catOpenStatus) {
                this.playUrl = await this.setVideoProxy(playUrl)
            } else {
                this.playUrl = playUrl
            }
        }
    }

    async setSearch(wd, quick) {
        let $ = await this.getHtml(this.siteUrl + `/vodsearch.html?wd=${decodeURI(wd)}`)
        this.vodList = await this.parseVodShortListFromDocBySearch($)
    }

}

let spider = new PiPiXiaSpider()

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
        proxy: proxy,
        search: search,
    };
}
export {spider}
