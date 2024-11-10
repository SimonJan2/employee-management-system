# app/utils/decorators.py
from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_permission(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# app/utils/aws.py
import boto3
from botocore.exceptions import ClientError
from flask import current_app
import uuid

def upload_file_to_s3(file):
    """Upload a file to S3 bucket"""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=current_app.config['AWS_DEFAULT_REGION']
    )
    
    # Generate unique filename
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    new_filename = f"{uuid.uuid4()}.{file_extension}"
    
    try:
        s3_client.upload_fileobj(
            file,
            current_app.config['S3_BUCKET'],
            new_filename,
            ExtraArgs={
                'ACL': 'public-read',
                'ContentType': file.content_type
            }
        )
        
        # Return the URL of the uploaded file
        return f"https://{current_app.config['S3_BUCKET']}.s3.amazonaws.com/{new_filename}"
        
    except ClientError as e:
        print(f"Error uploading file to S3: {str(e)}")
        raise

# app/utils/email.py
from flask_mail import Message
from app import mail
from flask import render_template

def send_email(to, subject, template, **kwargs):
    """Send an email"""
    msg = Message(
        subject,
        recipients=[to],
        html=render_template(template + '.html', **kwargs),
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)

def send_welcome_email(email, name, username, password):
    """Send welcome email with login credentials"""
    send_email(
        to=email,
        subject="Welcome to Employee Management System",
        template='email/welcome',
        name=name,
        username=username,
        password=password
    )

def send_password_reset_email(user):
    """Send password reset email"""
    token = user.get_reset_password_token()
    send_email(
        to=user.email,
        subject="Reset Your Password",
        template='email/reset_password',
        user=user,
        token=token
    )

# app/utils/helpers.py
import random
import string

def generate_password(length=12):
    """Generate a random password"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

def log_activity(user_id, action, description, target_type=None, target_id=None):
    """Log user activity"""
    activity = ActivityLog(
        user_id=user_id,
        action=action,
        description=description,
        target_type=target_type,
        target_id=target_id
    )
    db.session.add(activity)
    db.session.commit()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def format_currency(amount):
    """Format currency amount"""
    try:
        return "${:,.2f}".format(float(amount))
    except (ValueError, TypeError):
        return "$0.00"

def send_notification(user_id, title, message):
    """Send in-app notification"""
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message
    )
    db.session.add(notification)
    db.session.commit()