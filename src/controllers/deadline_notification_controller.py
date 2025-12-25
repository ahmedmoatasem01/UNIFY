from flask import Blueprint, render_template, request, jsonify, session
from repositories.repository_factory import RepositoryFactory
from services.deadline_notification_service import DeadlineNotificationService
from services.deadline_tracking_service import DeadlineTrackingService
from models.deadline_notification_preference import DeadlineNotificationPreference
from datetime import datetime
from core.user_helper import get_user_data

deadline_notification_bp = Blueprint("deadline_notification", __name__, url_prefix="/deadline-notifications")


@deadline_notification_bp.route("/")
def deadline_notifications_page():
    """Deadline notifications page"""
    user_data = get_user_data()
    if not user_data:
        return render_template("login.html")
    
    return render_template("deadline_notifications.html", user_data=user_data, user=user_data)


# API Endpoints
@deadline_notification_bp.route("/api/user/<int:user_id>", methods=["GET"])
def api_get_user_deadlines(user_id):
    """API endpoint to get all deadline notifications for a user"""
    try:
        service = DeadlineNotificationService()
        notifications = service.get_user_deadlines(user_id)
        return jsonify([n.to_dict() for n in notifications])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@deadline_notification_bp.route("/api/upcoming", methods=["GET"])
def api_get_upcoming_deadlines():
    """API endpoint to get upcoming deadline notifications for current user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        service = DeadlineNotificationService()
        limit = request.args.get('limit', 10, type=int)
        notifications = service.get_upcoming_deadlines(user_id, limit)
        return jsonify([n.to_dict() for n in notifications])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@deadline_notification_bp.route("/api/urgent", methods=["GET"])
def api_get_urgent_deadlines():
    """API endpoint to get urgent deadline notifications for current user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        service = DeadlineNotificationService()
        hours = request.args.get('hours', 24, type=int)
        notifications = service.get_urgent_deadlines(user_id, hours)
        return jsonify([n.to_dict() for n in notifications])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@deadline_notification_bp.route("/api/<int:notification_id>", methods=["GET"])
