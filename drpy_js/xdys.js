var rule = {
    title: 'brovod',
    host: 'https://www.brovod.com',
    url: '/show/fyclass--hits------fypage---/',
    searchUrl: '/ss/**----------fypage---/',
    searchable: 2,
    quickSearch: 0,
    filterable: 0,
    headers: {
        'User-Agent': 'MOBILE_UA',
    },
    class_name: '电影&电视剧&综艺&动漫&记录片&短剧',
    class_url: '1&2&3&4&5&6',
    tab_order:['自建','PC蓝光','蓝光1线'],
    //tab_remove:['急速1线','急速2线','急速3线','急速4线'],
    play_parse: true,
    lazy: `js:
    var html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
    log(html)
    var url = html.url;
    if (html.from == 'bilibili' || html.from== 'lzm3u8' || html.from== 'ffm3u8'|| html.from== 'bfzym3u8' || html.from== 'leshi'|| html.from== 'qiyi'|| html.from== 'xdzj'|| html.from== 'qq'|| html.from== 'youku'|| html.from== 'NBY') {
    let jxhtml = post('https://api.xdys.vip/lx/post.php', {
        body:url
        });
    let jxurl =JSON.parse(jxhtml)
    input=jxurl.url || input
    }
    if (html.from == 'mytv') {
    let jxinput = 'https://pl.qcheng.cc/?url='+url
    let jxhtml=JSON.parse(request(jxinput))
    input=jxhtml.url || input
    }
  `,
    limit: 6,
    推荐: '.tab-list.active;a.module-poster-item.module-item;.module-poster-item-title&&Text;.lazyload&&data-original;.module-item-note&&Text;a&&href',
    double: true,
    一级: 'body a.module-poster-item.module-item;a&&title;.lazyload&&data-original;.module-item-note&&Text;a&&href',
    二级: {
        title: 'h1&&Text;.module-info-tag-link:eq(2)&&Text',
        img: '.lazyload&&data-original',
        desc: '.module-info-item:eq(3)&&Text;.module-info-tag-link:eq(0)&&Text;.module-info-tag-link:eq(1)&&Text;.module-info-item:eq(2)&&Text;.module-info-item:eq(1)&&Text',
        content: '.module-info-introduction&&Text',
        tabs: '.module-tab-items-box.hisSwiper span',
        lists: '.module-play-list:eq(#id) a',
    },
    搜索: 'body .module-item;.module-card-item-title&&Text;.lazyload&&data-original;.module-item-note&&Text;a&&href;.module-info-item-content&&Text',
}
