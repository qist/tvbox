/*
* @File     : ikanbot.js
* @Author   : jade
* @Date     : 2024/1/15 10:32
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 爱看机器人(已失效：上盾)
*/

import {Spider} from "./spider.js";
import {load, _} from "../lib/cat.js";
import {VodDetail, VodShort} from "../lib/vod.js";
import * as Utils from "../lib/utils.js";


function _0xf746(_0xbb40c4, _0x1cb776) {
    const _0x45e084 = _0x45e0();
    return _0xf746 = function (_0xf74696, _0x4d32af) {
        _0xf74696 = _0xf74696 - 0x1a8;
        let _0xcbfa28 = _0x45e084[_0xf74696];
        return _0xcbfa28;
    }, _0xf746(_0xbb40c4, _0x1cb776);
}

function _0x45e0() {
    const _0x58b10c = ['1580630GngmmA', '117uvwflw', 'join', 'current_id', '565448Apkhig', '23092JwmytW', '707152yowhOv', 'getElementById', '855936CGaczt', 'length', '2966831GCGpvn', '611266nfcTEf', 'value', 'substring'];
    _0x45e0 = function () {
        return _0x58b10c;
    };
    return _0x45e0();
}

(function (_0x27923d, _0x43d7fc) {
    const _0x439396 = _0xf746, _0x30f164 = _0x27923d();
    while (!![]) {
        try {
            const _0xa560eb = -parseInt(_0x439396(0x1b4)) / 0x1 + parseInt(_0x439396(0x1ad)) / 0x2 + -parseInt(_0x439396(0x1b1)) / 0x3 * (-parseInt(_0x439396(0x1b5)) / 0x4) + -parseInt(_0x439396(0x1b0)) / 0x5 + parseInt(_0x439396(0x1aa)) / 0x6 + parseInt(_0x439396(0x1ac)) / 0x7 + parseInt(_0x439396(0x1a8)) / 0x8;
            if (_0xa560eb === _0x43d7fc) break; else _0x30f164['push'](_0x30f164['shift']());
        } catch (_0x3ae316) {
            _0x30f164['push'](_0x30f164['shift']());
        }
    }
}(_0x45e0, 0x4a3d9));

function get_tks(play_id, e_token) {
    const _0xf07220 = _0xf746;
    let _0x35162d = play_id, _0xf25678 = e_token;
    if (!_0x35162d || !_0xf25678) return;
    let _0x3882a3 = _0x35162d['length'], _0x52a097 = _0x35162d[_0xf07220(0x1af)](_0x3882a3 - 0x4, _0x3882a3),
        _0x2d9d1b = [];
    for (let _0x570711 = 0x0; _0x570711 < _0x52a097[_0xf07220(0x1ab)]; _0x570711++) {
        let _0x23e537 = parseInt(_0x52a097[_0x570711]), _0x48b93d = _0x23e537 % 0x3 + 0x1;
        _0x2d9d1b[_0x570711] = _0xf25678[_0xf07220(0x1af)](_0x48b93d, _0x48b93d + 0x8), _0xf25678 = _0xf25678[_0xf07220(0x1af)](_0x48b93d + 0x8, _0xf25678[_0xf07220(0x1ab)]);
    }
    return _0x2d9d1b[_0xf07220(0x1b2)]('');
}

class IKanBotSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://v.ikanbot.com"
    }

    getName() {
        return `🤖┃爱看机器人┃🤖`
    }

    getAppName() {
        return "爱看机器人"
    }

    getJSName() {
        return "ikanbot"
    }

    getType() {
        return 3
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
        let vod_list = [];
        let VodShortElements = $($("[class=\"row list-wp\"]")).find("a")
        for (const vodShortElement of VodShortElements) {
            let vodShort = new VodShort()
            let reElement = $(vodShortElement).find("img")[0]
            vodShort.vod_id = vodShortElement.attribs["href"]
            vodShort.vod_pic = this.jsBase + Utils.base64Encode(reElement.attribs["data-src"])
            vodShort.vod_name = reElement.attribs["alt"]
            vod_list.push(vodShort)
        }
        return vod_list
    }

    getChildren(detail, index) {
        try {
            return detail[index].children[0].data;
        } catch (e) {
            return ""
        }
    }

    async parseVodDetailFromDoc($) {
        const detail = $('div.detail > .meta');
        let vodDetail = new VodDetail();
        vodDetail.vod_pic = this.jsBase + Utils.base64Encode($('div.item-root > img')[0].attribs['data-src'])
        vodDetail.vod_name = this.getChildren(detail, 0)
        vodDetail.vod_year = this.getChildren(detail, 1)
        vodDetail.vod_area = this.getChildren(detail, 3);
        vodDetail.vod_actor = this.getChildren(detail, 4);

        let id = Utils.getStrByRegex(/<input type="hidden" id="current_id" value="(.*?)"/, $.html())
        let token = Utils.getStrByRegex(/<input type="hidden" id="e_token" value="(.*?)"/, $.html())
        let mtype = Utils.getStrByRegex(/<input type="hidden" id="mtype" value="(.*?)"/, $.html())
        let params = {
            "videoId": id, "mtype": mtype, "token": get_tks(id, token),
        }
        let content = await this.fetch(this.siteUrl + '/api/getResN', params, this.getHeader())

        const list = JSON.parse(content)["data"]["list"];
        let playlist = {};

        let index = 0
        let form_list = []
        for (const l of list) {
            const flagData = JSON.parse(l["resData"]);
            for (const f of flagData) {
                index = index + 1
                const from = f.flag;
                const urls = f.url;
                if (!from || !urls) continue;
                if (playlist[from]) continue;
                form_list.push(`线路${index}`)
                playlist[from] = urls;
            }
        }
        vodDetail.vod_play_from = form_list.join('$$$');
        vodDetail.vod_play_url = _.values(playlist).join('$$$');
        return vodDetail
    }

    async parseVodShortListFromDocBySearch($) {
        let vod_list = []
        const items = $('div.media > div.media-left > a');
        for (const item of items) {
            let vodShort = new VodShort();
            const img = $(item).find('img:first')[0];
            vodShort.vod_id = item.attribs.href
            vodShort.vod_name = img.attribs.alt
            vodShort.vod_pic = this.jsBase + Utils.base64Encode(img.attribs['data-src'])
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async setClasses() {
        let html = await this.fetch(this.siteUrl + "/category", null, this.getHeader())
        if (!_.isEmpty(html)) {
            let $ = load(html)
            let classElements = $($($("[class=\"row visible-xs-block visible-sm-block\"]")).find("li")).find("a")
            for (const classElement of classElements) {
                this.classes.push({"type_name": $(classElement).text(), "type_id": classElement.attribs["href"]})
            }
        }
    }

    async setFilterObj() {
        for (const class_dic of this.classes.slice(1, 9)) {
            let type_id = class_dic["type_id"]
            if (type_id.indexOf("category") === -1 || type_id.indexOf(",") > -1) {
                let type_url = type_id.split(",").slice(-1)[0]
                let html = await this.fetch(this.siteUrl + type_url, null, this.getHeader())
                if (!_.isEmpty(html)) {
                    let $ = load(html)
                    let containerElement = $("[class=\"row visible-xs-block visible-sm-block\"]")
                    let filterElements = containerElement.find("[class=\"nav nav-pills\"]").find("a")
                    let value_list = []
                    if (type_id.indexOf(",") > -1) {
                        value_list.push({"n": "全部", "v": type_id.split(",")[0]})

                    }
                    let extend_dic = {
                        "key": type_id, "name": $(containerElement.find("h5")).text(), "value": value_list
                    }
                    for (const filterElement of filterElements) {
                        value_list.push({"n": $(filterElement).text(), "v": filterElement.attribs["href"]})
                    }
                    if (value_list.length > 0) {
                        this.filterObj[type_id] = [extend_dic]
                    }

                }
            }

        }
    }

    async setHomeVod() {
        let html = await this.fetch(this.siteUrl, null, this.getHeader())
        if (!_.isEmpty(html)) {
            let $ = load(html)
            this.homeVodList = await this.parseVodShortListFromDoc($)
        }
    }

    async setCategory(tid, pg, filter, extend) {
        let categoryUrl = (this.siteUrl + (extend[tid] || tid.split(",")[0]))
        let update_page = false
        if (categoryUrl.indexOf("html") > -1) {
            categoryUrl = categoryUrl.replace('.html', pg > 1 ? `-p-${pg}.html` : '.html');
        } else {
            categoryUrl = categoryUrl + `?p=${pg}`
            update_page = true

        }
        await this.jadeLog.debug(`分类URL:${categoryUrl}`)
        let html = await this.fetch(categoryUrl, null, this.getHeader())
        if (!_.isEmpty(html)) {
            let $ = load(html)
            this.vodList = await this.parseVodShortListFromDoc($)
            let pageDoc = $('div.page-more > a:contains(下一页)')
            if (update_page) {
                this.page = parseInt(pageDoc[0].attribs["href"].split("p=")[1])
            }
            const hasMore = pageDoc.length > 0;
            this.limit = 24
            this.count = hasMore ? parseInt(pg) + 1 : parseInt(pg);
            this.total = this.limit * this.count

        }
    }

    async setDetail(id) {
        let html = await this.fetch(this.siteUrl + id, null, this.getHeader())
        if (!_.isEmpty(html)) {
            let $ = load(html);
            this.vodDetail = await this.parseVodDetailFromDoc($)
        }
    }


    async setSearch(wd, quick) {
        const html = await this.fetch(this.siteUrl + '/search?q=' + wd, null, this.getHeader());
        if (!_.isEmpty(html)) {
            let $ = load(html)
            this.vodList = await this.parseVodShortListFromDocBySearch($)
        }

    }

    async setPlay(flag, id, flags) {
        this.playUrl = id
    }

}


let spider = new IKanBotSpider()

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