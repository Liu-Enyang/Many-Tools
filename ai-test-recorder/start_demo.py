import http.server
import socketserver
import threading
import webbrowser
import time
import os

PORT = 8000

DIRECTORY = os.path.dirname(os.path.abspath(__file__))

os.chdir(DIRECTORY)

Handler = http.server.SimpleHTTPRequestHandler


def start_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Demo server started at http://localhost:{PORT}")
        httpd.serve_forever()


# 启动HTTP服务器线程
server_thread = threading.Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

# 等待服务器启动
time.sleep(1)

# 自动打开浏览器
url = f"http://localhost:{PORT}/demo/testpage.html"
print("Opening browser:", url)

webbrowser.open(url)

# 保持程序运行
try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print("\nServer stopped")