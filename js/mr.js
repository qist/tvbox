var rule = {
    title: '黑木耳资源',//规则标题,没有实际作用,但是可以作为cms类名称依据
    编码: '',//不填就默认utf-8
    搜索编码: '',//不填则不编码，默认都是按utf-8.可优先于全局编码属性.比如网页源码编码是gbk,这里可以指定utf-8搜索独立编码。多数情况这个属性不填或者填写gbk应对特殊的网站搜索
    host: 'https://heimuer.tv',//网页的域名根,包含http头如 https://www,baidu.com
    //url: '/api.php/provide/vod?ac=detail&t=fyclass&pg=fypage&f=',//网站的分类页面链接
    url: '/index.php/ajax/data?mid=1&tid=fyfilter&page=fypage&limit=20',//网站的分类页面链接
    class_name: '电影&电视剧&动漫&综艺&短剧',//静态分类名称拼接
    class_url: '1&2&3&4&27',//静态分类标识拼接
    homeUrl: '/api.php/provide/vod?ac=detail',//网站的首页链接,可以是完整路径或者相对路径,用于分类获取和推荐获取 fyclass是分类标签 fypage是页数
    searchUrl: '/api.php/provide/vod?ac=detail&wd=**&pg=fypage', //搜索链接 可以是完整路径或者相对路径,用于分类获取和推荐获取 **代表搜索词 fypage代表页数
    detailUrl: '/api.php/provide/vod?ac=detail&ids=fyid', //非必填,二级详情拼接链接,感觉没啥卵用
    searchable: 2,//是否启用全局搜索,
    quickSearch: 0,//是否启用快速搜索,
    filterable: 1,//是否启用筛选,
    filter_url: '{{fl.cateId}}',
    filter: {
        "1": [{ "key": "cateId", "name": "剧情", "value": [{ "n": "全部", "v": "" }, { "n": "剧情片", "v": "6" }, { "n": "动作片", "v": "7" }, { "n": "冒险", "v": "8" }, { "n": "同性", "v": "9" }, { "n": "喜剧", "v": "10" }, { "n": "奇幻", "v": "11" }, { "n": "恐怖", "v": "12" }, { "n": "悬疑", "v": "20" }, { "n": "惊悚", "v": "21" }, { "n": "灾难", "v": "22" }, { "n": "爱情", "v": "23" }, { "n": "犯罪", "v": "24" }, { "n": "科幻", "v": "25" }, { "n": "动画电影", "v": "26" }, { "n": "歌舞", "v": "33" }, { "n": "战争", "v": "34" }, { "n": "经典", "v": "35" }, { "n": "网络电影", "v": "36" }, { "n": "其它", "v": "37" }] }],
        "2": [{ "key": "cateId", "name": "剧情", "value": [{ "n": "全部", "v": "" }, { "n": "国产剧", "v": "13" }, { "n": "港剧", "v": "14" }, { "n": "韩剧", "v": "15" }, { "n": "日剧", "v": "16" }, { "n": "泰剧", "v": "28" }, { "n": "台剧", "v": "29" }, { "n": "欧美剧", "v": "30" }, { "n": "新马剧", "v": "31" }, { "n": "其他剧", "v": "32" }] }],
        "4": [{ "key": "cateId", "name": "剧情", "value": [{ "n": "全部", "v": "" }, { "n": "国产综艺", "v": "38" }, { "n": "港台综艺", "v": "39" }, { "n": "韩国综艺", "v": "40" }, { "n": "日本综艺", "v": "41" }, { "n": "欧美综艺", "v": "42" }, { "n": "新马泰综艺", "v": "43" }, { "n": "其他综艺", "v": "44" }] }],
        "3": [{ "key": "cateId", "name": "剧情", "value": [{ "n": "全部", "v": "" }, { "n": "欧美", "v": "57" }, { "n": "日本", "v": "58" }, { "n": "韩国", "v": "59" }, { "n": "国产", "v": "60" }, { "n": "港台", "v": "61" }, { "n": "新马泰", "v": "62" }, { "n": "其它", "v": "63" }] }]
    },
    filter_def:{
        1:{cateId:'1'},
        2:{cateId:'2'},
        4:{cateId:'4'},
        3:{cateId:'3'},
        27:{cateId:'27'}
    },
    play_parse: false,
    lazy: '',
    multi: 1,
    timeout: 5000,//网站的全局请求超时,默认是3000毫秒
    limit: 20,// 首页推荐显示数量
    推荐: 'json:list;vod_name;vod_pic;vod_remarks;vod_id', // double: true, // 推荐内容是否双层定位
    一级: 'json:list;vod_name;vod_pic;vod_remarks;vod_id',
    /**
     * 资源采集站，二级链接解析
     */
    //二级: `json:list;vod_name;vod_pic;vod_remarks;vod_id`,
    二级: `js:
        let html = request(input);
        let list = JSON.parse(html).list;
        if(list.length===1){
           VOD = list[0];
            VOD.vod_blurb = VOD.vod_blurb.replace(/　/g, '').replace(/<[^>]*>/g, '');
            VOD.vod_content = VOD.vod_content.replace(/　/g, '').replace(/<[^>]*>/g, '');
        }
    `,
    /**
     * 搜索解析 过滤部分资源
     */
    搜索: 'json:list;vod_name;vod_pic;vod_remarks;vod_id',
}