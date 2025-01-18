<?php
header('Content-Type: text/plain; charset=utf-8');
header('Content-Type: application/vnd.apple.mpegurl');
$url = $_GET['url'] ?? '';
if (strpos($url, '/litv/') !== false) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    $response = curl_exec($ch);
    curl_close($ch);
    $modified_content = str_replace("litvpc-hichannel.cdn.hinet.net", "ntdfreevcpc-tgc.cdn.hinet.net", $response);
    echo $modified_content;
} elseif (strpos($url, '/4gtv/') !== false) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    $response = curl_exec($ch);
    curl_close($ch);
    echo $response;
} else {
    echo "錯誤或尚未輸入網址";
}
?>
