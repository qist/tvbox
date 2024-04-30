/*
* @File     : dubo.js
* @Author   : jade
* @Date     : 2024/4/16 18:46
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/
import {TianTianSpider} from "./tiantian.js"

class DuboSpider extends TianTianSpider {
    constructor() {
        super();
        this.siteUrl = "http://v.rbotv.cn"
        this.cookie = ""
        this.extendObj = {"extend": "类型", "area": "地区", "year": "年代"}
        this.parseMap = {};

    }

    getName() {
        return "🛶┃独播影视┃🛶"
    }
    getAppName() {
        return "独播影视"
    }
    getJSName() {
        return "dubo"
    }
    getType() {
        return 3
    }
    async init(cfg) {
        await super.init(cfg);
        this.danmuStaus = false
    }
}

let spider = new DuboSpider()

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