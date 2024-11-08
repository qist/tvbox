var rule = {
    模板: '首图2',
    title: '[影]桃花源',
    host: 'https://a.thyys.com/',
    url: '/vodshow/fyclass--------fypage---.html',
    searchUrl: '/vodsearch/**----------fypage---.html',
    class_parse: '.stui-header__menu li;a&&Text;a&&href;/.*/(\\w+)-----------.html',
  lazy: $js.toString(() => {
    let html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
    let url = html.url;
    if (html.encrypt == '1') {
      url = unescape(url)
    } else if (html.encrypt == '2') {
      url = unescape(base64Decode(url))
    }
    if (/\.m3u8|\.mp4/.test(url)) {
      input = {
        jx: 0,
        url: url,
        parse: 0
      }
    } else {
      input
    }
}),
    推荐: 'ul.stui-vodlist.clearfix;li;a&&title;.lazyload&&data-original;.pic-text&&Text;a&&href',
    double: true,
    一级: '.stui-vodlist li;a&&title;a&&data-original;.pic-text&&Text;a&&href',
    二级: {
        title: '.stui-content__detail .title&&Text;.stui-content__detail p:eq(-2)&&Text',
        img: '.stui-content__thumb .lazyload&&data-original',
        desc: '.stui-content__detail p:eq(0)&&Text;.stui-content__detail p:eq(1)&&Text;.stui-content__detail p:eq(2)&&Text',
        content: '.detail&&Text',
        tabs: '',
        lists: '.play-btn a',
    },
    搜索: 'ul.stui-vodlist__media:eq(0),ul.stui-vodlist:eq(0),#searchList li;a&&title;.lazyload&&data-original;.text-muted&&Text;a&&href;.text-muted:eq(-1)&&Text',
}
