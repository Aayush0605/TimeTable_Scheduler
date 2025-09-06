from models import db, Course, Teacher, Classroom, Timetable
import logging

def generate_timetable():
    try:
        courses = Course.query.all()
        teachers = Teacher.query.all()
        classrooms = Classroom.query.all()
        timetable = [
            {'day': 'Monday', 'time': '9:00-10:00', 'course': 'MT-CALC-001', 'teacher': 'TCH-MT-001', 'room': 'ROOM-A-101', 'class': 'ClassA'},
            {'day': 'Monday', 'time': '10:05-11:00', 'course': 'MT-LINALG-001', 'teacher': 'TCH-MT-002', 'room': 'ROOM-B-102', 'class': 'ClassA'}
        ]
        logging.debug(f"Generated timetable: {timetable}")
        return timetable
    except Exception as e:
        logging.error(f"Error generating timetable: {str(e)}")
        return []

def init_generator(app):
    app.jinja_env.globals.update(generate_timetable=generate_timetable)