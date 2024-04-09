/*
 * @Author: samples jadehh@live.com
 * @Date: 2023-12-14 11:03:04
 * @LastEditors: samples jadehh@live.com
 * @LastEditTime: 2023-12-14 11:03:04
 * @FilePath: /lib/ali_api.js
 * @Description: 阿里云盘Api
 */
import {_, jinja2} from "./cat.js";
import * as Utils from "./utils.js";
import {JadeLogging} from "./log.js";
import {
    Code, Drive, getHeader, getOAuthCache, getUserCache, Item, OAuth, post, postJson, Sub, User, CLIENT_ID
} from "./ali_object.js";

let quality = {}, tempIds = [], shareToken = "", shareId = "", oauth = new OAuth(), user = new User(),
    driveInfo = new Drive(), tmpFolderName = "TV", curTmpFolderFileId = "",
    JadeLog = new JadeLogging("阿里云盘", "INFO");

async function initSome() {
    let user_cache_str = await getUserCache();
    user = User.objectFrom(user_cache_str);
    if (!_.isEmpty(user.getRefreshToken())) {
        await JadeLog.info("读取用户缓存成功", true);
    } else {
        await JadeLog.error("读取用户缓存失败", true);
    }

    let oauth_cache_str = await getOAuthCache();
    oauth = OAuth.objectFrom(oauth_cache_str);
    if (!_.isEmpty(oauth.getAccessToken())) {
        await JadeLog.info("读取授权成功", true)
    } else {
        await JadeLog.error("读取授权失败", true)

    }
    // quality = {
    //     "4K": "UHD", "2k": "QHD", "超清": "FHD", "高清": "HD", "标清": "SD", "流畅": "LD"
    // };
    quality = {
        "4K": "UHD", "2k": "QHD", "超清": "QHD", "高清": "HD", "标清": "SD", "流畅": "LD"
    };
    await JadeLog.info("阿里Api初始化完成")
}

async function getTempFileId() {
    curTmpFolderFileId = await createTmpFolder();
}

async function clearFile() {
    try {
        await deleteTmpFolderAndRecreate();
    } catch (e) {
        await JadeLog.error("清空缓存文件失败,失败原因为:{}" + e)
    }
    await cleanRecord()
}

async function cleanRecord() {
  await local.set("file", "file_id", JSON.stringify({}))
}

async function setShareId(share_id) {
    getOAuthCache().length === 0 && (await oauth.clean().save());
    getUserCache().length === 0 && (await user.clean().save());
    shareId = share_id;
    return await refreshShareToken();
}

function getHeaderAuth(shareToken) {
    const params = {};
    params["x-share-token"] = shareToken;
    params["X-Canary"] = "client=Android,app=adrive,version=v4.3.1";

    if (user.isAuthed()) {
        params.authorization = user.getAuthorization();
    }

    return params;
}

function getHeaderShare() {
    const params = getHeader();
    params["x-share-token"] = shareToken;
    params["X-Canary"] = "client=Android,app=adrive,version=v4.3.1";
    return params;
}

function getHeaderOpen() {
    const params = {};
    params.authorization = oauth.getAuthorization();
    return params;
}

function aliExpection(data_str) {
    if (data_str.indexOf("TooManyRequests") > -1) {
        Utils.sleep(1)
        return {code: 429, content: data_str}
    } else if (data_str.indexOf("AccessTokenInvalid") > -1) {
        return {code: 400, content: data_str}
    } else if (data_str.indexOf("AccessTokenExpired") > -1) {
        return {code: 401, content: data_str}
    } else if (data_str.indexOf("BadRequest") > -1) {
        return {code: 402, content: data_str}
    } else if (data_str.indexOf("NotFound.File") > -1 || data_str.indexOf("ForbiddenFileInTheRecycleBin") > -1) {
        return {code: 403, content: data_str}
    } else if (data_str.indexOf("ForbiddenNoPermission.File") > -1) {
        return {code: 500, content: data_str}
    } else if (data_str.indexOf("InvalidParameter.ToParentFileId") > -1) {
        return {code: 501, content: data_str}
    } else if (data_str.indexOf("NotFound.ParentFileId") > -1) {
        return {code: 502, content: data_str}
    } else if (data_str.indexOf("The resource drive has exceeded the limit. File size exceeded drive capacity") > -1) {
        return {code: 503, content: data_str}
    }
    return {code: 200, content: data_str}
}

