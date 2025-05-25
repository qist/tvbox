var rule = {
    title: '花子动漫[漫]',
    host: 'https://www.huazidm.com',
    class_name: 'TV动漫&剧场&特摄',
    class_url: '1&2&3',
    searchUrl: '/index.php/ajax/suggest?mid=1&wd=**&limit=50',
    searchUrl: '/vodsearch/**----------fypage---.html',
    searchable: 2,
    quickSearch: 0,
    headers: {
        'User-Agent': 'MOBILE_UA',
    },
    url: '/index.php/api/vod#type=fyclassfyfilter&page=fypage',
    filterable: 0,
    filter_url: '&class={{fl.class}}&year={{fl.year}}&letter={{fl.letter}}&by={{fl.by}}',
    filter: 'H4sIAAAAAAAAA+2W204TURSG32WuMdnT0nbDnZzP57PhopImEhETWk0IIUFOloNQDLSigGJCLCIWhJCWgr4MM9O+hdPO2mstDzE10cSYudv/989u55t0uteUpmuVd6a0+6FJrVIbGQuGw1qZNh58ELKjdZo19lbs/Dg49ihUvG7cxsZCMj+XLGA7aNNlQK9mb9Jxa2sVCsrqCmv7sxGLQg0Bd8fWjI9HaqsTcN/ccW5/Ru1zAnaXKSt6qjonYHf4JXexrDon4PcdPDUyWfV9TlCdGX1hxhPQQSjlPs3YnvVhQ+1zAnaJAyOdVp0T8D7fbdC9QMB9n7LmvHpmELB7s2+8OladE7B7skLPBQI6LD7Pbx8qByfgvrWkFVtU+5yA3c6l/TRU5wTV5V+f3WRi0EFQXS62m1tbgg4C3WfMnInjfRYDdnPL5uxL1TkBu7P9/O5ba+u9qjHjFem0GV03NzPqCsz4HE7Wc6lzuoIyfsbVkbWZZZ+BGd0WlHRhNT1c4M67NBkKTtCrZGTOb7LXJb5KHuEpB1ZcMu4l7uXcQ9zDuU5c51wQF4zrFcjtJeOSuOQ8QDzAuZ+4n3MfcR/n5KtzX518de6rk6/OfXXy1bmvTr469xXkK7ivIF/BfQX5Cu4ryFdwX0G+gvsK8hXcV5Cv4L6CfAX3FeQruK8gX0G+ekWF8i0uGZfEJecB4gHO/cT9nPuI+zgvJ17OuZe4l3MPcQ/nOnGdc0Gc+0ryldxXkq/kvpJ8JfeV5Cu5ryRfyX0l+UruK8lXcl9JvpL7SvKV3FeSr73kfztjoUgkxP94jhNm6lmJfzy3AdxGUgWkCkk1kGokNUBqkNQCqUVSB6QOST2QeiQNQBqQNAJpRNIEpAlJM5BmJC1AWpC0AmlF0gakDUk7kHYkHUA6kHQC6UTSBaQLSTeQbiQ9QHqQ9ALpRdIHpA9JP5B+JANABpAMAhlEMgRkCIm4pd6Bwor/VO5O0s/ETFzkE+c//EzM1SVzZ8aMn8BHREbtq/F0LJb2QAblvdFImJe51LwRVbNEeOThRKjw9cNlmuefGDl/OVb+hdHxvxgPf3cEdAcidyByByK1dAcidyByByJ3IPp+IPL+qYFoOXlzvaOObieUMrb8dMRwj2736HaPbrV0j2736HaPbvfo/vbonv4K+TrlXkAbAAA=',
    filter_def: {},
    detailUrl: '/voddetail/fyid.html',
    play_parse: true,
    sniffer: 1,
    is_video: 'obj/tos|bd.xhscdn|/ugc/',
    lazy: $js.toString(() => {
        input = {
            parse: 1,
            url: input,
            //js:'try{let urls=Array.from(document.querySelectorAll("iframe")).filter(x=>x.src.includes("?url="));if(urls){location.href=urls[0].src}}catch{}document.querySelector("button").click()',
            js: 'try{location.href=document.querySelector("#playleft iframe").src}catch{}document.querySelector("button.swal-button--confirm").click()',
            parse_extra: '&is_pc=1&custom_regex=' + rule.is_video,
        }
    }),
    limit: 6,
    推荐: '.list-vod.flex .public-list-box;a&&title;.lazy&&data-original;.public-list-prb&&Text;a&&href',
    一级: $js.toString(() => {
        let body = input.split("#")[1];
        let t = Math.round(new Date / 1e3).toString();
        let key = md5("DS" + t + "DCC147D11943AF75");
        let url = input.split("#")[0];
        body = body + "&time=" + t + "&key=" + key;
        print(body);
        fetch_params.body = body;
        let html = post(url, fetch_params);
        let data = JSON.parse(html);
        VODS = data.list.map(function (it) {
            it.vod_pic = urljoin2(input.split("/i")[0], it.vod_pic);
            return it
        });
    }),
    二级: {
        title: '.slide-info-title&&Text;.slide-info:eq(3)--strong&&Text',
        img: '.detail-pic&&data-original',
        desc: '.fraction&&Text;.slide-info-remarks:eq(1)&&Text;.slide-info-remarks:eq(2)&&Text;.slide-info:eq(2)--strong&&Text;.slide-info:eq(1)--strong&&Text',
        content: '#height_limit&&Text',
        tabs: '.anthology.wow.fadeInUp.animated&&.swiper-wrapper&&a',
        tab_text: '.swiper-slide&&Text',
        lists: '.anthology-list-box:eq(#id) li',
    },
    搜索: 'json:list;name;pic;;id',
    搜索: $js.toString(() => {
        let html = fetch(input);
        let list = pdfa(html, ".public-list-box");
        VODS = list.map(x => {
            return {
                vod_name: pdfh(x, ".thumb-txt&&Text"),
                vod_pic: pdfh(x, ".lazy&&data-src"),
                vod_remarks: pdfh(x, ".public-list-prb&&Text"),
                vod_content: pdfh(x, ".thumb-blurb&&Text"),
                vod_id: pdfh(x, "a&&href")
            }
        });
    }),
    图片替换: '&amp;=>&'
}