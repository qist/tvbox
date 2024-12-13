/**
 * 搜索 > 图片加法验证
 * 网址导航 https://auete.site
 */

var rule = {
	title: 'Auete',
	// host:'https://haozhansou.com',
	host: 'https://auete.site',
	hostJs: 'print(HOST);let html=request(HOST,{headers:{"User-Agent":PC_UA}});let src = jsp.pdfh(html,"ul&&li&&a&&href");print(src);HOST=src',//网页域名根动态抓取js代码。通过HOST=赋值
	// url:'/fyclassfyfilter/indexfypage.html[/fyclassfyfilter/index.html]',
	url: '/fyclassfyfilter/indexfypage.html[/fyclassfyfilter/index.html]',
	filterable: 1,
	filter_url: '{{fl.class}}',
	filter: {
		"Movie":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"喜剧片","v":"/xjp"},{"n":"动作片","v":"/dzp"},{"n":"爱情片","v":"/aqp"},{"n":"科幻片","v":"/khp"},{"n":"恐怖片","v":"/kbp"},{"n":"惊悚片","v":"/jsp"},{"n":"战争片","v":"/zzp"},{"n":"剧情片","v":"/jqp"}]}],
		"Tv":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"美剧","v":"/oumei"},{"n":"韩剧","v":"/hanju"},{"n":"日剧","v":"/riju"},{"n":"泰剧","v":"/yataiju"},{"n":"网剧","v":"/wangju"},{"n":"台剧","v":"/taiju"},{"n":"国产","v":"/neidi"},{"n":"港剧","v":"/tvbgj"},{"n":"英剧","v":"/yingju"}]}],
		"Zy":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"国综","v":"/guozong"},{"n":"韩综","v":"/hanzong"},{"n":"美综","v":"/meizong"}]}],
		"Dm":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"动画","v":"/donghua"},{"n":"日漫","v":"/riman"},{"n":"国漫","v":"/guoman"},{"n":"美漫","v":"/meiman"}]}],
		"qita":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"记录片","v":"/Jlp"},{"n":"经典片","v":"/Jdp"},{"n":"经典剧","v":"/Jdj"},{"n":"网大电影","v":"/wlp"},{"n":"国产老电影","v":"/laodianying"}]}]
	},
	searchUrl: '/auete2so.php?page=fypage&searchword=**',
	searchable: 2,
	quickSearch: 1,
	headers: {
		'User-Agent': 'PC_UA',
        'Cookie': 'ssea2_search=ok'
	},
	class_parse: '.mr-auto li:gt(0):lt(6);a&&Text;a&&href;/(\\w+)/index.html',
	play_parse: true,
	lazy:'js:eval(unescape(base64Decode("anM6CgkJcGRmaCA9IGpzcC5wZGZoOyBwZGZhID0ganNwLnBkZmE7IHBkID0ganNwLnBkOwoJCWxldCBkb2N1bWVudCA9IHt9OwoJCWxldCBuYXZpZ2F0b3IgPSB7CgkJCXVzZXJBZ2VudDogTU9CSUxFX1VBLAoJCX07CgkJbGV0IGJhc2U2NGRlY29kZSA9IGJhc2U2NERlY29kZTsKCQlsZXQgcG4gPSAnJywgbm93ID0gJycsIG5leHRQYWdlID0gJycsIHByZVBhZ2UgPSAnJywgbmV4dCA9ICcnLCB2aWQgPSAnJywgdmZyb20gPSAnJywgdnBhcnQgPSAnJywgc3JjVXJsID0gJyc7CgkJZXZhbChyZXF1ZXN0KEhPU1QgKyAiL2pzL3BsYXkuanMiKSk7CgkJbGV0IGh0bWwgPSByZXF1ZXN0KGlucHV0KTsKCQlldmFsKHBkZmgoaHRtbCwgIi5tYi0yJiZzY3JpcHQmJkh0bWwiKS5yZXBsYWNlQWxsKCd2YXIgJywnJykpOwoJCWV2YWwocGRmaChodG1sLCAiLm1iLTImJnNjcmlwdCwxJiZIdG1sIikucmVwbGFjZUFsbCgndmFyICcsJycpLnNwbGl0KCJkb2N1bWVudCIpWzBdKTsKCQlsZXQgcGFyc2VIdG1sID0gcmVxdWVzdChIT1NUICsgIi9qcy9wbGF5ZXIvIiArIHBuICsgIi5odG1sIik7CgkJbGV0IHBhcmVudCA9IHsKCQkJbm93OiBub3csCgkJCW5leHRQYWdlOiBuZXh0UGFnZSwKCQkJbmV4dDogbmV4dCwKCQkJdmlkOiB2aWQsCgkJCXZmcm9tOiB2ZnJvbSwKCQkJdnBhcnQ6IHZwYXJ0LAoJCX07CgkJbGV0IHBhcmpzID0gcGRmaChwYXJzZUh0bWwsICJib2R5JiZzY3JpcHQmJkh0bWwiKTsKCQlldmFsKCJzcmNVcmwgPSAnIiArIHBkZmgocGFyanMsICJpZnJhbWUmJnNyYyIpICsgIiciKTsKCQlpZiAoc3JjVXJsLmluZGV4T2YoIj91cmw9IikgPiAtMSB8fCBzcmNVcmwuaW5kZXhPZigiP3VpZD0iKSA+IC0xKSB7CgkJCWlucHV0ID0ge2p4OjAsIHVybDpzcmNVcmwuc3BsaXQoIj0iKVsxXSwgcGFyc2U6MH0KCQl9IGVsc2UgewoJCQlsZXQgcHVybCA9IHNyY1VybC5zcGxpdCgiPSIpWzFdLnNwbGl0KCIsIilbMV07CgkJCWlucHV0ID0ge2p4OjAsIHVybDpwdXJsLCBwYXJzZTowfQoJCX0=")))',
	limit: 6,
	推荐: '*',
	一级: '.threadlist .trans_3;.title&&Text;.lazy&&src;.hdtag&&Text;a&&href',
	二级: {
		"title":".cover a&&title;.message&&p:eq(2)&&Text",
		"img": ".cover img&&src",
		"desc":".w-100&&Text;;.message&&p:eq(4)&&Text;.message&&p:eq(5)&&Text;.message&&p:eq(6)&&Text",
		"content": ".message p:eq(-1)&&Text",
		"tabs": `js:
			TABS = [];
			let tabs = pdfa(html, 'h2');
			tabs.forEach((it) => {
				TABS.push(pdfh(it, "body&&Text").split('』')[1].split('：')[0])
			});
		`,
		"lists": "#player_list:eq(#id) li"
	},
	搜索: '.card-body .media;.text-danger&&Text;;.data&&Text;a&&href',
}