from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from repositories.repository_factory import RepositoryFactory

user_bp = Blueprint("user", __name__, url_prefix="/users")


@user_bp.route("/")
def list_users():
    """List all users"""
    repo = RepositoryFactory.get_repository("user")
    users = repo.get_all()
    return render_template("user/list.html", users=users)


@user_bp.route("/<int:user_id>")
def view_user(user_id):
    """View a specific user"""
    repo = RepositoryFactory.get_repository("user")
    user = repo.get_by_id(user_id)
    if not user:
        return "User not found", 404
    return render_template("user/profile.html", user=user)


@user_bp.route("/api", methods=["GET"])
def api_list_users():
    """API endpoint to get all users"""
    repo = RepositoryFactory.get_repository("user")
    users = repo.get_all()
    return jsonify([user.to_dict() for user in users])


@user_bp.route("/api/<int:user_id>", methods=["GET"])
def api_get_user(user_id):
    """API endpoint to get a specific user"""
    repo = RepositoryFactory.get_repository("user")
    user = repo.get_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())


@user_bp.route("/api", methods=["POST"])
def api_create_user():
    """API endpoint to create a new user"""
    from models.user import User
    data = request.get_json()
    user = User(
        Username=data.get("Username"),
        Email=data.get("Email"),
        Password_Hash=data.get("Password_Hash")
    )
    repo = RepositoryFactory.get_repository("user")
    created_user = repo.create(user)
    return jsonify(created_user.to_dict()), 201