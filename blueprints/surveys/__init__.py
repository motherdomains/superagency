# blueprints/song_contest/__init__.py
from flask import Blueprint
from .admin import register_admin_views  # Import the function for registering admin views
from .routes import surveys_bp

# Initialize the surveys Blueprint
surveys_bp = Blueprint('surveys', __name__, template_folder='templates')

def init_app(app):
    app.register_blueprint(surveys_bp)