from flask import render_template, session
from . import home_bp  # Import the blueprint defined in __init__.py


@home_bp.route('/')
def index():
    username = session.get('username')
    greeting = f"Welcome back, {username}!" if username else "Please log in."
    return render_template('index.html', greeting=greeting, title="Home")