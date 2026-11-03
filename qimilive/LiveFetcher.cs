using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Net;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;

// 便携版直播源获取器：双击即走 双节点配置 -> 最新ZIP -> 解密解压 -> 解析 -> 过滤广告 -> 生成 FongMi JSON
// 用法:
//   LiveConfig.exe                     自动从双节点获取最新配置与 ZIP
//   LiveConfig.exe <url>               从指定 URL 下载 (zip/txt)
//   LiveConfig.exe <本地文件.zip|txt>   直接解析本地文件
//   可选参数: -p <解压密码>  -kw <广告关键词,逗号分隔>  -o <输出json路径>
class Program
{
    const string ZIP_PASSWORD = "DBhkhdnefkhfq,#%";
    const string DEFAULT_EPG = "http://207.56.16.135:9999/tv/diyp.php?ch={name}&date={date}";
    static readonly string[] CONFIG_NODES = new string[] {
        "http://207.56.13.146:9999/qmtv/config.json",
        "http://qmtv.tvbus.cc/qmtv/config.json"
    };
    static readonly string[] AD_KEYWORDS = new string[] {
        "applive", "甄选", "好物", "福利", "会员专享", "今日推荐", "精品推荐", "优享",
        "养生馆", "严选", "银龄", "美好生活", "健康有约", "健康在线"
    };

    static string zipPass = ZIP_PASSWORD;
    static List<string> adKw = new List<string>(AD_KEYWORDS);
    static int filteredCount = 0;

    class Group { public string Name; public Dictionary<string, List<string>> Chs = new Dictionary<string, List<string>>(); }
    static List<Group> groups = new List<Group>();

