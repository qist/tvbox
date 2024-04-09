/*
 * @Author: samples jadehh@live.com
 * @Date: 2023-12-14 11:03:04
 * @LastEditors: samples jadehh@live.com
 * @LastEditTime: 2023-12-14 11:03:04
 * @FilePath: /lib/ali_object.js
 * @Description: 阿里云盘基础类
 */
import {_} from "./cat.js";

const UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
const CLIENT_ID = "76917ccccd4441c39457a04f6084fb2f";
import * as Utils from "./utils.js";
// 引用会导致出错
// import qs from "qs";
// import axios from "axios";
// import https from "https";

function getHeader() {
    const params = {};
    params["User-Agent"] = UA;
    params.Referer = "https://www.aliyundrive.com/";
    return params;
}

class User {
    constructor() {
        this.driveId = "";
        this.userId = "";
        this.tokenType = "";
        this.accessToken = "";
        this.refreshToken = "";
    }

    static objectFrom(json_str) {
        if (_.isEmpty(json_str)) {
            return new User();
        }

        let resonse = JSON.parse(json_str), user = new User();
        user.driveId = resonse.default_drive_id;
        user.userId = resonse.user_id;
        user.tokenType = resonse.token_type;
        user.accessToken = resonse.access_token;
        user.refreshToken = resonse.refresh_token; // 刷新Token记录原有的Token
        return user;
    }

    getDriveId() {
        return _.isEmpty(this.driveId) ? "" : this.driveId;
    }

    getUserId() {
        return _.isEmpty(this.userId) ? "" : this.userId;
    }

    getTokenType() {
        return _.isEmpty(this.tokenType) ? "" : this.tokenType;
    }

    getAccessToken() {
        return _.isEmpty(this.accessToken) ? "" : this.accessToken;
    }

    getRefreshToken() {
        return _.isEmpty(this.refreshToken) ? "" : this.refreshToken;
    }

    setRefreshToken(refresh_token) {
        this.refreshToken = refresh_token
    }

    getAuthorization() {
        return this.getTokenType() + " " + this.getAccessToken();
    }

    isAuthed() {
        return this.getTokenType().length > 0 && this.getAccessToken().length > 0;
    }

    clean() {
        this.refreshToken = "";
        this.accessToken = "";
        return this;
    }

    async save() {
        await local.set("ali", "aliyundrive_user", this.toString());


        return this;
    }

    toString() {
        return JSON.stringify(this.toDict());
    }

    toDict() {
        return {
            default_drive_id: this.getDriveId(),
            user_id: this.getUserId(),
            token_type: this.getTokenType(),
            access_token: this.getAccessToken(),
            refresh_token: this.getRefreshToken()
        };

    }

}

class OAuth {
    constructor() {
        this.tokenType = "";
        this.accessToken = "";
        this.refreshToken = "";
    }

    static objectFrom(json_str) {
        if (_.isEmpty(json_str)) {
            return new OAuth();
        }
        let oauth_json = JSON.parse(json_str), oAuth = new OAuth();
        oAuth.tokenType = oauth_json.token_type;
        oAuth.accessToken = oauth_json.access_token;
        oAuth.refreshToken = oauth_json.refresh_token;
        return oAuth;
    }

    getTokenType() {
        return _.isEmpty(this.tokenType) ? "" : this.tokenType;
    }

    getAccessToken() {
        return _.isEmpty(this.accessToken) ? "" : this.accessToken;
    }

    getRefreshToken() {
        return _.isEmpty(this.refreshToken) ? "" : this.refreshToken;
    }

    getAuthorization() {
        return this.getTokenType() + " " + this.getAccessToken();
    }

    clean() {
        this.refreshToken = "";
        this.accessToken = "";
        return this;
    }

    async save() {
        await local.set("ali", "aliyundrive_oauth", this.toString());

        return this;
    }

    toString() {
        return JSON.stringify(this.toDict());
    }

    toDict() {
        return {
            token_type: this.getTokenType(), access_token: this.getAccessToken(), refresh_token: this.getRefreshToken()
        };
    }
}

class Drive {
    constructor() {
        this.defaultDriveId = "";
        this.resourceDriveId = "";
        this.backupDriveId = "";
    }

    static objectFrom(json_str) {
        if (_.isEmpty(json_str)) {
            return new Drive();
        }
        let obj = JSON.parse(json_str), drive = new Drive();
        drive.defaultDriveId = obj.default_drive_id;
        drive.resourceDriveId = obj.resource_drive_id;
        drive.backupDriveId = obj.backup_drive_id;
        return drive;
    }

