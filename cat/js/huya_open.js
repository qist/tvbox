import { Crypto, _ } from 'assets://js/lib/cat.js';

let host = '';
let customArea = '';
let dataFrom = 'official';
let isJustLive = false;
let siteKey = '';
let siteType = 0;

const MOBILE_UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36';

async function requestRaw(reqUrl, headers) {
    let resRaw = await req(reqUrl, {
        method: 'get',
        headers: headers,
    });
    return resRaw;
}

async function request(reqUrl) {
    let defHeader = {
        'User-Agent': MOBILE_UA,
    };
    let resRaw = await requestRaw(reqUrl, defHeader);
    return resRaw.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
    if (cfg.hasOwnProperty('ext')) {
        if (cfg.ext.hasOwnProperty('custom')) {
            customArea = cfg.ext.custom;
        }
        if (cfg.ext.hasOwnProperty('from')) {
            dataFrom = cfg.ext.from;
        }
    }
    if (dataFrom == 'justlive') {
        host = 'http://live.yj1211.work';
        isJustLive = true;
    } else {
        host = 'https://www.huya.com';
    }
}

async function home(filter) {
    let classes = [{"type_id":"1","type_name":"网游"},{"type_id":"2","type_name":"单机"},{"type_id":"3","type_name":"手游"},{"type_id":"8","type_name":"娱乐"}];
    let filterObj = {
        "1":[{"key":"cateId","name":"分类","init":"1","value":[{"n":"英雄联盟","v":"1"},{"n":"CS2","v":"862"},{"n":"穿越火线","v":"4"},{"n":"lol云顶之弈","v":"5485"},{"n":"无畏契约","v":"5937"},{"n":"CFHD","v":"6079"},{"n":"逆战","v":"135"},{"n":"炉石传说","v":"393"},{"n":"DOTA2","v":"7"},{"n":"地下城与勇士","v":"2"},{"n":"魔兽世界","v":"8"},{"n":"坦克世界","v":"802"},{"n":"DOTA1","v":"6"},{"n":"梦三国","v":"489"},{"n":"魔兽争霸3","v":"4615"},{"n":"问道","v":"107"},{"n":"命运方舟","v":"3058"},{"n":"QQ飞车","v":"9"},{"n":"星际争霸","v":"5"},{"n":"网游竞技","v":"100023"},{"n":"射击综合游戏","v":"100141"},{"n":"暴雪专区","v":"100043"},{"n":"彩虹岛Online","v":"683"},{"n":"剑灵","v":"897"},{"n":"军事游戏","v":"100133"},{"n":"冒险岛","v":"2243"},{"n":"暗黑破坏神","v":"1123"},{"n":"诛仙3","v":"1646"},{"n":"热血江湖","v":"387"},{"n":"英魂之刃","v":"1830"},{"n":"武林外传一世琴缘","v":"1661"},{"n":"起凡：群雄逐鹿","v":"1612"},{"n":"神武4电脑版","v":"3227"},{"n":"龙之谷","v":"15"},{"n":"炉石战棋","v":"5751"},{"n":"御龙在天","v":"675"},{"n":"逆水寒","v":"2952"},{"n":"千年3","v":"878"},{"n":"永恒之塔","v":"446"},{"n":"体育游戏","v":"100135"},{"n":"寻仙","v":"734"},{"n":"战舰世界","v":"1947"},{"n":"QQ三国","v":"1090"},{"n":"流放之路","v":"427"},{"n":"反恐精英Online","v":"1918"},{"n":"反恐行动online","v":"861"},{"n":"征途","v":"2715"},{"n":"战争雷霆","v":"624"},{"n":"丝路传说2","v":"1026"},{"n":"星际战甲","v":"627"},{"n":"NBA2KOL系列","v":"3959"},{"n":"九阴真经","v":"1009"},{"n":"跑跑卡丁车","v":"162"},{"n":"诛仙世界","v":"7749"},{"n":"QQ华夏","v":"1878"},{"n":"天涯明月刀","v":"1219"},{"n":"大话西游：归来","v":"8239"},{"n":"荒野行动PC版","v":"3185"},{"n":"新剑侠情缘","v":"586"},{"n":"剑网3","v":"900"},{"n":"生死狙击2","v":"6091"},{"n":"全球使命","v":"939"},{"n":"梦想世界3","v":"486"},{"n":"枪神纪","v":"496"},{"n":"新天龙八部","v":"5671"},{"n":"铁甲雄兵","v":"2765"},{"n":"神泣","v":"2531"},{"n":"斗战神","v":"591"},{"n":"造梦西游OL","v":"6815"},{"n":"天堂","v":"1966"},{"n":"大话西游2","v":"2975"},{"n":"使命召唤：战区","v":"5911"},{"n":"希望OL","v":"1161"},{"n":"极光世界 弑神传","v":"514"},{"n":"守望先锋归来","v":"2174"},{"n":"QQ自由幻想","v":"1862"},{"n":"命运2","v":"2942"},{"n":"奇迹世界2","v":"766"},{"n":"坦克大战","v":"4359"},{"n":"生死狙击","v":"2471"},{"n":"天翼决","v":"779"},{"n":"QQ幻想","v":"2419"},{"n":"新飞飞(FlyFF)","v":"1582"},{"n":"刀剑英雄","v":"915"},{"n":"FIFA Online系列","v":"100079"},{"n":"全球使命3","v":"2953"},{"n":"完美端游系列","v":"3034"},{"n":"战意","v":"2599"},{"n":"泡泡堂","v":"440"},{"n":"赛尔号","v":"2755"},{"n":"大唐无双零","v":"1584"},{"n":"QQ炫舞","v":"2440"},{"n":"007：传奇","v":"1135"},{"n":"天下","v":"1597"},{"n":"天谕","v":"1899"},{"n":"新倩女幽魂","v":"1579"},{"n":"传世无双","v":"984"},{"n":"剑侠世界","v":"903"},{"n":"Warhaven","v":"9053"},{"n":"诺亚传说","v":"190"},{"n":"新挑战","v":"583"},{"n":"超激斗梦境","v":"5691"},{"n":"QQ音速","v":"1085"},{"n":"征途2","v":"677"},{"n":"征程","v":"678"},{"n":"蜀门","v":"4711"},{"n":"完美世界：诸神之战","v":"7217"},{"n":"战之刃：幸存者","v":"8627"},{"n":"黎明之光","v":"41"},{"n":"天命西游","v":"1086"},{"n":"炫舞时代","v":"3353"},{"n":"荣誉空间","v":"225"},{"n":"卡拉彼丘","v":"9073"},{"n":"成吉思汗怀旧版","v":"640"},{"n":"英雄年代3","v":"1232"},{"n":"天书奇谈","v":"2225"},{"n":"劲舞团","v":"2420"},{"n":"远征Online梦想版","v":"142"},{"n":"奇迹：传奇","v":"3917"},{"n":"封印者","v":"2294"},{"n":"上古世纪","v":"1046"},{"n":"梦幻诛仙2","v":"488"},{"n":"TERA Online","v":"1072"},{"n":"倚天Ⅱ","v":"959"},{"n":"街头篮球","v":"206"},{"n":"永恒轮回：无限","v":"7847"},{"n":"火线精英","v":"2550"},{"n":"忍者村大战2","v":"2369"},{"n":"领地人生","v":"2282"},{"n":"仙侠世界","v":"995"},{"n":"洛奇英雄传","v":"432"},{"n":"KARDS","v":"8261"},{"n":"无限法则","v":"3189"},{"n":"全面战争：竞技场","v":"5901"},{"n":"自由篮球","v":"243"},{"n":"FC Online4","v":"3683"},{"n":"战地之王","v":"618"},{"n":"古剑奇谭OL","v":"1892"},{"n":"QQ仙侠传","v":"2291"},{"n":"300英雄","v":"1132"}]}],
        "2":[{"key":"cateId","name":"分类","init":"2793","value":[{"n":"天天吃鸡","v":"2793"},{"n":"永劫无间","v":"6219"},{"n":"主机游戏","v":"100032"},{"n":"猛兽派对","v":"6165"},{"n":"互动点播","v":"5907"},{"n":"我的世界","v":"1732"},{"n":"方舟","v":"1997"},{"n":"单机热游","v":"100002"},{"n":"怀旧游戏","v":"100125"},{"n":"逃离塔科夫","v":"3493"},{"n":"俄罗斯钓鱼4","v":"5495"},{"n":"部落：上升","v":"1318"},{"n":"Dark and Darker","v":"7905"},{"n":"The Front","v":"9497"},{"n":"Apex英雄","v":"5011"},{"n":"生化危机4重制版","v":"8013"},{"n":"DayZ独立版","v":"1125"},{"n":"星空","v":"7857"},{"n":"互动剧游","v":"6919"},{"n":"艾尔登法环","v":"5801"},{"n":"恐惧之间","v":"6679"},{"n":"SCUM","v":"4245"},{"n":"Dread Hunger","v":"7601"},{"n":"塞尔达传说：王国之泪","v":"7883"},{"n":"欧洲卡车模拟","v":"475"},{"n":"洛克王国","v":"2864"},{"n":"卧龙：苍天陨落","v":"7859"},{"n":"无人深空","v":"2566"},{"n":"帝国神话","v":"6821"},{"n":"饥荒","v":"74"},{"n":"森林之子","v":"7943"},{"n":"星球大战系列","v":"554"},{"n":"极限竞速：地平线","v":"2634"},{"n":"最终幻想16","v":"7869"},{"n":"Among Us","v":"6163"},{"n":"怪物猎人：崛起","v":"6479"},{"n":"怪物猎人物语","v":"7101"},{"n":"骑马与砍杀系列","v":"4783"},{"n":"荒野大镖客2","v":"4319"},{"n":"太荒初境","v":"7685"},{"n":"罗布乐思","v":"5771"},{"n":"只狼：影逝二度","v":"4505"},{"n":"双人成行","v":"6737"},{"n":"重生边缘","v":"6201"},{"n":"海贼王 寻秘世界","v":"5097"},{"n":"战神：诸神黄昏","v":"7771"},{"n":"恐鬼症","v":"6205"},{"n":"鬼谷八荒","v":"6571"},{"n":"霍格沃茨之遗","v":"7881"},{"n":"全面战争","v":"3521"},{"n":"仁王2","v":"5795"},{"n":"奥拉星","v":"2846"},{"n":"甜蜜之家","v":"6739"},{"n":"仙剑奇侠传七","v":"6509"},{"n":"消逝的光芒2","v":"7581"},{"n":"渡神记","v":"6231"},{"n":"归家异途","v":"2949"},{"n":"博德之门3","v":"6147"},{"n":"看门狗：军团","v":"6155"},{"n":"使命召唤系列","v":"100137"},{"n":"育碧游戏","v":"100139"},{"n":"帝国时代4","v":"4835"},{"n":"英灵神殿","v":"6609"},{"n":"蛮荒志异：起源","v":"9709"},{"n":"岛","v":"3019"},{"n":"沙盒与副本","v":"9151"},{"n":"扫雷","v":"2349"},{"n":"街机游戏","v":"5999"},{"n":"幽灵线：东京","v":"7669"},{"n":"怪物猎人世界","v":"3519"},{"n":"盗贼之海","v":"3641"},{"n":"纸人","v":"5257"},{"n":"黑色像素人","v":"28"},{"n":"对马岛之魂","v":"6039"},{"n":"瑞奇与叮当","v":"2455"},{"n":"港诡实录","v":"5853"},{"n":"剑士","v":"1467"},{"n":"魔法门之英雄无敌系列","v":"2096"},{"n":"星露谷物语","v":"2443"},{"n":"仙剑奇侠传四","v":"1659"},{"n":"伤害世界","v":"2337"},{"n":"禁闭求生","v":"6065"},{"n":"真三国无双","v":"1599"},{"n":"恐怖黎明","v":"3435"},{"n":"其他单机","v":"3069"},{"n":"幽灵行动：荒野","v":"2794"},{"n":"边缘","v":"151"},{"n":"阿凡达","v":"106"},{"n":"全面战争：三国","v":"3004"},{"n":"黎明之星","v":"40"},{"n":"翼星求生","v":"7463"},{"n":"黎明传说","v":"39"},{"n":"恶魔之魂","v":"6151"},{"n":"艾兰岛","v":"3855"},{"n":"龙与地下城：秘影历代记HD","v":"17"},{"n":"龙与地下城：匕首谷","v":"18"},{"n":"沙石镇时光","v":"7687"},{"n":"三国志曹操传","v":"2592"},{"n":"FIFA足球","v":"1888"},{"n":"最终幻想7：重制版","v":"5809"},{"n":"四海兄弟","v":"5995"},{"n":"最终幻想：起源","v":"7653"},{"n":"摔跤城大乱斗","v":"7773"},{"n":"音乐游戏","v":"2761"},{"n":"精灵与萤火意志","v":"5895"},{"n":"桥梁建造师","v":"3275"},{"n":"哈迪斯","v":"6153"},{"n":"小缇娜的奇幻之地","v":"7647"},{"n":"宝可梦：剑盾","v":"5715"},{"n":"边境","v":"4779"},{"n":"人类一败涂地","v":"3289"},{"n":"糖豆人：终极淘汰赛","v":"6083"},{"n":"精灵宝可梦Let's Go","v":"4375"},{"n":"战锤40K：暗潮","v":"3016"},{"n":"石油骚动","v":"2585"},{"n":"紫塞秋风","v":"6045"},{"n":"阿尔比恩","v":"8115"},{"n":"猎人：荒野的召唤","v":"2906"},{"n":"FIFA 23","v":"7789"},{"n":"都市：天际线","v":"2201"},{"n":"乐高大电影：游戏版","v":"1439"},{"n":"全面战争：阿提拉","v":"2383"},{"n":"斩妖行","v":"6105"},{"n":"马里奥赛车8","v":"5947"},{"n":"复仇者联盟","v":"6121"},{"n":"霓虹深渊","v":"5743"}]}],
        "3":[{"key":"cateId","name":"分类","init":"2336","value":[{"n":"王者荣耀","v":"2336"},{"n":"和平精英","v":"3203"},{"n":"英雄联盟手游","v":"6203"},{"n":"CF手游","v":"2413"},{"n":"金铲铲之战","v":"7185"},{"n":"三国杀","v":"1669"},{"n":"原神","v":"5489"},{"n":"棋牌桌游","v":"100036"},{"n":"综合手游","v":"100029"},{"n":"劲乐幻想","v":"7691"},{"n":"新游广场","v":"100052"},{"n":"崩坏：星穹铁道","v":"7349"},{"n":"火影忍者手游","v":"2429"},{"n":"第五人格","v":"3115"},{"n":"问道手游","v":"2477"},{"n":"暗区突围","v":"7209"},{"n":"QQ飞车手游","v":"2928"},{"n":"球球大作战","v":"2411"},{"n":"明日之后","v":"3483"},{"n":"皇室战争","v":"2439"},{"n":"COD手游","v":"4769"},{"n":"手游休闲","v":"100004"},{"n":"二次元手游","v":"100091"},{"n":"摸了个鱼","v":"9283"},{"n":"MMORPG","v":"100273"},{"n":"动作游戏","v":"100197"},{"n":"战争冲突","v":"7449"},{"n":"王者模拟战","v":"5699"},{"n":"逆水寒手游","v":"7725"},{"n":"幻塔","v":"6437"},{"n":"欢乐斗地主","v":"1749"},{"n":"神武4手游","v":"3135"},{"n":"阴阳师","v":"2598"},{"n":"DNF手游","v":"4921"},{"n":"欢乐麻将","v":"1751"},{"n":"英雄联盟电竞经理","v":"7177"},{"n":"狼人杀手游","v":"100049"},{"n":"新天龙八部手游","v":"6945"},{"n":"中国象棋","v":"1671"},{"n":"天天象棋","v":"4997"},{"n":"传奇世界3D","v":"3961"},{"n":"御龙在天手游","v":"2568"},{"n":"高能英雄","v":"8359"},{"n":"天龙八部手游","v":"2852"},{"n":"三国志战略版","v":"5619"},{"n":"忍者必须死3","v":"4041"},{"n":"SKY光遇","v":"3719"},{"n":"虎牙领主争霸","v":"7529"},{"n":"云上城之歌","v":"5977"},{"n":"晶核","v":"7279"},{"n":"仙境传说RO","v":"2675"},{"n":"天天狼人","v":"2774"},{"n":"JJ棋牌","v":"3841"},{"n":"奇迹MU：觉醒","v":"3116"},{"n":"指尖四川麻将","v":"7215"},{"n":"部落冲突","v":"1797"},{"n":"新剑侠情缘手游","v":"6259"},{"n":"萌宠远征","v":"9385"},{"n":"暗黑破坏神：不朽","v":"6385"},{"n":"英雄杀","v":"2688"},{"n":"热血江湖手游","v":"2817"},{"n":"蛋仔派对","v":"6909"},{"n":"完美世界手游","v":"4237"},{"n":"巅峰战舰","v":"2502"},{"n":"狼人杀","v":"2785"},{"n":"斗罗大陆：魂师对决","v":"6745"},{"n":"武侠乂手游","v":"4929"},{"n":"诛仙手游","v":"2647"},{"n":"斗破苍穹手游","v":"4337"},{"n":"迷你世界","v":"2683"},{"n":"风云","v":"3061"},{"n":"妄想山海","v":"6007"},{"n":"曙光英雄","v":"6169"},{"n":"三国战纪2","v":"6049"},{"n":"梦幻新诛仙","v":"5975"},{"n":"黎明觉醒：生机","v":"6131"},{"n":"远征","v":"7837"},{"n":"航海王：燃烧意志","v":"3943"},{"n":"火炬之光：无限","v":"6399"},{"n":"巅峰极速","v":"6979"},{"n":"圣境之塔","v":"7055"},{"n":"魔力宝贝","v":"2891"},{"n":"香肠派对","v":"3639"},{"n":"创造与魔法","v":"2931"},{"n":"JJ斗地主","v":"6271"},{"n":"永恒纪元：戒","v":"2646"},{"n":"天涯明月刀手游","v":"5115"},{"n":"狼人杀官方","v":"3679"},{"n":"混沌起源","v":"5985"},{"n":"多多自走棋","v":"5133"},{"n":"梦幻诛仙手游","v":"2672"},{"n":"鸿图之下","v":"6027"},{"n":"新笑傲江湖","v":"5669"},{"n":"凡人修仙传：人界篇","v":"8297"},{"n":"多乐棋牌","v":"6209"},{"n":"口袋觉醒","v":"5953"},{"n":"跑跑卡丁车手游","v":"2620"},{"n":"奶块","v":"2775"},{"n":"月圆之夜","v":"4339"},{"n":"率土之滨","v":"2691"},{"n":"征途2手游","v":"2811"},{"n":"英魂之刃口袋版","v":"2760"},{"n":"精灵盛典：黎明","v":"6123"},{"n":"方舟手游","v":"4035"},{"n":"掼蛋","v":"6225"},{"n":"绝世仙王","v":"6619"},{"n":"流星群侠传","v":"3927"},{"n":"寻仙手游","v":"2979"},{"n":"一梦江湖","v":"3082"},{"n":"Lost Light（萤火突击国际服）","v":"6859"},{"n":"弹幕云游戏","v":"7001"},{"n":"猎魂觉醒","v":"3071"},{"n":"冒险岛：枫之传说","v":"8005"},{"n":"征途手游","v":"2556"},{"n":"海岛奇兵","v":"2624"},{"n":"倩女幽魂手游","v":"2503"},{"n":"超凡先锋","v":"6507"},{"n":"龙之谷2手游","v":"2736"},{"n":"崩坏3","v":"2639"},{"n":"猫和老鼠","v":"2758"},{"n":"七人传奇：光与暗之交战","v":"8125"},{"n":"JJ麻将","v":"9487"},{"n":"拉轰西游","v":"9543"},{"n":"三国战纪","v":"6047"},{"n":"自由幻想手游","v":"4015"},{"n":"秦时明月世界","v":"5279"},{"n":"新斗罗大陆","v":"6657"},{"n":"新神魔大陆","v":"5939"},{"n":"逃跑吧！少年","v":"4137"},{"n":"太古神王2","v":"6649"},{"n":"剑侠世界3","v":"7183"},{"n":"天天吃鸡手机版","v":"4341"},{"n":"时空猎人3","v":"6411"},{"n":"合金弹头：觉醒","v":"6931"},{"n":"明日方舟","v":"4925"},{"n":"原始征途","v":"7713"},{"n":"奇迹：最强者","v":"3215"},{"n":"天天酷跑","v":"1715"},{"n":"FC 足球世界","v":"3873"},{"n":"万国觉醒","v":"6159"},{"n":"机动都市阿尔法","v":"5411"},{"n":"航海王热血航线","v":"6181"},{"n":"幻世九歌","v":"7199"},{"n":"植物大战僵尸","v":"485"},{"n":"无悔华夏","v":"7063"},{"n":"时空猎人","v":"1742"},{"n":"荒野乱斗","v":"4613"},{"n":"拳皇98终极之战OL","v":"2687"},{"n":"蛇蛇争霸","v":"2680"},{"n":"王牌竞速","v":"6463"},{"n":"重返帝国","v":"6955"},{"n":"吞噬星空：黎明","v":"6651"},{"n":"口袋妖怪","v":"2541"},{"n":"QQ炫舞手游","v":"2991"},{"n":"一拳超人：最强之男","v":"4629"},{"n":"荣耀新三国","v":"6943"},{"n":"少年三国志2","v":"6125"},{"n":"我的起源","v":"5365"},{"n":"决战平安京","v":"3064"},{"n":"剑灵2","v":"7223"},{"n":"开心消消乐","v":"1712"},{"n":"小小蚁国","v":"7803"},{"n":"最强NBA","v":"2988"},{"n":"剑侠情缘手游","v":"2621"},{"n":"长安幻想","v":"6727"},{"n":"我叫MT4","v":"4087"},{"n":"全明星街球派对","v":"8401"},{"n":"大话西游手游","v":"2626"},{"n":"荣耀大天使","v":"6477"},{"n":"镇魂街：天生为王","v":"6557"},{"n":"摩尔庄园","v":"5981"},{"n":"游戏王：决斗链接","v":"4451"},{"n":"剑侠世界2手游","v":"3150"},{"n":"青云诀2","v":"6009"},{"n":"战地无疆","v":"7909"},{"n":"一念逍遥","v":"6419"},{"n":"永劫无间手游","v":"7579"},{"n":"尘白禁区","v":"7297"},{"n":"元梦之星","v":"9521"},{"n":"不良人3","v":"5891"},{"n":"剑灵：革命","v":"4545"},{"n":"魔力宝贝：旅人","v":"7573"},{"n":"米加小镇","v":"7269"},{"n":"龙武手游","v":"5219"},{"n":"斗罗大陆2：绝世唐门","v":"6581"},{"n":"西行纪燃魂","v":"8303"},{"n":"坦克世界闪击战","v":"4977"},{"n":"军棋","v":"2561"},{"n":"饥荒：新家","v":"6491"},{"n":"拳皇命运","v":"3379"},{"n":"实况足球","v":"3741"},{"n":"战舰世界闪击战","v":"4101"},{"n":"时空召唤","v":"2551"},{"n":"王牌战争：文明重启","v":"5479"},{"n":"雀魂麻将","v":"7107"},{"n":"欢乐升级","v":"3925"},{"n":"绿色征途","v":"4227"},{"n":"弹弹堂手游","v":"2857"},{"n":"太极熊猫3：猎龙","v":"2778"},{"n":"哈利波特：魔法觉醒","v":"5835"},{"n":"天地劫：幽城再临","v":"5987"},{"n":"热血街篮","v":"5859"},{"n":"神雕侠侣手游","v":"1781"},{"n":"山海镜花","v":"5089"},{"n":"三国志战棋版","v":"7937"},{"n":"神雕侠侣2","v":"4209"},{"n":"仙魔决","v":"1674"},{"n":"王者荣耀星之破晓","v":"7927"},{"n":"我在江湖之神魔道","v":"7699"},{"n":"梦幻模拟战","v":"3481"},{"n":"单机手游","v":"2777"},{"n":"斗罗大陆-斗神再临","v":"6631"},{"n":"未来之役","v":"6831"},{"n":"风云岛行动","v":"4695"},{"n":"新游推荐","v":"3160"},{"n":"火影忍者OL","v":"3901"},{"n":"九灵神域","v":"7719"},{"n":"武动乾坤","v":"3829"},{"n":"秦时明月2","v":"1784"},{"n":"文明与征服","v":"7071"},{"n":"战双：帕弥什","v":"4133"},{"n":"大航海时代：海上霸主","v":"6929"},{"n":"剑网1：归来","v":"7361"},{"n":"绝区零","v":"7711"},{"n":"黑色沙漠手游","v":"7287"},{"n":"虎牙吃鸡","v":"7465"},{"n":"一剑斩仙","v":"6843"},{"n":"传奇天下","v":"6927"},{"n":"斗斗堂","v":"7133"},{"n":"斗罗大陆","v":"6119"},{"n":"天谕手游","v":"5925"},{"n":"坎公骑冠剑","v":"6641"},{"n":"最终幻想觉醒","v":"2721"},{"n":"神将三国","v":"6621"},{"n":"灌篮高手正版授权手游","v":"5399"},{"n":"剑与家园","v":"2838"},{"n":"极无双2","v":"7825"},{"n":"光明大陆","v":"2832"},{"n":"荒野行动","v":"3084"},{"n":"战斗法则","v":"9513"},{"n":"疯狂原始人","v":"4619"},{"n":"逆战手游","v":"7575"},{"n":"石器时代：觉醒","v":"9159"}]}],
        "8":[{"key":"cateId","name":"分类","init":"1663","value":[{"n":"星秀","v":"1663"},{"n":"户外","v":"2165"},{"n":"一起看","v":"2135"},{"n":"二次元","v":"2633"},{"n":"虚拟偶像","v":"6055"},{"n":"旅游","v":"6791"},{"n":"放映厅","v":"6245"},{"n":"娱乐天地","v":"100022"},{"n":"交友","v":"4079"},{"n":"组队","v":"5367"},{"n":"吃喝玩乐","v":"100044"},{"n":"原创","v":"6861"},{"n":"虎牙文化","v":"4089"},{"n":"体育","v":"2356"},{"n":"虎牙地方","v":"5123"},{"n":"颜值","v":"2168"},{"n":"科技","v":"2408"},{"n":"音乐","v":"3793"},{"n":"趣分享","v":"5883"},{"n":"一起买","v":"7759"},{"n":"派对","v":"7785"}]}],
    };
    if (customArea.length > 0) {
        const filterCfg = customArea.split('#');
        classes.unshift({"type_id":"custom","type_name":"自选"});
        const filterList = _.map(filterCfg, (it) => {
            const filterKv = it.split(',');
            return {
                n: filterKv[1],
                v: filterKv[0],
            };
        });
        const defKey = filterList[0];
        filterObj["custom"] = [{"key":"cateId","name":"分类","init":defKey.v,"value":filterList}];
    }
    if (isJustLive) {
        // key-value映射修改
        const filterKeys = Object.keys(filterObj);
        for (const filterKey of filterKeys) {
            const filterItem = filterObj[filterKey];
            for (const typeItem of filterItem) {
                typeItem.value = _.map(typeItem.value, (it) => {
                    // 修改默认值
                    if (it.v == typeItem.init) {
                        typeItem.init = it.n;
                    }
                    return {
                        n: it.n,
                        v: it.n,
                    };
                });
            }
        }
    }
    classes.unshift({"type_id":"home","type_name":"首页"});
    return JSON.stringify({
        class: _.map(classes, (it) => {
            return {
                type_id: it.type_id,
                type_name: it.type_name,
                land: 1,
                ratio: 1.78,
            };
        }),
        filters: filterObj,
    });
}

