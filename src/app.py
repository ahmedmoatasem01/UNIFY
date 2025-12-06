from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import os


# Configure Flask to use src directory for templates and static files
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = 'unify-secret-key-change-in-production'

# Sample data - in production, this would come from a database
SAMPLE_USER = {
    'id': 1,
    'name': 'John Doe',
    'email': 'john.doe@zewailcity.edu.eg',
    'role': 'student',
    'university': 'Zewail City',
    'major': 'Computer Science',
    'year': 'Sophomore'
}

SAMPLE_STATS = {
    'total_courses': 6,
    'active_tasks': 12,
    'upcoming_events': 5,
    'completed_assignments': 24,
    'gpa': 3.75,
    'credits_completed': 45,
    'credits_total': 120,
    'credits_percentage': round((45 / 120) * 100, 1)
}

# Notifications data
NOTIFICATIONS = [
    {
        'id': 1,
        'title': 'Assignment Due Tomorrow',
        'message': 'Data Structures Assignment 3 is due tomorrow at 11:59 PM',
        'type': 'assignment',
        'time': '2 hours ago',
        'read': False,
        'priority': 'high'
    },
    {
        'id': 2,
        'title': 'New Grade Posted',
        'message': 'Your grade for Machine Learning Midterm has been posted',
        'type': 'grade',
        'time': '5 hours ago',
        'read': False,
        'priority': 'medium'
    },
    {
        'id': 3,
        'title': 'Class Cancelled',
        'message': 'Introduction to CS lecture on Friday has been cancelled',
        'type': 'announcement',
        'time': '1 day ago',
        'read': True,
        'priority': 'medium'
    },
    {
        'id': 4,
        'title': 'Exam Reminder',
        'message': 'Final exam for Algorithms is scheduled for next week',
        'type': 'exam',
        'time': '2 days ago',
        'read': True,
        'priority': 'high'
    }
]

@app.route('/')
def index():
    """Redirect to overview page"""
    return redirect(url_for('overview'))

@app.route('/overview')
def overview():
    """Overview/Dashboard page"""
    # Load today's schedule from dataset
    today = datetime.now().date()
    today_schedule = [
        {'time': '09:00 AM', 'event': 'Data Structures Lecture'},
        {'time': '11:00 AM', 'event': 'Machine Learning Lab'},
        {'time': '02:00 PM', 'event': 'Study Group Meeting'},
        {'time': '04:00 PM', 'event': 'Gym Session'}
    ]
    
    return render_template('overview.html', 
                         user=SAMPLE_USER, 
                         stats=SAMPLE_STATS,
                         today_schedule=today_schedule,
                         notifications=NOTIFICATIONS)

@app.route('/settings')
def settings():
    """Settings page"""
    # Load user settings - in production, from database
    user_settings = {
        'notifications': {
            'email': True,
            'push': True,
            'calendar_reminders': True,
            'assignment_deadlines': True
        },
        'calendar': {
            'sync_google': False,
            'default_view': 'week',
            'timezone': 'Africa/Cairo'
        },
        'appearance': {
            'theme': 'light',
            'language': 'en',
            'colorblind_mode': False,
            'dyslexia_font': False
        },
        'privacy': {
            'profile_visibility': 'public',
            'share_schedule': False
        }
    }
    return render_template('settings.html', user=SAMPLE_USER, settings=user_settings)

@app.route('/api/settings/update', methods=['POST'])
def update_settings():
    """API endpoint to update user settings"""
    data = request.json
    # In production, save to database
    return jsonify({'success': True, 'message': 'Settings updated successfully'})

@app.route('/api/stats')
def get_stats():
    """API endpoint to get current statistics"""
    return jsonify(SAMPLE_STATS)




if __name__ == '__main__':
    app.run(debug=True, port=5000)
