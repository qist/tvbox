/*
* @File     : haiwaikan.js
* @Author   : jade
* @Date     : 2024/04/02 9:15
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 海外看
*/
import {VodSpider} from "./vodSpider.js";
class HaiWaiKanSpider extends VodSpider {
    constructor() {
        super();
        this.siteUrl = "https://haiwaikan.com"
        this.remove18 = true
        this.type_id_18 = 0
    }

    async spiderInit(inReq) {
       await super.spiderInit(inReq);
    }



    async init(cfg) {
        await super.init(cfg);
        await this.spiderInit(null)

    }

    getAppName() {
        return "海外看"
    }

    getName() {
        return "☕┃海外看┃☕墙"
    }

    getJSName() {
        return "haiwaikan"
    }

    getType() {
        return 3
    }

    async setClasses() {
        let content = await this.fetch(this.siteUrl + "/api.php/provide/vod/from", {"ac": "list"}, this.getHeader())
        let content_json = JSON.parse(content)
        for (const class_dic of content_json["class"]) {
            if (class_dic["type_id"] < 26 ) {
                this.classes.push(this.getTypeDic(class_dic["type_name"], class_dic["type_id"].toString()))
            }
        }
        this.content_json = content_json
    }

    async getFilter(type_id,obj) {
        let extend_list = []
        let extend_dic = {"key": "1", "name": "全部类别", "value": [{"n":"全部类别","v":type_id.toString()}]}
        for (const  type_dic of obj["class"]){
            let a_type_id = type_dic["type_id"]
            let max_type_id = 0
            let min_type_id = 0
            if (type_id === 20){
                max_type_id = 50
                min_type_id = 27
            }
            if (type_id === 21){
                max_type_id = 128
                min_type_id = 100
            }
            if (type_id === 22){
                max_type_id = 143
                min_type_id = 134
            }
            if (type_id === 23){
                max_type_id = 135
                min_type_id = 127
            }
            if (a_type_id < max_type_id && a_type_id > min_type_id){
                  extend_dic["value"].push({"n":type_dic["type_name"],"v":a_type_id.toString()})
            }
        }
        if (extend_dic["value"].length > 1){
              extend_list.push(extend_dic)
            return extend_list
        }else{
            return null
        }

    }

    async setFilterObj() {
        let content = await this.fetch(this.siteUrl + "/api.php/provide/vod/from", {"ac": "list"}, this.getHeader())
        let content_json = JSON.parse(content)
        for (const type_dic of this.classes){
            let type_id = type_dic["type_id"]
            if (type_id !== "最近更新"){
                let extend_list =  await this.getFilter(parseInt(type_id),content_json)
                if (extend_list !== null){
                    this.filterObj[type_id] = extend_list
                }
            }
        }
    }


}

let spider = new HaiWaiKanSpider()

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
