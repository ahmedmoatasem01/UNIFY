from flask import Blueprint, render_template, request, jsonify
from repositories.repository_factory import RepositoryFactory

task_bp = Blueprint("task", __name__, url_prefix="/tasks")


@task_bp.route("/")
def list_tasks():
    """List all tasks"""
    repo = RepositoryFactory.get_repository("task")
    tasks = repo.get_all()
    return render_template("task/list.html", tasks=tasks)


@task_bp.route("/<int:task_id>")
def view_task(task_id):
    """View a specific task"""
    repo = RepositoryFactory.get_repository("task")
    task = repo.get_by_id(task_id)
    if not task:
        return "Task not found", 404
    return render_template("task/detail.html", task=task)


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
    from models.task import Task
    data = request.get_json()
    task = Task(
        Student_ID=data.get("Student_ID"),
        Task_Title=data.get("Task_Title"),
        Due_Date=data.get("Due_Date"),
        Priority=data.get("Priority", "medium"),
        Status=data.get("Status", "pending")
    )
    repo = RepositoryFactory.get_repository("task")
    created_task = repo.create(task)
    return jsonify(created_task.to_dict()), 201

