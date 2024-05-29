/**
 * File: /workspaces/TVSpider/lib/quark_api.js
 * Project: /workspaces/TVSpider
 * Created Date: Monday, May 20th 2024, 6:38:12 am
 * Author: jade
 * -----
 * Last Modified: Tue May 21 2024
 * Modified By: jade
 * -----
 * Copyright (c) 2024 samples
 * ------------------------------------
 * Javascript will save your soul!
 */
import {_,Crypto} from "../lib/cat.js";
import * as Utils from "../lib/utils.js"
import {Item} from  "../lib/quark_object.js"

class Quark{
    constructor(){
        this.apiUrl = "https://drive-pc.quark.cn/1/clouddrive/"
        this.cookie = ""
        this.ckey = ""
        this.shareTokenCache = {}
        this.pr = "pr=ucpro&fr=pc"
        this.subtitleExts = ['.srt', '.ass', '.scc', '.stl', '.ttml'];
        this.saveFileIdCaches = {}
        this.saveDirId = null
        this.saveDirName = 'TV';
        this.isVip = false;

    }
    async initQuark(cookie) {
        this.ckey = Crypto.enc.Hex.stringify(Crypto.MD5(cookie)).toString();
        this.cookie = cookie
        this.isVip = await this.getVip()
    }

    getHeaders(){
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) quark-cloud-drive/2.5.20 Chrome/100.0.4896.160 Electron/18.3.5.4-b478491100 Safari/537.36 Channel/pckk_other_ch',
            'Referer': 'https://pan.quark.cn/',
            "Content-Type":"application/json",
            "Cookie":this.cookie,
            "Host":"drive-pc.quark.cn"
        };
        
    }

    async api(url,data,retry,method){
        const leftRetry = retry || 3;
        let resp = await req(this.apiUrl + url,{
            method:method || "post",
            data:data,
            headers:this.getHeaders()
        })
        if (resp.headers['set-cookie']) {
            const puus = [resp.headers['set-cookie']].join(';;;').match(/__puus=([^;]+)/);
            if (puus) {
                if (this.cookie.match(/__puus=([^;]+)/)[1] != puus[1]) {
                    this.cookie = this.cookie.replace(/__puus=[^;]+/, `__puus=${puus[1]}`);
                }
            }
        }
        if (resp.code !== 200 && leftRetry > 0) {
            Utils.sleep(1)
            return await this.api(url, data, leftRetry - 1);
        }
        return JSON.parse(resp.content) || {};
    }

    getShareData(url) {
        let regex = /https:\/\/pan\.quark\.cn\/s\/([^\\|#/]+)/;
        let matches = regex.exec(url);
        if (matches) {
            return {
                shareId: matches[1],
                folderId: '0',
            };
        }
        return null;
    }

    async getVip(){
        const listData = await this.api(`member?pr=ucpro&fr=pc&uc_param_str=&fetch_subscribe=true&_ch=home&fetch_identity=true`, null,null, 'get');
        if (listData.data.member_type==="EXP_SVIP"){
            return true
        }else{
            return false
        }
    }

    getPlayFormatList(){
        if(this.isVip){
            return ["4K","超清","高清","普画"] 
        }else{
            return ["普画"]
        }
    }

    getPlayFormtQuarkList(){
        if(this.isVip){
            return ["4k","2k","super","high","normal","low"]
        }{
            return ["low"]
        }
    }


    async  getShareToken(shareData) {
        if (!this.shareTokenCache[shareData.shareId]) {
            delete this.shareTokenCache[shareData.shareId];
            const shareToken = await this.api(`share/sharepage/token?${this.pr}`, {
                pwd_id: shareData.shareId,
                passcode: shareData.sharePwd || '',
            });
            if (shareToken.data && shareToken.data.stoken) {
                this.shareTokenCache[shareData.shareId] = shareToken.data;
            }
        }
    }
    async listFile (shareIndex,shareData,videos,subtitles,shareId, folderId, page) {
        const prePage = 200;
        page = page || 1;
        const listData = await this.api(`share/sharepage/detail?${this.pr}&pwd_id=${shareId}&stoken=${encodeURIComponent(this.shareTokenCache[shareId].stoken)}&pdir_fid=${folderId}&force=0&_page=${page}&_size=${prePage}&_sort=file_type:asc,file_name:asc`, null,null, 'get');
        if (!listData.data) return [];
        const items = listData.data.list;
        if (!items) return [];
        const subDir = [];
        for (const item of items) {
            if (item.dir === true) {
                subDir.push(item);
            } else if (item.file === true && item.obj_category === 'video') {
                if (item.size < 1024 * 1024 * 5) continue;
                item.stoken = this.shareTokenCache[shareData.shareId].stoken;
                videos.push(Item.objectFrom(item,shareData.shareId,shareIndex));
            } else if (item.type === 'file' && this.subtitleExts.some((x) => item.file_name.endsWith(x))) {
                subtitles.push(Item.objectFrom(item,shareData,shareIndex));
            }
        }
        if (page < Math.ceil(listData.metadata._total / prePage)) {
            const nextItems = await this.listFile(shareIndex,shareData.shareId,videos,subtitles,shareId, folderId, page + 1);
            for (const item of nextItems) {
                items.push(item);
            }
        }
        for (const dir of subDir) {
            const subItems = await this.listFile(shareIndex,shareData,videos,subtitles,shareId, dir.fid);
            for (const item of subItems) {
                items.push(item);
            }
        }
        return items;
    };

    findBestLCS(mainItem, targetItems) {
        const results = [];
        let bestMatchIndex = 0;
        for (let i = 0; i < targetItems.length; i++) {
            const currentLCS = Utils.lcs(mainItem.name, targetItems[i].name);
            results.push({ target: targetItems[i], lcs: currentLCS });
            if (currentLCS.length > results[bestMatchIndex].lcs.length) {
                bestMatchIndex = i;
            }
        }
        const bestMatch = results[bestMatchIndex];
        return { allLCS: results, bestMatch: bestMatch, bestMatchIndex: bestMatchIndex };
    }

    async getFilesByShareUrl(shareIndex,shareInfo,videos,subtitles){
        const shareData = typeof shareInfo === 'string' ? this.getShareData(shareInfo) : shareInfo;
        if (!shareData) return [];
        await this.getShareToken(shareData);
        if (!this.shareTokenCache[shareData.shareId]) return [];
        await this.listFile(shareIndex,shareData,videos,subtitles,shareData.shareId, shareData.folderId);
        if (subtitles.length > 0) {
            videos.forEach((item) => {
                var matchSubtitle = this.findBestLCS(item, subtitles);
                if (matchSubtitle.bestMatch) {
                    item.subtitle = matchSubtitle.bestMatch.target;
                }
            });
        }
    }

    clean(){
        const saves = Object.keys(this.saveFileIdCaches);
        for (const save of saves) {
            delete this.saveFileIdCaches[save];
        }
    }


    async  clearSaveDir() {
        const listData = await this.api(`file/sort?${this.pr}&pdir_fid=${this.saveDirId}&_page=1&_size=200&_sort=file_type:asc,updated_at:desc`, {}, {}, 'get');
        if (listData.data && listData.data.list && listData.data.list.length > 0) {
           await this.api(`file/delete?${this.pr}`, {
                action_type: 2,
                filelist: listData.data.list.map((v) => v.fid),
                exclude_fids: [],
            });
        }
    }

    async  createSaveDir(clean) {
        if (this.saveDirId) {
            // 删除所有子文件
            if (clean) await this.clearSaveDir();
            return;
        }
        const listData = await this.api(`file/sort?${this.pr}&pdir_fid=0&_page=1&_size=200&_sort=file_type:asc,updated_at:desc`, {}, {}, 'get');
        if (listData.data && listData.data.list)
            for (const item of listData.data.list) {
                if (item.file_name === this.saveDirName) {
                    this.saveDirId = item.fid;
                    await this.clearSaveDir();
                    break;
                }
            }
        if (!this.saveDirId) {
            const create = await this.api(`file?${this.pr}`, {
                pdir_fid: '0',
                file_name: this.saveDirName,
                dir_path: '',
                dir_init_lock: false,
            });
            if (create.data && create.data.fid) {
                this.saveDirId = create.data.fid;
            }
        }
    }

    async save(shareId, stoken, fileId, fileToken, clean) {
        await this.createSaveDir(clean);
        if (clean) {
            this.clean()
        }
        if (!this.saveDirId) return null;
        if (!stoken) {
            await this.getShareToken({
                shareId: shareId,
            });
            if (!this.shareTokenCache[shareId]) return null;
        }
        const saveResult = await this.api(`share/sharepage/save?${this.pr}`, {
            fid_list: [fileId],
            fid_token_list: [fileToken],
            to_pdir_fid: this.saveDirId,
            pwd_id: shareId,
            stoken: stoken || this.shareTokenCache[shareId].stoken,
            pdir_fid: '0',
            scene: 'link',
        });
        if (saveResult.data && saveResult.data.task_id) {
            let retry = 0;
            // wait task finish
            while (true) {
                const taskResult = await this.api(`task?${this.pr}&task_id=${saveResult.data.task_id}&retry_index=${retry}`, {}, {}, 'get');
                if (taskResult.data && taskResult.data.save_as && taskResult.data.save_as.save_as_top_fids && taskResult.data.save_as.save_as_top_fids.length > 0) {
                    return taskResult.data.save_as.save_as_top_fids[0];
                }
                retry++;
                if (retry > 2) break;
                Utils.sleep(1);
            }
        }
        return false;
    }

    
    async  getLiveTranscoding(shareId, stoken, fileId, fileToken,flag) {
        if (!this.saveFileIdCaches[fileId]) {
            const saveFileId = await this.save(shareId, stoken, fileId, fileToken, true);
            if (!saveFileId) return null;
            this.saveFileIdCaches[fileId] = saveFileId;
        }
        const transcoding = await this.api(`file/v2/play?${this.pr}`, {
            fid: this.saveFileIdCaches[fileId],
            resolutions: 'normal,low,high,super,2k,4k',
            supports: 'fmp4',
        });

     
        if (transcoding.data && transcoding.data.video_list) {
            let flag_id = flag.split("-").slice(-1)[0]
            let index = Utils.findAllIndexes(this.getPlayFormatList(),flag_id);
            let quarkFormat = this.getPlayFormtQuarkList()[index]
            for (const video of transcoding.data.video_list){
                if (video.resolution === quarkFormat){
                    return video.video_info.url
                }
            }
            return transcoding.data.video_list[index].video_info.url
        }
        return null;
    }

  async  getDownload(shareId, stoken, fileId, fileToken, clean) {
        if (!this.saveFileIdCaches[fileId]) {
            const saveFileId = await this.save(shareId, stoken, fileId, fileToken, clean);
            if (!saveFileId) return null;
            this.saveFileIdCaches[fileId] = saveFileId;
        }
        const down = await this.api(`file/download?${this.pr}&uc_param_str=`, {
            fids: [this.saveFileIdCaches[fileId]],
        });
        if (down.data) {
            return down.data[0];
        }
        return null;
    }

}
export {Quark}