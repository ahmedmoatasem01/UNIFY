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
from repositories.repository_factory import RepositoryFactory
from utils.schedule_loader import get_today_schedule
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

# --- Repository instances ---
user_repo = RepositoryFactory.get_repository('user')
student_repo = RepositoryFactory.get_repository('student')
course_repo = RepositoryFactory.get_repository('course')
task_repo = RepositoryFactory.get_repository('task')
enrollment_repo = RepositoryFactory.get_repository('enrollment')

# --- Fallback sample data for demo/dev ---
SAMPLE_USER = {
    'User_ID': 1,
    'Username': 'demo_user',
    'Email': 'demo@example.com',
    'name': 'Demo User',
    'role': 'student',
    'university': 'Zewail City',
    'major': 'Computer Science',
    'year': 'Sophomore'
}

SAMPLE_STATS = {
    'total_courses': 0,
    'active_tasks': 0,
    'upcoming_events': 0,
    'completed_assignments': 0,
    'gpa': 0,
    'credits_completed': 0,
    'credits_total': 0,
    'credits_percentage': 0
}

SAMPLE_NOTIFICATIONS = []

DEFAULT_USER_ID = 1  # Only for fallback during dev

# --- Routes ---
@app.route('/')
def index():
    """Redirect to login page"""
    return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    """Render login page"""
    return render_template('login.html')

@app.route('/overview')
def overview():
    """Overview/Dashboard page – requires login"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    user_id = session.get('user_id', DEFAULT_USER_ID)
    
    try:
        # Fetch user from repository
        user = user_repo.get_by_id(user_id)
        if not user:
            user = SAMPLE_USER
        else:
            user = {
                'User_ID': user.User_ID,
                'Username': user.Username,
                'Email': user.Email,
                'name': user.Username,
                'role': 'student',
                'university': 'Zewail City',
                'major': 'Computer Science',
                'year': 'Sophomore'
            }
        
        # Fetch student stats if available
        stats = SAMPLE_STATS.copy()
        try:
            student = student_repo.get_by_user_id(user_id) if hasattr(student_repo, 'get_by_user_id') else None
            if student:
                # Get enrollments for course count
                enrollments = enrollment_repo.get_by_student_id(student.Student_ID) if hasattr(enrollment_repo, 'get_by_student_id') else []
                stats['total_courses'] = len(enrollments)
                
                # Get tasks
                tasks = task_repo.get_by_user_id(user_id) if hasattr(task_repo, 'get_by_user_id') else []
                stats['active_tasks'] = len([t for t in tasks if not getattr(t, 'completed', False)])
        except Exception as e:
            print(f"Error fetching student stats: {e}")
        
        # Get today's schedule
        today_schedule = get_today_schedule()
        
        return render_template(
            'overview.html',
            user=user,
            stats=stats,
            today_schedule=today_schedule,
            notifications=SAMPLE_NOTIFICATIONS
        )
    except Exception as e:
        print(f"Error loading overview: {e}")
        return render_template(
            'overview.html',
            user=SAMPLE_USER,
            stats=SAMPLE_STATS,
            today_schedule=get_today_schedule(),
            notifications=SAMPLE_NOTIFICATIONS
        )

@app.route('/settings')
def settings():
    """Settings page"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session.get('user_id', DEFAULT_USER_ID)
    
    try:
        # Fetch user from repository
        user = user_repo.get_by_id(user_id)
        if not user:
            user = SAMPLE_USER
        else:
            user = {
                'User_ID': user.User_ID,
                'Username': user.Username,
                'Email': user.Email,
                'name': user.Username
            }
    except Exception as e:
        print(f"Error fetching user: {e}")
        user = SAMPLE_USER

    user_settings = {
        'notifications': {'email': True, 'push': True, 'calendar_reminders': True, 'assignment_deadlines': True},
        'calendar': {'sync_google': False, 'default_view': 'week', 'timezone': 'Africa/Cairo'},
        'appearance': {'theme': 'light', 'language': 'en', 'colorblind_mode': False, 'dyslexia_font': False},
        'privacy': {'profile_visibility': 'public', 'share_schedule': False}
    }
    return render_template('settings.html', user=user, settings=user_settings)

@app.route('/api/settings/update', methods=['POST'])
def update_settings():
    """API endpoint to update user settings"""
    data = request.json
    # In production, save to database
    return jsonify({'success': True, 'message': 'Settings updated successfully'})

@app.route('/api/stats')
def get_stats():
    """API endpoint to get current statistics"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session.get('user_id', DEFAULT_USER_ID)
    stats = SAMPLE_STATS.copy()
    
    try:
        # Try to fetch real stats from repo
        student = student_repo.get_by_user_id(user_id) if hasattr(student_repo, 'get_by_user_id') else None
        if student:
            enrollments = enrollment_repo.get_by_student_id(student.Student_ID) if hasattr(enrollment_repo, 'get_by_student_id') else []
            stats['total_courses'] = len(enrollments)
            
            tasks = task_repo.get_by_user_id(user_id) if hasattr(task_repo, 'get_by_user_id') else []
            stats['active_tasks'] = len([t for t in tasks if not getattr(t, 'completed', False)])
    except Exception as e:
        print(f"Error getting stats: {e}")
    
    return jsonify(stats)

# --- Run app ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)