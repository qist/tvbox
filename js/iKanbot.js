var 二级=`js:
try {
    VOD={};
	let html1 = request(input);
	pdfh = jsp.pdfh;
	VOD.vod_id = pdfh(html1, "#current_id&&value");
	VOD.vod_name = pdfh(html1, "h2&&Text");
	// VOD.vod_pic = pdfh(html1, ".item-root&&img&&src");
	VOD.vod_pic = pdfh(html1, ".item-root&&img&&data-src");
	// VOD.vod_actor = pdfh(html1, ".celebrity&&Text");
	VOD.vod_actor = pdfh(html1, ".meta:eq(4)&&Text");
	// VOD.vod_area = pdfh(html1, ".country&&Text");
	VOD.vod_area = pdfh(html1, ".meta:eq(3)&&Text");
	// VOD.vod_year = pdfh(html1, ".year&&Text");
	VOD.vod_year = pdfh(html1, ".meta:eq(2)&&Text");
	VOD.vod_remarks = "";
	VOD.vod_director = "";
	VOD.vod_content = "";
	log(VOD);
	var v_tks = '';
	// let script = pdfa(html1,'script').find(it=>it.includes('v_tks+=')).replace(/<script>|<\\/script>/g,'');
    // print(script);
    // eval(script);
	// print('v_tks:'+v_tks);
	input = "https://v.ikanbot.com/api/getResN?videoId=" + input.split("/").pop() + "&mtype=2"+"&token="+v_tks;
	// let html = request(input,{headers: {'User-Agent':'PC_UA','Referer': input}});
	// let html = request(input,{headers: {'User-Agent':'MOBILE_UA','Referer': input}});
	let html = request(input, {
        headers: {
            'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
            'Referer': input,
        }
    });
	print(html);
	html = JSON.parse(html);
	let episodes = html.data.list;
	let playMap = {};
	if (typeof play_url === "undefined") {
		var play_url = ""
	}
	episodes.forEach(function(ep) {
		let playurls = JSON.parse(ep["resData"]);
		playurls.forEach(function(playurl) {
			let source = playurl["flag"];
			if (!playMap.hasOwnProperty(source)) {
				playMap[source] = []
			}
			playMap[source].push(playurl["url"].replaceAll('##','#'))
		})
	});
	let playFrom = [];
	let playList = [];
	Object.keys(playMap).forEach(function(key) {
		playFrom.append(key);
		playList.append(playMap[key])
	});
	let vod_play_from = playFrom.join("$$$");
	let vod_play_url = playList.join("$$$");
	VOD["vod_play_from"] = vod_play_from;
	VOD["vod_play_url"] = vod_play_url;
	log(VOD);
} catch (e) {
	log("获取二级详情页发生错误:" + e.message)
}
`;

