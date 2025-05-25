var rule = {
    title:'猫了个咪',
    host:'http://119.28.59.69:8089',
    homeUrl:'/latest/',
    url:'/api/video/index#class=fyclass&page=fypage',
    searchUrl:'/api/special/video?params=#keyword=**&page=fypage',
    headers:{
        'User-Agent':'MOBILE_UA'
    },
    // searchable:2,
    quickSearch:0,
    timeout:5000,
    class_name:'全部&国产专区&欧美精品&动漫&中文字幕&人气女忧&不雅视频&韩三级&热剧大人版&抖音妹合集&猫咪自拍',
    class_url:'0&32&16&31&34&35&37&39&40&41&42',
    limit:5,
    play_parse:true,
    lazy:'js:log(input);',
    lazy:'js:let VID=input.split(";")[1];let VURL=input.split(";")[0];var fn=rc("maomi_aes.js");let url=VURL+"?params="+fn.En(\'{"id":"\'+VID+\'"}\');input=JSON.parse(fn.De(request(url))).data.video_item[0].file;',
    一级:'',
    一级:'js:let d=[];let bodys={access_token:"",cate_id:MY_CATE,identifier:"ffffffff-c67a-899b-ffff-ffffef05ac4a",page:MY_PAGE,region:0,type_id:0,vip:0,year:""};var fn=rc("maomi_aes.js");bodys=fn.En(stringify(bodys));let obj={headers:{"Content-Type":"application/x-www-form-urlencoded"},method:"POST",body:"params="+bodys+"&version=26&sign="+md5("QEBBQADSwrXIXaNqBmMofjfRY/8Sxaxgparams"+bodys+"version26QEBBQADSwrXIXaNqBmMofjfRY/8Sxaxg")};let api=input.split("#")[0];let html=JSON.parse(fn.De(request(api,obj)));html.data.data.forEach(function(it){d.push({title:it.name,img:it.image,desc:it.rate,url:api.replace("index","detail")+";"+it.id})});setResult(d);',
    二级:'*',
    搜索:'',
    // 搜索:'js:let bodys={keyword:KEY,page:MY_PAGE};var fn=rc("maomi_aes.js");bodys=fn.En(stringify(bodys));let url=input.split("#")[0];print(url);var html=JSON.parse(fn.De(request(url+bodys)));let d=html.data.data.map(function(data){return{title:data.video_name,img:data.image,desc:data.rate,url:"http://119.28.59.69:8089/api/video/detail?params=;"+fn.En(\'{"id":"\'+data.video_id+\'"}\')}});setResult(d);',

}