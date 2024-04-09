/*
* @File     : ffm3u8_open.js.js
* @Author   : jade
* @Date     : 2024/2/5 16:06
* @Email    : jadehh@1ive.com
* @Software : Samples
* @Desc     :
*/
import { _ } from './cat.js';
import * as HLS from './hls.js';

let key = 'ffm3u8';
let url = '';
let categories = [];
let siteKey = '';
let siteType = 0;

async function request(reqUrl, agentSp) {
    let res = await req(reqUrl, {
        method: 'get',
    });
    return JSON.parse(res.content);
}

async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
    url = cfg.ext.url;
    categories = cfg.ext.categories;
}

async function home(filter) {
    const data = await request(url);
    let classes = [];
    for (const cls of data.class) {
        const n = cls.type_name.toString().trim();
        if (categories && categories.length > 0) {
            if (categories.indexOf(n) < 0) continue;
        }
        classes.push({
            type_id: cls.type_id.toString(),
            type_name: n,
        });
    }
    if (categories && categories.length > 0) {
        classes = _.sortBy(classes, (p) => {
            return categories.indexOf(p.type_name);
        });
    }
    return {
        class: classes,
    };
}

async function homeVod() {
    return '{}';
}

async function category(tid, pg, filter, extend) {
    let page = pg || 1;
    if (page == 0) page = 1;
    const data = await request(url + `?ac=detail&t=${tid}&pg=${page}`);
    let videos = [];
    for (const vod of data.list) {
        videos.push({
            vod_id: vod.vod_id.toString(),
            vod_name: vod.vod_name.toString(),
            vod_pic: vod.vod_pic,
            vod_remarks: vod.vod_remarks,
        });
    }
    return {
        page: parseInt(data.page),
        pagecount: data.pagecount,
        total: data.total,
        list: videos,
    };
}

async function detail(id) {
    const data = (await request(url + `?ac=detail&ids=${id}`)).list[0];
    let vod = {
        vod_id: data.vod_id,
        vod_name: data.vod_name,
        vod_pic: data.vod_pic,
        type_name: data.type_name,
        vod_year: data.vod_year,
        vod_area: data.vod_area,
        vod_remarks: data.vod_remarks,
        vod_actor: data.vod_actor,
        vod_director: data.vod_director,
        vod_content: data.vod_content.trim(),
        vod_play_from: data.vod_play_from,
        vod_play_url: data.vod_play_url,
    };
    return {
        list: [vod],
    };
}

async function proxy(segments, headers, reqHeaders) {
    let what = segments[0];
    let segs = decodeURIComponent(segments[1]);
    if (what == 'hls') {
        function hlsHeader(data, hls) {
            let hlsHeaders = {};
            if (data.headers['content-length']) {
                Object.assign(hlsHeaders, data.headers, { 'content-length': hls.length.toString() });
            } else {
                Object.assign(hlsHeaders, data.headers);
            }
            delete hlsHeaders['transfer-encoding'];
            if (hlsHeaders['content-encoding'] == 'gzip') {
                delete hlsHeaders['content-encoding'];
            }
            return hlsHeaders;
        }
        const hlsData = await hlsCache(segs, headers);
        if (hlsData.variants) {
            // variants -> variants -> .... ignore
            const hls = HLS.stringify(hlsData.plist);
            return {
                code: hlsData.code,
                content: hls,
                headers: hlsHeader(hlsData, hls),
            };
        } else {
            const hls = HLS.stringify(hlsData.plist, (segment) => {
                return js2Proxy(false, siteType, siteKey, 'ts/' + encodeURIComponent(hlsData.key + '/' + segment.mediaSequenceNumber.toString()), headers);
            });
            return {
                code: hlsData.code,
                content: hls,
                headers: hlsHeader(hlsData, hls),
            };
        }
    } else if (what == 'ts') {
        const info = segs.split('/');
        const hlsKey = info[0];
        const segIdx = parseInt(info[1]);
        return await tsCache(hlsKey, segIdx, headers);
    }
    return '{}';
}

async function play(flag, id, flags) {
    try {
        const pUrls = await hls2Urls(id, {});
        for (let index = 1; index < pUrls.length; index += 2) {
            pUrls[index] = js2Proxy(false, siteType, siteKey, 'hls/' + encodeURIComponent(pUrls[index]), {});
        }
        pUrls.push('original');
        pUrls.push(id);
        return {
            parse: 0,
            url: pUrls,
        };
    } catch (e) {
        return {
            parse: 0,
            url: id,
        };
    }
}

