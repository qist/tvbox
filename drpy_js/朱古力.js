var rule = {
    title:'朱古力',
    host:'https://pigav.com',
    url:'/fyclass/page/fypage',
    headers:{
        'User-Agent':'MOBILE_UA'
    },
    timeout:5000,
    class_name:'最新&熱門&每日&精選',//静态分类名称拼接
    class_url:'最新av線上看&熱門av線上看&每日av線上看線上看&精選av線上看',//静态分类标识拼接
    limit:5,
    play_parse:true,
    lazy:'',
    一级:'.l-post div&&a;a&&title;span&&data-bgsrc;.absolute.bottom-1&&Text;a&&href',
    二级:'*',
}

