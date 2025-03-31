/**
 * 传参 ?type=url&params=http://122.228.85.203:1000@泽少1
 * 传参 ?type=url&params=http://122.228.85.203:1000@泽少2
 */

var rule = {
    title: 'APPV2[模板]',
    author: '道长',
    version: '20241012 beta1',
    update_info: `
20241012:
1.根据群友嗷呜的appv2模板修改成可传参源，类似采集之王用法传参
`.trim(),
    host: '',
    url: '/api.php/app/video?tid=fyclassfyfilter&limit=20&pg=fypage',
    filter_url: '',
    filter: {},
    homeUrl: '/api.php/app/index_video',
    detailUrl: '/api.php/app/video_detail?id=fyid',
    searchUrl: '/api.php/app/search?text=**&pg=fypage',
    parseUrl: '',
    searchable: 2,
    quickSearch: 1,
    filterable: 1,
    headers: {
        'User-Agent': 'okhttp/4.1.0'
    },
    params: 'http://122.228.85.203:1000$http://122.228.85.203:1000/play?url=',
    hostJs: $js.toString(() => {
        HOST = rule.params.split('$')[0];
    }),
    预处理: $js.toString(() => {
        log(`传入参数:${rule.params}`);
        let _host = rule.params.split('$')[0];
        rule.parseUrl = rule.params.split('$')[1];
        let _url = _host.rstrip('/') + '/api.php/app/nav?token';
        let _headers = {'User-Agent': 'Dart/2.14 (dart:io)'};
        let html = request(_url, {headers: _headers});
        let data = JSON.parse(html);
        let _classes = [];
        let _filter = {};
        let _filter_url = '';
        let dy = {"class": "类型", "area": "地区", "lang": "语言", "year": "年份", "letter": "字母", "by": "排序"};
        let jsonData = data.list;
        for (let k = 0; k < jsonData.length; k++) {
            let hasNonEmptyField = false;
            let _obj = {
                type_name: jsonData[k].type_name,
                type_id: jsonData[k].type_id,
            };
            _classes.push(_obj);
            for (let key in dy) {
                if (key in jsonData[k].type_extend && jsonData[k].type_extend[key].trim() !== "") {
                    hasNonEmptyField = true;
                    break
                }
            }
            if (hasNonEmptyField) {
                _filter[String(jsonData[k].type_id)] = [];
                for (let dkey in jsonData[k].type_extend) {
                    if (dkey in dy && jsonData[k].type_extend[dkey].trim() !== "") {
                        if (k === 0) {
                            _filter_url += `&${dkey}={{fl.${dkey}}}`
                        }
                        let values = jsonData[k].type_extend[dkey].split(',');
                        let valueArray = values.map(value => ({"n": value.trim(), "v": value.trim()}));
                        _filter[String(jsonData[k].type_id)].push({"key": dkey, "name": dy[dkey], "value": valueArray})
                    }
                }
            }
        }
        rule.classes = _classes;
        rule.filter = _filter;
        rule.filter_url = _filter_url;
    }),
    class_parse: $js.toString(() => {
        input = rule.classes;
    }),
    play_parse: true,
    lazy: $js.toString(() => {
        if (!/^http/.test(input)) {
            input = rule.parseUrl + input
        } else {
            input = {
                url: input,
                parse: 0,
                header: ''
            }
        }

    }),
    推荐: $js.toString(() => {
        let data = JSON.parse(request(input)).list;
        let com = [];
        data.forEach(item => {
            if (Array.isArray(item.vlist) && item.vlist.length !== 0) {
                com = com.concat(item.vlist)
            }
        })
        VODS = com
    }),
    一级: $js.toString(() => {
        VODS = JSON.parse(request(input)).list
    }),
    二级: $js.toString(() => {
        VOD = JSON.parse(request(input)).data
    }),
    搜索: '*',
}