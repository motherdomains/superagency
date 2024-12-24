from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, DateField
from wtforms.validators import InputRequired, Email, Length
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename
from logging.handlers import RotatingFileHandler
import os
import logging
from datetime import datetime

# Import configuration
from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Blueprint management


# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Set up logging
handler = RotatingFileHandler(
    app.config['LOG_FILE'], 
    maxBytes=app.config['LOG_MAX_BYTES'], 
    backupCount=app.config['LOG_BACKUP_COUNT']
)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
admin = Admin(app, name="Super Agency Admin", template_mode='bootstrap4')

# Models
class User(db.Model):
    __tablename__ = 'superTest'
    superID = db.Column(db.Integer, primary_key=True)
    superName = db.Column(db.String(80), unique=True, nullable=False)
    superPassword = db.Column(db.String(120), nullable=False)
    superEmail = db.Column(db.String(60), nullable=False)
    superRole = db.Column(db.String(5), nullable=False)

class Country(db.Model):
    __tablename__ = 'songCountry'
    countryID = db.Column(db.SmallInteger, primary_key=True)
    country = db.Column(db.String(60), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Enum('0', '1'), default='1', nullable=False)
    display_order = db.Column('display_order', db.SmallInteger, nullable=False, default=0)

class SongShow(db.Model):
    __tablename__ = 'songShows'

    showID = db.Column(db.Integer, primary_key=True)
    showName = db.Column(db.String(255), nullable=False)
    showDesc = db.Column(db.Text, nullable=True)
    showDate = db.Column(db.Date, nullable=False)
    totalContestants = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<SongShow {self.showName}>"

    # Method to format showDate
    def formatted_showDate(self):
        return self.showDate.strftime('%d %B %Y')

# Forms
class UserForm(FlaskForm):
    superName = StringField('Username', validators=[InputRequired(), Length(max=80)])
    superEmail = StringField('Email', validators=[InputRequired(), Email(), Length(max=60)])
    superPassword = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    superRole = SelectField('Role', choices=[('admin', 'Admin'), ('user', 'User'), ('mod', 'Moderator')], validators=[InputRequired()])

class LoginForm(FlaskForm):
    superName = StringField('Username', validators=[InputRequired(), Length(max=80)])
    superPassword = PasswordField('Password', validators=[InputRequired()])

class CountryForm(FlaskForm):
    country = StringField('Country Name', validators=[InputRequired(), Length(max=60)])
    image = FileField('Image File', validators=[FileAllowed(Config.ALLOWED_EXTENSIONS, 'Images only!')])
    status = SelectField('Status', choices=[('1', 'Active'), ('0', 'Inactive')], validators=[InputRequired()])

class SongShowForm(FlaskForm):
    showName = StringField('Show Name', validators=[InputRequired()])
    showDesc = StringField('Description')
    showDate = DateField('Show Date', format='%Y-%m-%d', validators=[InputRequired()])
    totalContestants = SelectField('Total Contestants', choices=[(str(i), str(i)) for i in range(6, 13)], coerce=int, validators=[InputRequired()])

# Admin Views
class UserAdmin(ModelView):
    column_list = ('superName', 'superEmail', 'superRole')
    column_display_pk = True
    form = UserForm

    def on_model_change(self, form, model, is_created):
        if is_created and form.superPassword.data:
            model.superPassword = bcrypt.generate_password_hash(form.superPassword.data).decode('utf-8')
        return super().on_model_change(form, model, is_created)

class CountryAdmin(ModelView):
    form = CountryForm
    column_list = ('country', 'status')
    column_display_pk = True

    def on_model_change(self, form, model, is_created):
        uploaded_file = form.image.data
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(upload_path)
            model.image = url_for('uploaded_file', filename=filename, _external=True)
        return super().on_model_change(form, model, is_created)

class SongShowAdmin(ModelView):
    form = SongShowForm
    column_list = ('showName', 'showDate', 'totalContestants')  # Simplified columns
    column_display_pk = True

    # Display showDate in "Day Month Year" format
    column_formatters = {
        'showDate': lambda v, c, m, p: m.formatted_showDate()  # Format showDate
    }
    # Custom column labels
    column_labels = {
        'showName': 'Show Name',
        'showDate': 'Show Date',
        'totalContestants': 'Contestants'
    }

# Add Admin Views
admin.add_view(UserAdmin(User, db.session))
admin.add_view(CountryAdmin(Country, db.session))
admin.add_view(SongShowAdmin(SongShow, db.session))

# Routes
@app.route('/')
def home():
    username = session.get('username')
    greeting = f"Welcome back, {username}!" if username else "Please log in."
    return render_template('home.html', greeting=greeting, title="Home")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.superPassword.data).decode('utf-8')
        user = User(
            superName=form.superName.data, 
            superEmail=form.superEmail.data, 
            superPassword=hashed_password, 
            superRole='user'
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, title="Register")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(superName=form.superName.data).first()
        if user and bcrypt.check_password_hash(user.superPassword, form.superPassword.data):
            session['user_id'] = user.superID
            session['username'] = user.superName
            flash(f'Welcome {user.superName}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')
    return render_template('login.html', form=form, title="Login")

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Check UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Run Flask App
if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])