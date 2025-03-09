from flask import Blueprint

def create_cms():
    cms_bp = Blueprint('cms', __name__, template_folder='templates')

    @cms_bp.route('/')
    def cms_home():
        return "Welcome to the CMS Home!"

    @cms_bp.route('/test')
    def cms_test():
        return "This is a test route in the CMS blueprint!"

    return cms_bp