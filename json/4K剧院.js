var rule = {
  // 资源类型
  类型: '影视', 
  // 资源标题
  title: '4K-AV', 
  // 网站主机地址
  host: 'https://4k-av.com', 
  // 页面的 URL 地址
  url: '/fyclass/page-fypage.html', 
  // 搜索的 URL 格式
  searchUrl: '/s?q=**&page=fypage', 
  // 搜索功能的级别（可能表示搜索能力的程度）
  searchable: 2, 
  // 是否支持快速搜索（0 表示不支持）
  quickSearch: 0, 
  // 请求的头部信息
  headers: {
    'User-Agent': 'IOS_UA',
  },
  // 请求超时时间（5000 毫秒）
  timeout: 5000, 
  // 分类解析的选择器和正则表达式，用于提取分类信息
  class_parse: '#cate_list&&li;a&&title;a&&href;/(\\w+)/', 
  // 要排除的分类（此处是“成人视频”分类）
  cate_exclude: '成人视频', 
  // 播放解析设置
  play_parse: true, 
  // 懒加载的 JavaScript 函数
  lazy: $js.toString(() => {
      // 设置输入对象，包含解析、URL 和头部信息
      input = {parse: 1, url: input, header:rule.headers};
  }),
  // 是否支持双模式（具体含义需根据上下文确定）
  double: true, 
  // 推荐内容的提取规则
  推荐: '#recommlist;ul&&li;h2&&Text;img&&src;span&&Text;a&&href', 
  // 一级内容的提取规则
  一级: '#MainContent_newestlist&&.NTMitem;h2&&Text;img&&src;div.resyear&&Text;a&&href',


二级: {
    title: 'h2&&Text;#MainContent_tags&&Text',
    img: 'img&&src',
    desc: '#MainContent_videodetail&&label&&Text;#MainContent_videodetail&&label:eq(2)&&Text;;;',
    content: '',
    tabs: '',
    
lists: $js.toString(() => {

  LISTS = [];
  pdfa(html,'body&&.flexcolumn').forEach((it) => {
    let lis = pdfa(it,'#rtlist&&li');
    let lis1 = [];
    // 获取第一个元素
    let firstItem = lis[0];
  //  let firstTT = pdfh(firstItem,'source&&src');
    let firstTT = request(input).match(/<source src="(.*?)"/)[1];
    if (firstTT && firstTT!== '') {
    let tt = pdfh(firstItem,'.screenshot&&span&&Text');
      lis1.push(tt + '$' + firstTT);
    }
    // 从第二个元素开始遍历 'lis' 数组
    for(let index = 1; index < lis.length; index++) { 
      // 获取当前遍历到的 'lis' 数组中的元素
      let item = lis[index];
      // 获取 'item' 元素内的文本内容
      let tt = pdfh(item,'.screenshot&&span&&Text');
      let uu = pd(item,'a&&href',MY_URL);     
        lis1.push(tt + '$' + uu);
    }
    // 将 'lis1' 数组添加到 'LISTS' 数组
    LISTS.push(lis1);
  });
}),




},

  
  // 搜索的提取规则
  搜索: '*',
  // 新增的集数搜索筛选条件
  searchFilters: {
    // 不同集数范围的筛选条件
    episodes: {
      few: '1-10',
      medium: '11-30',
      many: '31+'
    }
  }
}