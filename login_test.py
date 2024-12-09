from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>Welcome to the Login Test App</h1><a href='/login-test'>Go to Login Test</a>"

@app.route('/login-test', methods=['GET', 'POST'])
def login_test():
    if request.method == 'POST':
        # Retrieve posted form data
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        return f"<h1>Form submitted!</h1><p>Username: {username}</p><p>Password: {password}</p>"
    return render_template('login-test.html')

if __name__ == '__main__':
    app.run(debug=True)