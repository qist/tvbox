var rule = {
    title: '360影视[官]',
    host: 'https://www.360kan.com',
    homeUrl: 'https://api.web.360kan.com/v1/rank?cat=2&size=9',
    detailUrl: 'https://api.web.360kan.com/v1/detail?cat=fyclass&id=fyid',
    searchUrl: 'https://api.so.360kan.com/index?force_v=1&kw=**&from=&pageno=fypage&v_ap=1&tab=all',
    url: 'https://api.web.360kan.com/v1/fyfilter&size=35&pageno=fypage&callback=',
    filterable: 1,
    filter_url: 'filter/list?catid=fyclass&rank={{fl.排序}}&cat={{fl.类型}}&year={{fl.年代}}&area={{fl.地区}}',
    filter: {
        "1": [{
            "key": "类型",
            "name": "类型",
            "value": [{
                "n": "全部",
                "v": ""
            }, {
                "n": "喜剧",
                "v": "喜剧"
            }, {
                "n": "爱情",
                "v": "爱情"
            }, {
                "n": "动作",
                "v": "动作"
            }, {
                "n": "恐怖",
                "v": "恐怖"
            }, {
                "n": "科幻",
                "v": "科幻"
            }, {
                "n": "剧情",
                "v": "剧情"
            }, {
                "n": "犯罪",
                "v": "犯罪"
            }, {
                "n": "奇幻",
                "v": "奇幻"
            }, {
                "n": "战争",
                "v": "战争"
            }, {
                "n": "悬疑",
                "v": "悬疑"
            }, {
                "n": "动画",
                "v": "动画"
            }, {
                "n": "文艺",
                "v": "文艺"
            }, {
                "n": "纪录",
                "v": "纪录"
            }, {
                "n": "传记",
                "v": "传记"
            }, {
                "n": "歌舞",
                "v": "歌舞"
            }, {
                "n": "古装",
                "v": "古装"
            }, {
                "n": "历史",
                "v": "历史"
            }, {
                "n": "惊悚",
                "v": "惊悚"
            }, {
                "n": "伦理",
                "v": "伦理"
            }, {
                "n": "其他",
                "v": "其他"
            }]
        }, {
            "key": "地区",
            "name": "地区",
            "value": [{
                "n": "全部",
                "v": ""
            }, {
                "n": "内地",
                "v": "大陆"
            }, {
                "n": "中国香港",
                "v": "香港"
            }, {
                "n": "中国台湾",
                "v": "台湾"
            }, {
                "n": "泰国",
                "v": "泰国"
            }, {
                "n": "美国",
                "v": "美国"
            }, {
                "n": "韩国",
                "v": "韩国"
            }, {
                "n": "日本",
                "v": "日本"
            }, {
                "n": "法国",
                "v": "法国"
            }, {
                "n": "英国",
                "v": "英国"
            }, {
                "n": "德国",
                "v": "德国"
            }, {
                "n": "印度",
                "v": "印度"
            }, {
                "n": "其他",
                "v": "其他"
            }]
        }, {
            "key": "年代",
            "name": "年代",
            "value": [{
                "n": "全部",
                "v": ""
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
            }, {
                "n": "2014",
                "v": "2014"
            }, {
                "n": "2013",
                "v": "2013"
            }, {
                "n": "2012",
                "v": "2012"
            }, {
                "n": "2010",
                "v": "2010"
            }, {
                "n": "2009",
                "v": "2009"
            }, {
                "n": "2008",
                "v": "2008"
            }, {
                "n": "2007",
                "v": "2007"
            }, {
                "n": "更早",
                "v": "lt_year"
            }]
        }, {
            "key": "排序",
            "name": "排序",
            "value": [{
                "n": "最近热映",
                "v": "rankhot"
            }, {
                "n": "最近上映",
                "v": "ranklatest"
            }, {
                "n": "最受好评",
                "v": "rankpoint"
            }]
        }],
        "2": [{
            "key": "类型",
            "name": "类型",
            "value": [{
                "n": "全部",
                "v": ""
            }, {
                "n": "言情",
                "v": "言情"
            }, {
                "n": "剧情",
                "v": "剧情"
            }, {
                "n": "伦理",
                "v": "伦理"
            }, {
                "n": "喜剧",
                "v": "喜剧"
            }, {
                "n": "悬疑",
                "v": "悬疑"
            }, {
                "n": "都市",
                "v": "都市"
            }, {
                "n": "偶像",
                "v": "偶像"
            }, {
                "n": "古装",
                "v": "古装"
            }, {
                "n": "军事",
                "v": "军事"
            }, {
                "n": "警匪",
                "v": "警匪"
            }, {
                "n": "历史",
                "v": "历史"
            }, {
                "n": "励志",
                "v": "励志"
            }, {
                "n": "神话",
                "v": "神话"
            }, {
                "n": "谍战",
                "v": "谍战"
            }, {
                "n": "青春",
                "v": "青春剧"
            }, {
                "n": "家庭",
                "v": "家庭剧"
            }, {
                "n": "动作",
                "v": "动作"
            }, {
                "n": "情景",
                "v": "情景"
            }, {
                "n": "武侠",
                "v": "武侠"
            }, {
                "n": "科幻",
                "v": "科幻"
            }, {
                "n": "其他",
                "v": "其他"
            }]
        }, {
            "key": "地区",
            "name": "地区",
            "value": [{
                "n": "全部",
                "v": ""
            }, {
                "n": "内地",
                "v": "内地"
            }, {
                "n": "中国香港",
                "v": "香港"
            }, {
                "n": "中国台湾",
                "v": "台湾"
            }, {
                "n": "泰国",
                "v": "泰国"
            }, {
                "n": "日本",
                "v": "日本"
            }, {
                "n": "韩国",
                "v": "韩国"
            }, {
                "n": "美国",
                "v": "美国"
            }, {
                "n": "英国",
                "v": "英国"
            }, {
                "n": "新加坡",
                "v": "新加坡"
            }]
        }, {
            "key": "年代",
            "name": "年代",
            "value": [{
                "n": "全部",
                "v": ""
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
            }, {
                "n": "2014",
                "v": "2014"
            }, {
                "n": "2013",
                "v": "2013"
            }, {
                "n": "2012",
                "v": "2012"
            }, {
                "n": "2010",
                "v": "2010"
            }, {
                "n": "2009",
                "v": "2009"
            }, {
                "n": "2008",
                "v": "2008"
            }, {
                "n": "2007",
                "v": "2007"
            }, {
                "n": "更早",
                "v": "lt_year"
            }]
        }, {
            "key": "排序",
            "name": "排序",
            "value": [{
                "n": "最近热映",
                "v": "rankhot"
            }, {
                "n": "最近上映",
                "v": "ranklatest"
            }, {
                "n": "最受好评",
                "v": "rankpoint"
            }]
        }],
        "3": [{
            "key": "类型",
            "name": "类型",
            "value": [{
                "n": "全部",
                "v": ""
            }, {
                "n": "脱口秀",
                "v": "脱口秀"
            }, {
                "n": "真人秀",
                "v": "真人秀"
            }, {
                "n": "搞笑",
                "v": "搞笑"
            }, {
                "n": "选秀",
                "v": "选秀"
            }, {
                "n": "八卦",
                "v": "八卦"
            }, {
                "n": "访谈",
                "v": "访谈"
            }, {
                "n": "情感",
                "v": "情感"
            }, {
                "n": "生活",
                "v": "生活"
            }, {
                "n": "晚会",
                "v": "晚会"
            }, {
                "n": "音乐",
                "v": "音乐"
            }, {
                "n": "职场",
                "v": "职场"
            }, {
                "n": "美食",
                "v": "美食"
            }, {
                "n": "时尚",
                "v": "时尚"
            }, {
                "n": "游戏",
                "v": "游戏"
            }, {
                "n": "少儿",
                "v": "少儿"
            }, {
                "n": "体育",
                "v": "体育"
            }, {
                "n": "纪实",
                "v": "纪实"
            }, {
                "n": "科教",
                "v": "科教"
            }, {
                "n": "曲艺",
                "v": "曲艺"
            }, {
                "n": "歌舞",
                "v": "歌舞"
            }, {
                "n": "财经",
                "v": "财经"
            }, {
                "n": "汽车",
                "v": "汽车"
            }, {
                "n": "播报",
                "v": "播报"
            }, {
                "n": "其他",
                "v": "其他"
            }]
        }, {
            "key": "地区",
            "name": "地区",
            "value": [{
                "n": "全部",
                "v": ""
            }, {
                "n": "内地",
                "v": "大陆"
            }, {
                "n": "中国香港",
                "v": "香港"
            }, {
                "n": "中国台湾",
                "v": "台湾"
            }, {
                "n": "日本",
                "v": "日本"
            }, {
                "n": "欧美",
                "v": "欧美"
            }]
        }, {
            "key": "排序",
            "name": "排序",
            "value": [{
                "n": "最近热映",
                "v": "rankhot"
            }, {
                "n": "最近上映",
                "v": "ranklatest"
            }]
        }],
        "4": [{
            "key": "类型",
            "name": "类型",
            "value": [{
                "n": "全部",
                "v": ""
            }, {
                "n": "热血",
                "v": "热血"
            }, {
                "n": "科幻",
                "v": "科幻"
            }, {
                "n": "美少女",
                "v": "美少女"
            }, {
                "n": "魔幻",
                "v": "魔幻"
            }, {
                "n": "经典",
                "v": "经典"
            }, {
                "n": "励志",
                "v": "励志"
            }, {
                "n": "少儿",
                "v": "少儿"
            }, {
                "n": "冒险",
                "v": "冒险"
            }, {
                "n": "搞笑",
                "v": "搞笑"
            }, {
                "n": "推理",
                "v": "推理"
            }, {
                "n": "恋爱",
                "v": "恋爱"
            }, {
                "n": "治愈",
                "v": "治愈"
            }, {
                "n": "幻想",
                "v": "幻想"
            }, {
                "n": "校园",
                "v": "校园"
            }, {
                "n": "动物",
                "v": "动物"
            }, {
                "n": "机战",
                "v": "机战"
            }, {
                "n": "亲子",
                "v": "亲子"
            }, {
                "n": "儿歌",
                "v": "儿歌"
            }, {
                "n": "运动",
                "v": "运动"
            }, {
                "n": "悬疑",
                "v": "悬疑"
            }, {
                "n": "怪物",
                "v": "怪物"
            }, {
                "n": "战争",
                "v": "战争"
            }, {
                "n": "益智",
                "v": "益智"
            }, {
                "n": "青春",
                "v": "青春"
            }, {
                "n": "童话",
                "v": "童话"
            }, {
                "n": "竞技",
                "v": "竞技"
            }, {
                "n": "动作",
                "v": "动作"
            }, {
                "n": "社会",
                "v": "社会"
            }, {
                "n": "友情",
                "v": "友情"
            }, {
                "n": "真人版",
                "v": "真人版"
            }, {
                "n": "电影版",
                "v": "电影版"
            }, {
                "n": "OVA版",
                "v": "OVA版"
            }, {
                "n": "TV版",
                "v": "TV版"
            }, {
                "n": "新番动画",
                "v": "新番动画"
            }, {
                "n": "完结动画",
                "v": "完结动画"
            }]
        }, {
            "key": "地区",
            "name": "地区",
            "value": [{
                "n": "全部",
                "v": ""
            }, {
                "n": "内地",
                "v": "大陆"
            }, {
                "n": "日本",
                "v": "日本"
            }, {
                "n": "美国",
                "v": "美国"
            }]
        }, {
            "key": "年代",
            "name": "年代",
            "value": [{
                "n": "全部",
                "v": ""
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
            }, {
                "n": "2014",
                "v": "2014"
            }, {
                "n": "2013",
                "v": "2013"
            }, {
                "n": "2012",
                "v": "2012"
            }, {
                "n": "2011",
                "v": "2011"
            }, {
                "n": "2010",
                "v": "2010"
            }, {
                "n": "2009",
                "v": "2009"
            }, {
                "n": "2008",
                "v": "2008"
            }, {
                "n": "2007",
                "v": "2007"
            }, {
                "n": "2006",
                "v": "2006"
            }, {
                "n": "2005",
                "v": "2005"
            }, {
                "n": "2004",
                "v": "2004"
            }, {
                "n": "更早",
                "v": "更早"
            }]
        }, {
            "key": "排序",
            "name": "排序",
            "value": [{
                "n": "最近热映",
                "v": "rankhot"
            }, {
                "n": "最近上映",
                "v": "ranklatest"
            }]
        }]
    },
    filter_def: {},
    headers: {
        'User-Agent': 'MOBILE_UA'
    },
    timeout: 5000,
    class_name: '电视剧&电影&综艺&动漫',
    class_url: '2&1&3&4',
    limit: 5,
    multi: 1,
    searchable: 2,
    play_parse: true,
    lazy: $js.toString(() => {
        try {
            let api = "" + input.split("?")[0];
            console.log(api);
            let response = fetch(api, {
                method: 'get',
                headers: {
                    'User-Agent': 'okhttp/3.14.9',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });
            let bata = JSON.parse(response);
            if (bata.url.includes("qq,qiyi,imgo,youku,leshi,bilibili1,m1905")) {
                input = {
                    parse: 0,
                    url: bata.url,
                    jx: 0,
                    danmaku: "http://103.45.162.207:25252/hbdm.php?key=7894561232&id=" + input.split("?")[0]
                };
            } else {
                input = {
                    parse: 0,
                    url: input.split("?")[0],
                    jx: 1,
                    danmaku: "http://103.45.162.207:25252/hbdm.php?key=7894561232&id=" + input.split("?")[0]
                };
            }
        } catch {
            input = {
                parse: 0,
                url: input.split("?")[0],
                jx: 1,
                danmaku: "http://103.45.162.207:25252/hbdm.php?key=7894561232&id=" + input.split("?")[0]
            };
        }
    }),
    // 疑似t4专用的
    // lazy:'js:input={parse: 1, playUrl: "", jx: 1, url: input.split("?")[0]}',
    // 手动调用解析请求json的url,此lazy不方便
    // lazy:'js:input="https://cache.json.icu/home/api?type=ys&uid=292796&key=fnoryABDEFJNPQV269&url="+input.split("?")[0];log(input);let html=JSON.parse(request(input));log(html);input=html.url||input',
    推荐: 'json:data;title;cover;comment;cat+ent_id;description',
    一级: 'json:data.movies;title;cover;pubdate;id;description',
    二级: '',
    二级: $js.toString(() => {
        let html = JSON.parse(fetch(input, fetch_params));
        let data = html.data;
        let tilte = data.title;
        let img = data.cdncover;
        let vod_type = data.moviecategory.join(",");
        let area = data.area.join(",");
        let director = data.director.join(",");
        let actor = data.actor.join(",");
        let content = data.description;
        let base_vod = {
            vod_id: input,
            vod_name: tilte,
            type_name: vod_type,
            vod_actor: actor,
            vod_director: director,
            vod_content: content,
            vod_remarks: area,
            vod_pic: urljoin2(input, img)
        };
        let delta = 50;
        let vod_play = {};
        let sites = data.playlink_sites;
        sites.forEach(function(site) {
            let playList = "";
            let vodItems = [];
            print(data)
            if (data.allupinfo) {
                let total = parseInt(data.allupinfo[site]);
                print(total)
                for (let j = 1; j < total; j += delta) {
                    let end = Math.min(total, j + delta - 1);
                    print(end)
                    let url2 = buildUrl(input, {
                        start: j,
                        end: end,
                        site: site
                    });
                    let vod_data = JSON.parse(fetch(url2), fetch_params).data;
                    if (vod_data != null) {
                        if (vod_data.allepidetail) {
                            vod_data = vod_data.allepidetail[site];
                            vod_data.forEach(function(item, index) {
                                vodItems.push((item.playlink_num || "") + "$" + urlDeal(item.url || ""))
                            })
                        } else {
                            vod_data = vod_data.defaultepisode;
                            vod_data.forEach(function(item, index) {
                                vodItems.push((item.period || "") + (item.name || "") + "$" + urlDeal(item.url) || "")
                            })
                        }
                    }
                }
            } else {
                let item = data.playlinksdetail[site];
                vodItems.push((item.sort || "") + "$" + urlDeal(item.default_url || ""))
            }
            if (vodItems.length > 0) {
                playList = vodItems.join("#")
            }
            if (playList.length < 1) {
                return
            }
            vod_play[site] = playList
        });
        let tabs = Object.keys(vod_play);
        let playUrls = [];
        for (let id in tabs) {
            print("id:" + id);
            playUrls.push(vod_play[tabs[id]])
        }
        if (tabs.length > 0) {
            let vod_play_from = tabs.join("$$$");
            let vod_play_url = playUrls.join("$$$");
            base_vod.vod_play_from = vod_play_from;
            base_vod.vod_play_url = vod_play_url
        }
        VOD = base_vod;
    }),
    搜索: 'json:data.longData.rows;titleTxt||titlealias;cover;cat_name;cat_id+en_id;description',
}