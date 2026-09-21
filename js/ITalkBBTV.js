function getNuxtData(html) {
    var m = html.match(/window\.__NUXT__=([\s\S]*?);<\/script>/);
    if (!m) {
        return null;
    }
    try {
        return eval(m[1]);
    } catch (e) {
        return null;
    }
}

function pickPic(obj) {
    if (!obj) return '';
    var poster = (((obj.images || {}).poster) || [])[0];
    var landscape = (((obj.images || {}).landscape) || [])[0];
    var imgUrl = obj.imgUrl || '';
    return poster || landscape || imgUrl;
}

function joinStars(stars) {
    if (!Array.isArray(stars)) return '';
    return stars.map(function (it) {
        return it.name || '';
    }).filter(Boolean).join('/');
}

function uniqueById(list) {
    var map = {};
    return (list || []).filter(function (it) {
        var id = it && it.vod_id;
        if (!id || map[id]) return false;
        map[id] = 1;
        return true;
    });
}

function makeVodFromSeries(series, fallbackName) {
    if (!series) return null;
    var categoryId = Array.isArray(series.category_id) ? (series.category_id[0] || '') : (series.category_id || '');
    var rootId = series.root_id || '';
    var seriesId = series.id || series.series_id || '';
    var route = rootId === '66b1d25cf2dde82c215f9b59' ? 'shortsPlay' : 'play';
    var typeName = series.rootName || series.categoryName || '';
    var remark = series.latest_episode_name || series.latest_episode_shortname || (series.episode_count ? ('更新至' + series.episode_count) : '');
    return {
        vod_id: route + '$' + seriesId,
        vod_name: series.name || fallbackName || '',
        vod_pic: pickPic(series),
        vod_remarks: remark,
        vod_year: series.released_at ? new Date(series.released_at * 1000).getFullYear() + '' : '',
        type_name: typeName,
        vod_content: series.description || '',
        vod_actor: joinStars(((series.stars || {}).actor) || []),
        vod_director: joinStars(((series.stars || {}).director) || [])
    };
}

function makeVodFromCard(card) {
    if (!card) return null;
    var series = card.series || card.target || card;
    var vod = makeVodFromSeries(series, card.name || card.title || '');
    if (!vod) return null;
    if (!vod.vod_name) {
        vod.vod_name = card.name || card.title || '';
    }
    if (!vod.vod_pic) {
        vod.vod_pic = pickPic(card) || ((card.image || {}).poster || '') || ((card.image || {}).landscape || '');
    }
    if (!vod.vod_remarks) {
        vod.vod_remarks = card.description || '';
    }
    return vod;
}

var rule = {
    title: 'ITalkBBTV',
    host: 'https://www.italkbbtv.com',
    url: '/fyclass/fyfilter',
    searchable: 2,
    quickSearch: 1,
    filterable: 0,
    play_parse: true,
    class_name: '电视剧&电影&综艺&动画',
    class_url: 'drama/62c670dc1dca2d424404499c&movie/62ac4ef36e0b5a13ed291544&variety/62ce7417c7daaa4a5d3fea14&cartoon/62ac4e6e4beefe53586478ca',
    headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
        'Referer': 'https://www.italkbbtv.com/'
    },
    limit: 24,
    推荐: '*',
    一级: $js.toString(() => {
        var link = input;
        if (MY_PAGE && MY_PAGE > 1) {
            link += (link.indexOf('?') > -1 ? '&' : '?') + 'page=' + MY_PAGE;
        }
        var html = request(link);
        var nuxt = getNuxtData(html);
        var list = [];
        if (nuxt && nuxt.state && nuxt.state.pageList) {
            var parts = MY_CATE.split('/');
            var alias = parts[0];
            var cid = parts[1];
            var keyMap = {
                drama: 'dramaSeriesLists',
                movie: 'movieSeriesLists',
                variety: 'varietySeriesLists',
                cartoon: 'cartoonSeriesLists',
                shorts: 'shortsSeriesLists'
            };
            var store = nuxt.state.pageList[keyMap[alias]] || {};
            var data = store[cid] || {};
            list = data.series || [];
        }
        VODS = uniqueById(list.map(function (it) {
            return makeVodFromSeries(it);
        }).filter(Boolean));
    }),
    二级: $js.toString(() => {
        var parts = input.split('$');
        var route = parts[0] || 'play';
        var sid = parts[1] || '';
        var html = request(HOST + '/' + route + '/' + sid);
        var nuxt = getNuxtData(html);
        var play = (((nuxt || {}).state || {}).play) || {};
        var info = play.SeriesInfo || {};
        var eps = play.EpisodeList || [];
        var vod = makeVodFromSeries(info) || { vod_id: input };
        var tabs = route === 'shortsPlay' ? 'ITalkBB短剧' : 'ITalkBB';
        var playUrl = eps.map(function (ep) {
            var name = ep.shortname || ep.name || '';
            return name + '$' + route + '@' + sid + '@' + (ep.id || '');
        }).filter(Boolean).join('#');
        vod.vod_id = input;
        vod.vod_name = info.name || vod.vod_name || '';
        vod.vod_pic = pickPic(info) || vod.vod_pic || '';
        vod.type_name = info.rootName || info.categoryName || vod.type_name || '';
        vod.vod_content = info.description || vod.vod_content || '';
        vod.vod_actor = joinStars((((info || {}).stars || {}).actor) || []);
        vod.vod_director = joinStars((((info || {}).stars || {}).director) || []);
        vod.vod_remarks = info.latest_episode_name || info.latest_episode_shortname || vod.vod_remarks || '';
        vod.vod_play_from = tabs;
        vod.vod_play_url = playUrl;
        VOD = vod;
    }),
    搜索: $js.toString(() => {
        var html = request(HOST + '/?keyword=' + encodeURIComponent(KEY));
        var nuxt = getNuxtData(html);
        var list = [];
        if (nuxt && nuxt.data && nuxt.data[0]) {
            var data = nuxt.data[0];
            var banners = data.bannerData || [];
            var groups = data.serverGroupDataList || [];
            banners.forEach(function (it) {
                list.push(makeVodFromCard(it));
            });
            groups.forEach(function (g) {
                (g.list || []).forEach(function (it) {
                    list.push(makeVodFromCard(it));
                });
            });
        }
        list = uniqueById(list.filter(function (it) {
            if (!it || !it.vod_name) return false;
            var text = [it.vod_name, it.vod_remarks, it.vod_content, it.type_name].join(' ');
            return text.indexOf(KEY) > -1;
        }));
        VODS = list;
    }),
    lazy: $js.toString(() => {
        var parts = input.split('@');
        var route = parts[0] || 'play';
        var sid = parts[1] || '';
        var eid = parts[2] || '';
        var url = HOST + '/' + route + '/' + sid;
        if (eid) {
            url += '?ep=' + eid;
        }
        input = {
            jx: 0,
            parse: 1,
            url: url
        };
    })
};
