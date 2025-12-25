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
from controllers.transcript_controller import transcript_bp
from controllers.overview_controller import overview_bp
from repositories.repository_factory import RepositoryFactory
from core.user_helper import get_user_data
from core.role_auth import requires_student, requires_role

# Conditionally import AI Note controller (requires additional dependencies)
try:
    from controllers.AI_Note_controller import ai_note_bp
    ai_note_available = True
except ImportError as e:
    print(f"Warning: AI Note controller not available: {e}")
    ai_note_bp = None
    ai_note_available = False

# Import AI Assistant controller
try:
    from controllers.ai_assistant_controller import ai_assistant_bp
    ai_assistant_available = True
except ImportError as e:
    print(f"Warning: AI Assistant controller not available: {e}")
    ai_assistant_bp = None
    ai_assistant_available = False

# Import Advisor Chatbot controller
try:
    from controllers.advisor_chatbot_controller import advisor_chatbot_bp
    advisor_chatbot_available = True
except ImportError as e:
    print(f"Warning: Advisor Chatbot controller not available: {e}")
    advisor_chatbot_bp = None
    advisor_chatbot_available = False

# Import Notification controller
try:
    from controllers.notification_controller import notification_bp
    notification_available = True
except ImportError as e:
    print(f"Warning: Notification controller not available: {e}")
    notification_bp = None
    notification_available = False

# Import Appointment controller
try:
    from controllers.appointment_controller import appointment_bp
    appointment_available = True
except ImportError as e:
    print(f"Warning: Appointment controller not available: {e}")
    appointment_bp = None
    appointment_available = False

# Import Assignment controller
try:
    from controllers.assignment_controller import assignment_bp
    assignment_available = True
except ImportError as e:
    print(f"Warning: Assignment controller not available: {e}")
    assignment_bp = None
    assignment_available = False
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

#create app factory
def create_app(config=None):
    """
    Application Factory Pattern
    Creates and configures the Flask application instance.
    
    Args:
        config: Optional configuration dictionary to override defaults
        
    Returns:
        Flask application instance
    """
    # Create Flask app instance
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # Configuration
    app.secret_key = os.environ.get('SECRET_KEY', 'unify-secret-key-change-in-production')
    
    # Apply custom config if provided
    if config:
        app.config.update(config)
    
    # --- Register Blueprints ---
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(course_bp)
    # Note: task_bp registered after routes to avoid conflicts
    app.register_blueprint(message_bp)
    app.register_blueprint(enrollment_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(course_reg_bp)
    app.register_blueprint(transcript_bp)
    app.register_blueprint(overview_bp)
    if ai_note_available and ai_note_bp:
        app.register_blueprint(ai_note_bp)
    if ai_assistant_available and ai_assistant_bp:
        app.register_blueprint(ai_assistant_bp)
    if advisor_chatbot_available and advisor_chatbot_bp:
        app.register_blueprint(advisor_chatbot_bp)
    if notification_available and notification_bp:
        app.register_blueprint(notification_bp)
    if appointment_available and appointment_bp:
        app.register_blueprint(appointment_bp)
    if assignment_available and assignment_bp:
        app.register_blueprint(assignment_bp)
    app.register_blueprint(task_bp)  # Register after routes to ensure app routes take precedence
    
    return app


# Create app instance using factory
app = create_app()

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


# NOTE: get_user_data is imported from core.user_helper (line 15) which properly checks roles
# The duplicate function was removed to ensure correct role detection for RBAC
# DO NOT re-add a get_user_data function here - use the one from core.user_helper


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
    return render_template('login.html')


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/overview')
@app.route('/dashboard')
def overview():
    """Overview page - redirects to overview blueprint"""
    return redirect('/overview/')


@app.route('/schedule')
def schedule_page():
    """Schedule page - requires authentication"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    user_data = get_user_data(session.get('user_id'))
    return render_template('schedule.html', user_data=user_data)


@app.route('/tasks', strict_slashes=False)
@requires_student
def tasks_page():
    """Tasks page - STUDENT ONLY"""
    user_id = session.get('user_id')
    user_data = get_user_data(user_id)
    return render_template('tasks.html', user_data=user_data)


@app.route('/notes')
def notes_page():
    """Notes page - requires authentication"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    user_data = get_user_data(session.get('user_id'))
    return render_template('notes.html', user_data=user_data)


@app.route('/calendar')
def calendar_page():
    """Calendar page - requires authentication"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    user_data = get_user_data(session.get('user_id'))
    return render_template('Calendar.html', user_data=user_data)


@app.route('/reminders')
@requires_student
def reminders_page():
    """Smart Reminders page - STUDENT ONLY"""
    user_id = session.get('user_id')
    user_data = get_user_data(user_id)
    return render_template('Reminder.html', user_data=user_data)


@app.route('/messages')
def messages_page():
    """Messages page - requires authentication"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    user_data = get_user_data(session.get('user_id'))
    return render_template('messages.html', user_data=user_data)


@app.route('/transcript')
@requires_student
def transcript_page():
    """Transcript page - STUDENT ONLY"""
    user_id = session.get('user_id')
    user_data = get_user_data(user_id)
    return render_template('Transcript.html', user_data=user_data)


@app.route('/settings')
def settings():
    """Settings page - loads user settings from database"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    user_id = session.get('user_id', DEFAULT_USER_ID)
    user_data = get_user_data(user_id)
    
    # Get settings from database (or create default if doesn't exist)
    settings_repo = RepositoryFactory.get_repository("user_settings")
    user_settings_obj = settings_repo.get_or_create(user_id)
    user_settings = user_settings_obj.to_dict()
    
    return render_template('settings.html', user=user_data, user_data=user_data, settings=user_settings)


@app.route('/api/settings/update', methods=['POST'])
def update_settings():
    """API endpoint to update user settings"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        user_id = session.get('user_id')
        data = request.json
        
        # Get current settings
        settings_repo = RepositoryFactory.get_repository("user_settings")
        user_settings = settings_repo.get_or_create(user_id)
        
        # Update settings from request data
        if 'notifications' in data:
            user_settings.email_notifications = data['notifications'].get('email', True)
            user_settings.push_notifications = data['notifications'].get('push', True)
            user_settings.calendar_reminders = data['notifications'].get('calendar_reminders', True)
            user_settings.assignment_deadlines = data['notifications'].get('assignment_deadlines', True)
        
        if 'calendar' in data:
            user_settings.sync_google_calendar = data['calendar'].get('sync_google', False)
            user_settings.calendar_default_view = data['calendar'].get('default_view', 'week')
            user_settings.timezone = data['calendar'].get('timezone', 'Africa/Cairo')
        
        if 'appearance' in data:
            user_settings.theme = data['appearance'].get('theme', 'dark')
            user_settings.language = data['appearance'].get('language', 'en')
            user_settings.colorblind_mode = data['appearance'].get('colorblind_mode', False)
            user_settings.dyslexia_font = data['appearance'].get('dyslexia_font', False)
        
        if 'privacy' in data:
            user_settings.profile_visibility = data['privacy'].get('profile_visibility', 'public')
            user_settings.share_schedule = data['privacy'].get('share_schedule', False)
        
        # Save to database
        settings_repo.update(user_settings)
        
        return jsonify({'success': True, 'message': 'Settings updated successfully'})
    except Exception as e:
        print(f"Error updating settings: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats')
def get_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user_id = session.get('user_id', DEFAULT_USER_ID)
    stats = get_user_stats(user_id)
    return jsonify(stats)


if __name__ == '__main__':
    # App is created using factory pattern above
    app.run(debug=True, host='0.0.0.0', port=5000)