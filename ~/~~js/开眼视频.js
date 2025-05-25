var rule = {
    title:'开眼视频',
    host:'http://baobab.kaiyanapp.com:80',
    url:'/api/v5/index/tab/feed?udid=ecab2cc100f540e482c5f7db5542a33cc5a908bc&vc=591&vn=6.2.1&size=1080X2340&deviceModel=HLK-AL00&first_channel=eyepetizer_zhihuiyun_market&last_channel=eyepetizer_zhihuiyun_market&system_version_code=29',
    searchUrl:'',
    searchable:0,
    quickSearch:0,
    filterable:0,
    headers:{
        'User-Agent':'MOBILE_UA'
    },
    class_name:'今日开眼精选',//静态分类名称拼接
    class_url:'/',//静态分类标识拼接
    timeout:5000,
    play_parse:true,
    pagecount:{"/":1},
    lazy:"js:input=JSON.parse(request(input)).playUrl+'&_t=.m3u8'",
    limit:6,
    推荐:'',
    一级:"js:var s=request(input);var json={};eval('json='+s);var next=json.nextPageUrl;var s2=fetch(next,{});var j2={};eval('j2='+s2);for(var i=0;i<j2.itemList.length;i++){json.itemList.push(j2.itemList[i])}var d=[];for(var i=0;i<json.itemList.length;i++){var j=json.itemList[i];if(j.type!='followCard')continue;var r={};r.pic_url=j.data.content.data.cover.feed;r.title=j.data.content.data.title;r.desc=j.data.header.description;r.url='https://baobab.kaiyanapp.com/api/v1/video/'+j.data.header.id+'?f=web';d.push(r)}setResult(d);",
    二级:'*',
    搜索:'',
}