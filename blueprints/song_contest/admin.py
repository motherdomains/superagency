# blueprints/song_contest/admin.py
from flask_admin.contrib.sqla import ModelView
from extensions import db
from .models import SongShow, SongCountry

# Admin Views for SongShow and SongCountry
class SongShowModelView(ModelView):
    column_list = ('showName', 'showDate', 'totalContestants', 'showDesc')
    form_excluded_columns = ('id',)  # Example of excluded columns
    column_formatters = {
        'showDate': lambda v, c, m, p: m.formatted_showDate()
    }

class SongCountryModelView(ModelView):
    column_list = ('country', 'status', 'display_order')
    form_excluded_columns = ('id',)  # Example of excluded columns

def register_admin_views(admin):
    admin.add_view(SongShowModelView(SongShow, db.session, name="Song Shows"))
    admin.add_view(SongCountryModelView(SongCountry, db.session, name="Song Countries"))