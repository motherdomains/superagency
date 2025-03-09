from .models import Survey, SurveyQuestion, SurveyResponse

def validate_survey_data(data):
    if not data.get('title'):
        return False, "Title is required"
    return True, ""

def validate_question_data(data):
    if not data.get('question_text') or not data.get('question_type'):
        return False, "Question text and type are required"
    return True, ""