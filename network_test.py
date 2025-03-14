import socket
import subprocess
import sys
import os

def print_header(message):
    print("\n" + "="*60)
    print(message)
    print("="*60)

def test_localhost():
    print_header("测试localhost连接")
    
    # 测试ping localhost
    print("Ping localhost...")
    try:
        result = subprocess.run(["ping", "-n", "3", "localhost"], capture_output=True, text=True)
        print(result.stdout)
        if "无法访问目标主机" in result.stdout or "could not find host" in result.stdout.lower():
            print("❌ Ping localhost失败，请检查您的hosts文件")
        else:
            print("✅ Ping localhost成功")
    except Exception as e:
        print(f"执行ping命令时出错: {e}")
    
    # 测试hosts文件
    try:
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        if os.path.exists(hosts_path):
            with open(hosts_path, "r") as f:
                hosts_content = f.read()
            if "localhost" in hosts_content:
                print("✅ hosts文件中包含localhost条目")
            else:
                print("❌ 警告：hosts文件中可能缺少localhost条目")
                print("建议添加: 127.0.0.1 localhost")
        else:
            print(f"❌ 找不到hosts文件: {hosts_path}")
    except Exception as e:
        print(f"读取hosts文件时出错: {e}")

def test_port(port):
    print_header(f"测试端口 {port}")
    
    # 检查端口是否被占用
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # 2秒超时
        result = sock.connect_ex(('127.0.0.1', port))
        if result == 0:
            print(f"✅ 端口 {port} 已经打开并且有程序在监听")
        else:
            print(f"❌ 端口 {port} 未打开或没有程序在监听")
        sock.close()
    except Exception as e:
        print(f"测试端口时出错: {e}")
    
    # 检查是否被防火墙阻止
    try:
        result = subprocess.run(
            ["netsh", "advfirewall", "firewall", "show", "rule", f"localport={port}"], 
            capture_output=True, 
            text=True
        )
        if "没有符合指定条件的规则" in result.stdout:
            print(f"❌ 未找到针对端口 {port} 的防火墙规则")
        else:
            print(f"ℹ️ 找到针对端口 {port} 的防火墙规则:")
            print(result.stdout)
    except Exception as e:
        print(f"检查防火墙规则时出错: {e}")

def test_flask_server():
    print_header("测试Flask服务器")
    
    try:
        # 检查Flask是否已安装
        try:
            import flask
            print(f"✅ Flask已安装 (版本: {flask.__version__})")
        except ImportError:
            print("❌ Flask未安装")
            return
        
        # 尝试启动一个短暂的Flask服务器
        import threading
        import time
        import requests
        
        def run_flask():
            from flask import Flask
            app = Flask(__name__)
            
            @app.route('/network_test')
            def hello():
                return "Flask服务器测试成功!"
            
            app.run(host='127.0.0.1', port=5555, debug=False)
        
        print("启动测试Flask服务器 (5555端口)...")
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.daemon = True  # 设置为守护线程，这样主线程结束时它也会结束
        flask_thread.start()
        
        # 等待服务器启动
        time.sleep(2)
        
        # 尝试连接
        try:
            print("尝试连接到测试服务器...")
            response = requests.get("http://127.0.0.1:5555/network_test", timeout=5)
            print(f"✅ 连接成功! 状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"❌ 连接失败: {e}")
        
    except Exception as e:
        print(f"测试过程中出错: {e}")

def main():
    print("\n📡 网络和Flask服务器诊断工具 📡\n")
    
    print(f"Python版本: {sys.version}")
    print(f"操作系统: {sys.platform}")
    
    test_localhost()
    test_port(8888)  # 测试我们使用的端口
    test_port(80)    # 测试默认HTTP端口
    test_flask_server()
    
    print("\n诊断完成! 如果看到任何错误，请尝试解决或联系系统管理员。")
    input("\n按Enter键退出...")

if __name__ == "__main__":
    main() 