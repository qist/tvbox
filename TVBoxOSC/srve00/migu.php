<?php

// 先检查 cache/cache_{id}.json 是否存在，且时间未超过 CACHE_TIMEOUT（5分钟）。
// 如果缓存有效，直接返回缓存的 m3u8 地址。
// 如果缓存无效，则请求 API，并存入缓存。
// 异常处理

// 增加 isset($n[$id]) 检测，防止 id 不存在时报错。
// 检查 API 返回的数据是否正确，避免解析 null 时报错。
// 优化 generateRandomString()

// 直接使用 str_shuffle() 生成随机字符串，性能更优。

// 运行逻辑
// 1.首次访问
// 没有缓存 → 请求 API → 解析 URL → 存入缓存 → 返回播放地址。
// 2.后续访问
// 在 5 分钟内使用缓存，避免重复请求 API。
// 超过 5 分钟后自动刷新缓存。

// 群 https://t.me/IPTV_9999999
// https://t.me/livednowgroup/379744



error_reporting(0);

// 缓存目录
define("CACHE_DIR", __DIR__ . "/cache/");
define("CACHE_TIMEOUT", 600); // 缓存时间 5 分钟

// 确保缓存目录存在
if (!file_exists(CACHE_DIR)) {
    mkdir(CACHE_DIR, 0777, true);
}

$id = isset($_GET['id']) ? $_GET['id'] : 'cctv1';
$n = [
    'cctv1' => '608807420', //CCTV1综合
    'cctv2' => '631780532', //CCTV2财*
    'cctv3' => '624878271', //CCTV3综艺
    'cctv4' => '631780421', //CCTV4中文国际
    'cctv4a' => '608807416', //CCTV4美洲
    'cctv4o' => '608807419', //CCTV4欧洲
    'cctv5' => '641886683', //CCTV5体育
    'cctv5p' => '641886773', //CCTV5+体育赛事
    'cctv6' => '624878396', //CCTV6电影
    'cctv7' => '673168121', //CCTV7国防军事
    'cctv8' => '624878356', //CCTV8电视剧
    'cctv9' => '673168140', //CCTV9纪录
    'cctv10' => '624878405', //CCTV10科教
    'cctv11' => '667987558', //CCTV11戏曲
    'cctv12' => '673168185', //CCTV12社会与法
    'cctv13' => '608807423', //CCTV13新闻
    'cctv14' => '624878440', //CCTV14少儿
    'cctv15' => '673168223', //CCTV15音乐
    'cctv17' => '673168256', //CCTV17农业农村

    'fxzl' => '624878970', //CCTV发现之旅
    'lgs' => '884121956', //CCTV老故事
    'zxs' => '708869532', //CCTV中学生

    'cgtn' => '609017205', //CGTN
    'cgtnjl' => '609006487', //CGTN纪录
    'cgtne' => '609006450', //CCTV西班牙语
    'cgtnf' => '609006476', //CCTV法语
    'cgtna' => '609154345', //CCTV阿拉伯语
    'cgtnr' => '609006446', //CCTV俄语

    'dfws' => '651632648', //东方卫视
    'cqws' => '738910914', //重庆卫视
    'jlws' => '738906889', //吉林卫视
    'lnws' => '630291707', //辽宁卫视
    'nmws' => '738911430', //内蒙古卫视
    'nxws' => '738910535', //宁夏卫视
    'gsws' => '738910997', //甘肃卫视
    'qhws' => '738898486', //青海卫视
    'sxws' => '738910838', //陕西卫视
    'sdws' => '738910366', //山东卫视
    'hnws' => '790187291', //河南卫视
    'hubws' => '738906825', //湖北卫视
    'hunws' => '635491149', //湖南卫视
    'jxws' => '783847495', //江西卫视
    'jsws' => '623899368', //江苏卫视
    'dnws' => '849116810', //东南卫视
    'hxws' => '849119120', //海峡卫视
    'gdws' => '608831231', //广东卫视
    'dwqws' => '608917627', //大湾区卫视
    'gxws' => '783844132', //广西卫视
    'ynws' => '783846580', //云南卫视
    'gzws' => '783845222', //贵州卫视
    'xjws' => '738910476', //新疆卫视
    'xzws' => '738910461', //西藏卫视
    'hinws' => '738906860', //海南卫视

    'shdy' => '895358641', //四海钓鱼
    'chcjt' => '644368373', //CHC家庭影院
    'chcdz' => '644368714', //CHC动作电影

    'dfys' => '617290047', //东方影视
    'shxwzh' => '651632657', //上海新闻综合
    'dycj' => '608780988', //上海第一财经
    'shjsrw' => '617289997', //上视纪实人文
    'shics' => '618954688', //上海外语
    'fztd' => '790188943', //法治天地
    'jbty' => '796071336', //劲爆体育
    'mlzq' => '796070308', //魅力足球
    'ly' => '796070452', //乐游
    'hxjc' => '790187880', //欢笑剧场
    'qcxj' => '796071456', //七彩戏剧
    'yxfy' => '790188417', //游戏风云

    'lttv' => '668225749', //临洮电视台

    'jscs' => '626064714', //江苏城市
    'jszy' => '626065193', //江苏综艺
    'jsys' => '626064697', //江苏影视
    'jsggxw' => '626064693', //江苏公共新闻
    'jsgj' => '626064674', //江苏国际
    'jsjy' => '628008321', //江苏教育
    'jstyxx' => '626064707', //江苏体育休闲
    'ymkt' => '626064703', //优漫卡通

    'njxwzh' => '838109047', //南京新闻综合
    'njkj' => '838153729', //南京教科
    'njsb' => '838151753', //南京十八

    'haxwzh' => '639731826', //淮安新闻综合
    'lygxwzh' => '639731715', //连云港新闻综合
    'szxwzh' => '639731952', //苏州新闻综合
    'tzxwzh' => '639731818', //泰州新闻综合
    'sqxwzh' => '639731832', //宿迁新闻综合
    'xzxwzh' => '639731747', //徐州新闻综合

    'gdys' => '614961829', //广东影视
    'jjkt' => '614952364', //嘉佳卡通

    '24hyzb' => '895932793', //24小时亚洲杯频道
    'cbajd' => '788813182', //CBA经典
    'gdjys' => '631354620', //掼蛋精英赛
    'gqdp' => '629943678', //高清大片
    'hpjxss' => '780290695', //和平精英赛事
    'hslbt' => '713600957', //红色轮播台
    'jddhdjh' => '629942219', //经典动画大集合
    'jdxgdy' => '625703337', //经典香港电影
    'jsdp' => '617432318', //军事迷必看大片
    'hyytzqy' => '707671890', //华语乐坛最强音
    'mg24hty' => '654102378', //咪咕24小时体育台
    'nbajd' => '788815380', //NBA经典
    'ozzqfy' => '788816794', //欧洲足球风云
    'qmpp' => '788818045', //全民乒乓
    'sszjd' => '646596895', //赛事最经典
    'ttmlh' => '629943305', //体坛名栏汇
    'ufcgdjx' => '788818804', //UFC格斗精选
    'wdlsjd' => '780288994', //五大联赛经典
    'jsjc' => '713591450', //金色剧场
    'xczx' => '713589837', //乡村振兴
    'xfzgn' => '617432318', //幸福中国年
    'xpfyt' => '619495952', //新片放映厅
    'jpjc' => '615810094', //精品剧场
    'yxlmss' => '780286989', //英雄联盟赛事
    'zjlxc' => '625133682', //周杰伦现场
    'zqzyp' => '629942228', //最强综艺趴

    'xmpd' => '609158151', //熊猫01高清
    'xm1' => '608933610', //熊猫1
    'xm2' => '608933640', //熊猫2
    'xm3' => '608934619', //熊猫3
    'xm4' => '608934721', //熊猫4
    'xm5' => '608935104', //熊猫5
    'xm6' => '608935797', //熊猫6
    'xm7' => '609169286', //熊猫7
    'xm8' => '609169287', //熊猫8
    'xm9' => '609169226', //熊猫9
    'xm10' => '609169285', //熊猫10
];

