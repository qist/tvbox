/**
 * File: h:\PycharmProjects\Github\TVSpider\lib\cloud.js
 * Project: h:\PycharmProjects\Github\TVSpider
 * Created Date: Tuesday, May 21st 2024, 2:01:09 pm
 * Author: jade
 * -----
 * Last Modified: Tue May 21 2024
 * Modified By: jade
 * -----
 * Copyright (c) 2024 samples
 * ------------------------------------
 * Javascript will save your soul!
 */

import {initAli,detailContentAli,playContentAli, aliPlayFormatList,aliName} from "./ali.js"
import { initQuark,detailContentQuark,playContentQuark,getQuarkPlayFormatList,quarkName,getQuarkHeaders} from "./quark.js"
import * as Utils from "./utils.js";
import {_} from "../lib/cat.js";


async function initCloud(cfg){
    initAli(cfg["aliToken"])
    initQuark(cfg["quarkCookie"])
}

async function detailContent(share_url_list,type_name="电影"){
    let ali_share_url_list = [],quark_share_url_list = []
    const playVod = {}
    for (const shareUrl of share_url_list){
        let aliMatches = shareUrl.match(Utils.patternAli);
        if (!_.isEmpty(aliMatches)) {
            ali_share_url_list.push(aliMatches[1])
        }
        let quarkMatches = shareUrl.match(Utils.patternQuark);
        if (!_.isEmpty(quarkMatches)){
            quark_share_url_list.push(quarkMatches[1])
        }
    }
    let aliItems = await detailContentAli(ali_share_url_list)
    let quarkItems = await detailContentQuark(quark_share_url_list)
    let quarkPlayFormatList =  getQuarkPlayFormatList();
    await getVod(aliPlayFormatList,aliName,playVod,aliItems.video_items,aliItems.sub_items,type_name)
    await getVod(quarkPlayFormatList,quarkName,playVod,quarkItems.video_items,quarkItems.sub_items,type_name)

    return playVod
}


async function getVod(play_foramt_list,cloud_name,playVod,video_item_list, sub_item_list, type_name) {
    if (video_item_list.length ==0){
        return 
    }
    for (let i=0; i<video_item_list.slice(-1)[0].shareIndex;i++){
        for (let index = 0; index < play_foramt_list.length; index++) {
            let vodItems = []
            for (const video_item of video_item_list) {
                if (video_item.shareIndex === i + 1){
                    vodItems.push( video_item.getEpisodeUrl(type_name)+ findSubs(video_item.getName(), sub_item_list));                }
                }
            playVod[`${cloud_name}-${i+1}-${play_foramt_list[index]}`] = vodItems.join("#")
        }
    }
}

//字幕匹配
function pair(name, item_list, sub_item_list) {
    for (const item of item_list) {
        const sub_name = Utils.removeExt(item.getName()).toLowerCase();
        if (name.indexOf(sub_name) > -1 || sub_name.indexOf(name) > -1) {
            sub_item_list.push(item);
        }
    }
}

//找出所有字幕
function findSubs(name, item_list) {
    let sub_item_list = [];
    pair(Utils.removeExt(name).toLowerCase(), item_list, sub_item_list);
    if (sub_item_list.length === 0) {
        for (const item of item_list) {
            sub_item_list.push(item);
        }
    }
    let sub_str = "";
    for (const item of sub_item_list) {
        sub_str += "+" + Utils.removeExt(item.getName()) + "@@@" + item.getExt() + "@@@" + item.getFileId();
    }
    return sub_str;
}
async function playContent(flag,id,flags){
    if (flag.indexOf(aliName) > -1) {
        return await playContentAli(flag, id, flags)
    }else if (flag.indexOf(quarkName) > -1){
        return await playContentQuark(flag,id,flags)
    }
}

function getHeaders(flag){
    if (flag.indexOf(aliName) > -1) {
        return {}
    }else if (flag.indexOf(quarkName) > -1){
        return getQuarkHeaders()
    }
}


export {initCloud,detailContent,playContent,getHeaders,aliName,quarkName}