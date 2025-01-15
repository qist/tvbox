## Update a file from a docker host:
======
```
#!/bin/bash

# 下载 litv.yaml 文件并复制到指定的 Docker 目录
curl -o /tmp/litv.yaml https://x.tt8.us.kg/litv.yaml

# 将文件复制到 Docker 容器内部的指定路径
docker cp /tmp/litv.yaml pixman:/app/app/channel_list/litv.yaml

# 删除临时文件
rm /tmp/litv.yaml

# 重启 Docker 容器
docker restart pixman

# 输出成功信息
echo "litv.yaml 更新成功，Docker 容器已重启。"
```


## Pixman: https://pixman.io/topics/17
    1. How to modify file:
       1. Go to "Console" (instance, console) https://app.koyeb.com/services/aa524a02-5577-4377-9ecc-7223a9ad3a6f/console
       2. use "vi titv.yaml"
       3. modify
       4. "esc" on keyboard, then :wq   to save
    2. (after restart/redeloy, saved files are gone!) How to download a file to the instant
       1. Go to "Console" (instance, console) https://app.koyeb.com/services/aa524a02-5577-4377-9ecc-7223a9ad3a6f/console
       2. /app/app/channel_list # cd /app/app/channel_list
       3. Rename the file: mv litv.yaml litv.yaml2 
       4. Download a file: wget https://raw.githubusercontent.com/bobyang3/tvbox/refs/heads/own/TVBoxOSC/pixman/litv.yaml
       4. Rename the file: mv fourgtv.yaml fourgtv.yaml2 
       5. Download a file: wget https://raw.githubusercontent.com/bobyang3/tvbox/refs/heads/own/TVBoxOSC/pixman/fourgtv.yaml  (download but save with a different name: wget -o 4gtv.yaml https://raw.githubusercontent.com/bobyang3/tvbox/refs/heads/own/TVBoxOSC/pixman/fourgtv.yaml)
       6. read file: vi fourgtv.yaml
       7. close file: "esc" on keyboard, then 
          1. :wq to save
          2. :q! to not save 
       8. Restart the instance: "Settings" ,"Pause", wait for 2 mins, then "Resume"
   

## Instances / Accounts: 
======
1. (bobyang.03 login) https://robyang-3487.koyeb.app/4gtv.m3u
2. (bobyang03 login) https://robyang-3487.koyeb.app/youtube/ylYJSBUgaMA


## 謝安琪 4gtv docker 教學:
======
koyeb官方網站
https://www.koyeb.com

左邊 Create Service

右邊 docker

輸入 docker.io/pixman/pixman:latest

端口8000改成5000

4GTV直播源
http://分配的網址/4gtv.m3u

## 謝安琪 4gtv docker 教學
https://pixman.io/topics/17





## Pixman 项目 傻瓜式 自动化搭建

bash <(curl -sL https://www.567858.xyz/pixman.sh)

如果🔝软路由不支持使用👇命令
bash -c "$(curl -sL https://www.567858.xyz/pixman.sh)"

主要更新内容：
1.系统识别：根据操作系统类型（Ubuntu、Debian、CentOS）和架构（arm32、arm64、x86）选择相应的 Docker 安装方法。

2.环境变量支持：支持在运行 Docker 容器时传入多个环境变量，如 MYTVSUPER_TOKEN、HAMI_SESSION_ID、HAMI_SERIAL_NO、HAMI_SESSION_IP、HTTP_PROXY 和 HTTPS_PROXY。

3.自动更新功能：增加了自动检查 Docker 镜像更新的功能，并在发现新
版本时进行更新

4.增加了docker墙内使用(代理)

5.优化代码逻辑，修复定时任务BUG。增加快捷指令，自动更新脚本功能。（ 默认直接安装，默认端口52055，需要修改端口、token等参数请再 选择2 进行调整 ）




## 支持的直播源 https://pixman.io/topics/17
■四季線上 4GTV (http://ip:port/4gtv.m3u)
■江苏移动魔百盒 TPTV (http://ip:port/tptv.m3u 或 http://ip:port/tptv_proxy.m3u)
■央视频直播源 (http://ip:port/ysp.m3u)
■YouTube 直播源 (http://ip:port/youtube/{VIDEO_ID})
■MytvSuper 直播源 (http://ip:port/mytvsuper.m3u)
■Beesport 直播源 (http://ip:port/beesport.m3u)
■中国移动 iTV 平台 (http://ip:port/itv.m3u 或 http://ip:port/itv_proxy.m3u)
■TheTV (http://ip:port/thetv.m3u)
■Hami Video (http://ip:port/hami.m3u)
■DLHD (http://ip:port/dlhd.m3u)



🛠️工具 https://github.com/fanmingming/live/tree/main/tv
📆EPG接口地址：
https://live.fanmingming.com/e.xml
🏞️Bing每日图片：
https://fanmingming.com/bing
🎞️m3u8在线下载：
https://live.fanmingming.com/m3u8
🆕TXT转M3U格式：
https://live.fanmingming.com/txt2m3u
📄在线M3U转TXT：
Demo🔗 https://fanmingming.com/txt?url=https://live.fanmingming.com/tv/m3u/ipv6.m3u
🌐M3U8 Web Player:
Demo🔗 https://live.fanmingming.com/player/?vurl=https://0472.org/hls/cgtn.m3u8




api/pixman



謝安琪4gtv直播源
m3u格式
https://kaytse2024.koyeb.app/4gtv.m3u

謝安琪4gtv直播源
txt格式
https://fanmingming.com/txt?url=https://kaytse2024.koyeb.app/4gtv.m3u

===========
謝安琪itv直播源
m3u格式
https://kaytse2024.koyeb.app/itv_proxy.m3u

謝安琪itv直播源
txt格式
https://fanmingming.com/txt?url=https://kaytse2024.koyeb.app/itv_proxy.m3u

===========
謝安琪35455直播源
m3u格式
https://35455.koyeb.app/tv.m3u

謝安琪35455直播源
txt格式
https://fanmingming.com/txt?url=https://35455.koyeb.app/tv.m3u