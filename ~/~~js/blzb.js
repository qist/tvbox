/* 直播弹幕 -> vod_area:'bililivedanmu'
目前只有皮皮虾大佬的DMBox, 支持弹幕
DMBox下载:https://t.me/pipixiawerun
设置 > 窗口预览 > 开启
*/

/* Cookie设置
Cookie获取方法 https://github.com/UndCover/PyramidStore/blob/main/list.md#%E6%B3%A8%E6%84%8F%E4%BA%8B%E9%A1%B9

Cookie设置方法1: DR-PY 后台管理界面
CMS后台管理 > 设置中心 > 环境变量 > {"bili_cookie":"XXXXXXX","vmid":"XXXXXX"} > 保存

Cookie设置方法2: 手动替换Cookie
底下代码 headers的
"Cookie":"$bili_cookie"
手动替换为
"Cookie":"将获取的Cookie黏贴在这"
*/

var rule = {
    title:'哔哩直播',
    host:'https://api.live.bilibili.com',
    homeUrl:'/xlive/web-interface/v1/second/getUserRecommend?page=1&page_size=30&platform=web',//用于"分类获取"和"推荐获取"
    url:'/xlive/web-interface/v1/second/getList?platform=web&parent_area_id=fyclass&area_id=fyfilter&sort_type=online&page=fypage',
    class_name:'娱乐&网游&手游&单机游戏&电台&虚拟主播&生活&知识&赛事&购物',
    class_url:'10&2&3&6&1&5&9&11&13&300',
    filterable: 1,
    filter_url: '{{fl.area}}',
    filter_def:{
        10:{area:'33'},
        2:{area:'86'},
        3:{area:'35'},
        6:{area:'236'},
        1:{area:'21'},
        5:{area:'190'},
        9:{area:'371'},
        11:{area:'376'},
        13:{area:'561'},
        300:{area:'30000'}
    },
    filter: {
        "2":[{"key":"area","name":"分区","value":[{"n":"英雄联盟","v":"86"},{"n":"DOTA2","v":"92"},{"n":"CS:GO","v":"89"},{"n":"APEX英雄","v":"240"},{"n":"永劫无间","v":"666"},{"n":"穿越火线","v":"88"},{"n":"守望先锋","v":"87"},{"n":"吃鸡行动","v":"80"},{"n":"逃离塔科夫","v":"252"},{"n":"传奇","v":"695"},{"n":"DNF","v":"78"},{"n":"生死狙击2","v":"575"},{"n":"洛奇英雄传","v":"599"},{"n":"最终幻想14","v":"102"},{"n":"星际战甲","v":"249"},{"n":"梦三国","v":"710"},{"n":"英魂之刃","v":"690"},{"n":"剑网3","v":"82"},{"n":"铁甲雄兵","v":"691"},{"n":"封印者","v":"300"},{"n":"新天龙八部","v":"653"},{"n":"赛尔号","v":"667"},{"n":"造梦西游","v":"668"},{"n":"洛克王国","v":"669"},{"n":"问道","v":"670"},{"n":"诛仙世界","v":"654"},{"n":"大话西游","v":"652"},{"n":"奇迹MU","v":"683"},{"n":"永恒之塔","v":"684"},{"n":"QQ三国","v":"685"},{"n":"人间地狱","v":"677"},{"n":"VALORANT","v":"329"},{"n":"彩虹岛","v":"686"},{"n":"洛奇","v":"663"},{"n":"跑跑卡丁车","v":"664"},{"n":"星际公民","v":"658"},{"n":"Squad战术小队","v":"659"},{"n":"反恐精英Online","v":"629"},{"n":"风暴奇侠","v":"648"},{"n":"装甲战争","v":"642"},{"n":"失落的方舟","v":"590"},{"n":"阿尔比恩","v":"639"},{"n":"猎杀对决","v":"600"},{"n":"CFHD ","v":"472"},{"n":"骑士精神2","v":"650"},{"n":"超击突破","v":"680"},{"n":"武装突袭","v":"634"},{"n":"300英雄","v":"84"},{"n":"炉石传说","v":"91"},{"n":"剑网3缘起","v":"499"},{"n":"街头篮球","v":"649"},{"n":"综合射击","v":"601"},{"n":"剑灵","v":"505"},{"n":"艾尔之光","v":"651"},{"n":"黑色沙漠","v":"632"},{"n":"天涯明月刀","v":"596"},{"n":"超激斗梦境","v":"519"},{"n":"冒险岛","v":"574"},{"n":"逆战","v":"487"},{"n":"魔兽争霸3","v":"181"},{"n":"QQ飞车","v":"610"},{"n":"魔兽世界","v":"83"},{"n":"FIFA ONLINE 4","v":"388"},{"n":"NBA2KOL2","v":"581"},{"n":"使命召唤:战区","v":"318"},{"n":"VRChat","v":"656"},{"n":"坦克世界","v":"115"},{"n":"战舰世界","v":"248"},{"n":"战争雷霆","v":"316"},{"n":"战意","v":"383"},{"n":"风暴英雄","v":"114"},{"n":"星际争霸2","v":"93"},{"n":"刀塔自走棋","v":"239"},{"n":"堡垒之夜","v":"164"},{"n":"枪神纪","v":"251"},{"n":"三国杀","v":"81"},{"n":"龙之谷","v":"112"},{"n":"古剑奇谭OL","v":"173"},{"n":"幻想全明星","v":"176"},{"n":"怀旧网游","v":"288"},{"n":"新游前瞻","v":"298"},{"n":"星战前夜：晨曦","v":"331"},{"n":"梦幻西游端游","v":"350"},{"n":"流放之路","v":"551"},{"n":"FPS沙盒","v":"633"},{"n":"永恒轮回","v":"459"},{"n":"激战2","v":"607"},{"n":"其他网游","v":"107"}] }],
        "3":[{"key":"area","name":"分区","value":[{"n":"王者荣耀","v":"35"},{"n":"和平精英","v":"256"},{"n":"LOL手游","v":"395"},{"n":"原神","v":"321"},{"n":"第五人格","v":"163"},{"n":"明日方舟","v":"255"},{"n":"哈利波特：魔法觉醒 ","v":"474"},{"n":"幻塔","v":"550"},{"n":"金铲铲之战","v":"514"},{"n":"APEX手游","v":"506"},{"n":"深空之眼","v":"598"},{"n":"无期迷途","v":"675"},{"n":"光遇","v":"687"},{"n":"跃迁旅人","v":"717"},{"n":"香肠派对","v":"689"},{"n":"猫之城","v":"645"},{"n":"玛娜希斯回响","v":"644"},{"n":"使命召唤手游","v":"386"},{"n":"黑色沙漠手游","v":"615"},{"n":"崩坏3","v":"40"},{"n":"游戏王：决斗链接","v":"407"},{"n":"游戏王","v":"303"},{"n":"蛋仔派对","v":"571"},{"n":"阴阳师","v":"36"},{"n":"空之要塞：启航","v":"718"},{"n":"火影忍者手游","v":"292"},{"n":"Fate/GO","v":"37"},{"n":"综合棋牌","v":"354"},{"n":"QQ飞车手游","v":"154"},{"n":"决战！平安京","v":"140"},{"n":"狼人杀","v":"41"},{"n":"三国杀移动版","v":"352"},{"n":"碧蓝航线","v":"113"},{"n":"影之诗","v":"156"},{"n":"明日之后","v":"189"},{"n":"部落冲突:皇室战争","v":"50"},{"n":"奥比岛手游","v":"661"},{"n":"盾之勇者成名录：浪潮","v":"704"},{"n":"雀姬","v":"214"},{"n":"公主连结Re:Dive","v":"330"},{"n":"DNF手游","v":"343"},{"n":"FIFA足球世界","v":"641"},{"n":"BanG Dream","v":"258"},{"n":"荒野乱斗","v":"469"},{"n":"CF手游","v":"333"},{"n":"战双帕弥什","v":"293"},{"n":"天涯明月刀手游","v":"389"},{"n":"解密游戏","v":"42"},{"n":"恋爱养成游戏","v":"576"},{"n":"暗黑破坏神：不朽","v":"492"},{"n":"暗区突围","v":"502"},{"n":"跑跑卡丁车手游","v":"265"},{"n":"非人学园","v":"212"},{"n":"百闻牌","v":"286"},{"n":"猫和老鼠手游","v":"269"},{"n":"坎公骑冠剑","v":"442"},{"n":"忍者必须死3","v":"203"},{"n":"梦幻西游手游","v":"342"},{"n":"航海王热血航线","v":"504"},{"n":"少女前线","v":"39"},{"n":"300大作战","v":"688"},{"n":"少女前线：云图计划","v":"525"},{"n":"漫威超级战争","v":"478"},{"n":"摩尔庄园手游","v":"464"},{"n":"宝可梦大集结","v":"493"},{"n":"小动物之星","v":"473"},{"n":"天地劫：幽城再临","v":"448"},{"n":"漫威对决","v":"511"},{"n":" 东方归言录","v":"538"},{"n":"梦幻模拟战","v":"178"},{"n":"时空猎人3","v":"643"},{"n":"重返帝国","v":"613"},{"n":"休闲小游戏","v":"679"},{"n":"其他手游","v":"98"},{"n":"新游评测","v":"274"}] }],
        "6":[{"key":"area","name":"分区","value":[{"n":"主机游戏","v":"236"},{"n":"我的世界","v":"216"},{"n":"独立游戏","v":"283"},{"n":"怀旧游戏","v":"237"},{"n":"弹幕互动玩法","v":"460"},{"n":"恐怖游戏","v":"276"},{"n":"禁闭求生","v":"707"},{"n":"斯普拉遁3","v":"694"},{"n":"卧龙：苍天陨落","v":"700"},{"n":"使命召唤19","v":"282"},{"n":"异度神剑","v":"665"},{"n":"艾尔登法环","v":"555"},{"n":"聚会游戏","v":"636"},{"n":"哥谭骑士","v":"716"},{"n":"命运2","v":"277"},{"n":"沙石镇时光","v":"630"},{"n":"Dread Hunger","v":"591"},{"n":"红色警戒2","v":"693"},{"n":"失落迷城：群星的诅咒","v":"714"},{"n":"策略游戏","v":"570"},{"n":"战地风云","v":"597"},{"n":"幽灵线：东京","v":"612"},{"n":"糖豆人","v":"357"},{"n":"消逝的光芒2","v":"586"},{"n":"只狼","v":"245"},{"n":"怪物猎人","v":"578"},{"n":"饥荒","v":"218"},{"n":"精灵宝可梦","v":"228"},{"n":"FIFA23","v":"708"},{"n":"暖雪","v":"582"},{"n":"全面战争：战锤3","v":"594"},{"n":"彩虹六号：异种","v":"580"},{"n":"战神","v":"579"},{"n":"FORZA 极限竞速","v":"302"},{"n":"NBA2K","v":"362"},{"n":"帝国时代4","v":"548"},{"n":"光环：无限","v":"559"},{"n":"孤岛惊魂6","v":"537"},{"n":"植物大战僵尸","v":"309"},{"n":"仙剑奇侠传七","v":"540"},{"n":"灵魂筹码","v":"223"},{"n":"格斗游戏","v":"433"},{"n":"荒野大镖客2","v":"226"},{"n":"重生细胞","v":"426"},{"n":"刺客信条","v":"227"},{"n":"恐鬼症","v":"387"},{"n":"以撒","v":"219"},{"n":"双人成行","v":"446"},{"n":"方舟","v":"295"},{"n":"仁王2","v":"313"},{"n":"鬼泣5","v":"244"},{"n":"枪火重生","v":"364"},{"n":"盗贼之海","v":"341"},{"n":"胡闹厨房","v":"507"},{"n":"体育游戏","v":"500"},{"n":"恐惧之间","v":"439"},{"n":"塞尔达","v":"308"},{"n":"马力欧制造2","v":"261"},{"n":"全境封锁2","v":"243"},{"n":"骑马与砍杀","v":"326"},{"n":"人类一败涂地","v":"270"},{"n":"鬼谷八荒","v":"424"},{"n":"无主之地3","v":"273"},{"n":"辐射76","v":"220"},{"n":"全面战争","v":"257"},{"n":"亿万僵尸","v":"463"},{"n":"暗黑破坏神2","v":"535"},{"n":"文字游戏","v":"583"},{"n":"恋爱模拟游戏","v":"592"},{"n":"泰拉瑞亚","v":"593"},{"n":"雨中冒险2","v":"441"},{"n":"游戏速通","v":"678"},{"n":"摔角城大乱斗","v":"681"},{"n":"勇敢的哈克","v":"692"},{"n":" 审判系列","v":"698"},{"n":"其他单机","v":"235"}] }],
        "1":[{"key":"area","name":"分区","value":[{"n":"视频唱见","v":"21"},{"n":"萌宅领域","v":"530"},{"n":"视频聊天","v":"145"},{"n":"舞见","v":"207"},{"n":"情感","v":"706"},{"n":"户外","v":"123"},{"n":"日常","v":"399"}] }],
        "5":[{"key":"area","name":"分区","value":[{"n":"唱见电台","v":"190"},{"n":"聊天电台","v":"192"},{"n":"配音","v":"193"}] }],
        "9":[{"key":"area","name":"分区","value":[{"n":"虚拟主播","v":"371"},{"n":"3D虚拟主播","v":"697"}] }],
        "10":[{"key":"area","name":"分区","value":[{"n":"生活分享","v":"646"},{"n":"运动","v":"628"},{"n":"搞笑","v":"624"},{"n":"手工绘画","v":"627"},{"n":"萌宠","v":"369"},{"n":"美食","v":"367"},{"n":"时尚","v":"378"},{"n":"影音馆","v":"33"}] }],
        "11":[{"key":"area","name":"分区","value":[{"n":"社科法律心理","v":"376"},{"n":"人文历史","v":"702"},{"n":"校园学习","v":"372"},{"n":"职场·技能","v":"377"},{"n":" 科技","v":"375"},{"n":"科学科普","v":"701"},{"n":"时政","v":"715"}] }],
        "13":[{"key":"area","name":"分区","value":[{"n":"游戏赛事","v":"561"},{"n":"体育赛事","v":"562"},{"n":"赛事综合","v":"563"}] }],
        "300":[{"key":"area","name":"分区","value":[{"n":"购物","v":"300000"}] }]
    },
    detailUrl:'https://live.bilibili.com/fyid',//二级详情拼接链接(json格式用)
    // detailUrl:'https://api.live.bilibili.com/xlive/web-room/v1/playUrl/playUrl?cid=fyid&platform=h5&otype=json&quality=0',//二级详情拼接链接(json格式用)
    // searchUrl:'/x/web-interface/search/type?__refresh__=true&page=fypage&page_size=42&order=online&platform=pc&highlight=1&single_column=0&keyword=**&search_type=live&dynamic_offset=0&preload=true',
    searchUrl:'https://api.bilibili.com/x/web-interface/search/type?search_type=live&keyword=**&page=1',
    searchable:2,
    quickSearch:0,
    headers:{
        "User-Agent":"PC_UA",
        "Referer": "https://www.bilibili.com",
        "Cookie":"$bili_cookie"
    },
    timeout:5000,
    limit:8,
    play_parse:true,
    // play_json:[{re:'*', json:{jx:0, parse:1,header:JSON.stringify({"user-agent":"Mozilla/5.0 (Linux; U; Android 9; zh-CN; MI 9 Build/PKQ1.181121.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/12.5.5.1035 Mobile Safari/537.36"})}}],
    // play_json:[{re:'*', json:{jx:0, parse:1,header:JSON.stringify({"user-agent":"uc_ua"})}}],
    // play_json:0,
    lazy:"js:let ids=input.split('_');let result={};let iurl='https://api.live.bilibili.com/room/v1/Room/playUrl?cid='+ids[1]+'&'+ids[0];let html=request(iurl);let jRoot=JSON.parse(html);let jo=jRoot['data'];let ja=jo['durl'];let purl='';if(ja.length>0){purl=ja[0]['url']}result['parse']=0;result['playUrl']='';result['url']=unescape(purl);result['header']={Referer:'https://live.bilibili.com','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'};if(/h5/.test(ids[0])){result['contentType']='';input=result}else{result['contentType']='video/x-flv';input=result}",
    double:false,
    推荐:'*',
    一级:'json:data.list;title;system_cover;uname;roomid',
    // 二级:'*',
    二级:"js:let aid=input.match(/\\/(\\d+)/)[1];log(aid);let html=request('https://api.live.bilibili.com/room/v1/Room/get_info?room_id='+aid);let jo=JSON.parse(html).data;let title=jo['title'];let pic=jo['keyframe'];let desc=jo['description'];let dire=jo['uid'];let typeName=jo['area_name'];let remark='在线人数:'+jo['online'];let vod={vod_id:aid,vod_name:title,vod_pic:pic,type_name:typeName,vod_area:'bililivedanmu',vod_remarks:remark,vod_actor:'直播间id-'+aid,vod_director:dire,vod_content:desc};vod['vod_play_from']='B站';vod['vod_play_url']='flv线路原画$platform=web&quality=4_'+aid+'#flv线路高清$platform=web&quality=3_'+aid+'#h5线路原画$platform=h5&quality=4_'+aid+'#h5线路高清$platform=h5&quality=3_'+aid;VOD=vod;",
    // 搜索:'json:data.result.live_room;title;cover;uname;roomid',
    搜索:'js:let html=request(input);let msg=JSON.parse(html).message;if(msg!=="0"){VODS=[{vod_name:KEY+"➢"+msg,vod_id:"no_data",vod_remarks:"别点,缺少bili_cookie",vod_pic:"https://ghproxy.com/https://raw.githubusercontent.com/hjdhnx/dr_py/main/404.jpg"}]}else{let videos=[];let vodList=JSON.parse(html).data.result.live_room;vodList.forEach(function(vod){let aid=vod["roomid"];let title="直播间："+vod["title"].replace(\'<em class="keyword">\',"").replace("</em>","");let img="https:"+vod["user_cover"];let remark=vod["watched_show"]["text_small"]+"  "+vod["uname"];videos.push({vod_id:aid,vod_name:title,vod_pic:img,vod_remarks:remark})});VODS=videos}',
}