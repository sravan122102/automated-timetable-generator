from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    availabilities = db.relationship('TeacherAvailability', backref='teacher', cascade='all, delete-orphan')
    assignments = db.relationship('Assignment', backref='teacher', cascade='all, delete-orphan')

class TeacherAvailability(db.Model):
    __tablename__ = 'teacher_availability'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False) # e.g., 'Monday'
    period_number = db.Column(db.Integer, nullable=False) # e.g., 1, 2, 3

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    weekly_hours = db.Column(db.Integer, nullable=False)
    needs_lab = db.Column(db.Boolean, default=False)
    assignments = db.relationship('Assignment', backref='subject', cascade='all, delete-orphan')

class Classroom(db.Model):
    __tablename__ = 'classrooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    is_lab = db.Column(db.Boolean, default=False)

class ClassGroup(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False) # e.g., 'II BCA A'
    assignments = db.relationship('Assignment', backref='class_group', cascade='all, delete-orphan')

class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)

class TimeSlot(db.Model):
    __tablename__ = 'time_slots'
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.String(20), nullable=False)
    period_number = db.Column(db.Integer, nullable=False)
    is_lunch_break = db.Column(db.Boolean, default=False)

class TimetableEntry(db.Model):
    __tablename__ = 'timetable_entries'
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    time_slot_id = db.Column(db.Integer, db.ForeignKey('time_slots.id'), nullable=False)
    assignment = db.relationship('Assignment')
    classroom = db.relationship('Classroom')
    time_slot = db.relationship('TimeSlot')
