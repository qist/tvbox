var rule = {
  title : '皮皮虾[优]',
  host : 'http://www.52ppx.top/',
  url : '/s/fyclass-fypage.html',
  searchUrl : '/vodsearch.html?wd=**',
  searchable : 2,  // 是否启用全局搜索,
  quickSearch : 0, // 是否启用快速搜索,
  filterable : 0,  // 是否启用分类筛选,
  headers : {
    'User-Agent' : 'okhttp/3.12.11', // "Cookie":"searchneed=ok"
  },
  编码 : 'utf-8',
  timeout : 5000,
  class_name : '剧集&电影&动漫番剧',
  class_url : '1&2&3',
  tab_exclude : '今日更新|APP|留言|硬核指南',
  play_parse : true,
  lazy : `js:
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
  limit : 6,
  double : true,
  推荐 : '*',
  一级 :'.module-item;img&&alt;img&&data-original;.module-item-note&&Text;a&&href',
  二级 : {
    "title" : "h1&&a&&Text",
    "img" : "img&&data-original",
    "desc" : ".module-info-tag&&Text",
    "content" : ".module-info-introduction-content&&p&&Text",
    "tabs" : ".module-tab-item.tab-item--small",
    "lists" : ".module-play-list:eq(#id)&&a"
  },
  搜索 :'.module-item;img&&alt;img&&data-original;.module-item-note&&Text;a&&href',
}