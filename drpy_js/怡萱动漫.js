// 发布页 https://acgfans.org/pub.html
var rule={
	title:'怡萱动漫',
	// host:'https://www.yxdmlove.com',
	host:'https://acgfans.org/pub.html',
	hostJs:'print(HOST);let html=request(HOST,{headers:{"User-Agent":PC_UA}});let src = jsp.pdfh(html,"p:eq(0)&&a&&Text");print(src);HOST=src',//网页域名根动态抓取js代码。通过HOST=赋值
	// url:'/category.html?channel=17&zhonglei=fyclass&orderby=pubdate&totalresult=2999&pageno=fypage',
	url:'/category.html?channel=17&zhonglei=fyclassfyfilter&pageno=fypage',
	filterable:1,//是否启用分类筛选,
	filter_url:'&{{fl.by or "orderby=pubdate"}}&{{fl.year}}&{{fl.area}}&{{fl.sta}}&{{fl.class}}',
	filter: {
		"TV":[{"key":"sta","name":"进度","value":[{"n":"全部","v":""},{"n":"连载中","v":"status=连载中"},{"n":"已完结","v":"status=已完结"},{"n":"未播放","v":"status=未播放"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"日本","v":"area=日本"},{"n":"中国","v":"area=中国"},{"n":"欧美","v":"area=欧美"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"year=2024"},{"n":"2023","v":"year=2023"},{"n":"2022","v":"year=2022"},{"n":"2021","v":"year=2021"},{"n":"2020","v":"year=2020"},{"n":"2019","v":"year=2019"},{"n":"2018","v":"year=2018"},{"n":"2017","v":"year=2017"},{"n":"2016","v":"year=2016"},{"n":"2015","v":"year=2015"},{"n":"2014","v":"year=2014"},{"n":"2013","v":"year=2013"},{"n":"2012","v":"year=2012"},{"n":"2011","v":"year=2011"},{"n":"2010","v":"year=2010"},{"n":"更早","v":"year=2010前"}]},{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"冒险","v":"jqlx=冒险"},{"n":"热血","v":"jqlx=热血"},{"n":"爱情","v":"jqlx=爱情"},{"n":"搞笑","v":"jqlx=搞笑"},{"n":"后宫","v":"jqlx=后宫"},{"n":"校园","v":"jqlx=校园"},{"n":"机战","v":"jqlx=机战"},{"n":"幻想","v":"jqlx=幻想"},{"n":"科幻","v":"jqlx=科幻"},{"n":"竞技","v":"jqlx=竞技"},{"n":"百合","v":"jqlx=百合"},{"n":"耽美","v":"jqlx=耽美"},{"n":"悬疑","v":"jqlx=悬疑"},{"n":"剧情","v":"jqlx=剧情"},{"n":"战争","v":"jqlx=战争"},{"n":"恐怖","v":"jqlx=恐怖"},{"n":"运动","v":"jqlx=运动"},{"n":"动作","v":"jqlx=动作"},{"n":"童话","v":"jqlx=童话"},{"n":"历史","v":"jqlx=历史"},{"n":"真人","v":"jqlx=真人"},{"n":"女性向","v":"jqlx=女性向"},{"n":"泡面番","v":"jqlx=泡面番"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"orderby=pubdate"},{"n":"热度","v":"orderby=click"}]}],
		"剧场版":[{"key":"sta","name":"进度","value":[{"n":"全部","v":""},{"n":"连载中","v":"status=连载中"},{"n":"已完结","v":"status=已完结"},{"n":"未播放","v":"status=未播放"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"日本","v":"area=日本"},{"n":"中国","v":"area=中国"},{"n":"欧美","v":"area=欧美"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"year=2024"},{"n":"2023","v":"year=2023"},{"n":"2022","v":"year=2022"},{"n":"2021","v":"year=2021"},{"n":"2020","v":"year=2020"},{"n":"2019","v":"year=2019"},{"n":"2018","v":"year=2018"},{"n":"2017","v":"year=2017"},{"n":"2016","v":"year=2016"},{"n":"2015","v":"year=2015"},{"n":"2014","v":"year=2014"},{"n":"2013","v":"year=2013"},{"n":"2012","v":"year=2012"},{"n":"2011","v":"year=2011"},{"n":"2010","v":"year=2010"},{"n":"更早","v":"year=2010前"}]},{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"冒险","v":"jqlx=冒险"},{"n":"热血","v":"jqlx=热血"},{"n":"爱情","v":"jqlx=爱情"},{"n":"搞笑","v":"jqlx=搞笑"},{"n":"后宫","v":"jqlx=后宫"},{"n":"校园","v":"jqlx=校园"},{"n":"机战","v":"jqlx=机战"},{"n":"幻想","v":"jqlx=幻想"},{"n":"科幻","v":"jqlx=科幻"},{"n":"竞技","v":"jqlx=竞技"},{"n":"百合","v":"jqlx=百合"},{"n":"耽美","v":"jqlx=耽美"},{"n":"悬疑","v":"jqlx=悬疑"},{"n":"剧情","v":"jqlx=剧情"},{"n":"战争","v":"jqlx=战争"},{"n":"恐怖","v":"jqlx=恐怖"},{"n":"运动","v":"jqlx=运动"},{"n":"动作","v":"jqlx=动作"},{"n":"童话","v":"jqlx=童话"},{"n":"历史","v":"jqlx=历史"},{"n":"真人","v":"jqlx=真人"},{"n":"女性向","v":"jqlx=女性向"},{"n":"泡面番","v":"jqlx=泡面番"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"orderby=pubdate"},{"n":"热度","v":"orderby=click"}]}],
		"OVA":[{"key":"sta","name":"进度","value":[{"n":"全部","v":""},{"n":"连载中","v":"status=连载中"},{"n":"已完结","v":"status=已完结"},{"n":"未播放","v":"status=未播放"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"日本","v":"area=日本"},{"n":"中国","v":"area=中国"},{"n":"欧美","v":"area=欧美"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"year=2024"},{"n":"2023","v":"year=2023"},{"n":"2022","v":"year=2022"},{"n":"2021","v":"year=2021"},{"n":"2020","v":"year=2020"},{"n":"2019","v":"year=2019"},{"n":"2018","v":"year=2018"},{"n":"2017","v":"year=2017"},{"n":"2016","v":"year=2016"},{"n":"2015","v":"year=2015"},{"n":"2014","v":"year=2014"},{"n":"2013","v":"year=2013"},{"n":"2012","v":"year=2012"},{"n":"2011","v":"year=2011"},{"n":"2010","v":"year=2010"},{"n":"更早","v":"year=2010前"}]},{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"冒险","v":"jqlx=冒险"},{"n":"热血","v":"jqlx=热血"},{"n":"爱情","v":"jqlx=爱情"},{"n":"搞笑","v":"jqlx=搞笑"},{"n":"后宫","v":"jqlx=后宫"},{"n":"校园","v":"jqlx=校园"},{"n":"机战","v":"jqlx=机战"},{"n":"幻想","v":"jqlx=幻想"},{"n":"科幻","v":"jqlx=科幻"},{"n":"竞技","v":"jqlx=竞技"},{"n":"百合","v":"jqlx=百合"},{"n":"耽美","v":"jqlx=耽美"},{"n":"悬疑","v":"jqlx=悬疑"},{"n":"剧情","v":"jqlx=剧情"},{"n":"战争","v":"jqlx=战争"},{"n":"恐怖","v":"jqlx=恐怖"},{"n":"运动","v":"jqlx=运动"},{"n":"动作","v":"jqlx=动作"},{"n":"童话","v":"jqlx=童话"},{"n":"历史","v":"jqlx=历史"},{"n":"真人","v":"jqlx=真人"},{"n":"女性向","v":"jqlx=女性向"},{"n":"泡面番","v":"jqlx=泡面番"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"orderby=pubdate"},{"n":"热度","v":"orderby=click"}]}],
		"其他":[{"key":"sta","name":"进度","value":[{"n":"全部","v":""},{"n":"连载中","v":"status=连载中"},{"n":"已完结","v":"status=已完结"},{"n":"未播放","v":"status=未播放"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"日本","v":"area=日本"},{"n":"中国","v":"area=中国"},{"n":"欧美","v":"area=欧美"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"year=2024"},{"n":"2023","v":"year=2023"},{"n":"2022","v":"year=2022"},{"n":"2021","v":"year=2021"},{"n":"2020","v":"year=2020"},{"n":"2019","v":"year=2019"},{"n":"2018","v":"year=2018"},{"n":"2017","v":"year=2017"},{"n":"2016","v":"year=2016"},{"n":"2015","v":"year=2015"},{"n":"2014","v":"year=2014"},{"n":"2013","v":"year=2013"},{"n":"2012","v":"year=2012"},{"n":"2011","v":"year=2011"},{"n":"2010","v":"year=2010"},{"n":"更早","v":"year=2010前"}]},{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"冒险","v":"jqlx=冒险"},{"n":"热血","v":"jqlx=热血"},{"n":"爱情","v":"jqlx=爱情"},{"n":"搞笑","v":"jqlx=搞笑"},{"n":"后宫","v":"jqlx=后宫"},{"n":"校园","v":"jqlx=校园"},{"n":"机战","v":"jqlx=机战"},{"n":"幻想","v":"jqlx=幻想"},{"n":"科幻","v":"jqlx=科幻"},{"n":"竞技","v":"jqlx=竞技"},{"n":"百合","v":"jqlx=百合"},{"n":"耽美","v":"jqlx=耽美"},{"n":"悬疑","v":"jqlx=悬疑"},{"n":"剧情","v":"jqlx=剧情"},{"n":"战争","v":"jqlx=战争"},{"n":"恐怖","v":"jqlx=恐怖"},{"n":"运动","v":"jqlx=运动"},{"n":"动作","v":"jqlx=动作"},{"n":"童话","v":"jqlx=童话"},{"n":"历史","v":"jqlx=历史"},{"n":"真人","v":"jqlx=真人"},{"n":"女性向","v":"jqlx=女性向"},{"n":"泡面番","v":"jqlx=泡面番"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"orderby=pubdate"},{"n":"热度","v":"orderby=click"}]}]
	},
	// filter_def:{
	// 	TV:{by:'orderby=pubdate'},
	// 	剧场版:{by:'orderby=pubdate'},
	// 	OVA:{by:'orderby=pubdate'},
	// 	其他:{by:'orderby=pubdate'}
	// },
	searchUrl:'/search.html?keyword=**&PageNo=fypage',
	searchable:2,//是否启用全局搜索,
	headers:{//网站的请求头,完整支持所有的,常带ua和cookies
		'User-Agent': 'PC_UA',
	},
	class_name:'TV&剧场版&OVA&其他',
	class_url:'TV&剧场版&OVA&其他',
	play_parse: true,
	lazy:'',
	limit:6,
	// 推荐:'.dhnew.adj li;*;*;*;*',
	推荐:'.dhnew.adj li;a&&title;img&&src;p:eq(-1)&&Text;a&&href',
	// 一级:'.dhnew li;a&&title;img&&src;p:eq(-1)&&Text;a&&href',
	一级:`js:
		let d = [];
		pdfh = jsp.pdfh;pdfa = jsp.pdfa;pd = jsp.pd;
		let html = '';
		let totalresult = getItem("totalresult_" + MY_CATE, '')
		if (totalresult == '') {
			html = request(input);
			totalresult = pdfh(html, ".pageinfo&&strong&&Text");
			setItem("totalresult_" + MY_CATE, totalresult)
        }
		input += '&totalresult=' + getItem("totalresult_" + MY_CATE, '');
		html = request(input);
		let list = pdfa(html, ".dhnew&&li");
		list.forEach(it => {
			d.push({
				title: pdfh(it, "a&&title"),
				desc: pdfh(it, "p:eq(-1)&&Text"),
				pic_url: pd(it, "img&&src"),
				url: pd(it, "a&&href")
			})
		});
		setResult(d)
	`,
	二级:{
		"title":"h1&&Text;.dhxx p:eq(4)&&Text",
		"img":".anime-img&&img&&src",
		"desc":".info1-left li:eq(1)&&Text;.dhxx p:eq(3)&&Text;.dhxx p:eq(2)&&Text;.info1-left li:eq(0)&&Text;.info1-left li:eq(2)&&Text",
		"content":".info2--strong&&Text",
		"tabs":".ol-select li",
		"lists":".ol-content:eq(#id) li"
	},
	// 搜索:'*;*;*;p:eq(3)&&Text;*',
	搜索:'.dhnew li;a&&title;img&&src;p:eq(3)&&Text;a&&href',
}