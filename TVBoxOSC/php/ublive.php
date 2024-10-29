<?php
// 代理脚本 ublive.php

// 获取远程服务器上的文件的URL
$url = $_GET['url'];

$burl = explode("index.m3u8",$url)[0];

//$d = file_get_contents($url2);
$d = get_url_content($url);

//$str = preg_replace("/(.*?.ts)/", $burl."$1",$d);
$str = preg_replace("/(.*?.ts)/", "proxy.php?url=".$burl."$1",$d);
header("Content-Type: application/vnd.apple.mpegurl");
header("Content-Disposition: inline; filename=index.m3u8");
echo $str;

//echo $d;
//echo $url2;


function get_url_content($url) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);

    $data = curl_exec($ch);
    if (curl_errno($ch)) {
        echo 'cURL error: ' . curl_error($ch);
        curl_close($ch);
        exit;
    }
    curl_close($ch);
    return $data;
}
?>