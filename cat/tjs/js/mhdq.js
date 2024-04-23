/*
* @File     : mhdq.js
* @Author   : jade
* @Date     : 2024/1/24 9:15
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 18+韩漫
*/
import {Spider} from "./spider.js";
import {BookDetail, BookShort} from "../lib/book.js";

class MHDQSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = 'https://www.18hanman.com';
    }

    getName() {
        return "🔞|韩漫18|🔞"
    }

    getAppName() {
        return "韩漫18"
    }

    getJSName() {
        return "mhdq"
    }

    getType() {
        return 20
    }

    async setClasses() {
        this.classes = []
        let $ = await this.getHtml(this.siteUrl + "/category/")
        for (const a of $('div.classopen ul.duzhe  a[href!="/"]')) {
            this.classes.push({
                type_id: a.attribs.href,
                type_name: a.children[0].data.trim()
            });
        }
    }

    async parseVodShortListFromDocByCategory($) {
        const list = eval($('div[class="row exemptComic-box"]')[0].attribs.list);
        let books = [];
        for (const book of list) {
            let bookShort = this.parseVodShortFromJson(book)
            books.push(bookShort)
        }
        return books
    }

    parseVodShortFromElement($, element) {
        let bookShort = new BookShort()
        const a = $(element).find('a:first')[0];
        const img = $(element).find('img:first-child')[0];
        bookShort.book_id = a.attribs.href
        bookShort.book_name = $($(element).find("a").slice(-1)[0]).html()
        bookShort.book_pic = img.attribs.src
        bookShort.book_remarks = $($(element).find("span")).text()
        return bookShort

    }

    async parseVodShortListFromDoc($) {
        let vodElements = $('ul.catagory-list li')
        let books = []
        for (const vodElement of vodElements) {
            let bookShort = await this.parseVodShortFromElement($, vodElement)
            books.push(bookShort)
        }
        return books
    }

    async parseVodShortListFromDocBySearch($) {
        let vodElements = $('ul.u_list')
        let books = []
        for (const vodElement of vodElements) {
            let bookShort = await this.parseVodShortFromElement($, vodElement)
            books.push(bookShort)
        }
        return books
    }

    async parseVodDetailFromDoc($, id) {
        let html = $.html()
        let bookDetail = new BookDetail()
        bookDetail.book_id = id
        bookDetail.book_name = $('div.title:first').text().trim()
        bookDetail.pic = $($('div.img:first-child')).find("img")[0].attribs.src
        let contentElements = $('div.info ').find("p")
        for (const contentElelent of contentElements) {
            if ($(contentElelent).text().indexOf("更新至")) {
                bookDetail.book_remarks = $(contentElelent).text().replaceAll("更新至：","")
            }
            if ($(contentElelent).text().indexOf("作者")) {
                bookDetail.book_director = $(contentElelent).text().replaceAll("作者：","")
            }
        }
        bookDetail.book_content = $("[class=\"text\"]").text()
        let urls = [];
        const links = $('ul.list a[href!="/"]');
        for (const l of links) {
            let name = l.children[0].data;
            let link = l.attribs.href;
            urls.push(name + '$' + link);
        }
        bookDetail.volumes = '全卷';
        bookDetail.urls = urls.join('#');
        return bookDetail
    }

    async setCategory(tid, pg, filter, extend) {
        const $ = await this.getHtml(this.siteUrl + `${tid}/page/${pg}`)
        this.vodList = await this.parseVodShortListFromDoc($)

    }

    async setDetail(id) {
        let $ = await this.getHtml(this.siteUrl + `${id}`)
        this.vodDetail = await this.parseVodDetailFromDoc($, id)
    }

    async setPlay(flag, id, flags) {
        const $ = await this.getHtml(this.siteUrl + id);
        let content = [];
        for (const l of $('div.chapterbox img')) {
            const img = $(l).attr('src');
            content.push(img);
        }
        this.playUrl = {
            "content": content,
        }
    }

    async setSearch(wd, quick) {
        const $ = await this.getHtml(this.siteUrl + `/index.php/search?key=${wd}`);
        this.vodList = await this.parseVodShortListFromDocBySearch($)

    }
}

let spider = new MHDQSpider()

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
