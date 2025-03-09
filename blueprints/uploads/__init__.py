from flask import Blueprint

# Define the blueprint first
uploads_bp = Blueprint('uploads', __name__)

# Import routes after defining the Blueprint
from . import routes