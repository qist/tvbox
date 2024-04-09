/*
* @File     : bqg_open.js.js
* @Author   : jade
* @Date     : 2024/1/30 15:38
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/
import {_} from '../lib/cat.js';
import * as Utils from "../lib/utils.js";
import {Spider} from "./spider.js";
import {BookDetail, BookShort} from "../lib/book.js";

class BQQSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://m.13bqg.com"
    }

    getAppName() {
        return "笔趣阁"
    }

    getJSName() {
        return "bqg_open"
    }

    getType() {
        return 10
    }

    getName() {
        return "📚︎┃笔趣阁┃📚︎"
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

    async parseVodShortListFromDoc($) {
        let books = []
        let bookElements = $("[class=\"block\"]")
        for (const bookElement of $(bookElements[0]).find("li")) {
            let bookShort = new BookShort()
            let bookShortElements = $(bookElement).find("span")
            bookShort.book_remarks = $(bookShortElements[0]).text()
            bookShort.book_name = $(bookShortElements[1]).text()
            bookShort.book_id = $(bookShortElements[1]).find("a")[0].attribs.href
            bookShort.book_pic = this.jsBase + Utils.base64Encode(bookShort.book_id)
            books.push(bookShort)
        }
        return books
    }

    async parseVodShortListFromDocByCategory($) {
        let books = [];
        for (const item of $('div.item')) {
            let bookShort = new BookShort()
            bookShort.book_id = $(item).find('a:first')[0].attribs.href;
            const img = $(item).find('img:first')[0];
            bookShort.book_name = img.attribs.alt
            bookShort.book_pic = img.attribs.src
            bookShort.book_remarks = $(item).find('span:first')[0].children[0].data.trim();
            books.push(bookShort)
        }
        return books
    }

    async parseVodDetailFromDoc($, id) {
        let bookDetail = new BookDetail()
        bookDetail.book_name = $('[property$=book_name]')[0].attribs.content
        bookDetail.book_year = $('[property$=update_time]')[0].attribs.content
        bookDetail.book_director = $('[property$=author]')[0].attribs.content
        bookDetail.book_content = $('[property$=description]')[0].attribs.content
        bookDetail.book_pic = $($("[class=\"cover\"]")).find("img")[0].attribs.src
        bookDetail.book_id = id
        if (id !== undefined) {
            $ = await this.getHtml(this.siteUrl + id + `list.html`);
            let urls = [];
            const links = $('dl>dd>a[href*="/html/"]');
            for (const l of links) {
                const name = $(l).text().trim();
                const link = l.attribs.href;
                urls.push(name + '$' + link);
            }
            bookDetail.volumes = '全卷';
            bookDetail.urls = urls.join('#');
        }
        return bookDetail

    }

    async setClasses() {
        let $ = await this.getHtml()
        for (const a of $('div.nav > ul > li > a[href!="/"]')) {
            this.classes.push({
                type_id: a.attribs.href.replace(/\//g, ''), type_name: a.children[0].data.trim(), tline: 2,
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
        let $ = await this.getHtml(this.siteUrl + `/${tid}/${pg}.html`);
        this.vodList = await this.parseVodShortListFromDocByCategory($)
    }

    async setPlay(flag, id, flags) {
        try {
            let content = '';
            while (true) {
                let $ = await this.getHtml(this.siteUrl + id)
                content += $('#chaptercontent')
                    .html()
                    .replace(/<br>|请收藏.*?<\/p>/g, '\n')
                    .trim();
                id = $('a.Readpage_down')[0].attribs.href;
                if (id.indexOf('_') < 0) break;
            }
            this.playUrl = {"content":content + '\n\n'}
        } catch (e) {
            this.playUrl = {"content":""}
        }
    }

    async search(wd, quick) {
        const cook = await req(`${this.siteUrl}/user/hm.html?q=${encodeURIComponent(wd)}`, {
            headers: {
                accept: 'application/json',
                'User-Agent': Utils.MOBILEUA,
                Referer: `${this.siteUrl}/s?q=${encodeURIComponent(wd)}`,
            },
        });
        const set_cookie = _.isArray(cook.headers['set-cookie']) ? cook.headers['set-cookie'].join(';;;') : cook.headers['set-cookie'];
        const cks = set_cookie.split(';;;');
        const cookie = {};
        for (const c of cks) {
            const tmp = c.trim();
            const idx = tmp.indexOf('=');
            const k = tmp.substr(0, idx);
            cookie[k] = tmp.substr(idx + 1, tmp.indexOf(';') - idx - 1);
        }
        const resp = await req(`${this.siteUrl}/user/search.html?q=${encodeURIComponent(wd)}&so=undefined`, {
            headers: {
                accept: 'application/json',
                'User-Agent': Utils.MOBILEUA,
                cookie: 'hm=' + cookie['hm'],
                Referer: `${this.siteUrl}/s?q=${encodeURIComponent(wd)}`,
            },
        });
        let data = JSON.parse(resp.content);
        let books = [];
        for (const book of data) {
            books.push({
                book_id: book["url_list"],
                book_name: book["articlename"],
                book_pic: book["url_img"],
                book_remarks: book["author"],
            });
        }
        return {
            tline: 2, list: books,
        };
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

let spider = new BQQSpider()

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