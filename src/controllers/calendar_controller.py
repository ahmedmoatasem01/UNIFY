from flask import Blueprint, request, jsonify
from repositories.repository_factory import RepositoryFactory

calendar_bp = Blueprint("calendar", __name__, url_prefix="/calendar")


@calendar_bp.route("/api", methods=["GET"])
def api_list_events():
    """API endpoint to get all calendar events"""
    repo = RepositoryFactory.get_repository("calendar")
    events = repo.get_all()
    return jsonify([event.to_dict() for event in events])


@calendar_bp.route("/api/<int:event_id>", methods=["GET"])
def api_get_event(event_id):
    """API endpoint to get a specific calendar event"""
    repo = RepositoryFactory.get_repository("calendar")
    event = repo.get_by_id(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(event.to_dict())


@calendar_bp.route("/api/student/<int:student_id>", methods=["GET"])
def api_get_events_by_student(student_id):
    """API endpoint to get calendar events by student"""
    repo = RepositoryFactory.get_repository("calendar")
    events = repo.get_by_student(student_id)
    return jsonify([event.to_dict() for event in events])


@calendar_bp.route("/api/user", methods=["GET"])
def api_get_events_by_user():
    """API endpoint to get calendar events for current user"""
    from flask import session
    
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    # Get student_id from user_id
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id)
    
    if not student:
        return jsonify([]), 200
    
    repo = RepositoryFactory.get_repository("calendar")
    events = repo.get_by_student(student.Student_ID)
    return jsonify([event.to_dict() for event in events])


@calendar_bp.route("/api", methods=["POST"])
def api_create_event():
    """API endpoint to create a new calendar event"""
    from flask import session
    from models.calendar import Calendar
    
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    # Get student_id from user_id
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id)
    
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    data = request.get_json()
    event = Calendar(
        Student_ID=student.Student_ID,
        Title=data.get("Title"),
        Date=data.get("Date"),
        Time=data.get("Time"),
        Source=data.get("Source", "manual")
    )
    repo = RepositoryFactory.get_repository("calendar")
    created_event = repo.create(event)
    return jsonify(created_event.to_dict()), 201

