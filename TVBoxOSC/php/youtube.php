<?php
$id = $_GET["id"] ?? "36YnV9STBqc";
function get_data($url) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    $data = curl_exec($ch);
    curl_close($ch);
    return $data;
}
$string = get_data('http://youtube.com/watch?v=' . $id);
if (preg_match('/"hlsManifestUrl":"(.*?)"/', $string, $matches)) {
    $rawURL = $matches[1];
    header("Content-type: application/vnd.apple.mpegurl");
    echo $rawURL;
}
?>
