import { Crypto, load, _ } from './lib/cat.js';

let key = 'misaav';
let url = 'https://missav789.com';
let siteKey = '';
let siteType = 0;

const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1';

const cookie = {};
const default_filter=[
		{
			key:'filters',
			name:'过滤',
			init:'',
			value:[
				{n:'所有',v:''},
				{n:'单人作品',v:'individual'},
				{n:'中文字幕',v:'chinese-subtitle'},
				]
		},
		{
			key:'sort',
			name:'排序',
			init:'',
			value:[
				{n:'發行日期',v:'released_at'},
				{n:'最近更新',v:'published_at'},
				{n:'收藏數',v:'saved'},
				{n:'今日瀏覽數',v:'today_views'},
				{n:'本週瀏覽數',v:'weekly_views'},
				{n:'本月瀏覽數',v:'monthly_views'},
				{n:'瀏覽數',v:'views'},
				]
		}
	]

async function request(reqUrl, referer, mth, data, hd) {
    const headers = {
        'User-Agent': UA,
        Cookie: _.map(cookie, (value, key) => {
            return `${key}=${value}`;
        }).join(';'),
    };
    if (referer) headers.referer = encodeURIComponent(referer);
    let res = await req(reqUrl, {
        method: mth || 'get',
        headers: headers,
        data: data,
        postType: mth === 'post' ? 'form' : '',
    });
    if (res.headers['set-cookie']) {
        const set_cookie = _.isArray(res.headers['set-cookie']) ? res.headers['set-cookie'].join(';') : res.headers['set-cookie'];
        const cks = set_cookie.split(';');
        for (const c of cks) {
            const tmp = c.trim();
            if (tmp.startsWith('result=')) {
                cookie.result = tmp.substring(7);
                return await request(reqUrl, reqUrl, 'post', {
                    result: cookie.result,
                });
            } else if (tmp.startsWith('esc_search_captcha=1')) {
                cookie.esc_search_captcha = 1;
                delete cookie.result;
                return await request(reqUrl);
            }
        }
        // console.log(res.headers['set-cookie']);
    }
    return res.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
    //let html=await request(url)
}

async function home(filter) {
    
    let type_list="最近更新=new+新作上市=release+今日热门=today-hot+本周热门=weekly-hot+本月热门=monthly-hot+专题=tags+女优大全=actresses+女优排行榜=actresses/ranking+类型=genres+发行商=makers".split('+')
    let filter_list="无码流出=uncensored-leak+中文字幕=chinese-subtitle+素人SIRO=siro+LUXU=luxu+GANA=gana+PrestigePremium=maan+S-CUTE=scute+ARA=ara+无码FC2=fc2+HEYZO=heyzo+东京热=tokyohot+一本道=1pondo+Caribbeancom=caribbeancom+Caribbeancompr=caribbeancompr+10musume=10musume+pacopacomama=pacopacomama+Gachinco=gachinco+XXX-AV=xxxav+人妻斩=marriedslash+顽皮4610=naughty4610+顽皮0930=naughty0930+麻豆传媒=madou+TWAV=twav+Furuke=furuke".split('+')
    let classes = _.map(type_list, (s) => {
      let typeId = s.split('=')
        return {
            type_id: typeId[1],
            type_name: typeId[0],
        };
        
    });
    let filterss = _.map(filter_list, (s) => {
        let fobj = s.split('=')
        return {
            v: fobj[1],
            n: fobj[0],
        };
    });
    let filterObj = {
      "tags":[
        {
          key:'tag',
          name:'主題',
          init:'uncensored-leak',
          value:filterss
        }
      ],
      "actresses":default_filter,
      "genres":default_filter,
      "makers":default_filter,
      "actresses/ranking":default_filter,
      
    };
    return JSON.stringify({
        class: classes,
        filters: filterObj,
    });
}

async function homeVod() {
  const min=1
  const max=100
  const range =max-min
  const random= Math.random()
  const result=min + Math.round(range*random)
  
  const html=await request(url+'/random/'+result)
  const $ =load(html)
  const items = $('div.thumbnail')
  let videos=_.map(items,(item)=>{
    const a = $(item).find('a')[0]
    const aa=$($(item).find('a')[1]).text()
   // console.log(a)
    const vid= a.attribs.href
    const img =$(a).find('img')[0].attribs.src
    const title=$(a).find('img')[0].attribs.alt
    return {
           vod_id: vid,
            vod_name: title,
            vod_pic:img,
            vod_remarks:aa
    }
  } )
  return JSON.stringify({
        list: videos,
    })
}

