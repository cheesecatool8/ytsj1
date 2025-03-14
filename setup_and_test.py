import subprocess
import sys
import os
import time

def print_step(message):
    """打印带有格式的步骤信息"""
    print("\n" + "="*70)
    print(f">>> {message}")
    print("="*70)

def run_command(command):
    """运行命令并返回结果"""
    print(f"执行命令: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"错误: {result.stderr}")
    return result.returncode == 0

def check_packages():
    """检查是否已安装必要的包"""
    print_step("检查已安装的包")
    packages = {
        "flask": False,
        "google-api-python-client": False,
        "python-dotenv": False
    }
    
    for package in packages:
        try:
            __import__(package.replace("-", "_"))
            packages[package] = True
            print(f"✓ {package} 已安装")
        except ImportError:
            print(f"✗ {package} 未安装")
    
    return packages

def install_packages(packages):
    """安装缺失的包"""
    print_step("安装必要的包")
    for package, installed in packages.items():
        if not installed:
            print(f"安装 {package}...")
            if not run_command(f"{sys.executable} -m pip install {package}"):
                print(f"无法安装 {package}，请检查网络连接或尝试手动安装")
                return False
        else:
            print(f"{package} 已安装，跳过")
    return True

def test_minimal_app():
    """测试最小化Flask应用"""
    print_step("测试最小化Flask应用")
    test_code = """
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "<h1>Hello World!</h1><p>Flask is working!</p>"

if __name__ == '__main__':
    print("Flask测试服务器已启动")
    print("请在浏览器中访问: http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000)
"""
    
    with open("test_flask.py", "w") as f:
        f.write(test_code)
    
    print("启动测试Flask服务器...")
    print("请在看到服务器启动后打开浏览器访问: http://127.0.0.1:5000")
    print("测试完成后，请回到命令行窗口并按Ctrl+C结束测试")
    time.sleep(3)
    
    subprocess.run([sys.executable, "test_flask.py"], shell=True)
    return True

def test_main_app():
    """测试主应用"""
    print_step("测试主应用")
    print("启动主应用...")
    print("请在看到服务器启动后打开浏览器访问: http://127.0.0.1:8888")
    print("测试完成后，请回到命令行窗口并按Ctrl+C结束测试")
    time.sleep(3)
    
    subprocess.run([sys.executable, "app.py"], shell=True)
    return True

def main():
    """主函数"""
    print("\n🔧 YouTube数据采集工具 - 安装和测试脚本 🔧\n")
    
    # 检查Python版本
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"Python版本: {python_version}")
    
    # 检查并安装包
    packages = check_packages()
    if not all(packages.values()):
        if not install_packages(packages):
            print("\n❌ 安装包失败，请尝试手动安装所需的包")
            return
    
    print("\n✅ 所有必要的包都已安装")
    
    # 询问用户是否要进行测试
    choice = input("\n是否要测试Flask是否正常工作? (y/n): ").strip().lower()
    if choice == 'y':
        if not test_minimal_app():
            print("\n❌ 最小化Flask应用测试失败")
            return
    
    # 询问用户是否要测试主应用
    choice = input("\n是否要测试主应用? (y/n): ").strip().lower()
    if choice == 'y':
        if not test_main_app():
            print("\n❌ 主应用测试失败")
            return
    
    print("\n✅ 安装和测试完成!")
    print("您现在可以通过运行 'python app.py' 来启动YouTube数据采集工具")

if __name__ == "__main__":
    main() 