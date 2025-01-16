from flask import Blueprint
from .admin import register_admin_views  # Import the admin view registration function

# Initialize the Blueprint
song_contest_bp = Blueprint(
    'song_contest', 
    __name__, 
    template_folder='templates', 
    static_folder='static'
)

# Define routes specific to the blueprint
@song_contest_bp.route('/add_countries_to_show/<int:showID>', methods=['GET', 'POST'])
def add_countries_to_show(showID):
    # Example placeholder response
    return f"Adding countries to show ID: {showID}"

# Import routes and models to avoid circular imports
from . import views, models

# Function to register admin views
def register_admin(app, admin):
    """
    Registers admin views for Song Contest models.
    :param app: Flask application instance
    :param admin: Flask-Admin instance
    """
    with app.app_context():
        register_admin_views(admin)

# Function to register the blueprint
def register_blueprints(app):
    """
    Registers the Song Contest blueprint.
    :param app: Flask application instance
    """
    app.register_blueprint(song_contest_bp)