    getDefaultDriveId() {
        return _.isEmpty(this.defaultDriveId) ? "" : this.defaultDriveId;
    }

    getResourceDriveId() {
        return _.isEmpty(this.resourceDriveId) ? "" : this.resourceDriveId;
    }

    getBackupDriveId() {
        return _.isEmpty(this.backupDriveId) ? "" : this.backupDriveId;
    }

    clean() {
        this.defaultDriveId = "";
        this.backupDriveId = "";
        this.resourceDriveId = "";
        return this;
    }

    async save() {
        await local.set("ali", "aliyundrive_drive", this.toString());
        return this;
    }

    toString() {
        const params = {
            default_drive_id: this.getDefaultDriveId(),
            resource_drive_id: this.getResourceDriveId(),
            backup_drive_id: this.getBackupDriveId()
        };
        return JSON.stringify(params);
    }

}

class Code {
    constructor() {
        this.redirectUri = "";
    }

    static objectFrom(json_str) {
        if (_.isEmpty(json_str)) {
            return new Code();
        }
        let code_json = JSON.parse(json_str), code = new Code();
        code.redirectUri = code_json.redirectUri;
        return code;
    }

    getRedirectUri() {
        return _.isEmpty(this.redirectUri) ? "" : this.redirectUri;
    }

    getCode() {
        return this.getRedirectUri().split("code=")[1];
    }
}

class Item {
    constructor(file_id) {
        this.items = [];
        this.nextMarker = "";
        this.fileId = file_id;
        this.shareId = "";
        this.name = "";
        this.type = "";
        this.fileExtension = "";
        this.category = "";
        this.size = "";
        this.parent = "";
        this.shareToken = ""
    }

    static objectFrom(json_str, shareToken) {
        if (_.isEmpty(json_str)) {
            return new Item();
        }

        let item_json = JSON.parse(json_str), item = new Item();

        item.nextMarker = typeof item_json.next_marker == "undefined" ? "" : item_json.next_marker;
        item.fileId = typeof item_json.file_id == "undefined" ? "" : item_json.file_id;
        item.shareId = typeof item_json.share_id == "undefined" ? "" : item_json.share_id;
        item.shareToken = shareToken
        item.name = typeof item_json.name == "undefined" ? "" : item_json.name;
        item.type = typeof item_json.type == "undefined" ? "" : item_json.type;
        item.fileExtension = typeof item_json.file_extension == "undefined" ? "" : item_json.file_extension;
        item.category = typeof item_json.category == "undefined" ? "" : item_json.category;
        item.size = typeof item_json.size == "undefined" ? "" : item_json.size;
        item.parent = typeof item_json.parent_file_id == "undefined" ? "" : item_json.parent_file_id;
        typeof item.items != "undefined" && Array.isArray(item_json.items) && !_.isEmpty(item_json.items) && item_json.items.forEach(function (x) {
            let new_item = Item.objectFrom(JSON.stringify((x)), shareToken)
            item.items.push(new_item);
        });
        return item;
    }

    getItems() {
        return _.isEmpty(this.items) ? [] : this.items;
    }

    getNextMarker() {
        return _.isEmpty(this.nextMarker) ? "" : this.nextMarker;
    }

    getFileId() {
        return _.isEmpty(this.fileId) ? "" : this.fileId;
    }

    getShareId() {
        return _.isEmpty(this.shareId) ? "" : this.shareId;
    }

    getFileExtension() {
        return _.isEmpty(this.fileExtension) ? "" : this.fileExtension;
    }

    getName() {
        return _.isEmpty(this.name) ? "" : this.name;
    }

    getType() {
        return _.isEmpty(this.type) ? "" : this.type;
    }

    getExt() {
        return _.isEmpty(this.fileExtension) ? "" : this.fileExtension;
    }

    getCategory() {
        return _.isEmpty(this.category) ? "" : this.category;
    }

    getSize() {
        return this.size === 0 ? "" : "[" + Utils.getSize(this.size) + "]";
    }

    getParent() {
        return _.isEmpty(this.parent) ? "" : "[" + this.parent + "]";
    }

    parentFunc(item) {
        this.parent = item;
        return this;
    }

    // getDisplayName() {
    //     return this.getParent() + " " + this.getName() + " " + this.getSize();
    // }

