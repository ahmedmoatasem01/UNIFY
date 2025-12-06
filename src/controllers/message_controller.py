from flask import Blueprint, render_template, request, jsonify
from repositories.repository_factory import RepositoryFactory

message_bp = Blueprint("message", __name__, url_prefix="/messages")


@message_bp.route("/")
def list_messages():
    """List all messages"""
    repo = RepositoryFactory.get_repository("message")
    messages = repo.get_all()
    return render_template("message/list.html", messages=messages)


@message_bp.route("/api", methods=["GET"])
def api_list_messages():
    """API endpoint to get all messages"""
    repo = RepositoryFactory.get_repository("message")
    messages = repo.get_all()
    return jsonify([message.to_dict() for message in messages])


@message_bp.route("/api/<int:message_id>", methods=["GET"])
def api_get_message(message_id):
    """API endpoint to get a specific message"""
    repo = RepositoryFactory.get_repository("message")
    message = repo.get_by_id(message_id)
    if not message:
        return jsonify({"error": "Message not found"}), 404
    return jsonify(message.to_dict())


@message_bp.route("/api/conversation/<int:user1_id>/<int:user2_id>", methods=["GET"])
def api_get_conversation(user1_id, user2_id):
    """API endpoint to get conversation between two users"""
    repo = RepositoryFactory.get_repository("message")
    messages = repo.get_conversation(user1_id, user2_id)
    return jsonify([message.to_dict() for message in messages])


@message_bp.route("/api/receiver/<int:receiver_id>", methods=["GET"])
def api_get_messages_by_receiver(receiver_id):
    """API endpoint to get messages for a receiver"""
    repo = RepositoryFactory.get_repository("message")
    messages = repo.get_by_receiver(receiver_id)
    return jsonify([message.to_dict() for message in messages])


@message_bp.route("/api", methods=["POST"])
def api_create_message():
    """API endpoint to create a new message"""
    from models.message import Message
    from datetime import datetime
    data = request.get_json()
    message = Message(
        Sender_ID=data.get("Sender_ID"),
        Receiver_ID=data.get("Receiver_ID"),
        Message_Text=data.get("Message_Text"),
        Timestamp=data.get("Timestamp", datetime.now())
    )
    repo = RepositoryFactory.get_repository("message")
    created_message = repo.create(message)
    return jsonify(created_message.to_dict()), 201

