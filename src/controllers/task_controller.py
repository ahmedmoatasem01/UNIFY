from flask import Blueprint, render_template, request, jsonify, session
from repositories.repository_factory import RepositoryFactory
from models.focus_session import FocusSession
from datetime import datetime

task_bp = Blueprint("task", __name__, url_prefix="/tasks")


@task_bp.route("/api", methods=["GET"])
def api_list_tasks():
    """API endpoint to get all tasks"""
    repo = RepositoryFactory.get_repository("task")
    tasks = repo.get_all()
    return jsonify([task.to_dict() for task in tasks])


@task_bp.route("/api/<int:task_id>", methods=["GET"])
def api_get_task(task_id):
    """API endpoint to get a specific task"""
    repo = RepositoryFactory.get_repository("task")
    task = repo.get_by_id(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task.to_dict())


@task_bp.route("/api/student/<int:student_id>", methods=["GET"])
def api_get_tasks_by_student(student_id):
    """API endpoint to get tasks by student"""
    repo = RepositoryFactory.get_repository("task")
    tasks = repo.get_by_student(student_id)
    return jsonify([task.to_dict() for task in tasks])


@task_bp.route("/api", methods=["POST"])
def api_create_task():
    """API endpoint to create a new task"""
    from flask import session
    from models.task import Task
    from datetime import datetime
    
    data = request.get_json()
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    # Get student_id from user_id
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id)
    
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    # Parse due date if provided
    due_date = None
    if data.get("Due_Date"):
        try:
            if isinstance(data.get("Due_Date"), str):
                # Handle datetime-local format: "2024-01-15T10:30"
                due_date = datetime.strptime(data.get("Due_Date"), "%Y-%m-%dT%H:%M")
            else:
                due_date = data.get("Due_Date")
        except:
            due_date = None
    
    task = Task(
        Student_ID=student.Student_ID,
        Task_Title=data.get("Task_Title", ""),
        Due_Date=due_date,
        Priority=data.get("Priority", "medium"),
        Status=data.get("Status", "pending")
    )
    repo = RepositoryFactory.get_repository("task")
    created_task = repo.create(task)
    return jsonify(created_task.to_dict()), 201


@task_bp.route("/api/<int:task_id>", methods=["PUT"])
def api_update_task(task_id):
    """API endpoint to update a task"""
    from flask import session
    from datetime import datetime
    
    data = request.get_json()
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    repo = RepositoryFactory.get_repository("task")
    task = repo.get_by_id(task_id)
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    # Verify ownership (optional - can be added if needed)
    
    # Update fields
    if "Task_Title" in data:
        task.Task_Title = data["Task_Title"]
    if "Due_Date" in data:
        if data["Due_Date"]:
            try:
                if isinstance(data["Due_Date"], str):
                    task.Due_Date = datetime.strptime(data["Due_Date"], "%Y-%m-%dT%H:%M")
                else:
                    task.Due_Date = data["Due_Date"]
            except:
                pass
        else:
            task.Due_Date = None
    if "Priority" in data:
        task.Priority = data["Priority"]
    if "Status" in data:
        task.Status = data["Status"]
    
    updated_task = repo.update(task)
    return jsonify(updated_task.to_dict()), 200


@task_bp.route("/api/<int:task_id>", methods=["DELETE"])
def api_delete_task(task_id):
    """API endpoint to delete a task"""
    from flask import session
    
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    repo = RepositoryFactory.get_repository("task")
    task = repo.get_by_id(task_id)
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    success = repo.delete(task_id)
    if success:
        return jsonify({"message": "Task deleted successfully"}), 200
    else:
        return jsonify({"error": "Failed to delete task"}), 500


@task_bp.route("/api/user", methods=["GET"])
def api_get_tasks_by_user():
    """API endpoint to get tasks for current user"""
    from flask import session
    
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    repo = RepositoryFactory.get_repository("task")
    tasks = repo.get_by_user_id(user_id)
    return jsonify([task.to_dict() for task in tasks])


