/*
* @File     : feifan.js
* @Author   : jade
* @Date     : 2024/02/06 14:58
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 非凡资源
*/

import {VodSpider} from "./vodSpider.js";

class FeiFan18Spider extends VodSpider {
    constructor() {
        super();
        this.siteUrl = "http://cj.ffzyapi.com"
        this.remove18 = false
        this.type_id_18 = 34
    }

    getAppName() {
        return "非凡资源18+"
    }

    getName() {
        return "🔞┃非凡资源18+┃🔞"
    }

    getJSName() {
        return "feifan18"
    }

    getType() {
        return 3
    }

    async spiderInit(inReq) {
        await super.spiderInit(inReq);
    }


    async init(cfg) {
        await super.init(cfg);
        await this.spiderInit(null)

    }

}

let spider = new FeiFan18Spider()

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