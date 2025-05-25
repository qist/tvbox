var rule = {
    title: '小胡',
    host: 'http://cc.xzam.cn',
    homeUrl: '/api.php/provide/vod?ac=detail',
    searchUrl: '/api.php/provide/vod?ac=detail&wd=**&pg=fypage',
    detailUrl: '/api.php/provide/vod?ac=detail&ids=fyid',
    url: '/api.php/provide/vod?ac=detail&t=fyclass&pg=fypage&f=',
    class_name: '电影&国剧&美剧&韩剧&动漫',
    class_url: '20&1&2&3&4',
    tab_rename:{'公众号：小胡不胡':'东辰影视'}, 
    推荐: 'json:list;vod_name;vod_pic;vod_remarks;vod_id',
    一级: 'json:list;vod_name;vod_pic;vod_remarks;vod_id',
    二级: `js:
        let html = request(input);
        let list = JSON.parse(html).list;
        if(list.length===1){
           VOD = list[0];
            VOD.vod_blurb = VOD.vod_blurb.replace(/　/g, '').replace(/<[^>]*>/g, '');
            VOD.vod_content = VOD.vod_content.replace(/　/g, '').replace(/<[^>]*>/g, '');
        }
    `,
    搜索: 'json:list;vod_name;vod_pic;vod_remarks;vod_id',
}