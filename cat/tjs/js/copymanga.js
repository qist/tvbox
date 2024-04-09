import {Spider} from "./spider.js";
import {BookDetail, BookShort} from "../lib/book.js";
import {Crypto} from "../lib/cat.js";

class CopyManhuaSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = 'https://www.copymanga.tv';
    }

    getName() {
        return "🧑‍🎨|拷贝漫画|🧑‍🎨"
    }

    getAppName() {
        return "拷贝漫画"
    }

    getJSName() {
        return "copymanga"
    }

    getType() {
        return 20
    }


    async setClasses() {
        this.classes.push(this.getTypeDic("全部", "c1"))
    }

    async getFilter($) {
        let region = {
            key: 'region', name: '地區', init: '',
        };
        let regionValues = [];
        regionValues.push({n: '全部', v: ''});
        regionValues.push({n: '日漫', v: '0'});
        regionValues.push({n: '韓漫', v: '1'});
        regionValues.push({n: '美漫', v: '2'});
        region['value'] = regionValues;
        let ordering = {
            key: 'ordering', name: '排序', init: '-datetime_updated',
        };
        let orderingValues = [];
        orderingValues.push({n: '更新時間↓', v: '-datetime_updated'});
        orderingValues.push({n: '更新時間↑', v: 'datetime_updated'});
        orderingValues.push({n: '熱門↓', v: '-popular'});
        orderingValues.push({n: '熱門↑', v: 'popular'});
        ordering['value'] = orderingValues;
        let status = {
            key: 'sort', name: '狀態', init: '',
        };
        let statusValues = [];
        statusValues.push({n: '全部', v: ''});
        statusValues.push({n: '連載中', v: '0'});
        statusValues.push({n: '已完結', v: '1'});
        statusValues.push({n: '短篇', v: '2'});
        status['value'] = statusValues;
        let extend_list = []
        let themeValues = [{n: '全部', v: ''}];
        for (const a of $('div.classify-right>a[href*="theme="]')) {
            themeValues.push({
                n: $(a).text().trim(), v: a.attribs.href.match(/.*?theme=(.*)&/)[1],
            });
        }
        extend_list.push({
            key: 'theme', name: '', init: '', wrap: 1, value: themeValues,
        });
        extend_list.push(region);
        extend_list.push(status);
        extend_list.push(ordering);
        return extend_list
    }

    async setFilterObj() {
        let $ = await this.getHtml(this.siteUrl + '/comics');
        this.filterObj['c1'] = await this.getFilter($);
    }

    parseVodShortFromJson(obj) {
        let bookShort = new BookShort()
        bookShort.book_id = obj["path_word"]
        bookShort.book_name = obj["name"]
        bookShort.book_pic = obj["cover"]
        bookShort.book_remarks = obj.author ? obj.author[0].name : '';
        return bookShort
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

    async parseVodShortListFromDoc($) {
        let vodElements = $("[class=\"container edit\"]").find("[class=\"col-auto\"]")
        let books = []
        for (const vodElement of vodElements) {
            let bookShort = new BookShort()
            bookShort.book_id = $(vodElement).find("a")[0].attribs.href.split("/comic/")[1]
            bookShort.book_pic = $(vodElement).find("img")[0].attribs["data-src"]
            bookShort.book_name = $($(vodElement).find("p")).text()
            books.push(bookShort)
        }
        return books
    }


    async parseVodDetailFromDoc($, id) {
        let bookDetail = new BookDetail()
        bookDetail.book_pic = $("[class=\"comicParticulars-left-img loadingIcon\"]").find("img")[0].attribs["data-src"]
        bookDetail.book_name = $('h6').text().trim()
        bookDetail.book_director = $('span.comicParticulars-right-txt>a[href*="/author/"]')
            .map((_, a) => $(a).text().trim())
            .get()
            .join('/')
        bookDetail.book_content = $('p.intro').text().trim()
        let data = JSON.parse(await this.fetch(this.siteUrl + `/comicdetail/${id}/chapters`, null, this.getHeader()))["results"]
        let key = Crypto.enc.Utf8.parse('xxxmanga.woo.key');
        let iv = Crypto.enc.Utf8.parse(data.substr(0, 16));
        let src = Crypto.enc.Hex.parse(data.substr(16));
        let dst = Crypto.AES.decrypt({ciphertext: src}, key, {iv: iv, padding: Crypto.pad.Pkcs7});
        dst = Crypto.enc.Utf8.stringify(dst);
        const groups = JSON.parse(dst).groups;
        let urls = groups.default["chapters"]
            .map((c) => {
                return c.name + '$' + id + '|' + c.id;
            })
            .join('#');
        bookDetail.volumes = '默認';
        bookDetail.urls = urls;
        bookDetail.book_id = id
        return bookDetail
    }

    async parseVodShortListFromJson(obj) {
        const books = [];
        for (const book of obj) {
            books.push(this.parseVodShortFromJson(book))
        }
        return books
    }

    async setHomeVod() {
        let $ = await this.getHtml(this.siteUrl)
        this.homeVodList = await this.parseVodShortListFromDoc($)
    }

    async setCategory(tid, pg, filter, extend) {
        let page = pg || 1;
        if (page === 0) page = 1;
        let link = this.siteUrl + `/comics?theme=${extend.theme || ''}&region=${extend.region || ''}&status=${extend.status || ''}&ordering=${extend.ordering || '-datetime_updated'}`;
        if (page > 1) {
            link += '&offset=' + (page - 1) * 50 + '&limit=50';
        }
        let $ = await this.getHtml(link)
        this.vodList = await this.parseVodShortListFromDocByCategory($)
    }

    async setDetail(id) {
        let $ = await this.getHtml(this.siteUrl + `/comic/${id}`)
        this.vodDetail = await this.parseVodDetailFromDoc($, id)
    }

    async setPlay(flag, id, flags) {
        let info = id.split('|');
        let $ = await this.getHtml(this.siteUrl + `/comic/${info[0]}/chapter/${info[1]}`);
        const data = $('div.imageData')[0].attribs["contentkey"];
        let key = Crypto.enc.Utf8.parse('xxxmanga.woo.key');
        let iv = Crypto.enc.Utf8.parse(data.substr(0, 16));
        let src = Crypto.enc.Hex.parse(data.substr(16));
        let dst = Crypto.AES.decrypt({ciphertext: src}, key, {iv: iv, padding: Crypto.pad.Pkcs7});
        dst = Crypto.enc.Utf8.stringify(dst);
        const list = JSON.parse(dst);
        let content = [];
        for (let index = 0; index < list.length; index++) {
            const element = list[index];
            content[index] = element.url;
        }
        this.playUrl =  {
            "content": content,
        }
    }
    async setSearch(wd, quick) {
        let page = 1
        const link = `${this.siteUrl}/api/kb/web/searcha/comics?offset=${page > 1 ? ((page - 1) * 12).toString() : ''}&platform=2&limit=12&q=${wd}&q_type=`;
        let list = JSON.parse(await this.fetch(link, null, this.getHeader()))["results"]["list"]
        this.vodList = await this.parseVodShortListFromJson(list)
    }
}

let spider = new CopyManhuaSpider()

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
