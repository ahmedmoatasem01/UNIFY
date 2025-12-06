from flask import Blueprint, request, jsonify
from repositories.repository_factory import RepositoryFactory

schedule_bp = Blueprint("schedule", __name__, url_prefix="/schedules")


@schedule_bp.route("/api", methods=["GET"])
def api_list_schedules():
    """API endpoint to get all schedules"""
    repo = RepositoryFactory.get_repository("schedule")
    schedules = repo.get_all()
    return jsonify([schedule.to_dict() for schedule in schedules])


@schedule_bp.route("/api/<int:schedule_id>", methods=["GET"])
def api_get_schedule(schedule_id):
    """API endpoint to get a specific schedule"""
    repo = RepositoryFactory.get_repository("schedule")
    schedule = repo.get_by_id(schedule_id)
    if not schedule:
        return jsonify({"error": "Schedule not found"}), 404
    return jsonify(schedule.to_dict())


@schedule_bp.route("/api/student/<int:student_id>", methods=["GET"])
def api_get_schedule_by_student(student_id):
    """API endpoint to get schedule by student"""
    repo = RepositoryFactory.get_repository("schedule")
    schedule = repo.get_by_student(student_id)
    if not schedule:
        return jsonify({"error": "Schedule not found"}), 404
    return jsonify(schedule.to_dict())


@schedule_bp.route("/api", methods=["POST"])
def api_create_schedule():
    """API endpoint to create a new schedule"""
    from models.schedule import Schedule
    data = request.get_json()
    schedule = Schedule(
        Student_ID=data.get("Student_ID"),
        Course_List=data.get("Course_List"),
        Optimized=data.get("Optimized", False)
    )
    repo = RepositoryFactory.get_repository("schedule")
    created_schedule = repo.create(schedule)
    return jsonify(created_schedule.to_dict()), 201

