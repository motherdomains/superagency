# blueprints/song_contest/__init__.py
from flask import Blueprint
from .admin import register_admin_views  # Import the admin view registration function

# Initialize the Blueprint
song_contest_bp = Blueprint(
    'song_contest', 
    __name__, 
    template_folder='templates', 
    static_folder=None  # Do not serve static files from this blueprint
)

# Function to register admin views
def register_song_contest_admin(app, admin):
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
    app.register_blueprint(song_contest_bp, url_prefix='/song_contest')  # Register with URL prefix