from flask import current_app
import uuid

def allowed_file(filename):
    """
    Check if the file extension is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def generate_unique_filename(filename):
    """
    Generate a unique filename while preserving the original extension
    """
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return f"{str(uuid.uuid4())}.{ext}"

def format_currency(amount):
    """
    Format currency amount
    """
    try:
        return "${:,.2f}".format(float(amount))
    except (ValueError, TypeError):
        return "$0.00"