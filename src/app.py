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
    """overview page - requires authentication"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('overview.html')  # You'll need to create this template


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

