# blueprints/song_contest/__init__.py
from flask import Blueprint
from .admin import register_admin_views  # Import the register function

# Initialize the Blueprint
song_contest_bp = Blueprint('song_contest', __name__, template_folder='templates', static_folder='static')

@song_contest_bp.route('/add_countries_to_show/<int:showID>', methods=['GET', 'POST'])
def add_countries_to_show(showID):
    # Example placeholder response
    return f"Adding countries to show ID: {showID}"

# Import routes and models to avoid circular imports
from .views import *
from .models import *

# Register admin views inside the app context
def register_admin(app):
    register_admin_views(app)

# Ensure the blueprint is registered when the app is created
def register_blueprints(app):
    app.register_blueprint(song_contest_bp)