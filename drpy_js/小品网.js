var rule = {
    title:'小品网',
    host:'http://www.xiaopin.tv',
    url:'/?cate=fyclass&page=fypage',
    searchUrl:'/search.php?q=**',
    searchable:2,
    quickSearch:0,
    filterable:0,
    headers:{
        'User-Agent':'MOBILE_UA'
    },
    timeout:5000,
    class_name:'小品&相声&二人转&春晚小品',
    class_url:'2&1&3&14',
    play_parse:true,
    lazy:'',
    limit:6,
    double:true,
    推荐:'.itemlist;ul&&li;.itemname&&a&&Text;.itemimg img&&src;*;*',
    一级:'.catecon&&ul&&li;.catename&&a&&Text;img&&src;.icoplay&&Text;a&&href',
    二级:'*',
    搜索:'*',
}