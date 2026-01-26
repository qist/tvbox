var rule = {
    title:'闪雷影视',
    编码:'gb2312',

    host:'http://114.100.48.52:18008',

    // 列表页在 jdl 目录
    url:'/jdl/List.asp?ClassID=fyclass&page=fypage',
    searchUrl:'/jdl/List.asp?ClassID=30&searchword=**&page=fypage',

    class_name:'动作片&喜剧片&恐怖片&科幻片&战争片&动画片&爱情片&综艺片&剧情片&MTV&连续剧',
    class_url:'1&2&3&4&5&6&7&8&9&12&10',

    filterable:0,
    searchable:2,
    quickSearch:1,

    headers:{
        'User-Agent':'MOBILE_UA',
    },

    play_parse:true,

    // ⚠️ 重点：PlayMov 在根目录
    lazy:$js.toString(() => {
        let ids = input.split(",");
        let classId = ids[2];
        let movNo = ids[3];

        let playUrl = rule.host + '/PlayMov.asp'
            + '?ClassId=' + classId
            + '&video=2&exe=0&down=0'
            + '&movNo=' + movNo
            + '&vgver=undefined'
            + '&ClientIP=114.100.48.52';

        let html = request(playUrl);
        let real = html.match(/push\('(.*?)'/)[1];

        // 修正相对路径
        if(real.startsWith('/')){
            real = rule.host + real;
        }

        input = {
            jx:0,
            url:real,
            parse:0
        };
    }),

    limit:6,

    // 首页推荐
    推荐:'ul.pic&&li;img&&alt;img&&src;span:eq(1)&&Text;a&&href',

    // 分类列表
    一级:'ul.pic&&li;img&&alt;img&&src;span:eq(1)&&Text;a&&href',

    二级:{
        title:'body&&h1&&Text',
        img:'img&&src',
        desc:'body&&dd:eq(1)&&Text;body&&dd:eq(2)&&Text;body&&dd:eq(3)&&Text',
        content:'body&&div:has(p)&&p&&Text',

        // 集数按钮是 onclick="senfe(...)"
        tabs:'',
        lists:'a[onclick^="senfe"]',
        list_url:'a&&onclick',
        list_text:'a&&Text'
    },

    搜索:'*'
}
