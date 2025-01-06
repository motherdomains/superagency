from flask import render_template, session
from . import home_bp

@home_bp.route('/')
def home():
    username = session.get('username')
    greeting = f"Welcome back, {username}!" if username else "Please log in."
    return render_template('index.html', greeting=greeting, title="Home")