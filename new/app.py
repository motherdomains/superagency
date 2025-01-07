from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_admin import Admin
import os
from config.config import Config
from extensions import db, bcrypt  # Import db and bcrypt from extensions
from blueprints.admin_views import UserAdmin, CustomAdminIndexView  # Import UserAdmin
from blueprints.forms import UserForm  # Import UserForm
from models.user import User  # Import User model

# Import song_contest blueprint and register_admin_views function
from blueprints.song_contest import song_contest_bp, register_admin_views

# Create the app
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)

    # Create an Admin instance and initialize it
    admin = Admin(app, name='Admin Dashboard', template_mode='bootstrap3', index_view=CustomAdminIndexView())

    # Set up logging (as in the original code)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    app.register_blueprint(song_contest_bp, url_prefix='/song_contest')

    # Register admin views for User model
    admin.add_view(UserAdmin(User, db.session))

    # Register Song Contest admin views (from the song_contest blueprint)
    register_admin_views(admin)

    return app