    static int Main(string[] args)
    {
        Console.WriteLine("========================================================");
        Console.WriteLine("   直播源便携获取器 (TVBox/FongMi LiveConfig 生成)");
        Console.WriteLine("   双击运行: 自动获取最新配置 -> 下载ZIP -> 生成JSON");
        Console.WriteLine("========================================================");

        string target = null, outFile = null;
        for (int i = 0; i < args.Length; i++)
        {
            string a = args[i];
            if (a == "-p" && i + 1 < args.Length) zipPass = args[++i];
            else if (a == "-kw" && i + 1 < args.Length)
            {
                adKw = args[++i].Split(new[] { ',', '，', ' ' }, StringSplitOptions.RemoveEmptyEntries)
                                .Select(s => s.Trim().ToLowerInvariant()).Where(s => s.Length > 0).ToList();
            }
            else if (a == "-o" && i + 1 < args.Length) outFile = args[++i];
            else target = a;
        }
        if (outFile == null) outFile = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "sss.json");

        ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12 | SecurityProtocolType.Tls11 | SecurityProtocolType.Tls;
        try { Run(target, outFile); }
        catch (Exception ex) { Console.WriteLine("[失败] " + ex.Message); }
        Console.Write("\n按回车键退出...");
        Console.ReadLine();
        return 0;
    }

    static void Run(string target, string outFile)
    {
        string epg = DEFAULT_EPG;
        byte[] data = null;

        if (target != null && File.Exists(target))
        {
            Console.WriteLine("[本地] 加载文件: " + target);
            data = File.ReadAllBytes(target);
        }
        else if (target != null && Regex.IsMatch(target, @"^https?://", RegexOptions.IgnoreCase))
        {
            Console.WriteLine("[下载] " + target);
            data = HttpGetBytes(target);
        }
        else
        {
            // 双节点接力: 节点返回 source 后尝试下载, 失败则切下一个节点
            foreach (string node in CONFIG_NODES)
            {
                Console.WriteLine("[节点] " + node);
                string cfgText;
                try { cfgText = Encoding.UTF8.GetString(HttpGetBytes(node)); }
                catch (Exception ex) { Console.WriteLine("       节点失败: " + ex.Message); continue; }

                var mEpg = Regex.Match(cfgText, "\"epg\"\\s*:\\s*\"([^\"]+)\"");
                if (mEpg.Success) epg = JsonUnescape(mEpg.Groups[1].Value);
                var mApk = Regex.Match(cfgText, "\"apk\"\\s*:\\s*\"([^\"]+)\"");
                if (mApk.Success) Console.WriteLine("       APK更新地址: " + JsonUnescape(mApk.Groups[1].Value));

                var mSrc = Regex.Match(cfgText, "\"source\"\\s*:\\s*\"([^\"]+)\"");
                if (!mSrc.Success) { Console.WriteLine("       返回中无 source 字段"); continue; }
                string src = JsonUnescape(mSrc.Groups[1].Value);
                Console.WriteLine("       最新源: " + src);
                try { data = HttpGetBytes(src); break; }
                catch (Exception ex) { Console.WriteLine("       下载失败: " + ex.Message); }
            }
            if (data == null) throw new Exception("所有配置节点均不可用, 可将 ZIP/TXT 拖到本 EXE 上离线解析");
        }

        // 内容分发: ZIP / 文本
        List<KeyValuePair<string, byte[]>> files = new List<KeyValuePair<string, byte[]>>();
        if (data.Length > 4 && data[0] == 'P' && data[1] == 'K')
        {
            Console.WriteLine("[ZIP] 检测到压缩包, 开始解密解压 (密码: " + zipPass + ")");
            files = ReadZip(data);
            Console.WriteLine("[ZIP] 解出 " + files.Count + " 个文件: " +
                string.Join(", ", files.Select(f => f.Key).ToArray()));
        }
        else files.Add(new KeyValuePair<string, byte[]>("input.txt", data));

        foreach (var f in files)
        {
            string text = DecodeBytes(f.Value);
            if (text.TrimStart().StartsWith("[") || text.TrimStart().StartsWith("{")) IngestJson(text, f.Key);
            else if (text.TrimStart().StartsWith("#EXTM3U")) IngestM3u(text, f.Key);
            else IngestTxt(text, f.Key);
        }

        // 追加来源: 咕噜 APP 直播源 (协议加密, 失败不影响 qmtv 主流程)
        try { FetchGulu(); }
        catch (Exception gex) { Console.WriteLine("[咕噜] 获取失败(不影响主流程): " + gex.Message); }

        if (groups.Count == 0) throw new Exception("没有解析到任何频道");
        string json = BuildJson(epg);
        File.WriteAllText(outFile, json, new UTF8Encoding(false));

        int chTotal = groups.Sum(g => g.Chs.Count);
        int urlTotal = groups.Sum(g => g.Chs.Values.Sum(v => v.Count));
        int qmtvG = 0, qmtvC = 0, guluG = 0, guluC = 0;
        foreach (Group g in groups)
        {
            if (g.Name.StartsWith("咕噜·")) { guluG++; guluC += g.Chs.Count; }
            else { qmtvG++; qmtvC += g.Chs.Count; }
        }
        Console.WriteLine("\n--------------------------------------------------------");
        Console.WriteLine("总计 分组 " + groups.Count + " | 频道 " + chTotal + " | 线路 " + urlTotal + " | 已过滤广告 " + filteredCount);
        Console.WriteLine("qmtv 来源: 分组 " + qmtvG + " | 频道 " + qmtvC + "    咕噜来源: 分组 " + guluG + " | 频道 " + guluC);
        Console.WriteLine("EPG: " + epg);
        Console.WriteLine("已生成: " + outFile);
        Console.WriteLine("在 FongMi TV / 影视仓 中以本 JSON 文件作为直播配置导入即可");
        Console.WriteLine("--------------------------------------------------------");
    }

    // ==================== 网络与文本 ====================
    static byte[] HttpGetBytes(string url)
    {
        HttpWebRequest req = (HttpWebRequest)WebRequest.Create(url);
        req.UserAgent = "okhttp/3.12.0";
        req.Timeout = 20000;
        req.ReadWriteTimeout = 30000;
        req.AllowAutoRedirect = true;
        using (HttpWebResponse resp = (HttpWebResponse)req.GetResponse())
        using (var ms = new MemoryStream())
        using (var rs = resp.GetResponseStream())
        {
            byte[] buf = new byte[65536]; int n;
            while ((n = rs.Read(buf, 0, buf.Length)) > 0) ms.Write(buf, 0, n);
            Console.WriteLine("       下载成功: " + ms.Length + " 字节");
            return ms.ToArray();
        }
    }

    static string DecodeBytes(byte[] b)
    {
        try { return new UTF8Encoding(false, true).GetString(b); }
        catch { return Encoding.GetEncoding("gbk").GetString(b); }
    }

    // 还原 JSON 字符串转义: \/ -> / , \" -> " , \\ -> \ , \uXXXX -> 字符
    static string JsonUnescape(string s)
    {
        var sb = new StringBuilder();
        for (int i = 0; i < s.Length; i++)
        {
            if (s[i] != '\\' || i + 1 >= s.Length) { sb.Append(s[i]); continue; }
            char c = s[++i];
            switch (c)
            {
                case '/': sb.Append('/'); break;
                case '"': sb.Append('"'); break;
                case '\\': sb.Append('\\'); break;
                case 'n': sb.Append('\n'); break;
                case 'r': sb.Append('\r'); break;
                case 't': sb.Append('\t'); break;
                case 'u':
                    {
                        int cp;
                        if (i + 4 < s.Length && int.TryParse(s.Substring(i + 1, 4), System.Globalization.NumberStyles.HexNumber, null, out cp))
                        {
                            sb.Append((char)cp); i += 4;
                        }
                        else sb.Append(c);
                        break;
                    }
                default: sb.Append(c); break;
            }
        }
        return sb.ToString();
    }

    // ==================== ZIP: 解密 + 解压 ====================
    static List<KeyValuePair<string, byte[]>> ReadZip(byte[] buf)
    {
        int eocd = -1;
        for (int i = buf.Length - 22; i >= Math.Max(0, buf.Length - 65557); i--)
            if (buf[i] == 0x50 && buf[i + 1] == 0x4b && buf[i + 2] == 0x05 && buf[i + 3] == 0x06) { eocd = i; break; }
        if (eocd < 0) throw new Exception("ZIP 目录未找到");
        int count = BitConverter.ToUInt16(buf, eocd + 10);
        int p = (int)BitConverter.ToUInt32(buf, eocd + 16);
        var passBytes = Encoding.UTF8.GetBytes(zipPass);
        var result = new List<KeyValuePair<string, byte[]>>();

        for (int n = 0; n < count; n++)
        {
            if (p + 46 > buf.Length || BitConverter.ToUInt32(buf, p) != 0x02014b50) break;
            int flag = BitConverter.ToUInt16(buf, p + 8);
            int method = BitConverter.ToUInt16(buf, p + 10);
            int modTime = BitConverter.ToUInt16(buf, p + 12);
            uint crc = BitConverter.ToUInt32(buf, p + 16);
            int compSize = (int)BitConverter.ToUInt32(buf, p + 20);
            int nameLen = BitConverter.ToUInt16(buf, p + 28);
            int extraLen = BitConverter.ToUInt16(buf, p + 30);
            int cmtLen = BitConverter.ToUInt16(buf, p + 32);
            int loff = (int)BitConverter.ToUInt32(buf, p + 42);
            string name = Encoding.UTF8.GetString(buf, p + 46, nameLen);
            string enc = null;

            if (method == 99)   // WinZip AES: extra field 0x9901
            {
                bool found = false;
                for (int e = p + 30 + nameLen; e + 4 <= p + 30 + nameLen + extraLen; )
                {
                    int id = BitConverter.ToUInt16(buf, e); int sz = BitConverter.ToUInt16(buf, e + 2);
                    if (id == 0x9901)
                    {
                        method = BitConverter.ToUInt16(buf, e + 9);
                        enc = "aes:" + buf[e + 8]; found = true; break;
                    }
                    e += 4 + sz;
                }
                if (!found) { p += 46 + nameLen + extraLen + cmtLen; continue; }
            }
            else if ((flag & 1) != 0) enc = "zip";

            if (!name.EndsWith("/") && compSize > 0)
            {
                int dataStart = loff + 30 + BitConverter.ToUInt16(buf, loff + 26) + BitConverter.ToUInt16(buf, loff + 28);
                byte[] raw = Slice(buf, dataStart, compSize);
                try
                {
                    if (enc == "zip") raw = ZipCryptoDecrypt(raw, passBytes, (modTime >> 8) & 0xff, (int)((crc >> 24) & 0xff));
                    else if (enc != null && enc.StartsWith("aes")) raw = AesDecrypt(raw, passBytes, int.Parse(enc.Split(':')[1]));
                }
                catch (Exception ex) { throw new Exception("解密失败(" + name + "): " + ex.Message + " —— 检查解压密码"); }

                byte[] bytes;
                if (method == 0) bytes = raw;
                else if (method == 8) bytes = Inflate(raw);
                else { p += 46 + nameLen + extraLen + cmtLen; continue; }
                result.Add(new KeyValuePair<string, byte[]>(name, bytes));
            }
            p += 46 + nameLen + extraLen + cmtLen;
        }
        return result;
    }

    static byte[] Slice(byte[] src, int off, int len)
    {
        byte[] r = new byte[len]; Buffer.BlockCopy(src, off, r, 0, len); return r;
    }

    static byte[] Inflate(byte[] raw)
    {
        using (var ms = new MemoryStream(raw))
        using (var ds = new DeflateStream(ms, CompressionMode.Decompress))
        using (var outMs = new MemoryStream())
        {
            ds.CopyTo(outMs);
            return outMs.ToArray();
        }
    }

    // ---- PKWARE ZipCrypto ----
    static uint[] CRCT = BuildCrcTable();
    static uint[] BuildCrcTable()
    {
        var t = new uint[256];
        for (uint n = 0; n < 256; n++)
        {
            uint c = n;
            for (int k = 0; k < 8; k++) c = ((c & 1) != 0) ? (0xEDB88320 ^ (c >> 1)) : (c >> 1);
            t[n] = c;
        }
        return t;
    }
    static void ZcUpd(uint[] k, byte b)
    {
        k[0] = (k[0] >> 8) ^ CRCT[(k[0] ^ b) & 0xff];
        k[1] = unchecked(k[1] + (k[0] & 0xff));
        k[1] = unchecked(k[1] * 134775813 + 1);
        k[2] = (k[2] >> 8) ^ CRCT[(k[2] ^ (byte)(k[1] >> 24)) & 0xff];
    }
    static byte[] ZipCryptoDecrypt(byte[] data, byte[] pw, int chk1, int chk2)
    {
        if (pw == null || pw.Length == 0) throw new Exception("ZIP 已加密, 请用 -p 提供解压密码");
        uint[] k = { 0x12345678, 0x23456789, 0x34567890 };
        foreach (byte b in pw) ZcUpd(k, b);
        byte[] outB = new byte[data.Length];
        for (int i = 0; i < data.Length; i++)
        {
            ushort t = (ushort)((k[2] | 2) & 0xffff);
            byte plain = (byte)(data[i] ^ (byte)(((t * (t ^ 1)) >> 8) & 0xff));
            outB[i] = plain;
            ZcUpd(k, plain);
        }
        if (outB.Length >= 12 && outB[11] != chk1 && outB[11] != chk2) throw new Exception("密码校验不通过");
        byte[] res = new byte[outB.Length - 12]; Buffer.BlockCopy(outB, 12, res, 0, res.Length);
        return res;  // 前 12 字节为加密头
    }

    // ---- WinZip AES (zip4j 兼容: PBKDF2-SHA1 1000 轮 + AES-CTR, 计数器从 1 开始) ----
    static byte[] AesDecrypt(byte[] data, byte[] pw, int strength)
    {
        int keyLen = strength == 1 ? 16 : strength == 2 ? 24 : 32;
        int saltLen = strength == 1 ? 8 : strength == 2 ? 12 : 16;
        if (data.Length < saltLen + 2) throw new Exception("数据过短");
        byte[] salt = Slice(data, 0, saltLen);
        byte[] payload = Slice(data, saltLen + 2, data.Length - saltLen - 2);
        using (var pbkdf2 = new Rfc2898DeriveBytes(pw, salt, 1000, HashAlgorithmName.SHA1))
        {
            byte[] bits = pbkdf2.GetBytes(keyLen + 16 + 2);   // key + macKey + iv + pvv
            byte[] aesKey = Slice(bits, 0, keyLen);
            byte[] iv = Slice(bits, keyLen, 16);
            using (var aes = Aes.Create())
            {
                aes.Key = aesKey; aes.Mode = CipherMode.ECB; aes.Padding = PaddingMode.None;
                using (var enc = aes.CreateEncryptor())
                {
                    byte[] outB = new byte[payload.Length];
                    byte[] counter = new byte[16];
                    for (int off = 0, blockIdx = 1; off < payload.Length; off += 16, blockIdx++)
                    {
                        // 16 字节大端计数器, 从 1 开始
                        uint lo = (uint)blockIdx;
                        counter[15] = (byte)(lo & 0xff); counter[14] = (byte)((lo >> 8) & 0xff);
                        counter[13] = (byte)((lo >> 16) & 0xff); counter[12] = (byte)((lo >> 24) & 0xff);
                        byte[] ks = enc.TransformFinalBlock(counter, 0, 16);
                        int n = Math.Min(16, payload.Length - off);
                        for (int i = 0; i < n; i++) outB[off + i] = (byte)(payload[off + i] ^ ks[i]);
                    }
                    return outB;
                }
            }
        }
    }

    // ==================== 解析: TXT / M3U / JSON ====================
    static void AddCh(string groupName, string chName, List<string> urls)
    {
        string hay = (chName + " " + string.Join(" ", urls.ToArray())).ToLowerInvariant();
        foreach (string kw in adKw)
            if (hay.Contains(kw)) { filteredCount++; return; }
        Group g = groups.FirstOrDefault(x => x.Name == groupName);
        if (g == null) { g = new Group { Name = groupName }; groups.Add(g); }
        List<string> lst;
        if (!g.Chs.TryGetValue(chName, out lst)) { lst = new List<string>(); g.Chs[chName] = lst; }
        foreach (string u in urls) if (!lst.Contains(u)) lst.Add(u);
    }

    static void IngestTxt(string text, string srcName)
    {
        string cur = "未分组"; int n = 0;
        foreach (string rawLine in text.Split(new[] { "\r\n", "\n" }, StringSplitOptions.None))
        {
            string line = rawLine.Trim();
            if (line.Length == 0 || line.StartsWith("#")) continue;
            if (Regex.IsMatch(line, "#genre#", RegexOptions.IgnoreCase))
            {
                cur = line.Split(',')[0].Replace("#genre#", "").Replace("#GENRE#", "").Trim();
                if (cur.Length == 0) cur = "未分组";
                continue;
            }
            int ci = line.IndexOf(',');
            if (ci < 1) continue;
            string ch = line.Substring(0, ci).Trim();
            List<string> urls = line.Substring(ci + 1).Split('#').Select(s => s.Trim()).Where(s => s.Length > 0).ToList();
            if (ch.Length > 0 && urls.Count > 0) { AddCh(cur, ch, urls); n++; }
        }
        Console.WriteLine("[" + srcName + "] TXT 解析: " + n + " 个频道");
    }

    static void IngestM3u(string text, string srcName)
    {
        string cur = "未分组", name = ""; int n = 0;
        foreach (string rawLine in text.Split(new[] { "\r\n", "\n" }, StringSplitOptions.None))
        {
            string line = rawLine.Trim();
            if (line.Length == 0) continue;
            if (line.StartsWith("#EXTINF"))
            {
                var g = Regex.Match(line, "group-title=\"([^\"]*)\"", RegexOptions.IgnoreCase);
                cur = g.Success && g.Groups[1].Value.Length > 0 ? g.Groups[1].Value : "未分组";
                int li = line.LastIndexOf(',');
                name = li >= 0 ? line.Substring(li + 1).Trim() : "";
                continue;
            }
            if (line.StartsWith("#")) continue;
            if (name.Length > 0 && Regex.IsMatch(line, "^https?://", RegexOptions.IgnoreCase))
            {
                AddCh(cur, name, new List<string> { line }); n++; name = "";
            }
        }
        Console.WriteLine("[" + srcName + "] M3U 解析: " + n + " 个频道");
    }

    static void IngestJson(string text, string srcName)
    {
        object data;
        try { data = new JavaScriptSerializer().DeserializeObject(text); }
        catch (Exception ex) { Console.WriteLine("[" + srcName + "] JSON 解析失败: " + ex.Message); return; }
        int n = JsonWalk(data);
        Console.WriteLine("[" + srcName + "] JSON 解析: " + n + " 个频道");
    }

    static int JsonWalk(object data)
    {
        int n = 0;
        var list = data as object[];
        var dict = data as Dictionary<string, object>;
        if (list != null) { foreach (object g in list) n += WalkGroup(g); return n; }
        if (dict != null)
        {
            if (dict.ContainsKey("lives") && dict["lives"] is object[])
            {
                foreach (object l in (object[])dict["lives"])
                {
                    var ld = l as Dictionary<string, object>; if (ld == null) continue;
                    object gs;
                    if (ld.TryGetValue("groups", out gs) && gs is object[]) n += JsonWalk(gs);
                    else
                    {
                        object chs; object gname;
                        ld.TryGetValue("name", out gname); if (gname == null) ld.TryGetValue("group", out gname);
                        if (ld.TryGetValue("channels", out chs) && chs is object[])
                        {
                            var wrap = new Dictionary<string, object>();
                            wrap["name"] = gname; wrap["channel"] = chs;
                            n += WalkGroup(wrap);
                        }
                    }
                }
                return n;
            }
            if (dict.ContainsKey("groups")) return JsonWalk(dict["groups"]);
        }
        return n;
    }

    static int WalkGroup(object gObj)
    {
        var g = gObj as Dictionary<string, object>; if (g == null) return 0;
        object tmp;
        string gName = "未分组";
        if (g.TryGetValue("name", out tmp) && tmp is string) gName = (string)tmp;
        else if (g.TryGetValue("group", out tmp) && tmp is string) gName = (string)tmp;
        int n = 0;
        object chans = null;
        if (!g.TryGetValue("channel", out chans)) g.TryGetValue("channels", out chans);
        var chList = chans as object[]; if (chList == null) return 0;
        foreach (object cObj in chList)
        {
            var c = cObj as Dictionary<string, object>; if (c == null) continue;
            object nameObj, urlsObj;
            if (!c.TryGetValue("name", out nameObj) || !(nameObj is string)) continue;
            var urls = new List<string>();
            if (c.TryGetValue("urls", out urlsObj) && urlsObj is object[])
                foreach (object u in (object[])urlsObj)
                {
                    if (u is string) urls.Add((string)u);
                    else { var ud = u as Dictionary<string, object>; object uu; if (ud != null && ud.TryGetValue("url", out uu) && uu is string) urls.Add((string)uu); }
                }
            if (urls.Count > 0) { AddCh(gName, (string)nameObj, urls); n++; }
        }
        return n;
    }

    // ==================== 咕噜 APP 直播源 (移植自 MyTv GuluClient.java) ====================
    static void FetchGulu()
    {
        Console.WriteLine("\n[咕噜] 拉取 咕噜APP 直播源: " + GuluClient.ENDPOINT);
        string did = GuluCrypto.RandomHex(8);   // 16 位 hex deviceId
        GuluClient client = new GuluClient(did);
        client.Handshake();
        Console.WriteLine("[咕噜] 握手成功 session=" + Brief(client.Session, 24));
        client.Boot();
        Console.WriteLine("[咕噜] 设备注册 code=0 deviceId=" + did);
        GuluClient.Resp resp = client.Request(3, 76, new byte[0]);   // 直播列表
        if (resp.code != 0) throw new Exception("直播列表 code=" + resp.code + " " + resp.msg);
        Console.WriteLine("[咕噜] 直播列表 code=0 data=" + (resp.data == null ? 0 : resp.data.Length) + " 字节");
        List<GuluClient.LiveCh> chs = GuluClient.ParseLive(resp.data);
        foreach (GuluClient.LiveCh ch in chs)
            AddCh("咕噜·" + ch.group, ch.name, new List<string> { ch.url });
        int gg = 0, gc = 0, gu = 0;
        foreach (Group g in groups)
            if (g.Name.StartsWith("咕噜·"))
            {
                gg++; gc += g.Chs.Count;
                foreach (List<string> v in g.Chs.Values) gu += v.Count;
            }
        Console.WriteLine("[咕噜] 入库: 分组 " + gg + " | 频道 " + gc + " | 线路 " + gu);
    }

    static string Brief(string s, int n)
    {
        if (string.IsNullOrEmpty(s)) return "";
        return s.Length <= n ? s : s.Substring(0, n) + "...";
    }

    // ==================== 生成 FongMi LiveConfig JSON ====================
    static string Esc(string s)
    {
        var sb = new StringBuilder();
        foreach (char c in s)
        {
            switch (c)
            {
                case '"': sb.Append("\\\""); break;
                case '\\': sb.Append("\\\\"); break;
                case '\b': sb.Append("\\b"); break;
                case '\f': sb.Append("\\f"); break;
                case '\n': sb.Append("\\n"); break;
                case '\r': sb.Append("\\r"); break;
                case '\t': sb.Append("\\t"); break;
                default:
                    if (c < ' ') sb.Append("\\u").Append(((int)c).ToString("x4"));
                    else sb.Append(c);
                    break;
            }
        }
        return sb.ToString();
    }

    static string BuildJson(string epg)
    {
        var sb = new StringBuilder();
        sb.Append("{\n  \"lives\": [{\n");
        sb.Append("    \"name\": \"直播\",\n");
        if (!string.IsNullOrEmpty(epg)) sb.Append("    \"epg\": \"").Append(Esc(epg)).Append("\",\n");
        sb.Append("    \"groups\": [");
        bool firstGroup = true;
        foreach (Group g in groups)
        {
            if (!firstGroup) sb.Append(",");
            firstGroup = false;
            sb.Append("\n      {\n        \"name\": \"").Append(Esc(g.Name)).Append("\",\n        \"channel\": [");
            bool firstCh = true;
            foreach (var kv in g.Chs)
            {
                if (!firstCh) sb.Append(",");
                firstCh = false;
                sb.Append("\n          {\n            \"name\": \"").Append(Esc(kv.Key)).Append("\",\n            \"urls\": [");
                bool firstUrl = true;
                foreach (string u in kv.Value)
                {
                    if (!firstUrl) sb.Append(",");
                    firstUrl = false;
                    sb.Append("\n              \"").Append(Esc(u)).Append("\"");
                }
                sb.Append("\n            ]\n          }");
            }
            sb.Append("\n        ]\n      }");
        }
        sb.Append("\n    ]\n  }]\n}");
        return sb.ToString();
    }
}

