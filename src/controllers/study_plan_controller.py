"""
Study Plan Controller
Handles HTTP requests for study plan management
"""
from flask import Blueprint, render_template, request, jsonify, session
from repositories.repository_factory import RepositoryFactory
from services.study_plan_service import StudyPlanService
from services.task_decomposition_service import TaskDecompositionService
from models.study_plan import StudyPlan
from models.study_task import StudyTask
from models.study_recommendation import StudyRecommendation
from datetime import datetime, date
import json


study_plan_bp = Blueprint("study_plan", __name__, url_prefix="/study-plans")


# Initialize services
study_plan_service = StudyPlanService()
task_decomposition_service = TaskDecompositionService()


# ============================================================================
# WEB ROUTES (HTML Pages)
# ============================================================================

@study_plan_bp.route("/", methods=["GET"])
def study_plans_page():
    """Render the study plans page"""
    user_id = session.get('user_id')
    if not user_id:
        return render_template('login.html')
    
    return render_template('study_plans.html')


@study_plan_bp.route("/<int:plan_id>", methods=["GET"])
def study_plan_detail_page(plan_id):
    """Render the study plan detail page"""
    user_id = session.get('user_id')
    if not user_id:
        return render_template('login.html')
    
    return render_template('study_plan_detail.html', plan_id=plan_id)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@study_plan_bp.route("/api/student/<int:student_id>", methods=["GET"])