@task_bp.route("/api/focus-sessions", methods=["POST"])
def api_create_focus_session():
    """API endpoint to create a focus session (from pomodoro timer)"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    # Get student_id from user_id
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id) if student_repo else None
    
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    data = request.get_json()
    duration = data.get("duration", 0)  # Duration in minutes
    completed = data.get("completed", True)
    
    focus_repo = RepositoryFactory.get_repository("focus_session")
    if not focus_repo:
        return jsonify({"error": "Focus session repository not available"}), 503
    
    start_time = datetime.now()
    end_time = datetime.now() if completed else None
    
    focus_session = FocusSession(
        Student_ID=student.Student_ID,
        Duration=duration,
        Start_Time=start_time,
        End_Time=end_time,
        Completed=completed
    )
    
    created_session = focus_repo.create(focus_session)
    return jsonify(created_session.to_dict()), 201


@task_bp.route("/api/focus-sessions/stats", methods=["GET"])
def api_get_focus_session_stats():
    """API endpoint to get focus session statistics for current user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    # Get student_id from user_id
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id) if student_repo else None
    
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    try:
        focus_repo = RepositoryFactory.get_repository("focus_session")
        if not focus_repo:
            return jsonify({
                "total_sessions": 0,
                "total_minutes": 0,
                "today_sessions": 0,
                "avg_duration": 0
            })
        
        # Initialize table
        focus_repo.create_table()
        
        sessions = focus_repo.get_by_student(student.Student_ID)
        
        # Calculate statistics
        total_sessions = len([s for s in sessions if s.Completed])
        total_minutes = sum(s.Duration for s in sessions if s.Completed)
        
        # Today's sessions
        today = datetime.now().date()
        today_sessions = len([s for s in sessions if s.Completed and s.Start_Time and s.Start_Time.date() == today])
        
        # Average duration
        avg_duration = round(total_minutes / total_sessions, 1) if total_sessions > 0 else 0
        
        return jsonify({
            "total_sessions": total_sessions,
            "total_minutes": total_minutes,
            "today_sessions": today_sessions,
            "avg_duration": avg_duration
        })
    except Exception as e:
        print(f"Error getting focus session stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "total_sessions": 0,
            "total_minutes": 0,
            "today_sessions": 0,
            "avg_duration": 0
        })