async function alistManyRequest(data_str) {
    if (!(data_str.indexOf("Too Many Requests") > -1)) {
        return false;
    }
    await oauth.clean().save();
    return true;
}

// Alist Token获取
async function alist(url_param, params) {
    let url = "https://api-cf.nn.ci/alist/ali_open/" + url_param;
    let response = await postJson(url, params, getHeader()), response_content = response.content;
    if (await alistManyRequest(response_content)) {
        await JadeLog.error(`Alist授权Token失败,失败原因为:太多请求,失败详情为:${response_content}`)
        return false;
    }
    oauth = await OAuth.objectFrom(response_content).save();
    return true;
}

// 阿里云盘用户Api
async function auth(url, params, shareToken, retry) {
    url = url.startsWith("https") ? url : "https://api.aliyundrive.com/" + url;
    let response = await postJson(url, params, getHeaderAuth(shareToken));
    await JadeLog.debug(`正在请求需要阿里登录的url:${url},参数为:${JSON.stringify(params)}`)
    response = aliExpection(response.content)
    if (retry && (response.code === 400)) {
        await JadeLog.error("登录阿里云盘失败,失败原因为:登录Token无效,准备重新授权,失败详情:" + response.content)
        await refreshAccessToken("")
        return await auth(url, params, shareToken, false);
    }
    await JadeLog.debug(`完成请求需要阿里登录的url:${url},参数为:${JSON.stringify(params)},请求结果为${response.content}`)
    return response.content;

}


// 需要授权的Api
async function oauthFunc(url, params, retry) {
    url = url.startsWith("https") ? url : "https://open.aliyundrive.com/adrive/v1.0/" + url;
    await JadeLog.debug(`正在请求需要阿里授权的url:${url},参数为:${JSON.stringify(params)}`)
    let open_header = getHeaderOpen();
    let response = await postJson(url, params, open_header);
    response = aliExpection(response.content)
    if (retry && (response.code === 400 || response.code === 401 || response.code === 429 || response.code === 402 || response.code === 403)) {
        if (response.code === 400) {
            await JadeLog.error("阿里授权失败,失败原因为:授权Token无效,准备重新授权,失败详情:" + response.content)
            await activateRefreshOpenToken()
        } else if (response.code === 401) {
            await JadeLog.error("阿里授权失败,失败原因为:授权Token失效,准备重新授权,失败详情:" + response.content)
            await activateRefreshOpenToken()
        } else if (response.code === 402) {
            await JadeLog.error("阿里授权失败,失败原因为:授权Token失效,准备重新授权,失败详情:" + response.content)
            return await oauthFunc(url, params, true)
        } else if (response.code === 403) {
            await JadeLog.error("阿里授权失败,失败原因为:没有找到缓存文件,失败详情:" + response.content)
            await cleanRecord()
            return "retry"
        } else if (response.code === 429) {
            await JadeLog.error(`正在请求需要阿里授权的url:${url},请求过于频繁,稍后重试,10分钟后再重试`)
            Utils.sleep(10 * 60)
            return await oauthFunc(url, params, true)
        }
        return await oauthFunc(url, params, false)
    }
    await JadeLog.debug(`完成请求需要阿里授权的url:${url},参数为:${JSON.stringify(params)},请求结果为:${JSON.stringify(response)}`)
    return response.content;

}

async function shareFunc(url, params) {
    url = url.startsWith("https") ? url : "https://api.aliyundrive.com/" + url;
    let headers = getHeaderShare(), response = await postJson(url, params, headers);
    return response.content;
}

