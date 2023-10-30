var rule = {
    title: '美益达[V2]', // csp_AppYsV2
	host:'https://www.myd666.tv/api.php/v1.vod',
    url: 'video?tid=fyclassfyfilter&limit=20&pg=fypage',
    filter_url:'&class={{fl.class}}&area={{fl.area}}&lang={{fl.lang}}&letter={{fl.letter}}&year={{fl.year}}&by={{fl.by}}',
	filter:{
		"1":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"动作","v":"动作"},{"n":"喜剧","v":"喜剧"},{"n":"爱情","v":"爱情"},{"n":"科幻","v":"科幻"},{"n":"恐怖","v":"恐怖"},{"n":"剧情","v":"剧情"},{"n":"战争","v":"战争"},{"n":"家庭","v":"家庭"},{"n":"奇幻","v":"奇幻"},{"n":"魔幻","v":"魔幻"},{"n":"冒险","v":"冒险"},{"n":"歌舞","v":"歌舞"},{"n":"院线","v":"院线"},{"n":"悬疑","v":"悬疑"},{"n":"惊悚","v":"惊悚"},{"n":"犯罪","v":"犯罪"},{"n":"警匪","v":"警匪"},{"n":"枪战","v":"枪战"},{"n":"网络电影","v":"网络电影"},{"n":"古装","v":"古装"},{"n":"灾难","v":"灾难"},{"n":"传记","v":"传记"},{"n":"华语","v":"华语"},{"n":"纪实","v":"纪实"},{"n":"青春","v":"青春"},{"n":"历史","v":"历史"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"大陆"},{"n":"香港","v":"香港"},{"n":"台湾","v":"台湾"},{"n":"美国","v":"美国"},{"n":"法国","v":"法国"},{"n":"英国","v":"英国"},{"n":"日本","v":"日本"},{"n":"韩国","v":"韩国"},{"n":"德国","v":"德国"},{"n":"泰国","v":"泰国"},{"n":"印度","v":"印度"},{"n":"意大利","v":"意大利"},{"n":"西班牙","v":"西班牙"},{"n":"加拿大","v":"加拿大"},{"n":"其他","v":"其他"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"法语","v":"法语"},{"n":"德语","v":"德语"},{"n":"其它","v":"其它"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
		"2":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"国产","v":"国产"},{"n":"香港","v":"香港"},{"n":"台湾","v":"台湾"},{"n":"韩国","v":"韩国"},{"n":"日本","v":"日本"},{"n":"泰国","v":"泰国"},{"n":"海外","v":"海外"},{"n":"欧美","v":"欧美"},{"n":"家庭","v":"家庭"},{"n":"悬疑","v":"悬疑"},{"n":"犯罪","v":"犯罪"},{"n":"惊悚","v":"惊悚"},{"n":"爱情","v":"爱情"},{"n":"剧情","v":"剧情"},{"n":"青春","v":"青春"},{"n":"古装","v":"古装"},{"n":"奇幻","v":"奇幻"},{"n":"都市","v":"都市"},{"n":"情感","v":"情感"},{"n":"言情","v":"言情"},{"n":"玄幻","v":"玄幻"},{"n":"芒果出品","v":"芒果出品"},{"n":"校园","v":"校园"},{"n":"励志","v":"励志"},{"n":"农村","v":"农村"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"大陆"},{"n":"韩国","v":"韩国"},{"n":"香港","v":"香港"},{"n":"台湾","v":"台湾"},{"n":"日本","v":"日本"},{"n":"美国","v":"美国"},{"n":"泰国","v":"泰国"},{"n":"英国","v":"英国"},{"n":"新加坡","v":"新加坡"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
		"3":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"大陆综艺","v":"大陆综艺"},{"n":"港台综艺","v":"港台综艺"},{"n":"日韩综艺","v":"日韩综艺"},{"n":"欧美综艺","v":"欧美综艺"},{"n":"真人秀","v":"真人秀"},{"n":"相声","v":"相声"},{"n":"脱口秀","v":"脱口秀"},{"n":"喜剧","v":"喜剧"},{"n":"搞笑","v":"搞笑"},{"n":"访谈","v":"访谈"},{"n":"情感","v":"情感"},{"n":"文化","v":"文化"},{"n":"明星","v":"明星"},{"n":"旅游","v":"旅游"},{"n":"教育","v":"教育"},{"n":"亲子","v":"亲子"},{"n":"美食","v":"美食"},{"n":"游戏","v":"游戏"},{"n":"养成","v":"养成"},{"n":"音乐","v":"音乐"},{"n":"生活","v":"生活"},{"n":"竞演","v":"竞演"},{"n":"晚会","v":"晚会"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"大陆"},{"n":"香港","v":"香港"},{"n":"台湾","v":"台湾"},{"n":"韩国","v":"韩国"},{"n":"美国","v":"美国"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
		"4":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"国产动漫","v":"国产动漫"},{"n":"港台动漫","v":"港台动漫"},{"n":"日韩动漫","v":"日韩动漫"},{"n":"欧美动漫","v":"欧美动漫"},{"n":"热血","v":"热血"},{"n":"冒险","v":"冒险"},{"n":"玄幻","v":"玄幻"},{"n":"武侠","v":"武侠"},{"n":"动漫","v":"动漫"},{"n":"动作","v":"动作"},{"n":"动画","v":"动画"},{"n":"奇幻","v":"奇幻"},{"n":"古装","v":"古装"},{"n":"搞笑","v":"搞笑"},{"n":"励志","v":"励志"},{"n":"青春","v":"青春"},{"n":"校园","v":"校园"},{"n":"恋爱","v":"恋爱"},{"n":"漫画改编","v":"漫画改编"},{"n":"TV版","v":"TV版"},{"n":"治愈","v":"治愈"},{"n":"职场","v":"职场"},{"n":"日常","v":"日常"},{"n":"益智","v":"益智"},{"n":"合家欢","v":"合家欢"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"大陆"},{"n":"日本","v":"日本"},{"n":"美国","v":"美国"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"英语","v":"英语"},{"n":"粤语","v":"粤语"},{"n":"闽南语","v":"闽南语"},{"n":"韩语","v":"韩语"},{"n":"日语","v":"日语"},{"n":"其它","v":"其它"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}]
	},
    detailUrl:'/detail?vod_id=fyid',
    searchUrl: '/search?text=**&pg=fypage',
    searchable: 2,
    quickSearch: 0,
    filterable:1,//是否启用分类筛选,
    headers:{'User-Agent':'okhttp/4.1.0'},
    timeout:5000,
    // 分类筛选 /api.php/app/nav || /xgapp.php/v1/nav || /api.php/v1.vod/types
    class_name:'电影&电视剧&综艺&动漫',
    class_url:'1&2&3&4',
    play_parse:true,
	lazy:`js:
		let play_Url = '';
		if (/\\.m3u8|\\.mp4/.test(input)) {
			input = {
				jx: 0,
				url: input,
				parse: 0
			}
		} else if (/,/.test(input) && /url=/.test(input)) {
			input = input.split('url=');
			play_Url = input[0].split(',')[0];
			input = {
				jx: 0,
				url: input[1],
				playUrl: play_Url,
				parse: 1
			}
		} else if (/url=|id=/.test(input)) {
			input = {
				jx: 0,
				url: JSON.parse(request(input)).url,
				parse: 0
			}
        } else if (/youku|iqiyi|v\\.qq\\.com|pptv|sohu|le\\.com|1905\\.com|mgtv|bilibili|ixigua/.test(input)) {
			play_Url = /bilibili/.test(input) ? 'https://jx.xmflv.com/?url=' : 'https://jx.777jiexi.com/player/?url='; // type0的parse
			// play_Url = /bilibili/.test(input) ? 'https://jx.xmflv.com/?url=' : 'json:http://pandown.pro/app/kkdy.php?url='; // type1的parse可加'json:'直接解析url (除了蜂蜜的'影视TV'，其它的壳皆可用)
			input = {
				jx: 0,
				url: input,
				playUrl: play_Url,
				parse: 1,
				header: JSON.stringify({
					'user-agent': 'Mozilla/5.0',
				}),
			}
		} else {
			input
		}
    `,
    limit:6,
    // 图片来源:'@Referer=https://api.douban.com/@User-Agent=Mozilla/5.0%20(Windows%20NT%2010.0;%20Win64;%20x64)%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/113.0.0.0%20Safari/537.36',
    推荐:`js:
        let d = [];
        let jsondata = [];
        let videoList = [];
        if (/v1\\.vod/.test(HOST)) {
            if(HOST.endsWith('/')){
                jsondata = JSON.parse(request(HOST + 'vodPhbAll'));
            } else {
                jsondata = JSON.parse(request(HOST + '/vodPhbAll'));
            }
            videoList = jsondata.data.list;
        } else {
            if(HOST.endsWith('/')){
                jsondata = JSON.parse(request(HOST + 'index_video'));
            } else {
                jsondata = JSON.parse(request(HOST + '/index_video'));
            }
            videoList = /xgapp/.test(HOST) ? jsondata.data : jsondata.list;
        }
        // log('videoList =========> '+stringify(videoList));
        videoList.forEach((it,idex) => {
            let vlist = /v1\\.vod/.test(HOST) ? videoList[idex].vod_list : videoList[idex].vlist ;
            vlist.forEach(it => {
                d.push({
                    url:it.vod_id,
                    title:it.vod_name,
                    img:it.vod_pic.startsWith('http') ? it.vod_pic : it.vod_pic.startsWith('//') ? 'https:' + it.vod_pic : it.vod_pic.startsWith('/') ? getHome(HOST) + it.vod_pic : getHome(HOST) + '/' + it.vod_pic,
                    desc:it.vod_remarks,
                });
            });
        });
        setResult(d);
    `,
    一级:`js:
        let d = [];
        let jsondata = [];
        let videoList = [];
        if (/v1\\.vod/.test(HOST)) {
            input = input.replace('video','v1.vod').replace('tid','type').replace('pg=','page=');
            jsondata = JSON.parse(request(input));
            videoList = jsondata.data.list;
        } else {
            input = HOST + '/'+ input.split('/')[4];
            jsondata = JSON.parse(request(input));
            videoList = jsondata.list || jsondata.data;
        }
        // log('videoList =========> '+stringify(videoList));
        videoList.forEach(it => {
            d.push({
                url:it.vod_id,
                title:it.vod_name,
                img:it.vod_pic.startsWith('http') ? it.vod_pic : it.vod_pic.startsWith('//') ? 'https:' + it.vod_pic : it.vod_pic.startsWith('/') ? getHome(HOST) + it.vod_pic : getHome(HOST) + '/' + it.vod_pic,
                desc:it.vod_remarks,
            });
        });
        setResult(d);
    `,
	二级:`js: 
		if (/v1\\.vod/.test(HOST)) {
			input = HOST + '/'+ input.split('/')[3];
		} else {
			input = HOST + '/'+ input.split('/')[3].replace('detail','video_detail').replace('vod_id','id');
		}
		try {
			let html = request(input);
			html = JSON.parse(html);
			let node = /xgapp/.test(HOST) ? html.data.vod_info : html.data;
			VOD = {
				vod_id: node.vod_id,
				vod_name: node.vod_name,
				vod_pic: node.vod_pic,
				type_name: node.vod_class,
				vod_year: node.vod_year,
				vod_area: node.vod_area,
				vod_remarks: node.vod_remarks,
				vod_actor: node.vod_actor,
				vod_director: node.vod_director,
				vod_content: node.vod_content.strip()
			};
			if (typeof play_url === 'undefined') {
				var play_url = ''
			}
			var name = {
				'bfzym3u8': '暴风',
				'1080zyk': '优质',
				'kuaikan': '快看',
				'lzm3u8': '量子',
				'ffm3u8': '非凡',
				'haiwaikan': '海外看',
				'gsm3u8': '光速',
				'zuidam3u8': '最大',
				'bjm3u8': '八戒',
				'snm3u8': '索尼',
				'wolong': '卧龙',
				'xlm3u8': '新浪',
				'yhm3u8': '樱花',
				'tkm3u8': '天空',
				'jsm3u8': '极速',
				'wjm3u8': '无尽',
				'sdm3u8': '闪电',
				'kcm3u8': '快车',
				'jinyingm3u8': '金鹰',
				'fsm3u8': '飞速',
				'tpm3u8': '淘片',
				'lem3u8': '鱼乐',
				'dbm3u8': '百度',
				'tomm3u8': '番茄',
				'ukm3u8': 'U酷',
				'ikm3u8': '爱坤',
				'hnzym3u8': '红牛资源',
				'hnm3u8': '红牛',
				'68zy_m3u8': '68',
				'kdm3u8': '酷点',
				'bdxm3u8': '北斗星',
				'qhm3u8': '奇虎',
				'hhm3u8': '豪华',
				'kbm3u8': '快播'
			};
			let episodes = /v1\\.vod/.test(HOST)?node.vod_play_list:node.vod_url_with_player;
			if (episodes != '') {
				let playMap = {};
				let arr = [];
				episodes.forEach(ep => {
					let from = [];
					if (/v1\\.vod/.test(HOST)) {
						from = ep.player_info.from||ep.player_info.show||ep.from||ep.show;
					} else {
						from = ep.code||ep.name;
					}
					if (!playMap.hasOwnProperty(from)) {
						playMap[from] = []
					}
					let parse_api = '';
					if (/v1\\.vod/.test(HOST)) {
						parse_api = ep.player_info.parse != null ? ep.player_info.parse : ep.player_info.parse2;
						// parse_api = /,/.test(parse_api) ? parse_api.split(',')[1] : parse_api;
					} else {
						parse_api = ep.parse_api;
					}
					log('parse_api =========> '+parse_api);
					if (parse_api != null && !/\\.m3u8|\\.mp4/.test(ep.url)) {
						parse_api = parse_api.replaceAll('..','.') ;
						ep.url = ep.url.replaceAll('$','$'+parse_api);
					}
					if (from != null) playMap[from].push(ep.url)
				});
				for (var key in playMap) {
					if ('bfzym3u8' == key) {
						arr.push({
							flag: name[key],
							url: playMap[key],
							sort: 1
						})
					} else if ('1080zyk' == key) {
						arr.push({
							flag: name[key],
							url: playMap[key],
							sort: 2
						})
					} else if ('kuaikan' == key) {
						arr.push({
							flag: name[key],
							url: playMap[key],
							sort: 3
						})
					} else if ('lzm3u8' == key) {
						arr.push({
							flag: name[key],
							url: playMap[key],
							sort: 4
						})
					} else if ('ffm3u8' == key) {
						arr.push({
							flag: name[key],
							url: playMap[key],
							sort: 5
						})
					} else if ('snm3u8' == key) {
						arr.push({
							flag: name[key],
							url: playMap[key],
							sort: 6
						})
					} else if ('qhm3u8' == key) {
						arr.push({
							flag: name[key],
							url: playMap[key],
							sort: 7
						})
					} else {
						arr.push({
							flag: name[key] ? name[key] : key,
							url: playMap[key],
							sort: 8
						})
					}
				}
				arr.sort((a, b) => a.sort - b.sort);
				let playFrom = [];
				let playList = [];
				arr.map(val => {
					if (!/undefined/.test(val.flag)) {
						playFrom.push(val.flag);
						playList.push(val.url);
					}
				})
				VOD.vod_play_from = playFrom.join('$$$');
				VOD.vod_play_url = playList.join('$$$');
			} else {
				VOD.vod_play_from = node.vod_play_from;
				VOD.vod_play_url = node.vod_play_url;
			}
		} catch (e) {
			log("获取二级详情页发生错误:" + e.message);
		}
	`,
	搜索:`js:
		let d = [];
		let jsondata = [];
		let videoList = [];
		if (/v1\\.vod/.test(HOST)) {
			input = (HOST + '/'+ input.split('/')[3]).replace('/search','').replace('text=','wd=').replace('pg=','page=');
			jsondata = JSON.parse(request(input));
			videoList = jsondata.data.list;
		} else {
			input = HOST + '/'+ input.split('/')[3]
			jsondata = JSON.parse(request(input));
			videoList = jsondata.list || jsondata.data;
		}
		// log('videoList =========> '+stringify(videoList));
		videoList.forEach(it => {
			d.push({
				url:it.vod_id,
				title:it.vod_name,
				img:it.vod_pic.startsWith('http') ? it.vod_pic : it.vod_pic.startsWith('//') ? 'https:' + it.vod_pic : it.vod_pic.startsWith('/') ? getHome(HOST) + it.vod_pic : getHome(HOST) + '/' + it.vod_pic,
				desc:it.vod_remarks,
			});
		});
		setResult(d);
	`,
}