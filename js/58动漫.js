muban.vfed.二级.title = 'h1&&Text;.fed-col-md3:eq(0)&&Text';
muban.vfed.二级.desc = '.fed-col-md3:eq(3)&&Text;;;.fed-col-md6--span:eq(0)&&Text;.fed-col-md6--span:eq(1)&&Text';
muban.vfed.二级.tabs = '.nav-tabs&&li';
muban.vfed.二级.lists = '.myui-content__list:eq(#id)&&li';
var rule = {
    title: '58动漫[漫]',
    模板: 'vfed',
    host: 'http://www.ting38.com',
    url: '/search.php?page=fypage&searchtype=5&tid=fyclassfyfilter',
    class_parse: '.fed-pops-navbar&&li;a&&Text;a&&href;.*/(.*?).html',
    play_parse: true,
    lazy: "js:var html=JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);var url=html.url;if(html.encrypt=='1'){url=unescape(url)}else if(html.encrypt=='2'){url=unescape(base64Decode(url))}if(/m3u8|mp4/.test(url)){input=url}else{input}",
    limit: 6,
    filterable: 1,//是否启用分类筛选,
    filter_url: '&order={{fl.by}}&area={{fl.area}}&year={{fl.year}}',
    filter: 'H4sIAAAAAAAAA+2TzUrDQBSF32XWWWTSX/sq0kXUAYsmhVCFULKSutJURAzFghu1EQoGLMWmtE+TjOYtzM9k7gU37pPdnO/MvTN3DjMmlPQOx+SM2aRHbKZbRCGmbrBUxZtVtN2l+lI/v2D5NjPDEz+58jOcCuIoBdVUrSFYvkRcA65hToFTzFXgKuL0QPJ0iXgXeBfzDvAO5m3gbcxbwFuYN4E3MYd5KZ6XwrwU5jWGFhM8Xzr9zCme/ciGR+fufRxO/zw699aJtxINRoN0a9k4CkMePAjndDCSBnf9n9s7YRwPDYOZJ9mxfYVodeaVy7xRZ165zJsoc91iOsp8HsQ34T8zj18WyexaUCFKL3mb8a8P4Qkh66YB3+zLukLIW3uvfL4UnhCy5/N7/LQrexZC1i0X33u3rCuE9D4DqBNC3mWyjraP5V0KgbOpv0QVvoTzCxTHT5vwCAAA',
    filter_def: {
        1: {cateId: '1'},
        2: {cateId: '2'},
        3: {cateId: '3'},
        4: {cateId: '4'}
    },
    searchUrl: '/search.php?page=fypage&searchword=**&searchtype=',
    搜索: '.fed-list-item;a&&title;a&&data-original;.fed-list-remarks&&Text;a&&href',
}