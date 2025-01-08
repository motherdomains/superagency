# blueprints/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, DateField
from wtforms.validators import InputRequired, Email, Length
from flask_wtf.file import FileField, FileAllowed
from config.config import Config

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