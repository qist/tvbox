/*
 * @Author: samples jadehh@live.com
 * @Date: 2023-12-14 11:03:04
 * @LastEditors: samples jadehh@live.com
 * @LastEditTime: 2023-12-14 11:03:04
 * @FilePath: js/aiyingshi.js
 * @Description: 爱影视爬虫类
 */
import {_, load} from '../lib/cat.js';
import {VodDetail, VodShort} from "../lib/vod.js"
import * as Utils from "../lib/utils.js";
import {Spider} from "./spider.js";


class AiYingShiSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = 'https://aiyingshis.com';
    }

    getName() {
        return "🚀‍┃爱影视┃🚀"
    }

    getAppName() {
        return "爱影视"
    }
    getJSName() {
        return "aiyingshi"
    }

    getType() {
        return 3
    }

    async parseVodShortListFromDoc($) {
        let items = $('.module-item');
        let vod_list = [];
        for (const item of items) {
            let vodShort = new VodShort()
            let oneA = $(item).find('.module-item-cover .module-item-pic a').first();
            vodShort.vod_id = oneA.attr('href');
            vodShort.vod_name = oneA.attr('title');
            let pic = $(item).find('.module-item-cover .module-item-pic img').first().attr('data-src')
            if (pic.indexOf("img.php?url=") > 0) {
                pic = pic.split("img.php?url=")[1]
            }else if (pic.indexOf("https:") === -1 && pic.indexOf("http:") === -1){
                pic = "https:" + pic
            }
            vodShort.vod_pic = pic
            vodShort.vod_remarks = $(item).find('.module-item-text').first().text();
            if (vodShort.vod_name !== undefined){
                 vod_list.push(vodShort)
            }

        }
        return vod_list
    }

    async parseVodDetailFromDoc($) {
        let vodDetail = new VodDetail()
        vodDetail.vod_name = $('.page-title')[0].children[0].data
        vodDetail.vod_pic =  $($("[class=\"video-cover\"]")).find(".lazyload")[0].attribs["data-src"]
        let video_info_list = $($(".video-info-aux")).text().replaceAll("\t","").split("\n")
        let type_list = []
        for (const video_info of video_info_list){
            if (!_.isEmpty(video_info.replaceAll(" ","").replaceAll("/",""))){
                type_list.push(video_info.replaceAll(" ","").replaceAll("/",""))
            }
        }
        vodDetail.type_name = type_list.slice(0,2).join("*")
        let video_items = $("[class=\"video-info-items\"]")
        vodDetail.vod_director = $(video_items[0]).find("a")[0].children[0].data
        let vidoe_info_actor_list = $(video_items[1]).find("a")
        let actor_list = []
        for (const vidoe_info_actor of vidoe_info_actor_list) {
            actor_list.push(vidoe_info_actor.children[0].data)
        }
        vodDetail.vod_actor = actor_list.join(" * ")
        vodDetail.vod_year = type_list[2]
        vodDetail.vod_remarks = $($(video_items[3]).find(".video-info-item")).text()
        vodDetail.vod_content = $($(video_items[5]).find(".video-info-item")).text()
        vodDetail.vod_area = type_list[3]
        vodDetail.vod_content = vodDetail.vod_content.replace("[收起部分]", "").replace("[展开全部]", "").replaceAll("\t","").replaceAll("\n","")

        let playElements = $($("[class=\"module-tab-content\"]")[0]).find("span")
        let urlElements = $("[class=\"module-list module-player-list tab-list sort-list \"]")
        let form_list = []
        for (const playerElement of playElements){
            form_list.push($(playerElement).text())
        }
        let play_url_list = []
        for (const urlElement of urlElements){
            let playUrlElements = $($(urlElement).find("[class=\"sort-item\"]")).find("a")
            let vodItems = []
            for (const playUrlElement of playUrlElements){
                let name = $(playUrlElement).text()
                let url = playUrlElement.attribs["href"]
                let play_url = name + "$" + url
                vodItems.push(play_url)
            }
            play_url_list.push(vodItems.join("#"))
        }
        vodDetail.vod_play_from = form_list.join('$$$');
        vodDetail.vod_play_url = _.values(play_url_list).join('$$$');
        return vodDetail
    }

    async parseVodShortListFromDocBySearch($) {
        let items = $('.module-search-item');
        let vod_list = [];
        for (const item of items) {
            let vodShort = new VodShort()
            vodShort.vod_id = $(item).find(".video-serial")[0].attribs.href;
            vodShort.vod_name = $(item).find(".video-serial")[0].attribs.title;
            vodShort.vod_pic = $(item).find(".module-item-pic > img")[0].attribs['data-src']
            vodShort.vod_remarks = '';
            vod_list.push(vodShort);
        }
        return vod_list
    }

    async setClasses() {
        let con = await this.fetch(this.siteUrl, null, this.getHeader());
        if (!_.isEmpty(con)) {
            const $ = load(con);
            let elements = $($("[class=\"nav-menu-items\"]")[0]).find("li")
            for (const element of elements.slice(0,6)) {
                let type_name = $($(element).find("span")).text()
                if (type_name !== "首页"){
                    let type_id =  $(element).find("a")[0].attribs["href"].split("/").slice(-1)[0].split(".")[0]
                    let type_dic = {"type_id": type_id, "type_name": type_name}
                    this.classes.push(type_dic)
                }
            }
        }
    }

    async getFilter($) {
        let elements = $("[class=\"scroll-content\"]").slice(1)
        let extend_list = []
        for (let i = 0; i < elements.length; i++) {
            let extend_dic = {"key": (i + 1).toString(), "name": "", "value": []}
            if (i < elements.length - 1) {
                extend_dic["name"] = $($(elements[i]).find("a")[0]).text()
                extend_dic["value"].push({"n": "全部", "v": "0"})
                for (const ele of $(elements[i]).find("a").slice(1)) {
                    if ($($(elements[i]).find("a")[0]).text() === "全部类型"){
                        extend_dic["value"].push({"n": $(ele).text(), "v":ele.attribs["href"].split("/").slice(-1)[0].split(".")[0]})
                    }else{
                        extend_dic["value"].push({"n": $(ele).text(), "v":$(ele).text()})

                    }
                }
                extend_list.push(extend_dic)
            } else {
                extend_dic["name"] = $($(elements[i]).find("a")[0]).text()
                extend_dic["value"] = [{"n": "全部", "v": "0"}, {
                    "n": $($(elements[i]).find("a")[1]).text(),
                    "v": "hits"
                }, {"n": $($(elements[i]).find("a")[2]).text(), "v": "score"}]

                extend_list.push(extend_dic)
            }

        }
        return extend_list
    }

    async setFilterObj() {
        for (const type_dic of this.classes) {
            let type_id = type_dic["type_id"]
            if (type_id !== "/" && type_id !== "最近更新") {
                let url = this.siteUrl + `/vodshow/id/${type_id}.html`
                let html = await this.fetch(url, null, this.getHeader())
                if (html != null) {
                    let $ = load(html)
                    this.filterObj[type_id] = await this.getFilter($)
                }
            }
        }
    }
    async setHomeVod() {
        let con = await this.fetch(this.siteUrl, null, this.getHeader());
        if (!_.isEmpty(con)) {
            const $ = load(con);
            this.homeVodList = await this.parseVodShortListFromDoc($)
        }
    }

    getExtend(value,defaultvalue,key = ""){
        if (value !== undefined && value !== "0"){
            return key + value
        }else{
            return defaultvalue
        }

    }

    async getCateUrl(tid,pg,extend){
        tid = this.getExtend(extend["1"],tid)
        let area = this.getExtend(extend["2"],"","/area/")
        let lanuage = this.getExtend(extend["3"],"","/lang/")
        let year = this.getExtend(extend["4"],"","/year/")
        let letter = this.getExtend(extend["5"],"","/letter/")
        let time = this.getExtend(extend['6'],"","/by/")
        return this.siteUrl + `/vodshow${time}${area}/id/${tid}${lanuage}${letter}${year}/page/${pg}.html`
    }

    async setCategory(tid, pg, filter, extend) {
        let reqUrl = await this.getCateUrl(tid,pg,extend)
        let html = await this.fetch(reqUrl, null, this.getHeader())
        if (!_.isEmpty(html)) {
            let $ = load(html)
            this.vodList = await this.parseVodShortListFromDoc($)
            let total = Utils.getStrByRegex(/\$\("\.mac_total"\)\.text\('(\d+)'\)/, html)
            this.limit = 72;
            if (total.length > 0) {
                this.total = parseInt(total)
            }
            if (this.total <= this.limit) {
                this.count = 1
            } else {
                this.count = Math.ceil(this.total / this.limit)
            }
        }
    }

    async setDetail(id) {
        let detailUrl = this.siteUrl + id;
        let html = await this.fetch(detailUrl, null, this.getHeader());
        if (!_.isEmpty(html)) {
            let $ = load(html)
            this.vodDetail = await this.parseVodDetailFromDoc($)
        }
    }


    async setPlay(flag, id, flags) {
        let html = await this.fetch(this.siteUrl + id,null,this.getHeader())
        if (!_.isEmpty(html)){
            let player_str = Utils.getStrByRegex(/<script type="text\/javascript">var player_aaaa=(.*?)<\/script>/,html)
            let play_dic = JSON.parse(player_str)
            this.playUrl = play_dic["url"]
        }

    }

    async setSearch(wd, quick) {
        let searchUrl = this.siteUrl + `/vodsearch/wd/${wd}.html`
        let html = await this.fetch(searchUrl, null, this.getHeader())
        if (!_.isEmpty(html)) {
            let $ = load(html)
            this.vodList = await this.parseVodShortListFromDocBySearch($)
        }
    }

}

let spider = new AiYingShiSpider()


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
        init: init, home: home, homeVod: homeVod, category: category, detail: detail, play: play, search: search,proxy:proxy
    };
}
export {spider}