import requests
import time

# 待ping的IP地址列表
ip_addresses = [
    "66.90.99.154",
    "50.7.234.10",
    "50.7.220.170",
    "67.159.6.34",
    "198.16.100.186"
]

# 存储每个IP地址的延迟
latencies = []

# 遍历每个IP地址
for ip in ip_addresses:
    url = f"http://{ip}:8278"
    start_time = time.time()  # 记录开始时间

    try:
        # 发起请求
        response = requests.get(url, timeout=5)  # 超时时间设为5秒
        latency = (time.time() - start_time) * 1000  # 计算延迟（毫秒）

        # 添加到latencies列表
        latencies.append((ip, latency))
    except requests.exceptions.RequestException as e:
        # 处理请求异常
        print(f"无法访问 {ip}:8278 - {e}")

# 根据延迟排序
latencies.sort(key=lambda x: x[1])

# 输出结果
for ip, latency in latencies:
    print(f"IP: {ip}, 延迟: {latency:.2f} ms")