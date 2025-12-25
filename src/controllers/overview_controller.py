"""
Overview Controller
Handles the overview/dashboard page with real database statistics
"""
from flask import Blueprint, render_template, session, redirect, url_for
from repositories.repository_factory import RepositoryFactory
from core.user_helper import get_user_data
from services.notification_service import get_notification_service
from datetime import datetime, date, timedelta

overview_bp = Blueprint("overview", __name__, url_prefix="/overview")


@overview_bp.route("/")
def overview_page():
    """Overview page with real database statistics"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    user_id = session.get('user_id')
    user_data = get_user_data(user_id)
    
    # Initialize default values
    stats = {
        'total_courses': 0,
        'active_tasks': 0,
        'upcoming_events': 0,
        'completed_assignments': 0
    }
    today_schedule = []
    notifications = []
    
    # Get student data
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id)
    
    if student:
        # ===== GET ENROLLED COURSES COUNT =====
        try:
            enrollment_repo = RepositoryFactory.get_repository("enrollment")
            enrollments = enrollment_repo.get_by_student(student.Student_ID)
            stats['total_courses'] = len([e for e in enrollments if e.Status == 'enrolled'])
        except Exception as e:
            print(f"Error fetching enrollments: {e}")
        
        # ===== GET ACTIVE TASKS COUNT =====
        try:
            task_repo = RepositoryFactory.get_repository("task")
            tasks = task_repo.get_by_student(student.Student_ID)
            stats['active_tasks'] = len([t for t in tasks if t.Status == 'pending'])
            
            # Count completed tasks this month for assignments stat
            today = date.today()
            first_day_of_month = today.replace(day=1)
            completed_this_month = len([
                t for t in tasks 
                if t.Status == 'completed' and t.Due_Date and t.Due_Date.date() >= first_day_of_month
            ]) if any(hasattr(t, 'Due_Date') and t.Due_Date for t in tasks) else 0
            stats['completed_assignments'] = completed_this_month
        except Exception as e:
            print(f"Error fetching tasks: {e}")
        
        # ===== GET UPCOMING CALENDAR EVENTS COUNT =====
        try:
            calendar_repo = RepositoryFactory.get_repository("calendar")
            events = calendar_repo.get_by_student(student.Student_ID)
            today = date.today()
            upcoming = [e for e in events if e.Date and e.Date >= today]
            stats['upcoming_events'] = len(upcoming)
        except Exception as e:
            print(f"Error fetching calendar events: {e}")
        
        # ===== GET TODAY'S SCHEDULE =====
        try:
            schedule_repo = RepositoryFactory.get_repository("schedule")
            schedules = schedule_repo.get_by_student(student.Student_ID)
            
            # Get today's day name (e.g., "MON", "TUE", etc.)
            today_day = datetime.now().strftime('%A').upper()[:3]
            # Also try full day name
            today_day_full = datetime.now().strftime('%A').upper()
            
            for sched in schedules:
                if sched.Day and (sched.Day.upper() == today_day or sched.Day.upper() == today_day_full or sched.Day.upper() in today_day_full):
                    # Format time
                    time_str = 'TBA'
                    if sched.Start_Time and sched.End_Time:
                        try:
                            if isinstance(sched.Start_Time, str):
                                time_str = f"{sched.Start_Time} - {sched.End_Time}"
                            else:
                                time_str = f"{sched.Start_Time.strftime('%I:%M %p')} - {sched.End_Time.strftime('%I:%M %p')}"
                        except:
                            time_str = 'TBA'
                    
                    today_schedule.append({
                        'time': time_str,
                        'course_name': sched.Course_Code if hasattr(sched, 'Course_Code') and sched.Course_Code else 'Course',
                        'instructor': sched.Instructor if hasattr(sched, 'Instructor') and sched.Instructor else 'TBA',
                        'location': sched.Location if hasattr(sched, 'Location') and sched.Location else 'TBA',
                        'type': sched.Type if hasattr(sched, 'Type') and sched.Type else 'Lecture'
                    })
            
            # Sort by time if possible
            if today_schedule:
                today_schedule.sort(key=lambda x: x['time'])
        except Exception as e:
            print(f"Error fetching today's schedule: {e}")
        
        # ===== GET NOTIFICATIONS =====
        try:
            notification_service = get_notification_service()
            notification_list = notification_service.get_notifications(user_id, limit=10)
            
            for notif in notification_list:
                time_str = 'Now'
                if notif.Created_At:
                    try:
                        if isinstance(notif.Created_At, str):
                            time_str = notif.Created_At
                        else:
                            # Calculate relative time
                            time_diff = datetime.now() - notif.Created_At
                            if time_diff.days > 0:
                                time_str = f"{time_diff.days}d ago"
                            elif time_diff.seconds > 3600:
                                hours = time_diff.seconds // 3600
                                time_str = f"{hours}h ago"
                            elif time_diff.seconds > 60:
                                minutes = time_diff.seconds // 60
                                time_str = f"{minutes}m ago"
                            else:
                                time_str = "Just now"
                    except:
                        time_str = 'Recently'
                
                notifications.append({
                    'title': notif.Title,
                    'message': notif.Message,
                    'time': time_str,
                    'type': notif.Type or 'system',
                    'priority': notif.Priority or 'medium',
                    'read': bool(notif.Is_Read),
                    'action_url': notif.Action_URL
                })
        except Exception as e:
            print(f"Error fetching notifications: {e}")
    
    return render_template(
        'overview.html',
        user_data=user_data,
        user=user_data,  # For backwards compatibility
        stats=stats,
        today_schedule=today_schedule,
        notifications=notifications
    )

