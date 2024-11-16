<?php
/*
食用方法litv.php?id=4gtv-4gtv001
一般来说没声音调节第二个参数就行，从1-10.
*/
error_reporting(0);
header('Content-Type: text/plain; charset=utf-8');

$id = isset($_GET['id']) ? $_GET['id'] : 'litv-longturn14';

$n = array(
		'4gtv-4gtv001' => [1, 6],//民视台湾台
		'4gtv-4gtv002' => [1, 10],//民视
		'4gtv-4gtv003' => [1, 6],//民视第一台
		'4gtv-4gtv004' => [1, 8],//民视综艺
		'4gtv-4gtv006' => [1, 9],//猪哥亮歌厅秀
		'4gtv-4gtv009' => [2, 7],//中天新闻
		'4gtv-4gtv010' => [1, 2],//非凡新闻
		'4gtv-4gtv011' => [1, 6],//影迷數位電影台
		'4gtv-4gtv013' => [1, 2],//視納華仁紀實頻道
		'4gtv-4gtv014' => [1, 5],//时尚运动X
		'4gtv-4gtv016' => [1, 6],//GLOBETROTTER
		'4gtv-4gtv017' => [1, 6],//amc电影台
		'4gtv-4gtv018' => [1, 10],//达文西频道
		'4gtv-4gtv034' => [1, 6],//八大精彩台
		'4gtv-4gtv039' => [1, 7],//八大综艺台
		'4gtv-4gtv040' => [1, 6],//中视
		'4gtv-4gtv041' => [1, 6],//华视
		'4gtv-4gtv042' => [1, 6],//公视戏剧
		'4gtv-4gtv043' => [1, 6],//客家电视台
		'4gtv-4gtv044' => [1, 8],//靖天卡通台
		'4gtv-4gtv045' => [1, 6],//靖洋戏剧台
		'4gtv-4gtv046' => [1, 8],//靖天综合台
		'4gtv-4gtv047' => [1, 8],//靖天日本台
		'4gtv-4gtv048' => [1, 2],//非凡商业
		'4gtv-4gtv049' => [1, 8],//采昌影剧
		'4gtv-4gtv051' => [1, 6],//台视新闻
		'4gtv-4gtv052' => [1, 8],//华视新闻
		'4gtv-4gtv053' => [1, 8],//GinxTV
		'4gtv-4gtv054' => [1, 8],//靖天欢乐台
		'4gtv-4gtv055' => [1, 8],//靖天映画
		'4gtv-4gtv056' => [1, 2],//台视财经
		'4gtv-4gtv057' => [1, 8],//靖洋卡通台
		'4gtv-4gtv058' => [1, 8],//靖天戏剧台
		'4gtv-4gtv059' => [1, 6],//古典音乐台
		'4gtv-4gtv061' => [1, 7],//靖天电影台
		'4gtv-4gtv062' => [1, 8],//靖天育乐台
		'4gtv-4gtv063' => [1, 6],//靖天国际台
		'4gtv-4gtv064' => [1, 8],//中视菁采
		'4gtv-4gtv065' => [1, 8],//靖天资讯台
		'4gtv-4gtv066' => [1, 2],//台视
		'4gtv-4gtv067' => [1, 8],//tvbs精采台
		'4gtv-4gtv068' => [1, 7],//tvbs欢乐台
		'4gtv-4gtv070' => [1, 7],//爱尔达娱乐
		'4gtv-4gtv072' => [1, 2],//tvbs新闻台
		'4gtv-4gtv073' => [1, 8],//tvbs
		'4gtv-4gtv074' => [1, 8],//中视新闻
		'4gtv-4gtv075' => [1, 6],//镜新闻
		'4gtv-4gtv076' => [1, 2],//CATCHPLAY电影台
		'4gtv-4gtv077' => [1, 7],//TRACE SPORTS STARS
		'4gtv-4gtv079' => [1, 2],//阿里郎
		'4gtv-4gtv080' => [1, 5],//中视经典
		'4gtv-4gtv082' => [1, 7],//TRACE URBAN
		'4gtv-4gtv083' => [1, 6],//MEZZO LIVE
		'4gtv-4gtv084' => [1, 6],//国会频道1
		'4gtv-4gtv085' => [1, 5],//国会频道2
		'4gtv-4gtv101' => [1, 6],//智林体育台
		'4gtv-4gtv104' => [1, 7],//国际财经
		'4gtv-4gtv109' => [1, 7],//第1商業台
		'4gtv-4gtv152' => [1, 6],//东森新闻
		'4gtv-4gtv153' => [1, 6],//东森财经新闻
		'4gtv-4gtv155' => [1, 6],//民视
		'4gtv-4gtv156' => [1, 2],//民视台湾台
		'litv-ftv03' => [1, 7],//美国之音
		'litv-ftv07' => [1, 7],//民视旅游
		'litv-ftv09' => [1, 7],//民视影剧
		'litv-ftv10' => [1, 7],//半岛新闻
		'litv-ftv13' => [1, 7],//民视新闻台
		'litv-ftv15' => [1, 7],//爱放动漫
		'litv-ftv16' => [1, 2],//好消息
		'litv-ftv17' => [1, 2],//好消息2台
		'litv-longturn01' => [4, 2],//龙华卡通
		'litv-longturn03' => [5, 2],//龙华电影
		'litv-longturn04' => [5, 2],//博斯魅力
		'litv-longturn05' => [5, 2],//博斯高球1
		'litv-longturn06' => [5, 2],//博斯高球2
		'litv-longturn07' => [5, 2],//博斯运动1
		'litv-longturn08' => [5, 2],//博斯运动2
		'litv-longturn09' => [5, 2],//博斯网球
		'litv-longturn10' => [5, 2],//博斯无限
		'litv-longturn11' => [5, 2],//龙华日韩
		'litv-longturn12' => [5, 2],//龙华偶像
		'litv-longturn13' => [4, 2],//博斯无限2
		'litv-longturn14' => [1, 6],//寰宇新闻台
		'litv-longturn15' => [5, 2],//寰宇新闻台湾台
		'litv-longturn17' => [5, 2],//亚洲旅游台
		'litv-longturn18' => [5, 2],//龙华戏剧
		'litv-longturn19' => [5, 2],//Smart知识台
		'litv-longturn20' => [5, 2],//生活英语台
		'litv-longturn21' => [5, 2],//龙华经典
		'litv-longturn22' => [5, 2],//台湾戏剧台
);

$timestamp = intval(time() / 4 - 355017625);
$t = $timestamp * 4;

$current = "#EXTM3U" . "\r\n";
$current .= "#EXT-X-VERSION:3" . "\r\n";
$current .= "#EXT-X-TARGETDURATION:4" . "\r\n";
$current .= "#EXT-X-MEDIA-SEQUENCE:{$timestamp}" . "\r\n";

for ($i = 0; $i < 10; $i++) {
    $current .= "#EXTINF:4," . "\r\n";
    $current .= "proxy.php?url=https://litvpc-hichannel.cdn.hinet.net/live/pool/{$id}/litv-pc/{$id}-avc1_6000000={$n[$id][0]}-mp4a_134000_zho={$n[$id][1]}-begin={$t}0000000-dur=40000000-seq={$timestamp}.ts" . "\r\n";
    $timestamp++;
    $t += 4;
}

header('Content-Type: application/vnd.apple.mpegurl'); 
header('Content-Disposition: inline; filename='.$id.'.m3u8');
header('Content-Length: ' . strlen($current)); 
echo $current;
?>