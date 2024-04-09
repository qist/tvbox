/*
 * @Author: samples jadehh@live.com
 * @Date: 2023-12-14 11:03:04
 * @LastEditors: samples jadehh@live.com
 * @LastEditTime: 2023-12-14 11:03:04
 * @FilePath: lib/ali.js
 * @Description: 阿里云盘Spider公共
 */
import {
    getVod,
    initSome,
    clearFile,
    playerContent,
    playerContentByFlag,
    setShareId,
    setToken,
    getFileByShare, getTempFileId
} from './ali_api.js';
import {JadeLogging} from "./log.js";

const JadeLog = new JadeLogging("阿里云盘")


async function initAli(token) {
    await initSome();
    await setToken(token);
    await getTempFileId();
    // await clearFile();
    await JadeLog.info("阿里云盘初始化完成", true)
}


function getShareId(share_url) {
    let patternAli = /https:\/\/www\.alipan\.com\/s\/([^\\/]+)(\/folder\/([^\\/]+))?|https:\/\/www\.aliyundrive\.com\/s\/([^\\/]+)(\/folder\/([^\\/]+))?/
    let matches = patternAli.exec(share_url)
    const filteredArr = matches.filter(item => item !== undefined);
    if (filteredArr.length > 1) {
        return filteredArr[1]
    } else {
        return ""
    }
}

async function detailContent(share_url_list, type_name = "电影") {
    try {
        let video_items = [], sub_items = []

        for (const share_url of share_url_list) {
            let share_id = getShareId(share_url)
            let share_token = await setShareId(share_id)
            if (share_token !== undefined) {
                await getFileByShare(share_token, share_url, video_items, sub_items)
            }
        }
        if (video_items.length > 0) {
            await JadeLog.info(`获取播放链接成功,分享链接为:${share_url_list.join("\t")}`)
        } else {
            await JadeLog.error(`获取播放链接失败,检查分享链接为:${share_url_list.join("\t")}`)
        }
        return getVod(video_items, sub_items, type_name)
    } catch (e) {
        await JadeLog.error('获取阿里视频失败,失败原因为:' + e.message + ' 行数为:' + e.lineNumber);
    }
}

async function playContent(flag, id, flags) {
    if (flags.length > 0) {
        await JadeLog.info(`准备播放,播放类型为:${flag},播放文件Id为:${id},播放所有类型为:${flags.join("")}`)
    } else {
        await JadeLog.info(`准备播放,播放类型为:${flag},播放文件Id为:${id},播放所有类型为:${flags.join("")}`)
    }
    let file_id_list = id.split("+")
    let share_id = file_id_list[1]
    let file_id = file_id_list[0]
    let share_token = file_id_list[2]
    return flag === "原画" ? await playerContent(file_id, share_id, share_token) : await playerContentByFlag(file_id, flag, share_id, share_token);
}

export {
    initAli,
    detailContent,
    playContent
};