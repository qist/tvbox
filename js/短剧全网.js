var rule = {
    title: '全网短剧搜|虎斑',
    siteurl: "http://xsayang.fun:14710",
    host: "http://127.0.0.1/",
    pic: "https://gimg3.baidu.com/search/src=http%3A%2F%2Fgips0.baidu.com%2Fit%2Fu%3D3826931526%2C1218106811%26fm%3D3030%26app%3D3030%26f%3DJPEG%3Fw%3D255%26h%3D170%26s%3D09A77732952477015C5349470200E0E2&refer=http%3A%2F%2Fwww.baidu.com&app=2021&size=f242,150&n=0&g=0n&q=100&fmt=auto?sec=1744995600&t=7adeeb1928d2f75b9dcf68740fff3e4c",
    baidupic: "https://img0.baidu.com/it/u=2646803025,2626552004&fm=253&fmt=auto&app=138&f=PNG?w=500&h=500",
    detailUrl: 'fyid',
    searchUrl: '**',
    url: 'fyclass',
    searchable: 1,
    quickSearch: 0,
    filterable: 0,
    headers: {
        'User-Agent': 'MOBILE_UA',
    },
    timeout: 20000,
    play_parse: true,
    lazy: $js.toString(() => {
        input = "push://" + input;
    }),
    double: false,
    推荐: '',
    一级: '',
    二级: $js.toString(() => {
        const parts = input.replace(rule.host + "/", "").split('~~');
        if (decodeURIComponent(parts[0]) == "网络") {
            const options = {
                method: 'POST',
                headers: {},
                body: {
                    'url': urlencode(parts[2]),
                    'title': decodeURIComponent(parts[1])
                }
            };
            let html = request(rule.siteurl + "/api/other/save_url", options)
            parts[2] = JSON.parse(html).data.url;
        }
        let picsm;
        if (parts[2].includes("baidu")) {
            picsm = rule.baidupic;
        } else {
            picsm = rule.pic;
        }
        let data = {
            vod_name: decodeURIComponent(parts[1]),
            vod_pic: picsm,
            vod_play_from: '推送',
            vod_play_url: "推送$" + parts[2]
        };
        VOD = data;
    }),
    搜索: $js.toString(() => {
        let html2 = request(rule.siteurl + "/api/other/web_search?title=" + input.replace(rule.host + "/", "") + "&is_type=2");
        //  console.log(html);
        const strArray2 = html2.split('\n');
        for (const s of strArray2) {
            if (s.includes('data') && !s.includes('DONE')) {
                const jsonStr = s.replace(/^data:/, '');
                try {
                    const js = JSON.parse(jsonStr);
                    const name = js.title || '';
                    const url = js.url || '';
                    d.push({
                        url: "网络" + "~~" + name + "~~" + url,
                        title: name,
                        img: rule.baidupic,
                    })
                } catch (e) {
                    console.error('解析JSON失败:', e);
                }
            }
        }

        let html1 = request(rule.siteurl + "/api/other/web_search?title=" + input.replace(rule.host + "/", "") + "&is_type=0");
        //  console.log(html);
        const strArray = html1.split('\n');
        for (const s of strArray) {
            if (s.includes('data') && !s.includes('DONE')) {
                const jsonStr = s.replace(/^data:/, '');
                try {
                    const js = JSON.parse(jsonStr);
                    const name = js.title || '';
                    const url = js.url || '';
                    d.push({
                        url: "网络" + "~~" + name + "~~" + url,
                        title: name,
                        img: rule.pic,
                    })
                } catch (e) {
                    console.error('解析JSON失败:', e);
                }
            }
        }

        let html = request(rule.siteurl + "/s/" + input.replace(rule.host + "/", ""), {})
        const regex = /copyText\(\$event,'([^']+)','([^']+)'/g;
        let matcher;
        while ((matcher = regex.exec(html)) !==
            null) {
            const title = matcher[1];
            const url = matcher[2];
            let picsm;
            if (url.includes("baidu")) {
                picsm = rule.baidupic;
            } else {
                picsm = rule.pic;
            }
            d.push({
                url: "本地" + "~~" + title + "~~" + url,
                title: title,
                img: picsm,
            })
        }

        setResult(d)
    }),
}