# blueprints/song_contest/views.py
from flask import render_template, request, redirect, url_for, flash
from extensions import db
from .models import SongCountry, SongShow, SongShowCountry  # Ensure SongShowCountry is imported
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

@song_contest_bp.route('/add_countries/<int:showID>', methods=['GET', 'POST'], endpoint='add_countries_to_show')
def add_countries_to_show(showID):
    """Route to add countries to the selected show."""
    show = SongShow.query.get_or_404(showID)  # Get the show
    countries = SongCountry.query.all()  # List of all available countries
    
    if request.method == 'POST':
        selected_countries = request.form.getlist('countries')  # Get selected countries from form
        for countryID in selected_countries:
            song_country = SongCountry.query.get(countryID)
            if song_country:
                # Add the country to the show using the SongShowCountry relationship
                show_country = SongShowCountry(showID=showID, countryID=countryID)
                db.session.add(show_country)
        db.session.commit()  # Commit the transaction
        flash('Countries successfully added to the show!', 'success')

        # Debugging: Print the URL that is being generated
        print(f"Redirecting to URL for showID={showID}: {url_for('song_contest.add_countries_to_show', showID=showID)}")
        return redirect(url_for('song_contest.add_countries_to_show', showID=showID))

    return render_template('add_countries_to_show.html', show=show, countries=countries)  # Render the form to add countries