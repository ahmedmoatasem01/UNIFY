"""
Role-Based Access Control (RBAC) Decorator
Restricts access to routes based on user roles (Instructor, TA, Student)
"""
from functools import wraps
from flask import session, redirect, url_for, jsonify
from repositories.repository_factory import RepositoryFactory


def get_user_role(user_id):
    """
    Get user's role (Instructor, TA, or Student)
    
    Args:
        user_id: The user ID
        
    Returns:
        str: 'Instructor', 'TA', 'Student', or None
    """
    if not user_id:
        return None
    
    # Check if user is an instructor
    instructor_repo = RepositoryFactory.get_repository("instructor")
    instructor = instructor_repo.get_by_user_id(user_id)
    if instructor:
        return 'Instructor'
    
    # Check if user is a TA
    ta_repo = RepositoryFactory.get_repository("teaching_assistant")
    ta = ta_repo.get_by_user_id(user_id)
    if ta:
        return 'TA'
    
    # Check if user is a student
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id)
    if student:
        return 'Student'
    
    return None


def requires_role(*allowed_roles):
    """
    Decorator to restrict route access to specific roles
    
    Usage:
        @app.route('/transcript')
        @requires_role('Instructor', 'TA')
        def transcript_page():
            ...
    
    Args:
        *allowed_roles: Variable number of allowed role strings ('Instructor', 'TA', 'Student')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            if 'user_id' not in session:
                return redirect(url_for('login_page'))
            
            user_id = session.get('user_id')
            user_role = get_user_role(user_id)
            
            # Check if user has required role
            if user_role not in allowed_roles:
                # Return JSON error for API routes, redirect for page routes
                if request.path.startswith('/api/'):
                    return jsonify({
                        "error": "Access denied",
                        "message": f"This resource requires one of the following roles: {', '.join(allowed_roles)}",
                        "your_role": user_role or "Unknown"
                    }), 403
                else:
                    # Redirect to overview with error message
                    from flask import flash
                    flash(f"Access denied. This page requires: {', '.join(allowed_roles)}", "error")
                    return redirect(url_for('overview.overview_page'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def requires_instructor_or_ta(f):
    """
    Shortcut decorator for routes that require Instructor or TA
    """
    return requires_role('Instructor', 'TA')(f)


def requires_student(f):
    """
    Shortcut decorator for routes that require Student role
    """
    return requires_role('Student')(f)
