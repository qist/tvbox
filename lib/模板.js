if (typeof Object.assign !== 'function') {
    Object.assign = function () {
        let target = arguments[0];
        for (let i = 1; i < arguments.length; i++) {
            let source = arguments[i];
            for (let key in source) {
                if (Object.prototype.hasOwnProperty.call(source, key)) {
                    target[key] = source[key];
                }
            }
        }
        return target;
    };
}

// 通用免嗅探播放
let common_lazy = `js:
  let html = request(input);
  let hconf = html.match(/r player_.*?=(.*?)</)[1];
  let json = JSON5.parse(hconf);
  let url = json.url;
  if (json.encrypt == '1') {
    url = unescape(url);
  } else if (json.encrypt == '2') {
    url = unescape(base64Decode(url));
  }
  if (/\\.(m3u8|mp4|m4a|mp3)/.test(url)) {
    input = {
      parse: 0,
      jx: 0,
      url: url,
    };
  } else {
    input;
  }`;
// 默认嗅探播放

let def_lazy = `js:
  input = { parse: 1, url: input, js: '' };`;
// 采集站播放

let cj_lazy = `js:
  if (/\\.(m3u8|mp4)/.test(input)) {
    input = { parse: 0, url: input };
  } else {
    if (rule.parse_url.startsWith('json:')) {
      let purl = rule.parse_url.replace('json:', '') + input;
      let html = request(purl);
      let json = JSON.parse(html);
      if (json.url) {
        input = { parse: 0, url: json.url };
      }
    } else {
      input = rule.parse_url + input;
    }
  }`;

