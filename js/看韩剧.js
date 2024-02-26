muban.首图.二级.title = 'h1&&Text;.data--span:eq(5)&&Text';
muban.首图.二级.desc = '.data:eq(4)&&Text;;;.data--span:eq(3)&&Text;.data--span:eq(2)&&Text';
muban.首图.二级.lists = '.myui-content__list:eq(#id) li:not(:matches(APP秒播))';
var rule={
    title:'看韩剧',
    模板:'首图',
    // host:'https://www.kan.cc',
    // host:'https://www.kangii.com',
    host:'https://cc.kan.cc',
    url:'/search.html?page=fypage&searchtype=5&tid=fyclassfyfilter',
    filterable:1,//是否启用分类筛选,
    filter_url:'&order={{fl.by or "time"}}&year={{fl.year}}',
    filter:{
        "1":[{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"more","v":"more"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hit"},{"n":"评分","v":"commend"}]}],
        "2":[{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"more","v":"more"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hit"},{"n":"评分","v":"commend"}]}],
        "3":[{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"more","v":"more"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hit"},{"n":"评分","v":"commend"}]}]
    },
    searchUrl:'/search.html?page=fypage&searchword=**&submit=submit',
    headers:{
        "User-Agent":"MOBILE_UA",
        "Cookie":"_funcdn_token=15ecdee338f7976141723bc370d27780861128baf03c8ad523ee358d77eb6848;Hm_lvt_193d42d6df9341f3a303004df15e3f0d=1666062561;_clck=jtnlof|1|f5t|0;_clsk=1qend98|1666062751559|7|1|h.clarity.ms/collect;Hm_lpvt_193d42d6df9341f3a303004df15e3f0d=1666062756"
    },
    class_parse:'div.myui-panel__head.clearfix;h2&&Text;a&&href;.*/(\\d+).html',
    lazy:`js:
        let html = request(input);
        let url = unescape(html.match(/var now=unescape\\("(.*?)"/)[1]);
        let pn = html.match(/var pn="(.*?)"/)[1];
        let jx = 'https://jiexi.ddmz6.com/api/publicApi.php?url=';
        if (/无尽/.test(pn)) {
            url = urljoin2(url, request(url).match(/var main = "(.*?)"/)[1])
        } else {
            url = request(jx + url + '&code=' + pn).match(/var url = '(.*?)'/)[1]
        }
        input = {
            jx: 0,
            url: url,
            parse: 0
        }
    `,
    搜索: '.myui-vodlist__media.clearfix li;a&&title;.lazyload&&data-original;.pic-text&&Text;a&&href;.text-muted:eq(-1)&&Text',
}