async function homeVod() {
    return '{}';
}

async function category(tid, pg, filter, extend) {
    if (pg <= 0 || typeof pg == 'undefined') pg = 1;
    let url = '';
    let videos = [];
    if (isJustLive) {
        if (tid == 'home') {
            url = host + '/api/live/getRecommendByPlatform?platform=huya&size=20&page=' + pg;
        } else {
            url = host + '/api/live/getRecommendByPlatformArea?platform=huya&size=20&area=' + extend.cateId + '&page=' + pg;
        }
        const data = JSON.parse(await request(url));
        videos = _.map(data.data, (it) => {
            return {
                vod_id: it.roomId,
                vod_name: it.roomName,
                vod_pic: it.roomPic,
                vod_remarks: it.ownerName,
            }
        });
    } else {
        if (tid == 'home') {
            url = host + '/cache.php?m=LiveList&do=getLiveListByPage&tagAll=1&page=' + pg;
        } else {
            url = host + '/cache.php?m=LiveList&do=getLiveListByPage&gameId=' + extend.cateId + '&tagAll=0&page=' + pg;
        }
        const data = JSON.parse(await request(url));
        videos = _.map(data.data.datas, (it) => {
            return {
                vod_id: it.profileRoom,
                vod_name: it.roomName,
                vod_pic: it.screenshot,
                vod_remarks: it.nick,
            }
        });
    }

    return JSON.stringify({
        page: parseInt(pg),
        pagecount: 9999,
        limit: 90,
        total: 999999,
        list: videos,
    });
}

