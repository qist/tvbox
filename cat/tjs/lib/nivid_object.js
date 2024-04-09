/*
* @File     : nivid_object.js
* @Author   : jade
* @Date     : 2023/12/20 9:50
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/
import {Crypto} from "./cat.js";

let DesKey = "diao.com"

class ChannelResponse {
    // classes
    constructor() {
        this.channelMsg = ""
        this.channelStatus = 0
        this.channelList = []
        this.channelFilters = {}
    }

    fromJsonString(json_str, remove18ChannelCode = 0) {
        let json_dic = JSON.parse(json_str)
        this.channelMsg = json_dic.msg
        this.channelStatus = json_dic.status
        let channel_list = []
        for (const channel_info of json_dic.list) {
            let new_channel_info = new ChannelInfo()
            switch (remove18ChannelCode) {
                case 0:
                    new_channel_info.fromJson(channel_info)
                    channel_list.push(new_channel_info)
                    break
                case 1:
                    if (channel_info.channelName !== "午夜场" && channel_info.channelName !== "午夜直播") {
                        new_channel_info.fromJson(channel_info)
                        channel_list.push(new_channel_info)
                    }
                    break
                case 2:
                    if (channel_info.channelName === "午夜场" || channel_info.channelName === "午夜直播") {
                        new_channel_info.fromJson(channel_info)
                        channel_list.push(new_channel_info)
                    }
                    break
            }
        }
        this.channelList = channel_list
        this.channelFilters = json_dic.filter
    }

    setChannelFilters(filter_str) {
        this.channelFilters = JSON.parse(filter_str)
    }

    getValues(typeList, name_key, id_key) {
        let values = []
        values.push({"n": "全部", "v": "0"})
        for (const obj of typeList) {
            values.push({"n": obj[name_key], "v": obj[id_key].toString()})
        }
        return values
    }

    getFilters() {
        let filters = {}
        for (const channel_info of this.channelList) {
            filters[channel_info.channelId] = []
            let sortMapList = this.channelFilters["sortsMap"][parseInt(channel_info.channelId)]
            let sortValues = this.getValues(sortMapList, "title", "id")
            filters[channel_info.channelId].push({"key": "1", "name": "排序", "value": sortValues})
            let typeMapList = this.channelFilters["typesMap"][parseInt(channel_info.channelId)]
            let typeValues = this.getValues(typeMapList, "showTypeName", "showTypeId")
            filters[channel_info.channelId].push({"key": "2", "name": "类型", "value": typeValues})
            let areaValues = this.getValues(this.channelFilters["regions"], "regionName", "regionId")
            filters[channel_info.channelId].push({"key": "3", "name": "地区", "value": areaValues})
            let langValues = this.getValues(this.channelFilters["langs"], "langName", "langId")
            filters[channel_info.channelId].push({"key": "4", "name": "语言", "value": langValues})
            let yearValues = this.getValues(this.channelFilters["yearRanges"], "name", "code")
            filters[channel_info.channelId].push({"key": "5", "name": "年份", "value": yearValues})
        }
        return filters
    }

    getChannelFilters() {
        return this.channelFilters
    }



    getChannelMsg() {
        return this.channelMsg
    }

    getChannelStatus() {
        return this.channelStatus
    }

    getChannelList() {
        return this.channelList
    }

    getClassList() {
        let classes = []
        for (const channel_info of this.channelList) {
            classes.push({"type_id": channel_info.channelId, "type_name": channel_info.channelName})
        }
        return classes
    }


    async save() {
        await local.set("niba", "niba_channel", this.toString());
        return this;
    }

    clear() {
        this.channelMsg = ""
        this.channelStatus = 0
        this.channelList = []
    }

    async clearCache() {
        this.clear()
        await local.set("niba", "niba_channel", "{}");
    }

    toString() {
        const params = {
            msg: this.getChannelMsg(),
            status: this.getChannelStatus(),
            list: this.getChannelList(),
            filter: this.getChannelFilters()
        };
        return JSON.stringify(params);
    }
}

async function getChannelCache() {
    return await local.get("niba", "niba_channel");
}

class ChannelInfo {
    constructor() {
        this.channelId = 0
        this.channelName = ""
    }

    fromJsonString(json_str) {
        let json_dic = JSON.parse(json_str)
        this.channelId = json_dic.channelId
        this.channelName = json_dic.channelName
    }

    fromJson(json) {
        this.channelId = json.channelId
        this.channelName = json.channelName
    }

    getChannelName() {
        return this.channelName
    }

    getChannelId() {
        return this.channelId
    }
}

function isNumeric(str) {
    return !isNaN(parseInt(str));
}

function getVod(video_dic_list, play_foramt_list, showIdCode) {
    let episode_list = [], episode_str_list = [];
    for (const video_dic of video_dic_list) {
        let video_name = ""
        if (isNumeric((video_dic['episodeName']))) {
            video_name = "第" + video_dic["episodeName"] + "集"
        } else {
            video_name = video_dic["episodeName"]
        }
        episode_list.push(video_name + "$" + video_dic["playIdCode"] + "@" + showIdCode);
    }

    for (let index = 0; index < play_foramt_list.length; index++) {
        episode_str_list.push(episode_list.join("#"));
    }
    return {
        vod_play_url: episode_str_list.join("$$$"),
        vod_play_from: play_foramt_list.map(item => item).join("$$$"),
    };
}

function getHeader() {
    return {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Referer": "https://m.nivod.tv/",
        "Content-Type": "application/x-www-form-urlencoded"
    }
}


function md5(text) {
    return Crypto.MD5(text).toString()
}

//加密
async function createSign(body = null) {
    let params = {
        "_ts": Date.now(), "app_version": "1.0",
        "platform": "3", "market_id": "web_nivod",
        "device_code": "web", "versioncode": 1,
        "oid": "8ca275aa5e12ba504b266d4c70d95d77a0c2eac5726198ea"
    }
    /**
     * __QUERY::_ts=1702973558399&app_version=1.0&device_code=web&market_id=web_nivod&oid=8ca275aa5e12ba504b266d4c70d95d77a0c2eac5726198ea&platform=3&versioncode=1&__BODY::__KEY::2x_Give_it_a_shot
     */
    let params_list = []
    for (const key of Object.keys(params).sort()) {
        params_list.push(`${key}=${params[key]}`)
    }
    let body_str = "&__BODY::"
    if (body !== null) {
        let body_list = []
        for (const key of Object.keys(body).sort()) {
            body_list.push(`${key}=${body[key]}`)
        }
        body_str = body_str + body_list.join("&") + "&"
    }


    let params_str = "__QUERY::" + params_list.join("&") + body_str + "__KEY::2x_Give_it_a_shot"
    let sign_code = md5(params_str)
    params_list.push(`sign=${sign_code}`)
    return "?" + params_list.join("&")

}

//解密
function desDecrypt(content) {
    // 定义密钥
    const key = Crypto.enc.Utf8.parse(DesKey); // 密钥需要进行字节数转换
    /*
    const encrypted = Crypto.DES.encrypt(content, key, {
        mode: Crypto.mode.ECB, // 使用ECB模式
        padding: Crypto.pad.Pkcs7, // 使用Pkcs7填充
    }).ciphertext.toString();
     */
    return Crypto.DES.decrypt({ciphertext: Crypto.enc.Hex.parse(content)}, key, {
        mode: Crypto.mode.ECB,
        padding: Crypto.pad.Pkcs7,
    }).toString(Crypto.enc.Utf8);
}

export {getChannelCache, desDecrypt, createSign, ChannelResponse, getHeader, getVod};