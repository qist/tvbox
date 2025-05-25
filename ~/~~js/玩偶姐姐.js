var rule = {
    title:'玩偶姐姐',
    host:'https://hongkongdollvideo.com',
    homeUrl:'/latest/',
    url:'/fyclass/fypage.html[/fyclass/]',
    headers:{
        'User-Agent':'MOBILE_UA'
    },
    searchable:0,
    quickSearch:0,
    timeout:5000,
    class_parse:'#side-menu:lt(1) li;a&&Text;a&&href;com/(.*?)/',
    limit:5,
    play_parse:true,
    lazy:'',
    一级:'.col-sm-6;h3&&Text;img&&data-src;.date&&Text;a&&href',
    二级:'*',
}