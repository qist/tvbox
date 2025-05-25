/**
 * 20240201 测试OK
 */

var rule = {
    title:'UrleBird[飞]',
    host:'https://urlebird.com',
    homeUrl:'/trending/',
    url:'fyclass/page/fypage/[fyclass/]',
    searchUrl:'/search/?q=**',//Search @user or #hash
    searchable:2,
    quickSearch:0,
    class_name:'更新&人气&热搜',
    class_url:'videos&videos/popular&trending',
    headers:{
        'User-Agent':'PC_UA'
    },
    play_parse:true,
    lazy:'js:let html=request(input);let rurl=html.match(/video src="(.*?)"/)[1];input={parse:0,url:rurl};',
    limit:10,
    推荐:'*',
    一级:"js:var d=[];pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;var list=pdfa(request(input),'body&&.thumb');list.forEach(function(it){let img=pd(it,'.img img&&data-src');if(!/jpg|jpeg|webp/.test(img)){img=pd(it,'.img img&&src')};d.push({desc:pdfh(it,'.author-name&&Text'),title:'♥'+pdfh(it,'.stats div:eq(2)&&Text')+' '+pdfh(it,'.info3--div&&Text'),pic_url:img,url:pd(it,'a:eq(-1)&&href')})});setResult(d);",
    二级:'*',
    搜索:'*',
}
