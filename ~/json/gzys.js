rule = {
    host: 'http://gz360.tv',
    class_name: '电影&电视剧&动漫&综艺',
    class_url: '3&4&5&6',
    //homeVod: '.van-swipe-item;img&&alt;a&&href;img&&data-src;.movie-cover&&Text',
    categoryVodJS: `
      var params = '{"pid":' + classId+',"pageSize":24,"page":' +page+'}';
      var enData = aesEncode(params, '181cc88340ae5b2b', '4423d1e2773476ce', 'hex');
      request('https://api.zaqohu.com/H5/Category/GetChoiceList', {params: enData}, {}, 'post');|||
      var res = aesDecode(JSON.parse(html).data, '181cc88340ae5b2b', '4423d1e2773476ce','hex');
      let json = JSON.parse(res);
      json.list.forEach(function(item){
        videos.push({
          vod_id: item.vod_id,
          vod_name: item.c_name,
          vod_pic: item.c_pic,
          vod_remarks: item.vod_continu,
          vod_year: item.vod_douban_score,
        });
      });
    `,
    detailVodJS: `
      var params = '{"vod_id":"'+input+'"}';
      var enData = aesEncode(params, '181cc88340ae5b2b', '4423d1e2773476ce', 'hex');
      request('https://api.zaqohu.com/H5/Resource/GetVodInfo', {params: enData}, {}, 'post');|||
      var res = aesDecode(JSON.parse(html).data, '181cc88340ae5b2b', '4423d1e2773476ce','hex');
      var json = JSON.parse(res).vodInfo;
      videoDetail = {
        vod_id: json.vod_id,
        vod_name: json.vod_name,
        vod_pic: json.pic,
        vod_year: json.vod_year,
        vod_area: json.vod_area,
        vod_remarks: json.vod_continu,
        vod_actor: json.vod_actor,
        vod_director: json.vod_director,
        vod_content: json.vod_use_content,
      };
      var params = '{"vod_id":"'+input+'","pageSize":"10000","page":"1"}';
      var enData = aesEncode(params, '181cc88340ae5b2b', '4423d1e2773476ce', 'hex');
      request('https://api.zaqohu.com/H5/Resource/GetOnePlayList', {params: enData}, {}, 'post');|||
      var res = aesDecode(JSON.parse(html).data, '181cc88340ae5b2b', '4423d1e2773476ce','hex');
      var json = JSON.parse(res);
      videoDetail.vod_play_url = _.map(json.urls, item => item.name + '$' + item.url).join('#');
      videoDetail.vod_play_from = 'leospring';
      videos.push(videoDetail);
    `,
  }