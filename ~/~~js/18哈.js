muban.短视2.二级.img = '.lazy&&data-src';
muban.短视2.二级.tab_text = 'body--i--span&&Text';
var rule={
    title:'18哈',
    模板:'短视2',
    host:'https://sk100.tv',
    detailUrl:'/voddetail/fyid.html',
	class_name:'电影&电视剧&综艺&动漫&爽文短剧',
    class_url:'1&2&4&3&33',
    lazy:`js:
        var html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
        var url = html.url;
        if (html.encrypt == '1') {
            url = unescape(url)
        } else if (html.encrypt == '2') {
            url = unescape(base64Decode(url))
        }
        if (/m3u8|mp4/.test(url)) {
            input = url
        } else {
            input
        }
    `,
    推荐:'.public-list-box;a&&title;.lazy&&data-src;.public-list-prb&&Text;a&&href',
}