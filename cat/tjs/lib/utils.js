/*
* @File     : utils.js
* @Author   : jade
* @Date     : 2024/1/25 15:01
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/
import {Crypto} from "./cat.js";
import {TextDecoder} from "./TextDecoder.js";
// import {TextDecoder} from "text-decoding";

let CHROME = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36";
const MOBILEUA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1';
let RESOURCEURL = "https://gh.con.sh/https://raw.githubusercontent.com/jadehh/TV/js"

function isSub(ext) {
    return ext === "srt" || ext === "ass" || ext === "ssa";
}

function isNumeric(str) {
    return !isNaN(parseInt(str));
}

function getSize(size) {
    if (size <= 0) return "";
    if (size > 1024 * 1024 * 1024 * 1024.0) {
        size /= (1024 * 1024 * 1024 * 1024.0);
        return size.toFixed(2) + "TB";
    } else if (size > 1024 * 1024 * 1024.0) {
        size /= (1024 * 1024 * 1024.0);
        return size.toFixed(2) + "GB";
    } else if (size > 1024 * 1024.0) {
        size /= (1024 * 1024.0);
        return size.toFixed(2) + "MB";
    } else {
        size /= 1024.0;
        return size.toFixed(2) + "KB";
    }
}

function removeExt(text) {
    return text.indexOf('.') > -1 ? text.substring(0, text.lastIndexOf(".")) : text;
}

async function log(str) {
    console.debug(str);
}

function isVideoFormat(url) {
    var RULE = /http((?!http).){12,}?\.(m3u8|mp4|flv|avi|mkv|rm|wmv|mpg|m4a|mp3)\?.*|http((?!http).){12,}\.(m3u8|mp4|flv|avi|mkv|rm|wmv|mpg|m4a|mp3)|http((?!http).)*?video\/tos*/;
    if (url.indexOf("url=http") > -1 || url.indexOf(".js") > -1 || url.indexOf(".css") > -1 || url.indexOf(".html") > -1) {
        return false;
    }
    return RULE.test(url);
}

function jsonParse(input, json) {
    var jsonPlayData = JSON.parse(json);
    var url = jsonPlayData.url;
    if (url.startsWith("//")) {
        url = "https:" + url;
    }
    if (!url.startsWith("http")) {
        return null;
    }
    if (url === input) {
        if (!isVideoFormat(url)) {
            return null;
        }
    }
    var headers = {};
    var ua = jsonPlayData["user-agent"] || "";
    if (ua.trim().length > 0) {
        headers["User-Agent"] = " " + ua;
    }
    var referer = jsonPlayData.referer || "";
    if (referer.trim().length > 0) {
        headers["Referer"] = " " + referer;
    }
    var taskResult = {
        header: headers, url: url
    };
    return taskResult;
}

function debug(obj) {
    for (var a in obj) {
        if (typeof (obj[a]) == "object") {
            debug(obj[a]); //递归遍历
        } else {
            console.debug(a + "=" + obj[a]);
        }
    }
}

function objectToStr(params = null, isBase64Encode = false) {
    let params_str_list = []
    if (params !== null) {
        for (const key of Object.keys(params)) {
            if (isBase64Encode) {
                params_str_list.push(`${key}=${encodeURIComponent(params[key])}`)
            } else {
                params_str_list.push(`${key}=${params[key]}`)
            }

        }
    }

    return params_str_list.join("&")
}

function sleep(delay) {
    const start = (new Date()).getTime();
    while ((new Date()).getTime() - start < delay * 1000) {
        continue;
    }
}

function getStrByRegex(pattern, str) {
    let matcher = pattern.exec(str);
    if (matcher !== null) {
        if (matcher.length >= 1) {
            if (matcher.length >= 1) return matcher[1]
        }
    }
    return "";
}

function getStrByRegexDefault(pattern, str) {
    let matcher = pattern.exec(str);
    if (matcher !== null) {
        if (matcher.length >= 1) {
            if (matcher.length >= 1) return matcher[1]
        }
    }
    return str;
}

function base64Encode(text) {
    return Crypto.enc.Base64.stringify(Crypto.enc.Utf8.parse(text));
}

function base64Decode(text) {
    return Crypto.enc.Utf8.stringify(Crypto.enc.Base64.parse(text));
}

function unescape(code) {
    return code.replace(/\\('|\\)/g, "$1").replace(/[\r\t\n]/g, " ");
}

function decode(buffer, encode_type) {
    let decoder = new TextDecoder(encode_type)
    return decoder.decode(buffer)
}

function getHost(url) {
    let url_list = url.split("/")
    return url_list[0] + "//" + url_list[2]
}

function unquote(str) {
    return str.replace(/^"(.*)"$/, '$1');
}

function md5Encode(text) {
    return Crypto.MD5(Crypto.enc.Utf8.parse(text)).toString();
}


function getUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        let r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    }) + "-" + new Date().getTime().toString(16)

}

function objToList(list, key, split_value = "*") {
    let value_list = []
    for (const dic of list) {
        value_list.push(dic[key])
    }
    return value_list.join(split_value)
}

function getPropertiesAndMethods(obj) {
    let str = ""
    for (let key in obj) {
        if (typeof obj[key] === 'function') {
            str = str + "方法名:" + key + '()' + "\n";
        } else {
            str = str + "属性名:"+(key + ': ' + obj[key]) + "\n";
        }
    }
    return str
}

let patternAli = /(https:\/\/www\.aliyundrive\.com\/s\/[^"]+|https:\/\/www\.alipan\.com\/s\/[^"]+)/

export {
    isSub,
    getSize,
    removeExt,
    log,
    isVideoFormat,
    jsonParse,
    debug,
    CHROME,
    objectToStr,
    sleep,
    getStrByRegex,
    RESOURCEURL,
    base64Encode,
    base64Decode,
    patternAli,
    unescape,
    decode,
    MOBILEUA,
    isNumeric,
    getHost,
    unquote,
    md5Encode,
    getStrByRegexDefault,
    getUUID,
    objToList,
    getPropertiesAndMethods
};