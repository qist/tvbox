var rule = {
    title:'闪雷影视',
    编码:'gb2312',
    host:'http://114.100.48.52:18008/jdl',
    url:'/index.asp?action=classlist&classid=fyclass&page=fypage',
    filterable:0,//是否启用分类筛选,
    class_name:'电影&电视剧&综艺&动漫&音乐&动作片&喜剧片&恐怖片&科幻片&战争片&爱情片',
    class_url:'1&10&8&6&12&1&2&3&4&5&7',
    searchUrl:'/List.asp?classid=30&searchword=**&page=fypage',
    searchable:2,
    quickSearch:1,
    headers:{
        'User-Agent':'MOBILE_UA',
    },
    play_parse:true,
    lazy:$js.toString(() => {
        var html = request(input);
        var url = html.match(/var DownURL = "(.*?)"/);
        if(url){
            url = url[1];
            url = url.replace(/https?:\/\/(?:[\d.]+|[\w\-]+)(?::\d+)?\//, rule.host + '/');
            input = {
                jx:0,
                url:url,
                parse:0
            };
        } else {
            // 如果找不到DownURL，尝试从onclick事件中提取
            var movNo = input.split(',')[3];
            var classId = input.split(',')[2];
            var playUrl = rule.host + '/PlayMov.asp?ClassId=' + classId + '&video=2&exe=0&down=0&movNo=' + movNo + '&vgver=undefined';
            var playHtml = request(playUrl);
            var extractedUrl = playHtml.match(/push\('(.*?)'/);
            if(extractedUrl && extractedUrl.length>1){
                input = extractedUrl[1];
            }
        }
    }),
    limit:6,
    推荐:'div.box&&div.all.border&&ul.pic&&li;a&&title;img&&src;;a&&href',
    一级:'div.box&&div.allx.border&&ul.pic&&li;a&&title;img&&src;;a&&href',
    二级:{
        title:"div.intro&&ul&&li.h4&&Text",
        img:"div.intro&&div.img&&img&&src",
        desc:"div.intro&&ul&&li:eq(2)&&Text;div.intro&&ul&&li:eq(4)&&Text;div.intro&&ul&&li:eq(3)&&Text;div.intro&&ul&&li:eq(5)&&Text;div.intro&&ul&&li:eq(6)&&Text",
        content:"div.textnr&&Text",
        tabs:"div.title&&h3&&Text",
        lists:'#content&&a[onclick^=\"senfe\"]',
        list_url:'a&&onclick',
        list_text:'a&&Text'
    },
    搜索:'div.list&&dl;dt&&a&&title;dt&&img&&src;dd:eq(1)&&Text;dd&&a&&href',
}