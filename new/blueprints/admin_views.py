from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt
from models.user import User
from blueprints.forms import UserForm
from extensions import db
from flask import render_template, redirect, url_for

bcrypt = Bcrypt()

# UserAdmin view definition
class UserAdmin(ModelView):
    column_list = ('superName', 'superEmail', 'superRole')
    column_display_pk = True
    form = UserForm

    def on_model_change(self, form, model, is_created):
        if is_created and form.superPassword.data:
            model.superPassword = bcrypt.generate_password_hash(form.superPassword.data).decode('utf-8')
        return super().on_model_change(form, model, is_created)

# Custom Admin Index View
class CustomAdminIndexView(AdminIndexView):
    def is_accessible(self):
        # You can customize this logic for access control
        return True  # Example: always accessible

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            # If not accessible, redirect to login or other page
            return redirect(url_for('login'))

        return super()._handle_view(name, **kwargs)

# Flask-Admin setup with the custom AdminIndexView
admin = Admin(
    name='My Admin Panel', 
    template_mode='bootstrap3', 
    index_view=CustomAdminIndexView(url='/admin/')
)

# Register the views for the User model
admin.add_view(UserAdmin(User, db.session))

# Add other views as necessary