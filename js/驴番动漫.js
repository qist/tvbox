Object.assign(muban.mxpro.二级, {
    tab_text: 'div--small&&Text',
});
var rule = {
    模板: 'mxpro',
    title: '驴番[漫]',
    host: 'https://www.lvfan.fun',
    url: 'vodshow/fyclass--------fypage---/',
    class_parse: '.navbar-items li;a&&Text;a&&href;.*/(\\d+)/',
    searchUrl: '/vodsearch/**----------fypage---/',
    tab_exclude: '排序',
}