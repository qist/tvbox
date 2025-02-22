globalThis.getHeaders= function(input){
	let headers = {
        'User-Agent': 'okhttp/4.1.0'
	};
	return headers
}
var rule = {
	title:'点播',
	host:'http://tv.jsp47.com',
	homeUrl:'',
    //searchUrl:'https://www.suying.lol/index.php/vod/search.html?wd=**',
    searchUrl:'https://search.video.iqiyi.com/o?if=html5&key=**&pageNum=fypage&pos=1&pageSize=25&site=iqiyi',
    searchable:2,
	quickSearch:1,
	multi:1,
    filterable:1,
    headers:{
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.289 Safari/537.36'
    },
    timeout:5000,
    limit:20,	
	play_parse:true, 
	lazy:"", 
    推荐:"",
    一级:"",
    二级:`js: 
		let d = [];
		try {		
			let html = request(input, {
						headers: getHeaders(url)
					});
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

			
			VOD.type_name = "";
			
			VOD.vod_actor = "";
			VOD.vod_content = "特别提醒:ㅤ友情提示您请勿相信影片中的广告，以免上当受骗";
			let playData = json;
			let playMap = {};		
			playData.forEach(function(it, index) {
				VOD.vod_name =it.name;
                VOD.vod_pic = "http://114.100.48.52:18008/movjpg/" + it.name + ".jpg";
				let names = it.name +"  ("+ (index+1) +")";
				let playEsp = it.source.eps;
				playEsp.forEach(function(it) {
                    let source = names; 
                    if (!playMap.hasOwnProperty(source)) {
                        playMap[source] = []
                    }					
					playMap[source].append(it['name'].strip() + '$' + it['url']);
					
				})
			})
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
		let d = [];
		let html = request(input);
		let json = JSON.parse(html);
		json.data.docinfos.forEach(function(data) {
            let channelName = data.albumDocInfo.channel.split(',')[0];
            if ((data.is_exactly_same === true)&&(channelName.includes('电影') || channelName.includes('电视剧') || channelName.includes('综艺') || channelName.includes('动漫') || channelName.includes('少儿'))) {
                d.push({
                    url: "https://www.swsixtwo.top/jsp.php?jx=" + data.albumDocInfo.albumTitle,
                    title: data.albumDocInfo.albumTitle,
                    img: data.albumDocInfo.albumVImage,
                    content:data.albumDocInfo.channel,
                    desc: data.albumDocInfo.tvFocus
                })
            }
		});
		setResult(d);
	`    
}
