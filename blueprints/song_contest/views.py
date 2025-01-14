from flask import Blueprint, render_template, redirect, url_for, flash, request
from blueprints.song_contest.models import SongCountry, SongShow, SongShowCountry
from blueprints.song_contest.forms import CountryForm, SongShowForm
from flask_admin.contrib.sqla import ModelView
from extensions import db

# Initialize Blueprint
song_contest_bp = Blueprint('song_contest', __name__, template_folder='templates')  # Use the main templates folder

# Admin views for Song Contest models
class SongCountryAdmin(ModelView):
    form = CountryForm
    column_list = ('country', 'status', 'display_order')
    column_display_pk = True

class SongShowAdmin(ModelView):
    form = SongShowForm
    column_list = ('showName', 'showDate', 'totalContestants')
    column_display_pk = True
    column_formatters = {
        'showDate': lambda view, context, model, name: model.formatted_showDate()
    }

# Function to register admin views
def register_admin_views(admin):
    """Registers the Song Contest admin views."""
    admin.add_view(SongCountryAdmin(SongCountry, db.session, name="Countries"))
    admin.add_view(SongShowAdmin(SongShow, db.session, name="Shows"))

# Routes for Song Contest

# Route for listing all countries
@song_contest_bp.route('/countries', endpoint='country_list')
def country_list():
    """Render a list of countries."""
    countries = SongCountry.query.order_by(SongCountry.display_order.asc()).all()
    return render_template('country_list.html', countries=countries)  # Templates are now in the main 'templates' folder

# Route for adding countries to a show
@song_contest_bp.route('/shows/<int:show_id>/add-countries', methods=['GET', 'POST'], endpoint='add_countries')
def add_countries(show_id):
    """Add countries to a specific show."""
    show = SongShow.query.get_or_404(show_id)
    countries = SongCountry.query.order_by(SongCountry.country.asc()).all()
    total_contestants = show.totalContestants
    selected_countries = []

    if request.method == 'POST':
        selected_ids = request.form.getlist('countries')
        if len(selected_ids) != total_contestants:
            flash(f"Please select exactly {total_contestants} countries.", "warning")
        else:
            # Clear any existing countries for this show
            SongShowCountry.query.filter_by(showID=show.id).delete()

            # Add the selected countries to the show
            for country_id in selected_ids:
                show_country = SongShowCountry(showID=show.id, countryID=int(country_id))
                db.session.add(show_country)
            db.session.commit()

            flash(f"{len(selected_ids)} countries added to the show successfully!", "success")
            return redirect(url_for('song_contest.add_countries', show_id=show_id))

    return render_template(
        'add_countries.html',
        show=show,
        countries=countries,
        selected_countries=selected_countries,
        total_contestants=total_contestants,
    )