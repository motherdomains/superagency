from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import InputRequired, Email, Length
import logging
from logging.handlers import RotatingFileHandler

# Initialize Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object('config.Config')  # Ensure you have a config file or module
app.config['CACHE_TYPE'] = 'null'  # Disable caching during development
app.config['PROPAGATE_EXCEPTIONS'] = True  # Ensure exceptions propagate to Flask's error handling

# Set up detailed logging
handler = RotatingFileHandler('app.log', maxBytes=100000, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Flask-Admin setup
admin = Admin(app, name="Super Agency Admin", template_mode='bootstrap4')

# User model
class User(db.Model):
    __tablename__ = 'superTest'  # Change to match your table name
    superID = db.Column(db.Integer, primary_key=True)
    superName = db.Column(db.String(80), unique=True, nullable=False)
    superPassword = db.Column(db.String(120), nullable=False)
    superEmail = db.Column(db.String(60), nullable=False)
    superRole = db.Column(db.String(5), nullable=False)

# User form for creating new users
class UserForm(FlaskForm):
    superName = StringField('Username', validators=[InputRequired()])
    superPassword = PasswordField('Password', validators=[InputRequired()])
    superEmail = StringField('Email', validators=[InputRequired(), Email(), Length(max=60)])
    superRole = SelectField('Role', choices=[('admin', 'Admin'), ('user', 'User'), ('mod', 'Moderator')], validators=[InputRequired()])

# Custom ModelView for User
class UserAdmin(ModelView):
    # Exclude 'superPassword' from the list view
    column_exclude_list = ['superPassword']
    # Optionally, specify the default sorting for the list view
    column_default_sort = ('superName', True)
    form = UserForm  # Explicitly set the form for user management
    
    def create_form(self):
        form = super().create_form()
        form.superPassword.data = None  # Ensure the password field is empty on form load
        return form

    def on_model_change(self, form, model, is_created):
        # Handle password hashing on both creation and edit
        if is_created:
            # Hash the password when a new user is created
            model.superPassword = bcrypt.generate_password_hash(form.superPassword.data).decode('utf-8')
        else:
            # If the password is being updated, hash it
            if form.superPassword.data:
                model.superPassword = bcrypt.generate_password_hash(form.superPassword.data).decode('utf-8')
        return super().on_model_change(form, model, is_created)

# Add Flask-Admin views
admin.add_view(UserAdmin(User, db.session))

# Home Route
@app.route('/')
def home():
    username = session.get('username')
    greeting = f"Welcome back, {username}!" if username else "Please log in."
    app.logger.debug(f"Home route accessed. Greeting: {greeting}")
    return render_template('index.html', greeting=greeting)

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    app.logger.debug("Entered login route")
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        app.logger.debug(f"Login form submitted. Username: {username}, Password: {password}")

        # Fetch user from database
        user = User.query.filter_by(superName=username).first()
        if user:
            app.logger.debug(f"User found: {user.superName}")
            if bcrypt.check_password_hash(user.superPassword, password):
                session['user_id'] = user.superID
                session['username'] = user.superName
                flash(f'Welcome back, {user.superName}!', 'success')
                return redirect('/')
            else:
                app.logger.warning("Invalid credentials provided.")
                flash('Invalid credentials, please try again.', 'danger')
        else:
            app.logger.warning("User not found.")
            flash('User not found, please try again.', 'danger')
    return render_template('login.html', greeting="Logon to Super Agency")

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    app.logger.info("User logged out successfully.")
    flash("You have been logged out successfully.", "success")
    return redirect('/login')

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Add user to database
        new_user = User(superName=username, superPassword=hashed_password, superEmail=email, superRole='user')
        db.session.add(new_user)
        db.session.commit()

        app.logger.info(f"New user registered: {username}")
        flash('Account created successfully! You can now log in.', 'success')
        return redirect('/login')
    return render_template('register.html')

# Forgot Password Route
@app.route('/password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        app.logger.debug(f"Password reset requested for email: {email}")
        flash('A password reset link has been sent to your email.', 'info')
        return redirect('/login')
    return render_template('forgot_password.html')

# Print the URL map to verify routes
app.logger.debug(f"Registered routes: {app.url_map}")

if __name__ == '__main__':
    app.run(debug=True)