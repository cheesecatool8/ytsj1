import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 获取YouTube API密钥
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')

if not YOUTUBE_API_KEY:
    print("警告: 未设置YOUTUBE_API_KEY环境变量。请在.env文件中设置。") 