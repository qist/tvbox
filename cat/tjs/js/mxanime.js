/*
* @File     : mxanime.js
* @Author   : jade
* @Date     : 2024/3/30 14:13
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     : MX动漫
 */
import {Spider} from "./spider.js";
import {VodDetail, VodShort} from "../lib/vod.js";
import {_, load} from "../lib/cat.js";
import * as Utils from "../lib/utils.js";


class MxAnimeSpider extends Spider {
    constructor() {
        super();
        this.siteUrl = "https://www.mxdm6.com/"
    }

    getName() {
        return "🍒┃MX动漫┃🍒"
    }

    getAppName() {
        return "MX动漫"
    }

    getJSName() {
        return "mxanime"
    }

    getType() {
        return 3
    }

    async setClasses() {
        let $ = await this.getHtml()
        let navElements = $($("[class=\"nav-menu-items\"]")[0]).find("[class=\"nav-menu-item  \"]")
        for (const navElement of navElements) {
            let element = $(navElement).find("a")[0]
            let type_name = element.attribs.title
            let type_id = element.attribs.href
            if (type_name !== "萌图") {
                this.classes.push(this.getTypeDic(type_name, Utils.getStrByRegex(/type\/(.*?).html/, type_id)))
            }

        }
    }

    async getFilter($) {
        let elements = $("[class=\"library-box scroll-box\"]")
        let extend_list = []
        for (let i = 0; i < elements.length; i++) {
            let extend_dic = {"key": (i + 1).toString(), "name": "", "value": []}
            if (i < elements.length - 1) {
                extend_dic["name"] = $($(elements[i]).find("a")[0]).text()
                extend_dic["value"].push({"n": "全部", "v": "0"})
                for (const ele of $(elements[i]).find("a").slice(1)) {
                    extend_dic["value"].push({"n": $(ele).text(), "v": $(ele).text()})
                }
                extend_list.push(extend_dic)
            } else {
                extend_dic["name"] = $($(elements[i]).find("a")[0]).text()
                extend_dic["value"] = [{"n": "全部", "v": "0"}, {
                    "n": $($(elements[i]).find("a")[1]).text(),
                    "v": "hits"
                }, {"n": $($(elements[i]).find("a")[2]).text(), "v": "score"}]

                extend_list.push(extend_dic)
            }

        }
        return extend_list

    }

    async setFilterObj() {
        for (const type_dic of this.classes) {
            let type_id = type_dic["type_id"]
            if (type_id !== "最近更新") {
                let $ = await this.getHtml(this.siteUrl + `/type/${type_id}.html`)
                this.filterObj[type_id] = await this.getFilter($)
            }
        }
    }

    parseVodShortFromElement($, vodElement) {
        let vodShort = new VodShort()
        let element = $($(vodElement).find("[class=\"module-item-titlebox\"]")).find("a")[0]
        vodShort.vod_id = element.attribs.href
        vodShort.vod_name = element.attribs.title
        vodShort.vod_pic = $($(vodElement).find("[class=\"module-item-pic\"]")).find("img")[0].attribs["data-src"]
        vodShort.vod_remarks = $($(vodElement).find("[class=\"module-item-text\"]")).text()
        return vodShort
    }

