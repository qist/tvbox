var rule = {
author: '小可乐/2409/第一版',
title: '555app',
类型: '影视',
//host: 'https://wuj6h9g3.com',
host: 'https://5moviehub.com',
hostJs: 'let kcode=atob(pdfh(request(HOST),"body&&#domainData&&data-info"));let khost=JSON.parse(kcode).site_main;if(!khost.startsWith("http")){khost="https://"+khost};HOST=khost',
headers: {'User-Agent': 'MOBILE_UA'},
编码: 'utf-8',
timeout: 5000,

homeUrl: '/api.php/app/index_video',
url: '/api.php/app/video?tid=fyfilter&pg=fypage&limit=20',
filter_url: '{{fl.cateId}}&{{fl.class}}&{{fl.area}}&{{fl.lang}}&{{fl.year}}',
detailUrl: '/api.php/app/video_detail?id=fyid',
searchUrl: '/api.php/app/search?text=**&pg=fypage',
searchable: 1, 
quickSearch: 1, 
filterable: 1, 

class_name: '电影&剧集&综艺&动漫&福利',
class_url: '1&2&3&4&124',
filter_def: {
1: {cateId: '1'},
2: {cateId: '2'},
3: {cateId: '3'},
4: {cateId: '4'},
124: {cateId: '124'}
},

tab_remove: ['ddvip'],
play_parse: true,
lazy: `js:
if (/\\.(m3u8|mp4)/.test(input)) {
    input = { jx: 0, parse: 0, url: input }
} else {
    input = { jx: 0, parse: 1, url: input }
}
`,

limit: 9,
double: true,
推荐: 'json:list;vlist;*;*;*;*',
一级: 'json:list;vod_name;vod_pic;vod_remarks;vod_id',
二级: `js:
let kdata = JSON.parse(request(input)).data;
VOD = kdata;
VOD.type_name = kdata.vod_class
`,
搜索: '*',

filter: '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'
}