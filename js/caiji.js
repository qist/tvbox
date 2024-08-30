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
    searchUrl:'https://www.tycng.com/cj.php?q=**&pageNum=fypage',
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
            let json = JSON.parse(html);
            VOD = {
                vod_name: "",
                type_name: "",
                vod_actor: "",
                vod_year: "",
                vod_content: "",
                vod_remarks: "",
                vod_pic: ""
            }; 
            let playData = json.data;
            let playMap = {};               
            playData.forEach(function(it, index) {
                VOD.vod_name =it.name;
                VOD.type_name = it.class ? it.class+"  &nbsp;&nbsp;&nbsp;&nbsp;线路："+json.portname : "未知  &nbsp;&nbsp;&nbsp;&nbsp;线路："+json.portname;
                VOD.vod_actor = it.actor;
                VOD.vod_content = it.content ? it.content : "特别提醒:ㅤ友情提示您请勿相信影片中的广告，以免上当受骗";
                VOD.vod_year = it.year;
                VOD.vod_pic = it.pic ? it.pic : "http://114.100.48.52:18008/movjpg/" + it.name + ".jpg";
                //let names = it.name +"  ("+ (index+1) +")";
                let names = it.name;
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
            Object.keys(playMap).forEach(function(key) {
                    playFrom.append(key);
                    playList.append(playMap[key].join('#'))
                });               
            let vod_play_from = playFrom.join('$$$');
            let vod_play_url = playList.join('$$$');
            VOD['vod_play_from'] = vod_play_from;
            VOD['vod_play_url'] = vod_play_url
        } catch (e) {
            log('获取二级详情页发生错误:' + e.message)
        }`,
    搜索:`js:
		let d = [];
		let html = request(input);
		let json = JSON.parse(html);
		json.data.forEach(function(data) {
            data.list.forEach(function(it) {
                d.push({
                    url: "https://www.tycng.com/cj.php?id=" + it.id + "&port=" + data.port,
                    title: it.name + "【" + data.portname + "】",
                    img: it.pic,
                    content:it.content,
                    desc: it.remarks + "," + it.type_name
                })
            });            
		});
		setResult(d);
	` 
}
