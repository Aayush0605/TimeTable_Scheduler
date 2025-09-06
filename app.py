import sys
import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# local imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from routes1 import init_routes
from models import db
from timetable_generator import init_generator
from utils import init_utils

# Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sih-smart-classroom'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://scheduler_user:aayush.new12@localhost:3307/scheduler'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # This will show SQL queries in logs

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

# Logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Init DB
db.init_app(app)

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'routes.login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(user_id)

# Initialize components
with app.app_context():
    try:
        db.create_all()
        from utils import init_demo_data
        init_demo_data()
        logging.debug("Database and demo data initialized successfully")
    except Exception as e:
        logging.error(f"Initialization error: {str(e)}")
        print(f"Initialization error: {str(e)}")

# Initialize routes and utilities
init_routes(app)
init_generator(app)
init_utils(app)

if __name__ == '__main__':
    print("Starting Flask server...")
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        logging.error(f"Error starting server: {str(e)}")
        print(f"Error starting server: {str(e)}")