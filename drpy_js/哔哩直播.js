/**
 * 影视TV 弹幕支持 
    * https://t.me/fongmi_offical/
    * https://github.com/FongMi/Release/tree/main/apk
 * 皮皮虾DMBox 弹幕支持
    * 设置 > 窗口预览 > 开启
    * https://t.me/pipixiawerun
    * vod_area:'bililivedanmu'
 * Cookie设置
    * Cookie获取方法 https://ghproxy.net/https://raw.githubusercontent.com/UndCover/PyramidStore/main/list.md
 * Cookie设置方法1: DR-PY 后台管理界面
    * CMS后台管理 > 设置中心 > 环境变量 > {"bili_cookie":"XXXXXXX","vmid":"XXXXXX"} > 保存
 * Cookie设置方法2: 手动替换Cookie
    * 底下代码 headers的
    * "Cookie":"$bili_cookie"
    * 手动替换为
    * "Cookie":"将获取的Cookie黏贴在这"
 */

var rule = {
    title:'哔哩直播',
    host:'https://api.live.bilibili.com',
    homeUrl:'/xlive/web-interface/v1/second/getUserRecommend?page=1&page_size=30&platform=web',//用于"分类获取"和"推荐获取"
    url:'/xlive/web-interface/v1/second/getList?platform=web&parent_area_id=fyclass&area_id=fyfilter&sort_type=online&page=fypage',
    class_name:'生活&网游&手游&单机游戏&娱乐&电台&虚拟主播&聊天室&知识&赛事&帮我玩&互动玩法',
    class_url:'10&2&3&6&1&5&9&14&11&13&301&15',
    filterable: 1,
    filter_url: '{{fl.area}}',
    filter_def:{
        10:{area:'624'},
        2:{area:'86'},
        3:{area:'35'},
        6:{area:'236'},
        1:{area:'21'},
        5:{area:'190'},
        9:{area:'744'},
        14:{area:'818'},
        11:{area:'376'},
        13:{area:'562'},
        301:{area:'301000'},
        15:{area:'814'}
    },
    filter: {
        "10":[{"key":"area","name":"分区","value":[{"n":"生活分享","v":"646"},{"n":"聊天交友","v":"825"},{"n":"手工绘画","v":"627"},{"n":"情感","v":"623"},{"n":"户外","v":"368"},{"n":"萌宠","v":"369"},{"n":"运动","v":"628"},{"n":"美食","v":"367"},{"n":"时尚","v":"378"},{"n":"电子榨菜","v":"624"},{"n":"沉浸体验","v":"827"}]}],
        "2":[{"key":"area","name":"分区","value":[{"n":"英雄联盟","v":"86"},{"n":"无畏契约","v":"329"},{"n":"CS:GO","v":"89"},{"n":"APEX英雄","v":"240"},{"n":"永劫无间","v":"666"},{"n":"穿越火线","v":"88"},{"n":"命运方舟","v":"590"},{"n":"DOTA2","v":"92"},{"n":"吃鸡行动","v":"80"},{"n":"逃离塔科夫","v":"252"},{"n":"传奇","v":"695"},{"n":"DNF","v":"78"},{"n":"卡拉彼丘","v":"782"},{"n":"幕后高手","v":"774"},{"n":"生死狙击2","v":"575"},{"n":"洛奇英雄传","v":"599"},{"n":"最终幻想14","v":"102"},{"n":"重生边缘","v":"809"},{"n":"星际战甲","v":"249"},{"n":"梦三国","v":"710"},{"n":"英魂之刃","v":"690"},{"n":"剑网3","v":"82"},{"n":"从军","v":"829"},{"n":"铁甲雄兵","v":"691"},{"n":"封印者","v":"300"},{"n":"新天龙八部","v":"653"},{"n":"赛尔号","v":"667"},{"n":"造梦西游","v":"668"},{"n":"洛克王国","v":"669"},{"n":"问道","v":"670"},{"n":"诛仙世界","v":"654"},{"n":"大话西游","v":"652"},{"n":"奇迹MU","v":"683"},{"n":"永恒之塔","v":"684"},{"n":"QQ三国","v":"685"},{"n":"人间地狱","v":"677"},{"n":"彩虹岛","v":"686"},{"n":"洛奇","v":"663"},{"n":"跑跑卡丁车","v":"664"},{"n":"星际公民","v":"658"},{"n":"Squad战术小队","v":"659"},{"n":"反恐精英Online","v":"629"},{"n":"风暴奇侠","v":"648"},{"n":"创世战车","v":"705"},{"n":"装甲战争","v":"642"},{"n":"守望先锋","v":"87"},{"n":"阿尔比恩","v":"639"},{"n":"猎杀对决","v":"600"},{"n":"CFHD","v":"472"},{"n":"骑士精神2","v":"650"},{"n":"超击突破","v":"680"},{"n":"武装突袭","v":"634"},{"n":"Wayfinder寻路者","v":"773"},{"n":"300英雄","v":"84"},{"n":"炉石传说","v":"91"},{"n":"剑网3缘起","v":"499"},{"n":"街头篮球","v":"649"},{"n":"综合射击","v":"601"},{"n":"剑灵","v":"505"},{"n":"艾尔之光","v":"651"},{"n":"黑色沙漠","v":"632"},{"n":"天涯明月刀","v":"596"},{"n":"超激斗梦境","v":"519"},{"n":"冒险岛","v":"574"},{"n":"逆战","v":"487"},{"n":"魔兽争霸3","v":"181"},{"n":"QQ飞车","v":"610"},{"n":"魔兽世界","v":"83"},{"n":"FIFAONLINE4","v":"388"},{"n":"NBA2KOL2","v":"581"},{"n":"使命召唤:战区","v":"318"},{"n":"VRChat","v":"656"},{"n":"坦克世界","v":"115"},{"n":"战舰世界","v":"248"},{"n":"战争与抉择","v":"729"},{"n":"战争雷霆","v":"316"},{"n":"战意","v":"383"},{"n":"风暴英雄","v":"114"},{"n":"星际争霸2","v":"93"},{"n":"刀塔自走棋","v":"239"},{"n":"堡垒之夜","v":"164"},{"n":"枪神纪","v":"251"},{"n":"三国杀","v":"81"},{"n":"龙之谷","v":"112"},{"n":"古剑奇谭OL","v":"173"},{"n":"幻想全明星","v":"176"},{"n":"怀旧网游","v":"288"},{"n":"新游前瞻","v":"298"},{"n":"星战前夜：晨曦","v":"331"},{"n":"流放之路","v":"551"},{"n":"FPS沙盒","v":"633"},{"n":"永恒轮回","v":"459"},{"n":"激战2","v":"607"},{"n":"其他网游","v":"107"},{"n":"蓝色协议","v":"760"}]}],
        "3":[{"key":"area","name":"分区","value":[{"n":"王者荣耀","v":"35"},{"n":"和平精英","v":"256"},{"n":"原神","v":"321"},{"n":"崩坏：星穹铁道","v":"549"},{"n":"第五人格","v":"163"},{"n":"LOL手游","v":"395"},{"n":"明日方舟","v":"255"},{"n":"黎明觉醒：生机","v":"479"},{"n":"蛋仔派对","v":"571"},{"n":"冒险岛手游","v":"796"},{"n":"元梦之星","v":"822"},{"n":"闪耀！优俊少女","v":"805"},{"n":"斯露德","v":"797"},{"n":"千年之旅","v":"806"},{"n":"白夜极光","v":"781"},{"n":"逆水寒手游","v":"771"},{"n":"率土之滨","v":"807"},{"n":"月圆之夜","v":"215"},{"n":"哈利波特：魔法觉醒","v":"474"},{"n":"七人传奇","v":"823"},{"n":"幻塔","v":"550"},{"n":"星之破晓","v":"799"},{"n":"金铲铲之战","v":"514"},{"n":"少女前线2：追放","v":"832"},{"n":"深空之眼","v":"598"},{"n":"无期迷途","v":"675"},{"n":"晶核","v":"777"},{"n":"星球重启","v":"828"},{"n":"宿命回响：弦上的叹息","v":"826"},{"n":"光遇","v":"687"},{"n":"桃源深处有人家","v":"792"},{"n":"三国志战棋版","v":"756"},{"n":"战火勋章","v":"765"},{"n":"以闪亮之名","v":"755"},{"n":"尘白禁区","v":"778"},{"n":"古魂","v":"759"},{"n":"鬼泣-巅峰之战","v":"470"},{"n":"奇点时代","v":"762"},{"n":"香肠派对","v":"689"},{"n":"猫之城","v":"645"},{"n":"高能英雄","v":"783"},{"n":"使命召唤手游","v":"386"},{"n":"崩坏3","v":"40"},{"n":"银河境界线","v":"793"},{"n":"蔚蓝档案","v":"787"},{"n":"第七史诗","v":"784"},{"n":"游戏王：决斗链接","v":"407"},{"n":"游戏王","v":"303"},{"n":"JJ斗地主","v":"724"},{"n":"阴阳师","v":"36"},{"n":"欢乐斗地主","v":"719"},{"n":"太空行动","v":"791"},{"n":"空之要塞：启航","v":"718"},{"n":"长安幻想","v":"738"},{"n":"火影忍者手游","v":"292"},{"n":"Fate/GO","v":"37"},{"n":"综合棋牌","v":"354"},{"n":"QQ飞车手游","v":"154"},{"n":"决战！平安京","v":"140"},{"n":"狼人杀","v":"41"},{"n":"三国杀移动版","v":"352"},{"n":"碧蓝航线","v":"113"},{"n":"影之诗","v":"156"},{"n":"明日之后","v":"189"},{"n":"重返未来：1999","v":"761"},{"n":"环行旅舍","v":"786"},{"n":"幻世与冒险","v":"813"},{"n":"部落冲突:皇室战争","v":"50"},{"n":"奥比岛手游","v":"661"},{"n":"弹弹堂","v":"734"},{"n":"雀姬","v":"214"},{"n":"公主连结Re:Dive","v":"330"},{"n":"DNF手游","v":"343"},{"n":"FIFA足球世界","v":"641"},{"n":"BanGDream","v":"258"},{"n":"荒野乱斗","v":"469"},{"n":"CF手游","v":"333"},{"n":"战双帕弥什","v":"293"},{"n":"天涯明月刀手游","v":"389"},{"n":"一拳超人：世界","v":"779"},{"n":"解密游戏","v":"42"},{"n":"恋爱养成游戏","v":"576"},{"n":"暗黑破坏神：不朽","v":"492"},{"n":"暗区突围","v":"502"},{"n":"跑跑卡丁车手游","v":"265"},{"n":"非人学园","v":"212"},{"n":"百闻牌","v":"286"},{"n":"猫和老鼠手游","v":"269"},{"n":"坎公骑冠剑","v":"442"},{"n":"忍者必须死3","v":"203"},{"n":"梦幻西游手游","v":"342"},{"n":"航海王热血航线","v":"504"},{"n":"少女前线","v":"39"},{"n":"300大作战","v":"688"},{"n":"少女前线：云图计划","v":"525"},{"n":"漫威超级战争","v":"478"},{"n":"摩尔庄园手游","v":"464"},{"n":"宝可梦大集结","v":"493"},{"n":"小动物之星","v":"473"},{"n":"天地劫：幽城再临","v":"448"},{"n":"漫威对决","v":"511"},{"n":"东方归言录","v":"538"},{"n":"梦幻模拟战","v":"178"},{"n":"时空猎人3","v":"643"},{"n":"重返帝国","v":"613"},{"n":"休闲小游戏","v":"679"},{"n":"其他手游","v":"98"},{"n":"新游评测","v":"274"},{"n":"山海镜花","v":"821"},{"n":"小冰冰传奇","v":"824"}]}],
        "6":[{"key":"area","name":"分区","value":[{"n":"主机游戏","v":"236"},{"n":"我的世界","v":"216"},{"n":"独立游戏","v":"283"},{"n":"怀旧游戏","v":"237"},{"n":"猛兽派对","v":"384"},{"n":"赛博朋克2077","v":"402"},{"n":"星空","v":"808"},{"n":"塞尔达传说","v":"308"},{"n":"苍翼：混沌效应","v":"798"},{"n":"命运2","v":"277"},{"n":"收获日3","v":"811"},{"n":"FC24","v":"830"},{"n":"机战佣兵VI境界天火","v":"800"},{"n":"暗黑破坏神Ⅳ","v":"780"},{"n":"匹诺曹的谎言","v":"812"},{"n":"博德之门3","v":"385"},{"n":"绝世好武功","v":"801"},{"n":"恐怖游戏","v":"276"},{"n":"DarkandDarker","v":"795"},{"n":"Warlander","v":"785"},{"n":"FORZA极限竞速","v":"302"},{"n":"边境","v":"763"},{"n":"生化危机","v":"721"},{"n":"最终幻想","v":"328"},{"n":"暗黑破坏神","v":"535"},{"n":"森林之子","v":"751"},{"n":"卧龙：苍天陨落","v":"700"},{"n":"红色警戒2","v":"693"},{"n":"策略游戏","v":"570"},{"n":"禁闭求生","v":"707"},{"n":"战神","v":"579"},{"n":"斯普拉遁3","v":"694"},{"n":"使命召唤19","v":"282"},{"n":"艾尔登法环","v":"555"},{"n":"聚会游戏","v":"636"},{"n":"DreadHunger","v":"591"},{"n":"战地风云","v":"597"},{"n":"糖豆人","v":"357"},{"n":"消逝的光芒2","v":"586"},{"n":"只狼","v":"245"},{"n":"怪物猎人","v":"578"},{"n":"宝可梦集换式卡牌游戏","v":"720"},{"n":"饥荒","v":"218"},{"n":"精灵宝可梦","v":"228"},{"n":"FIFA23","v":"708"},{"n":"全面战争：战锤3","v":"594"},{"n":"NBA2K","v":"362"},{"n":"帝国时代4","v":"548"},{"n":"植物大战僵尸","v":"309"},{"n":"格斗游戏","v":"433"},{"n":"荒野大镖客2","v":"226"},{"n":"重生细胞","v":"426"},{"n":"刺客信条","v":"227"},{"n":"恐鬼症","v":"387"},{"n":"以撒","v":"219"},{"n":"双人成行","v":"446"},{"n":"方舟","v":"295"},{"n":"仁王2","v":"313"},{"n":"鬼泣5","v":"244"},{"n":"枪火重生","v":"364"},{"n":"盗贼之海","v":"341"},{"n":"胡闹厨房","v":"507"},{"n":"体育游戏","v":"500"},{"n":"全境封锁2","v":"243"},{"n":"骑马与砍杀","v":"326"},{"n":"人类一败涂地","v":"270"},{"n":"无主之地3","v":"273"},{"n":"辐射76","v":"220"},{"n":"全面战争","v":"257"},{"n":"文字游戏","v":"583"},{"n":"恋爱模拟游戏","v":"592"},{"n":"泰拉瑞亚","v":"593"},{"n":"游戏速通","v":"678"},{"n":"Roblox","v":"753"},{"n":"雀魂麻将","v":"803"},{"n":"德州电锯","v":"834"},{"n":"其他单机","v":"235"}]}],
        "1":[{"key":"area","name":"分区","value":[{"n":"聊天室","v":"740"},{"n":"视频唱见","v":"21"},{"n":"萌宅领域","v":"530"},{"n":"视频聊天","v":"145"},{"n":"舞见","v":"207"}]}],
        "5":[{"key":"area","name":"分区","value":[{"n":"唱见电台","v":"190"},{"n":"聊天电台","v":"192"},{"n":"甜宠电台","v":"817"}]}],
        "9":[{"key":"area","name":"分区","value":[{"n":"TopStar","v":"743"},{"n":"虚拟Singer","v":"744"},{"n":"虚拟Gamer","v":"745"},{"n":"虚拟声优","v":"746"},{"n":"虚拟日常","v":"371"},{"n":"虚拟APEX","v":"789"},{"n":"虚拟PK","v":"775"}]}],
        "14":[{"key":"area","name":"分区","value":[{"n":"交友","v":"818"},{"n":"点唱","v":"819"},{"n":"兴趣","v":"820"}]}],
        "11":[{"key":"area","name":"分区","value":[{"n":"社科法律心理","v":"376"},{"n":"人文历史","v":"702"},{"n":"校园学习","v":"372"},{"n":"职场·技能","v":"377"},{"n":"科技","v":"375"},{"n":"科学科普","v":"701"}]}],
        "13":[{"key":"area","name":"分区","value":[{"n":"游戏赛事","v":"561"},{"n":"体育赛事","v":"562"},{"n":"赛事综合","v":"563"}]}],
        "301":[{"key":"area","name":"分区","value":[{"n":"热门帮玩","v":"301000"},{"n":"手游帮玩","v":"301002"},{"n":"网游帮玩","v":"301003"},{"n":"单机帮玩","v":"301004"}]}],
        "15":[{"key":"area","name":"分区","value":[{"n":"兵临城下","v":"814"},{"n":"功夫狂飙","v":"833"},{"n":"竞技玩法","v":"815"},{"n":"休闲玩法","v":"816"}]}]
    },
    detailUrl:'https://live.bilibili.com/fyid',//二级详情拼接链接(json格式用)
    // detailUrl:'https://api.live.bilibili.com/xlive/web-room/v1/playUrl/playUrl?cid=fyid&platform=h5&otype=json&quality=0',//二级详情拼接链接(json格式用)
    // searchUrl:'/x/web-interface/search/type?__refresh__=true&page=fypage&page_size=42&order=online&platform=pc&highlight=1&single_column=0&keyword=**&search_type=live&dynamic_offset=0&preload=true',
    searchUrl:'https://api.bilibili.com/x/web-interface/search/type?search_type=live&keyword=**&page=fypage',
    searchable:2,
    quickSearch:0,
    headers:{
        "User-Agent":"PC_UA",
        "Referer": "https://www.bilibili.com",
        // "Cookie":"$bili_cookie"
        "Cookie":"https://ghproxy.net/https://raw.githubusercontent.com/FongMi/CatVodSpider/main/txt/cookie.txt"
    },
    timeout:5000,
    limit:8,
    play_parse:true,
    // play_json:[{re:'*', json:{jx:0, parse:1,header:JSON.stringify({"user-agent":"Mozilla/5.0 (Linux; U; Android 9; zh-CN; MI 9 Build/PKQ1.181121.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/12.5.5.1035 Mobile Safari/537.36"})}}],
    // play_json:[{re:'*', json:{jx:0, parse:1,header:JSON.stringify({"user-agent":"uc_ua"})}}],
    // play_json:0,
    lazy:`js:
        let ids = input.split('_');
        let dan = 'https://api.bilibili.com/x/v1/dm/list.so?oid=' + ids[1];
        let result = {};
        let iurl = 'https://api.live.bilibili.com/room/v1/Room/playUrl?cid=' + ids[1] + '&' + ids[0];
        let html = request(iurl);
        let jRoot = JSON.parse(html);
        let jo = jRoot['data'];
        let ja = jo['durl'];
        let purl = '';
        if (ja.length > 0) {
            purl = ja[0]['url']
        }
        result['parse'] = 0;
        result['playUrl'] = '';
        result['url'] = unescape(purl);
        result['header'] = {
            Referer: 'https://live.bilibili.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        };
        result['danmaku'] = dan;
        if (/h5/.test(ids[0])) {
            result['contentType'] = '';
            input = result
        } else {
            result['contentType'] = 'video/x-flv';
            input = result
        }
    `,
    double:false,
    推荐:'*',
    一级:'json:data.list;title;system_cover;uname;roomid',
    // 二级:'*',
    二级:"js:let aid=input.match(/\\/(\\d+)/)[1];log(aid);let html=request('https://api.live.bilibili.com/room/v1/Room/get_info?room_id='+aid);let jo=JSON.parse(html).data;let title=jo['title'];let pic=jo['keyframe'];let desc=jo['description'];let dire=jo['uid'];let typeName=jo['area_name'];let remark='在线人数:'+jo['online'];let vod={vod_id:aid,vod_name:title,vod_pic:pic,type_name:typeName,vod_area:'bililivedanmu',vod_remarks:remark,vod_actor:'直播间id-'+aid,vod_director:dire,vod_content:desc};vod['vod_play_from']='B站';vod['vod_play_url']='flv线路原画$platform=web&quality=4_'+aid+'#flv线路高清$platform=web&quality=3_'+aid+'#h5线路原画$platform=h5&quality=4_'+aid+'#h5线路高清$platform=h5&quality=3_'+aid;VOD=vod;",
    // 搜索:'json:data.result.live_room;title;cover;uname;roomid',
    搜索:'js:let html=request(input);let msg=JSON.parse(html).message;if(msg!=="0"){VODS=[{vod_name:KEY+"➢"+msg,vod_id:"no_data",vod_remarks:"别点,缺少bili_cookie",vod_pic:"https://ghproxy.net/https://raw.githubusercontent.com/hjdhnx/dr_py/main/404.jpg"}]}else{let videos=[];let vodList=JSON.parse(html).data.result.live_room;vodList.forEach(function(vod){let aid=vod["roomid"];let title="直播间："+vod["title"].replace(\'<em class="keyword">\',"").replace("</em>","");let img="https:"+vod["user_cover"];let remark=vod["watched_show"]["text_small"]+"  "+vod["uname"];videos.push({vod_id:aid,vod_name:title,vod_pic:img,vod_remarks:remark})});VODS=videos}',
    // 预处理:'if(rule_fetch_params.headers.Cookie.startsWith("http")){rule_fetch_params.headers.Cookie=fetch(rule_fetch_params.headers.Cookie);setItem(RULE_CK,cookie)};log(rule_fetch_params.headers.Cookie)',
}