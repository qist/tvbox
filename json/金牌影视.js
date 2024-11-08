var rule = {
  title: '金牌影院',
  host: 'https://m.cfkj86.com',
  url: '/api/mw-movie/anonymous/video/list?pageNum=fypage&pageSize=30&sort=1&sortBy=1&type1=fyclass',
  searchUrl: '/api/mw-movie/anonymous/video/searchByWordPageable?keyword=**&pageNum=fypage&pageSize=12&type=false',
  headers: {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Referer': 'https://www.cfkj86.com/'
  },
  searchable: 2,
  quickSearch: 0,
  filterable: 0,
  class_name: '电影&电视剧&综艺&动漫',
  class_url: '1&2&3&4',
  limit: 6,
  double: false,
  play_parse:true,
  lazy:$js.toString(()=>{
     let pid = input.split('/')[5]
     let nid = input.split('/')[7]
     const t = new Date().getTime()
     eval(getCryptoJS)
     let signkey = 'id='+pid+'&nid='+nid+'&key=cb808529bae6b6be45ecfab29a4889bc&t='+t
     const key = CryptoJS.SHA1(CryptoJS.MD5(signkey).toString()).toString()
     let json_data = JSON.parse(request('https://www.cfkj86.com/api/mw-movie/anonymous/v1/video/episode/url?id='+pid+'&nid='+nid,{headers: {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'deviceid': 'c6bce57d-bb62-4db7-96cd-265dfb2a79cf',
    'sign': key,
    't': t
    }}))
    log(json_data)
     let link = json_data.data.playUrl
     input={url:link,header:rule.headers}

  }),
  一级: $js.toString(()=>{
        let d = []
        let url = ''
        const t = new Date().getTime()
        const signkey = 'pageNum='+MY_PAGE+'&pageSize=30&sort=1&sortBy=1&type1='+MY_CATE+'&key=cb808529bae6b6be45ecfab29a4889bc&t='+t
        const key = CryptoJS.SHA1(CryptoJS.MD5(signkey).toString()).toString()
        const list = JSON.parse(request(input,{headers:{
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'deviceId': 'c6bce57d-bb62-4db7-96cd-265dfb2a79cf',
            'sign': key,
            't': t 
        }})).data.list
        list.forEach((it)=>{
            url = 'https://www.cfkj86.com/detail/'+it.vodId
            d.push({
              title: it.vodName,
              desc:it.vodRemarks,
              img:it.vodPic,
              url:url
            })
        })
        setResult(d)
  }),
  二级: {
    title: 'h1&&Text',
    tabs: '.top a',
    lists: '.main-list-sections__BodyArea-sc-8bb7334b-2 .listitem a',
  },
  搜索: $js.toString(()=>{
    const t = new Date().getTime()
     eval(getCryptoJS)
     let pg = MY_PAGE
     let signkey = 'keyword='+KEY+'&pageNum='+pg+'&pageSize=12&type=false&key=cb808529bae6b6be45ecfab29a4889bc&t='+t
     const key = CryptoJS.SHA1(CryptoJS.MD5(signkey).toString()).toString()
      let html = JSON.parse(request(input,{headers: {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'deviceid': '58a80c52-138c-48fd-8edb-138fd74d12c8',
    'sign': key,
    't': t
    }}))
      let data = html.data.list
      let d = []
      data.forEach(it=>{
        let reurl = 'https://www.cfkj86.com/detail/'+it.vodId
        d.push({
          title: it.vodName,
          desc:it.vodVersion,
          img:it.vodPic,
          url:reurl
        })
      })
    setResult(d)
  }),
}