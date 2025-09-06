import smtplib
from email.mime.text import MIMEText
import logging
from models import db, User, Teacher, Course, Classroom, Timetable, Attendance
import datetime

def send_email(to_email, subject, body):
    try:
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        sender_email = 'sih.2025.auth@gmail.com'
        sender_password = 'project2025'
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = to_email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        logging.debug(f"Email sent to {to_email}")
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")

def generate_id(prefix, department, model, num_length=3):
    count = model.query.filter(model.id.like(f"{prefix}-{department}-%")).count() + 1
    return f"{prefix}-{department}-{count:0{num_length}d}"

def init_demo_data():
    try:
        if not Teacher.query.first():
            # Add teachers
            db.session.add(Teacher(
                id=generate_id('TCH', 'MT', Teacher),
                name='Prof. Jones',
                department='MT',
                subjects='Calculus|Linear Algebra',
                availability='Monday:9-12,Tuesday:9-12',
                management_role='Head',
                preferences='{"no_back_to_back": true, "max_lectures": 5}'
            ))
            db.session.add(Teacher(
                id=generate_id('TCH', 'MT', Teacher),
                name='Dr. Smith',
                department='MT',
                subjects='Statistics',
                availability='Monday:13-16,Wednesday:9-12'
            ))
            db.session.commit()
            logging.debug("Teachers initialized")

        if not Classroom.query.first():
            # Add classrooms
            db.session.add(Classroom(
                id=generate_id('ROOM', 'A', Classroom),
                name='Lecture Hall A101',
                capacity=30,
                availability='Monday:9-16',
                room_type='lecture'
            ))
            db.session.add(Classroom(
                id=generate_id('ROOM', 'B', Classroom),
                name='Lab B102',
                capacity=25,
                availability='Monday:9-16',
                room_type='lab'
            ))
            db.session.commit()
            logging.debug("Classrooms initialized")

        if not Course.query.first():
            # Add courses
            teacher1 = Teacher.query.filter_by(name='Prof. Jones').first()
            teacher2 = Teacher.query.filter_by(name='Dr. Smith').first()
            db.session.add(Course(
                id=generate_id('MT-CALC', 'MT', Course),
                name='Calculus',
                department='MT',
                teacher_id=teacher1.id,
                class_size=25,
                class_id='ClassA'
            ))
            db.session.add(Course(
                id=generate_id('MT-LINALG', 'MT', Course),
                name='Linear Algebra',
                department='MT',
                teacher_id=teacher2.id,
                class_size=25,
                class_id='ClassA'
            ))
            db.session.commit()
            logging.debug("Courses initialized")

        if not Timetable.query.first():
            # Add timetable
            course1 = Course.query.filter_by(name='Calculus').first()
            course2 = Course.query.filter_by(name='Linear Algebra').first()
            teacher1 = Teacher.query.filter_by(name='Prof. Jones').first()
            teacher2 = Teacher.query.filter_by(name='Dr. Smith').first()
            room1 = Classroom.query.filter_by(name='Lecture Hall A101').first()
            room2 = Classroom.query.filter_by(name='Lab B102').first()
            db.session.add(Timetable(
                id=generate_id('TT', 'MT', Timetable),
                day='Monday',
                time='9:00-10:00',
                course_id=course1.id,
                teacher_id=teacher1.id,
                room_id=room1.id,
                class_id='ClassA',
                conflicts=0
            ))
            db.session.add(Timetable(
                id=generate_id('TT', 'MT', Timetable),
                day='Monday',
                time='10:05-11:00',
                course_id=course2.id,
                teacher_id=teacher2.id,
                room_id=room2.id,
                class_id='ClassA',
                conflicts=0
            ))
            db.session.commit()
            logging.debug("Timetable initialized")

        if not User.query.first():
            # Add users
            teacher1 = Teacher.query.filter_by(name='Prof. Jones').first()
            db.session.add(User(
                id=generate_id('ADMIN', 'MT', User),
                username='admin',
                password_hash='$2b$12$examplehash1234567890abcdef',
                role='admin',
                department='MT',
                email='admin@example.com'
            ))
            db.session.add(User(
                id=generate_id('TEACHER', 'MT', User),
                username='teacher1',
                password_hash='$2b$12$examplehash1234567890abcdef',
                role='teacher',
                associated_id=teacher1.id,
                department='MT',
                email='teacher1@example.com'
            ))
            db.session.commit()
            logging.debug("Users initialized")

        if not Attendance.query.first():
            # Add attendance
            teacher1 = Teacher.query.filter_by(name='Prof. Jones').first()
            teacher2 = Teacher.query.filter_by(name='Dr. Smith').first()
            db.session.add(Attendance(
                id=generate_id('ATT', 'MT', Attendance),
                teacher_id=teacher1.id,
                date=datetime.date(2025, 9, 5),
                status='present',
                substitute_id=None
            ))
            db.session.add(Attendance(
                id=generate_id('ATT', 'MT', Attendance),
                teacher_id=teacher2.id,
                date=datetime.date(2025, 9, 5),
                status='absent',
                substitute_id=teacher1.id
            ))
            db.session.commit()
            logging.debug("Attendance initialized")
    except Exception as e:
        logging.error(f"Error in init_demo_data: {str(e)}")
        db.session.rollback()
        raise

def init_utils(app):
    app.jinja_env.globals.update(send_email=send_email)