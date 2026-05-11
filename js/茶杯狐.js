var rule = {
    title: '茶杯狐',
    host: 'https://www.cupfox.in',
    url: '/type/fyclass/?page=fypage',
    searchUrl: '/search?q=**',
    searchable: 2,
    quickSearch: 1,
    filterable: 0,
    headers: {
        'User-Agent': 'PC_UA',
    },
    class_name: '电视剧&电影&动漫&综艺&纪录片',
    class_url: 'tv&movie&anime&show&doc',
    play_parse: true,
    limit: 6,
    推荐: '*',
    一级: $js.toString(() => {
        let html = request(input);
        let items = pdfa(html, '.movie-list-item');
        let seen = {};
        VODS = items.map((it) => {
            let url = pd(it, 'a:eq(0)&&href', HOST);
            let id = (url.match(/vod-detail\/(\d+)\.html/) || [])[1] || url;
            let title = pdfh(it, '.movie-title&&Text');
            let pic = pd(it, 'img&&src', HOST);
            let remark = pdfh(it, '.movie-rating&&Text');
            if (!title || seen[id]) {
                return null;
            }
            seen[id] = true;
            return {
                vod_id: url,
                vod_name: title,
                vod_pic: pic,
                vod_remarks: remark || ''
            };
        }).filter(Boolean);
    }),
    二级: $js.toString(() => {
        let html = request(input);
        let id = (input.match(/vod-detail\/(\d+)\.html/) || [])[1];
        let title = pdfh(html, '.movie-list-title:eq(0)&&Text') || pdfh(html, 'title&&Text').replace(' 在线观看 - 茶杯狐 Cupfox', '');
        let pic = HOST + '/simg/' + id + '.jpg';
        let content = pdfh(html, 'meta[name=description]&&content');
        let subjects = pdfa(html, '.movie-list-subject-block:eq(0) .movie-list-subject').map((it) => pdfh(it, 'body&&Text')).filter(Boolean);
        let eps = pdfa(html, '.play-btn').reverse();
        let urls = eps.map((it) => {
            let ep = (pdfh(it, 'body&&Html').match(/ep_slug="([^"]+)"/) || [])[1];
            let name = pdfh(it, 'body&&Text');
            return ep && name ? name + '$' + id + '-' + ep : '';
        }).filter(Boolean);
        VOD = {
            vod_id: input,
            vod_name: title,
            vod_pic: pic,
            type_name: subjects.slice(0, 3).join(' '),
            vod_year: subjects.find((it) => /^\d{4}$/.test(it)) || '',
            vod_actor: subjects.slice(3).join(' '),
            vod_content: content,
            vod_play_from: '茶杯狐',
            vod_play_url: urls.join('#')
        };
    }),
    搜索: $js.toString(() => {
        let html = request(input);
        let items = pdfa(html, '.movie-list-item');
        let seen = {};
        VODS = items.map((it) => {
            let url = pd(it, 'a:eq(0)&&href', HOST);
            let id = (url.match(/vod-detail\/(\d+)\.html/) || [])[1] || url;
            let title = pdfh(it, '.movie-title&&Text');
            let pic = pd(it, 'img&&src', HOST);
            let remark = pdfh(it, '.movie-rating&&Text');
            if (!title || seen[id]) {
                return null;
            }
            seen[id] = true;
            return {
                vod_id: url,
                vod_name: title,
                vod_pic: pic,
                vod_remarks: remark || ''
            };
        }).filter(Boolean);
    }),
    lazy: $js.toString(() => {
        let html = request(HOST + '/tea/' + input, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
                'Referer': HOST + '/'
            }
        });
        let data = JSON.parse(html);
        let plays = data.video_plays || [];
        let url = plays.length ? plays[0].play_data : '';
        input = {
            jx: 0,
            parse: 0,
            url: url
        };
    })
};
