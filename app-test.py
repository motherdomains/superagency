from flask import Flask

app = Flask(__name__)

@app.route('/test')
def test():
    return "Test Route is Working!"

@app.route('/users')
def users():
    return "Users Route is Working!"

if __name__ == '__main__':
    app.run(debug=True)