    getDisplayName(type_name) {
        let name = this.getName();
        name = name.replaceAll("玩偶哥 q 频道：【神秘的哥哥们】", "")
        if (type_name === "电视剧") {
            let replaceNameList = ["4k", "4K"]
            name = name.replaceAll("." + this.getFileExtension(), "")
            name = name.replaceAll(" ", "").replaceAll(" ", "")
            for (const replaceName of replaceNameList) {
                name = name.replaceAll(replaceName, "")
            }
            name = Utils.getStrByRegexDefault(/\.S01E(.*?)\./, name)
            const numbers = name.match(/\d+/g);
            if (numbers.length > 0) {
                name = numbers[0]
            }
        }
        return name + " " + this.getParent() + " " + this.getSize();
    }

}

class Sub {
    constructor() {
        this.url = "";
        this.name = "";
        this.lang = "";
        this.format = "";
    }

    static create() {
        return new Sub();
    }

    setName(name) {
        this.name = name;
        return this;
    }

    setUrl(url) {
        this.url = url;
        return this;
    }

    setLang(lang) {
        this.lang = lang;
        return this;
    }

    setFormat(format) {
        this.format = format;
        return this;
    }

    setExt(ext) {
        switch (ext) {
            case "vtt":
                return this.setFormat("text/vtt");
            case "ass":
            case "ssa":
                return this.setFormat("text/x-ssa");
            default:
                return this.setFormat("application/x-subrip");
        }
    }

}


async function getUserCache() {
    return await local.get("ali", "aliyundrive_user");
}

async function getOAuthCache() {
    return await local.get("ali", "aliyundrive_oauth");
}

function getShareId(share_url) {
    let patternAli = /https:\/\/www\.alipan\.com\/s\/([^\\/]+)(\/folder\/([^\\/]+))?|https:\/\/www\.aliyundrive\.com\/s\/([^\\/]+)(\/folder\/([^\\/]+))?/
    let matches = patternAli.exec(share_url)
    const filteredArr = matches.filter(item => item !== undefined);
    if (filteredArr.length > 1) {
        return matches[1]
    } else {
        return ""
    }
}

async function ali_request(url, opt) {

    let resp;
    let data;
    try {
        data = opt ? opt.data || null : null;
        const postType = opt ? opt.postType || null : null;
        const returnBuffer = opt ? opt.buffer || 0 : 0;
        const timeout = opt ? opt.timeout || 5000 : 5000;

        const headers = opt ? opt.headers || {} : {};
        if (postType === 'form') {
            headers['Content-Type'] = 'application/x-www-form-urlencoded';

            if (data != null) {
                data = qs.stringify(data, {encode: false});
            }
        }
        let respType = returnBuffer === 1 || returnBuffer === 2 ? 'arraybuffer' : undefined;
        resp = await axios(url, {
            responseType: respType,
            method: opt ? opt.method || 'get' : 'get',
            headers: headers,
            data: data,
            timeout: timeout,
            httpsAgent: https.Agent({
                rejectUnauthorized: false,
            }),
        });
        data = resp.data;

        const resHeader = {};
        for (const hks of resp.headers) {
            const v = hks[1];
            resHeader[hks[0]] = Array.isArray(v) ? (v.length === 1 ? v[0] : v) : v;
        }

        if (!returnBuffer) {
            if (typeof data === 'object') {
                data = JSON.stringify(data);
            }
        } else if (returnBuffer === 1) {
            return {code: resp.status, headers: resHeader, content: data};
        } else if (returnBuffer === 2) {
            return {code: resp.status, headers: resHeader, content: data.toString('base64')};
        }
        return {code: resp.status, headers: resHeader, content: data};
    } catch (error) {
        // await Utils.log(`请求失败,URL为:${url},失败原因为:${error}`)
        resp = error.response
        try {
            return {code: resp.status, headers: resp.headers, content: JSON.stringify(resp.data)};
        } catch (err) {
            return {headers: {}, content: ''};
        }
    }
}

async function post(url, params) {
    url = url.startsWith("https") ? url : "https://api.aliyundrive.com/" + url;
    let response = await postJson(url, params, getHeader());
    return response.content;
}

async function postJson(url, params, headers) {
    params["Content-Type"] = "application/json";
    return await req(url, {
        headers: headers, method: "post", data: params
    });
}


export {
    UA,
    CLIENT_ID,
    OAuth,
    Code,
    Sub,
    User,
    Item,
    Drive,
    getHeader,
    getShareId,
    getOAuthCache,
    getUserCache,
    post,
    postJson
};