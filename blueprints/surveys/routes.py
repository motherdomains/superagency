# blueprints/surveys/views.py
from flask import Blueprint, request, jsonify, current_app as app, render_template, session, redirect, url_for, flash

from app import db  # Import from the main app file
from .models import Survey, SurveyQuestion, SurveyResponse, SurveyUser

# Initialize Blueprint
surveys_bp = Blueprint('surveys', __name__, url_prefix='/surveys')

@surveys_bp.route('/create', methods=['GET', 'POST'])
def create_survey():
    if request.method == 'POST':
        data = request.get_json()
        new_survey = Survey(
            title=data['title'],
            description=data.get('description')
        )
        db.session.add(new_survey)
        db.session.commit()
        return jsonify({"message": "Survey created", "surveyID": new_survey.surveyID}), 201
    else:
        return render_template('surveys/create.html')  # Render a form for creating surveys

# Route to add a question to a survey
@surveys_bp.route('/<int:survey_id>/add_question', methods=['POST'])
def add_question(survey_id):
    data = request.get_json()
    new_question = SurveyQuestion(
        survey_id=survey_id,
        question_text=data['question_text'],
        question_type=data['question_type'],
        options=data.get('options')
    )
    db.session.add(new_question)
    db.session.commit()
    return jsonify({"message": "Question added", "questionID": new_question.questionID}), 201

# Route to submit a response to a question
@surveys_bp.route('/respond', methods=['POST'])
def submit_response():
    data = request.get_json()
    new_response = SurveyResponse(
        user_id=data['user_id'],
        question_id=data['question_id'],
        answer=data['answer']
    )
    db.session.add(new_response)
    db.session.commit()
    return jsonify({"message": "Response submitted", "responseID": new_response.responseID}), 201

# Route to get all surveys
@surveys_bp.route('/', methods=['GET'])
def get_surveys():
    surveys = Survey.query.all()
    return jsonify([{"surveyID": s.surveyID, "title": s.title, "description": s.description} for s in surveys]), 200