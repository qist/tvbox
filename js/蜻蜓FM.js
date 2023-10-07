var rule = {
    title:'蜻蜓FM',
    host:'http://www.qingting.fm',
    url:'/radiopage/fyclass/fypage',
    searchUrl:'',
    searchable:0,
    quickSearch:0,
    class_name:'广东&浙江&北京&天津&河北&上海&山西&内蒙古&辽宁&吉林&黑龙江&江苏&安徽&福建&江西&山东&河南&湖北&湖南&广西&海南&重庆&四川&贵州&云南&陕西&甘肃&宁夏&新疆&西藏&青海&资讯&音乐&交通&经济&文艺&都市&体育&双语&综合&生活&旅游&曲艺&方言',
    class_url:'217&99&3&5&7&83&19&31&44&59&69&85&111&129&139&151&169&187&202&239&254&257&259&281&291&316&327&351&357&308&342&433&442&429&439&432&441&430&431&440&438&435&436&434',
    headers:{
        'User-Agent':'PC_UA'
    },
    timeout:5000,
    play_parse:true,
    play_json:0,
    lazy:'js:input=input.replace("www.qingting.fm/radios/","lhttp.qingting.fm/live/")+"/64k.mp3"',
    limit:6,
    double:false,
    //推荐:'*',
    一级:'.contentSec&&.radio;span&&Text;img&&src;.descRadio&&Text;a&&href',
    二级:'*',
    搜索:'',

    //是否启用辅助嗅探: 1,0
    sniffer:1,
    // 辅助嗅探规则
    isVideo:"http((?!http).){26,}\\.(m3u8|mp4|flv|avi|mkv|wmv|mpg|mpeg|mov|ts|3gp|rm|rmvb|asf|m4a|mp3|wma)",
}