from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import InputRequired, Email, Length

class UserForm(FlaskForm):
    superName = StringField('Username', validators=[InputRequired(), Length(max=80)])
    superEmail = StringField('Email', validators=[InputRequired(), Email(), Length(max=60)])
    superPassword = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    superRole = SelectField('Role', choices=[('admin', 'Admin'), ('user', 'User'), ('mod', 'Moderator')], validators=[InputRequired()])

class LoginForm(FlaskForm):
    superName = StringField('Username', validators=[InputRequired(), Length(max=80)])
    superPassword = PasswordField('Password', validators=[InputRequired()])