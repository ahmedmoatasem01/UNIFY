from flask import Blueprint, request, jsonify
from repositories.repository_factory import RepositoryFactory

enrollment_bp = Blueprint("enrollment", __name__, url_prefix="/enrollments")


@enrollment_bp.route("/api", methods=["GET"])
def api_list_enrollments():
    """API endpoint to get all enrollments"""
    repo = RepositoryFactory.get_repository("enrollment")
    enrollments = repo.get_all()
    return jsonify([enrollment.to_dict() for enrollment in enrollments])


@enrollment_bp.route("/api/<int:enrollment_id>", methods=["GET"])
def api_get_enrollment(enrollment_id):
    """API endpoint to get a specific enrollment"""
    repo = RepositoryFactory.get_repository("enrollment")
    enrollment = repo.get_by_id(enrollment_id)
    if not enrollment:
        return jsonify({"error": "Enrollment not found"}), 404
    return jsonify(enrollment.to_dict())


@enrollment_bp.route("/api/student/<int:student_id>", methods=["GET"])
def api_get_enrollments_by_student(student_id):
    """API endpoint to get enrollments by student"""
    repo = RepositoryFactory.get_repository("enrollment")
    enrollments = repo.get_by_student(student_id)
    return jsonify([enrollment.to_dict() for enrollment in enrollments])


@enrollment_bp.route("/api/course/<int:course_id>", methods=["GET"])
def api_get_enrollments_by_course(course_id):
    """API endpoint to get enrollments by course"""
    repo = RepositoryFactory.get_repository("enrollment")
    enrollments = repo.get_by_course(course_id)
    return jsonify([enrollment.to_dict() for enrollment in enrollments])


@enrollment_bp.route("/api", methods=["POST"])
def api_create_enrollment():
    """API endpoint to create a new enrollment"""
    from models.enrollment import Enrollment
    data = request.get_json()
    enrollment = Enrollment(
        Student_ID=data.get("Student_ID"),
        Course_ID=data.get("Course_ID"),
        Status=data.get("Status", "enrolled")
    )
    repo = RepositoryFactory.get_repository("enrollment")
    created_enrollment = repo.create(enrollment)
    return jsonify(created_enrollment.to_dict()), 201

