# song_contest/admin.py
from flask import url_for
from flask_admin.contrib.sqla import ModelView
from markupsafe import Markup
from extensions import db
from .models import SongShow, SongCountry

class SongShowAdmin(ModelView):
    form_columns = ('showName', 'showDate', 'totalContestants')  # Define the form columns
    column_list = ('showName', 'showDate', 'totalContestants')  # 'actions' column added
    column_display_pk = True

    # Formatter for custom columns
    column_formatters = {
        'showDate': lambda view, context, model, name: model.formatted_showDate(),  # Format date
    }


# Register admin views
def register_admin_views(admin):
    # Register the SongShow and SongCountry admin views
    admin.add_view(SongShowAdmin(SongShow, db.session, name="Shows"))
    admin.add_view(ModelView(SongCountry, db.session, name="Countries"))