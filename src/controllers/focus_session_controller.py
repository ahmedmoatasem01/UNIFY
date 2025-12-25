from flask import Blueprint, render_template, request, jsonify, session, redirect
from repositories.repository_factory import RepositoryFactory
from models.focus_session import FocusSession
from datetime import datetime, timedelta
from core.user_helper import get_user_data

focus_session_bp = Blueprint("focus_session", __name__, url_prefix="/focus-session")


@focus_session_bp.route("/", methods=["GET"])
def focus_session_page():
    """Render the focus session tracking page"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    
    user_data = get_user_data(user_id)
    return render_template("focus_session.html", user_data=user_data)


@focus_session_bp.route("/api/save", methods=["POST"])
def api_save_session():
    """API endpoint to save a focus session"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        data = request.json
        duration = data.get('duration', 0)  # Duration in seconds
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        completed = data.get('completed', True)
        
        # Get student ID from user ID
        student_repo = RepositoryFactory.get_repository("student")
        student = student_repo.get_by_user_id(user_id)
        
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        # Parse datetime strings
        start_datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00')) if start_time else datetime.now()
        end_datetime = datetime.fromisoformat(end_time.replace('Z', '+00:00')) if end_time else datetime.now()
        
        # Create focus session
        focus_session = FocusSession(
            Student_ID=student.Student_ID,
            Duration=duration,
            Start_Time=start_datetime,
            End_Time=end_datetime,
            Completed=completed
        )
        
        # Save to database
        focus_session_repo = RepositoryFactory.get_repository("focus_session")
        saved_session = focus_session_repo.create(focus_session)
        
        return jsonify({
            "success": True,
            "session": saved_session.to_dict()
        })
    except Exception as e:
        print(f"Error saving focus session: {e}")
        return jsonify({"error": str(e)}), 500


@focus_session_bp.route("/api/productivity", methods=["GET"])
def api_get_productivity():
    """API endpoint to get daily and weekly productivity statistics"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        # Get student ID from user ID
        student_repo = RepositoryFactory.get_repository("student")
        student = student_repo.get_by_user_id(user_id)
        
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        # Get focus sessions for the student
        focus_session_repo = RepositoryFactory.get_repository("focus_session")
        all_sessions = focus_session_repo.get_by_student(student.Student_ID)
        
        # Calculate daily statistics (last 7 days)
        today = datetime.now().date()
        daily_stats = []
        for i in range(7):
            date = today - timedelta(days=i)
            day_start = datetime.combine(date, datetime.min.time())
            day_end = datetime.combine(date, datetime.max.time())
            
            day_sessions = [
                s for s in all_sessions
                if s.Start_Time and day_start <= s.Start_Time <= day_end
            ]
            
            total_duration = sum(s.Duration for s in day_sessions)
            session_count = len(day_sessions)
            
            daily_stats.append({
                'date': date.isoformat(),
                'duration': total_duration,  # in seconds
                'duration_hours': round(total_duration / 3600, 2),
                'session_count': session_count
            })
        
        daily_stats.reverse()  # Oldest to newest
        
        # Calculate weekly statistics (last 4 weeks)
        weekly_stats = []
        for i in range(4):
            week_end = today - timedelta(days=i * 7)
            week_start = week_end - timedelta(days=6)
            week_start_dt = datetime.combine(week_start, datetime.min.time())
            week_end_dt = datetime.combine(week_end, datetime.max.time())
            
            week_sessions = [
                s for s in all_sessions
                if s.Start_Time and week_start_dt <= s.Start_Time <= week_end_dt
            ]
            
            total_duration = sum(s.Duration for s in week_sessions)
            session_count = len(week_sessions)
            
            weekly_stats.append({
                'week': f"Week {4-i}",
                'start_date': week_start.isoformat(),
                'end_date': week_end.isoformat(),
                'duration': total_duration,
                'duration_hours': round(total_duration / 3600, 2),
                'session_count': session_count
            })
        
        weekly_stats.reverse()  # Oldest to newest
        
        # Calculate overall statistics
        total_sessions = len(all_sessions)
        total_duration = sum(s.Duration for s in all_sessions)
        avg_session_duration = total_duration / total_sessions if total_sessions > 0 else 0
        
        # Today's statistics
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        today_sessions = [
            s for s in all_sessions
            if s.Start_Time and today_start <= s.Start_Time <= today_end
        ]
        today_duration = sum(s.Duration for s in today_sessions)
        
        # This week's statistics
        week_start = today - timedelta(days=today.weekday())
        week_start_dt = datetime.combine(week_start, datetime.min.time())
        week_end_dt = datetime.combine(today, datetime.max.time())
        week_sessions = [
            s for s in all_sessions
            if s.Start_Time and week_start_dt <= s.Start_Time <= week_end_dt
        ]
        week_duration = sum(s.Duration for s in week_sessions)
        
        return jsonify({
            'daily': daily_stats,
            'weekly': weekly_stats,
            'overall': {
                'total_sessions': total_sessions,
                'total_duration': total_duration,
                'total_duration_hours': round(total_duration / 3600, 2),
                'avg_session_duration': round(avg_session_duration, 0),
                'avg_session_duration_minutes': round(avg_session_duration / 60, 1)
            },
            'today': {
                'sessions': len(today_sessions),
                'duration': today_duration,
                'duration_hours': round(today_duration / 3600, 2),
                'duration_minutes': round(today_duration / 60, 1)
            },
            'this_week': {
                'sessions': len(week_sessions),
                'duration': week_duration,
                'duration_hours': round(week_duration / 3600, 2),
                'duration_minutes': round(week_duration / 60, 1)
            }
        })
    except Exception as e:
        print(f"Error getting productivity data: {e}")
        return jsonify({"error": str(e)}), 500


@focus_session_bp.route("/api/sessions", methods=["GET"])
def api_get_recent_sessions():
    """API endpoint to get recent focus sessions"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Get student ID from user ID
        student_repo = RepositoryFactory.get_repository("student")
        student = student_repo.get_by_user_id(user_id)
        
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        # Get focus sessions for the student
        focus_session_repo = RepositoryFactory.get_repository("focus_session")
        all_sessions = focus_session_repo.get_by_student(student.Student_ID)
        
        # Get recent sessions (limit)
        recent_sessions = all_sessions[:limit]
        
        # Format sessions for response
        sessions_data = []
        for session in recent_sessions:
            start_time = session.Start_Time
            duration_minutes = session.Duration // 60
            duration_seconds = session.Duration % 60
            
            sessions_data.append({
                'id': session.Session_ID,
                'date': start_time.date().isoformat() if start_time else None,
                'start_time': start_time.strftime('%H:%M:%S') if start_time else None,
                'duration': f"{duration_minutes}m {duration_seconds}s",
                'duration_seconds': session.Duration,
                'completed': session.Completed
            })
        
        return jsonify({
            'sessions': sessions_data,
            'total': len(all_sessions)
        })
    except Exception as e:
        print(f"Error getting recent sessions: {e}")
        return jsonify({"error": str(e)}), 500

