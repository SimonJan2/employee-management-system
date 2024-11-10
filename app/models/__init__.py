# Option 1: Using absolute imports
from app.models.user import User
from app.models.department import Department
from app.models.employee import Employee
from app.models.ticket import Ticket
from app.models.permission import Permission
from app.models.role import Role
from app.models.ticket_comment import TicketComment
from app.models.activity_log import ActivityLog

# Option 2: Using relative imports with explicit dot notation
# from .user import User
# from .department import Department
# from .employee import Employee
# from .ticket import Ticket
# from .permission import Permission
# from .role import Role
# from .ticket_comment import TicketComment
# from .activity_log import ActivityLog

__all__ = [
    'User',
    'Department',
    'Employee',
    'Ticket',
    'Permission',
    'Role',
    'TicketComment',
    'ActivityLog'
]