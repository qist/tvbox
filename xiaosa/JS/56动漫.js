var rule = {
    title: '56动漫',
    host: 'https://www.56dm.cc/',
    url: 'https://www.56dm.cc/type/fyclass-fypage.html',
    searchUrl: 'https://www.56dm.cc/search/**----------fypage---.html',
    searchable: 2, //是否启用全局搜索,
    quickSearch: 0, //是否启用快速搜索,
    filterable: 0, //是否启用分类筛选,
    headers: {
        'User-Agent': 'UC_UA', // "Cookie": ""
    }, // class_parse:'.stui-header__menu li:gt(0):lt(7);a&&Text;a&&href;/(\\d+).html',
    class_parse: '.snui-header-menu-nav li:gt(0):lt(6);a&&Text;a&&href;.*/(.*?).html',
    play_parse: true,
    lazy: `js:
            if(/\\.(m3u8|mp4)/.test(input)){
                input = {parse:0,url:input}
            }else{
                if(rule.parse_url.startsWith('json:')){
                    let purl = rule.parse_url.replace('json:','')+input;
                    let html = request(purl);
                    input = {parse:0,url:JSON.parse(html).url}
                }else{
                    input= rule.parse_url+input; 
                }
            }
            `,
    limit: 6,
    推荐: '.cCBf_FAAEfbc;li;a&&title;.lazyload&&data-original;.dAD_BBCI&&Text;a&&href',
    double: true, // 推荐内容是否双层定位
    一级: '.cCBf_FAAEfbc li;a&&title;a&&data-original;.dAD_BBCI&&Text;a&&href',
    二级: {
        "title": "h1&&Text",
        "img": ".stui-content__thumb .lazyload&&data-original",
        "desc": ".cCBf_DABCcac__hcIdeE p:eq(0)&&Text;.cCBf_DABCcac__hcIdeE p:eq(1)&&Text;.cCBf_DABCcac__hcIdeE p:eq(2)&&Text;.cCBf_DABCcac__hcIdeE p:eq(3)&&Text;.cCBf_DABCcac__hcIdeE p:eq(4)&&Text",
        "content": ".detail&&Text",
        "tabs": ".channel-tab li",
        "lists": ".play-list-content:eq(#id) li"
    },
    搜索: '.cCBf_FAAEfbc__dbD;a&&title;.lazyload&&data-original;.dAD_BBCI&&Text;a&&href;.cCBf_FAAEfbc__hcIdeE&&p:eq(0) p&&Text',
}