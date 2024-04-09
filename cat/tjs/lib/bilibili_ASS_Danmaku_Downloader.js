/*
* @File     : bilibili_ASS_Danmaku_Downloader.js
* @Author   : jade
* @Date     : 2024/3/14 13:19
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/
function parseXML(json) {
    let list = [];
       /**
     * <d p="{time},{type},{size},{color},{timestamp},{pool},{uid_crc32},{row_id}">
     *
     * {Text}
     * time为弹幕在视频里的时间 -->
     * type为弹幕类型 -->
     * size为字体大小 -->
     * color为十进制的RGB颜色（16进制转10进制） -->
     * timestamp为弹幕发送时间戳（unix时间戳） -->
     * pool为弹幕池 -->
     * uid_crc32为发送者uid的crc32 -->
     */
    Array.from(json.danmuku).forEach(x => {
        let start = Number(x[0]);
        let content = x[4];
        list.push(`<d p="${start},1,25,16777215,1659282294,0,8b53b65c,1108899274487246080"><![CDATA[${content}]]></d>`)
    });
    return String.raw`<?xml version="1.0" encoding="UTF-8"?><i><chatserver>chat.bilibili.com</chatserver><chatid>52175602</chatid><mission>0</mission><maxlimit>1000</maxlimit><state>0</state><real_name>0</real_name><source>k-v</source>` + list.join('') + "</i>"
}
export {parseXML}

