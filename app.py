# Welcome the AI Super Agency
from flask import Flask, send_from_directory, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_admin import Admin
import os
from config.config import Config
from extensions import db, bcrypt
from blueprints.admin_views import UserAdmin, CustomAdminIndexView
from models.user import User
from blueprints.song_contest import song_contest_bp, register_admin_views  # Import from song_contest
from blueprints.home import home_bp
from blueprints.auth import auth_bp
from blueprints.song_contest.models import SongShow

# Create the app
def create_app():
    app = Flask(__name__)
    
    # Disable Jinja2 template caching during development
    app.jinja_env.cache = {}

    app.config.from_object(Config)

    # Set the path for the upload folder (ensure this matches Config)
    app.config['UPLOAD_FOLDER'] = app.config['UPLOAD_FOLDER']  # Path already in config
    print(f"Upload folder path set to: {app.config['UPLOAD_FOLDER']}")  # Debugging print statement

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)

    # Create an Admin instance and initialize it
    admin = Admin(app, name='Admin Dashboard', template_mode='bootstrap3', index_view=CustomAdminIndexView())

    # Create the upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    app.register_blueprint(home_bp)  # Register the home blueprint
    app.register_blueprint(song_contest_bp, url_prefix='/song_contest')  # Register the song contest blueprint
    app.register_blueprint(auth_bp, url_prefix='/auth')  # Register the auth blueprint with a URL prefix

    # Register admin views - only do this once here
    admin.add_view(UserAdmin(User, db.session))
    register_admin_views(admin)  # Ensure Song Contest admin views are registered

    # Register the uploads route to serve uploaded files
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"Serving file from: {file_path}")  # Debugging print statement
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Debugging route to view SongShows and their Actions links
    @app.route('/debug_admin')
    def debug_admin():
        # Query the SongShow data to ensure it's available
        song_shows = SongShow.query.all()  # Assuming you're querying the SongShow model
        print(f"Song Shows: {[show.__dict__ for show in song_shows]}")  # Debugging print statement to verify data

        # Pass the queried data to the template
        return render_template('admin/debug.html', song_shows=song_shows)

    # List routes when app starts (Optional)
    @app.before_request
    def list_routes_once():
        if not hasattr(app, '_routes_listed'):
            for rule in app.url_map.iter_rules():
                print(rule)
            app._routes_listed = True  # Ensure it runs only once

    return app

# Run the app
if __name__ == '__main__':
    app = create_app()  # Create the app before running it
    app.run(debug=True)