function getMubans() {
    const mubanDict = { // 模板字典
        mx: {
            title: '',
            host: '',
            url: '/vodshow/fyclass--------fypage---/',
            searchUrl: '/vodsearch/**----------fypage---/',
            class_parse: '.top_nav li;a&&Text;a&&href;.*/(.*?)/',
            searchable: 2,
            quickSearch: 0,
            filterable: 0,
            headers: {
                'User-Agent': 'MOBILE_UA',
            },
            play_parse: true,
            lazy: common_lazy,
            limit: 6,
            double: true,
            推荐: '.cbox_list;*;*;*;*;*',
            一级: 'ul.vodlist li;a&&title;a&&data-original;.pic_text&&Text;a&&href',
            二级: {
                title: 'h2&&Text;.content_detail:eq(1)&&li&&a:eq(2)&&Text',
                img: '.vodlist_thumb&&data-original',
                desc: '.content_detail:eq(1)&&li:eq(1)&&Text;.content_detail:eq(1)&&li&&a&&Text;.content_detail:eq(1)&&li&&a:eq(1)&&Text;.content_detail:eq(1)&&li:eq(2)&&Text;.content_detail:eq(1)&&li:eq(3)&&Text',
                content: '.content_desc&&span&&Text',
                tabs: '.play_source_tab&&a',
                lists: '.content_playlist:eq(#id) li',
            },
            搜索: '*',
        },
        mxpro: {
            title: '',
            host: '', // homeUrl:'/',
            url: '/vodshow/fyclass--------fypage---.html',
            searchUrl: '/vodsearch/**----------fypage---.html',
            searchable: 2,//是否启用全局搜索,
            quickSearch: 0,//是否启用快速搜索,
            filterable: 0,//是否启用分类筛选,
            headers: {//网站的请求头,完整支持所有的,常带ua和cookies
                'User-Agent': 'MOBILE_UA', // "Cookie": "searchneed=ok"
            },
            class_parse: '.navbar-items li:gt(0):lt(10);a&&Text;a&&href;/(\\d+)',
            play_parse: true,
            lazy: common_lazy,
            limit: 6,
            double: true, // 推荐内容是否双层定位
            推荐: '.tab-list.active;a.module-poster-item.module-item;.module-poster-item-title&&Text;.lazyload&&data-original;.module-item-note&&Text;a&&href',
            一级: 'body a.module-poster-item.module-item;a&&title;.lazyload&&data-original;.module-item-note&&Text;a&&href',
            二级: {
                title: 'h1&&Text;.module-info-tag-link:eq(-1)&&Text',
                img: '.lazyload&&data-original||data-src||src',
                desc: '.module-info-item:eq(-2)&&Text;.module-info-tag-link&&Text;.module-info-tag-link:eq(1)&&Text;.module-info-item:eq(2)&&Text;.module-info-item:eq(1)&&Text',
                content: '.module-info-introduction&&Text',
                tabs: '.module-tab-item',
                lists: '.module-play-list:eq(#id) a',
                tab_text: 'div--small&&Text',
            },
            搜索: 'body .module-item;.module-card-item-title&&Text;.lazyload&&data-original;.module-item-note&&Text;a&&href;.module-info-item-content&&Text',
        }, mxone5: {
            title: '',
            host: '',
            url: '/show/fyclass--------fypage---.html',
            searchUrl: '/search/**----------fypage---.html',
            searchable: 2,//是否启用全局搜索,
            quickSearch: 0,//是否启用快速搜索,
            filterable: 0,//是否启用分类筛选,
            class_parse: '.nav-menu-items&&li;a&&Text;a&&href;.*/(.*?)\.html',
            play_parse: true,
            lazy: common_lazy,
            limit: 6,
            double: true, // 推荐内容是否双层定位
            推荐: '.module-list;.module-items&&.module-item;a&&title;img&&data-src;.module-item-text&&Text;a&&href',
            一级: '.module-items .module-item;a&&title;img&&data-src;.module-item-text&&Text;a&&href',
            二级: {
                title: 'h1&&Text;.tag-link&&Text',
                img: '.module-item-pic&&img&&data-src',
                desc: '.video-info-items:eq(3)&&Text;.tag-link:eq(2)&&Text;.tag-link:eq(1)&&Text;.video-info-items:eq(1)&&Text;.video-info-items:eq(0)&&Text',
                content: '.vod_content&&Text',
                tabs: '.module-tab-item',
                lists: '.module-player-list:eq(#id)&&.scroll-content&&a',
                tab_text: 'div--small&&Text',
            },
            搜索: '.module-items .module-search-item;a&&title;img&&data-src;.video-serial&&Text;a&&href',
        }, 首图: {
            title: '',
            host: '',
            url: '/vodshow/fyclass--------fypage---/',
            searchUrl: '/vodsearch/**----------fypage---.html',
            searchable: 2,//是否启用全局搜索,
            quickSearch: 0,//是否启用快速搜索,
            filterable: 0,//是否启用分类筛选,
            headers: {//网站的请求头,完整支持所有的,常带ua和cookies
                'User-Agent': 'MOBILE_UA', // "Cookie": "searchneed=ok"
            },
            class_parse: '.myui-header__menu li.hidden-sm:gt(0):lt(7);a&&Text;a&&href;/(\\d+).html',
            play_parse: true,
            lazy: common_lazy,
            limit: 6,
            double: true, // 推荐内容是否双层定位
            推荐: 'ul.myui-vodlist.clearfix;li;a&&title;a&&data-original;.pic-text&&Text;a&&href',
            一级: '.myui-vodlist li;a&&title;a&&data-original;.pic-text&&Text;a&&href',
            二级: {
                title: '.myui-content__detail .title--span&&Text;.myui-content__detail p.data:eq(3)&&Text',
                img: '.myui-content__thumb .lazyload&&data-original',
                desc: '.myui-content__detail p.otherbox&&Text;.year&&Text;.myui-content__detail p.data:eq(4)&&Text;.myui-content__detail p.data:eq(2)&&Text;.myui-content__detail p.data:eq(0)&&Text',
                content: '.content&&Text',
                tabs: '.myui-panel__head&&li',
                // tabs: '.nav-tabs&&li',
                lists: '.myui-content__list:eq(#id) li',
            },
            搜索: '#searchList li;a&&title;.lazyload&&data-original;.pic-text&&Text;a&&href;.detail&&Text',
        }, 首图2: {
            title: '',
            host: '',
            url: '/list/fyclass-fypage.html',
            searchUrl: '/vodsearch/**----------fypage---.html',
            searchable: 2,//是否启用全局搜索,
            quickSearch: 0,//是否启用快速搜索,
            filterable: 0,//是否启用分类筛选,
            headers: {
                'User-Agent': 'UC_UA', // "Cookie": ""
            },
            class_parse: '.stui-header__menu li:gt(0):lt(7);a&&Text;a&&href;.*/(.*?).html',
            play_parse: true,
            lazy: common_lazy,
            limit: 6,
            double: true, // 推荐内容是否双层定位
            推荐: 'ul.stui-vodlist.clearfix;li;a&&title;.lazyload&&data-original;.pic-text&&Text;a&&href',
            一级: '.stui-vodlist li;a&&title;a&&data-original;.pic-text&&Text;a&&href',
            二级: {
                title: '.stui-content__detail .title&&Text;.stui-content__detail&&p:eq(-2)&&a&&Text',
                title1: '.stui-content__detail .title&&Text;.stui-content__detail&&p&&Text',
                img: '.stui-content__thumb .lazyload&&data-original',
                desc: '.stui-content__detail p&&Text;.stui-content__detail&&p:eq(-2)&&a:eq(2)&&Text;.stui-content__detail&&p:eq(-2)&&a:eq(1)&&Text;.stui-content__detail p:eq(2)&&Text;.stui-content__detail p:eq(1)&&Text',
                desc1: '.stui-content__detail p:eq(4)&&Text;;;.stui-content__detail p:eq(1)&&Text',
                content: '.detail&&Text',
                tabs: '.stui-pannel__head h3',
                tabs1: '.stui-vodlist__head h3',
                lists: '.stui-content__playlist:eq(#id) li',
            },
            搜索: 'ul.stui-vodlist__media,ul.stui-vodlist,#searchList li;a&&title;.lazyload&&data-original;.pic-text&&Text;a&&href;.detail&&Text',
        }, 默认: {
            title: '',
            host: '',
            url: '',
            searchUrl: '',
            searchable: 2,
            quickSearch: 0,
            filterable: 0,
            filter: '',
            filter_url: '',
            filter_def: {},
            headers: {
                'User-Agent': 'MOBILE_UA',
            },
            timeout: 5000,
            class_parse: '#side-menu li;a&&Text;a&&href;/(.*?)\.html',
            cate_exclude: '',
            play_parse: true,
            lazy: def_lazy,
            double: true,
            推荐: '列表1;列表2;标题;图片;描述;链接;详情',
            一级: '列表;标题;图片;描述;链接;详情',
            二级: {
                title: 'vod_name;vod_type',
                img: '图片链接',
                desc: '主要信息;年代;地区;演员;导演',
                content: '简介',
                tabs: '',
                lists: 'xx:eq(#id)&&a',
                tab_text: 'body&&Text',
                list_text: 'body&&Text',
                list_url: 'a&&href',
            },
            搜索: '列表;标题;图片;描述;链接;详情',
        }, vfed: {
            title: '',
            host: '',
            url: '/index.php/vod/show/id/fyclass/page/fypage.html',
            searchUrl: '/index.php/vod/search/page/fypage/wd/**.html',
            searchable: 2,//是否启用全局搜索,
            quickSearch: 0,//是否启用快速搜索,
            filterable: 0,//是否启用分类筛选,
            headers: {
                'User-Agent': 'UC_UA',
            },
            class_parse: '.fed-pops-navbar&&ul.fed-part-rows&&a;a&&Text;a&&href;.*/(.*?).html',
            play_parse: true,
            lazy: common_lazy,
            limit: 6,
            double: true, // 推荐内容是否双层定位
            推荐: 'ul.fed-list-info.fed-part-rows;li;a.fed-list-title&&Text;a&&data-original;.fed-list-remarks&&Text;a&&href',
            一级: '.fed-list-info&&li;a.fed-list-title&&Text;a&&data-original;.fed-list-remarks&&Text;a&&href',
            二级: {
                title: 'h1.fed-part-eone&&Text;.fed-deta-content&&.fed-part-rows&&li&&Text',
                img: '.fed-list-info&&a&&data-original',
                desc: '.fed-deta-content&&.fed-part-rows&&li:eq(1)&&Text;.fed-deta-content&&.fed-part-rows&&li:eq(2)&&Text;.fed-deta-content&&.fed-part-rows&&li:eq(3)&&Text',
                content: '.fed-part-esan&&Text',
                tabs: '.fed-drop-boxs&&.fed-part-rows&&li',
                lists: '.fed-play-item:eq(#id)&&ul:eq(1)&&li',
            },
            搜索: '.fed-deta-info;h1&&Text;.lazyload&&data-original;.fed-list-remarks&&Text;a&&href;.fed-deta-content&&Text',
        }, 海螺3: {
            title: '',
            host: '',
            searchUrl: '/v_search/**----------fypage---.html',
            url: '/vod_____show/fyclass--------fypage---.html',
            headers: {
                'User-Agent': 'MOBILE_UA',
            },
            timeout: 5000,
            class_parse: 'body&&.hl-nav li:gt(0);a&&Text;a&&href;.*/(.*?).html',
            cate_exclude: '明星|专题|最新|排行',
            limit: 40,
            play_parse: true,
            lazy: common_lazy,
            double: true,
            推荐: '.hl-vod-list;li;a&&title;a&&data-original;.remarks&&Text;a&&href',
            一级: '.hl-vod-list&&.hl-list-item;a&&title;a&&data-original;.remarks&&Text;a&&href',
            二级: {
                title: '.hl-dc-title&&Text;.hl-dc-content&&li:eq(6)&&Text',
                img: '.hl-lazy&&data-original',
                desc: '.hl-dc-content&&li:eq(10)&&Text;.hl-dc-content&&li:eq(4)&&Text;.hl-dc-content&&li:eq(5)&&Text;.hl-dc-content&&li:eq(2)&&Text;.hl-dc-content&&li:eq(3)&&Text',
                content: '.hl-content-text&&Text',
                tabs: '.hl-tabs&&a',
                tab_text: 'a--span&&Text',
                lists: '.hl-plays-list:eq(#id)&&li',
            },
            搜索: '.hl-list-item;a&&title;a&&data-original;.remarks&&Text;a&&href',
            searchable: 2,//是否启用全局搜索,
            quickSearch: 0,//是否启用快速搜索,
            filterable: 0,//是否启用分类筛选,
        }, 海螺2: {
            title: '',
            host: '',
            searchUrl: '/index.php/vod/search/page/fypage/wd/**/',
            url: '/index.php/vod/show/id/fyclass/page/fypage/',
            headers: {
                'User-Agent': 'MOBILE_UA',
            },
            timeout: 5000,
            class_parse: '#nav-bar li;a&&Text;a&&href;id/(.*?)/',
            limit: 40,
            play_parse: true,
            lazy: common_lazy,
            double: true,
            推荐: '.list-a.size;li;a&&title;.lazy&&data-original;.bt&&Text;a&&href',
            一级: '.list-a&&li;a&&title;.lazy&&data-original;.list-remarks&&Text;a&&href',
            二级: {
                title: 'h2&&Text;.deployment&&Text',
                img: '.lazy&&data-original',
                desc: '.deployment&&Text',
                content: '.ec-show&&Text',
                tabs: '#tag&&a',
                lists: '.play_list_box:eq(#id)&&li',
            },
            搜索: '.search-list;a&&title;.lazy&&data-original;.deployment&&Text;a&&href',
            searchable: 2,//是否启用全局搜索,
            quickSearch: 0,//是否启用快速搜索,
            filterable: 0,//是否启用分类筛选,
        }, 短视: {
            title: '',
            host: '', // homeUrl:'/',
            url: '/channel/fyclass-fypage.html',
            searchUrl: '/search.html?wd=**',
            searchable: 2,//是否启用全局搜索,
            quickSearch: 0,//是否启用快速搜索,
            filterable: 0,//是否启用分类筛选,
            headers: {//网站的请求头,完整支持所有的,常带ua和cookies
                'User-Agent': 'MOBILE_UA', // "Cookie": "searchneed=ok"
            },
            class_parse: '.menu_bottom ul li;a&&Text;a&&href;.*/(.*?).html',
            cate_exclude: '解析|动态',
            play_parse: true,
            lazy: common_lazy,
            limit: 6,
            double: true, // 推荐内容是否双层定位
            推荐: '.indexShowBox;ul&&li;a&&title;img&&data-src;.s1&&Text;a&&href',
            一级: '.pic-list&&li;a&&title;img&&data-src;.s1&&Text;a&&href',
            二级: {
                title: 'h1&&Text;.content-rt&&p:eq(0)&&Text',
                img: '.img&&img&&data-src',
                desc: '.content-rt&&p:eq(1)&&Text;.content-rt&&p:eq(2)&&Text;.content-rt&&p:eq(3)&&Text;.content-rt&&p:eq(4)&&Text;.content-rt&&p:eq(5)&&Text',
                content: '.zkjj_a&&Text',
                tabs: '.py-tabs&&option',
                lists: '.player:eq(#id) li',
            },
            搜索: '.sr_lists&&ul&&li;h3&&Text;img&&data-src;.int&&p:eq(0)&&Text;a&&href',
        }, 短视2: {
            title: '',
            host: '',
            class_name: '电影&电视剧&综艺&动漫',
            class_url: '1&2&3&4',
            searchUrl: '/index.php/ajax/suggest?mid=1&wd=**&limit=50',
            searchable: 2,
            quickSearch: 0,
            headers: {'User-Agent': 'MOBILE_UA'},
            url: '/index.php/api/vod#type=fyclass&page=fypage',
            filterable: 0,//是否启用分类筛选,
            filter_url: '',
            filter: {},
            filter_def: {},
            detailUrl: '/index.php/vod/detail/id/fyid.html',
            play_parse: true,
            lazy: common_lazy,
            limit: 6,
            推荐: '.list-vod.flex .public-list-box;a&&title;.lazy&&data-original;.public-list-prb&&Text;a&&href',
            一级: 'js:let body=input.split("#")[1];let t=Math.round(new Date/1e3).toString();let key=md5("DS"+t+"DCC147D11943AF75");let url=input.split("#")[0];body=body+"&time="+t+"&key="+key;print(body);fetch_params.body=body;let html=post(url,fetch_params);let data=JSON.parse(html);VODS=data.list.map(function(it){it.vod_pic=urljoin2(input.split("/i")[0],it.vod_pic);return it});',
            二级: {
                title: '.slide-info-title&&Text;.slide-info:eq(2)--strong&&Text',
                img: '.detail-pic&&data-original',
                desc: '.slide-info-remarks&&Text;.slide-info-remarks:eq(1)&&Text;.slide-info-remarks:eq(2)&&Text;.slide-info:eq(1)--strong&&Text;.info-parameter&&ul&&li:eq(3)&&Text',
                content: '#height_limit&&Text',
                tabs: '.anthology.wow.fadeInUp.animated&&.swiper-wrapper&&a',
                tab_text: 'a--span&&Text',
                lists: '.anthology-list-box:eq(#id) li',
            },
            搜索: 'json:list;name;pic;;id',
        }, 采集1: {
            title: '',
            host: '',
            homeTid: '13',
            homeUrl: '/api.php/provide/vod/?ac=detail&t={{rule.homeTid}}',
            detailUrl: '/api.php/provide/vod/?ac=detail&ids=fyid',
            searchUrl: '/api.php/provide/vod/?wd=**&pg=fypage',
            url: '/api.php/provide/vod/?ac=detail&pg=fypage&t=fyclass',
            headers: {'User-Agent': 'MOBILE_UA'},
            timeout: 5000, // class_name: '电影&电视剧&综艺&动漫',
            // class_url: '1&2&3&4',
            // class_parse:'js:let html=request(input);input=JSON.parse(html).class;',
            class_parse: 'json:class;',
            limit: 20,
            multi: 1,
            searchable: 2,//是否启用全局搜索,
            quickSearch: 1,//是否启用快速搜索,
            filterable: 0,//是否启用分类筛选,
            play_parse: true,
            parse_url: '',
            lazy: cj_lazy,
            推荐: '*',
            一级: 'json:list;vod_name;vod_pic;vod_remarks;vod_id;vod_play_from',
            二级: `js:
            let html=request(input);
            html=JSON.parse(html);
            let data=html.list;
            VOD=data[0];`,
            搜索: '*',
        },
    };
    return JSON.parse(JSON.stringify(mubanDict));
}

var mubanDict = getMubans();
var muban = getMubans();
export default {muban, getMubans};