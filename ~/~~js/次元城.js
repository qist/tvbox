var rule = {
    title: '次元城动漫[漫]',//规则标题,没有实际作用,但是可以作为cms类名称依据
    编码: '',//不填就默认utf-8
    搜索编码: '',//不填则不编码，默认都是按utf-8.可优先于全局编码属性.比如网页源码编码是gbk,这里可以指定utf-8搜索独立编码。多数情况这个属性不填或者填写gbk应对特殊的网站搜索
    host: 'https://www.cycanime.com',//网页的域名根,包含http头如 https://www,baidu.com
    //url: '/api.php/provide/vod?ac=detail&t=fyclass&pg=fypage&f=',//网站的分类页面链接
    url: '/api.php/provide/vod?&ac=detail&t=fyclass&pg=fypage&f=',//网站的分类页面链接
    ///api.php/provide/vod?&ac=detail&t=fyclass&pg=fypage
    class_name: 'TV动画&剧场版&4K专区',//静态分类名称拼接
    class_url: '20&21&26',//静态分类标识拼接
    homeUrl: '/api.php/provide/vod?ac=detail',//网站的首页链接,可以是完整路径或者相对路径,用于分类获取和推荐获取 fyclass是分类标签 fypage是页数
    searchUrl: '/api.php/provide/vod?ac=detail&wd=**&pg=fypage', //搜索链接 可以是完整路径或者相对路径,用于分类获取和推荐获取 **代表搜索词 fypage代表页数
    detailUrl: '/api.php/provide/vod?ac=detail&ids=fyid', //非必填,二级详情拼接链接,感觉没啥卵用
    searchable: 2,//是否启用全局搜索,
    quickSearch: 0,//是否启用快速搜索,
    play_parse: true,
    parse_url: 'https://player.cycanime.com/?url=',
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
    multi: 1,
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