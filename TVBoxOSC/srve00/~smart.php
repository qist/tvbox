<?php
error_reporting(E_ALL); // 开启所有错误报告，便于调试
header('Content-Type: text/json;charset=UTF-8');
date_default_timezone_set("Asia/Shanghai");

// 继续执行其他逻辑
$name = $_GET["id"] ?? "";
$port = 'http://66.90.99.154:8278/';
$ts = $_GET["ts"] ?? "";

// 代理设置
$proxy = $_GET["proxy"] ?? ""; // 获取代理设置，例如 "http://username:password@host:port" 或 "socks5://host:port"
// 这里去掉了 token 相关的逻辑

$ip = '127.0.0.1';
$header = array(
    "CLIENT-IP:" . $ip,
    "X-FORWARDED-FOR:" . $ip,
);

if ($ts) {
    $host = $port . $name . "/";
    $url = $host . $ts;
    $data = curl_get($url, $header, $proxy);
    echo $data;
} else {
    $url = $port . $name . "/playlist.m3u8";
    $seed = "tvata nginx auth module";
    $path = parse_url($url, PHP_URL_PATH);
    $tid = "mc42afe745533";
    $t = strval(intval(time() / 150));
    $str = $seed . $path . $tid . $t;
    $tsum = md5($str);
    $link = http_build_query(["ct" => $t, "tsum" => $tsum]);
    $url .= "?tid=$tid&$link";

    $parseUrl = "http://" . $_SERVER['HTTP_HOST'] . $_SERVER['PHP_SELF'];

    $result = curl_get($url, $header, $proxy);

    // 检查返回结果
    if (empty($result) || strpos($result, "404 Not Found") !== false) {
        header("Location: https://www.youtube.com/watch?v=MV9mI0GChwo");
        exit();
    }

    if (strpos($result, "EXTM3U") !== false) {
        $m3u8s = explode("\n", $result);
        $result = '';
        foreach ($m3u8s as $v) {
            if (strpos($v, ".ts") !== false) {
                $result .= $parseUrl . "?id=" . $name . "&ts=" . $v . "\n";
            } else {
                if ($v != '') {
                    $result .= $v . "\n";
                }
            }
        }
    }
    echo $result;
}
exit();

function curl_get($url, $header = array(), $proxy = "")
{
    $curl = curl_init();
    curl_setopt($curl, CURLOPT_URL, $url);
    curl_setopt($curl, CURLOPT_HEADER, 0);
    curl_setopt($curl, CURLOPT_TIMEOUT, 20);
    curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, false);
    curl_setopt($curl, CURLOPT_HTTPHEADER, $header);

    // 配置代理
    if (!empty($proxy)) {
        curl_setopt($curl, CURLOPT_PROXY, $proxy);
        if (strpos($proxy, 'socks5') === 0) {
            curl_setopt($curl, CURLOPT_PROXYTYPE, CURLPROXY_SOCKS5);
        } else {
            curl_setopt($curl, CURLOPT_PROXYTYPE, CURLPROXY_HTTP);
        }
    }

    curl_setopt($curl, CURLINFO_HEADER_OUT, true);

    $data = curl_exec($curl);

    // 获取HTTP状态码
    $httpCode = curl_getinfo($curl, CURLINFO_HTTP_CODE);

    if ($httpCode == 404) {
        // 如果返回404，则返回空数据
        $data = null;
    }

    if (curl_error($curl)) {
        return "Error: " . curl_error($curl);
    } else {
        curl_close($curl);
        return $data;
    }
}
?>