from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from extensions import db
from .models import Survey, SurveyQuestion, SurveyResponse, SurveyUser
import os
from werkzeug.utils import secure_filename
from flask import flash, url_for
from wtforms import SelectField, TextAreaField  # Import SelectField and TextAreaField
from wtforms.widgets import TextArea
import json

class JSONTextAreaField(TextAreaField):
    """
    Custom field for handling JSON data in a textarea.
    """
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = json.loads(valuelist[0])  # Parse JSON input
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON data")

class CustomModelView(ModelView):
    """
    Custom base class for ModelViews to handle extra arguments like upload_folder
    """
    def __init__(self, model, session, upload_folder=None, **kwargs):
        super().__init__(model, session, **kwargs)
        self.upload_folder = upload_folder

    def on_model_change(self, form, model, is_created):
        """
        Override this method to handle file uploads or other custom logic.
        """
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

class SurveyAdmin(CustomModelView):
    """
    Admin view for the Survey model.
    """
    form_columns = ('title', 'description', 'created_at')
    column_list = ('surveyID', 'title', 'description', 'created_at')
    column_display_pk = True  # Show primary key in the list view
    column_searchable_list = ['title', 'description']  # Enable search by title and description
    column_filters = ['created_at']  # Add filters for creation date

class SurveyQuestionAdmin(CustomModelView):
    """
    Admin view for the SurveyQuestion model.
    """
    form_overrides = {
        'question_type': SelectField,  # Use SelectField for question_type
        'options': JSONTextAreaField  # Use the custom JSON field
    }
    form_args = {
        'question_type': {
            'choices': [('select', 'Select'), ('multiple_choice', 'Multiple Choice'), ('scale', 'Scale'), ('open_ended', 'Open Ended')]
        }
    }
    form_widget_args = {
        'options': {
            'widget': TextArea(),  # Render as a textarea
            'rows': 10  # Set the number of rows for the textarea
        }
    }
    form_columns = ('survey_id', 'question_text', 'question_type', 'options')
    column_list = ('questionID', 'survey_id', 'question_text', 'question_type', 'options')
    column_display_pk = True
    column_searchable_list = ['question_text']  # Enable search by question text
    column_filters = ['question_type']  # Add filters for question type

    def on_form_prefill(self, form, id):
        """
        Log form data for debugging.
        """
        print("Form data:", form.data)
        super().on_form_prefill(form, id)

class SurveyResponseAdmin(CustomModelView):
    """
    Admin view for the SurveyResponse model.
    """
    form_columns = ('user_id', 'question_id', 'answer', 'responded_at')
    column_list = ('responseID', 'user_id', 'question_id', 'answer', 'responded_at')
    column_display_pk = True
    column_searchable_list = ['answer']  # Enable search by answer text
    column_filters = ['responded_at']  # Add filters for response date

class SurveyUserAdmin(CustomModelView):
    """
    Admin view for the SurveyUser model.
    """
    form_columns = ('name', 'email', 'contact_info')
    column_list = ('userID', 'name', 'email', 'contact_info')
    column_display_pk = True
    column_searchable_list = ['name', 'email']  # Enable search by name and email
    column_filters = ['email']  # Add filters for email

# Function to register admin views
def register_admin_views(admin):
    """
    Registers admin views for Surveys models.
    :param admin: Flask-Admin instance
    """
    # Ensure the upload folder exists (if needed)
    upload_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'uploads'))
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Register the admin views for Survey, SurveyQuestion, SurveyResponse, and SurveyUser
    admin.add_view(SurveyAdmin(Survey, db.session, upload_folder=upload_folder, name="Surveys"))
    admin.add_view(SurveyQuestionAdmin(SurveyQuestion, db.session, upload_folder=upload_folder, name="Questions"))
    admin.add_view(SurveyResponseAdmin(SurveyResponse, db.session, upload_folder=upload_folder, name="Responses"))
    admin.add_view(SurveyUserAdmin(SurveyUser, db.session, upload_folder=upload_folder, name="Users"))