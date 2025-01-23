<?php
//20250116
error_reporting(0);
header("Content-Type:application/json;charset=utf-8");
function f_curl($url,$hdr,$data,$hosts,$ist){
    $ch=curl_init();
    curl_setopt($ch,CURLOPT_URL,$url);
    curl_setopt($ch,CURLOPT_SSL_VERIFYPEER,false);
    curl_setopt($ch,CURLOPT_SSL_VERIFYHOST,false);
    curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
    if($hdr!="") curl_setopt($ch,CURLOPT_HTTPHEADER,$hdr);
    if($data!="") curl_setopt($ch,CURLOPT_POSTFIELDS,$data);
    if($hosts!="") curl_setopt($ch,CURLOPT_RESOLVE,$hosts);
    if($ist==1) curl_setopt($ch,CURLOPT_HEADER,1);
    $cj_tempz=curl_exec($ch);
    if($ist==1) $cj_tempz=curl_getinfo($ch);
    curl_close($ch);
    return $cj_tempz;
}
function f_hurl($id,$pt,$n){
    if($n==3) die("404");
    $n++;
    $hdr=["User-Agent:okhttp/3.12.0"];
    $auth=json_decode(f_curl("http://223.105.251.59:33200/EPG/Ott/jsp/Auth.jsp",$hdr,'{"ContentID":"'.$id.'"}',"",0))->AuthCode;
    if($auth==""){
        die("404");
    }elseif($auth=="accountinfo="){
        f_hurl($id,$pt,$n);
    }else{
        $auth=explode(":",urldecode($auth))[0].",END";
        return $auth;
    }
}
$id=str_replace(".m3u8","",$_GET["id"]);
$pt=$_GET["p"];
if($id=="" || $pt=="") die("404");
$purl=f_hurl($id,$pt,1);
header("location:http://tptvh.mobaibox.com/".$pt."/lookback/".$id."/".$id."?".$purl."&Author=DaBenDan");
die();
?>
