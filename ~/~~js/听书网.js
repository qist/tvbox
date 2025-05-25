var rule = {
    title:'听书网',
    host:'https://www.tingbook.cc',
    // url:'/book/fyclass_fypage.html',
    url:'/book/fyclass-fypage.html',
    searchUrl:'/search.php?page=fypage&searchword=**&searchtype=-1',
    searchable:2,
    quickSearch:0,
    headers:{
        'User-Agent':'MOBILE_UA'
    },
    timeout:5000,
    class_parse:'.nav li;a&&Text;a&&href;/book/(\\d+).html',
    play_parse:true,
    lazy:'js:let purl=request(input).match(/r now=\"(.*?)\"/)[1];log("=================================>"+purl);input={jx:0,url:purl,parse:0}',
    limit:6,
    double:true,
    推荐:'.row2;ul&&li;.f-bold&&Text;.img-box img&&src;.f-gray&&Text;a&&href',
    一级:'.row3&&li;.f-bold&&Text;.img-box img&&src;.f-gray&&Text;a&&href',
    二级:{
        "title":"h2&&Text",
        "img":".img-box img&&src",
        "desc":"section&&p:eq(1)&&Text",
        "content":"section&&p:eq(2)&&Text",
        "tabs":"#yuedu&&h2",
        "lists":"#yuedu:eq(#id)&&ul&&li"
    },
    搜索:'*',
}