import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# 这里必须改成你刚才设置的IP
HOST_IP = "192.168.137.1"
PORT = 80

# 这个页面会加载到平板的强制门户弹窗里
PORTAL_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>校园网认证</title></head>
<body style="font-family:sans-serif;text-align:center;padding:40px;">
    <h2>校园网认证</h2>
    <p>请点击下方按钮完成认证</p>
    <a href="intent://com.android.settings/#Intent;scheme=android-app;end"
       style="display:block;margin:10px;padding:12px;background:#007aff;color:#fff;text-decoration:none;border-radius:8px;">
       打开系统设置
    </a>
    <a href="intent://com.android.documentsui/#Intent;scheme=android-app;end"
       style="display:block;margin:10px;padding:12px;background:#5856d6;color:#fff;text-decoration:none;border-radius:8px;">
       打开文件管理器
    </a>
    <a href="/LocalSend.apk"
       style="display:block;margin:10px;padding:12px;background:#ff3b30;color:#fff;text-decoration:none;border-radius:8px;">
       下载 InkBoard 桌面
    </a>
</body>
</html>
"""

class PortalHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/LocalSend.apk":
            try:
                with open("LocalSend.apk", "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/vnd.android.package-archive")
                self.send_header("Content-Disposition", "attachment; filename=InkBoard.apk")
                self.end_headers()
                self.wfile.write(data)
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
        else:
            # 所有其他请求都返回我们的伪装登录页
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(PORTAL_HTML.encode("utf-8"))

def run_http():
    server = HTTPServer(("0.0.0.0", PORT), PortalHandler)
    print(f"HTTP 服务器运行在 {HOST_IP}:{PORT}")
    server.serve_forever()

def run_dns():
    # DNS 劫持：把所有域名解析到我们自己的 IP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 53))
    print("DNS 服务器运行中（所有域名 -> 本机）")
    while True:
        data, addr = sock.recvfrom(512)
        tid = data[:2]
        flags = b"\x81\x80"
        qdcount = data[4:6]
        ancount = b"\x00\x01"
        nscount = b"\x00\x00"
        arcount = b"\x00\x00"
        question = data[12:]
        # 伪造 A 记录响应，指向我们的 IP
        answer = b"\xc0\x0c" + b"\x00\x01" + b"\x00\x01" + b"\x00\x00\x00\x3c" + b"\x00\x04" + socket.inet_aton(HOST_IP)
        response = tid + flags + qdcount + ancount + nscount + arcount + question + answer
        sock.sendto(response, addr)

if __name__ == "__main__":
    threading.Thread(target=run_dns, daemon=True).start()
    run_http()