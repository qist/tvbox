/*
* @File     : audiomack.js
* @Author   : jade
* @Date     : 2024/1/31 15:56
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 音乐之声
*/
import {Spider} from "./spider.js";
import {BookShort} from "../lib/book.js";
import {Crypto} from "../lib/cat.js";

function u(e) {
    (this._parameters = {}), this._loadParameters(e || {});
}

u.prototype = {
    _loadParameters: function (e) {
        e instanceof Array ? this._loadParametersFromArray(e) : "object" == typeof e && this._loadParametersFromObject(e);
    }, _loadParametersFromArray: function (e) {
        var n;
        for (n = 0; n < e.length; n++) this._loadParametersFromObject(e[n]);
    }, _loadParametersFromObject: function (e) {
        var n;
        for (n in e) if (e.hasOwnProperty(n)) {
            var r = this._getStringFromParameter(e[n]);
            this._loadParameterValue(n, r);
        }
    }, _loadParameterValue: function (e, n) {
        var r;
        if (n instanceof Array) {
            for (r = 0; r < n.length; r++) {
                var i = this._getStringFromParameter(n[r]);
                this._addParameter(e, i);
            }
            0 == n.length && this._addParameter(e, "");
        } else this._addParameter(e, n);
    }, _getStringFromParameter: function (e) {
        var n = e || "";
        try {
            ("number" == typeof e || "boolean" == typeof e) && (n = e.toString());
        } catch (e) {
        }
        return n;
    }, _addParameter: function (e, n) {
        this._parameters[e] || (this._parameters[e] = []), this._parameters[e].push(n);
    }, get: function () {
        return this._parameters;
    },
};

function _decode(e) {
    return e ? decodeURIComponent(e) : "";
}

function getNormalizedParams(parameters) {
    const sortedKeys = [];
    const normalizedParameters = [];
    for (let e in parameters) {
        sortedKeys.push(_encode(e));
    }
    sortedKeys.sort();
    for (let idx = 0; idx < sortedKeys.length; idx++) {
        const e = sortedKeys[idx];
        var n, r, i = _decode(e), a = parameters[i];
        for (a.sort(), n = 0; n < a.length; n++) (r = _encode(a[n])), normalizedParameters.push(e + "=" + r);
    }
    return normalizedParameters.join("&");
}

function nonce(e = 10) {
    let n = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789", r = "";
    for (let i = 0; i < e; i++) r += n.charAt(Math.floor(Math.random() * n.length));
    return r;
}

function _encode(e) {
    return e ? encodeURIComponent(e)
        .replace(/[!'()]/g, escape)
        .replace(/\*/g, "%2A") : "";
}

function getSignature(method, urlPath, params, secret = "f3ac5b086f3eab260520d8e3049561e6") {
    urlPath = urlPath.split("?")[0];
    urlPath = urlPath.startsWith("http") ? urlPath : "https://api.audiomack.com/v1" + urlPath;
    const r = new u(params).get();
    const httpMethod = method.toUpperCase();
    const normdParams = getNormalizedParams(r);
    const l = _encode(httpMethod) + "&" + _encode(urlPath) + "&" + _encode(normdParams);
    return Crypto.HmacSHA1(l, secret + "&").toString(Crypto.enc.Base64);
}

class AudioMackSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://api.audiomack.com/v1";
    }

    getName() {
        return "🎵┃音声┃🎵"
    }

    getAppName() {
        return "音声"
    }

    getJSName() {
        return "audiomack"
    }

    getType() {
        return 10
    }

    async parseVodShortListFromJson(obj) {
        let books = []
        for (const data of obj["results"]["playlists"]) {
            let bookShort = new BookShort()
            bookShort.book_id = data["id"]
            bookShort.book_pic = data["image"]
            bookShort.book_name = data["title"]
            bookShort.book_remarks = data["description"]
            books.push(bookShort)
        }
        return books
    }

    async setClasses() {
        this.classes = [{"type_name": "推荐榜单", "type_id": "最近更新"}]
        const genres = [{
            title: "All Genres", url_slug: "null",
        }, {
            title: "Afrosounds", url_slug: "afrobeats",
        }, {
            title: "Hip-Hop/Rap", url_slug: "rap",
        }, {
            title: "Latin", url_slug: "latin",
        }, {
            title: "Caribbean", url_slug: "caribbean",
        }, {
            title: "Pop", url_slug: "pop",
        }, {
            title: "R&B", url_slug: "rb",
        }, {
            title: "Gospel", url_slug: "gospel",
        }, {
            title: "Electronic", url_slug: "electronic",
        }, {
            title: "Rock", url_slug: "rock",
        }, {
            title: "Punjabi", url_slug: "punjabi",
        }, {
            title: "Country", url_slug: "country",
        }, {
            title: "Instrumental", url_slug: "instrumental",
        }, {
            title: "Podcast", url_slug: "podcast",
        },];
        for (const genre of genres) {
            this.classes.push(this.getTypeDic(genre["title"], genre["url_slug"]))
        }
    }


    /* 推荐歌单
     * */
    async setHomeVod() {
        let tag = {id: "34", title: "What's New", url_slug: "whats-new"};
        const params = {
            featured: "yes",
            limit: 20,
            oauth_consumer_key: "audiomack-js",
            oauth_nonce: nonce(32),
            oauth_signature_method: "HMAC-SHA1",
            oauth_timestamp: Math.round(Date.now() / 1e3),
            oauth_version: "1.0",
            page: 1,
            slug: tag.url_slug,
        };
        const oauth_signature = getSignature("GET", "/playlist/categories", params);
        let url = this.siteUrl + "/playlist/categories"
        let content = await this.fetch(url, Object.assign(Object.assign({}, params), {oauth_signature}), this.getHeader());
        this.homeVodList = await this.parseVodShortListFromJson(JSON.parse(content))
    }

    async setCategory(tid, pg, filter, extend) {
        let partialUrl;
        if (tid === "null"){
            partialUrl = `/music/page/${pg}`;
        }else{
            partialUrl = `/music/${tid}/page/${pg}`;
        }

        const url = `https://api.audiomack.com/v1${partialUrl}`;
        const params = {
            oauth_consumer_key: "audiomack-js",
            oauth_nonce: nonce(32),
            oauth_signature_method: "HMAC-SHA1",
            oauth_timestamp: Math.round(Date.now() / 1e3),
            oauth_version: "1.0",
            type: "song",
        };
        const oauth_signature = getSignature("GET", partialUrl, params);
        const results = await this.fetch(url, Object.assign(Object.assign({}, params), {oauth_signature}),this.getHeader())

        let x = 0
    }


}

let spider = new AudioMackSpider()

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