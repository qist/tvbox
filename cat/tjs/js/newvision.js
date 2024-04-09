/*
* @File     : newvision.js
* @Author   : jade
* @Date     : 2024/2/20 14:14
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 新视觉影院
*/
import {VodDetail, VodShort} from "../lib/vod.js"
import * as Utils from "../lib/utils.js";
import {Spider} from "./spider.js";
import {Crypto} from "../lib/cat.js";


class NewVisionSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://www.6080yy3.com"
    }

    getAppName() {
        return "新视觉影院"
    }

    getName() {
        return "🐼┃新视觉影院┃🐼"
    }
    getJSName() {
        return "newvision"
    }

    getType() {
        return 3
    }
    async setClasses() {
        let $ = await this.getHtml()
        let navElements = $($("[class=\"nav-menu-items\"]")[0]).find("a")
        for (const navElement of navElements) {
            let type_id = Utils.getStrByRegex(/\/vodtype\/(.*?).html/, navElement.attribs.href)
            let type_name = navElement.attribs.title
            if (Utils.isNumeric(type_id)) {
                this.classes.push(this.getTypeDic(type_name, type_id))
            }
        }
    }

    async getFilter($) {
        let elements = $("[class='scroll-content']").slice(1)
        let extend_list = []
        let type_key_list = [3, 1, 11, 2]
        for (let i = 0; i < elements.length; i++) {
            let name = $($(elements[i]).find("a")[0]).text()
            let extend_dic = {"key": name, "name": name, "value": []}
            extend_dic["name"] = name
            extend_dic["value"].push({"n": "全部", "v": "0"})
            for (const ele of $(elements[i]).find("a").slice(1)) {
                let type_id_list = Utils.getStrByRegex(/\/vodshow\/(.*?).html/, ele.attribs.href).split("-")
                extend_dic["value"].push({
                    "n": $(ele).text(), "v": decodeURIComponent(type_id_list[type_key_list[i]])
                })
            }
            extend_list.push(extend_dic)
        }
        return extend_list
    }

    async setFilterObj() {
        for (const type_dic of this.classes) {
            let type_id = type_dic["type_id"]
            if (type_id !== "最近更新") {
                let url = this.siteUrl + `/vodshow/${type_id}-----------.html`
                let $ = await this.getHtml(url)
                this.filterObj[type_id] = await this.getFilter($)
            }
        }
    }

    async parseVodShortListFromDoc($) {
        let items = $('.module-item');
        let vod_list = [];
        for (const item of items) {
            let vodShort = new VodShort()
            let oneA = $(item).find('.module-item-cover .module-item-pic a').first();
            vodShort.vod_id = oneA.attr('href');
            vodShort.vod_name = oneA.attr('title');
            vodShort.vod_pic = $(item).find('.module-item-cover .module-item-pic img').first().attr('data-src');
            if (vodShort.vod_pic.indexOf("img.php?url=") > 0) {
                vodShort.vod_pic = vodShort.vod_pic.split("img.php?url=")[1]
            }
            vodShort.vod_remarks = $(item).find('.module-item-text').first().text();
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodShortListFromJson(obj) {
        let vod_list = []
        for (const result of obj["Data"]["result"]){
            let vodShort = new VodShort()
            vodShort.vod_id = result["vod_url"].replaceAll(this.siteUrl,"")
            vodShort.vod_pic = result["vod_pic"]
            vodShort.vod_name = result["vod_name"]
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodDetailFromDoc($) {
        let html = $.html()
        let vodDetail = new VodDetail()
        let vodDetailElement = $("[class=\"box view-heading\"]")
        vodDetail.vod_name = $($(vodDetailElement).find("[class=\"page-title\"]")).text()
        let typeElements = $($(vodDetailElement).find("[class=\"tag-link\"]").find("a"))
        vodDetail.vod_area = $($(vodDetailElement).find("[class=\"tag-link\"]").slice(-1)[0]).text()
        let type_list = []
        for (const typeElement of typeElements) {
            type_list.push($(typeElement).text())
        }
        vodDetail.type_name = type_list.join("/")
        let itemElements = $(vodDetailElement).find("[class=\"video-info-items\"]")
        vodDetail.vod_director = $($(itemElements[0]).find("a")).text()
        let actor_list = []
        for (const actorElement of $(itemElements[1]).find("a")) {
            actor_list.push($(actorElement).text())
        }
        vodDetail.vod_pic = $($(vodDetailElement).find("[class=\"module-item-pic\"]")).find("img")[0].attribs["data-src"]
        vodDetail.vod_actor = actor_list.join("/")
        vodDetail.vod_year = $($(itemElements[2]).find("[class=\"video-info-item\"]")).text()
        vodDetail.vod_remarks = $($(itemElements[3]).find("[class=\"video-info-item\"]")).text()
        vodDetail.vod_content = $($(itemElements[5]).find("[class=\"video-info-item video-info-content vod_content\"]")).text().replaceAll("\n", "\t").replaceAll("\t收起", "")
        let playerformatElements = $("[class=\"module-tab-item tab-item\"]")
        let playUrlElements = $("[class=\"scroll-content\"]")
        let vod_play_from_list = []
        let vod_play_list = []
        for (let i = 0; i < playerformatElements.length; i++) {
            let playFormatElement = playerformatElements[i]
            let format_name = playFormatElement.attribs["data-dropdown-value"]
            if (format_name.indexOf("夸克") === -1) {
                vod_play_from_list.push(format_name)
                let vodItems = []
                for (const playUrlElement of $(playUrlElements[i]).find("a")) {
                    let episodeName = $(playUrlElement).text()
                    let episodeUrl = playUrlElement.attribs.href
                    vodItems.push(episodeName + "$" + episodeUrl)
                }
                vod_play_list.push(vodItems.join("#"))

            }
        }
        vodDetail.vod_play_from = vod_play_from_list.join("$$$")
        vodDetail.vod_play_url = vod_play_list.join("$$$")
        return vodDetail
    }

    async setHomeVod() {
        let $ = await this.getHtml()
        this.homeVodList = await this.parseVodShortListFromDoc($)
    }

    async setCategory(tid, pg, filter, extend) {
        let urlParams = [tid.toString(), "", "", "", "", "", "", "", pg.toString(), "", "", ""]
        let type_key_list = [3, 11, 1, 2]
        if (extend["全部剧情"] !== undefined && extend["全部剧情"] !== "0") {
            urlParams[type_key_list[0]] = extend["全部剧情"]
        }
        if (extend["全部时间"] !== undefined && extend["全部时间"] !== "0") {
            urlParams[type_key_list[1]] = extend["全部时间"]
        }
        if (extend["全部地区"] !== undefined && extend["全部地区"] !== "0") {
            urlParams[type_key_list[2]] = extend["全部地区"]
        }
        if (extend["时间排序"] !== undefined && extend["时间排序"] !== "0") {
            urlParams[type_key_list[3]] = extend["时间排序"]
        }
        let reqUrl = this.siteUrl + '/index.php/vodshow/' + urlParams.join("-") + '.html';
        let $ = await this.getHtml(reqUrl)
        this.vodList = await this.parseVodShortListFromDoc($)
    }

    async setDetail(id) {
        let $ = await this.getHtml(this.siteUrl + id)
        this.vodDetail = await this.parseVodDetailFromDoc($)
    }

     uic(url,uid){
        let ut = Crypto.enc.Utf8.parse('2890'+uid+'tB959C')
        let mm = Crypto.enc.Utf8.parse("2F131BE91247866E")
        let decrypted = Crypto.AES.decrypt(url, ut, {iv: mm, mode: Crypto.mode.CBC, padding: Crypto.pad.Pkcs7});
        return Crypto.enc.Utf8.stringify(decrypted);
}

    async setPlay(flag, id, flags) {
        let $ = await this.getHtml(this.siteUrl + id)
        let playUrl = $("[id=\"bfurl\"]")[0].attribs.href
        if (playUrl.indexOf("http") > -1){
            this.playUrl = playUrl
        }else{
            //需要解析URL,支持弹幕
            let newUrl = "https://jiexi.xn--1lq90i13mxk5bolhm8k.xn--fiqs8s/player/ec.php?code=ak&if=1&url=" + playUrl
            let play$ = await this.getHtml(newUrl)
            let playHtml = play$.html()
            let playConfig = JSON.parse(Utils.getStrByRegex(/let ConFig = (.*?),box = /,playHtml))
            this.playUrl = this.uic(playConfig["url"],playConfig["config"]["uid"])
        }
    }

    async setSearch(wd, quick) {
        let url = `http://123.207.150.253/zxapi/public/?service=App.F.Fetch&req_p=${wd}&type=6080`
        let content = await this.fetch(url,null,this.getHeader())
        this.vodList = await this.parseVodShortListFromJson(JSON.parse(content))
    }

}

let spider = new NewVisionSpider()

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