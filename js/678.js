var rule = {
	title:'点播',
	host:'http://tv.jsp47.com',
	homeUrl:'',
    searchUrl:'https://www.ugigc.us.kg/shanlei.php?searchword=**',
    searchable:2,
	quickSearch:1,
	multi:1,
	filterable:1,
	headers:{
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.289 Safari/537.36'
    },
    timeout:5000,
	class_name:'电影&电视剧&综艺&动漫',
    class_url:'5000&10&8&6',
    limit:20,	
	play_parse:true, 
	lazy:"", 
    一级:`js:
		let d = [];
		let html = request(input);
		let json = JSON.parse(html);		
		json.data.forEach(function(data) {
			d.push({
				url: data.url,
				title: data.name,
				img: data.img,
				desc: data.desc
			})
		});
		setResult(d);
	`,
    二级:`js: 
		let d = [];
		let html = request(input);
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
		VOD.vod_name = json.name;
		VOD.vod_year = json.year;
		VOD.type_name = json.type_name;
		VOD.vod_pic = json.pic;
		VOD.vod_actor = json.actor;
		VOD.vod_content = json.content;
		let playData = json.eps;
		playData.forEach(function(it) {
			d.push({
				url: it.url,
				img: json.pic,
				title: it.name,
				desc: ""
			})
		})
		VOD.vod_play_from = "默认";
		VOD.vod_play_url = d.map(function(it) {
			return it.title + "$" + it.url
		}).join("#");
	`,
    搜索:`js:
		let d = [];
		let html = request(input);
		let json = JSON.parse(html);
		json.data.forEach(function(data) {
			d.push({
				url: data.url,
				title: data.name,
				img: data.img,
				desc: data.desc
			})
		});
		setResult(d);
	`
}
