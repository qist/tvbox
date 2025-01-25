// 搜索验证 -> drpy_ocr自动过搜索验证失败
var rule={
    title:'骚火电影',
    // host:'https://shdy3.com',
    host:'http://shapp.us',
    hostJs:'print(HOST);let html=request(HOST,{headers:{"User-Agent":PC_UA}});let src=jsp.pdfh(html,"a:eq(2)&&href");print(src);HOST=src',
    // url:'/list/fyclass-fypage.html',
    url:'/list/fyfilter-fypage.html',
    filterable:1,//是否启用分类筛选,
    filter_url:'{{fl.cateId}}',
    filter: {
        "1":[{"key":"cateId","name":"类型","value":[{"v":"1","n":"全部"},{"v":"6","n":"喜剧"},{"v":"7","n":"爱情"},{"v":"8","n":"恐怖"},{"v":"9","n":"动作"},{"v":"10","n":"科幻"},{"v":"11","n":"战争"},{"v":"12","n":"犯罪"},{"v":"13","n":"动画"},{"v":"14","n":"奇幻"},{"v":"15","n":"剧情"},{"v":"16","n":"冒险"},{"v":"17","n":"悬疑"},{"v":"18","n":"惊悚"},{"v":"19","n":"其它"}]}],
        "2":[{"key":"cateId","name":"类型","value":[{"v":"2","n":"全部"},{"v":"20","n":"🇨🇳中国"},{"v":"21","n":"TVB"},{"v":"22","n":"韩剧"},{"v":"23","n":"美剧"},{"v":"24","n":"日剧"},{"v":"25","n":"英剧"},{"v":"26","n":"台剧"},{"v":"27","n":"其它"}]}],
        "4":[{"key":"cateId","name":"类型","value":[{"v":"4","n":"全部"},{"v":"38","n":"搞笑"},{"v":"39","n":"恋爱"},{"v":"40","n":"热血"},{"v":"41","n":"格斗"},{"v":"42","n":"美少女"},{"v":"43","n":"魔法"},{"v":"44","n":"机战"},{"v":"45","n":"校园"},{"v":"46","n":"亲子"},{"v":"47","n":"童话"},{"v":"48","n":"冒险"},{"v":"49","n":"真人"},{"v":"50","n":"LOLI"},{"v":"51","n":"其它"}]}],
        // "28":[{"key":"cateId","name":"综艺","value":[{"v":"28","n":"脱口秀"},{"v":"29","n":"真人秀"},{"v":"30","n":"选秀"},{"v":"31","n":"美食"},{"v":"32","n":"旅游"},{"v":"33","n":"汽车"},{"v":"34","n":"访谈"},{"v":"35","n":"纪实"},{"v":"36","n":"搞笑"},{"v":"37","n":"其它"}]}]
    },
    filter_def:{
        1:{cateId:'1'},
        2:{cateId:'2'},
        4:{cateId:'4'}
        // 28:{cateId:'28'}
    },
    searchUrl:'/search.php?page=fypage&searchword=**&searchtype=',
    searchable:2,
    quickSearch:0,
    headers:{'User-Agent':'MOBILE_UA', },
    timeout:5000,//网站的全局请求超时,默认是3000毫秒
    class_name:'电影&电视剧&动漫',
    class_url:'1&2&4',
    play_parse:true,
    lazy:`js:
        pdfh = jsp.pdfh;pdfa = jsp.pdfa;pd = jsp.pd;
        var html = pd(request(input), 'iframe&&src');
        var apiurl = '';
        if (/api\\.hhplayer/.test(html)) {
            apiurl = 'https://api.hhplayer.com/api.php';
        } else if (/hkjx\\.hhplayer/.test(html)) {
            apiurl = 'https://hkjx.hhplayer.com/api.php';
        } else if (/hhjx\\.hhplayer/.test(html)) {
            apiurl = 'https://hhjx.hhplayer.com/api.php';
        } else if (/play\\.hhplayer/.test(html)) {
            apiurl = 'https://play.hhplayer.com/hhjx/api.php';
        }
        var url = '';
        var t = '';
        var key = '';
        eval(pdfh(request(html), 'body&&script,0&&Html').split('var act')[0].replaceAll('var ', ''));
        var purl = JSON.parse(request(apiurl, {
            headers: {
                'User-Agent': MOBILE_UA,
                'referer': html
            },
            body: 'url=' + url + '&t=' + t + '&key=' + key + '&act=0&play=1',
            method: 'POST'
        })).url;
        if (/obj\\/tos/.test(purl)) {
            input = {
                jx: 0,
                url: purl,
                parse: 0
            }
        } else {
            input = {
                jx: 0,
                url: /http/.test(purl) ? purl: 'https://api.hhplayer.com' + purl,
                parse: 0
            }
        }
    `,
    推荐:'.v_list,0&&li;*;*;*;*',
    一级:'.v_list li;a&&title;.lazyload&&data-original;.v_note&&Text;a&&href',
    二级:{
        "title":"h1&&Text;",
        "img":".m_background&&style",
        "desc":";;;.v_info_box&&p&&Text",
        "content":".p_txt.show_part&&Text",
        "tabs":".from_list&&li",
        "lists":"#play_link&&li:eq(#id)&&a"
    },
    搜索:'*',
}
