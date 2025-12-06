from flask import Flask, render_template, session, redirect, url_for
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
from core.user_helper import get_user_data
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Register blueprints
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
    """Overview page - requires authentication"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    user_data = get_user_data(session.get('user_id'))
    return render_template('overview.html', user_data=user_data)


@app.route('/schedule')
def schedule_page():
    """Schedule page - requires authentication"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    user_data = get_user_data(session.get('user_id'))
    return render_template('schedule.html', user_data=user_data)


@app.route('/tasks')
def tasks_page():
    """Tasks page - requires authentication"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    user_data = get_user_data(session.get('user_id'))
    return render_template('tasks.html', user_data=user_data)


@app.route('/notes')
def notes_page():
    """Notes & Summaries page - requires authentication"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    user_data = get_user_data(session.get('user_id'))
    return render_template('notes.html', user_data=user_data)


@app.route('/calendar')
def calendar_page():
    """Calendar & Reminders page - requires authentication"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    user_data = get_user_data(session.get('user_id'))
    return render_template('Calendar.html', user_data=user_data)  # Keep existing filename


@app.route('/messages')
def messages_page():
    """Messages page - requires authentication"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    user_data = get_user_data(session.get('user_id'))
    return render_template('messages.html', user_data=user_data)


@app.route('/transcript')
def transcript_page():
    """Transcript page - requires authentication"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    user_data = get_user_data(session.get('user_id'))
    return render_template('Transcript.html', user_data=user_data)  # Keep existing filename


@app.route('/settings')
def settings_page():
    """Settings page - requires authentication"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    user_data = get_user_data(session.get('user_id'))
    return render_template('settings.html', user_data=user_data)


@app.route('/course-registration')
def course_registration_route():
    """Course Registration page - requires authentication (alternative route)"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return redirect(url_for('course_registration.course_registration_page'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

