import json
import requests
import re
import sys
import hashlib
import os

# 默认 jar 路径和下载 URL（如需下载）
default_jar = "./xiaosa/spider.jar"
# 如果需要自动下载 jar，可替换为真实链接；否则留空
default_jar_url = "../xiaosa/spider.jar"

# 保存 JSON 文件（折叠字典数组为单行，空数组和基础数组一行）
class CompactJSONEncoder(json.JSONEncoder):
    def iterencode(self, o, _one_shot=False):
        def _compact_list(lst, indent_level):
            pad = '  ' * indent_level
            if not lst or all(isinstance(i, (str, int, float, bool, type(None))) for i in lst):
                return json.dumps(lst, ensure_ascii=False)
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

def fetch_json(path_or_url):
    if os.path.exists(path_or_url):
        # 本地文件
        with open(path_or_url, "r", encoding="utf-8") as f:
            return json.load(f)
    elif path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        # 网络 URL
        resp = requests.get(path_or_url)
        resp.raise_for_status()
        return resp.json()
    else:
        raise ValueError(f"无效路径或 URL：{path_or_url}")


def get_md5(filepath):
    md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            md5.update(chunk)
    return md5.hexdigest()

def ensure_jar_with_md5(site):
    if not isinstance(site, dict):
        return
    jar_val = site.get("jar")
    if jar_val and ";md5;" in jar_val:
        return  # 已包含 md5
    if not os.path.exists(default_jar_url):
        print(f"⚠️ 找不到本地 jar 文件：{default_jar_url}")
        return
    md5_val = get_md5(default_jar_url)
    site["jar"] = f"{default_jar};md5;{md5_val}"

def insert_sites_at_key(base_sites, insert_sites, key_marker):
    for i, item in enumerate(base_sites):
        if item.get("key") == key_marker:
            return base_sites[:i] + insert_sites + base_sites[i:]
    print(f"⚠️ 未找到 key 为 {key_marker} 的插入点，追加到末尾")
    return base_sites + insert_sites

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python script.py <远程json_url> <本地dianshi.json路径>")
        print("示例: python script.py https://raw.githubusercontent.com/qist/tvbox/master/xiaosa/api.json dianshi.json")
        sys.exit(1)

    remote_url = sys.argv[1]
    local_file = sys.argv[2]

    # 1. 下载远程 JSON
    data = fetch_json(remote_url)

    # 2. 筛选 sites，只保留 name 含 APP
    sites = data.get("sites", [])
    filtered_sites = [s for s in sites if isinstance(s, dict) and "name" in s and "APP" in s["name"]]

    # 3. 为每个筛选 site 添加 jar 字段和 md5
    for site in filtered_sites:
        ensure_jar_with_md5(site)
    print(f"✅ 筛选并更新 {len(filtered_sites)} 个含 APP 的 sites（包含 md5 jar 字段）")

    # 4. 读取本地文件
    with open(local_file, "r", encoding="utf-8") as f:
        dianshi = json.load(f)

    # 5. 插入到 key="玩偶" 处
    dianshi_sites = dianshi.get("sites", [])
    dianshi["sites"] = insert_sites_at_key(dianshi_sites, filtered_sites, "玩偶")

    # 6. 保存合并结果
    output_file = f"{local_file.rsplit('.',1)[0]}_with_app_sites.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(dianshi, f, ensure_ascii=False, indent=2, cls=CompactJSONEncoder)

    print(f"✅ 合并完成，已保存为 {output_file}")
