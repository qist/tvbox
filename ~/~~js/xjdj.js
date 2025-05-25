var rule = {
    title: '世界短剧',
    host: 'http://106.52.241.21:83',
    homeUrl: '/api.php/provide/vod?ac=detail', 
    searchUrl: '/api.php/provide/vod?ac=detail&wd=**&pg=fypage',
    detailUrl: '/api.php/provide/vod?ac=detail&ids=fyid',
    url: '/api.php/provide/vod?ac=detail&t=fyclass&pg=fypage&f=',
    class_name: '短剧&快手&抖音&都市&古装&重生&逆袭&虐恋&萌宝&言情&穿越&战神&神医&赘婿&甜宠&其他',
    class_url: '1&2&3&4&5&6&7&8&9&10&11&12&13&14&15&16',
    tab_rename:{'zzdj':'东辰影视2群：783264601'}, 
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