//小心儿悠悠//
var rule = {
    title: '腾讯视频',
    host: 'https://v.qq.com',
    homeUrl: '/x/bu/pagesheet/list?_all=1&append=1&channel=cartoon&listpage=1&offset=0&pagesize=21&iarea=-1&sort=18',
    detailUrl: 'https://node.video.qq.com/x/api/float_vinfo2?cid=fyid',
    searchUrl: '**',
    searchable: 2,
    filterable: 1,
    multi: 1,
    url: '/x/bu/pagesheet/list?_all=1&append=1&channel=fyclass&listpage=1&offset=((fypage-1)*21)&pagesize=21&iarea=-1',
    filter_url: 'sort={{fl.sort or 75}}&iyear={{fl.iyear}}&year={{fl.year}}&itype={{fl.type}}&ifeature={{fl.feature}}&iarea={{fl.area}}&itrailer={{fl.itrailer}}&gender={{fl.sex}}&prefer={{fl.prefer}}&identity={{fl.identity}}&attraction={{fl.attraction}}&story={{fl.story}}',
    filter: {
        "choice": [{
            "key": "sort",
            "name": "排序",
            "value": [{
                "n": "最热",
                "v": "75"
            }, {
                "n": "最新",
                "v": "83"
            }, {
                "n": "好评",
                "v": "81"
            }]
        }, {
            "key": "iyear",
            "name": "年代",
            "value": [{
                "n": "全部",
                "v": "-1"
            }, {
                "n": "2026",
                "v": "2026"
            }, {
                "n": "2025",
                "v": "2025"
            }, {
                "n": "2024",
                "v": "2024"
            }, {
                "n": "2023",
                "v": "2023"
            }, {
                "n": "2022",
                "v": "2022"
            }, {
                "n": "2021",
                "v": "2021"
            }, {
                "n": "2020",
                "v": "2020"
            }, {
                "n": "2019",
                "v": "2019"
            }, {
                "n": "2018",
                "v": "2018"
            }, {
                "n": "2017",
                "v": "2017"
            }, {
                "n": "2016",
                "v": "2016"
            }, {
                "n": "2015",
                "v": "2015"
            }]
        }],
        "tv": [{
            "key": "sort",
            "name": "排序",
            "value": [{
                "n": "最热",
                "v": "75"
            }, {
                "n": "最新",
                "v": "79"
            }, {
                "n": "好评",
                "v": "16"
            }]
        }, {
            "key": "feature",
            "name": "类型",
            "value": [{
                "n": "全部",
                "v": "-1"
            }, {
                "n": "爱情",
                "v": "1"
            }, {
                "n": "古装",
                "v": "2"
            }, {
                "n": "悬疑",
                "v": "3"
            }, {
                "n": "都市",
                "v": "4"
            }, {
                "n": "家庭",
                "v": "5"
            }, {
                "n": "喜剧",
                "v": "6"
            }, {
                "n": "传奇",
                "v": "7"
            }, {
                "n": "武侠",
                "v": "8"
            }, {
                "n": "军旅",
                "v": "9"
            }, {
                "n": "权谋",
                "v": "10"
            }, {
                "n": "革命",
                "v": "11"
            }, {
                "n": "现实",
                "v": "13"
            }, {
                "n": "青春",
                "v": "14"
            }, {
                "n": "猎奇",
                "v": "15"
            }, {
                "n": "科幻",
                "v": "16"
            }, {
                "n": "竞技",
                "v": "17"
            }, {
                "n": "玄幻",
                "v": "18"
            }]
        }, {
            "key": "iyear",
            "name": "年代",
            "value": [{
                "n": "全部",
                "v": "-1"
            }, {
                "n": "2026",
                "v": "2026"
            }, {
                "n": "2025",
                "v": "2025"
            }, {
                "n": "2024",
                "v": "2024"
            }, {
                "n": "2023",
                "v": "2023"
            }, {
                "n": "2022",
                "v": "2022"
            }, {
                "n": "2021",
                "v": "2021"
            }, {
                "n": "2020",
                "v": "2020"
            }, {
                "n": "2019",
                "v": "2019"
            }, {
                "n": "2018",
                "v": "2018"
            }, {
                "n": "2017",
                "v": "2017"
            }, {
                "n": "2016",
                "v": "2016"
            }, {
                "n": "2015",
                "v": "2015"
            }]
        }],
        "movie": [{
            "key": "sort",
            "name": "排序",
            "value": [{
                "n": "最热",
                "v": "75"
            }, {
                "n": "最新",
                "v": "83"
            }, {
                "n": "好评",
                "v": "81"
            }]
        }, {
            "key": "type",
            "name": "类型",
            "value": [{
                "n": "全部",
                "v": "-1"
            }, {
                "n": "犯罪",
                "v": "4"
            }, {
                "n": "励志",
                "v": "2"
            }, {
                "n": "喜剧",
                "v": "100004"
            }, {
                "n": "热血",
                "v": "100061"
            }, {
                "n": "悬疑",
                "v": "100009"
            }, {
                "n": "爱情",
                "v": "100005"
            }, {
                "n": "科幻",
                "v": "100012"
            }, {
                "n": "恐怖",
                "v": "100010"
            }, {
                "n": "动画",
                "v": "100015"
            }, {
                "n": "战争",
                "v": "100006"
            }, {
                "n": "家庭",
                "v": "100017"
            }, {
                "n": "剧情",
                "v": "100022"
            }, {
                "n": "奇幻",
                "v": "100016"
            }, {
                "n": "武侠",
                "v": "100011"
            }, {
                "n": "历史",
                "v": "100021"
            }, {
                "n": "老片",
                "v": "100013"
            }, {
                "n": "西部",
                "v": "3"
            }, {
                "n": "记录片",
                "v": "100020"
            }]
        }, {
            "key": "year",
            "name": "年代",
            "value": [{
                "n": "全部",
                "v": "-1"
            }, {
                "n": "2026",
                "v": "2026"
            }, {
                "n": "2025",
                "v": "2025"
            }, {
                "n": "2024",
                "v": "2024"
            }, {
                "n": "2023",
                "v": "2023"
            }, {
                "n": "2022",
                "v": "2022"
            }, {
                "n": "2021",
                "v": "2021"
            }, {
                "n": "2020",
                "v": "2020"
            }, {
                "n": "2019",
                "v": "2019"
            }, {
                "n": "2018",
                "v": "2018"
            }, {
                "n": "2017",
                "v": "2017"
            }, {
                "n": "2016",
                "v": "2016"
            }, {
                "n": "2015",
                "v": "2015"
            }]
        }],
        "variety": [{
            "key": "sort",
            "name": "排序",
            "value": [{
                "n": "最热",
                "v": "75"
            }, {
                "n": "最新",
                "v": "23"
            }]
        }, {
            "key": "iyear",
            "name": "年代",
            "value": [{
                "n": "全部",
                "v": "-1"
            }, {
                "n": "2026",
                "v": "2026"
            }, {
                "n": "2025",
                "v": "2025"
            }, {
                "n": "2024",
                "v": "2024"
            }, {
                "n": "2023",
                "v": "2023"
            }, {
                "n": "2022",
                "v": "2022"
            }, {
                "n": "2021",
                "v": "2021"
            }, {
                "n": "2020",
                "v": "2020"
            }, {
                "n": "2019",
                "v": "2019"
            }, {
                "n": "2018",
                "v": "2018"
            }, {
                "n": "2017",
                "v": "2017"
            }, {
                "n": "2016",
                "v": "2016"
            }, {
                "n": "2015",
                "v": "2015"
            }]
        }],
        "cartoon": [{
            "key": "sort",
            "name": "排序",
            "value": [{
                "n": "最热",
                "v": "75"
            }, {
                "n": "最新",
                "v": "83"
            }, {
                "n": "好评",
                "v": "81"
            }]
        }, {
            "key": "area",
            "name": "地区",
            "value": [{
                "n": "全部",
                "v": "-1"
            }, {
                "n": "内地",
                "v": "1"
            }, {
                "n": "日本",
                "v": "2"
            }, {
                "n": "欧美",
                "v": "3"
            }, {
                "n": "其他",
                "v": "4"
            }]
        }, {
            "key": "type",
            "name": "类型",
            "value": [{
                "n": "全部",
                "v": "-1"
            }, {
                "n": "玄幻",
                "v": "9"
            }, {
                "n": "科幻",
                "v": "4"
            }, {
                "n": "武侠",
                "v": "13"
            }, {
                "n": "冒险",
                "v": "3"
            }, {
                "n": "战斗",
                "v": "5"
            }, {
                "n": "搞笑",
                "v": "1"
            }, {
                "n": "恋爱",
                "v": "7"
            }, {
                "n": "魔幻",
                "v": "6"
            }, {
                "n": "竞技",
                "v": "20"
            }, {
                "n": "悬疑",
                "v": "17"
            }, {
                "n": "日常",
                "v": "15"
            }, {
                "n": "校园",
                "v": "16"
            }, {
                "n": "真人",
                "v": "18"
            }, {
                "n": "推理",
                "v": "14"
            }, {
                "n": "历史",
                "v": "19"
            }, {
                "n": "经典",
                "v": "3"
            }, {
                "n": "其他",
                "v": "12"
            }]
        }, {
            "key": "iyear",
            "name": "年代",
            "value": [{
                "n": "全部",
                "v": "-1"
            }, {
                "n": "2026",
                "v": "2026"
            }, {
                "n": "2025",
                "v": "2025"
            }, {
                "n": "2024",
                "v": "2024"
            }, {
                "n": "2023",
                "v": "2023"
            }, {
                "n": "2022",
                "v": "2022"
            }, {
                "n": "2021",
                "v": "2021"
            }, {
                "n": "2020",
                "v": "2020"
            }, {
                "n": "2019",
                "v": "2019"
            }, {
                "n": "2018",
                "v": "2018"
            }, {
                "n": "2017",
                "v": "2017"
            }, {
                "n": "2016",
                "v": "2016"
            }, {
                "n": "2015",
                "v": "2015"
            }]
        }],
        "child": [{
            "key": "sort",
            "name": "排序",
            "value": [{
                "n": "最热",
                "v": "75"
            }, {
                "n": "最新",
                "v": "76"
            }, {
                "n": "好评",
                "v": "20"
            }]
        }, {
            "key": "sex",
            "name": "性别",
            "value": [{
                "n": "全部",
                "v": "-1"
            }, {
                "n": "女孩",
                "v": "1"
            }, {
                "n": "男孩",
                "v": "2"
            }]
        }, {
            "key": "area",
            "name": "地区",
            "value": [{
                "n": "全部",
                "v": "-1"
            }, {
                "n": "内地",
                "v": "3"
            }, {
                "n": "日本",
                "v": "2"
            }, {
                "n": "其他",
                "v": "1"
            }]
        }, {
            "key": "iyear",
            "name": "年龄段",
            "value": [{
                "n": "全部",
                "v": "-1"
            }, {
                "n": "0-3岁",
                "v": "1"
            }, {
                "n": "4-6岁",
                "v": "2"
            }, {
                "n": "7-9岁",
                "v": "3"
            }, {
                "n": "10岁以上",
                "v": "4"
            }, {
                "n": "全年龄段",
                "v": "7"
            }]
        }],
        "doco": [{
            "key": "sort",
            "name": "排序",
            "value": [{
                "n": "最热",
                "v": "75"
            }, {
                "n": "最新",
                "v": "74"
            }]
        }, {
            "key": "itrailer",
            "name": "出品方",
            "value": [{
                "n": "全部",
                "v": "-1"
            }, {
                "n": "BBC",
                "v": "1"
            }, {
                "n": "国家地理",
                "v": "4"
            }, {
                "n": "HBO",
                "v": "3175"
            }, {
                "n": "NHK",
                "v": "2"
            }, {
                "n": "历史频道",
                "v": "7"
            }, {
                "n": "ITV",
                "v": "3530"
            }, {
                "n": "探索频道",
                "v": "3174"
            }, {
                "n": "ZDF",
                "v": "3176"
            }, {
                "n": "腾讯自制",
                "v": "15"
            }, {
                "n": "合作机构",
                "v": "6"
            }, {
                "n": "其他",
                "v": "5"
            }]
        }, {
            "key": "type",
            "name": "类型",
            "value": [{
                "n": "全部",
                "v": "-1"
            }, {
                "n": "自然",
                "v": "4"
            }, {
                "n": "美食",
                "v": "10"
            }, {
                "n": "社会",
                "v": "3"
            }, {
                "n": "人文",
                "v": "6"
            }, {
                "n": "历史",
                "v": "1"
            }, {
                "n": "军事",
                "v": "2"
            }, {
                "n": "科技",
                "v": "8"
            }, {
                "n": "财经",
                "v": "14"
            }, {
                "n": "探险",
                "v": "15"
            }, {
                "n": "罪案",
                "v": "7"
            }, {
                "n": "竞技",
                "v": "12"
            }, {
                "n": "旅游",
                "v": "11"
            }]
        }],
        "mini_series": [{
            "key": "prefer",
            "name": "频道",
            "value": [{
                "n": "全部",
                "v": ""
            }, {
                "n": "女频",
                "v": "1"
            }, {
                "n": "男频",
                "v": "2"
            }]
        }, {
            "key": "identity",
            "name": "身份",
            "value": [{
                "n": "全部",
                "v": ""
            }, {
                "n": "总裁",
                "v": "1"
            }, {
                "n": "大女主",
                "v": "2"
            }, {
                "n": "萌娃",
                "v": "4"
            }]
        }, {
            "key": "attraction",
            "name": "看点",
            "value": [{
                "n": "全部",
                "v": ""
            }, {
                "n": "先婚后爱",
                "v": "1"
            }, {
                "n": "颜值逆袭",
                "v": "45"
            }]
        }, {
            "key": "story",
            "name": "题材",
            "value": [{
                "n": "全部",
                "v": ""
            }, {
                "n": "都市奇幻",
                "v": "3"
            }]
        }]
    },
    headers: {
        'User-Agent': 'PC_UA'
    },
    timeout: 5000,
    cate_exclude: '会员|游戏|全部',
    class_name: '电影&电视剧&短剧&综艺&动漫&少儿&纪录片',
    class_url: 'movie&tv&mini_series&variety&cartoon&child&doco',
    limit: 20,
    play_parse: true,
    lazy: $js.toString(() => {
        try {
            let bata = JSON.parse(response);
            log(bata)
            if (bata.url.includes("http")) {
                input = {
                    header: {
                        'User-Agent': ""
                    },
                    parse: 0,
                    url: bata.url,
                    jx: 0,
                    danmaku: "http://127.0.0.1:9978/proxy?do=danmu&site=js&url=" + input.split("?")[0]
                };
            } else {
                input = {
                    header: {
                        'User-Agent': ""
                    },
                    parse: 0,
                    url: input.split("?")[0],
                    jx: 1,
                    danmaku: "http://127.0.0.1:9978/proxy?do=danmu&site=js&url=" + input.split("?")[0]
                };
            }
        } catch {
            input = {
                header: {
                    'User-Agent': ""
                },
                parse: 0,
                url: input.split("?")[0],
                jx: 1,
                danmaku: "http://127.0.0.1:9978/proxy?do=danmu&site=js&url=" + input.split("?")[0]
            };
        }
    }),

    推荐: '.list_item;img&&alt;img&&src;a&&Text;a&&data-float',
    一级: $js.toString(() => {
        let fyclass = MY_CATE;
        let fypage = MY_PAGE;
        let fl = MY_FL || {};
        // 腾讯频道“全部”列表接口（旧 /x/bu/pagesheet/list 已 404）。MVLPage 返回
        // 最新数据；page_context 续页；短剧与其它频道同接口。
        let channelMap = {
            movie: '100173', tv: '100113', mini_series: '120188',
            variety: '100109', cartoon: '100119', child: '100150', doco: '100105'
        };
        let channelId = channelMap[fyclass] || fyclass;
        let apiUrl = 'https://pbaccess.video.qq.com/trpc.multi_vector_layout.mvl_controller.MVLPageHTTPService/getMVLPage?&vversion_platform=18';
        let apiHdr = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'Origin': 'https://v.qq.com',
            'Referer': 'https://v.qq.com/tv-series-list/v-index.html'
        };
        // filter_params：新接口键（sort/itype/iyear/iarea/characteristic…）
        let flKeys = ['sort', 'itype', 'iyear', 'iarea', 'characteristic', 'ipay', 'producer', 'award', 'theater', 'anime_status', 'item'];
        let fparts = [];
        flKeys.forEach(function(k) {
            if (fl[k] !== undefined && fl[k] !== null && fl[k] !== '' && fl[k] !== '-1') {
                fparts.push(k + '=' + fl[k]);
            }
        });
        if (fl.feature !== undefined && fl.feature !== '' && fl.feature !== '-1' && fparts.join('&').indexOf('itype=') < 0) {
            fparts.push('itype=' + fl.feature);
        }
        if (fparts.length === 0) fparts.push('sort=75');
        let filterParams = fparts.join('&');
        // page_context 不透明，且端内 storage 不保证跨请求持久：从第 1 页顺链
        // 取到目标页（用户通常只看前几页，代价可控）。
        let ctx = null;
        let resp = null;
        let target = fypage > 1 ? fypage : 1;
        for (let i = 1; i <= target; i++) {
            let reqBody = {
                page_params: {
                    channel_id: channelId,
                    filter_params: filterParams,
                    page_id: 'channel_list',
                    page_type: 'operation'
                },
                page_context: ctx || null
            };
            resp = JSON.parse(request(apiUrl, {
                body: JSON.stringify(reqBody),
                headers: apiHdr,
                method: 'POST'
            }));
            ctx = (resp.data && resp.data.page_context) || null;
            if (!ctx && i < target) break; // 已到末页
        }
        let data = resp.data || {};
        // 递归收集条目（searchlist_poster_card：params.cid/title/new_pic_vt…）
        let items = [];
        let walk = function(o) {
            if (!o || typeof o !== 'object') return;
            if (Array.isArray(o)) {
                for (let i = 0; i < o.length; i++) walk(o[i]);
                return;
            }
            let p = o.params;
            if (p && typeof p === 'object' && p.cid) {
                let title = p.title || p.name || '';
                if (title) {
                    let img = p.new_pic_vt || p.new_pic_hz || p.image_url || p.pic || p.cover || '';
                    if (typeof img === 'string' && img.indexOf('http://') === 0) img = 'https://' + img.slice(7);
                    let desc = '';
                    try {
                        if (p.chnlist_search_label) {
                            let m = typeof p.chnlist_search_label === 'string' ? JSON.parse(p.chnlist_search_label) : p.chnlist_search_label;
                            if (m && m.length > 0) desc = m[0].label || '';
                        }
                    } catch (e) {}
                    if (!desc) desc = p.main_genre || p.area_name || '';
                    items.push({ title: title, img: img, desc: desc, url: p.cid });
                }
            }
            for (let k in o) walk(o[k]);
        };
        walk(data.modules || data);
        let seen = {};
        let dd = [];
        items.forEach(function(it) {
            if (!seen[it.url]) {
                seen[it.url] = 1;
                dd.push(it);
            }
        });
        setResult(dd);
    }),
    二级: $js.toString(() => {
        VOD = {};
        let d = [];
        let video_list = [];
        let video_lists = [];
        let QZOutputJson;
        let html = fetch(input, fetch_params);
        let sourceId = /get_playsource/.test(input) ? input.match(/id=(\d*?)&/)[1] : input.split("cid=")[1];
        let cid = sourceId;
        let detailUrl = "https://v.qq.com/detail/m/" + cid + ".html";
        try {
            let json = JSON.parse(html);
            VOD = {
                vod_url: input,
                vod_name: json.c.title,
                type_name: json.typ.join(","),
                vod_actor: json.nam.join(","),
                vod_year: json.c.year,
                vod_content: json.c.description,
                vod_remarks: json.rec,
                vod_pic: urljoin2(input, json.c.pic)
            }
        } catch (e) {}
        if (/get_playsource/.test(input)) {
            eval(html);
            let indexList = QZOutputJson.PlaylistItem.indexList;
            indexList.forEach(function(it) {
                let dataUrl = "https://s.video.qq.com/get_playsource?id=" + sourceId + "&plat=2&type=4&data_type=3&range=" + it + "&video_type=10&plname=qq&otype=json";
                eval(fetch(dataUrl, fetch_params));
                let vdata = QZOutputJson.PlaylistItem.videoPlayList;
                vdata.forEach(function(item) {
                    d.push({
                        title: item.title,
                        pic_url: item.pic,
                        desc: item.episode_number + "\t\t\t播放量：" + item.thirdLine,
                        url: item.playUrl
                    })
                });
                video_lists = video_lists.concat(vdata)
            })
        } else {
            let json = JSON.parse(html);
            video_lists = json.c.video_ids;
            let url = "https://v.qq.com/x/cover/" + sourceId + ".html";
            if (video_lists.length === 1) {
                let vid = video_lists[0];
                let o_url = "https://union.video.qq.com/fcgi-bin/data?otype=json&tid=1804&appid=20001238&appkey=6c03bbe9658448a4&union_platform=1&idlist=" + vid;
                let o_html = fetch(o_url, fetch_params);
                eval(o_html);
                if (QZOutputJson.results && QZOutputJson.results.length > 0) {
                    let it1 = QZOutputJson.results[0].fields;
                    url = "https://v.qq.com/x/cover/" + cid + "/" + vid + ".html";
                    d.push({
                        title: it1.title,
                        url: url
                    })
                } else {
                    url = "https://v.qq.com/x/cover/" + cid + "/" + vid + ".html";
                    d.push({
                        title: "正片播放",
                        url: url
                    })
                }
            } else if (video_lists.length > 1) {
                for (let i = 0; i < video_lists.length; i += 30) {
                    video_list.push(video_lists.slice(i, i + 30))
                }
                video_list.forEach(function(it, idex) {
                    let o_url = "https://union.video.qq.com/fcgi-bin/data?otype=json&tid=1804&appid=20001238&appkey=6c03bbe9658448a4&union_platform=1&idlist=" + it.join(",");
                    let o_html = fetch(o_url, fetch_params);
                    eval(o_html);
                    QZOutputJson.results.forEach(function(it1) {
                        it1 = it1.fields;
                        let url = "https://v.qq.com/x/cover/" + cid + "/" + it1.vid + ".html";
                        d.push({
                            title: it1.title,
                            pic_url: it1.pic160x90.replace("/160", ""),
                            desc: it1.video_checkup_time,
                            url: url,
                            type: it1.category_map && it1.category_map.length > 1 ? it1.category_map[1] : ""
                        })
                    })
                })
            }
        }

        let playFrom = [];
        let playUrl = [];

        let ygKeywords = ["预告", "花絮", "片花", "特辑", "幕后", "采访", "制作", "MV", "主题曲"];

        let yg = d.filter(function(it) {
            return it.type && ygKeywords.some(keyword => it.type.includes(keyword));
        });
        let zp = d.filter(function(it) {
            return !(it.type && ygKeywords.some(keyword => it.type.includes(keyword)));
        });

        if (zp.length > 0) {
            playFrom.push("正片");
            playUrl.push(zp.map(it => it.title + "$" + it.url).join("#"));
        }

        if (yg.length > 0) {
            let 预告 = yg.filter(it => it.type && it.type.includes("预告"));
            let 花絮片花 = yg.filter(it => it.type && (it.type.includes("花絮") || it.type.includes("片花")));
            let 特辑 = yg.filter(it => it.type && (it.type.includes("特辑") || it.type.includes("幕后")));

            if (预告.length > 0) {
                playFrom.push("预告");
                playUrl.push(预告.map(it => it.title + "$" + it.url).join("#"));
            }
            if (花絮片花.length > 0) {
                playFrom.push("花絮片花");
                playUrl.push(花絮片花.map(it => it.title + "$" + it.url).join("#"));
            }
            if (特辑.length > 0) {
                playFrom.push("特辑");
                playUrl.push(特辑.map(it => it.title + "$" + it.url).join("#"));
            }
        }

        VOD.vod_play_from = playFrom.join("$$$");
        VOD.vod_play_url = playUrl.join("$$$");
    }),
    搜索: $js.toString(() => {
        let d = [],
            keyword = input.split("/")[3];
        let seenIds = new Set();

        function vodSearch(keyword, page = 0) {
            return request('https://pbaccess.video.qq.com/trpc.videosearch.mobile_search.MultiTerminalSearch/MbSearch?vplatform=2', {
                body: JSON.stringify({
                    version: "25042201",
                    clientType: 1,
                    filterValue: "",
                    uuid: "B1E50847-D25F-4C4B-BBA0-36F0093487F6",
                    retry: 0,
                    query: keyword,
                    pagenum: page,
                    isPrefetch: true,
                    pagesize: 30,
                    queryFrom: 0,
                    searchDatakey: "",
                    transInfo: "",
                    isneedQc: true,
                    preQid: "",
                    adClientInfo: "",
                    extraInfo: {
                        isNewMarkLabel: "1",
                        multi_terminal_pc: "1",
                        themeType: "1",
                        sugRelatedIds: "{}",
                        appVersion: ""
                    }
                }),
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.139 Safari/537.36',
                    'Content-Type': 'application/json',
                    'Origin': 'https://v.qq.com',
                    'Referer': 'https://v.qq.com/'
                },
                method: 'POST'
            });
        }

        const nonMainContentKeywords = [
            '：', '#', '特辑', '"', '剪辑', '片花', '独家', '专访', '纯享',
            '制作', '幕后', '宣传', 'MV', '主题曲', '插曲', '彩蛋',
            '精彩', '集锦', '盘点', '回顾', '解说', '评测', '反应', 'reaction'
        ];

        function isMainContent(title) {
            if (!title) return false;
            if (title.includes('<em>') || title.includes('</em>')) return false;
            return !nonMainContentKeywords.some(keyword => title.includes(keyword));
        }

        function isQQPlatform(playSites) {
            if (!playSites || !Array.isArray(playSites)) return true;
            return playSites.some(site => site.enName && site.enName.toLowerCase() === 'qq');
        }

        try {
            let html = vodSearch(keyword, 0);
            let json = JSON.parse(html);

            function processItemList(itemList) {
                if (!itemList) return;

                itemList.forEach(it => {
                    if (it.doc && it.doc.id && it.videoInfo &&
                        isMainContent(it.videoInfo.title) &&
                        isQQPlatform(it.videoInfo.playSites) &&
                        Object.keys(it.videoInfo.episodeSites || {}).length > 0) {

                        const itemId = it.doc.id;
                        if (!seenIds.has(itemId)) {
                            seenIds.add(itemId);
                            d.push({
                                title: it.videoInfo.title,
                                img: it.videoInfo.imgUrl || "",
                                url: itemId,
                                desc: it.videoInfo.secondLine || ""
                            });
                        }
                    }
                });
            }

            if (json.data && json.data.normalList) {
                processItemList(json.data.normalList.itemList);
            }

            if (json.data && json.data.areaBoxList) {
                json.data.areaBoxList.forEach(box => {
                    processItemList(box.itemList);
                });
            }

        } catch (e) {
            log("搜索出错: " + e.message);
        }

        setResult(d);
    })
};