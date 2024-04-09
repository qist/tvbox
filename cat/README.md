## nginx配置 dav


参考文档：https://forevertime.site/nginx-setup-webdav-for-zotero-sync/

## 自己配置

```bash
cd /opt/nginx/html
git clone https://github.com/qist/tvbox.git

# 定时任务 

crontab -e 

10 */1 * * * cd /opt/nginx/html/tvbox && git pull

#每个小时地10分钟执行一次
```

```nginx
    location /dav {
        lua_need_request_body off;
        alias /opt/nginx/html/tvbox;
        autoindex on;
        dav_methods PUT MKCOL COPY MOVE;
        dav_ext_methods PROPFIND OPTIONS;
        create_full_put_path on;
        dav_access user:rw group:r all:r;
        auth_basic "Authorized Users Only";
        auth_basic_user_file /etc/nginx/.credentials.list;
    }
```

#### 新源地址

```text
#V1.1.3版本以上

https://你的账号:你的密码@你的域名/dav/cat/dist/index.js.md5 

#V1.1.2版本以下
https://你的账号:你的密码@你的域名/dav/cat/tjs/open_config.json
```