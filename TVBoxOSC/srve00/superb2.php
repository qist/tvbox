<?php
error_reporting(0);
header('Content-Type: text/json;charset=UTF-8',true,200);

$m3u8 = $_GET["m3u8"];
$ts = $_GET["ts"];
$uid = $_GET["uid"];
$token = $_GET["token"];

if(empty($m3u8) and empty($ts)){
$init = curl("http://cookies.elementfx.com/superb/superb.php",1,"");
$data = curl("http://cookies.elementfx.com/superb/superb.php?list=1",1,"");
$data = gzuncompress(base64_decode($data));
$data = json_decode($data);
$count = count($data);
$pro = $_SERVER['HTTP_X_FORWARDED_PROTO'];
if(empty($pro)){
$pro = json_decode($_SERVER['HTTP_CF_VISITOR'],true)["scheme"];
if(empty($pro)){
$pro = "http";
}}
$self = $pro."://".$_SERVER['HTTP_HOST'].$_SERVER['REQUEST_URI'];
for($i=0;$i<$count;$i++){
if(substr($data[$i]->url,0,1) == "/"){
$result.=str_replace("/","",$data[$i]->category)."_".$data[$i]->name.",".$self."?m3u8=".$data[$i]->url."\n";
}}
print_r($result);
}

if(!empty($m3u8) and empty($ts)){
$host = file_get_contents("./host.txt");
$uid = file_get_contents("./uid.txt");
$token = file_get_contents("./token.txt");
if(time() - filemtime("./token.txt") > 300){
$info = curl("http://cookies.elementfx.com/superb/superb.php",1,"");
$info = json_decode($info);
$host = $info->host;
$uid = $info->uid;
$token = $info->token;
file_put_contents("./host.txt",$host);
file_put_contents("./uid.txt",$uid);
file_put_contents("./token.txt",$token);
}
$url = $host.$m3u8;
$pre = explode("/index",$url)[0];
$header = array("User-Agent: Lavf/58.12.100","Accept: */*","Connection: keep-alive","Icy-MetaData: 1","userid: {$uid}","usertoken: {$token}","Cache-Control: no-cache","Pragma: no-cache");
$data = curl($url,1,$header);
$data = array_filter(explode("\n",$data));
$count = count($data);
$pro = $_SERVER['HTTP_X_FORWARDED_PROTO'];
if(empty($pro)){
$pro = json_decode($_SERVER['HTTP_CF_VISITOR'],true)["scheme"];
if(empty($pro)){
$pro = "http";
}}
$self = $pro."://".$_SERVER['HTTP_HOST'].$_SERVER['SCRIPT_NAME'];
for($i=0;$i<$count;$i++){
if(substr($data[$i],0,1) !== "#"){
$data[$i] = $self."?ts={$pre}/{$data[$i]}&uid={$uid}&token={$token}";
}}
print_r(implode("\n",$data));
}

if(empty($m3u8) and !empty($ts)){
$header = array("User-Agent: Lavf/58.12.100","Accept: */*","Connection: keep-alive","Icy-MetaData: 1","userid: {$uid}","usertoken: {$token}","Cache-Control: no-cache","Pragma: no-cache");
header("Content-Type: video/mp2t");
header('Content-Disposition: attachment; filename=superb.ts');
print_r(curl($ts,0,$header));
}

function curl($url,$type,$header){
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, $type);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, False);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, False);
if(!empty($header)){
curl_setopt($ch, CURLOPT_HTTPHEADER, $header);
}
$result = curl_exec($ch);
curl_close($ch);
return $result;
}
?>