// ==================== 咕噜 APP 协议: 极简 protobuf (移植自 MyTv GuluProto.java) ====================
static class GuluProto
{
    public static byte[] Vint(long n)
    {
        ulong v = (ulong)n;
        using (var o = new MemoryStream())
        {
            do
            {
                uint b = (uint)(v & 0x7f);
                v >>= 7;
                if (v != 0) b |= 0x80u;
                o.WriteByte((byte)b);
            } while (v != 0);
            return o.ToArray();
        }
    }

    public static byte[] Tag(int field, int wire) { return Vint((long)(((ulong)(uint)field << 3) | ((ulong)(uint)wire))); }
    public static byte[] V(int f, long val) { return Concat(Tag(f, 0), Vint(val)); }
    public static byte[] S(int f, string str) { byte[] b = Encoding.UTF8.GetBytes(str); return Concat(Tag(f, 2), Concat(Vint(b.Length), b)); }
    public static byte[] B(int f, byte[] bytes) { if (bytes == null) bytes = new byte[0]; return Concat(Tag(f, 2), Concat(Vint(bytes.Length), bytes)); }
    public static byte[] M(int f, byte[] msg) { return B(f, msg); }

    public static byte[] Slice(byte[] src, int off, int len)
    {
        if (src == null || off >= src.Length || len <= 0) return new byte[0];
        if (off < 0) off = 0;
        if (off + len > src.Length) len = src.Length - off;
        byte[] outB = new byte[len];
        Buffer.BlockCopy(src, off, outB, 0, len);
        return outB;
    }

