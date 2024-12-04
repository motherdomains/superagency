from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from config import Config
import mysql.connector

# Initialize Flask app from configuration
app = Flask(__name__)
app.config.from_object(Config)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/users.db'  # Using SQLite for now
#app.config['SECRET_KEY'] = 'your_secret_key'  # Required for Flask-Admin and Flash messages
#app.config['TEMPLATES_AUTO_RELOAD'] = True
#app.config['DEBUG'] = True  # Explicitly enable debug mode

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Test connection
with app.app_context():
    db.create_all()  # Creates tables if they don’t exist

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # Role for admin/user differentiation

# Flask-Admin setup
admin = Admin(app, name='Super Agency Admin', template_mode='bootstrap4')
admin.add_view(ModelView(User, db.session))  # Add User model to admin interface


#### APP TEST - TEMP
@app.route('/test', methods=['GET', 'POST'])
def test():
    # Execute raw SQL
    result = db.session.execute("SELECT superName, superEmail FROM superTest LIMIT 1").fetchone()
    
    if result:
        # Extract fields from the query result
        super_name, super_email = result
        return render_template('test.html', super_name=super_name, super_email=super_email)
    else:
        return "No data found in the table."


# Route: Home
@app.route('/')
def home():
    return render_template('index.html')

# Route: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        flash('Invalid credentials, please try again.', 'danger')
    return render_template('login.html')

# Route: Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Add user to database
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# For Debug Mode
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created
    app.run(debug=True)  # Enable debug mode only for the server

# Print the URL map to verify routes
print("Registered routes:")
print(app.url_map)
