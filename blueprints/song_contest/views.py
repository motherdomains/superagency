# blueprints/song_contest/views.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_admin.contrib.sqla import ModelView
from extensions import db
from .models import SongCountry, SongShow, SongShowCountry  # Make sure SongShowCountry is imported

# Initialize Blueprint
song_contest_bp = Blueprint('song_contest', __name__, template_folder='templates')  # Use the main templates folder

# Admin views for Song Contest models
class SongCountryAdmin(ModelView):
    form_columns = ('country', 'status', 'display_order')  # Define the form columns
    column_list = ('country', 'status', 'display_order')
    column_display_pk = True

class SongShowAdmin(ModelView):
    form_columns = ('showName', 'showDate','totalContestants')
    column_list = ('showName', 'showDate', 'totalContestants', 'actions')  # Added 'actions' column
    column_display_pk = True
    column_formatters = {
        'showDate': lambda view, context, model, name: model.formatted_showDate(),
        'actions': lambda view, context, model, name: f'<a href="{url_for("song_contest.add_countries_to_show", showID=model.showID)}">Add Countries</a>',
    }

    # Formatter for showing countries for a show (if needed)
    column_formatters.update({
        'countries': lambda view, context, model, name: ', '.join([country.song_country.country for country in model.songShowCountries])  # Show countries
    })

# Function to register admin views
def register_admin_views(admin):
    """Registers the Song Contest admin views."""
    admin.add_view(SongCountryAdmin(SongCountry, db.session, name="Countries"))
    print("Registering SongCountryAdmin...")
    admin.add_view(SongShowAdmin(SongShow, db.session, name="Shows"))
    print("SongCountryAdmin registered successfully.")

# Routes for Song Contest
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
        return redirect(url_for('song_contest.add_countries_to_show', showID=showID))

    return render_template('add_countries_to_show.html', show=show, countries=countries)  # Render the form to add countries