def api_get_deadline_notification(notification_id):
    """API endpoint to get a specific deadline notification"""
    try:
        repo = RepositoryFactory.get_repository("deadline_notification")
        notification = repo.get_by_id(notification_id)
        if not notification:
            return jsonify({"error": "Deadline notification not found"}), 404
        return jsonify(notification.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@deadline_notification_bp.route("/api", methods=["POST"])
def api_create_deadline_notification():
    """API endpoint to create a new deadline notification"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        data = request.get_json()
        service = DeadlineNotificationService()
        
        # Parse deadline date
        deadline_date = None
        if data.get("Deadline_Date"):
            try:
                if isinstance(data.get("Deadline_Date"), str):
                    deadline_date = datetime.fromisoformat(data.get("Deadline_Date").replace('Z', '+00:00'))
                else:
                    deadline_date = data.get("Deadline_Date")
            except:
                deadline_date = datetime.strptime(data.get("Deadline_Date"), '%Y-%m-%dT%H:%M')
        
        notification = service.create_deadline_notification(
            user_id=user_id,
            deadline_type=data.get("Deadline_Type", "task"),
            source_id=data.get("Source_ID", 0),
            source_type=data.get("Source_Type", "task"),
            deadline_date=deadline_date,
            title=data.get("Title", ""),
            description=data.get("Description"),
            priority=data.get("Priority", "medium")
        )
        return jsonify(notification.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@deadline_notification_bp.route("/api/<int:notification_id>", methods=["PUT"])
def api_update_deadline_notification(notification_id):
    """API endpoint to update a deadline notification"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        data = request.get_json()
        service = DeadlineNotificationService()
        
        # Parse deadline date if provided
        deadline_date = None
        if data.get("Deadline_Date"):
            try:
                if isinstance(data.get("Deadline_Date"), str):
                    deadline_date = datetime.fromisoformat(data.get("Deadline_Date").replace('Z', '+00:00'))
                else:
                    deadline_date = data.get("Deadline_Date")
            except:
                deadline_date = datetime.strptime(data.get("Deadline_Date"), '%Y-%m-%dT%H:%M')
        
        notification = service.update_deadline_notification(
            notification_id=notification_id,
            deadline_date=deadline_date,
            title=data.get("Title"),
            description=data.get("Description"),
            priority=data.get("Priority"),
            status=data.get("Status")
        )
        
        if not notification:
            return jsonify({"error": "Deadline notification not found"}), 404
        
        return jsonify(notification.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@deadline_notification_bp.route("/api/<int:notification_id>", methods=["DELETE"])
def api_delete_deadline_notification(notification_id):
    """API endpoint to delete a deadline notification"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        service = DeadlineNotificationService()
        success = service.delete_deadline_notification(notification_id)
        if success:
            return jsonify({"message": "Deadline notification deleted successfully"})
        else:
            return jsonify({"error": "Failed to delete deadline notification"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@deadline_notification_bp.route("/api/<int:notification_id>/complete", methods=["PUT"])
def api_mark_deadline_complete(notification_id):
    """API endpoint to mark a deadline notification as completed"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        service = DeadlineNotificationService()
        success = service.mark_deadline_completed(notification_id)
        if success:
            return jsonify({"message": "Deadline marked as completed"})
        else:
            return jsonify({"error": "Failed to mark deadline as completed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@deadline_notification_bp.route("/api/preferences/<int:user_id>", methods=["GET"])
def api_get_preferences(user_id):
    """API endpoint to get deadline notification preferences for a user"""
    user_id_session = session.get('user_id')
    if not user_id_session or user_id_session != user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        repo = RepositoryFactory.get_repository("deadline_notification_preference")
        preferences = repo.get_by_user_id(user_id)
        return jsonify([p.to_dict() for p in preferences])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@deadline_notification_bp.route("/api/preferences/<int:user_id>", methods=["PUT"])
def api_update_preferences(user_id):
    """API endpoint to update deadline notification preferences for a user"""
    user_id_session = session.get('user_id')
    if not user_id_session or user_id_session != user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        data = request.get_json()
        repo = RepositoryFactory.get_repository("deadline_notification_preference")
        
        preference = DeadlineNotificationPreference(
            User_ID=user_id,
            Deadline_Type=data.get("Deadline_Type", "all"),
            Email_Enabled=data.get("Email_Enabled", False),
            In_App_Enabled=data.get("In_App_Enabled", True),
            Quiet_Hours_Start=data.get("Quiet_Hours_Start"),
            Quiet_Hours_End=data.get("Quiet_Hours_End")
        )
        
        # Set alert intervals
        if data.get("Alert_Intervals"):
            if isinstance(data.get("Alert_Intervals"), list):
                preference.set_alert_intervals_list(data.get("Alert_Intervals"))
            else:
                preference.Alert_Intervals = data.get("Alert_Intervals")
        
        preference = repo.upsert(preference)
        return jsonify(preference.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@deadline_notification_bp.route("/api/calendar/<int:user_id>", methods=["GET"])
def api_get_deadline_calendar(user_id):
    """API endpoint to get deadline calendar for a user"""
    user_id_session = session.get('user_id')
    if not user_id_session or user_id_session != user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        service = DeadlineNotificationService()
        
        start_date = None
        end_date = None
        if request.args.get('start_date'):
            start_date = datetime.fromisoformat(request.args.get('start_date'))
        if request.args.get('end_date'):
            end_date = datetime.fromisoformat(request.args.get('end_date'))
        
        calendar_items = service.get_deadline_calendar(user_id, start_date, end_date)
        return jsonify(calendar_items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@deadline_notification_bp.route("/api/check-deadlines", methods=["POST"])
def api_check_deadlines():
    """API endpoint to check and sync deadlines from tasks and calendar"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        tracking_service = DeadlineTrackingService()
        results = tracking_service.sync_all_deadlines(user_id)
        
        # Also check for overdue deadlines
        notification_service = DeadlineNotificationService()
        overdue_count = notification_service.check_and_update_overdue(user_id)
        
        return jsonify({
            "message": "Deadlines checked and synced",
            "synced": results,
            "overdue_count": overdue_count
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

