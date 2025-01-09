from flask import Blueprint, render_template
from blueprints.song_contest.models import SongCountry, SongShow
from blueprints.song_contest.forms import CountryForm, SongShowForm
from flask_admin.contrib.sqla import ModelView
from extensions import db

# Initialize Blueprint
song_contest_bp = Blueprint('song_contest', __name__, template_folder='templates')  # Use the main templates folder

# Admin views for Song Contest models
class SongCountryAdmin(ModelView):
    form = CountryForm
    column_list = ('country', 'status', 'display_order')
    column_display_pk = True

class SongShowAdmin(ModelView):
    form = SongShowForm
    column_list = ('showName', 'showDate', 'totalContestants')
    column_display_pk = True
    column_formatters = {
        'showDate': lambda view, context, model, name: model.formatted_showDate()
    }

# Function to register admin views
def register_admin_views(admin):
    """Registers the Song Contest admin views."""
    admin.add_view(SongCountryAdmin(SongCountry, db.session, name="Countries"))
    admin.add_view(SongShowAdmin(SongShow, db.session, name="Shows"))

# Routes for Song Contest

# Route for listing all shows
#@song_contest_bp.route('/')
#def show_list():
#    """Render a list of song shows."""
#    shows = SongShow.query.order_by(SongShow.showDate.desc()).all()
#    return render_template('show_list.html', shows=shows)  # Templates are now in the main #'templates' folder

# Route for listing all countries
@song_contest_bp.route('/countries', endpoint='country_list')
def country_list():
    """Render a list of countries."""
    countries = SongCountry.query.order_by(SongCountry.display_order.asc()).all()
    return render_template('country_list.html', countries=countries)  # Templates are now in the main 'templates' folder