    public static byte[] Concat(params byte[][] arrs)
    {
        int n = 0;
        foreach (byte[] a in arrs) n += a.Length;
        byte[] t = new byte[n];
        int o = 0;
        foreach (byte[] a in arrs) { Buffer.BlockCopy(a, 0, t, o, a.Length); o += a.Length; }
        return t;
    }

    // 单个解码后的 protobuf 字段
    public class F
    {
        public int f;      // 字段号
        public int w;      // wire type
        public long vi;    // wire=0 时的 varint 值
        public byte[] bb;  // wire=2 时的原始字节
        public F(int f, int w, long vi, byte[] bb) { this.f = f; this.w = w; this.vi = vi; this.bb = bb; }
    }

    public static List<F> Decode(byte[] b)
    {
        var outL = new List<F>();
        int i = 0;
        while (i < b.Length)
        {
            long[] t = ReadVint(b, i);
            i = (int)t[1];
            int f = (int)(t[0] >> 3);
            int w = (int)(t[0] & 7);
            if (f == 0) throw new Exception("bad field 0");
            if (w == 0)
            {
                long[] r = ReadVint(b, i);
                i = (int)r[1];
                outL.Add(new F(f, w, r[0], null));
            }
            else if (w == 1)
            {
                if (i + 8 > b.Length) throw new Exception("truncated");
                outL.Add(new F(f, w, 0, Slice(b, i, 8)));
                i += 8;
            }
            else if (w == 2)
            {
                long[] l = ReadVint(b, i);
                i = (int)l[1];
                int len = (int)l[0];
                if (len < 0 || i + len > b.Length) throw new Exception("truncated");
                outL.Add(new F(f, w, 0, Slice(b, i, len)));
                i += len;
            }
            else if (w == 5)
            {
                if (i + 4 > b.Length) throw new Exception("truncated");
                outL.Add(new F(f, w, 0, Slice(b, i, 4)));
                i += 4;
            }
            else throw new Exception("bad wire " + w);
        }
        return outL;
    }

