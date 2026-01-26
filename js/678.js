var rule = {
    title:'闪雷影视',
    编码:'gb2312',
    host:'http://114.100.48.52:18008/jdl',
    url:'/List.asp?ClassID=fyclass&page=fypage',
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
        try {
            // 获取播放页面
            let playUrl = rule.host + `/PlayMov.asp?ClassId=${input}&video=2&exe=0&down=0&movNo=1&vgver=undefined`;
            let content = request(playUrl);
            
            // 从播放页面提取真实播放地址
            let urls = content.match(/top\.location\.href\s*=\s*['"]([^'"]+)['"]/);
            if (!urls) {
                urls = content.match(/window\.open\(['"]([^'"]+)['"]/);
            }
            if (!urls) {
                urls = content.match(/parent\.location\.href\s*=\s*['"]([^'"]+)['"]/);
            }
            if (!urls) {
                urls = content.match(/location\.replace\(['"]([^'"]+)['"]/);
            }
            
            if (urls && urls.length > 1) {
                input = {
                    jx:0,
                    url: urls[1],
                    parse:0
                };
            } else {
                // 如果无法提取播放地址，尝试直接使用影片详情页
                input = {
                    jx:0,
                    url: rule.host + `/movie.asp?ClassID=${input}`,
                    parse:0
                };
            }
        } catch(e) {
            log('解析播放地址出错: ' + e.message);
            input = '';
        }
    }),
    limit:6,
    推荐:'div.box&&div.all.border&&ul.pic&&li;a&&title;img&&src;span&&Text;a&&href',
    一级:'div.lit&&dl;dt&&a&&title;dt&&img&&src;dd:eq(2)&&Text;a&&href',
    二级:{
        title:"div.intro&&ul&&li.h4&&Text;div.intro&&ul&&li:eq(0)&&Text",
        img:"div.intro&&div.img&&img&&src",
        desc:"div.intro&&ul&&li:eq(2)&&Text;div.intro&&ul&&li:eq(4)&&Text;div.intro&&ul&&li:eq(3)&&Text;div.intro&&ul&&li:eq(5)&&Text;div.intro&&ul&&li:eq(6)&&Text",
        content:"div.textnr&&Text",
        tabs:"#content&&div.title&&h3:eq(0)&&Text",
        lists:"#content&&a[onclick^=\"senfe\"]",
        list_url:'a&&onclick',
        list_text:'a&&Text'
    },
    搜索:'div.cont&&dl;dt&&a&&title;dt&&img&&src;dd:eq(1)&&Text;dd&&a&&href',
}