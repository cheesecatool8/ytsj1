#!/bin/bash

# 安装依赖
pip install -r requirements.txt

# 创建必要的目录
mkdir -p .vercel/output/static
mkdir -p .vercel/output/functions

# 复制静态文件
cp -r static/* .vercel/output/static/

# 创建函数配置
echo '{
  "version": 1,
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/api/index"
    }
  ]
}' > .vercel/output/config.json

# 创建函数
mkdir -p .vercel/output/functions/api/index.func
echo '{
  "runtime": "python3.9",
  "handler": "index.handler",
  "memory": 1024
}' > .vercel/output/functions/api/index.func/.vc-config.json

# 复制应用文件到函数目录
cp -r app.py templates static requirements.txt .vercel/output/functions/api/index.func/

# 创建函数入口点
echo 'from app import app

def handler(request, context):
    return app(request, context)
' > .vercel/output/functions/api/index.func/index.py 