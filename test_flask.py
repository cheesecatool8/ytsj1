
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "<h1>Hello World!</h1><p>Flask is working!</p>"

if __name__ == '__main__':
    print("Flask���Է�����������")
    print("����������з���: http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000)
