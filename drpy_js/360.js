var rule = {
    title:'360影视',
    host:'https://www.360kan.com',
    homeUrl:'https://api.web.360kan.com/v1/rank?cat=2&size=9',
    detailUrl:'https://api.web.360kan.com/v1/detail?cat=fyclass&id=fyid',
    searchUrl:'https://api.so.360kan.com/index?force_v=1&kw=**&from=&pageno=fypage&v_ap=1&tab=all',
    url:'https://api.web.360kan.com/v1/filter/list?catid=fyclass&rank=rankhot&cat=&year=&area=&act=&size=35&pageno=fypage&callback=',
    headers:{
        'User-Agent':'MOBILE_UA'
    },
    timeout:5000,
    class_name:'电视剧&电影&综艺&动漫',
    class_url:'2&1&3&4',
    limit:5,
    multi:1,
    searchable:2,
    play_parse:true,
    lazy:'js:input=input.split("?")[0];log(input);',
    // 疑似t4专用的
    // lazy:'js:input={parse: 1, playUrl: "", jx: 1, url: input.split("?")[0]}',
    // 手动调用解析请求json的url,此lazy不方便
    // lazy:'js:input="https://cache.json.icu/home/api?type=ys&uid=292796&key=fnoryABDEFJNPQV269&url="+input.split("?")[0];log(input);let html=JSON.parse(request(input));log(html);input=html.url||input',
    推荐:'json:data;title;cover;comment;cat+ent_id;description',
    一级:'json:data.movies;title;cover;pubdate;id;description',
    二级:'',
    二级:'js:let html=JSON.parse(fetch(input,fetch_params));let data=html.data;let tilte=data.title;let img=data.cdncover;let vod_type=data.moviecategory.join(",");let area=data.area.join(",");let director=data.director.join(",");let actor=data.actor.join(",");let content=data.description;let base_vod={vod_id:input,vod_name:tilte,type_name:vod_type,vod_actor:actor,vod_director:director,vod_content:content,vod_remarks:area,vod_pic:urljoin2(input,img)};let delta=200;let vod_play={};let sites=data.playlink_sites;sites.forEach(function(site){let playList="";let vodItems=[];if(data.allupinfo){let total=parseInt(data.allupinfo[site]);for(let j=1;j<total;j+=delta){let end=Math.min(total,j+delta-1);let url2=buildUrl(input,{start:j,end:end,site:site});let vod_data=JSON.parse(fetch(url2),fetch_params).data;if(vod_data.allepidetail){vod_data=vod_data.allepidetail[site];vod_data.forEach(function(item,index){vodItems.push((item.playlink_num||"")+"$"+urlDeal(item.url||""))})}else{vod_data=vod_data.defaultepisode;vod_data.forEach(function(item,index){vodItems.push((item.period||"")+(item.name||"")+"$"+urlDeal(item.url)||"")})}}}else{let item=data.playlinksdetail[site];vodItems.push((item.sort||"")+"$"+urlDeal(item.default_url||""))}if(vodItems.length>0){playList=vodItems.join("#")}if(playList.length<1){return}vod_play[site]=playList});let tabs=Object.keys(vod_play);let playUrls=[];for(let id in tabs){print("id:"+id);playUrls.push(vod_play[tabs[id]])}if(tabs.length>0){let vod_play_from=tabs.join("$$$");let vod_play_url=playUrls.join("$$$");base_vod.vod_play_from=vod_play_from;base_vod.vod_play_url=vod_play_url}VOD=base_vod;',
    搜索:'json:data.longData.rows;titleTxt||titlealias;cover;cat_name;cat_id+en_id;description',
}