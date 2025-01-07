from flask import Blueprint
from .admin import register_admin_views  # Import the register function

# Initialize the Blueprint
song_contest_bp = Blueprint('song_contest', __name__, template_folder='templates', static_folder='static')

# Import routes and models here to avoid circular imports
from .views import *
from .models import *

# Register admin views inside the app context
def register_admin(app):
    register_admin_views(app)