//主动刷新授权Token

async function activateRefreshOpenToken() {
    await oauth.clean().save()
    await refreshOpenToken()
}


async function refreshShareToken() {
    try {
        let params = {};
        params.share_id = shareId;
        params.share_pwd = "";
        let response_content = await post("v2/share_link/get_share_token", params),
            response_json = JSON.parse(response_content);
        if (response_json["code"] === "ShareLink.Cancelled") {
            await JadeLog.error("分享链接被取消了")
        }
        shareToken = response_json.share_token;
        return shareToken
    } catch (e) {
        await JadeLog.error("刷新Share Token失败" + e)
    }
}

//支持切换Token
async function refreshAccessToken(token) {
    try {
        if (_.isEmpty(user.getAccessToken()) || user.getRefreshToken() !== token) {
            let refresh_token_params = {};
            refresh_token_params.refresh_token = user.getRefreshToken();
            refresh_token_params.grant_type = "refresh_token";
            await JadeLog.info(`准备登录阿里云盘,登录Token为:${user.getRefreshToken()}`)
            let response_conetent = await post("https://auth.aliyundrive.com/v2/account/token", refresh_token_params);
            if (response_conetent.indexOf("InvalidParameter.RefreshToken") > 1 || _.isEmpty(response_conetent)) {
                if (_.isEmpty(response_conetent)) {
                    await JadeLog.error(`登录阿里云盘失败,登录Token为:${user.getRefreshToken()},失败原因为:检查Token是否正确`)
                } else {
                    await JadeLog.error(`登录阿里云盘失败,登录Token为:${user.getRefreshToken()},失败原因为:检查Token是否正确,返回结果为:${response_conetent}`)
                }
            } else {
                await JadeLog.info(`登录阿里云盘成功,登录Token为:${user.getRefreshToken()}`)
                user = await User.objectFrom(response_conetent).save();
            }
        } else {
            await JadeLog.info(`阿里云盘已登录,无需重复登录,登录Token为:${user.getRefreshToken()}`)
        }
        return true;
    } catch (e) {
        await JadeLog.error(`登录阿里云盘失败,登录Token为:${user.getRefreshToken()},失败原因为:${e}`)
        await user.clean().save();
        return true;
    }
}

async function oauthRequest() {
    try {
        let params = {};
        params.authorize = 1;
        params.scope = "user:base,file:all:read,file:all:write";
        let url = "https://open.aliyundrive.com/oauth/users/authorize?client_id=" + CLIENT_ID + "&redirect_uri=https://alist.nn.ci/tool/aliyundrive/callback&scope=user:base,file:all:read,file:all:write&state="
        await JadeLog.debug(`正在请求获取阿里授权码的url:${url},参数为:${params}`)
        let response_str = await auth(url, params, shareToken, true);
        await JadeLog.debug(`完成请求获取阿里授权码的url:${url},参数为:${params},返回值为:${response_str}`)
        if (_.isEmpty(response_str) || response_str.indexOf("AccessTokenInvalid") > -1) {
            if (_.isEmpty(response_str)) {
                await JadeLog.error(`请求获取阿里授权码失败,失败原因为:还未登录`)
            } else {
                await JadeLog.error(`请求获取阿里授权码失败,失败原因为:还未登录,失败详情为:${response_str}`)
            }
        } else {
            await JadeLog.info(`请求获取阿里授权码成功,返回值为:${response_str}`)
            return await oauthRedirect(Code.objectFrom(response_str).getCode());
        }
    } catch (e) {
        await JadeLog.error(`请求获取阿里授权失败,失败原因为:${e}`)
        return false;
    }
}

async function oauthRedirect(code) {
    try {
        let params = {};
        params.code = code;
        params.grant_type = "authorization_code";
        return await alist("code", params);
    } catch (e) {
        // // console.debug(_0x114c46);
        await oauth.clean().save();
        return false;
    }
}

