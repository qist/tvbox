<?php
// 获取请求的 URL 并修正编码
$request_url = isset($_GET['url']) ? urldecode($_GET['url']) : '';
if (empty($request_url)) {
    die('缺少 url 参数');
}

// 允许代理的域名列表
$allowed_domains = [
    'aktv.top',
    'php.jdshipin.com',
    'cdn12.jdshipin.com',
    'v2h.jdshipin.com',
    'v2hcdn.jdshipin.com',
    'cdn.163189.xyz',
    'cdn2.163189.xyz',
    'cdn3.163189.xyz',
    'cdn5.163189.xyz',
    'cdn9.163189.xyz'
];

$parsed_url = parse_url($request_url);
if (!$parsed_url || !isset($parsed_url['host']) || !in_array($parsed_url['host'], $allowed_domains)) {
    die('非法请求的域名');
}

//自定义 getallheaders() 函数，使得代码可以兼容 FastCGI 模式
if (!function_exists('getallheaders')) {
    function getallheaders() {
        $headers = [];
        foreach ($_SERVER as $name => $value) {
            if (substr($name, 0, 5) == 'HTTP_') {
                $headers[str_replace(' ', '-', ucwords(strtolower(str_replace('_', ' ', substr($name, 5)))))] = $value;
            }
        }
        return $headers;
    }
}

// 处理 HTTP 头信息
$headers = [];
foreach (getallheaders() as $name => $value) {
    if (strtolower($name) !== 'host') {
        $headers[] = "$name: $value";
    }
}
$headers[] = "Host: {$parsed_url['host']}";
$headers[] = "User-Agent: AppleCoreMedia/1.0.0.7B367 (iPad; U; CPU OS 4_3_3 like Mac OS X)";
$headers[] = "Referer: https://{$parsed_url['host']}/";
$headers[] = "Accept-Encoding: gzip, deflate";

// 发送请求
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $request_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HEADER, true); // 获取完整响应头
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, false); // 禁用自动跳转
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($ch, CURLOPT_ENCODING, "");

// 禁用 HTTP/2，强制使用 HTTP/1.1
curl_setopt($ch, CURLOPT_HTTP_VERSION, CURL_HTTP_VERSION_1_1);

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, file_get_contents('php://input'));
}

$response = curl_exec($ch);
$curl_error = curl_error($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
curl_close($ch);

// 分离响应头和响应体
$headers = substr($response, 0, $header_size);
$body = substr($response, $header_size);

// 解析响应头
$response_headers = [];
foreach (explode("\r\n", $headers) as $line) {
    if (strpos($line, 'HTTP/') === 0) {
        $response_headers[] = $line;
        continue;
    }
    $parts = explode(': ', $line, 2);
    if (count($parts) === 2) {
        $name = strtolower($parts[0]);
        $response_headers[$name] = $parts[1];
    }
}

// 处理重定向
if (in_array($http_code, [301, 302, 303, 307, 308]) && isset($response_headers['location'])) {
    $location = $response_headers['location'];
    
    // 处理相对路径
    if (!parse_url($location, PHP_URL_SCHEME)) {
        $base = $parsed_url['scheme'] . '://' . $parsed_url['host'];
        if (isset($parsed_url['port'])) {
            $base .= ':' . $parsed_url['port'];
        }
        $location = $base . '/' . ltrim($location, '/');
    }
    
    // 生成代理地址并跳转
    header("Location: mytv.php?url=" . urlencode($location), true, $http_code);
    exit();
}

// 保留原始 Content-Type
if (isset($response_headers['content-type'])) {
    header('Content-Type: ' . $response_headers['content-type']);
}

// 设置 HTTP 响应状态码
http_response_code($http_code);

if ($response === false) {
    die("CURL ERROR: " . $curl_error);
}

// 处理 m3u8 文件
if (strpos($request_url, '.m3u8') !== false || (isset($response_headers['content-type']) && strpos($response_headers['content-type'], 'application/vnd.apple.mpegurl') !== false)) {
    $base_url = dirname($request_url) . '/';
    $allowed_domains_regex = implode('|', array_map(function($domain) {
        return preg_quote($domain, '/');
    }, $allowed_domains));
    
    $body = preg_replace_callback(
        '/(https?:\/\/(?:' . $allowed_domains_regex . ')\/[^\s"\']+\.ts)|([^\s"\']+\.ts)/',
        function ($matches) use ($base_url) {
            if (!empty($matches[1])) {
                return 'mytv.php?url=' . urlencode($matches[1]);
            } elseif (!empty($matches[2])) {
                $ts_url = $base_url . ltrim($matches[2], '/');
                return 'mytv.php?url=' . urlencode($ts_url);
            }
            return $matches[0];
        },
        $body
    );
    header('Content-Disposition: inline; filename=index.m3u8');
}

echo $body;
?>