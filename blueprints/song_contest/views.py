from flask import render_template, request, session, redirect, url_for, flash
from flask import current_app as app
from extensions import db
from .models import SongCountry, SongShow, SongShowCountry, SongShowVotes
from sqlalchemy.orm import aliased
from functools import wraps  # For admin authentication
from datetime import datetime

# Make sure to have PuLP installed in your environment:
from pulp import LpProblem, LpVariable, LpBinary, lpSum, LpStatus, value, LpMinimize

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

    # Home Route
    @song_contest_bp.route('/')
    def song_contest_home():
        return render_template('song_contest_home.html')  # Ensure this template exists
    
    # Admin authentication decorator
    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get("is_admin") is not True:  # Ensure admin is logged in
                flash("Access Denied! Admins only.", "danger")
                return redirect(url_for("song_contest.admin_login"))
            return f(*args, **kwargs)
        return decorated_function
    

    # Admin dashboard
    @song_contest_bp.route('/admin')
    @admin_required
    def admin_dashboard():
        """Admin dashboard for managing shows and voting status."""

        today = datetime.today().date()

        # Fetch only upcoming and current shows
        shows = SongShow.query.filter(SongShow.showDate >= today).order_by(SongShow.showDate.asc()).all()

        # Check if results exist for each show
        for show in shows:
            show.has_results = db.session.query(SongShowVotes).filter_by(showID=show.showID).first() is not None

        return render_template("admin_dashboard.html", shows=shows)
    

    # Admin login page
    @song_contest_bp.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            password = request.form.get("password")
            if password == "superSHOW25!":  # Set a strong password!
                session["is_admin"] = True
                flash("Admin login successful!", "success")
                return redirect(url_for("song_contest.admin_dashboard"))
            else:
                flash("Incorrect password!", "danger")

        return render_template("admin_login.html")

    # Admin logout
    @song_contest_bp.route('/admin/logout')
    def admin_logout():
        session.pop("is_admin", None)
        flash("Logged out successfully!", "info")
        return redirect(url_for("song_contest.admin_login"))
   
    # VOTING LOCK / UNLOCK
    @song_contest_bp.route('/show/<int:show_id>/change_voting_status/<int:status>', methods=['POST'])
    @admin_required
    def change_voting_status(show_id, status):
        """Allows admins to lock/unlock voting for a show."""

        # Fetch the show
        show = SongShow.query.get_or_404(show_id)

        # Update voting status (0 = Locked, 1 = Open, 2 = Final Lock)
        show.voting_status = status
        db.session.commit()

        flash("Voting status updated!", "success")
        return redirect(url_for('song_contest.admin_dashboard'))
    
    
    # UNDO FINAL LOCK (ADMIN OVERRIDE)
    @song_contest_bp.route('/show/<int:show_id>/undo_final_lock', methods=['POST'])
    @admin_required
    def undo_final_lock(show_id):
        """Allows admins to undo the final voting lock and re-open voting."""

        # Fetch the show
        show = SongShow.query.get_or_404(show_id)

        # Ensure show is in final lock state
        if show.voting_status != 2:
            flash("Voting is not in a final locked state!", "danger")
            return redirect(url_for('song_contest.admin_dashboard'))

        # Reset status to 1 (Re-open voting)
        show.voting_status = 1
        db.session.commit()

        flash("Final lock undone! Voting is now open again.", "success")
        return redirect(url_for('song_contest.admin_dashboard'))


    # Reset votes for a specific show
    @song_contest_bp.route('/admin/reset_votes/<int:show_id>', methods=['POST'])
    @admin_required
    def reset_votes(show_id):
        """Resets all votes for a show and locks voting (voting_status = 0)."""
        try:
            # Reset all vote counts
            db.session.query(SongShowCountry).filter(SongShowCountry.showID == show_id).update({
                "votesFirst": 0,
                "votesSecond": 0,
                "votesThird": 0
            })

            # Optionally reset voting status to 0 (Pre-voting Locked)
            show = SongShow.query.get_or_404(show_id)
            show.voting_status = 0  # Lock voting

            db.session.commit()

            flash(f"✅ Successfully reset votes and locked voting for Show ID {show_id}!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Error resetting votes: {e}", "danger")

        return redirect(url_for("song_contest.admin_dashboard"))
    
    # RETURN TO PRE-OPEN VOTING
    @song_contest_bp.route('/show/<int:show_id>/return_to_preopen', methods=['POST'])
    @admin_required
    def return_to_preopen(show_id):
        """
        Returns a show from Voting Open (voting_status == 1) to the pre-open state (voting_status = 0).
        This allows admins to revert a show back to locked state without resetting votes.
        """
        try:
            show = SongShow.query.get_or_404(show_id)
            if show.voting_status != 1:
                flash("Show is not in a Voting Open state.", "danger")
            else:
                show.voting_status = 0  # Revert to pre-open (locked)
                db.session.commit()
                flash("Show has been returned to pre-open (voting locked) state.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating show state: {e}", "danger")
        return redirect(url_for("song_contest.admin_dashboard"))


    
    # GENERATE LIVE SCOREBOARD
    import json

    # GENERATE LIVE SCOREBOARD
    @song_contest_bp.route('/show/<int:show_id>/scoreboard')
    def live_scoreboard(show_id):
        """
        Display the scoreboard using a cumulative-sum approach.
        On first visit (session index == -1) all scores are 0.
        Each press of NEXT increments the session index by one,
        and the cumulative votes (from index 0 to current index) are summed.
        """
        # Fetch the show and ensure voting is locked
        show = SongShow.query.get_or_404(show_id)
        if show.voting_status != 2:
            flash("Scoreboard is only available after voting is closed!", "danger")
            return redirect(url_for('song_contest.admin_dashboard'))

        # Retrieve all participating countries in showOrder
        show_countries = (SongShowCountry.query
                          .join(SongCountry)
                          .filter(SongShowCountry.showID == show_id)
                          .order_by(SongShowCountry.showOrder.asc())
                          .all())

        # Build a blank scores dictionary (keys are countryID, values start at 0)
        blank_scores = {sc.countryID: 0 for sc in show_countries}

        # Use a session key to store the vote index (i.e. the number of vote rounds processed)
        progress_key = f'scoreboard_progress_{show_id}'

        # On first visit or when reset is requested, clear session and set index to -1
        if progress_key not in session or request.args.get("reset") == "1":
            session.clear()
            session[progress_key] = -1  # -1 indicates "no votes processed"
            print("DEBUG: Session reset - starting with blank scoreboard")

        # Always convert the session index to an integer
        current_index = int(session.get(progress_key, -1))

        # Fetch the entire vote_results list from the database
        vote_results = SongShowVotes.query.filter_by(showID=show_id).all()
        total_votes = len(vote_results)

        # If the session index is -1, then display a blank scoreboard (all scores 0)
        if current_index == -1:
            print(f"DEBUG: First visit - displaying blank scoreboard for show {show_id}")
            leaderboard = [{
                "country": sc.song_country.country,
                "image": sc.song_country.image if sc.song_country.image else "static/uploads/default.jpg",
                "score": 0
            } for sc in show_countries]
            return render_template('scoreboard.html', 
                                   show_id=show_id, 
                                   leaderboard=leaderboard, 
                                   vote_results=[], 
                                   current_index=current_index,
                                   total_steps=total_votes)

        # Otherwise, recalculate cumulative scores from vote index 0 to current_index (inclusive)
        cumulative_scores = blank_scores.copy()
        vote_history = []
        # Process votes 0 through current_index
        for i in range(current_index + 1):
            if i < total_votes:
                vote = vote_results[i]
                cumulative_scores[vote.recipient_12] += 12
                cumulative_scores[vote.recipient_10] += 10
                cumulative_scores[vote.recipient_8]  += 8
                vote_history.append({
                    "country": vote.awarding_country.country,
                    "votes": [
                        (12, vote.recipient_12_country.country),
                        (10, vote.recipient_10_country.country),
                        (8, vote.recipient_8_country.country)
                    ]
                })

        # Build the leaderboard by sorting countries by their cumulative score (highest first)
        leaderboard = sorted([
            {
                "country": sc.song_country.country,
                "image": sc.song_country.image if sc.song_country.image else "static/uploads/default.jpg",
                "score": cumulative_scores.get(sc.countryID, 0)
            } for sc in show_countries
        ], key=lambda x: x["score"], reverse=True)

        print(f"DEBUG: Cumulative Scores (show {show_id}) after processing {current_index+1} votes: {cumulative_scores}")
        print(f"DEBUG: Session Scoreboard Progress (show {show_id}): {current_index}")

        return render_template('scoreboard.html', 
                               show_id=show_id, 
                               leaderboard=leaderboard, 
                               vote_results=vote_history, 
                               current_index=current_index, 
                               total_steps=total_votes)


    # NEXT BUTTON ROUTE
    @song_contest_bp.route('/show/<int:show_id>/scoreboard/next')
    def advance_scoreboard(show_id):
        """
        Increment the session vote index by one (if not at max) so that the cumulative score 
        includes one more round of votes.
        """
        progress_key = f'scoreboard_progress_{show_id}'
        total_votes = SongShowVotes.query.filter_by(showID=show_id).count()

        if progress_key not in session:
            session[progress_key] = -1

        current_index = int(session[progress_key])

        if current_index < total_votes - 1:
            session[progress_key] = current_index + 1
            print(f"DEBUG: 'Next' pressed. New session progress (show {show_id}): {session[progress_key]}")
        else:
            print(f"DEBUG: 'Next' pressed but already at max index (show {show_id}).")

        return redirect(url_for('song_contest.live_scoreboard', show_id=show_id))


    # PREV BUTTON ROUTE
    @song_contest_bp.route('/show/<int:show_id>/scoreboard/prev')
    def rewind_scoreboard(show_id):
        """
        Decrement the session vote index by one, so that the cumulative score is recalculated 
        without the last round of votes. If the index goes below 0, reset to blank state (-1).
        """
        progress_key = f'scoreboard_progress_{show_id}'

        if progress_key not in session:
            session[progress_key] = -1

        current_index = int(session[progress_key])

        if current_index > -1:
            session[progress_key] = current_index - 1
            print(f"DEBUG: 'Prev' pressed. New session progress (show {show_id}): {session[progress_key]}")
        else:
            session[progress_key] = -1
            print(f"DEBUG: 'Prev' pressed. Already at blank state (show {show_id}).")

        return redirect(url_for('song_contest.live_scoreboard', show_id=show_id))


    # List of Countries
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
        """Render a list of countries for a specific show, or display voting status messages."""

        # Fetch the show and check voting status
        show = SongShow.query.get_or_404(show_id)

        # If voting is locked before the show
        if show.voting_status == 0:
            return render_template('voting_locked.html', message="Voting opens soon!")

        # If voting is locked after the show (final results generated)
        elif show.voting_status == 2:
            return render_template('voting_locked.html', message="Voting is closed!")

        # If voting is open, proceed to show country selection
        countries = SongCountry.query.join(SongShowCountry).filter(SongShowCountry.showID == show_id).order_by(SongCountry.display_order.asc()).all()

        # Handle missing images by setting a default value
        for country in countries:
            if not country.image:
                country.image = "static/uploads/default.jpg"  # Set a default image path or URL if needed

        # Prepare the data for the template
        country_data = [(country.countryID, country.country, country.image) for country in countries]

        return render_template('select_country.html', countries=country_data, show_id=show_id)

    
    # VOTE ON CONTESTANTS
    @song_contest_bp.route('/vote/<int:show_id>/<int:assigned_country>', methods=['GET', 'POST'])
    def vote_page(show_id, assigned_country):
        # Fetch the assigned country details
        assigned_country_data = SongCountry.query.get(assigned_country)

        if not assigned_country_data:
            flash("Assigned country not found!", 'danger')
            return redirect(url_for('song_contest.select_country', show_id=show_id))

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

        # Ensure `assigned_country_data.image` is valid and fallback to default
        assigned_country_image = assigned_country_data.image if assigned_country_data.image else "static/uploads/default_flag.jpg"

        return render_template('vote_page.html', 
                               countries=countries,
                               show_id=show_id,
                               assigned_country={
                                   'name': assigned_country_data.country,
                                   'image': assigned_country_image
                               })

    
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

    # (Existing helper functions such as get_show_results() and calculate_grand_totals() remain unchanged)
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
        # Convert to a list of dicts for convenience
        results_list = []
        for r in results:
            results_list.append({
                'countryID': r.countryID,
                'country': r.country,
                'showOrder': r.showOrder,
                'votesFirst': r.votesFirst,
                'votesSecond': r.votesSecond,
                'votesThird': r.votesThird
            })
        return results_list

    def calculate_grand_totals(results):
        """Calculate grand totals for each country.
           (This example uses a sample calculation; adjust as needed.)"""
        grand_totals = []
        for result in results:
            # For our sample, assume the Grand Total is stored as follows:
            total = (result['votesFirst'] * 12) + (result['votesSecond'] * 10) + (result['votesThird'] * 8)
            grand_totals.append({
                'countryID': result['countryID'],
                'country': result['country'],
                'total': total,
                'votesFirst': result['votesFirst'],
                'votesSecond': result['votesSecond'],
                'votesThird': result['votesThird']
            })
        # Sort descending by total
        return sorted(grand_totals, key=lambda x: x['total'], reverse=True)

    # GENERATE EMCEE SCRIPT FOR LIVE ANNOUNCING OF SCORES
    @song_contest_bp.route('/show/<int:show_id>/emcee_script')
    def generate_emcee_script(show_id):
        """Generate and store the emcee script using ILP vote assignment (with countryID references)."""

        # Ensure voting is locked before generating results
        show = SongShow.query.get_or_404(show_id)
        if show.voting_status != 2:
            flash("Voting must be closed before generating results!", "danger")
            return redirect(url_for('song_contest.admin_dashboard'))

        # Fetch results and determine show countries
        results = get_show_results(show_id)
        grand_totals = calculate_grand_totals(results)

        # Retrieve all contestants (countryIDs) sorted by total score
        contestants_list = [ct['countryID'] for ct in grand_totals]

        # Retrieve awarding order dynamically from DB (ordered by showOrder)
        show_countries = SongShowCountry.query.join(SongCountry)\
            .filter(SongShowCountry.showID == show_id)\
            .order_by(SongShowCountry.showOrder.asc()).all()
        awarding_order = [sc.countryID for sc in show_countries]  # Use countryID instead of names

        # Compute targets dynamically based on number of contestants
        N = len(grand_totals)
        d = 12 / (N - 1) if N > 1 else 0  # Step adjustment
        targets = {ct['countryID']: int(round(36 - (i * d))) for i, ct in enumerate(grand_totals)}

        # ILP Formulation: Define decision variables
        vote_values = [12, 10, 8]
        prob = LpProblem("Song_Contest_Vote_Assignment", LpMinimize)
        prob += 0  # Dummy objective

        x = {}  # Decision variable dictionary
        for i in contestants_list:
            for j in contestants_list:
                if i != j:
                    for p in vote_values:
                        x[(i, j, p)] = LpVariable(f"x_{i}_{j}_{p}", cat=LpBinary)

        # Constraints
        for i in contestants_list:
            for p in vote_values:
                prob += lpSum(x[(i, j, p)] for j in contestants_list if j != i) == 1, f"One_{p}_vote_from_{i}"

        for i in contestants_list:
            for j in contestants_list:
                if i != j:
                    prob += lpSum(x[(i, j, p)] for p in vote_values) <= 1, f"At_most_one_vote_{i}_to_{j}"

        for j in contestants_list:
            prob += lpSum(p * x[(i, j, p)] for i in contestants_list if i != j for p in vote_values) == targets[j], f"Target_for_{j}"

        # Solve ILP
        status = prob.solve()
        if LpStatus[status] != "Optimal":
            flash("Could not generate a valid emcee script. Please check vote targets or constraints.", "danger")
            return redirect(url_for("song_contest.admin_dashboard"))

        # Build ILP assignment dictionary: {awarding_countryID: {12: recipientID, 10: recipientID, 8: recipientID}}
        assignment = {}
        for i in contestants_list:
            assignment[i] = {}
            for p in vote_values:
                for j in contestants_list:
                    if i != j and x[(i, j, p)].varValue == 1:
                        assignment[i][p] = j

        # Clear existing stored votes for this show
        SongShowVotes.query.filter_by(showID=show_id).delete()

        # Store ILP-generated vote assignments in DB
        for awarding in awarding_order:
            vote_entry = SongShowVotes(
                showID=show_id,
                awarding_countryID=awarding,
                recipient_12=assignment[awarding][12],
                recipient_10=assignment[awarding][10],
                recipient_8=assignment[awarding][8]
            )
            db.session.add(vote_entry)

        db.session.commit()

        # Generate emcee script with country names dynamically retrieved
        emcee_script = []
        for vote_entry in SongShowVotes.query.filter_by(showID=show_id).all():
            script_line = f"{vote_entry.awarding_country.country} announces: " \
                          f"'We award 8 points to {vote_entry.recipient_8_country.country}, " \
                          f"10 points to {vote_entry.recipient_10_country.country}, " \
                          f"and 12 points to {vote_entry.recipient_12_country.country}!'"
            emcee_script.append(script_line)

        # Tally manipulated totals
        manipulated_totals = {countryID: 0 for countryID in contestants_list}
        vote_breakdown = {countryID: {12: 0, 10: 0, 8: 0} for countryID in contestants_list}

        for i in contestants_list:
            for p in vote_values:
                recipient = assignment[i][p]
                manipulated_totals[recipient] += p
                vote_breakdown[recipient][p] += 1

        # Build leaderboard data
        leaderboard = []
        for ct in grand_totals:
            countryID = ct['countryID']
            leaderboard.append({
                'country': SongCountry.query.get(countryID).country,
                'grand_total': ct['total'],
                'adjusted_total': manipulated_totals.get(countryID, 0),
                'votes_first': vote_breakdown[countryID][12],
                'votes_second': vote_breakdown[countryID][10],
                'votes_third': vote_breakdown[countryID][8]
            })

        # Manual adjustments
        manual_adjustments = []
        top_two = sorted(leaderboard, key=lambda x: x['adjusted_total'], reverse=True)[:2]
        if abs(top_two[0]['adjusted_total'] - top_two[1]['adjusted_total']) > 12:
            manual_adjustments.append("Consider swapping a 10-point vote with an 8-point vote between the top two countries.")

        return render_template('emcee_script.html', 
                               script=emcee_script, 
                               leaderboard=leaderboard,
                               targets=targets,
                               adjustments=manual_adjustments)
