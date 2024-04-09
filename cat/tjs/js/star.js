/*
* @File     : star.js
* @Author   : jade
* @Date     : 2024/2/21 10:36
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 星视界 需要翻墙
*/
import {VodDetail, VodShort} from "../lib/vod.js"
import * as Utils from "../lib/utils.js";
import {Spider} from "./spider.js";
import {_} from "../lib/cat.js";


class StarSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://www.histar.tv"
        this.apiUrl = "https://aws.ulivetv.net"
    }

    getAppName() {
        return "星视界"
    }

    getName() {
        return "☄️┃星视界┃墙☄️"
    }
    getJSName() {
        return "star"
    }

    getType() {
        return 3
    }

    getApiHeader() {
        return {'User-Agent': Utils.MOBILEUA, "Content-Type": 'application/json'}
    }

    async setClasses() {
        let $ = await this.getHtml()
        let navElements = $($("[class=\"nav_nav__zgz60\"]")[0]).find("a")
        for (const navElement of navElements) {
            let type_id = navElement.attribs.href
            let type_name = $(navElement).text()
            if (type_id !== "/" && type_name !== "电视直播") {
                this.classes.push(this.getTypeDic(type_name, type_id))
            }
        }
    }

    convertTypeData(typeData, key, name) {
        if (!typeData || !typeData[key] || typeData[key].length <= 2) {
            return null;
        }
        let valueList = typeData[key];
        if (key === 'time') {
            valueList = valueList.sort((a, b) => {
                return b - a;
            });
            valueList.pop();
        }
        const values = _.map(valueList, (item) => {
            let name;
            let value;
            if (item instanceof Array) {
                name = item[0];
                value = item[0];
            } else {
                name = item.toString();
                value = item.toString();
            }
            return {
                n: name, v: value,
            };
        });
        values.unshift({
            n: '全部', v: '',
        });
        return {
            key: key, name: name, init: '', value: values,
        };
    }

    async getFilter($) {
        const json = $('#__NEXT_DATA__')[0].children[0].data;
        const obj = JSON.parse(json).props["pageProps"]["filterCondition"];
        const label = this.convertTypeData(obj, 'label', '类型');
        const country = this.convertTypeData(obj, 'country', '地区');
        const time = this.convertTypeData(obj, 'time', '年份');
        return [label, country, time];
    }

    async setFilterObj() {
        for (const type_dic of this.classes.slice(1, 5)) {
            let type_id = type_dic["type_id"]
            if (type_id !== "最近更新") {
                let url = this.siteUrl + `${type_id}/all/all/all`
                let $ = await this.getHtml(url)
                this.filterObj[type_id] = await this.getFilter($)
            }
        }
    }

    parseVodShortFromtJson(obj) {
        let vodShort = new VodShort()
        vodShort.vod_id = obj["id"]
        vodShort.vod_name = obj["name"]
        vodShort.vod_pic = obj["img"]
        if (_.isEmpty(vodShort.vod_pic)) {
            vodShort.vod_pic = obj["picurl"] ?? ""
        }
        vodShort.vod_remarks = obj["countStr"]
        if (_.isEmpty(vodShort.vod_remarks)) {
            vodShort.vod_remarks = obj["time"]
        }
        return vodShort
    }

    async parseVodShortListFromJson(obj) {
        let vod_list = []
        for (const results of obj) {
            let name = results["name"]
            if (name !== "电视直播") {
                let cards = results["cards"]
                for (const result of cards) {
                    let vodShort = this.parseVodShortFromtJson(result)
                    vod_list.push(vodShort)
                }
            }
        }
        return vod_list
    }

    async parseVodShortListFromJsonByCategory(obj) {
        let vod_list = []
        for (const result of obj.list) {
            let vodShort = this.parseVodShortFromtJson(result)
            vod_list.push(vodShort)
        }
        return vod_list
    }

    getObjectValues(objList,key){
        let value_list = []
        for (const result  of objList){
            value_list.push(result[key])
        }
        return value_list
    }

    async parseVodDetailfromJson(obj) {
        const vObj = obj["collectionInfo"];
        let vodDetail = new VodDetail();
        vodDetail.vod_name = vObj["name"]
        vodDetail.type_name = vObj["chname"]
        vodDetail.vod_pic = vObj["picurl"]
        vodDetail.vod_area = vObj["country"]
        vodDetail.vod_remarks = vObj["countStr"]
        vodDetail.vod_actor =  this.getObjectValues(vObj["actor"],"name").join("/")
        vodDetail.vod_director = this.getObjectValues(vObj["director"],"name").join("/")
        vodDetail.vod_content = vObj["desc"]
        const playInfo = vObj["videosGroup"];
        const playVod = {};
        _.each(playInfo, (info) => {
            const sourceName = info.name;
            let playList = '';
            const videoInfo = info["videos"];
            const vodItems = _.map(videoInfo, (epObj) => {
                const epName = "第" + epObj["eporder"] + "集";
                const playUrl = epObj["purl"]
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
        let json = await this.fetch(this.apiUrl + "/v3/web/api/home?chName=首页", null, this.getApiHeader())
        const obj = JSON.parse(json)["data"]["cardsGroup"];
        this.homeVodList = await this.parseVodShortListFromJson(obj)
    }

    getClassChName(tid) {
        for (const class_dic of this.classes) {
            if (tid === class_dic["type_id"]) {
                return class_dic["type_name"]
            }
        }
    }

    async setCategory(tid, pg, filter, extend) {
        this.limit = 16;
        const param = {
            chName: this.getClassChName(tid), page: parseInt(pg), pageSize: this.limit
        };
        if (extend["label"] !== undefined) {
            param["label"] = extend["label"]
        }
        if (extend["country"] !== undefined) {
            param["country"] = extend["country"]
        }
        if (extend["time"] !== undefined) {
            const year = parseInt(extend["time"]);
            param["startTime"] = year;
            param["endTime"] = year;
        }
        const json = await this.post(this.apiUrl + '/v3/web/api/filter', JSON.stringify(param), {
            'User-Agent': Utils.MOBILEUA, "Content-Type": 'application/json'
        }, "")
        const data = JSON.parse(json).data;
        this.vodList = await this.parseVodShortListFromJsonByCategory(data)
        this.count = Math.floor(data["total"] / this.limit);
        this.total = data.total

    }

    async setDetail(id) {

        const $ = await this.getHtml(this.siteUrl + '/vod/detail/' + id);
        const json = $('#__NEXT_DATA__')[0].children[0].data;
        const obj = JSON.parse(json).props["pageProps"];
        this.vodDetail = await this.parseVodDetailfromJson(obj)
    }

    async setSearch(wd, quick) {
        const limit = 20;
        const param = {
            word: wd, page: 1, pageSize: limit,
        };
        const json = await this.post(this.apiUrl + '/v3/web/api/search', JSON.stringify(param), this.getApiHeader(), "");
        const data = JSON.parse(json).data;
        this.vodList = await this.parseVodShortListFromJsonByCategory(data)
    }

}

let spider = new StarSpider()

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