    static long[] ReadVint(byte[] b, int o)
    {
        long r = 0; int s = 0; int i = o;
        for (; ; )
        {
            if (i >= b.Length) throw new Exception("truncated varint");
            int x = b[i++];
            r |= (long)(x & 0x7f) << s;
            if ((x & 0x80) == 0) return new long[] { r, i };
            s += 7;
        }
    }

    public static F Find(List<F> fs, int field, int wire)
    {
        if (fs == null) return null;
        foreach (F x in fs) if (x.f == field && x.w == wire) return x;
        return null;
    }

    public static List<F> All(List<F> fs, int field)
    {
        var outL = new List<F>();
        if (fs == null) return outL;
        foreach (F x in fs) if (x.f == field) outL.Add(x);
        return outL;
    }

    // 严格 UTF-8 且无控制字符才视为可读文本
    public static string LooksText(byte[] b)
    {
        if (b == null || b.Length == 0) return null;
        string s;
        try { s = new UTF8Encoding(false, true).GetString(b); }
        catch { return null; }
        foreach (char c in s)
            if ((c >= 0x00 && c <= 0x08) || c == 0x0b || c == 0x0c || (c >= 0x0e && c <= 0x1f)) return null;
        return s;
    }

    public static string Text(F x) { return (x != null && x.w == 2) ? LooksText(x.bb) : null; }
}

// ==================== 咕噜 APP 协议: 加密套件 (移植自 MyTv GuluCrypto.java) ====================
// ECDH P-256 手写点乘 + AES-256-CBC/GCM 手写 + HMAC-SHA256 + zlib(裸 deflate 加头尾包装)
static class GuluCrypto
{
    static readonly RandomNumberGenerator Rng = RandomNumberGenerator.Create();

    // P-256 (secp256r1) 域参数
    static readonly BigInteger P = Big("ffffffff00000001000000000000000000000000ffffffffffffffffffffffff");
    static readonly BigInteger A = P - 3;
    static readonly BigInteger Gx = Big("6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296");
    static readonly BigInteger Gy = Big("4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5");
    static readonly BigInteger N = Big("ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551");

    public static byte[] RandomBytes(int n) { byte[] b = new byte[n]; Rng.GetBytes(b); return b; }
    public static string RandomHex(int nBytes) { var sb = new StringBuilder(); foreach (byte x in RandomBytes(nBytes)) sb.Append(x.ToString("x2")); return sb.ToString(); }

    // ---------------- 字节序: 大端无符号 <-> BigInteger ----------------
    static BigInteger Big(string hex)
    {
        byte[] be = new byte[hex.Length / 2];
        for (int i = 0; i < be.Length; i++) be[i] = Convert.ToByte(hex.Substring(i * 2, 2), 16);
        return FromBE(be);
    }

    static BigInteger FromBE(byte[] be)
    {
        byte[] le = new byte[be.Length + 1];
        for (int i = 0; i < be.Length; i++) le[i] = be[be.Length - 1 - i];
        le[be.Length] = 0;   // 保证正数
        return new BigInteger(le);
    }

    // 取 32 字节大端表示 (高位补零), 与 Java pad32/ecdhSecret 归一化一致
    static byte[] ToBE32(BigInteger v)
    {
        byte[] tmp = v.ToByteArray();   // 小端, 可能带符号 0x00
        int tlen = tmp.Length;
        while (tlen > 1 && tmp[tlen - 1] == 0) tlen--;
        byte[] outB = new byte[32];
        int n = Math.Min(tlen, 32);
        for (int i = 0; i < n; i++) outB[31 - i] = tmp[i];
        return outB;
    }

    // ---------------- zlib ----------------

    // 握手压缩: zlib 包装 = 0x78 0x9C + 裸 deflate + adler32(原文)
    public static byte[] DeflateZlib(byte[] data)
    {
        byte[] raw = RawDeflate(data);
        byte[] outB = new byte[raw.Length + 6];
        outB[0] = 0x78; outB[1] = 0x9c;
        Buffer.BlockCopy(raw, 0, outB, 2, raw.Length);
        uint ad = Adler32(data);
        outB[outB.Length - 4] = (byte)(ad >> 24);
        outB[outB.Length - 3] = (byte)(ad >> 16);
        outB[outB.Length - 2] = (byte)(ad >> 8);
        outB[outB.Length - 1] = (byte)ad;
        return outB;
    }

    // 握手解压: 剥 zlib 头尾 + 裸 inflate
    public static byte[] InflateZlib(byte[] data)
    {
        if (data.Length < 6) throw new Exception("zlib 数据过短");
        return RawInflate(GuluProto.Slice(data, 2, data.Length - 6));
    }

    public static byte[] RawDeflate(byte[] data)
    {
        using (var ms = new MemoryStream())
        {
            using (var ds = new DeflateStream(ms, CompressionMode.Compress))
            {
                ds.Write(data, 0, data.Length);
            }
            return ms.ToArray();
        }
    }

    public static byte[] RawInflate(byte[] data)
    {
        using (var ms = new MemoryStream(data))
        using (var ds = new DeflateStream(ms, CompressionMode.Decompress))
        using (var outMs = new MemoryStream())
        {
            ds.CopyTo(outMs);
            return outMs.ToArray();
        }
    }

