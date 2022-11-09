from flask import Flask
from waitress import serve

app = Flask(__name__)


@app.route('/api/v1/hello-world-6')
def variant():
    return 'Hello world 6'


if __name__ == '__main__':
    serve(app, host='localhost', port=8000)

# http://localhost:{порт}/api/v1/hello-world-6