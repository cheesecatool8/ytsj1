"""
测试Vercel部署的简单脚本
"""

from app import app

if __name__ == "__main__":
    # 打印所有注册的路由
    print("注册的路由:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint}: {rule.methods} {rule}")
    
    # 测试应用是否能正常启动
    app.run(debug=True, port=5000) 