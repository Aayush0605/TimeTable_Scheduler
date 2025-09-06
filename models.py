from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

def generate_id(prefix, department, model, num_length=3):
    """Generate a meaningful ID like TCH-MT-001"""
    count = model.query.filter(model.id.like(f"{prefix}-{department}-%")).count() + 1
    return f"{prefix}-{department}-{count:0{num_length}d}"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, management, teacher, student
    associated_id = db.Column(db.String(50))  # teacher_id or class_id
    department = db.Column(db.String(10))  # MT, ET, HM, BTTM, FD, Pharma
    email = db.Column(db.String(100))  # For notifications

    def get_id(self):
        return self.id

class Teacher(db.Model):
    __tablename__ = 'teacher'
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(10), nullable=False)
    subjects = db.Column(db.String(200))  # e.g., "Calculus|Physics"
    availability = db.Column(db.String(200))  # e.g., "Monday:9-16"
    management_role = db.Column(db.String(50))  # e.g., "Dean of MT"
    preferences = db.Column(db.Text)  # JSON: {"no_back_to_back": true, "max_lectures": 5}

class Classroom(db.Model):
    __tablename__ = 'classrooms'
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    availability = db.Column(db.String(200))  # e.g., "Monday:9-16"
    room_type = db.Column(db.String(20))  # lecture, lab

class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(10), nullable=False)
    teacher_id = db.Column(db.String(50), db.ForeignKey('teacher.id'))
    class_size = db.Column(db.Integer, nullable=False)
    class_id = db.Column(db.String(50))  # e.g., ClassA

class Timetable(db.Model):
    __tablename__ = 'timetable'
    id = db.Column(db.String(50), primary_key=True)
    day = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(20), nullable=False)  # e.g., "9:00-10:00"
    course_id = db.Column(db.String(50), db.ForeignKey('course.id'))
    teacher_id = db.Column(db.String(50), db.ForeignKey('teacher.id'))
    room_id = db.Column(db.String(50), db.ForeignKey('classrooms.id'))
    class_id = db.Column(db.String(50))
    conflicts = db.Column(db.Integer, default=0)

    course = db.relationship('Course', backref='timetables')
    teacher = db.relationship('Teacher', backref='timetables')
    room = db.relationship('Classroom', backref='timetables')

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.String(50), primary_key=True)
    teacher_id = db.Column(db.String(50), db.ForeignKey('teacher.id'))
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # present/absent
    substitute_id = db.Column(db.String(50), db.ForeignKey('teacher.id'))

    teacher = db.relationship('Teacher', foreign_keys=[teacher_id], backref='attendances')
    substitute = db.relationship('Teacher', foreign_keys=[substitute_id], backref='substitute_attendances')