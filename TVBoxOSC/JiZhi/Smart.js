//https://files.catbox.moe/4dqdzg.js


function main(item) {
	const id = jz.getQuery(item.url, "id");
	let url = "http://50.7.234.10:8278/" + id + "/playlist.m3u8";
	const tid = "mc42afe745533";
	const t = String(Math.floor(Date.now() / 150));
	const tsum = jz.md5("tvata nginx auth module" + "/" + id + "/playlist.m3u8" + tid + t);
	url += "?tid=" + tid + "&" + "ct=" + t + "&tsum=" + tsum;
	return { url: url, headers: { 'CLIENT-IP': '127.0.0.1', 'X-FORWARDED-FOR': '127.0.0.1' } };
}