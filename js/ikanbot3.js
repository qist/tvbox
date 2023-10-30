var rule = {
    title:'爱看机器人3',
    // host:'https://www.ikanbot.com',
    host:'https://www.aikanbot.com',
    url:'/hot/index-fyclass-fyfilter-p-fypage.html[/hot/index-fyclass-fyfilter.html]',
    searchUrl:'/search?q=**&p=fypage[/search?q=**]',
    searchable:2,
    quickSearch:0,
    filterable:1,
    filter_url:'{{fl.tag}}',
    // 图片来源:'@Referer=https://api.douban.com/@User-Agent=Mozilla/5.0%20(Windows%20NT%2010.0;%20Win64;%20x64)%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/113.0.0.0%20Safari/537.36',
    图片来源:'@Referer=https://www.aikanbot.com/@User-Agent=Mozilla/5.0%20(Windows%20NT%2010.0;%20Win64;%20x64)%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/113.0.0.0%20Safari/537.36',
    filter:{
        "movie":[{"key":"tag","name":"标签","value":[{"n":"热门","v":"热门"},{"n":"最新","v":"最新"},{"n":"经典","v":"经典"},{"n":"豆瓣高分","v":"豆瓣高分"},{"n":"冷门佳片","v":"冷门佳片"},{"n":"华语","v":"华语"},{"n":"欧美","v":"欧美"},{"n":"韩国","v":"韩国"},{"n":"日本","v":"日本"},{"n":"动作","v":"动作"},{"n":"喜剧","v":"喜剧"},{"n":"爱情","v":"爱情"},{"n":"科幻","v":"科幻"},{"n":"悬疑","v":"悬疑"},{"n":"恐怖","v":"恐怖"},{"n":"治愈","v":"治愈"},{"n":"豆瓣top250","v":"豆瓣top250"}]}],
        "tv":[{"key":"tag","name":"标签","value":[{"n":"热门","v":"热门"},{"n":"美剧","v":"美剧"},{"n":"英剧","v":"英剧"},{"n":"韩剧","v":"韩剧"},{"n":"日剧","v":"日剧"},{"n":"国产剧","v":"国产剧"},{"n":"港剧","v":"港剧"},{"n":"日本动画","v":"日本动画"},{"n":"综艺","v":"综艺"},{"n":"纪录片","v":"纪录片"}]}]
    },
    filter_def:{
        movie:{tag:'热门'},
        tv:{tag:'国产剧'},
    },
    filter获取方法:`
        let value = [];
        $('ul').eq(2).find('li').each(function() {
            // console.log($(this).text());
            let n = $(this).text().trim();
            value.push({
            'n': n, 'v': n
            });
        });
        // 电影执行:
        let data = {'movie': [{'key': 'tag', 'name': '标签', 'value': value}]};
        console.log(JSON.stringify(data));

        //剧集执行:
        let data = {'tv': [{'key': 'tag', 'name': '标签', 'value': value}]};
        console.log(JSON.stringify(data));
    `,
    headers:{'User-Agent':'PC_UA',},
    class_name:'电影&剧集',
    class_url:'movie&tv',
    play_parse:true,
    double:true,
    推荐:'.v-list;div.item;*;*;*;*', //这里可以为空，这样点播不会有内容
    一级:'.v-list&&div.item;p&&Text;img&&data-src;;a&&href', //一级的内容是推荐或者点播时候的一级匹配
    // 二级:二级,
    二级:'js:eval(unescape(base64Decode("anM6CnBkZmggPSBqc3AucGRmaDsKZnVuY3Rpb24gZ2V0VG9rZW4oaHRtbDEpIHsKICAgIGxldCBjdXJyZW50SWQgPSBwZGZoKGh0bWwxLCAnI2N1cnJlbnRfaWQmJnZhbHVlJyk7CiAgICBsZXQgZVRva2VuID0gcGRmaChodG1sMSwgJyNlX3Rva2VuJiZ2YWx1ZScpOwogICAgaWYgKCFjdXJyZW50SWQgfHwgIWVUb2tlbikgcmV0dXJuICcnOwogICAgbGV0IGlkTGVuZ3RoID0gY3VycmVudElkLmxlbmd0aDsKICAgIGxldCBzdWJJZCA9IGN1cnJlbnRJZC5zdWJzdHJpbmcoaWRMZW5ndGggLSA0LCBpZExlbmd0aCk7CiAgICBsZXQga2V5cyA9IFtdOwogICAgZm9yIChsZXQgaSA9IDA7IGkgPCBzdWJJZC5sZW5ndGg7IGkrKykgewogICAgICAgIGxldCBjdXJJbnQgPSBwYXJzZUludChzdWJJZFtpXSk7CiAgICAgICAgbGV0IHNwbGl0UG9zID0gY3VySW50ICUgMyArIDE7CiAgICAgICAga2V5c1tpXSA9IGVUb2tlbi5zdWJzdHJpbmcoc3BsaXRQb3MsIHNwbGl0UG9zICsgOCk7CiAgICAgICAgZVRva2VuID0gZVRva2VuLnN1YnN0cmluZyhzcGxpdFBvcyArIDgsIGVUb2tlbi5sZW5ndGgpOwogICAgfQogICAgcmV0dXJuIGtleXMuam9pbignJyk7Cn0KdHJ5IHsKICAgIFZPRD17fTsKICAgIGxldCBodG1sMSA9IHJlcXVlc3QoaW5wdXQpOwogICAgVk9ELnZvZF9pZCA9IHBkZmgoaHRtbDEsICcjY3VycmVudF9pZCYmdmFsdWUnKTsKICAgIFZPRC52b2RfbmFtZSA9IHBkZmgoaHRtbDEsICdoMiYmVGV4dCcpOwogIAlWT0Qudm9kX3BpYyA9IHBkZmgoaHRtbDEsICcuaXRlbS1yb290JiZpbWcmJmRhdGEtc3JjJyk7CiAgCVZPRC52b2RfYWN0b3IgPSBwZGZoKGh0bWwxLCAnLm1ldGE6ZXEoNCkmJlRleHQnKTsKICAJVk9ELnZvZF9hcmVhID0gcGRmaChodG1sMSwgJy5tZXRhOmVxKDMpJiZUZXh0Jyk7CiAgCVZPRC52b2RfeWVhciA9IHBkZmgoaHRtbDEsICcubWV0YTplcSgyKSYmVGV4dCcpOwogICAgVk9ELnZvZF9yZW1hcmtzID0gJyc7CiAgICBWT0Qudm9kX2RpcmVjdG9yID0gJyc7CiAgICBWT0Qudm9kX2NvbnRlbnQgPSAnJzsKICAgIGxvZyhWT0QpOwogICAgdmFyIHZfdGtzID0gZ2V0VG9rZW4oaHRtbDEpOwoJaW5wdXQgPSAnaHR0cHM6Ly93d3cuaWthbmJvdC5jb20vYXBpL2dldFJlc04/dmlkZW9JZD0nICsgaW5wdXQuc3BsaXQoJy8nKS5wb3AoKSArICcmbXR5cGU9MiZ0b2tlbj0nK3ZfdGtzOwoJbGV0IGh0bWwgPSByZXF1ZXN0KGlucHV0LCB7CiAgICAgICAgaGVhZGVyczogewogICAgICAgICAgICAnVXNlci1BZ2VudCc6J01vemlsbGEvNS4wIChpUGhvbmU7IENQVSBpUGhvbmUgT1MgMTNfMl8zIGxpa2UgTWFjIE9TIFgpIEFwcGxlV2ViS2l0LzYwNS4xLjE1IChLSFRNTCwgbGlrZSBHZWNrbykgVmVyc2lvbi8xMy4wLjMgTW9iaWxlLzE1RTE0OCBTYWZhcmkvNjA0LjEnLAogICAgICAgICAgICAnUmVmZXJlcic6IGlucHV0LAogICAgICAgIH0KICAgIH0pOwogICAgcHJpbnQoaHRtbCk7CiAgICBodG1sID0gSlNPTi5wYXJzZShodG1sKTsKICAgIGxldCBlcGlzb2RlcyA9IGh0bWwuZGF0YS5saXN0OwogICAgbGV0IHBsYXlNYXAgPSB7fTsKICAgIGlmICh0eXBlb2YgcGxheV91cmwgPT09ICd1bmRlZmluZWQnKSB7CiAgICAgICAgdmFyIHBsYXlfdXJsID0gJycKICAgIH0KICAgIGxldCBtYXAgPSB7fQogICAgbGV0IGFyciA9IFtdCiAgICBsZXQgbmFtZSA9IHsKICAgICAgICAnYmZ6eW0zdTgnOiAn5pq06aOOJywKICAgICAgICAnMTA4MHp5ayc6ICfkvJjotKgnLAogICAgICAgICdrdWFpa2FuJzogJ+W/q+eciycsCiAgICAgICAgJ2x6bTN1OCc6ICfph4/lrZAnLAogICAgICAgICdmZm0zdTgnOiAn6Z2e5YehJywKICAgICAgICAnaGFpd2Fpa2FuJzogJ+a1t+WklueciycsCiAgICAgICAgJ2dzbTN1OCc6ICflhYnpgJ8nLAogICAgICAgICd6dWlkYW0zdTgnOiAn5pyA5aSnJywKICAgICAgICAnYmptM3U4JzogJ+WFq+aIkicsCiAgICAgICAgJ3NubTN1OCc6ICfntKLlsLwnLAogICAgICAgICd3b2xvbmcnOiAn5Y2n6b6ZJywKICAgICAgICAneGxtM3U4JzogJ+aWsOa1qicsCiAgICAgICAgJ3lobTN1OCc6ICfmqLHoirEnLAogICAgICAgICd0a20zdTgnOiAn5aSp56m6JywKICAgICAgICAnanNtM3U4JzogJ+aegemAnycsCiAgICAgICAgJ3dqbTN1OCc6ICfml6DlsL0nLAogICAgICAgICdzZG0zdTgnOiAn6Zeq55S1JywKICAgICAgICAna2NtM3U4JzogJ+W/q+i9picsCiAgICAgICAgJ2ppbnlpbmdtM3U4JzogJ+mHkem5sCcsCiAgICAgICAgJ2ZzbTN1OCc6ICfpo57pgJ8nLAogICAgICAgICd0cG0zdTgnOiAn5reY54mHJywKICAgICAgICAnbGVtM3U4JzogJ+mxvOS5kCcsCiAgICAgICAgJ2RibTN1OCc6ICfnmb7luqYnLAogICAgICAgICd0b21tM3U4JzogJ+eVquiMhCcsCiAgICAgICAgJ3VrbTN1OCc6ICdV6YW3JywKICAgICAgICAnaWttM3U4JzogJ+eIseWdpCcsCiAgICAgICAgJ2huenltM3U4JzogJ+e6oueJm+i1hOa6kCcsCiAgICAgICAgJ2hubTN1OCc6ICfnuqLniZsnLAogICAgICAgICc2OHp5X20zdTgnOiAnNjgnLAogICAgICAgICdrZG0zdTgnOiAn6YW354K5JywKICAgICAgICAnYmR4bTN1OCc6ICfljJfmlpfmmJ8nLAogICAgICAgICdxaG0zdTgnOiAn5aWH6JmOJywKICAgICAgICAnaGhtM3U4JzogJ+ixquWNjicKICAgIH07CiAgICBlcGlzb2Rlcy5mb3JFYWNoKGZ1bmN0aW9uKGVwKSB7CiAgICAgICAgbGV0IGRhdGEgPSBKU09OLnBhcnNlKGVwWydyZXNEYXRhJ10pOwogICAgICAgIGRhdGEubWFwKHZhbCA9PiB7CiAgICAgICAgICAgIGlmKCFtYXBbdmFsLmZsYWddKXsKICAgICAgICAgICAgICAgIG1hcFt2YWwuZmxhZ10gPSBbdmFsLnVybC5yZXBsYWNlQWxsKCcjIycsJyMnKV0KICAgICAgICAgICAgfSBlbHNlIHsKICAgICAgICAgICAgICAgIG1hcFt2YWwuZmxhZ10ucHVzaCh2YWwudXJsLnJlcGxhY2VBbGwoJyMjJywnIycpKQogICAgICAgICAgICB9CiAgICAgICAgfSkKICAgIH0pOwogICAgZm9yICh2YXIga2V5IGluIG1hcCkgewogICAgICAgIGlmICgnYmZ6eW0zdTgnID09IGtleSkgewogICAgICAgICAgICBhcnIucHVzaCh7CiAgICAgICAgICAgICAgICBmbGFnOiBuYW1lW2tleV0sCiAgICAgICAgICAgICAgICB1cmw6IG1hcFtrZXldLAogICAgICAgICAgICAgICAgc29ydDogMQogICAgICAgICAgICB9KQogICAgICAgIH0gZWxzZSBpZiAoJzEwODB6eWsnID09IGtleSkgewogICAgICAgICAgICBhcnIucHVzaCh7CiAgICAgICAgICAgICAgICBmbGFnOiBuYW1lW2tleV0sCiAgICAgICAgICAgICAgICB1cmw6IG1hcFtrZXldLAogICAgICAgICAgICAgICAgc29ydDogMgogICAgICAgICAgICB9KQogICAgICAgIH0gZWxzZSBpZiAoJ2t1YWlrYW4nID09IGtleSkgewogICAgICAgICAgICBhcnIucHVzaCh7CiAgICAgICAgICAgICAgICBmbGFnOiBuYW1lW2tleV0sCiAgICAgICAgICAgICAgICB1cmw6IG1hcFtrZXldLAogICAgICAgICAgICAgICAgc29ydDogMwogICAgICAgICAgICB9KQogICAgICAgIH0gZWxzZSBpZiAoJ2x6bTN1OCcgPT0ga2V5KSB7CiAgICAgICAgICAgIGFyci5wdXNoKHsKICAgICAgICAgICAgICAgIGZsYWc6IG5hbWVba2V5XSwKICAgICAgICAgICAgICAgIHVybDogbWFwW2tleV0sCiAgICAgICAgICAgICAgICBzb3J0OiA0CiAgICAgICAgICAgIH0pCiAgICAgICAgfSBlbHNlIGlmICgnZmZtM3U4JyA9PSBrZXkpIHsKICAgICAgICAgICAgYXJyLnB1c2goewogICAgICAgICAgICAgICAgZmxhZzogbmFtZVtrZXldLAogICAgICAgICAgICAgICAgdXJsOiBtYXBba2V5XSwKICAgICAgICAgICAgICAgIHNvcnQ6IDUKICAgICAgICAgICAgfSkKICAgICAgICB9IGVsc2UgaWYgKCdzbm0zdTgnID09IGtleSkgewogICAgICAgICAgICBhcnIucHVzaCh7CiAgICAgICAgICAgICAgICBmbGFnOiBuYW1lW2tleV0sCiAgICAgICAgICAgICAgICB1cmw6IG1hcFtrZXldLAogICAgICAgICAgICAgICAgc29ydDogNgogICAgICAgICAgICB9KQogICAgICAgIH0gZWxzZSBpZiAoJ3FobTN1OCcgPT0ga2V5KSB7CiAgICAgICAgICAgIGFyci5wdXNoKHsKICAgICAgICAgICAgICAgIGZsYWc6IG5hbWVba2V5XSwKICAgICAgICAgICAgICAgIHVybDogbWFwW2tleV0sCiAgICAgICAgICAgICAgICBzb3J0OiA3CiAgICAgICAgICAgIH0pCiAgICAgICAgfSBlbHNlIHsKICAgICAgICAgICAgYXJyLnB1c2goewogICAgICAgICAgICAgICAgZmxhZzogKG5hbWVba2V5XSkgPyBuYW1lW2tleV0gOiBrZXksCiAgICAgICAgICAgICAgICB1cmw6IG1hcFtrZXldLAogICAgICAgICAgICAgICAgc29ydDogOAogICAgICAgICAgICB9KQogICAgICAgIH0KICAgIH0KICAgIGFyci5zb3J0KChhLCBiKSA9PiBhLnNvcnQgLSBiLnNvcnQpOwogICAgbGV0IHBsYXlGcm9tID0gW107CiAgICBsZXQgcGxheUxpc3QgPSBbXTsKICAgIGFyci5tYXAodmFsID0+IHsKICAgICAgICBpZiAoIS91bmRlZmluZWQvLnRlc3QodmFsLmZsYWcpKSB7CiAgICAgICAgICAgIHBsYXlGcm9tLnB1c2godmFsLmZsYWcpOwogICAgICAgICAgICBwbGF5TGlzdC5wdXNoKHZhbC51cmwpOwogICAgICAgIH0KICAgIH0pCiAgICBsZXQgdm9kX3BsYXlfZnJvbSA9IHBsYXlGcm9tLmpvaW4oJyQkJCcpOwogICAgbGV0IHZvZF9wbGF5X3VybCA9IHBsYXlMaXN0LmpvaW4oJyQkJCcpOwogICAgVk9EWyd2b2RfcGxheV9mcm9tJ10gPSB2b2RfcGxheV9mcm9tOwogICAgVk9EWyd2b2RfcGxheV91cmwnXSA9IHZvZF9wbGF5X3VybDsKICAgIGxvZyhWT0QpOwp9IGNhdGNoIChlKSB7CiAgICBsb2coJ+iOt+WPluS6jOe6p+ivpuaDhemhteWPkeeUn+mUmeivrzonICsgZS5tZXNzYWdlKQp9")))',
    搜索:'.col-md-8&&.media;h5&&a&&Text;a&&img&&data-src;.label&&Text;a&&href',//第三个是描述，一般显示更新或者完结
}