# app/routes/employee.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.forms import LoginForm, RegistrationForm
from app.utils import upload_file_to_s3, allowed_file
from app import db

bp = Blueprint('employee', __name__, url_prefix='/employees')
@bp.route('/employees')
@login_required
def list_employees():
    employees = Employee.query.all()
    return render_template('employee/list.html', employees=employees)

@bp.route('/employees/add', methods=['POST'])
@login_required
def add_employee():
    if not current_user.has_permission('employee_manage'):
        flash('Permission denied', 'error')
        return redirect(url_for('employee.list_employees'))
        
    form = EmployeeForm()
    if form.validate_on_submit():
        # Handle profile picture upload
        profile_picture_url = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                profile_picture_url = upload_file_to_s3(file)

        user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            profile_picture_url=profile_picture_url
        )
        user.password = generate_password()  # Generate random password
        
        employee = Employee(
            user=user,
            department_id=form.department_id.data,
            position=form.position.data,
            hire_date=form.hire_date.data,
            salary=form.salary.data
        )
        
        db.session.add(user)
        db.session.add(employee)
        db.session.commit()
        
        # Send welcome email with credentials
        send_welcome_email(user.email, user.full_name, form.email.data, password)
        
        flash('Employee added successfully', 'success')
        return redirect(url_for('employee.list_employees'))
        
    return render_template('employee/list.html', form=form)