    static uint Adler32(byte[] data)
    {
        uint a = 1, b = 0;
        foreach (byte x in data)
        {
            a = (a + x) % 65521;
            b = (b + a) % 65521;
        }
        return (b << 16) | a;
    }

    // ---------------- ECDH P-256 (手写点乘, .NET Framework 拿不到裸 X 坐标共享密钥) ----------------

    // 生成密钥对: 返回 65B 非压缩公钥 0x04||X||Y, 私钥经 out 带出
    public static byte[] EcNewKeyPair(out BigInteger priv)
    {
        byte[] buf = new byte[32];
        Rng.GetBytes(buf);
        priv = FromBE(buf) % (N - 1) + 1;
        BigInteger[] pub = EcMul(priv, new BigInteger[] { Gx, Gy });
        byte[] out65 = new byte[65];
        out65[0] = 4;
        Buffer.BlockCopy(ToBE32(pub[0]), 0, out65, 1, 32);
        Buffer.BlockCopy(ToBE32(pub[1]), 0, out65, 33, 32);
        return out65;
    }

    // ECDH 共享密钥 = 共享点 X 坐标, 32B 大端高位补零
    public static byte[] EcShared(BigInteger priv, byte[] peerRaw65)
    {
        if (peerRaw65 == null || peerRaw65.Length != 65 || peerRaw65[0] != 4) throw new Exception("无效的 EC 公钥");
        BigInteger x = FromBE(GuluProto.Slice(peerRaw65, 1, 32));
        BigInteger y = FromBE(GuluProto.Slice(peerRaw65, 33, 32));
        BigInteger[] p = EcMul(priv, new BigInteger[] { x, y });
        if (p == null) throw new Exception("ECDH 得到无穷远点");
        return ToBE32(p[0]);
    }

    static BigInteger EcMod(BigInteger v) { BigInteger r = v % P; return r.Sign >= 0 ? r : r + P; }

    static BigInteger EcInv(BigInteger v) { return BigInteger.ModPow(EcMod(v), P - 2, P); }

    // 仿射点加/倍点, null = 无穷远点
    static BigInteger[] EcAdd(BigInteger[] p1, BigInteger[] p2)
    {
        if (p1 == null) return p2;
        if (p2 == null) return p1;
        BigInteger x1 = p1[0], y1 = p1[1], x2 = p2[0], y2 = p2[1];
        if (x1 == x2)
        {
            if (EcMod(y1 + y2) == BigInteger.Zero) return null;
            BigInteger lam = EcMod(EcMod(3 * x1 * x1 + A) * EcInv(EcMod(2 * y1)));
            BigInteger x3 = EcMod(lam * lam - 2 * x1);
            BigInteger y3 = EcMod(lam * (x1 - x3) - y1);
            return new BigInteger[] { x3, y3 };
        }
        BigInteger l = EcMod(EcMod(y2 - y1) * EcInv(EcMod(x2 - x1)));
        BigInteger xr = EcMod(l * l - x1 - x2);
        BigInteger yr = EcMod(l * (x1 - xr) - y1);
        return new BigInteger[] { xr, yr };
    }

    // 双加标量乘
    static BigInteger[] EcMul(BigInteger k, BigInteger[] pt)
    {
        BigInteger[] r = null;
        BigInteger[] add = pt;
        while (k.Sign > 0)
        {
            if (!k.IsEven) r = EcAdd(r, add);
            add = EcAdd(add, add);
            k >>= 1;
        }
        return r;
    }

    // ---------------- HMAC / AES ----------------

    public static byte[] HmacSha256(byte[] key, byte[] msg)
    {
        using (var h = new HMACSHA256(key)) return h.ComputeHash(msg);
    }

    public static byte[] AesCbcEncrypt(byte[] key, byte[] iv, byte[] plain)
    {
        using (var aes = Aes.Create())
        {
            aes.Key = key; aes.IV = iv; aes.Mode = CipherMode.CBC; aes.Padding = PaddingMode.PKCS7;
            using (var enc = aes.CreateEncryptor()) return enc.TransformFinalBlock(plain, 0, plain.Length);
        }
    }

    public static byte[] AesCbcDecrypt(byte[] key, byte[] iv, byte[] ct)
    {
        using (var aes = Aes.Create())
        {
            aes.Key = key; aes.IV = iv; aes.Mode = CipherMode.CBC; aes.Padding = PaddingMode.PKCS7;
            using (var dec = aes.CreateDecryptor()) return dec.TransformFinalBlock(ct, 0, ct.Length);
        }
    }

    // ---------------- AES-256-GCM (12B nonce, 128b tag, 无 AAD; .NET Framework 无 AesGcm, 手写 GHASH+CTR) ----------------

    public static byte[] AesGcmEncrypt(byte[] key, byte[] nonce, byte[] plain)
    {
        using (var aes = Aes.Create())
        {
            aes.Key = key; aes.Mode = CipherMode.ECB; aes.Padding = PaddingMode.None;
            using (var enc = aes.CreateEncryptor())
            {
                byte[] h = AesBlock(enc, new byte[16]);
                byte[] j0 = J0(nonce);
                byte[] ct = GcmCtr(enc, j0, plain);
                byte[] s = Ghash(h, ct);
                byte[] mask = AesBlock(enc, j0);
                byte[] outB = new byte[ct.Length + 16];
                Buffer.BlockCopy(ct, 0, outB, 0, ct.Length);
                for (int i = 0; i < 16; i++) outB[ct.Length + i] = (byte)(s[i] ^ mask[i]);
                return outB;
            }
        }
    }

    public static byte[] AesGcmDecrypt(byte[] key, byte[] nonce, byte[] ctWithTag)
    {
        if (ctWithTag.Length < 16) throw new Exception("GCM 密文过短");
        int ctLen = ctWithTag.Length - 16;
        byte[] ct = GuluProto.Slice(ctWithTag, 0, ctLen);
        byte[] tag = GuluProto.Slice(ctWithTag, ctLen, 16);
        using (var aes = Aes.Create())
        {
            aes.Key = key; aes.Mode = CipherMode.ECB; aes.Padding = PaddingMode.None;
            using (var enc = aes.CreateEncryptor())
            {
                byte[] h = AesBlock(enc, new byte[16]);
                byte[] j0 = J0(nonce);
                byte[] s = Ghash(h, ct);
                byte[] mask = AesBlock(enc, j0);
                for (int i = 0; i < 16; i++)
                    if (tag[i] != (byte)(s[i] ^ mask[i])) throw new Exception("GCM 校验失败");
                return GcmCtr(enc, j0, ct);
            }
        }
    }

    static byte[] J0(byte[] nonce)
    {
        byte[] j0 = new byte[16];
        Buffer.BlockCopy(nonce, 0, j0, 0, 12);
        j0[15] = 1;
        return j0;
    }

    static byte[] AesBlock(ICryptoTransform enc, byte[] block)
    {
        byte[] outB = new byte[16];
        enc.TransformBlock(block, 0, 16, outB, 0);
        return outB;
    }

