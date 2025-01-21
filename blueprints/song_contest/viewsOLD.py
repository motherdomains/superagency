from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from .models import SongCountry, SongShow, SongShowCountry

# Initialize Blueprint
song_contest_bp = Blueprint('song_contest', __name__, template_folder='templates')

# Routes for Song Contest
@song_contest_bp.route('/countries', endpoint='country_list')
def country_list():
    """Render a list of countries."""
    countries = SongCountry.query.order_by(SongCountry.display_order.asc()).all()
    return render_template('country_list.html', countries=countries)

@song_contest_bp.route('/add_countries/<int:showID>', methods=['GET', 'POST'], endpoint='add_countries_to_show')
def add_countries_to_show(showID):
    """Route to add countries to the selected show."""
    show = SongShow.query.get_or_404(showID)
    countries = SongCountry.query.all()

    if request.method == 'POST':
        selected_countries = request.form.getlist('countries')
        for countryID in selected_countries:
            song_country = SongCountry.query.get(countryID)
            if song_country:
                show_country = SongShowCountry(showID=showID, countryID=countryID)
                db.session.add(show_country)
        db.session.commit()
        flash('Countries successfully added to the show!', 'success')
        return redirect(url_for('song_contest.add_countries_to_show', showID=showID))

    return render_template('add_countries_to_show.html', show=show, countries=countries)