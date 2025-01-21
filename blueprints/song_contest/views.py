from flask import render_template, request, redirect, url_for, flash
from extensions import db
from .models import SongCountry, SongShow  # Removed SongShowCountry since it's no longer needed
from . import song_contest_bp  # Import the blueprint from the current package (no circular import)

# Routes for Song Contest

@song_contest_bp.route('/')
def song_contest_home():
    return render_template('song_contest_home.html')  # Ensure this template exists

@song_contest_bp.route('/test')
def test_route():
    return "Song Contest Blueprint is working!"

@song_contest_bp.route('/countries', endpoint='country_list')
def country_list():
    """Render a list of countries."""
    countries = SongCountry.query.order_by(SongCountry.display_order.asc()).all()
    return render_template('country_list.html', countries=countries)
