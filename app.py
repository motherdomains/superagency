from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import InputRequired, Email, Length
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename
from logging.handlers import RotatingFileHandler
from config import Config  # Import configuration
import os
import logging

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

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

# User Model
class User(db.Model):
    __tablename__ = 'superTest'
    superID = db.Column(db.Integer, primary_key=True)
    superName = db.Column(db.String(80), unique=True, nullable=False)
    superPassword = db.Column(db.String(120), nullable=False)
    superEmail = db.Column(db.String(60), nullable=False)
    superRole = db.Column(db.String(5), nullable=False)

# Country Model
class Country(db.Model):
    __tablename__ = 'songCountry'
    countryID = db.Column(db.SmallInteger, primary_key=True)
    country = db.Column(db.String(60), nullable=False)
    image = db.Column(db.String(255), nullable=True)  # Stores the image URL
    status = db.Column(db.Enum('0', '1'), default='1', nullable=False)
    display_order = db.Column('display_order', db.SmallInteger, nullable=False, default=0)

# Country Admin Form
class CountryForm(FlaskForm):
    country = StringField('Country Name', validators=[InputRequired(), Length(max=60)])
    image = FileField('Image File', validators=[FileAllowed(Config.ALLOWED_EXTENSIONS, 'Images only!')])
    status = SelectField('Status', choices=[('1', 'Active'), ('0', 'Inactive')], validators=[InputRequired()])
#    display_order = StringField('Display Order', validators=[InputRequired()])

# User Admin Form
class UserForm(FlaskForm):
    superName = StringField('Username', validators=[InputRequired(), Length(max=80)])
    superEmail = StringField('Email', validators=[InputRequired(), Email(), Length(max=60)])
    superPassword = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    superRole = SelectField('Role', choices=[('admin', 'Admin'), ('user', 'User')], validators=[InputRequired()])

# Custom User Admin View
class UserAdmin(ModelView):
    form = UserForm
    column_list = ('superName', 'superEmail', 'superRole')
    column_default_sort = ('superName', True)
    column_display_pk = True

# Custom Country Admin View
class CountryAdmin(ModelView):
    form = CountryForm
    column_list = ('country', 'status')
    column_default_sort = ('display_order', True)
    column_display_pk = True

    # Format the 'status' field to display "Active" or "Hidden"
    column_formatters = {
        'status': lambda v, c, m, p: "Active" if m.status == '1' else "Hidden"
    }
    column_formatters_detail = column_formatters

    def on_model_change(self, form, model, is_created):
        """Handle file upload and save file URL."""
        uploaded_file = form.image.data
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(upload_path)
            model.image = url_for('uploaded_file', filename=filename, _external=True)
        return super().on_model_change(form, model, is_created)

# Admin Views
admin.add_view(UserAdmin(User, db.session))
admin.add_view(CountryAdmin(Country, db.session))

# Serve Uploaded Files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
    
# Check UPLOAD_FOLDER and ensure it exists
print("UPLOAD_FOLDER:", app.config['UPLOAD_FOLDER'])
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)