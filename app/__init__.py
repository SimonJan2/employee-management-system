from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import Config
import time
import psycopg2

db = SQLAlchemy()
login_manager = LoginManager()

def wait_for_db(app):
    retries = 5
    while retries > 0:
        try:
            # Try to connect to the database
            conn = psycopg2.connect(app.config['SQLALCHEMY_DATABASE_URI'])
            conn.close()
            return True
        except psycopg2.OperationalError:
            retries -= 1
            print(f"Database not ready, waiting... ({retries} retries left)")
            time.sleep(5)
    return False

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Wait for database to be ready
    if not wait_for_db(app):
        raise RuntimeError("Could not connect to database")

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    with app.app_context():
        # Import models
        from .models import User, Department, Employee, Ticket, Permission
        
        # Create tables
        db.create_all()

        # Register blueprints
        from .routes import auth, employee, ticket, admin
        app.register_blueprint(auth.bp)
        app.register_blueprint(employee.bp)
        app.register_blueprint(ticket.bp)
        app.register_blueprint(admin.bp)

        return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(user_id)