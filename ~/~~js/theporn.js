var rule = {
    title: 'theporn',
    host: 'https://theporn.cc',
    url: '/fyclass/fypage',
    searchUrl: '/search/**/fypage?',
    searchable: 2,
    quickSearch: 0,
    headers: {
        'User-Agent': 'PC_UA',
    },
    timeout: 5000,
    class_name: '全站&最佳影片&推荐&日本无码&欧美&日本AV&VR&动画&人妻&巨乳&肛交&熟女&少女&少妇&制服&学生&女教师&长腿&角色扮演&足交&口交&群P&颜射&自慰&强奸&接吻&处女&SM&按摩&中出&护士&女同&办公室&潮吹&黑人&自拍&中国&欧美&日本&韩国&俄罗斯&印度&泰国&台湾&香港',
    class_url: 'categories/all&video/best/2023-10&categories/recommended&jav/uncensored&eu&jav&vr&cartoon&categories/wife&categories/big_tits&categories/anal&categories/MILF&categories/teen&categories/young_woman&categories/uniform&categories/student&categories/female_teacher&categories/long_legs&categories/cosplay&categories/footjob&categories/oral_sex&categories/group_sex&categories/facial&categories/masturbation&categories/rape&categories/kiss&categories/virgin&categories/sm&categories/massage&categories/creampie&categories/nurse&categories/lesbian&categories/office&categories/squirting&categories/ebony&categories/amateur&categories/chinese&categories/eu&categories/japan&categories/south_korean&categories/russian&categories/india&categories/thailand&categories/taiwan&categories/hongkong',
    play_parse: true,

    lazy: '',
    一级: '.video-list .avdata-outer;a&&img&&alt;img&&data-src;.duration&&Text;a&&href',
    二级: '*',
    搜索: '*',
}