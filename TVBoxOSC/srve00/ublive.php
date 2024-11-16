<?php
header("Content-type: application/json; charset=utf-8");
include_once("cache.php");
error_reporting(0);
$cache = new Cache(17200);
$filename = pathinfo(__FILE__, PATHINFO_FILENAME);


$site = "https://www.twtvcdn.com/ul02";
#$site = "https://www.usplaytv.com"; uplive2.0
$indexMap = array("0" => 10, "1" => 11, "2" => 12, "3" => 13, "4" => 14, "5" => 15, "6" => 16, "7" => 17, "8" => 18, "9" => 19, "a" => 10, "b" => 11, "c" => 12, "d" => 13, "e" => 14, "f" => 15, "g" => 16, "h" => 17, "i" => 18, "j" => 19, "k" => 20, "l" => 21, "m" => 22, "n" => 23, "o" => 24, "p" => 25, "q" => 26, "r" => 27, "s" => 28, "t" => 29, "u" => 30, "v" => 31, "w" => 32, "x" => 33, "y" => 34, "z" => 35, "A" => 36, "B" => 37, "C" => 38, "D" => 39, "E" => 40, "F" => 41, "G" => 42, "H" => 43, "I" => 44, "J" => 45, "K" => 46, "L" => 47, "M" => 48, "N" => 49, "O" => 50, "P" => 51, "Q" => 52, "R" => 53, "S" => 54, "T" => 55, "U" => 56, "V" => 57, "W" => 58, "X" => 59, "Y" => 60, "Z" => 61, "+" => 62, "/" => 63);

$id = $_GET['id'] ?? "";

$mac = "0027496cc341";

if ($id) {

    $token = $cache->get($filename);
    if (!$token) $token = getToken();

    //https://ht.vipub1818.com/?app=ubl&sn=0831ea8ebc8cd8b8feb9eeecf5379985&re=0&t=1705418753358
    $url = "https://ht.vipub1818.com/?app=ubl&sn=" . md5(strtoupper($mac) . "<HT@2021>") . "&re=0&t=" . time();
    $data = curl_get($url, aesEncrypt(getheader($token)));

    $data = curl_post($site . "/uri.php", aesEncrypt(getId($id)), aesEncrypt(getheader($token)));

    $data = json_decode($data);
    
    $sign = $data->sign;
    $iv = $data->iv;
    $ok = aesDecrypt($sign, $iv);
    
    $playUrl = json_decode($ok)->return_uri;

    $playUrl = preg_replace('/z\d+\./', "z88.", $playUrl);
    //file_put_contents('upid.txt',$playUrl."\n",FILE_APPEND);
    header("location: " . $playUrl);
    print_r($playUrl);

} else {
    $result = $cache->get($filename . "_list");
    if (!$result) {
        $data = curl_get($site . "/live.php?g=1", aesEncrypt(getheader("99185d988d8bd9d6acebc0af79d705c0")));
    #    echo $data . PHP_EOL;
        $data = json_decode($data);
        $sign = $data->sign;
        $iv = $data->iv;
        $ok = aesDecrypt($sign, $iv);
        file_put_contents("anbo.json", $ok);
        $jok = json_decode($ok, true)['return_code'];
        if ($jok == 94) {
            echo "blocked";
            exit();
        }
        $parseUrl = isset($_SERVER['HTTPS']) ? 'https://' : 'http://';
        $parseUrl .= $_SERVER['HTTP_HOST'];
        $parseUrl .= $_SERVER['SCRIPT_NAME'];

        $json = json_decode($ok, true)['return_live'];
        $result = "";
        foreach ($json as $key) {
            $result = $result . $key['name'] . ",#genre#" . PHP_EOL;
            $channel = $key['channel'];
            foreach ($channel as $c) {
                $result = $result . $c['title'] . "," . $parseUrl . "?id=" . $c['id'] . PHP_EOL;
            }
        }
        $cache->put($filename . "_list", $result);
    }
    echo $result;
    
}
exit();


function getToken()
{
    global $site, $cache, $filename;
    $data = curl_get($site . "/info.php?g=1", aesEncrypt(getheader("99185d988d8bd9d6acebc0af79d705c0")));
    $data = json_decode($data);
    $sign = $data->sign;
    $iv = $data->iv;
    $ok = aesDecrypt($sign, $iv);
    #   echo $ok;
    $jok = json_decode($ok, true)['return_code'];
    if ($jok == 94) {
        echo "blocked";
        exit();
    }
    $token = json_decode($ok)->return_token;
    if ($token) $cache->put($filename, $token);
    return $token;
}

function getId($str)
{
    $postId = array(
        "id" => $str,
        "re" => 0
    );
    return json_encode($postId, true);
}


