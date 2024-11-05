<?php
error_reporting(0);
header('Content-Type: text/json;charset=UTF-8');

function real_ip(){
$ip = $_SERVER['REMOTE_ADDR'];
if (isset($_SERVER['HTTP_CLIENT_IP']) && preg_match('/^([0-9]{1,3}\.){3}[0-9]{1,3}$/', $_SERVER['HTTP_CLIENT_IP'])) {
	$ip = $_SERVER['HTTP_CLIENT_IP'];
} elseif(isset($_SERVER['HTTP_X_FORWARDED_FOR']) AND preg_match_all('#\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}#s', $_SERVER['HTTP_X_FORWARDED_FOR'], $matches)) {
	foreach ($matches[0] AS $xip) {
		if (!preg_match('#^(10|172\.16|192\.168)\.#', $xip)) {
			$ip = $xip;
			break;
		}
	}
}
return $ip;
}

$id = $_GET['id'];
if(isset($id) && !empty($id)){
	if(strlen($id)<9){
		header('HTTP/1.0 404 Not Found');
	    exit('Unknown link.');
	}
	$ip=real_ip();
	$headers['CLIENT-IP'] = $ip;  
    $headers['X-FORWARDED-FOR'] = $ip; 
    $headerArr = array();
	 
	foreach( $headers as $n => $v ) {
		$headerArr[] = $n .':' . $v; 
	}
    $time = time()."000";
	$url = "https://app.4gtv.tv/Data/HiNetGetChannelURL.ashx?ChannelNamecallback=channelname&Type=LIVE&Content=".$id."&HostURL=https://www.hinet.net/tv/?channel=021&_=$time";
	$ch = curl_init();  
    $timeout = 5;  
    curl_setopt ($ch, CURLOPT_URL, $url);
	curl_setopt ($ch, CURLOPT_USERAGENT, 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)');
    curl_setopt ($ch, CURLOPT_RETURNTRANSFER, 1);  
    curl_setopt ($ch, CURLOPT_CONNECTTIMEOUT, $timeout);  
    curl_setopt ($ch, CURLOPT_HTTPHEADER , $headerArr );  //构造IP 
	$contents = curl_exec($ch);  
    curl_close($ch);
	
	preg_match_all('|VideoURL":"(.*?)"|i', $contents, $v);
	$token = $v[1][0];
    header('location:'.$token);
	exit;
}else{
	header('403 Forbidden');
	echo 'Unknown link.';
}
?>
