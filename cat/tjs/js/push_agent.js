/*
* @File     : push_agent.js
* @Author   : jade
* @Date     : 2024/3/6 9:30
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/
import {Spider} from "./spider.js";
import {VodDetail} from "../lib/vod.js";
import * as Utils from "../lib/utils.js";
import {detailContent, initAli, playContent} from "../lib/ali.js";

class PushSpider extends Spider {
    constructor() {
        super();
    }

    getName() {
        return "┃推送┃"
    }

    getAppName() {
        return "推送"
    }

    getJSName() {
        return "push"
    }

    getType() {
        return 4
    }

    async init(cfg) {
        try {
            this.cfgObj = await this.SpiderInit(cfg)
             this.catOpenStatus = this.cfgObj.CatOpenStatus
            await initAli(this.cfgObj["token"]);
        } catch (e) {
            await this.jadeLog.error(`初始化失败,失败原因为:${e}`)
        }

    }

    async check(args){
        // CatVodOpen目前支持http链接和https链接
        await spider.jadeLog.debug(`剪切板输入内容为:${args}`)
        if (this.catOpenStatus){
            return !!args.startsWith("http");
        }else{
            // TV目前支持http链接和https链接和Ftp和magnet等格式
            return !!(args.startsWith("http") || args.startsWith("ftp") || args.startsWith("magnet"));
        }
    }

    async parseVodDetailfromJson(id) {
        let vodDetail = new VodDetail()
        vodDetail.vod_pic = Utils.RESOURCEURL + "/resources/push.jpg"
        let mather = Utils.patternAli.exec(id)
        if (mather !== null && mather.length > 0) {
            let aliVodDetail = await detailContent([id])
            vodDetail.vod_play_url = aliVodDetail.vod_play_url
            vodDetail.vod_play_from = aliVodDetail.vod_play_from
        } else {
            vodDetail.vod_play_from = '推送';
            vodDetail.vod_play_url = '推送$' + id;
        }
        return vodDetail
    }

    async setDetail(id) {
        this.vodDetail = await this.parseVodDetailfromJson(id)
    }

    async setPlay(flag, id, flags) {
        if (flag === "推送"){
            this.playUrl = id
        }else{
           this.playUrl = JSON.parse(await playContent(flag, id, flags))["url"];
        }
    }
}

let spider = new PushSpider()

async function check(args) {
  return await spider.check(args)
}

async function init(cfg) {
    await spider.init(cfg)
}

async function detail(id) {
    return await spider.detail(id)
}

async function play(flag, id, flags) {
    return await spider.play(flag, id, flags)
}

export function __jsEvalReturn() {
    return {
        support: check, init: init, detail: detail, play: play,
    };
}
export {spider}