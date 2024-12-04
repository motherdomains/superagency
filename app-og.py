from flask import Flask, render_template, request, redirect, url_for

# Initialize Flask app only once
app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return render_template('index.html',pagetitle='Home Welcome')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Basic login check (replace with real validation)
        if username == 'admin' and password == 'password':
            return redirect(url_for('home'))
        return "Invalid credentials, try again."
    return render_template('login.html')

# Enable auto-reload for templates
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Run the app in debug mode
if __name__ == '__main__':
    app.run(debug=True)  # Enable debug mode for the server

# Print the URL map to verify routes
# print(app.url_map)
