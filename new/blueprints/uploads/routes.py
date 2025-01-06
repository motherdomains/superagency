from flask import request, redirect, url_for
from . import uploads_bp

@uploads_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return f"File: {filename}"  # Add your file handling logic here