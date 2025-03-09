from flask_admin import Admin
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
admin = Admin(name='Super Agency Admin Panel', template_mode='bootstrap3')