async function refreshOpenToken() {
    try {
        // 刷新 Refresh Token
        if (_.isEmpty(oauth.getRefreshToken())) {
            return await oauthRequest();
        }
        // 刷新Access Token
        if (_.isEmpty(oauth.getAccessToken())) {
            let params = {};
            params.grant_type = "refresh_token";
            params.refresh_token = oauth.getRefreshToken();
            return await alist("token", params);
        }
        return true;
    } catch (e) {
        await JadeLog.error("刷新授权Token失败,失败原因为:" + e);
        await oauth.clean().save();
        return false;
    }
}

async function getFileByShare(share_token, share_url, video_item_list, sub_item_list) {
    await JadeLog.info(`正在获取播放链接,分享链接为:${share_url}`)
    let params = {};
    params.share_id = shareId;
    let file_id = share_url.split("folder/").slice(-1)[0]
    if (file_id.length !== 40) {
        file_id = ""
    }
    let response_str = await post("adrive/v3/share_link/get_share_by_anonymous", params),
        response_json = JSON.parse(response_str), item_file_id = getParentFileId(file_id, response_json),
        item = new Item(item_file_id);
    await listFiles(item, video_item_list, sub_item_list, share_token);
}

async function getVod(video_item_list, sub_item_list, type_name) {
    let play_foramt_list = ["原画", "超清", "高清", "标清"], episode_list = [], episode_str_list = [];
    for (const video_item of video_item_list) {
        episode_list.push(video_item.getDisplayName(type_name) + "$" + video_item.getFileId() + "+" + video_item.shareId + "+" + video_item.shareToken + findSubs(video_item.getName(), sub_item_list));
    }
    for (let index = 0; index < play_foramt_list.length; index++) {
        episode_str_list.push(episode_list.join("#"));
    }
    return {
        vod_play_url: episode_str_list.join("$$$"), vod_play_from: play_foramt_list.map(item => item).join("$$$"),
    };
}

async function listFiles(item, video_item_list, sub_item_list, share_token) {
    return await listFilesMarker(item, video_item_list, sub_item_list, "", share_token);
}

async function listFilesMarker(item, video_item_list, sub_item_list, netxt_markers, share_token) {
    let new_item = {}, file_list = [];
    new_item.limit = 200;
    new_item.share_id = shareId;
    new_item.share_token = share_token
    new_item.parent_file_id = item.getFileId();
    new_item.order_by = "name";
    new_item.order_direction = "ASC";
    if (netxt_markers.length > 0) {
        new_item.marker = netxt_markers;
    }
    let items = Item.objectFrom(await shareFunc("adrive/v2/file/list_by_share", new_item), shareToken);
    for (const r_item of items.getItems()) {
        if (r_item.getType() === "folder") {
            file_list.push(r_item);
        } else {
            if ((r_item.getCategory() === "video" || r_item.getCategory() === "audio")) {
                //判断数组中是否有file_id
                //
                let is_video_file_exists = false
                for (const video_item of video_item_list) {
                    if (r_item.getFileId() === video_item.getFileId()) {
                        is_video_file_exists = true
                        await JadeLog.debug('视频分享文件重复,无需添加')
                    }
                }
                if (!is_video_file_exists) {
                    if (r_item.getCategory() === "video" && r_item.size / 1000000 > 10) {
                        video_item_list.push(r_item.parentFunc(item.getName()));
                    }
                }

            } else {
                if (Utils.isSub(r_item.getExt())) {
                    let is_sub_file_exists = false
                    for (const sub_item of sub_item_list) {
                        if (r_item.getFileId() === sub_item.getFileId()) {
                            is_sub_file_exists = true
                            await JadeLog.debug('字幕分享文件重复,无需添加')
                        }
                    }
                    if (!is_sub_file_exists) {
                        sub_item_list.push(r_item);
                    }
                }
            }
        }
    }
    items.getNextMarker().length > 0 && (await listFilesMarker(item, video_item_list, sub_item_list, items.getNextMarker()));
    for (const file of file_list) {
        await listFiles(file, video_item_list, sub_item_list);
    }
}

