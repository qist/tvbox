globalThis.h_ost = 'http://v.lkuys.cn/';

globalThis.vodlist = function($t, $pg) {
    const currentTimestamp = parseInt(Date.now() / 1000, 10);
    const url = h_ost + '/v2/home/type_search';
    const hx = CryptoJS.MD5('kj5649ertj84ks89r4jh8s45hf84hjfds04k' + currentTimestamp).toString();
    let html = request(url, {
        body: {
            sign: hx,
            type_id: $t,
            page: $pg,
        },
        headers: {
            'User-Agent': 'okhttp-okgo/jeasonlzy',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        'method': 'POST'
    }, true);
    return JSON.parse(html).data.list;
}

globalThis.seach = function(wd) {
    const currentTimestamp = parseInt(Date.now() / 1000, 10);
    const url = h_ost + '/v2/home/search';
    const hx = CryptoJS.MD5('kj5649ertj84ks89r4jh8s45hf84hjfds04k' + currentTimestamp).toString();
    let html = request(url, {
        body: {
            sign: hx,
            keyword: wd,
            timestamp: currentTimestamp,
        },
        headers: {
            'User-Agent': 'okhttp-okgo/jeasonlzy',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        'method': 'POST'
    }, true);
    return JSON.parse(html).data.list;
}
globalThis.vodids = function(ids) {
    const currentTimestamp = parseInt(Date.now() / 1000, 10);
    const url = h_ost + '/v2/home/vod_details';
    const hx = CryptoJS.MD5('kj5649ertj84ks89r4jh8s45hf84hjfds04k' + currentTimestamp).toString();
    let html = request(url, {
        body: {
            sign: hx,
            vod_id: ids,
            timestamp: currentTimestamp,
        },
        headers: {
            'User-Agent': 'okhttp-okgo/jeasonlzy',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        'method': 'POST'
    }, true);
    const redata = JSON.parse(html);
    let vodPlayFrom = '';
    let vodPlayUrl = '';
    redata.data.vod_play_list.forEach((value, key) => {
        if (value.flag.includes("nby") || value.flag.includes("mgtv") || value.flag.includes("qq") || value.flag.includes("qiyi") || value.flag.includes("mgtv")) {
            vodPlayFrom += `${value.flag}$$$`;
            value.urls.forEach(url => {
                vodPlayUrl += `${url.name}$${value.parse_urls[0]}${url.url}~${url.name}#`;
            });
            vodPlayUrl += '$$$';
        }
    });
    const regeshi = {
        vod_id: redata.data.vod_id,
        vod_name: redata.data.vod_name,
        vod_remarks: `${redata.data.vod_remarks}`,
        type_name: redata.data.vod_class,
        vod_pic: redata.data.vod_pic,
        vod_year: redata.data.vod_year,
        vod_area: redata.data.vod_area,
        vod_actor: `${redata.data.vod_actor}`,
        vod_director: redata.data.vod_director,
        vod_content: `${redata.data.vod_content}`,
        vod_play_from: vodPlayFrom,
        vod_play_url: vodPlayUrl
    };
    return regeshi;
}
globalThis.jxx = function(input) {
    if ("741852963" !== '741852963') {
        return 'https://s0.mall.tcl.com/group1/M00/00/89/CvoGBGdcOPaAAUxvADwZniVV2bc476.mp4';
    }
    const parts = input.split('~');
    try {
        let response = fetch(parts[0], {
            method: 'get',
            headers: {
                'User-Agent': 'okhttp/3.14.9',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });

        if (response.includes("成功") || response.includes("success") || response.includes("nby")) {
            let bata = JSON.parse(response);
            input = {
                parse: 0,
                url: bata.url,
                jx: 0,
                danmaku: 'http://103.45.162.207:25252/hbdm.php?key=7894561232&id=' + '&jm=' + VOD.vod_name + '&js=' + parts[1] + '&key=741852963'
            }
        } else {
            input = {
                parse: 0,
                url: parts[0].includes('url=') ? parts[0].slice(parts[0].indexOf('url=') + 4) : null,
                jx: 1,
                danmaku: 'http://103.45.162.207:25252/hbdm.php?key=7894561232&id=' + '&jm=' + VOD.vod_name + '&js=' + parts[1] + '&key=741852963'
            }
        }
    } catch {
        input = {
            parse: 0,
            url: '解析失败',
            jx: 0,
        }
    }
    return input;
}

var rule = {
    title: '追剧',
    host: '',
    detailUrl: 'fyid',
    searchUrl: '**',
    url: 'fyclass',
    searchable: 2,
    quickSearch: 1,
    filterable: 0,
    class_name: '电影&电视剧&综艺&动漫',
    class_url: '1&2&4&3',
    play_parse: true,
    lazy: $js.toString(() => {
        input = jxx(input);
    }),
    推荐: $js.toString(() => {
        let bdata = vodlist(0, 1);
        console.log(bdata);
        bdata.forEach(it => {
            d.push({
                url: it.vod_id,
                title: it.vod_name,
                img: it.vod_pic,
                desc: it.vod_remarks
            });
        });
        setResult(d);
    }),
    一级: $js.toString(() => {
        let bdata = vodlist(input, MY_PAGE);
        console.log(bdata);
        bdata.forEach(it => {
            d.push({
                url: it.vod_id,
                title: it.vod_name,
                img: it.vod_pic,
                desc: it.vod_remarks
            });
        });
        setResult(d);
    }),
    二级: $js.toString(() => {
        console.log("调试信息2" + input);
        let data = vodids(input);
        //console.log(data);
        VOD = (data);
    }),
    搜索: $js.toString(() => {
        let ddata = seach(input);
        ddata.forEach(it => {
            d.push({
                url: it.vod_id,
                title: it.vod_name,
                img: it.vod_pic,
                desc: it.vod_remarks
            });
        });
        setResult(d);
    }),
}