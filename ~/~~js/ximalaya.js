var rule = {
    title: '喜马拉雅',
    host: 'https://www.ximalaya.com',
    homeUrl: '/channel/7/',//网站的首页链接,用于分类获取和推荐获取
    url: '/revision/metadata/v2/channel/albums?pageNum=fypage&pageSize=50&sort=1&metadata=&groupId=fyclass',
    detailUrl: '/revision/album/v1/getTracksList?albumId=fyid',//二级详情拼接链接(json格式用)
    searchUrl: '/revision/search/main?core=album&kw=**&page=fypage&spellchecker=true&rows=20&condition=relation&device=iPhone&fq=&paidFilter=false',
    searchable: 2,
    quickSearch: 0,
    headers: {
        'User-Agent': 'PC_UA'
    },
    class_parse: '.first .channel;a&&Text;a&&href;.*/(.*?)/',
    play_parse: true,
    lazy: 'js:let result={};let Play_Ref="https://www.ximalaya.com/sound/"+input+"/";let url="https://www.ximalaya.com/revision/play/v1/audio?id="+input+"&ptype=1";let html=request(url,{headers:{"Referer":Play_Ref,"User-Agent":PC_UA}});let jo=JSON.parse(html);let purl=jo["data"]["src"];result["parse"]=0;result["playUrl"]="";result["url"]=purl;result["header"]="";input=result;',
    limit: 6,
    推荐: 'js:let d=[];function home_lists(){let lists=[];let html=request(input);let jo=JSON.parse(html.match(/window.__INITIAL_STATE__ =(.*?);</)[1]);let vodList=jo.store.ChannelDetailPageV2.channelAlbumsInfo.albums;vodList.forEach(function(vod){let aid=vod["albumId"];let title=vod["albumTitle"];let img=/http/.test(vod.albumCoverPath)?vod["albumCoverPath"]:"https://imagev2.xmcdn.com/"+vod["albumCoverPath"];let remark=vod["albumListenCount"]+"❤️"+vod["intro"];lists.push({"vod_id":aid,"vod_name":title,"vod_pic":img,"vod_remarks":remark})});return lists}VODS=home_lists();',
    一级: 'js:let d=[];function cate_lists(){let lists=[];let html=request(input);let jo=JSON.parse(html);let vodList=jo.data.albums;vodList.forEach(function(vod){if(vod["vipType"]!==2){let aid=vod["albumId"];let title=vod["albumTitle"];let img=/http/.test(vod.albumCoverPath)?vod["albumCoverPath"]:"https://imagev2.xmcdn.com/"+vod["albumCoverPath"];let remark=vod["intro"];lists.push({"vod_id":aid,"vod_name":title,"vod_pic":img,"vod_remarks":remark})}});return lists}VODS=cate_lists();',
    二级: 'js:let d=[];let html=request(input);let json=JSON.parse(html).data.tracks[0];VOD={vod_id:"",vod_url:input,vod_name:"",type_name:"",vod_actor:"",vod_year:"",vod_director:"",vod_area:"",vod_content:"",vod_remarks:"",vod_pic:""};VOD.vod_id=json.albumId;VOD.vod_name=json.albumTitle;VOD.vod_pic=/http/.test(json.albumCoverPath)?json.albumCoverPath:"https://imagev2.xmcdn.com/"+json.albumCoverPath;VOD.vod_year=(json.createDateFormat+"").split("-")[0];VOD.vod_actor=json.anchorName;VOD.vod_director=json.anchorName;VOD.vod_content=json.albumTitle;let playlists=[];let listUrl="https://www.ximalaya.com/revision/album/v1/getTracksList?albumId="+json.albumId+"&pageSize=100&pageNum=1";let data=JSON.parse(request(listUrl)).data;let total=data.trackTotalCount;playlists=data.tracks;if(total>100){for(let i=2;i<total/100+1;i++){let listUrl="https://www.ximalaya.com/revision/album/v1/getTracksList?albumId="+json.albumId+"&pageSize=100&pageNum="+i;let data=JSON.parse(request(listUrl)).data;playlists=playlists.concat(data.tracks)}}playlists.forEach(function(it){d.push({title:"第"+it.index+"集",desc:it.albumTitle||it.anchorName||it.length,img:/http/.test(it.albumCoverPath)?it.albumCoverPath:"https://imagev2.xmcdn.com/"+it.albumCoverPath,url:it.trackId})});VOD.vod_play_from="ximalaya";VOD.vod_play_url=d.map(function(it){return it.title+"$"+it.url}).join("#");',
    搜索: 'json:data.album.docs;title;coverPath;intro;albumId',
}