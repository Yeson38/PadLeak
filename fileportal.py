import socket
import threading
import os
import cgi
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# ⚠️ 改成你电脑上“本地连接* 3”的实际 IPv4 地址（通常是 192.168.137.1）
HOST_IP = "192.168.137.1"
PORT = 80

# 电脑共享文件夹路径（改成你电脑上实际存在的文件夹）
SHARE_DIR = r"C:\FileShare"

if not os.path.exists(SHARE_DIR):
    os.makedirs(SHARE_DIR)

def get_file_icon(filename):
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']: return '🖼️'
    if ext in ['mp4', 'mkv', 'avi', 'mov', 'flv']: return '🎬'
    if ext in ['mp3', 'wav', 'flac', 'aac']: return '🎵'
    if ext in ['pdf']: return '📕'
    if ext in ['doc', 'docx']: return '📘'
    if ext in ['xls', 'xlsx']: return '📗'
    if ext in ['zip', 'rar', '7z']: return '🗜️'
    if ext in ['apk']: return '📦'
    if ext in ['txt', 'md']: return '📄'
    return '📄'

class FileShareHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/download/"):
            filename = urllib.parse.unquote(self.path.split("/")[-1])
            safe_path = os.path.abspath(os.path.join(SHARE_DIR, filename))
            if safe_path.startswith(os.path.abspath(SHARE_DIR)) and os.path.isfile(safe_path):
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Disposition", f"attachment; filename*=UTF-8''{urllib.parse.quote(filename)}")
                self.end_headers()
                with open(safe_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File Not Found")
            return

        files = []
        try:
            for f in os.listdir(SHARE_DIR):
                filepath = os.path.join(SHARE_DIR, f)
                if os.path.isfile(filepath):
                    size = os.path.getsize(filepath)
                    size_str = f"{size/1024:.1f} KB" if size < 1024*1024 else f"{size/(1024*1024):.2f} MB"
                    files.append({"name": f, "size": size_str, "is_dir": False})
                elif os.path.isdir(filepath):
                    files.append({"name": f, "size": "文件夹", "is_dir": True})
        except Exception:
            pass

        file_list_html = ""
        if not files:
            file_list_html = '<div style="text-align:center;color:#888;padding:20px;">暂无文件</div>'
        else:
            for f in sorted(files, key=lambda x: (not x['is_dir'], x['name'])):
                icon = get_file_icon(f['name']) if not f['is_dir'] else '📁'
                download_link = f'<a href="/download/{urllib.parse.quote(f["name"])}" download="{f["name"]}" style="color:#007aff;text-decoration:none;display:block;padding:12px 15px;">{icon} {f["name"]} <span style="float:right;color:#888;font-size:12px;">{f["size"]}</span></a>'
                file_list_html += f'<div style="border-bottom:1px solid #eee;">{download_link}</div>'

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>文件互传中心</title>
            <style>
                body {{ font-family: -apple-system, sans-serif; background: #f4f6f8; margin: 0; padding: 20px; display: flex; justify-content: center; }}
                .container {{ width: 100%; max-width: 600px; }}
                .card {{ background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px; overflow: hidden; }}
                .card-header {{ background: #007aff; color: white; padding: 15px 20px; font-size: 18px; font-weight: bold; display: flex; justify-content: space-between; align-items: center; }}
                .upload-area {{ padding: 20px; text-align: center; border: 2px dashed #ccc; border-radius: 8px; margin: 15px; background: #fafafa; }}
                .upload-btn {{ background: #34c759; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 16px; cursor: pointer; margin-top: 10px; width: 100%; font-weight: 500; }}
                .file-item {{ display: flex; align-items: center; justify-content: space-between; padding: 12px 20px; border-bottom: 1px solid #f0f0f0; }}
                .file-item a {{ color: #333; text-decoration: none; flex-grow: 1; }}
                .file-size {{ color: #999; font-size: 12px; }}
                .progress-bar {{ width: 100%; height: 6px; background: #eee; border-radius: 3px; margin-top: 10px; overflow: hidden; display: none; }}
                .progress-bar-inner {{ height: 100%; background: #34c759; width: 0%; transition: width 0.2s; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="card">
                    <div class="card-header"><span>📂 局域网文件互传</span><button style="background: rgba(255,255,255,0.2); color: white; border: none; padding: 5px 12px; border-radius: 15px; font-size: 12px; cursor: pointer;" onclick="location.reload()">刷新</button></div>
                </div>
                <div class="card">
                    <div class="card-body">
                        <form id="uploadForm" action="/upload" method="post" enctype="multipart/form-data" class="upload-area" onsubmit="uploadFile(event)">
                            <div style="font-size: 40px; margin-bottom: 10px;">📤</div>
                            <div>点击选择文件上传到电脑</div>
                            <input type="file" name="file" id="fileInput" style="display: none;" onchange="document.getElementById('fileName').textContent = this.files[0] ? this.files[0].name : ''">
                            <button type="button" class="upload-btn" onclick="document.getElementById('fileInput').click()">选择文件</button>
                            <div id="fileName" style="margin-top:10px; font-size:14px; color:#555;"></div>
                            <button type="submit" class="upload-btn" style="background:#007aff; display:none;" id="submitBtn">开始上传</button>
                            <div class="progress-bar" id="progressBar"><div class="progress-bar-inner" id="progressInner"></div></div>
                        </form>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header" style="background:#5856d6;">📁 电脑共享文件 (点击下载)</div>
                    <div class="card-body" style="padding:0;">{file_list_html}</div>
                </div>
                <div style="text-align: center; color: #888; font-size: 12px; margin-top: 20px;">仅限局域网内使用 · 电脑IP: {HOST_IP}</div>
            </div>
            <script>
                function uploadFile(e) {{
                    e.preventDefault();
                    const form = document.getElementById('uploadForm');
                    const fileInput = document.getElementById('fileInput');
                    const submitBtn = document.getElementById('submitBtn');
                    const progressBar = document.getElementById('progressBar');
                    const progressInner = document.getElementById('progressInner');
                    if (!fileInput.files.length) {{ alert('请先选择文件'); return; }}
                    progressBar.style.display = 'block'; submitBtn.style.display = 'none';
                    const xhr = new XMLHttpRequest();
                    xhr.open('POST', '/upload', true);
                    xhr.upload.onprogress = function(e) {{ if (e.lengthComputable) {{ progressInner.style.width = (e.loaded / e.total) * 100 + '%'; }} }};
                    xhr.onload = function() {{ if (xhr.status === 200 || xhr.status === 302) {{ alert('上传成功！'); location.reload(); }} else {{ alert('上传失败'); progressBar.style.display = 'none'; submitBtn.style.display = 'block'; }} }};
                    xhr.onerror = function() {{ alert('网络错误'); progressBar.style.display = 'none'; submitBtn.style.display = 'block'; }};
                    xhr.send(new FormData(form));
                }}
                document.getElementById('fileInput').addEventListener('change', function() {{ document.getElementById('submitBtn').style.display = this.files.length ? 'block' : 'none'; }});
            </script>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        if self.path == "/upload":
            try:
                form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type']})
                if "file" in form:
                    file_item = form["file"]
                    if file_item.filename:
                        filename = os.path.basename(file_item.filename)
                        with open(os.path.join(SHARE_DIR, filename), "wb") as f:
                            f.write(file_item.file.read())
                        self.send_response(302)
                        self.send_header("Location", "/")
                        self.end_headers()
                        return
                self.send_error(400)
            except Exception as e:
                print(f"上传错误: {e}")
                self.send_error(500)
            return

def run_http():
    server = HTTPServer(("0.0.0.0", PORT), FileShareHandler)
    print(f"文件互传服务器运行在 http://{HOST_IP}:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run_http()