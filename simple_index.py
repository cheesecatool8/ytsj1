from simple_app import app

# Vercel在无服务器环境中使用此处理程序
def handler(request, context):
    return app(request) 