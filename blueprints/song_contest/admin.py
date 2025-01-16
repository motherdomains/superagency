from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask import url_for, flash
from extensions import db
from .models import SongCountry, SongShow
import os
from werkzeug.utils import secure_filename

class SongCountryAdmin(ModelView):
    form_columns = ('country', 'image')  # Only 'country' and 'image' will be editable
    column_list = ('country', 'status', 'image')  # Include image in the column list
    column_display_pk = True

    column_formatters = {
        'status': lambda view, context, model, name: 'Active' if model.status == '1' else 'Inactive'
    }

    form_widget_args = {
        'image': {
            'type': 'file',  # Treat 'image' as file input field
        }
    }

    def on_model_change(self, form, model, is_created):
        """Override to handle image file upload and save"""
        if form.image.data:
            file = form.image.data
            filename = secure_filename(file.filename)
            file_path = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(file_path)
                model.image = filename  # Save the filename in the database
            except Exception as e:
                flash(f'Error saving image: {str(e)}', 'error')
                raise e
        elif not is_created and model.image:
            # If the image is not being changed, retain the old one
            model.image = model.image

class SongShowAdmin(ModelView):
    form_columns = ('showName', 'showDate', 'totalContestants')
    column_list = ('showName', 'showDate', 'totalContestants', 'actions')
    column_display_pk = True
    column_formatters = {
        'showDate': lambda view, context, model, name: model.formatted_showDate(),
        'actions': lambda view, context, model, name: f'<a href="{url_for("song_contest.add_countries_to_show", showID=model.showID)}">Add Countries</a>',
    }

    column_formatters.update({
        'countries': lambda view, context, model, name: ', '.join([country.song_country.country for country in model.songShowCountries])
    })

# Function to register admin views
def register_admin_views(admin: Admin):
    admin.add_view(SongShowAdmin(SongShow, db.session, name="Shows"))
    admin.add_view(SongCountryAdmin(SongCountry, db.session, name="Countries"))