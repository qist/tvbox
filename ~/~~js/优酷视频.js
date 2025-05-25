var rule = {
    title: '优酷[官]',
    host: 'https://www.%79%6f%75%6b%75.com',
    homeUrl: '',
    searchUrl: 'https://search.%79%6f%75%6b%75.com/api/search?pg=fypage&keyword=**',
    searchable: 2,
    quickSearch: 0,
    filterable: 1,
    multi: 1,
    url: '/category/data?optionRefresh=1&pageNo=fypage&params=fyfilter',
    filter_url: '{{fl}}',
    filter: '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',
    headers: {
        'User-Agent': 'PC_UA',
        'Cookie': 'cna=VvNvGX3e0ywCAavVEXlnA2bg; __ysuid=1626676228345Rl1; __ayft=1652434048647; __arycid=dm-1-00; __arcms=dm-1-00; __ayvstp=85; __arpvid=1667204023100cWWdgM-1667204023112; __ayscnt=10; __aypstp=60; isg=BBwcqxvvk3BxkWQGugbLpUSf7TrOlcC_U7GAj_YdfYfvQbzLHqYGT4Hgp6m5TvgX; tfstk=c3JOByYUH20ilVucLOhh0pCtE40lZfGc-PjLHLLfuX7SWNyAiQvkeMBsIw7PWDC..; l=eBQguS-PjdJFGJT-BOfwourza77OSIRA_uPzaNbMiOCPOb1B5UxfW6yHp4T6C3GVhsGJR3rp2umHBeYBqQd-nxvOF8qmSVDmn',
        'Referer': 'https://www.youku.com',
    },
    timeout: 5000,
    class_name: '电视剧&电影&综艺&动漫&少儿&纪录片&文化&亲子&教育&搞笑&生活&体育&音乐&游戏',
    class_url: '电视剧&电影&综艺&动漫&少儿&纪录片&文化&亲子&教育&搞笑&生活&体育&音乐&游戏',
    limit: 20,
    play_parse: true,
    lazy: $js.toString(() => {
        input = {
            parse: 1,
            jx: 1,
            url: input
        };
    }),
    一级: $js.toString(() => {
        let d = [];
        MY_FL.type = MY_CATE;
        let fl = stringify(MY_FL);
        fl = encodeUrl(fl);
        input = input.split("{")[0] + fl;
        if (MY_PAGE > 1) {
            let old_session = getItem("yk_session_" + MY_CATE, "{}");
            if (MY_PAGE === 2) {
                input = input.replace("optionRefresh=1", "session=" + encodeUrl(old_session))
            } else {
                input = input.replace("optionRefresh=1", "session=" + encodeUrl(old_session))
            }
        }
        let html = fetch(input, fetch_params);
        try {
            html = JSON.parse(html);
            let lists = html.data.filterData.listData;
            let session = html.data.filterData.session;
            session = stringify(session);
            if (session !== getItem("yk_session_" + MY_CATE, "{}")) {
                setItem("yk_session_" + MY_CATE, session)
            }
            lists.forEach(function (it) {
                let vid;
                if (it.videoLink.includes("id_")) {
                    vid = it.videoLink.split("id_")[1].split(".html")[0]
                } else {
                    vid = "msearch:"
                }
                d.push({
                    title: it.title,
                    img: it.img,
                    desc: it.summary,
                    url: "https://search.youku.com/api/search?appScene=show_episode&showIds=" + vid,
                    content: it.subTitle
                })
            })
        } catch (e) {
            log("一级列表解析发生错误:" + e.message)
        }
        setResult(d);
    }),
    二级: $js.toString(() => {
        var d = [];
        VOD = {};
        let html = request(input);
        let json = JSON.parse(html);
        if (/keyword/.test(input)) {
            input = "https://search.youku.com/api/search?appScene=show_episode&showIds=" + json.pageComponentList[0].commonData.showId;
            json = JSON.parse(fetch(MY_URL, fetch_params))
        }
        let video_lists = json.serisesList;
        var name = json.sourceName;
        if (/优酷/.test(name) && video_lists.length > 0) {
            let ourl = "https://v.youku.com/v_show/id_" + video_lists[0].videoId + ".html";
            let _img = video_lists[0].thumbUrl;
            let html = fetch(ourl, {
                headers: {
                    Referer: "https://v.youku.com/",
                    "User-Agent": PC_UA
                }
            });
            let json = /__INITIAL_DATA__/.test(html) ? html.split("window.__INITIAL_DATA__ =")[1].split(";")[0] : "{}";
            if (json === "{}") {
                log("触发了优酷人机验证");
                VOD.vod_remarks = ourl;
                VOD.vod_pic = _img;
                VOD.vod_name = video_lists[0].title.replace(/(\d+)/g, "");
                VOD.vod_content = "触发了优酷人机验证,本次未获取详情,但不影响播放(" + ourl + ")"
            } else {
                try {
                    json = JSON.parse(json);
                    let data = json.data.data;
                    let data_extra = data.data.extra;
                    let img = data_extra.showImgV;
                    let model = json.data.model;
                    let m = model.detail.data.nodes[0].nodes[0].nodes[0].data;
                    let _type = m.showGenre;
                    let _desc = m.updateInfo || m.subtitle;
                    let JJ = m.desc;
                    let _title = m.introTitle;
                    VOD.vod_pic = img;
                    VOD.vod_name = _title;
                    VOD.vod_type = _type;
                    VOD.vod_remarks = _desc;
                    VOD.vod_content = JJ
                } catch (e) {
                    log("海报渲染发生错误:" + e.message);
                    print(json);
                    VOD.vod_remarks = name
                }
            }
        }
        if (!/优酷/.test(name)) {
            VOD.vod_content = "非自家播放源,暂无视频简介及海报";
            VOD.vod_remarks = name
        }

        function adhead(url) {
            return urlencode(url)
        }

        play_url = play_url.replace("&play_url=", "&type=json&play_url=");
        video_lists.forEach(function (it) {
            let url = "https://v.youku.com/v_show/id_" + it.videoId + ".html";
            if (it.thumbUrl) {
                d.push({
                    desc: it.showVideoStage ? it.showVideoStage.replace("期", "集") : it.displayName,
                    pic_url: it.thumbUrl,
                    title: it.title,
                    url: play_url + adhead(url)
                })
            } else if (name !== "优酷") {
                d.push({
                    title: it.displayName ? it.displayName : it.title,
                    url: play_url + adhead(it.url)
                })
            }
        });
        VOD.vod_play_from = name;
        VOD.vod_play_url = d.map(function (it) {
            return it.title + "$" + it.url
        })
            .join("#");
    }),

    搜索: $js.toString(() => {
        var d = [];
        let html = request(input);
        let json = JSON.parse(html);
        json.pageComponentList.forEach(function (it) {
            if (it.hasOwnProperty("commonData")) {
                it = it.commonData;
                d.push({
                    title: it.titleDTO.displayName,
                    img: it.posterDTO.vThumbUrl,
                    desc: it.stripeBottom,
                    content: it.updateNotice + " " + it.feature,
                    url: "https://search.youku.com/api/search?appScene=show_episode&showIds=" + it.showId + "&appCaller=h5"
                })
            }
        });
        setResult(d)
    }),
}