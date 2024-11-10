# app/routes/ticket.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.forms import LoginForm, RegistrationForm
from app.utils import upload_file_to_s3, allowed_file
from app import db

bp = Blueprint('ticket', __name__, url_prefix='/tickets')
@bp.route('/tickets')
@login_required
def list_tickets():
    tickets = Ticket.query.all()
    return render_template('ticket/list.html', tickets=tickets)

@bp.route('/tickets/create', methods=['POST'])
@login_required
def create_ticket():
    form = TicketForm()
    if form.validate_on_submit():
        ticket = Ticket(
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data,
            created_by=current_user,
            assigned_to_id=form.assigned_to.data
        )
        db.session.add(ticket)
        db.session.commit()
        
        # Log activity
        log_activity(
            user_id=current_user.id,
            action='created_ticket',
            description=f'Created ticket: {ticket.title}',
            target_type='ticket',
            target_id=ticket.id
        )
        
        flash('Ticket created successfully', 'success')
        return redirect(url_for('ticket.view_ticket', ticket_id=ticket.id))
        
    return render_template('ticket/list.html', form=form)

@bp.route('/tickets/<ticket_id>')
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    return render_template('ticket/view.html', ticket=ticket)

@bp.route('/tickets/<ticket_id>/comment', methods=['POST'])
@login_required
def add_comment(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        comment = TicketComment(
            ticket=ticket,
            user=current_user,
            comment=form.comment.data
        )
        db.session.add(comment)
        db.session.commit()
        
        # Notify assigned user
        if ticket.assigned_to_id != current_user.id:
            send_notification(
                user_id=ticket.assigned_to_id,
                title=f'New comment on ticket #{ticket.id}',
                message=f'{current_user.full_name} commented on ticket: {ticket.title}'
            )
        
        flash('Comment added successfully', 'success')
        
    return redirect(url_for('ticket.view_ticket', ticket_id=ticket_id))