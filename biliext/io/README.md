## 当前仓库配置地址
```bash
https://ghp.ci/https://raw.githubusercontent.com/fish2018/ol/main/all.json
https://raw.yzuu.cf/fish2018/ol/main/all.json
https://fastly.jsdelivr.net/gh/fish2018/ol/all.json
```

## [tvbox_tools](https://hub.docker.com/r/2011820123/tvbox)
写这个工具的主要原因是网上各种接口重复率和失效率极高。几个多仓接口能有成千上万个线路，实际上不重复、可用的线路只有那么几十个，实在是过于冗余了。所以做了这个整理工具，把接口中所有线路进行去重和格式化，json下载保存为同名txt文件，jar文件保存到jar目录下，最后输出个all.json(包含所有历史下载线路接口)和{target}.json(本次下载线路接口，默认tvbox.json)文件用于配置app，看起来比较简洁，方便修改维护。

## 功能概述
- 支持多仓、单仓、线路接口的私有化(json和对应的jar文件下载到本地，经过格式化后推送到自己的git仓库)
- 支持js动态渲染数据的接口
- 移除失效线路
- 移除名称中的emoj表情
- 根据hash和文件大小去重线路
- 为文件链接自动使用加速（支持多种加速）

## 使用方法：

#### 参数选项 
docker run时使用-e选项通过环境变量传参

