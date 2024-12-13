
var rule = {
    title:'有声小说吧',
    编码:'gb18030',
    host:'http://m.ysxs8.vip',
    url:'/downlist/fyclass_fypage.html',
    searchUrl:'/search.asp?page=fypage&searchword=**&searchtype=-1',
    searchable:2,
    quickSearch:0,
    headers:{
        'User-Agent':'MOBILE_UA'
    },
    timeout:5000,
    // homeUrl:'/fenlei/',
    // class_parse: '.pd-class:eq(0) dd;a&&Text;a&&href;.*/(.*?).html',
    class_name:'网络玄幻&恐怖悬疑&传统武侠&都市言情&官场刑侦&历史军事&探险盗墓&职场商战&明朝那些事儿&评书下载&相声戏曲&人物传记&广播剧&百家讲坛&外语读物&有声文学&儿童读物&管理营销',
    class_url:'r52&r17&r12&r13&r14&r15&r45&r81&r36&r3&r7&r16&r18&r32&r35&r41&r4&r6',
    play_parse:true,
    lazy:'',
    limit:6,
    // double:true,
    推荐:'.list-ul .list-li;.list-name&&Text;*;.module-slide-author&&Text;*',
    一级:'.book-ol&&li;h4&&Text;img&&data-original;.book-meta&&Text;a&&href',
    二级:{
    	// title:'h2&&Text;.book-cell .book-rand-a:eq(2)&&Text',
        title:'h1&&Text;.book-cell .book-rand-a:eq(0)&&a&&Text',
    	img:'.book img&&src',
    	// desc:';;;;.book-des p&&Text',
        desc:';;;.book-rand-a:eq(2)&&Text;.book-des p&&Text',
    	content:'.book-des--p&&Text',
	    tabs:'.playlist-top&&h2',
    	// lists:'js:pd=jsp.pd;let url=pd(html,".bookbutton&&a&&href");log(url);html=request(url);let v=pd(html,".booksite&&script&&Html");var document={};var VideoListJson;VideoListJson=eval(v.split("VideoListJson=")[1].split(",urlinfo")[0]);log(typeof VideoListJson);let list1=VideoListJson[0][1];LISTS=[list1];log(LISTS);',
   		// 有声小说有防盗链,我服了(上面的列表数据正常拿到了,没法播放)
   		//  lists:'#playlist:eq(#id)&&ul&&li',
    	lists:'#playlist ul li',
    },
    搜索:'*',
}