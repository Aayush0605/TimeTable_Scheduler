from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, login_user, logout_user
from models import db, User, Timetable, Attendance
import logging

routes = Blueprint('routes', __name__)

# Basic routes
@routes.route('/')
def home():
    return "Timetable Scheduler is running!"

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('routes.admin_dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('routes.teacher_dashboard'))
            else:
                return redirect(url_for('routes.home'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('routes.login'))

# Dashboard routes
@routes.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('routes.home'))
    return render_template('admin_dashboard.html')

@routes.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('routes.home'))
    return render_template('teacher_dashboard.html')

# Timetable route (SIMPLIFIED)
@routes.route('/timetable')
@login_required
def timetable():
    try:
        timetable_data = Timetable.query.limit(10).all()  # Limit to 10 entries for testing
        
        simple_timetable = []
        for t in timetable_data:
            simple_timetable.append({
                'day': t.day or 'Monday',
                'time': t.time or '9:00-10:00',
                'course': getattr(t, 'course_id', 'N/A'),
                'teacher': getattr(t, 'teacher_id', 'N/A'),
                'room': getattr(t, 'room_id', 'N/A'),
                'class_id': getattr(t, 'class_id', 'N/A')
            })
        
        return render_template('timetable.html', timetable=simple_timetable)
        
    except Exception as e:
        logging.error(f"Timetable error: {str(e)}")
        return render_template('timetable.html', timetable=[], error="Could not load timetable")

# Basic form handlers
@routes.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        return "Access denied", 403
    
    if request.method == 'POST':
        flash('User added successfully (demo)', 'success')
        return redirect(url_for('routes.add_user'))
    
    return render_template('add_user.html')

@routes.route('/admin/upload_csv', methods=['GET', 'POST'])
@login_required
def upload_csv():
    if current_user.role != 'admin':
        return "Access denied", 403
    
    if request.method == 'POST':
        flash('CSV uploaded successfully (demo)', 'success')
        return redirect(url_for('routes.upload_csv'))
    
    return render_template('upload_csv.html')

# Debug route
@routes.route('/debug')
def debug_info():
    users = User.query.all()
    timetable_count = Timetable.query.count()
    
    return f"""
    <h1>Debug Information</h1>
    <p>Users: {len(users)}</p>
    <p>Timetable entries: {timetable_count}</p>
    <p>Current user: {current_user.is_authenticated}</p>
    <p><a href="/">Home</a></p>
    """

def init_routes(app):
    app.register_blueprint(routes)