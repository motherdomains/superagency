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

# Route to display a survey for users to fill out
@surveys_bp.route('/<int:survey_id>', methods=['GET'])
def view_survey(survey_id):
    # Retrieve the survey and its questions
    survey = Survey.query.get_or_404(survey_id)
    questions = SurveyQuestion.query.filter_by(survey_id=survey_id).all()
    
    # Render the survey template with the survey and questions
    return render_template('view_survey.html', survey=survey, questions=questions)

# Route to submit responses for a survey
@surveys_bp.route('/<int:survey_id>/respond', methods=['POST'])
def submit_response(survey_id):
    data = request.form  # Use form data for user responses
    user_id = session.get('user_id')  # Assuming the user is logged in and their ID is stored in the session

    # Iterate through the submitted responses
    for question_id, answer in data.items():
        if question_id.startswith('question_'):
            question_id = int(question_id.replace('question_', ''))
            new_response = SurveyResponse(
                user_id=user_id,
                question_id=question_id,
                answer=answer
            )
            db.session.add(new_response)
    
    db.session.commit()
    flash('Thank you for completing the survey!', 'success')
    return redirect(url_for('surveys.view_survey', survey_id=survey_id))

# Route to get all surveys
@surveys_bp.route('/', methods=['GET'])
def get_surveys():
    surveys = Survey.query.all()
    return jsonify([{"surveyID": s.surveyID, "title": s.title, "description": s.description} for s in surveys]), 200