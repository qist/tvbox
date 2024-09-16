/**
 *    原创诺临风
 *  原创时间：2024-05-07
 *  转载请不要删除此版权声明
 */


var rule = {
    title: "新茶杯狐",
    host: "https://www.cbhfox.com/",
    url: "/chbys/fyfilter.html",
    searchable: 2,
    quickSearch: 0,
    filterable: 1,
    detailUrl: "/cbhtv/fyid.html",
    homeUrl: "/label/hot.html",
    filter_url: "{{fl.cateId}}{{fl.area}}{{fl.by}}{{fl.class}}{{fl.lang}}{{fl.letter}}/page/fypage{{fl.year}}",
    filter: 'H4sIAAAAAAAAA+2ZW1MaSRiG/wvXbjFjNse7nM/nc7ZyQbJUQtaQLdGtYlNWeYKgUVFKIa4Yk43nFUHjugiF/hlmgH+xDd180/MOVYyb1F71pe/z+k331+3wfvjW83PAFwwHgi88p3566/nFH/ac8jzv8oVCng5P0Pfaz340RlbMoQj7+TdfV6+/4QvW5chqbWi1LrMfPH0dQk2mmV+o3kYlr9CalkpsS9SzLEJrWsyBSbM/abcIjR40uloupeFBXKMHrUwZe0V4ENeoCu1NqsI1WkvsQ7kwAmvhWtNSzSwbY+t2i9BoLaPZSgksQpN2VJkuOnZU18iy9M6xI6HRcjPL5f1PsFyuUZVooja7BlW4RlU+rrM9QhWuHeKMzMGNSnIKLFwjy9CoOfgHWLhGrSvGjUgeWse1pqU2nzA/LNktQqMHJd9VRwrwIK5RX/Y3K9N/G6UtaA3JZIwvVr/greEaWSaiRnwbLFyjW3MwyY4Xbg3XrJNKm/NTeFINjSzDB5W/YOtCowaWpirFdKut2Ujf0/ov8FeAr9vvk94A6ZwxVnD7Blhcqc1Gm8+pF/KW8xljriQAndnyrJnPtvAJYDU7Z+7tt6rHAe1yf4KJNp+Q6IkLa+gQEh3J+y10CImuUWrJTG/YHEKybtE/WENIVONrDh1CohrjOaOwbK/BJavGjLPGjO0pw3HWcSO2ZjeRSnteOqjEM5WRWfu2SbVeT5/M9wfsl+3LIpV8kd1yMWk3cUm+YF0+9pFDF6yazVRX+91esLkS8zcfUC/kFZJ0jOgQEl2W7UV0CIkuS6pkjKfQZKnSpXKYuCRdGXQISTpMh4NL0qVy7JlLUtuNzSG7g0ty28N+X7f0d723Uy6WXLa9U+v8sVm+XsbbECR6BOkRmXYi7ZSpjlSXqYZUk6h+EigTJHoC6QmZHkd6XKbHkB6T6VGkR2WKvdLlXunYK13ulY690uVe6dgrXe6Vjr3S5V5p2CtN7pWGvdLkXmnYDU3uhobd0ORuaNgNJtjeBv6eHr98MTMpMzvu8mKepkvfqOI9TeQMkDNEzgI5S+QckHNEzgM5T+QCkAtELgK5SOQSkEtELgO5TOQKkCtErgK5SuQakGtErgO5TuQGkBtEbgK5SeQWkFtEbgO5TeQOkDtE7gK5S+QekHtE7gO5T+QBkAdEHgJ5SOQRkEdEHgN5TOQJkCdEtB9OAqsr8p/As7B1/c2JhFGIO66/mdqtpXaadZ6FvT0BZm8+olwomLlpib4M9ISsj8TssBGLSjT0/E23v76Cpx2NGTD0MvCq93sNge3zsYupigd4Y2DXGIq3ivaCHGLyNDZ3jUIGLFw73JzWbvJ0Mae5mDxdzBAuZqPy3mfHDCE0awiLmLNZOAyu0Vpmoo6BUGjSmOE4AKG1zoaiijMcfsv0EY0wvz19csn9FNBiMmk/k8A00n5OaD+vtJ8TXMwryRyL6Mb8Z3sZUlVq/8+pXSVulbhV4laJWyVulbgPm7h/fxN8EQ58W9y2XmC1/pHKSj9kZK7JEW94wRnxmEYL3jyo5mJ2i9CoSiJjjsKXzUKzPjcjZh4SqdCsD9+v5b1JWC7XpHBU+wLLFRpZCuvG5kewcI3WMrft/M6fa1RlesHcwf8RcY2q5PNmLF4uJBzf1tsItXHnT5bAoY1co4pbg9WBMajFtf8tBrM4yyKrPRVySUpALBNhhK1L5NhYYYdid3BJhUYVGlVoVKFRhUYVGlVo/F5f07LQ+Drok1KjSggqIaiEoBKCSggqIaiEoBLCq0BX768BX1BFBBURVERQEUFFBI+KCCoiqIjQjAh9/wLqgnhI8TMAAA==',
    filter_def: {
        dianying: {cateId: "dianying"},
        dianshiju: {cateId: "dianshiju"},
        zongyi: {cateId: "zongyi"},
        dongmna: {cateId: "dongmna"},
        jilupian: {cateId: "jilupian"},
    },
    class_name: "电影&剧集&动漫&综艺&记录片",
    class_url: "dianying&dianshiju&dongmna&zongyi&jilupian",
    headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/"
    },
    play_parse: true,
    lazy: `js:	
		var html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
        var url = html.url;
        var from = html.from;
        if (html.encrypt == '1') {
            url = decodeURI(url)
        } else if (html.encrypt == '2') {
            url = decodeURI(base64Decode(url))
        }
        if (/\.m3u8|\.mp4/.test(url)) {
            input = url
        } else {
            var currentDate = new Date();
            var year = currentDate.getFullYear();
            var month = String(currentDate.getMonth() + 1).padStart(2, '0');
            var day = String(currentDate.getDate()).padStart(2, '0');
            const urlTime = year + month + day;
            var MacPlayerConfig = {};
            eval(fetch(HOST + '/static/js/playerconfig.js?t=' + urlTime).replace('var Mac', 'Mac'));
            var parseUrl = MacPlayerConfig.player_list[from].parse;
            if (parseUrl && parseUrl != "") {
				let $playUrl = "";
				if(parseUrl.startsWith("http")){
					$playUrl = parseUrl;
				}else{
					$playUrl = HOST + parseUrl;
				}
                input = {
                    url: url,
                    playUrl: $playUrl,
                    parse: 1,
                    header: JSON.stringify({
                        'user-agent': 'Mozilla/5.0',
                        'Origin': input
                    })
                }
            } else {
                input       
            }
        }
	`,
    推荐: `js:
        let d = [];
        pdfh = jsp.pdfh;pdfa = jsp.pdfa;pd = jsp.pd;
        let html = request(input);
		let items = pdfa(html, "div.module-items div.module-card-item");
		function shuffleArray(array) {
            for (let i = array.length - 1; i > 0; i--) {
              const j = Math.floor(Math.random() * (i + 1));
              [array[i], array[j]] = [array[j], array[i]];
            }
            return array;
        }
		const shuffledArray = shuffleArray(items);
        shuffledArray.forEach(it => {
            d.push({
				url:pdfh(it,"div.module-card-item-title&&a&&href"),
                title:pdfh(it,"div.module-card-item-title&&a&&Text"),
                img:pdfh(it,"div.module-item-pic&&img&&data-original"),
                desc:pdfh(it,"div.module-card-item-class&&Text") + "/" + pdfh(it,"div.module-item-note&&Text")
            })
        });
        setResult(d);
    `,
    一级: `js:
        var d = [];
        pdfh = jsp.pdfh;pdfa = jsp.pdfa;pd = jsp.pd;
        var html = request(input);
        let items = pdfa(html, "a.module-item");		
        items.forEach(it => {
            d.push({
                url:pdfh(it,"a&&href"),
                title:pdfh(it,"a&&title"),
                img:pdfh(it,"div.module-item-pic&&img&&data-original"),
                desc:pdfh(it,"div.module-item-note&&Text")
            })
        });
        setResult(d)
    `,
    二级: $js.toString(() => {
        VOD = {};
        let html = request(input);
        VOD.vod_name = pdfh(html, "h1&&Text");
        VOD.vod_pic = pd(html, ".module-item-pic&&img&&data-original");
        VOD.vod_year = pdfh(html, ".module-info-tag-link:eq(0)&&Text");
        VOD.vod_area = pdfh(html, ".module-info-tag-link:eq(1)&&Text");
        VOD.type_name = pdfh(html, ".module-info-tag-link:eq(2)&&Text");
        VOD.vod_actor = pdfh(html, ".module-info-item-content:eq(1)&&Text");
        VOD.vod_director = pdfh(html, ".module-info-item-content:eq(0)&&Text");
        VOD.vod_remarks = "不信广告就你赢了";
        VOD.vod_content = pdfh(html, ".module-info-introduction-content&&Text");
        if (typeof play_url === "undefined") {
            var play_url = ""
        }
        let playFrom = [];
        let playUrl = [];
        let tabs = pdfa(html, "div.module-tab-item");
        tabs.forEach((it, index) => {
            playFrom.push('諾临風-' + pdfh(it, 'span&&Text') + "[" + pdfh(it, 'small&&Text') + "]");
            let playTag = "div.module-play-list:eq(" + index + ") a";
            let tags = pdfa(html, playTag);
            let mapUrl = tags.map((tag) => {
                let title = pdfh(tag, "a&&Text").trim();
                let purl = pd(tag, "a&&href");
                return title + "$" + play_url + urlencode(purl);
            });
            playUrl.push(mapUrl.join("#"))
        });
        VOD.vod_play_from = playFrom.join("$$$");
        VOD.vod_play_url = playUrl.join("$$$");
    }),
    double: false,
    searchUrl: "/index.php/vod/search/wd/**.html",
    搜索: `js:
        var d = [];
        pdfh = jsp.pdfh;pdfa = jsp.pdfa;pd = jsp.pd;
        var html = request(input);       
        let list = pdfa(html, "div.module-item");
        list.forEach(it => {
            d.push({
                title: pdfh(it, "div.module-card-item-title&&Text"),
                desc: pdfh(it, "div.module-item-note&&Text"),
                pic_url: pdfh(it, "div.module-item-pic&&img&&data-original"),
                url: pdfh(it, "div.module-card-item-title&&a&&href")
            })
        });
        setResult(d)
    `
};
