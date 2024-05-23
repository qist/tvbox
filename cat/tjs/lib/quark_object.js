/**
 * File: h:\PycharmProjects\Github\TVSpider\lib\quark_object.js
 * Project: h:\PycharmProjects\Github\TVSpider
 * Created Date: Monday, May 20th 2024, 5:26:45 pm
 * Author: jade
 * -----
 * Last Modified: Tue May 21 2024
 * Modified By: jade
 * -----
 * Copyright (c) 2024 samples
 * ------------------------------------
 * Javascript will save your soul!
 */
import {_} from "../lib/cat.js";
import * as Utils from "./utils.js";


class Item {
    constructor() {
        this.fileId = "";
        this.shareId = ""
        this.shareToken = "";
        this.shareFileToken = ""
        this.seriesId = ""
        this.name = "";
        this.type = "";
        this.formatType = "";
        this.size = "";
        this.parent = "";
        this.shareData = null;
        this.shareIndex = 0;
        this.lastUpdateAt = 0
    }

    static objectFrom(item_json, shareId,shareIndex) {
        let item = new Item();
        item.fileId = typeof item_json.fid == undefined ? "" : item_json.fid;
        item.shareId = shareId
        item.shareToken = typeof item_json.stoken == undefined ? "" : item_json.stoken;
        item.shareFileToken = typeof item_json.share_fid_token == undefined ? "" : item_json.share_fid_token;
        item.seriesId = typeof item_json.series_id == undefined?  "":item_json.series_id
        item.name = typeof item_json.file_name == undefined ? "" : item_json.file_name;
        item.type = typeof item_json.obj_category == undefined ? "" : item_json.obj_category;
        item.formatType = typeof item_json.format_type == undefined? "" : item_json.format_type;
        item.size = typeof item_json.size == undefined ? "" : item_json.size;
        item.parent = typeof item_json.pdir_fid == undefined ? "" : item_json.pdir_fid;
        item.lastUpdateAt = typeof item_json.last_update_at == undefined ? "" : item_json.last_update_at
        item.shareIndex = shareIndex
        return item;
    }

    getFileExtension(){
        return this.name.split(".").slice(-1)[0]
    }

    getFileId() {
        return _.isEmpty(this.fileId) ? "" : this.fileId 
    }

    getName() {
        return _.isEmpty(this.name) ? "" : this.name;
    }

    getParent() {
        return _.isEmpty(this.parent) ? "" : "[" + this.parent + "]";
    }

    getSize() {
        return this.size === 0 ? "" : "[" + Utils.getSize(this.size) + "]";
    }
    
    getShareIndex(){
        return this.shareIndex
    }
    getDisplayName(type_name) {
        let name = this.getName();
        if (type_name === "电视剧") {
            let replaceNameList = ["4k", "4K"]
            name = name.replaceAll("." + this.getFileExtension(), "")
            name = name.replaceAll(" ", "").replaceAll(" ", "")
            for (const replaceName of replaceNameList) {
                name = name.replaceAll(replaceName, "")
            }
            name = Utils.getStrByRegexDefault(/\.S01E(.*?)\./, name)
            const numbers = name.match(/\d+/g);
            if (!_.isEmpty(numbers) && numbers.length > 0) {
                name = numbers[0]
            }
        }
        
        return  name  + " " + this.getSize();
    }

    getEpisodeUrl(type_name){
        return  this.getDisplayName(type_name) + "$" + this.getFileId() + "++" + this.shareFileToken + "++" + this.shareId + "++" + this.shareToken
    }
}
export {Item}