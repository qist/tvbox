/*
* @File     : bilibili.js
* @Author   : jade
* @Date     : 2024/4/3 9:27
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : 哔哩哔哩
*/
import {Spider} from "./spider.js";
import * as Utils from "../lib/utils.js";
import {Crypto, _, load} from "../lib/cat.js";
import {VodDetail, VodShort} from "../lib/vod.js";

class BilibiliSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://www.bilibili.com"
        this.apiUrl = "https://api.bilibili.com"
        this.cookie = ""
        this.bili_jct = '';
        this.is_login = false
        this.is_vip = false
        this.vod_audio_id = {
            30280: 192000,
            30232: 132000,
            30216: 64000,
        };
        this.vod_codec = {
            // 13: 'AV1',
            12: 'HEVC',
            7: 'AVC',
        };

        this.play_url_obj = {
            80: "1080P 高清",
            64: "720P 高清",
            32: "420P 清晰",
            16: "360P 流畅"
        }
    }

    getHeader() {
        const headers = super.getHeader();
        if (!_.isEmpty(this.cookie)) {
            headers["cookie"] = this.cookie;
        }
        return headers;
    }


    initCookie(cookie) {
        this.cookie = cookie
        if (cookie.includes('bili_jct')) {
            this.bili_jct = cookie.split('bili_jct=')[1].split(";")[0];
        }
    }

    async spiderInit(Req) {
        this.is_login = await this.checkLogin()
        if (this.is_login) {
            await this.jadeLog.info("哔哩哔哩登录成功", true)
        } else {
            await this.jadeLog.error("哔哩哔哩登录失败", true)
        }
        if (Req === null) {
            // dash mpd 代理
            this.js2Base = await js2Proxy(true, this.siteType, this.siteKey, 'dash/', this.getHeader());
        } else {
            this.js2Base = await js2Proxy(Req, "dash", this.getHeader());
        }
    }

    async init(cfg) {
        await super.init(cfg);
        await this.initCookie(this.cfgObj["cookie"])
        await this.spiderInit(null)
        this.danmuStaus = true
    }

    getName() {
        return "🏰┃哔哩哔哩┃🏰"
    }

    getAppName() {
        return "哔哩哔哩"
    }

    getJSName() {
        return "bilibili"
    }

    getType() {
        return 3
    }

    async setClasses() {
        let $ = await this.getHtml(this.siteUrl)
        let navElements = $("[class=\"channel-items__left\"]").find("a")
        for (const navElement of navElements) {
            this.classes.push(this.getTypeDic($(navElement).text(), $(navElement).text()))
        }
        if (!_.isEmpty(this.bili_jct) && this.is_login) {
            this.classes.push(this.getTypeDic("历史记录", "历史记录"))
        }
    }

    async getFilter($) {
        return [
            {
                key: 'order',
                name: '排序',
                value: [
                    {n: '综合排序', v: '0'},
                    {n: '最多点击', v: 'click'},
                    {n: '最新发布', v: 'pubdate'},
                    {n: '最多弹幕', v: 'dm'},
                    {n: '最多收藏', v: 'stow'},
                ],
            },
            {
                key: 'duration',
                name: '时长',
                value: [
                    {n: '全部时长', v: '0'},
                    {n: '60分钟以上', v: '4'},
                    {n: '30~60分钟', v: '3'},
                    {n: '10~30分钟', v: '2'},
                    {n: '10分钟以下', v: '1'},
                ],
            },
        ];
    }

    async setFilterObj() {
        for (const typeDic of this.classes) {
            let type_id = typeDic["type_name"]
            if (type_id !== "最近更新" && type_id !== "历史记录") {
                this.filterObj[type_id] = await this.getFilter()
            }
        }
    }

    getFullTime(numberSec) {
        let totalSeconds = '';
        try {
            let timeParts = numberSec.split(":");
            let min = parseInt(timeParts[0]);
            let sec = parseInt(timeParts[1]);
            totalSeconds = min * 60 + sec;
        } catch (e) {
            totalSeconds = parseInt(numberSec);
        }
        if (isNaN(totalSeconds)) {
            return '无效输入';
        }
        if (totalSeconds >= 3600) {
            const hours = Math.floor(totalSeconds / 3600);
            const remainingSecondsAfterHours = totalSeconds % 3600;
            const minutes = Math.floor(remainingSecondsAfterHours / 60);
            const seconds = remainingSecondsAfterHours % 60;
            return `${hours}小时 ${minutes}分钟 ${seconds}秒`;
        } else {
            const minutes = Math.floor(totalSeconds / 60);
            const seconds = totalSeconds % 60;
            return `${minutes}分钟 ${seconds}秒`;
        }
    }

    removeTags(input) {
        return input.replace(/<[^>]*>/g, '');
    }

    async parseVodShortListFromJson(objList) {
        let vod_list = []
        for (const vodData of objList) {
            let vodShort = new VodShort()
            vodShort.vod_id = vodData["bvid"]
            if (vodData.hasOwnProperty("rcmd_reason")) {
                vodShort.vod_remarks = vodData["rcmd_reason"]["content"]
            } else {
                vodShort.vod_remarks = this.getFullTime(vodData["duration"])
            }

            vodShort.vod_name = this.removeTags(vodData["title"])
            let imageUrl = vodData["pic"];
            if (imageUrl.startsWith('//')) {
                imageUrl = 'https:' + imageUrl;
            }
            vodShort.vod_pic = imageUrl
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodDetailfromJson(obj, bvid) {
        let cd = this.getFullTime(obj["duration"]);
        const aid = obj.aid;
        let vodDetail = new VodDetail()
        vodDetail.vod_name = obj["title"]
        vodDetail.vod_pic = obj["pic"]
        vodDetail.type_name = obj["tname"]
        vodDetail.vod_remarks = cd
        vodDetail.vod_content = obj["desc"]

        let params = {"avid": aid, "cid": obj["cid"], "qn": "127", "fnval": 4048, "fourk": 1}
        let playUrlDatas = JSON.parse(await this.fetch(this.apiUrl + "/x/player/playurl", params, this.getHeader()));
        let playUrldDataList = playUrlDatas["data"];
        const accept_quality = playUrldDataList["accept_quality"];
        const accept_description = playUrldDataList["accept_description"];
        const qualityList = [];
        const descriptionList = [];

        for (let i = 0; i < accept_quality.length; i++) {
            if (!this.is_vip) {
                if (this.is_login) {
                    if (accept_quality[i] > 80) continue;
                } else {
                    if (accept_quality[i] > 32) continue;
                }

            }
            descriptionList.push(Utils.base64Encode(accept_description[i]));
            qualityList.push(accept_quality[i]);
        }
        let treeMap = {};
        const jSONArray = obj["pages"];
        let playList = [];
        for (let j = 0; j < jSONArray.length; j++) {
            const jSONObject6 = jSONArray[j];
            const cid = jSONObject6.cid;
            const playUrl = j + '$' + aid + '+' + cid + '+' + qualityList.join(':') + '+' + descriptionList.join(':');
            playList.push(playUrl);
        }
        if (this.catOpenStatus) {
            for (let quality of qualityList) {
                treeMap[`dash - ${this.play_url_obj[quality]}`] = playList.join("#")
            }
        } else {
            await this.jadeLog.warning("TV暂不支持Dash播放")
        }

        for (let quality of qualityList) {
            treeMap[`mp4 - ${this.play_url_obj[quality]}`] = playList.join("#")
        }
        let relatedParams = {"bvid": bvid}
        const relatedData = JSON.parse(await this.fetch(this.apiUrl + "/x/web-interface/archive/related", relatedParams, this.getHeader())).data;
        playList = [];
        for (let j = 0; j < relatedData.length; j++) {
            const jSONObject6 = relatedData[j];
            const cid = jSONObject6.cid;
            const title = jSONObject6.title;
            const aaid = jSONObject6.aid;
            const playUrl = title + '$' + aaid + '+' + cid + '+' + qualityList.join(':') + '+' + descriptionList.join(':');
            playList.push(playUrl);
        }
        if (this.catOpenStatus) {
            for (let quality of qualityList) {
                treeMap["相关" + ` - ${this.play_url_obj[quality]}`] = playList.join("#")
            }
        } else {
            await this.jadeLog.warning("TV暂不支持相关播放")
        }

        vodDetail.vod_play_from = Object.keys(treeMap).join("$$$");
        vodDetail.vod_play_url = Object.values(treeMap).join("$$$");
        return vodDetail
    }

    async setHomeVod() {
        let params = {"ps": 20}
        let content = await this.fetch(this.apiUrl + "/x/web-interface/popular", params, this.getHeader())
        this.homeVodList = await this.parseVodShortListFromJson(JSON.parse(content)["data"]["list"])

    }

    async setDetail(id) {
        const detailUrl = this.apiUrl + "/x/web-interface/view";
        let params = {"bvid": id}

        const detailData = JSON.parse(await this.fetch(detailUrl, params, this.getHeader())).data
        // 记录历史
        if (!_.isEmpty(this.bili_jct)) {
            const historyReport = this.apiUrl + '/x/v2/history/report';
            let dataPost = {
                aid: detailData.aid,
                cid: detailData.cid,
                csrf: this.bili_jct,
            }
            await this.post(historyReport, dataPost, this.getHeader(), "form");
        }
        this.vodDetail = await this.parseVodDetailfromJson(detailData, id)

    }

    findKeyByValue(obj, value) {
        for (const key in obj) {
            if (obj[key] === value) {
                return key;
            }
        }
        return null;
    }


    async setPlay(flag, id, flags) {
        const ids = id.split('+');
        const aid = ids[0];
        const cid = ids[1];
        let quality_name = flag.split(" - ")[1]
        let quality_id = this.findKeyByValue(this.play_url_obj, quality_name)
        this.danmuUrl = this.apiUrl + '/x/v1/dm/list.so?oid=' + cid;
        this.result.header = this.getHeader()
        if (flag.indexOf("dash") > -1 || flag.indexOf('相关') > -1) {
            // dash mpd 代理
            if (this.catOpenStatus) {
                this.playUrl = this.js2Base + Utils.base64Encode(aid + '+' + cid + '+' + quality_id)
            }

        } else if (flag.indexOf('mp4') > -1) {
            // 直链
            const url = this.apiUrl + `/x/player/playurl`;
            let params = {"avid": aid, "cid": cid, "qn": parseInt(quality_id), "fourk": "1"}
            const resp = JSON.parse(await this.fetch(url, params, this.getHeader()));
            const data = resp.data;
            this.playUrl = data["durl"][0].url;
        } else {
            // 音频外挂
            let urls = [];
            let audios = [];
            const url = this.siteUrl + "/x/player/playurl"
            let params = {"avid": aid, "cid": cid, "qn": quality_id, "fnval": 4048, "fourk": 1};
            let resp = JSON.parse(await this.fetch(url, params, this.getHeader()));
            const dash = resp.data.dash;
            const video = dash.video;
            const audio = dash.audio;
            for (let j = 0; j < video.length; j++) {
                const dashjson = video[j];
                if (dashjson.id === quality_id) {
                    for (const key in this.vod_codec) {
                        if (dashjson["codecid"] === key) {
                            urls.push(Utils.base64Decode(quality_id) + ' ' + this.vod_codec[key], dashjson["baseUrl"]);
                        }
                    }
                }
            }
            if (audios.length === 0) {
                for (let j = 0; j < audio.length; j++) {
                    const dashjson = audio[j];
                    for (const key in this.vod_audio_id) {
                        if (dashjson.id === key) {
                            audios.push({
                                title: _.floor(parseInt(this.vod_audio_id[key]) / 1024) + 'Kbps',
                                bit: this.vod_audio_id[key],
                                url: dashjson["baseUrl"],
                            });
                        }
                    }
                }
                audios = _.sortBy(audios, 'bit');
            }
            this.playUrl = urls
            this.extra = {"audio": audios}
        }
    }

    async checkLogin() {
        let result = JSON.parse(await this.fetch('https://api.bilibili.com/x/web-interface/nav', null, this.getHeader()));
        this.is_vip = result["data"]["vipStatus"]
        return result["data"]["isLogin"]
    }

    async setCategory(tid, pg, filter, extend) {
        let page;
        if (parseInt(pg) < 1) {
            page = 1;
        } else {
            page = parseInt(pg)
        }
        if (Object.keys(extend).length > 0 && extend.hasOwnProperty('tid') && extend['tid'].length > 0) {
            tid = extend['tid'];
        }
        let url = '';
        url = this.apiUrl + `/x/web-interface/search/type?search_type=video&keyword=${encodeURIComponent(tid)}`;

        if (Object.keys(extend).length > 0) {
            for (const k in extend) {
                if (k === 'tid') {
                    continue;
                }
                url += `&${encodeURIComponent(k)}=${encodeURIComponent(extend[k])}`;
            }
        }
        url += `&page=${encodeURIComponent(page)}`;
        if (tid === "历史记录") {
            url = this.apiUrl + "/x/v2/history?pn=" + page;
        }
        const data = JSON.parse(await this.fetch(url, null, this.getHeader())).data;
        let items = data.result;
        if (tid === "历史记录") {
            items = data;
        }
        this.vodList = await this.parseVodShortListFromJson(items)
    }

    async setSearch(wd, quick, pg) {
        const ext = {
            duration: '0',
        };
        let page = parseInt(pg)
        const limit = 20
        let resp = JSON.parse(await this.category(wd, page, true, ext));
        this.vodList = resp["list"]
        let pageCount = page;
        if (this.vodList.length === limit) {
            pageCount = page + 1;
        }
        this.result.setPage(page, pageCount, limit, pageCount)
    }

    getDashMedia(dash) {
        try {
            let qnid = dash.id;
            const codecid = dash["codecid"];
            const media_codecs = dash["codecs"];
            const media_bandwidth = dash["bandwidth"];
            const media_startWithSAP = dash["startWithSap"];
            const media_mimeType = dash.mimeType;
            const media_BaseURL = dash["baseUrl"].replace(/&/g, '&amp;');
            const media_SegmentBase_indexRange = dash["SegmentBase"]["indexRange"];
            const media_SegmentBase_Initialization = dash["SegmentBase"]["Initialization"];
            const mediaType = media_mimeType.split('/')[0];
            let media_type_params = '';

            if (mediaType === 'video') {
                const media_frameRate = dash.frameRate;
                const media_sar = dash["sar"];
                const media_width = dash.width;
                const media_height = dash.height;
                media_type_params = `height='${media_height}' width='${media_width}' frameRate='${media_frameRate}' sar='${media_sar}'`;
            } else if (mediaType === 'audio') {
                for (const key in this.vod_audio_id) {
                    if (qnid === key) {
                        const audioSamplingRate = this.vod_audio_id[key];
                        media_type_params = `numChannels='2' sampleRate='${audioSamplingRate}'`;
                    }
                }
            }
            qnid += '_' + codecid;
            return `<AdaptationSet lang="chi">
        <ContentComponent contentType="${mediaType}"/>
        <Representation id="${qnid}" bandwidth="${media_bandwidth}" codecs="${media_codecs}" mimeType="${media_mimeType}" ${media_type_params} startWithSAP="${media_startWithSAP}">
          <BaseURL>${media_BaseURL}</BaseURL>
          <SegmentBase indexRange="${media_SegmentBase_indexRange}">
            <Initialization range="${media_SegmentBase_Initialization}"/>
          </SegmentBase>
        </Representation>
      </AdaptationSet>`;
        } catch (e) {
            // Handle exceptions here
        }
    }

    getDash(ja, videoList, audioList) {
        const duration = ja.data.dash["duration"];
        const minBufferTime = ja.data.dash["minBufferTime"];
        return `<MPD xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:mpeg:dash:schema:mpd:2011" xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd" type="static" mediaPresentationDuration="PT${duration}S" minBufferTime="PT${minBufferTime}S" profiles="urn:mpeg:dash:profile:isoff-on-demand:2011">
      <Period duration="PT${duration}S" start="PT0S">
        ${videoList}
        ${audioList}
      </Period>
    </MPD>`;
    }

    async proxy(segments, headers) {
        let what = segments[0];
        let url = Utils.base64Decode(segments[1]);
        if (what === 'dash') {
            const ids = url.split('+');
            const aid = ids[0];
            const cid = ids[1];
            const str5 = ids[2];
            const urls = this.apiUrl + `/x/player/playurl?avid=${aid}&cid=${cid}&qn=${str5}&fnval=4048&fourk=1`;
            let videoList = '';
            let audioList = '';
            let content = await this.fetch(urls, null, headers);
            let resp = JSON.parse(content)
            const dash = resp.data.dash;
            const video = dash.video;
            const audio = dash.audio;
            for (let i = 0; i < video.length; i++) {
                // if (i > 0) continue; // 只取一个
                const dashjson = video[i];
                if (dashjson.id.toString() === str5) {
                    videoList += this.getDashMedia(dashjson);
                }
            }

            for (let i = 0; i < audio.length; i++) {
                // if (i > 0) continue;
                const ajson = audio[i];
                for (const key in this.vod_audio_id) {
                    if (ajson.id.toString() === key) {
                        audioList += this.getDashMedia(ajson);
                    }
                }
            }
            let mpd = this.getDash(resp, videoList, audioList);
            return JSON.stringify({
                code: 200,
                content: mpd,
                headers: {
                    'Content-Type': 'application/dash+xml',
                },
            });
        }
        return JSON.stringify({
            code: 500,
            content: '',
        });
    }

}

let spider = new BilibiliSpider()

async function init(cfg) {
    await spider.init(cfg)
}

async function home(filter) {
    return await spider.home(filter)
}

async function homeVod() {
    return await spider.homeVod()
}

async function category(tid, pg, filter, extend) {
    return await spider.category(tid, pg, filter, extend)
}

async function detail(id) {
    return await spider.detail(id)
}

async function play(flag, id, flags) {
    return await spider.play(flag, id, flags)
}

async function search(wd, quick) {
    return await spider.search(wd, quick)
}

async function proxy(segments, headers) {
    return await spider.proxy(segments, headers)
}

export function __jsEvalReturn() {
    return {
        init: init,
        home: home,
        homeVod: homeVod,
        category: category,
        detail: detail,
        play: play,
        search: search,
        proxy: proxy
    };
}

export {spider}