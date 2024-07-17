globalThis.getHeaders= function(input){
    let t = Math.round(new Date().getTime()/1000).toString();
	let headers = {
        'User-Agent': 'Yunfan Android 1.0.0.88'
	};
	return headers
}
var rule = {
    title:'百忙无果',
    host:'https://pianku.api.%6d%67%74%76.com',
    homeUrl:'',
    searchUrl:'https://mobileso.bz.%6d%67%74%76.com/pc/search/v1?q=**&pn=fypage&pc=10',
    detailUrl:'https://v5m.api.mgtv.com/remaster/vrs/getByPartId?abroad=0&src=mgtv&partId=fyid',
    searchable:2,
    quickSearch:0,
    filterable:1,
    multi:1,
    // 分类链接fypage参数支持1个()表达式
    // https://www.mgtv.com/lib/3?lastp=list_index&kind=a1&year=all&chargeInfo=a1&sort=c2
    url:'/rider/list/pcweb/v3?platform=pcweb&channelId=fyclass&pn=fypage&pc=80&hudong=1&_support=10000000&kind=a1&area=a1',
    filter_url:'year={{fl.year or "all"}}&sort={{fl.sort or "all"}}&chargeInfo={{fl.chargeInfo or "all"}}',
    headers:{
        'User-Agent':'PC_UA'
    },
    timeout:5000,
    class_name:'电影&电视剧&综艺&动漫&纪录片&教育&少儿',
    class_url:'3&2&1&50&51&115&10',
    filter:{'2': [{'key': 'chargeInfo', 'name': '付费类型', 'value': [{'n': '全部', 'v': 'all'}, {'n': '免费', 'v': 'b1'}, {'n': 'vip', 'v': 'b2'}, {'n': 'VIP用券', 'v': 'b3'}, {'n': '付费点播', 'v': 'b4'}]}, {'key': 'sort', 'name': '排序', 'value': [{'n': '最新', 'v': 'c1'}, {'n': '最热', 'v': 'c2'}, {'n': '知乎高分', 'v': 'c4'}]}, {'key': 'year', 'name': '年代', 'value': [{'n': '全部', 'v': 'all'}, {'n': '2023', 'v': '2023'}, {'n': '2022', 'v': '2022'}, {'n': '2021', 'v': '2021'}, {'n': '2020', 'v': '2020'}, {'n': '2019', 'v': '2019'}, {'n': '2018', 'v': '2018'}, {'n': '2017', 'v': '2017'}, {'n': '2016', 'v': '2016'}, {'n': '2015', 'v': '2015'}, {'n': '2014', 'v': '2014'}, {'n': '2013', 'v': '2013'}, {'n': '2012', 'v': '2012'}, {'n': '2011', 'v': '2011'}, {'n': '2010', 'v': '2010'}, {'n': '2009', 'v': '2009'}, {'n': '2008', 'v': '2008'}, {'n': '2007', 'v': '2007'}, {'n': '2006', 'v': '2006'}, {'n': '2005', 'v': '2005'}, {'n': '2004', 'v': '2004'}]}], '3': [{'key': 'chargeInfo', 'name': '付费类型', 'value': [{'n': '全部', 'v': 'all'}, {'n': '免费', 'v': 'b1'}, {'n': 'vip', 'v': 'b2'}, {'n': 'VIP用券', 'v': 'b3'}, {'n': '付费点播', 'v': 'b4'}]}, {'key': 'sort', 'name': '排序', 'value': [{'n': '最新', 'v': 'c1'}, {'n': '最热', 'v': 'c2'}, {'n': '知乎高分', 'v': 'c4'}]}, {'key': 'year', 'name': '年代', 'value': [{'n': '全部', 'v': 'all'}, {'n': '2023', 'v': '2023'}, {'n': '2022', 'v': '2022'}, {'n': '2021', 'v': '2021'}, {'n': '2020', 'v': '2020'}, {'n': '2019', 'v': '2019'}, {'n': '2018', 'v': '2018'}, {'n': '2017', 'v': '2017'}, {'n': '2016', 'v': '2016'}, {'n': '2015', 'v': '2015'}, {'n': '2014', 'v': '2014'}, {'n': '2013', 'v': '2013'}, {'n': '2012', 'v': '2012'}, {'n': '2011', 'v': '2011'}, {'n': '2010', 'v': '2010'}, {'n': '2009', 'v': '2009'}, {'n': '2008', 'v': '2008'}, {'n': '2007', 'v': '2007'}, {'n': '2006', 'v': '2006'}, {'n': '2005', 'v': '2005'}, {'n': '2004', 'v': '2004'}]}], '1': [{'key': 'chargeInfo', 'name': '付费类型', 'value': [{'n': '全部', 'v': 'all'}, {'n': '免费', 'v': 'b1'}, {'n': 'vip', 'v': 'b2'}, {'n': 'VIP用券', 'v': 'b3'}, {'n': '付费点播', 'v': 'b4'}]}, {'key': 'sort', 'name': '排序', 'value': [{'n': '最新', 'v': 'c1'}, {'n': '最热', 'v': 'c2'}, {'n': '知乎高分', 'v': 'c4'}]}, {'key': 'year', 'name': '年代', 'value': [{'n': '全部', 'v': 'all'}, {'n': '2023', 'v': '2023'}, {'n': '2022', 'v': '2022'}, {'n': '2021', 'v': '2021'}, {'n': '2020', 'v': '2020'}, {'n': '2019', 'v': '2019'}, {'n': '2018', 'v': '2018'}, {'n': '2017', 'v': '2017'}, {'n': '2016', 'v': '2016'}, {'n': '2015', 'v': '2015'}, {'n': '2014', 'v': '2014'}, {'n': '2013', 'v': '2013'}, {'n': '2012', 'v': '2012'}, {'n': '2011', 'v': '2011'}, {'n': '2010', 'v': '2010'}, {'n': '2009', 'v': '2009'}, {'n': '2008', 'v': '2008'}, {'n': '2007', 'v': '2007'}, {'n': '2006', 'v': '2006'}, {'n': '2005', 'v': '2005'}, {'n': '2004', 'v': '2004'}]}], '50': [{'key': 'chargeInfo', 'name': '付费类型', 'value': [{'n': '全部', 'v': 'all'}, {'n': '免费', 'v': 'b1'}, {'n': 'vip', 'v': 'b2'}, {'n': 'VIP用券', 'v': 'b3'}, {'n': '付费点播', 'v': 'b4'}]}, {'key': 'sort', 'name': '排序', 'value': [{'n': '最新', 'v': 'c1'}, {'n': '最热', 'v': 'c2'}, {'n': '知乎高分', 'v': 'c4'}]}, {'key': 'year', 'name': '年代', 'value': [{'n': '全部', 'v': 'all'}, {'n': '2023', 'v': '2023'}, {'n': '2022', 'v': '2022'}, {'n': '2021', 'v': '2021'}, {'n': '2020', 'v': '2020'}, {'n': '2019', 'v': '2019'}, {'n': '2018', 'v': '2018'}, {'n': '2017', 'v': '2017'}, {'n': '2016', 'v': '2016'}, {'n': '2015', 'v': '2015'}, {'n': '2014', 'v': '2014'}, {'n': '2013', 'v': '2013'}, {'n': '2012', 'v': '2012'}, {'n': '2011', 'v': '2011'}, {'n': '2010', 'v': '2010'}, {'n': '2009', 'v': '2009'}, {'n': '2008', 'v': '2008'}, {'n': '2007', 'v': '2007'}, {'n': '2006', 'v': '2006'}, {'n': '2005', 'v': '2005'}, {'n': '2004', 'v': '2004'}]}], '51': [{'key': 'chargeInfo', 'name': '付费类型', 'value': [{'n': '全部', 'v': 'all'}, {'n': '免费', 'v': 'b1'}, {'n': 'vip', 'v': 'b2'}, {'n': 'VIP用券', 'v': 'b3'}, {'n': '付费点播', 'v': 'b4'}]}, {'key': 'sort', 'name': '排序', 'value': [{'n': '最新', 'v': 'c1'}, {'n': '最热', 'v': 'c2'}, {'n': '知乎高分', 'v': 'c4'}]}, {'key': 'year', 'name': '年代', 'value': [{'n': '全部', 'v': 'all'}, {'n': '2023', 'v': '2023'}, {'n': '2022', 'v': '2022'}, {'n': '2021', 'v': '2021'}, {'n': '2020', 'v': '2020'}, {'n': '2019', 'v': '2019'}, {'n': '2018', 'v': '2018'}, {'n': '2017', 'v': '2017'}, {'n': '2016', 'v': '2016'}, {'n': '2015', 'v': '2015'}, {'n': '2014', 'v': '2014'}, {'n': '2013', 'v': '2013'}, {'n': '2012', 'v': '2012'}, {'n': '2011', 'v': '2011'}, {'n': '2010', 'v': '2010'}, {'n': '2009', 'v': '2009'}, {'n': '2008', 'v': '2008'}, {'n': '2007', 'v': '2007'}, {'n': '2006', 'v': '2006'}, {'n': '2005', 'v': '2005'}, {'n': '2004', 'v': '2004'}]}], '115': [{'key': 'chargeInfo', 'name': '付费类型', 'value': [{'n': '全部', 'v': 'all'}, {'n': '免费', 'v': 'b1'}, {'n': 'vip', 'v': 'b2'}, {'n': 'VIP用券', 'v': 'b3'}, {'n': '付费点播', 'v': 'b4'}]}, {'key': 'sort', 'name': '排序', 'value': [{'n': '最新', 'v': 'c1'}, {'n': '最热', 'v': 'c2'}, {'n': '知乎高分', 'v': 'c4'}]}, {'key': 'year', 'name': '年代', 'value': [{'n': '全部', 'v': 'all'}, {'n': '2023', 'v': '2023'}, {'n': '2022', 'v': '2022'}, {'n': '2021', 'v': '2021'}, {'n': '2020', 'v': '2020'}, {'n': '2019', 'v': '2019'}, {'n': '2018', 'v': '2018'}, {'n': '2017', 'v': '2017'}, {'n': '2016', 'v': '2016'}, {'n': '2015', 'v': '2015'}, {'n': '2014', 'v': '2014'}, {'n': '2013', 'v': '2013'}, {'n': '2012', 'v': '2012'}, {'n': '2011', 'v': '2011'}, {'n': '2010', 'v': '2010'}, {'n': '2009', 'v': '2009'}, {'n': '2008', 'v': '2008'}, {'n': '2007', 'v': '2007'}, {'n': '2006', 'v': '2006'}, {'n': '2005', 'v': '2005'}, {'n': '2004', 'v': '2004'}]}]},
    limit:20,
    play_parse:true,
	lazy:`js:
        try {
            function getvideo(url) {
                let jData = JSON.parse(request(url, {
                    headers: getHeaders(url)
                }));
                return jData.data.url
            }
			let videoUrl = getvideo('http://mgtv.ckflv.cn/?url=' + input);
			input = {
                jx: 0,
                url: videoUrl,
                parse: 0
            }
        } catch (e) {
            log(e.toString())
        }
	`,    

    推荐:`js:
        let d = [];
        let html = request("https://pianku.api.mgtv.com/rider/list/pcweb/v3?allowedRC=1&platform=pcweb&channelId=3&pn=1&pc=40&hudong=1&_support=10000000&kind=a1&year=all&chargeInfo=a1&sort=c1&edition=a1&area=a1");
		let json = JSON.parse(html);
		json.data.hitDocs.forEach(function(data,index) {
            d.push({
                url: data.playPartId,
                title: data.title,
                img: data.img,
                desc: data.year
            })
		});
		setResult(d);
	`,    
    一级:'json:data.hitDocs;title;img;updateInfo||rightCorner.text;playPartId',
    // 一级:'json:data.hitDocs;title;img;updateInfo;playPartId',
    二级:`js: 
		let d = [];
		let html = request(input);
        let partId = input.split('partId=')[1].split('&')[0];
		let json = JSON.parse(html).data;
		VOD = {
			vod_name: "",
			type_name: "",
			vod_actor: "",
			vod_year: "",
			vod_content: "",
			vod_remarks: "",
			vod_pic: ""
		};
		VOD.vod_name = json.title;
        VOD.type_name = json.mediaInfo.detail.font
		VOD.vod_pic = json.colImage;
        const info = {};

        // 遍历数组，解析并存储信息
        json.intro.forEach(item => {
            const [key, value] = item.split('：');
            info[key.trim()] = value.trim();
        });        
        VOD.vod_year = info['年份'];
        VOD.vod_actor = info['演员'];
		VOD.vod_content = info['简介'];
		let playlists = [];
		if (json.locateChannel === '3') {
            let listUrl = "https://pcweb.api.mgtv.com/episode/list?page=1&size=50&video_id=" + json.collPlayPartId;
            let jsons = JSON.parse(request(listUrl)).data;            
            playlists = [{
                playUrl: "https://www.mgtv.com" + jsons.list[0].url,
                imageUrl: json.colImage,
                shortTitle: "正片",
                period: info['简介']
            }]
		} else {
            let listUrl = "https://pcweb.api.mgtv.com/episode/list?page=1&size=50&video_id=" + json.collPlayPartId;
            let data = JSON.parse(request(listUrl)).data;
            let total = data.count;
            if (total <= 50) {
                let playData = data.list;
                playData.forEach(function(it) {
                    if (it.isIntact === "1") {
                        playlists.push({
                            playUrl: "https://www.mgtv.com" + it.url,
                            imageUrl: json.colImage,
                            shortTitle: it.t4,
                            period: info['简介']
                        })
                    }
                })
            } else {
                for (let i = 1; i < total / 50 + 1; i++) {
                    let listUrl = "https://pcweb.api.mgtv.com/episode/list?page=" + i + "&size=50&video_id=" + json.collPlayPartId;
                    let data = JSON.parse(request(listUrl)).data;
                    let playData = data.list;
                    playData.forEach(function(it) {                      
                        if (it.isIntact === "1") {                   
                            playlists.push({
                                playUrl: "https://www.mgtv.com" + it.url,
                                imageUrl: json.colImage,
                                shortTitle: it.t4,
                                period: info['简介']
                            })
                        }
                    })
                }
            }
		}
		playlists.forEach(function(it) {
			d.push({
				title: it.shortTitle,
				desc: it.period,
				img: it.imageUrl,
				url: it.playUrl
			})
		});
		VOD.vod_play_from = "芒果TV";
		VOD.vod_play_url = d.map(function(it) {
			return it.title + "$" + it.url
		}).join("#");
	`,
    搜索:'',
    搜索:'js:fetch_params.headers.Referer="https://www.mgtv.com";fetch_params.headers["User-Agent"]=UA;let d=[];let html=request(input);let json=JSON.parse(html);json.data.contents.forEach(function(data){if(data.data.sourceList||data.data.yearList){let list=data.data.sourceList?data.data.sourceList:data.data.yearList[0].sourceList;let desc="";list.forEach(function(it){desc+=it.name+"\\t"});if(list[0].source==="imgo"){let img=data.data.pic?data.data.pic:data.data.yearList[0].pic;d.push({title:data.data.title?data.data.title:data.data.yearList[0].title,img:img,content:data.data.story?data.data.story:data.data.yearList[0].story,desc:data.data.playTime,url:list[0].vid})}}});setResult(d);',
}