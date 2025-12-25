"""
Study Plan Generator - Standalone Demo
A minimal demo to showcase the Smart Study Plan Generator feature
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import sys
from datetime import datetime, timedelta, date

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Import controllers
from controllers.study_plan_controller import study_plan_bp

# Create Flask app
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = 'demo-study-planner-secret-key'

# Register blueprint
app.register_blueprint(study_plan_bp)

# Demo user data
DEMO_USER = {
    'User_ID': 1,
    'Username': 'demo_student',
    'Email': 'demo@unify.edu',
    'name': 'Demo Student',
    'role': 'student',
    'university': 'Zewail City',
    'major': 'Computer Science',
    'year': 'Sophomore'
}

@app.context_processor
def inject_user_data():
    """Inject user data into all templates"""
    return {'user_data': DEMO_USER}

@app.before_request
def setup_session():
    """Set up demo session"""
    if 'user_id' not in session:
        session['user_id'] = 1

@app.route('/')
def index():
    """Redirect to demo landing page"""
    return render_template('demo_study_planner.html')

@app.route('/demo')
def demo_page():
    """Demo landing page"""
    return render_template('demo_study_planner.html')

# Mock topbar component for demo
@app.route('/components/topbar_right.html')
def topbar_right():
    """Mock topbar component"""
    return '''
    <div class="cr-topbar-right">
        <div class="cr-user-info">
            <div class="cr-user-avatar">D</div>
            <div class="cr-user-details">
                <p class="cr-user-name">Demo Student</p>
                <p class="cr-user-role">Computer Science</p>
            </div>
        </div>
    </div>
    '''

# Mock auth logout for demo
@app.route('/auth/logout', methods=['POST'])
def logout():
    """Mock logout"""
    session.clear()
    return jsonify({'success': True})

# Mock API endpoints for demo (if database is not available)
@app.errorhandler(500)
def handle_500(error):
    """Handle internal server errors gracefully in demo mode"""
    return jsonify({
        'error': 'Demo Mode: Database not configured',
        'message': 'This is a demo. Some features require database setup.',
        'demo': True
    }), 200  # Return 200 to prevent error alerts

@app.errorhandler(404)
def handle_404(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not found',
        'demo': True
    }), 404

if __name__ == '__main__':
    print("=" * 80)
    print("UNIFY Study Plan Generator - Demo Mode")
    print("=" * 80)
    print("\nStarting demo server...")
    print("\nAccess the demo at:")
    print("   -> http://localhost:5001")
    print("   -> http://127.0.0.1:5001")
    print("\nDemo Pages:")
    print("   -> http://localhost:5001/           (Landing page)")
    print("   -> http://localhost:5001/study-plans (Study plans list)")
    print("\nNote: This is a demo version.")
    print("      Database operations will show demo data if not configured.")
    print("\nFeatures to explore:")
    print("   * Beautiful UI matching tasks.html design")
    print("   * Create AI-powered study plans")
    print("   * Auto-decompose complex tasks")
    print("   * Track progress with analytics")
    print("   * Get personalized recommendations")
    print("\n" + "=" * 80)
    print("\nPress CTRL+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
