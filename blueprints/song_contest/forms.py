# blueprints/song_contest/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField
from wtforms.validators import InputRequired, Length
from flask_wtf.file import FileField, FileAllowed
from config.config import Config

class CountryForm(FlaskForm):
    country = StringField('Country Name', validators=[InputRequired(), Length(max=60)])
    image = FileField('Image File', validators=[FileAllowed(Config.ALLOWED_EXTENSIONS, 'Images only!')])
    status = SelectField('Status', choices=[('1', 'Active'), ('0', 'Inactive')], validators=[InputRequired()])

class SongShowForm(FlaskForm):
    showName = StringField('Show Name', validators=[InputRequired()])
    showDesc = StringField('Description')
    showDate = DateField('Show Date', format='%Y-%m-%d', validators=[InputRequired()])
    totalContestants = SelectField('Total Contestants', choices=[(str(i), str(i)) for i in range(6, 13)], coerce=int, validators=[InputRequired()])