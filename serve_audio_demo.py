# serve_audio_demo.py
# 启动本地HTTP服务器并生成二维码供手机扫描访问
import http.server
import socketserver
import socket
import qrcode
import os
from pathlib import Path


def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        # 创建一个UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接到外部地址（不会真的发送数据）
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def generate_qr_code(url, filename="qr_code.png"):
    """生成二维码"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    print(f"✅ 二维码已保存为: {filename}")
    return filename


class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # 添加CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def log_message(self, format, *args):
        # 自定义日志格式
        print(f"[{self.log_date_time_string()}] {format % args}")


def start_server(port=8000):
    """启动HTTP服务器"""
    # 获取本机IP
    local_ip = get_local_ip()

    # 检查audio_samples目录
    if not os.path.exists("audio_samples"):
        print("⚠️  警告: 'audio_samples' 目录不存在!")
        print("   请先运行 extract_audio.py 生成音频文件")
        return

    # 检查HTML文件
    if not os.path.exists("audio_demo.html"):
        print("❌ 错误: 'audio_demo.html' 文件不存在!")
        return

    # 构造访问URL
    url = f"http://{local_ip}:{port}/audio_demo.html"

    print("\n" + "=" * 60)
    print("🚀 语音演示服务器启动中...")
    print("=" * 60)
    print(f"\n📱 手机访问地址:")
    print(f"   {url}")
    print(f"\n💻 电脑访问地址:")
    print(f"   http://localhost:{port}/audio_demo.html")

    # 生成二维码
    print(f"\n📊 正在生成二维码...")
    qr_file = generate_qr_code(url)

    print(f"\n" + "=" * 60)
    print("📋 使用说明:")
    print("=" * 60)
    print("1. 确保手机和电脑在同一个WiFi网络")
    print("2. 用手机扫描生成的二维码 (qr_code.png)")
    print("3. 或直接在手机浏览器输入上面的网址")
    print("4. 按 Ctrl+C 停止服务器")
    print("=" * 60 + "\n")

    # 尝试打开二维码图片
    try:
        if os.name == 'nt':  # Windows
            os.startfile(qr_file)
        elif os.name == 'posix':  # macOS/Linux
            os.system(f'open {qr_file}')
    except:
        pass

    # 启动服务器
    Handler = MyHTTPRequestHandler

    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"✅ 服务器运行在端口 {port}...\n")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ 错误: 端口 {port} 已被占用!")
            print(f"   尝试使用其他端口, 例如: python serve_audio_demo.py 8001")
        else:
            print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    import sys

    # 检查端口参数
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("❌ 无效的端口号!")
            sys.exit(1)

    start_server(port)
