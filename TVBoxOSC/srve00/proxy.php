<?php
// 代理脚本 proxy.php

// 获取远程服务器上的文件的URL
$url = $_GET['url'];

// 执行GET请求
$response = file_get_contents($url);

// 输出响应
echo $response;
?>