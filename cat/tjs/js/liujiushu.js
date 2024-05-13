/*
* @File     : liujiushu.js
* @Author   : jade
* @Date     : 2024/04/23 10:02
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/
import {_, load} from '../lib/cat.js';
import * as Utils from "../lib/utils.js";
import {Spider} from "./spider.js";
import {BookDetail, BookShort} from "../lib/book.js";
import {formatContent} from "../lib/utils.js";

class LiuJiuShuSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://www.diyi69.com"
    }

    getAppName() {
        return "六九书吧"
    }

    getJSName() {
        return "liujiushu"
    }

    getType() {
        return 10
    }

    getName() {
        return "📚︎┃六九书吧┃📚︎"
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
        bookShort.book_remarks = $(bookShortElements[2]).text()
        bookShort.book_name = $(bookShortElements[1]).text()
        bookShort.book_id = bookShortElements[0].attribs.href
        bookShort.book_pic = $(element).find("img")[0].attribs["src"]
        return bookShort
    }

    async parseVodShortListFromDoc($) {
        let books = []
        let bookElements = $($("[class=\"flex\"]")[0]).find("li")
        for (const bookElement of bookElements) {
            let bookShort = this.parseVodShortFromElement($, bookElement)
            books.push(bookShort)
        }
        return books
    }

    async parseVodShortListFromDocByCategory($) {
        let bookElements = $("ul.flex > li")
        let books = [];
        for (const item of bookElements) {
            let bookShort = new BookShort()
            bookShort.book_id = $(item).find('a:first')[0].attribs.href;
            const img = $(item).find('img:first')[0];
            bookShort.book_name = img.attribs.title
            bookShort.book_pic = img.attribs["data-original"]
            bookShort.book_remarks = $($(item).find('em:first')).text();
            books.push(bookShort)
        }
        return books
    }

    async parseVodShortListFromDocBySearch($) {
        let books = []
        let bookElements = $('li.searchresult')
        for (const bookElement of bookElements) {
            let bookShort = new BookShort()
            let bookShortElements = $(bookElement).find("a")
            bookShort.book_remarks = $(bookShortElements[2]).text()
            bookShort.book_name = $(bookShortElements[1]).text()
            bookShort.book_id = bookShortElements[0].attribs.href
            bookShort.book_pic = $(bookShortElements[0]).find("img")[0].attribs["data-original"]
            books.push(bookShort)
        }
        return books
    }

    async parseVodDetailFromDoc($, id) {
        let html = $.html()
        let bookDetail = new BookDetail()
        bookDetail.book_name = $('[property$=title]')[0].attribs.content
        bookDetail.book_year = $('[property$=update_time]')[0].attribs.content
        bookDetail.book_director = $('[property$=author]')[0].attribs.content
        bookDetail.book_content = $('[property$=description]')[0].attribs.content
        bookDetail.book_remarks = $('[property$=category]')[0].attribs.content
        bookDetail.book_pic = $('div.novel_info_main>img')[0].attribs.src
        bookDetail.book_id = id
        const playBook = {};
        const sectionsElements = $("[class=\"flex ulcard\"]").find("li")
        const urlElements = $("[class=\"section chapter_list\"]")
        for (let i = 0; i < sectionsElements.length; i++) {
            const sectionElement = sectionsElements[i]
            const urlElemnet = urlElements[i]
            let vodItems = []
            for (const urlEle of $(urlElemnet).find("a")) {
                const epName = $(urlEle).text();
                const playUrl = epName + "-" + urlEle.attribs.href;
                vodItems.push(epName + '$' + playUrl)
            }
            let name = $($(urlElemnet).find("[class=\"title jcc\"]")).text()
            if (_.isEmpty(name)) {
                let text = $(sectionElement).text().split("（")[0]
                playBook[text] = vodItems.join("#")
            } else {
                name = name.replaceAll("《","").replaceAll("》","").replaceAll(bookDetail.book_name,"")
                playBook[name] = vodItems.reverse().join("#")
            }
        }
        bookDetail.volumes = _.keys(playBook).join('$$$');
        bookDetail.urls = _.values(playBook).join('$$$');
        return bookDetail
    }

    async setClasses() {
        let $ = await this.getHtml()
        for (const a of $('div.navigation > nav > a[href!="/"]')) {
            let type_id_list = a.attribs.href.split("/").slice(0, 3)
            this.classes.push({
                type_id: type_id_list.join("/"), type_name: a.children[0].data.trim(), tline: 2,
            });
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

    async setCategory(tid, pg, filter, extend) {
        let $ = await this.getHtml(this.siteUrl + `${tid}/${pg}.html`);
        this.vodList = await this.parseVodShortListFromDocByCategory($)
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
        let params = {"searchkey": wd, "searchtype": "all", "Submit": ""}
        let content = await this.fetch(this.siteUrl + "/search/", params, this.getHeader())
        let $ = load(content)
        this.vodList = await this.parseVodShortListFromDocBySearch($)
    }

    async proxy(segments, headers) {
        await this.jadeLog.debug(`正在设置反向代理 segments = ${segments.join(",")},headers = ${JSON.stringify(headers)}`)
        let what = segments[0];
        let url = Utils.base64Decode(segments[1]);
        if (what === 'img') {
            await this.jadeLog.debug(`反向代理ID为:${url}`)
            let $ = await this.getHtml(this.siteUrl + url)
            let bookDetail = await this.parseVodDetailFromDoc($)
            let resp;
            if (!_.isEmpty(headers)) {
                resp = await req(bookDetail.book_pic, {
                    buffer: 2, headers: headers
                });
            } else {
                resp = await req(bookDetail.book_pic, {
                    buffer: 2, headers: {
                        Referer: url, 'User-Agent': Utils.CHROME,
                    },
                });
            }
            return JSON.stringify({
                code: resp.code, buffer: 2, content: resp.content, headers: resp.headers,
            });
        }
        return JSON.stringify({
            code: 500, content: '',
        });
    }

}

let spider = new LiuJiuShuSpider()

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