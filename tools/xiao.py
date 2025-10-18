import json
import requests
import sys
import hashlib
import os

# 默认 jar 路径和下载 URL（如需下载）
default_jar = "./xiaosa/spider.jar"
default_jar_url = "../xiaosa/spider.jar"

# 需要删除的站点 key
remove_keys = {"巴士动漫"}   # 可以加多个，例如 {"巴士动漫", "电影牛"}

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
        with open(path_or_url, "r", encoding="utf-8") as f:
            return json.load(f)
    elif path_or_url.startswith("http://") or path_or_url.startswith("https://"):
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


def ensure_xyqhiker_ext_and_jar(site):
    """修正所有 csp_XYQHiker 站点的 ext 路径，并加上 jar md5"""
    if not isinstance(site, dict):
        return
    if site.get("api") == "csp_XYQHiker":
        ext_val = site.get("ext", "")
        if ext_val.startswith("./XYQHiker/"):
            site["ext"] = ext_val.replace("./XYQHiker/", "./xiaosa/XYQHiker/")
        ensure_jar_with_md5(site)


def insert_sites_at_key(base_sites, insert_sites, key_marker):
    for i, item in enumerate(base_sites):
        if item.get("key") == key_marker:
            return base_sites[:i] + insert_sites + base_sites[i:]
    print(f"⚠️ 未找到 key 为 {key_marker} 的插入点，追加到末尾")
    return base_sites + insert_sites


def remove_sites(sites, keys_to_remove):
    """从站点列表中删除指定 key 的站点"""
    return [s for s in sites if s.get("key") not in keys_to_remove]


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

    # 3. 为每个 APP site 添加 jar 字段和 md5
    for site in filtered_sites:
        ensure_jar_with_md5(site)

    # 3.1 处理所有 csp_XYQHiker
    for site in sites:
        if isinstance(site, dict) and site.get("api") == "csp_XYQHiker":
            ensure_xyqhiker_ext_and_jar(site)
            filtered_sites.append(site)
    print(f"✅ 筛选并更新 {len(filtered_sites)} 个站点（APP + XYQHiker，含 jar+md5）")

    # 4. 读取本地文件
    with open(local_file, "r", encoding="utf-8") as f:
        dianshi = json.load(f)

    # 5. 插入到 key="玩偶" 处
    dianshi_sites = dianshi.get("sites", [])
    dianshi["sites"] = insert_sites_at_key(dianshi_sites, filtered_sites, "玩偶")

    # 6. 删除指定的站点
    before_count = len(dianshi["sites"])
    dianshi["sites"] = remove_sites(dianshi["sites"], remove_keys)
    after_count = len(dianshi["sites"])
    print(f"✅ 删除了 {before_count - after_count} 个指定站点: {', '.join(remove_keys)}")

    # 7. 保存合并结果
    output_file = f"{local_file.rsplit('.',1)[0]}_with_app_sites.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(dianshi, f, ensure_ascii=False, indent=2, cls=CompactJSONEncoder)

    print(f"✅ 合并完成，已保存为 {output_file}")
