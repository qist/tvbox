var rule = {
    title: '弹幕[资]',
    host: 'http://gy.xn--yet24tmq1a.xyz/',
    homeTid: '',
    homeUrl: '/api.php/provide/vod/?ac=detail&t={{rule.homeTid}}',
    detailUrl: '/api.php/provide/vod/?ac=detail&ids=fyid',
    searchUrl: '/api.php/provide/vod/?ac=detail&wd=**&pg=fypage',
    url: '/api.php/provide/vod/?ac=detail&pg=fypage&t=fyclass',
    headers: {
        'User-Agent': 'MOBILE_UA',
    },
    class_parse: 'json:class;',
    timeout: 5000,
    filterable: 1,
    limit: 20,
    multi: 1,
    searchable: 2,
    play_parse: true,
    parse_url: '',
    lazy: $js.toString(() => {
        let json = request("http://103.45.162.207:25252/hbdm.php?key=7894561232&id=" + input);
        let bata = JSON.parse(json);
        input = {
            parse: 0,
            url: bata.url,
            jx: 0,
            danmaku: bata.danmaku
        };
    }),
    推荐: 'json:list;vod_name;vod_pic;vod_remarks;vod_id;vod_play_from',
    一级: $js.toString(() => {
        let bata = JSON.parse(request(input)).list;
        bata.forEach(it => {
            d.push({
                url: it.vod_id,
                title: it.vod_name,
                img: it.vod_pic,
                desc: it.vod_remarks
            })
        });
        setResult(d)
    }),
    二级: 'js:\n      let html=request(input);\n      html=JSON.parse(html);\n      let data=html.list;\n      VOD=data[0];',
    搜索: 'json:list;vod_name;vod_pic;vod_remarks;vod_id;vod_play_from',
}