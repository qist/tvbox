/*
* @File     : lovemovie.js
* @Author   : jade
* @Date     : 2024/4/29 09:36
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 爱情电影网
*/
import {Spider} from "./spider.js";
import {_, Crypto, load} from "../lib/cat.js";
import {VodDetail, VodShort} from "../lib/vod.js";
import * as Utils from "../lib/utils.js";
import {gbk_us} from "../lib/gbk_us.js";

class LoveMovieSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://b.aqdyje.com"
        this.removeKey = "骑兵营"
    }

    getName() {
        return "💕┃爱情电影网┃💕"
    }

    getAppName() {
        return "爱情电影网"
    }

    getJSName() {
        return "lovemovie"
    }

    getType() {
        return 3
    }

    async init(cfg) {
        await super.init(cfg);
    }

    async getHtml(url = this.siteUrl, proxy = false, headers = this.getHeader()) {
        let buffer = await this.fetch(url, null, headers, false, false, 1, proxy)

        let html = Utils.decode(buffer, "gb2312")
        await this.jadeLog.debug(`html content:${html}`)
        if (!_.isEmpty(html)) {
            return load(html)
        } else {
            return load(gbkDecode(buffer))
        }
    }

    async getFilter($, navElements) {
        let extend_list = []
        let extend_dic = {"key": "class", "name": "类型", "value": [this.getFliterDic("全部", "全部")]}
        for (const navElement of $(navElements).find("li")) {
            let element = $(navElement).find("a")[0]
            let type_name = $(element).text()
            let type_id = element.attribs.href
            extend_dic["value"].push(this.getFliterDic(type_name, type_id))
        }
        if (extend_dic["value"].length > 1) {
            extend_list.push(extend_dic)
        }
        return extend_list
    }

    async setClasses() {
        let $ = await this.getHtml()
        let navElements = $("[class=\"nav-item drop-down \"]")
        for (const navElement of navElements) {
            let elemenet = $(navElement).find("a")[0]
            let type_name = $(elemenet).text()
            let type_id = elemenet.attribs.href
            if (type_name !== this.removeKey) {
                this.classes.push(this.getTypeDic(type_name, type_id))
                this.filterObj[type_id] = await this.getFilter($, navElement)
            }
        }
    }

    async parseVodShortListFromDoc($) {
        let vod_list = []
        let vodElements = $("[class=\"play-img\"]")
        if (vodElements.length === 0) {
            vodElements = $("[class=\"show-list list-mode fn-clear\"]").find("li")
        }
        for (const vodElement of vodElements) {
            let vodShort = new VodShort()
            vodShort.vod_id = vodElement.attribs.href
            if (_.isEmpty(vodShort.vod_id)) {
                vodShort.vod_id = $(vodElement).find("a")[0].attribs.href
            }
            let imgElement = $(vodElement).find("img")[0]
            vodShort.vod_pic = imgElement.attribs.src
            vodShort.vod_name = imgElement.attribs.alt
            for (const element of $(vodElement).find("label")) {
                let text = $(element).text().trim()
                if (!_.isEmpty(text)) {
                    vodShort.vod_remarks = text
                    break
                }
            }
            if (_.isEmpty(vodShort.vod_remarks)) {
                vodShort.vod_remarks = $($(vodElement).find("p")[0]).text().replace("\n")
            }
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodShortListFromDocBySearch($) {
        let vodElements = $("[class=\"show-list\"]").find("li")
        let vod_list = []
        for (const vodElement of vodElements) {
            let vodShort = new VodShort()
            vodShort.vod_id = $(vodElement).find("a")[0].attribs.href
            let imgElement = $(vodElement).find("img")[0]
            vodShort.vod_pic = imgElement.attribs.src
            vodShort.vod_name = imgElement.attribs.alt
            vodShort.vod_remarks = $($(vodElement).find("[class=\"type fn-left\"]")).text().replace("类型：", "")
            if (vodShort.vod_remarks !== "社处片" && vodShort.vod_remarks !== "社保片" && vodShort.vod_remarks !== "撸丝片" && vodShort.vod_remarks !== "撸丝动漫") {
                vod_list.push(vodShort)
            }
        }
        return vod_list
    }

    async parseVodDetailFromDoc($) {
        let vodDetail = new VodDetail()
        let imgElement = $("[class=\"detail-pic fn-left\"]").find("img")[0]
        vodDetail.vod_pic = imgElement.attribs.src
        vodDetail.vod_name = imgElement.attribs.alt
        let vodInfoElement = $("[class=\"info fn-clear\"]")
        for (const vodDlElement of $(vodInfoElement).find("dl")) {
            let text = $(vodDlElement).text()
            if (text.indexOf("主演") > -1) {
                vodDetail.vod_actor = text.replaceAll("主演：", "").replaceAll("\n", "")
            }
            if (text.indexOf("状态") > -1) {
                vodDetail.vod_remarks = text.replaceAll("状态：", "").replaceAll("\n", "")
            }
            if (text.indexOf("类型") > -1) {
                vodDetail.type_name = text.replaceAll("类型：", "").replaceAll("\n", "")
            }
            if (text.indexOf("地区") > -1) {
                vodDetail.vod_area = text.replaceAll("地区：", "").replaceAll("\n", "")
            }
            if (text.indexOf("导演") > -1) {
                vodDetail.vod_director = text.replaceAll("导演：", "").replaceAll("\n", "")
            }
            if (text.indexOf("年份") > -1) {
                vodDetail.vod_year = text.replaceAll("年份：", "").replaceAll("\n", "")
            }
            if (text.indexOf("剧情") > -1) {
                vodDetail.vod_content = text.replaceAll("剧情：", "").replaceAll("\n", "")
            }
        }
        let playList = {}
        let html = $.html()
        let playListElements = $("[class=\"play-list\"]")
        let index = 1
        for (const playListElement of playListElements) {
            let playName = `播放连接-${index}`
            let vodItems = []
            for (const playUrlElement of $(playListElement).find("a")) {
                let playUrlName = playUrlElement.attribs.title
                let playUrl = playUrlElement.attribs.href
                vodItems.push(playUrlName + "$" + playUrl)
            }
            playList[playName] = vodItems.join("#")
            index = index + 1
        }
        index = 1
        let ciliListElements = $("[class=\"con4\"]")
        for (const ciliListElement of ciliListElements) {
            let playName = `磁力链接-${index}`
            let vodItems = []
            let playUrlName = playName
            let playUrl = $($(ciliListElement).find("div")).find("a")[0].attribs.href
            if (playUrl !== "javascript:void(0);") {
                vodItems.push(playUrlName + "$" + playUrl)
                playList[playName] = vodItems.join("#")
                index = index + 1
            }
        }
        vodDetail.vod_play_url = _.values(playList).join('$$$');
        vodDetail.vod_play_from = _.keys(playList).join('$$$');
        return vodDetail
    }


    async setHomeVod() {
        let $ = await this.getHtml()
        this.homeVodList = await this.parseVodShortListFromDoc($)
    }

    async setDetail(id) {
        let $ = await this.getHtml(this.siteUrl + id)
        this.vodDetail = await this.parseVodDetailFromDoc($)
    }

    getExtend(extend) {
        if (extend["class"] !== undefined) {
            if (extend["class"] !== "全部") {
                return extend["class"]
            }
        }
        return undefined
    }

    async setCategory(tid, pg, filter, extend) {
        let classes = this.getExtend(extend) ?? tid
        let url
        if (classes === tid) {
            url = this.siteUrl + classes
        } else {
            if (parseInt(pg) === 1) {
                url = this.siteUrl + classes
            } else {
                url = this.siteUrl + classes + `index${pg}.html`
            }
        }
        let $ = await this.getHtml(url)
        this.vodList = await this.parseVodShortListFromDoc($)
    }

    async setPlay(flag, id, flags) {
        if (flag.indexOf("磁力") > -1) {
            this.playUrl = id
        } else {
            let idSplitList = id.split("-")
            let flag_id = parseInt(idSplitList[1])
            let episode = parseInt(idSplitList[2].split(".")[0])
            let $ = await this.getHtml(this.siteUrl + id)
            let playJsUrl = Utils.getStrByRegex(/<script type="text\/javascript" src="(.*?)">/, $.html())
            let playJsContent = await this.fetch(this.siteUrl + playJsUrl, null, this.getHeader())
            let playUrlListStr = Utils.getStrByRegex(/var VideoListJson=(.*?),urlinfo=/, playJsContent)
            let playDic = eval(playUrlListStr)
            this.playUrl = playDic[flag_id][1][episode].split("$")[1]
            if (this.playUrl.indexOf("m3u8") === -1) {
                let html = await this.fetch(this.playUrl, null, this.getHeader())
                this.playUrl = Utils.getStrByRegex(/url: '(.*?)'/, html)
            }
        }
    }

    GBKEncode(str) {
        var arr_index = 0x8140; //33088;
        str += '';
        var gbk = [];
        var wh = '?'.charCodeAt(0); //gbk中没有的字符的替换符
        for (var i = 0; i < str.length; i++) {
            var charcode = str.charCodeAt(i);
            if (charcode < 0x80) gbk.push(charcode);
            else {
                var gcode = gbk_us.indexOf(charcode);
                if (~gcode) {
                    gcode += arr_index;
                    gbk.push(0xFF & (gcode >> 8), 0xFF & gcode);
                } else {
                    gbk.push(wh);
                }
            }
        }
        return gbk;
    }


    encode(str) {
        let encodeStr = ""
        for (const ch of str) {
            let bitArr = this.GBKEncode(ch);
            for (let i = 0; i < bitArr.length; i++) {
                bitArr[i] = '%' + ('0' + bitArr[i].toString(16)).substr(-2).toUpperCase();
            }
            encodeStr = encodeStr + bitArr.join('');
        }
        return encodeStr
    }

    async setSearch(wd, quick) {
        let params = {"searchword": this.encode(wd)}
        let buffer = await this.post(this.siteUrl + "/search.asp", params, this.getHeader(), "form", 1)
        let $ = load(Utils.decode(buffer, "gb2312"))
        this.vodList = await this.parseVodShortListFromDocBySearch($)
    }

}

let spider = new LoveMovieSpider()

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

export {spider, LoveMovieSpider}