async function detail(id) {
    let liveInfo = null;
    let streamInfoList = null;
    if (isJustLive) {
        const headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': MOBILE_UA,
        };
        const resp = await requestRaw('https://www.huya.com/' + id, headers);
        let liveData = null;
        let streamInfo = resp.content.match(/stream: ([\s\S]*?)\n/);
        if (streamInfo) {
            liveData = JSON.parse(streamInfo[1]);
        } else {
            streamInfo = resp.content.match(/"stream": "([\s\S]*?)"/);
            if (streamInfo) {
                let liveDataBase64 = streamInfo[1];
                liveData = JSON.parse(base64Decode(liveDataBase64));
            }
        }
        const vodData = liveData.data[0];
        liveInfo = vodData.gameLiveInfo;
        streamInfoList = vodData.gameStreamInfoList;
    } else {
        const resp = await request('https://mp.huya.com/cache.php?m=Live&do=profileRoom&roomid=' + id);
        const data = JSON.parse(resp);
        liveInfo = data.data.liveData;
        streamInfoList = data.data.stream.baseSteamInfoList;
    }
    let vod = {
        vod_id: id,
        vod_name: liveInfo.introduction,
        vod_pic: liveInfo.screenshot,
        vod_remarks: liveInfo.gameFullName,
        type_name: liveInfo.gameFullName,
        vod_director: liveInfo.nick,
        vod_actor: '',
        vod_content: liveInfo.activityCount + '人在线',
        vod_year: '',
        vod_area: '',
    };
    let vodList = [];
    let playUrl = '';
    for (const streamInfo of streamInfoList) {
        const urlData = getPlayUrlData(streamInfo);
        playUrl += `${urlData.cdnType}$${urlData.playUrl}#`;
    }
    vod.vod_play_from = 'huya';
    vod.vod_play_url = playUrl.replace(/#$/g, '');
    return JSON.stringify({
        list: [vod],
    });
}

