from flask import Blueprint, render_template, request, jsonify
from repositories.repository_factory import RepositoryFactory

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