async function search(wd, quick, pg) {
    let page = pg || 1;
    if (page == 0) page = 1;
    const data = await request(url + `?ac=detail&wd=${wd}`);
    let videos = [];
    for (const vod of data.list) {
        videos.push({
            vod_id: vod.vod_id.toString(),
            vod_name: vod.vod_name.toString(),
            vod_pic: vod.vod_pic,
            vod_remarks: vod.vod_remarks,
        });
    }
    return {
        page: parseInt(data.page),
        pagecount: data.pagecount,
        total: data.total,
        list: videos,
    };
}

const cacheRoot = 'hls_cache';
const hlsKeys = [];
const hlsPlistCaches = {};
const interrupts = {};
const downloadTask = {};
let currentDownloadHlsKey = '';

function hlsCacheInsert(key, data) {
    hlsKeys.push(key);
    hlsPlistCaches[key] = data;
    if (hlsKeys.length > 5) {
        const rmKey = hlsKeys.shift();
        hlsCacheRemove(rmKey);
    }
}

function hlsCacheRemove(key) {
    delete hlsPlistCaches[key];
    delete hlsKeys[key];
    new JSFile(cacheRoot + '/' + key).delete();
}

function plistUriResolve(baseUrl, plist) {
    if (plist.variants) {
        for (const v of plist.variants) {
            if (!v.uri.startsWith('http')) {
                v.uri = relative2Absolute(baseUrl, v.uri);
            }
        }
    }
    if (plist.segments) {
        for (const s of plist.segments) {
            if (!s.uri.startsWith('http')) {
                s.uri = relative2Absolute(baseUrl, s.uri);
            }
            if (s.key && s.key.uri && !s.key.uri.startsWith('http')) {
                s.key.uri = relative2Absolute(baseUrl, s.key.uri);
            }
        }
    }
    return plist;
}

async function hls2Urls(url, headers) {
    let urls = [];
    let resp = {};
    let tmpUrl = url;
    while (true) {
        resp = await req(tmpUrl, {
            headers: headers,
            redirect: 0,
        });
        if (resp.headers['location']) {
            tmpUrl = resp.headers['location'];
        } else {
            break;
        }
    }
    if (resp.code == 200) {
        var hls = resp.content;
        const plist = plistUriResolve(tmpUrl, HLS.parse(hls));
        if (plist.variants) {
            for (const vari of _.sortBy(plist.variants, (v) => -1 * v.bandwidth)) {
                urls.push(`proxy_${vari.resolution.width}x${vari.resolution.height}`);
                urls.push(vari.uri);
            }
        } else {
            urls.push('proxy');
            urls.push(url);
            const hlsKey = md5X(url);
            hlsCacheInsert(hlsKey, {
                code: resp.code,
                plist: plist,
                key: hlsKey,
                headers: resp.headers,
            });
        }
    }
    return urls;
}

async function hlsCache(url, headers) {
    const hlsKey = md5X(url);
    if (hlsPlistCaches[hlsKey]) {
        return hlsPlistCaches[hlsKey];
    }
    let resp = {};
    let tmpUrl = url;
    while (true) {
        resp = await req(tmpUrl, {
            headers: headers,
            redirect: 0,
        });
        if (resp.headers['location']) {
            tmpUrl = resp.headers['location'];
        } else {
            break;
        }
    }
    if (resp.code == 200) {
        var hls = resp.content;
        const plist = plistUriResolve(tmpUrl, HLS.parse(hls));
        hlsCacheInsert(hlsKey, {
            code: resp.code,
            plist: plist,
            key: hlsKey,
            headers: resp.headers,
        });
        return hlsPlistCaches[hlsKey];
    }
    return {};
}

