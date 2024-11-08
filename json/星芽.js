var rule = {
    类型: '影视',
    title: '星芽短剧[优]',
    host: 'https://app.whjzjx.cn',
    url: '/cloud/v2/theater/home_page?theater_class_id=fyclass&type=1&class2_ids=0&page_num=fypage&page_size=24',
    //    https://app.whjzjx.cn/cloud/v2/theater/home_page?theater_class_id=1&type=1&class2_ids=0&page_num=1&page_size=24
    //https://app.whjzjx.cn/cloud/v2/theater/home_page?theater_class_id=1&type=1&class2_ids=0&page_num=2&page_size=24
    searchUrl: '/v3/search',
    searchable: 2,
    quickSearch: 0,
    headers: {
        'User-Agent': 'okhttp/4.10.0',
        'authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjY1MTQ3MzYsIlVzZXJJZCI6NTcxMjk0OTgsInJlZ2lzdGVyX3RpbWUiOiIyMDI0LTA5LTAyIDAzOjI1OjM2IiwiaXNfbW9iaWxlX2JpbmQiOmZhbHNlfQ.umYgwq2KknucsWGImHSJEEKpRXol6Mu7S6YSZlgb26Q'
    },
    timeout: 5000,
    class_name: '剧场&热播剧&星选好剧&新剧&阳光剧场',
    class_url: '1&2&7&3&5',
    play_parse: true,
    lazy: $js.toString(() => {
        input = {
            url: input,
            parse: 0
        }
    }),
    double: true,
    一级: $js.toString(() => {
        let d = [];
        let html = request(input);
        let data = JSON.parse(html).data.list;
        data.forEach(it => {
            let id = 'https://app.whjzjx.cn/v2/theater_parent/detail?theater_parent_id=' + it.theater.id;
            d.push({
                url: id,
                title: it.theater.title,
                img: it.theater.cover_url,
                desc: it.theater.theme,
            })
        })
        setResult(d);
    }),
    二级: $js.toString(() => {
        let urls = [];
        let html = request(input);
        let data = JSON.parse(html).data;
        data.theaters.forEach(it => {
            urls.push(it.num + '$' + it.son_video_url);
        })
        VOD = {
            vod_name: data.title,
            vod_pic: data.cover_url,
            vod_play_from: '完美',
            vod_play_url: urls.join('#')
        };
    }),
    搜索: $js.toString(() => {
        let d = [];
        let html = post(input, {
            body: {
                "text": KEY
            }
        })
        let list = JSON.parse(html).data.theater.search_data;
        list.forEach(it => {
            let id = 'https://app.whjzjx.cn/v2/theater_parent/detail?theater_parent_id=' + it.id;
            d.push({
                url: id,
                title: it.title,
                img: it.cover_url,
                content: it.introduction,
            })
        })
        setResult(d);
    }),
}