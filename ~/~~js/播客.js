// 无搜索
var rule = {
	title:'播客',
	host:'https://getpodcast.xyz',
	url: '/fyclass',
	searchUrl: '',
	searchable:0,
	quickSearch:0,
	headers:{
		'User-Agent': 'PC_UA'
	},
	timeout:5000,
	class_name:'播客&人文&NEWS热点&影视与读书&教育&历史&音乐&情感&有声书',
	class_url:'0&1&2&3&4&5&6&7&8',
	cate_exclude:'',
	play_parse:true,
	lazy:`js:
		input = {jx:0, url:input, parse:0}
	`,
	limit:6,
	推荐: `js:
		pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
		var d = [];
		var html = request(HOST);
		var list = pdfa(html, 'body&&.pic_list:eq(0)&&li');
		list.forEach(it => {
			d.push({
				title: pdfh(it, '.title&&Text'),
				pic_url: pdfh(it, 'img&&src'),
				url: pd(it, 'a&&href') + '|' + pdfh(it, '.title&&Text') + '|' + pdfh(it, 'img&&src')
			});
		})
		setResult(d);
	`,
	一级: `js:
		pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
		var d = [];
		var html = request(HOST);
		var list = pdfa(html, 'body&&.pic_list:eq(list_idx)&&li'.replace("list_idx", MY_CATE));
		list.forEach(it => {
			d.push({
				title: pdfh(it, '.title&&Text'),
				pic_url: pdfh(it, 'img&&src'),
				url: pd(it, 'a&&href') + '|' + pdfh(it, '.title&&Text') + '|' + pdfh(it, 'img&&src')
			});
		})
		setResult(d);
	`,
	二级: `js:
        pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
		let purl = input.split('|')[0];
		let title = input.split('|')[1];
		let pic = input.split('|')[2];
		var html = request(purl);
		let d = [];
		VOD = {};
		VOD.vod_name = title;
		VOD.vod_pic = pic;
		if (typeof play_url === 'undefined') {
            var play_url = ''
        }
        let episodes = pdfa(html, 'body&&item');
		log('episodes =========>'+episodes);
		let vod_play_url = episodes.map(function(it) {
			let ititle = it.match(/<title>(.*?)<\\/title>/)[1].replace(/&lt;!\\[CDATA\\[|\\]\\]&gt;||<!\\[CDATA\\[|\\]\\]>/g, '');
			let iurl = pdfh(it, 'enclosure&&url');
			return ititle + '$' + iurl
        }).join('#')
        VOD.vod_play_from = '道长在线';
        VOD.vod_play_url = vod_play_url
	`,
	搜索:'',
}