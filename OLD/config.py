import os  # Required for handling file paths

class Config:
    SQLALCHEMY_DATABASE_URI = (
        'mysql+mysqlconnector://superagent:x5GvGYSXJXK(!qi2@localhost/superagency'
    )
    SECRET_KEY = 'superCHAPAtestingDOG'  # Used for sessions and Flask-Admin
    DEBUG = True  # Debug mode during development
    TEMPLATES_AUTO_RELOAD = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids unnecessary overhead warnings

    # File Upload Settings
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Absolute base directory
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')      # Folder where files are uploaded
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}     # Allowed file extensions

    # Logging Settings
    LOG_FILE = 'app.log'
    LOG_MAX_BYTES = 100000
    LOG_BACKUP_COUNT = 3