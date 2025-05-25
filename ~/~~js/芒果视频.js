var rule = {
    title: '百忙无果[官]',
    host: 'https://pianku.api.%6d%67%74%76.com',
    homeUrl: '',
    // searchUrl: 'https://mobileso.bz.%6d%67%74%76.com/pc/search/v1?q=**&pn=fypage&pc=10',
    // 新版接口搜索变成v2并且加了验证，蛋疼
    // searchUrl: 'https://mobileso.bz.mgtv.com/pc/search/v2?allowedRC=1&src=mgtv&did=cf03b959-6945-4cb6-bcb3-88762459354d&timestamp=2024-06-21T15%3A52%3A55Z&signVersion=1&signNonce=8dae67a1fafc4bda984ec8deb47666ad&q=**&pn=fypage&pc=10&corr=1&_support=10000000&signature=4e27fddcd2a1a66d6c1764ed6b74bab7',
    // 用手机的吧，搞不定这个
    searchUrl: 'https://mobileso.bz.%6d%67%74%76.com/msite/search/v2?q=**&pn=fypage&pc=10',
    detailUrl: 'https://pcweb.api.mgtv.com/episode/list?page=1&size=50&video_id=fyid',
    searchable: 2,
    quickSearch: 0,
    filterable: 1,
    multi: 1,
    // 分类链接fypage参数支持1个()表达式
    // https://www.mgtv.com/lib/3?lastp=list_index&kind=a1&year=all&chargeInfo=a1&sort=c2
    url: '/rider/list/pcweb/v3?platform=pcweb&channelId=fyclass&pn=fypage&pc=80&hudong=1&_support=10000000&kind=a1&area=a1',
    filter_url: 'year={{fl.year or "all"}}&sort={{fl.sort or "all"}}&chargeInfo={{fl.chargeInfo or "all"}}',
    headers: {
        'User-Agent': 'PC_UA'
    },
    timeout: 5000,
    class_name: '电视剧&电影&综艺&动漫&纪录片&教育&少儿',
    class_url: '2&3&1&50&51&115&10',
    filter: 'H4sIAAAAAAAAA+2XvUrDUBSA3+XOHc65adraN+jm5CIdYok/GFupWiilIBalIFYoIh1EBxEKIih0MOZ1msS+hbc1yTni4mKms6XfIbnnC/mG9hSq6mZP7btdVVWNXae949aa2y1VUE3nwDVsHkw+Z378FoT3l4Z2HO/EXd3SNMPwfLoYTJfY/HA8T/UL6eDK3JUMtjDjnb3DFOoMbtTW45tpOHxPR1Y2Sk4/86PxSzotqn59Of/e+ajVPqZto9E4/Lj+tWd0dxrdviYPaNA6hseD9MEN2ih+eJr7o8XzJBxepNOfx3Zdp03Hhv5sHjz+/fVo0MUEry4Zt4hbnGvimnMkjpwDcWAc1zJuLhmvEK9wXiZe5rxEvMS5TdzmnHyR+yL5IvdF8kXui+SL3BfJF7kvkC9wXyBf4L5AvsB9gXyB+wL5AvcF8oXVl1MvKC2pSWqSWh6pWZKapCap5ZGaDdKatCat5dKa/FuT1qS1XFpD80YkNolNYvv32PpfCLkneIcUAAA=',
    limit: 20,
    play_parse: true,
    // 手动调用解析请求json的url,此lazy不方便
    // lazy:'js:print(input);fetch_params.headers["user-agent"]=MOBILE_UA;let html=request(input);let rurl=html.match(/window\\.open\\(\'(.*?)\',/)[1];rurl=urlDeal(rurl);input={parse:1,url:rurl};',
    // 推荐:'.list_item;img&&alt;img&&src;a&&Text;a&&data-float',
    一级: 'json:data.hitDocs;title;img;updateInfo||rightCorner.text;playPartId',
    // 一级:'json:data.hitDocs;title;img;updateInfo;playPartId',
    二级: $js.toString(() => {
        fetch_params.headers.Referer = "https://www.mgtv.com";
        fetch_params.headers["User-Agent"] = UA;
        pdfh = jsp.pdfh;
        pdfa = jsp.pdfa;
        pd = jsp.pd;
        VOD = {};
        let d = [];
        let html = request(input);
        let json = JSON.parse(html);
        let host = "https://www.mgtv.com";
        let ourl = json.data.list.length > 0 ? json.data.list[0].url : json.data.series[0].url;
        if (!/^http/.test(ourl)) {
            ourl = host + ourl
        }
        fetch_params.headers["User-Agent"] = MOBILE_UA;
        html = request(ourl);
        if (html.includes("window.location =")) {
            print("开始获取ourl");
            ourl = pdfh(html, "meta[http-equiv=refresh]&&content").split("url=")[1];
            print("获取到ourl:" + ourl);
            html = request(ourl)
        }
        try {
            let details = pdfh(html, ".m-details&&Html").replace(/h1>/, "h6>").replace(/div/g, "br");
            print(details);
            let actor = "",
                director = "",
                time = "";
            if (/播出时间/.test(details)) {
                actor = pdfh(html, "p:eq(5)&&Text").substr(0, 25);
                director = pdfh(html, "p:eq(4)&&Text");
                time = pdfh(html, "p:eq(3)&&Text")
            } else {
                actor = pdfh(html, "p:eq(4)&&Text").substr(0, 25);
                director = pdfh(html, "p:eq(3)&&Text");
                time = "已完结"
            }
            let _img = pd(html, ".video-img&&img&&src");
            let JJ = pdfh(html, ".desc&&Text").split("简介：")[1];
            let _desc = time;
            VOD.vod_name = pdfh(html, ".vt-txt&&Text");
            VOD.type_name = pdfh(html, "p:eq(0)&&Text").substr(0, 6);
            VOD.vod_area = pdfh(html, "p:eq(1)&&Text");
            VOD.vod_actor = actor;
            VOD.vod_director = director;
            VOD.vod_remarks = _desc;
            VOD.vod_pic = _img;
            VOD.vod_content = JJ;
            if (!VOD.vod_name) {
                VOD.vod_name = VOD.type_name;
            }
        } catch (e) {
            log("获取影片信息发生错误:" + e.message)
        }

        function getRjpg(imgUrl, xs) {
            xs = xs || 3;
            let picSize = /jpg_/.test(imgUrl) ? imgUrl.split("jpg_")[1].split(".")[0] : false;
            let rjpg = false;
            if (picSize) {
                let a = parseInt(picSize.split("x")[0]) * xs;
                let b = parseInt(picSize.split("x")[1]) * xs;
                rjpg = a + "x" + b + ".jpg"
            }
            let img = /jpg_/.test(imgUrl) && rjpg ? imgUrl.replace(imgUrl.split("jpg_")[1], rjpg) : imgUrl;
            return img
        }

        if (json.data.total === 1 && json.data.list.length === 1) {
            let data = json.data.list[0];
            let url = "https://www.mgtv.com" + data.url;
            d.push({
                title: data.t4,
                desc: data.t2,
                pic_url: getRjpg(data.img),
                url: url
            })
        } else if (json.data.list.length > 1) {
            for (let i = 1; i <= json.data.total_page; i++) {
                if (i > 1) {
                    json = JSON.parse(fetch(input.replace("page=1", "page=" + i), {}))
                }
                json.data.list.forEach(function (data) {
                    let url = "https://www.mgtv.com" + data.url;
                    if (data.isIntact == "1") {
                        d.push({
                            title: data.t4,
                            desc: data.t2,
                            pic_url: getRjpg(data.img),
                            url: url
                        })
                    }
                })
            }
        } else {
            print(input + "暂无片源")
        }
        VOD.vod_play_from = "mgtv";
        VOD.vod_play_url = d.map(function (it) {
            return it.title + "$" + it.url
        }).join("#");
        setResult(d);
    }),

    搜索: $js.toString(() => {
        fetch_params.headers.Referer = "https://www.mgtv.com";
        fetch_params.headers["User-Agent"] = UA;
        let d = [];
        let html = request(input);
        let json = JSON.parse(html);
        json.data.contents.forEach(function (data) {
            if (data.type && data.type == 'media') {
                let item = data.data[0];
                let desc = item.desc.join(',');
                let fyclass = '';
                if (item.source === "imgo") {
                    let img = item.img ? item.img : '';
                    try {
                        fyclass = item.rpt.match(/idx=(.*?)&/)[1] + '$';
                    } catch (e) {
                        log(e.message);
                        fyclass = '';
                    }
                    log(fyclass);
                    d.push({
                        title: item.title.replace(/<B>|<\/B>/g, ''),
                        img: img,
                        content: '',
                        desc: desc,
                        url: fyclass + item.url.match(/.*\/(.*?)\.html/)[1]
                    })
                }
            }
        });
        setResult(d);
    }),
}