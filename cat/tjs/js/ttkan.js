/*
* @File     : ttkan.js
* @Author   : jade
* @Date     : 2024/5/10 9:59
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/
import {_, load} from '../lib/cat.js';
import * as Utils from "../lib/utils.js";
import {Spider} from "./spider.js";
import {BookDetail, BookShort} from "../lib/book.js";

class TTKanSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://cn.ttkan.co"
        this.apiUrl = "https://cn.ttkan.co/api"
    }

    getAppName() {
        return "天天看小说"
    }

    getJSName() {
        return "ttkan"
    }

    getType() {
        return 10
    }

    getName() {
        return "📚︎┃天天看小说┃📚︎"
    }

    async spiderInit(inReq = null) {
        if (inReq !== null) {
            this.jsBase = await js2Proxy(inReq, "img", this.getHeader());
        } else {
            this.jsBase = await js2Proxy(true, this.siteType, this.siteKey, 'img/', this.getHeader());
        }
    }

    async init(cfg) {
        await super.init(cfg);
        await this.spiderInit(null)
    }

    parseVodShortFromElement($, element) {
        let bookShort = new BookShort()
        let bookShortElements = $(element).find("a")
        bookShort.book_name = bookShortElements[0].attribs["aria-label"]
        bookShort.book_id = bookShortElements[0].attribs.href
        if ($(element).find("amp-img").length > 0) {
            bookShort.book_pic = $(element).find("amp-img")[0].attribs["src"].split("?")[0]
        }
        bookShort.book_remarks = $($(element).find("p")[0]).text()
        return bookShort
    }

    async parseVodShortListFromDoc($) {
        let books = []
        let bookElements = $("[class=\"frame_body\"]").find("[class=\"pure-g\"]").slice(-1)[0]
        for (const bookElement of bookElements.children) {
            let bookShort = this.parseVodShortFromElement($, $(bookElement).find("li")[0])
            books.push(bookShort)
        }
        return books
    }

    async parseVodShortListFromDocByCategory($) {
        let bookImgElements = $("[class=\"pure-u-xl-1-5 pure-u-lg-1-4 pure-u-md-1-3 pure-u-sm-1-3 pure-u-13-24\"]")
        let bookMsgElements = $("[class=\"pure-u-xl-4-5 pure-u-lg-3-4 pure-u-md-2-3 pure-u-sm-2-3 pure-u-11-24\"]")
        let books = [];
        for (let i = 0; i < bookImgElements.length; i++) {
            let bookShort = new BookShort()
            let imgElement = bookImgElements[i]
            let msgElement = bookMsgElements[i]
            let element = $(imgElement).find('a')[0]
            bookShort.book_id = element.attribs.href;
            const img = $(imgElement).find('amp-img')[0];
            bookShort.book_name = $(element).text()
            bookShort.book_pic = img.attribs["src"].split("?")[0]
            bookShort.book_name = img.attribs["alt"]
            bookShort.book_remarks = $($(msgElement).find('li').slice(-1)).text().replaceAll("状态：","");
            books.push(bookShort)
        }
        return books
    }

    async parseVodShortListFromJson(obj) {
        let books = [];
        for (const data of obj) {
            let bookShort = new BookShort()
            bookShort.book_id = "/novel/chapters/" + data["novel_id"]
            bookShort.book_name = data["name"]
            bookShort.book_remarks = "作者：" + data.author
            bookShort.book_pic = "https://static.ttkan.co/cover/" + data["topic_img"]
            books.push(bookShort)
        }
        return books
    }

    async parseVodShortListFromDocBySearch($) {
        let books = []
        let bookElements = $("[class=\"frame_body\"]").find("[class=\"pure-g\"]").slice(-1)[0]
        for (const bookElement of bookElements.children) {
            let bookShort = new BookShort()
            bookShort.book_id = $(bookElement).find("a")[0].attribs.href
            bookShort.book_name = $($(bookElement).find("li")[0]).text()
            bookShort.book_remarks = $($(bookElement).find("li")[1]).text()
            bookShort.book_pic = $(bookElement).find("amp-img")[0].attribs.src.split("?")[0]
            books.push(bookShort)
        }
        return books
    }

    async parseVodDetailFromDoc($, id) {
        let html = $.html()
        let bookDetail = new BookDetail()
        let infoElement = $("[class=\"pure-g novel_info\"]")
        bookDetail.book_pic = $(infoElement).find("amp-img")[0].attribs.src.split("?")[0]
        let elements  = $(infoElement).find("[class=\"pure-u-xl-5-6 pure-u-lg-5-6 pure-u-md-2-3 pure-u-1-2\"]").find("li")
        bookDetail.book_name = $(elements[0]).text()
        bookDetail.book_director = $(elements[1]).text().replaceAll("作者：","")
        bookDetail.book_remarks = $(elements[3]).text().replaceAll("状态：","")
        bookDetail.book_year= $("[class=\"near_chapter\"]").find("time")[0].attribs.datetime.replaceAll("T"," ").split(".")[0]
        bookDetail.book_content = $($('[class="description"]')).text().trim()
        bookDetail.book_id = id
        const playBook = {};
        
        const nearElement = $('[class="near_chapter"]').find("a")[0]
        
        let nearVodItems = []
        const epName = $(nearElement).text();
        const page = nearElement.attribs.href.split("&page=").slice(-1)[0]
        const playUrl = epName + "+" +  `${id.replaceAll("/novel/chapters/","")}_${page}.html` ;
        nearVodItems.push(epName + '$' + playUrl)
      

        const lastestElements = $('[class="chapters_frame"]').find("a")
        for (const lastestElement of lastestElements){
            const epName = $(lastestElement).text();
            const page = lastestElement.attribs.href.split("&page=").slice(-1)[0]
            const playUrl = epName + "+" +  `${id.replaceAll("/novel/chapters/","")}_${page}.html` ;
            nearVodItems.push(epName + '$' + playUrl)
        }
        playBook["最近章节"] = nearVodItems.reverse().join("#")
        let params = {"language":"cn","novel_id":id.replaceAll("/novel/chapters/",""),"__amp_source_origin":encodeURIComponent(this.siteUrl)}
        let resJSon = JSON.parse(await this.fetch(this.apiUrl + "/nq/amp_novel_chapters" ,params,this.getHeader()))
        let allVodItems = []
        for (const data of resJSon["items"]){
            const epName = data.chapter_name;
            const playUrl = epName + "+" + `${id.replaceAll("/novel/chapters/","")}_${data.chapter_id}.html` ;
            allVodItems.push(epName + '$' + playUrl)
        }
        playBook["目录"] = allVodItems.join("#")
        bookDetail.volumes = _.keys(playBook).join('$$$');
        bookDetail.urls = _.values(playBook).join('$$$');
        return bookDetail
    }

    async setClasses() {
        let $ = await this.getHtml()
        let navElements = $('div.novel_class_nav  > a')
        for (const element of navElements) {
            let type_id = element.attribs.href
            let type_name = $(element).text()
            this.classes.push(this.getTypeDic(type_name, type_id));
        }
    }

    async getFilter($) {
        let extend_list = []
        let extend_dic = {"name": "排序", "key": "sort", "value": []}
        let elements = $('div.rank_nav > a')
        let sortList = []
        let isNewSort = false
        if (elements.length === 0) {
            elements = $('div.nav_filter_inner > a')
            isNewSort = true
        }
        for (const element of elements) {
            let type_name = $(element).text()
            let type_id = element.attribs.href
            sortList.push(this.getFliterDic(type_name, type_id))
        }
        if (isNewSort) {
            const lastItem = sortList.splice(-1, 1);
            sortList = lastItem.concat(sortList);
        }
        extend_dic["value"] = sortList
        extend_list.push(extend_dic)
        return extend_list
    }

    async setFilterObj() {
        for (const type_dic of this.classes) {
            let type_id = type_dic["type_id"]
            if (type_id !== "最近更新") {
                let $ = await this.getHtml(this.siteUrl + type_id)
                this.filterObj[type_id] = await this.getFilter($)
            }
        }
    }


    async setHomeVod() {
        let $ = await this.getHtml()
        this.homeVodList = await this.parseVodShortListFromDoc($)
    }


    async setDetail(id) {
        let $ = await this.getHtml(this.siteUrl + id)
        this.vodDetail = await this.parseVodDetailFromDoc($, id)
    }

    getExtend(extend) {
        if (extend["sort"] === undefined) {
            return "*"
        }
        if (extend["sort"] === "全部") {
            return "*"
        } else {
            let value = extend["sort"].replaceAll("/novel/", "").replaceAll("class/", "")
            if (value.indexOf("_") > -1){
                return value.split("_").slice(-1)[0]
            }else{
                return value
            }
        }
    }

    async setCategory(tid, pg, filter, extend) {
        if (tid === "/novel/rank") {
            tid = extend["sort"] ?? tid
            let $ = await this.getHtml(this.siteUrl + tid)
            this.vodList = await this.parseVodShortListFromDocByCategory($)
            let x = 0
        } else {
            let extendFilter = this.getExtend(extend)
            let limit = 18
            let params = {
                "language": "cn",
                "limit": limit,
                "type": tid.replaceAll("/novel/", "").replaceAll("class/", ""),
                "filter": extendFilter,
                "page": parseInt(pg),
                "__amp_source_origin": encodeURIComponent(this.siteUrl)
            }
            let resJson = JSON.parse(await this.fetch(this.apiUrl + "/nq/amp_novel_list", params, this.getHeader()))
            this.vodList = await this.parseVodShortListFromJson(resJson["items"])
        }

    }

    async setPlay(flag, id, flags) {
        let id_list = id.split("-")
        id = id_list[1]
        let content = id_list[0] + "\n\n"
        while (true) {
            let $ = await this.getHtml(this.siteUrl + id)
            content += Utils.formatContent($("[class=\"content\"]").html().trim().replaceAll("<p>", "    ").replaceAll("</p>", "\n"));
            id = $("[id=\"next_url\"]")[0].attribs.href;
            if (id.indexOf('_') < 0) break;
        }
        this.playUrl = {"content": content}
    }

    async setSearch(wd, quick) {
        let params = {"q":encodeURIComponent(wd)}
        let content = await this.fetch(this.siteUrl + "/novel/search", params, this.getHeader())
        let $ = load(content)
        this.vodList = await this.parseVodShortListFromDocBySearch($)
        let x = 0
    }
    async setPlay(flag, id, flags) {
        let id_list = id.split("+")
        id = id_list[1]
        let content = id_list[0] + "\n\n"
        let $ = await this.getHtml(this.siteUrl + "/novel/pagea/" + id)
        let bookContentList = $('[class="content"]').text().trim().replaceAll("章节报错 分享给朋友：","").replaceAll("              ","").split("\n")
        let newBookContentList = []
        for (const bookContent of bookContentList){
            if (!_.isEmpty(bookContent.replaceAll(" ",""))){
                newBookContentList.push(bookContent.replaceAll("            ","     "))
            }
        }
        content = content + "     " + newBookContentList.join("\n\n")
        this.playUrl = {"content": content}
    }
}

let spider = new TTKanSpider()

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