var rule = {
    title:'爱看机器人',
    host:'https://v.ikanbot.com',
    url:'/hot/index-fyclass-fyfilter-p-fypage.html[/hot/index-fyclass-fyfilter.html]',
    //https://www.ikanbot.com/search?q=%E6%96%97%E7%BD%97%E5%A4%A7&p=2
    // searchUrl:'/search?q=**&p=fypage',
	searchUrl:'/search?q=**',
    searchable:2,
    quickSearch:0,
    filterable:1,
    filter_url:'{{fl.tag}}',
    图片来源:'@Referer=https://v.ikanbot.com/@User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    filter:{
        "movie":[{"key":"tag","name":"标签","value":[{"n":"热门","v":"热门"},{"n":"最新","v":"最新"},{"n":"经典","v":"经典"},{"n":"豆瓣高分","v":"豆瓣高分"},{"n":"冷门佳片","v":"冷门佳片"},{"n":"华语","v":"华语"},{"n":"欧美","v":"欧美"},{"n":"韩国","v":"韩国"},{"n":"日本","v":"日本"},{"n":"动作","v":"动作"},{"n":"喜剧","v":"喜剧"},{"n":"爱情","v":"爱情"},{"n":"科幻","v":"科幻"},{"n":"悬疑","v":"悬疑"},{"n":"恐怖","v":"恐怖"},{"n":"治愈","v":"治愈"},{"n":"豆瓣top250","v":"豆瓣top250"}]}]
        ,"tv":[{"key":"tag","name":"标签","value":[{"n":"热门","v":"热门"},{"n":"美剧","v":"美剧"},{"n":"英剧","v":"英剧"},{"n":"韩剧","v":"韩剧"},{"n":"日剧","v":"日剧"},{"n":"国产剧","v":"国产剧"},{"n":"港剧","v":"港剧"},{"n":"日本动画","v":"日本动画"},{"n":"综艺","v":"综艺"},{"n":"纪录片","v":"纪录片"}]}]
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
	tab_remove:['wjm3u8','ikm3u8','sdm3u8','M3U8','jinyingm3u8','fsm3u8','ukm3u8'],//移除某个线路及相关的选集
	tab_order:['bfzym3u8','1080zyk','kuaikan','lzm3u8','ffm3u8','snm3u8','qhm3u8','gsm3u8','zuidam3u8','bjm3u8','wolong','xlm3u8','yhm3u8'],//线路顺序,按里面的顺序优先，没写的依次排后面
	tab_rename:{'bfzym3u8':'暴风','1080zyk':'优质','kuaikan':'快看','lzm3u8':'量子','ffm3u8':'非凡','snm3u8':'索尼','qhm3u8':'奇虎','haiwaikan':'海外看','gsm3u8':'光速','zuidam3u8':'最大','bjm3u8':'八戒','wolong':'卧龙','xlm3u8':'新浪','yhm3u8':'樱花','tkm3u8':'天空','jsm3u8':'极速','wjm3u8':'无尽','sdm3u8':'闪电','kcm3u8':'快车','jinyingm3u8':'金鹰','fsm3u8':'飞速','tpm3u8':'淘片','lem3u8':'鱼乐','dbm3u8':'百度','tomm3u8':'番茄','ukm3u8':'U酷','ikm3u8':'爱坤','hnzym3u8':'红牛资源','hnm3u8':'红牛','68zy_m3u8':'68','kdm3u8':'酷点','bdxm3u8':'北斗星','hhm3u8':'豪华','kbm3u8':'快播'},//线路名替换如:lzm3u8替换为量子资源
    推荐:'.v-list;div.item;*;*;*;*', //这里可以为空，这样点播不会有内容
    // 一级:'.v-list&&div.item;p&&Text;img&&src;;a&&href', //一级的内容是推荐或者点播时候的一级匹配
	一级:'.v-list&&div.item;p&&Text;img&&data-src;;a&&href', //一级的内容是推荐或者点播时候的一级匹配
    // 二级:二级,
    二级:'js:eval(unescape(base64Decode("anM6CiAgICAgICAgcGRmaCA9IGpzcC5wZGZoOwogICAgICAgIGZ1bmN0aW9uIGdldFRva2VuKGh0bWwxKSB7CiAgICAgICAgICAgIGxldCBjdXJyZW50SWQgPSBwZGZoKGh0bWwxLCAnI2N1cnJlbnRfaWQmJnZhbHVlJyk7CiAgICAgICAgICAgIGxldCBlVG9rZW4gPSBwZGZoKGh0bWwxLCAnI2VfdG9rZW4mJnZhbHVlJyk7CiAgICAgICAgICAgIGlmICghY3VycmVudElkIHx8ICFlVG9rZW4pIHJldHVybiAnJzsKICAgICAgICAgICAgbGV0IGlkTGVuZ3RoID0gY3VycmVudElkLmxlbmd0aDsKICAgICAgICAgICAgbGV0IHN1YklkID0gY3VycmVudElkLnN1YnN0cmluZyhpZExlbmd0aCAtIDQsIGlkTGVuZ3RoKTsKICAgICAgICAgICAgbGV0IGtleXMgPSBbXTsKICAgICAgICAgICAgZm9yIChsZXQgaSA9IDA7IGkgPCBzdWJJZC5sZW5ndGg7IGkrKykgewogICAgICAgICAgICAgICAgbGV0IGN1ckludCA9IHBhcnNlSW50KHN1YklkW2ldKTsKICAgICAgICAgICAgICAgIGxldCBzcGxpdFBvcyA9IGN1ckludCAlIDMgKyAxOwogICAgICAgICAgICAgICAga2V5c1tpXSA9IGVUb2tlbi5zdWJzdHJpbmcoc3BsaXRQb3MsIHNwbGl0UG9zICsgOCk7CiAgICAgICAgICAgICAgICBlVG9rZW4gPSBlVG9rZW4uc3Vic3RyaW5nKHNwbGl0UG9zICsgOCwgZVRva2VuLmxlbmd0aCk7CiAgICAgICAgICAgIH0KICAgICAgICAgICAgcmV0dXJuIGtleXMuam9pbignJyk7CiAgICAgICAgfQogICAgICAgIHRyeSB7CiAgICAgICAgICAgIFZPRD17fTsKICAgICAgICAgICAgbGV0IGh0bWwxID0gcmVxdWVzdChpbnB1dCk7CiAgICAgICAgICAgIFZPRC52b2RfaWQgPSBwZGZoKGh0bWwxLCAnI2N1cnJlbnRfaWQmJnZhbHVlJyk7CiAgICAgICAgICAgIFZPRC52b2RfbmFtZSA9IHBkZmgoaHRtbDEsICdoMiYmVGV4dCcpOwogICAgICAgICAgICBWT0Qudm9kX3BpYyA9IHBkZmgoaHRtbDEsICcuaXRlbS1yb290JiZpbWcmJmRhdGEtc3JjJyk7CiAgICAgICAgICAgIFZPRC52b2RfYWN0b3IgPSBwZGZoKGh0bWwxLCAnLm1ldGE6ZXEoNCkmJlRleHQnKTsKICAgICAgICAgICAgVk9ELnZvZF9hcmVhID0gcGRmaChodG1sMSwgJy5tZXRhOmVxKDMpJiZUZXh0Jyk7CiAgICAgICAgICAgIFZPRC52b2RfeWVhciA9IHBkZmgoaHRtbDEsICcubWV0YTplcSgyKSYmVGV4dCcpOwogICAgICAgICAgICBWT0Qudm9kX3JlbWFya3MgPSAnJzsKICAgICAgICAgICAgVk9ELnZvZF9kaXJlY3RvciA9ICcnOwogICAgICAgICAgICBWT0Qudm9kX2NvbnRlbnQgPSBwZGZoKGh0bWwxLCAnI2xpbmUtdGlwcyYmVGV4dCcpOwogICAgICAgICAgICAvLyBsb2coVk9EKTsKICAgICAgICAgICAgdmFyIHZfdGtzID0gZ2V0VG9rZW4oaHRtbDEpOwogICAgICAgICAgICBsb2coJ3ZfdGtzID09PT4gJyArIHZfdGtzKTsKICAgICAgICAgICAgaW5wdXQgPSBIT1NUICsgJy9hcGkvZ2V0UmVzTj92aWRlb0lkPScgKyBpbnB1dC5zcGxpdCgnLycpLnBvcCgpICsgJyZtdHlwZT0yJnRva2VuPScrdl90a3M7CiAgICAgICAgICAgIGxldCBodG1sID0gcmVxdWVzdChpbnB1dCwgewogICAgICAgICAgICAgICAgaGVhZGVyczogewogICAgICAgICAgICAgICAgICAgICdVc2VyLUFnZW50JzonTW96aWxsYS81LjAgKGlQaG9uZTsgQ1BVIGlQaG9uZSBPUyAxM18yXzMgbGlrZSBNYWMgT1MgWCkgQXBwbGVXZWJLaXQvNjA1LjEuMTUgKEtIVE1MLCBsaWtlIEdlY2tvKSBWZXJzaW9uLzEzLjAuMyBNb2JpbGUvMTVFMTQ4IFNhZmFyaS82MDQuMScsCiAgICAgICAgICAgICAgICAgICAgJ1JlZmVyZXInOiBNWV9VUkwsCiAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgIH0pOwogICAgICAgICAgICBwcmludChodG1sKTsKICAgICAgICAgICAgaHRtbCA9IEpTT04ucGFyc2UoaHRtbCk7CiAgICAgICAgICAgIGxldCBlcGlzb2RlcyA9IGh0bWwuZGF0YS5saXN0OwogICAgICAgICAgICBsZXQgcGxheU1hcCA9IHt9OwogICAgICAgICAgICBpZiAodHlwZW9mIHBsYXlfdXJsID09PSAndW5kZWZpbmVkJykgewogICAgICAgICAgICAgICAgdmFyIHBsYXlfdXJsID0gJycKICAgICAgICAgICAgfQogICAgICAgICAgICBsZXQgbWFwID0ge30KICAgICAgICAgICAgbGV0IGFyciA9IFtdCiAgICAgICAgICAgIGxldCBuYW1lID0gewogICAgICAgICAgICAgICAgJ2JmenltM3U4JzogJ+aatOmjjicsCiAgICAgICAgICAgICAgICAnMTA4MHp5ayc6ICfkvJjotKgnLAogICAgICAgICAgICAgICAgJ2t1YWlrYW4nOiAn5b+r55yLJywKICAgICAgICAgICAgICAgICdsem0zdTgnOiAn6YeP5a2QJywKICAgICAgICAgICAgICAgICdmZm0zdTgnOiAn6Z2e5YehJywKICAgICAgICAgICAgICAgICdoYWl3YWlrYW4nOiAn5rW35aSW55yLJywKICAgICAgICAgICAgICAgICdnc20zdTgnOiAn5YWJ6YCfJywKICAgICAgICAgICAgICAgICd6dWlkYW0zdTgnOiAn5pyA5aSnJywKICAgICAgICAgICAgICAgICdiam0zdTgnOiAn5YWr5oiSJywKICAgICAgICAgICAgICAgICdzbm0zdTgnOiAn57Si5bC8JywKICAgICAgICAgICAgICAgICd3b2xvbmcnOiAn5Y2n6b6ZJywKICAgICAgICAgICAgICAgICd4bG0zdTgnOiAn5paw5rWqJywKICAgICAgICAgICAgICAgICd5aG0zdTgnOiAn5qix6IqxJywKICAgICAgICAgICAgICAgICd0a20zdTgnOiAn5aSp56m6JywKICAgICAgICAgICAgICAgICdqc20zdTgnOiAn5p6B6YCfJywKICAgICAgICAgICAgICAgICd3am0zdTgnOiAn5peg5bC9JywKICAgICAgICAgICAgICAgICdzZG0zdTgnOiAn6Zeq55S1JywKICAgICAgICAgICAgICAgICdrY20zdTgnOiAn5b+r6L2mJywKICAgICAgICAgICAgICAgICdqaW55aW5nbTN1OCc6ICfph5HpubAnLAogICAgICAgICAgICAgICAgJ2ZzbTN1OCc6ICfpo57pgJ8nLAogICAgICAgICAgICAgICAgJ3RwbTN1OCc6ICfmt5jniYcnLAogICAgICAgICAgICAgICAgJ2xlbTN1OCc6ICfpsbzkuZAnLAogICAgICAgICAgICAgICAgJ2RibTN1OCc6ICfnmb7luqYnLAogICAgICAgICAgICAgICAgJ3RvbW0zdTgnOiAn55Wq6IyEJywKICAgICAgICAgICAgICAgICd1a20zdTgnOiAnVemFtycsCiAgICAgICAgICAgICAgICAnaWttM3U4JzogJ+eIseWdpCcsCiAgICAgICAgICAgICAgICAnaG56eW0zdTgnOiAn57qi54mb6LWE5rqQJywKICAgICAgICAgICAgICAgICdobm0zdTgnOiAn57qi54mbJywKICAgICAgICAgICAgICAgICc2OHp5X20zdTgnOiAnNjgnLAogICAgICAgICAgICAgICAgJ2tkbTN1OCc6ICfphbfngrknLAogICAgICAgICAgICAgICAgJ2JkeG0zdTgnOiAn5YyX5paX5pifJywKICAgICAgICAgICAgICAgICdxaG0zdTgnOiAn5aWH6JmOJywKICAgICAgICAgICAgICAgICdoaG0zdTgnOiAn6LGq5Y2OJwogICAgICAgICAgICB9OwogICAgICAgICAgICBlcGlzb2Rlcy5mb3JFYWNoKGZ1bmN0aW9uKGVwKSB7CiAgICAgICAgICAgICAgICBsZXQgZGF0YSA9IEpTT04ucGFyc2UoZXBbJ3Jlc0RhdGEnXSk7CiAgICAgICAgICAgICAgICBkYXRhLm1hcCh2YWwgPT4gewogICAgICAgICAgICAgICAgICAgIGlmKCFtYXBbdmFsLmZsYWddKXsKICAgICAgICAgICAgICAgICAgICAgICAgbWFwW3ZhbC5mbGFnXSA9IFt2YWwudXJsLnJlcGxhY2VBbGwoJyMjJywnIycpXQogICAgICAgICAgICAgICAgICAgIH0gZWxzZSB7CiAgICAgICAgICAgICAgICAgICAgICAgIG1hcFt2YWwuZmxhZ10ucHVzaCh2YWwudXJsLnJlcGxhY2VBbGwoJyMjJywnIycpKQogICAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgIH0pCiAgICAgICAgICAgIH0pOwogICAgICAgICAgICBmb3IgKHZhciBrZXkgaW4gbWFwKSB7CiAgICAgICAgICAgICAgICBpZiAoJ2JmenltM3U4JyA9PSBrZXkpIHsKICAgICAgICAgICAgICAgICAgICBhcnIucHVzaCh7CiAgICAgICAgICAgICAgICAgICAgICAgIGZsYWc6IG5hbWVba2V5XSwKICAgICAgICAgICAgICAgICAgICAgICAgdXJsOiBtYXBba2V5XSwKICAgICAgICAgICAgICAgICAgICAgICAgc29ydDogMQogICAgICAgICAgICAgICAgICAgIH0pCiAgICAgICAgICAgICAgICB9IGVsc2UgaWYgKCcxMDgwenlrJyA9PSBrZXkpIHsKICAgICAgICAgICAgICAgICAgICBhcnIucHVzaCh7CiAgICAgICAgICAgICAgICAgICAgICAgIGZsYWc6IG5hbWVba2V5XSwKICAgICAgICAgICAgICAgICAgICAgICAgdXJsOiBtYXBba2V5XSwKICAgICAgICAgICAgICAgICAgICAgICAgc29ydDogMgogICAgICAgICAgICAgICAgICAgIH0pCiAgICAgICAgICAgICAgICB9IGVsc2UgaWYgKCdrdWFpa2FuJyA9PSBrZXkpIHsKICAgICAgICAgICAgICAgICAgICBhcnIucHVzaCh7CiAgICAgICAgICAgICAgICAgICAgICAgIGZsYWc6IG5hbWVba2V5XSwKICAgICAgICAgICAgICAgICAgICAgICAgdXJsOiBtYXBba2V5XSwKICAgICAgICAgICAgICAgICAgICAgICAgc29ydDogMwogICAgICAgICAgICAgICAgICAgIH0pCiAgICAgICAgICAgICAgICB9IGVsc2UgaWYgKCdsem0zdTgnID09IGtleSkgewogICAgICAgICAgICAgICAgICAgIGFyci5wdXNoKHsKICAgICAgICAgICAgICAgICAgICAgICAgZmxhZzogbmFtZVtrZXldLAogICAgICAgICAgICAgICAgICAgICAgICB1cmw6IG1hcFtrZXldLAogICAgICAgICAgICAgICAgICAgICAgICBzb3J0OiA0CiAgICAgICAgICAgICAgICAgICAgfSkKICAgICAgICAgICAgICAgIH0gZWxzZSBpZiAoJ2ZmbTN1OCcgPT0ga2V5KSB7CiAgICAgICAgICAgICAgICAgICAgYXJyLnB1c2goewogICAgICAgICAgICAgICAgICAgICAgICBmbGFnOiBuYW1lW2tleV0sCiAgICAgICAgICAgICAgICAgICAgICAgIHVybDogbWFwW2tleV0sCiAgICAgICAgICAgICAgICAgICAgICAgIHNvcnQ6IDUKICAgICAgICAgICAgICAgICAgICB9KQogICAgICAgICAgICAgICAgfSBlbHNlIGlmICgnc25tM3U4JyA9PSBrZXkpIHsKICAgICAgICAgICAgICAgICAgICBhcnIucHVzaCh7CiAgICAgICAgICAgICAgICAgICAgICAgIGZsYWc6IG5hbWVba2V5XSwKICAgICAgICAgICAgICAgICAgICAgICAgdXJsOiBtYXBba2V5XSwKICAgICAgICAgICAgICAgICAgICAgICAgc29ydDogNgogICAgICAgICAgICAgICAgICAgIH0pCiAgICAgICAgICAgICAgICB9IGVsc2UgaWYgKCdxaG0zdTgnID09IGtleSkgewogICAgICAgICAgICAgICAgICAgIGFyci5wdXNoKHsKICAgICAgICAgICAgICAgICAgICAgICAgZmxhZzogbmFtZVtrZXldLAogICAgICAgICAgICAgICAgICAgICAgICB1cmw6IG1hcFtrZXldLAogICAgICAgICAgICAgICAgICAgICAgICBzb3J0OiA3CiAgICAgICAgICAgICAgICAgICAgfSkKICAgICAgICAgICAgICAgIH0gZWxzZSB7CiAgICAgICAgICAgICAgICAgICAgYXJyLnB1c2goewogICAgICAgICAgICAgICAgICAgICAgICBmbGFnOiAobmFtZVtrZXldKSA/IG5hbWVba2V5XSA6IGtleSwKICAgICAgICAgICAgICAgICAgICAgICAgdXJsOiBtYXBba2V5XSwKICAgICAgICAgICAgICAgICAgICAgICAgc29ydDogOAogICAgICAgICAgICAgICAgICAgIH0pCiAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgIH0KICAgICAgICAgICAgYXJyLnNvcnQoKGEsIGIpID0+IGEuc29ydCAtIGIuc29ydCk7CiAgICAgICAgICAgIGxldCBwbGF5RnJvbSA9IFtdOwogICAgICAgICAgICBsZXQgcGxheUxpc3QgPSBbXTsKICAgICAgICAgICAgYXJyLm1hcCh2YWwgPT4gewogICAgICAgICAgICAgICAgaWYgKCEvdW5kZWZpbmVkLy50ZXN0KHZhbC5mbGFnKSkgewogICAgICAgICAgICAgICAgICAgIHBsYXlGcm9tLnB1c2godmFsLmZsYWcpOwogICAgICAgICAgICAgICAgICAgIHBsYXlMaXN0LnB1c2godmFsLnVybCk7CiAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgIH0pCiAgICAgICAgICAgIGxldCB2b2RfcGxheV9mcm9tID0gcGxheUZyb20uam9pbignJCQkJyk7CiAgICAgICAgICAgIGxldCB2b2RfcGxheV91cmwgPSBwbGF5TGlzdC5qb2luKCckJCQnKTsKICAgICAgICAgICAgVk9EWyd2b2RfcGxheV9mcm9tJ10gPSB2b2RfcGxheV9mcm9tOwogICAgICAgICAgICBWT0RbJ3ZvZF9wbGF5X3VybCddID0gdm9kX3BsYXlfdXJsOwogICAgICAgICAgICAvLyBsb2coVk9EKTsKICAgICAgICB9IGNhdGNoIChlKSB7CiAgICAgICAgICAgIGxvZygn6I635Y+W5LqM57qn6K+m5oOF6aG15Y+R55Sf6ZSZ6K+vOicgKyBlLm1lc3NhZ2UpCiAgICAgICAgfQ==")))',
    // 搜索:'#search-result&&.media;h5&&a&&Text;a&&img&&data-src;.label&&Text;a&&href',//第三个是描述，一般显示更新或者完结
	搜索:'.col-md-8&&.media;h5&&a&&Text;a&&img&&data-src;.label&&Text;a&&href',//第三个是描述，一般显示更新或者完结
}