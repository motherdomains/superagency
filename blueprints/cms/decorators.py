# blueprints/cms/decorators.py

from flask import request, abort

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.admin:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function