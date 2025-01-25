// 注入全局方法 (仅支持tvbox的js1以及c#版drpy的js0，暂不支持drpy官方py版的js0)
// 注入全局方法 (仅支持tvbox的js1以及c#版drpy的js0，暂不支持drpy官方py版的js0)
// 注入全局方法 (仅支持tvbox的js1以及c#版drpy的js0，暂不支持drpy官方py版的js0)
globalThis.getHeaders= function(input){
    let t = new Date().getTime().toString();
	let headers = {
        'version_name': '1.0.6',
        'version_code': '6',
        'package_name': 'com.app.nanguatv',
        'sign': md5('c431ea542cee9679#uBFszdEM0oL0JRn@' + t).toUpperCase(),
        'imei': 'c431ea542cee9679',
        'timeMillis': t,
        'User-Agent': 'okhttp/4.6.0'
	};
	return headers
}
	
var rule = {
	title:'南瓜影视',
	host:'http://ys.changmengyun.com',
	homeUrl:'/api.php/provide/vod_rank?app=ylys&sort_type=month&imei=c431ea542cee9679&id=2&page=1',
    url:'/api.php/provide/vod_list?app=ylys&id=fyclassfyfilter&page=fypage&imei=c431ea542cee9679',
    detailUrl:'/api.php/provide/vod_detail?app=ylys&imei=c431ea542cee9679&id=fyid',
    searchUrl:'/api.php/provide/search_result_more?app=ylys&video_name=**&pageSize=20&tid=0&imei=c431ea542cee9679&page=fypage',
	searchable:2,
	quickSearch:0,
	filterable:1,
	filter_url:'&area={{fl.area}}&year={{fl.year}}&type={{fl.class}}&total={{fl.total or "状态"}}&order={{fl.by or "新上线"}}',
    filter:{
        "2":[{"key":"class","name":"类型","value":[{"n":"全部","v":"类型"},{"n":"国产剧","v":"国产剧"},{"n":"港台剧","v":"港台剧"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":"地区"},{"n":"🇨🇳中国","v":"内地"},{"n":"香港地区","v":"香港地区"},{"n":"台湾地区","v":"台湾地区"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":"年份"},{"n":"2025","v":"2025"},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"10年代","v":"10年代"},{"n":"00年代","v":"00年代"},{"n":"90年代","v":"90年代"},{"n":"80年代","v":"80年代"}]},{"key":"by","name":"排序","value":[{"n":"热播榜","v":"热播榜"},{"n":"好评榜","v":"好评榜"},{"n":"新上线","v":"新上线"}]}],
        "1":[{"key":"class","name":"类型","value":[{"n":"全部","v":"类型"},{"n":"动作片","v":"动作片"},{"n":"喜剧片","v":"喜剧片"},{"n":"爱情片","v":"爱情片"},{"n":"科幻片","v":"科幻片"},{"n":"恐怖片","v":"恐怖片"},{"n":"剧情片","v":"剧情片"},{"n":"战争片","v":"战争片"},{"n":"惊悚片","v":"惊悚片"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":"地区"},{"n":"华语","v":"华语"},{"n":"香港地区","v":"香港地区"},{"n":"🇺🇸美国","v":"美国"},{"n":"欧洲","v":"欧洲"},{"n":"🇰🇷韩国","v":"韩国"},{"n":"🇯🇵日本","v":"日本"},{"n":"台湾地区","v":"台湾地区"},{"n":"泰国","v":"泰国"},{"n":"台湾地区","v":"台湾地区"},{"n":"印度","v":"印度"},{"n":"其它","v":"其它"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":"年份"},{"n":"2025","v":"2025"},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"10年代","v":"10年代"},{"n":"00年代","v":"00年代"},{"n":"90年代","v":"90年代"},{"n":"80年代","v":"80年代"}]},{"key":"by","name":"排序","value":[{"n":"热播榜","v":"热播榜"},{"n":"好评榜","v":"好评榜"},{"n":"新上线","v":"新上线"}]}],
        "4":[{"key":"class","name":"类型","value":[{"n":"全部","v":"类型"},{"n":"国产漫","v":"国产漫"},{"n":"欧美漫","v":"欧美漫"},{"n":"日韩漫","v":"日韩漫"},{"n":"港台漫","v":"港台漫"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":"地区"},{"n":"🇨🇳中国","v":"中国大陆"},{"n":"🇯🇵日本","v":"日本"},{"n":"🇰🇷韩国","v":"韩国"},{"n":"欧美","v":"欧美"},{"n":"其它","v":"其它"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":"年份"},{"n":"2025","v":"2025"},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"10年代","v":"10年代"},{"n":"00年代","v":"00年代"},{"n":"90年代","v":"90年代"},{"n":"80年代","v":"80年代"}]},{"key":"by","name":"排序","value":[{"n":"热播榜","v":"热播榜"},{"n":"新上线","v":"新上线"}]},{"key":"total","name":"状态","value":[{"n":"全部","v":"状态"},{"n":"连载","v":"连载"},{"n":"完结","v":"完结"}]}],
        "3":[{"key":"class","name":"类型","value":[{"n":"全部","v":"类型"},{"n":"🇨🇳中国","v":"大陆"},{"n":"港台","v":"港台"},{"n":"日韩","v":"日韩"},{"n":"欧美","v":"欧美"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":"地区"},{"n":"🇨🇳中国","v":"内地"},{"n":"港台","v":"港台"},{"n":"日韩","v":"日韩"},{"n":"欧美","v":"欧美"},{"n":"其它","v":"其它"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":"年份"},{"n":"2025","v":"2025"},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"10年代","v":"10年代"},{"n":"00年代","v":"00年代"},{"n":"90年代","v":"90年代"},{"n":"80年代","v":"80年代"}]},{"key":"by","name":"排序","value":[{"n":"热播榜","v":"热播榜"},{"n":"新上线","v":"新上线"}]}],
        "46":[{"key":"class","name":"类型","value":[{"n":"全部","v":"类型"},{"n":"日韩剧","v":"日韩剧"},{"n":"欧美剧","v":"欧美剧"},{"n":"海外剧","v":"海外剧"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":"地区"},{"n":"🇰🇷韩国","v":"韩国"},{"n":"美剧","v":"美剧"},{"n":"🇯🇵日本","v":"日本"},{"n":"泰国","v":"泰国"},{"n":"英国","v":"英国"},{"n":"新加坡","v":"新加坡"},{"n":"其他","v":"其他"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":"年份"},{"n":"2025","v":"2025"},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"10年代","v":"10年代"},{"n":"00年代","v":"00年代"},{"n":"90年代","v":"90年代"},{"n":"80年代","v":"80年代"}]},{"key":"by","name":"排序","value":[{"n":"热播榜","v":"热播榜"},{"n":"好评榜","v":"好评榜"},{"n":"新上线","v":"新上线"}]}]
    },
	headers:{
		"User-Agent":"okhttp/4.6.0"
	},
	timeout:5000,
	class_name:'电视剧&电影&动漫&综艺&海外精选', // /api.php/provide/home_nav
	class_url:'2&1&4&3&46',
	limit:20,
	play_parse:true,
	lazy:`js:
        try {
            function getvideo(url) {
                let jData = JSON.parse(request(url, {
                    headers: getHeaders(url)
                }));
                if (jData.code == 1) {
                    return jData.data.url
                } else {
                    return 'http://43.154.104.152:1234/jhapi/cs.php?url=' + url.split('=')[1]
                }
            }
            if (/,/.test(input)) {
                let mjurl = input.split(',')[1]
                let videoUrl = getvideo(mjurl);
                input = {
                    jx: 0,
                    url: videoUrl,
                    parse: 0,
                    header: JSON.stringify({
                        'user-agent': 'Lavf/58.12.100'
                    })
                }
            } else {
                let videoUrl = getvideo(input);
                if (/jhapi/.test(videoUrl)) {
                    videoUrl = getvideo(videoUrl);
                    input = {
                        jx: 0,
                        url: videoUrl,
                        parse: 0,
                        header: JSON.stringify({
                            'user-agent': 'Lavf/58.12.100'
                        })
                    }
                } else {
                    input = {
                        jx: 0,
                        url: videoUrl,
                        parse: 0
                    }
                }
            }
        } catch (e) {
            log(e.toString())
        }
	`,
	推荐:`js:
        var d = [];
        let html = request(input, {
            headers: getHeaders(input)
        });
        html = JSON.parse(html);
        html.forEach(function(it) {
            d.push({
                title: it.name,
                img: it.img,
                desc: it.remarks,
                url: it.id
            })
        });
        setResult(d);
    `,
	一级:`js:
		var d = [];
		let html = request(input, {
			headers: getHeaders(input)
		});
		html = JSON.parse(html);
		html.list.forEach(function(it) {
			d.push({
				title: it.name,
				img: it.img,
				desc: it.msg,
				url: it.id
			})
		});
		setResult(d);
	`,
	二级:`js:
        var d = [];
        VOD = {
            vod_id: input.split('id=')[1]
        };
        try {
            let html = request(input, {
                headers: getHeaders(input)
            });
            html = JSON.parse(html);
            let node = html.data;
            VOD = {
                vod_name: node['name'],
                vod_pic: node['img'],
                type_name: node['type'],
                vod_year: node['year'],
                vod_remarks: '更新至: ' + node['msg'] + ' / 评分: ' + node['score'],
                vod_content: node['info'].strip()
            };
            let episodes = node.player_info;
            let playMap = {};
            if (typeof play_url === 'undefined') {
                var play_url = ''
            }
            episodes.forEach(function(ep) {
                let playurls = ep['video_info'];
                playurls.forEach(function(playurl) {
                    let source = ep['show'];
                    if (!playMap.hasOwnProperty(source)) {
                        playMap[source] = []
                    }
                    playMap[source].append(playurl['name'].strip() + '$' + play_url + urlencode(playurl['url']))
                })
            });
            let playFrom = [];
            let playList = [];
            Object.keys(playMap)
                .forEach(function(key) {
                    playFrom.append(key);
                    playList.append(playMap[key].join('#'))
                });
            let vod_play_from = playFrom.join('$$$');
            let vod_play_url = playList.join('$$$');
            VOD['vod_play_from'] = vod_play_from;
            VOD['vod_play_url'] = vod_play_url
        } catch (e) {
            log('获取二级详情页发生错误:' + e.message)
        }
	`,
	搜索:`js:
        var d = [];
        let html = request(input, {
            headers: getHeaders(input)
        });
        html = JSON.parse(html);
        html.data.forEach(function(it) {
            d.push({
                title: it.video_name,
                img: it.img,
                desc: it.qingxidu + '/' + it.category,
                url: it.id,
                content: it.blurb
            })
        });
        setResult(d);
    `,
}