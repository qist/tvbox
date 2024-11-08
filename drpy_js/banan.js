var rule = {
    title:'banan',
    host:'https://banan.tv',
    url:'/vodtype/fyclass-fypage.html',
    headers:{ 
        'User-Agent':'MOBILE_UA'
    },
    timeout:5000,
    class_name:'探花&91大神&素人&国产&高清&FC2',//静态分类名称拼接
    class_url:'57&23&63&25&22&28',//静态分类标识拼接
    //class_parse:'ul.navbar-nav&&li:gt(1):lt(6);a&&Text;a&&href',
    limit:5,
    play_parse:true,
    lazy:'',
    一级:'.img-box.cover-md&&a;img&&alt;img&&data-src;.grid_date&&Text;a&&href',
    二级:'*',
	
}

