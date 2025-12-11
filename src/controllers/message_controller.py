from flask import Blueprint, render_template, request, jsonify, session
from repositories.repository_factory import RepositoryFactory
from models.message import Message
from datetime import datetime

message_bp = Blueprint("message", __name__, url_prefix="/messages")


def require_login(f):
    """Decorator to require user to be logged in"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function


@message_bp.route("/")
@require_login
def messages_page():
    """Render the messages page"""
    return render_template("messages.html")


@message_bp.route("/api/conversations", methods=["GET"])
@require_login
def api_get_conversations():
    """API endpoint to get all conversations for current user"""
    user_id = session.get('user_id')
    repo = RepositoryFactory.get_repository("message")
    conversations = repo.get_user_conversations(user_id)
    
    # Format timestamps for JSON
    for conv in conversations:
        if conv['Last_Message_Time']:
            conv['Last_Message_Time'] = conv['Last_Message_Time'].isoformat()
    
    return jsonify(conversations)


@message_bp.route("/api/conversation/<int:other_user_id>", methods=["GET"])
@require_login
def api_get_conversation(other_user_id):
    """API endpoint to get conversation with a specific user"""
    user_id = session.get('user_id')
    repo = RepositoryFactory.get_repository("message")
    messages = repo.get_conversation(user_id, other_user_id)
    
    # Mark messages as read
    repo.mark_conversation_as_read(user_id, other_user_id)
    
    return jsonify([message.to_dict() for message in messages])


@message_bp.route("/api/send", methods=["POST"])
@require_login
def api_send_message():
    """API endpoint to send a new message"""
    user_id = session.get('user_id')
    data = request.get_json()
    
    receiver_id = data.get("receiver_id")
    message_text = data.get("message_text")
    
    if not receiver_id or not message_text:
        return jsonify({"error": "receiver_id and message_text are required"}), 400
    
    # Validate message text is not empty
    if not message_text.strip():
        return jsonify({"error": "Message cannot be empty"}), 400
    
    message = Message(
        Sender_ID=user_id,
        Receiver_ID=receiver_id,
        Message_Text=message_text.strip(),
        Timestamp=datetime.now(),
        Is_Read=False
    )
    
    repo = RepositoryFactory.get_repository("message")
    created_message = repo.create(message)
    
    return jsonify(created_message.to_dict()), 201


@message_bp.route("/api/unread-count", methods=["GET"])
@require_login
def api_get_unread_count():
    """API endpoint to get unread message count"""
    user_id = session.get('user_id')
    repo = RepositoryFactory.get_repository("message")
    count = repo.get_unread_count(user_id)
    return jsonify({"unread_count": count})


@message_bp.route("/api/mark-read/<int:message_id>", methods=["POST"])
@require_login
def api_mark_message_read(message_id):
    """API endpoint to mark a message as read"""
    repo = RepositoryFactory.get_repository("message")
    success = repo.mark_as_read(message_id)
    if success:
        return jsonify({"message": "Marked as read"}), 200
    return jsonify({"error": "Message not found"}), 404


@message_bp.route("/api/users", methods=["GET"])
@require_login
def api_get_users():
    """API endpoint to get all users for starting new conversations"""
    user_repo = RepositoryFactory.get_repository("user")
    current_user_id = session.get('user_id')
    
    # Get all users except current user
    all_users = user_repo.get_all()
    users = [
        {
            'User_ID': user.User_ID,
            'Username': user.Username,
            'Email': user.Email
        }
        for user in all_users if user.User_ID != current_user_id
    ]
    
    return jsonify(users)


# Legacy endpoints for backwards compatibility
@message_bp.route("/list")
@require_login
def list_messages():
    """List all messages (legacy endpoint)"""
    repo = RepositoryFactory.get_repository("message")
    messages = repo.get_all()
    return render_template("message/list.html", messages=messages)


@message_bp.route("/api", methods=["GET"])
@require_login
def api_list_messages():
    """API endpoint to get all messages (legacy endpoint)"""
    repo = RepositoryFactory.get_repository("message")
    messages = repo.get_all()
    return jsonify([message.to_dict() for message in messages])


@message_bp.route("/api/<int:message_id>", methods=["GET"])
@require_login
def api_get_message(message_id):
    """API endpoint to get a specific message"""
    repo = RepositoryFactory.get_repository("message")
    message = repo.get_by_id(message_id)
    if not message:
        return jsonify({"error": "Message not found"}), 404
    return jsonify(message.to_dict())


@message_bp.route("/api/receiver/<int:receiver_id>", methods=["GET"])
@require_login
def api_get_messages_by_receiver(receiver_id):
    """API endpoint to get messages for a receiver"""
    repo = RepositoryFactory.get_repository("message")
    messages = repo.get_by_receiver(receiver_id)
    return jsonify([message.to_dict() for message in messages])

