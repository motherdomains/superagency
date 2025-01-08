from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_admin import Admin
import os
from config.config import Config
from extensions import db, bcrypt
from blueprints.admin_views import UserAdmin, CustomAdminIndexView
from models.user import User

# Import blueprints
from blueprints.home import home_bp
from blueprints.song_contest import song_contest_bp, register_admin_views
from blueprints.auth import auth_bp  # Import the auth blueprint


# Create the app
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)

    # Create an Admin instance and initialize it
    admin = Admin(app, name='Admin Dashboard', template_mode='bootstrap3', index_view=CustomAdminIndexView())

    # Set up logging
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    app.register_blueprint(home_bp)  # Register the home blueprint
    app.register_blueprint(song_contest_bp, url_prefix='/song_contest')  # Register the song contest blueprint
    app.register_blueprint(auth_bp, url_prefix='/auth')  # Register the auth blueprint with a URL prefix

    # Register admin views
    admin.add_view(UserAdmin(User, db.session))
    register_admin_views(admin)

    return app


# Run the app
if __name__ == '__main__':
    app = create_app()  # Create the app before running it
    app.run(debug=True)