def api_get_student_plans(student_id):
    """Get all study plans for a student"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        plan_repo = RepositoryFactory.get_repository('study_plan')
        plans = plan_repo.get_by_student(student_id)
        return jsonify([plan.to_dict() for plan in plans]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@study_plan_bp.route("/api/generate", methods=["POST"])
def api_generate_plan():
    """Generate a new study plan"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        data = request.get_json()
        
        # Get student_id from user_id
        student_repo = RepositoryFactory.get_repository("student")
        student = student_repo.get_by_user_id(user_id)
        
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        # Parse dates
        start_date = None
        end_date = None
        
        if data.get('start_date'):
            try:
                start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            except:
                start_date = date.today()
        
        if data.get('end_date'):
            try:
                end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            except:
                from datetime import timedelta
                end_date = (start_date or date.today()) + timedelta(days=30)
        
        # Generate the study plan
        plan = study_plan_service.generate_study_plan(
            student_id=student.Student_ID,
            course_id=data.get('course_id'),
            plan_name=data.get('plan_name', ''),
            start_date=start_date,
            end_date=end_date,
            include_existing_tasks=data.get('include_existing_tasks', True)
        )
        
        return jsonify(plan.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@study_plan_bp.route("/api/<int:plan_id>", methods=["GET"])
def api_get_plan(plan_id):
    """Get a specific study plan"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        plan_repo = RepositoryFactory.get_repository('study_plan')
        plan = plan_repo.get_by_id(plan_id)
        
        if not plan:
            return jsonify({"error": "Study plan not found"}), 404
        
        return jsonify(plan.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@study_plan_bp.route("/api/<int:plan_id>", methods=["PUT"])
def api_update_plan(plan_id):
    """Update a study plan"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        data = request.get_json()
        plan_repo = RepositoryFactory.get_repository('study_plan')
        plan = plan_repo.get_by_id(plan_id)
        
        if not plan:
            return jsonify({"error": "Study plan not found"}), 404
        
        # Update fields
        if 'plan_name' in data:
            plan.Plan_Name = data['plan_name']
        if 'start_date' in data:
            try:
                plan.Start_Date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            except:
                pass
        if 'end_date' in data:
            try:
                plan.End_Date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            except:
                pass
        if 'status' in data:
            plan.Status = data['status']
        if 'completion_percentage' in data:
            plan.Completion_Percentage = float(data['completion_percentage'])
        
        updated_plan = plan_repo.update(plan)
        return jsonify(updated_plan.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@study_plan_bp.route("/api/<int:plan_id>", methods=["DELETE"])
def api_delete_plan(plan_id):
    """Delete a study plan"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        plan_repo = StudyPlanRepository()
        success = plan_repo.delete(plan_id)
        
        if success:
            return jsonify({"message": "Study plan deleted successfully"}), 200
        else:
            return jsonify({"error": "Failed to delete study plan"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@study_plan_bp.route("/api/<int:plan_id>/tasks", methods=["GET"])
def api_get_plan_tasks(plan_id):
    """Get all tasks for a study plan"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        task_repo = RepositoryFactory.get_repository('study_task')
        tasks = task_repo.get_by_plan(plan_id)
        return jsonify([task.to_dict() for task in tasks]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@study_plan_bp.route("/api/<int:plan_id>/tasks", methods=["POST"])
def api_create_plan_task(plan_id):
    """Create a new task for a study plan"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        data = request.get_json()
        
        # Parse due date
        due_date = None
        if data.get('due_date'):
            try:
                due_date = datetime.strptime(data['due_date'], '%Y-%m-%dT%H:%M')
            except:
                try:
                    due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
                except:
                    pass
        
        # Create the task
        task = StudyTask(
            Plan_ID=plan_id,
            Parent_Task_ID=data.get('parent_task_id'),
            Task_Title=data.get('task_title', ''),
            Description=data.get('description'),
            Estimated_Hours=data.get('estimated_hours'),
            Due_Date=due_date,
            Priority=data.get('priority', 'medium'),
            Status=data.get('status', 'pending')
        )
        
        # Handle suggested resources
        if data.get('suggested_resources'):
            if isinstance(data['suggested_resources'], list):
                task.set_resources_list(data['suggested_resources'])
            else:
                task.Suggested_Resources = data['suggested_resources']
        
        task_repo = RepositoryFactory.get_repository('study_task')
        created_task = task_repo.create(task)
        
        # Auto-decompose if requested and task is large
        if data.get('auto_decompose', False) and created_task.Estimated_Hours and created_task.Estimated_Hours > 4.0:
            subtasks = task_decomposition_service.decompose_task(
                created_task.Task_Title,
                created_task.Description or '',
                created_task.Estimated_Hours,
                created_task.Due_Date or datetime.now()
            )
            
            for subtask_data in subtasks:
                subtask = StudyTask(
                    Plan_ID=plan_id,
                    Parent_Task_ID=created_task.Task_ID,
                    Task_Title=subtask_data['title'],
                    Description=subtask_data['description'],
                    Estimated_Hours=subtask_data['estimated_hours'],
                    Due_Date=subtask_data['due_date'],
                    Priority=subtask_data['priority'],
                    Status='pending'
                )
                task_repo.create(subtask)
        
        return jsonify(created_task.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@study_plan_bp.route("/api/tasks/<int:task_id>", methods=["PUT"])
def api_update_task(task_id):
    """Update a study task"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        data = request.get_json()
        task_repo = RepositoryFactory.get_repository('study_task')
        task = task_repo.get_by_id(task_id)
        
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        # Update fields
        if 'task_title' in data:
            task.Task_Title = data['task_title']
        if 'description' in data:
            task.Description = data['description']
        if 'estimated_hours' in data:
            task.Estimated_Hours = data['estimated_hours']
        if 'actual_hours' in data:
            task.Actual_Hours = data['actual_hours']
        if 'due_date' in data:
            try:
                task.Due_Date = datetime.strptime(data['due_date'], '%Y-%m-%dT%H:%M')
            except:
                try:
                    task.Due_Date = datetime.strptime(data['due_date'], '%Y-%m-%d')
                except:
                    pass
        if 'priority' in data:
            task.Priority = data['priority']
        if 'status' in data:
            task.Status = data['status']
        if 'suggested_resources' in data:
            if isinstance(data['suggested_resources'], list):
                task.set_resources_list(data['suggested_resources'])
            else:
                task.Suggested_Resources = data['suggested_resources']
        
        updated_task = task_repo.update(task)
        
        # Update plan completion percentage
        plan_repo = RepositoryFactory.get_repository('study_plan')
        tasks = task_repo.get_by_plan(task.Plan_ID)
        completed = len([t for t in tasks if t.Status == 'completed'])
        if tasks:
            completion_pct = (completed / len(tasks)) * 100
            plan_repo.update_completion_percentage(task.Plan_ID, completion_pct)
        
        return jsonify(updated_task.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@study_plan_bp.route("/api/recommendations/student/<int:student_id>", methods=["GET"])
def api_get_recommendations(student_id):
    """Get study recommendations for a student"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        course_id = request.args.get('course_id', type=int)
        topic = request.args.get('topic')
        
        # Generate new recommendations
        recommendations = study_plan_service.generate_recommendations(
            student_id=student_id,
            course_id=course_id,
            topic=topic
        )
        
        return jsonify([rec.to_dict() for rec in recommendations]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@study_plan_bp.route("/api/<int:plan_id>/adjust", methods=["POST"])
def api_adjust_plan(plan_id):
    """Adjust a study plan based on progress"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        data = request.get_json()
        reason = data.get('reason', 'manual')
        
        adjusted_plan = study_plan_service.adjust_study_plan(plan_id, reason)
        
        return jsonify(adjusted_plan.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@study_plan_bp.route("/api/<int:plan_id>/analytics", methods=["GET"])
def api_get_plan_analytics(plan_id):
    """Get analytics for a study plan"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        analytics = study_plan_service.get_study_plan_analytics(plan_id)
        return jsonify(analytics), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