    async parseVodShortListFromDoc($) {
        let vod_list = []
        let vodElements = $("[class=\"module-list module-lines-list mxone-box\"]").find("[class=\"module-item\"]")
        for (const vodElement of vodElements) {
            let vodShort = await this.parseVodShortFromElement($, vodElement)
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodShortListFromDocByCategory($) {
        let vod_list = []
        let vodElements = $("[class=\"module-item\"]")
        for (const vodElement of vodElements) {
            let vodShort = await this.parseVodShortFromElement($, vodElement)
            vod_list.push(vodShort)
        }
        return vod_list
    }

    async parseVodShortListFromDocBySearch($) {
        let vod_list = []
        let vodElements = $("[class=\"module-search-item\"]")
        for (const vodElement of vodElements) {
            let vodShort = new VodShort()
            let element = $(vodElement).find("[class=\"video-serial\"]")[0]
            vodShort.vod_id = element.attribs.href
            vodShort.vod_name = element.attribs.title
            vodShort.vod_pic = $($(vodElement).find("[class=\"module-item-pic\"]")).find("img")[0].attribs["data-src"]
            let remarkElements = $($(vodElement).find("[class=\"video-info-item video-info-actor\"]").slice(-1)[0]).find("a")
            let remark_list = []
            for (const remarkElement of remarkElements){
                let remark = remarkElement.children[0].data
                remark_list.push(remark)
            }
            vodShort.vod_remarks = remark_list.join("*")
            vod_list.push(vodShort)

        }
        return vod_list
    }

    async parseVodDetailFromDoc($) {
        let vodDetail = new VodDetail()
        let vodElement = $("[class=\"video-info\"]")
        vodDetail.vod_pic = $("[class=\"module-item-pic\"]").find("img")[0].attribs["data-src"]
        vodDetail.vod_name = $($(vodElement).find("[class=\"page-title\"]")).text()
        let classElements = $(vodElement).find("[class=\"video-info-items\"]")
        for (const classElement of classElements){
            let text = $(classElement).text().replaceAll("\n","").replaceAll("\t","").replaceAll(" ","") + "end"
            if (text.indexOf("年份") > -1){
                vodDetail.vod_year = Utils.getStrByRegex(/年份：(.*?)end/,text).replaceAll("/","")
            }
            if(text.indexOf("备注") > -1){
                let x = Utils.getStrByRegex(/备注：(.*?)end/,text)
                vodDetail.vod_remarks = Utils.getStrByRegex(/备注：\/(.*?)end/,text)
            }
            if (text.indexOf("标签") > -1){
                vodDetail.type_name = Utils.getStrByRegex(/标签：(.*?)end/,text)
            }
            if (text.indexOf("剧情") > -1){
                vodDetail.vod_content = Utils.getStrByRegex(/剧情：(.*?)end/,text)
            }
        }
        let playFormatElemets = $("[class=\"module-tab-item tab-item\"]")
        let playUrlElements = $("[class=\"scroll-content\"]")
        let vod_play_from_list = []
        let vod_play_list = []
        for (let i = 0; i < playFormatElemets.length; i++) {
            let playFormatElement = playFormatElemets[i]
            vod_play_from_list.push(playFormatElement.attribs["data-dropdown-value"])
            let vodItems = []
            for (const playUrlElement of $(playUrlElements[i]).find("a")) {
                let episodeName = $(playUrlElement).text()
                let episodeUrl = playUrlElement.attribs.href
                vodItems.push(episodeName + "$" + episodeUrl)
            }
            vod_play_list.push(vodItems.join("#"))
        }
        vodDetail.vod_play_from = vod_play_from_list.join("$$$")
        vodDetail.vod_play_url = vod_play_list.join("$$$")
        return vodDetail
    }

    async setHomeVod() {
        let $ = await this.getHtml()
        this.homeVodList = await this.parseVodShortListFromDoc($)
    }

    getExtendValue(extent, key) {
        if (extent[key] === undefined) {
            return ""
        } else {
            if (extent[key] === "0") {
                return ""
            } else {
                return extent[key]
            }
        }
    }


    async setCategory(tid, pg, filter, extend) {
        await this.jadeLog.debug(`extend:${JSON.stringify(extend)}`)
        let type = this.getExtendValue(extend, "1")
        let time = this.getExtendValue(extend, "2")
        let word = this.getExtendValue(extend, "3")
        let sort = this.getExtendValue(extend, "4")
        let urlParams = [tid.toString(), "", sort, type, "", word, "", "", pg.toString(), "", "", time]
        let url = this.siteUrl + "/show/" + urlParams.join("-") + ".html"
        let $ = await this.getHtml(url)
        this.vodList = await this.parseVodShortListFromDocByCategory($)
    }
    async setDetail(id) {
        let $ = await this.getHtml(this.siteUrl + id)
        this.vodDetail = await this.parseVodDetailFromDoc($)
    }
    async setSearch(wd, quick) {
        let url = this.siteUrl + `/search/${wd}-------------.html`
        let $ = await this.getHtml(url)
        this.vodList = await this.parseVodShortListFromDocBySearch($)
    }

    async setPlay(flag, id, flags) {
        let $ = await this.getHtml(this.siteUrl + id)
        let playerConfig = JSON.parse(Utils.getStrByRegex(/var player_aaaa=(.*?)<\/script>/,$.html()))
        const m3mu8_url = "https://danmu.yhdmjx.com/m3u8.php?url=" + playerConfig["url"]
        const m3u8_res = await (await this.fetch(m3mu8_url,null,this.getHeader()));
        const m3u8_result = m3u8_res.match(/"url": getVideoInfo\("(.*?)"\),/)[1];
        const bt_token = m3u8_res.match(/<script>var bt_token = "(.*?)"/)[1];
        let m3u8_token_key = await (await this.fetch("https://danmu.yhdmjx.com/js/play.js",null,this.getHeader()));
        m3u8_token_key = m3u8_token_key.match(/var _token_key=CryptoJS\['enc'\]\['Utf8'\]\[_0x17f1\('67','qETJ'\)\]\((.*?\))/)[1];
        m3u8_token_key = this.decrypt_token_key(m3u8_token_key);
        this.playUrl = await this.getVideoInfo(m3u8_result, m3u8_token_key, bt_token);
    }

    decrypt_token_key(toekn_key){
        var _0xod4 = 'jsjiami.com.v6',
        _0x175e = [_0xod4, 'JMOsw6omwoDCmw==', 'wp3DkSx5Eg==', 'HB7CscOJfS3DuUjDv2bDjsOmwr3Cm8KcwoI=', 'fR/Dqg==', 'ShRGTcKa', 'w5Y8VBs=', 'esKYKQ==', 'FgIdwrPDnMKOw7k=', 'HhXCmA==', 'woNrRsKSwpnDvcKfw4g=', 'ezBn', 'w43DkcK5w4MaJiE=', 'w44Ob8KjwrjCrMKtUA==', 'HwtswqI=', 'YsKnwrRawro=', 'Sm/CpQXCjz4RH8ORSXw=', 'IsO6w64=', 'T8OeAQ==', 'VcK4Hg==', 'csOmfBJ4', 'd8OAcA5L', 'Tn4RL2s=', 'w7goGizCmw==', 'w6XDlcOGwpoY', 'TsK7wpNPwrg=', 'w7J1CzLCnsO+HA==', 'w4XDkcK0w5YXPg==', 'S8KoCcKS', 'PcKWHcK/Eg==', 'Z2oMJ3rCiw==', 'YsKMG8KMwo0=', 'QsOecgRIwp4=', 'dFzDkUUxw48Qw7nCmX3CicODCMKnw74IOg==', 'acO2KU1B', 'wrAnw6DDrg==', 'w5MsScKwwoA=', 'wohZG8KhBg==', 'b8OieSpZ', 'w4ZmEsORw6I=', 'w7jDhxvCh8KY', 'w7wQa8KFwr0=', 'IMObw4E3wqU=', 'JsOjw5Erwrg=', 'w6MwcsKOwqU=', 'b8KIwqF0wrs=', 'XhXDvT52', 'wrDCmirChSE=', 'w5t1wpvDuwE=', 'XA7CtsKeEA==', 'wonCvVthw78=', 'U8KPP8KMwq4=', 'wp7DhCxjGTU=', 'woPDoBdiEQ==', 'HjzCrE/Dvg==', 'SsOQOWHCgg==', 'w6NdwoXCkMOx', 'w6shYWQ/', 'eE/Cgg==', 'XW/Csj7CmDoA', 'w680OynCgcK5BA8=', 'w4PDoMOTwrog', 'w5R7wqbCpMOPwrMxUcOiM8OuMVLCisKKFsOXAcOWY8O6w5hM', 'WwjDoht0', 'PzXCiHHDiA==', 'QMOFaMKcfQ==', 'bz9bVsK+', 'w7Npwp/DsB9ONw==', 'EcOPBQ3Cig==', 'woHDnzk=', 'DsKQLxtd', 'R8OCJmk=', 'wp55O8On', 'bkXCmhTCqg==', 'w7vDgx3Cg8KU', 'w6nDo8KdAn8=', 'O8KwP8KEDw==', 'wqzCtCHCtCg=', 'w5nDgmYhw5c=', 'wp0OZsK+w4A=', 'wrFxe8KFwp/DvcKew4EbN8K7BMORMx3DuxtOVELChsOEIQ==', 'BMKWRDc=', 'IS5dw6nDhQ==', 'w6geeG8t', 'SsK/wohywpc=', 'LBlnw7jDkA==', 'wodiLsOg', 'Ig5Ow7/Dlw==', 'TMOOewRZwoQ=', 'LjnClV7DvA==', 'woZsO8KcPQ==', 'eWvClMKeKQ==', 'wq1KWsKswr8=', 'w4p+AGFa', 'C8O7F8K2CQcKFxxgwo5sfh3DpAFV', 'w6XDqMKoCw==', 'w6Z8wqnCpMOe', 'w6x/CHRhXhV/w7I=', 'wrvClndGw5Y=', 'VsKcwo5RwoA=', 'ZcK2BMKmLQ==', 'BCcPwofDvQ==', 'eGEsF20=', 'eMOcUglq', 'w4U9XEAMw4/Dm3rCuzpxTg/DvyDDvMONH8OTwpTCtsKbw6k=', 'VwXDkTxG', 'CzHCrl3DkQ==', 'w7PDkVovw4o=', 'dsONYDdj', 'w79pwr3Duh4=', 'w55kwoLCpMOR', 'w6gbc8KGwpw=', 'bCnCtMKCCg==', 'Php5w64=', 'w7x8wpfDtiQ=', 'w4TDk2AB', 'w7lowoHDtgQ=', 'DB/CsnjDuQ==', 'woTDl8K3wp4S', 'wr0Ewq7Dq8Oh', 'GmHCpGxN', 'w5/Dm2XDpw==', 'w5bDpsOCwqoA', 'YMKowphwwqc=', 'ahFuVsK9', 'w57DtEsbw7k=', 'w6LDo8Kq', 'UsKzE8KO', 'w6xlBFl9', 'WMOgIXbCiw==', 'DBhjw5fDhQ==', 'w6pUwoHCnsOs', 'ZF7CtsKiHg==', 'wos4w7wCwr0c', 'JlXCjlpyw5pMw6s=', 'TcO1N8K4wqE=', 'SMOzTcKYRw==', 'w4HDosOzwrUc', 'wqxdwqE2wrY=', 'A8OPGQjChw==', 'wpkxasOxBQ==', 'wpIZSA==', 'VsOnEEvChg==', 'bMOSZy93', 'c8OwZsKnRQ==', 'SsK/wpBHwoQ=', 'ccOsHVFf', 'w6ZKYMO8w6rDr8OrCHxdwqtdwrDDksOMccKZwobDpQPDgsOrAMKXF8OMPcOySsKuL8KLwq8vwr/DkjbDqsOCbRrCkcOTTFfDlsKkw7PChCM1wqTDisKawpHDt8KCQRY3w6DDgMKVw6M=', 'w7hYwq3ClsOa', 'Fic5wqLDiw==', 'KcKqHCVV', 'wqvDucKSwrs/', 'YcOfQcKPSQ==', 'wpjClmNRw7U=', 'wpHClSnCizg=', 'w4PDh8Kw', 'JsOYGwnCpw==', 'w5vDksK8w6sl', 'U8ORCHt+Rw==', 'woVxO8OSJQ==', 'b37Chw/Clw==', 'w6ViBXZlQg==', 'UwPCucKQCgU=', 'UMOeZgs=', 'MTLCtW7Dq2o=', 'wqAQwr/DqcOi', 'DiLDtsOOZsKEbsOrGm03EcKEwr/CplQ=', 'dzPDnRhP', 'wplgT8KBwow=', 'XUzCg8KF', 'K8KTCcKrCQ==', 'w6ZKJMOw', 'LxTCmn/DsA==', 'wooObcKBw6g=', 'w5djwofDoTQ=', 'VMOHeAts', 'Kw96w7bDig==', 'wogpw6crwps=', 'PDzDn8OcWQ==', 'wrfCoWxfw4E=', 'wrrDv8KDwoI+', 'w7hnwrjCssOq', 'w4LDrMOwwpMp', 'S2vCvyjCjic=', 'w6DDoT7CtcKNwoo=', 'wp1Lw5zCpj4=', 'RsOEGcKVwps=', 'woxlwo0twoM=', 'MAZYw7TDmg==', 'w7ENEC7CgA==', 'wolVw4jCryEqVMOYdg==', 'wp45w6cCwqY=', 'w6UhVHs1', 'QBZFW8KH', 'Ozhvw7vDkQ==', 'E8O4DAXCnA==', 'AcOXR8OZ', 'w4NhwqbCk8O6', 'f8OyScKpRRJTBQd9w4t3PgzCtRMQwrjDrUZ9Z8Od', 'A8OHw7Inwoc=', 'wqlQE8KHDg==', 'wqYbZMOVMg==', 'w57DuVwAw60=', 'W8OyQMKtVAk=', 'w60PBwXCng==', 'w4h7w70gw55WbHfDuR0VQ8K+asOxwoJn', 'w5rDhMK2w5gX', 'N0HCklc=', 'w58TTsK4wrg=', 'w7dXNMOhw79pwqBMw70=', 'SsKQCcKf', 'KSXCumrDug==', 'woc1w7gUwrEEw7s=', 'wplowqIvwoFGMQ==', 'acO9DcK+', 'UMKBwpJNwp1ZfA==', 'wpV+NsKCLQ==', 'w5PDrMOrwo4iwrcU', 'XHjCoyPCkw==', 'w5kOUsKkwqXCqcKm', 'QMKRAcKDDMK+AA==', 'bMKoNcKgwrc=', 'w6k0HTPClw==', 'wpUYYcOcBA==', 'w6k6BjnCnMK9', 'w5HDnncPw60=', 'jEsjiamLiI.coRVzmBz.v6gWBKxrg=='];
        (function (_0x2410c8, _0x4731c1, _0x21bfda) {
            var _0x12d6b4 = function (_0x56792e, _0x26ff38, _0x14a967, _0x1f013c, _0x21c988) {
                _0x26ff38 = _0x26ff38 >> 0x8,
                    _0x21c988 = 'po';
                var _0x10be12 = 'shift',
                    _0x47704d = 'push';
                if (_0x26ff38 < _0x56792e) {
                    while (--_0x56792e) {
                        _0x1f013c = _0x2410c8[_0x10be12]();
                        if (_0x26ff38 === _0x56792e) {
                            _0x26ff38 = _0x1f013c;
                            _0x14a967 = _0x2410c8[_0x21c988 + 'p']();
                        } else if (_0x26ff38 && _0x14a967['replace'](/[ELIRVzBzgWBKxrg=]/g, '') === _0x26ff38) {
                            _0x2410c8[_0x47704d](_0x1f013c);
                        }
                    }
                    _0x2410c8[_0x47704d](_0x2410c8[_0x10be12]());
                }
                return 0xa44cc;
            };
            return _0x12d6b4(++_0x4731c1, _0x21bfda) >> _0x4731c1 ^ _0x21bfda;
        }(_0x175e, 0x15c, 0x15c00));

        var _0x17f1 = function (_0x3abb24, _0x9f8a97) {
            _0x3abb24 = ~~'0x' ['concat'](_0x3abb24);
            var _0x411694 = _0x175e[_0x3abb24];
            if (_0x17f1['nIHPps'] === undefined) {
                (function () {
                    var _0x264909 = typeof window !== 'undefined' ? window : typeof process === 'object' && typeof require === 'function' && typeof global === 'object' ? global : this;
                    var _0x52b78f = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';
                    // _0x264909['atob'] || (_0x264909['atob'] = function (_0x202c2d) {
                    //     var _0x2e97e4 = String(_0x202c2d)['replace'](/=+$/, '');
                    //     for (var _0x488147 = 0x0,
                    //             _0x1702c1, _0x5d977a, _0x1a87f9 = 0x0,
                    //             _0x2378be = ''; _0x5d977a = _0x2e97e4['charAt'](_0x1a87f9++); ~_0x5d977a && (_0x1702c1 = _0x488147 % 0x4 ? _0x1702c1 * 0x40 + _0x5d977a : _0x5d977a, _0x488147++ % 0x4) ? _0x2378be += String['fromCharCode'](0xff & _0x1702c1 >> (-0x2 * _0x488147 & 0x6)) : 0x0) {
                    //         _0x5d977a = _0x52b78f['indexOf'](_0x5d977a);
                    //     }
                    //     return _0x2378be;
                    // });
                }());
                var _0x5cedb3 = function (_0x19b8a7, _0x9f8a97) {
                    var _0x2b0e6a = [],
                        _0x4f25fe = 0x0,
                        _0x29acd8,
                        _0x2643f2 = '',
                        _0x58e8bd = '';
                    _0x19b8a7 = atob(_0x19b8a7);
                    for (var _0x1ac59f = 0x0,
                            _0x3346bd = _0x19b8a7['length']; _0x1ac59f < _0x3346bd; _0x1ac59f++) {
                        _0x58e8bd += '%' + ('00' + _0x19b8a7['charCodeAt'](_0x1ac59f)['toString'](0x10))['slice'](-0x2);
                    }
                    _0x19b8a7 = decodeURIComponent(_0x58e8bd);
                    for (var _0xb0c930 = 0x0; _0xb0c930 < 0x100; _0xb0c930++) {
                        _0x2b0e6a[_0xb0c930] = _0xb0c930;
                    }
                    for (_0xb0c930 = 0x0; _0xb0c930 < 0x100; _0xb0c930++) {
                        _0x4f25fe = (_0x4f25fe + _0x2b0e6a[_0xb0c930] + _0x9f8a97['charCodeAt'](_0xb0c930 % _0x9f8a97['length'])) % 0x100;
                        _0x29acd8 = _0x2b0e6a[_0xb0c930];
                        _0x2b0e6a[_0xb0c930] = _0x2b0e6a[_0x4f25fe];
                        _0x2b0e6a[_0x4f25fe] = _0x29acd8;
                    }
                    _0xb0c930 = 0x0;
                    _0x4f25fe = 0x0;
                    for (var _0x4f50dd = 0x0; _0x4f50dd < _0x19b8a7['length']; _0x4f50dd++) {
                        _0xb0c930 = (_0xb0c930 + 0x1) % 0x100;
                        _0x4f25fe = (_0x4f25fe + _0x2b0e6a[_0xb0c930]) % 0x100;
                        _0x29acd8 = _0x2b0e6a[_0xb0c930];
                        _0x2b0e6a[_0xb0c930] = _0x2b0e6a[_0x4f25fe];
                        _0x2b0e6a[_0x4f25fe] = _0x29acd8;
                        _0x2643f2 += String['fromCharCode'](_0x19b8a7['charCodeAt'](_0x4f50dd) ^ _0x2b0e6a[(_0x2b0e6a[_0xb0c930] + _0x2b0e6a[_0x4f25fe]) % 0x100]);
                    }
                    return _0x2643f2;
                };
                _0x17f1['RtnfNa'] = _0x5cedb3;
                _0x17f1['afYpDj'] = {};
                _0x17f1['nIHPps'] = !![];
            }
            var _0x5dc739 = _0x17f1['afYpDj'][_0x3abb24];
            if (_0x5dc739 === undefined) {
                if (_0x17f1['OqAPEJ'] === undefined) {
                    _0x17f1['OqAPEJ'] = !![];
                }
                _0x411694 = _0x17f1['RtnfNa'](_0x411694, _0x9f8a97);
                _0x17f1['afYpDj'][_0x3abb24] = _0x411694;
            } else {
                _0x411694 = _0x5dc739;
            }
            return _0x411694;
        };
        return eval(toekn_key)
    }

     async getVideoInfo(data,key,iv) {
                /*
        Crypto v3.1.2
        code.google.com/p/crypto-js
        (c) 2009-2013 by Jeff Mott. All rights reserved.
        code.google.com/p/crypto-js/wiki/License
        */
        var Crypto=Crypto||function(u,p){var d={},l=d.lib={},s=function(){},t=l.Base={extend:function(a){s.prototype=this;var c=new s;a&&c.mixIn(a);c.hasOwnProperty("init")||(c.init=function(){c.$super.init.apply(this,arguments)});c.init.prototype=c;c.$super=this;return c},create:function(){var a=this.extend();a.init.apply(a,arguments);return a},init:function(){},mixIn:function(a){for(var c in a)a.hasOwnProperty(c)&&(this[c]=a[c]);a.hasOwnProperty("toString")&&(this.toString=a.toString)},clone:function(){return this.init.prototype.extend(this)}},
        r=l.WordArray=t.extend({init:function(a,c){a=this.words=a||[];this.sigBytes=c!=p?c:4*a.length},toString:function(a){return(a||v).stringify(this)},concat:function(a){var c=this.words,e=a.words,j=this.sigBytes;a=a.sigBytes;this.clamp();if(j%4)for(var k=0;k<a;k++)c[j+k>>>2]|=(e[k>>>2]>>>24-8*(k%4)&255)<<24-8*((j+k)%4);else if(65535<e.length)for(k=0;k<a;k+=4)c[j+k>>>2]=e[k>>>2];else c.push.apply(c,e);this.sigBytes+=a;return this},clamp:function(){var a=this.words,c=this.sigBytes;a[c>>>2]&=4294967295<<
        32-8*(c%4);a.length=u.ceil(c/4)},clone:function(){var a=t.clone.call(this);a.words=this.words.slice(0);return a},random:function(a){for(var c=[],e=0;e<a;e+=4)c.push(4294967296*u.random()|0);return new r.init(c,a)}}),w=d.enc={},v=w.Hex={stringify:function(a){var c=a.words;a=a.sigBytes;for(var e=[],j=0;j<a;j++){var k=c[j>>>2]>>>24-8*(j%4)&255;e.push((k>>>4).toString(16));e.push((k&15).toString(16))}return e.join("")},parse:function(a){for(var c=a.length,e=[],j=0;j<c;j+=2)e[j>>>3]|=parseInt(a.substr(j,
        2),16)<<24-4*(j%8);return new r.init(e,c/2)}},b=w.Latin1={stringify:function(a){var c=a.words;a=a.sigBytes;for(var e=[],j=0;j<a;j++)e.push(String.fromCharCode(c[j>>>2]>>>24-8*(j%4)&255));return e.join("")},parse:function(a){for(var c=a.length,e=[],j=0;j<c;j++)e[j>>>2]|=(a.charCodeAt(j)&255)<<24-8*(j%4);return new r.init(e,c)}},x=w.Utf8={stringify:function(a){try{return decodeURIComponent(escape(b.stringify(a)))}catch(c){throw Error("Malformed UTF-8 data");}},parse:function(a){return b.parse(unescape(encodeURIComponent(a)))}},
        q=l.BufferedBlockAlgorithm=t.extend({reset:function(){this._data=new r.init;this._nDataBytes=0},_append:function(a){"string"==typeof a&&(a=x.parse(a));this._data.concat(a);this._nDataBytes+=a.sigBytes},_process:function(a){var c=this._data,e=c.words,j=c.sigBytes,k=this.blockSize,b=j/(4*k),b=a?u.ceil(b):u.max((b|0)-this._minBufferSize,0);a=b*k;j=u.min(4*a,j);if(a){for(var q=0;q<a;q+=k)this._doProcessBlock(e,q);q=e.splice(0,a);c.sigBytes-=j}return new r.init(q,j)},clone:function(){var a=t.clone.call(this);
        a._data=this._data.clone();return a},_minBufferSize:0});l.Hasher=q.extend({cfg:t.extend(),init:function(a){this.cfg=this.cfg.extend(a);this.reset()},reset:function(){q.reset.call(this);this._doReset()},update:function(a){this._append(a);this._process();return this},finalize:function(a){a&&this._append(a);return this._doFinalize()},blockSize:16,_createHelper:function(a){return function(b,e){return(new a.init(e)).finalize(b)}},_createHmacHelper:function(a){return function(b,e){return(new n.HMAC.init(a,
        e)).finalize(b)}}});var n=d.algo={};return d}(Math);
        (function(){var u=Crypto,p=u.lib.WordArray;u.enc.Base64={stringify:function(d){var l=d.words,p=d.sigBytes,t=this._map;d.clamp();d=[];for(var r=0;r<p;r+=3)for(var w=(l[r>>>2]>>>24-8*(r%4)&255)<<16|(l[r+1>>>2]>>>24-8*((r+1)%4)&255)<<8|l[r+2>>>2]>>>24-8*((r+2)%4)&255,v=0;4>v&&r+0.75*v<p;v++)d.push(t.charAt(w>>>6*(3-v)&63));if(l=t.charAt(64))for(;d.length%4;)d.push(l);return d.join("")},parse:function(d){var l=d.length,s=this._map,t=s.charAt(64);t&&(t=d.indexOf(t),-1!=t&&(l=t));for(var t=[],r=0,w=0;w<
        l;w++)if(w%4){var v=s.indexOf(d.charAt(w-1))<<2*(w%4),b=s.indexOf(d.charAt(w))>>>6-2*(w%4);t[r>>>2]|=(v|b)<<24-8*(r%4);r++}return p.create(t,r)},_map:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="}})();
        (function(u){function p(b,n,a,c,e,j,k){b=b+(n&a|~n&c)+e+k;return(b<<j|b>>>32-j)+n}function d(b,n,a,c,e,j,k){b=b+(n&c|a&~c)+e+k;return(b<<j|b>>>32-j)+n}function l(b,n,a,c,e,j,k){b=b+(n^a^c)+e+k;return(b<<j|b>>>32-j)+n}function s(b,n,a,c,e,j,k){b=b+(a^(n|~c))+e+k;return(b<<j|b>>>32-j)+n}for(var t=Crypto,r=t.lib,w=r.WordArray,v=r.Hasher,r=t.algo,b=[],x=0;64>x;x++)b[x]=4294967296*u.abs(u.sin(x+1))|0;r=r.MD5=v.extend({_doReset:function(){this._hash=new w.init([1732584193,4023233417,2562383102,271733878])},
        _doProcessBlock:function(q,n){for(var a=0;16>a;a++){var c=n+a,e=q[c];q[c]=(e<<8|e>>>24)&16711935|(e<<24|e>>>8)&4278255360}var a=this._hash.words,c=q[n+0],e=q[n+1],j=q[n+2],k=q[n+3],z=q[n+4],r=q[n+5],t=q[n+6],w=q[n+7],v=q[n+8],A=q[n+9],B=q[n+10],C=q[n+11],u=q[n+12],D=q[n+13],E=q[n+14],x=q[n+15],f=a[0],m=a[1],g=a[2],h=a[3],f=p(f,m,g,h,c,7,b[0]),h=p(h,f,m,g,e,12,b[1]),g=p(g,h,f,m,j,17,b[2]),m=p(m,g,h,f,k,22,b[3]),f=p(f,m,g,h,z,7,b[4]),h=p(h,f,m,g,r,12,b[5]),g=p(g,h,f,m,t,17,b[6]),m=p(m,g,h,f,w,22,b[7]),
        f=p(f,m,g,h,v,7,b[8]),h=p(h,f,m,g,A,12,b[9]),g=p(g,h,f,m,B,17,b[10]),m=p(m,g,h,f,C,22,b[11]),f=p(f,m,g,h,u,7,b[12]),h=p(h,f,m,g,D,12,b[13]),g=p(g,h,f,m,E,17,b[14]),m=p(m,g,h,f,x,22,b[15]),f=d(f,m,g,h,e,5,b[16]),h=d(h,f,m,g,t,9,b[17]),g=d(g,h,f,m,C,14,b[18]),m=d(m,g,h,f,c,20,b[19]),f=d(f,m,g,h,r,5,b[20]),h=d(h,f,m,g,B,9,b[21]),g=d(g,h,f,m,x,14,b[22]),m=d(m,g,h,f,z,20,b[23]),f=d(f,m,g,h,A,5,b[24]),h=d(h,f,m,g,E,9,b[25]),g=d(g,h,f,m,k,14,b[26]),m=d(m,g,h,f,v,20,b[27]),f=d(f,m,g,h,D,5,b[28]),h=d(h,f,
        m,g,j,9,b[29]),g=d(g,h,f,m,w,14,b[30]),m=d(m,g,h,f,u,20,b[31]),f=l(f,m,g,h,r,4,b[32]),h=l(h,f,m,g,v,11,b[33]),g=l(g,h,f,m,C,16,b[34]),m=l(m,g,h,f,E,23,b[35]),f=l(f,m,g,h,e,4,b[36]),h=l(h,f,m,g,z,11,b[37]),g=l(g,h,f,m,w,16,b[38]),m=l(m,g,h,f,B,23,b[39]),f=l(f,m,g,h,D,4,b[40]),h=l(h,f,m,g,c,11,b[41]),g=l(g,h,f,m,k,16,b[42]),m=l(m,g,h,f,t,23,b[43]),f=l(f,m,g,h,A,4,b[44]),h=l(h,f,m,g,u,11,b[45]),g=l(g,h,f,m,x,16,b[46]),m=l(m,g,h,f,j,23,b[47]),f=s(f,m,g,h,c,6,b[48]),h=s(h,f,m,g,w,10,b[49]),g=s(g,h,f,m,
        E,15,b[50]),m=s(m,g,h,f,r,21,b[51]),f=s(f,m,g,h,u,6,b[52]),h=s(h,f,m,g,k,10,b[53]),g=s(g,h,f,m,B,15,b[54]),m=s(m,g,h,f,e,21,b[55]),f=s(f,m,g,h,v,6,b[56]),h=s(h,f,m,g,x,10,b[57]),g=s(g,h,f,m,t,15,b[58]),m=s(m,g,h,f,D,21,b[59]),f=s(f,m,g,h,z,6,b[60]),h=s(h,f,m,g,C,10,b[61]),g=s(g,h,f,m,j,15,b[62]),m=s(m,g,h,f,A,21,b[63]);a[0]=a[0]+f|0;a[1]=a[1]+m|0;a[2]=a[2]+g|0;a[3]=a[3]+h|0},_doFinalize:function(){var b=this._data,n=b.words,a=8*this._nDataBytes,c=8*b.sigBytes;n[c>>>5]|=128<<24-c%32;var e=u.floor(a/
        4294967296);n[(c+64>>>9<<4)+15]=(e<<8|e>>>24)&16711935|(e<<24|e>>>8)&4278255360;n[(c+64>>>9<<4)+14]=(a<<8|a>>>24)&16711935|(a<<24|a>>>8)&4278255360;b.sigBytes=4*(n.length+1);this._process();b=this._hash;n=b.words;for(a=0;4>a;a++)c=n[a],n[a]=(c<<8|c>>>24)&16711935|(c<<24|c>>>8)&4278255360;return b},clone:function(){var b=v.clone.call(this);b._hash=this._hash.clone();return b}});t.MD5=v._createHelper(r);t.HmacMD5=v._createHmacHelper(r)})(Math);
        (function(){var u=Crypto,p=u.lib,d=p.Base,l=p.WordArray,p=u.algo,s=p.EvpKDF=d.extend({cfg:d.extend({keySize:4,hasher:p.MD5,iterations:1}),init:function(d){this.cfg=this.cfg.extend(d)},compute:function(d,r){for(var p=this.cfg,s=p.hasher.create(),b=l.create(),u=b.words,q=p.keySize,p=p.iterations;u.length<q;){n&&s.update(n);var n=s.update(d).finalize(r);s.reset();for(var a=1;a<p;a++)n=s.finalize(n),s.reset();b.concat(n)}b.sigBytes=4*q;return b}});u.EvpKDF=function(d,l,p){return s.create(p).compute(d,
        l)}})();
        Crypto.lib.Cipher||function(u){var p=Crypto,d=p.lib,l=d.Base,s=d.WordArray,t=d.BufferedBlockAlgorithm,r=p.enc.Base64,w=p.algo.EvpKDF,v=d.Cipher=t.extend({cfg:l.extend(),createEncryptor:function(e,a){return this.create(this._ENC_XFORM_MODE,e,a)},createDecryptor:function(e,a){return this.create(this._DEC_XFORM_MODE,e,a)},init:function(e,a,b){this.cfg=this.cfg.extend(b);this._xformMode=e;this._key=a;this.reset()},reset:function(){t.reset.call(this);this._doReset()},process:function(e){this._append(e);return this._process()},
        finalize:function(e){e&&this._append(e);return this._doFinalize()},keySize:4,ivSize:4,_ENC_XFORM_MODE:1,_DEC_XFORM_MODE:2,_createHelper:function(e){return{encrypt:function(b,k,d){return("string"==typeof k?c:a).encrypt(e,b,k,d)},decrypt:function(b,k,d){return("string"==typeof k?c:a).decrypt(e,b,k,d)}}}});d.StreamCipher=v.extend({_doFinalize:function(){return this._process(!0)},blockSize:1});var b=p.mode={},x=function(e,a,b){var c=this._iv;c?this._iv=u:c=this._prevBlock;for(var d=0;d<b;d++)e[a+d]^=
        c[d]},q=(d.BlockCipherMode=l.extend({createEncryptor:function(e,a){return this.Encryptor.create(e,a)},createDecryptor:function(e,a){return this.Decryptor.create(e,a)},init:function(e,a){this._cipher=e;this._iv=a}})).extend();q.Encryptor=q.extend({processBlock:function(e,a){var b=this._cipher,c=b.blockSize;x.call(this,e,a,c);b.encryptBlock(e,a);this._prevBlock=e.slice(a,a+c)}});q.Decryptor=q.extend({processBlock:function(e,a){var b=this._cipher,c=b.blockSize,d=e.slice(a,a+c);b.decryptBlock(e,a);x.call(this,
        e,a,c);this._prevBlock=d}});b=b.CBC=q;q=(p.pad={}).Pkcs7={pad:function(a,b){for(var c=4*b,c=c-a.sigBytes%c,d=c<<24|c<<16|c<<8|c,l=[],n=0;n<c;n+=4)l.push(d);c=s.create(l,c);a.concat(c)},unpad:function(a){a.sigBytes-=a.words[a.sigBytes-1>>>2]&255}};d.BlockCipher=v.extend({cfg:v.cfg.extend({mode:b,padding:q}),reset:function(){v.reset.call(this);var a=this.cfg,b=a.iv,a=a.mode;if(this._xformMode==this._ENC_XFORM_MODE)var c=a.createEncryptor;else c=a.createDecryptor,this._minBufferSize=1;this._mode=c.call(a,
        this,b&&b.words)},_doProcessBlock:function(a,b){this._mode.processBlock(a,b)},_doFinalize:function(){var a=this.cfg.padding;if(this._xformMode==this._ENC_XFORM_MODE){a.pad(this._data,this.blockSize);var b=this._process(!0)}else b=this._process(!0),a.unpad(b);return b},blockSize:4});var n=d.CipherParams=l.extend({init:function(a){this.mixIn(a)},toString:function(a){return(a||this.formatter).stringify(this)}}),b=(p.format={}).OpenSSL={stringify:function(a){var b=a.ciphertext;a=a.salt;return(a?s.create([1398893684,
        1701076831]).concat(a).concat(b):b).toString(r)},parse:function(a){a=r.parse(a);var b=a.words;if(1398893684==b[0]&&1701076831==b[1]){var c=s.create(b.slice(2,4));b.splice(0,4);a.sigBytes-=16}return n.create({ciphertext:a,salt:c})}},a=d.SerializableCipher=l.extend({cfg:l.extend({format:b}),encrypt:function(a,b,c,d){d=this.cfg.extend(d);var l=a.createEncryptor(c,d);b=l.finalize(b);l=l.cfg;return n.create({ciphertext:b,key:c,iv:l.iv,algorithm:a,mode:l.mode,padding:l.padding,blockSize:a.blockSize,formatter:d.format})},
        decrypt:function(a,b,c,d){d=this.cfg.extend(d);b=this._parse(b,d.format);return a.createDecryptor(c,d).finalize(b.ciphertext)},_parse:function(a,b){return"string"==typeof a?b.parse(a,this):a}}),p=(p.kdf={}).OpenSSL={execute:function(a,b,c,d){d||(d=s.random(8));a=w.create({keySize:b+c}).compute(a,d);c=s.create(a.words.slice(b),4*c);a.sigBytes=4*b;return n.create({key:a,iv:c,salt:d})}},c=d.PasswordBasedCipher=a.extend({cfg:a.cfg.extend({kdf:p}),encrypt:function(b,c,d,l){l=this.cfg.extend(l);d=l.kdf.execute(d,
        b.keySize,b.ivSize);l.iv=d.iv;b=a.encrypt.call(this,b,c,d.key,l);b.mixIn(d);return b},decrypt:function(b,c,d,l){l=this.cfg.extend(l);c=this._parse(c,l.format);d=l.kdf.execute(d,b.keySize,b.ivSize,c.salt);l.iv=d.iv;return a.decrypt.call(this,b,c,d.key,l)}})}();
        (function(){for(var u=Crypto,p=u.lib.BlockCipher,d=u.algo,l=[],s=[],t=[],r=[],w=[],v=[],b=[],x=[],q=[],n=[],a=[],c=0;256>c;c++)a[c]=128>c?c<<1:c<<1^283;for(var e=0,j=0,c=0;256>c;c++){var k=j^j<<1^j<<2^j<<3^j<<4,k=k>>>8^k&255^99;l[e]=k;s[k]=e;var z=a[e],F=a[z],G=a[F],y=257*a[k]^16843008*k;t[e]=y<<24|y>>>8;r[e]=y<<16|y>>>16;w[e]=y<<8|y>>>24;v[e]=y;y=16843009*G^65537*F^257*z^16843008*e;b[k]=y<<24|y>>>8;x[k]=y<<16|y>>>16;q[k]=y<<8|y>>>24;n[k]=y;e?(e=z^a[a[a[G^z]]],j^=a[a[j]]):e=j=1}var H=[0,1,2,4,8,
        16,32,64,128,27,54],d=d.AES=p.extend({_doReset:function(){for(var a=this._key,c=a.words,d=a.sigBytes/4,a=4*((this._nRounds=d+6)+1),e=this._keySchedule=[],j=0;j<a;j++)if(j<d)e[j]=c[j];else{var k=e[j-1];j%d?6<d&&4==j%d&&(k=l[k>>>24]<<24|l[k>>>16&255]<<16|l[k>>>8&255]<<8|l[k&255]):(k=k<<8|k>>>24,k=l[k>>>24]<<24|l[k>>>16&255]<<16|l[k>>>8&255]<<8|l[k&255],k^=H[j/d|0]<<24);e[j]=e[j-d]^k}c=this._invKeySchedule=[];for(d=0;d<a;d++)j=a-d,k=d%4?e[j]:e[j-4],c[d]=4>d||4>=j?k:b[l[k>>>24]]^x[l[k>>>16&255]]^q[l[k>>>
        8&255]]^n[l[k&255]]},encryptBlock:function(a,b){this._doCryptBlock(a,b,this._keySchedule,t,r,w,v,l)},decryptBlock:function(a,c){var d=a[c+1];a[c+1]=a[c+3];a[c+3]=d;this._doCryptBlock(a,c,this._invKeySchedule,b,x,q,n,s);d=a[c+1];a[c+1]=a[c+3];a[c+3]=d},_doCryptBlock:function(a,b,c,d,e,j,l,f){for(var m=this._nRounds,g=a[b]^c[0],h=a[b+1]^c[1],k=a[b+2]^c[2],n=a[b+3]^c[3],p=4,r=1;r<m;r++)var q=d[g>>>24]^e[h>>>16&255]^j[k>>>8&255]^l[n&255]^c[p++],s=d[h>>>24]^e[k>>>16&255]^j[n>>>8&255]^l[g&255]^c[p++],t=
        d[k>>>24]^e[n>>>16&255]^j[g>>>8&255]^l[h&255]^c[p++],n=d[n>>>24]^e[g>>>16&255]^j[h>>>8&255]^l[k&255]^c[p++],g=q,h=s,k=t;q=(f[g>>>24]<<24|f[h>>>16&255]<<16|f[k>>>8&255]<<8|f[n&255])^c[p++];s=(f[h>>>24]<<24|f[k>>>16&255]<<16|f[n>>>8&255]<<8|f[g&255])^c[p++];t=(f[k>>>24]<<24|f[n>>>16&255]<<16|f[g>>>8&255]<<8|f[h&255])^c[p++];n=(f[n>>>24]<<24|f[g>>>16&255]<<16|f[h>>>8&255]<<8|f[k&255])^c[p++];a[b]=q;a[b+1]=s;a[b+2]=t;a[b+3]=n},keySize:8});u.AES=p._createHelper(d)})();

        iv = Crypto.enc.Utf8.parse(iv);
        key = Crypto.enc.Utf8.parse(key);

        let result =  Crypto.AES.decrypt(data, key,
            {
                iv : iv,
                mode : Crypto.mode.CBC,
            })
        return Crypto.enc.Utf8.stringify(result).toString();
    }


}


let spider = new MxAnimeSpider()

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