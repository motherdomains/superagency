from flask import Flask, send_from_directory
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from config.config import Config
from extensions import db, bcrypt
from models.user import User
from blueprints.home import home_bp
from blueprints.auth import auth_bp
from blueprints.cms import create_cms  # New CMS blueprint
from blueprints.admin_views import UserAdmin, CustomAdminIndexView
from blueprints.song_contest import register_blueprints  # Ensure song_contest blueprint is registered
from blueprints.surveys import init_app as surveys_init
from blueprints.surveys.admin import register_admin_views, CustomModelView  # Import CustomModelView
from blueprints.surveys.models import Survey, SurveyQuestion, SurveyResponse, SurveyUser  # Import Survey models
from blueprints.surveys.routes import surveys_bp

import os

# Create the Flask app
def create_app():
    app = Flask(__name__)
    
    # Configurations
    app.config.from_object(Config)
    app.jinja_env.cache = {}  # Disable template caching for development
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Ensure upload folder exists

    # Log the template search path
    print("Template search path:", app.jinja_loader.searchpath)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)

    # Flask-Admin setup
    admin = Admin(app, name='Admin Dashboard', template_mode='bootstrap3', index_view=CustomAdminIndexView())

    # Register Blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    cms_bp = create_cms()
    app.register_blueprint(cms_bp, url_prefix='/cms')

    # Register song contest blueprint and admin views
    register_blueprints(app, admin)  # Ensure song_contest blueprint is registered

    # Register Surveys Blueprint
    app.register_blueprint(surveys_bp)  # Directly register the surveys Blueprint

    # Register surveys admin views
    register_admin_views(admin)  # Register surveys admin views

    # Admin views
    admin.add_view(UserAdmin(User, db.session))

    # File uploads route
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(os.path.join(app.config['STATIC_FOLDER'], 'uploads'), filename)

    # Debugging route for CMS
    @app.route('/cms/debug')
    def cms_debug():
        return "CMS Debug Route Working!"

    # List routes (run once at app startup)
    @app.before_request
    def list_routes():
        global routes_listed  # Declare that we're using the global variable
        if 'routes_listed' not in globals():  # Check if the variable is not already defined
            routes_listed = False  # Initialize if it's not already initialized

        if not routes_listed:
            print("Listing all routes:")
            for rule in app.url_map.iter_rules():
                print(rule)
            routes_listed = True  # Set the flag to True to prevent repeated listings

    return app

# Run the Flask app
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create