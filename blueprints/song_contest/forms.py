# blueprints/song_contest/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField
from wtforms.validators import InputRequired, Length
from flask_wtf.file import FileField, FileAllowed
from config.config import Config

class CountryForm(FlaskForm):
    """
    Form for creating and editing countries.
    """
    country = StringField('Country Name', validators=[InputRequired(), Length(max=60)])
    image = FileField('Image File', validators=[FileAllowed(Config.ALLOWED_EXTENSIONS, 'Images only!')])

    # Leave as a 2-tuple, the default expected format for Flask-Admin
    status = SelectField(
        'Status', 
        choices=[('1', 'Active'), ('0', 'Inactive')],  # Two values: (value, label)
        validators=[InputRequired()]
    )

class SongShowForm(FlaskForm):
    """
    Form for creating and editing Song Shows.
    """
    showName = StringField('Show Name', validators=[InputRequired()])
    showDesc = StringField('Description', validators=[Length(max=255)])  # Added a length validator
    showDate = DateField('Show Date', format='%Y-%m-%d', validators=[InputRequired()])
    totalContestants = SelectField(
        'Total Contestants', 
        choices=[(str(i), str(i)) for i in range(6, 13)],  # Correctly pass two values (value, label)
        coerce=int, 
        validators=[InputRequired()]
    )