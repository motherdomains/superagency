from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from extensions import db
from .models import SongShow, SongCountry  # Import the models

class SongShowModelView(ModelView):
    column_list = ('name', 'artist', 'country', 'date')  # Example fields

class SongCountryModelView(ModelView):
    column_list = ('name', 'code')  # Example fields

def register_admin_views(app):
    with app.app_context():  # Ensure the app context is available
        admin = Admin(app, name='Song Contest Admin', template_mode='bootstrap3')
        admin.add_view(SongShowModelView(SongShow, db.session, name="Song Shows"))
        admin.add_view(SongCountryModelView(SongCountry, db.session, name="Song Countries"))