
## Current dockers


歐飛+雜(限台),直播點播混合,限台
http://live1.robyang.ggff.net:50001/Sub?type=m3u 

31臺而已
http://live1.robyang.ggff.net:50002/Sub.txt
http://live1.robyang.ggff.net:50002/Sub.m3u
http://live1.robyang.ggff.net:50002/Sub.vod.m3u

四季+雜(限台) 全世界,不要排序~
http://live1.robyang.ggff.net:50003/?type=m3u 

smart php, slow (convert to traditional chinese, sort needed)
http://live1.robyang.ggff.net:50004/smart.m3u?token=RobYang 


dead, no TV 2025-10-18, Judy v0.05
http://live1.robyang.ggff.net:50008/?type=txt
http://live1.robyang.ggff.net:50008/?type=m3u        


dead, no TV!! 2025-10-18 三岁抬頭當王者
http://live1.robyang.ggff.net:50009/?type=m3u         
http://live1.robyang.ggff.net:50009/?type=txt

四季+雜(限台) 
http://live1.robyang.dpdns.org:50010/?type=m3u 







## sound fix: Update a file from a docker host:
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

## Intall Docker to Ubuntu:
1. install docker engine: https://docs.docker.com/engine/install/ubuntu/
2. install Portainer UI: https://youtu.be/_2Llvz_0pB4?si=jHaaW4Aw-ISerwFM 





## 1. liuyong1987 劉墉 刘墉: (taiwan IP only) https://hub.docker.com/u/liuyong1987
    1. sudo docker pull liuyong1987/fourgtv:latest
    3. sudo docker run -d --name=fourgtv -p 50013:8000 --restart=always liuyong1987/fourgtv:latest
    4. 订阅列表：
         - mytvsuper: http://[IP:PORT]/mytvsuper.m3u
         - now: http://[IP:PORT]/now.m3u
         - now-free: http://[IP:PORT]/now-free.m3u
         - 4gtv: http://[IP:PORT]/4gtv.m3u https://live1.RobYang.ggff.net/TxtM3u?url=http://[IP:PORT]/4gtv.m3u 
         - itv: http://[IP:PORT]/itv.m3u
         - beesport: http://[IP:PORT]/beesport.m3u
         - Plex: http://[IP:PORT]/plex.m3u
         - Pluto: http://[IP:PORT]/pluto-us.m3u
         - Thetvapp: http://[IP:PORT]/thetvapp.m3u
         - Tubi: http://[IP:PORT]/tubi-us.m3u (美国线路)
         - http://[IP:PORT]/tubi-ca.m3u (加拿大线路)
一键修复:
curl -sL https://x.tt8.us.kg/update_fourgtv.sh | bash
ds
修复now 获取新的mpd key。 整合多了个 now-self.m3u 等于free列表 详情 https://t.me/livednowgroup/386393
目录更正 https://t.me/livednowgroup/387376
网友的备份1: https://t.me/livednowgroup/387476
备份2: ru2025/fourgtv




## 3. 4GTV pixman （taiwan IP only, ofiii + 4GTV整合版）https://hub.docker.com/r/mybtjson/pixman-4gtv: 
======
vps 服务器 Docker镜像运行:
sudo docker run -d --name=mybtjson009 -p 50010:5000 --dns=8.8.8.8 --dns=1.1.1.1 --restart=always mybtjson/pixman-4gtv:0.0.9


