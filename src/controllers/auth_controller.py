from flask import Blueprint, request, jsonify, session, redirect, url_for
from repositories.repository_factory import RepositoryFactory
from core.db_singleton import DatabaseConnection
import hashlib
import os

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    """Handle user login"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request data"}), 400
            
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Get user by email
        user_repo = RepositoryFactory.get_repository("user")
        user = user_repo.get_by_email(email)
        
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Hash the provided password (in production, use proper password hashing like bcrypt)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Compare password hashes
        if user.Password_Hash != password_hash:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Set session
        session['user_id'] = user.User_ID
        session['email'] = user.Email
        session['username'] = user.Username
        
        # Set user database context for multi-tenant mode
        if os.environ.get('MULTI_TENANT_MODE', 'false').lower() == 'true':
            try:
                db = DatabaseConnection.get_instance()
                db.set_user_context(user.User_ID)
                print(f"[Multi-Tenant] User {user.User_ID} database context set")
            except Exception as e:
                print(f"Warning: Could not set user database context: {e}")
        
        return jsonify({
            "message": "Login successful",
            "user": {
                "User_ID": user.User_ID,
                "Username": user.Username,
                "Email": user.Email
            }
        }), 200
    except Exception as e:
        print(f"Login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@auth_bp.route("/register", methods=["POST"])
def register():
    """Handle user registration"""
    from models.user import User
    import hashlib
    
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "student")
    
    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required"}), 400
    
    # Check if user already exists
    user_repo = RepositoryFactory.get_repository("user")
    existing_user = user_repo.get_by_email(email)
    if existing_user:
        return jsonify({"error": "User with this email already exists"}), 400
    
    # Hash password (in production, use proper password hashing like bcrypt)
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Create new user
    new_user = User(
        Username=username,
        Email=email,
        Password_Hash=password_hash
    )
    
    created_user = user_repo.create(new_user)
    
    # Initialize user database in multi-tenant mode
    if os.environ.get('MULTI_TENANT_MODE', 'false').lower() == 'true':
        try:
            from core.multi_tenant_db import MultiTenantDatabaseManager
            db_manager = MultiTenantDatabaseManager()
            db_manager.initialize_user_database(created_user.User_ID, db_type='sqlite')
            print(f"[Multi-Tenant] Initialized database for user {created_user.User_ID}")
        except Exception as e:
            print(f"Warning: Could not initialize user database: {e}")
    
    # Create student/instructor/TA record based on role
    if role == "student":
        from models.student import Student
        student_repo = RepositoryFactory.get_repository("student")
        student = Student(User_ID=created_user.User_ID)
        student_repo.create(student)
    elif role == "instructor":
        from models.instructor import Instructor
        instructor_repo = RepositoryFactory.get_repository("instructor")
        instructor = Instructor(User_ID=created_user.User_ID)
        instructor_repo.create(instructor)
    elif role == "ta":
        from models.teaching_assistant import TeachingAssistant
        ta_repo = RepositoryFactory.get_repository("teaching_assistant")
        # Note: TA needs a course assignment, but we'll create with a placeholder
        # In a real app, you might want to handle this differently
        ta = TeachingAssistant(
            User_ID=created_user.User_ID,
            Assigned_Course_ID=1,  # Placeholder - should be assigned later
            Role="Teaching Assistant"
        )
        ta_repo.create(ta)
    
    return jsonify({
        "message": "Registration successful",
        "user": created_user.to_dict()
    }), 201


@auth_bp.route("/logout", methods=["POST", "GET"])
def logout():
    """Handle user logout"""
    # Clear user database context
    if os.environ.get('MULTI_TENANT_MODE', 'false').lower() == 'true':
        try:
            db = DatabaseConnection.get_instance()
            db.clear_user_context()
            print("[Multi-Tenant] User database context cleared")
        except Exception as e:
            print(f"Warning: Could not clear user database context: {e}")
    
    session.clear()
    
    # If GET request, redirect directly. If POST, return JSON
    if request.method == "GET":
        return redirect(url_for('login_page'))
    return jsonify({"message": "Logout successful"}), 200


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """Get current logged in user"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    user_repo = RepositoryFactory.get_repository("user")
    user = user_repo.get_by_id(session['user_id'])
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user.to_dict()), 200

