var rule = {
    title: '含羞草',
    host: 'https://ap988.hydzswyxgs.com',
    url: '/videos/getList',
    homeurl: "/videos/getList",
    searchUrl: '/base/globalSearch',
    searchable: 2,
    quickSearch: 1,
    filterable: 1,
    headers: { 'User-Agent': MOBILE_UA },
    filter: 'H4sIAAAAAAAAA6vmUgACJQslK4VoMBMEquEssGR2aiVQWqmksiBVSQdVKi8xNxUk93zj7qfzutFlyxJzSlNRTMZuA8I4kFnBvmjmIMwDSpsbYsjVYirHZ/7zvROf71qEzw4zC0rteLF80ovOTXjtMKfYjglzX/R14rXDjFI7nm6Y+HRZO147TCm2Y0Lz88lz8NphRLEd/b1Pt6/Da4clxelq076XDZ2OYXhtMaHUlie7dj1dNg2fHYYU55CXuyc+n7kXnx1YIgRFJJYLVTyWqxYA9q28dWoEAAA=',
    timeout: 5000,
    class_name: '秒播&少女&精选&女同&男同&热播&专题&国产&主播&日韩',
    class_url: '3&7&1&8&4&11&17',
    proxy_rule: $js.toString(() => {
        // console.log("tup====="+input);
        if (input) {
            let data1 = request(input.url);
            let key = CryptoJS.enc.Utf8.parse("46cc793c53dc451b");
            let img
            if (/pK0H/.test(data1)) {
                var decrypt = CryptoJS.AES.decrypt(data1, key, {
                    mode: CryptoJS.mode.ECB,
                    padding: CryptoJS.pad.Pkcs7
                });
                img = decrypt.toString(CryptoJS.enc.Utf8);
            } else {
                var decrypt = CryptoJS.AES.decrypt(data1, key, {
                    mode: CryptoJS.mode.ECB,
                    padding: CryptoJS.pad.NoPadding
                });
                img = decrypt.toString(CryptoJS.enc.Utf8);

            }
            let type=img.match(/.*image\/([^;]+);/)[1];
            input = [200, `image/${type}`, img, null, 1];
        }

    }),
    推荐: $js.toString(() => {
        let d = [];
        function enData(word) {
            let keyStr = 'B77A9FF7F323B5404902102257503C2F';
            const key = CryptoJS.enc.Utf8.parse(keyStr);
            const iv = CryptoJS.enc.Utf8.parse(keyStr);
            const srcs = CryptoJS.enc.Utf8.parse(word);
            const encrypted = CryptoJS.AES.encrypt(srcs, key, {
                iv: iv,
                mode: CryptoJS.mode.CBC,
                padding: CryptoJS.pad.Pkcs7
            });
            return CryptoJS.enc.Base64.stringify(encrypted.ciphertext);
        }
        var postParam = '{"length":7,"orderType":3,"page":1,"payType":['+3+'],"tagIds":[],"tags":[],"type":0,"typeIds":[],"videoIds":[]}';
        console.log(JSON.stringify(postParam))        
        var data = JSON.parse(
            fetch('https://ap988.hydzswyxgs.com/videos/getList', {
                method: 'POST',
                body: {
                    endata: enData(postParam),
                    ents: enData(parseInt(new Date().getTime() / 1e3) + 60 * new Date().getTimezoneOffset()),
                },
            })).data.list;
        data.forEach(it => {
            d.push({
                url: it.id + '#' + it.isAngle,
                title: it.name,
                img: it.coverImgUrl,
                desc: it.seeCount ? `${(it.seeCount / 10000).toFixed(2)}万⏯️` : ''
            })
        })
        setResult(d)
    }),
    一级: $js.toString(() => {
        let d = [];
        function enData(word) {
            let keyStr = 'B77A9FF7F323B5404902102257503C2F';
            const key = CryptoJS.enc.Utf8.parse(keyStr);
            const iv = CryptoJS.enc.Utf8.parse(keyStr);
            const srcs = CryptoJS.enc.Utf8.parse(word);
            const encrypted = CryptoJS.AES.encrypt(srcs, key, {
                iv: iv,
                mode: CryptoJS.mode.CBC,
                padding: CryptoJS.pad.Pkcs7
            });
            return CryptoJS.enc.Base64.stringify(encrypted.ciphertext);
        }
        var postParam
        switch (MY_CATE) {

            case '17':
            case '11':
            case '4':
            case '7':
            case '1':
                postParam = {
                    length: 20,
                    orderType: MY_CATE === '7' ? parseInt(MY_CATE) : 3,
                    page: MY_PAGE,
                    payType: MY_CATE === '7' ? [3] : [3, 4],
                    tagIds: [],
                    tags: [],
                    type: 0,
                    typeIds: MY_CATE === '7' || MY_CATE === '1' ? [] : [parseInt(MY_CATE)],
                    videoIds: []
                };
                break;
            case '3':
                postParam = {
                    length: 20,
                    orderType: parseInt(MY_CATE),
                    page: MY_PAGE,
                    payType: [1, 3, 4],
                    recommendIds: [],
                    tagIds: [],
                    tags: [],
                    type: 0,
                    typeIds: []
                };
                break;
            case '8':
                postParam = {
                    length: 20,
                    orderType: parseInt(MY_CATE),
                    page: MY_PAGE,
                    subjectId: parseInt(MY_FL.type) || 68,
                    type: 0
                };
                break;
            default:
                postParam = {};
                break;
        }                
        var data = JSON.parse(
            fetch(input, {
                method: 'POST',
                body: {
                    endata: enData(JSON.stringify(postParam)),
                    ents: enData(parseInt(new Date().getTime() / 1e3) + 60 * new Date().getTimezoneOffset()),
                },
            })).data.list;
        data.forEach(it => {
            d.push({
                url: it.id + '#' + it.isAngle,
                title: it.name,
                img: it.coverImgUrl,
                desc: it.seeCount ? `${(it.seeCount / 10000).toFixed(2)}万⏯️` : ''
            })
        })
        setResult(d)
    }),
    图片替换: $js.toString(() => {       
        input = getProxyUrl() + '&url=' + input;
    }),
    二级: $js.toString(() => {
        //let urls = [];
        function enData(word) {
            let keyStr = 'B77A9FF7F323B5404902102257503C2F';
            const key = CryptoJS.enc.Utf8.parse(keyStr);
            const iv = CryptoJS.enc.Utf8.parse(keyStr);
            const srcs = CryptoJS.enc.Utf8.parse(word);
            const encrypted = CryptoJS.AES.encrypt(srcs, key, {
                iv: iv,
                mode: CryptoJS.mode.CBC,
                padding: CryptoJS.pad.Pkcs7
            });
            return CryptoJS.enc.Base64.stringify(encrypted.ciphertext);
        }
        let postUrl = ''
        if (vod_id.match(/#(.*)/)[1] === '0') {
            postUrl = 'https://ap988.hydzswyxgs.com/videos/v2/getUrl'
        } else {
            postUrl = 'https://ap988.hydzswyxgs.com/videos/getPreUrl'
        }
        let url = JSON.parse(fetch(postUrl, {
            method: 'POST',
            body: { "endata": enData(JSON.stringify({ "videoId": parseInt(vod_id.match(/(.*?)(?=#)/)[1]) })), "ents": enData(parseInt(new Date().getTime() / 1e3) + 60 * new Date().getTimezoneOffset()) }
        })).data.url;
        url = url.replace(/start.*?&sign/, 'sign');
        VOD = {           
            vod_play_from: 'hxc',
            vod_play_url: vod_name + '$' + url,
            desc:'合理安排时间，且勿沉迷',
        }
    }),
    搜索: $js.toString(() => {
        let d = [];
        function enData(word) {
            let keyStr = 'B77A9FF7F323B5404902102257503C2F';
            const key = CryptoJS.enc.Utf8.parse(keyStr);
            const iv = CryptoJS.enc.Utf8.parse(keyStr);
            const srcs = CryptoJS.enc.Utf8.parse(word);
            const encrypted = CryptoJS.AES.encrypt(srcs, key, {
                iv: iv,
                mode: CryptoJS.mode.CBC,
                padding: CryptoJS.pad.Pkcs7
            });
            return CryptoJS.enc.Base64.stringify(encrypted.ciphertext);
        }      
        var postParam = { "key": KEY, "length": 20, "page": MY_PAGE, "type": 1 };
        var data = JSON.parse(
            fetch(input, {
                method: 'POST',
                body: {
                    "endata": enData(JSON.stringify(postParam)),
                    "ents": enData(parseInt(new Date().getTime() / 1e3) + 60 * new Date().getTimezoneOffset()),
                },
            })).data.infos;
        data.forEach(it => {
            d.push({
                url: it.id + '#' + it.isAngle,
                title: it.name,
                img: it.coverImgUrl,
                desc: it.seeCount ? `${(it.seeCount / 10000).toFixed(2)}万⏯️` : ''
            })
        })
        setResult(d)
    }),
}