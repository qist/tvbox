/*
* @File     : changzhang.js
* @Author   : jade
* @Date     : 2024/2/2 16:02
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/
import {Spider} from "./spider.js";
import {_, Crypto, load} from "../lib/cat.js";
import {VodDetail, VodShort} from "../lib/vod.js";
import * as Utils from "../lib/utils.js";
import { aliName, detailContent,initCloud,playContent, quarkName } from "../lib/cloud.js";

function cryptJs(text, key, iv, type) {
    let key_value = Crypto.enc.Utf8.parse(key || 'PBfAUnTdMjNDe6pL');
    let iv_value = Crypto.enc.Utf8.parse(iv || 'sENS6bVbwSfvnXrj');
    let content
    if (type) {
        content = Crypto.AES.encrypt(text, key_value, {
            iv: iv_value, mode: Crypto.mode.CBC, padding: Crypto.pad.Pkcs7
        })
    } else {
        content = Crypto.AES.decrypt(text, key_value, {
            iv: iv_value, padding: Crypto.pad.Pkcs7
        }).toString(Crypto.enc.Utf8)
    }
    return content
}


class ChangZhangSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://www.czys.top"
    }

    async init(cfg) {
        await super.init(cfg);
        await initCloud(this.cfgObj);
    }


    getName() {
        return "🏭️┃厂长直连┃🏭️"
    }

    getAppName() {
        return "厂长直连"
    }

    getJSName() {
        return "changzhang"
    }

    getType() {
        return 3
    }

    async getHtml(url = this.siteUrl, headers = this.getHeader()) {
        let response = await this.fetch(url, null, headers,false,true);
        let html = response["content"]
        if (!_.isEmpty(html) && html.indexOf("人机验证")===-1) {
            return load(html)
        } else {
            await this.jadeLog.error(`html获取失败`, true)
        }
    }
    getSearchHeader() {
        return {
            "Cookie": "cf_clearance=otYZbHg1safCIxkCtZfy9DPKbf1Gs_zUskkVDc0MVKM-1707026063-1-ATOpKnTLv9+pv171YE/rzxN/nmvGN9Mucx7vpwp0kW2vZb/cbtz5e2md2/ym7EE+9dT7pPBV+kQOg9vJx2v8cks=;myannoun=1;PHPSESSID=73386nobqugs7r3pb2ljcsp5q4",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/100.0.4896.77 Mobile/15E148 Safari/604.1",
            "Connection":"keep-alive",
            "Host":"www.czzy55.com"
        }
    }



    parseVodShortFromElement($, element) {
        let vodShort = new VodShort()
        let imgElement = $($(element).find("a")).find("img")[0]
        vodShort.vod_name = imgElement.attribs.alt
        vodShort.vod_pic = imgElement.attribs["data-original"]
        vodShort.vod_remarks = $($($(element).find("[class='hdinfo']")).find("span")).text()
        vodShort.vod_id = $(element).find("a")[0].attribs.href
        return vodShort
    }

    async parseVodShortListFromDoc($) {
        let vod_list = []
        let aList = $($("[class=\"mi_cont\"]").find("ul")).find("li")
        for (const a of aList) {
            vod_list.push(this.parseVodShortFromElement($, a))
        }
        return vod_list
    }

    async parseVodShortListFromDocByCategory($) {
        let vod_list = []
        let aList = $($("[class=\"mi_cont \"]").find("ul")).find("li")
        for (const a of aList) {
            vod_list.push(this.parseVodShortFromElement($, a))
        }
        return vod_list
    }

    async parseVodDetailFromDoc($) {
        let vodDetail = new VodDetail()
        let nodeElement = $("[class='dyxingq']")
        vodDetail.vod_pic = $(nodeElement).find("img")[0].attribs.src
        vodDetail.vod_name = $($(nodeElement).find("h1")[0]).text()
        vodDetail.vod_content = $($($("[class='yp_context']")).find("p")).text()
        let infoArray = $(nodeElement).find("[class='moviedteail_list']").find("li")
        let x = $(infoArray).text()
        for (const info of infoArray) {
            let content = $(info).text()
            if (content.indexOf("类型") > -1) {
                vodDetail.type_name = content.replaceAll("类型", "").replaceAll("：", "")
            } else if (content.indexOf("年份") > -1) {
                vodDetail.vod_year = content.replaceAll("年份", "").replaceAll("：", "")
            } else if (content.indexOf("地区") > -1) {
                vodDetail.vod_area = content.replaceAll("地区", "").replaceAll("：", "")
            } else if (content.indexOf("豆瓣") > -1) {
                vodDetail.vod_remarks = content.replaceAll("豆瓣", "").replaceAll("：", "")
            } else if (content.indexOf("主演") > -1) {
                vodDetail.vod_actor = content.replaceAll("主演", "").replaceAll("：", "")
            } else if (content.indexOf("导演") > -1) {
                vodDetail.vod_director = content.replaceAll("导演", "").replaceAll("：", "")
            } else if (content.indexOf("剧情") > -1) {
                vodDetail.vod_content = content.replaceAll("剧情", "").replaceAll("：", "")
            }
        }
        let vod_play_from_list = ["厂长资源"]

        let vodPlayList = $("[class='paly_list_btn']")
        let vod_play_list = []
        for (const v1 of vodPlayList) {
            let vodItems = []
            let aList = $(v1).find("a")
            for (const tA of aList) {
                let episodeUrl = tA.attribs.href
                let episodeName = $(tA).text().replaceAll("立即播放  (", "").replaceAll(")", "")
                vodItems.push(episodeName + "$" + episodeUrl)
            }
            vod_play_list.push(vodItems.join("#"))
        }
        let valify_formt_list = ["磁力链接", aliName]
        let otherPlayList = $("[class=\"ypbt_down_list\"]").find("li")
        let playVod = {}
        for (const otherPlay of otherPlayList) {
            let form_name = $(otherPlay).text()
            let is_valify = false
            for (const valify_format_name of valify_formt_list) {
                if (form_name.indexOf(valify_format_name) > -1) {
                    is_valify = true
                    if (form_name.indexOf(aliName) === -1) {
                        vod_play_from_list.push(valify_format_name)
                    }
                }
            }
            if (is_valify) {
                let vodItems = []
                for (const ciliPlayUrl of $(otherPlay).find("a")) {
                    let episodeUrl = ciliPlayUrl.attribs.href
                    if ($(otherPlay).text().indexOf(aliName)) {
                        playVod = await detailContent([episodeUrl])
                    } else {
                        let episodeName = Utils.getStrByRegex(/\[(.*?)]/, $(ciliPlayUrl).text())
                        vodItems.push(episodeName + "$" + episodeUrl)
                        playVod["磁力链接"] = (vodItems.join("#"))
                    }
                }
            }
        }
        vodDetail.vod_play_from = _.keys(playVod).join('$$$');
        vodDetail.vod_play_url = _.values(playVod).join('$$$');
        return vodDetail
    }

    async parseVodShortListFromDocBySearch($) {
        const items = $('div.search_list > ul > li');
        return _.map(items, (item) => {
            const img = $(item).find('img:first')[0];
            const a = $(item).find('a:first')[0];
            const hdinfo = $($(item).find('div.hdinfo')[0]).text().trim();
            const jidi = $($(item).find('div.jidi')[0]).text().trim();
            return {
                vod_id: a.attribs.href,
                vod_name: img.attribs.alt,
                vod_pic: img.attribs['data-original'],
                vod_remarks: jidi || hdinfo || '',
            };
        })
    }

    async setClasses() {
        const $ = await this.getHtml(this.siteUrl + '/movie_bt');
        const series = $('div#beautiful-taxonomy-filters-tax-movie_bt_series > a[cat-url*=movie_bt_series]');
        const tags = $('div#beautiful-taxonomy-filters-tax-movie_bt_tags > a');
        let tag = {
            key: 'tag', name: '类型', value: _.map(tags, (n) => {
                let v = n.attribs['cat-url'] || '';
                v = v.substring(v.lastIndexOf('/') + 1);
                return {n: n.children[0].data, v: v};
            }),
        };
        tag['init'] = tag.value[0].v;
        let classes = _.map(series, (s) => {
            let typeId = s.attribs['cat-url'];
            typeId = typeId.substring(typeId.lastIndexOf('/') + 1);
            this.filterObj[typeId] = [tag];
            return {
                type_id: typeId, type_name: s.children[0].data,
            };
        });
        const sortName = ['电影', '电视剧', '国产剧', '美剧', '韩剧', '日剧', '海外剧（其他）', '华语电影', '印度电影', '日本电影', '欧美电影', '韩国电影', '动画', '俄罗斯电影', '加拿大电影'];
        let sort_classes = _.sortBy(classes, (c) => {
            const index = sortName.indexOf(c.type_name);
            return index === -1 ? sortName.length : index;
        });
        for (const sort_class of sort_classes){
            let type_name = sort_class["type_name"]
            if (type_name!=="会员专区" && type_name !== "站长推荐"){
                this.classes.push(sort_class)
            }
        }
    }

    async setHomeVod() {
        let $ = await this.getHtml()
        this.homeVodList = await this.parseVodShortListFromDoc($)
    }

    async setCategory(tid, pg, filter, extend) {
        if (pg <= 0) pg = 1;
        const tag = extend.tag || '';
        const link = this.siteUrl + '/movie_bt' + (tag.length > 0 ? `/movie_bt_tags/${tag}` : '') + '/movie_bt_series/' + tid + (pg > 1 ? `/page/${pg}` : '');
        let $ = await this.getHtml(link)
        this.vodList = await this.parseVodShortListFromDocByCategory($)
    }

    async setDetail(id) {
        let $ = await this.getHtml(id)
        this.vodDetail = await this.parseVodDetailFromDoc($)
    }

    async setSearch(wd, quick) {
        const $ = await this.getHtml(this.siteUrl + '/xssearch?q=' + wd,this.getSearchHeader());
        let html = $.html()
        this.vodList = await this.parseVodShortListFromDocBySearch($)

    }

    async setPlay(flag, id, flags) {
        if (flag.indexOf(aliName) > -1 || flag.indexOf(quarkName) > -1) {
            this.playUrl = await playContent(flag, id, flags)
            this.result.setHeader(getHeaders(flag))
        } else {
            if (id.indexOf("magnet") > -1) {
                this.playUrl = id
            } else {
                let $ = await this.getHtml(id)
                const iframe = $('body iframe[src*=https]');
                if (iframe.length > 0) {
                    const iframeHtml = (await req(iframe[0].attribs.src, {
                        headers: {
                            Referer: id, 'User-Agent': Utils.CHROME,
                        },
                    })).content;
                    let player = Utils.getStrByRegex(/var player = "(.*?)"/, iframeHtml)
                    let rand = Utils.getStrByRegex(/var rand = "(.*?)"/, iframeHtml)
                    let content = JSON.parse(cryptJs(player, "VFBTzdujpR9FWBhe", rand))
                    this.playUrl = content["url"]
                } else {
                    const js = $('script:contains(window.wp_nonce)').html();
                    const group = js.match(/(var.*)eval\((\w*\(\w*\))\)/);
                    const md5 = Crypto;
                    const result = eval(group[1] + group[2]);
                    this.playUrl = result.match(/url:.*?['"](.*?)['"]/)[1];
                }
            }
        }
    }
}

let spider = new ChangZhangSpider()

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
        proxy: proxy,
        search: search,
    };
}
export {spider}