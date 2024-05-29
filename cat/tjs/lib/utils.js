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
import {TextEncoder} from "./TextEncoder.js";
// import {TextDecoder} from "text-decoding";
const deviceBrands = ['Huawei', 'Xiaomi'];
const deviceModels = [
    ['MHA-AL00', 'HUAWEI Mate 9', 'MHA-TL00', 'HUAWEI Mate 9', 'LON-AL00', 'HUAWEI Mate 9 Pro', 'ALP-AL00', 'HUAWEI Mate 10', 'ALP-TL00', 'HUAWEI Mate 10', 'BLA-AL00', 'HUAWEI Mate 10 Pro', 'BLA-TL00', 'HUAWEI Mate 10 Pro', 'HMA-AL00', 'HUAWEI Mate 20', 'HMA-TL00', 'HUAWEI Mate 20', 'LYA-AL00', 'HUAWEI Mate 20 Pro', 'LYA-AL10', 'HUAWEI Mate 20 Pro', 'LYA-TL00', 'HUAWEI Mate 20 Pro', 'EVR-AL00', 'HUAWEI Mate 20 X', 'EVR-TL00', 'HUAWEI Mate 20 X', 'EVR-AN00', 'HUAWEI Mate 20 X', 'TAS-AL00', 'HUAWEI Mate 30', 'TAS-TL00', 'HUAWEI Mate 30', 'TAS-AN00', 'HUAWEI Mate 30', 'TAS-TN00', 'HUAWEI Mate 30', 'LIO-AL00', 'HUAWEI Mate 30 Pro', 'LIO-TL00', 'HUAWEI Mate 30 Pro', 'LIO-AN00', 'HUAWEI Mate 30 Pro', 'LIO-TN00', 'HUAWEI Mate 30 Pro', 'LIO-AN00m', 'HUAWEI Mate 30E Pro', 'OCE-AN10', 'HUAWEI Mate 40', 'OCE-AN50', 'HUAWEI Mate 40E', 'OCE-AL50', 'HUAWEI Mate 40E', 'NOH-AN00', 'HUAWEI Mate 40 Pro', 'NOH-AN01', 'HUAWEI Mate 40 Pro', 'NOH-AL00', 'HUAWEI Mate 40 Pro', 'NOH-AL10', 'HUAWEI Mate 40 Pro', 'NOH-AN50', 'HUAWEI Mate 40E Pro', 'NOP-AN00', 'HUAWEI Mate 40 Pro', 'CET-AL00', 'HUAWEI Mate 50', 'CET-AL60', 'HUAWEI Mate 50E', 'DCO-AL00', 'HUAWEI Mate 50 Pro', 'TAH-AN00', 'HUAWEI Mate X', 'TAH-AN00m', 'HUAWEI Mate Xs', 'TET-AN00', 'HUAWEI Mate X2', 'TET-AN10', 'HUAWEI Mate X2', 'TET-AN50', 'HUAWEI Mate X2', 'TET-AL00', 'HUAWEI Mate X2', 'PAL-AL00', 'HUAWEI Mate Xs 2', 'PAL-AL10', 'HUAWEI Mate Xs 2', 'EVA-AL00', 'HUAWEI P9', 'EVA-AL10', 'HUAWEI P9', 'EVA-TL00', 'HUAWEI P9', 'EVA-DL00', 'HUAWEI P9', 'EVA-CL00', 'HUAWEI P9', 'VIE-AL10', 'HUAWEI P9 Plus', 'VTR-AL00', 'HUAWEI P10', 'VTR-TL00', 'HUAWEI P10', 'VKY-AL00', 'HUAWEI P10 Plus', 'VKY-TL00', 'HUAWEI P10 Plus', 'EML-AL00', 'HUAWEI P20', 'EML-TL00', 'HUAWEI P20', 'CLT-AL00', 'HUAWEI P20 Pro', 'CLT-AL01', 'HUAWEI P20 Pro', 'CLT-AL00l', 'HUAWEI P20 Pro', 'CLT-TL00', 'HUAWEI P20 Pro', 'CLT-TL01', 'HUAWEI P20 Pro', 'ELE-AL00', 'HUAWEI P30', 'ELE-TL00', 'HUAWEI P30', 'VOG-AL00', 'HUAWEI P30 Pro', 'VOG-AL10', 'HUAWEI P30 Pro', 'VOG-TL00', 'HUAWEI P30 Pro', 'ANA-AL00', 'HUAWEI P40', 'ANA-AN00', 'HUAWEI P40', 'ANA-TN00', 'HUAWEI P40', 'ELS-AN00', 'HUAWEI P40 Pro', 'ELS-TN00', 'HUAWEI P40 Pro', 'ELS-AN10', 'HUAWEI P40 Pro', 'ELS-TN10', 'HUAWEI P40 Pro', 'ABR-AL00', 'HUAWEI P50', 'ABR-AL80', 'HUAWEI P50', 'ABR-AL60', 'HUAWEI P50E', 'ABR-AL90', 'HUAWEI P50E', 'JAD-AL00', 'HUAWEI P50 Pro', 'JAD-AL80', 'HUAWEI P50 Pro', 'JAD-AL50', 'HUAWEI P50 Pro', 'JAD-AL60', 'HUAWEI P50 Pro', 'BAL-AL00', 'HUAWEI P50 Pocket', 'BAL-AL60', 'HUAWEI Pocket S', 'PIC-AL00', 'HUAWEI nova 2', 'PIC-TL00', 'HUAWEI nova 2', 'BAC-AL00', 'HUAWEI nova 2 Plus', 'BAC-TL00', 'HUAWEI nova 2 Plus', 'HWI-AL00', 'HUAWEI nova 2s', 'HWI-TL00', 'HUAWEI nova 2s', 'ANE-AL00', 'HUAWEI nova 3e', 'ANE-TL00', 'HUAWEI nova 3e', 'PAR-AL00', 'HUAWEI nova 3', 'PAR-TL00', 'HUAWEI nova 3', 'INE-AL00', 'HUAWEI nova 3i', 'INE-TL00', 'HUAWEI nova 3i', 'VCE-AL00', 'HUAWEI nova 4', 'VCE-TL00', 'HUAWEI nova 4', 'MAR-AL00', 'HUAWEI nova 4e', 'MAR-TL00', 'HUAWEI nova 4e', 'SEA-AL00', 'HUAWEI nova 5', 'SEA-TL00', 'HUAWEI nova 5', 'SEA-AL10', 'HUAWEI nova 5 Pro', 'SEA-TL10', 'HUAWEI nova 5 Pro', 'GLK-AL00', 'HUAWEI nova 5i', 'GLK-TL00', 'HUAWEI nova 5i', 'GLK-LX1U', 'HUAWEI nova 5i', 'SPN-TL00', 'HUAWEI nova 5i Pro', 'SPN-AL00', 'HUAWEI nova 5z', 'WLZ-AL10', 'HUAWEI nova 6', 'WLZ-AN00', 'HUAWEI nova 6', 'JNY-AL10', 'HUAWEI nova 6 SE', 'JNY-TL10', 'HUAWEI nova 6 SE', 'JEF-AN00', 'HUAWEI nova 7', 'JEF-AN20', 'HUAWEI nova 7', 'JEF-TN00', 'HUAWEI nova 7', 'JEF-TN20', 'HUAWEI nova 7', 'JER-AN10', 'HUAWEI nova 7 Pro', 'JER-AN20', 'HUAWEI nova 7 Pro', 'JER-TN10', 'HUAWEI nova 7 Pro', 'JER-TN20', 'HUAWEI nova 7 Pro', 'CDY-AN00', 'HUAWEI nova 7 SE', 'CDY-AN20', 'HUAWEI nova 7 SE', 'CDY-TN00', 'HUAWEI nova 7 SE', 'CDY-TN20', 'HUAWEI nova 7 SE', 'ANG-AN00', 'HUAWEI nova 8', 'BRQ-AN00', 'HUAWEI nova 8 Pro', 'BRQ-AL00', 'HUAWEI nova 8 Pro', 'JSC-AN00', 'HUAWEI nova 8 SE', 'JSC-TN00', 'HUAWEI nova 8 SE', 'JSC-AL50', 'HUAWEI nova 8 SE', 'NAM-AL00', 'HUAWEI nova 9', 'RTE-AL00', 'HUAWEI nova 9 Pro', 'JLN-AL00', 'HUAWEI nova 9 SE', 'NCO-AL00', 'HUAWEI nova 10', 'GLA-AL00', 'HUAWEI nova 10 Pro', 'CHA-AL80', 'HUAWEI nova 10z'],
    ['M2001J2C', 'Xiaomi 10', 'M2001J2G', 'Xiaomi 10', 'M2001J2I', 'Xiaomi 10', 'M2011K2C', 'Xiaomi 11', 'M2011K2G', 'Xiaomi 11', '2201123C', 'Xiaomi 12', '2201123G', 'Xiaomi 12', '2112123AC', 'Xiaomi 12X', '2112123AG', 'Xiaomi 12X', '2201122C', 'Xiaomi 12 Pro', '2201122G', 'Xiaomi 12 Pro'],
];
var charStr = 'abacdefghjklmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ0123456789';

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

