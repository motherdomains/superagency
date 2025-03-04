from flask import render_template, request, session, redirect, url_for, flash
from flask import current_app as app
from app import db  # Import from the main app file
from .models import SongCountry, SongShow, SongShowCountry
from sqlalchemy.orm import aliased


# Function to update votes in the database
def update_votes(show_id, vote_1, vote_2, vote_3):
    # Fetch the SongCountry rows for each vote
    country_1 = SongCountry.query.filter_by(countryID=vote_1).first()
    country_2 = SongCountry.query.filter_by(countryID=vote_2).first()
    country_3 = SongCountry.query.filter_by(countryID=vote_3).first()

    if not country_1 or not country_2 or not country_3:
        raise ValueError("One or more selected countries are invalid.")

    # Update the vote counts
    country_1.votesFirst += 1
    country_2.votesSecond += 1
    country_3.votesThird += 1

    # Commit changes to the database
    db.session.commit()


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
        countries = SongCountry.query.order_by(SongCountry.country.asc()).all()
        
        # Ensure we handle the image attribute properly in the backend
        for country in countries:
            if country.image is None:
                country.image = ""  # Provide a default value or handle as appropriate
        
        return render_template('country_list.html', countries=countries)

    # LIST OF SHOWS
    @song_contest_bp.route('/shows')
    def show_list():
        """List of shows."""
        shows = SongShow.query.all()  # Ensure shows are being fetched from the SongShow model
        print(shows)  # Log the result to confirm data is fetched
        return render_template('show_list.html', shows=shows)  # Render the show_list template
    
    # SELECT ASSIGNED COUNTRY
    @song_contest_bp.route('/show/<int:show_id>/countries')
    def show_countries(show_id):
        """Render a list of countries for a specific show."""
        # Join the SongShowCountry table to fetch the countries linked to the show
        countries = SongCountry.query.join(SongShowCountry).filter(SongShowCountry.showID == show_id).order_by(SongCountry.display_order.asc()).all()

        # Handle missing images by setting a default value
        for country in countries:
            if not country.image:
                country.image = "static/uploads/default.jpg"  # Set a default image path or URL if needed
        
        # Prepare the data for the template
        country_data = [(country.countryID, country.country, country.image) for country in countries]
    
        return render_template('select_country.html', countries=country_data, show_id=show_id)
    
    
    # VOTING SYSTEM
    @song_contest_bp.route('/vote/<int:show_id>/<int:assigned_country>', methods=['GET', 'POST'])
    def vote_page(show_id, assigned_country):
        # Fetch countries for the show, excluding the assigned country
        show_countries = SongShowCountry.query.filter(
            SongShowCountry.showID == show_id,
            SongShowCountry.countryID != assigned_country
        ).all()

        # Prepare country choices for the template
        countries = [(sc.countryID, sc.song_country.country) for sc in show_countries]

        if request.method == 'POST':
            try:
                # Ensure all votes are selected and valid
                vote_1 = int(request.form.get('vote_1'))
                vote_2 = int(request.form.get('vote_2'))
                vote_3 = int(request.form.get('vote_3'))
            except (TypeError, ValueError):
                # Handle invalid input (e.g., empty or non-integer values)
                flash("Invalid votes! Please ensure all votes are selected.", 'danger')
                return redirect(url_for('song_contest.vote_page', show_id=show_id, assigned_country=assigned_country))

            # Ensure no duplicate votes
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

        # Render the template with the correct variable
        return render_template('vote_page.html', countries=countries, assigned_country=assigned_country)
    
    # CONFIRM VOTE PAGE
    @song_contest_bp.route('/confirm_vote/<int:show_id>', methods=['GET', 'POST'])
    def confirm_vote(show_id):
        votes = session.get('votes', {})
        print(f"Votes from session: {votes}")
    
        # Query SongCountry for the country name and image for each vote
        country_1 = SongCountry.query.filter_by(countryID=votes.get('vote_1')).first()
        country_2 = SongCountry.query.filter_by(countryID=votes.get('vote_2')).first()
        country_3 = SongCountry.query.filter_by(countryID=votes.get('vote_3')).first()

        # If POST request, process the vote submission
        if request.method == 'POST':
            
            print("POST request received")  # Debug print
            
            try:
                # Retrieve the corresponding SongShowCountry rows for the show and countries
                song_show_country_1 = SongShowCountry.query.filter_by(showID=show_id, countryID=votes['vote_1']).first()
                song_show_country_2 = SongShowCountry.query.filter_by(showID=show_id, countryID=votes['vote_2']).first()
                song_show_country_3 = SongShowCountry.query.filter_by(showID=show_id, countryID=votes['vote_3']).first()

                # Update vote counts in the SongShowCountry table
                if song_show_country_1:
                    song_show_country_1.votesFirst += 1
                    print(f"Updated votesFirst: {song_show_country_1.votesFirst}")
                if song_show_country_2:
                    song_show_country_2.votesSecond += 1
                    print(f"Updated votesSecond: {song_show_country_2.votesSecond}")
                if song_show_country_3:
                    song_show_country_3.votesThird += 1
                    print(f"Updated votesThird: {song_show_country_3.votesThird}")

                    # Commit the changes to the database
                    db.session.commit()
                    print("Votes committed to the database")  # Debug print

                    # Mark that the user has voted
                    session['voted'] = True

                # Redirect to thank you page
                return redirect(url_for('song_contest.thank_you'))
            except Exception as e:
                print(f"Error processing vote: {e}")  # Debug print to capture any error
                flash(f"There was an error processing your vote: {e}", 'danger')

        # Pass the country data to the template
        return render_template('confirm_vote.html', 
                                votes=votes, 
                                country_1=country_1, 
                                country_2=country_2, 
                                country_3=country_3)
    
    # Post-voting Thank You results
    @song_contest_bp.route('/thank_you')
    def thank_you():
        return render_template('thank_you.html')
    
    # Function to fetch results from the database
    def get_show_results(show_id):
        results = db.session.query(
            SongShowCountry.countryID,
            SongCountry.country,
            SongShowCountry.showOrder,  # Include showOrder in the query
            SongShowCountry.votesFirst,
            SongShowCountry.votesSecond,
            SongShowCountry.votesThird
        ).join(
            SongCountry, SongShowCountry.countryID == SongCountry.countryID
        ).filter(
            SongShowCountry.showID == show_id
        ).all()

        # Debugging: Print the results to verify
        print("Fetched Results:", results)
        return results

    # Function to calculate grand totals
    def calculate_grand_totals(results):
        grand_totals = []
        for result in results:
            total = (result.votesFirst * 12) + (result.votesSecond * 8) + (result.votesThird * 5)
            grand_totals.append({
                'countryID': result.countryID,
                'country': result.country,
                'total': total,
                'votesFirst': result.votesFirst,  # Include 1st place votes
                'votesSecond': result.votesSecond,  # Include 2nd place votes
                'votesThird': result.votesThird,  # Include 3rd place votes
            })

        # Debugging: Print the grand totals
        print("Grand Totals:", grand_totals)
        return sorted(grand_totals, key=lambda x: x['total'], reverse=True)

    @song_contest_bp.route('/show/<int:show_id>/emcee_script')
    def generate_emcee_script(show_id):
        # Fetch results and calculate grand totals
        results = get_show_results(show_id)
        grand_totals = calculate_grand_totals(results)

        # Generate the emcee script
        script, leaderboard = generate_suspenseful_script(results, grand_totals)

        # Sort the leaderboard by total points in descending order
        sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)

        # Create a mapping of countryID to country name
        country_names = {result['countryID']: result['country'] for result in grand_totals}

        # Debug prints
        print("Script:", script)
        print("Leaderboard:", sorted_leaderboard)
        print("Country Names:", country_names)

        # Render the emcee script template
        return render_template('emcee_script.html', script=script, leaderboard=sorted_leaderboard, country_names=country_names)

    # Function to generate suspenseful emcee script
    def generate_suspenseful_script(results, grand_totals):
        script = []
        current_totals = {result['countryID']: 0 for result in grand_totals}  # Initialize current totals for each country

        # Create a mapping of countryID to country name
        country_names = {result['countryID']: result['country'] for result in grand_totals}

        # Sort results by showOrder (the order in which countries will announce their votes)
        sorted_results = sorted(results, key=lambda x: x.showOrder)

        # Track how many times each country has been mentioned
        mention_counts = {result['countryID']: 0 for result in grand_totals}

        for result in sorted_results:
            country_id = result.countryID
            country_name = result.country

            # Assign points to maintain suspense and ensure each country is mentioned exactly 3 times
            points = assign_points(country_id, current_totals, grand_totals, mention_counts)

            # Replace countryID with country name in the points dictionary
            points_with_names = {
                country_names[recipient_id]: value for recipient_id, value in points.items()
            }

            script.append({
                'country': country_name,
                'points': points_with_names
            })

            # Update current totals and mention counts
            for recipient_id, value in points.items():
                current_totals[recipient_id] += value
                mention_counts[recipient_id] += 1

        return script, current_totals

    # Function to assign points for suspenseful results
    def assign_points(country_id, current_totals, grand_totals, mention_counts):
        # Sort grand_totals by total points in descending order
        sorted_grand_totals = sorted(grand_totals, key=lambda x: x['total'], reverse=True)

        # Exclude the current country from the list of recipients
        eligible_recipients = [result for result in sorted_grand_totals if result['countryID'] != country_id]

        # Distribute points fairly while ensuring each country is mentioned exactly 3 times
        points = {}
        for i, recipient in enumerate(eligible_recipients):
            if mention_counts[recipient['countryID']] < 3:  # Ensure each country is mentioned exactly 3 times
                if i == 0:
                    points[recipient['countryID']] = 12  # 12 points for 1st place
                elif i == 1:
                    points[recipient['countryID']] = 8   # 8 points for 2nd place
                elif i == 2:
                    points[recipient['countryID']] = 5    # 5 points for 3rd place

        return points