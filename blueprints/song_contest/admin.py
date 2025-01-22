from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from extensions import db
from .models import SongCountry, SongShow
import os
from werkzeug.utils import secure_filename
from flask import flash, url_for

class CustomModelView(ModelView):
    """
    Custom base class for ModelViews to handle extra arguments like upload_folder
    """
    def __init__(self, model, session, upload_folder=None, **kwargs):
        super().__init__(model, session, **kwargs)
        self.upload_folder = upload_folder

    def on_model_change(self, form, model, is_created):
        if hasattr(form, 'image') and form.image.data:
            file = form.image.data
            filename = secure_filename(file.filename)
            file_path = os.path.join(self.upload_folder, filename)
            try:
                file.save(file_path)
                model.image = filename
            except Exception as e:
                flash(f"Error saving image: {str(e)}", 'error')
                raise e

class SongCountryAdmin(CustomModelView):
    form_columns = ('country', 'image')
    column_list = ('country', 'status', 'image')
    column_display_pk = True

    column_formatters = {
        'status': lambda view, context, model, name: 'Active' if model.status == '1' else 'Inactive'
    }

class SongShowAdmin(CustomModelView):
    form_columns = ('showName', 'showDate', 'totalContestants')
    column_list = ('showName', 'showDate', 'totalContestants')  # Removed 'actions' column
    column_display_pk = True
    column_formatters = {
        'showDate': lambda view, context, model, name: model.formatted_showDate(),
    }

# Function to register admin views
def register_admin_views(admin):
    """
    Registers admin views for Song Contest models.
    :param admin: Flask-Admin instance
    """
    # Ensure the upload folder exists
    upload_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'uploads'))
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Register the admin views for SongShow and SongCountry
    admin.add_view(SongShowAdmin(SongShow, db.session, upload_folder=upload_folder, name="Shows"))
    admin.add_view(SongCountryAdmin(SongCountry, db.session, upload_folder=upload_folder, name="Countries"))