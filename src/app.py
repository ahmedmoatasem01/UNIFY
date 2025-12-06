from flask import Flask, render_template, session, redirect, url_for 
from flask import request, jsonify
from datetime import datetime
from controllers.auth_controller import auth_bp
from controllers.user_controller import user_bp
from controllers.student_controller import student_bp
from controllers.course_controller import course_bp
from controllers.task_controller import task_bp
from controllers.message_controller import message_bp
from controllers.enrollment_controller import enrollment_bp
from controllers.schedule_controller import schedule_bp
from controllers.calendar_controller import calendar_bp
import os

# --- Setup Flask app ---
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = 'unify-secret-key-change-in-production'

# --- Register Blueprints ---
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(student_bp)
app.register_blueprint(course_bp)
app.register_blueprint(task_bp)
app.register_blueprint(message_bp)
app.register_blueprint(enrollment_bp)
app.register_blueprint(schedule_bp)
app.register_blueprint(calendar_bp)
app.register_blueprint(course_reg_bp)

# --- Repository instances ---
try:
    user_repo = RepositoryFactory.get_repository('user')
    student_repo = RepositoryFactory.get_repository('student')
    course_repo = RepositoryFactory.get_repository('course')
    task_repo = RepositoryFactory.get_repository('task')
    enrollment_repo = RepositoryFactory.get_repository('enrollment')
    db_available = True
except Exception as e:
    print(f"Warning: Database not available: {e}")
    db_available = False
    user_repo = None
    student_repo = None
    course_repo = None
    task_repo = None
    enrollment_repo = None

DEFAULT_USER_ID = 1  # Only for fallback during dev

def get_default_user():
    """Return default user object"""
    return {
        'User_ID': DEFAULT_USER_ID,
        'Username': 'demo_user',
        'Email': 'demo@example.com',
        'name': 'Demo User',
        'role': 'student',
        'university': 'Zewail City',
        'major': 'Computer Science',
        'year': 'Sophomore'
    }

def get_default_stats():
    """Return default stats object"""
    return {
        'total_courses': 0,
        'active_tasks': 0,
        'upcoming_events': 0,
        'completed_assignments': 0,
        'gpa': 0.0,
        'credits_completed': 0,
        'credits_total': 0,
        'credits_percentage': 0
    }

def get_user_data(user_id):
    """Fetch user data from repository with fallback"""
    user = get_default_user()
    
    if db_available and user_repo:
        try:
            db_user = user_repo.get_by_id(user_id)
            if db_user:
                user = {
                    'User_ID': db_user.User_ID,
                    'Username': db_user.Username,
                    'Email': db_user.Email,
                    'name': db_user.Username,
                    'role': 'student',
                    'university': 'Zewail City',
                    'major': 'Computer Science',
                    'year': 'Sophomore'
                }
        except Exception as e:
            print(f"Error fetching user from database: {e}")
    
    return user

def get_user_stats(user_id):
    """Fetch user statistics from repositories with fallback"""
    stats = get_default_stats()
    
    if not (db_available and user_repo and student_repo):
        return stats
    
    try:
        # Get student record
        student = student_repo.get_by_user_id(user_id)
        if not student:
            return stats
        
        # Get GPA from student record
        if hasattr(student, 'GPA') and student.GPA:
            stats['gpa'] = float(student.GPA)
        
        # Get course count
        if enrollment_repo and hasattr(enrollment_repo, 'get_by_student_id'):
            try:
                enrollments = enrollment_repo.get_by_student_id(student.Student_ID)
                stats['total_courses'] = len(enrollments) if enrollments else 0
            except Exception as e:
                print(f"Error fetching enrollments: {e}")
        
        # Get active tasks
        if task_repo and hasattr(task_repo, 'get_by_user_id'):
            try:
                tasks = task_repo.get_by_user_id(user_id)
                if tasks:
                    stats['active_tasks'] = len([t for t in tasks if not getattr(t, 'Completed', False)])
                    stats['completed_assignments'] = len([t for t in tasks if getattr(t, 'Completed', False)])
            except Exception as e:
                print(f"Error fetching tasks: {e}")
        
        # Get upcoming events from schedule
        if schedule_repo and hasattr(schedule_repo, 'get_by_user_id'):
            try:
                schedules = schedule_repo.get_by_user_id(user_id)
                if schedules:
                    stats['upcoming_events'] = len(schedules)
            except Exception as e:
                print(f"Error fetching schedules: {e}")
        
        # Calculate credits (assuming each course = 3 credits)
        stats['credits_completed'] = stats['total_courses'] * 3
        stats['credits_total'] = 120  # Default degree requirement
        stats['credits_percentage'] = int((stats['credits_completed'] / stats['credits_total']) * 100) if stats['credits_total'] > 0 else 0
        
    except Exception as e:
        print(f"Error fetching user stats: {e}")
    
    return stats

def get_user_notifications(user_id):
    """Fetch user notifications from repository with fallback"""
    notifications = []
    
    if not (db_available and message_repo):
        return notifications
    
    try:
        if hasattr(message_repo, 'get_by_recipient_id'):
            messages = message_repo.get_by_recipient_id(user_id)
            if messages:
                notifications = [
                    {
                        'id': getattr(msg, 'Message_ID', i),
                        'title': getattr(msg, 'Subject', 'New Message'),
                        'message': getattr(msg, 'Content', '')[:100],
                        'type': 'message',
                        'priority': 'medium',
                        'read': getattr(msg, 'Read', False),
                        'time': getattr(msg, 'Sent_Date', 'Recently')
                    }
                    for i, msg in enumerate(messages[:5])
                ]
    except Exception as e:
        print(f"Error fetching notifications: {e}")
    
    return notifications

# --- Routes ---
@app.route('/')
def index():
    """Redirect to overview if logged in, otherwise to login"""
    if 'user_id' not in session:
        # Auto-set demo user for testing
        session['user_id'] = DEFAULT_USER_ID
    return redirect(url_for('overview'))

@app.route('/login')
def login_page():
    """Render login page"""
    return render_template('login.html')

@app.route('/overview')
@app.route('/dashboard')
def overview():
    """overview page - requires authentication"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('overview.html')  # You'll need to create this template


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)