## Support using private Gitee or GitHub repositories as remote config.
    * github://<your personal access token>@github.com/<owner>/<repo>/<ref>/<file path>
    * gitee://<your access token>@gitee.com/<owner>/<repo>/<ref>/<file path>
    * github://ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@github.com/omii/catvod/main/config_open.json
    * gitee://xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@gitee.com/omii/catvod/master/config_open.json
    * https://omii%40qq.com:88888888@dav.jianguoyun.com/dav/cat/js/config_open.json


## personal access token
    * Settings > Developer settings > Personal access tokens > Token (classic) > Generate new token
    * Settings > Developer settings > Personal access tokens > Fine-grained tokens > Generate new token


## 远端配置：
    * github://ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@github.com/omiitop/CatVod/main/js/config_open.json
    * github://github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@github.com/omiitop/CatVod/main/js/config_open.json


## 本地配置：
    * assets://js/config_open.json

## 远程配置教程：
    * https://omii.top/1296.html

## iOS签名教程
    * https://omii.top/826.html
    * https://omii.top/1498.html 推荐

## 自定义背景
     "color": [
        {
            "light": { "bg": "https://i2.100024.xyz/2024/01/13/qrnuwt.webp", "bgMask": "0x50ffffff", "primary": "0xFF2B6C00", "onPrimary": "0xFFFFFFFF", "primaryContainer": "0xFFA6F779", "onPrimaryContainer": "0xFF082100", "secondary": "0xFF55624C", "onSecondary": "0xFFFFFFFF", "secondaryContainer": "0xFFD9E7CA", "onSecondaryContainer": "0xFF131F0D", "tertiary": "0xFF386666", "onTertiary": "0xFFFFFFFF", "tertiaryContainer": "0xFFBBEBEB", "onTertiaryContainer": "0xFF002020", "error": "0xFFBA1A1A", "onError": "0xFFFFFFFF", "errorContainer": "0xFFFFDAD6", "onErrorContainer": "0xFF410002", "background": "0xFFFDFDF5", "onBackground": "0xFF1A1C18", "surface": "0xFFFDFDF5", "onSurface": "0xFF1A1C18", "surfaceVariant": "0xFFE0E4D6", "onSurfaceVariant": "0xFF1A1C18", "inverseSurface": "0xFF2F312C", "onInverseSurface": "0xFFF1F1EA", "outline": "0xFF74796D", "outlineVariant": "0xFFC3C8BB", "shadow": "0xFF000000", "scrim": "0xFF000000", "inversePrimary": "0xFF8CDA60", "surfaceTint": "0xFF2B6C00" },
            "dark": { "bg": "https://i2.100024.xyz/2024/01/13/qrc37o.webp", "bgMask": "0x50000000", "primary": "0xFF8CDA60", "onPrimary": "0xFF133800", "primaryContainer": "0xFF1F5100", "onPrimaryContainer": "0xFFA6F779", "secondary": "0xFFBDCBAF", "onSecondary": "0xFF283420", "secondaryContainer": "0xFF3E4A35", "onSecondaryContainer": "0xFFD9E7CA", "tertiary": "0xFFA0CFCF", "onTertiary": "0xFF003737", "tertiaryContainer": "0xFF1E4E4E", "onTertiaryContainer": "0xFFBBEBEB", "error": "0xFFFFB4AB", "errorContainer": "0xFF93000A", "onError": "0xFF690005", "onErrorContainer": "0xFFFFDAD6", "background": "0xFF1A1C18", "onBackground": "0xFFE3E3DC", "outline": "0xFF8D9286", "onInverseSurface": "0xFF1A1C18", "inverseSurface": "0xFFE3E3DC", "inversePrimary": "0xFF2B6C00", "shadow": "0xFF000000", "surfaceTint": "0xFF8CDA60", "outlineVariant": "0xFF43483E", "scrim": "0xFF000000", "surface": "0xFF1A1C18", "onSurface": "0xFFC7C7C0", "surfaceVariant": "0xFF43483E", "onSurfaceVariant": "0xFFC7C7C0" }
        }
    ],


## 自助添加接口格式：
           {
                "key": "wogg",  
                "name": "🟢 玩偶",
                "type": 3,
                "api": "./wogg_open.js",
                "ext": "填入阿里token"
            },
            
         "key"、"name" 内:与其他不重复的名称均可。     
         "type" 3为影视，10为有声读物
         "api" 填写js路径，"ext" 填写扩展内容，例如玩偶的token。
         以上由omii.top提供
