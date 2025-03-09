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
<<<<<<< HEAD
=======
        
>>>>>>> 395f008 (Daily update: 2025-03-09)
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
    
<<<<<<< HEAD
=======
       # Function to adjust totals for "exciting" results
    def adjust_totals(grand_totals, audience_size):
        max_total = grand_totals[0]['total']
        scaling_factor = audience_size / max_total

        adjusted_totals = []
        for i, result in enumerate(grand_totals):
            adjusted_total = int((max_total - i) * scaling_factor)
            adjusted_totals.append({
                'countryID': result['countryID'],
                'country': result['country'],
                'adjusted_total': adjusted_total
            })
        # Debugging: Print the adjusted totals
        print("Adjusted Totals:", adjusted_totals)
        return adjusted_totals
>>>>>>> 395f008 (Daily update: 2025-03-09)
    
    # Internal voting results
    @song_contest_bp.route('/show/<int:show_id>/results')
    def display_results(show_id):
        # Fetch results and calculate grand totals
        results = get_show_results(show_id)
        grand_totals = calculate_grand_totals(results)
        # Get audience size (e.g., from the database or a configuration)
        audience_size = 100  # Example: Replace with actual audience size
        # Calculate adjusted totals
        adjusted_totals = adjust_totals(grand_totals, audience_size)
        # Combine grand_totals and adjusted_totals into a single list of dictionaries
        combined_results = []
        for grand, adjusted in zip(grand_totals, adjusted_totals):
            combined_results.append({
                'countryID': grand['countryID'],
                'country': grand['country'],
                'grand_total': grand['total'],
                'adjusted_total': adjusted['adjusted_total'],
                'votes_first': grand['votesFirst'],  # Add 1st place votes
                'votes_second': grand['votesSecond'],  # Add 2nd place votes
                'votes_third': grand['votesThird'],  # Add 3rd place votes
            })
        # Debugging: Print the final data being passed to the template
        print("Data Passed to Template:", combined_results)
        # Render the results template
        return render_template('results.html', results=combined_results)
    
    # Functions for results and emcee script
    def get_show_results(show_id):
        """Fetch results for a specific show."""
        results = db.session.query(
            SongShowCountry.countryID,
            SongCountry.country,
            SongShowCountry.showOrder,
            SongShowCountry.votesFirst,
            SongShowCountry.votesSecond,
            SongShowCountry.votesThird
        ).join(
            SongCountry, SongShowCountry.countryID == SongCountry.countryID
        ).filter(
            SongShowCountry.showID == show_id
        ).all()

        # Convert SQLAlchemy Row objects to tuples for simplicity
        return [(r.countryID, r.country, r.showOrder, r.votesFirst, r.votesSecond, r.votesThird) for r in results]


    def calculate_grand_totals(results):
        """Calculate grand totals for each country."""
        grand_totals = []
        for result in results:
            total = (result[3] * 12) + (result[4] * 8) + (result[5] * 5)
            grand_totals.append({
                'countryID': result[0],
                'country': result[1],
                'total': total,
                'votesFirst': result[3],
                'votesSecond': result[4],
                'votesThird': result[5],
            })

        # Sort by total points in descending order
        return sorted(grand_totals, key=lambda x: x['total'], reverse=True)


    def generate_suspenseful_script(results, grand_totals):
        """Generate the emcee script with suspenseful results."""
        script = []

        # Sort countries by showOrder (Country1 to Country7)
        sorted_by_show_order = sorted(results, key=lambda x: x[2])  # showOrder is at index 2

        # Sort countries by finishing position (Place1 to Place7)
        sorted_by_finishing_position = sorted(grand_totals, key=lambda x: x['total'], reverse=True)

        # Create a mapping of countryID to country name
        country_names = {result['countryID']: result['country'] for result in grand_totals}

        # Define the script rules
        script_rules = [
            {'12': 3, '8': 6, '5': 7},  # Country1
            {'12': 4, '8': 3, '5': 2},  # Country2
            {'12': 1, '8': 7, '5': 5},  # Country3
            {'12': 2, '8': 6, '5': 5},  # Country4
            {'12': 2, '8': 4, '5': 7},  # Country5
            {'12': 1, '8': 3, '5': 6},  # Country6
            {'12': 5, '8': 1, '5': 4},  # Country7
        ]

        # Create a preliminary array of points distributions
        preliminary_script = []
        for i, country in enumerate(sorted_by_show_order):
            country_id = country[0]  # countryID is at index 0
            country_name = country[1]  # country name is at index 1

            # Get the points distribution for this country
            rule = script_rules[i]
            points = []

            # Assign points based on the rule
            for points_value, place in rule.items():
                place_index = place - 1  # Convert to 0-based index
                recipient = sorted_by_finishing_position[place_index]

                # Ensure the recipient is not the same as the voting country
                if recipient['countryID'] != country_id:
                    points.append((int(points_value), recipient['country']))
                else:
                    # Mark this as a conflict
                    points.append(('conflict', (points_value, place_index)))

            preliminary_script.append({
                'country': country_name,
                'points': points
            })

        # Step 2: Assess conflicts
        conflicts = []
        for i, entry in enumerate(preliminary_script):
            for j, (points_value, recipient) in enumerate(entry['points']):
                if points_value == 'conflict':
                    conflicts.append((i, j, recipient))

        # Step 3: Resolve conflicts
        for conflict in conflicts:
            entry_index, point_index, (points_value, place_index) = conflict
            entry = preliminary_script[entry_index]
            country_id = sorted_by_show_order[entry_index][0]  # countryID is at index 0

            # Find a non-conflicting recipient
            for j in range(len(sorted_by_finishing_position)):
                if j != place_index and sorted_by_finishing_position[j]['countryID'] != country_id:
                    recipient = sorted_by_finishing_position[j]
                    entry['points'][point_index] = (int(points_value), recipient['country'])
                    break

        # Step 4: Regenerate the final script
        for entry in preliminary_script:
            script.append({
                'country': entry['country'],
                'points': sorted(entry['points'], key=lambda x: x[0], reverse=True)  # Sort by points value
            })

        return script


    def calculate_leaderboard(script, grand_totals):
        """Calculate the leaderboard based on the script."""
        leaderboard = {}
        for entry in script:
            for points_value, recipient in entry['points']:
                if recipient in leaderboard:
                    leaderboard[recipient] += points_value
                else:
                    leaderboard[recipient] = points_value

        # Sort the leaderboard by total points in descending order
        sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)

        # Ensure Contestant #1 has exactly 32 points
        if sorted_leaderboard[0][1] != 32:
            # Adjust points for Contestant #1
            sorted_leaderboard[0] = (sorted_leaderboard[0][0], 32)

            # Adjust points for the 2nd bottom team to break ties
            if len(sorted_leaderboard) >= 6:
                sorted_leaderboard[-2] = (sorted_leaderboard[-2][0], sorted_leaderboard[-2][1] + 1)

        return sorted_leaderboard

    # Emcee script for reading out the scores
    @song_contest_bp.route('/show/<int:show_id>/emcee_script')
    def generate_emcee_script(show_id):
        """Generate the emcee script and leaderboard."""
        # Fetch results and calculate grand totals
        results = get_show_results(show_id)
        grand_totals = calculate_grand_totals(results)

        # Generate the emcee script
        script = generate_suspenseful_script(results, grand_totals)

        # Calculate the leaderboard
        leaderboard = calculate_leaderboard(script, grand_totals)

        # Create a mapping of countryID to country name
        country_names = {result['countryID']: result['country'] for result in grand_totals}

        # Render the emcee script template
        return render_template('emcee_script.html', script=script, leaderboard=leaderboard, grand_totals=grand_totals, country_names=country_names)

