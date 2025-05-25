var rule = {
    title:'养端',
    host:'https://aaq48.com:33666',
    homeUrl:'/home/index.html',
    url:'/home/vodlist/38/fyclass-fypage.html',
    headers:{
        'User-Agent':'MOBILE_UA'
    },
    searchable:0,
    quickSearch:0,
    timeout:5000,
    class_parse:'.menu&&dl&&dd;a&&Text;a&&href;.*/(.*?)-',
    limit:5,
    play_parse:true,
    lazy:'',
    一级:'.channel-list&&dl;h3&&Text;img&&data-original;font&&Text;a&&href',
    二级:'*',
}