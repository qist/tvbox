var rule = {
    title:'评书随身听',
    host:'https://www.psmp3.com',
    // url:'/fyclass/fypage.html',
    url:'/fyfilter/fypage.html',
    filterable:1,//是否启用分类筛选,
    filter_url:'{{fl.cateId}}',
    filter:{
        "ykc":[{"key":"cateId","name":"分类","value":[{"n":"全部","v":"ykc"},{"n":"袁阔成三国演义","v":"ykc-sgyy"},{"n":"袁阔成水泊梁山","v":"ykc-sbls"},{"n":"袁阔成封神演义","v":"ykc-fsyy"},{"n":"袁阔成薛刚反唐","v":"ykc-xgft"},{"n":"袁阔成林海雪原","v":"ykc-lhxy"},{"n":"袁阔成楚汉相争","v":"ykc-chxz"},{"n":"袁阔成彭公案","v":"ykc-pga"},{"n":"袁阔成烈火金刚","v":"ykc-lhjg"},{"n":"袁阔成金钱镖","v":"ykc-jqb"},{"n":"袁阔成三气周瑜","v":"ykc-sqzy"},{"n":"袁阔成群英会","v":"ykc-qyh"},{"n":"袁阔成长坂雄风","v":"ykc-cbxf"},{"n":"袁阔成平原枪声","v":"ykc-pyqs"},{"n":"袁阔成暴风骤雨","v":"ykc-bfzy"},{"n":"野火春风斗古城","v":"ykc-yhcfdgc"}]}],
        "stf":[{"key":"cateId","name":"分类","value":[{"n":"全部","v":"stf"},{"n":"单田芳隋唐演义","v":"stf-styy"},{"n":"单田芳乱世枭雄","v":"stf-lsxx"},{"n":"单田芳白眉大侠","v":"stf-bmdx"},{"n":"单田芳童林传","v":"stf-tlz"},{"n":"单田芳水浒传","v":"stf-shz"},{"n":"单田芳三侠五义","v":"stf-sxwy"},{"n":"单田芳三侠剑","v":"stf-sxj"},{"n":"单田芳大明演义","v":"stf-dmyy"},{"n":"单田芳龙虎风云会","v":"stf-lhfyh"},{"n":"单田芳三国演义","v":"stf-sgyy"},{"n":"单田芳薛家将","v":"stf-xjj"},{"n":"单田芳清官册","v":"stf-qgc"},{"n":"单田芳小五义","v":"stf-xwy"},{"n":"单田芳铁扇怪侠","v":"stf-tsgx"},{"n":"单田芳楚汉争雄","v":"stf-chzx"}]}],
        "tly":[{"key":"cateId","name":"分类","value":[{"n":"全部","v":"tly"},{"n":"田连元水浒传","v":"tly-shz"},{"n":"田连元杨家将","v":"tly-yjj"},{"n":"田连元隋唐演义","v":"tly-styy"},{"n":"田连元三侠五义","v":"tly-sxwy"},{"n":"田连元刘秀传","v":"tly-lxz"},{"n":"田连元小八义","v":"tly-xby"},{"n":"田连元包公案","v":"tly-bga"},{"n":"田连元大话成语","v":"tly-dhcy"},{"n":"田连元双镖记","v":"tly-sbj"},{"n":"田连元海青天","v":"tly-hqt"},{"n":"田连元辽沈战役","v":"tly-lszy"},{"n":"田连元血溅津门","v":"tly-xjjm"},{"n":"田连元镜花缘","v":"tly-jhy"},{"n":"田连元孙庞斗智","v":"tly-spdz"},{"n":"田连元孙膑与庞涓","v":"tly-sbypj"}]}],
        "llf":[{"key":"cateId","name":"分类","value":[{"n":"全部","v":"llf"},{"n":"刘兰芳岳飞传","v":"llf-yfz"},{"n":"刘兰芳杨家将全传","v":"llf-yjjqz"},{"n":"刘兰芳呼家将","v":"llf-hjj"},{"n":"刘兰芳赵匡胤演义","v":"llf-zkyyy"},{"n":"刘兰芳朱元璋演义","v":"llf-zyzyy"},{"n":"刘兰芳红楼梦","v":"llf-hlm"},{"n":"刘兰芳五凤朝阳刀","v":"llf-wfcyd"},{"n":"刘兰芳新岳飞传","v":"llf-xyfz"},{"n":"刘兰芳杨家将","v":"llf-yjj"},{"n":"刘兰芳西唐演义","v":"llf-xtyy"},{"n":"刘兰芳樊梨花","v":"llf-flh"},{"n":"刘兰芳大唐侠女","v":"llf-dtxn"},{"n":"刘兰芳黑虎传","v":"llf-hhz"},{"n":"刘兰芳洪武大帝","v":"llf-hwdd"},{"n":"刘兰芳契丹萧太后","v":"llf-qdxth"}]}],
        "llr":[{"key":"cateId","name":"分类","value":[{"n":"全部","v":"llr"},{"n":"连丽如东汉演义","v":"llr-dhyy"},{"n":"连丽如大隋唐","v":"llr-dst"},{"n":"连丽如三国演义","v":"llr-sgyy"},{"n":"连丽如雍正剑侠图","v":"llr-yzjxt"},{"n":"连丽如红楼梦","v":"llr-hlm"},{"n":"连丽如龙图公案","v":"llr-ltga"},{"n":"连丽如鹿鼎记","v":"llr-ldj"},{"n":"连丽如刘公案","v":"llr-lga"},{"n":"连丽如康熙私访","v":"llr-kxsf"},{"n":"连丽如东周列国","v":"llr-dzlg"},{"n":"连丽如十二女侠","v":"llr-senx"},{"n":"连丽如智圣东方朔","v":"llr-zsdfs"},{"n":"连丽如侠义英雄传","v":"llr-xyyxz"},{"n":"连丽如蓬莱剑侠","v":"llr-pljx"},{"n":"连丽如康熙大帝","v":"llr-kxdd"}]}],
        "zsz":[{"key":"cateId","name":"分类","value":[{"n":"全部","v":"zsz"},{"n":"张少佐大明剑侠","v":"zsz-dmjx"},{"n":"张少佐雍正剑侠图","v":"zsz-yzjxt"},{"n":"张少佐天龙八部","v":"zsz-tlbb"},{"n":"张少佐昆仑剑侠","v":"zsz-kljx"},{"n":"张少佐多情剑客无情剑","v":"zsz-dqjkwqj"},{"n":"张少佐笑傲江湖","v":"zsz-xajh"},{"n":"张少佐射雕英雄传","v":"zsz-sdyxz"},{"n":"张少佐倚天屠龙记","v":"zsz-yttlj"},{"n":"张少佐神雕侠侣","v":"zsz-sdxl"},{"n":"张少佐钟凌传","v":"zsz-zlz"},{"n":"张少佐明史奇侠","v":"zsz-msqx"},{"n":"张少佐中国血案","v":"zsz-zgxa"},{"n":"张少佐神剑惊天刺雍正","v":"zsz-sjjtcyz"},{"n":"张少佐豪气惊天","v":"zsz-hqjt"},{"n":"张少佐乱世恩仇","v":"zsz-lsec"}]}],
        "tzy":[{"key":"cateId","name":"分类","value":[{"n":"全部","v":"tzy"},{"n":"田战义李自成","v":"tzy-lzc"},{"n":"田战义秘密列车","v":"tzy-mmlc"},{"n":"田战义民国风云","v":"tzy-mgfy"},{"n":"田战义夕照紫禁城","v":"tzy-xzzjc"},{"n":"田战义风雨关山","v":"tzy-fygs"},{"n":"田战义聊斋志异","v":"tzy-lzzy"},{"n":"田战义侠义豪杰","v":"tzy-xyhj"},{"n":"风云人物蒋介石","v":"tzy-fyrwjjs"},{"n":"田战义绝密行动","v":"tzy-jmxd"},{"n":"田战义燕子李三传奇","v":"tzy-yzlscq"},{"n":"田战义中国古代奇案","v":"tzy-zggdqa"},{"n":"田战义火牛阵","v":"tzy-hnz"},{"n":"田战义县委书记","v":"tzy-xwsj"},{"n":"田战义摧毁神风号","v":"tzy-chsfh"},{"n":"田战义仇大娘","v":"tzy-cdn"}]}]
    },
    filter_def:{
        ykc:{cateId:'ykc'},
        stf:{cateId:'stf'},
        tly:{cateId:'tly'},
        llf:{cateId:'llf'},
        llr:{cateId:'llr'},
        zsz:{cateId:'zsz'},
        tzy:{cateId:'tzy'}
    },
    searchUrl:'/so/**_fypage.html',
    searchable:2,
    quickSearch:0,
    headers:{
        'User-Agent':'MOBILE_UA'
    },
    timeout:5000,
    class_parse: '.list-navi&&li:gt(1);a&&Text;a&&href;/(\\w+).html',
    play_parse:true,
    lazy:'js:input={jx:0,url:input,parse:0}',
    limit:6,
    推荐:'*',
    一级:'#post_list_box&&li;h2&&Text;img&&src;.f_r&&span:eq(3)&&Text;a&&href',
    二级:{
        title:'h1&&Text;.view&&Text',
        img:'img&&src',
        desc:'.view&&Text;;;.lmname&&Text;.author&&Text',
        content:'.jAsrPyf4&&p:eq(1)&&Text',
        // tabs:'js:TABS=["评书随身听"]',
        lists:'js:var VideoListJson;VideoListJson=eval(html.split("audio: ")[1].split("}\)")[0]);let list1=[];VideoListJson.forEach(function(it){list1.push(it.name.strip()+"$https:"+it.url)});LISTS=[list1];',
    },
    搜索: '*',
}