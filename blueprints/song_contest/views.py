# blueprints/song_contest/views.py

from flask import render_template, request, session, redirect, url_for, flash
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
    
    
    # VOTING SYSTEM
    
    @song_contest_bp.route('/select_country/<int:show_id>', methods=['GET'])
    def select_country(show_id):
        # Fetch countries for the current show
        show_countries = SongShowCountry.query.filter_by(showID=show_id).all()
        country_choices = [(sc.countryID, sc.song_country.country, sc.song_country.image) for sc in show_countries]
        
        print(country_choices)  # Add this line before rendering the template
        return render_template('select_country.html', countries=country_choices, show_id=show_id)
    
    @song_contest_bp.route('/vote/<int:show_id>/<int:assigned_country>', methods=['GET', 'POST'])
    def vote_page(show_id, assigned_country):
        # Fetch countries for the show, excluding the assigned country
        show_countries = SongShowCountry.query.filter(
            SongShowCountry.showID == show_id,
            SongShowCountry.countryID != assigned_country
        ).all()
    
        country_choices = [(sc.countryID, sc.song_country.country) for sc in show_countries]
    
        if request.method == 'POST':
            vote_1 = int(request.form.get('vote_1'))
            vote_2 = int(request.form.get('vote_2'))
            vote_3 = int(request.form.get('vote_3'))

            # Ensure valid votes
            if len({vote_1, vote_2, vote_3}) != 3:
                flash("Invalid votes! Please ensure no duplicate selections.", 'danger')
                return redirect(url_for('song_contest.vote_page', show_id=show_id, assigned_country=assigned_country))
        
            # Store votes temporarily in session
            session['votes'] = {
                'assigned_country': assigned_country,
                'vote_1': vote_1,
                'vote_2': vote_2,
                'vote_3': vote_3,
            }
            return redirect(url_for('song_contest.confirm_vote', show_id=show_id))
    
        return render_template('vote_page.html', countries=country_choices, assigned_country=assigned_country)
    
    @song_contest_bp.route('/confirm_vote/<int:show_id>', methods=['GET', 'POST'])
    def confirm_vote(show_id):
        votes = session.get('votes', {})
    
        # Query SongCountry for the country name and image for each vote
        country_1 = SongCountry.query.filter_by(countryID=votes.get('vote_1')).first()
        country_2 = SongCountry.query.filter_by(countryID=votes.get('vote_2')).first()
        country_3 = SongCountry.query.filter_by(countryID=votes.get('vote_3')).first()

        if request.method == 'POST':
            try:
                update_votes(show_id, votes['vote_1'], votes['vote_2'], votes['vote_3'])
                session['voted'] = True
                return redirect(url_for('song_contest.thank_you'))
            except:
                flash("There was an error processing your vote. Please try again.", 'danger')

        # Pass the country data to the template
        return render_template('confirm_vote.html', 
                               votes=votes, 
                               country_1=country_1, 
                               country_2=country_2, 
                               country_3=country_3)
    
    @song_contest_bp.route('/thank_you')
    def thank_you():
        return render_template('thank_you.html')