    // GHASH(仅密文, AAD 恒为空)
    static byte[] Ghash(byte[] h, byte[] ct)
    {
        int padC = (16 - ct.Length % 16) % 16;
        byte[] all = new byte[ct.Length + padC + 16];
        Buffer.BlockCopy(ct, 0, all, 0, ct.Length);
        ulong cBits = (ulong)ct.Length * 8;
        for (int i = 0; i < 8; i++) all[all.Length - 8 + i] = (byte)(cBits >> (56 - 8 * i));
        byte[] y = new byte[16];
        for (int off = 0; off < all.Length; off += 16)
        {
            for (int i = 0; i < 16; i++) y[i] ^= all[off + i];
            y = GfMul(y, h);
        }
        return y;
    }

    // GF(2^128) 乘法, R = 0xE1 << 120
    static byte[] GfMul(byte[] x, byte[] y)
    {
        byte[] z = new byte[16];
        byte[] v = (byte[])y.Clone();
        for (int i = 0; i < 128; i++)
        {
            if ((x[i >> 3] & (0x80 >> (i & 7))) != 0)
                for (int k = 0; k < 16; k++) z[k] ^= v[k];
            bool lsb = (v[15] & 1) != 0;
            for (int k = 15; k > 0; k--) v[k] = (byte)((v[k] >> 1) | ((v[k - 1] & 1) << 7));
            v[0] >>= 1;
            if (lsb) v[0] ^= 0xe1;
        }
        return z;
    }

    static void Inc32(byte[] ctr)
    {
        for (int i = 15; i >= 12; i--)
        {
            ctr[i]++;
            if (ctr[i] != 0) break;
        }
    }

    static byte[] GcmCtr(ICryptoTransform enc, byte[] j0, byte[] data)
    {
        byte[] outB = new byte[data.Length];
        byte[] ctr = (byte[])j0.Clone();
        for (int off = 0; off < data.Length; off += 16)
        {
            Inc32(ctr);
            byte[] ks = AesBlock(enc, ctr);
            int n = Math.Min(16, data.Length - off);
            for (int i = 0; i < n; i++) outB[off + i] = (byte)(data[off + i] ^ ks[i]);
        }
        return outB;
    }
}

// ==================== 咕噜 APP 协议: 客户端 (移植自 MyTv GuluClient.java) ====================
// 链路: ECDH 握手 -> 设备注册(boot, 免登录) -> 直播列表 cat=3 m=76
class GuluClient
{
    public const string ENDPOINT = "http://103.45.132.22:19987/app/bn/v2";
    const string TAG_VERSION = "1.0.0";
    const long CODE_CLOCK = 10002;   // 时钟偏移被拒, 重同步后重试一次

    public readonly string DeviceId;   // 16 位 hex
    public string Session;
    public byte[] SessionKey;
    long seq = 1;
    long clockOffset = 0;

    public GuluClient(string deviceId) { DeviceId = deviceId; }

    // ECDH 握手: pb{1:pub,2:"1.0.0",3:{1:0,2:1,3:1}} -> zlib -> IV||AES-CBC -> base64(IV||CT)
    public void Handshake()
    {
        BigInteger priv;
        byte[] pub = GuluCrypto.EcNewKeyPair(out priv);
        string hsKeyHex = GuluCrypto.RandomHex(16);
        byte[] hsKey = Encoding.UTF8.GetBytes(hsKeyHex);   // 32 位 hex 字符串的 UTF-8 32 字节作 AES-256 key

        byte[] cap = GuluProto.V(1, 0);
        cap = GuluProto.Concat(cap, GuluProto.V(2, 1), GuluProto.V(3, 1));
        byte[] payload = GuluProto.B(1, pub);
        payload = GuluProto.Concat(payload, GuluProto.S(2, TAG_VERSION), GuluProto.M(3, cap));

        byte[] zipped = GuluCrypto.DeflateZlib(payload);
        byte[] iv = GuluCrypto.RandomBytes(16);
        byte[] ct = GuluCrypto.AesCbcEncrypt(hsKey, iv, zipped);
        byte[] body = Encoding.UTF8.GetBytes(Convert.ToBase64String(GuluProto.Concat(iv, ct)));

        var headers = new Dictionary<string, string>();
        headers["X-Handshake-Key"] = hsKeyHex;
        byte[] resp = HttpPost(body, headers);

        // 响应 base64 -> IV||CT -> CBC 解密 -> inflate -> pb{1:session, 2:服务器 65B 公钥}
        byte[] bin = Convert.FromBase64String(Encoding.UTF8.GetString(resp).Trim());
        byte[] plain = GuluCrypto.InflateZlib(GuluCrypto.AesCbcDecrypt(hsKey,
            GuluProto.Slice(bin, 0, 16), GuluProto.Slice(bin, 16, bin.Length - 16)));
        List<GuluProto.F> msg = GuluProto.Decode(plain);
        GuluProto.F sess = GuluProto.Find(msg, 1, 2);
        GuluProto.F spub = GuluProto.Find(msg, 2, 2);
        if (sess == null || spub == null || spub.bb.Length != 65 || spub.bb[0] != 4)
            throw new Exception("握手响应结构异常");

        Session = Encoding.UTF8.GetString(sess.bb);
        // 派生: secret32 -> prk=HMAC(key=sessionUTF8, msg=secret32) -> sessionKey=HMAC(prk, "v2-session"||0x01)
        byte[] secret = GuluCrypto.EcShared(priv, spub.bb);
        byte[] prk = GuluCrypto.HmacSha256(Encoding.UTF8.GetBytes(Session), secret);
        SessionKey = GuluCrypto.HmacSha256(prk, GuluProto.Concat(Encoding.UTF8.GetBytes("v2-session"), new byte[] { 1 }));
    }

    // 设备注册 (免登录关键): cat=1 m=0, 握手成功后必须立即调用
    public void Boot()
    {
        Resp r = Request(1, 0, BuildBootPayload(DeviceId));
        if (r.code != 0) throw new Exception("设备注册失败 code=" + r.code + " " + r.msg);
    }

    // envelope{1:seq,2:cat,3:method,4:deviceId,5:空,6:payload,7:毫秒时间戳}
    public Resp Request(int cat, int method, byte[] payload)
    {
        if (Session == null || SessionKey == null) Handshake();
        Resp outR = SendOnce(cat, method, payload);
        if (outR.code == CODE_CLOCK) outR = SendOnce(cat, method, payload);   // 时钟重同步后重试一次
        return outR;
    }

