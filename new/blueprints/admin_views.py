from flask_admin.contrib.sqla import ModelView
from werkzeug.utils import secure_filename
from flask import url_for
from extensions import db, bcrypt
from models.user import User
from .forms import UserForm  # Relative import for forms in the same directory

class UserAdmin(ModelView):
    column_list = ('superName', 'superEmail', 'superRole')
    column_display_pk = True
    form = UserForm

    def on_model_change(self, form, model, is_created):
        if is_created and form.superPassword.data:
            model.superPassword = bcrypt.generate_password_hash(form.superPassword.data).decode('utf-8')
        return super().on_model_change(form, model, is_created)

# Add other Admin classes like CountryAdmin, SongShowAdmin similarly