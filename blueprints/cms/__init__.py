from flask import Blueprint

def create_cms():
    cms_bp = Blueprint('cms', __name__, template_folder='templates', static_folder='static')

    @cms_bp.route('/')
    def index():
        return "Welcome to the CMS Home Page!"

    @cms_bp.route('/test')
    def test():
        return "CMS Test Route"

    return cms_bp