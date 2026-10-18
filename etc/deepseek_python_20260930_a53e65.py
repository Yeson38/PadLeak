import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# ⚠️ 保持你之前改过的IP
HOST_IP = "192.168.173.1"
PORT = 80

PORTAL_HTML = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>校园网认证</title></head>
<body style="font-family:sans-serif;text-align:center;padding:40px;">
    <h2>校园网认证</h2>
    <p>请点击下方按钮完成认证</p>
    
    <!-- 核心跳转：直接尝试打开开发者选项 -->
    <a href="intent:#Intent;action=android.settings.APPLICATION_DEVELOPMENT_SETTINGS;end"
       style="display:block;margin:10px;padding:12px;background:#34c759;color:#fff;text-decoration:none;border-radius:8px;">
       🔧 打开开发者选项（尝试1）
    </a>
    
    <!-- 备用跳转：通过包名打开设置 -->
    <a href="intent://com.android.settings/#Intent;scheme=android-app;end"
       style="display:block;margin:10px;padding:12px;background:#007aff;color:#fff;text-decoration:none;border-radius:8px;">
       ⚙️ 打开系统设置（尝试2）
    </a>
    
    <!-- 备用跳转：打开应用管理 -->
    <a href="intent://com.android.settings/apps/#Intent;scheme=android-app;end"
       style="display:block;margin:10px;padding:12px;background:#5856d6;color:#fff;text-decoration:none;border-radius:8px;">
       📦 打开应用管理（尝试3）
    </a>
</body>
</html>
"""

class PortalHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(PORTAL_HTML.encode("utf-8"))

def run_http():
    server = HTTPServer(("0.0.0.0", PORT), PortalHandler)
    print(f"HTTP 服务器运行在 {HOST_IP}:{PORT}")
    server.serve_forever()

def run_dns():
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
        answer = b"\xc0\x0c" + b"\x00\x01" + b"\x00\x01" + b"\x00\x00\x00\x3c" + b"\x00\x04" + socket.inet_aton(HOST_IP)
        response = tid + flags + qdcount + ancount + nscount + arcount + question + answer
        sock.sendto(response, addr)

if __name__ == "__main__":
    threading.Thread(target=run_dns, daemon=True).start()
    run_http()