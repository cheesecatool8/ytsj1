from flask import Flask, render_template, request, jsonify, send_from_directory
from googleapiclient.discovery import build
from datetime import datetime
import json
import traceback
from googleapiclient.errors import HttpError
import os
import logging
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 启用CORS支持

# 添加请求限制
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def test_api_key(api_key):
    """测试API密钥是否有效"""
    try:
        logger.info(f"开始测试API密钥...")
        
        # 创建YouTube客户端
        youtube = build(
            'youtube',
            'v3',
            developerKey=api_key,
            cache_discovery=False
        )
        
        # 测试API密钥
        request = youtube.videos().list(
            part='snippet',
            id='dQw4w9WgXcQ'  # 使用一个确定存在的视频ID进行测试
        )
        response = request.execute()
        
        if response:
            logger.info("API密钥测试成功")
            return True, "API密钥有效"
            
    except HttpError as e:
        error_content = json.loads(e.content)
        error_message = error_content.get('error', {}).get('message', str(e))
        logger.error(f"API密钥测试失败: {error_message}")
        
        if 'quota' in error_message.lower():
            return False, "API配额已用完，请等待重置或使用新的API密钥"
        else:
            return False, f"API密钥无效: {error_message}"
            
    except Exception as e:
        logger.error(f"API密钥测试出现未知错误: {str(e)}")
        return False, f"测试出错: {str(e)}"

def create_youtube_client(api_key):
    """创建YouTube API客户端"""
    try:
        # 首先测试API密钥
        is_valid, message = test_api_key(api_key)
        if not is_valid:
            raise Exception(message)
            
        # 创建YouTube客户端（无代理）
        youtube = build(
            'youtube',
            'v3',
            developerKey=api_key,
            cache_discovery=False
        )
        
        return youtube
    except Exception as e:
        error_msg = str(e)
        logger.error(f"创建YouTube客户端时出错: {error_msg}")
        raise Exception(error_msg)

@app.route('/')
def home():
    # 获取项目根目录下的index.html路径
    index_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'index.html')
    
    # 检查文件是否存在
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as file:
            return file.read()
    else:
        # 如果找不到index.html，返回备用HTML
        return """
        <html>
        <head>
            <title>芝士猫YouTube数据采集工具</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
                h1 { color: #333; }
                .nav { margin: 20px; }
                .nav a { margin: 0 10px; text-decoration: none; color: #0066cc; }
            </style>
        </head>
        <body>
            <h1>芝士猫YouTube数据采集工具</h1>
            <p>服务已成功部署！</p>
            <div class="nav">
                <a href="/health">查看服务状态</a> | 
                <a href="/hello">测试页面</a>
            </div>
        </body>
        </html>
        """

@app.route('/test_key', methods=['POST'])
@limiter.limit("20 per minute")  # 限制API调用频率
def test_key():
    """测试API密钥路由"""
    try:
        logger.info("收到API密钥测试请求")
        
        if not request.is_json:
            logger.error("请求不是JSON格式")
            return jsonify({'success': False, 'error': '请求格式错误，需要JSON数据'}), 400
            
        data = request.get_json()
        if not data or 'apiKey' not in data:
            logger.error("未提供API密钥")
            return jsonify({'success': False, 'error': '请提供API密钥'}), 400
            
        api_key = data['apiKey'].strip()
        logger.info(f"测试API密钥: {api_key[:5]}...{api_key[-5:] if len(api_key) > 10 else ''}")
        
        is_valid, message = test_api_key(api_key)
        
        if is_valid:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        error_msg = f"API密钥测试路由出错: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/search', methods=['POST'])
