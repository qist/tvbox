var lazy = $('').lazyRule(() => {
   var url = fetch(input,{});
      if (/.m3u8|.mp4/.test(url)) {
        return fetch(input).match(/https.*?m3u8/)[0]
      }/*if (/iframe/.test(url)) {
        return pdfh(fetch(input,{}), 'iframe&&src')
      }*/else {
        return "pics://"+pdfa( request(input,{}), '.pic-detail&&img').map(img =>pd(img, 'img&&src')+"@Referer=https://4fang.tv/",).join('&&')
     }
});