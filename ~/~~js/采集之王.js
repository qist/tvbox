globalThis.getRandomItem = function (items) {
    return items[Math.random() * items.length | 0];
}
var rule = {
    title: '采集之王[合]',
    author: '道长',
    version: '20240705 beta16',
    update_info: ``.trim(),
    host: '',
    homeTid: '',
    homeUrl: '/api.php/provide/vod/?ac=detail&t={{rule.homeTid}}',
    detailUrl: '/api.php/provide/vod/?ac=detail&ids=fyid',
    searchUrl: '/api.php/provide/vod/?wd=**&pg=#TruePage##page=fypage',
    classUrl: '/api.php/provide/vod/',
    url: '/api.php/provide/vod/?ac=detail&pg=fypage&t=fyfilter',
    filter_url: '{{fl.类型}}',
    headers: {
        'User-Agent': 'MOBILE_UA'
    },
    timeout: 5000,
    limit: 20,
    search_limit: 10,
    searchable: 1,
    quickSearch: 0,
    filterable: 1,
    play_parse: true,
    parse_url: '',
    search_match: false,
    search_pic: true,
    预处理: $js.toString(() => {
        function getClasses(item) {
            let classes = [];
            if (item.class_name && item.class_url) {
                if (!/&|电影|电视剧|综艺|动漫[\u4E00-\u9FA5]+/.test(item.class_name)) {
                    try {
                        item.class_name = ungzip(item.class_name)
                    } catch (e) {
                        log(`不识别的class_name导致gzip解码失败:${e}`)
                        return classes
                    }
                }
                let names = item.class_name.split('&');
                let urls = item.class_url.split('&');
                let cnt = Math.min(names.length, urls.length);
                for (let i = 0; i < cnt; i++) {
                    classes.push({
                        'type_id': urls[i],
                        'type_name': names[i]
                    });
                }
            }
            return classes
        }
        if (typeof(batchFetch) === 'function') {
            rule.search_limit = 16;
            log('当前程序支持批量请求[batchFetch],搜索限制已设置为16');
        }
        let _url = rule.params;
        log(`传入参数:${_url}`);
        if (_url && typeof(_url) === 'string' && /^(http|file)/.test(_url)) {
            if (_url.includes('$')) {
                let _url_params = _url.split('$');
                _url = _url_params[0];
                rule.search_match = !!(_url_params[1]);
                if (_url_params.length > 2) {
                    rule.search_pic = !!(_url_params[2]);
                }
            }
            let html = request(_url);
            let json = JSON.parse(html);
            let _classes = [];
            rule.filter = {};
            rule.filter_def = {};
            json.forEach(it => {
                let _obj = {
                    type_name: it.name,
                    type_id: it.url,
                    parse_url: it.parse_url || '',
                    searchable: it.searchable !== 0,
                    api: it.api || '',
                    cate_exclude: it.cate_exclude || '',
                };
                _classes.push(_obj);
                try {
                    let json1 = [];
                    if (it.class_name && it.class_url) {
                        json1 = getClasses(it);
                    } else {
                        json1 = JSON.parse(request(urljoin(_obj.type_id, _obj.api || rule.classUrl))).class;
                    }
                    if (_obj.cate_exclude) {
                        json1 = json1.filter(cl => !new RegExp(_obj.cate_exclude, 'i').test(cl.type_name));
                    }
                    rule.filter[_obj.type_id] = [{
                            "key": "类型",
                            "name": "类型",
                            "value": json1.map(i => {
                                return {
                                    "n": i.type_name,
                                    'v': i.type_id
                                }
                            })
                        }
                    ];
                    if (json1.length > 0) {
                        rule.filter_def[it.url] = {
                            "类型": json1[0].type_id
                        };
                    }
                } catch (e) {
                    rule.filter[it.url] = [{
                            "key": "类型",
                            "name": "类型",
                            "value": [{
                                    "n": "全部",
                                    "v": ""
                                }
                            ]
                        }
                    ];
                }
            });
            rule.classes = _classes;
        }
    }),
    class_parse: $js.toString(() => {
        input = rule.classes;
    }),
    推荐: $js.toString(() => {
        VODS = [];
        if (rule.classes) {
            let randomClass = getRandomItem(rule.classes);
            let _url = urljoin(randomClass.type_id, input);
            if (randomClass.api) {
                _url = _url.replace('/api.php/provide/vod/', randomClass.api)
            }
            try {
                let html = request(_url, {
                    timeout: rule.timeout
                });
                let json = JSON.parse(html);
                VODS = json.list;
                VODS.forEach(it => {
                    it.vod_id = randomClass.type_id + '$' + it.vod_id;
                    it.vod_remarks = it.vod_remarks + '|' + randomClass.type_name;
                });
            } catch (e) {}
        }
    }),
    一级: $js.toString(() => {
        VODS = [];
        if (rule.classes) {
            let _url = urljoin(MY_CATE, input);
            let current_vod = rule.classes.find(item => item.type_id === MY_CATE);
            if (current_vod && current_vod.api) {
                _url = _url.replace('/api.php/provide/vod/', current_vod.api)
            }
            let html = request(_url);
            let json = JSON.parse(html);
            VODS = json.list;
            VODS.forEach(it => {
                it.vod_id = MY_CATE + '$' + it.vod_id
            });
        }
    }),
    二级: $js.toString(() => {
        VOD = {};
        if (orId === 'update_info') {
            VOD = {
                vod_content: rule.update_info.trim(),
                vod_name: '更新日志',
                type_name: '更新日志',
                vod_pic: 'https://resource-cdn.tuxiaobei.com/video/FtWhs2mewX_7nEuE51_k6zvg6awl.png',
                vod_remarks: `版本:${rule.version}`,
                vod_play_from: '道长在线',
                vod_play_url: '随机小视频$http://api.yujn.cn/api/zzxjj.php',
            };
        } else {
            if (rule.classes) {
                let _url = urljoin(fyclass, input);
                let current_vod = rule.classes.find(item => item.type_id === fyclass);
                if (current_vod && current_vod.api) {
                    _url = _url.replace('/api.php/provide/vod/', current_vod.api)
                }
                let html = request(_url);
                let json = JSON.parse(html);
                let data = json.list;
                VOD = data[0];
                if (current_vod && current_vod.type_name) {
                    VOD.vod_play_from = VOD.vod_play_from.split('$$$').map(it => current_vod.type_name + '|' + it).join('$$$')
                }
            }
        }
    }),
    搜索: $js.toString(() => {
        VODS = [];
        if (rule.classes) {
            let canSearch = rule.classes.filter(it => it.searchable);
            let page = Number(MY_PAGE);
            page = (MY_PAGE - 1) % Math.ceil(canSearch.length / rule.search_limit) + 1;
            let truePage = Math.ceil(MY_PAGE / Math.ceil(canSearch.length / rule.search_limit));
            if (rule.search_limit) {
                let start = (page - 1) * rule.search_limit;
                let end = page * rule.search_limit;
                let t1 = new Date().getTime();
                let searchMode = typeof(batchFetch) === 'function' ? '批量' : '单个';
                log('start:' + start);
                log('end:' + end);
                log('搜索模式:' + searchMode);
                log('精准搜索:' + rule.search_match);
                if (start < canSearch.length) {
                    let search_classes = canSearch.slice(start, end);
                    let urls = [];
                    search_classes.forEach(it => {
                        let _url = urljoin(it.type_id, input);
                        if (it.api) {
                            _url = _url.replace('/api.php/provide/vod/', it.api)
                        }
                        _url = _url.replace("#TruePage#", "" + truePage);
                        urls.push(_url);
                    });
                    let results_list = [];
                    let results = [];
                    if (typeof(batchFetch) === 'function') {
                        let reqUrls = urls.map(it => {
                            return {
                                url: it,
                                options: {
                                    timeout: rule.timeout
                                }
                            }
                        });
                        let rets = batchFetch(reqUrls);
                        let detailUrls = [];
                        let detailUrlCount = 0;
                        rets.forEach((ret, idx) => {
                            let it = search_classes[idx];
                            if (ret) {
                                try {
                                    let json = JSON.parse(ret);
                                    let data = json.list;
                                    data.forEach(i => {
                                        i.site_name = it.type_name;
                                        i.vod_id = it.type_id + '$' + i.vod_id;
                                        i.vod_remarks = i.vod_remarks + '|' + it.type_name;
                                    });
                                    if (rule.search_match) {
                                        data = data.filter(item => item.vod_name && (new RegExp(KEY, 'i')).test(item.vod_name))
                                    }
                                    if (data.length > 0) {
                                        if (rule.search_pic && !data[0].vod_pic) {
                                            log(`当前搜索站点【${it.type_name}】没图片,尝试访问二级去获取图片`);
                                            let detailUrl = urls[idx].split('wd=')[0] + 'ac=detail&ids=' + data.map(k => k.vod_id.split('$')[1]).join(',');
                                            detailUrls.push(detailUrl);
                                            results_list.push({
                                                data: data,
                                                has_pic: false,
                                                detailUrlCount: detailUrlCount
                                            });
                                            detailUrlCount++;
                                        } else {
                                            results_list.push({
                                                data: data,
                                                has_pic: true
                                            });
                                        }
                                    }
                                } catch (e) {
                                    log(`请求:${it.type_id}发生错误:${e.message}`)
                                }
                            }
                        });
                        let reqUrls2 = detailUrls.map(it => {
                            return {
                                url: it,
                                options: {
                                    timeout: rule.timeout
                                }
                            }
                        });
                        let rets2 = batchFetch(reqUrls2);
                        for (let k = 0; k < results_list.length; k++) {
                            let result_data = results_list[k].data;
                            if (!results_list[k].has_pic) {
                                try {
                                    let detailJson = JSON.parse(rets2[results_list[k].detailUrlCount]);
                                    log('二级数据列表元素数:' + detailJson.list.length);
                                    result_data.forEach((d, _seq) => {
                                        let detailVodPic = detailJson.list.find(vod => vod.vod_id.toString() === d.vod_id.split('$')[1]);
                                        if (detailVodPic) {
                                            Object.assign(d, {
                                                vod_pic: detailVodPic.vod_pic
                                            });
                                        }
                                    });
                                } catch (e) {
                                    log(`强制获取网站${result_data[0].site_name}的搜索图片失败:${e.message}`);
                                }
                            }
                            results = results.concat(result_data);
                        }
                    } else {
                        urls.forEach((_url, idx) => {
                            let it = search_classes[idx];
                            try {
                                let html = request(_url);
                                let json = JSON.parse(html);
                                let data = json.list;
                                data.forEach(i => {
                                    i.vod_id = it.type_id + '$' + i.vod_id;
                                    i.vod_remarks = i.vod_remarks + '|' + it.type_name;
                                });
                                if (rule.search_match) {
                                    data = data.filter(item => item.vod_name && (new RegExp(KEY, 'i')).test(item.vod_name))
                                }
                                if (data.length > 0) {
                                    if (rule.search_pic && !data[0].vod_pic) {
                                        log(`当前搜索站点【${it.type_name}】没图片,尝试访问二级去获取图片`);
                                        let detailUrl = urls[idx].split('wd=')[0] + 'ac=detail&ids=' + data.map(k => k.vod_id.split('$')[1]).join(',');
                                        try {
                                            let detailJson = JSON.parse(request(detailUrl));
                                            log('二级数据列表元素数:' + detailJson.list.length);
                                            data.forEach((d, _seq) => {
                                                let detailVodPic = detailJson.list.find(vod => vod.vod_id.toString() === d.vod_id.split('$')[1]);
                                                if (detailVodPic) {
                                                    Object.assign(d, {
                                                        vod_pic: detailVodPic.vod_pic
                                                    });
                                                }
                                            });
                                        } catch (e) {
                                            log(`强制获取网站${it.type_id}的搜索图片失败:${e.message}`);
                                        }
                                    }
                                    results = results.concat(data);
                                }
                                results = results.concat(data);
                            } catch (e) {
                                log(`请求:${it.type_id}发生错误:${e.message}`)
                            }
                        });
                    }
                    VODS = results;
                    let t2 = new Date().getTime();
                    log(`${searchMode}搜索:${urls.length}个站耗时:${(Number(t2) - Number(t1))}ms`)
                }
            }
        }
    }),
    lazy: $js.toString(() => {
        let parse_url = '';
        if (flag && flag.includes('|')) {
            let type_name = flag.split('|')[0];
            let current_vod = rule.classes.find(item => item.type_name === type_name);
            if (current_vod && current_vod.parse_url) {
                parse_url = current_vod.parse_url
            }
        }
        if (/\.(m3u8|mp4)/.test(input)) {
            input = {
                parse: 0,
                url: input
            }
        } else {
            if (parse_url.startsWith('json:')) {
                let purl = parse_url.replace('json:', '') + input;
                let html = request(purl);
                input = {
                    parse: 0,
                    url: JSON.parse(html).url
                }
            } else {
                input = parse_url + input;
            }
        }
    }),
}
