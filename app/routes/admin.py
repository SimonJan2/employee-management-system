# app/routes/admin.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.forms import LoginForm, RegistrationForm
from app.utils import upload_file_to_s3, allowed_file
from app import db

bp = Blueprint('admin', __name__, url_prefix='/admin')
@bp.route('/admin')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('main.dashboard'))
        
    stats = {
        'total_users': User.query.count(),
        'total_employees': Employee.query.count(),
        'active_tickets': Ticket.query.filter_by(status='open').count(),
        'departments': Department.query.count()
    }
    
    recent_activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_activities=recent_activities)

@bp.route('/admin/users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('main.dashboard'))
        
    users = User.query.all()
    roles = Role.query.all()
    return render_template('admin/users.html', users=users, roles=roles)

@bp.route('/admin/roles')
@login_required
def manage_roles():
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('main.dashboard'))
        
    roles = Role.query.all()
    permissions = Permission.query.all()
    return render_template('admin/roles.html', roles=roles, permissions=permissions)