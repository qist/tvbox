var rule = {
author: '小可乐/2408/第一版',
title: '旺旺影视',
类型: '影视',
//host: 'https://www.wwgz.cn',
host: 'https://www.nmdvd.com',
hostJs: 'HOST = pdfh(request(HOST), "b:eq(0)&&Text"); !HOST.startsWith("http") ? HOST = "https://"+HOST : HOST',
headers: {'User-Agent': 'MOBILE_UA'},
编码: 'utf-8',
timeout: 5000,

homeUrl: '/',
url: '/vod-list-id-fyfilter.html',
filter_url: '{{fl.cateId}}-pg-fypage-order--by-{{fl.by}}-class-0-year-{{fl.year}}-letter-{{fl.letter}}-area-{{fl.area}}-lang-',
detailUrl: '',
searchUrl: '/index.php?m=vod-search&wd=**',
searchable: 1, 
quickSearch: 1, 
filterable: 1, 

class_name: '电影&剧集&综艺&动漫&短剧',
class_url: '1&2&3&4&26',
filter_def: {
1: {cateId: '1'},
2: {cateId: '2'},
3: {cateId: '3'},
4: {cateId: '4'},
26: {cateId: '26'}
},

play_parse: true,
lazy: `js: input = { jx: 0, parse: 1, url: input }`,
// lazy: `js:
// let init_js = 'Object.defineProperties(navigator, {platform: {get: () => "Android"} })';
// input = {
// parse: 1,
// url: input,
// js: 'try { location.href = document.querySelectorAll("iframe")[1].src }catch(err) {}document.querySelector(".line").click()',
// parse_extra: '&init_script=' + encodeURIComponent(base64Encode(init_js)),
// }
// `,


limit: 9,
double: false,
推荐: '*',
一级: 'li:has(.pic);.sTit&&Text;img:eq(-1)&&data-echo;.sBottom&&Text;a&&href',
二级: {
title: '.title&&Text;.type-title&&Text',
img: '.page-hd&&img&&src',
desc: '.desc_item--span:eq(0)&&Text;.desc_item--span:eq(-1)&&Text;;.desc_item--span:eq(1)&&Text;.desc_item--span:eq(2)&&Text',
content: 'p:contains(介)&&Text',
tabs: '.hd&&a',
tab_text: 'body&&Text',
lists: '.numList:eq(#id)&&a',
list_text: 'body&&Text',
list_url: 'a&&href'
},
搜索: '*;*;img&&data-src;.sStyle&&Text;*',

filter: 'H4sIAAAAAAAAA+3aW09cVRjG8Xs+xr7GZB32OtC7nkvP52N6gXUSG2tNKJoQQlKlWA62qLEglXpInEIjlSE1jZ1K+TLsDXwLZzprr+fBC0OCxmDWHeu/OjP7Nx0m715hqCuT2Z5rXUPZB7XBbE92o2+g1vte1p3d7vuw1lqvL78uvp9srT/pu/VxK1wbym63cjG6sDmy0M6thcyGu0OeWFhbmVsfvx92DHam54rxeezYuLM+tlyOjGLHYWf+q+LVa+z4uFN++mV5dxo7PXid8fktzyYFHjT27VpznLZw3eXIRPnZY9rC5RX1+1suQrau7/pwd3zD+vprfXi7irlG8UXz798uPPXP85uzn4caFtXe5tPZ8velsBcW8XFTjfLVm+pxnUV8z948LL5bCXthEZ/zh2fYC4v4DszUy7nFsBcWce9FA48Li7g33Sgmfiye/FRtx3V81WeL5ZP6Rn11rfm4em1OUfWgUTSfVqrOotrbmFzGFYQFru4RX90j3mtdSjm52nprq6eN6/jM9dX1qefr47PVk8d19S/WVu+tr8yU09V/BtbxVUZfFr+OVC/RWWz5jAzW+vrxGSlnXm7O/LbNz4gSKg/t7Y/UNbrmrtAVd4kuuQt0QV32xC57uHt0z92hO+4W3XI36IY7vJK9El7JXgmvZK+EV7JXwivZK+AV7BXwCvYKeAV7BbyCvQJewV4Br2CvgFewV8Ar2CvgFewV8Ap4ZU9P5X37I3WP7rk7dMfdolvuBt1wz9Fz7hpdc1foirtEl9wFOns9vJ69Hl7PXg+vZ6+H17PXw+vZ6+H17PXwevZ6eD17PbyevR5ez14Hr2Ovg9ex18Hr2Ovgdex18Dr2Ongdex28jr0OXsdeB69jr4PXsdfCa9lr4bXstfBa9lp4LXstvJa9Fl7LXguvZa+F17LXwmvZa+G17DXwGvYaeA17DbyGvQZew14Dr2Gvgdew18Br2GvgNew18Br2GngNe3N4c/bm8ObszeHN2ZvDm7M3hzdnbw5vzt4c3py9Obw5e3N4c/bm8Obs1fBq9mp4NXs1vJq9Gl7NXg2vZq+GV7NXw6vZq+HV7NXwavZqeDV7FbyKvQpexV4Fr2KvglexV8Gr2KvgVexV8Cr2KngVexW8ir0KXsVeCa9kr4RXslfCK9kr4ZXslfBK9kp42/MVz6m3agMDNZpUi+cz5dKDbU6qe0PYG8u+UPbFsj+U/bEcCOVALAdDORjLoVAOxXI4lMOxHAnlSCy9ofTGcjSUo7EcC+VYLMdDOR7LiVBOxHIylJOxnArlVCynQzkdy5lQzsRyNpSzsZwL5Vws50M5H8uFUC7EcjGUi7FcCuVSLJdDuRzLlVCuxHI1lKuxiHeqD2n7py2flXcH8TkpH35dNKe2+TnB7U9rMXCz9QTVzlqzWTa+CTvv3xy4E3c2lu4VY9Wd8p0bH/XX2hfTdb27K1M7Pb3A73DrznGtOV+MV3eLdDvRuv1u32i/aFRbmjz19r00HoUvkXJxvn0Lji2Tzg7S2UE6O0hnB+nsoLNIZwedRTo76CzS2UFn8e+cHaRZP0uz/i6e9TXP+ml4TsNzGp7T8JyG5zQ872R4TkNRloaiXTwU5Ts9AMXvRjGxUP7xC51X+r9s0Z9B9aSjzDSNpWksTWNpGsvSNPaPTWPo6Sgz+w+OMtM0nKVpeBdPw8qmM8I0lf5fp9L07Zy+nXftt3PX8J8nkdqKbTYAAA=='
}