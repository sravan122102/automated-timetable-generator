import os
import sys

# Add root directory to sys.path so we can import from root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, Teacher, TeacherAvailability, Subject, Classroom, ClassGroup, Assignment, TimeSlot, TimetableEntry
from scheduler import generate_timetable
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import datetime

app = Flask(__name__)
# Enable CORS for frontend
CORS(app)

# Database Configuration
# Fallback to local SQLite if DATABASE_URL is not set
# Use /tmp for Vercel's read-only filesystem if running as serverless without Postgres
default_db_path = '/tmp/database.db' if os.environ.get('VERCEL') else os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')
database_url = os.environ.get('DATABASE_URL', 'sqlite:///' + default_db_path)

# Render/Neon Postgres URLs start with postgres:// but SQLAlchemy requires postgresql://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
    
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

db.init_app(app)

# Ensure database tables and default admin exist before requests
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(username='admin', password_hash=generate_password_hash('password123')))
    
    if TimeSlot.query.count() == 0:
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        for day in days:
            for period in range(1, 9):
                db.session.add(TimeSlot(day_of_week=day, period_number=period, is_lunch_break=(period == 5)))
    
    db.session.commit()


# --- AUTHENTICATION ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        token = jwt.encode({
            'user': user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

# --- DASHBOARD STATS ---
@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify({
        'teachers': Teacher.query.count(),
        'subjects': Subject.query.count(),
        'classrooms': Classroom.query.count(),
        'classes': ClassGroup.query.count()
    })

# --- TEACHERS ---
@app.route('/api/teachers', methods=['GET', 'POST'])
def manage_teachers():
    if request.method == 'GET':
        teachers = Teacher.query.all()
        return jsonify([{'id': t.id, 'name': t.name} for t in teachers])
    
    if request.method == 'POST':
        data = request.json
        new_teacher = Teacher(name=data['name'])
        db.session.add(new_teacher)
        db.session.commit()
        return jsonify({'message': 'Teacher added', 'id': new_teacher.id})

@app.route('/api/teachers/<int:id>', methods=['DELETE'])
def delete_teacher(id):
    t = Teacher.query.get(id)
    if t:
        db.session.delete(t)
        db.session.commit()
    return jsonify({'message': 'Deleted'})

# --- SUBJECTS ---
@app.route('/api/subjects', methods=['GET', 'POST'])
def manage_subjects():
    if request.method == 'GET':
        subjects = Subject.query.all()
        return jsonify([{'id': s.id, 'name': s.name, 'weekly_hours': s.weekly_hours, 'needs_lab': s.needs_lab} for s in subjects])
    
    if request.method == 'POST':
        data = request.json
        new_subject = Subject(name=data['name'], weekly_hours=data['weekly_hours'], needs_lab=data.get('needs_lab', False))
        db.session.add(new_subject)
        db.session.commit()
        return jsonify({'message': 'Subject added', 'id': new_subject.id})

@app.route('/api/subjects/<int:id>', methods=['DELETE'])
def delete_subject(id):
    s = Subject.query.get(id)
    if s:
        db.session.delete(s)
        db.session.commit()
    return jsonify({'message': 'Deleted'})

# --- CLASSROOMS ---
@app.route('/api/classrooms', methods=['GET', 'POST'])
def manage_classrooms():
    if request.method == 'GET':
        rooms = Classroom.query.all()
        return jsonify([{'id': r.id, 'name': r.name, 'capacity': r.capacity, 'is_lab': r.is_lab} for r in rooms])
    
    if request.method == 'POST':
        data = request.json
        new_room = Classroom(name=data['name'], capacity=data['capacity'], is_lab=data.get('is_lab', False))
        db.session.add(new_room)
        db.session.commit()
        return jsonify({'message': 'Classroom added', 'id': new_room.id})

@app.route('/api/classrooms/<int:id>', methods=['DELETE'])
def delete_classroom(id):
    r = Classroom.query.get(id)
    if r:
        db.session.delete(r)
        db.session.commit()
    return jsonify({'message': 'Deleted'})

# --- CLASSES ---
@app.route('/api/classes', methods=['GET', 'POST'])
def manage_classes():
    if request.method == 'GET':
        classes = ClassGroup.query.all()
        return jsonify([{'id': c.id, 'name': c.name} for c in classes])
    
    if request.method == 'POST':
        data = request.json
        new_class = ClassGroup(name=data['name'])
        db.session.add(new_class)
        db.session.commit()
        return jsonify({'message': 'Class added', 'id': new_class.id})

@app.route('/api/classes/<int:id>', methods=['DELETE'])
def delete_class(id):
    c = ClassGroup.query.get(id)
    if c:
        db.session.delete(c)
        db.session.commit()
    return jsonify({'message': 'Deleted'})

# --- ASSIGNMENTS ---
@app.route('/api/assignments', methods=['GET', 'POST'])
def manage_assignments():
    if request.method == 'GET':
        assignments = Assignment.query.all()
        result = []
        for a in assignments:
            result.append({
                'id': a.id,
                'class_name': a.class_group.name,
                'subject_name': a.subject.name,
                'teacher_name': a.teacher.name
            })
        return jsonify(result)
        
    if request.method == 'POST':
        data = request.json
        new_assign = Assignment(class_id=data['class_id'], subject_id=data['subject_id'], teacher_id=data['teacher_id'])
        db.session.add(new_assign)
        db.session.commit()
        return jsonify({'message': 'Assignment added', 'id': new_assign.id})

# --- GENERATE ---
@app.route('/api/generate', methods=['POST'])
def trigger_generation():
    data = request.json
    class_id = data.get('class_id')
    success = generate_timetable(class_id)
    if success:
        return jsonify({'message': 'Timetable generated successfully!'})
    return jsonify({'message': 'Failed to generate completely'}), 400

# --- TIMETABLE VIEW ---
@app.route('/api/timetable/class/<int:class_id>', methods=['GET'])
def get_class_timetable(class_id):
    entries = TimetableEntry.query.join(Assignment).filter(Assignment.class_id == class_id).all()
    result = []
    for e in entries:
        result.append({
            'day': e.time_slot.day_of_week,
            'period': e.time_slot.period_number,
            'subject': e.assignment.subject.name,
            'teacher': e.assignment.teacher.name,
            'classroom': e.classroom.name
        })
    return jsonify(result)

@app.route('/api/timetable/teacher/<int:teacher_id>', methods=['GET'])
def get_teacher_timetable(teacher_id):
    entries = TimetableEntry.query.join(Assignment).filter(Assignment.teacher_id == teacher_id).all()
    result = []
    for e in entries:
        result.append({
            'day': e.time_slot.day_of_week,
            'period': e.time_slot.period_number,
            'subject': e.assignment.subject.name,
            'class_name': e.assignment.class_group.name,
            'classroom': e.classroom.name
        })
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
