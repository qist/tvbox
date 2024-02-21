var rule = {
	title: '追剧迷',
	模板: 'vfed',
	host: 'https://www.zhuijumi.cc',
	// url:'/videotype/fyclass-fypage.html',
	url: '/mp4type/fyclass-fypage.html',
	searchUrl: '/vodsearch/**-fypage.html',
	class_parse: '.fed-part-tips li;a&&Text;a&&href;.*/(.*?).html',
	cate_exclude: '更多|申请',
	lazy: `js:
        var html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
        var url = html.url;
        if (html.encrypt == '1') {
            url = unescape(url)
        } else if (html.encrypt == '2') {
            url = unescape(base64Decode(url))
        }
        if (/\\.m3u8|\\.mp4/.test(url)) {
            input = {
                jx: 0,
                url: url,
                parse: 0
            }
        } else {
            input
        }
    `,
	二级: {
		"title": "h1&&Text;.fed-col-xs6--span:eq(0)&&Text",
		"img": ".fed-list-info&&a&&data-original",
		"desc": ".fed-col-xs12.fed-part-eone:eq(3)&&Text;;;.fed-col-xs12.fed-part-eone--span:eq(0)&&Text;.fed-col-xs12.fed-part-eone--span:eq(1)&&Text",
		"content": ".fed-conv-text:eq(0)&&Text",
		"tabs": "ul.fed-padding&&li",
		"lists": ".fed-tabs-btm:eq(#id) li"
	},
	搜索: '.fed-list-deta;h1&&Text;.fed-lazy&&data-original;.fed-list-remarks&&Text;a&&href;.fed-col-xs12.fed-part-eone:eq(2)&&Text',
}