- [ * ] username or u 指定用户名
- [ * ] token [github.com中设置token](https://github.com/settings/tokens)
- [ * ] url 指定要下载的源，多个url使用英文逗号分隔，`?&signame=`指定单线路名
- repo 指定你的代码仓库名，默认tvbox
- target 指定你想保存的json文件名，默认tvbox.json
- num 多仓时可以指定下载前num个仓库源
- timeout http请求超时，默认3s
- signame url是单个线路时可以指定线路名(jar同名)，不指定随机生成
- jar_suffix 指定spider字段jar包保存后缀名，默认`jar`，一些CDN禁止'jar'后缀，可以修改为`txt`、`json`、`js`、`css`、`html`
- mirror 指定镜像cdn加速，默认mirror=1
  - gh1类型 https://raw.githubusercontent.com/fish2018/tvbox/master/all.json => https://xxxx/gh/fish2018/tvbox/all.json
    - mirror=1 https://ghp.ci/https://raw.githubusercontent.com
    - mirror=2 https://gitdl.cn/https://raw.githubusercontent.com
    - mirror=3 https://ghproxy.net/https://raw.githubusercontent.com
    - mirror=4 https://github.moeyy.xyz/https://raw.githubusercontent.com
    - mirror=5 https://gh-proxy.com/https://raw.githubusercontent.com
    - mirror=6 https://ghproxy.cc/https://raw.githubusercontent.com
    - mirror=7 https://raw.yzuu.cf 可加速clone、push速度非常快(限制低于50M)
    - mirror=8 https://raw.nuaa.cf
    - mirror=9 https://raw.kkgithub.com
    - mirror=10 https://gh.con.sh/https://raw.githubusercontent.com
    - mirror=11 https://gh.llkk.cc/https://raw.githubusercontent.com
    - mirror=12 https://gh.ddlc.top/https://raw.githubusercontent.com
    - mirror=13 https://gh-proxy.llyke.com/https://raw.githubusercontent.com
  - gh2类型(缓存不能及时更新，禁止缓存jar后缀，建议txt、json、js、css、html) https://raw.githubusercontent.com/fish2018/tvbox/master/all.json => https://xxxx/fish2018/tvbox/master/all.json
    - mirror=21 https://fastly.jsdelivr.net
    - mirror=22 https://jsd.onmicrosoft.cn
    - mirror=23 https://gcore.jsdelivr.net
    - mirror=24 https://cdn.jsdmirror.com
    - mirror=25 https://cdn.jsdmirror.cn
    - mirror=26 https://jsd.proxy.aks.moe
    - mirror=27 https://jsdelivr.b-cdn.net
    - mirror=28 https://jsdelivr.pai233.top

#### Docker执行示例:
Docker镜像`2011820123/tvbox`，也可以使用代理拉取镜像`dockerproxy.com/2011820123/tvbox:latest`<br>
首先在github.com上创建自己的代码仓库，推荐命名'tvbox'，其他仓库名需要指定参数repo<br>
支持多url下载，英文逗号`,`分隔多个url，`?&signame={name}`指定单线路名，不指定会生成随机名，{target}.json以最后一个url为准。<br>

```bash
docker run --rm  -e username=xxx -e token=xxx -e url='http://肥猫.com?&signame=肥猫,http://www.饭太硬.com/tv/?&signame=饭太硬' 2011820123/tvbox
```

演示：

```
docker run --rm -e repo=ol -e mirror=2 -e jar_suffix=css -e token=XXX -e username=fish2018 -e num=1 -e url='https://www.iyouhun.com/tv/0'  2011820123/tvbox

>>>

开始克隆：git clone https://githubfast.com/fish2018/ol.git
--------- 开始私有化在线接口 ----------
当前url: https://www.iyouhun.com/tv/0
【多仓】 🌹游魂主仓库🌹.json: https://xn--s6wu47g.u.nxog.top/nxog/ou1.php?b=游魂
开始下载【线路】游魂家庭1: https://xn--s6wu47g.u.nxog.top/m/111.php?ou=公众号欧歌app&mz=index&jar=index&123&b=游魂
开始下载【线路】游魂云盘2: https://xn--s6wu47g.u.nxog.top/m/111.php?ou=公众号欧歌app&mz=all&jar=all&b=游魂
开始下载【线路】游魂学习3: https://xn--s6wu47g.u.nxog.top/m/111.php?ou=公众号欧歌app&mz=a3&jar=a3&b=游魂
开始下载【线路】下面游魂收集网络: https://xn--s6wu47g.u.nxog.top/m/111.php?ou=公众号欧歌app&mz=index&jar=index&321&b=游魂
开始下载【线路】饭太硬: http://py.nxog.top/?ou=http://www.饭太硬.com/tv/
开始下载【线路】OK: http://py.nxog.top/?ou=http://ok321.top/ok
开始下载【线路】盒子迷: http://py.nxog.top/?ou=https://盒子迷.top/禁止贩卖
开始下载【线路】D佬: https://download.kstore.space/download/2883/nzk/nzk0722.json
开始下载【线路】PG: https://gh.con.sh/https://raw.githubusercontent.com/ouhaibo1980/tvbox/master/pg/jsm.json
开始下载【线路】肥猫: http://py.nxog.top/?ou=http://肥猫.com
开始下载【线路】小米: http://py.nxog.top/?ou=http://www.mpanso.com/%E5%B0%8F%E7%B1%B3/DEMO.json
开始下载【线路】放牛: http://py.nxog.top/?ou=http://tvbox.xn--4kq62z5rby2qupq9ub.top
开始下载【线路】小马: https://szyyds.cn/tv/x.json
开始下载【线路】天天开心: http://ttkx.live:55/天天开心
开始下载【线路】摸鱼: http://我不是.摸鱼儿.top
开始下载【线路】老刘备: https://raw.liucn.cc/box/m.json
开始下载【线路】香雅情: https://gh.con.sh/https://raw.githubusercontent.com/xyq254245/xyqonlinerule/main/XYQTVBox.json
开始下载【线路】俊佬: http://home.jundie.top:81/top98.json
开始下载【线路】月光: https://gh.con.sh/https://raw.githubusercontent.com/guot55/yg/main/max.json
开始下载【线路】巧技: http://cdn.qiaoji8.com/tvbox.json
开始下载【线路】荷城茶秀: https://gh.con.sh/https://raw.githubusercontent.com/HeChengChaXiu/tvbox/main/hccx.json
开始下载【线路】云星日记: http://itvbox.cc/云星日记
开始下载【线路】吾爱: http://52pan.top:81/api/v3/file/get/174964/%E5%90%BE%E7%88%B1%E8%AF%84%E6%B5%8B.m3u?sign=rPssLoffquDXszCARt6UNF8MobSa1FA27XomzOluJBY%3D%3A0
开始下载【线路】南风: https://gh.con.sh/https://raw.githubusercontent.com/yoursmile66/TVBox/main/XC.json
开始下载【线路】2游魂收集不分排名: https://xn--s6wu47g.u.nxog.top/m/333.php?ou=公众号欧歌app&mz=all&jar=all&b=游魂
开始写入单仓🌹游魂主仓库🌹.json
开始写入tvbox.json
开始写入all.json
--------- 完成私有化在线接口 ----------
开始推送：git push https://githubfast.com/fish2018/ol.git
耗时: 176.29488706588745 秒

#################影视仓APP配置接口########################

https://gitdl.cn/https://raw.githubusercontent.com/fish2018/ol/main/all.json
https://gitdl.cn/https://raw.githubusercontent.com/fish2018/ol/main/tvbox.json

```
  

## 更新说明
- V2.5版本 新增三个gh1代理；设置jar_suffix后会自动把历史的jar后缀批量成新的后缀；兼容证书失效的接口
- V2.4版本 mirror=1 https://mirror.ghproxy.com变更为https://ghp.ci；增加mirror=10为'https://gh.con.sh/https://raw.githubusercontent.com'
- V2.3版本 更新大量cdn支持；默认使用githubfast.com加速clone和push，失败切换hub.yzuu.cf
- V2.2版本 支持通过jar_suffix参数修改jar包后缀
- V2.1版本 支持多种镜像加速，通过mirror={num}指定；当mirror<4时自动设置/etc/hosts加速github.com，解决运行docker的本地网络不能访问github
- V2.0版本 修复指定target生成指定`{target}`.json；支持多url下载，英文逗号分隔多个url，`?&signame={name}`指定单线路名，不指定会生成随机名。例子：url = 'http://肥猫.com?&signame=肥猫,http://www.饭太硬.com/tv/?&signame=饭太硬'
- V1.9版本 移除多线程下载接口；已下载接口不重复下载；支持js动态渲染数据的接口；增加根据文件大小去重线路；单线路下载不指定signame(单线路名)时会生成一个"{随机字符串}.txt"；兼容主分支main/master
- V1.8版本 移除agit.ai支持；all.json线路排序；
- V1.7版本 优化git clone速度，仓库重置提交记录计数(始终commit 1，使仓库存储占用小，下载速度快)
- V1.6版本 不规范json兼容优化，http请求timeout默认3s，优化移除emoji表情
- V1.5版本 bug修复，github.com支持优化
- V1.4版本 bug修复，jar下载失败，不会创建0字节jar文件，保留原jar链接
- V1.3版本 支持github.com
- V1.2版本 支持jar本地化
- V1.1版本 bug修复，仅支持agit.ai，不支持jar本地化
- V1.0版本 支持单线路、单仓、多仓下载，输出：{target}(默认tvbox.json)，和url填写的源内容一致；all.json是仓库中所有下载的历史线路总和，并且去重了内容相同的线路
  