    Resp SendOnce(int cat, int method, byte[] payload)
    {
        long sq = seq++;
        byte[] env = GuluProto.V(1, sq);
        env = GuluProto.Concat(env, GuluProto.V(2, cat), GuluProto.V(3, method),
            GuluProto.B(4, Encoding.UTF8.GetBytes(DeviceId)));
        env = GuluProto.Concat(env, GuluProto.B(5, new byte[0]));
        env = GuluProto.Concat(env, GuluProto.B(6, payload));
        env = GuluProto.Concat(env, GuluProto.V(7,
            (long)(DateTime.UtcNow - new DateTime(1970, 1, 1)).TotalMilliseconds + clockOffset));

        byte[] z = GuluCrypto.RawDeflate(env);
        byte[] nonce = GuluCrypto.RandomBytes(12);
        byte[] ct = GuluCrypto.AesGcmEncrypt(SessionKey, nonce, z);
        byte[] body = GuluProto.Concat(GuluProto.V(1, sq), GuluProto.B(2, GuluProto.Concat(nonce, ct)));

        var headers = new Dictionary<string, string>();
        headers["X-Session-Id"] = Session;
        headers["X-Player-Page-Protection"] = "1";
        byte[] resp = HttpPost(body, headers);

        // 响应 pb{2:nonce||CT} -> GCM 解密 -> inflate-raw -> envelope{2:code,3:msg,4:data}
        List<GuluProto.F> top = GuluProto.Decode(resp);
        GuluProto.F enc = GuluProto.Find(top, 2, 2);
        if (enc == null) throw new Exception("响应无 field2 密文");
        byte[] nb = GuluProto.Slice(enc.bb, 0, 12);
        byte[] ctb = GuluProto.Slice(enc.bb, 12, enc.bb.Length - 12);
        byte[] envPlain = GuluCrypto.RawInflate(GuluCrypto.AesGcmDecrypt(SessionKey, nb, ctb));
        List<GuluProto.F> e = GuluProto.Decode(envPlain);
        Resp r = new Resp();
        GuluProto.F code = GuluProto.Find(e, 2, 0);
        r.code = code == null ? 0 : code.vi;
        GuluProto.F msg = GuluProto.Find(e, 3, 2);
        r.msg = msg == null ? "" : Encoding.UTF8.GetString(msg.bb);
        GuluProto.F data = GuluProto.Find(e, 4, 2);
        r.data = data == null ? null : data.bb;
        return r;
    }

    public class Resp { public long code; public string msg; public byte[] data; }

    // 设备注册 payload (csp_Gulu boot 设备指纹)
    public static byte[] BuildBootPayload(string deviceId)
    {
        byte[] app = GuluProto.S(1, "咕噜咕噜");
        app = GuluProto.Concat(app, GuluProto.S(2, "2.1.2"), GuluProto.S(3, "com.jymqfh.xee"),
            GuluProto.S(4, deviceId), GuluProto.S(5, "212"));
        byte[] dev = GuluProto.S(1, deviceId);
        dev = GuluProto.Concat(dev, GuluProto.V(2, 0), GuluProto.S(3, "11"), GuluProto.S(4, "Pixel 4"),
            GuluProto.S(5, "google/redfin/redfin:11/RQ3A.211001.001"), GuluProto.S(6, "google"),
            GuluProto.S(7, "redfin"), GuluProto.V(8, 0), GuluProto.S(9, "unknown"),
            GuluProto.S(10, "unknown"), GuluProto.V(11, 0), GuluProto.V(12, 30));
        byte[] p = GuluProto.S(1, "v1");
        p = GuluProto.Concat(p, GuluProto.S(2, "Android 11"), GuluProto.S(3, "gulu"),
            GuluProto.M(4, app), GuluProto.M(5, dev));
        return p;
    }

    // 直播频道: 分组名 + 频道名 + 播放直链
    public class LiveCh { public string group; public string name; public string url; }

    // 直播列表 data: {1:{1:typeId,3:"直播"}, 2:(repeated 包装){1:卡片{1:id, 5/6/12:分组名,
    //   75:{1:"zhibo", 2:(repeated){1:序号, 3:m3u8直链, 4:频道名}}}}}
    public static List<LiveCh> ParseLive(byte[] data)
    {
        var outL = new List<LiveCh>();
        if (data == null || data.Length == 0) return outL;
        List<GuluProto.F> top;
        try { top = GuluProto.Decode(data); } catch { return outL; }
        foreach (GuluProto.F card in GuluProto.All(top, 2))
        {
            if (card.w != 2) continue;
            List<GuluProto.F> cm;
            try
            {
                // 顶层 #2 是包装消息, 真实卡片在其 #1 内
                List<GuluProto.F> wrap = GuluProto.Decode(card.bb);
                GuluProto.F inner = GuluProto.Find(wrap, 1, 2);
                cm = inner == null ? wrap : GuluProto.Decode(inner.bb);
            }
            catch { continue; }
            string group = GuluProto.Text(GuluProto.Find(cm, 5, 2));
            if (group == null) group = GuluProto.Text(GuluProto.Find(cm, 6, 2));
            if (group == null) group = GuluProto.Text(GuluProto.Find(cm, 12, 2));
            if (group == null || group.Length == 0) group = "直播";
            foreach (GuluProto.F g in GuluProto.All(cm, 75))
            {
                if (g.w != 2) continue;
                List<GuluProto.F> gm;
                try { gm = GuluProto.Decode(g.bb); } catch { continue; }
                foreach (GuluProto.F e in GuluProto.All(gm, 2))
                {
                    if (e.w != 2) continue;
                    List<GuluProto.F> em;
                    try { em = GuluProto.Decode(e.bb); } catch { continue; }
                    string url = GuluProto.Text(GuluProto.Find(em, 3, 2));
                    string name = GuluProto.Text(GuluProto.Find(em, 4, 2));
                    if (url == null || url.Length == 0) continue;
                    if (name == null || name.Length == 0) name = "未命名频道";
                    outL.Add(new LiveCh { group = group, name = name, url = url });
                }
            }
        }
        return outL;
    }

    byte[] HttpPost(byte[] body, Dictionary<string, string> headers)
    {
        HttpWebRequest req = (HttpWebRequest)WebRequest.Create(ENDPOINT);
        req.Method = "POST";
        req.UserAgent = "okhttp/3.12.0";
        req.ContentType = "application/x-protobuf";
        req.Timeout = 20000;
        req.ReadWriteTimeout = 20000;
        req.Proxy = null;
        req.ServicePoint.Expect100Continue = false;
        if (headers != null)
            foreach (KeyValuePair<string, string> kv in headers) req.Headers[kv.Key] = kv.Value;
        req.ContentLength = body.Length;
        using (Stream rs = req.GetRequestStream()) rs.Write(body, 0, body.Length);
        try
        {
            using (HttpWebResponse resp = (HttpWebResponse)req.GetResponse())
            {
                SyncClock(resp);
                using (var ms = new MemoryStream())
                using (Stream s = resp.GetResponseStream())
                {
                    byte[] buf = new byte[65536]; int n;
                    while ((n = s.Read(buf, 0, buf.Length)) > 0) ms.Write(buf, 0, n);
                    return ms.ToArray();
                }
            }
        }
        catch (WebException ex)
        {
            var rsp = ex.Response as HttpWebResponse;
            if (rsp != null) throw new Exception("HTTP " + (int)rsp.StatusCode + " " + rsp.StatusDescription);
            throw;
        }
    }

    // 从 HTTP Date 头同步时钟, 规避本机时间偏移导致的 10002
    void SyncClock(HttpWebResponse resp)
    {
        try
        {
            string d = resp.Headers[HttpResponseHeader.Date];
            if (string.IsNullOrEmpty(d)) return;
            DateTime p;
            if (DateTime.TryParseExact(d, "R", System.Globalization.CultureInfo.InvariantCulture,
                System.Globalization.DateTimeStyles.AssumeUniversal | System.Globalization.DateTimeStyles.AdjustToUniversal, out p))
                clockOffset = (long)(p - DateTime.UtcNow).TotalMilliseconds;
        }
        catch { }
    }
}