async function tsCache(hlsKey, segmentIndex, headers) {
    if (!hlsPlistCaches[hlsKey]) {
        return {};
    }
    const plist = hlsPlistCaches[hlsKey].plist;
    const segments = plist.segments;

    let startFirst = !downloadTask[hlsKey];
    if (startFirst) {
        downloadTask[hlsKey] = {};
        for (const seg of segments) {
            const tk = md5X(seg.uri + seg.mediaSequenceNumber.toString());
            downloadTask[hlsKey][tk] = {
                file: cacheRoot + '/' + hlsKey + '/' + tk,
                uri: seg.uri,
                key: tk,
                index: seg.mediaSequenceNumber,
                order: seg.mediaSequenceNumber,
                state: -1,
                read: false,
            };
        }
    }

    // sort task
    for (const tk in downloadTask[hlsKey]) {
        const task = downloadTask[hlsKey][tk];
        if (task.index >= segmentIndex) {
            task.order = task.index - segmentIndex;
        } else {
            task.order = segments.length - segmentIndex + task.index;
        }
    }

    if (startFirst) {
        fixedCachePool(hlsKey, 5, headers);
    }

    const segment = segments[segmentIndex];
    const tsKey = md5X(segment.uri + segment.mediaSequenceNumber.toString());
    const task = downloadTask[hlsKey][tsKey];
    if (task.state == 1 || task.state == -1) {
        const file = new JSFile(task.file);
        if (await file.exist()) {
            task.state = 1;
            // download finish
            return {
                buffer: 3,
                code: 200,
                headers: {
                    connection: 'close',
                    'content-type': 'video/mp2t',
                },
                content: file,
            };
        } else {
            // file miss?? retry
            task.state = -1;
        }
    }
    if (task.state == -1) {
        // start download
        startTsTask(hlsKey, task, headers);
    }
    // wait read dwonload
    if (task.state == 0) {
        var stream = new JSProxyStream();
        stream.head(200, {
            connection: 'close',
            'content-type': 'video/mp2t',
        });
        let downloaded = 0;
        task.read = true;
        new Promise(async function (resolve, reject) {
            const f = new JSFile(task.file + '.dl');
            await f.open('r');
            (async function waitReadFile() {
                const s = await f.size();
                if (s > downloaded) {
                    var downloadBuf = await f.read(s - downloaded, downloaded);
                    await stream.write(downloadBuf);
                    downloaded = s;
                }
                if (task.state == 1 || task.state < 0) {
                    // finish error or done
                    stream.done();
                    await f.close();
                    await f.delete();
                    task.read = false;
                    resolve();
                    return;
                }
                setTimeout(waitReadFile, 5);
            })();
        });
        return {
            buffer: 3,
            content: stream,
        };
    }
}

async function startTsTask(hlsKey, task, headers) {
    if (task.state >= 0) return;
    if (!interrupts[hlsKey]) {
        return;
    }
    task.state = 0;
    if (await new JSFile(task.file).exist()) {
        task.state = 1;
        return;
    }
    const file = new JSFile(task.file + '.dl');
    await file.open('w');
    const resp = await req(task.uri, {
        buffer: 3,
        headers: headers,
        stream: file,
        timeout: [5000, 10000],
    });
    if (resp.error || resp.code >= 300) {
        await file.close();
        if (!task.read) {
            await file.delete();
        }
        task.state = -1;
        return;
    }
    await file.close();
    if (task.read) {
        await file.copy(task.file);
    } else {
        await file.move(task.file);
    }
    task.state = 1;
}

async function fixedCachePool(hlsKey, limit, headers) {
    // keep last cache task only
    if (currentDownloadHlsKey && currentDownloadHlsKey != hlsKey) {
        delete interrupts[currentDownloadHlsKey];
    }
    currentDownloadHlsKey = hlsKey;
    interrupts[hlsKey] = true;
    for (let index = 0; index < limit; index++) {
        if (!interrupts[hlsKey]) break;
        new Promise(function (resolve, reject) {
            (async function doTask() {
                if (!interrupts[hlsKey]) {
                    resolve();
                    return;
                }
                const tasks = _.pickBy(downloadTask[hlsKey], function (o) {
                    return o.state == -1;
                });
                const task = _.minBy(Object.values(tasks), function (o) {
                    return o.order;
                });
                if (!task) {
                    resolve();
                    return;
                }
                await startTsTask(hlsKey, task, headers);
                setTimeout(doTask, 5);
            })();
        });
    }
}

function relative2Absolute(base, relative) {
    var stack = base.split('/'),
        parts = relative.split('/');
    stack.pop();
    for (var i = 0; i < parts.length; i++) {
        if (parts[i] == '.') continue;
        if (parts[i] == '..') stack.pop();
        else stack.push(parts[i]);
    }
    return stack.join('/');
}
export {hls2Urls,hlsCache,tsCache}