function getPlayUrlData(streamInfo) {
    const hlsUrl = streamInfo.sHlsUrl + '/' + streamInfo.sStreamName + '.' + streamInfo.sHlsUrlSuffix;
    const srcAntiCode = unescape(streamInfo.sHlsAntiCode);
    let codeList = srcAntiCode.split('&');
    codeList = codeList.filter(code => code != '');
    let cryptoInfo = {};
    for (const code of codeList) {
      const [k, v] = code.split('=');
      cryptoInfo[k] = v;
    }
    const fm = unquote(cryptoInfo.fm);
    const fmDecoded = base64Decode(fm);
    const hashPrefix = fmDecoded.split('_')[0];
    const ctype = cryptoInfo.ctype || '';
    const txyp = cryptoInfo.txyp || '';
    const fs = cryptoInfo.fs || '';
    const t = cryptoInfo.t || '';
    const u = 1463993859134;
    const curTime = Date.now();
    const seqid = Math.floor(curTime + u);
    const wsTime = (Math.floor(curTime / 1e3) + 3600).toString(16);
    const v0 = seqid + '|' + ctype + '|' + t;
    const v1 = md5Encode(v0);
    const v2 = hashPrefix + '_' + u + '_' + streamInfo.sStreamName + '_' + v1 + '_' + wsTime;
    const hash = md5Encode(v2);
    const ratio = ''
    const purl = `${hlsUrl}?wsSecret=${hash}&wsTime=${wsTime}&seqid=${seqid}&ctype=${ctype}&ver=1&txyp=${txyp}&fs=${fs}&ratio=${ratio}&u=${u}&t=${t}&sv=2107230339`;
    return {
        cdnType: streamInfo.sCdnType,
        playUrl: purl,
    };
}

async function play(flag, id, flags) {
    return JSON.stringify({
        parse: 0,
        url: id,
        header: {
            "User-Agent": MOBILE_UA,
        },
    });
}

async function search(wd, quick) {
    const resp = await request('https://search.cdn.huya.com/?m=Search&do=getSearchContent&q=' + wd + '&uid=0&v=4&typ=-5&livestate=0&rows=40&start=0');
    const data = JSON.parse(resp);
    let videos = [];
    for (const vod of data.response['3'].docs) {
        videos.push({
            vod_id: vod.room_id,
            vod_name: vod.game_roomName,
            vod_pic: vod.game_screenshot,
            vod_remarks: vod.game_nick,
        });
    }
    return JSON.stringify({
        list: videos,
    });
}

function unquote(str) {
    return str.replace(/^"(.*)"$/, '$1');
}

function md5Encode(text) {
    return Crypto.MD5(Crypto.enc.Utf8.parse(text)).toString();
}

function base64Decode(text) {
    return Crypto.enc.Utf8.stringify(Crypto.enc.Base64.parse(text));
}

export function __jsEvalReturn() {
    return {
        init: init,
        home: home,
        homeVod: homeVod,
        category: category,
        detail: detail,
        play: play,
        search: search,
    };
}