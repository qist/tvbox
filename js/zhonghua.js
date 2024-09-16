// 搜索验证
var rule = {
    title:'中华听书网',
    host:'https://www.tingshucn.com',
    url:'/list/fyclass-fypage.html',
    searchUrl:'/search.php?page=fypage#searchword=**&searchtype=;post',
    searchable:2,
    quickSearch:0,
    headers:{
        'User-Agent':'PC_UA'
    },
    timeout:5000,
    class_parse: '#news_nav&&li:has(a);a&&Text;a&&href;.*/(\\d+).html',
    play_parse:true,
    lazy:'js:input=input.replace("www","m")',
    limit:6,
    图片来源:'@Referer=https://www.tingshucn.com',
    推荐:'.layout_right:eq(1)&&li;*;*;em&&Text;*',
    一级:'.listBox&&li;img&&alt;img&&src;p:eq(0)&&span&&Text;a&&href',
    二级:{
        title:'h3&&Text;.webzi_top&&li:eq(4)&&Text',
        img:'.pic&&img&&src',
        desc:'.webzi_top&&li:eq(1)&&span&&Text;;;.webzi_top&&li:eq(3)&&Text;.webzi_top&&li:eq(2)&&Text',
        content:'#idDIV--a&&Text',
        tabs:'.content_jrtop:eq(0)&&li',
        lists:'.videourl:eq(#id)&&li'
    },
    搜索:'*',
}