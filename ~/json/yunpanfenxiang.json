//写法思路来自biubiu影院，海阔视界，xpath筛选。2022年9月22日
//项目魔改至github开源仓库https://github.com/Tangsan99999/TvJar中的XBiubiu.java文件，
//本文档为完整模板，实际情况可按规则写法删去不需要的。
{
    //规则名
    "title": "云盘分享",
    //作者
    "author": "聆听优美旋律",
    
    //搜索专属请求头UA,不填则默认okhttp/3.12.11，可填MOBILE_UA或PC_UA使用内置的手机版或电脑版UA
    //多个请求头参数写法示例，"User-Agent$PC_UA#Referer$http://ww.baidu.com#Cookie$ser=ok",
    //习惯查看手机源码写建议用手机版UA，习惯查看PC版源码写建议用电脑版UA
    "SUserAgent":"PC_UA",
    //搜索链接，搜索关键字用{wd}表示，post请求的最后面加;post
    //POST链接示例 http://www.lezhutv.com/index.php?m=vod-search;post
    "search_url": "https://www.yunpanfenxiang.cn/api/bbs/api/getdata2?key={wd}",
    //POST搜索body，填写搜索关键字的键值，一般常见的是searchword和wd，不是POST搜索的可留空或删除。
    "sea_PtBody":"",
    
    //搜索模式,0为json搜索，只支持列表在list数组里的，其它为网页截取。
    "search_mode": "1",
    
    //搜索是否二次截取  
    "sea_YN_twice": "0",
    //搜索二次截取前
    "sea_twice_pre": "空",
    //搜索二次截取后
    "sea_twice_suf": "</ul>",
    
    //搜索数组前缀
    "sea_arr_pre": "page_",
    //搜索数组后缀
    "sea_arr_suf": "content",
    //搜索片单图片，截取前缀&&截取后缀
    "sea_pic": "https://inews.gtimg.com/newsapp_bt/0/13263837859/1000",
    //搜索片单标题，截取前缀&&截取后缀
    "sea_title": "title\":\"&&\"",
    //搜索片单链接，截取前缀&&截取后缀
    "sea_url": "url\":\"&&\"",
    //搜索副标题，截取前缀&&截取后缀
    "sea_subtitle": "",
    
    //搜索片单链接补前缀
    "search_prefix": "",
    //搜索片单链接补后缀，这个一般json搜索的需要
    "search_suffix": ""
    
    
}