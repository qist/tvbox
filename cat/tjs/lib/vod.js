// LocalAddress = "http://192.168.29.156:8099"
import * as Utils from "./utils.js";

export class VodShort {
    constructor() {
        this.vod_id = ""        //id
        this.vod_name = ""      //名称
        this.vod_pic = Utils.RESOURCEURL + "/resources/ali.jpg"   //图片
        this.vod_remarks = ""  //备注
    }

    to_dict() {
        return JSON.stringify(this);
    }

    load_dic(json_str) {
        let obj = JSON.parse(json_str)
        for (let propName in obj) {
            this[propName] = obj[propName];
        }

    }

    load_data(data) {
        for (let propName in JSON.parse(this.to_dict())) {
            this[propName] = data[propName];
        }
    }

}

export class VodDetail extends VodShort {
    constructor() {
        super();
        this.type_name = ""      // 类别
        this.vod_year = ""      // 年份
        this.vod_area = ""      // 地区
        this.vod_actor = ""     // 导演
        this.vod_director = ""      // 演员
        this.vod_content = ""  // 剧情
        this.vod_play_from = ""  // 播放格式
        this.vod_play_url = ""  // 播放连接
    }

    to_short() {
        let vodShort = new VodShort()
        vodShort.load_dic(this.to_dict())
        return vodShort
    }

    load_dic(json_str) {
        let obj = JSON.parse(json_str)
        for (let propName in JSON.parse(this.to_dict())) {
            this[propName] = obj[propName];
        }
    }


}



