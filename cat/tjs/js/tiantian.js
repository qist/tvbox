/*
* @File     : tiantian.js
* @Author   : jade
* @Date     : 2024/04/15 10:48
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 天天影视
*/
import {Spider} from "./spider.js";
import {_} from "../lib/cat.js";
import * as Utils from "../lib/utils.js";
import {VodDetail, VodShort} from "../lib/vod.js";

class TianTianSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "http://op.ysdqjs.cn"
        this.cookie = ""
        this.extendObj = {"extend": "类型", "area": "地区", "lang": "语言", "year": "年代"}
        this.parseMap = {};

    }

    async request(reqUrl, method, data) {
        const headers = {
            'User-Agent': Utils.CHROME,
        };
        if (!_.isEmpty(this.cookie)) {
            headers['Cookie'] = this.cookie;
        }
        const postType = method === 'post' ? 'form-data' : '';
        let res = await req(reqUrl, {
            method: method || 'get', headers: headers, data: data, postType: postType,
        });
        if (res.code === 403) {
            const path = res.data.match(/window\.location\.href ="(.*?)"/)[1];
            this.cookie = _.isArray(res.headers['set-cookie']) ? res.headers['set-cookie'].join(';') : res.headers['set-cookie'];
            headers['Cookie'] = this.cookie;
            res = await req(this.siteUrl + path, {
                method: method || 'get', headers: headers, data: data, postType: postType,
            });
        }
        return res.content;
    }

    async postData(url, data) {
        const timestamp = Math.floor(new Date().getTime() / 1000);
        const key = 'kj5649ertj84ks89r4jh8s45hf84hjfds04k';
        const sign = md5X(key + timestamp).toString();
        let defaultData = {
            sign: sign, timestamp: timestamp,
        };
        const reqData = data ? _.merge(defaultData, data) : defaultData;
        return await this.request(url, 'post', reqData);
    }


    getName() {
        return "⛄┃天天影视┃⛄"
    }

    getAppName() {
        return "天天影视"
    }

    getJSName() {
        return "tiantian"
    }

    getType() {
        return 3
    }


    async init(cfg) {
        await super.init(cfg);
        this.danmuStaus = false
    }

    generateParam(tid, pg, extend, limit) {
        const param = {
            type_id: tid, page: pg, limit: limit,
        };
        if (extend.class) {
            param.class = extend.class;
        }
        if (extend.area) {
            param.area = extend.area;
        }
        if (extend.lang) {
            param.lang = extend.lang;
        }
        if (extend.year) {
            param.year = extend.year;
        }
        // if (extend.order) {
        //     param.order = extend.order;
        // }
        return param;
    }

    async getFilter(data) {
        let extend_list = []
        Object.keys(data).forEach(key => {
            if (Array.isArray(data[key])) {
                let extend_dic = {"key": key, "name": this.extendObj[key], "value": []}
                for (const extend_data of data[key]) {
                    extend_dic["value"].push({"n": extend_data, "v": extend_data})
                }
                extend_list.push(extend_dic)
            }
        })
        return extend_list
    }

    async setClasses() {
        let resJson = JSON.parse(await this.postData(this.siteUrl + '/v2/type/top_type'))
        for (const data of resJson["data"]["list"]) {
            let type_name = data["type_name"]
            let type_id = data["type_id"].toString()
            this.classes.push(this.getTypeDic(type_name, type_id))
            this.filterObj[type_id] = await this.getFilter(data)
        }
    }

    async parseVodShortListFromJson(vodList) {
        let vod_list = []
        for (const vodData of vodList) {
            let vodShort = new VodShort()
            vodShort.load_data(vodData)
            if (_.isEmpty(vodShort.vod_pic) && vodData["vod_pic_thumb"] !== undefined){
                vodShort.vod_pic = vodData["vod_pic_thumb"]
            }
            if (vodShort.vod_name !== "首页轮播"){
                vod_list.push(vodShort)
            }

        }
        return vod_list
    }

    async parseVodDetailfromJson(detailObj) {
        let vodDetail = new VodDetail()
        vodDetail.load_data(detailObj)
        vodDetail.vod_content = Utils.formatContent(vodDetail.vod_content)
        const playInfo = detailObj["vod_play_list"];
        const playVod = {};
        _.each(playInfo, (obj) => {
            const sourceName = obj.name;
            let playList = '';
            const videoInfo = obj.urls;
            const parse = obj["parse_urls"];
            if (!_.isEmpty(parse)) this.parseMap[sourceName] = parse;
            const vodItems = _.map(videoInfo, (epObj) => {
                const epName = epObj.name;
                const playUrl = epObj.url;
                return epName + '$' + playUrl;
            });
            if (_.isEmpty(vodItems)) return;
            playList = vodItems.join('#');
            playVod[sourceName] = playList;
        });
        vodDetail.vod_play_from = _.keys(playVod).join('$$$');
        vodDetail.vod_play_url = _.values(playVod).join('$$$');
        return vodDetail
    }

    async setHomeVod() {
        let resJson = JSON.parse(await this.postData(this.siteUrl + '/v2/type/tj_vod'))

        let vod_list = []

        for (const data of resJson["data"]["type_vod"]) {
            if (data["type_name"] !== "广告") {
               vod_list = await this.parseVodShortListFromJson(data["vod"])
               this.homeVodList = [...this.homeVodList,...vod_list]
            }

        }
        vod_list = await this.parseVodShortListFromJson(resJson["data"]["loop"])
        this.homeVodList = [...this.homeVodList,...vod_list]
        vod_list = await this.parseVodShortListFromJson(resJson["data"]["cai"])
        this.homeVodList = [...this.homeVodList,...vod_list]
    }

    async setCategory(tid, pg, filter, extend) {
        const limit = 12;
        const param = this.generateParam(tid, pg, extend, limit);
        const resJson = JSON.parse(await this.postData(this.siteUrl + '/v2/home/type_search', param));
        this.vodList = await this.parseVodShortListFromJson(resJson["data"]["list"])
    }

    async setDetail(id) {
        const param = {
            vod_id: id,
        }
        const resJson = JSON.parse(await this.postData(this.siteUrl + '/v2/home/vod_details', param));
        this.vodDetail = await this.parseVodDetailfromJson(resJson["data"])
    }

    async setPlay(flag, id, flags) {
        const parsers = this.parseMap[flag];
        if (flag.indexOf("芒果") > -1 || flag.indexOf("腾讯") > -1 || flag.indexOf("爱奇艺") > -1) {
            this.danmuStaus = true
            if (!this.catOpenStatus) {
                this.danmuUrl = await this.danmuSpider.downloadDanmu("https://dmku.thefilehosting.com/?ac=dm&url=" + id)
            }
        }
        if (!_.isEmpty(parsers)) {
            for (const parser of parsers) {
                if (_.isEmpty(parser)) continue;
                try {
                    const resp = await this.request(parser + id);
                    const json = JSON.parse(resp);
                    if (!_.isEmpty(json.url)) {
                        this.playUrl = json.url;
                        break;
                    }
                } catch (e) {
                }
            }
        }
    }

    async setSearch(wd, quick, pg) {
        const limit = 12;
        const param = {
            keyword: wd, page: pg, limit: limit,
        };
        const resJson = JSON.parse(await this.postData(this.siteUrl + '/v2/home/search', param));
        this.vodList = await this.parseVodShortListFromJson(resJson["data"]["list"])
        const page = parseInt(pg);
        let pageCount = page;
        if (this.vodList.length === limit) {
            pageCount = page + 1;
        }
        this.result.setPage(page, pageCount, limit, pageCount)
    }
}

let spider = new TianTianSpider()

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

export {spider, TianTianSpider}