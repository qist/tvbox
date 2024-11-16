<?php
class Cache {
    private $cachePath;

    public function __construct($expireTime) {
        $this->cachePath = sys_get_temp_dir() . '/cache/';
        $this->expireTime = $expireTime;

        if (!is_dir($this->cachePath)) {
            mkdir($this->cachePath, 0777, true);
        }
    }

    public function get($key) {
        $file = $this->getCacheFile($key);

        if (!file_exists($file) || (time() - filemtime($file)) > $this->expireTime) {
            return false;
        }

        return file_get_contents($file);
    }

    public function put($key, $data) {
        $file = $this->getCacheFile($key);
        file_put_contents($file, $data);
    }

    private function getCacheFile($key) {
        return $this->cachePath . md5($key);
    }
}
?>
