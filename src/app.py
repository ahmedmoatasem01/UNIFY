from flask import Flask, render_template, session, redirect, url_for, jsonify, request
from controllers.auth_controller import auth_bp
from controllers.user_controller import user_bp
from controllers.student_controller import student_bp
from controllers.course_controller import course_bp
from controllers.task_controller import task_bp
from controllers.message_controller import message_bp
from controllers.enrollment_controller import enrollment_bp
from controllers.schedule_controller import schedule_bp
from controllers.calendar_controller import calendar_bp
from controllers.course_registration_controller import course_reg_bp
from repositories.repository_factory import RepositoryFactory
from utils.schedule_loader import get_today_schedule, get_sample_schedule
from core.user_helper import get_user_data
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = os.environ.get('SECRET_KEY', 'unify-secret-key-change-in-production')

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
    message_repo = RepositoryFactory.get_repository('message')
    schedule_repo = RepositoryFactory.get_repository('schedule')
    db_available = True
except Exception as e:
    print(f"Warning: Database not available: {e}")
    db_available = False
    user_repo = None
    student_repo = None
    course_repo = None
    task_repo = None
    enrollment_repo = None
    message_repo = None
    schedule_repo = None

DEFAULT_USER_ID = 1  # Fallback user ID for testing


def get_default_user():
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
    user = get_default_user()
    if db_available and user_repo:
        try:
            db_user = user_repo.get_by_id(user_id)
            if db_user:
                user = {
                    'User_ID': getattr(db_user, 'User_ID', DEFAULT_USER_ID),
                    'Username': getattr(db_user, 'Username', 'demo_user'),
                    'Email': getattr(db_user, 'Email', 'demo@example.com'),
                    'name': getattr(db_user, 'Username', 'Demo User'),
                    'role': getattr(db_user, 'Role', 'student') if hasattr(db_user, 'Role') else 'student',
                    'university': getattr(db_user, 'University', 'Zewail City') if hasattr(db_user, 'University') else 'Zewail City',
                    'major': getattr(db_user, 'Major', 'Computer Science') if hasattr(db_user, 'Major') else 'Computer Science',
                    'year': getattr(db_user, 'Year', 'Sophomore') if hasattr(db_user, 'Year') else 'Sophomore'
                }
        except Exception as e:
            print(f"Error fetching user from database: {e}")
    return user


def get_user_stats(user_id):
    stats = get_default_stats()
    if not (db_available and user_repo and student_repo):
        return stats
    try:
        student = student_repo.get_by_user_id(user_id)
        if not student:
            return stats
        if hasattr(student, 'GPA') and student.GPA:
            stats['gpa'] = float(student.GPA)
        # enrollments
        if enrollment_repo and hasattr(enrollment_repo, 'get_by_student_id'):
            try:
                enrollments = enrollment_repo.get_by_student_id(getattr(student, 'Student_ID', None))
                stats['total_courses'] = len(enrollments) if enrollments else 0
            except Exception:
                pass
        # tasks
        if task_repo and hasattr(task_repo, 'get_by_user_id'):
            try:
                tasks = task_repo.get_by_user_id(user_id)
                if tasks:
                    stats['active_tasks'] = len([t for t in tasks if not getattr(t, 'Completed', False)])
                    stats['completed_assignments'] = len([t for t in tasks if getattr(t, 'Completed', False)])
            except Exception:
                pass
        # schedules/events
        if schedule_repo and hasattr(schedule_repo, 'get_by_user_id'):
            try:
                schedules = schedule_repo.get_by_user_id(user_id)
                if schedules:
                    stats['upcoming_events'] = len(schedules)
            except Exception:
                pass
        stats['credits_completed'] = stats['total_courses'] * 3
        stats['credits_total'] = 120
        stats['credits_percentage'] = int((stats['credits_completed'] / stats['credits_total']) * 100) if stats['credits_total'] > 0 else 0
    except Exception as e:
        print(f"Error fetching user stats: {e}")
    return stats


def get_user_notifications(user_id):
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
                        'message': getattr(msg, 'Content', '')[:200],
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


# Inject `user_data` into all templates so `topbar.html` can access it
@app.context_processor
def inject_user_data():
    try:
        user_id = session.get('user_id', DEFAULT_USER_ID)
        return {'user_data': get_user_data(user_id)}
    except Exception:
        return {'user_data': None}


# --- Routes ---
@app.route('/')
def index():
    if 'user_id' not in session:
        session['user_id'] = DEFAULT_USER_ID
    return redirect(url_for('overview'))


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/overview')
@app.route('/dashboard')
def overview():
    """Overview page - requires authentication"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    user_id = session.get('user_id', DEFAULT_USER_ID)
    user = get_user_data(user_id)
    return render_template('overview.html', user=user, user_data=user)


@app.route('/schedule')
def schedule_page():
    """Schedule page - requires authentication"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    user_data = get_user_data(session.get('user_id'))
    return render_template('schedule.html', user_data=user_data)


@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    user_id = session.get('user_id', DEFAULT_USER_ID)
    user = get_user_data(user_id)
    user_settings = {
        'notifications': {'email': True, 'push': True, 'calendar_reminders': True, 'assignment_deadlines': True},
        'calendar': {'sync_google': False, 'default_view': 'week', 'timezone': 'Africa/Cairo'},
        'appearance': {'theme': 'light', 'language': 'en', 'colorblind_mode': False, 'dyslexia_font': False},
        'privacy': {'profile_visibility': 'public', 'share_schedule': False}
    }
    return render_template('settings.html', user=user, settings=user_settings)


@app.route('/api/settings/update', methods=['POST'])
def update_settings():
    data = request.json
    return jsonify({'success': True, 'message': 'Settings updated successfully'})


@app.route('/api/stats')
def get_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user_id = session.get('user_id', DEFAULT_USER_ID)
    stats = get_user_stats(user_id)
    return jsonify(stats)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)