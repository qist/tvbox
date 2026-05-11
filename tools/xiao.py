import json
import sys
import hashlib
import os

# jar 路径（用于计算 md5）
primary_jar_path = "jar/spider.jar"
fallback_jar_path = "../xiaosa/spider.jar"

# 需要删除的站点 key（在此填写即可删除）
remove_keys = {"版本信息","腾讯视频","优酷视频","芒果视频","爱奇艺","三六零","豆瓣","push_agent","配置中心","本地","预告"}   # 可以加多个，例如 {"巴士动漫", "电影牛"}

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
    raise ValueError(f"无效路径或 URL：{path_or_url}")


def get_md5(filepath):
    md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            md5.update(chunk)
    return md5.hexdigest()

def replace_drpy_path(site):
    """将 ./js/drpy2.min.js 替换为 ./lib/drpy2.min.js"""
    if not isinstance(site, dict):
        return
    for field in ("api", "ext"):
        val = site.get(field)
        if isinstance(val, str) and val == "./js/drpy2.min.js":
            site[field] = "./lib/drpy2.min.js"




def insert_sites_at_key(base_sites, insert_sites, key_marker):
    for i, item in enumerate(base_sites):
        if item.get("key") == key_marker:
            return base_sites[:i + 1] + insert_sites + base_sites[i + 1:]
    print(f"⚠️ 未找到 key 为 {key_marker} 的插入点，追加到末尾")
    return base_sites + insert_sites


def remove_sites(sites, keys_to_remove):
    """从站点列表中删除指定 key 的站点"""
    return [s for s in sites if s.get("key") not in keys_to_remove]


def dedupe_by_name(base_sites, insert_sites):
    """按 name 去重：若重名，优先保留 base_sites 中的条目"""
    base_names = {s.get("name") for s in base_sites if isinstance(s, dict)}
    return [s for s in insert_sites if s.get("name") not in base_names]


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python xiao.py <本地api.json路径> <本地dianshi.json路径>")
        print("示例: python xiao.py ../xiaosa/api.json dianshi.json")
        sys.exit(1)

    remote_url = sys.argv[1]
    local_file = sys.argv[2]

    # 1. 下载远程 JSON
    data = fetch_json(remote_url)

    # 2. 读取 sites（不再筛选）
    sites = data.get("sites", [])
    filtered_sites = [s for s in sites if isinstance(s, dict)]

    # 3. 不再单独追加 XYQHiker（已包含在 sites 中）

    # 3.1 不删除站点，仅移除每个站点的 jar 字段
    before_count = len(filtered_sites)
    removed_sites = []
    for site in filtered_sites:
        replace_drpy_path(site)
        if isinstance(site, dict) and "jar" in site:
            site.pop("jar", None)
    removed_count = before_count - len(filtered_sites)
    print(f"✅ 更新 {len(filtered_sites)} 个站点")

    # 4. 读取本地文件
    with open(local_file, "r", encoding="utf-8") as f:
        dianshi = json.load(f)

    # 5. 插入到 key="cbh" 之后（按 name 去重，保留本地）
    dianshi_sites = dianshi.get("sites", [])
    # 先按 key 删除来源站点
    if remove_keys:
        filtered_sites = [s for s in filtered_sites if s.get("key") not in remove_keys]
    filtered_sites = dedupe_by_name(dianshi_sites, filtered_sites)
    dianshi["sites"] = insert_sites_at_key(dianshi_sites, filtered_sites, "qiletv")

    # 6. 删除指定的站点
    # before_count = len(dianshi["sites"])
    # dianshi["sites"] = remove_sites(dianshi["sites"], remove_keys)
    # after_count = len(dianshi["sites"])
    # print(f"✅ 删除了 {before_count - after_count} 个指定站点: {', '.join(remove_keys)}")

    # 7. 设置 spider 为 jar+md5（统一在输出文件中）
    jar_path = primary_jar_path if os.path.exists(primary_jar_path) else fallback_jar_path
    if os.path.exists(jar_path):
        md5_val = get_md5(jar_path)
        dianshi["spider"] = f"./jar/spider.jar;md5;{md5_val}"
        print(f"🔄 spider 已更新为: {dianshi['spider']}")
    else:
        print(f"⚠️ 找不到 jar 文件，未更新 spider：{primary_jar_path} / {fallback_jar_path}")

    # 8. 保存合并结果（新文件）
    output_file = f"{local_file.rsplit('.',1)[0]}_with_app_sites.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(dianshi, f, ensure_ascii=False, indent=2, cls=CompactJSONEncoder)

    print(f"✅ 合并完成，已保存为 {output_file}")
