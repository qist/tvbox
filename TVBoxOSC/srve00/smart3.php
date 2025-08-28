<?php
/**
 * Author: Passwd Word
 * Version: 1.0.0
 * Description: 带故障转移功能的 m3u8 代理脚本
 * 交流群  https://t.me/IPTV_9999999
 * 使用方法: https://域名/Smart.php?id=
 */
error_reporting(E_ALL); // 开启所有错误报告，便于调试
header('Content-Type: text/json;charset=UTF-8');
date_default_timezone_set("Asia/Shanghai");

// 继续执行其他逻辑
$name = $_GET["id"] ?? "";

// 定义多个IP地址
$serverIPs = [
    '66.90.99.154',
];

// 从可用服务器中选择一个IP
function selectServer($servers, $name = '') {
    // 使用频道名称作为种子，保持同一频道使用相同服务器
    if (!empty($name)) {
        $index = crc32($name) % count($servers);
        return $servers[$index];
    }
    
    // 如果没有频道名，随机选择一个服务器
    return $servers[array_rand($servers)];
}

// 选择一个服务器IP
$selectedIP = selectServer($serverIPs, $name);
$port = "http://{$selectedIP}:8278/";

$ts = $_GET["ts"] ?? "";

// 下面的逻辑保持不变
$ip = '127.0.0.1';
$header = array(
    "CLIENT-IP:" . $ip,
    "X-FORWARDED-FOR:" . $ip,
);

// 添加故障转移功能
function getWithFailover($url, $header, $servers, $port, $name, $path = '') {
    $attempts = 0;
    $maxAttempts = count($servers);
    $data = null;
    $tried = [];
    
    while ($attempts < $maxAttempts) {
        $data = curl_get($url, $header);
        
        // 检查是否获取成功
        if ($data && !strpos($data, "Error:") && !strpos($data, "404 Not Found")) {
            return $data;
        }
        
        // 记录已尝试的服务器
        $urlParts = parse_url($url);
        $tried[] = $urlParts['host'];
        
        // 尝试下一个服务器
        $attempts++;
        if ($attempts < $maxAttempts) {
            // 排除已尝试的服务器
            $availableServers = array_diff($servers, $tried);
            if (empty($availableServers)) break;
            
            // 选择新服务器
            $newIP = array_values($availableServers)[0];
            $newUrl = "http://{$newIP}:8278/" . $name;
            if (!empty($path)) {
                $newUrl .= "/" . $path;
            }
            $url = $newUrl;
        }
    }
    
    return $data;
}

if ($ts) {
    $host = $port . $name . "/";
    $url = $host . $ts;
    $data = getWithFailover($url, $header, $serverIPs, $port, $name, $ts);
    echo $data;
} else {
    $url = $port . $name . "/playlist.m3u8";
    $seed = "tvata nginx auth module";
    $path = parse_url($url, PHP_URL_PATH);
    //$tid = "mc42afe745533";
    $tid = "mc42afe834703";
    $t = strval(intval(time() / 150));
    $str = $seed . $path . $tid . $t;
    $tsum = md5($str);
    $link = http_build_query(["ct" => $t, "tsum" => $tsum]);
    $url .= "?tid=$tid&$link";

    $parseUrl = $_SERVER['PHP_SELF'];

    $result = getWithFailover($url, $header, $serverIPs, $port, $name);
    
    // 检查返回结果
    if (empty($result) || strpos($result, "404 Not Found") !== false) {
        header("Location: https://simate.pendy.dpdns.org/judy/output.m3u8");
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

function curl_get($url, $header = array())
{
    $curl = curl_init();
    curl_setopt($curl, CURLOPT_URL, $url);
    curl_setopt($curl, CURLOPT_HEADER, 0);
    curl_setopt($curl, CURLOPT_TIMEOUT, 20);
    curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, false);
    curl_setopt($curl, CURLOPT_HTTPHEADER, $header);
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