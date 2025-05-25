var rule = {
    title:'闪雷影视',
    编码:'gb2312',
    host:'http://114.100.48.52:18008',
    url:'/www/List.asp?classid=fyclass&searchword=&page=fypage',
    filterable:0,//是否启用分类筛选,
    class_name:'电影&电视剧&综艺&动漫&音乐',
    class_url:'5000&10&8&6&12',
    searchUrl:'/www/List.asp?classid=30&searchword=**&page=fypage',
    searchable:2,
    quickSearch:1,
    headers:{
        'User-Agent':'MOBILE_UA',
    },
    play_parse:true,
    lazy:$js.toString(() => {
        var html = 'http://114.100.48.52:18008/PlayMov.asp?ClassId=' + input.split(",")[2] + '&video=2&exe=0&down=0&movNo=' + input.split(",")[3] + '&vgver=undefined&ClientIP=114.100.48.52'
        var url = request(html).match(/push\('(.*?)'/)[1]
        input = {
            jx:0,
            url:url,
            parse:0
        };
    }),
    limit:6,
    推荐:'ul:eq(4)&&strong;img&&alt;img&&src;span:eq(1)&&Text;a&&href',
    一级:'ul:eq(5)&&strong;img&&alt;img&&src;span:eq(1)&&Text;a&&href',
    二级:{
        title:"ul:eq(2)&&li:eq(0)&&Text",
        img:"img:eq(1)&&src",
        desc:"ul:eq(2)&&li:eq(1)&&Text;ul:eq(2)&&li:eq(2)&&Text;ul:eq(2)&&li:eq(3)&&Text",
        content:"body&&div:has(p)&&p:eq(3)&&Text",
        tabs:"",
        lists:'body&&a[onclick^="senfe"]',
        list_url:'a&&onclick',
        list_text:'a&&Text'
    },
    搜索:'*',
}