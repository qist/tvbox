import { __jsEvalReturn } from './kunyu77_open.js';

var spider = __jsEvalReturn();

function jsonParse(obj) {
    if (typeof obj === 'string') {
        return JSON.parse(obj);
    }
    return obj;
}

async function test() {
    var spType = null;
    var spVid = null;
    spType = '2';
    // spVid = '95873';

    await spider.init({ skey: 'siteKey', ext: '' });
    var classes = jsonParse(await spider.home(true));
    console.log(classes);
    var homeVod = jsonParse(await spider.homeVod());
    console.log(homeVod);
    if (classes.class && classes.class.length > 0) {
        var page = jsonParse(await spider.category(spType || classes.class[0].type_id, 0, undefined, {}));
        console.log(page);
        if (page.list && page.list.length > 0) {
            for (const k in page.list) {
                if (k >= 5) break;
                var detail = jsonParse(await spider.detail(spVid || page.list[k].vod_id));
                console.log(detail);
                if (detail.list && detail.list.length > 0) {
                    var pFlag = detail.list[0].vod_play_from.split('$$$');
                    var pUrls = detail.list[0].vod_play_url.split('$$$');
                    if (pFlag.length > 0 && pUrls.length > 0) {
                        for (const i in pFlag) {
                            var flag = pFlag[i];
                            var urls = pUrls[i].split('#');
                            if (urls.length > 0) {
                                var url = urls[0].split('$')[1];
                                console.log(flag, url);
                                var playUrl = await spider.play(flag, url, []);
                                console.log(playUrl);
                            }
                        }
                    }
                }
                if (spVid) break;
            }
        }
    }
    var search = jsonParse(await spider.search('奥特曼'));
    console.log(search);

    search = jsonParse(await spider.search('喜欢'));
    console.log(search);
}

export { test };
