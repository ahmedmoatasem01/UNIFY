from flask import Blueprint, request, jsonify, session, redirect, url_for
from repositories.repository_factory import RepositoryFactory
import hashlib

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    """Handle user login"""
    data = request.get_json()
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
    
    return jsonify({
        "message": "Login successful",
        "user": {
            "User_ID": user.User_ID,
            "Username": user.Username,
            "Email": user.Email
        }
    }), 200


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


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Handle user logout"""
    session.clear()
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

