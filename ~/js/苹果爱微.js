/* 已知问题:
1.图片是base64文本编码壳子无法显示
2.播放地址 https://ss.rongliren.com/api/video/m3u8?id=22180&admin=1 像这样，壳子无法播放
 */
var rule = {
    title:'苹果爱微',
    host:'https://files.yuchenglw.com',
    homeUrl:'/Index/lists?cat=1',
    url:'/Index/lists?cat=fyclass',
    headers:{
        'User-Agent':'IOS_UA'
    },
    searchable:0,
    quickSearch:0,
    timeout:5000,
    // play_json:[{re:'*', json:{jx:0, parse:1,header:JSON.stringify({"user-agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"})}}],
    // play_json:0,
    class_parse:'.childs a;a&&Text;a&&href;cat=(.*)',
    limit:5,
    play_parse:true,
    lazy:'',
    推荐:'*',
    一级:'.row.lists .item;.time&&Text;img&&data-src;.time&&Text;a&&href',
    // 二级:'*',
    二级:'*',
    图片来源:'@Referer=https://files.yuchenglw.com@Type=base64',
    lazy:'js:pd=jsp.pd;let html=request(input);let a=pd(html,"source&&src")+"#.m3u8";input=a'
}