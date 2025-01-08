from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import logging
from logging.handlers import RotatingFileHandler

# Initialize Flask app from configuration
app = Flask(__name__)
app.config.from_object('config.Config')

# Set up logging
logging.basicConfig(level=logging.DEBUG)
handler = logging.StreamHandler()
app.logger.addHandler(handler)

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# User model
class User(db.Model):
    __tablename__ = 'superTest'  # Change to match your table name
    superID = db.Column(db.Integer, primary_key=True)
    superName = db.Column(db.String(80), unique=True, nullable=False)
    superPassword = db.Column(db.String(120), nullable=False)
    
# Login Route
@app.route('/login-test', methods=['GET', 'POST'])
def login_test():
    app.logger.debug("Entered login route")  # Confirm we're hitting the login route
    if request.method == 'POST':
        app.logger.debug(f"Form submitted with method: {request.method}")
        username = request.form.get('username')
        password = request.form.get('password')
        app.logger.debug(f"Username: {username}, Password: {password}")  # Log form data

        # Test database connection and query
        # try:
        test_user = User.query.first()
        app.logger.debug(f"First user in database: {test_user.superName if test_user else 'No users found'}")
        # except Exception as e:
        #app.logger.error(f"Database error: {str(e)}")

        # Fetch user from database
        user = User.query.filter_by(superName=username).first()
        if user:
            app.logger.debug(f"User found: {user.superName}")
            if bcrypt.check_password_hash(user.superPassword, password):
                session['user_id'] = user.superID
                session['username'] = user.superName
                flash(f'Welcome back, {user.superName}!', 'success')
                #return f"<h1>Form submitted!</h1><p>Username: {username}</p><p>Password: {password}</p>"
                #return render_template('login-test.html')
                return redirect('/home')
            else:
                flash('Invalid credentials, please try again.', 'danger')
                return f"<h1>Invalid credentials</h1>"
        else:
            flash('User not found, please try again.', 'danger')
            return f"<h1>User not found</h1>"
        
        #return f"<h1>Form submitted!</h1><p>Username: {username}</p><p>Password: {password}</p>"
    return render_template('login-test.html')


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
    
# Print the URL map to verify routes
print("Registered routes:")
print(app.url_map)