@limiter.limit("100 per hour")  # 限制搜索频率
def search():
    try:
        if not request.is_json:
            return jsonify({'error': '请求格式错误，需要JSON数据'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '无法解析JSON数据'}), 400
        
        search_type = data.get('type')
        query = data.get('query', '').strip()
        sort_by = data.get('sortBy')
        api_key = data.get('apiKey', '').strip()
        
        if not api_key:
            return jsonify({'error': '请提供YouTube API密钥。您可以在Google Cloud Console中获取免费的API密钥。'}), 400
        
        if not query:
            return jsonify({'error': '请提供搜索关键词或频道链接'}), 400
            
        logger.info(f"收到搜索请求 - 类型: {search_type}, 查询: {query}, 排序: {sort_by}")
        
        try:
            youtube = create_youtube_client(api_key)
        except Exception as e:
            return jsonify({'error': str(e)}), 503
            
        videos = []
        next_page_token = None
        total_results = 0
        max_results = 200  # 设置最大获取视频数

        try:
            while total_results < max_results:
                if search_type == 'keyword':
                    request_obj = youtube.search().list(
                        q=query,
                        part='snippet',
                        type='video',
                        order=sort_by,
                        maxResults=50,
                        pageToken=next_page_token
                    )
                else:
                    # 频道搜索
                    channel_id = None
                    
                    if 'youtube.com/channel/' in query:
                        channel_id = query.split('youtube.com/channel/')[1].split('/')[0]
                    elif 'youtube.com/c/' in query or 'youtube.com/@' in query or query.startswith('@'):
                        search_term = (
                            query.split('youtube.com/c/')[-1].split('/')[0] if 'youtube.com/c/' in query
                            else query.split('youtube.com/@')[-1].split('/')[0] if 'youtube.com/@' in query
                            else query[1:]
                        )
                        
                        search_response = youtube.search().list(
                            q=search_term,
                            part='snippet',
                            type='channel',
                            maxResults=1
                        ).execute()
                        
                        if search_response.get('items'):
                            channel_id = search_response['items'][0]['id']['channelId']
                    
                    if not channel_id:
                        search_response = youtube.search().list(
                            q=query,
                            part='snippet',
                            type='channel',
                            maxResults=1
                        ).execute()
                        
                        if search_response.get('items'):
                            channel_id = search_response['items'][0]['id']['channelId']
                        else:
                            return jsonify({'error': f'找不到与"{query}"匹配的频道，请尝试使用完整的频道URL或检查拼写'}), 404
                    
                    request_obj = youtube.search().list(
                        channelId=channel_id,
                        part='snippet',
                        type='video',
                        order=sort_by,
                        maxResults=50,
                        pageToken=next_page_token
                    )

                response = request_obj.execute()
                video_ids = [item['id']['videoId'] for item in response.get('items', [])]
                
                if video_ids:
                    videos_response = youtube.videos().list(
                        part='statistics,snippet',
                        id=','.join(video_ids)
                    ).execute()

                    for video in videos_response.get('items', []):
                        try:
                            thumbnails = video['snippet'].get('thumbnails', {})
                            thumbnail = (
                                thumbnails.get('maxres', {}) or 
                                thumbnails.get('high', {}) or 
                                thumbnails.get('medium', {}) or 
                                thumbnails.get('default', {})
                            )
                            
                            statistics = video.get('statistics', {})
                            
                            videos.append({
                                'channelTitle': video['snippet']['channelTitle'],
                                'publishedAt': datetime.strptime(
                                    video['snippet']['publishedAt'], 
                                    '%Y-%m-%dT%H:%M:%SZ'
                                ).strftime('%Y-%m-%d'),
                                'title': video['snippet']['title'],
                                'viewCount': int(statistics.get('viewCount', 0)),
                                'likeCount': int(statistics.get('likeCount', 0)),
                                'commentCount': int(statistics.get('commentCount', 0)),
                                'url': f"https://www.youtube.com/watch?v={video['id']}",
                                'thumbnails': video['snippet'].get('thumbnails', {}),
                            })
                        except Exception as e:
                            logger.error(f"处理视频数据时出错: {str(e)}")

                total_results = len(videos)
                next_page_token = response.get('nextPageToken')
                
                if not next_page_token or total_results >= max_results:
                    break

            if sort_by == 'date':
                videos.sort(key=lambda x: x['publishedAt'], reverse=True)
            elif sort_by == 'viewCount':
                videos.sort(key=lambda x: x['viewCount'], reverse=True)
            elif sort_by == 'rating':
                videos.sort(key=lambda x: x['likeCount'], reverse=True)

            return jsonify({
                'videos': videos,
                'totalResults': total_results,
                'maxResults': max_results
            })
            
        except HttpError as e:
            error_content = json.loads(e.content)
            error_reason = error_content.get('error', {}).get('message', str(e))
            
            if 'quota' in error_reason.lower():
                return jsonify({'error': 'API配额已用完，请明天再试或使用新的API密钥'}), 429
            elif 'api key' in error_reason.lower():
                return jsonify({'error': 'API密钥无效，请检查您的密钥是否正确'}), 401
            else:
                return jsonify({'error': f'YouTube API错误: {error_reason}'}), 400

    except Exception as e:
        logger.error(f"搜索功能错误: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/test_api', methods=['POST'])
def test_api():
    """简化的API测试路由"""
    try:
        logger.info("收到API测试请求（简化版）")
        
        if not request.is_json:
            return jsonify({'success': False, 'error': '请求格式错误'}), 400
            
        data = request.get_json()
        if not data or 'apiKey' not in data:
            return jsonify({'success': False, 'error': '请提供API密钥'}), 400
            
        api_key = data['apiKey']
        logger.info(f"收到API密钥: {api_key[:5]}...")
        
        # 简单返回成功响应进行测试
        return jsonify({
            'success': True,
            'message': '路由测试成功',
            'received_key': api_key[:5] + '...'
        })
        
    except Exception as e:
        logger.error(f"简化API测试路由出错: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/static/<path:path>')
def serve_static(path):
    # 提供静态文件服务
    static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    return send_from_directory(static_folder, path)

@app.route('/hello')
def hello():
    return "Hello from Serverless Flask on Vercel!"

@app.route('/health')
def health_check():
    # 健康检查页面
    health_template = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'health.html')
    if os.path.exists(health_template):
        with open(health_template, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return """
        <html>
        <head>
            <title>服务状态 - 芝士猫YouTube数据采集工具</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
                h1 { color: #333; }
                .status { padding: 20px; background-color: #e7f7e7; border-radius: 5px; margin: 20px auto; max-width: 500px; }
                .status h2 { color: #2e8b57; }
                .nav { margin: 20px; }
                .nav a { margin: 0 10px; text-decoration: none; color: #0066cc; }
            </style>
        </head>
        <body>
            <h1>芝士猫YouTube数据采集工具</h1>
            <div class="status">
                <h2>服务状态: 正常</h2>
                <p>所有系统运行正常</p>
            </div>
            <div class="nav">
                <a href="/">返回首页</a>
                <a href="/hello">测试API</a>
            </div>
        </body>
        </html>
        """

@app.route('/api/health', methods=['GET'])
def api_health_check():
    return jsonify({'status': 'ok', 'message': '服务正常运行'}), 200

# 确保模板文件夹存在并创建必要的模板
def ensure_templates_exist():
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    if not os.path.exists(templates_dir):
        try:
            os.makedirs(templates_dir)
        except Exception as e:
            logger.error(f"创建模板目录失败: {str(e)}")
            return
    
    # 确保404.html存在
    error_404_path = os.path.join(templates_dir, '404.html')
    if not os.path.exists(error_404_path):
        try:
            with open(error_404_path, 'w', encoding='utf-8') as f:
                f.write("""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>404 - 页面未找到</title>
                </head>
                <body>
                    <h1>404 - 页面未找到</h1>
                    <p>您访问的页面不存在。</p>
                    <a href="/">返回首页</a>
                </body>
                </html>
                """)
        except Exception as e:
            logger.error(f"创建404模板失败: {str(e)}")

# 预创建模板
ensure_templates_exist()

# 设置Flask应用调试模式
app.debug = True

# Vercel Serverless函数处理程序
def handler(request, context):
    """处理Vercel Serverless函数请求"""
    with app.test_request_context(
        path=request.get('path', '/'),
        method=request.get('method', 'GET'),
        headers=request.get('headers', {}),
        data=request.get('body', b'')
    ):
        try:
            response = app.full_dispatch_request()
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data().decode('utf-8')
            }
        except Exception as e:
            logger.error(f"Serverless处理错误: {str(e)}")
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'text/plain'},
                'body': str(e)
            } 