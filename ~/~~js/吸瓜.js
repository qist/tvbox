var rule = {
    title:'吸瓜',
    host:'https://xgsp.tv',
    // homeUrl:'',
    url:'/list/?fyclass-fypage.html',
    headers:{
        'User-Agent':'MOBILE_UA'
    },
    searchable:0,
    quickSearch:0,
    timeout:5000,
    class_parse:'.wap-roll&&li;a&&Text;a&&href;(\\d+).html',
    cate_exclude:'独家',
    limit:5,
    play_parse:true,
    lazy:'js:let html=request(input);let a=html.match(/var now="(.*?)"/)[1];input=a',
    推荐:'ul.row.row-space7.row-m-space7.tx-column-5.tx-column-m-2;li;a&&title;img&&src;.ico-right&&Text;a&&href',
    double:true,
    一级:'.tx-column-m-2.mb20&&li;h2&&Text;img&&src;.ico-right&&Text;a&&href',
    二级:'*',
}