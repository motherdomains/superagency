# blueprints/song_contest/views.py
from flask import Blueprint, render_template, request
from blueprints.song_contest.models import SongCountry, SongShow
from blueprints.song_contest.forms import CountryForm, SongShowForm
from flask_admin.contrib.sqla import ModelView
from extensions import db

song_contest_bp = Blueprint('song_contest', __name__)

# Views for Country and Song Show models
class SongCountryAdmin(ModelView):
    form = CountryForm
    column_list = ('country', 'status')
    column_display_pk = True

class SongShowAdmin(ModelView):
    form = SongShowForm
    column_list = ('showName', 'showDate', 'totalContestants')
    column_display_pk = True
    column_formatters = {'showDate': lambda v, c, m, p: m.formatted_showDate()}

# Register admin views for Song Contest
def register_admin_views(admin):
    admin.add_view(SongCountryAdmin(SongCountry, db.session))
    admin.add_view(SongShowAdmin(SongShow, db.session))

# Routes for Song Contest
@song_contest_bp.route('/')
def show_list():
    shows = SongShow.query.all()
    return render_template('song_contest/show_list.html', shows=shows)