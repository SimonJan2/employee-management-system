# app/routes/api.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.forms import LoginForm, RegistrationForm
from app.utils import upload_file_to_s3, allowed_file
from app import db

bp = Blueprint('api', __name__, url_prefix='/api')
@bp.route('/api/users/<user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'profile_picture_url': user.profile_picture_url,
        'is_active': user.is_active,
        'roles': [{'id': role.id, 'name': role.name} for role in user.roles]
    })

@bp.route('/api/tickets/<ticket_id>', methods=['GET'])
@login_required
def get_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    return jsonify({
        'id': ticket.id,
        'title': ticket.title,
        'description': ticket.description,
        'status': ticket.status,
        'priority': ticket.priority,
        'created_at': ticket.created_at.isoformat(),
        'created_by': {
            'id': ticket.created_by.id,
            'name': ticket.created_by.full_name,
            'profile_picture_url': ticket.created_by.profile_picture_url
        },
        'assigned_to': {
            'id': ticket.assigned_to.id,
            'name': ticket.assigned_to.full_name,
            'profile_picture_url': ticket.assigned_to.profile_picture_url
        } if ticket.assigned_to else None,
        'comments': [{
            'id': comment.id,
            'user': {
                'id': comment.user.id,
                'name': comment.user.full_name,
                'profile_picture_url': comment.user.profile_picture_url
            },
            'comment': comment.comment,
            'created_at': comment.created_at.isoformat()
        } for comment in ticket.comments]
    })

@bp.route('/api/tickets/<ticket_id>/status', methods=['PUT'])
@login_required
def update_ticket_status(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if not current_user.has_permission('ticket_manage') and ticket.assigned_to_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    ticket.status = data.get('status')
    db.session.commit()
    
    # Log activity
    log_activity(
        user_id=current_user.id,
        action='updated_ticket_status',
        description=f'Updated ticket #{ticket.id} status to {ticket.status}',
        target_type='ticket',
        target_id=ticket.id
    )
    
    return jsonify({'status': 'success'})

@bp.route('/api/employees/<employee_id>', methods=['GET'])
@login_required
def get_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    return jsonify({
        'id': employee.id,
        'user': {
            'id': employee.user.id,
            'email': employee.user.email,
            'first_name': employee.user.first_name,
            'last_name': employee.user.last_name,
            'profile_picture_url': employee.user.profile_picture_url
        },
        'department': {
            'id': employee.department.id,
            'name': employee.department.name
        } if employee.department else None,
        'position': employee.position,
        'hire_date': employee.hire_date.isoformat(),
        'statistics': {
            'active_tickets': Ticket.query.filter_by(
                assigned_to_id=employee.user.id, 
                status='open'
            ).count(),
            'completed_tickets': Ticket.query.filter_by(
                assigned_to_id=employee.user.id, 
                status='closed'
            ).count(),
            'recent_activities': [{
                'action': activity.action,
                'description': activity.description,
                'created_at': activity.created_at.isoformat()
            } for activity in ActivityLog.query.filter_by(
                user_id=employee.user.id
            ).order_by(ActivityLog.created_at.desc()).limit(5)]
        }
    })

@bp.route('/api/departments/<department_id>', methods=['GET'])
@login_required
def get_department(department_id):
    department = Department.query.get_or_404(department_id)
    return jsonify({
        'id': department.id,
        'name': department.name,
        'description': department.description,
        'employee_count': len(department.employees),
        'employees': [{
            'id': emp.id,
            'name': emp.user.full_name,
            'position': emp.position
        } for emp in department.employees]
    })

@bp.route('/api/roles/<role_id>', methods=['GET'])
@login_required
@admin_required
def get_role(role_id):
    role = Role.query.get_or_404(role_id)
    return jsonify({
        'id': role.id,
        'name': role.name,
        'description': role.description,
        'permissions': [{
            'id': perm.id,
            'name': perm.name,
            'description': perm.description
        } for perm in role.permissions]
    })

@bp.route('/api/users/<user_id>/roles', methods=['PUT'])
@login_required
@admin_required
def update_user_roles(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    role_ids = data.get('role_ids', [])
    
    # Update user roles
    user.roles = Role.query.filter(Role.id.in_(role_ids)).all()
    db.session.commit()
    
    # Log activity
    log_activity(
        user_id=current_user.id,
        action='updated_user_roles',
        description=f'Updated roles for user: {user.full_name}',
        target_type='user',
        target_id=user.id
    )
    
    return jsonify({'status': 'success'})

@bp.route('/api/upload/profile-picture', methods=['POST'])
@login_required
def upload_profile_picture():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
        
    try:
        file_url = upload_file_to_s3(file)
        return jsonify({'url': file_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'notifications': [{
            'id': notif.id,
            'title': notif.title,
            'message': notif.message,
            'is_read': notif.is_read,
            'created_at': notif.created_at.isoformat()
        } for notif in notifications.items],
        'total_pages': notifications.pages,
        'current_page': page,
        'total_items': notifications.total
    })

@bp.route('/api/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    data = request.get_json()
    notification_ids = data.get('notification_ids', [])
    
    if notification_ids:
        Notification.query.filter(
            Notification.id.in_(notification_ids),
            Notification.user_id == current_user.id
        ).update({Notification.is_read: True}, synchronize_session=False)
    else:
        # Mark all as read if no specific IDs provided
        Notification.query.filter_by(user_id=current_user.id)\
            .update({Notification.is_read: True}, synchronize_session=False)
    
    db.session.commit()
    return jsonify({'status': 'success'})

@bp.route('/api/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    # Get user-specific statistics
    if current_user.is_admin:
        stats = {
            'total_users': User.query.count(),
            'total_employees': Employee.query.count(),
            'total_departments': Department.query.count(),
            'active_tickets': Ticket.query.filter_by(status='open').count(),
            'tickets_by_priority': {
                'low': Ticket.query.filter_by(priority='low').count(),
                'medium': Ticket.query.filter_by(priority='medium').count(),
                'high': Ticket.query.filter_by(priority='high').count(),
                'urgent': Ticket.query.filter_by(priority='urgent').count()
            },
            'tickets_by_status': {
                'open': Ticket.query.filter_by(status='open').count(),
                'in_progress': Ticket.query.filter_by(status='in_progress').count(),
                'resolved': Ticket.query.filter_by(status='resolved').count(),
                'closed': Ticket.query.filter_by(status='closed').count()
            },
            'department_stats': [{
                'name': dept.name,
                'employee_count': len(dept.employees)
            } for dept in Department.query.all()]
        }
    else:
        stats = {
            'my_tickets': Ticket.query.filter_by(
                assigned_to_id=current_user.id,
                status='open'
            ).count(),
            'completed_tickets': Ticket.query.filter_by(
                assigned_to_id=current_user.id,
                status='closed'
            ).count(),
            'department_members': Employee.query.filter_by(
                department_id=current_user.employee.department_id
            ).count() if current_user.employee else 0
        }
    
    return jsonify(stats)

# Error handlers
@bp.errorhandler(404)
def not_found_error(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Resource not found'}), 404
    return render_template('errors/404.html'), 404

@bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('errors/500.html'), 500