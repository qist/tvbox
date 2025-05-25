Object.assign(muban.mxone5.二级,{
   desc: '.video-info-items:eq(3)&&Text;.tag-link:eq(2)&&Text;.tag-link:eq(3)&&Text;.video-info-actor:eq(1)&&Text;.video-info-actor:eq(0)&&Text',
    content: '.sqjj_a--span&&Text',
    lists: '.module-row-one:eq(#id)&&a.module-row-text',
    list_text:'h4&&Text',
    list_url:'a&&data-clipboard-text',
    list_url_prefix:'push://'
});
var rule = {
    title: '多多影音',
    模板: 'mxone5',
    host: 'https://tv.yydsys.top',
    url: '/index.php/vod/show/id/fyclass/page/fypage.html',
    filter_url:'{{fl.cateId}}{{fl.area}}{{fl.by}}{{fl.class}}{{fl.lang}}{{fl.letter}}/page/fypage{{fl.year}}',
    searchUrl: '/index.php/vod/search.html?wd=**',
    filter:'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',
    class_parse: '.grid-box&&ul&&li;a&&Text;a&&href;.*/(.*?).html',
    cate_exclude: '网址|专题|全部影片',
    一级: '.module-items .module-item;a&&title;img&&data-src;.module-item-text&&Text;a&&href',
    lazy:` if (/aliyundrive.com|quark.cn|alipan.com/.test(url)) { input = 'push://'+ url }`
}