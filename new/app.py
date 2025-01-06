from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from extensions import db, bcrypt, admin
from blueprints.admin_views import UserAdmin  # Import UserAdmin
from blueprints.forms import UserForm  # Import UserForm
from models.user import User  # Import the User model here
from flask_admin.contrib.sqla import ModelView
import os
import logging
from datetime import datetime
from config.config import Config  # Import the Config class from the correct location


# Create the app
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    admin.init_app(app)

    # Initialize Flask-Admin and register the User model
    admin.add_view(UserAdmin(User, db.session))  # Register UserAdmin view

    # Register blueprints
    # app.register_blueprint(home_bp)
    # app.register_blueprint(auth_bp, url_prefix='/auth')
    # app.register_blueprint(uploads_bp, url_prefix='/uploads')

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app