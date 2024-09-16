var rule = {
  title: '片多多[优]',
  host: 'https://www.herbal-china.com/',
  url: '/mo-zea4s/fyclass/1/0/0/0/0/fypage',
  searchUrl: '/se-zea4s/**-1',
  searchable: 2,
  quickSearch: 0,
  filterable: 0,
  headers: {
    'User-Agent': 'UC_UA',
  },
  class_parse: '.stui-header__menu li:gt(0):lt(6);a&&Text;a&&href;.*/(.*?)/',
  play_parse: true,
  lazy: "js:\n  let html = request(input);\n  let hconf = html.match(/r player_.*?=(.*?)</)[1];\n  let json = JSON5.parse(hconf);\n  let url = json.url;\n  if (json.encrypt == '1') {\n    url = unescape(url);\n  } else if (json.encrypt == '2') {\n    url = unescape(base64Decode(url));\n  }\n  if (/\\.(m3u8|mp4|m4a|mp3)/.test(url)) {\n    input = {\n      parse: 0,\n      jx: 0,\n      url: url,\n    };\n  } else {\n    input = url && url.startsWith('http') && tellIsJx(url) ? {parse:0,jx:1,url:url}:input;\n  }",
  limit: 6,
  double: true,
  推荐: 'ul.stui-vodlist.clearfix;li;a&&title;.lazyload&&data-original;.text-top-left&&Text;a&&href',
  一级: '.stui-vodlist li;a&&title;a&&data-original;.text-top-left&&Text;a&&href',
  二级: {
    title: '.stui-content__detail .title&&Text;.stui-content__detail&&p:eq(-2)&&a&&Text',
    title1: '.stui-content__detail .title&&Text;.stui-content__detail&&p&&Text',
    img: '.lazyload&&data-original',
    desc: '.stui-content__detail p&&Text;.stui-content__detail&&p:eq(-2)&&a:eq(2)&&Text;.stui-content__detail&&p:eq(-2)&&a:eq(1)&&Text;.stui-content__detail p:eq(2)&&Text;.stui-content__detail p:eq(1)&&Text',
    desc1: '.stui-content__detail p:eq(4)&&Text;;;.stui-content__detail p:eq(1)&&Text',
    content: '.text-muted&&p&&Text',
    tabs: '.tab&&li',
    tabs1: '.stui-pannel_bd h1',
    lists: 'div.v1-div:eq(#id) a',
  },
  搜索: 'ul.stui-vodlist__media,ul.stui-vodlist,#searchList li;a&&title;.lazyload&&data-original;.text-top-left&&Text;a&&href;.detail&&Text',
}



