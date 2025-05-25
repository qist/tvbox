var rule={
  title: "剧狗狗",
  host: "https://www.jugougou.me",
  url: "/vodtype/fyclass-fypage.html",
  searchUrl: "/vodsearch/**----------fypage---.html",
  searchable: 2,
  quickSearch: 0,
  filterable: 1,
  filter: "",
  filter_url: "",
  filter_def: "",
  headers: {
    "User-Agent": "MOBILE_UA"
  },
  timeout: 5000,
  class_parse: ".foornav li;a&&Text;a&&href;/(\\d+)\\.html",
  cate_exclude: "Netflix|今日更新|专题列表|排行榜",
  play_parse: true,
  lazy:$js.toString(()=>{
    input = {parse:1,url:input,js:'document.querySelector("#playleft iframe").contentWindow.document.querySelector("#start").click();'};
  }),
  double: false,
  推荐: "*",
  一级: ".ewave-vodlist__item;a&&title;a&&data-original;.pic-text&&Text;a&&href",
  二级: {
    title: ".ewave-content__detail&&.title&&Text;.data:eq(0)&&Text",
    img: ".pic&&img&&data-original",
    desc: ".data:eq(5)&&Text;.data:eq(3)&&Text;.data:eq(2)&&Text;;",
    content: ".art-content&&Text",
    tabs: ".ewave-pannel:has(.ewave-content__playlist)",
    lists: ".ewave-content__playlist:eq(#id)&&li",
    tab_text: "h3&&Text",
    list_text: "body&&Text",
    list_url: "a&&href"
  },
  detailUrl: "",
  搜索: "*"
}