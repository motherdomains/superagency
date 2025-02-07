from extensions import db
from datetime import datetime
from sqlalchemy import JSON, Enum

class Survey(db.Model):
    __tablename__ = 'surveys'
    surveyID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

class SurveyQuestion(db.Model):
    __tablename__ = 'surveyQuestions'
    questionID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.surveyID'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum('select_field', 'multiple_choice', 'scale', 'open_ended', name='question_type'), nullable=False)
    options = db.Column(db.JSON, nullable=True)  # Ensure options is nullable

class SurveyResponse(db.Model):
    __tablename__ = 'surveyResponses'
    responseID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('surveyUsers.userID'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('surveyQuestions.questionID'), nullable=False)
    answer = db.Column(db.Text)
    responded_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

class SurveyUser(db.Model):
    __tablename__ = 'surveyUsers'
    userID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    contact_info = db.Column(db.Text)