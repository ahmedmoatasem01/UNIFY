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
    from core.user_helper import get_user_data
    user_id = session.get('user_id')
    user_data = get_user_data(user_id)
    return render_template("messages.html", user_data=user_data)


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
    
    return jsonify([message.to_dict(current_user_id=user_id) for message in messages])


@message_bp.route("/api/send", methods=["POST"])
@require_login
def api_send_message():
    """API endpoint to send a new message"""
    try:
        user_id = session.get('user_id')
        print(f"\n{'='*60}")
        print(f"[Messages] ▶ Sending message from user_id: {user_id}")
        
        data = request.get_json()
        print(f"[Messages] ▶ Raw request data: {data}")
        print(f"[Messages] ▶ Data type: {type(data)}")
        
        receiver_id = data.get("receiver_id") if data else None
        message_text = data.get("message_text") if data else None
        
        print(f"[Messages] ▶ Extracted - receiver_id: {receiver_id} (type: {type(receiver_id)})")
        print(f"[Messages] ▶ Extracted - message_text: {message_text} (type: {type(message_text)})")
        
        # Convert receiver_id to int and validate
        try:
            if receiver_id is None or receiver_id == '':
                print(f"[Messages] ❌ receiver_id is empty/None")
                receiver_id = None
            else:
                receiver_id = int(receiver_id)
                print(f"[Messages] ✅ Converted receiver_id to int: {receiver_id}")
        except (ValueError, TypeError) as e:
            print(f"[Messages] ❌ Error converting receiver_id: {e}")
            receiver_id = None
        
        if not receiver_id or not message_text:
            print(f"[Messages] ❌ Validation failed - receiver_id: {receiver_id}, message_text: {message_text}")
            print(f"{'='*60}\n")
            return jsonify({"error": "receiver_id and message_text are required"}), 400
        
        # Validate message text is not empty
        if not message_text.strip():
            print("[Messages] ❌ Empty message text")
            print(f"{'='*60}\n")
            return jsonify({"error": "Message cannot be empty"}), 400
        
        print(f"[Messages] ✅ Validation passed!")
        print(f"[Messages] ▶ Creating message:")
        print(f"[Messages]    Sender ID: {user_id}")
        print(f"[Messages]    Receiver ID: {receiver_id}")
        print(f"[Messages]    Text: '{message_text[:50]}...'")
        
        message = Message(
            Sender_ID=user_id,
            Receiver_ID=receiver_id,
            Message_Text=message_text.strip(),
            Timestamp=datetime.now(),
            Is_Read=False
        )
        
        print(f"[Messages] ▶ Message object created, calling repository...")
        repo = RepositoryFactory.get_repository("message")
        created_message = repo.create(message)
        
        print(f"[Messages] ✅ SUCCESS! Message created with ID: {created_message.Message_ID}")
        print(f"{'='*60}\n")
        
        return jsonify(created_message.to_dict()), 201
        
    except Exception as e:
        print(f"\n[Messages] ❌❌❌ EXCEPTION OCCURRED ❌❌❌")
        print(f"[Messages] Error type: {type(e).__name__}")
        print(f"[Messages] Error message: {str(e)}")
        print(f"[Messages] Full traceback:")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


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

