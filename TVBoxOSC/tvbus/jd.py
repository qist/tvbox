import socket

def check_port(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)  # 设置超时时间
        try:
            s.connect((ip, port))
            return True
        except:
            return False

ip = "108.181.32.169"
open_ports = []

for port in range(10000, 65537):
    if check_port(ip, port):
        open_ports.append(port)

with open("Py.txt", "w") as file:
    for port in open_ports:
        file.write(f"{port}
")

print(f"开放的端口已保存到 Py.txt 文件中。")
