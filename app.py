from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import logging
from logging.handlers import RotatingFileHandler


# Initialize Flask app from configuration
app = Flask(__name__)
app.config.from_object('config.Config')
app.config['CACHE_TYPE'] = 'null'  # Disable caching (temp during dev)
app.config['PROPAGATE_EXCEPTIONS'] = True  # Ensure exceptions propagate to Flask's error handling

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
    superEmail = db.Column(db.String(60), nullable=False)
    superRole = db.Column(db.String(5), nullable=False)
    
# check if logged in    
#logged_in = 'user_id' in session

# Home Route
@app.route('/')
def home():
    username = session.get('username')
    if username:
        return render_template('index.html', greeting=f"Welcome back, {username}!")
    else:
        return render_template('index.html', greeting=f"Please log in.")
    
#@app.route('/users', methods=['GET'])
#def users():
#    return "Users route is working"

#@app.route('/test', methods=['GET'])
#def test():
#    return "Test route is working"
    
# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
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
                return redirect('/')
            else:
                flash('Invalid credentials, please try again.', 'danger')
                #return f"<h1>Invalid credentials</h1>"
                return render_template('login.html', greeting=f"Invalid credentials, please try again.")
        else:
            flash('User not found, please try again.', 'danger')
            #return f"<h1>User not found</h1>"
            return render_template('login.html', greeting=f"User not found, please try again.")
        
        #return f"<h1>Form submitted!</h1><p>Username: {username}</p><p>Password: {password}</p>"
    return render_template('login.html', greeting=f"Logon to Super Agency")

# Logout route
@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    
    # Flash a confirmation message
    flash("You have been logged out successfully.", "success")
    
    # Redirect to the login page
    return redirect('/login')

# Register Route
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
        return redirect('/login')
    return render_template('register.html')

# Forgot Password Route
@app.route('/password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        flash('A password reset link has been sent to your email.', 'info')
        return redirect('/login')
    return render_template('forgot_password.html')

# Admin route to view and manage users (add admin later)
@app.route('/users', methods=['GET'])
def users():
    #return "Users route is working... again. But no template. Again.xxxxx"
    app.logger.debug("Fetching user data...")

    # Fetch all users from the database, ordered alphabetically by superName
    users = User.query.order_by(User.superName.asc()).all()
    
    app.logger.debug(f"Rendering user list with {len(users)} users.")
    #return "Rendering user list with {len(users)} users."
    
    # Render the admin users template
    return render_template('user_list.html', users=users)

#@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
#def edit_user(user_id):
#    user = User.query.get_or_404(user_id)
#    if request.method == 'POST':
#        user.superName = request.form['username']
#        user.superEmail = request.form['email']
#        user.superRole = request.form['role']
#        db.session.commit()
#        flash('User updated successfully!', 'success')
#        return redirect(url_for('users'))
#    return render_template('edit_user.html', user=user)


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
    
# Print the URL map to verify routes
print("Registered routes:")
print(app.url_map)
