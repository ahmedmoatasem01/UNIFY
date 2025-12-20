"""
Reminder Controller
Handles smart reminders functionality
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from repositories.repository_factory import RepositoryFactory
from models.reminder import Reminder
from core.user_helper import get_user_data
from datetime import datetime, timedelta

reminder_bp = Blueprint("reminder", __name__, url_prefix="/reminders")


@reminder_bp.route("/")
def reminders_page():
    """Render the reminders page"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    user_id = session.get('user_id')
    user_data = get_user_data(user_id)
    return render_template('Reminder.html', user_data=user_data)


@reminder_bp.route("/api", methods=["GET"])
def api_get_reminders():
    """API endpoint to get reminders for current user"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = session.get('user_id')
    
    # Get student_id from user_id
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id)
    
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    reminder_repo = RepositoryFactory.get_repository("reminder")
    reminders = reminder_repo.get_by_student(student.Student_ID)
    
    # Get calendar events for each reminder
    calendar_repo = RepositoryFactory.get_repository("calendar")
    reminder_data = []
    
    for reminder in reminders:
        event = calendar_repo.get_by_id(reminder.Event_ID) if reminder.Event_ID else None
        reminder_dict = reminder.to_dict()
        if event:
            reminder_dict['event'] = {
                'Event_ID': event.Event_ID,
                'Title': event.Title,
                'Date': event.Date.isoformat() if event.Date else None,
                'Time': str(event.Time) if event.Time else None,
                'Source': event.Source
            }
        reminder_data.append(reminder_dict)
    
    return jsonify(reminder_data)


@reminder_bp.route("/api/pending", methods=["GET"])
def api_get_pending_reminders():
    """API endpoint to get pending reminders"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = session.get('user_id')
    
    # Get student_id from user_id
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id)
    
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    reminder_repo = RepositoryFactory.get_repository("reminder")
    reminders = reminder_repo.get_pending(student.Student_ID)
    
    reminder_data = []
    calendar_repo = RepositoryFactory.get_repository("calendar")
    
    for reminder in reminders:
        event = calendar_repo.get_by_id(reminder.Event_ID) if reminder.Event_ID else None
        reminder_dict = reminder.to_dict()
        if event:
            reminder_dict['event'] = {
                'Event_ID': event.Event_ID,
                'Title': event.Title,
                'Date': event.Date.isoformat() if event.Date else None,
                'Time': str(event.Time) if event.Time else None,
                'Source': event.Source
            }
        reminder_data.append(reminder_dict)
    
    return jsonify(reminder_data)


@reminder_bp.route("/api", methods=["POST"])
def api_create_reminder():
    """API endpoint to create a new reminder"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        # Get student_id from user_id
        student_repo = RepositoryFactory.get_repository("student")
        student = student_repo.get_by_user_id(user_id)
        
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        # Parse reminder_time
        reminder_time = None
        if data.get("reminder_time"):
            try:
                if isinstance(data.get("reminder_time"), str):
                    reminder_time = datetime.fromisoformat(data["reminder_time"].replace('Z', '+00:00'))
                else:
                    reminder_time = data["reminder_time"]
            except:
                return jsonify({"error": "Invalid reminder_time format"}), 400
        
        reminder = Reminder(
            Student_ID=student.Student_ID,
            Event_ID=data.get("event_id", 0),
            Reminder_Time=reminder_time or datetime.now() + timedelta(hours=1),
            Status=data.get("status", "pending")
        )
        
        reminder_repo = RepositoryFactory.get_repository("reminder")
        created_reminder = reminder_repo.create(reminder)
        
        return jsonify(created_reminder.to_dict()), 201
    except Exception as e:
        print(f"Error creating reminder: {e}")
        return jsonify({"error": str(e)}), 500


@reminder_bp.route("/api/<int:reminder_id>", methods=["PUT"])
def api_update_reminder(reminder_id):
    """API endpoint to update a reminder"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        data = request.get_json()
        reminder_repo = RepositoryFactory.get_repository("reminder")
        reminder = reminder_repo.get_by_id(reminder_id)
        
        if not reminder:
            return jsonify({"error": "Reminder not found"}), 404
        
        # Update fields
        if "reminder_time" in data:
            try:
                if isinstance(data["reminder_time"], str):
                    reminder.Reminder_Time = datetime.fromisoformat(data["reminder_time"].replace('Z', '+00:00'))
                else:
                    reminder.Reminder_Time = data["reminder_time"]
            except:
                pass
        
        if "status" in data:
            reminder.Status = data["status"]
        
        updated_reminder = reminder_repo.update(reminder)
        return jsonify(updated_reminder.to_dict()), 200
    except Exception as e:
        print(f"Error updating reminder: {e}")
        return jsonify({"error": str(e)}), 500


@reminder_bp.route("/api/<int:reminder_id>", methods=["DELETE"])
def api_delete_reminder(reminder_id):
    """API endpoint to delete a reminder"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        reminder_repo = RepositoryFactory.get_repository("reminder")
        success = reminder_repo.delete(reminder_id)
        
        if success:
            return jsonify({"message": "Reminder deleted successfully"}), 200
        else:
            return jsonify({"error": "Reminder not found"}), 404
    except Exception as e:
        print(f"Error deleting reminder: {e}")
        return jsonify({"error": str(e)}), 500

