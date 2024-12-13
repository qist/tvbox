var rule = {
	title:'爱盘搜[夸]',
	host:'https://aipanso.com',
	homeUrl:'/',
	url: '/forum-fyclass-fypage.html?',
	filter_url:'{{fl.class}}',
	filter:{
	},
	searchUrl: '/search?page=fypage&s=1&t=-1&k=**',
	searchable:2,
	quickSearch:0,
	filterable:0,
	headers:{
		'User-Agent': PC_UA,
		'Accept': '*/*',
		'Referer': 'https://aipanso.com/'
	},
	timeout:5000,
	class_name:'',
	class_url:'',
	play_parse:true,
	play_json:[{
		re:'*',
		json:{
			parse:0,
			jx:0
		}
	}],
	lazy:'',
	limit:6,
	推荐:'',
	一级:'',
	二级:{
		title:"van-row h3&&Text",
		img:"",
		desc:"van-row h3&&Text",
		content:"van-row h3&&Text",
		tabs:`js:
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
TABS=[]
TABS.push("夸克網盤");
log('meijumi TABS >>>>>>>>>>>>>>>>>>' + TABS);
`,
		lists:`js:
log(TABS);
LISTS=[];
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
let requestHeaders = {
    withHeaders: true,
    redirect: 0,
    headers:{
    	Referer: MY_URL
    }
};
let _fetch_params = JSON.parse(JSON.stringify(rule_fetch_params));
Object.assign(_fetch_params, requestHeaders);
let new_html = request ( MY_URL.replace("/s/","/cv/"), _fetch_params);
let json=JSON.parse(new_html);
let redirectUrl = "";
if (json.hasOwnProperty("Location")){
	redirectUrl = json["Location"];
}else if (json.hasOwnProperty("location")){
	redirectUrl = json["location"];
}
let title = pdfh(html, 'van-row h3&&Text');
LISTS.push([title + '$' + 'push://' + redirectUrl]);
`,
	},
	搜索:`js:
pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;

log("aipanso enter search >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" + KEY);
let withHeaders = {
    withHeaders: true
};
let _fetch_params = JSON.parse(JSON.stringify(rule_fetch_params));
Object.assign(_fetch_params, withHeaders);

log('aipanso search params >>>>>>>>>>>>>>>>>>>>>' + JSON.stringify(_fetch_params));
let new_html=request(rule.homeUrl + 'search?page=' + MY_PAGE + '&s=1&t=-1&k=' + encodeURIComponent(KEY) , _fetch_params);
//log('aipanso search new_html >>>>>>>>>>>>>>>>>>>>>' + new_html);
let json=JSON.parse(new_html);
let setCk=Object.keys(json).find(it=>it.toLowerCase()==="set-cookie");
let cookie="";
if (typeof setCk !== "undefined"){
	let d=[];
	for(const key in json[setCk]){
		if (typeof json[setCk][key] === "string"){
			log("aipanso header setCk key>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" + json[setCk][key] + " " + (typeof json[setCk][key]));
			d.push(json[setCk][key].split(";")[0]);
		}
	}
	cookie=d.join(";");
	setItem(RULE_CK, cookie);
	fetch_params.headers.Cookie=cookie;
	rule_fetch_params.headers.Cookie=cookie;
}
log('aipanso search cookie >>>>>>>>>>>>>>>>>>>>>' + cookie);
//log('aipanso search body >>>>>>>>>>>>>>>>>>>>>' + json['body'].substring(4096));

new_html = json['body'];

let d=[];
let dlist = pdfa(new_html, 'van-row:has(>a[href^="/s/"])');
dlist.forEach(function(it){
	let title = pdfh(it, 'van-card template&&Text');
	if (title.includes(KEY)){
		if (searchObj.quick === true){
			title = KEY;
		}
		let img = pd(it, 'van-card&&thumb', HOST);
		let content = pdfh(it, 'van-card template:eq(1)&&Text');
		let desc = pdfh(it, 'van-card template:eq(1)&&Text');
		let url = pd(it, 'a&&href', HOST);
		d.push({
			title:title,
			img:img,
			content:content,
			desc:desc,
			url:url
			})
	}
});
setResult(d);
`,
}
