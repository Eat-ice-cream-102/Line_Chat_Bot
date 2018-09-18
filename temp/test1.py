from flask import Flask, request, abort

app = Flask(__name__)

@app.route('/')
def homepage():
    return 'Hello, World!'

@app.route('/test')
def in_test_page():
    return 'In test page'

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)