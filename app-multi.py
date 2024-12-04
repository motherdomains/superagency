from flask import Flask
from config import Config
from extensions import db, bcrypt, admin
from routes import home, login, register  # Import routes directly
from models import User
from flask_debugtoolbar import DebugToolbarExtension

# Initialize the Flask app with configuration settings
app = Flask(__name__)
app.config.from_object(Config)  # Use the Config class for configurations

toolbar = DebugToolbarExtension(app)

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
admin.init_app(app)

# Register routes
app.add_url_rule('/', 'home', home)
app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/register', 'register', register, methods=['GET', 'POST'])

# For Debug Mode
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created
        print("Multi-file App is starting...")
    app.run(debug=True)
    
print(app.url_map)  # Add this line in app.py after app initialization

 