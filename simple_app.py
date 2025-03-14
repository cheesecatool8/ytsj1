from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Hello from Vercel!</h1>"

@app.route('/test')
def test():
    return "<h1>Test Route Works!</h1>" 