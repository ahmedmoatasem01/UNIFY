from flask import Blueprint, render_template, request, jsonify
from repositories.repository_factory import RepositoryFactory

student_bp = Blueprint("student", __name__, url_prefix="/students")


@student_bp.route("/")
def list_students():
    """List all students"""
    repo = RepositoryFactory.get_repository("student")
    students = repo.get_all()
    return render_template("student/list.html", students=students)


@student_bp.route("/<int:student_id>")
def view_student(student_id):
    """View a specific student"""
    repo = RepositoryFactory.get_repository("student")
    student = repo.get_by_id(student_id)
    if not student:
        return "Student not found", 404
    return render_template("student/profile.html", student=student)


@student_bp.route("/api", methods=["GET"])
def api_list_students():
    """API endpoint to get all students"""
    repo = RepositoryFactory.get_repository("student")
    students = repo.get_all()
    return jsonify([student.to_dict() for student in students])


@student_bp.route("/api/<int:student_id>", methods=["GET"])
def api_get_student(student_id):
    """API endpoint to get a specific student"""
    repo = RepositoryFactory.get_repository("student")
    student = repo.get_by_id(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(student.to_dict())


@student_bp.route("/api/user/<int:user_id>", methods=["GET"])
def api_get_student_by_user(user_id):
    """API endpoint to get student by User_ID"""
    repo = RepositoryFactory.get_repository("student")
    student = repo.get_by_user_id(user_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(student.to_dict())


@student_bp.route("/api", methods=["POST"])
def api_create_student():
    """API endpoint to create a new student"""
    from models.student import Student
    data = request.get_json()
    student = Student(
        User_ID=data.get("User_ID"),
        Department=data.get("Department"),
        Year_Level=data.get("Year_Level"),
        GPA=data.get("GPA")
    )
    repo = RepositoryFactory.get_repository("student")
    created_student = repo.create(student)
    return jsonify(created_student.to_dict()), 201

