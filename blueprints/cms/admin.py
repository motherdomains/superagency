# blueprints/cms/admin.py

from .routes import cms as cms_blueprint  # Import the blueprint directly from routes.py

@admin_required
@cms_blueprint.route('/dashboard')
def dashboard():
    return render_template('cms/dashboard.html')

# Other admin-related code...