function encode(buffer, encode_type) {
    let encoder = new TextEncoder(encode_type)
    return encoder.encode(buffer)
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
            str = str + "属性名:" + (key + ': ' + obj[key]) + "\n";
        }
    }
    return str
}

function formatPlayUrl(src, name) {
    return name
        .trim()
        .replaceAll(src, '')
        .replace(/<|>|《|》/g, '')
        .replace(/\$|#/g, ' ')
        .trim();
}

function rand(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randDevice() {
    let brandIdx = rand(0, deviceBrands.length - 1);
    let brand = deviceBrands[brandIdx];
    let modelIdx = rand(0, deviceModels[brandIdx].length / 2 - 1);
    let model = deviceModels[brandIdx][modelIdx * 2 + 1];
    let release = rand(8, 13);
    let buildId = randStr(3, false).toUpperCase() + rand(11, 99) + randStr(1, false).toUpperCase();
    return {
        brand: brand,
        model: model,
        release: release,
        buildId: buildId,
    };
}

function randStr(len, withNum, onlyNum) {
    let _str = '';
    let containsNum = withNum === undefined ? true : withNum;
    for (let i = 0; i < len; i++) {
        let idx = onlyNum ? rand(charStr.length - 10, charStr.length - 1) : rand(0, containsNum ? charStr.length - 1 : charStr.length - 11);
        _str += charStr[idx];
    }
    return _str;
}

function randDeviceWithId(len) {
    let device = randDevice();
    device['id'] = randStr(len);
    return device;
}

function randUUID() {
    return randStr(8).toLowerCase() + '-' + randStr(4).toLowerCase() + '-' + randStr(4).toLowerCase() + '-' + randStr(4).toLowerCase() + '-' + randStr(12).toLowerCase();
}

function formatUrl(url) {
    if (url.indexOf("https:////") > -1) {
        url = "https://" + url.replaceAll("https:////", "")
    }
    if (url.indexOf("http:////") > -1) {
        url = "http://" + url.replaceAll("http:////", "")
    }
    return url
}

function formatContent(content) {
    return content.replaceAll('&amp;', '&')
        .replaceAll('&lt;', '<')
        .replaceAll('&gt;', '>')
        .replaceAll('&quot;', '\"')
        .replaceAll(/<\/?[^>]+>/g, '');
}
/**
 * 字符串相似度匹配
 * @returns
 */
function lcs(str1, str2) {
    if (!str1 || !str2) {
        return {
            length: 0,
            sequence: '',
            offset: 0,
        };
    }

    var sequence = '';
    var str1Length = str1.length;
    var str2Length = str2.length;
    var num = new Array(str1Length);
    var maxlen = 0;
    var lastSubsBegin = 0;

    for (var i = 0; i < str1Length; i++) {
        var subArray = new Array(str2Length);
        for (var j = 0; j < str2Length; j++) {
            subArray[j] = 0;
        }
        num[i] = subArray;
    }
    var thisSubsBegin = null;
    for (i = 0; i < str1Length; i++) {
        for (j = 0; j < str2Length; j++) {
            if (str1[i] !== str2[j]) {
                num[i][j] = 0;
            } else {
                if (i === 0 || j === 0) {
                    num[i][j] = 1;
                } else {
                    num[i][j] = 1 + num[i - 1][j - 1];
                }

                if (num[i][j] > maxlen) {
                    maxlen = num[i][j];
                    thisSubsBegin = i - num[i][j] + 1;
                    if (lastSubsBegin === thisSubsBegin) {
                        // if the current LCS is the same as the last time this block ran
                        sequence += str1[i];
                    } else {
                        // this block resets the string builder if a different LCS is found
                        lastSubsBegin = thisSubsBegin;
                        sequence = ''; // clear it
                        sequence += str1.substr(lastSubsBegin, i + 1 - lastSubsBegin);
                    }
                }
            }
        }
    }
    return {
        length: maxlen,
        sequence: sequence,
        offset: thisSubsBegin,
    };
}


function findAllIndexes(arr, value) {
    const indexes = arr.map((item, index) => index).filter(index => arr[index] === value);
    return indexes;
  }
   
let patternAli = /(https:\/\/www\.aliyundrive\.com\/s\/[^"]+|https:\/\/www\.alipan\.com\/s\/[^"]+)/
let patternQuark = /(https:\/\/pan\.quark\.cn\/s\/[^"]+)/


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
    patternQuark,
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
    getPropertiesAndMethods,
    formatPlayUrl,
    randDeviceWithId,
    randStr,
    randUUID,
    formatContent,
    formatUrl,
    encode,
    lcs,
    findAllIndexes
};