muban.mxpro.二级.title = 'h1&&Text;.module-info-tag&&Text';
muban.mxpro.二级.desc = '.module-info-item:eq(4)&&Text;;;.module-info-item-content:eq(1)&&Text;.module-info-item-content:eq(0)&&Text';
muban.mxpro.二级.tabs = '#y-playList&&span';
muban.mxpro.二级.lists = '.module-play-list:eq(#id)&&a';
var rule = {
	title:'桃子影视', //原91free
	模板:'mxpro',
	host:'https://www.taozi007.com',
	url:'/show/fyclass--------fypage---.html',
    headers:{
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'DNT': '1',
    'Pragma': 'no-cache',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Cookie': '__51vcke__KOfCv4E7m6sGPKS0=7531925e-234b-592c-88fb-5e27dc5c6a88; __51vuft__KOfCv4E7m6sGPKS0=1720324224220; showBtn=true; guardok=WasjNYb09JIaojsJ/S+KShFkARhQHdnBxrO4++HKVp+o6rejwvH/0eK6+xUWGVtl/4OaehKwNFqWOlg7e6bQRw==; __51uvsct__KOfCv4E7m6sGPKS0=3; mx_style=black; PHPSESSID=ujne091om1t08498dhsqardr1n; mac_history_mxpro=%5B%7B%22vod_name%22%3A%22%E7%AC%AC%E4%BA%8C%E6%AC%A1%E5%88%9D%E8%A7%81%22%2C%22vod_url%22%3A%22https%3A%2F%2Fwww.taozi007.com%2Fplay%2F67544-2-1.html%22%2C%22vod_part%22%3A%22%E7%AC%AC01%E9%9B%86%22%7D%2C%7B%22vod_name%22%3A%22AR%E7%89%A9%E8%AF%AD%22%2C%22vod_url%22%3A%22https%3A%2F%2Fwww.taozi007.com%2Fplay%2F56467-1-1.html%22%2C%22vod_part%22%3A%221080P%22%7D%2C%7B%22vod_name%22%3A%22%E9%99%86%E5%9C%B0%E9%94%AE%E4%BB%99%22%2C%22vod_url%22%3A%22https%3A%2F%2Fwww.taozi007.com%2Fplay%2F66963-2-1.html%22%2C%22vod_part%22%3A%22%E7%AC%AC1%E9%9B%86%22%7D%2C%7B%22vod_name%22%3A%22%E5%85%A8%E8%81%8C%E9%AB%98%E6%89%8B%20%E7%AC%AC%E4%B8%89%E5%AD%A3%22%2C%22vod_url%22%3A%22https%3A%2F%2Fwww.taozi007.com%2Fplay%2F12936-2-2.html%22%2C%22vod_part%22%3A%22%E7%AC%AC02%E9%9B%86%22%7D%2C%7B%22vod_name%22%3A%22%E6%97%B6%E5%85%89%E4%BB%A3%E7%90%86%E4%BA%BA%E5%89%A7%E7%89%88%22%2C%22vod_url%22%3A%22https%3A%2F%2Fwww.taozi007.com%2Fplay%2F66735-1-1.html%22%2C%22vod_part%22%3A%22%E7%AC%AC01%E9%9B%86%22%7D%5D; __vtins__KOfCv4E7m6sGPKS0=%7B%22sid%22%3A%20%225f801cfe-55b8-50cf-82c3-5ad27b9592c5%22%2C%20%22vd%22%3A%208%2C%20%22stt%22%3A%20662233%2C%20%22dr%22%3A%20201754%2C%20%22expires%22%3A%201720776998094%2C%20%22ct%22%3A%201720775198094%7D'
  },
	class_parse: '.navbar-items&&a[href*=type];a&&title;a&&href;(\\d+).html',
	    lazy: $js.toString(() => {
        var html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
        var url = html.url;
  if (html.encrypt == '1') {
    url = unescape(url);
  } else if (html.encrypt == '2') {
    url = unescape(base64Decode(url));
  }
  
    let Code = {};
    let code=request(HOST + '/static/js/playerconfig.js');
   
       eval(code + '\nCode=MacPlayerConfig;');
        let jx = HOST+Code.player_list[html.from].parse;
        if (jx == '') {
            jx =  HOST+Code.parse
        }
      log(jx)
      
      if(/feidaozy|1080zyk|subm3u8/.test(html.from)){
      
      input={
      url: url,
      parse:0,
      jx:0
      
      }
      
    }else if (/qiyi|qq|youku|mgtv/.test(html.from)){
    
    let api="https://jx.taozi007.com/player/ec.php?code=tz&if=1&url="
    let 请求=request(api+ url, {
                    headers: {
                        'Referer': ""
                    }
                })
       let config={};
       let 链接 =请求.match(/let ConFig.*}/)[0]
          log('链接:'+链接)
            eval(链接 + '\nconfig=ConFig');
              
            log('url:'+config.config.uid)
              eval(getCryptoJS())             
    function decryptVideoUrl(encryptedUrl, uid) {
    const key = CryptoJS.enc.Utf8.parse('2890' + uid + 'tB959C');
    const iv = CryptoJS.enc.Utf8.parse('2F131BE91247866E');
    const decrypted = CryptoJS.AES.decrypt(encryptedUrl, key, {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
    });
    return CryptoJS.enc.Utf8.stringify(decrypted);
}
  let video = decryptVideoUrl(config.url,config.config.uid)

         input = {
				jx: 0,
				url: video,
				parse: 0
			}

  } else if (/ty/.test(html.from)){
      
      
      let ty跳转= JSON.parse(request(jx+url,{
      redirect:false, 
      withHeaders:true
      })).location
      
      log(ty跳转)
      let ty请求=request(ty跳转,{
        headers: {
            'Referer': ''
        }
    })
   let rand= ty请求.match(/var rand = "(.*?)";/)[1];
   let player= ty请求.match(/var player = "(.*?)";/)[1];
log(rand)
function js_decrypt(str, key, iv) {
                eval(getCryptoJS())
                var key = CryptoJS.enc.Utf8.parse(key);
                var iv = CryptoJS.enc.Utf8.parse(iv);
                var decrypted = CryptoJS.AES.decrypt(str, key, {
                    iv: iv,
                    padding: CryptoJS.pad.Pkcs7
                }).toString(CryptoJS.enc.Utf8);
                return decrypted
            }

            var ur =JSON.parse(js_decrypt(player, 'VFBTzdujpR9FWBhe', rand)).url
            input={
              jx:0,
              url:ur,
              parse:0
            }
            
      }else{
      let wj= JSON.parse(request(jx+url,{redirect:false, withHeaders:true})).location
 let play= wj.replace('https://jx.wujinkk.com/dplayer/?url=','')
      
      input={
              jx:0,
              url:play,
              parse:0
            }
      
      }
      
    }),
	推荐: '*',
	double: false, // 推荐内容是否双层定
	searchUrl:'/search/**----------fypage---.html',
}