Alice: 154.12.177.22 
(US or UK only) ExpressVPN: 85.203.37.1, 85.203.37.2 (https://www.expressvpn.com/setup#mediastreamer)

sudo docker run -d --name=mybtjson4gtv001 -p 50009:5000 --restart=always mybtjson/vps-4gtv:0.0.1


软路由 Docker镜像运行:
docker run -d --name=pixman-4gtv -p 50007:5000 -e http_proxy="http://172.17.0.1:10082" -e https_proxy="http://172.17.0.1:10082" --restart=always mybtjson/pixman-4gtv:0.0.4

注释:
先去 https://app.alice.ws 注册账号，然后把你的vps的IP添加到他官网提供的dns解锁中， 添加成功之后会给你一个解锁HK和TW的IP，把上面--dns=8.8.8.8中的8.8.8.8替换成他给你提供的IP，然后你就可以愉快的玩耍了！！

##代理ts订阅
http://ip:port/?type=m3u&proxy=true

   http://ip:50007/help
   http://ip:50007/?type=txt
   http://ip:50007/?type=m3u




## 3. ofiii: (taiwan IP only 無民視) https://hub.docker.com/r/doubebly/doube-ofiii/tags
======
台湾vps部署：
docker run -d --name=doube-ofiii -p 50002:5000 --restart=always doubebly/doube-ofiii:1.1.0

软路由部署，下面运行命令中的"http://192.168.50.50:7890"为你软路由设置的台湾节点http代理：
docker run -d --name=doube-ofiii -p 50002:5000 --restart=always -e http_proxy=http://192.168.50.50:7890 -e https_proxy=http://192.168.50.50:7890 doubebly/doube-ofiii:1.1.0

   # 不代理TXT订阅，播放端需要挂台湾梯子：   http://ip:port/Sub?type=txt&sd=1080

   # 代理TXT订阅：   http://ip:port/Sub?type=txt&sd=1080&proxy=true

   # 不代理M3U订阅，播放端需要挂台湾梯子：   http://ip:port/Sub?type=m3u&sd=1080

   # 代理M3U订阅：   http://ip:port/Sub?type=m3u&sd=1080&proxy=true

   # 点播订阅，可同时订阅多个点播，建议三到五个，用英文逗号分割，例如：ofiii75,ofiii74,ofiii73

   http://ip:port/ofiii.m3u?pids=ofiii75,ofiii74,ofiii73&sd=1080&proxy=true
   doubebly.json文件内容如下：
   {
   "Token_enabled": false,
   "Token": ["Double001", "Double001"],
   "User-agent_enabled": false,
   "User-agent": ["PotPlayer/24.12.16", "Mozilla/5.0"]
   }

   txt: http://ip:port/Sub?type=m3u&sd=1080&proxy=true
   m3u: http://ip:port/Sub?type=m3u&sd=1080&proxy=true
   token，订阅地址请加token参数: http://ip:port/Sub?type=m3u&sd=1080&proxy=true&token=Double001



## 4. itv: (china only)
======
Author --by( 沐辰&&Doubebly )
docker镜像拉取: docker pull doubebly/doube-ofiii:1.1.0
docker镜像运行: docker run -d --name=doube-ofiii -p 50001:5000 --restart=always doubebly/doube-itv:1.1.0
Usage:
访问 http://ip:port/help (示例：http://127.0.0.1:50001/help)，可以看到txt和m3u的订阅链接



## 5. itv-plus: (china only)
======
docker镜像拉取: sudo docker pull doubebly/doube-itv-plus:1.0.3
docker镜像运行: docker run -d --name=doube-itv-plus -p 50103:5000 --restart=always doubebly/doube-itv-plus:1.0.3
Usage:
http://ip:port/Sub.m3u
http://ip:port/Sub.txt





## 5. Pixman: https://pixman.io/topics/17
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
   













## Docker Instances / Accounts: 
======
1. (bobyang.03 login) https://robyang-3487.koyeb.app/4gtv.m3u
2. (bobyang03 login) https://robyang-3487.koyeb.app/youtube/ylYJSBUgaMA


## ~~~~謝安琪 4gtv docker 教學:
======
koyeb官方網站
https://www.koyeb.com

左邊 Create Service

右邊 docker

輸入 docker.io/pixman/pixman:latest

端口8000改成5000

4GTV直播源
http://分配的網址/4gtv.m3u

## ~~~謝安琪 4gtv docker 教學
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

https://pixman.io/topics/218



## Pixman Hami的代理小工具
最近弄了一个针对Pixman Hami的代理小工具，有需求的可以自取。
适用：pixman和梯子等已经部署(tw vps), 但家庭网络环境不能访问Hami Video（例如分享给朋友免梯子）或者家庭网络环境虽有梯子但不方便做Hami分流。
- 群主的hami 要求不仅部署pixman docker的服务器网络能访问Hamivideo, 而且客服端(播放器)也必须能访问HamiVideo网络才行 （因为pixman 鉴权后做了HamiVideo重定向）.
- 对于有些客户端环境没有直接访问HamiVideo网络条件的情况下，一个优化方案可以用 hamiproxy docker 代理Pixman的Hami 访问HamiVideo
- hamiproxy docker 可以部署在和Pixman相同或不同的主机上 (该主机要求能访问HamiVideo网络) ,客户端只需访问 Hamiproxy docker 服务进行Hami 播放。
- 本方案适用于家庭网络环境中无法直接访问Hami Video的场景, 当然hamiproxy 也只是代理而已，用户自己确保部署的Pixman docker和Hami的key能工作, 而且多次代理对线路要求比较高，如果线路本来就不稳的慎用.
https://hub.docker.com/r/t2os/hamiproxy

Usage:

- pull the image
> docker pull t2os/hamiproxy:latest
- run & specify the pximan m3u full url: (http://your_pixman_host:5000/hami.m3u)
> docker run -d --name=hamiproxy -p 9000:9000 -e HAMI_M3U=http://your_pixman_host:5000/hami.m3u t2os/hamiproxy
- to get the proxied hami m3u list, and play wherever can access the hamiproxy server
> http://your_hamiproxy_host:9000/hami.m3u

【玩累了】发一下rptv的算法，以后会下掉rptv了
https://iptv.cc/forum.php?mod=viewthread&tid=5264&fromuid=9443
(出处: IPTV论坛)
https://t.me/livednowgroup/379194






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




## DDNS
1. dynv6.com
2. https://www.dynu.com/ (can created subdomain but can only hosted in dynu. they cannot change nameservers. up to 4 free third level domain per account)
   1. *.ooguy.com
   2. *.ddnsfree.com
   3. *.freeddns.org
   4. ...etc
   5. https://api.dynu.com/nic/update?hostname=example.dynu.com&alias=Alias&password=PASSWORD
   6. curl "https://api.dynu.com/nic/update?username=robyang&password=Ilovebob123!&hostname=usa1.robyang.ooguy.com&myip=1.2.3.4&myipv6=2602:1234::3"
   7. wget "https://api.dynu.com/nic/update?hostname=example.dynu.com&myip=198.144.117.32&myipv6=2604:4400:a:8a::f4&username=someusername&password=somepassword"





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

自媒体解锁一键修改DNS脚本 https://gaojilingjuli.blogspot.com/2024/11/alice-dns.html
sudo wget https://raw.githubusercontent.com/Jimmyzxk/DNS-Alice-Unlock/refs/heads/main/dns-unlock.sh && sudo bash dns-unlock.sh

测试IPv4解锁情况: bash <(curl -L -s media.ispvps.com)
in windows, use "wsl"