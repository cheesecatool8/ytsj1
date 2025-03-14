from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>端口80测试</title>
    </head>
    <body>
        <h1>80端口连接成功!</h1>
        <p>如果您能看到这个页面，说明服务器在80端口已成功连接。</p>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("="*50)
    print("启动80端口测试服务器...")
    print("请尝试访问:")
    print("- http://127.0.0.1")
    print("- http://localhost")
    print("(注意：这是不带端口号的URL，因为80是默认端口)")
    print("="*50)
    
    try:
        # 注意：在Windows系统上，使用80端口需要管理员权限
        app.run(host='127.0.0.1', port=80, debug=True)
    except Exception as e:
        print(f"错误: {e}")
        print("使用80端口失败，可能需要管理员权限。请尝试以管理员身份运行命令提示符。")
        input("按任意键退出...") 