@task_bp.route("/api/study-plans", methods=["GET"])
def api_get_study_plans():
    """API endpoint to get study plans for current user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id) if student_repo else None
    
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    try:
        study_plan_repo = RepositoryFactory.get_repository("study_plan")
        if not study_plan_repo:
            return jsonify([])
        
        # Initialize table
        study_plan_repo.create_table()
        
        plans = study_plan_repo.get_by_student(student.Student_ID)
        return jsonify([plan.to_dict() for plan in plans])
    except Exception as e:
        print(f"Error getting study plans: {e}")
        return jsonify([])


@task_bp.route("/api/study-plans/generate", methods=["POST"])
def api_generate_study_plan():
    """API endpoint to generate a new study plan"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id) if student_repo else None
    
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    data = request.get_json()
    course_id = data.get("course_id")
    plan_name = data.get("plan_name", "My Study Plan")
    start_date_str = data.get("start_date")
    end_date_str = data.get("end_date")
    tasks = data.get("tasks", [])  # List of tasks with priorities
    notes = data.get("notes", "")
    
    if not start_date_str or not end_date_str:
        return jsonify({"error": "start_date and end_date are required"}), 400
    
    try:
        from datetime import date as date_type
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    try:
        study_plan_repo = RepositoryFactory.get_repository("study_plan")
        if not study_plan_repo:
            return jsonify({"error": "Study plan repository not available"}), 503
        
        # Initialize table
        study_plan_repo.create_table()
        
        from models.study_plan import StudyPlan
        plan = StudyPlan(
            Student_ID=student.Student_ID,
            Course_ID=course_id,
            Plan_Name=plan_name,
            Start_Date=start_date,
            End_Date=end_date,
            Status='active',
            Completion_Percentage=0.0
        )
        
        created_plan = study_plan_repo.create(plan)
        
        # If tasks were provided, create study tasks (AI decomposition will happen later)
        if tasks and len(tasks) > 0:
            try:
                study_task_repo = RepositoryFactory.get_repository("study_task")
                if study_task_repo:
                    study_task_repo.create_table()
                    
                    from models.study_task import StudyTask
                    from datetime import timedelta
                    
                    # Distribute tasks across the plan duration
                    days_diff = (end_date - start_date).days
                    tasks_per_day = max(1, len(tasks) // max(1, days_diff // 7))  # Spread over weeks
                    
                    for idx, task_data in enumerate(tasks):
                        task_name = task_data.get("name", f"Task {idx + 1}")
                        task_priority = task_data.get("priority", "medium")
                        
                        # Calculate due date (distribute evenly)
                        days_offset = min(idx * (days_diff // max(1, len(tasks))), days_diff - 1)
                        task_due_date = start_date + timedelta(days=days_offset)
                        
                        study_task = StudyTask(
                            Plan_ID=created_plan.Plan_ID,
                            Task_Title=task_name,
                            Priority=task_priority,
                            Status='pending',
                            Due_Date=datetime.combine(task_due_date, datetime.min.time()),
                            Estimated_Hours=2.0 if task_priority == 'high' else 1.5 if task_priority == 'medium' else 1.0
                        )
                        study_task_repo.create(study_task)
            except Exception as task_error:
                print(f"Error creating study tasks: {task_error}")
                # Don't fail the whole request if tasks fail
        
        return jsonify(created_plan.to_dict()), 201
    except Exception as e:
        print(f"Error creating study plan: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@task_bp.route("/api/courses/enrolled", methods=["GET"])
def api_get_enrolled_courses():
    """API endpoint to get enrolled courses for current user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id) if student_repo else None
    
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    try:
        enrollment_repo = RepositoryFactory.get_repository("enrollment")
        course_repo = RepositoryFactory.get_repository("course")
        
        if not enrollment_repo or not course_repo:
            return jsonify([])
        
        enrollments = enrollment_repo.get_by_student(student.Student_ID)
        enrolled_courses = []
        
        for enrollment in enrollments:
            if enrollment.Status == 'enrolled':
                course = course_repo.get_by_id(enrollment.Course_ID)
                if course:
                    # Get course code from Course_Schedule_Slot if available
                    from core.db_singleton import DatabaseConnection
                    db = DatabaseConnection()
                    conn = db.get_connection()
                    try:
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT TOP 1 Course_Code FROM Course_Schedule_Slot 
                            WHERE Course_ID = ? 
                            ORDER BY Course_Code
                        """, (enrollment.Course_ID,))
                        row = cursor.fetchone()
                        course_code = row[0] if row else f"COURSE-{course.Course_ID}"
                    except:
                        course_code = f"COURSE-{course.Course_ID}"
                    finally:
                        cursor.close()
                        conn.close()
                    
                    enrolled_courses.append({
                        'Course_ID': course.Course_ID,
                        'Course_Code': course_code,
                        'Course_Name': course.Course_Name if hasattr(course, 'Course_Name') else str(course)
                    })
        
        return jsonify(enrolled_courses)
    except Exception as e:
        print(f"Error getting enrolled courses: {e}")
        return jsonify([])


@task_bp.route("/api/study-plans/<int:plan_id>", methods=["GET"])
def api_get_study_plan(plan_id):
    """API endpoint to get a specific study plan"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id) if student_repo else None
    
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    try:
        study_plan_repo = RepositoryFactory.get_repository("study_plan")
        if not study_plan_repo:
            return jsonify({"error": "Study plan repository not available"}), 503
        
        # Initialize table if needed
        study_plan_repo.create_table()
        
        plan = study_plan_repo.get_by_id(plan_id)
        if not plan:
            return jsonify({"error": "Study plan not found"}), 404
        
        # Verify ownership
        if plan.Student_ID != student.Student_ID:
            return jsonify({"error": "Unauthorized"}), 403
        
        return jsonify(plan.to_dict())
    except Exception as e:
        print(f"Error getting study plan: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@task_bp.route("/api/study-plans/<int:plan_id>/tasks", methods=["GET"])
def api_get_study_plan_tasks(plan_id):
    """API endpoint to get tasks for a study plan"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id) if student_repo else None
    
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    try:
        study_plan_repo = RepositoryFactory.get_repository("study_plan")
        study_task_repo = RepositoryFactory.get_repository("study_task")
        
        if not study_plan_repo or not study_task_repo:
            return jsonify([])
        
        # Verify plan ownership
        plan = study_plan_repo.get_by_id(plan_id)
        if not plan or plan.Student_ID != student.Student_ID:
            return jsonify({"error": "Unauthorized"}), 403
        
        # Initialize table if needed
        study_task_repo.create_table()
        
        tasks = study_task_repo.get_by_plan(plan_id)
        return jsonify([task.to_dict() for task in tasks])
    except Exception as e:
        print(f"Error getting study plan tasks: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([])


@task_bp.route("/api/study-plans/tasks/<int:task_id>", methods=["PUT"])
def api_update_study_task(task_id):
    """API endpoint to update a study task"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        study_task_repo = RepositoryFactory.get_repository("study_task")
        if not study_task_repo:
            return jsonify({"error": "Study task repository not available"}), 503
        
        task = study_task_repo.get_by_id(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        # Verify ownership through plan
        study_plan_repo = RepositoryFactory.get_repository("study_plan")
        if study_plan_repo:
            plan = study_plan_repo.get_by_id(task.Plan_ID)
            if plan:
                student_repo = RepositoryFactory.get_repository("student")
                student = student_repo.get_by_user_id(user_id) if student_repo else None
                if student and plan.Student_ID != student.Student_ID:
                    return jsonify({"error": "Unauthorized"}), 403
        
        data = request.get_json()
        if "Status" in data:
            task.Status = data["Status"]
        
        updated_task = study_task_repo.update(task)
        return jsonify(updated_task.to_dict())
    except Exception as e:
        print(f"Error updating study task: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@task_bp.route("/api/study-plans/<int:plan_id>/recommendations", methods=["GET"])
def api_get_study_recommendations(plan_id):
    """API endpoint to get AI-powered resource recommendations for a study plan using RAG"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id) if student_repo else None
    
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    try:
        study_plan_repo = RepositoryFactory.get_repository("study_plan")
        study_task_repo = RepositoryFactory.get_repository("study_task")
        
        if not study_plan_repo:
            return jsonify([])
        
        # Verify plan ownership
        plan = study_plan_repo.get_by_id(plan_id)
        if not plan or plan.Student_ID != student.Student_ID:
            return jsonify({"error": "Unauthorized"}), 403
        
        # Get tasks for context
        tasks = []
        if study_task_repo:
            study_task_repo.create_table()
            tasks = study_task_repo.get_by_plan(plan_id)
        
        # Use RAG to get recommendations
        from services.ai_assistant_service import get_rag_engine
        
        rag_engine = get_rag_engine()
        
        # Build query from plan and tasks
        query_parts = [plan.Plan_Name]
        if plan.Course_ID:
            course_repo = RepositoryFactory.get_repository("course")
            if course_repo:
                course = course_repo.get_by_id(plan.Course_ID)
                if course:
                    query_parts.append(course.Course_Name if hasattr(course, 'Course_Name') else str(course))
        
        for task in tasks[:5]:  # Use top 5 tasks
            query_parts.append(task.Task_Title)
        
        query = " ".join(query_parts)
        
        # Retrieve relevant documents using RAG
        relevant_docs = rag_engine.retrieve_relevant_docs(query, limit=5)
        
        # Generate recommendations
        recommendations = []
        for doc in relevant_docs:
            recommendations.append({
                'Title': doc.Title,
                'Content': doc.Content[:200] + '...' if len(doc.Content) > 200 else doc.Content,
                'Category': doc.Category,
                'Resource_Type': 'note' if 'note' in doc.Category.lower() else 'textbook' if 'book' in doc.Content.lower() else 'practice',
                'Relevance_Score': 0.85,  # Could be calculated based on keyword matching
                'Source': doc.Source if hasattr(doc, 'Source') else 'Knowledge Base'
            })
        
        # Also get course-specific recommendations if course is set
        if plan.Course_ID:
            course_query = f"{query_parts[-1]} course materials study resources"
            course_docs = rag_engine.retrieve_relevant_docs(course_query, limit=3)
            for doc in course_docs:
                if doc.KB_ID not in [r.get('KB_ID', -1) for r in recommendations]:
                    recommendations.append({
                        'Title': doc.Title,
                        'Content': doc.Content[:200] + '...' if len(doc.Content) > 200 else doc.Content,
                        'Category': doc.Category,
                        'Resource_Type': 'practice',
                        'Relevance_Score': 0.75,
                        'Source': doc.Source if hasattr(doc, 'Source') else 'Knowledge Base'
                    })
        
        return jsonify(recommendations[:10])  # Return top 10
        
    except Exception as e:
        print(f"Error getting study recommendations: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([])

