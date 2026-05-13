import json
import os
import shutil
import sys


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_index_by_key(sites, key):
    for i, item in enumerate(sites):
        if isinstance(item, dict) and item.get("key") == key:
            return i
    return -1


def extract_local_paths(value):
    """提取字符串中的本地路径（支持 ./ 和 ../），忽略 URL"""
    if not isinstance(value, str):
        return []
    paths = []
    # 先按 ? 切分，保留路径及查询参数里的路径
    parts = value.split("?")
    for part in parts:
        # 再按常见分隔符切
        for token in part.replace("&", " ").replace("$", " ").split():
            token = token.strip()
            if token.startswith("./") or token.startswith("../"):
                # 去掉可能的尾部参数
                token = token.split("&", 1)[0]
                token = token.split("$", 1)[0]
                paths.append(token)
    return paths


def iter_paths_between(sites, start_key, end_key):
    start_idx = find_index_by_key(sites, start_key)
    end_idx = find_index_by_key(sites, end_key)
    if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
        return []
    subset = sites[start_idx + 1 : end_idx]
    all_paths = []
    for item in subset:
        if not isinstance(item, dict):
            continue
        # api 仅拷贝 .py
        api_val = item.get("api")
        if isinstance(api_val, str):
            for p in extract_local_paths(api_val):
                if p.endswith(".py"):
                    all_paths.append(p)
        # ext 拷贝所有本地路径
        ext_val = item.get("ext")
        if isinstance(ext_val, str):
            all_paths.extend(extract_local_paths(ext_val))
    # 去重，保留顺序
    seen = set()
    deduped = []
    for p in all_paths:
        if p not in seen:
            seen.add(p)
            deduped.append(p)
    return deduped


def main():
    if len(sys.argv) < 2:
        print("用法: python copy_xbpq.py <json路径>")
        print("示例: python copy_xbpq.py jsm_with_app_sites.json")
        sys.exit(1)

    json_path = sys.argv[1]
    data = load_json(json_path)
    sites = data.get("sites", [])

    paths = iter_paths_between(sites, "qiletv", "电影天堂")
    if not paths:
        print("⚠️ 未找到 qiletv 到 电影天堂 之间的 ./XBPQ/ 电影天堂")
        return

    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_base = os.path.normpath(os.path.join(base_dir, "..", "xiaosa"))
    dst_base = os.path.normpath(os.path.join(base_dir, ".."))

    copied = 0
    missing = 0
    for path in paths:
        rel_path = path.replace("./", "", 1)
        rel_path = rel_path.replace("../", "", 1)
        src = os.path.join(src_base, rel_path)
        dst = os.path.join(dst_base, rel_path)
        if not os.path.exists(src):
            print(f"⚠️ 源文件不存在: {src}")
            missing += 1
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print(f"✅ 已覆盖: {dst}")
        copied += 1

    print(f"完成: 复制 {copied} 个，缺失 {missing} 个")


if __name__ == "__main__":
    main()