if (!isset($n[$id])) {
    die("无效的 ID");
}

$cacheFile = CACHE_DIR . "cache_" . $id . ".json";

// **Step 1: 先检查缓存**
if (file_exists($cacheFile) && (time() - filemtime($cacheFile)) < CACHE_TIMEOUT) {
    $cacheData = json_decode(file_get_contents($cacheFile), true);
    if (!empty($cacheData['url'])) {
        header("Content-Type: application/vnd.apple.mpegURL");
        header("Location: " . $cacheData['url']);
        exit;
    }
}

// **Step 2: 请求 API**
function generateRandomString($length = 32) {
    return substr(str_shuffle('0123456789abcdef'), 0, $length);
}

$clientId = md5(generateRandomString());
$bstrURL = 'https://webapi.miguvideo.com/gateway/playurl/v3/play/playurl?contId=' . $n[$id] . '&rateType=3&clientId=' . $clientId . '&startPlay=true&xh265=false&chip=mgwww&channelId=0132_10010001005';

$d = date("YmdHis");

$headers = [
    'Content-Type: application/json',
    "Referer: https://www.miguvideo.com/",
    'Origin: https://www.miguvideo.com',
    'User-Agent: Mozilla/5.0 (Linux; Android 8.0.0; Mi Note 2 Build/OPR1.170623.032)',
    'Vtraceid:' . $clientId,
    'Traceid:' . $clientId,
    'Datafreshversion:' . $d,
    'Dataversion:' . $d,
];

$json = json_decode(get_data($bstrURL, $headers), true);

if (empty($json['body']['urlInfo']['url'])) {
    die("API 请求失败");
}

$live = $json['body']['urlInfo']['url'];
$uas = parse_url($live);
parse_str($uas["query"], $arr);
$puData = str_split($arr['puData']);
$ProgramID = str_split($n[$id]);
$Program = str_split('yzwxcdwbgh');

$s = count($puData);
$arr_key = [];
for ($v = 0; $v < $s / 2; $v++) {
    $arr_key[] = $puData[$s - $v - 1];
    $arr_key[] = $puData[$v];
    switch ($v) {
        case 1:
        case 2:
        case 4:
            $arr_key[] = arrkey($v);
            break;
        case 3:
            $arr_key[] = $Program[$ProgramID[1]];
            break;
    }
}
$ddCalcu = join($arr_key);

function arrkey($v) {
    $put = ['z', 'y', '0', 'z'];
    return $put[$v - 1];
}

$p = $live . "&ddCalcu=" . $ddCalcu . '&sv=10000&crossdomain=www&ct=www';

$playurl = get_data($p, $headers);

// **Step 3: 存入缓存**
file_put_contents($cacheFile, json_encode(['url' => $playurl], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));

// **Step 4: 返回 M3U8 地址**
header("Content-Type: application/vnd.apple.mpegURL");
header('Location: ' . $playurl);
exit;

/**
 * 发送 GET 请求
 */
function get_data($url, $header) {
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_TIMEOUT, 1);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $header);
    $data = curl_exec($ch);
    curl_close($ch);
    return $data;
}