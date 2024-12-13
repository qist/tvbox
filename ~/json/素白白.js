// 地址发布页 https://subaibai.vip/
// 搜索数字验证
var rule = {
  title: '素白白',
  // host:'https://www.subaibaiys.com',
  host: 'https://subaibai.vip',
  hostJs: $js.toString(() => {
      print(HOST);
      let html = request(HOST, {headers: {"User-Agent": PC_UA}});
      let src = jsp.pdfh(html, ".go:eq(0)&&a&&href");
      print(src);
      HOST = src;
  }),
  url: '/fyclassfyfilter',
  filterable: 1,//是否启用分类筛选,
  filter_url: '{{fl.area}}{{fl.year}}{{fl.class}}{{fl.cateId}}/page/fypage',
  filter: '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',
  // searchUrl:'/search?q=**',
  searchUrl: '/page/fypage?s=**',
  searchable: 2,//是否启用全局搜索,
  quickSearch: 0,//是否启用快速搜索,
  headers: {
      'User-Agent': 'UC_UA',
  },
  // class_parse:'.navlist&&li;a&&Text;a&&href;.*/(\\w+)',
  class_name: '影视筛选&电影&电视剧&热门电影&高分电影&动漫电影&香港经典电影&国产剧&欧美剧&韩剧&动漫剧&漫威宇宙电影系列&速度与激情电影系列&007系列(25部正传+2部外传)',//静态分类名称拼接
  class_url: 'movie_bt&new-movie&tv-drama&hot-month&high-movie&cartoon-movie&hongkong-movie&domestic-drama&american-drama&korean-drama&anime-drama&marvel-movies&fastfurious&zero-zero-seven',//静态分类标识拼接
  play_parse: true,
  lazy: $js.toString(() => {
      pdfh = jsp.pdfh;
      var html = request(input);
      var ohtml = pdfh(html, '.videoplay&&Html');
      var url = pdfh(ohtml, "body&&iframe&&src");
      if (/Cloud/.test(url)) {
          var ifrwy = request(url);
          let code = ifrwy.match(/var url = '(.*?)'/)[1].split('').reverse().join('');
          let temp = '';
          for (let i = 0x0; i < code.length; i = i + 0x2) {
              temp += String.fromCharCode(parseInt(code[i] + code[i + 0x1], 0x10))
          }
          input = {
              jx: 0,
              url: temp.substring(0x0, (temp.length - 0x7) / 0x2) + temp.substring((temp.length - 0x7) / 0x2 + 0x7),
              parse: 0
          }
      } else if (/decrypted/.test(ohtml)) {
          var phtml = pdfh(ohtml, "body&&script:not([src])&&Html");
          eval(getCryptoJS());
          var scrpt = phtml.match(/var.*?\)\);/g)[0];
          var data = [];
          eval(scrpt.replace(/md5/g, 'CryptoJS').replace('eval', 'data = '));
          input = {
              jx: 0,
              url: data.match(/url:.*?[\'\"](.*?)[\'\"]/)[1],
              parse: 0
          }
      } else {
          input
      }
  }),
  lazy: '',
  推荐: 'body&&.mi_btcon;ul&&li;*;*;*;*',
  double:true, // 推荐内容是否双层定位
  一级: '.mrb&&li;img&&alt;img&&data-original;.jidi&&Text;a&&href',
  二级: {
      "title": "h1&&Text;.moviedteail_list&&li:eq(0)&&Text",
      "img": ".dyimg&&img&&src",
      "desc": ".moviedteail_list&&li:eq(-1)&&Text;;;.moviedteail_list&&li:eq(7)&&Text;.moviedteail_list&&li:eq(5)&&Text",
      "content": ".yp_context&&p&&Text",
      "tabs": ".mi_paly_box .ypxingq_t",
      "lists": ".paly_list_btn:eq(#id) a"
  },
  搜索: '.search_list&&li;*;*;*;*',
  图片来源: '@Referer=https://www.subaibaiys.com@User-Agent=Mozilla/5.0 (Linux; Android 11; PEHT00 Build/RKQ1.201217.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36',
}