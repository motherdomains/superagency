from flask import Blueprint, render_template, request, redirect, url_for
from flask_admin.contrib.sqla import ModelView
from models import db
from models.song import Song  # Assuming you have a Song model for Song Contest
from models.show import Show  # Assuming you have a Show model for Song Contest

# Initialize the blueprint
song_contest_bp = Blueprint('song_contest', __name__, template_folder='templates')

# Register Song and Show models to Flask-Admin
class SongAdmin(ModelView):
    column_searchable_list = ['name', 'artist']
    form_columns = ['name', 'artist', 'show']

class ShowAdmin(ModelView):
    column_searchable_list = ['name', 'date']
    form_columns = ['name', 'date']

# Define route to show all songs and shows
@song_contest_bp.route('/songs')
def songs():
    songs = Song.query.all()
    return render_template('song_contest/songs.html', songs=songs)

@song_contest_bp.route('/shows')
def shows():
    shows = Show.query.all()
    return render_template('song_contest/shows.html', shows=shows)

# Add Song and Show models to admin views
def register_admin_views(admin):
    admin.add_view(SongAdmin(Song, db.session))
    admin.add_view(ShowAdmin(Show, db.session))