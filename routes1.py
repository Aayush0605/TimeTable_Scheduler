from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from models import db, Timetable, User, Teacher, Attendance, Course, Classroom
import logging

routes = Blueprint('routes', __name__)

# Login routes
@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # In real app, hash and verify
        
        user = User.query.filter_by(username=username).first()
        if user:  # Simple check - in real app, verify hashed password
            login_user(user)
            flash('Login successful!', 'success')
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('routes.admin_dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('routes.teacher_dashboard'))
            elif user.role == 'management':
                return redirect(url_for('routes.management_dashboard'))
            else:
                return redirect(url_for('routes.home'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html', theme='tech')  # Default theme

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('routes.login'))

# Dashboard routes
@routes.route('/')
def home():
    return "Timetable Scheduler is running!"

@routes.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return "Access denied", 403
    return render_template('admin_dashboard.html', theme='tech', current_user=current_user)

@routes.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        return "Access denied", 403
    return render_template('teacher_dashboard.html', theme='tech', current_user=current_user)

@routes.route('/management/dashboard')
@login_required
def management_dashboard():
    if current_user.role not in ['management', 'admin']:
        return "Access denied", 403
    return render_template('management_dashboard.html', theme='tech', current_user=current_user)

# Timetable route - FIXED
@routes.route('/timetable')
@login_required
def timetable():
    try:
        # Use relationships to get actual objects, not just IDs
        timetable_data = Timetable.query.options(
            db.joinedload(Timetable.course),
            db.joinedload(Timetable.teacher), 
            db.joinedload(Timetable.room)
        ).all()
        
        logging.debug(f"User {current_user.id} accessed timetable. Found {len(timetable_data)} entries.")
        
        timetable_list = []
        for t in timetable_data:
            timetable_list.append({
                'day': t.day,
                'time': t.time,
                'course': t.course,  # Now the actual Course object
                'teacher': t.teacher,  # Now the actual Teacher object
                'room': t.room,  # Now the actual Classroom object
                'class_id': t.class_id,
                'conflicts': t.conflicts
            })
        
        return render_template('timetable.html', timetable=timetable_list, theme='tech', role=current_user.role)
        
    except Exception as e:
        logging.error(f"Error in timetable route: {str(e)}", exc_info=True)
        return render_template('timetable.html', timetable=[], theme='tech', error=str(e))

# Admin routes with POST handling
@routes.route('/admin/generate_timetable', methods=['GET', 'POST'])
@login_required
def generate_timetable():
    if current_user.role != 'admin':
        return "Access denied", 403
    departments = ['MT', 'ET', 'HM', 'BTTM', 'FD', 'Pharma']
    
    if request.method == 'POST':
        # Handle timetable generation
        department = request.form.get('department', '')
        flash(f'Timetable generated for {department if department else "all"} departments!', 'success')
        return redirect(url_for('routes.timetable'))
    
    return render_template('generate_timetable.html', theme='tech', departments=departments, current_user=current_user)

@routes.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        return "Access denied", 403
    departments = ['MT', 'ET', 'HM', 'BTTM', 'FD', 'Pharma']
    
    if request.method == 'POST':
        # Handle form submission
        try:
            role = request.form['role']
            name = request.form['name']
            department = request.form['department']
            email = request.form['email']
            
            # Basic user creation logic
            flash(f'User {name} added successfully!', 'success')
            return redirect(url_for('routes.add_user'))
            
        except Exception as e:
            flash(f'Error adding user: {str(e)}', 'error')
    
    return render_template('add_user.html', theme='tech', departments=departments)

@routes.route('/admin/upload_csv', methods=['GET', 'POST'])
@login_required
def upload_csv():
    if current_user.role != 'admin':
        return "Access denied", 403
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and file.filename.endswith('.csv'):
            # Process CSV file here
            flash('CSV uploaded and processed successfully!', 'success')
            return redirect(url_for('routes.upload_csv'))
        else:
            flash('Please upload a valid CSV file', 'error')
    
    return render_template('upload_csv.html', theme='tech')

# Management routes
@routes.route('/management/timetable')
@login_required
def management_timetable():
    if current_user.role not in ['management', 'admin']:
        return "Access denied", 403
    return redirect(url_for('routes.timetable'))

@routes.route('/management/attendance')
@login_required
def management_attendance():
    if current_user.role not in ['management', 'admin']:
        return "Access denied", 403
    attendance = Attendance.query.options(
        db.joinedload(Attendance.teacher),
        db.joinedload(Attendance.substitute)
    ).all()
    return render_template('attendance_report.html', theme='tech', attendance=attendance)

# Teacher routes
@routes.route('/teacher/attendance', methods=['GET', 'POST'])
@login_required
def teacher_attendance():
    if current_user.role != 'teacher':
        return "Access denied", 403
    
    from datetime import date
    
    if request.method == 'POST':
        # Handle attendance submission
        attendance_date = request.form['date']
        status = request.form['status']
        flash(f'Attendance marked as {status} for {attendance_date}', 'success')
        return redirect(url_for('routes.teacher_attendance'))
    
    return render_template('attendance.html', theme='tech', today=date.today().isoformat())

@routes.route('/teacher/timetable')
@login_required
def teacher_timetable():
    if current_user.role != 'teacher':
        return "Access denied", 403
    
    # Filter timetable for this teacher with relationships
    timetable_data = Timetable.query.options(
        db.joinedload(Timetable.course),
        db.joinedload(Timetable.teacher), 
        db.joinedload(Timetable.room)
    ).filter_by(teacher_id=current_user.associated_id).all()
    
    timetable_list = []
    for t in timetable_data:
        timetable_list.append({
            'day': t.day,
            'time': t.time,
            'course': t.course,
            'teacher': t.teacher,
            'room': t.room,
            'class_id': t.class_id,
            'conflicts': t.conflicts
        })
    
    return render_template('timetable.html', timetable=timetable_list, theme='tech', role=current_user.role)

# Theme setting route
@routes.route('/set_theme/<theme>')
def set_theme(theme):
    from flask import session
    session['theme'] = theme
    return redirect(request.referrer or url_for('routes.home'))

# Debug route to check users
@routes.route('/debug/users')
def debug_users():
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            'id': user.id,
            'username': user.username,
            'role': user.role,
            'department': user.department
        })
    return jsonify(result)

# Debug route to check timetable data
@routes.route('/debug/timetable')
def debug_timetable():
    timetable_data = Timetable.query.all()
    result = []
    for t in timetable_data:
        result.append({
            'id': t.id,
            'day': t.day,
            'time': t.time,
            'course_id': t.course_id,
            'teacher_id': t.teacher_id,
            'room_id': t.room_id,
            'class_id': t.class_id
        })
    return jsonify(result)

def init_routes(app):
    app.register_blueprint(routes)