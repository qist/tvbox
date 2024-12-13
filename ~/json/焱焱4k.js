var rule = {
author: '小可乐/2409/第二版',
title: '焱焱4kapp',
类型: '影视',
host: 'http://101.34.60.156:6541',
hostJs: '',
headers: {'User-Agent': 'Dart/2.14 (dart:io)'},
编码: 'utf-8',
timeout: 5000,

homeUrl: '/api.php/app/index_video',
url: '/api.php/app/video?tid=fyclass&fyfilter&pg=fypage&limit=20',
filter_url: '{{fl.class}}&{{fl.area}}&{{fl.lang}}&{{fl.year}}',
detailUrl: '/api.php/app/video_detail?id=fyid',
searchUrl: '/api.php/app/search?text=**&pg=fypage',
searchable: 1, 
quickSearch: 1, 
filterable: 1, 

class_name: '电影&剧集&综艺&动漫&少儿&纪录&短剧',
class_url: '1&2&3&4&5&20&21',
filter_def: {},

play_parse: true,
lazy: `js:
if (/\\.(m3u8|mp4)/.test(input)) {
    input = { jx: 0, parse: 0, url: input }
} else if (/qq|NBY/.test(input)) {
    let kurl = JSON.parse(request('http://101.34.60.156:81/api/?key=2af08b0f40d14046d89cd8682ce7e7ed&url=' + input)).url;
    input = { jx: 0, parse: 0, url: kurl }
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

filter: 'H4sIAAAAAAAAA+2Y31MaSRDH3/kz9tkHF2OSS5V/SSoP1JWVh3g+JJWrSllWqQgBYgQtg+HAX4kIeoKgxsBywD+zs7v8FzfQbe/0YGq508pL9pFPf+mZ6Znt7pmliGEaz55HloxX8++MZ8bvC7E3b4wpYzH2x7z8KdIVJ56Qv/+MLbyV4PmSsTjEieogXh1i+cNYnkKaL0k90pGjOUS3CjfVRHekQHSrcFZzzkqeKRDRKJmq3S3xUQDRKJUt0e7wUQCRD1qW7wMQzSP12bbSfB6AbhVe7URsnDEFIppH5sLtcgUiZS3uTkdfyxCRovxeXwsimmntxO4d8pkCIh/J7UHhlPsARD72z+TquA9ApFg7d/NbXAGIFPGMs/YXVwCieHSyItHi8QB0qxjsbTufy0yBiEbJv/fSFh8FEK22V3d3voluky+YKOmyx95X7QwAIsVmUmQvuQIQnYF+Tu4XPwOA/NiXnL0tLfYjRIr1vvs3XzMiilt3y+2U7lgUMyy/WJ6izzj2ej6mfMWlhtiwJv2KjyuDQhLp0M8cEtqkk4LTulAFSPzINpx2j3kAQgvqbYpiVxUgoV2++qQJkFDgPzQ1ARLysFt2SufMAxBaxcGp5gGJf46+awIk/iQbY5NsMA8fG8I6YR6AkIf1rIytSJ0yJwRpseW+m6256QJbL0E/mRw6H/ryv2xEgiRL3NidPNMAYQdoIbb40j9A3kXNq65MeoCKXalHOvQzh0TZPE2AhM7H5bEmQEKbt9sVH3c1jQ+VPdY1QJRTogmQKAdRFwBRTom+WCBKuEU9zgRAWLjfzcdeK99r+9rudCcMd3Q6+gjZ0Mvc6LdinNGMM6oxqhmjqtHUjKZqnNaM04rR/I0b5W/F+FQzPlWNTzTjE9X4WDM+Vo2zmnFWNWoRMtUImVqETDVCphYhU42QqUXIVCNkahGSv+WWR15MRYzog3VcgTUsuI+BAitWb0Q8e0flRcPkPZ6o3wirxhWA/lNfFNDjBfdFwT1ecH0P7ljs9pFe3xH5fVHCKVzwHQBE8/iU1LsvREoHoEcd0Z1ZHX3ckdbv0xckE1LP6gaQiSvq/RuHwKo+QWcRULSDO4t8QxZVsXfEnBAMy+z/KLNhkQyLpF4kZx6qSA5W0m5lhZc2QGqKXj8YS9ES0bdU73uNFL/oASIf2zUnw69xiPyvIOG0eDFB5H9IV3Y7x2cKSMlvg698pohIYZ2J+j5XAKJ5FC/HrtCAyMfOgXOtPaAAIh+tlpPK2ta2fv1lBore9RdZNnn0AJG/5pq3usE9Afpp5UsWIlltWFIHomQxmde04jMkJDivyM1gAiBhyg9Tfpjyg1P+o4dK+cEJPfiN2I3XvCNeNhDRKJtVN5fkowAiRW7fPddeTQH5aSnobdbL7Xmb/AaHiEY5PBJFfuNCNPl9yilZYy/AgGgegW+dwXdN0ZAhvubzAKQqyldjColoX4579j/8nRmRf687EKmidq8bIbq1WZeixgstIhqlmHEKvEgi8mPaFP1dLaYj9BPvZMWubfH3PiATX5h+XLPCe0xY1MKidv+iNqsWtXDrf6Wtl8EK9/5X3PvI8r8qPWwTWCEAAA=='
}