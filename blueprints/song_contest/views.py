from flask import render_template, request, session, redirect, url_for, flash
from flask import current_app as app
from app import db  # Import from the main app file
from .models import SongCountry, SongShow, SongShowCountry
from sqlalchemy.orm import aliased
from functools import wraps  # For admin authentication

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
            if session.get("is_admin") is not True:  # Only allow if admin is logged in
                flash("Access Denied! Admins only.", "danger")
                return redirect(url_for("song_contest.admin_login"))
            return f(*args, **kwargs)
        return decorated_function

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

    # Admin dashboard
    @song_contest_bp.route('/admin')
    @admin_required
    def admin_dashboard():
        return render_template("admin_dashboard.html")  # Create this template!

    # Reset votes for a specific show
    @song_contest_bp.route('/admin/reset_votes/<int:show_id>', methods=['POST'])
    @admin_required
    def reset_votes(show_id):
        try:
            db.session.query(SongShowCountry).filter(SongShowCountry.showID == show_id).update({
                "votesFirst": 0,
                "votesSecond": 0,
                "votesThird": 0
            })
            db.session.commit()
            flash(f"✅ Successfully reset votes for Show ID {show_id}!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Error resetting votes: {e}", "danger")

        return redirect(url_for("song_contest.admin_dashboard"))
    
    

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

    # New ILP-based emcee script route
    @song_contest_bp.route('/show/<int:show_id>/emcee_script')
    def generate_emcee_script(show_id):
        """Generate the emcee script and leaderboard using an ILP vote assignment."""
        # 1. Fetch show results and compute grand totals.
        results = get_show_results(show_id)
        grand_totals = calculate_grand_totals(results)
        # Sort by finishing position (descending Grand Total)
        sorted_grand_totals = grand_totals

        # 2. Compute targets dynamically based on number of contestants.
        N = len(sorted_grand_totals)
        # Total available points per country = 30 (since each awarding country gives 12+10+8)
        # So total available overall is 30 * N. For an arithmetic progression with N terms, we require:
        # (A + B)/2 * N = 30N, hence A + B = 60. For our sample we use A=36, B=24 if possible.
        # For N != 7, we calculate the step as:
        d = 12 / (N - 1) if N > 1 else 0
        targets = {}
        for i, ct in enumerate(sorted_grand_totals):
            rank = i + 1
            # Compute the target as a float, then round to the nearest integer.
            targets[ct['country']] = int(round(36 - (rank - 1) * d))

        # 3. Retrieve the awarding order dynamically from the database (ordered by showOrder)
        show_countries = SongShowCountry.query.join(SongCountry, SongShowCountry.countryID == SongCountry.countryID)\
                                .filter(SongShowCountry.showID == show_id)\
                                .order_by(SongShowCountry.showOrder.asc()).all()
        awarding_order = [sc.song_country.country for sc in show_countries]

        # Create a list of all contestants (by country name) from the grand totals
        contestants_list = [ct['country'] for ct in sorted_grand_totals]

        # 4. ILP Formulation: Each contestant is both awarding and receiving.
        vote_values = [12, 10, 8]
        from pulp import LpProblem, LpVariable, LpBinary, lpSum, LpStatus, LpMinimize
        prob = LpProblem("Song_Contest_Vote_Assignment", LpMinimize)
        prob += 0  # Dummy objective

        # Decision variables: x[(i, j, p)] is 1 if awarding country i gives vote p to recipient j.
        x = {}
        for i in contestants_list:
            for j in contestants_list:
                if i != j:
                    for p in vote_values:
                        x[(i, j, p)] = LpVariable(f"x_{i}_{j}_{p}", cat=LpBinary)

        # Constraint 1: Each awarding country gives exactly one vote of each type.
        for i in contestants_list:
            for p in vote_values:
                prob += lpSum(x[(i, j, p)] for j in contestants_list if j != i) == 1, f"One_{p}_vote_from_{i}"

        # Constraint 2: No awarding country gives more than one vote to the same recipient.
        for i in contestants_list:
            for j in contestants_list:
                if i != j:
                    prob += lpSum(x[(i, j, p)] for p in vote_values) <= 1, f"At_most_one_vote_{i}_to_{j}"

        # Constraint 3: For each recipient, the sum of points received equals their target.
        for j in contestants_list:
            prob += lpSum(p * x[(i, j, p)] for i in contestants_list if i != j for p in vote_values) == targets[j], f"Target_for_{j}"

        # Solve the ILP.
        status = prob.solve()
        if LpStatus[status] != "Optimal":
            flash("Could not generate a valid emcee script. Please check the vote targets or constraints.", "danger")
            return redirect(url_for("song_contest.show_list"))

        # Build assignment dictionary: assignment[awarding][vote_value] = recipient
        assignment = {}
        for i in contestants_list:
            assignment[i] = {}
            for p in vote_values:
                for j in contestants_list:
                    if i != j and x[(i, j, p)].varValue == 1:
                        assignment[i][p] = j

        # 5. Build the emcee script using the dynamic awarding_order.
        emcee_script = []
        for awarding in awarding_order:
            rec12 = assignment[awarding][12]
            rec10 = assignment[awarding][10]
            rec8  = assignment[awarding][8]
            script_line = f"{awarding} announces: 'We award 8 points to {rec8}, 10 points to {rec10}, and 12 points to {rec12}!'"
            emcee_script.append(script_line)

        # 6. Tally manipulated totals from the ILP assignment.
        manipulated_totals = {country: 0 for country in contestants_list}
        vote_breakdown = {country: {12: 0, 10: 0, 8: 0} for country in contestants_list}
        for i in contestants_list:
            for p in vote_values:
                recipient = assignment[i][p]
                manipulated_totals[recipient] += p
                vote_breakdown[recipient][p] += 1

        # 7. Build leaderboard data: include Grand Total (from DB) and Adjusted Total (from ILP)
        leaderboard = []
        for ct in sorted_grand_totals:
            country = ct['country']
            leaderboard.append({
                'country': country,
                'grand_total': ct['total'],
                'adjusted_total': manipulated_totals.get(country, 0),
                'votes_first': vote_breakdown[country][12],
                'votes_second': vote_breakdown[country][10],
                'votes_third': vote_breakdown[country][8]
            })

        # 8. Optionally, add manual adjustment instructions (fail-safe mechanism)
        manual_adjustments = []
        # Example check: if the gap between the top two is larger than desired.
        top_two = sorted(leaderboard, key=lambda x: x['adjusted_total'], reverse=True)[:2]
        if abs(top_two[0]['adjusted_total'] - top_two[1]['adjusted_total']) > 12:
            manual_adjustments.append("Consider swapping a 10-point vote with an 8-point vote between the top two countries.")

        return render_template('emcee_script.html', 
                               script=emcee_script, 
                               leaderboard=leaderboard,
                               targets=targets,
                               adjustments=manual_adjustments)
