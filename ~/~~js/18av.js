var rule = {
    title:'18av',
    host:'https://maa1812.com',
    url:'/zh/fyclass/all/fypage.html',
    headers:{
        'User-Agent':'MOBILE_UA'
    },
    timeout:5000,
    class_name:'最近更新',//静态分类名称拼接
    class_url:'chinese_list',//静态分类标识拼接
   //class_parse:'ul.animenu__nav&&li;a&&Text;a&&href',
    limit:5,
    play_parse:true,
    lazy:'',
    一级:'.posts&&.video_9s;h3&&Text;img&&src;.meta&&Text;a&&href',
    二级:'*',
}