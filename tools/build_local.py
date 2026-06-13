#!/usr/bin/env python3
"""
TVBox 本地构建脚本
将解密的 JSON 配置文件转换为本地资源版本

功能：
1. 下载 spider 并命名为 spider.jar
2. 下载 ext 中的 JSON 文件到 json 目录
3. 下载 JS 文件到 js 目录
4. 下载 api 中的 PY 文件到 py 目录
5. 生成本地版本的 JSON 配置文件
"""

import json
import os
import re
import sys
import hashlib
import requests
from pathlib import Path
from urllib.parse import urlparse


class TVBox本地构建器:
    def __init__(self, 输入文件, 输出目录="output"):
        self.输入文件 = 输入文件
        self.输出目录 = Path(输出目录)
        self.数据 = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def 加载数据(self):
        """加载 JSON 数据"""
        with open(self.输入文件, 'r', encoding='utf-8') as f:
            self.数据 = json.load(f)
        print(f"✓ 加载配置文件: {self.输入文件}")
        return True

    def 创建目录结构(self):
        """创建输出目录结构"""
        dirs = ['json', 'js', 'py']
        for d in dirs:
            (self.输出目录 / d).mkdir(parents=True, exist_ok=True)
        print(f"✓ 创建目录结构: {', '.join(dirs)}")

    def 计算MD5(self, 文件路径):
        """计算文件的 MD5"""
        md5 = hashlib.md5()
        with open(文件路径, 'rb') as f:
            while chunk := f.read(8192):
                md5.update(chunk)
        return md5.hexdigest()

    def 替换代理域名(self, url):
        """将代理域名替换为直接访问 raw.githubusercontent.com"""
        # 匹配各种 GitHub 代理域名
        proxy_patterns = [
            (r'https?://git\.yylx\.win/raw\.githubusercontent\.com/', 'https://raw.githubusercontent.com/'),
            (r'https?://gh-proxy\.com/https://raw\.githubusercontent\.com/', 'https://raw.githubusercontent.com/'),
            (r'https?://[^/]+/https://raw\.githubusercontent\.com/', 'https://raw.githubusercontent.com/'),
        ]

        for pattern, replacement in proxy_patterns:
            if re.match(pattern, url):
                new_url = re.sub(pattern, replacement, url)
                if new_url != url:
                    print(f"  替换代理: {url[:60]}...")
                    print(f"       ->: {new_url[:60]}...")
                    return new_url

        return url

    def 下载文件(self, url, 保存路径):
        """下载文件"""
        try:
            # 替换代理域名为直接访问
            url = self.替换代理域名(url)

            print(f"  下载: {url}")
            resp = self.session.get(url, timeout=30, allow_redirects=True)
            resp.raise_for_status()
            with open(保存路径, 'wb') as f:
                f.write(resp.content)
            print(f"  ✓ 保存到: {保存路径}")
            return True
        except Exception as e:
            print(f"  ✗ 下载失败: {e}")
            return False

    def 下载spider(self):
        """下载 spider 文件"""
        spider_url = self.数据.get('spider', '')
        if not spider_url:
            print("✗ 未找到 spider 配置")
            return False

        # 提取 URL（去掉 ;md5;xxx 部分）
        url = spider_url.split(';')[0]
        spider_path = self.输出目录 / 'spider.jar'

        print(f"\n=== 下载 Spider ===")
        if self.下载文件(url, spider_path):
            md5 = self.计算MD5(spider_path)
            print(f"  MD5: {md5}")
            self.数据['spider'] = f"./spider.jar;md5;{md5}"
            return True
        return False

    def 是URL(self, 路径):
        """判断是否为URL"""
        try:
            result = urlparse(路径)
            return all([result.scheme, result.netloc])
        except:
            return False

    def 提取文件名(self, url):
        """从 URL 提取文件名"""
        path = urlparse(url).path
        name = Path(path).name
        # 如果没有扩展名，根据内容添加
        if '.' not in name:
            name += '.txt'
        return name

    def 下载ext文件(self):
        """下载 ext 中的 JSON 文件"""
        print(f"\n=== 下载 ext 文件 ===")
        下载计数 = 0

        for site in self.数据.get('sites', []):
            ext = site.get('ext', '')

            # 处理字符串类型的 ext（可能是 URL）
            if isinstance(ext, str) and self.是URL(ext):
                文件名 = self.提取文件名(ext)
                # 根据扩展名决定保存目录
                if 文件名.endswith('.json'):
                    保存路径 = self.输出目录 / 'json' / 文件名
                    if self.下载文件(ext, 保存路径):
                        site['ext'] = f"./json/{文件名}"
                        下载计数 += 1
                elif 文件名.endswith('.js'):
                    保存路径 = self.输出目录 / 'js' / 文件名
                    if self.下载文件(ext, 保存路径):
                        site['ext'] = f"./js/{文件名}"
                        下载计数 += 1

            # 处理字典类型的 ext
            elif isinstance(ext, dict):
                for key, value in ext.items():
                    if isinstance(value, str) and self.是URL(value):
                        文件名 = self.提取文件名(value)
                        if 文件名.endswith('.json'):
                            保存路径 = self.输出目录 / 'json' / 文件名
                            if self.下载文件(value, 保存路径):
                                ext[key] = f"./json/{文件名}"
                                下载计数 += 1

        print(f"  共下载 {下载计数} 个 ext 文件")
        return 下载计数

    def 下载api文件(self):
        """下载 api 中的 PY 文件（JS 文件保持原链接）"""
        print(f"\n=== 下载 api 文件 ===")
        下载计数 = 0

        for site in self.数据.get('sites', []):
            api = site.get('api', '')

            # 处理以 http 开头的 api（仅下载 PY 文件，JS 保持原链接）
            if isinstance(api, str) and api.startswith('http'):
                文件名 = self.提取文件名(api)
                if 文件名.endswith('.py'):
                    保存路径 = self.输出目录 / 'py' / 文件名
                    if self.下载文件(api, 保存路径):
                        site['api'] = f"./py/{文件名}"
                        下载计数 += 1
                elif 文件名.endswith('.js'):
                    # JS 文件不下载，保持原链接
                    print(f"  跳过 JS (保持原链接): {api}")

        print(f"  共下载 {下载计数} 个 api 文件")
        return 下载计数

    def 下载lives文件(self):
        """下载 lives 中的文件"""
        print(f"\n=== 下载 lives 文件 ===")
        下载计数 = 0

        for live in self.数据.get('lives', []):
            url = live.get('url', '')
            if isinstance(url, str) and self.是URL(url):
                文件名 = self.提取文件名(url)
                保存路径 = self.输出目录 / 'json' / 文件名
                if self.下载文件(url, 保存路径):
                    live['url'] = f"./json/{文件名}"
                    下载计数 += 1

        print(f"  共下载 {下载计数} 个 lives 文件")
        return 下载计数

    def 压缩flags(self, flags):
        """压缩 flags 列表，去除带空格的重复项"""
        if not isinstance(flags, list):
            return flags

        # 去除带空格的重复项（如 "优 酷" -> "优酷"）
        compressed = []
        seen = set()

        for flag in flags:
            # 去除空格
            no_space = flag.replace(' ', '')
            if no_space not in seen:
                seen.add(no_space)
                compressed.append(flag)

        print(f"\n=== 压缩 flags ===")
        print(f"  原始: {len(flags)} 项")
        print(f"  压缩后: {len(compressed)} 项")

        return compressed

    def 保存配置(self):
        """保存本地版本的配置文件"""
        输出文件 = self.输出目录 / 'api.json'

        # 压缩 flags（去除带空格的重复项）
        if 'flags' in self.数据:
            self.数据['flags'] = self.压缩flags(self.数据['flags'])

        # 使用 CompactJSONEncoder 格式化输出
        class CompactJSONEncoder(json.JSONEncoder):
            def iterencode(self, o, _one_shot=False):
                def _compact_list(lst, indent_level):
                    pad = '  ' * indent_level
                    if all(isinstance(i, dict) for i in lst):
                        return '[\n' + ',\n'.join([pad + '  ' + json.dumps(i, ensure_ascii=False, separators=(',', ': ')) for i in lst]) + '\n' + pad + ']'
                    return json.dumps(lst, ensure_ascii=False, indent=2)
                def _encode(obj, indent_level=0):
                    pad = '  ' * indent_level
                    if isinstance(obj, dict):
                        lines = [f'"{k}": {_encode(v, indent_level+1)}' for k, v in obj.items()]
                        return '{\n' + pad + '  ' + (',\n' + pad + '  ').join(lines) + '\n' + pad + '}'
                    elif isinstance(obj, list):
                        return _compact_list(obj, indent_level)
                    return json.dumps(obj, ensure_ascii=False)
                return iter([_encode(o)])

        with open(输出文件, 'w', encoding='utf-8') as f:
            json.dump(self.数据, f, ensure_ascii=False, indent=2, cls=CompactJSONEncoder)

        print(f"\n✓ 保存配置文件: {输出文件}")
        return True

    def 构建(self):
        """执行构建流程"""
        print("=" * 50)
        print("TVBox 本地构建工具")
        print("=" * 50)

        # 加载数据
        if not self.加载数据():
            return False

        # 创建目录结构
        self.创建目录结构()

        # 下载各类资源
        self.下载spider()
        self.下载ext文件()
        self.下载api文件()
        self.下载lives文件()

        # 保存配置
        self.保存配置()

        print("\n" + "=" * 50)
        print("✓ 构建完成！")
        print(f"输出目录: {self.输出目录}")
        print("=" * 50)

        return True


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python build_local.py 输入文件 [输出目录]")
        print("")
        print("示例:")
        print("  python build_local.py api.json")
        print("  python build_local.py api.json output")
        print("  python build_local.py https://example.com/api.json output")
        print("")
        print("说明:")
        print("  将解密的 JSON 配置文件转换为本地资源版本")
        print("  自动下载 spider、ext、api、lives 等资源到本地")
        sys.exit(1)

    输入文件 = sys.argv[1]
    输出目录 = sys.argv[2] if len(sys.argv) > 2 else "output"

    构建器 = TVBox本地构建器(输入文件, 输出目录)
    构建器.构建()


if __name__ == "__main__":
    main()
