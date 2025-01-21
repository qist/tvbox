var rule = {
    title:'JRKAN直播',
    host:'http://www.jrs80.com/?lan=1',
    // JRKAN备用域名:www.jrkankan.com / www.jrkan365.com / jrsyyds.com / www.jryyds.com / jrskan.com / jrsbxj.com /Jrkan备用域名1: www.jrkan2022.com 备用域名2: www.jrs23.com 备用域名2: www.jrskk.com 最新网址发布:www.qiumi1314.co
    
    url:'/fyclass',
    searchUrl:'/x/search/?q=**',
    searchable:1,
    quickSearch:1,
    class_name:'全部',
    class_url:'/',
    //class_url:'?live',
    headers:{
        'User-Agent':'MOBILE_UA'
    },
    timeout:5000,
    play_parse:true,
    lazy:"",
    limit:6,
    double:false,
    推荐:'*',
    // 一级:'.loc_match:eq(2) ul;li:gt(1):lt(4)&&Text;img&&src;li:lt(2)&&Text;a:eq(1)&&href',//play.sportsteam333.com
    一级:"js:var items=[];pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;var html=request(input);var tabs=pdfa(html,'body&&.d-touch');tabs.forEach(function(it){var pz=pdfh(it,'.name:eq(1)&&Text');var ps=pdfh(it,'.name:eq(0)&&Text');var pk=pdfh(it,'.name:eq(2)&&Text');var img=pd(it,'img&&src');var url=pd(it,'a.me&&href');var timer=pdfh(it,'.lab_time&&Text');var parts = timer.split(' ');var dateParts = parts[0].split('-');var timeParts = parts[1].split(':');var year = new Date().getFullYear();var date = new Date(year, dateParts[0] - 1, dateParts[1], timeParts[0], timeParts[1]);var now = new Date();var hundredMinutesAgo = new Date(now.getTime() - 100 * 60 * 1000);if (date > hundredMinutesAgo) {timer = timer.split(' ')[1];items.push({desc:timer+ '  '+'🏆'+ps,title:pz+'  🆚  '+pk,pic_url:img,url:url})}});setResult(items);",
    二级:{
        "title":".sub_list li:lt(2)&&Text;.sub_list li:eq(0)&&Text",
        "img":"img&&src",
        "desc":";;;.lab_team_home&&Text;.lab_team_away&&Text",
        "content":".sub_list ul&&Text",
        "tabs":"js:TABS=['实时直播']",
        "lists":"js:LISTS=[];pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;let html=request(input);let data=pdfa(html,'.sub_playlist&&a');TABS.forEach(function(tab){let d=data.map(function(it){let name=pdfh(it,'strong&&Text');let url=pd(it,'a&&data-play');return name+'$'+url});LISTS.push(d)});",
    },
    搜索:'js:let d=[];setResult(d);',
}
