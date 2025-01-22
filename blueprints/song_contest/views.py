# blueprints/song_contest/views.py

from flask import render_template
from .models import SongCountry, SongShow, SongShowCountry

# Function to register all the routes
def register_routes(song_contest_bp):
    """
    Registers routes for the song contest blueprint.
    :param song_contest_bp: The blueprint to register the routes with
    """
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
        
        # Ensure we handle the image attribute properly in the backend
        for country in countries:
            if country.image is None:
                country.image = ""  # Provide a default value or handle as appropriate
        
        return render_template('country_list.html', countries=countries)
    
    @song_contest_bp.route('/test_show')
    def test_show_list():
        shows = SongShow.query.all()
        return render_template('show_list.html', shows=shows)


    @song_contest_bp.route('/shows')
    def show_list():
        """List of shows."""
        shows = SongShow.query.all()  # Ensure shows are being fetched from the SongShow model
        print(shows)  # Log the result to confirm data is fetched
        return render_template('show_list.html', shows=shows)  # Render the show_list template
    
    @song_contest_bp.route('/show/<int:show_id>/countries')
    def show_countries(show_id):
        """Render a list of countries for a specific show."""
        # Join the SongShowCountry table to fetch the countries linked to the show
        countries = SongCountry.query.join(SongShowCountry).filter(SongShowCountry.showID == show_id).order_by(SongCountry.display_order.asc()).all()

        # Handle missing images by setting a default value
        for country in countries:
            if not country.image:
                country.image = "path/to/default/image.png"  # Set a default image path or URL if needed
        
        return render_template('country_list.html', countries=countries)

