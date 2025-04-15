var rule = {
    类型: '影视',
    title: '思古影视',
    host: 'https://siguyy.cn',
    url: '/show/fyclass--------fypage---/',
    searchUrl: 'https://siguyy.cn/search/-------------/?wd=**',
    searchable: 2,
    quickSearch: 0,
    timeout: 5000,
    play_parse: true,
    filterable: 0,
    class_name: '电影&电视剧&综艺&动漫',
    class_url: '1&2&3&4',
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
            `,
    headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    },
    推荐: '*',
    一级: '.container .flex.desktop-hover-effect;span&&Text;img&&data-original;p.truncate&&Text;a&&href',
    二级: {
        title: '.p-3.mobile&&Text',
        img: 'img&&data-original',
        desc: '.text-sm.py-1&&Text',
        content: '.text-secondary&&Text',
        tabs: '.flex.flex-row.gap-1.items-center',
        lists: '.flex.flex-column.overflow-auto.no-scrollbar&&li',
        tab_text: 'body&&Text',
        list_text: 'a&&Text',
        list_url: 'a&&href',
    },
    double: false,
    搜索: '.col-lg-6.col-md-12.mt-2.mb-2.cursor-pointer;.topic-details-title-sub.text-secondary&&Text;img&&data-original;.topic-details-title&&Text;a&&href',
}