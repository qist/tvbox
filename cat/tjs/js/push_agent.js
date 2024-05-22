/*
* @File     : push_agent.js
* @Author   : jade
* @Date     : 2024/3/6 9:30
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/
import {_} from "../lib/cat.js";
import {Spider} from "./spider.js";
import {VodDetail} from "../lib/vod.js";
import * as Utils from "../lib/utils.js";
import { detailContent,initCloud,playContent,getHeaders} from "../lib/cloud.js";

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
            await initCloud(this.cfgObj);
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
        let quarkMatcher = Utils.patternQuark.exec(id)
        if (mather !== null && mather.length > 0) {
            let playVod = await detailContent([id])
            vodDetail.vod_play_from = _.keys(playVod).join('$$$');
            vodDetail.vod_play_url = _.values(playVod).join('$$$');
        } else if (quarkMatcher !== null && quarkMatcher.length > 0){
            let playVod = await detailContent([id])
            vodDetail.vod_play_from = _.keys(playVod).join('$$$');
            vodDetail.vod_play_url = _.values(playVod).join('$$$');
        }else {
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
            this.playUrl = await playContent(flag, id, flags);
            this.result.setHeader(getHeaders(flag))
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