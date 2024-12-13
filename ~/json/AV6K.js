var rule ={
            title: 'AV6K',
            host: 'https://dhfgbj-000.av6k505.top/home/?kc=https://xn--004-0u0e55rj80i.pdm-thkfds.top/',
            url: 'https://dhfgbj-000.av6k505.top/fyclass/fypage.html',
            //searchUrl: 'https://hdg.avkd6.world/cn/home/web/index.php/vod/search/page/fypage/wd/**.html',
            class_parse: '.frame&&.frameC&&.menu&&a;a&&Text;a&&href;.*/(.*?)/',
 //class_name:'国产&传媒&日韩&动漫&欧美&吃瓜',    
// class_url:'guochan&chuanmei&rihan&dongman&oumei&chigua',      
            searchable: 2,
            quickSearch: 0,
            filterable: 0,
            headers: {
                'User-Agent': 'PC_UA',
            },
            play_parse: true,
                                  lazy: `js:
let kcode=jsp.pdfh(request(input).match(/<iframe(.*?)</iframe>/)[1]);
let kurl=kcode.match(/url=(.*?)\"/)[1];
if (/m3u8|mp4/.test(kurl)) {
input = { jx: 0, parse: 0, url: kurl }
} else {
input = { jx: 0, parse: 1, url: rule.parse_url+kurl }
}`, 
            limit: 6,
            推荐: 'body&&.listAC;a&&title;img&&src;a&&Text;a&&href',
            double: true,
            一级: '#thumbsnum&&.listA;a&&title;img&&src;a&&Text;a&&href',
            二级:'*',
            搜索: '*',
        }