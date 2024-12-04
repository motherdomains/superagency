from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_admin import Admin

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
admin = Admin(name='Super Agency Admin', template_mode='bootstrap4')