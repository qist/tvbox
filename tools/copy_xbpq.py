import json
import os
import shutil
import sys


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_local_paths(value):
    """提取字符串中的本地路径（支持 ./ 和 ../），忽略 URL。按 ? 与常见分隔符切分。"""
    if not isinstance(value, str):
        return []
    paths = []
    for part in value.split("?"):
        for token in part.replace("&", " ").replace("$", " ").split():
            token = token.strip()
            if token.startswith("./") or token.startswith("../"):
                token = token.split("&", 1)[0].split("$", 1)[0]
                paths.append(token)
    return paths


def collect_local_paths(obj):
    """递归收集任意结构（dict/list/str）中的本地路径字符串"""
    found = []
    if isinstance(obj, str):
        found.extend(extract_local_paths(obj))
    elif isinstance(obj, dict):
        for v in obj.values():
            found.extend(collect_local_paths(v))
    elif isinstance(obj, list):
        for v in obj:
            found.extend(collect_local_paths(v))
    return found


def iter_all_local_paths(sites):
    """提取整份 sites 里所有本地路径（不限制区间），递归含 ext 字典"""
    all_paths = []
    for item in sites:
        if isinstance(item, dict):
            all_paths.extend(collect_local_paths(item))
    # 去重，保留顺序
    seen, deduped = set(), []
    for p in all_paths:
        if p not in seen:
            seen.add(p)
            deduped.append(p)
    return deduped


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) >= 2:
        json_path = sys.argv[1]
    else:
        json_path = os.path.join(base_dir, "output", "api.json")
    if not os.path.exists(json_path):
        print(f"⚠️ 找不到文件: {json_path}")
        sys.exit(1)

    data = load_json(json_path)
    sites = data.get("sites", [])

    # 直接提取整份 json 的全部本地路径，不做区间判断
    paths = iter_all_local_paths(sites)
    if not paths:
        print("⚠️ 未在 sites 中找到任何本地文件")
        return

    # 源来自 output 目录，按 json 相对路径复制到项目根（保留子目录，避免 404 且 py/js/json 不混淆）
    src_base = os.path.normpath(os.path.join(base_dir, "output"))
    dst_base = os.path.normpath(os.path.join(base_dir, ".."))

    copied = 0
    missing = 0
    for path in paths:
        rel = path.replace("./", "", 1).replace("../", "", 1)
        src = os.path.join(src_base, rel)
        dst = os.path.join(dst_base, rel)
        if not os.path.exists(src):
            print(f"⚠️ 源文件不存在: {src}")
            missing += 1
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print(f"✅ 已复制: {dst}")
        copied += 1

    print(f"完成: 复制 {copied} 个，缺失 {missing} 个")


if __name__ == "__main__":
    main()
