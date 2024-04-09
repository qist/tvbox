/*
* @File     : jianpian.js
* @Author   : jade
* @Date     : 2024/1/15 10:32
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 完成荐片所有功能（添加弹幕）
*/

import {Spider} from "./spider.js";
import {_, load} from "../lib/cat.js";
import {VodDetail, VodShort} from "../lib/vod.js";
import * as Utils from "../lib/utils.js";


class JianPianSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "http://api2.rinhome.com"
        // this.siteUrl = "https://ownjpykxttjzuhy.jiesiwa.com"
    }

    getName() {
        return "🌼┃荐片┃🌼"
    }

    getAppName() {
        return "荐片"
    }

    getJSName() {
        return "jianpian"
    }

    getType() {
        return 3
    }

    getHeader() {
        return {
            "User-Agent": "jianpian-android/360",
            "JPAUTH": "y261ow7kF2dtzlxh1GS9EB8nbTxNmaK/QQIAjctlKiEv",
            "Referer": "www.jianpianapp.com"
        }
    }

    async spiderInit(inReq=null) {
        if (inReq !== null){
            this.jsBase = await js2Proxy(inReq,"img",this.getHeader());
        }else{
            this.jsBase = await js2Proxy(true, this.siteType, this.siteKey, 'img/', this.getHeader());
        }

    }

    async init(cfg) {
        await super.init(cfg);
        this.danmuStaus = true
        await this.spiderInit(null)
    }


    async parseVodShortListFromJson(data_list) {
        let vod_list = [];
        for (const data of data_list) {
            let vodShort = new VodShort();
            vodShort.vod_id = data["id"]
            if (data["path"] !== undefined) {
                if (!this.catOpenStatus) {
                    vodShort.vod_pic = data["path"] + "@Referer=www.jianpianapp.com@User-Agent=jianpian-version353@JPAUTH=y261ow7kF2dtzlxh1GS9EB8nbTxNmaK/QQIAjctlKiEv"
                } else {
                    vodShort.vod_pic = this.jsBase + Utils.base64Encode(data["path"])
                }
            } else {
                if (!this.catOpenStatus) {
                    vodShort.vod_pic = data["thumbnail"] + "@Referer=www.jianpianapp.com@User-Agent=jianpian-version353@JPAUTH=y261ow7kF2dtzlxh1GS9EB8nbTxNmaK/QQIAjctlKiE"

                } else {
                    vodShort.vod_pic = this.jsBase + Utils.base64Encode(data["thumbnail"])
                }
            }
            vodShort.vod_name = data["title"]
            if (this.catOpenStatus) {
                vodShort.vod_remarks = `评分:${data["score"]}`
            } else {
                if (data["playlist"] !== undefined) {
                    vodShort.vod_remarks = `评分:${data["score"]}` + " " + data["playlist"]["title"]
                } else {
                    vodShort.vod_remarks = `评分:${data["score"]}`
                }
            }
            vod_list.push(vodShort)
        }
        return vod_list
    }


    objToList(list, key, split_value = "*") {
        let value_list = []
        for (const dic of list) {
            value_list.push(dic[key])
        }
        return value_list.join(split_value)
    }

    async parseVodDetailfromJson(obj) {
        let vodDetail = new VodDetail();
        vodDetail.vod_id = obj["id"]
        vodDetail.vod_year = obj["year"]["title"]
        vodDetail.vod_pic = this.jsBase + Utils.base64Encode(obj["thumbnail"])
        vodDetail.type_name = obj["category"][0]["title"]
        vodDetail.vod_name = obj["title"]
        vodDetail.vod_content = obj["description"]
        vodDetail.vod_area = obj["area"]["title"]
        vodDetail.vod_director = this.objToList(obj["directors"], "name")
        vodDetail.vod_actor = this.objToList(obj["actors"], "name")
        vodDetail.vod_remarks = "评分:" + obj["score"]
        let playKeyList = [{"btbo_downlist": "btbo"}, {"xunlei_downlist": "迅雷"}, {"m3u8_downlist": "m3u8"}, {"new_ftp_list": "new_ftp"}, {"new_m3u8_list": "new_m3u8"}]
        let playlist = {}
        let urlList = []
        for (const dic of playKeyList) {
            let key = Object.keys(dic)[0]
            let value = Object.values(dic)[0]
            if (obj[key].length > 0) {
                let url_str_list = []
                for (const dic of obj[key]) {
                    url_str_list.push(dic["title"] + "$" + dic["url"])
                }

                if (urlList.indexOf(url_str_list.join("#")) === -1) {
                    urlList.push(url_str_list.join("#"))
                    playlist[value] = url_str_list.join("#")
                } else {
                    await this.jadeLog.warning(`key为:${key},播放链接重复,无需保存`)
                }

            }
        }
        vodDetail.vod_play_url = _.values(playlist).join('$$$');
        vodDetail.vod_play_from = _.keys(playlist).join('$$$');
        return vodDetail
    }


    async setClasses() {
        let type_name_list = ["全部", "电影", "电视剧", "动漫", "综艺"]
        let type_id_list = ["0", "1", "2", "3", "4"]
        for (let i = 0; i < type_name_list.length; i++) {
            let type_name = type_name_list[i]
            let type_id = type_id_list[i]
            this.classes.push({"type_name": type_name, "type_id": type_id})
        }
    }

    async setFilterObj() {
        this.filterObj = {
            "0": [{
                "key": "area", "name": "地區", "value": [{
                    "n": "全部", "v": "0"
                }, {
                    "n": "国产", "v": "1"
                }, {
                    "n": "中国香港", "v": "3"
                }, {
                    "n": "中国台湾", "v": "6"
                }, {
                    "n": "美国", "v": "5"
                }, {
                    "n": "韩国", "v": "18"
                }, {
                    "n": "日本", "v": "2"
                }]
            }, {
                "key": "year", "name": "年份", "value": [{
                    "n": "全部", "v": "0"
                }, {
                    "n": "2024", "v": "119"
                }, {
                    "n": "2023", "v": "153"
                }, {
                    "n": "2022", "v": "101"
                }, {
                    "n": "2021", "v": "118"
                }, {
                    "n": "2020", "v": "16"
                }, {
                    "n": "2019", "v": "7"
                }, {
                    "n": "2018", "v": "2"
                }, {
                    "n": "2017", "v": "3"
                }, {
                    "n": "2016", "v": "22"
                }]
            }, {
                "key": "by", "name": "排序", "value": [{
                    "n": "热门", "v": "hot"
                }, {
                    "n": "更新", "v": "updata"
                }, {
                    "n": "评分", "v": "rating"
                }]
            }], "1": [{
                "key": "area", "name": "地區", "value": [{
                    "n": "全部", "v": "0"
                }, {
                    "n": "国产", "v": "1"
                }, {
                    "n": "中国香港", "v": "3"
                }, {
                    "n": "中国台湾", "v": "6"
                }, {
                    "n": "美国", "v": "5"
                }, {
                    "n": "韩国", "v": "18"
                }, {
                    "n": "日本", "v": "2"
                }]
            }, {
                "key": "year", "name": "年份", "value": [{
                    "n": "全部", "v": "0"
                }, {
                    "n": "2024", "v": "119"
                }, {
                    "n": "2023", "v": "153"
                }, {
                    "n": "2022", "v": "101"
                }, {
                    "n": "2021", "v": "118"
                }, {
                    "n": "2020", "v": "16"
                }, {
                    "n": "2019", "v": "7"
                }, {
                    "n": "2018", "v": "2"
                }, {
                    "n": "2017", "v": "3"
                }, {
                    "n": "2016", "v": "22"
                }]
            }, {
                "key": "by", "name": "排序", "value": [{
                    "n": "热门", "v": "hot"
                }, {
                    "n": "更新", "v": "updata"
                }, {
                    "n": "评分", "v": "rating"
                }]
            }], "2": [{
                "key": "area", "name": "地區", "value": [{
                    "n": "全部", "v": "0"
                }, {
                    "n": "国产", "v": "1"
                }, {
                    "n": "中国香港", "v": "3"
                }, {
                    "n": "中国台湾", "v": "6"
                }, {
                    "n": "美国", "v": "5"
                }, {
                    "n": "韩国", "v": "18"
                }, {
                    "n": "日本", "v": "2"
                }]
            }, {
                "key": "year", "name": "年份", "value": [{
                    "n": "全部", "v": "0"
                }, {
                    "n": "2024", "v": "119"
                }, {
                    "n": "2023", "v": "153"
                }, {
                    "n": "2022", "v": "101"
                }, {
                    "n": "2021", "v": "118"
                }, {
                    "n": "2020", "v": "16"
                }, {
                    "n": "2019", "v": "7"
                }, {
                    "n": "2018", "v": "2"
                }, {
                    "n": "2017", "v": "3"
                }, {
                    "n": "2016", "v": "22"
                }]
            }, {
                "key": "by", "name": "排序", "value": [{
                    "n": "热门", "v": "hot"
                }, {
                    "n": "更新", "v": "updata"
                }, {
                    "n": "评分", "v": "rating"
                }]
            }], "3": [{
                "key": "area", "name": "地區", "value": [{
                    "n": "全部", "v": "0"
                }, {
                    "n": "国产", "v": "1"
                }, {
                    "n": "中国香港", "v": "3"
                }, {
                    "n": "中国台湾", "v": "6"
                }, {
                    "n": "美国", "v": "5"
                }, {
                    "n": "韩国", "v": "18"
                }, {
                    "n": "日本", "v": "2"
                }]
            }, {
                "key": "year", "name": "年份", "value": [{
                    "n": "全部", "v": "0"
                }, {
                    "n": "2024", "v": "119"
                }, {
                    "n": "2023", "v": "153"
                }, {
                    "n": "2022", "v": "101"
                }, {
                    "n": "2021", "v": "118"
                }, {
                    "n": "2020", "v": "16"
                }, {
                    "n": "2019", "v": "7"
                }, {
                    "n": "2018", "v": "2"
                }, {
                    "n": "2017", "v": "3"
                }, {
                    "n": "2016", "v": "22"
                }]
            }, {
                "key": "by", "name": "排序", "value": [{
                    "n": "热门", "v": "hot"
                }, {
                    "n": "更新", "v": "updata"
                }, {
                    "n": "评分", "v": "rating"
                }]
            }], "4": [{
                "key": "area", "name": "地區", "value": [{
                    "n": "全部", "v": "0"
                }, {
                    "n": "国产", "v": "1"
                }, {
                    "n": "中国香港", "v": "3"
                }, {
                    "n": "中国台湾", "v": "6"
                }, {
                    "n": "美国", "v": "5"
                }, {
                    "n": "韩国", "v": "18"
                }, {
                    "n": "日本", "v": "2"
                }]
            }, {
                "key": "year", "name": "年份", "value": [{
                    "n": "全部", "v": "0"
                }, {
                    "n": "2024", "v": "119"
                }, {
                    "n": "2023", "v": "153"
                }, {
                    "n": "2022", "v": "101"
                }, {
                    "n": "2021", "v": "118"
                }, {
                    "n": "2020", "v": "16"
                }, {
                    "n": "2019", "v": "7"
                }, {
                    "n": "2018", "v": "2"
                }, {
                    "n": "2017", "v": "3"
                }, {
                    "n": "2016", "v": "22"
                }]
            }, {
                "key": "by", "name": "排序", "value": [{
                    "n": "热门", "v": "hot"
                }, {
                    "n": "更新", "v": "updata"
                }, {
                    "n": "评分", "v": "rating"
                }]
            }]
        }
    }

    async setHomeVod() {
        let content = await this.fetch(this.siteUrl + "/api/tag/hand?code=unknown601193cf375db73d&channel=wandoujia", null, this.getHeader())
        if (!_.isEmpty(content)) {
            let content_json = JSON.parse(content)
            let data_list = content_json["data"][0]["video"]
            this.homeVodList = await this.parseVodShortListFromJson(data_list)
        }
    }


    async setCategory(tid, pg, filter, extend) {
        let cateId = extend["cateId"] ?? tid
        let area = extend["area"] ?? "0";
        let year = extend["year"] ?? "0";
        let by = extend["by"] ?? "hot";
        this.limit = 24
        let categoryUrl = this.siteUrl + `/api/crumb/list?area=${area}&category_id=${cateId}&page=${pg}&type=0&limit=24&sort=${by}&year=${year}`
        await this.jadeLog.debug(`分类URL:${categoryUrl}`)
        let content = await this.fetch(categoryUrl, null, this.getHeader())
        if (!_.isEmpty(content)) {
            let content_json = JSON.parse(content)
            let data = content_json["data"]
            this.vodList = await this.parseVodShortListFromJson(data)
        }
    }

    async setDetail(id) {
        let url = this.siteUrl + "/api/node/detail?channel=wandoujia&token=&id=" + id;
        let content = await this.fetch(url, null, this.getHeader())
        if (!_.isEmpty(content)) {
            let content_json = JSON.parse(content);
            let data_list = content_json["data"]
            this.vodDetail = await this.parseVodDetailfromJson(data_list)
        }
    }


    async setSearch(wd, quick) {
        let url = this.siteUrl + "/api/video/search?page=1" + "&key=" + wd;
        const content = await this.fetch(url, null, this.getHeader());
        if (!_.isEmpty(content)) {
            let content_json = JSON.parse(content)
            let data_list = content_json["data"]
            this.vodList = await this.parseVodShortListFromJson(data_list)
        }
    }

    async setPlay(flag, id, flags) {
        await this.jadeLog.debug(`播放链接为:${id}`)
        this.playUrl = id
    }
}


let spider = new JianPianSpider()

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