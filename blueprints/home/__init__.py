from flask import Blueprint

# Define the blueprint
home_bp = Blueprint('home', __name__)

# Import the views to attach routes to the blueprint
from . import views