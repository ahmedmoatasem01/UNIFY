from flask import Blueprint, render_template, request, jsonify
from repositories.repository_factory import RepositoryFactory

course_bp = Blueprint("course", __name__, url_prefix="/courses")


@course_bp.route("/")
def list_courses():
    """List all courses"""
    repo = RepositoryFactory.get_repository("course")
    courses = repo.get_all()
    return render_template("course/list.html", courses=courses)


@course_bp.route("/<int:course_id>")
def view_course(course_id):
    """View a specific course"""
    repo = RepositoryFactory.get_repository("course")
    course = repo.get_by_id(course_id)
    if not course:
        return "Course not found", 404
    return render_template("course/detail.html", course=course)


@course_bp.route("/api", methods=["GET"])
def api_list_courses():
    """API endpoint to get all courses"""
    repo = RepositoryFactory.get_repository("course")
    courses = repo.get_all()
    return jsonify([course.to_dict() for course in courses])


@course_bp.route("/api/<int:course_id>", methods=["GET"])
def api_get_course(course_id):
    """API endpoint to get a specific course"""
    repo = RepositoryFactory.get_repository("course")
    course = repo.get_by_id(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    return jsonify(course.to_dict())


@course_bp.route("/api/instructor/<int:instructor_id>", methods=["GET"])
def api_get_courses_by_instructor(instructor_id):
    """API endpoint to get courses by instructor"""
    repo = RepositoryFactory.get_repository("course")
    courses = repo.get_by_instructor(instructor_id)
    return jsonify([course.to_dict() for course in courses])


@course_bp.route("/api", methods=["POST"])
def api_create_course():
    """API endpoint to create a new course"""
    from models.course import Course
    data = request.get_json()
    course = Course(
        Course_Name=data.get("Course_Name"),
        Credits=data.get("Credits"),
        Instructor_ID=data.get("Instructor_ID"),
        Schedule=data.get("Schedule")
    )
    repo = RepositoryFactory.get_repository("course")
    created_course = repo.create(course)
    return jsonify(created_course.to_dict()), 201

