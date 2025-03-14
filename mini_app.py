from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "<h1>Hello World!</h1><p>This is a minimal Flask application.</p>"

if __name__ == '__main__':
    print("="*50)
    print("Starting minimal Flask server...")
    print("Server will be available at: http://127.0.0.1:5050")
    print("="*50)
    
    # 使用5050端口，避开常用端口
    app.run(host='127.0.0.1', port=5050, debug=True) 