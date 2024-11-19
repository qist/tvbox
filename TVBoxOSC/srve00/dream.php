<?php
error_reporting(0);
header('Content-Type: text/json;charset=UTF-8',true,200);

$m3u8 = $_GET["m3u8"];
$ts = $_GET["ts"];

$devid = "00:fa:20:22:29:4be8:50:8b:8a:3b:1f";//失效更换这里
//备用    00:08:04:00:11:36f2:25:b7:a5:1b:86  "00:fa:20:22:29:4be8:50:8b:8a:3b:1f";

$hardware = "Dream TV-Amlogic-8.1.73GB-11.50 GB-nw";
$version = "DreamTV 20220516";
$salt = 'MZkF@270mp#cOKD0%8Y8dV&5AmH&BTzq';
$from = "2011";

if(empty($m3u8) and empty($ts)){
$time = time();
$list = file_get_contents("./list.txt");
if($time - filemtime("./list.txt") > 604800){
$url = "http://api.2011.boxtv.win/api/wbtj5hmx";
$method = "1-1-2";
$sign = md5($from.$salt.$time.$method.$devid);
$body = '{"method":"'.$method.'","params":{"device_id":"'.$devid.'","hardware":"'.$hardware.'","sn":"'.$devid.'","version":"'.$version.'"},"system":{"from":"'.$from.'","sign":"'.$sign.'","time":"'.$time.'","version":"V1"}}';
$header = array(
"Content-Type: application/json; charset=utf-8",
"Content-Length: ".strlen($body),
"Connection: Keep-Alive",
"User-Agent: okhttp/3.12.5",
);
$data = json_decode(curl($url,1,$header,$body,15))->data;
if(empty($data->client->token)){
print_r("你的ip或devid被Dream封锁,请更换");
exit;
}
$token = $data->client->token;
$id = $data->client->client_id;
$password = $data->client->password;
$time = $data->client->time;
$server = $data->server->hosts[0]->url;
file_put_contents("./id.txt",$id);
file_put_contents("./server.txt",$server);
$method = "1-1-3";
$sign = md5($from.$salt.$time.$method.$devid);
$body = '{"method":"'.$method.'","params":{"client_id":"'.$id.'","device_id":"'.$devid.'","hardware":"'.$hardware.'","password":"'.$password.'","sn":"'.$devid.'","token":"'.$token.'","version":"'.$version.'"},"system":{"from":"'.$from.'","sign":"'.$sign.'","time":"'.$time.'","version":"V1"}}';
$header = array(
"Content-Type: application/json; charset=utf-8",
"Content-Length: ".strlen($body),
"Connection: Keep-Alive",
"User-Agent: okhttp/3.12.5",
);
$data = json_decode(curl($url,1,$header,$body,15))->data;
$token = $data->client->token;
$method = "1-1-4";
$sign = md5($from.$salt.$time.$method.$devid);
$body = '{"method":"'.$method.'","params":{"client_id":"'.$id.'","device_id":"'.$devid.'","hardware":"'.$hardware.'","password":"'.$password.'","sn":"'.$devid.'","token":"'.$token.'","version":"'.$version.'"},"system":{"from":"'.$from.'","sign":"'.$sign.'","time":"'.$time.'","version":"V1"}}';
$header = array(
"Content-Type: application/json; charset=utf-8",
"Content-Length: ".strlen($body),
"Connection: Keep-Alive",
"User-Agent: okhttp/3.12.5",
);
$pro = $_SERVER['HTTP_X_FORWARDED_PROTO'];
if(empty($pro)){
$pro = json_decode($_SERVER['HTTP_CF_VISITOR'],true)["scheme"];
if(empty($pro)){
$pro = "http";
}}
$self = $pro."://".$_SERVER['HTTP_HOST'].$_SERVER['REQUEST_URI'];
$data = json_decode(curl($url,1,$header,$body,15))->data;
$count = count($data);
for($i=0;$i<$count;$i++){
if(substr($data[$i]->url,0,4) !== "http"){
$list.=$data[$i]->name."(".$data[$i]->category."),".$self."?m3u8=".base64_encode($server.$data[$i]->url)."\n";
}}
file_put_contents("./list.txt",$list);
}
print_r($list);
exit;
}

