import {__jsEvalReturn} from './jiujiuliu.js';

import * as Utils from "../lib/utils.js";


let spider = __jsEvalReturn();

async function testPlay(vodDetail) {
    if (vodDetail.list && vodDetail.list.length > 0) {
        const pFlag = vodDetail.list[0].vod_play_from.split('$$$');
        const pUrls = vodDetail.list[0].vod_play_url.split('$$$');
        if (pFlag.length > 0 && pUrls.length > 0) {
            for (const i in pFlag) {
                // console.debug(i)
                let flag = pFlag[i];
                let urls = pUrls[i].split('#');
                // console.debug(flag, urls)
                for (const j in urls) {
                    var name = urls[j].split('$')[0];
                    var url = urls[j].split('$')[1];
                    console.debug(flag + " | " + name + " | " + url);
                    var playUrl = await spider.play(flag, url, []);
                    console.debug('playURL: ' + playUrl);
                }
            }
        }
    }
}

async function testMusicPlay(vodDetail) {
    if (vodDetail.list && vodDetail.list.length > 0) {
        const pFlag = vodDetail.list[0].volumes.split('$$$');
        const pUrls = vodDetail.list[0].urls.split('$$$');
        if (pFlag.length > 0 && pUrls.length > 0) {
            for (const i in pFlag) {
                // console.debug(i)
                let flag = pFlag[i];
                let urls = pUrls[i].split('#');
                // console.debug(flag, urls)
                for (const j in urls) {
                    var name = urls[j].split('$')[0];
                    var url = urls[j].split('$')[1];
                    console.debug(flag + " | " + name + " | " + url);
                    var playUrl = await spider.play(flag, url, []);
                    console.debug('playURL: ' + playUrl);
                }
                break
            }
        }
    }
}

async function test() {
    let siteKey = 'jiujiuliu';
    let siteType = 3;
    await spider.init({
        skey: siteKey, stype: siteType, ext: {
            "aliToken": "51427b95ab9d47a6921a27951ebd3f1e",
            "box": "TV",
            "code": "1",
            "from": "star",
            "danmu": true,
            "cookie": "buvid3=02675249-8ED3-C418-87F5-59E18316459714816infoc; b_nut=1704421014; _uuid=5D435F74-F574-D9AB-62C1-B9294DE465D913102infoc; buvid_fp=e8c5650c749398e9b5cad3f3ddb5081e; buvid4=007E85D1-52C1-7E6E-07CF-837FFBC9349516677-024010502-J5vTDSZDCw4fNnXRejbSVg%3D%3D; rpdid=|()kYJmulRu0J'u~|RRJl)JR; PVID=1; SESSDATA=3be091d3%2C1720332009%2C699ed%2A11CjAcCdwXG5kY1umhCOpQHOn_WP7L9xFBfWO7KKd4BPweodpR6VyIfeNyPiRmkr5jCqsSVjg0R0dZOVVHRUo3RnhPRTZFc3JPbGdiUjFCdHpiRDhiTkticmdKTjVyS1VhbDdvNjFMSDJlbUJydUlRdjFUNGFBNkJlV2ZTa0N1Q1BEVi1QYTQzTUh3IIEC; bili_jct=b0ee7b5d3f27df893545d811d95506d4; DedeUserID=78014638; DedeUserID__ckMd5=4c8c5d65065e468a; enable_web_push=DISABLE; header_theme_version=CLOSE; home_feed_column=5; CURRENT_BLACKGAP=0; CURRENT_FNVAL=4048; b_lsid=75E916AA_18EA1A8D995; bsource=search_baidu; FEED_LIVE_VERSION=V_HEADER_LIVE_NO_POP; browser_resolution=1507-691; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTIzNjk5MTMsImlhdCI6MTcxMjExMDY1MywicGx0IjotMX0.8zQW_fNTCSBlK_JkHnzu3gDw62wuTK1qgKcbGec3swM; bili_ticket_expires=171236985",
            "quarkCookie":"_UP_A4A_11_=wb965111521e45ffa80410c24a071a54; _UP_D_=pc; tfstk=fXFith4nnRk114LAjWc1TT-OQUXL5hGjqodxDjnVLDoBBchYujR4Drht3GaYxmqYlcPtWc34mknIMcFTB-Y_tuAv6G6_uIcxggIRw_U15jGV2EjCXmnslyoqlSMN9PGjgMEW0dR85uVOAjYmgwcEoqOqgIrqLyoIlq-ZuC738DgqgCJZgH8EuqxZNmAqqSPQTaC3h7bb2rFnSvW87D8jTW0iX0zasIR2zVDi4Poh2svabvzjnSTXixaaFogzbhS-Cry3xVcc9dlz--roR55Jj2wT8znUrEdYrfV3t-kh71znscDo-vYWpf24fSD_IE_78frQF0MNdMg367HmVvxFbyUnbY20XMOqX84UxYFpvQhbA-rqok-G4A9eUc4wG27YtK9jQ2gnVNJioG_mbu_h-wv5CAuIWgQh-K9jQ2gn2wbHFhMZRVIR.; __pus=c81f57897dafcb65d4ecb501bc299199AARcqF72zsatdbsCbiT3qVqsk36caaycoPQW7hz8rbEf+UY7f5aGgH1e90lsONAUwCAW8y27u5A/KXyYqkHCWgjS; __kp=99fa2760-1669-11ef-90cf-8f7a59c3b86e; __kps=AATSt4xuf6r6bqes3LdJvxvy; __ktd=c2e+aLICIvFoeklXXz36VA==; __uid=AATSt4xuf6r6bqes3LdJvxvy; Video-Auth=smob3MOUslklDq2MutANJYZCVo50sLv0GFelx3+cu1nK2fkdL2kvkdpT5yNOhNz0NLTyi5ThWRL47+ztJA4kXQ==; __puus=72f667c533c9a22496f88d2f1bb7ae71AAQ7mrvFw7s9AUPUXvnuGPkcDU3RRTVPdYaYQfsM9Cje2doYXgRZXbImg02EaUaEG+G9ikpo3xubGGdElArOuYvUtJzIXb6yHDnSZbtEUxkwvjfQRNEnDnVwLQ6LL2ORjRaxa9OUfwk/WppWvy6OcDqQtHYkaqB+Poxn5kFs7ZVdAtX7ZQks1czD+g9gAZjsbeBHxHQ1AP5MGc1s3M4RhwZQ"
        }
    });

    let classes = JSON.parse(await spider.home(true));
    console.debug(JSON.stringify(classes))


    
    //测试首页列表
    let homeVod = JSON.parse(await spider.homeVod())
    console.debug(JSON.stringify(homeVod));




    
    // 测试分类
    let catePage = JSON.parse(await spider.category("/vod/type/id/1.html", "1", undefined, {}));
    console.debug(JSON.stringify(catePage))



    // 测试详情
    let detail1 = JSON.parse(await spider.detail("/detail/192466.html"))
    await testPlay(detail1)

    
    // 测试搜索
    let search_page = JSON.parse(await spider.search("庆余年", false, 1))
    console.debug(JSON.stringify(search_page))

















    // 测试详情
    if (search_page.list && search_page.list.length > 0) {
        for (const k in search_page.list) {
            // console.debug(k)
            if (k >= 1) break;
            let obj = search_page.list[k]
            let spVid = search_page.list[k].vod_id
            console.debug("===", spVid)
            var detail = JSON.parse(await spider.detail(spVid || search_page.list[k].vod_id));

            await testPlay(detail);
        }
    }
}

export {test};