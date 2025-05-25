 
var rule = {
    title: '蓝莓短剧',
    host: 'https://app.whjzjx.cn',
    url: '/v1/theater/home_page?theater_class_id=1&class2_id=fyclass&page_num=fypage&page_size=24',
    searchUrl: '/?**',
    searchable: 2,
    quickSearch: 1,
    // filterable: 1,
    class_name: '古装&穿越&逆袭&重生',
    class_url: '5&17&7&6',
    一级: $js.toString(() => {
        let d = [];
        let urlk = `https://app.whjzjx.cn/v1/theater/home_page?theater_class_id=${MY_CATE}&page_num=${MY_PAGE - 1}&page_size=24`;
        let tkurl = 'https://app.whjzjx.cn/v1/account/login';
        let head = JSON.parse(post(tkurl, {
            headers: {
                "Connection": "keep-alive",
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": "40",
                "user-agent": "okhttp/4.10.0",
                "user_agent": "Mozilla/5.0 (Linux; Android 9; ASUS_I003DD Build/PI; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.70 Mobile Safari/537.36",
                "Host": "app.whjzjx.cn",
                "Accept-Encoding": "gzip"
            },
            body: "device=20caaae96b3443174bf4ebdbdcc253776"
        })).data.token;
        let header={"authorization":head};
        let html = JSON.parse(request(urlk, {
            headers: header
        }));
        let bata = html.data.list;
        bata.forEach(it => {
            let id = 'https://app.whjzjx.cn/v2/theater_parent/detail?theater_parent_id=' + it.theater.id;
            d.push({
                url: id,
                title: it.theater.title,
                img: it.theater.cover_url,
                desc: it.theater.total + "集",
                content: "播放量:" + it.theater.play_amount_str,
            });
        });
        setResult(d);
    }),
    二级: $js.toString(() => {
        let urls = [];
        let tkurl = 'https://app.whjzjx.cn/v1/account/login';
        let head = JSON.parse(post(tkurl, {
            headers: {
                "Connection": "keep-alive",
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": "40",
                "user-agent": "okhttp/4.10.0",
                "user_agent": "Mozilla/5.0 (Linux; Android 9; ASUS_I003DD Build/PI; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.70 Mobile Safari/537.36",
                "Host": "app.whjzjx.cn",
                "Accept-Encoding": "gzip"
            },
            body: "device=20caaae96b3443174bf4ebdbdcc253776"
        })).data.token;
        let header={"authorization":head};
        let data = JSON.parse(request(input, {
            headers: header
        })).data;
        //console.log(data);
        data.theaters.forEach(it => {
            urls.push("第" + it.num + "集" + '$' + it.son_video_url);
        });
        VOD = {
            vod_name: data.title,
            vod_pic: data.cover_url,
            vod_remarks: data.total + "集",
            vod_play_from: 'XT短剧',
            vod_play_url: urls.join('#')
        };
    }),
    搜索: $js.toString(() => {
        let d = [];
        let ht = input.match(/\?(.*)/)[1];
        let ser = "https://app.whjzjx.cn/v2/search";
        let tkurl = 'https://app.whjzjx.cn/v1/account/login';
        let head = JSON.parse(post(tkurl, {
            headers: {
                "Connection": "keep-alive",
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": "40",
                "user-agent": "okhttp/4.10.0",
                "user_agent": "Mozilla/5.0 (Linux; Android 9; ASUS_I003DD Build/PI; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.70 Mobile Safari/537.36",
                "Host": "app.whjzjx.cn",
                "Accept-Encoding": "gzip"
            },
            body: "device=20caaae96b3443174bf4ebdbdcc253776"
        })).data.token;
        let header={"authorization":head};
        let html = JSON.parse(post(ser, {
            headers: header,
            body: "text=" + ht
        }));
        let bata = html.data.search_data;
        bata.forEach(it => {
            let id = 'https://app.whjzjx.cn/v2/theater_parent/detail?theater_parent_id=' + it.id;
            d.push({
                url: id,
                title: it.title,
                img: it.cover_url,
                desc: it.score_str + "|" + it.total + "集",
            });
        });
        setResult(d);
    }),
};
 