if(!empty($m3u8) and empty($ts)){
$host = file_get_contents("./server.txt");
$id = file_get_contents("./id.txt");
if(time() - filemtime("./id.txt") > 604800){
$pro = $_SERVER['HTTP_X_FORWARDED_PROTO'];
if(empty($pro)){
$pro = json_decode($_SERVER['HTTP_CF_VISITOR'],true)["scheme"];
if(empty($pro)){
$pro = "http";
}}
$self = $pro."://".$_SERVER['HTTP_HOST'].$_SERVER['SCRIPT_NAME'];
header("Location: {$self}",true,302);
exit;
}
$token = file_get_contents("./token.txt");
if(!empty($token)){
$token_exp = intval(explode("-",$token)[1]);
}
if($token_exp - time() < 60 or empty($token)){
$url = "http://api.2011.boxtv.win/api/wbtj5hmx";
$method = "1-1-2";
$sign = md5($from.$salt.$time.$method.$devid);
$body = '{"method":"'.$method.'","params":{"device_id":"'.$devid.'","hardware":"'.$hardware.'","sn":"'.$devid.'","version":"'.$version.'"},"system":{"from":"'.$from.'","sign":"'.$sign.'","time":"'.$time.'","version":"V1"}}';
$header = array(
"Content-Type: application/json; charset=utf-8",
"Content-Length: ".strlen($body),
"Connection: Keep-Alive",
"User-Agent: okhttp/3.12.5",
);
$data = json_decode(curl($url,1,$header,$body,15))->data;
if(empty($data->client->token)){
print_r("你的ip或devid被Dream封锁,请更换");
exit;
}
$token = $data->client->token;
$id = $data->client->client_id;
$password = $data->client->password;
$time = $data->client->time;
$method = "1-1-3";
$sign = md5($from.$salt.$time.$method.$devid);
$body = '{"method":"'.$method.'","params":{"client_id":"'.$id.'","device_id":"'.$devid.'","hardware":"'.$hardware.'","password":"'.$password.'","sn":"'.$devid.'","token":"'.$token.'","version":"'.$version.'"},"system":{"from":"'.$from.'","sign":"'.$sign.'","time":"'.$time.'","version":"V1"}}';
$header = array(
"Content-Type: application/json; charset=utf-8",
"Content-Length: ".strlen($body),
"Connection: Keep-Alive",
"User-Agent: okhttp/3.12.5",
);
$data = json_decode(curl($url,1,$header,$body,15))->data;
$token = $data->client->token;
file_put_contents("./token.txt",$token);
}
$m3u8 = base64_decode($m3u8);
$pre = explode("index",$m3u8)[0];
$header = array("User-Agent: Lavf/58.12.100","Accept: */*","Connection: keep-alive","Icy-MetaData: 1","userid: {$id}","usertoken: {$token}","Cache-Control: no-cache","Pragma: no-cache");
$data = curl($m3u8,1,$header,"",15);
$pro = $_SERVER['HTTP_X_FORWARDED_PROTO'];
if(empty($pro)){
$pro = json_decode($_SERVER['HTTP_CF_VISITOR'],true)["scheme"];
if(empty($pro)){
$pro = "http";
}}
$self = $pro."://".$_SERVER['HTTP_HOST'].$_SERVER['SCRIPT_NAME'];
$data = array_filter(explode("\n",$data));
$count = count($data);
for($i=0;$i<$count;$i++){
if(substr($data[$i],0,1) !== "#"){
$data[$i] = "{$self}?ts={$pre}{$data[$i]}";
}}
print_r(implode("\n",$data));
exit;
}

if(!empty($ts) and empty($m3u8)){
header("Content-Type: video/mp2t");
header('Content-Disposition: attachment; filename=dream.ts');
$id = file_get_contents("./id.txt");
$token = file_get_contents("./token.txt");
$header = array("User-Agent: Lavf/58.12.100","Accept: */*","Connection: keep-alive","Icy-MetaData: 1","userid: {$id}","usertoken: {$token}","Cache-Control: no-cache","Pragma: no-cache");
print_r(curl($ts,0,$header,"",""));
exit;
}

function curl($url,$type,$header,$body,$timeout){
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, $type);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, False);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, False);
if(!empty($body)){
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_POSTFIELDS, $body);
}
curl_setopt($ch, CURLOPT_HTTPHEADER, $header);
if(!empty($timeout)){
curl_setopt($ch, CURLOPT_TIMEOUT,$timeout);
}
$result = curl_exec($ch);
curl_close($ch);
return $result;
}
?>