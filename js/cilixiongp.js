var rule = {
	title:'磁力熊[磁]',
	//host:'https://www.cilixiong.com',
	//homeUrl:'/',
	//url: '/fyclassfyfilter-(fypage-1).html',
	host:'http://127.0.0.1:10079',
	homeUrl:'/p/0/socks5%253A%252F%252F192.168.101.1%253A1080/https://www.cilixiong.com',
	url:'/p/0/socks5%253A%252F%252F192.168.101.1%253A1080/https://www.cilixiong.com/fyclassfyfilter-(fypage-1).html',
	filter_url:'-{{fl.class or "0"}}-{{fl.area or "0"}}',
	filter:{
		"1":[{"key":"class","name":"类型","value":[{"n":"全部","v":"0"},{"n":"剧情","v":"1"},{"n":"喜剧","v":"2"},{"n":"惊悚","v":"3"},{"n":"动作","v":"4"},{"n":"爱情","v":"5"},{"n":"犯罪","v":"6"},{"n":"恐怖","v":"7"},{"n":"冒险","v":"8"},{"n":"悬疑","v":"9"},{"n":"科幻","v":"10"},{"n":"家庭","v":"11"},{"n":"奇幻","v":"12"},{"n":"动画","v":"13"},{"n":"战争","v":"14"},{"n":"历史","v":"15"},{"n":"传记","v":"16"},{"n":"音乐","v":"17"},{"n":"歌舞","v":"18"},{"n":"运动","v":"19"},{"n":"西部","v":"20"},{"n":"灾难","v":"21"},{"n":"古装","v":"22"},{"n":"情色","v":"23"},{"n":"同性","v":"24"},{"n":"儿童","v":"25"},{"n":"纪录片","v":"26"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":"0"},{"n":"大陆","v":"1"},{"n":"香港","v":"2"},{"n":"台湾","v":"3"},{"n":"美国","v":"4"},{"n":"日本","v":"5"},{"n":"韩国","v":"6"},{"n":"英国","v":"7"},{"n":"法国","v":"8"},{"n":"德国","v":"9"},{"n":"印度","v":"10"},{"n":"泰国","v":"11"},{"n":"丹麦","v":"12"},{"n":"瑞典","v":"13"},{"n":"巴西","v":"14"},{"n":"加拿大","v":"15"},{"n":"俄罗斯","v":"16"},{"n":"意大利","v":"17"},{"n":"比利时","v":"18"},{"n":"爱尔兰","v":"19"},{"n":"西班牙","v":"20"},{"n":"澳大利亚","v":"21"},{"n":"波兰","v":"22"},{"n":"土耳其","v":"23"},{"n":"越南","v":"24"}]}],
		"2":[{"key":"class","name":"类型","value":[{"n":"全部","v":"0"},{"n":"剧情","v":"1"},{"n":"喜剧","v":"2"},{"n":"惊悚","v":"3"},{"n":"动作","v":"4"},{"n":"爱情","v":"5"},{"n":"犯罪","v":"6"},{"n":"恐怖","v":"7"},{"n":"冒险","v":"8"},{"n":"悬疑","v":"9"},{"n":"科幻","v":"10"},{"n":"家庭","v":"11"},{"n":"奇幻","v":"12"},{"n":"动画","v":"13"},{"n":"战争","v":"14"},{"n":"历史","v":"15"},{"n":"传记","v":"16"},{"n":"音乐","v":"17"},{"n":"歌舞","v":"18"},{"n":"运动","v":"19"},{"n":"西部","v":"20"},{"n":"灾难","v":"21"},{"n":"古装","v":"22"},{"n":"情色","v":"23"},{"n":"同性","v":"24"},{"n":"儿童","v":"25"},{"n":"纪录片","v":"26"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":"0"},{"n":"大陆","v":"1"},{"n":"香港","v":"2"},{"n":"台湾","v":"3"},{"n":"美国","v":"4"},{"n":"日本","v":"5"},{"n":"韩国","v":"6"},{"n":"英国","v":"7"},{"n":"法国","v":"8"},{"n":"德国","v":"9"},{"n":"印度","v":"10"},{"n":"泰国","v":"11"},{"n":"丹麦","v":"12"},{"n":"瑞典","v":"13"},{"n":"巴西","v":"14"},{"n":"加拿大","v":"15"},{"n":"俄罗斯","v":"16"},{"n":"意大利","v":"17"},{"n":"比利时","v":"18"},{"n":"爱尔兰","v":"19"},{"n":"西班牙","v":"20"},{"n":"澳大利亚","v":"21"},{"n":"波兰","v":"22"},{"n":"土耳其","v":"23"},{"n":"越南","v":"24"}]}]
	},
	searchUrl: '/p/0/socks5%253A%252F%252F192.168.101.1%253A1080/https://www.cilixiong.com/e/search/index.php#classid=1,2&show=title&tempid=1&keyboard=**;post',
	searchable:0,
	quickSearch:0,
	filterable:1,
	headers:{
		'User-Agent': 'MOBILE_UA'
	},
	timeout:5000,
	class_name:'电影&剧集&豆瓣电影Top250&IMDB Top250&高分悬疑片&高分喜剧片&高分传记片&高分爱情片&高分犯罪片&高分恐怖片&高分冒险片&高分武侠片&高分奇幻片&高分历史片&高分战争片&高分歌舞片&高分灾难片&高分情色片&高分西部片&高分音乐片&高分科幻片&高分动作片&高分动画片&高分纪录片&冷门佳片',
	class_url:'1&2&/top250/&/s/imdbtop250/&/s/suspense/&/s/comedy/&/s/biopic/&/s/romance/&/s/crime/&/s/horror/&/s/adventure/&/s/martial/&/s/fantasy/&/s/history/&/s/war/&/s/musical/&/s/disaster/&/s/erotic/&/s/west/&/s/music/&/s/sci-fi/&/s/action/&/s/animation/&/s/documentary/&/s/unpopular/',
	play_parse:false,
	lazy:'',
	limit:6,
	推荐: `js:
		pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
		var d = [];
		var html = request(input);
		var list = pdfa(html, 'body&&.col');
		list.forEach(it => {
			d.push({
				title: pdfh(it, 'h2&&Text'),
				desc: pdfh(it, '.me-auto&&Text') + '分 / ' + pdfh(it, '.small&&Text'),
				pic_url: pd(it, '.card-img&&style')
			});
		})
		setResult(d);
	`,
	一级: `js:
		pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
		var d = [];
		if (MY_CATE !== '1' && MY_CATE !== '2') {
			let turl = (MY_PAGE === 1)? 'index' : 'index_'+ MY_PAGE;
			input = rule.homeUrl + MY_CATE + turl + '.html';
		}
		var html = request(input);
		var list = pdfa(html, 'body&&.col');
		list.forEach(it => {
			d.push({
				title: pdfh(it, 'h2&&Text'),
				desc: pdfh(it, '.me-auto&&Text') + '分 / ' + pdfh(it, '.small&&Text'),
				pic_url: pdfh(it, '.card-img&&style')
			});
		})
		setResult(d);
	`,
	二级:'',
	搜索:'',
}