function getParentFileId(file_id, items) {
    let file_infos = items.file_infos;

    if (!_.isEmpty(file_id)) {
        return file_id;
    }

    if (file_infos.length === 0) {
        return "";
    }

    let item = file_infos[0];

    if (item.type === "folder") {
        return item.file_id;
    }
    if (item.type === "file" && item.category === "video") {
        return "root";
    }
    return "";
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

async function getSubs(sub_list, share_id) {
    let sub_url_list = [];
    for (const sub_str of sub_list) {
        if (!(sub_str.indexOf("@@@") > -1)) {
            continue;
        }
        let sub_split_list = sub_str.split("@@@"), sub_name = sub_split_list[0], sub_ext = sub_split_list[1],
            sub_file_id = sub_split_list[2], sub_url = await getDownloadUrl(sub_file_id, share_id);

        sub_url_list.push(Sub.create().setName(sub_name).setExt(sub_ext).setUrl(sub_url));
    }
    return sub_url_list;
}

async function getDriveInfo() {
    if (!_.isEmpty(driveInfo) && !_.isEmpty(driveInfo.default_drive_id)) {
        return driveInfo;
    }

    let _0x3740f3 = await oauthFunc("user/getDriveInfo", {}, true), _0x56fde5 = JSON.parse(_0x3740f3);

    driveInfo = {
        default_drive_id: _0x56fde5.default_drive_id,
        resource_drive_id: _0x56fde5.resource_drive_id,
        backup_drive_id: _0x56fde5.backup_drive_id
    };
    return driveInfo;
}

async function getDriveId() {
    if (_.isEmpty(user.getDriveId())) {
        let drive = await getDriveInfo();
        return drive.resource_drive_id;
    }
    return user.getDriveId();
}

async function getDownloadUrl(file_id, share_id, share_token) {
    let drive_id = await getDriveId();
    tempIds.unshift(await copy(file_id, share_id, share_token));
    let params = {};
    params.file_id = tempIds[0];
    params.drive_id = drive_id;
    if (tempIds[0] !== null) {
        let response_str = await oauthFunc("openFile/getDownloadUrl", params, true);
        if (response_str === "retry") {
            await JadeLog.info("尝试重新获取下载链接");
            return await getDownloadUrl(file_id, share_id)
        } else {
            await JadeLog.info("获取下载链接成功:返回结果为:" + response_str + "请求参数为:" + JSON.stringify(params));
            return JSON.parse(response_str).url;
        }
    } else {
        await JadeLog.error("获取下载链接失败:失败原因:请检查转存文件失败原因")
        return null;
    }

}

async function getVideoPreviewPlayInfo(file_id, share_id, shareToken) {
    let drive_id = await getDriveId();
    tempIds.unshift(await copy(file_id, share_id, shareToken));
    let params = {};
    params.file_id = tempIds[0];
    params.drive_id = drive_id;
    params.category = "live_transcoding";
    params.url_expire_sec = "14400";
    let response_str = await oauthFunc("openFile/getVideoPreviewPlayInfo", params, true);
    return JSON.parse(response_str).video_preview_play_info;
}

async function playerContent(file_id, share_id, share_token) {
    try {
        await JadeLog.info("正在获取原画的播放地址和字幕下载链接", true)
        let download_url = await getDownloadUrl(file_id, share_id, share_token);
        // let sub_list = await getSubs(file_id_list,share_id);
        await JadeLog.info("获取原画的播放地址和字幕下载链接成功", true)
        await JadeLog.info(`下载地址为:${download_url}`)
        return JSON.stringify({
            parse: 0, url: download_url, header: getHeader(), format: "application/octet-stream", subs: []
        });
    } catch (e) {
        await JadeLog.error("获取原画的播放地址和字幕下载链接失败:失败原因为:" + e);
    }
}

// 转码头的Url和字幕
async function playerContentByFlag(file_id, flag, share_id, shareToken) {
    try {
        await JadeLog.info("正在获取转码后的播放地址和字幕下载链接", true)
        let video_preview_play_info = await getVideoPreviewPlayInfo(file_id, share_id, shareToken),
            video_preview_url = getPreviewUrl(video_preview_play_info, flag);
        // let sub_list = await getSubs(file_id_list,share_id),
        //     sub_p_list = getSubsByPlayInfo(video_preview_play_info);

        // for (const sub_p of sub_p_list) {
        //     sub_list.push(sub_p);
        // }

        await JadeLog.info("获取转码后的播放地址和字幕下载链接成功", true)
        await JadeLog.info(`下载地址为:${video_preview_url}`)
        return JSON.stringify({
            parse: 0, url: video_preview_url, header: getHeader(), format: "application/x-mpegURL", subs: []
        });
    } catch (e) {
        await JadeLog.error(`获取转码后的播放地址和字幕下载链接失败,失败原因为:${e}`)
    }
}

function getPreviewUrl(video_preview_play_info, flag) {
    if (!video_preview_play_info.hasOwnProperty("live_transcoding_task_list")) {
        return "";
    }
    let live_transcoding_task_list = video_preview_play_info.live_transcoding_task_list;
    for (let index = 0; index < live_transcoding_task_list.length; ++index) {
        let live_transcoding_task = live_transcoding_task_list[index];

        if (live_transcoding_task.template_id === quality[flag]) {
            return live_transcoding_task.url;
        }
    }
    return live_transcoding_task_list[0].url;
}

function getSubsByPlayInfo(video_preview_play_info) {
    if (!video_preview_play_info.hasOwnProperty("live_transcoding_subtitle_task_list")) {
        return [];
    }
    let live_transcoding_subtitle_task_list = video_preview_play_info.live_transcoding_subtitle_task_list,
        sub_p_list = [];
    for (let index = 0; index < live_transcoding_subtitle_task_list.length; ++index) {
        let live_transcoding_subtitle_task = live_transcoding_subtitle_task_list[index],
            language = live_transcoding_subtitle_task.language, url = live_transcoding_subtitle_task.url;
        sub_p_list.push(Sub.create().setUrl(url).setName(language).setLang(language).setExt("vtt"));
    }
    return sub_p_list;
}

async function copy(file_id, shareId, shareToken) {
    let copy_file_id
    let cache_dic = {}
    try {
       cache_dic = JSON.parse(await local.get("file", "file_id"))
    } catch (e) {
    }
    copy_file_id = cache_dic[file_id]
    if (typeof (copy_file_id) == "string") {
        await JadeLog.info(`file id为:${file_id},已经缓存过,copy file id为:${copy_file_id}`)
    } else {
        let params_str = "{\"requests\":[{\"body\":{\"file_id\":\"{{data.fileId}}\",\"share_id\":\"{{data.shareId}}\",\"auto_rename\":true,\"to_parent_file_id\":\"{{data.tmpFolderFileId}}\",\"to_drive_id\":\"{{data.driveId}}\"},\"headers\":{\"Content-Type\":\"application/json\"},\"id\":\"0\",\"method\":\"POST\",\"url\":\"/file/copy\"}],\"resource\":\"file\"}",
            drive_id = await getDriveId(), params = {
                fileId: file_id, shareId: shareId, driveId: drive_id, tmpFolderFileId: curTmpFolderFileId
            };
        params_str = jinja2(params_str, {
            data: params
        });
        await JadeLog.debug(`正在转存文件,文件id为:${file_id}`, true)
        let response_str = await auth("adrive/v2/batch", JSON.parse(params_str), shareToken, true);
        let response = aliExpection(response_str)
        if (response.code === 500 || response.code === 501 || response.code === 502 || response.code === 503 || response.code === 403) {
            if (response.code === 500) {
                await JadeLog.error("转存文件失败,失败详情:" + response.content)
                return copy(file_id);
            } else if (response.code === 501) {
                await JadeLog.error("转存文件失败,失败详情:" + response.content)
                return copy(file_id)
            } else if (response.code === 502) {
                await JadeLog.error("转存文件失败,失败原因为:转存文件夹不存在,失败详情:" + response.content)
                return null;
            } else if (response.code === 503) {
                await JadeLog.error("转存文件失败,失败原因为:转存文件夹大小被限制" + response.content)
                await clearFile()
                return copy(file_id)
            } else if (response.code === 403) {
                await JadeLog.error("转存文件失败,失败原因为:没有找到File Id,失败详情:" + response.content)
                return null;
            }
        }
        await JadeLog.debug(`转存文件成功,文件id为:${file_id},请求结果为:${response_str}`)
        copy_file_id = JSON.parse(response_str).responses[0].body.file_id;
        let file_dic = {}
        try {
            JSON.parse(await local.get("file", "file_id"))
        } catch (e) {
        }
        file_dic[file_id] = copy_file_id
        await local.set("file", "file_id", JSON.stringify(file_dic))
    }
    return copy_file_id;
}

async function deleteTmpFolderAndRecreate() {
    // 删除缓存文件夹
    let file_id = await tmpFolderExistsFunc();
    file_id && (await trashFile(file_id), await recyclebinClear());
    await getTempFileId();
}

//放入回车站
async function trashFile(file_id) {
    let params_str = "{\"requests\":[{\"body\":{\"file_id\":\"{{data.fileId}}\",\"drive_id\":\"{{data.driveId}}\"},\"headers\":{\"Content-Type\":\"application/json\"},\"id\":\"0\",\"method\":\"POST\",\"url\":\"/recyclebin/trash\"}],\"resource\":\"file\"}",
        drive_id = await getDriveId(), params = {
            fileId: file_id, driveId: drive_id
        };
    params_str = jinja2(params_str, {
        data: params
    });
    await JadeLog.debug(`正在准备删除文件,文件id为:${file_id}`, true)
    let response = await auth("v2/batch", JSON.parse(params_str), shareToken, true);
    await JadeLog.debug(`删除文件成功,文件id为:${file_id},请求结果为:${response}`)
    return true;
}

//清空回车站
async function recyclebinClear() {
    let drive_id = await getDriveId(), params = {
        drive_id: drive_id
    };
    await auth("v2/recyclebin/clear", params, shareToken, true);
    await JadeLog.info("清空回车站成功", true)
    return true;
}

async function createTmpFolder() {
    //创建文件夹
    let file_id = await tmpFolderExistsFunc();
    if (file_id) {
        await JadeLog.info("文件夹存在,无需重新创建")
        return file_id;
    }
    await JadeLog.debug("文件夹不存在,重新创建文件夹")
    let drive_id = await getDriveId(), params = {
        check_name_mode: "refuse", drive_id: drive_id, name: tmpFolderName, parent_file_id: "root", type: "folder"
    }, response_str = await oauthFunc("openFile/create", params, true);
    let response_json = JSON.parse(response_str);
    if (_.isEmpty(response_json.drive_id)) {
        await JadeLog.error(`创建文件夹失败,失败原因为:${response_str}`)
        return null;
    }
    await JadeLog.info(`创建文件夹成功`, true)
    return response_json.file_id;
}

async function tmpFolderExistsFunc() {
    let drive_id = await getDriveId(), params = {
        drive_id: drive_id, parent_file_id: "root", limit: 100, order_by: "updated_at", order_direction: "DESC"
    }, response_str = await oauthFunc("openFile/list", params, true);
    let response_json = JSON.parse(response_str);
    if (_.isEmpty(response_json.items)) {
        return false;
    }
    for (const item of response_json.items) {
        if (item.name === tmpFolderName) {
            return item.file_id;
        }
    }
    return false;
}


async function setToken(token) {
    // Token设置
    user.setRefreshToken(token);
    await refreshAccessToken(token);
    await refreshOpenToken();
}

export {
    initSome, setToken, clearFile, setShareId, getFileByShare, getVod, playerContent, playerContentByFlag, getTempFileId
};