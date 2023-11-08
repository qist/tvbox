import { _ } from 'assets://js/lib/cat.js';

let host = '';
let customArea = '';
let dataFrom = 'official';
let isJustLive = false;
let siteKey = '';
let siteType = 0;

const MOBILE_UA = 'Mozilla/5.0 (Linux; Android 11; M2007J3SC Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045714 Mobile Safari/537.36';

async function requestRaw(reqUrl, method) {
    let resRaw = await req(reqUrl, {
        method: method || 'get',
        headers: {
            'User-Agent': MOBILE_UA,
        },
    });
    return resRaw;
}

async function request(reqUrl) {
    let resRaw = await requestRaw(reqUrl)
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
        host = 'https://m.douyu.com';
    }
}

async function home(filter) {
    let classes = [{"type_id":"PCgame","type_name":"网游竞技"},{"type_id":"syxx","type_name":"手游休闲"},{"type_id":"djry","type_name":"单机热游"},{"type_id":"kjwh","type_name":"科技文化"},{"type_id":"yl","type_name":"娱乐天地"},{"type_id":"yp","type_name":"语音互动"},{"type_id":"voice","type_name":"语音直播"}];
    let filterObj = {
        "PCgame":[{"key":"cateId","name":"分类","init":"LOL","value":[{"n":"英雄联盟","v":"LOL"},{"n":"热门游戏","v":"rmyx"},{"n":"穿越火线","v":"CF"},{"n":"重生边缘","v":"CSBYOL"},{"n":"无畏契约","v":"VALORANT"},{"n":"CFHD","v":"CFHD"},{"n":"命运方舟","v":"LostArk"},{"n":"DNF","v":"DNF"},{"n":"DOTA2","v":"DOTA2"},{"n":"使命召唤","v":"COD"},{"n":"炉石传说","v":"How"},{"n":"CS2","v":"CounterStrike"},{"n":"lol云顶之弈","v":"ydzhy"},{"n":"魔兽争霸","v":"mszb"},{"n":"魔兽怀旧服","v":"wowclassic"},{"n":"自走棋","v":"dota2rpg"},{"n":"传奇","v":"cq"},{"n":"跑跑卡丁车","v":"Popkart"},{"n":"网易游戏","v":"wyyx"},{"n":"星际争霸","v":"SC"},{"n":"守望先锋","v":"Overwatch"},{"n":"DOTA","v":"DOTA"},{"n":"魔兽世界","v":"WOW"},{"n":"剑网3","v":"JX3"},{"n":"我的世界","v":"MC"},{"n":"超激斗梦境","v":"cjdmj"},{"n":"冒险岛","v":"mxd"},{"n":"三国杀","v":"sanguosha"},{"n":"梦幻西游","v":"MHXYOL"},{"n":"天涯明月刀","v":"tianya"},{"n":"街头篮球","v":"jtlq"},{"n":"NBA2KOL2","v":"NBA2KOL2"},{"n":"QQ飞车端游","v":"qqfcdy"},{"n":"军事游戏","v":"jsyx"},{"n":"棋牌娱乐","v":"qipai"},{"n":"FC ONLINE","v":"FCOL"},{"n":"热门网游","v":"rmwy"},{"n":"卡拉彼丘","v":"klbq"},{"n":"诛仙世界","v":"zxsj"},{"n":"APEX","v":"APEX"},{"n":"流放之路POE","v":"PathofExile"},{"n":"剑网3缘起","v":"JW3YQ"},{"n":"逆水寒","v":"nsh"},{"n":"风暴英雄","v":"HOTS"},{"n":"逆战","v":"NZ"},{"n":"坦克世界","v":"TKSJ"},{"n":"战舰世界","v":"wfws"},{"n":"反恐精英Online","v":"CS"},{"n":"暗黑破坏神","v":"DIABLO"},{"n":"梦三国2","v":"msg2"},{"n":"传奇世界","v":"cqsj"},{"n":"方舟：生存进化","v":"fzscjh"},{"n":"神武4电脑版","v":"swdnb"},{"n":"群雄逐鹿","v":"qxzl"},{"n":"堡垒之夜","v":"blzy"},{"n":"无限法则","v":"roe"},{"n":"问道电脑版","v":"wddnb"},{"n":"西山居游戏","v":"Seasun"},{"n":"最终幻想14","v":"FF14"},{"n":"战意","v":"WYZY"},{"n":"剑灵","v":"BladeSoul"},{"n":"星际战甲","v":"Warframe"},{"n":"龙之谷","v":"DragonNest"},{"n":"铁甲雄兵","v":"tjxb"},{"n":"古剑奇谭网络版","v":"gjqtwlb"},{"n":"轩辕传奇","v":"XYCQ"},{"n":"神途","v":"shentu"},{"n":"激战2","v":"GuildWars2"},{"n":"高达文化区","v":"gdyxq"},{"n":"忍者村大战2","v":"rzcdz2"},{"n":"RPG网游专区","v":"rpgwyzq"},{"n":"诛仙3","v":"zhuxian3"},{"n":"笑傲江湖OL","v":"xajhol"},{"n":"冒险岛2","v":"MXD2"},{"n":"超击突破","v":"SuperPeople"},{"n":"无尽战区","v":"WJZQ"},{"n":"永恒之塔","v":"AION"},{"n":"竞速游戏","v":"jingsu"},{"n":"FPS综合网游","v":"FPSOL"},{"n":"劲舞团","v":"jwt"},{"n":"天下","v":"tianxai"},{"n":"火箭联盟","v":"hjlm"},{"n":"泡泡堂","v":"ppt"},{"n":"音乐游戏","v":"MG"},{"n":"新倩女幽魂","v":"ONLINE"},{"n":"天谕","v":"tianyu"},{"n":"QQ炫舞","v":"qqxw"},{"n":"大唐无双","v":"dtws"},{"n":"怪物猎人ol","v":"MHol"},{"n":"手工星球","v":"sgxq"},{"n":"热血传奇：本源","v":"rxcqhjsgb"},{"n":"彩虹岛","v":"CHD"},{"n":"御龙在天","v":"YLZT"},{"n":"自由篮球","v":"ZYLQ"},{"n":"洛奇英雄传","v":"LQYXZ"},{"n":"洛奇","v":"LQ"},{"n":"封印者","v":"FYZ"},{"n":"合金弹头","v":"HJDT"},{"n":"新英雄年代","v":"XYXSD"},{"n":"盛趣游戏","v":"SQYX"},{"n":"新热血英豪","v":"XRXYH"},{"n":"沙盒游戏","v":"SHYX"},{"n":"恐鬼症","v":"KGZ"},{"n":"领地人生","v":"LDRS"},{"n":"大话西游2","v":"dhxy2"},{"n":"猎人","v":"lr"},{"n":"热血江湖online","v":"rxjhol"},{"n":"千年3","v":"qn3"},{"n":"逍遥情缘","v":"xyqy"},{"n":"快乐西游","v":"klxy"},{"n":"诺亚传说","v":"nycs"},{"n":"鹿鼎记","v":"ldj"},{"n":"武魂2电脑版","v":"wh2pc"},{"n":"奇迹世界sun","v":"qjsjsun"},{"n":"剑侠世界2电脑版","v":"jxsj2pc"},{"n":"斩魂","v":"zhpc"},{"n":"大唐2","v":"dt2pc"},{"n":"幻想神域电脑版","v":"hxsypc"},{"n":"蜀山：初章","v":"ssczpc"},{"n":"狼人对决网游","v":"lrdjpc"},{"n":"武林群侠传","v":"wlqxzpc"},{"n":"飘流幻境","v":"plhjpc"},{"n":"破天一剑","v":"ptyj"},{"n":"四国军棋","v":"sgjq"},{"n":"新大话西游3","v":"xy3"},{"n":"装甲战争","v":"zjzz"},{"n":"暴雪游戏综合","v":"g_bliz"},{"n":"HypeSquad","v":"HypeSquad"},{"n":"长尾4部虚拟分区","v":"cw4bxnfq"},{"n":"燕云十六声","v":"WHEREWINDSMEET"},{"n":"THE FINALS","v":"THEFINALS"},{"n":"NBA2K Online","v":"NBA2KOL"},{"n":"跑跑卡丁车：漂移","v":"KartRiderDrift"},{"n":"传奇永恒","v":"EternalLegend"},{"n":"盛趣传奇","v":"sqcq"},{"n":"火爆热游","v":"hbry"}]}],
        "syxx":[{"key":"cateId","name":"分类","init":"wzry","value":[{"n":"王者荣耀","v":"wzry"},{"n":"LOL手游","v":"LOLM"},{"n":"崩坏：星穹铁道","v":"bhxqtd"},{"n":"逆水寒手游","v":"NSHM"},{"n":"和平精英","v":"hpjy"},{"n":"暗区突围","v":"aqtw"},{"n":"蛋仔派对","v":"dzpd"},{"n":"高能英雄","v":"gnyx"},{"n":"幻塔","v":"ht"},{"n":"火影忍者","v":"hyrz"},{"n":"COD手游","v":"smzhsy"},{"n":"lol电竞经理","v":"EGAME"},{"n":"DNF手游","v":"mdnf"},{"n":"金铲铲之战","v":"JGAME"},{"n":"天刀手游","v":"tdsy"},{"n":"原神","v":"yuanshen"},{"n":"航海王热血航线","v":"HHWRXHX"},{"n":"元梦之星","v":"YMZX"},{"n":"鸿图之下","v":"htzx"},{"n":"欢乐麻将","v":"HLMJ"},{"n":"王者模拟战","v":"wzrpg"},{"n":"中国象棋","v":"ZGXQ"},{"n":"天谕手游","v":"tysy"},{"n":"巅峰坦克","v":"DFTK"},{"n":"新游中心","v":"xyzx"},{"n":"热门手游","v":"phone"},{"n":"梦幻手游","v":"mhxy"},{"n":"QQ飞车","v":"qqfcsy"},{"n":"第五人格","v":"dwrg"},{"n":"欢乐斗地主","v":"hlddz"},{"n":"荒野乱斗","v":"hyld"},{"n":"阴阳师","v":"yys"},{"n":"狼人杀","v":"LRS"},{"n":"JJ斗地主","v":"jj"},{"n":"梦幻新诛仙","v":"mhxzx"},{"n":"多多自走棋","v":"zzq"},{"n":"崩坏3","v":"bhxl"},{"n":"风云岛行动","v":"fydxd"},{"n":"云游戏","v":"cloudgame"},{"n":"跑跑手游","v":"PPKDCSY"},{"n":"率土之滨","v":"stzb"},{"n":"灌篮高手","v":"glgs"},{"n":"皇室战争","v":"hszz"},{"n":"忍者必须死3","v":"rzbxs3"},{"n":"神武4手游","v":"sw3"},{"n":"梦幻模拟战","v":"mhmnz"},{"n":"实况足球","v":"skzq"},{"n":"航海王：燃烧意志","v":"hhwrsyz"},{"n":"球球大作战","v":"qqdzz"},{"n":"英雄杀","v":"yxs"},{"n":"魔域口袋版","v":"mykdb"},{"n":"口袋新旅程","v":"KDXLC"},{"n":"剑网3：指尖江湖","v":"jw3zjjh"},{"n":"部落冲突","v":"blct"},{"n":"剑与家园","v":"jyjy"},{"n":"新笑傲江湖","v":"xxajh"},{"n":"猫和老鼠","v":"mhls"},{"n":"猎人手游","v":"lrlr"},{"n":"明日之后","v":"mrzh"},{"n":"影之诗","v":"yzs"},{"n":"决战平安京","v":"jzpaj"},{"n":"魂斗罗归来","v":"DLHGL"},{"n":"圣斗士星矢","v":"sdsxs"},{"n":"魔力宝贝手游","v":"mlbbsy"},{"n":"哈利波特：魔法觉醒","v":"HarryPotter"},{"n":"手游推广","v":"rmsy"},{"n":"魔灵召唤","v":"mlzh"},{"n":"香肠派对","v":"xcpd"},{"n":"迷你世界","v":"MNSJ"},{"n":"FC足球世界","v":"FCZQSJ"},{"n":"街篮","v":"jl"},{"n":"明日方舟","v":"mrfz"},{"n":"一梦江湖","v":"ymjh"},{"n":"完美世界手游","v":"wmsjsy"},{"n":"拳皇98OL","v":"kof98"},{"n":"赛尔号","v":"srh"},{"n":"仙境传说","v":"xjcs"},{"n":"流星群侠传","v":"liuxinghudiejian"},{"n":"逃跑吧少年","v":"tpbsn"},{"n":"石器时代","v":"sqsd"},{"n":"RPG手游","v":"rpgsy"},{"n":"英魂之刃口袋版","v":"yh"},{"n":"倩女幽魂手游","v":"qnyhsy"},{"n":"决斗之城2","v":"jdzc2"},{"n":"传奇手游","v":"cqsy"},{"n":"雀魂","v":"Majsoul"},{"n":"二次元手游","v":"ecysy"},{"n":"征途2手游","v":"zt2sy"},{"n":"万王之王3D","v":"wwzw3D"},{"n":"武林外传","v":"wlwz"},{"n":"潮人篮球","v":"crlq"},{"n":"元气骑士","v":"yuanqiqishi"},{"n":"红警OL手游","v":"hjolsy"},{"n":"植物大战僵尸手游","v":"ZWDZJS"},{"n":"创造与魔法","v":"ccymf"},{"n":"奇迹觉醒","v":"qjjx"},{"n":"光遇","v":"skygy"},{"n":"游戏王：决斗链接","v":"yxwjdlj"},{"n":"巅峰战舰","v":"dfzj"},{"n":"寻仙","v":"xunxian"},{"n":"天天象棋","v":"ttxq"},{"n":"王国纪元","v":"wgjy"},{"n":"龙族幻想","v":"lzhx"},{"n":"三国杀移动版","v":"SGSSY"},{"n":"罗布乐思","v":"Roblox"},{"n":"足球手游","v":"zqsy"},{"n":"月圆之夜","v":"yyzy"},{"n":"秦时明月世界","v":"qsmysj"},{"n":"麻将来了","v":"mjll"},{"n":"风之大陆","v":"fzdl"},{"n":"金属对决","v":"jsdj"},{"n":"轩辕剑龙舞云山","v":"xyjlwys"},{"n":"微乐棋牌","v":"WLQP"},{"n":"辐射：避难所Online","v":"fsbnsonline"},{"n":"街篮2","v":"jl2"},{"n":"极光计划","v":"jgjh"},{"n":"不良人3","v":"blr3"},{"n":"镇魔曲手游","v":"zmq"},{"n":"乱世王者","v":"lswz"},{"n":"篮球手游","v":"lqsy"},{"n":"鬼泣-巅峰之战","v":"gqdfzz"},{"n":"射击类手游","v":"qtsy"},{"n":"命运歌姬","v":"mygj"},{"n":"暗黑不朽","v":"diabloimmortal"},{"n":"新神魔大陆","v":"xsmdl"},{"n":"三国志战略版","v":"sgzzlb"},{"n":"天地劫：幽城再临","v":"tdj"},{"n":"Disorder","v":"Disorder"},{"n":"云上城之歌","v":"ysczg"},{"n":"五子棋","v":"wzq"},{"n":"围棋","v":"wq"},{"n":"全球行动","v":"qqxd"},{"n":"诛仙手游","v":"zxsy"},{"n":"妄想山海","v":"wxsh"},{"n":"黎明觉醒：生机","v":"lmjx"},{"n":"庆余年","v":"QYN"},{"n":"我的侠客","v":"wdxk"},{"n":"曙光英雄","v":"sgyx"},{"n":"大话西游手游","v":"dhxysy"},{"n":"战争怒吼","v":"zznh"},{"n":"忘川风华录","v":"wcfhl"},{"n":"新剑侠情缘手游","v":"xjxqysy"},{"n":"重生细胞","v":"csxb"},{"n":"汉家江湖","v":"HJJH"},{"n":"海岛奇兵","v":"hdqb"},{"n":"钢铁力量2","v":"gtll2"},{"n":"仙剑奇侠传九野","v":"xjqxzjy"},{"n":"大唐无双手游","v":"dtwssy"},{"n":"地铁跑酷","v":"dtpk"},{"n":"战舰世界闪击战","v":"zjsjsjz"},{"n":"狂暴之翼","v":"kbzy"},{"n":"横扫千军","v":"hsqj"},{"n":"节奏大爆炸","v":"jzdbz"},{"n":"喵斯快跑","v":"mskp"},{"n":"双子","v":"sz"},{"n":"小美斗地主","v":"xmddz"},{"n":"精灵之境","v":"jlzj"},{"n":"斗罗大陆：武魂觉醒","v":"dldlwhjx"},{"n":"斗罗大陆2绝世唐门","v":"dldl2jstm"},{"n":"战神觉醒","v":"zsjx"},{"n":"九州仙剑传H5","v":"jzxjzh5"},{"n":"荣耀大天使","v":"rydts"},{"n":"蓝月传奇","v":"lycq"},{"n":"凡人修仙传挂机版H5","v":"frxxzgjbh5"},{"n":"攻城掠地","v":"gcld"},{"n":"盗墓笔记","v":"dmbj"},{"n":"拳魂觉醒","v":"qhjx"},{"n":"大天使之剑","v":"dtszj"},{"n":"绝世仙王","v":"jsxw"},{"n":"一刀传世","v":"ydcs"},{"n":"斗罗大陆","v":"dldl"},{"n":"破雪刃","v":"pxr"},{"n":"JJ象棋","v":"jjxq"},{"n":"天姬变","v":"tjb"},{"n":"剑玲珑","v":"jll"},{"n":"火线精英","v":"hxjy"},{"n":"造梦西游OL","v":"zmxyol"},{"n":"奥奇传说手游","v":"aqcssy"},{"n":"战斗吧龙魂","v":"zdblh"},{"n":"剑开仙门","v":"jkxm"},{"n":"狼人对决","v":"lrdj"},{"n":"最终幻想：勇气启示录 幻影战争","v":"hyzz"},{"n":"葫芦娃兄弟","v":"hlwxd"},{"n":"造梦西游4","v":"zmxy4"},{"n":"比特小队","v":"btxd"},{"n":"流言侦探","v":"lyzt"},{"n":"战舰联盟","v":"zjlm"},{"n":"另一个伊甸：超越时空的猫","v":"lygyd"},{"n":"少女前线","v":"snqx"},{"n":"遇见","v":"yj"},{"n":"霓虹深渊：无限","v":"nhsywx"},{"n":"胡莱三国3","v":"hlsg3"},{"n":"奥拉星","v":"alx"},{"n":"先游云游戏","v":"Gamer"},{"n":"万象物语手游","v":"wxwy1"},{"n":"绿茵信仰","v":"lyxy"},{"n":"烟雨江湖","v":"yyjhsy"},{"n":"球球联盟","v":"qqlm"},{"n":"文明与征服","v":"wmyzf"},{"n":"碧蓝航线手游","v":"blhxsy"},{"n":"300大作战","v":"300dzz"},{"n":"2047","v":"2047"},{"n":"第七史诗","v":"dqss"},{"n":"汉末霸业","v":"hmby"},{"n":"EVE星战前夜：无烬星河","v":"evexzqywjxh"},{"n":"少女前线2：追放","v":"sq2zf"},{"n":"弹力果冻","v":"tlgd"},{"n":"火力苏打（T3）","v":"T3"},{"n":"植物大战僵尸2","v":"zwdzjs2"},{"n":"球球英雄","v":"qqyx"},{"n":"悠长假期","v":"ycjq"},{"n":"无悔华夏","v":"whrhx"},{"n":"猫之城","v":"mzc"},{"n":"未定事件簿","v":"wdsjp"},{"n":"白夜极光","v":"byjg"},{"n":"ProjectGAIA","v":"projectgaia"},{"n":"斗罗大陆：魂师对决","v":"dldlhsdj"},{"n":"古墓丽影传说：迷踪","v":"gmlycsmz"},{"n":"漫威对决","v":"mwdj"},{"n":"放置与召唤","v":"fzyzh"},{"n":"我是航海家","v":"wshhj"},{"n":"军团战棋英雄时代","v":"jtzqyxsd"},{"n":"繁荣美食市场物语","v":"frmsscwy"},{"n":"老农种树","v":"lnzs"},{"n":"三国演义：吞噬无界","v":"sgyytswj"},{"n":"偶像梦幻祭2","v":"oxmhj2"},{"n":"卡卡保皇","v":"kkbh"},{"n":"灵猫传","v":"lmz"},{"n":"剑侠世界3","v":"jxsj3"},{"n":"召唤与合成2","v":"zhyhc2"},{"n":"像素时代","v":"xssd"},{"n":"仙侠第一放置","v":"xxdyfz"},{"n":"无尽的拉格朗日","v":"wjdlglr"},{"n":"弓箭手大作战","v":"gjsdzz"},{"n":"挨饿荒野","v":"aehy"},{"n":"诺亚之心","v":"nyzx"},{"n":"闪耀暖暖","v":"synn"},{"n":"物种起源","v":"wzqy"},{"n":"模拟城市：我是市长","v":"mncswssc"},{"n":"重返帝国","v":"cfdg"},{"n":"太古仙尊","v":"tgxz"},{"n":"长安幻想","v":"cahx"},{"n":"火炬之光：无限","v":"hjzgwx"},{"n":"富豪闯三国","v":"fhcsg"},{"n":"拂晓","v":"fx"},{"n":"古剑奇谭木语人","v":"gjqtmyr"},{"n":"火影忍者：忍者新世代","v":"hyrzrzxsd"},{"n":"末日远征","v":"mryz"},{"n":"滚动的天空","v":"gddtk"},{"n":"新斗罗大陆","v":"xdldl"},{"n":"登山赛车","v":"dssc"},{"n":"荒野乱斗（腾讯版）","v":"hyldtxb"},{"n":"小小勇者","v":"xxyz"},{"n":"小冰冰传奇","v":"xbbcq"},{"n":"三国战纪2手游","v":"sgzj2"},{"n":"幸存者危城","v":"xczwc"},{"n":"冒险公社手游","v":"mxgs"},{"n":"欧陆战争5：帝国","v":"olzz5dg"},{"n":"纪念碑谷2","v":"jnbg2"},{"n":"大航海探险物语","v":"dhhtxwy"},{"n":"航海日记","v":"hhrj"},{"n":"一拳超人：最强之男","v":"yqcrzqzn"},{"n":"王国保卫战4","v":"wgbwz4"},{"n":"半世界之旅","v":"bsjzl"},{"n":"奥特曼宇宙英雄","v":"atmyzyx"},{"n":"新三国杀","v":"xsgs"},{"n":"奶块","v":"nk"},{"n":"策魂三国","v":"chsg"},{"n":"奥特曼系列OL","v":"atmxlol"},{"n":"欢喜斗地主","v":"HXDDZ"},{"n":"洪荒文明","v":"hhwm"},{"n":"街头足球","v":"jtzq"},{"n":"同人圣三国蜀汉传","v":"trssgshc"},{"n":"塔防之光","v":"tfzg"},{"n":"我做夫人那些年","v":"wzfrnxn"},{"n":"小小五千年","v":"xxwqn"},{"n":"乖离性百万亚瑟王：环","v":"glxbwyswh"},{"n":"时空猎人","v":"sklr"},{"n":"星际逆战","v":"xjnz"},{"n":"羽毛球高高手","v":"ymqggs"},{"n":"LoveLive! 学园偶像祭","v":"lovelivexyoxj"},{"n":"黑色沙漠手游","v":"hesmsy"},{"n":"魔力宝贝：旅人","v":"mlbblr"},{"n":"大家饿餐厅","v":"dject"},{"n":"魔力宝贝归来","v":"mlbbgl"},{"n":"巅峰极速","v":"dfjs"},{"n":"新盗墓笔记","v":"xdmbj"},{"n":"轩辕传奇手游","v":"XYCQSY"},{"n":"萤火突击国际服","v":"yhtj"},{"n":"武林闲侠","v":"wlxx"},{"n":"淘米游戏","v":"tmyx"},{"n":"无期迷途","v":"wqmt"},{"n":"逆光潜入","v":"ngqr"},{"n":"深空之眼","v":"skzy"},{"n":"CF手游","v":"CFSY"},{"n":"新天龙八部手游","v":"xtlbbsy"},{"n":"尘白禁区","v":"cbjq"},{"n":"原始征途","v":"yszt"},{"n":"全民大灌篮","v":"qmdgl"},{"n":"枪火重生手游","v":"GunfireReborn"},{"n":"火影三国志","v":"g_hysg"},{"n":"网易其它组","v":"g_wyqt"},{"n":"三国战纪手游","v":"sgzjsy"},{"n":"染·钟楼谜团","v":"BOTC"},{"n":"绝区零","v":"jql"},{"n":"重返CODM","v":"RECODM"},{"n":"综合手游","v":"zhsy"},{"n":"IP游戏","v":"ipyx"},{"n":"鸣潮","v":"cm"},{"n":"棋牌游戏","v":"QPYX"},{"n":"奥比岛：梦想国度","v":"abdmxgd"},{"n":"晶核","v":"jhcoa"},{"n":"星之破晓","v":"dhpx"},{"n":"赛尔计划","v":"srjh"},{"n":"SLG综合","v":"SLG"},{"n":"代号：伙伴","v":"DHGB"},{"n":"天使之战","v":"tszz"},{"n":"全明星街球派对","v":"hoopheroes"},{"n":"合金弹头：觉醒","v":"MetalSlug"},{"n":"劲乐幻想","v":"g_jyhx"},{"n":"白荆回廊","v":"BJHL"},{"n":"战地无疆","v":"zdwj"},{"n":"三国志战棋版","v":"g_sgzzqb"},{"n":"一拳超人：世界","v":"yqcrsj"},{"n":"鹅鸭杀手游","v":"GooseDuck"},{"n":"太空杀","v":"SuperSus"},{"n":"大话西游：归来","v":"dhxygl"},{"n":"战火勋章","v":"zhxz"},{"n":"西行纪 燃魂","v":"xxjrh"},{"n":"决胜巅峰","v":"jueshengdianfeng"},{"n":"冒险岛：枫之传说","v":"MapleStory"},{"n":"七人传奇：光与暗之交战","v":"qirenchuanqi"},{"n":"综合桌游","v":"ZHZY"},{"n":"闪耀！优俊少女","v":"PrettyDerby"},{"n":"三角洲行动","v":"DF"},{"n":"二次元游戏","v":"ECYYX"}]}],
        "djry":[{"key":"cateId","name":"分类","init":"TVgame","value":[{"n":"主机游戏","v":"TVgame"},{"n":"刺客信条:英灵殿","v":"AC"},{"n":"马里奥制造","v":"Mario"},{"n":"逃离塔科夫","v":"EFT"},{"n":"命运2","v":"MY2"},{"n":"恐怖游戏","v":"Horror"},{"n":"荒野大镖客","v":"hydbk"},{"n":"灵魂筹码","v":"lhcm"},{"n":"骑马与砍杀","v":"MountAndBlade"},{"n":"只狼","v":"ZL"},{"n":"格斗游戏","v":"FTG"},{"n":"饥荒","v":"DontStarve"},{"n":"全境封锁","v":"qjfs"},{"n":"怀旧游戏","v":"classic"},{"n":"NBA2K","v":"NBA2K"},{"n":"八方旅人","v":"OT"},{"n":"人类一败涂地","v":"Human"},{"n":"环世界","v":"RimWorld"},{"n":"古墓丽影","v":"gmly"},{"n":"鬼泣","v":"DMC"},{"n":"往日不再","v":"WRBZ"},{"n":"仙剑奇侠传","v":"PAL"},{"n":"神秘海域","v":"Uncharted"},{"n":"塞尔达系列","v":"TLoZ"},{"n":"僵尸世界大战","v":"WWZ"},{"n":"足球游戏","v":"zq"},{"n":"橙光","v":"cg"},{"n":"了不起的修仙模拟器","v":"ACS"},{"n":"超级马里奥","v":"SMO"},{"n":"三国志系列","v":"Sangokushi"},{"n":"星际公民","v":"StarCitizen"},{"n":"最终幻想","v":"FF"},{"n":"中土世界：战争之影","v":"MiddleEarth"},{"n":"流放者柯南","v":"Conan"},{"n":"三国群英传","v":"SANGO"},{"n":"无主之地","v":"Bor"},{"n":"辐射","v":"fs"},{"n":"太吾绘卷","v":"twhj"},{"n":"SCUM","v":"Scum"},{"n":"正当防卫","v":"zdfw"},{"n":"以撒的结合","v":"Isaac"},{"n":"文明","v":"CVI"},{"n":"仁王","v":"NIOH"},{"n":"缺氧","v":"ONI"},{"n":"皇牌空战","v":"hpkz"},{"n":"体育游戏","v":"tyyx"},{"n":"海岛大亨","v":"hddh"},{"n":"植物大战僵尸:花园战争系列","v":"PvsZ"},{"n":"蜘蛛侠","v":"Spide"},{"n":"勇者斗恶龙：建造者2","v":"DQB2"},{"n":"遗迹：灰烬重生","v":"Rem"},{"n":"血源","v":"BB"},{"n":"旺达与巨像","v":"SotC"},{"n":"模拟人生","v":"Sims"},{"n":"空洞骑士","v":"HKS"},{"n":"极品飞车","v":"jpfc"},{"n":"胡闹厨房","v":"Overcooked"},{"n":"地铁:离去","v":"ME"},{"n":"生死狙击2","v":"ssjjtwo"},{"n":"三国战纪","v":"sgzj"},{"n":"怀旧FC","v":"edwcy"},{"n":"经典单机","v":"jddj"},{"n":"英雄无敌","v":"HoMM"},{"n":"街机游戏","v":"jjyx"},{"n":"合金装备","v":"MetalGear"},{"n":"红色警戒","v":"hsjj"},{"n":"镜之边缘","v":"MsE"},{"n":"火焰纹章系列","v":"FireEmblem"},{"n":"星露谷物语","v":"Stardew"},{"n":"赛博朋克2077","v":"Cyberpunk"},{"n":"中国式家长","v":"CP"},{"n":"尼尔：机械纪元","v":"NieR"},{"n":"无人深空","v":"NMS"},{"n":"EVOTINCTION","v":"EVOTINCTION"},{"n":"GT赛车7","v":"GT"},{"n":"超级机器人大战","v":"SRW"},{"n":"信长之野望","v":"KOEINOBU"},{"n":"这是我的战争","v":"TWoM"},{"n":"杀戮尖塔","v":"sljt"},{"n":"冰汽时代","v":"Frostpunk"},{"n":"帝国时代","v":"AoEIV"},{"n":"死亡空间","v":"swkj"},{"n":"凯瑟琳Full Body","v":"CFB"},{"n":"足球经理","v":"Football"},{"n":"雨中冒险","v":"RoR"},{"n":"亿万僵尸","v":"Billions"},{"n":"武装突袭","v":"ArmA"},{"n":"石油大亨","v":"Oil"},{"n":"荣耀战魂","v":"Honor"},{"n":"欧洲卡车模拟器","v":"Truck"},{"n":"美国逃亡者","v":"Fugitive"},{"n":"漫漫长夜","v":"mmcy"},{"n":"永恒轮回","v":"Survival"},{"n":"孤岛惊魂","v":"FarCry"},{"n":"都市：天际线","v":"Skylines"},{"n":"盗贼之海","v":"hdzh"},{"n":"Dayz","v":"DayZ"},{"n":"60秒","v":"60S"},{"n":"俄罗斯钓鱼","v":"RF"},{"n":"猎人：荒野的召唤","v":"theHunter"},{"n":"恐怖黎明","v":"GD"},{"n":"看门狗","v":"kmg"},{"n":"真三国无双","v":"DW"},{"n":"泰拉瑞亚","v":"Terraria"},{"n":"UFC","v":"UFC"},{"n":"底特律:变人","v":"Detroit"},{"n":"恶魔城","v":"Castlevania"},{"n":"毁灭战士","v":"Doom"},{"n":"火影忍者：究极忍者风暴","v":"Naruto"},{"n":"无尽地牢","v":"DOTE"},{"n":"坎巴拉太空计划","v":"Kerbal"},{"n":"龙珠：超宇宙","v":"DBX"},{"n":"马里奥赛车","v":"MarioKart"},{"n":"模拟山羊","v":"GoatSim"},{"n":"欧陆风云","v":"EU"},{"n":"乞丐模拟器","v":"HoboToughLife"},{"n":"小偷模拟器","v":"ThiefSimulator"},{"n":"逆转裁判","v":"AceA"},{"n":"超越光速","v":"FTL"},{"n":"植物大战僵尸","v":"PvZ"},{"n":"游戏开发者","v":"GGM"},{"n":"最后的绿洲","v":"LO"},{"n":"大富翁","v":"RichMan"},{"n":"英雄连","v":"yxl"},{"n":"永劫无间","v":"NB"},{"n":"部落与弯刀","v":"BLYWD"},{"n":"森林","v":"Forest"},{"n":"只只大冒险","v":"biped"},{"n":"一起开火车！","v":"Unrailed"},{"n":"主机其他游戏","v":"OG"},{"n":"北境之地","v":"BJZD"},{"n":"temtem","v":"temtem"},{"n":"弹丸论破","v":"dwlp"},{"n":"基佬大乱斗","v":"jldld"},{"n":"僵尸毁灭工程","v":"jshmgc"},{"n":"神力科莎","v":"SLKS"},{"n":"超级兔子人","v":"Bunny"},{"n":"岛屿生存者","v":"Sur"},{"n":"盟军敢死队","v":"COMM"},{"n":"冬日计划","v":"drjh"},{"n":"泰坦陨落","v":"Titanfall"},{"n":"四海兄弟","v":"shxd"},{"n":"创世理想乡","v":"Craftopia"},{"n":"柯娜：精神之桥","v":"Kena"},{"n":"幽灵线：东京","v":"GTO"},{"n":"Solar Ash","v":"Ash"},{"n":"BUGSNAX","v":"BUGSNAX"},{"n":"生化危机4重制版","v":"ResidentEvil"},{"n":"Grounded","v":"Grounded"},{"n":"Superliminal","v":"Superliminal"},{"n":"Omno","v":"Omno"},{"n":"Röki","v":"Roki"},{"n":"Undungeon","v":"Undungeon"},{"n":"糖豆人","v":"FallGuys"},{"n":"渡神纪","v":"Gods"},{"n":"Aeolis Tournament","v":"Aeolis"},{"n":"猛兽派对","v":"Animals"},{"n":"Olija","v":"Olija"},{"n":"Creaks","v":"Creaks"},{"n":"暗影火炬城","v":"FIST"},{"n":"阿尔比恩","v":"Albion"},{"n":"Uragun","v":"Uragun"},{"n":"鬼谷八荒","v":"GGBH"},{"n":"Muse Dash","v":"MuseDash"},{"n":"恐惧之间","v":"Fearsurrounds"},{"n":"孤岛惊魂6","v":"FarCry6"},{"n":"怪物猎人","v":"MonsterHunterRise"},{"n":"黑神话：悟空","v":"BlackMythWuKong"},{"n":"仁王2","v":"Nioh2"},{"n":"三国志14","v":"THREEKINGDOMSXIV"},{"n":"杀手3","v":"Hitman3"},{"n":"双人成行","v":"ittakestwo"},{"n":"Scrapnaut","v":"Scrapnaut"},{"n":"租房达人","v":"TheTenants"},{"n":"狙击手：幽灵战士契约2","v":"SniperContracts2"},{"n":"全面战争","v":"TotalWarWARHAMMER"},{"n":"复体","v":"TheComplex"},{"n":"战争机器：战术小队","v":"GearsTactics"},{"n":"侠之道","v":"PathOfWuxia"},{"n":"海绵宝宝：比奇堡的冒险","v":"BattleforBikini"},{"n":"奇妙探险队2","v":"CuriousExpedition2"},{"n":"刺客信条：奥德赛","v":"Odyssey"},{"n":"星球大战：前线","v":"Battlefront"},{"n":"Moonray","v":"Moonray"},{"n":"灵魂旅人","v":"SpiritFarerlhlr"},{"n":"面容","v":"Visage"},{"n":"破门而入2：北方特遣队","v":"DoorKickers2"},{"n":"俄罗斯方块效应：连接","v":"TetrisEffect"},{"n":"SD高达G世纪：起源","v":"SDGundamG"},{"n":"东方计划：不可思议的幻想乡","v":"TouHou"},{"n":"Fate/EXTELLA","v":"FateEXTELLA"},{"n":"临终：重生试炼","v":"DYINGReborn"},{"n":"虚拟现实乐园","v":"VRWorlds"},{"n":"妖精剑士F","v":"FairyFencerF"},{"n":"苍翼默示录：神观之梦","v":"CentralFiction"},{"n":"晚班","v":"LateShift"},{"n":"子弹风暴","v":"Bulletstorm"},{"n":"巡警","v":"BeatCop"},{"n":"耻辱之日","v":"DayofInfamy"},{"n":"狙击精英4","v":"SniperElite4"},{"n":"三国志13：威力加强版","v":"Sangokushi13"},{"n":"热血物语：地下世界","v":"RiverCityRansom"},{"n":"史诗战争模拟器","v":"BattleSimulator"},{"n":"银河护卫队","v":"Guardians"},{"n":"闪乱神乐：少女们的选择","v":"SenranKagura"},{"n":"幽灵行动：荒野","v":"GhostReconWildland"},{"n":"白色情人节","v":"WhiteDay"},{"n":"美国职业摔角联盟2K17","v":"WWE2K"},{"n":"誓死坚守","v":"UntilWeDie"},{"n":"喷射侠","v":"Splasher"},{"n":"双截龙4","v":"DoubleDragon4"},{"n":"地下蚁国","v":"Undergrowth"},{"n":"九张羊皮纸","v":"NineParchments"},{"n":"咒语力量3","v":"Spellforce3"},{"n":"小兵大战","v":"Warpips"},{"n":"维京人 人中之狼","v":"VikingsWofM"},{"n":"你好邻居","v":"Helloneighbor"},{"n":"寻找天堂","v":"findparadise"},{"n":"画中世界","v":"Gorogoa"},{"n":"桥梁工程师传送门","v":"bridgecons"},{"n":"现代战争","v":"ModernCombat"},{"n":"SCP：秘密实验室","v":"scpsl"},{"n":"绯红结系","v":"SCARLETNEXUS"},{"n":"罪恶装备：STRIVE","v":"GuiltyGear"},{"n":"骑士精神2","v":"Chivalry2"},{"n":"Rune Knights","v":"RuneKnights"},{"n":"最后的咒语","v":"TheLastSpell"},{"n":"红至日2：幸存者","v":"TheRed2"},{"n":"真女神转生3","v":"ShinMegami3"},{"n":"速降王者","v":"Descenders"},{"n":"工业崛起","v":"RiseIndustry"},{"n":"征服的荣耀：围城","v":"SIEGE"},{"n":"前往中世纪","v":"GoMedieval"},{"n":"Arid","v":"Arid"},{"n":"伊始之地","v":"TerraNil"},{"n":"进击的巨人2","v":"AttackonTitan2"},{"n":"航海日记2","v":"hhrj2"},{"n":"隐龙传：影踪","v":"HiddenDragon"},{"n":"魔域之书","v":"Bookofdevil"},{"n":"诸神灰烬：救赎","v":"AshofGods"},{"n":"自由人：游击战争","v":"Freeman"},{"n":"战国无双5","v":"SWarriors5"},{"n":"死亡教堂","v":"DeathCathedral"},{"n":"灵魂能力6","v":"SoulCalibur6"},{"n":"不要喂食猴子","v":"NotFeedMonkeys"},{"n":"古剑奇谭3","v":"GuJianqitan3"},{"n":"迷城重生","v":"RebornCity"},{"n":"剑士","v":"KenshiJS"},{"n":"GRIS","v":"GRIS"},{"n":"古剑奇谭：永夜","v":"gujianyongye"},{"n":"核爆RPG","v":"ATOMRPG"},{"n":"Below","v":"Below"},{"n":"嗜血印","v":"BloodySpell"},{"n":"伊苏9","v":"Ys9"},{"n":"兽人必须死3","v":"OrcsDie3"},{"n":"狙击精英VR","v":"SniperEliteVR"},{"n":"遗忘之城","v":"ForgotCity"},{"n":"Last Stop","v":"LastStop"},{"n":"从军","v":"jointhearmy"},{"n":"石炉","v":"Stonehearth"},{"n":"狂热运输2","v":"TransportFever2"},{"n":"机甲战士5","v":"MechWarrior5"},{"n":"分手装修","v":"ToolUP"},{"n":"PICO PARK","v":"PICOPARK"},{"n":"光明记忆：无限","v":"Brightmemory"},{"n":"秘馆疑踪","v":"HeavenDust"},{"n":"英雄传说：创之轨迹","v":"HajimariNOKiseki"},{"n":"战地系列","v":"Battlefiel"},{"n":"塞尔达传说：天空之剑HD","v":"SkywardSword"},{"n":"国王的恩赐2","v":"KingsBounty2"},{"n":"脑航员2","v":"Psychonauts2"},{"n":"九十六号公路","v":"Road96"},{"n":"FORECLOSED","v":"FORECLOSED"},{"n":"RiMS Racing","v":"RiMSRacing"},{"n":"漫威银河护卫队","v":"GuardiansGalaxy"},{"n":"剑侠图","v":"JianXiaTu"},{"n":"审判之逝","v":"Lostjudgment"},{"n":"艾尔登法环","v":"ELDENRING"},{"n":"互动派对","v":"INTERACTIVEPARTY"},{"n":"极限竞速：地平线5","v":"ForzaHorizon5"},{"n":"使命召唤系列","v":"CALLOFDUTYCOD"},{"n":"网吧模拟器","v":"InternetCS"},{"n":"The Anacrusis","v":"TheAnacrusis"},{"n":"文字游戏","v":"WordGame"},{"n":"消逝的光芒2","v":"DyingLight2"},{"n":"战神：诸神黄昏","v":"GodofWarRagnarok"},{"n":"师父","v":"SIFU"},{"n":"海上狼人杀","v":"DreadHunger"},{"n":"最终幻想：起源","v":"STRANGEROFPARADISE"},{"n":"HordeCore","v":"HordeCore"},{"n":"Indies’ Lies","v":"IndiesLies"},{"n":"霍格沃茨之遗","v":"HogwartsLegacy"},{"n":"太荒初境","v":"TalesofWild"},{"n":"Deck of Ashes","v":"DeckofAshes"},{"n":"星空","v":"Starfield"},{"n":"隐秘的角落","v":"YinMiDeJiaoLuo"},{"n":"江湖客栈","v":"TheJianghu"},{"n":"Ilysia","v":"Ilysia"},{"n":"Project Q","v":"ProjectQ"},{"n":"Pummel Party","v":"PummelParty"},{"n":"Holomento","v":"Holomento"},{"n":"Overprime","v":"Overprime"},{"n":"森林之子","v":"SonsOfTheForest"},{"n":"弈仙牌","v":"yixianpai"},{"n":"夜族崛起","v":"VRising"},{"n":"漫威SNAP","v":"MarvelSnap"},{"n":"魔力宝贝","v":"CrossGate"},{"n":"木卫四协议","v":"CallistoProtocol"},{"n":"罗马复兴","v":"RomanRenaissance"},{"n":"风暴之门","v":"StormGate"},{"n":"暗邪西部","v":"EvilWest"},{"n":"堕落之主","v":"LordsofFallen"},{"n":"High on Life","v":"HighonLife"},{"n":"匹诺曹的谎言","v":"LiesofP"},{"n":"逃生：试炼","v":"TheOutlastTrials"},{"n":"战锤40K：暗潮","v":"40KDarktide"},{"n":"Isonzo","v":"Isonzo"},{"n":"索尼克 未知边境","v":"SonicFrontiers"},{"n":"漂泊牧歌","v":"WanderingVillage"},{"n":"塞尔达传说：王国之泪","v":"TEARSKINGDOM"},{"n":"破碎线","v":"Shatterline"},{"n":"卧龙：苍天陨落","v":"Wolong"},{"n":"卡库远古封印","v":"KAKU"},{"n":"原子之心","v":"AtomicHeart"},{"n":"霓虹入侵者","v":"FromSpace"},{"n":"Warhaven","v":"Warhaven"},{"n":"宝可梦：朱/紫","v":"ScarletandViolet"},{"n":"第一后裔","v":"TheFirstDescendant"},{"n":"铳墓G.O.R.E.","v":"GUNGRAVEGORE"},{"n":"Kingshunt","v":"Kingshunt"},{"n":"漫威暗夜之子","v":"MarvelMidnightSuns"},{"n":"奇怪的RPG","v":"WeirdRPG"},{"n":"Evercore Heroes","v":"EvercoreHeroes"},{"n":"东方：平野孤鸿","v":"MomentinEast"},{"n":"神之天平","v":"ASTLIBRARevision"},{"n":"伊克西翁","v":"IXION"},{"n":"主机一起看","v":"zjyqk"},{"n":"社交互动游戏","v":"SJHDYX"},{"n":"Divine Knockout","v":"DivineKnockout"},{"n":"巫师系列","v":"TheWitcher"},{"n":"至暗时刻","v":"DarkandDarker"},{"n":"江湖十一","v":"Jianghu11"},{"n":"XDefiant","v":"XDefiant"},{"n":"刺客信条：幻景","v":"ACMirage"},{"n":"Warlander","v":"Warlander"},{"n":"狂野之心","v":"WildHearts"},{"n":"Scars Above","v":"ScarsAbove"},{"n":"Pacific Drive","v":"PacificDrive"},{"n":"收获日3","v":"PAYDAY"},{"n":"浮生箓2：九九行歌","v":"FloatingLife"},{"n":"The Front","v":"TheFront"},{"n":"最终幻想16","v":"FinalFantasyXVI"},{"n":"街头霸王","v":"StreetFighter"},{"n":"Tchia","v":"Tchia"},{"n":"魔戒：咕噜","v":"Gollum"},{"n":"Prison Life 2","v":"PrisonLife"},{"n":"Innchanted","v":"Innchanted"},{"n":"Life by You","v":"LifebyYou"},{"n":"Eresys","v":"Eresys"},{"n":"Pax Dei","v":"PaxDei"},{"n":"Teravit","v":"Teravit"},{"n":"Caliber","v":"Caliber"},{"n":"沙盒与副本：英勇之地","v":"HerosLand"},{"n":"Coridden","v":"Coridden"},{"n":"Unrecord","v":"Unrecord"},{"n":"Deducto 2","v":"Deducto2"},{"n":"装甲核心6：境界天火","v":"ArmoredCore"},{"n":"Wayfinder","v":"Wayfinder"},{"n":"迷瘴纪事","v":"MiasmaChronicles"},{"n":"Minigame Madness","v":"MinigameMadness"},{"n":"Only Up","v":"onlyup"},{"n":"天文世界","v":"AstroWorld"},{"n":"学园构想家","v":"SchoolHomeroom"},{"n":"Jusant","v":"JUSANT"},{"n":"潜水员戴夫","v":"DAVETHEDIVER"},{"n":"GYLT","v":"GYLT"},{"n":"遗迹2","v":"RemnantII"},{"n":"索利斯堡","v":"FortSolis"},{"n":"Towerborne","v":"Towerborne"},{"n":"33 Immortals","v":"33Immortals"},{"n":"Wildmender","v":"Wildmender"},{"n":"How 2 Escape","v":"How2Escape"},{"n":"漫威蜘蛛侠2","v":"MarvelSpiderman2"},{"n":"博德之门3","v":"BG3"},{"n":"Eternights","v":"Eternights"},{"n":"Project F","v":"ProjectF"},{"n":"BaldMan Climbs Up","v":"BaldManClimbsUp"},{"n":"FC24","v":"FC24"},{"n":"NBA 2K24","v":"NBA2K24"},{"n":"超级马里奥兄弟：惊奇","v":"MarioWonder"},{"n":"蛮荒志异","v":"Taleswild"}]}],
        "kjwh":[{"key":"cateId","name":"分类","init":"qezb","value":[{"n":"数码科技","v":"smkj"},{"n":"纪录片","v":"jlp"},{"n":"成年教育","v":"jiaoyu"},{"n":"人文社科","v":"Humanities"},{"n":"企鹅直播","v":"qezb"}]}],
        "yl":[{"key":"cateId","name":"分类","init":"ecy","value":[{"n":"二次元","v":"ecy"},{"n":"一起看","v":"yqk"},{"n":"音乐","v":"music"},{"n":"户外","v":"HW"},{"n":"美食","v":"ms"},{"n":"原创IP","v":"ip"},{"n":"心动派对","v":"xdpd"},{"n":"音遇恋人","v":"yinyu"},{"n":"星秀","v":"xingxiu"},{"n":"心动FM","v":"dtxs"},{"n":"娱乐推荐","v":"yltj"},{"n":"中国地质大学（武汉）","v":"CUGWH"}]}],
        "yp":[{"key":"cateId","name":"分类","init":"paidui","value":[{"n":"派对","v":"paidui"},{"n":"心动FM.","v":"DIANT"},{"n":"一起玩","v":"yiqiwan"}]}],
        "voice":[{"key":"cateId","name":"分类","init":"yyjy","value":[{"n":"语音交友","v":"yyjy"},{"n":"音乐之声","v":"yyzs"},{"n":"连麦互动","v":"lianmaihudong"},{"n":"娱乐开黑","v":"ylkh"}]}]
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
            url = host + '/api/live/getRecommendByPlatform?platform=douyu&size=20&page=' + pg;
        } else {
            url = host + '/api/live/getRecommendByPlatformArea?platform=douyu&size=20&area=' + tid + '&page=' + pg;
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
            url = host + '/api/room/list?page=' + pg;
        } else {
            url = host + '/api/room/list?type=' + extend.cateId + '&page=' + pg;
        }
        const data = JSON.parse(await request(url));
        videos = _.map(data.data.list, (it) => {
            return {
                vod_id: it.rid,
                vod_name: it.roomName,
                vod_pic: it.roomSrc,
                vod_remarks: it.nickname,
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
    const data = JSON.parse(await request('http://live.yj1211.work/api/live/getRoomInfo?platform=douyu&roomId=' + id));
    const video = data.data;
    const vodList = [];
    let vod = {
        vod_id: video.roomId,
        vod_name: video.roomName,
        vod_pic: video.roomPic,
        vod_remarks: video.categoryName,
        type_name: video.categoryName,
        vod_director: video.ownerName,
        vod_actor: '',
        vod_content: video.online + '人在线',
        vod_year: '',
        vod_area: '',   
    };
    vodList.push(
        {
            title: "JustLive",
            url: "https://getplayurl.lmteam.repl.co/live?platform=douyu&rid=" + video.roomId
        },
        {
            title: "112114",
            url: "http://epg.112114.xyz/douyu/" + video.roomId
        },
        {
            title: "AOIS",
            url: "https://www.aois.eu.org/live/douyu/" + video.roomId
        },
        {
            title: "GIPTV",
            url: "https://www.goodiptv.club/douyu/" + video.roomId
        },
        {
            title: "KDTV",
            url: "http://maomao.kandiantv.cn/douyu1.php?id=" + video.roomId
        }
    );
    vod.vod_play_from = video.platForm;
    vod.vod_play_url = _.map(vodList, (it)=> {
        return it.title + "$" + it.url
    }).join("#");
    return JSON.stringify({
        list: [vod],
    });
}

async function play(flag, id, flags) {
    return JSON.stringify({
        parse: 0,
        url: id,
    });
}

async function search(wd, quick) {
    const resp = await requestRaw(host + '/api/search/liveRoom?did=10000000000000000000000000001501&limit=40&offset=0&sk=' + wd, 'post');
    const data = JSON.parse(resp.content);
    let videos = [];
    for (const vod of data.data.list) {
        videos.push({
            vod_id: vod.roomId,
            vod_name: vod.roomName,
            vod_pic: vod.roomSrc,
            vod_remarks: vod.nickname,
        });
    }
    return JSON.stringify({
        list: videos,
    });
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