function getheader($token)
{
    global $mac;
    $brand = "alps";
    $model = "S900_Pro";
    $headerDevice = array(
        "app_laguage" => 2,
        "brand" => $brand,
        "chip_id" => "",
        "chip_id2" => "b6afab3d0fdf18096ce822cf39abed1b",
        "cpu_api" => "armeabi-v7a",
        "cpu_api2" => "armeabi",
        "device_flag" => "0",
        "device_v_date" => "327",
        "mac" => $mac,
        "model" => $model,
        "model2" => "",
        "serial" => getSerialMD5($brand, $mac, $model),
        "sun_xi_info" => "[null]",
        "time" => time(),
        "token" => $token,
        "ubcode" => "00000000"
    );
    return json_encode($headerDevice, true);
}

function getSerialMD5($brand, $mac, $model)
{
    $md5Hash = md5(md5($brand . md5($mac) . $model . md5("Gooooogle") . "201306@202106>") . "Ub");
    return $md5Hash;
}

function aesDecrypt($str, $str2)
{
    global $indexMap;
    $substringIndex = intval($indexMap[substr($str, strlen($str) - 6, 1)]);
    $subDecrypt1 = subDecryptStr(5, subDecryptStr(12, substr($str, $substringIndex), $str2), $str2);
    $key = "W@ms7+2HZ34<iZz>";
    $result = openssl_decrypt(base64_decode($subDecrypt1), "AES-128-CBC", $key, OPENSSL_RAW_DATA, $str2);
    return $result;
}

function subDecryptStr($i, $str, $str2)
{
    try {
        $i2 = intval(substr($str2, $i, 1));
    } catch (Exception $e) {
        $i2 = 0;
    }
    if ($i2 == 0) {
        $i2 = 10;
    }
    $substring = substr($str, 0, $i2);
    $substring2 = substr($str, $i2 * 2);
    return $substring . $substring2;
}

function aesEncrypt($str)
{
    global $indexMap;
    $key = "W@ms7+2HZ34<iZz>";
    $iv = randomString(16);
    $encryptData = base64_encode(openssl_encrypt($str, "AES-128-CBC", $key, OPENSSL_RAW_DATA, $iv));
    //  echo $encryptData;
    $aesEncryptToResultBean = array();
    $subEncryptStr1 = subEncryptStr(12, subEncryptStr(5, $encryptData, $iv), $iv);

    $substringIndex = intval($indexMap[substr($subEncryptStr1, strlen($subEncryptStr1) - 6, 1)]);
    $randomString = randomString($substringIndex);

    $result = $randomString . $subEncryptStr1;
    $aesEncryptToResultBean["sign"] = $result;
    $aesEncryptToResultBean["iv"] = $iv;
    ksort($aesEncryptToResultBean);
    return json_encode($aesEncryptToResultBean);
}

function subEncryptStr($i, $str, $str2)
{
    try {
        $i2 = intval(substr($str2, $i, 1));
    } catch (Exception $e) {
        $i2 = 0;
    }
    if ($i2 == 0) {
        $i2 = 10;
    }
    $randomString = randomString($i2);
    $result = substr($str, 0, $i2) . $randomString . substr($str, $i2);

    return $result;
}

function randomString($length): string
{
    $characters = '0123456789abcdefghijklmnopqrstuvwxyz';
    $charactersLength = strlen($characters);
    $randomString = '';
    for ($i = 0; $i < $length; $i++) {
        $randomString .= $characters[rand(0, $charactersLength - 1)];
    }
    return $randomString;
}

function curl_post($url, $postdata, $json)
{
    $header = array(
        'User-Agent: okhttp/3.12.0',
        'device_info: ' . $json,
        'Content-Type: application/json; charset=utf-8'
    );
    $curl = curl_init();
    curl_setopt($curl, CURLOPT_URL, $url);
    curl_setopt($curl, CURLOPT_HEADER, 0);
    curl_setopt($curl, CURLOPT_TIMEOUT, 20);
    curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, false);
    curl_setopt($curl, CURLOPT_HTTPHEADER, $header);
    curl_setopt($curl, CURLOPT_POST, 1);
    curl_setopt($curl, CURLOPT_POSTFIELDS, $postdata);
    $data = curl_exec($curl);
    if (curl_error($curl)) {
        return "Error: " . curl_error($curl);
    } else {
        curl_close($curl);
        return $data;
    }
}

function curl_get($url, $json)
{
    $header = array(
        'User-Agent: okhttp/3.12.0',
        'device_info: ' . $json
    );
    $curl = curl_init();
    curl_setopt($curl, CURLOPT_URL, $url);
    curl_setopt($curl, CURLOPT_HEADER, 0);
    curl_setopt($curl, CURLOPT_TIMEOUT, 20);
    curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, false);
    curl_setopt($curl, CURLOPT_HTTPHEADER, $header);
    $data = curl_exec($curl);
    if (curl_error($curl)) {
        return "Error: " . curl_error($curl);
    } else {
        curl_close($curl);
        return $data;
    }
}