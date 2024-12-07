import mysql.connector  # Import MySQL connector for database interactions

class Config:
    # Update the URI to point to your MySQL database
    SQLALCHEMY_DATABASE_URI = (
        'mysql+mysqlconnector://superagent:x5GvGYSXJXK(!qi2@localhost/superagency'
    )
    SECRET_KEY = 'superCHAPAtestingDOG'  # Used for Flask-Admin and Flash messages
    TEMPLATES_AUTO_RELOAD = True
    DEBUT = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids overhead warnings
    
    
    
    