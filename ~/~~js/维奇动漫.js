var rule = {
    title: '维奇动漫[漫]',
    host: 'https://www.uiviki.com',
    hostJs: '',
    headers: {'User-Agent': 'MOBILE_UA'},
    编码: 'utf-8',
    timeout: 5000,
    homeUrl: '/',
    url: '/anime-select-fyfilter.html',
    filter_url: '{{fl.cateId}}-{{fl.area}}-{{fl.by}}-{{fl.class}}-----fypage---{{fl.year}}',
    detailUrl: '',
    searchUrl: '/anime-so/wd/**.html',
    searchable: 1,
    quickSearch: 1,
    filterable: 1,
    class_name: '连载动漫&国漫&日漫',
    class_url: 'lianzai&guoman&riman',
    filter_def: {
        lianzai: {cateId: 'lianzai'},
        guoman: {cateId: 'guoman'},
        riman: {cateId: 'riman'}
    },
    proxy_rule: '',
    sniffer: 0,
    isVideo: '',
    play_parse: true,
    parse_url: '',
    lazy: '',
    limit: 9,
    double: false,
    推荐: '*;*;*;*;*',
//列表;标题;图片;描述;链接;详情(可不写)
    一级: '.vodlist li;a&&title;img&&data-echo;.vodlist-title&&Text;a&&href',
    二级: {
        "title": ".show_right_info:eq(0)&&li:eq(0)&&Text",
        "img": "img&&src",
        "desc": "",
        "content": ".overlay-text&&Text",
//线路数组
        "tabs": ".tab&&.now&&li",
//线路标题
        "tab_text": "",
//播放数组 选集列表
        "lists": ".playlist:eq(#id)&&a",
//选集标题
        "list_text": "",
//选集链接
        "list_url": "a&&href"
    },
//列表;标题;图片;描述;链接;详情(可不写)
    搜索: '*',
    filter: 'H4sIAAAAAAAAA+2U207iUBSG73mMXvMEvorxomPITDOIiegkDiHhoFiRKcUonUYHJIYRD6hYQ6DF8jLdPbzFFNehJvMCXvSOb/+stddh9y9lpLwiF37KirS2nilJ33P70pq0mZeLRSkrFeStXIzBxBG9k5h/yPm9+GC9JBXiY3E4iuqj1XEMUjkLp+Gb45/N8RSBNH82SzQE1hb3HzQA0oTWF+oFaggcN/7ruVcUB0BacLsMp03UEDhn4zQybyknAMfddMTcoTgAjhseJRoC16L+9rsG1QJAmrd89BwTNQS+b9iLxmd0HwBp8W/fOkcNgWd9fRhVFjRrAK5T18TjPdUJwLXMTTG0qBYAzll5C1yNcgJwnaYrdJXqBOA4vRVYNBcEnoveCx46NBcAzlkfh4MK5QTgHmoPvnVHPQBwzks7njDlBGCtehKoE9IAuPfFnRhRHALHaaNAb1AcAGtXA3ExJg2A61zUgvMW1QnA++tb3lyn/QFwXHUq6m2KA+B5LnXRpK8LgeOeO8n+ELjOruGbNtUJwJoxFLMZaQCsvTj+Ae0W4cO79uzj5F2vgPfX0uKvgPYHwD0cvUb1KvUAwHGuFl33KQ6A+/vVDWt0HwJrzYlY0jeGwPdVW+KSekdI3uefUDvm9/kOnNMdiBvaEULiPQ3RfmHveYfyRjnLZvllP3FKXzsVdvs/p/SNaWS8Yo5dJf4rv0bb9p/py/+m7BaTep8OhEpvsbi5vZNbXZvZyGakr3vbW3IhNezUsFPDTg07NexPb9g7SurXqV+nfp36derXn96vM+V/+YAXbBURAAA='
}