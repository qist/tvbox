import json
import os
import sys
import gzip
import base64
import tempfile
from pathlib import Path
from urllib.parse import urlparse, quote
from urllib.request import urlopen, Request
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class 文件加解密器:
    def __init__(self, key="1234567890123", iv="1234567890123"):
        self.key = key
        self.iv = iv

    def 是URL(self, 路径):
        """判断是否为URL"""
        try:
            result = urlparse(路径)
            return all([result.scheme, result.netloc])
        except:
            return False

    def 从URL获取内容(self, url, 处理gzip=True, 处理base64=True):
        """从URL获取内容，支持gzip和base64解码"""
        import re
        try:
            print(f"正在从URL获取: {url}")
            # 处理中文域名：对域名部分进行IDNA编码
            parsed = urlparse(url)
            if parsed.netloc:
                # 尝试将域名转换为IDNA编码
                try:
                    idna_domain = parsed.netloc.encode('idna').decode('ascii')
                    url = parsed._replace(netloc=idna_domain).geturl()
                except:
                    # 如果IDNA编码失败，尝试对非ASCII字符进行percent编码
                    encoded_netloc = quote(parsed.netloc, safe='')
                    url = parsed._replace(netloc=encoded_netloc).geturl()

            req = Request(url, headers={
                'User-Agent': 'okhttp/3.12.0',
                'Accept-Encoding': 'gzip, deflate'
            })
            with urlopen(req, timeout=30) as response:
                raw_content = response.read()

                # 检查是否为图片或二进制文件
                content_type = response.headers.get('Content-Type', '')
                if content_type.startswith('image/') or content_type.startswith('video/') or content_type.startswith('audio/'):
                    print(f"  检测到{content_type}类型，尝试提取嵌入的数据...")

                # 检查文件头是否为常见图片格式
                image_headers = [
                    b'\xff\xd8\xff\xe0',  # JPEG
                    b'\xff\xd8\xff\xe1',  # JPEG
                    b'\x89PNG',           # PNG
                    b'GIF87a',            # GIF
                    b'GIF89a',            # GIF
                    b'BM',                # BMP
                ]
                is_image = False
                for header in image_headers:
                    if raw_content.startswith(header):
                        is_image = True
                        break

                # 如果是图片，尝试提取嵌入的base64数据
                if is_image:
                    print(f"  检测到图片文件，尝试提取嵌入的base64数据...")
                    try:
                        # 转为文本查找base64数据
                        text_content = raw_content.decode('latin-1')
                        # 查找长base64字符串（至少50个字符）
                        base64_pattern = r'[A-Za-z0-9+/=]{50,}'
                        match = re.search(base64_pattern, text_content)
                        if match:
                            base64_str = match.group(0)
                            print(f"  找到base64数据，长度: {len(base64_str)}")
                            decoded = base64.b64decode(base64_str)
                            # 将解码后的内容转为字符串
                            for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                                try:
                                    content = decoded.decode(encoding)
                                    print(f"✓ 成功提取图片中的base64数据 ({len(content)} 字节)")
                                    return content
                                except UnicodeDecodeError:
                                    continue
                    except Exception as e:
                        print(f"  提取图片数据失败: {e}")

                # 处理gzip解压
                if 处理gzip:
                    try:
                        raw_content = gzip.decompress(raw_content)
                        print(f"  ✓ gzip解压成功")
                    except:
                        # 不是gzip格式，继续处理
                        pass

                # 尝试多种编码解码
                content = None
                for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                    try:
                        content = raw_content.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue

                if content is None:
                    content = raw_content.decode('latin-1')

                # 处理base64解码（仅当内容看起来像base64且不是hex数据时）
                if 处理base64:
                    # 检查是否为hex数据（只包含0-9, a-f, A-F）
                    stripped = content.strip()
                    is_hex = re.match(r'^[0-9a-fA-F]+$', stripped) is not None

                    if not is_hex:
                        try:
                            # 尝试base64解码
                            decoded = base64.b64decode(content)
                            # 解码后再次尝试gzip解压
                            try:
                                decoded = gzip.decompress(decoded)
                                print(f"  ✓ base64+gzip解码成功")
                            except:
                                print(f"  ✓ base64解码成功")
                            # 将解码后的内容转为字符串
                            for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                                try:
                                    content = decoded.decode(encoding)
                                    break
                                except UnicodeDecodeError:
                                    continue
                        except:
                            # 不是base64格式，继续使用原内容
                            pass

                print(f"✓ 成功获取URL内容 ({len(content)} 字节)")
                return content
        except Exception as e:
            print(f"✗ 获取URL内容失败: {e}")
            return None

    def 保存到临时文件(self, 内容, 后缀=".json"):
        """将内容保存到临时文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=后缀, delete=False, encoding='utf-8') as f:
            f.write(内容)
            return f.name

    def 字符串转hex(self, 文本): 
        return 文本.encode().hex()
    
    def hex转字符串(self, hex文本): 
        return bytes.fromhex(hex文本).decode()
    
    def 加密文件(self, 输入文件, 输出文件):
        """加密单个文件（支持本地文件或URL）"""
        try:
            print(f"加密: {输入文件} -> {输出文件}")

            # 判断输入是URL还是本地文件
            if self.是URL(输入文件):
                内容 = self.从URL获取内容(输入文件)
                if 内容 is None:
                    return False
                data = json.loads(内容)
            else:
                with open(输入文件, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            # AES加密
            填充key = self.key.ljust(16, '0').encode()
            填充iv = self.iv.ljust(16, '0').encode()
            cipher = AES.new(填充key, AES.MODE_CBC, 填充iv)
            encrypted = cipher.encrypt(pad(json.dumps(data, ensure_ascii=False).encode(), 16))
            
            # 数据包装并转Hex
            header_hex = self.字符串转hex(f"$#{self.key}#$")
            cipher_hex = encrypted.hex()
            iv_hex = self.字符串转hex(self.iv)
            final_hex = header_hex + cipher_hex + iv_hex
            
            with open(输出文件, 'w') as f:
                f.write(final_hex)
            
            print(f"✓ 加密成功: {输入文件}")
            return True
            
        except Exception as e:
            print(f"✗ 加密失败 {输入文件}: {e}")
            return False
    
    def 解密文件(self, 输入文件, 输出文件):
        """解密单个文件（支持本地文件或URL）"""
        try:
            print(f"解密: {输入文件} -> {输出文件}")

            # 判断输入是URL还是本地文件
            if self.是URL(输入文件):
                内容 = self.从URL获取内容(输入文件)
                if 内容 is None:
                    return False
                hex数据 = 内容.strip()
            else:
                with open(输入文件, 'r', encoding='utf-8') as f:
                    hex数据 = f.read().strip()

            # 移除JavaScript风格的注释（// 开头的行）
            import re
            hex数据 = re.sub(r'^//.*$', '', hex数据, flags=re.MULTILINE).strip()

            # 尝试直接解析为JSON（如果已经是JSON格式）
            try:
                data = json.loads(hex数据)
                with open(输出文件, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"✓ 直接保存JSON成功: {输入文件}")
                return True
            except json.JSONDecodeError:
                # 不是JSON格式，尝试解密
                pass

            # 检查是否为有效的hex数据
            import re
            if not re.match(r'^[0-9a-fA-F]+$', hex数据):
                raise ValueError("内容既不是有效的JSON也不是有效的hex加密数据")

            # 解析Hex数据
            header_marker = self.字符串转hex("#$")
            header_pos = hex数据.find(header_marker)
            if header_pos == -1:
                raise ValueError("文件格式错误，未找到有效的头部标记")

            header_end = header_pos + 4
            header_hex = hex数据[:header_end]
            iv_hex = hex数据[-26:]
            cipher_hex = hex数据[header_end:-26]

            # 提取key和iv
            real_key = self.hex转字符串(header_hex)[2:-2]
            real_iv = self.hex转字符串(iv_hex)

            # AES解密
            填充key = real_key.ljust(16, '0').encode()
            填充iv = real_iv.ljust(16, '0').encode()
            cipher = AES.new(填充key, AES.MODE_CBC, 填充iv)
            decrypted = unpad(cipher.decrypt(bytes.fromhex(cipher_hex)), 16)

            with open(输出文件, 'w', encoding='utf-8') as f:
                json.dump(json.loads(decrypted.decode()), f, ensure_ascii=False, indent=2)

            print(f"✓ 解密成功: {输入文件}")
            return True

        except Exception as e:
            print(f"✗ 解密失败 {输入文件}: {e}")
            return False
    
    def 获取URL内容(self, url, 输出文件):
        """直接获取URL内容并保存（不进行加密/解密处理）"""
        try:
            print(f"获取URL内容: {url} -> {输出文件}")

            内容 = self.从URL获取内容(url)
            if 内容 is None:
                return False

            # 移除JavaScript风格的注释（// 开头的行）
            import re
            内容 = re.sub(r'^//.*$', '', 内容, flags=re.MULTILINE).strip()

            # 尝试解析为JSON并格式化保存
            try:
                data = json.loads(内容)
                with open(输出文件, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"✓ 获取并保存JSON成功: {输出文件}")
                return True
            except json.JSONDecodeError:
                # 不是JSON格式，直接保存原始内容
                with open(输出文件, 'w', encoding='utf-8') as f:
                    f.write(内容)
                print(f"✓ 获取并保存内容成功: {输出文件}")
                return True

        except Exception as e:
            print(f"✗ 获取URL内容失败 {url}: {e}")
            return False

    def 批量处理(self, 输入目录, 输出目录, 模式="enc"):
        """批量处理目录中的文件或URL，保持原文件名"""
        输出路径 = Path(输出目录)

        文件列表 = []

        # 判断输入是否为URL
        if self.是URL(输入目录):
            文件列表 = [输入目录]
        else:
            输入路径 = Path(输入目录)
            if 输入路径.is_file():
                文件列表 = [输入路径]
            else:
                # 只有当输入是目录时，才创建输出目录
                输出路径.mkdir(parents=True, exist_ok=True)
                文件列表 = [f for f in 输入路径.iterdir() if f.is_file()]

        if not 文件列表:
            print(f"在 {输入目录} 中未找到文件")
            return

        print(f"找到 {len(文件列表)} 个文件进行处理...")

        成功计数 = 0
        for 输入文件 in 文件列表:
            # 处理输出文件名
            if isinstance(输入文件, str) and self.是URL(输入文件):
                # 如果输出路径是文件（不是目录），直接使用它
                if 输出路径.suffix:
                    输出文件 = 输出路径
                else:
                    # 从URL提取文件名，如果没有则使用默认名称
                    url_path = urlparse(输入文件).path
                    文件名 = Path(url_path).name if url_path else "output.json"
                    输出文件 = 输出路径 / 文件名
                    输出文件.parent.mkdir(parents=True, exist_ok=True)
            else:
                输出文件 = 输出路径 / 输入文件.name

            if 模式 == "get":
                if self.获取URL内容(str(输入文件), str(输出文件)):
                    成功计数 += 1
            elif 模式 == "enc":
                if self.加密文件(str(输入文件), str(输出文件)):
                    成功计数 += 1
            else:
                if self.解密文件(str(输入文件), str(输出文件)):
                    成功计数 += 1

        print(f"\n处理完成: 成功 {成功计数}/{len(文件列表)} 个文件")

def main():
    if len(sys.argv) < 3:
        print("用法:")
        print("  单个文件: python tvbox.py 输入文件/URL 输出文件 [模式]")
        print("  批量处理: python tvbox.py 输入目录/URL 输出目录 [模式] [--batch]")
        print("模式: enc-加密(默认) / dec-解密 / get-获取URL内容")
        print("说明: 支持本地文件和URL作为输入源")
        print("示例:")
        print("  本地文件加密: python tvbox.py api.json api.json")
        print("  本地文件解密: python tvbox.py api.json api.json dec")
        print("  URL获取: python tvbox.py https://example.com/data.txt output.json get")
        print("  URL解密: python tvbox.py https://example.com/encrypted.txt output.json dec")
        print("  批量加密: python tvbox.py input_dir output_dir enc --batch")
        print("  批量解密: python tvbox.py input_dir output_dir dec --batch")
        sys.exit(1)

    输入路径, 输出路径 = sys.argv[1], sys.argv[2]
    
    # 判断模式
    模式 = sys.argv[3] if len(sys.argv) > 3 else "enc"
    
    # 判断是否批量模式
    批量模式 = len(sys.argv) > 4 and sys.argv[4] == "--batch"
    
    加解密器 = 文件加解密器()

    # 自动判断是否为目录或URL
    输入是URL = 加解密器.是URL(输入路径)
    输入路径是目录 = os.path.isdir(输入路径) if not 输入是URL else False

    if 批量模式 or 输入路径是目录 or 输入是URL:
        加解密器.批量处理(输入路径, 输出路径, 模式)
    else:
        if 模式 == "enc":
            加解密器.加密文件(输入路径, 输出路径)
        else:
            加解密器.解密文件(输入路径, 输出路径)

if __name__ == "__main__":
    main()