/**
 * 影视TV 超連結跳轉支持
 * https://t.me/fongmi_offical/
 * https://github.com/FongMi/Release/tree/main/apk
 */

var rule = {
	title: '荐片',
	host: 'http://112.124.0.131:20000/',
	homeUrl: '/api/tag/hand?code=unknown601193cf375db73d&channel=wandoujia',//网站的首页链接,用于分类获取和推荐获取
	// url:'/api/crumb/list?area=0&category_id=fyclass&page=fypage&type=0&limit=24&fyfilter',
	url: '/api/crumb/list?page=fypage&type=0&limit=24&fyfilter',
	class_name: '全部&电影&电视剧&动漫&综艺',     // 筛选 /api/term/ad_fenlei?limit=10&page=1
	class_url: '0&1&2&3&4',
	detailUrl: '/api/node/detail?channel=wandoujia&token=&id=fyid',//二级详情拼接链接(json格式用)
	searchUrl: '/api/video/search?key=**&page=fypage',
	searchable: 2,
	quickSearch: 0,
	filterable: 1,
	filter: {
		"0":[{"key":"area","name":"地區","value":[{"n":"全部","v":"0"},{"n":"国产","v":"1"},{"n":"中国香港","v":"3"},{"n":"中国台湾","v":"6"},{"n":"美国","v":"5"},{"n":"韩国","v":"18"},{"n":"日本","v":"2"}]},{"key":"year","name":"年代","value":[{"n":"全部","v":"0"},{"n":"2023","v":"153"},{"n":"2022","v":"101"},{"n":"2021","v":"118"},{"n":"2020","v":"16"},{"n":"2019","v":"7"},{"n":"2018","v":"2"},{"n":"2017","v":"3"},{"n":"2016","v":"22"}]},{"key":"sort","name":"排序","value":[{"n":"热门","v":"hot"},{"n":"评分","v":"rating"},{"n":"更新","v":"update"}]}],
		"1":[{"key":"cateId","name":"分类","value":[{"n":"全部","v":"1"},{"n":"首推","v":"5"},{"n":"动作","v":"6"},{"n":"喜剧","v":"7"},{"n":"战争","v":"8"},{"n":"恐怖","v":"9"},{"n":"剧情","v":"10"},{"n":"爱情","v":"11"},{"n":"科幻","v":"12"},{"n":"动画","v":"13"}]},{"key":"area","name":"地區","value":[{"n":"全部","v":"0"},{"n":"国产","v":"1"},{"n":"中国香港","v":"3"},{"n":"中国台湾","v":"6"},{"n":"美国","v":"5"},{"n":"韩国","v":"18"},{"n":"日本","v":"2"}]},{"key":"year","name":"年代","value":[{"n":"全部","v":"0"},{"n":"2023","v":"153"},{"n":"2022","v":"101"},{"n":"2021","v":"118"},{"n":"2020","v":"16"},{"n":"2019","v":"7"},{"n":"2018","v":"2"},{"n":"2017","v":"3"},{"n":"2016","v":"22"}]},{"key":"sort","name":"排序","value":[{"n":"热门","v":"hot"},{"n":"评分","v":"rating"},{"n":"更新","v":"update"}]}],
		"2":[{"key":"cateId","name":"分类","value":[{"n":"全部","v":"2"},{"n":"首推","v":"14"},{"n":"国产","v":"15"},{"n":"港台","v":"16"},{"n":"日韩","v":"17"},{"n":"海外","v":"18"}]},{"key":"area","name":"地區","value":[{"n":"全部","v":"0"},{"n":"国产","v":"1"},{"n":"中国香港","v":"3"},{"n":"中国台湾","v":"6"},{"n":"美国","v":"5"},{"n":"韩国","v":"18"},{"n":"日本","v":"2"}]},{"key":"year","name":"年代","value":[{"n":"全部","v":"0"},{"n":"2023","v":"153"},{"n":"2022","v":"101"},{"n":"2021","v":"118"},{"n":"2020","v":"16"},{"n":"2019","v":"7"},{"n":"2018","v":"2"},{"n":"2017","v":"3"},{"n":"2016","v":"22"}]},{"key":"sort","name":"排序","value":[{"n":"热门","v":"hot"},{"n":"评分","v":"rating"},{"n":"更新","v":"update"}]}],
		"3":[{"key":"cateId","name":"分类","value":[{"n":"全部","v":"3"},{"n":"首推","v":"19"},{"n":"海外","v":"20"},{"n":"日本","v":"21"},{"n":"国产","v":"22"}]},{"key":"area","name":"地區","value":[{"n":"全部","v":"0"},{"n":"国产","v":"1"},{"n":"中国香港","v":"3"},{"n":"中国台湾","v":"6"},{"n":"美国","v":"5"},{"n":"韩国","v":"18"},{"n":"日本","v":"2"}]},{"key":"year","name":"年代","value":[{"n":"全部","v":"0"},{"n":"2023","v":"153"},{"n":"2022","v":"101"},{"n":"2021","v":"118"},{"n":"2020","v":"16"},{"n":"2019","v":"7"},{"n":"2018","v":"2"},{"n":"2017","v":"3"},{"n":"2016","v":"22"}]},{"key":"sort","name":"排序","value":[{"n":"热门","v":"hot"},{"n":"评分","v":"rating"},{"n":"更新","v":"update"}]}],
		"4":[{"key":"cateId","name":"分类","value":[{"n":"全部","v":"4"},{"n":"首推","v":"23"},{"n":"国产","v":"24"},{"n":"海外","v":"25"},{"n":"港台","v":"26"}]},{"key":"area","name":"地區","value":[{"n":"全部","v":"0"},{"n":"国产","v":"1"},{"n":"中国香港","v":"3"},{"n":"中国台湾","v":"6"},{"n":"美国","v":"5"},{"n":"韩国","v":"18"},{"n":"日本","v":"2"}]},{"key":"year","name":"年代","value":[{"n":"全部","v":"0"},{"n":"2023","v":"153"},{"n":"2022","v":"101"},{"n":"2021","v":"118"},{"n":"2020","v":"16"},{"n":"2019","v":"7"},{"n":"2018","v":"2"},{"n":"2017","v":"3"},{"n":"2016","v":"22"}]},{"key":"sort","name":"排序","value":[{"n":"热门","v":"hot"},{"n":"评分","v":"rating"},{"n":"更新","v":"update"}]}]
	},
	filter_url: 'area={{fl.area or "0"}}&sort={{fl.sort or "update"}}&year={{fl.year or "0"}}&category_id={{fl.cateId}}',
	filter_def: {
		0:{cateId:'0'},
		1:{cateId:'1'},
		2:{cateId:'2'},
		3:{cateId:'3'},
		4:{cateId:'4'}
	},
	headers: {
		'User-Agent': 'jianpian-android/350',
		'JPAUTH': 'y261ow7kF2dtzlxh1GS9EB8nbTxNmaK/QQIAjctlKiEv'
	},
	timeout: 5000,
	limit: 8,
	play_parse: true,
	play_json: [{
		re: '*',
		json: {
			parse: 0,
			jx: 0
		}
	}],
	lazy: '',
	图片来源: '@Referer=www.jianpianapp.com@User-Agent=jianpian-version353',
	// 推荐:'json:.video;*;*;*;*',
	推荐: `js:
        var d = [];
        let html = request(input);
        html = JSON.parse(html).data[0].video;
        html.forEach(it => {
            d.push({
                title: it.title,
                img: it.path,
                desc: it.playlist.title + ' ⭐' + it.score,
                url: it.id
            })
        });
        setResult(d);
    `,
	// 一级:'json:data;title;path;playlist.title;id',
	一级: `js:
		cateObj.tid = cateObj.tid+'';
        if (cateObj.tid.endsWith('_clicklink')) {
            cateObj.tid = cateObj.tid.split('_')[0];
            input = HOST + '/api/video/search?key=' + cateObj.tid + '&page=' + + MY_PAGE;
        }
        var d = [];
        let html = request(input);
        html = JSON.parse(html).data;
        html.forEach(it => {
            d.push({
                title: it.title,
                img: it.thumbnail||it.path,
                desc: (it.mask || it.playlist.title) + ' ⭐' + it.score,
                url: it.id
            })
        });
        setResult(d);
    `,
	二级: `js:
        function getLink(data) {
            let link = data.map(it => {
                return '[a=cr:' + JSON.stringify({'id':it.name+'_clicklink','name':it.name}) + '/]' + it.name + '[/a]'
            }).join(', ');
            return link
        }
		try {
            let html = request(input);
            html = JSON.parse(html);
            let node = html.data;
            VOD = {
                vod_id: node.id,
                vod_name: node.title,
                vod_pic: node.thumbnail,
                type_name: node.types[0].name,
                vod_year: node.year.title,
                vod_area: node.area.title,
                vod_remarks: node.score,
                vod_actor: getLink(node.actors),
                vod_director: getLink(node.directors),
                vod_content: node.description.strip()
            };
            if (typeof play_url === 'undefined') {
                var play_url = ''
            }
            let playMap = {};
			if (node.have_ftp_ur == 1) {
				playMap["边下边播超清版"] = node.new_ftp_list.map(it => {
					return it.title + "$" + (/m3u8/.test(it.url) ? play_url + it.url : "tvbox-xg:" + it.url)
				}).join('#');
			}
			if (node.have_m3u8_ur == 1) {
				playMap["在线点播普清版"] = node.new_m3u8_list.map(it => {
					return it.title + "$" + (/m3u8/.test(it.url) ? play_url + it.url : "tvbox-xg:" + it.url)
				}).join('#');
			}
            let playFrom = [];
            let playList = [];
            Object.keys(playMap).forEach(key => {
                playFrom.append(key);
                playList.append(playMap[key])
            });
            VOD.vod_play_from = playFrom.join('$$$');
            VOD.vod_play_url = playList.join('$$$');
        } catch (e) {
            log("获取二级详情页发生错误:" + e.message);
        }
	`,
	// 搜索:'json:data;*;thumbnail;mask;*',
	搜索: `js:
        var d = [];
        let html = request(input);
        html = JSON.parse(html).data;
        html.forEach(it => {
            d.push({
                title: it.title,
                img: it.thumbnail,
                desc: it.mask + ' ⭐' + it.score,
                url: it.id
            })
        });
        setResult(d);
    `,
}