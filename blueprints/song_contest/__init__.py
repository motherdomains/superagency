# blueprints/song_contest/__init__.py
from flask import Blueprint
from .admin import register_admin_views  # Import the function for registering admin views

# Initialize the Blueprint here, but don't import views yet
song_contest_bp = Blueprint(
    'song_contest', 
    __name__, 
    template_folder='templates', 
    static_folder=None  # Do not serve static files from this blueprint
)

def register_blueprints(app, admin):
    """
    Registers the Song Contest blueprint and admin views.
    :param app: Flask application instance
    :param admin: Flask-Admin instance
    """
    # Now import register_routes inside the register_blueprints function to avoid circular imports
    from .views import register_routes
    register_routes(song_contest_bp)  # Pass the blueprint to the register_routes function
    
    app.register_blueprint(song_contest_bp, url_prefix='/song_contest')  # Register with URL prefix

    # Register admin views for Song Contest
    register_admin_views(admin)  # Register the admin views from song_contest/admin.py