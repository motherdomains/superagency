from flask import url_for
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from markupsafe import Markup
from blueprints.song_contest.models import SongShow, SongCountry
from extensions import db
from .forms import SongShowForm  # Ensure this is imported correctly

class SongShowAdmin(ModelView):
    form = SongShowForm
    column_list = ('showName', 'showDate', 'totalContestants', 'actions')  # Added 'actions' column
    column_display_pk = True

    column_formatters = {
        'showDate': lambda view, context, model, name: model.formatted_showDate(),
    }

    # Custom method to render 'actions' column
    def _render_actions(self, context, model, name):
        """Ensure the 'actions' column renders a clickable link."""
        # Ensure the URL is being generated correctly
        link = url_for('song_contest.add_countries_to_show', showID=model.showID)
        return Markup(f'<a href="{link}">Add Countries</a>')

    # Overriding 'actions' column to use custom render method
    column_formatters['actions'] = _render_actions

    # Optional: Show countries in the SongShow view
    column_formatters.update({
        'countries': lambda view, context, model, name: ', '.join([country.song_country.country for country in model.songShowCountries])
    })

# Function to register admin views
def register_admin_views(admin):
    """Registers the Song Contest admin views."""
    admin.add_view(SongShowAdmin(SongShow, db.session, name="Shows"))
    admin.add_view(SongCountryAdmin(SongCountry, db.session, name="Countries"))