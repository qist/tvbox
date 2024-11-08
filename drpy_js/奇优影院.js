// 网址发布页 www.qiyoudy.info
muban.首图2.二级.title = 'h1&&Text;.data--span:eq(0)&&Text';
muban.首图2.二级.desc = '.data.hidden-sm&&Text;;;p.line1--span&&Text;.data--span:eq(1)&&Text';
muban.首图2.二级.content = '.desc--span&&Text';
muban.首图2.二级.tabs = '.nav-tabs a';
var rule = {
    title:'奇优影院',
    模板:'首图2',
    host:'http://1e6e.com',
    // url:'/list/fyclass_fypage.html',
    url:'/list/fyclass_fypage.html?order=fyfilter',
    filterable:1,//是否启用分类筛选,
    filter_url:'{{fl.by}}',
    filter:{
        "1":[{"key":"by","name":"排序","value":[{"n":"按时间","v":"time"},{"n":"按人气","v":"hit"}]}],
        "2":[{"key":"by","name":"排序","value":[{"n":"按时间","v":"time"},{"n":"按人气","v":"hit"}]}],
        "3":[{"key":"by","name":"排序","value":[{"n":"按时间","v":"time"},{"n":"按人气","v":"hit"}]}],
        "4":[{"key":"by","name":"排序","value":[{"n":"按时间","v":"time"},{"n":"按人气","v":"hit"}]}],
        "6":[{"key":"by","name":"排序","value":[{"n":"按时间","v":"time"},{"n":"按人气","v":"hit"}]}]
    },
    filter_def:{
        1:{by:'time'},
        2:{by:'time'},
        3:{by:'time'},
        4:{by:'time'},
        6:{by:'time'}
    },
    class_parse: '.stui-header__menu li:gt(0):lt(5);a&&Text;a&&href;.*/(.*?).html',
    // searchUrl:'/search.php;**',
    searchUrl:'/search.php#searchword=**;post',
    // 搜索:'js:let url=input.split(";")[0];let d=[];let body={searchword:input.split(";")[1]};body="searchword="+input.split(";")[1];fetch_params.body=body;let html=post(url,fetch_params);let pdfa=jsp.pdfa;let pdfh=jsp.pdfh;let pd=jsp.pd;let lists=pdfa(html,"ul.stui-vodlist__media&&li");lists.forEach(function(it){d.push({title:pdfh(it,".title&&Text"),url:pd(it,"a&&href"),desc:pdfh(html,".pic-text&&Text"),pic_url:pd(html,".lazyload&&data-original")})});setResult(d);',
    //搜索:'li.stui-vodlist__item;a&&title;a&&data-original;.pic-text&&Text;a&&href'
}