async function category(tid, pg, filter, extend) {
    if (pg <= 0) pg = 1;
    let html=null,$=null,items=null,videos=null
    switch(tid){
      case 'makers':
        html = await request(url+'/'+ tid+'?page='+pg)
         $=load(html)
         items = $('div.grid.grid-cols-2.gap-4 > div')
         videos=_.map(items,(item)=>{
          const a = $(item).find('a')
         console.log(a)
          const vid= a[0].attribs.href
          const rem =$(a[1]).text().replaceAll('\n','')
          const title=$(a[0]).text().replaceAll('\n','')
          
          return {
                 vod_id: vid,
                  vod_name: title,
                  vod_remarks:rem,
                  vod_tag:'folder'
          }
        } )
        return JSON.stringify({
              page: parseInt(pg),
              pagecount: 9999,
              limit: 20,
              total: 99999,
              list: videos,
          })
        break
      case 'genres':
        html = await request(url+'/'+ tid+'?page='+pg)
         $=load(html)
         items = $('div.grid.grid-cols-2.gap-4 > div')
         videos=_.map(items,(item)=>{
          const a = $(item).find('a')
         console.log(a)
          const vid= a[0].attribs.href
          const rem =$(a[1]).text().replaceAll('\n','')
          const title=$(a[0]).text().replaceAll('\n','')
          
          return {
                 vod_id: vid,
                  vod_name: title,
                  vod_remarks:rem,
                  vod_tag:'folder'
          }
        } )
        return JSON.stringify({
              page: parseInt(pg),
              pagecount: 9999,
              limit: 20,
              total: 99999,
              list: videos,
          })
        break
      case 'actresses/ranking':
        html = await request(url+'/'+ tid+'?page='+pg)
         $=load(html)
         items = $('ul.grid.grid-cols-2.gap-4 > li')
         videos=_.map(items,(item)=>{
          const a = $(item).find('a')
          const vid= a[0].attribs.href
          const imgs=$(a[0]).find('img')[0]
          const img=imgs?imgs.attribs.src:''
          const rem =$($(item).find('span')[0]).text().replaceAll('\n','')
          const title=$($(item).find('h4')[0]).text().replaceAll('\n','')
          
          return {
                 vod_id: vid,
                  vod_name: title,
                  vod_remarks: rem,
                  vod_pic:img,
                  vod_tag:'folder'
          }
        } )
        return JSON.stringify({
              page: parseInt(pg),
              pagecount: 9999,
              limit: 20,
              total: 99999,
              list: videos,
              style: {
				        type: "list",
				        "ratio": 0.68
				      }
          })
        break
      case 'actresses':
        html = await request(url+'/'+ tid+'?page='+pg)
         $=load(html)
         items = $('ul.grid.grid-cols-2.gap-4 > li')
         videos=_.map(items,(item)=>{
          const a = $(item).find('a')
          const vid= a[0].attribs.href
          const imgs=$(a[0]).find('img')[0]
          const img=imgs?imgs.attribs.src:''
          const rem =$($(item).find('p')[0]).text().replaceAll('\n','')
          const title=$($(item).find('h4')[0]).text().replaceAll('\n','')
          
          return {
                 vod_id: vid,
                  vod_name: title,
                  vod_remarks: rem,
                  vod_pic:img,
                  vod_tag:'folder'
          }
        } )
        return JSON.stringify({
              page: parseInt(pg),
              pagecount: 9999,
              limit: 20,
              total: 99999,
              list: videos,
          })
        break
      default:
        let ttid=''
        if(tid=='tags')
        {
          ttid=extend.tag
        }else{
          ttid=tid
        }
        let urls=''
        if(tid.startsWith('http')){
          urls=tid+'?page='+pg+'&filters='+extend.filters+'&sort='+extend.sort
          
        }else{
          urls=url+'/'+ ttid+'?page='+pg
        }
        
        html = await request(urls)
         $=load(html)
         items = $('div.thumbnail')
         videos=_.map(items,(item)=>{
          const a = $(item).find('a')[0]
          const aa=$($(item).find('a')[1]).text()
         // console.log(a)
          const vid= a.attribs.href
          const img =$(a).find('img')[0].attribs['data-src']
          const title=$(a).find('img')[0].attribs.alt
          return {
                 vod_id: vid,
                  vod_name: title,
                  vod_pic:img,
                  vod_remarks:aa
          }
        } )
        return JSON.stringify({
              page: parseInt(pg),
              pagecount: 9999,
              limit: 20,
              total: 99999,
              list: videos,
          })
        break
        
    }
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: pgCount,
        limit: 20,
        total: 20 * pgCount,
        list: videos,
    });
}

function stripHtmlTag(src) {
    return src
        .replace(/<\/?[^>]+(>|$)/g, '')
        .replace(/&.{1,5};/g, '')
        .replace(/\s{2,}/g, ' ');
}

async function detail(id) {
    const html = await request(id);
    const $ = load(html);
    let script=html.match(/let source[\s\S]+?eval.+/)[0];
    let sourceFhd=""
    let source842=''
    let source1280=''
    let source=''
    eval(script);
    let list=[];
    let items=[];
    list.push({name:"默认",url:sourceFhd||source||""})
    list.push({name:"720p",url:source1280||""})
    list.push({name:"480p",url:source842||""})
    let vod = {
        vod_id: id,
        vod_pic: '',
        vod_remarks: '',
        vod_content: '',
    };
    
    const playlist = []
    _.map(list, (a) => {
      if (a.url!=''){
        playlist.push(a.name +'$' + a.url);
        
      }
    });
    vod.vod_play_from = 'missav';
    vod.vod_play_url = playlist.join('#');
    return JSON.stringify({
        list: [vod],
    });
}

async function play(flag, id, flags) {
  return JSON.stringify({
            parse: 0,
            url: id,
        });
    
}

async function search(wd, quick,pg) {
	if (pg <= 0) pg = 1;
    const html = await request(url + '/search/' + wd+"?page="+pg);
    const $=load(html)
        const items = $('div.thumbnail')
        let videos=_.map(items,(item)=>{
          const a = $(item).find('a')[0]
         // console.log(a)
          const vid= a.attribs.href
          const img =$(a).find('img')[0].attribs['data-src']
          const title=$(a).find('img')[0].attribs.alt
          return {
                 vod_id: vid,
                  vod_name: title,
                  vod_pic:img
          }
        } )
        return JSON.stringify({
              page: parseInt(pg),
              pagecount: 9999,
              limit: 20,
              total: 99999,
              list: videos,
          })
}

export function __jsEvalReturn() {
    return {
        init: init,
        home: home,
        homeVod: homeVod,
        category: category,
        detail: detail,
        play: play,
        search: search,
    };
}
