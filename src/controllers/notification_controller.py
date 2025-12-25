"""
Notification Controller
HTTP request handlers for notification endpoints
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from repositories.repository_factory import RepositoryFactory
from services.notification_service import get_notification_service
from models.notification import Notification

notification_bp = Blueprint('notification', __name__, url_prefix='/notifications')

# Initialize repository
try:
    notification_repo = RepositoryFactory.get_repository('notification')
    notification_repo.create_table()
    print("[Notification Controller] Notification table created/verified")
except Exception as e:
    print(f"Warning: Notification repository not available: {e}")
    notification_repo = None

# Initialize service (will handle None repo gracefully)
try:
    notification_service = get_notification_service()
except Exception as e:
    print(f"Warning: Notification service not available: {e}")
    notification_service = None


@notification_bp.route('/', methods=['GET'])
def get_notifications():
    """Get all notifications for current user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if not notification_service:
        return jsonify({'error': 'Notification service unavailable'}), 503
    
    try:
        user_id = session.get('user_id')
        limit = request.args.get('limit', type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        notifications = notification_service.get_notifications(
            user_id, 
            limit=limit, 
            unread_only=unread_only
        )
        
        return jsonify([n.to_dict() for n in notifications])
    except Exception as e:
        print(f"Error getting notifications: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/unread', methods=['GET'])
def get_unread_notifications():
    """Get unread notifications count"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if not notification_service:
        return jsonify({'error': 'Notification service unavailable'}), 503
    
    try:
        user_id = session.get('user_id')
        count = notification_service.get_unread_count(user_id)
        
        # Also get unread notifications
        notifications = notification_service.get_notifications(user_id, limit=10, unread_only=True)
        
        return jsonify({
            'count': count,
            'notifications': [n.to_dict() for n in notifications]
        })
    except Exception as e:
        print(f"Error getting unread notifications: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/<int:notification_id>', methods=['GET'])
def get_notification(notification_id):
    """Get a specific notification"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        if not notification_repo:
            return jsonify({'error': 'Service unavailable'}), 503
        
        notification = notification_repo.get_by_id(notification_id)
        if not notification:
            return jsonify({'error': 'Notification not found'}), 404
        
        # Check ownership
        user_id = session.get('user_id')
        if notification.User_ID != user_id:
            return jsonify({'error': 'Forbidden'}), 403
        
        return jsonify(notification.to_dict())
    except Exception as e:
        print(f"Error getting notification: {e}")
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/', methods=['POST'])
def create_notification():
    """Create a new notification (admin/system use)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if not notification_service:
        return jsonify({'error': 'Notification service unavailable'}), 503
    
    try:
        data = request.json
        user_id = data.get('user_id') or session.get('user_id')
        title = data.get('title')
        message = data.get('message')
        notification_type = data.get('type', 'system')
        priority = data.get('priority', 'medium')
        action_url = data.get('action_url')
        
        if not title or not message:
            return jsonify({'error': 'title and message are required'}), 400
        
        notification = notification_service.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            action_url=action_url
        )
        
        return jsonify(notification.to_dict()), 201
    except Exception as e:
        print(f"Error creating notification: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/<int:notification_id>/read', methods=['PUT'])
def mark_as_read(notification_id):
    """Mark a notification as read"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        if not notification_repo:
            return jsonify({'error': 'Service unavailable'}), 503
        
        notification = notification_repo.get_by_id(notification_id)
        if not notification:
            return jsonify({'error': 'Notification not found'}), 404
        
        # Check ownership
        user_id = session.get('user_id')
        if notification.User_ID != user_id:
            return jsonify({'error': 'Forbidden'}), 403
        
        if not notification_service:
            return jsonify({'error': 'Notification service unavailable'}), 503
        
        success = notification_service.mark_as_read(notification_id)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to mark as read'}), 400
    except Exception as e:
        print(f"Error marking notification as read: {e}")
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    """Delete a notification"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        if not notification_repo:
            return jsonify({'error': 'Service unavailable'}), 503
        
        notification = notification_repo.get_by_id(notification_id)
        if not notification:
            return jsonify({'error': 'Notification not found'}), 404
        
        # Check ownership
        user_id = session.get('user_id')
        if notification.User_ID != user_id:
            return jsonify({'error': 'Forbidden'}), 403
        
        if not notification_service:
            return jsonify({'error': 'Notification service unavailable'}), 503
        
        success = notification_service.delete_notification(notification_id)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to delete notification'}), 400
    except Exception as e:
        print(f"Error deleting notification: {e}")
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/mark-all-read', methods=['POST'])
def mark_all_as_read():
    """Mark all notifications as read for current user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if not notification_service:
        return jsonify({'error': 'Notification service unavailable'}), 503
    
    try:
        user_id = session.get('user_id')
        count = notification_service.mark_all_as_read(user_id)
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        print(f"Error marking all as read: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/test-db', methods=['GET'])
def test_database():
    """Test endpoint to verify database connection and table creation"""
    try:
        if not notification_repo:
            return jsonify({'error': 'Notification repository not available'}), 503
        
        # Test table creation
        notification_repo.create_table()
        
        # Test getting all notifications
        all_notifications = notification_repo.get_all()
        
        # Get user repo to count users
        user_repo = RepositoryFactory.get_repository('user')
        users = user_repo.get_all() if user_repo else []
        
        return jsonify({
            'status': 'success',
            'message': 'Database connection successful',
            'table_created': True,
            'notification_count': len(all_notifications),
            'user_count': len(users),
            'notifications': [n.to_dict() for n in all_notifications[:5]]  # Return first 5
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e),
            'error_type': type(e).__name__
        }), 500


@notification_bp.route('/seed', methods=['POST'])
def seed_notifications():
    """Seed the database with sample notifications for all users or current user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if not notification_service or not notification_repo:
        return jsonify({'error': 'Notification service unavailable'}), 503
    
    try:
        from datetime import datetime, timedelta
        user_repo = RepositoryFactory.get_repository('user')
        
        # Check if should seed for all users or just current user
        data = request.json or {}
        seed_all = data.get('all_users', False)
        
        if seed_all:
            # Seed for all users
            users = user_repo.get_all() if user_repo else []
            target_users = [{'user_id': u.User_ID, 'username': getattr(u, 'Username', 'User')} for u in users]
        else:
            # Seed for current user only
            current_user_id = session.get('user_id')
            current_user = user_repo.get_by_id(current_user_id) if user_repo else None
            target_users = [{'user_id': current_user_id, 'username': getattr(current_user, 'Username', 'User') if current_user else 'User'}]
        
        # Sample notifications
        sample_notifications = [
            {
                'title': 'Welcome to Unify!',
                'message': 'Welcome to the Unify student management system. Start exploring your courses and schedule.',
                'type': 'system',
                'priority': 'medium'
            },
            {
                'title': 'Task Reminder: Assignment Due Soon',
                'message': 'You have a task due soon: Complete Database Design Project. Due in 2 days.',
                'type': 'task',
                'priority': 'high',
                'action_url': '/tasks'
            },
            {
                'title': 'Grade Update Available',
                'message': 'Your grade for "Introduction to Computer Science" has been updated. Check your transcript.',
                'type': 'grade',
                'priority': 'medium',
                'action_url': '/transcript'
            },
            {
                'title': 'New Announcement',
                'message': 'Spring semester registration opens next week. Make sure to register for your courses.',
                'type': 'announcement',
                'priority': 'low'
            },
            {
                'title': 'Upcoming Assignment',
                'message': 'Assignment "Web Development Project" is due in 3 days. Don\'t forget to submit!',
                'type': 'assignment',
                'priority': 'high',
                'action_url': '/tasks'
            },
            {
                'title': 'Course Registration Reminder',
                'message': 'Don\'t forget to register for next semester courses. The registration deadline is approaching.',
                'type': 'system',
                'priority': 'medium',
                'action_url': '/course-registration'
            },
            {
                'title': 'New Message Received',
                'message': 'You have received a new message from your instructor. Check your messages.',
                'type': 'message',
                'priority': 'low',
                'action_url': '/messages'
            }
        ]
        
        total_created = 0
        user_results = []
        
        for user_info in target_users:
            user_id = user_info['user_id']
            username = user_info['username']
            user_created = 0
            
            for i, sample in enumerate(sample_notifications):
                # Check if already exists for this user
                existing = notification_repo.get_by_user(user_id, limit=100)
                if any(n.Title == sample['title'] for n in existing):
                    continue
                
                notification = notification_service.create_notification(
                    user_id=user_id,
                    title=sample['title'],
                    message=sample['message'],
                    notification_type=sample['type'],
                    priority=sample['priority'],
                    action_url=sample.get('action_url')
                )
                user_created += 1
                total_created += 1
            
            # Get counts for this user
            user_total = len(notification_repo.get_by_user(user_id))
            user_unread = notification_repo.get_unread_count(user_id)
            
            user_results.append({
                'user_id': user_id,
                'username': username,
                'created': user_created,
                'total': user_total,
                'unread': user_unread
            })
        
        return jsonify({
            'success': True,
            'message': f'Created {total_created} sample notifications for {len(target_users)} user(s)',
            'total_created': total_created,
            'users': user_results
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500